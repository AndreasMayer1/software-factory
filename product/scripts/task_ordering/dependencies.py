"""Blocked-task detection logic."""

# tier: B  # reusable library; imported by ranker and package __init__

from typing import Any


def is_blocked(task: dict[str, Any], completed_ids: set[str], known_ids: set[str]) -> bool:
    if task["status"] == "blocked" or bool(task.get("awaiting")):
        return True
    for dep_id in task.get("after", []):
        if dep_id and dep_id in known_ids and dep_id not in completed_ids:
            return True
    return False
