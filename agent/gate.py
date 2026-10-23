"""Human approval gate, kill switch and dry-run. Approval binds to payload_hash. Owner: P5."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def request_approval(proposal: ActionProposal) -> bool:
    """TODO(P5): implement."""
    raise NotImplementedError


def kill_switch_engaged() -> bool:
    """TODO(P5): implement."""
    raise NotImplementedError


