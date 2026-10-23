"""Checks that claims in a diagnosis are backed by ledger evidence. Owner: P4."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def verify_diagnosis(diagnosis: Diagnosis, ledger: List[LedgerEntry]) -> List[str]:
    """TODO(P4): implement."""
    raise NotImplementedError


