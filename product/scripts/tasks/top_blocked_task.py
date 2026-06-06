#!/usr/bin/env python3
# ruff: noqa: RUF002, RUF100
# RUF002: docstring uses the MULTIPLICATION SIGN intentionally in the priority formula
# "urgency x 10 + impact" rendered for human readability.
# RUF100: false-positive on file-level noqa for codes ruff cannot introspect into the file body.
"""
Find blocked tasks sorted by priority, or look up a specific task by ID.

A task is "blocked" when awaiting is non-empty OR status == 'blocked'.
Priority score = (urgency × 10) + impact.

Usage:
    python scripts/top_blocked_task.py                     # highest-priority blocked task
    python scripts/top_blocked_task.py --all               # all blocked tasks, priority order
    python scripts/top_blocked_task.py --task TASK-ID      # specific task (must be blocked)
    python scripts/top_blocked_task.py --count-older-than 7  # count blocked tasks older than N days

Output (stdout, --all separates blocks with ---):
    TASK_ID: <id>
    PATH: <path/to/goal.md>
    NAME: <name>
    AWAITING: <comma-separated awaiting items, or empty>
    AWAITING_NOTE: <note text, or empty>

--count-older-than prints a single integer and always exits 0.

Exit codes:
    0  task(s) found and printed
    1  no blocked tasks found (or specified task not found / not blocked)

Output:
    Prints one '<TASK-ID>\t<PATH>\t<NAME>\t<AWAITING>\t<NOTE>' line per blocked task to stdout, sorted by priority. --count-older-than prints a single integer.
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import re
import subprocess
import sys
from datetime import date
from io import StringIO
from pathlib import Path
from typing import Any, Optional, cast

from ruamel.yaml import YAML

# Make scripts/util importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    _split_frontmatter,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent
TERMINAL_STATUSES = {"completed", "cancelled", "superseded"}


# ---------------------------------------------------------------------------
# YAML parsing \u2014 delegates to scripts/util/yaml_frontmatter (REQ-PROC-051 AC-08)
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> Optional[dict[str, Any]]:
    if content.startswith("\ufeff"):
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
# Loading
# ---------------------------------------------------------------------------

def _task_name(goal_file: Path) -> str:
    folder = goal_file.parent.name
    name = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", folder)
    name = re.sub(r"^(impl|explore|analyze|fix|bugfix|create|update|define|review)_", "", name, flags=re.IGNORECASE)
    for suffix in ("_(completed)", "_(superseded)", "_(cancelled)", "_(paused)"):
        name = name.replace(suffix, "")
    return name.replace("_", " ").strip()


def _find_goal_files(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["find", str(root), "-name", "goal.md"],
            capture_output=True, text=True
        )
        return [Path(p) for p in result.stdout.splitlines() if p.strip()]
    except FileNotFoundError:
        return list(root.rglob("goal.md"))


def load_blocked_tasks() -> list[dict[str, Any]]:
    """Load all tasks that are externally blocked (awaiting non-empty or status==blocked)."""
    tasks = []
    root = PROJECT_ROOT / "requirements_tasks"
    for goal_file in _find_goal_files(root):
        try:
            content = goal_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = goal_file.read_text(encoding="latin-1")
            except Exception:
                continue
        except Exception:
            continue

        meta = parse_frontmatter(content)
        if not meta or "task_id" not in meta:
            continue

        status = str(meta.get("status", "unknown")).lower()
        if status in TERMINAL_STATUSES:
            continue

        awaiting = meta.get("awaiting", [])
        if not isinstance(awaiting, list):
            awaiting = [awaiting] if awaiting else []
        awaiting = [b for b in awaiting if b]

        if not awaiting and status != "blocked":
            continue

        awaiting_note = str(meta.get("awaiting_note", "") or "")

        tasks.append({
            "task_id": str(meta.get("task_id", "")),
            "path": str(goal_file),
            "name": _task_name(goal_file),
            "urgency": int(meta.get("urgency", 0) or 0),
            "impact": int(meta.get("impact", 0) or 0),
            "awaiting": awaiting,
            "awaiting_note": awaiting_note,
            "status": status,
            "created": str(meta.get("created", "") or ""),
        })

    return tasks


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _priority_score(task: dict[str, Any]) -> int:
    return cast("int", (task["urgency"] * 10) + task["impact"])


def _task_age_days(task: dict[str, Any]) -> Optional[int]:
    """Return task age in days, or None if created date is unparseable."""
    created_str = task.get("created", "")
    try:
        created_date = date.fromisoformat(str(created_str))
        return (date.today() - created_date).days
    except (ValueError, TypeError):
        return None


def _print_task(task: dict[str, Any]) -> None:
    awaiting_str = ", ".join(task["awaiting"]) if task["awaiting"] else ""
    print(f"TASK_ID: {task['task_id']}")
    print(f"PATH: {task['path']}")
    print(f"NAME: {task['name']}")
    print(f"AWAITING: {awaiting_str}")
    print(f"AWAITING_NOTE: {task['awaiting_note']}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Find blocked tasks sorted by priority.")
    parser.add_argument("--task", metavar="TASK-ID", help="Look up a specific task by ID")
    parser.add_argument("--all", action="store_true", help="Print all blocked tasks, priority order")
    parser.add_argument("--count-older-than", metavar="DAYS", type=int,
                        help="Print count of blocked tasks older than N days (always exits 0)")
    args = parser.parse_args()

    blocked = load_blocked_tasks()

    # --count-older-than: used by hooks, always exits 0
    if args.count_older_than is not None:
        cutoff = args.count_older_than
        count = sum(1 for t in blocked if (_task_age_days(t) or 0) >= cutoff)
        print(count)
        return

    if args.task:
        matches = [t for t in blocked if t["task_id"] == args.task]
        if not matches:
            # Task might exist but not be blocked — check all tasks for a better error
            all_root = PROJECT_ROOT / "requirements_tasks"
            all_goal_files = _find_goal_files(all_root)
            found_not_blocked = False
            for goal_file in all_goal_files:
                try:
                    content = goal_file.read_text(encoding="utf-8")
                    meta = parse_frontmatter(content)
                    if meta and str(meta.get("task_id", "")) == args.task:
                        found_not_blocked = True
                        break
                except Exception:
                    continue
            if found_not_blocked:
                print(f"Error: {args.task} exists but is not blocked (awaiting is empty and status != blocked).", file=sys.stderr)
            else:
                print(f"Error: {args.task} not found.", file=sys.stderr)
            sys.exit(1)
        _print_task(matches[0])
        return

    if not blocked:
        print("No blocked tasks found.", file=sys.stderr)
        sys.exit(1)

    sorted_blocked = sorted(blocked, key=_priority_score, reverse=True)

    if args.all:
        for i, task in enumerate(sorted_blocked):
            if i > 0:
                print("---")
            _print_task(task)
        return

    _print_task(sorted_blocked[0])


if __name__ == "__main__":
    main()
