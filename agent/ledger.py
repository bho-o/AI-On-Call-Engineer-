"""Evidence ledger: every tool call is recorded with an evidence_id. Owner: P4."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def record(tool: str, arguments: Dict[str, Any], summary: str, raw: Any = None) -> LedgerEntry:
    """TODO(P4): implement."""
    raise NotImplementedError


def get(evidence_id: str) -> Optional[LedgerEntry]:
    """TODO(P4): implement."""
    raise NotImplementedError


def all_entries() -> List[LedgerEntry]:
    """TODO(P4): implement."""
    raise NotImplementedError


