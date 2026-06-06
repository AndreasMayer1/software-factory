#!/usr/bin/env python3
"""Append one web-search row to .factory/optimize/history/web_searches.tsv (REQ-PROC-006 IMPL-J).

Executor skills call this CLI (via claude-log) to record each WebSearch or WebFetch
performed during a task session. The file is append-only and never pruned; the
claude-optimize-audit skill consumes it to evaluate web-research heuristics empirically.

CLI:
    python3 scripts/optimize/log_web_search.py \\
        --task-id TASK-FOO-001 \\
        --query "how does X work?" \\
        [--goal-path requirements_tasks/.../goal.md] \\
        [--timestamp 2026-05-28T12:00:00Z]

Output: nothing on success (exit 0); error message to stderr on failure (exit 1).
"""

# tier: B  # invoked by claude-log and executor skills; importable for direct testing

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS_DIR = str(Path(__file__).resolve().parents[1])
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    FrontmatterError,
    read_frontmatter,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TSV_PATH = PROJECT_ROOT / ".factory" / "optimize" / "history" / "web_searches.tsv"
TSV_HEADER = "timestamp\ttask_id\tquery\trecommended_by_optimization_approach\n"

# Timestamps are stored as UTC — machine-to-machine exchange artifact consumed by
# audit scripts; exempt from the OS-local-timezone display rule (monitor_common.py §comment).
_UTC_FMT = "%Y-%m-%dT%H:%M:%SZ"


def read_recommended_flag(goal_path: Path) -> bool:
    """Return optimization_approach.web_research_recommended from goal.md, or False."""
    try:
        doc = read_frontmatter(goal_path)
    except (FrontmatterError, OSError):
        return False
    approach = doc.metadata.get("optimization_approach")
    if not isinstance(approach, dict):
        return False
    return bool(approach.get("web_research_recommended", False))


def append_row(
    tsv_path: Path,
    timestamp: str,
    task_id: str,
    query: str,
    recommended: bool,
) -> None:
    """Append one row to web_searches.tsv, writing the header first if the file is new."""
    needs_header = not tsv_path.exists()
    tsv_path.parent.mkdir(parents=True, exist_ok=True)
    recommended_str = "true" if recommended else "false"
    with tsv_path.open("a", encoding="utf-8") as fh:
        if needs_header:
            fh.write(TSV_HEADER)
        fh.write(f"{timestamp}\t{task_id}\t{query}\t{recommended_str}\n")


def main(argv: list[str] | None = None) -> int:
    """Parse args, read goal.md if provided, and append one row. Returns exit code."""
    parser = argparse.ArgumentParser(
        description="Append one web-search row to .factory/optimize/history/web_searches.tsv."
    )
    parser.add_argument("--task-id", required=True, help="Task ID of the running task")
    parser.add_argument("--query", required=True, help="Search query string")
    parser.add_argument(
        "--goal-path",
        default=None,
        help="Path to goal.md; reads optimization_approach.web_research_recommended",
    )
    parser.add_argument(
        "--timestamp",
        default=None,
        help="ISO-8601 UTC timestamp (default: now)",
    )
    args = parser.parse_args(argv)

    ts = args.timestamp or datetime.now(timezone.utc).strftime(_UTC_FMT)
    goal_path = Path(args.goal_path) if args.goal_path else None
    recommended = read_recommended_flag(goal_path) if goal_path is not None else False

    try:
        append_row(TSV_PATH, ts, args.task_id, args.query, recommended)
    except OSError as exc:
        print(f"log_web_search: failed to write {TSV_PATH}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
