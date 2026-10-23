"""Writes the incident report to reports/. Owner: P5."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def write_report(incident: Incident, diagnosis: Optional[Diagnosis], timeline: List[TimelineEvent]) -> str:
    """TODO(P5): implement."""
    raise NotImplementedError


