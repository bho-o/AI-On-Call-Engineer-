<<<<<<< HEAD

"""Read-only investigation and remediation safety checks."""

from typing import Any


def validate_evidence(evidence_refs: Any) -> dict:
    """Check that evidence references are present and well-formed."""

    if not isinstance(evidence_refs, list) or not evidence_refs:
        return {
            "allowed": False,
            "reason": "At least one evidence reference is required.",
        }

    if not all(
        isinstance(ref, str) and ref.strip()
        for ref in evidence_refs
    ):
        return {
            "allowed": False,
            "reason": "Evidence references must be non-empty strings.",
        }

    return {
        "allowed": True,
        "reason": "Evidence reference format is valid.",
    }


def validate_diagnosis_inputs(inputs: Any) -> dict:
    """Reject feature-flag configuration as diagnosis input."""

    if not isinstance(inputs, dict):
        return {
            "allowed": False,
            "reason": "Diagnosis inputs must be a dictionary.",
        }

    forbidden_keys = {
        "feature_flag",
        "feature_flags",
        "feature_flag_config",
        "featureflag",
        "featureflag_config",
    }

    found = []

    def scan(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = str(key).lower().replace("-", "_")
                current = f"{path}.{key}" if path else str(key)

                if (
                    normalized in forbidden_keys
                    or "feature_flag_config" in normalized
                ):
                    found.append(current)

                scan(child, current)

        elif isinstance(value, list):
            for index, child in enumerate(value):
                scan(child, f"{path}[{index}]")

    scan(inputs)

    if found:
        return {
            "allowed": False,
            "reason": "Prohibited feature-flag configuration found.",
            "fields": found,
        }

    return {
        "allowed": True,
        "reason": "No prohibited configuration keys detected.",
    }


def validate_action(
    action: str,
    allowed_actions: set[str],
    approved: bool = False,
    kill_switch: bool = False,
) -> dict:
    """Require an allowlisted action and explicit human approval."""

    if kill_switch:
        return {
            "allowed": False,
            "reason": "Kill switch is active.",
        }

    if not isinstance(action, str) or action not in allowed_actions:
        return {
            "allowed": False,
            "reason": "Action is not allowlisted.",
        }

    if not approved:
        return {
            "allowed": False,
            "reason": "Explicit human approval is required.",
        }

    return {
        "allowed": True,
        "reason": "Safety checks passed; execution must still use the official Action API.",
    }
=======
"""Guards tool output (size caps, secret redaction, prompt-injection hygiene). Owner: P4."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def sanitize(result: ToolResult) -> ToolResult:
    """TODO(P4): implement."""
    raise NotImplementedError


>>>>>>> origin/main
