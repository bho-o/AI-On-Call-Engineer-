<<<<<<< HEAD

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090").rstrip("/")
TIMEOUT = int(os.getenv("TOOL_TIMEOUT_SECONDS", "8"))


def query_metrics(query: str) -> dict:
    if not isinstance(query, str) or not query.strip():
        return {
            "tool": "metrics",
            "status": "error",
            "data": None,
            "evidence_refs": [],
            "error": "A non-empty PromQL query is required.",
        }

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/query",
            params={"query": query},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        if payload.get("status") != "success":
            raise ValueError("Prometheus query failed")

        observations = payload.get("data", {}).get("result", [])

        return {
            "tool": "metrics",
            "status": "success",
            "data": {
                "query": query,
                "observations": observations,
            },
            "evidence_refs": [],
            "error": None,
        }

    except (requests.RequestException, ValueError) as exc:
        return {
            "tool": "metrics",
            "status": "error",
            "data": None,
            "evidence_refs": [],
            "error": str(exc),
        }


def check_prometheus() -> dict:
    return query_metrics("up")
=======
"""Read-only metrics tool (Prometheus). Owner: P2."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def query_metric(query: str, service: Optional[str] = None) -> ToolResult:
    """TODO(P2): implement."""
    raise NotImplementedError


>>>>>>> origin/main
