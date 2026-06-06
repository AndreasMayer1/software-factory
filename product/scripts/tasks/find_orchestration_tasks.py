#!/usr/bin/env python3
"""Detect orchestration tasks by structural signature.

An orchestration task is identified by TWO frontmatter conditions:
  1. target_release is set (non-empty string)
  2. scope_description starts with "Orchestration:" (case-sensitive, colon required)

This avoids grep on content and path-name assumptions.

Usage:
    python3 scripts/find_orchestration_tasks.py [--status STATUS] [--release VERSION] [--json]

Exit codes:
    0  found >=1 orchestration task matching filters (always 0 with --json)
    1  no orchestration tasks found matching filters (non-JSON mode only)
    3  argument error

Output:
    Default: prints one '<TASK-ID>\t<PATH>' line per match to stdout. --json: emits a single JSON array with one object per match.
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

# Make scripts/util importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from io import StringIO

from ruamel.yaml import YAML
from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    _split_frontmatter,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# YAML parsing — delegates to scripts/util/yaml_frontmatter (REQ-PROC-051 AC-08)
# ---------------------------------------------------------------------------

def _parse_frontmatter(content: str) -> Optional[dict[str, Any]]:
    """Extract and parse YAML frontmatter from markdown content."""
    if content.startswith("﻿"):
        content = content[1:]
    raw_yaml, _body = _split_frontmatter(content)
    if not raw_yaml.strip():
        return None
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True
    try:
        result = yaml.load(StringIO(raw_yaml))
    except Exception:
        return None
    if result is None or not isinstance(result, dict) or len(result) == 0:
        return None
    return dict(result)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _find_files(root: Path, name: str) -> list[Path]:
    """Locate files by name using native find (faster than rglob on WSL2)."""
    try:
        result = subprocess.run(
            ["find", str(root), "-name", name],
            capture_output=True, text=True,
        )
        return [Path(p) for p in result.stdout.splitlines() if p.strip()]
    except FileNotFoundError:
        return list(root.rglob(name))


def is_orchestration_task(meta: dict[str, Any]) -> bool:
    """Return True if frontmatter matches the orchestration task signature.

    Both conditions must hold:
    1. target_release is a non-empty string
    2. scope_description starts with 'Orchestration:' (case-sensitive)
    """
    target_release = str(meta.get("target_release", "") or "").strip()
    scope_desc = str(meta.get("scope_description", "") or "").strip()
    return bool(target_release) and scope_desc.startswith("Orchestration:")


def find_orchestration_tasks(
    status: Optional[str] = None,
    release: Optional[str] = None,
    root: Optional[Path] = None,
) -> list[dict[str, Any]]:
    """Return list of orchestration task dicts matching filters.

    Args:
        status: filter by status value, or None/'any' for all statuses
        release: filter by target_release exact match, or None for all
        root: requirements_tasks root directory (defaults to PROJECT_ROOT/requirements_tasks)
    """
    if root is None:
        root = PROJECT_ROOT / "requirements_tasks"

    results: list[dict[str, Any]] = []

    for goal_file in _find_files(root, "goal.md"):
        try:
            content = goal_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"WARNING: cannot read {goal_file}: {e}", file=sys.stderr)
            continue

        meta = _parse_frontmatter(content)
        if not meta:
            continue

        if not is_orchestration_task(meta):
            continue

        task_status = str(meta.get("status", "unknown")).lower().strip()
        task_release = str(meta.get("target_release", "") or "").strip()
        task_id = str(meta.get("task_id", "")).strip()
        scope_desc = str(meta.get("scope_description", "") or "").strip()

        # Apply status filter
        if status and status.lower() != "any":
            filter_statuses = [s.strip().lower() for s in status.split(",")]
            if task_status not in filter_statuses:
                continue

        # Apply release filter
        if release and task_release != release:
            continue

        results.append({
            "task_id": task_id,
            "status": task_status,
            "target_release": task_release,
            "scope_description": scope_desc,
            "path": str(goal_file),
        })

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect orchestration tasks by structural signature"
    )
    parser.add_argument(
        "--status",
        default="any",
        help="Filter by status: pending, in_progress, completed, any (default: any). "
             "Comma-separated for multiple.",
    )
    parser.add_argument("--release", metavar="VERSION", help="Filter by target_release value")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable lines")
    args = parser.parse_args()

    tasks = find_orchestration_tasks(
        status=args.status,
        release=args.release,
    )

    if args.json:
        print(json.dumps(tasks, indent=2))
        sys.exit(0)

    # Human-readable output — exit 0 regardless of match count
    # (callers that need boolean check should use --json and inspect array length)
    for task in tasks:
        print(f"{task['task_id']} {task['status']}  target_release={task['target_release']}")
        print(f"  path: {task['path']}")

    sys.exit(0)


if __name__ == "__main__":
    main()
