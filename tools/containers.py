<<<<<<< HEAD

"""Read-only Docker container health inspection."""

import os
import docker
from docker.errors import DockerException
from dotenv import load_dotenv

load_dotenv()

TIMEOUT = int(os.getenv("TOOL_TIMEOUT_SECONDS", "8"))


def list_container_health() -> dict:
    client = None

    try:
        client = docker.from_env(timeout=TIMEOUT)
        containers = client.containers.list(all=True)

        records = []

        for container in containers:
            attrs = container.attrs
            state = attrs.get("State", {})
            health = state.get("Health", {})

            records.append({
                "id": container.short_id,
                "name": container.name,
                "image": (
                    attrs.get("Config", {}).get("Image")
                ),
                "status": state.get("Status", "unknown"),
                "running": state.get("Running", False),
                "health": health.get("Status", "not_configured"),
                "restart_count": attrs.get("RestartCount", 0),
                "started_at": state.get("StartedAt"),
                "exit_code": state.get("ExitCode"),
            })

        evidence_refs = [
            f"docker:container:{record['id']}"
            for record in records
        ]

        return {
            "tool": "containers",
            "status": "success",
            "data": {
                "count": len(records),
                "containers": records,
            },
            "evidence_refs": evidence_refs,
            "error": None,
        }

    except DockerException as exc:
        return {
            "tool": "containers",
            "status": "error",
            "data": None,
            "evidence_refs": [],
            "error": str(exc),
        }

    finally:
        if client is not None:
            client.close()
=======
"""Read-only container status tool. No state-changing calls. Owner: P2."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.models import *  # noqa: F401,F403  shared types

def container_status(service: str) -> ToolResult:
    """TODO(P2): implement."""
    raise NotImplementedError


>>>>>>> origin/main
