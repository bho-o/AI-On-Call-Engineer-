"""ONLY module allowed to call the Action API, and only after gate approval. Owner: P5."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def execute(proposal: ActionProposal, dry_run: bool = True) -> Dict[str, Any]:
    """TODO(P5): implement."""
    raise NotImplementedError


