"""Guards tool output (size caps, secret redaction, prompt-injection hygiene). Owner: P4."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def sanitize(result: ToolResult) -> ToolResult:
    """TODO(P4): implement."""
    raise NotImplementedError


