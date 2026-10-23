from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal, Optional

IncidentStatus = Literal[
    "detecting", "investigating", "awaiting_approval", "acting", "verifying", "resolved", "escalated"
]
HypothesisStatus = Literal["open", "supported", "rejected"]
Actor = Literal["agent", "human"]


@dataclass
class Incident:
    id: str
    start_time: float  # epoch seconds
    symptom: str
    status: IncidentStatus = "detecting"
    timeline: List["TimelineEvent"] = field(default_factory=list)


@dataclass
class LedgerEntry:
    evidence_id: str
    tool: str
    arguments: Dict[str, Any]
    timestamp: float
    summary: str
    raw_stored_output: Any = None  # TODO(confirm): P4 may swap for a file path/blob ref


@dataclass
class Hypothesis:
    statement: str
    supporting_evidence_ids: List[str] = field(default_factory=list)
    disproving_attempts: List[str] = field(default_factory=list)
    status: HypothesisStatus = "open"


@dataclass
class Diagnosis:
    component: str
    root_cause: str
    confidence: float  # 0..1
    evidence_ids: List[str] = field(default_factory=list)
    alternatives_ruled_out: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)


@dataclass
class ActionProposal:
    # TODO(confirm): action names/parameters must match the organizer's Action API; none are defined yet.
    action: str
    target: str
    parameters: Dict[str, Any]
    reason: str
    expected_effect: str
    rollback: str
    payload_hash: str = ""

    def compute_hash(self) -> str:
        """Stable hash of the action payload so approval binds to exactly what runs."""
        payload = {"action": self.action, "target": self.target, "parameters": self.parameters}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


@dataclass
class TimelineEvent:
    time: float
    actor: Actor
    event: str
    reference_ids: List[str] = field(default_factory=list)


@dataclass
class ToolResult:
    tool: str
    service: Optional[str]
    timestamp: float
    summary: str
    data: Any = None
    provenance: Dict[str, Any] = field(default_factory=dict)  # query, URL (no secrets), window
    truncated: bool = False


def to_dict(obj: Any) -> Dict[str, Any]:
    """Dataclass -> plain dict (JSON-friendly)."""
    return asdict(obj)


def make_timeline_event(
    event: str, actor: Actor = "agent", reference_ids: Optional[List[str]] = None, at: Optional[float] = None
) -> TimelineEvent:
    return TimelineEvent(time=time.time() if at is None else at, actor=actor, event=event, reference_ids=reference_ids or [])


@dataclass
class Config:
    """Env-only config. No hosts or secrets in code. See .env.example."""

    metrics_url: str = ""
    llm_api_key: str = ""
    poll_interval_s: float = 10.0
    baseline_window: int = 30
    breach_polls: int = 3
    cooldown_s: float = 300.0
    sigma_k: float = 4.0  # breach = value > median + k * spread
    abs_floor: float = 0.01  # minimum spread so flat baselines don't trigger on noise
    min_baseline: int = 10  # polls needed before alerting
    error_rate_query: str = ""
    latency_p95_query: str = ""
    per_service_error_query: str = ""

    def __repr__(self) -> str:  # never leak the key into logs
        return f"Config(metrics_url={self.metrics_url!r}, llm_api_key={'***' if self.llm_api_key else ''!r}, ...)"


def load_config(env: Optional[Dict[str, str]] = None) -> Config:
    e = os.environ if env is None else env
    d = Config()
    return Config(
        metrics_url=e.get("METRICS_URL", d.metrics_url),
        llm_api_key=e.get("LLM_API_KEY", d.llm_api_key),
        poll_interval_s=float(e.get("POLL_INTERVAL_S", d.poll_interval_s)),
        baseline_window=int(e.get("BASELINE_WINDOW", d.baseline_window)),
        breach_polls=int(e.get("BREACH_POLLS", d.breach_polls)),
        cooldown_s=float(e.get("COOLDOWN_S", d.cooldown_s)),
        sigma_k=float(e.get("SIGMA_K", d.sigma_k)),
        abs_floor=float(e.get("ABS_FLOOR", d.abs_floor)),
        min_baseline=int(e.get("MIN_BASELINE", d.min_baseline)),
        error_rate_query=e.get("ERROR_RATE_QUERY", d.error_rate_query),
        latency_p95_query=e.get("LATENCY_P95_QUERY", d.latency_p95_query),
        per_service_error_query=e.get("PER_SERVICE_ERROR_QUERY", d.per_service_error_query),
    )
