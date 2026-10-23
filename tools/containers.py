"""Read-only container status tool. No state-changing calls. Owner: P2."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def container_status(service: str) -> ToolResult:
    """TODO(P2): implement."""
    raise NotImplementedError


