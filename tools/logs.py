<<<<<<< HEAD

"""Read-only log search tool for an OpenSearch-compatible backend."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OPENSEARCH_URL", "http://localhost:9200").rstrip("/")
INDEX = os.getenv("OPENSEARCH_INDEX", "otel-logs-*")
TIMEOUT = int(os.getenv("TOOL_TIMEOUT_SECONDS", "8"))


def search_logs(
    service: str,
    limit: int = 20,
    search_text: str | None = None,
) -> dict:
    if not isinstance(service, str) or not service.strip():
        return {
            "tool": "logs",
            "status": "error",
            "data": None,
            "evidence_refs": [],
            "error": "Service name is required.",
        }

    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        return {
            "tool": "logs",
            "status": "error",
            "data": None,
            "evidence_refs": [],
            "error": "Limit must be between 1 and 100.",
        }

    must = [
        {"match": {"serviceName": service}}
    ]

    if search_text and search_text.strip():
        must.append({
            "query_string": {
                "query": search_text.strip(),
                "default_operator": "AND",
            }
        })

    body = {
        "size": limit,
        "sort": [{"@timestamp": {"order": "desc", "unmapped_type": "date"}}],
        "query": {"bool": {"must": must}},
    }

    try:
        response = requests.post(
            f"{BASE_URL}/{INDEX}/_search",
            json=body,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        hits = payload.get("hits", {}).get("hits", [])
        records = []
        evidence_refs = []

        for hit in hits:
            source = hit.get("_source", {})
            record_id = hit.get("_id")

            records.append({
                "id": record_id,
                "index": hit.get("_index"),
                "timestamp": source.get("@timestamp"),
                "service": source.get("serviceName"),
                "message": (
                    source.get("body")
                    or source.get("message")
                    or source.get("log")
                ),
                "fields": source,
            })

            if record_id and hit.get("_index"):
                evidence_refs.append(
                    f"opensearch:{hit['_index']}:{record_id}"
                )

        return {
            "tool": "logs",
            "status": "success",
            "data": {
                "service": service,
                "count": len(records),
                "records": records,
            },
            "evidence_refs": evidence_refs,
            "error": None,
        }

    except (requests.RequestException, ValueError) as exc:
        return {
            "tool": "logs",
            "status": "error",
            "data": None,
            "evidence_refs": [],
            "error": str(exc),
        }
=======
"""Read-only logs tool (OpenSearch). Owner: P2."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def search_logs(service: str, query: str = '', lookback: str = '15m') -> ToolResult:
    """TODO(P2): implement."""
    raise NotImplementedError


>>>>>>> origin/main
