#!/usr/bin/env python3
"""
Check whether requirements authoring is complete enough to allow impl task creation.

Exit 0 (ready):
  - At least one task with writes_requirements: true has status: completed
  - No task with writes_requirements: true has status: pending or in_progress

Exit 1 (not ready): prints a human-readable reason.

Known limitation (TODO): Requirements authored before the `writes_requirements` flag was
introduced will not have any associated writes_requirements:true task, causing this script
to exit 1 with "No requirements-authoring tasks found". These grandfathered requirements
would need either a retroactive completed task or an explicit bypass mechanism.

Usage:
  python3 scripts/check_requirements_ready.py

Output:
    Prints a per-requirement readiness section (status, blockers) to stdout, ending with a summary line.
"""

# tier: B  # requirements-tooling script; imported only via CLI

import glob
import os
import sys
from pathlib import Path

# Make scripts/ importable when invoked directly as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    FrontmatterError,
    read_frontmatter,
)


def find_goal_files(base: str) -> list[str]:
    return glob.glob(os.path.join(base, "**", "goal.md"), recursive=True)


def parse_frontmatter_fields(path: str, fields: list[str]) -> dict[str, str]:
    """Extract specific YAML frontmatter fields as strings.

    Backwards-compatibility: returns values stringified (yaml booleans → "true"/"false")
    so call-sites that compare against literal "true" keep working. Missing fields and
    unreadable files yield an empty dict.
    """
    try:
        doc = read_frontmatter(Path(path))
    except (OSError, FrontmatterError):
        return {}
    if not doc.has_frontmatter:
        return {}

    result: dict[str, str] = {}
    for field in fields:
        if field in doc.metadata:
            value = doc.metadata[field]
            # Preserve historical string-coercion: booleans → "true"/"false",
            # None → "", everything else → str(value).
            if value is True:
                result[field] = "true"
            elif value is False:
                result[field] = "false"
            elif value is None:
                result[field] = ""
            else:
                result[field] = str(value)
    return result


def main() -> int:
    base = os.path.join(os.path.dirname(__file__), "..", "requirements_tasks")
    base = os.path.normpath(base)

    goal_files = find_goal_files(base)

    completed = []
    blocking = []

    for path in goal_files:
        fields = parse_frontmatter_fields(path, ["writes_requirements", "status"])
        if fields.get("writes_requirements") != "true":
            continue
        status = fields.get("status", "")
        if status == "completed":
            completed.append(path)
        elif status in ("pending", "in_progress"):
            blocking.append(path)

    if not completed and not blocking:
        print(
            "NOT READY: No requirements-authoring tasks found — "
            "requirements may not have been formally authored yet."
        )
        return 1

    if blocking:
        print(
            f"NOT READY: {len(blocking)} requirements-authoring task(s) still pending/in_progress:"
        )
        for p in blocking:
            print(f"  {p}")
        return 1

    if not completed:
        print(
            "NOT READY: No completed requirements-authoring tasks found — "
            "requirements authoring has not been confirmed complete."
        )
        return 1

    print(
        f"READY: {len(completed)} requirements-authoring task(s) completed, "
        "none pending or in_progress."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
