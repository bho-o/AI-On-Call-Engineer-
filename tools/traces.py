<<<<<<< HEAD

"""Read-only Jaeger distributed tracing tool."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("JAEGER_URL", "http://localhost:16686").rstrip("/")
TIMEOUT = int(os.getenv("TOOL_TIMEOUT_SECONDS", "8"))


def search_traces(
    service: str,
    lookback: str = "1h",
    limit: int = 20,
) -> dict:
    if not isinstance(service, str) or not service.strip():
        return {
            "tool": "traces",
            "status": "error",
            "data": None,
            "evidence_refs": [],
            "error": "Service name is required.",
        }

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        return {
            "tool": "traces",
            "status": "error",
            "data": None,
            "evidence_refs": [],
            "error": "Limit must be a positive integer.",
        }

    try:
        response = requests.get(
            f"{BASE_URL}/api/traces",
            params={
                "service": service,
                "lookback": lookback,
                "limit": limit,
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        traces = payload.get("data", [])
        evidence_refs = []

        for trace in traces:
            trace_id = trace.get("traceID")
            if trace_id:
                evidence_refs.append(f"jaeger:trace:{trace_id}")

        return {
            "tool": "traces",
            "status": "success",
            "data": {
                "service": service,
                "lookback": lookback,
                "traces": traces,
                "count": len(traces),
            },
            "evidence_refs": evidence_refs,
            "error": None,
        }

    except (requests.RequestException, ValueError) as exc:
        return {
            "tool": "traces",
            "status": "error",
            "data": None,
            "evidence_refs": [],
            "error": str(exc),
        }
=======
"""Read-only traces tool (Jaeger). Owner: P2."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def search_traces(service: str, lookback: str = '15m') -> ToolResult:
    """TODO(P2): implement."""
    raise NotImplementedError


>>>>>>> origin/main
