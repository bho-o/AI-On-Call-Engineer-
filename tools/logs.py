"""Read-only logs tool (OpenSearch). Owner: P2."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def search_logs(service: str, query: str = '', lookback: str = '15m') -> ToolResult:
    """TODO(P2): implement."""
    raise NotImplementedError


