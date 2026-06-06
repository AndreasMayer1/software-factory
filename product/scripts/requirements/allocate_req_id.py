#!/usr/bin/env python3
"""
Atomically allocate the next requirement ID under a parent requirement.

Prints the allocated REQ-ID to stdout (e.g. REQ-FUNC-007-06 or REQ-FUNC-022).
Uses the same exclusive file lock as allocate_task_id.py so that
REQ-ID and TASK-ID allocations are totally ordered — no interleaving.

Usage:
    # Allocate a new feature under an epic:
    python3 scripts/allocate_req_id.py --parent-id REQ-FUNC-007 \
        --parent-path requirements_tasks/functional/shared/epic_data_transfer

    # Allocate a new epic under a category:
    python3 scripts/allocate_req_id.py --parent-id REQ-FUNC \
        --parent-path requirements_tasks/functional/client

How it works:
  Inside the lock the script creates a .reserve-REQ-FUNC-007-06 marker file
  in the parent directory before releasing the lock. This marker persists
  permanently — it is the reservation. callers count both real child
  requirement folders (those containing requirements.md) and reserve markers,
  so a slow or resumed session never collides with a concurrent one.
  Gaps in IDs caused by unredeemed reservations are acceptable.

  The caller (requ-explore skill) deletes the .reserve-* file after
  writing requirements.md with the pre-allocated id: field.

Why the same lock as allocate_task_id.py:
  A new_needed explore task allocates a REQ-ID and then immediately a TASK-ID
  derived from it. Using the same lock serialises both allocations atomically,
  preventing a second session from grabbing the same REQ-ID in the window
  between the two script calls.

Output:
    Prints the newly allocated REQ-ID to stdout. Errors and lock-contention diagnostics go to stderr.
"""

# tier: C  # one-shot CLI requirements tool; no in-tree Python imports

import argparse
import fcntl
import glob
import os
import re
import sys
from pathlib import Path

LOCK_FILE = "requirements_tasks/_meta/.task_id_lock"
REGISTRY_FILE = "requirements_tasks/_meta/id_registry.md"
MAX_ITERATIONS = 100
# Accepts both epic parents (REQ-FUNC) and feature parents (REQ-FUNC-007)
PARENT_ID_PATTERN = re.compile(r"^REQ-[A-Z]+(-\d+)*$")


def _collect_goal_md_ids(requirements_tasks_dir: Path, parent_id: str) -> set[str]:
    """Scan goal.md files for parent_requirement: entries matching the parent_id prefix.

    Explore tasks pre-allocate a requirement ID by writing it into goal.md as
    parent_requirement: REQ-PROC-NNN before the requirements.md is created. Without
    this scan those IDs appear as gaps and get handed out again.
    """
    pattern = re.compile(
        r"^parent_requirement:\s*(" + re.escape(parent_id) + r"-\d+)\s*$",
        re.MULTILINE,
    )
    found: set[str] = set()
    for goal_file in requirements_tasks_dir.rglob("goal.md"):
        try:
            content = goal_file.read_bytes()[:512].decode("utf-8", errors="replace")
            m = pattern.search(content)
            if m:
                found.add(m.group(1))
        except OSError:
            pass
    return found


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Atomically allocate the next requirement ID under a parent."
    )
    parser.add_argument("--parent-id", required=True, help="e.g. REQ-FUNC-007")
    parser.add_argument(
        "--parent-path",
        required=True,
        help="path to the parent requirement folder (e.g. epic folder)",
    )
    args = parser.parse_args()

    parent_id: str = args.parent_id
    parent_path: str = args.parent_path

    if not PARENT_ID_PATTERN.match(parent_id):
        print(
            f"ERROR: --parent-id '{parent_id}' does not match pattern REQ-[A-Z]+-[0-9...]",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.isdir(parent_path):
        print(
            f"ERROR: --parent-path '{parent_path}' does not exist or is not a directory",
            file=sys.stderr,
        )
        sys.exit(1)

    # Ensure lock file exists
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, "a"):
        pass

    with open(LOCK_FILE) as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)

        # Collect IDs from real child requirement folders by reading their frontmatter
        child_req_files = glob.glob(os.path.join(parent_path, "*/requirements.md"))
        frontmatter_id_pattern = re.compile(r"^id:\s*(" + re.escape(parent_id) + r"-\d+)\s*$", re.MULTILINE)
        folder_ids: set[str] = set()
        for p in child_req_files:
            try:
                with open(p) as f:
                    content = f.read(512)  # frontmatter is always near the top
                m = frontmatter_id_pattern.search(content)
                if m:
                    folder_ids.add(m.group(1))
            except OSError:
                pass

        # Collect permanent reserve markers in parent directory
        reserve_prefix = f".reserve-{parent_id}-"
        reserves = [
            f for f in os.listdir(parent_path)
            if f.startswith(reserve_prefix)
        ]
        reserved_ids = {r.removeprefix(".reserve-") for r in reserves}

        # Read registry (may not exist yet)
        registry_content = ""
        if os.path.isfile(REGISTRY_FILE):
            with open(REGISTRY_FILE) as f:
                registry_content = f.read()

        # Collect IDs pre-allocated in goal.md frontmatter (explore tasks write
        # parent_requirement: REQ-PROC-NNN before requirements.md is created)
        requirements_tasks_dir = Path(REGISTRY_FILE).parent.parent
        goal_md_ids = _collect_goal_md_ids(requirements_tasks_dir, parent_id)

        # All known-taken IDs — union of folder frontmatter IDs, reserve markers,
        # goal.md pre-allocations, and registry
        taken_ids = folder_ids | reserved_ids | goal_md_ids

        # Use 3-digit padding for top-level epics (REQ-FUNC), 2-digit for features (REQ-FUNC-007)
        id_depth = len(re.findall(r"-\d+", parent_id))
        pad_width = 3 if id_depth == 0 else 2

        # Scan from 1 upward to find the first free slot (fills gaps correctly)
        candidate = None
        next_num = 1
        for _ in range(MAX_ITERATIONS):
            candidate = f"{parent_id}-{next_num:0{pad_width}d}"
            if candidate not in taken_ids and candidate not in registry_content:
                break
            next_num += 1
        else:
            print(
                f"ERROR: could not find a free requirement ID after {MAX_ITERATIONS} "
                f"iterations starting from {parent_id}-01",
                file=sys.stderr,
            )
            sys.exit(1)

        # Create the permanent reservation inside the lock
        reserve_path = os.path.join(parent_path, f".reserve-{candidate}")
        with open(reserve_path, "w") as f:
            f.write(
                f"Reserved by allocate_req_id.py for session writing {candidate}\n"
            )

        print(candidate)
        # Lock released when 'with' block exits


if __name__ == "__main__":
    main()
