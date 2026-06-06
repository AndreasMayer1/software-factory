#!/usr/bin/env python3
"""Check whether a task is in_progress and waiting for a user answer.

A task is "awaiting answer" when ALL of the following are true:
  1. automation/pending_feedback/<task_id>/question.md exists
  2. automation/pending_feedback/<task_id>/answer.md does not exist, is zero bytes,
     is whitespace-only, OR still contains only the TEMPLATE_answer.md placeholder

Exit codes:
  0 — task is NOT awaiting an answer (proceed normally)
  1 — task IS awaiting an answer (skip this task)

Usage:
  python3 scripts/is_awaiting_answer.py --task-id TASK-FUNC-007-14

Output:
    Prints nothing on stdout; the answer is encoded in the exit code (0 = not awaiting, 1 = awaiting).
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import os
import sys

FEEDBACK_DIR = os.path.join(
    os.path.dirname(__file__), "..", "automation", "pending_feedback"
)
TEMPLATE_PATH = os.path.join(FEEDBACK_DIR, "TEMPLATE_answer.md")
TEMPLATE_MARKER = "<!-- AWAITING_HUMAN_ANSWER -->"


def answer_is_empty(answer_path: str) -> bool:
    """Return True if answer.md is absent, empty, whitespace-only, or template-only.

    Why: orchestrate.py's answer_is_empty uses the same sentinel logic. The original
    script only checked os.path.getsize == 0, which missed template-only content
    (~400 bytes). This caused is_awaiting_answer to exit 0 (not awaiting) even when
    only the copied TEMPLATE_answer.md placeholder was present, letting automated
    sessions re-pick tasks that should be waiting for human input.
    See automation/bugfix_plan_orchestrator_task_hijack.md
    """
    if not os.path.exists(answer_path):
        return True
    if os.path.getsize(answer_path) == 0:
        return True
    try:
        with open(answer_path) as f:
            content = f.read()
        stripped = content.strip()
        if not stripped:
            return True
        if stripped.startswith(TEMPLATE_MARKER):
            try:
                with open(TEMPLATE_PATH) as tf:
                    template_stripped = tf.read().strip()
                if stripped == template_stripped:
                    return True
            except OSError:
                pass
    except OSError:
        pass
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True, help="Task ID to check")
    args = parser.parse_args()

    task_dir = os.path.join(FEEDBACK_DIR, args.task_id)
    question_path = os.path.join(task_dir, "question.md")
    answer_path = os.path.join(task_dir, "answer.md")

    if os.path.exists(question_path) and answer_is_empty(answer_path):
        print(f"{args.task_id} is awaiting answer — skip")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
