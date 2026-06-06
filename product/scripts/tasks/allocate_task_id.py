#!/usr/bin/env python3
"""
Atomically allocate the next task ID for a requirement.

Prints the allocated task ID to stdout (e.g. TASK-FUNC-007-06).
Uses an exclusive file lock so parallel sessions cannot get the same ID.

Usage:
    python scripts/allocate_task_id.py --req-id REQ-FUNC-007 \
        --req-path requirements_tasks/functional/shared/epic_data_transfer

How it works:
  Inside the lock the script creates a .reserve-TASK-* marker file in the
  requirement's tasks/ folder before releasing the lock. This marker persists
  permanently — it is the reservation. Callers count both real task folders and
  reserve markers, so a slow or resumed session never collides with a concurrent
  one. Gaps in IDs caused by unredeemed reservations are acceptable.

  The caller (task-create skill) deletes the .reserve-* file after writing goal.md.

Why a lock file instead of just the registry:
  Regenerating the registry + checking it is not atomic with respect to writing
  goal.md. Two sessions can both read the same registry, both get the same next
  number, and both pass the check before either writes. The flock + reserve-file
  pattern closes that window.

Output:
    Prints the newly allocated TASK-ID to stdout. Errors and lock-contention diagnostics go to stderr.
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import fcntl
import glob
import os
import re
import sys

LOCK_FILE = "requirements_tasks/_meta/.task_id_lock"
MAX_ITERATIONS = 100
REQ_ID_PATTERN = re.compile(r"^REQ-[A-Z]+-\d")


def allocate_id(req_id: str, req_path: str, lock_file: str = LOCK_FILE) -> str:
    """Allocate and reserve the next task ID for req_id inside req_path/tasks/.

    Creates a .reserve-TASK-* marker file inside tasks/ before returning so that
    concurrent calls (holding the same lock) cannot get the same ID.  The caller
    is responsible for deleting the reserve file after writing goal.md.

    Returns the allocated task ID string (e.g. "TASK-PROC-048-10").
    Raises SystemExit on unrecoverable errors.
    """
    if not REQ_ID_PATTERN.match(req_id):
        print(
            f"ERROR: --req-id '{req_id}' does not match pattern REQ-[A-Z]+-[0-9...]",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.isdir(req_path):
        print(
            f"ERROR: --req-path '{req_path}' does not exist or is not a directory",
            file=sys.stderr,
        )
        sys.exit(1)

    task_prefix = req_id.replace("REQ-", "TASK-", 1)
    tasks_dir = os.path.join(req_path, "tasks")
    os.makedirs(tasks_dir, exist_ok=True)

    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    with open(lock_file, "a"):
        pass

    with open(lock_file) as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)

        # Collect all used task numbers from existing goal.md files and reserve markers
        used_nums: set[int] = set()
        num_pattern = re.compile(rf"^{re.escape(task_prefix)}-(\d+)$")

        for goal_path in glob.glob(os.path.join(tasks_dir, "*/goal.md")):
            try:
                with open(goal_path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("task_id:"):
                            tid = line.split(":", 1)[1].strip()
                            m = num_pattern.match(tid)
                            if m:
                                used_nums.add(int(m.group(1)))
                            break
            except OSError:
                pass

        reserves = glob.glob(os.path.join(tasks_dir, ".reserve-*"))
        reserved_ids = {os.path.basename(r).removeprefix(".reserve-") for r in reserves}
        for rid in reserved_ids:
            m = num_pattern.match(rid)
            if m:
                used_nums.add(int(m.group(1)))

        next_num = max(used_nums, default=0) + 1
        candidate = None
        for _ in range(MAX_ITERATIONS):
            candidate = f"{task_prefix}-{next_num:02d}"
            if next_num not in used_nums and candidate not in reserved_ids:
                break
            next_num += 1
        else:
            print(
                f"ERROR: could not find a free task ID after {MAX_ITERATIONS} iterations "
                f"starting from {task_prefix}-{max(used_nums, default=0) + 1:02d}",
                file=sys.stderr,
            )
            sys.exit(1)

        reserve_path = os.path.join(tasks_dir, f".reserve-{candidate}")
        with open(reserve_path, "w") as f:
            f.write(f"Reserved by allocate_task_id.py for session writing {candidate}\n")

        return candidate


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Atomically allocate the next task ID for a requirement."
    )
    parser.add_argument("--req-id", required=True, help="e.g. REQ-FUNC-007")
    parser.add_argument(
        "--req-path",
        required=True,
        help="path to the requirement folder (contains tasks/)",
    )
    args = parser.parse_args()
    print(allocate_id(args.req_id, args.req_path))


if __name__ == "__main__":
    main()
