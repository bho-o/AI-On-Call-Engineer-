"""Read-only metrics tool (Prometheus). Owner: P2."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def query_metric(query: str, service: Optional[str] = None) -> ToolResult:
    """TODO(P2): implement."""
    raise NotImplementedError


