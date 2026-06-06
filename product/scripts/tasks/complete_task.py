#!/usr/bin/env python3
# Run with: python3 scripts/tasks/complete_task.py <task_path>
"""Mark a task folder as completed by renaming it with '(completed)' suffix.

Refuses to rename if the task's goal.md still has unchecked acceptance criteria
('- [ ]' lines under '## Acceptance Criteria'). Pass --force to override
(intended only for tasks that legitimately have no AC checklist).

Output:
    Prints the renamed folder path (new name with '(completed)' suffix) to stdout. Refusals and errors go to stderr.
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import os
import re
import sys
from pathlib import Path


def find_unchecked_acs(goal_md_path: Path) -> list[str]:
    """Return the unchecked AC lines under '## Acceptance Criteria' (empty if none)."""
    try:
        content = goal_md_path.read_text(encoding="utf-8")
    except OSError:
        return []

    # Why: orchestration tasks have been completed in the past with all ACs still
    # unchecked, silently dropping chain-perpetuation steps. Block this at the
    # rename gate so task-complete can never produce a half-finished task.
    section = re.search(
        r"^##\s+Acceptance Criteria\s*\n(.*?)(?=\n##\s|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if not section:
        return []

    return [line for line in section.group(1).splitlines() if re.match(r"^\s*-\s*\[\s\]", line)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mark a task folder as completed by renaming it with '(completed)' suffix."
    )
    parser.add_argument("task_path", help="Path to the task folder")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip the unchecked-AC guard (use only when the task has no AC checklist).",
    )
    args = parser.parse_args()

    task_path = args.task_path

    if not os.path.isdir(task_path):
        print(f"Error: The specified path '{task_path}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    task_name = os.path.basename(task_path.rstrip("/\\"))

    if "completed" in task_name:
        print("Task is already marked as completed.")
        sys.exit(0)

    if not args.force:
        goal_md = Path(task_path) / "goal.md"
        unchecked = find_unchecked_acs(goal_md)
        if unchecked:
            print(
                f"Error: Task '{task_name}' has {len(unchecked)} unchecked acceptance criteria.\n"
                f"Check each one off (`- [x]`) before completing, or pass --force to override.",
                file=sys.stderr,
            )
            for line in unchecked:
                print(f"  {line.strip()}", file=sys.stderr)
            sys.exit(2)

    parent_path = os.path.dirname(os.path.abspath(task_path))
    new_task_name = task_name + " (completed)"
    new_task_path = os.path.join(parent_path, new_task_name)

    try:
        os.rename(task_path, new_task_path)
        print(f"Task '{task_name}' has been marked as completed.")
    except OSError as e:
        print(f"Error: Failed to mark task '{task_name}' as completed. {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
