"""Anomaly detector. Owner: P1.

Polls a metrics client, keeps a rolling baseline (median + MAD spread) per series, and opens an
Incident when a series breaches for N consecutive polls. One open incident per symptom, with a cooldown.

No alert/webhook exists in the repo (TODO(confirm) with organizers), so this polls Prometheus directly.
Read-only: the only network call is an HTTP GET to the metrics API.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.parse
import urllib.request
import uuid
from collections import deque
from typing import Callable, Deque, Dict, List, Optional, Protocol

from agent.models import Config, Incident, load_config, make_timeline_event

Sample = Dict[str, float]  # series name -> current value, e.g. "error_rate", "latency_p95", "svc_error:cart"


class MetricsClient(Protocol):
    def fetch(self) -> Sample: ...


class PrometheusClient:
    """Instant queries against METRICS_URL/api/v1/query. Queries come from config (TODO(confirm) live)."""

    def __init__(self, cfg: Config, timeout: float = 5.0):
        if not cfg.metrics_url:
            raise ValueError("METRICS_URL is not set")
        self.cfg, self.timeout = cfg, timeout

    def _query(self, promql: str) -> List[dict]:
        url = self.cfg.metrics_url.rstrip("/") + "/api/v1/query?" + urllib.parse.urlencode({"query": promql})
        with urllib.request.urlopen(url, timeout=self.timeout) as r:  # noqa: S310 (configured URL, GET only)
            body = json.load(r)
        return body.get("data", {}).get("result", []) if body.get("status") == "success" else []

    @staticmethod
    def _val(item: dict) -> Optional[float]:
        try:
            v = float(item["value"][1])
        except (KeyError, IndexError, ValueError, TypeError):
            return None
        return v if v == v else None  # drop NaN

    def fetch(self) -> Sample:
        out: Sample = {}
        for name, q in (("error_rate", self.cfg.error_rate_query), ("latency_p95", self.cfg.latency_p95_query)):
            if q:
                vals = [v for v in map(self._val, self._query(q)) if v is not None]
                if vals:
                    out[name] = max(vals)
        if self.cfg.per_service_error_query:
            for item in self._query(self.cfg.per_service_error_query):
                svc = item.get("metric", {}).get("service_name")
                v = self._val(item)
                if svc and v is not None:
                    out[f"svc_error:{svc}"] = v
        return out


class Detector:
    def __init__(
        self,
        client: MetricsClient,
        cfg: Optional[Config] = None,
        on_incident: Optional[Callable[[Incident], None]] = None,
        clock: Callable[[], float] = time.time,
    ):
        self.client, self.cfg, self.clock = client, cfg or load_config(), clock
        self.on_incident = on_incident
        self.baselines: Dict[str, Deque[float]] = {}
        self.streak: Dict[str, int] = {}
        self.open: Dict[str, Incident] = {}  # symptom -> incident
        self.last_closed: Dict[str, float] = {}  # symptom -> time it was closed (cooldown start)
        self.last_opened: Dict[str, float] = {}

    def threshold(self, series: str) -> Optional[float]:
        base = self.baselines.get(series)
        if not base or len(base) < self.cfg.min_baseline:
            return None
        med = statistics.median(base)
        mad = statistics.median(abs(x - med) for x in base) * 1.4826
        spread = max(mad, self.cfg.abs_floor, 0.1 * abs(med))
        return med + self.cfg.sigma_k * spread

    def poll_once(self) -> List[Incident]:
        now, opened = self.clock(), []
        try:
            sample = self.client.fetch()
        except Exception:  # metrics outage must not crash the loop or fake an incident
            return opened
        for series, value in sample.items():
            base = self.baselines.setdefault(series, deque(maxlen=self.cfg.baseline_window))
            limit = self.threshold(series)
            if limit is not None and value > limit:
                self.streak[series] = self.streak.get(series, 0) + 1  # breaching points stay out of the baseline
                if self.streak[series] >= self.cfg.breach_polls and self._may_open(series, now):
                    opened.append(self._open(series, value, limit, now))
            else:
                self.streak[series] = 0
                base.append(value)
        return opened

    def _may_open(self, symptom: str, now: float) -> bool:
        if symptom in self.open:
            return False
        since = self.last_closed.get(symptom, self.last_opened.get(symptom))
        return since is None or now - since >= self.cfg.cooldown_s

    def _open(self, symptom: str, value: float, limit: float, now: float) -> Incident:
        inc = Incident(id=uuid.uuid4().hex[:8], start_time=now, symptom=symptom, status="detecting")
        inc.timeline.append(make_timeline_event(
            f"{symptom} breached: {value:.4g} > threshold {limit:.4g} for {self.cfg.breach_polls} polls", at=now))
        self.open[symptom] = inc
        self.last_opened[symptom] = now
        if self.on_incident:
            inc.status = "investigating"
            inc.timeline.append(make_timeline_event("handed off to investigator", at=now))
            self.on_incident(inc)
        return inc

    def close(self, incident: Incident, status: str = "resolved") -> None:
        """Called when an incident ends (resolved/escalated); starts the cooldown for that symptom."""
        incident.status = status  # type: ignore[assignment]
        if self.open.get(incident.symptom) is incident:
            del self.open[incident.symptom]
            self.last_closed[incident.symptom] = self.clock()
            self.streak[incident.symptom] = 0


def default_handoff(incident: Incident) -> None:
    """Hand off to the investigator; tolerate it not being implemented yet."""
    from agent import investigator

    try:
        investigator.investigate(incident)
    except NotImplementedError:
        print(f"[detector] investigator not implemented yet; incident {incident.id} left open")


class MockClient:
    """Healthy series with mild noise, then a sustained spike. For demos without the live system."""

    def __init__(self, healthy_polls: int = 20):
        self.n, self.healthy = 0, healthy_polls

    def fetch(self) -> Sample:
        self.n += 1
        noise = (self.n % 3) * 0.002
        if self.n > self.healthy:
            return {"error_rate": 0.25, "latency_p95": 900.0, "svc_error:checkout": 0.4}
        return {"error_rate": 0.01 + noise, "latency_p95": 120.0 + self.n % 5, "svc_error:checkout": 0.005 + noise}


def run(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m agent.detector")
    ap.add_argument("--mock", action="store_true", help="synthetic data, no live system")
    ap.add_argument("--dry-run", action="store_true", help="detect and print only; no investigator hand-off")
    ap.add_argument("--iterations", type=int, default=0, help="stop after N polls (0 = forever; mock defaults to 40)")
    a = ap.parse_args(argv)
    cfg = load_config()
    if a.mock:
        client, cfg.poll_interval_s = MockClient(), 0.0
    else:
        client = PrometheusClient(cfg)
    det = Detector(client, cfg, on_incident=None if (a.dry_run or a.mock) else default_handoff)
    limit = a.iterations or (40 if a.mock else 0)
    n = 0
    while limit == 0 or n < limit:
        for inc in det.poll_once():
            print(f"[detector] INCIDENT {inc.id} symptom={inc.symptom} status={inc.status}")
        n += 1
        time.sleep(cfg.poll_interval_s)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
