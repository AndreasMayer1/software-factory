#!/usr/bin/env python3
"""Reset the quality-rule proposals loop-task for the next round.

Restores `automation/pending_feedback/<LOOP_TASK_ID>/` from the canonical
templates and resets the loop-task `goal.md` back to its awaiting state
(`status: pending`, empty `session_id`). Designed to be invoked as the final
acceptance criterion of the permanent loop-task TASK-PROC-046-16 —
"Apply quality-rule proposals loop".

The script does NOT commit. The caller (the loop-task's last AC) is
responsible for commit ordering: the round's *applied changes* are committed
in this round; the reset's filesystem mutations land in the NEXT round's
commit.

Output:
    On success, prints a single-line confirmation to stdout
    ("Reset complete. <TASK_ID> is awaiting the next answer.") and exits 0.
    Errors are written to stderr with an `ERROR: ` prefix and a non-zero
    exit code.

Exit codes:
    0  reset successful, folder ready for the next round
    1  loop-task folder missing or malformed (cannot reset)
    2  invocation error (templates missing, unwritable target paths)
"""

# tier: B

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

LOOP_TASK_ID = "TASK-PROC-046-16"
REPO_ROOT = Path(__file__).resolve().parents[2]

LOOP_TASK_GOAL = (
    REPO_ROOT
    / "requirements_tasks"
    / "process"
    / "AI_rules"
    / "coding_standards"
    / "code_quality"
    / "tasks"
    / "2026-05-14_impl_apply-quality-rule-proposals-loop"
    / "goal.md"
)

PENDING_FEEDBACK_DIR = REPO_ROOT / "automation" / "pending_feedback" / LOOP_TASK_ID
TEMPLATE_ANSWER = REPO_ROOT / "automation" / "pending_feedback" / "TEMPLATE_answer.md"

# Why pinned account: the orchestrator requires a real account in question.md
# frontmatter (research §3); a sentinel value would be rejected as malformed.
# `gmail2` is the account that currently owns the automation orchestrator.
QUESTION_ACCOUNT = "gmail2"

QUESTION_TEMPLATE = """\
---
task_id: {task_id}
session_id: NEW_SESSION_REQUIRED
account: {account}
status: awaiting_answer
asked_at: {asked_at}
skill: apply-quality-rule-proposals
---

# Apply Quality-Rule Proposals

This is the recurring quality-rule application loop. It is *always* awaiting answer.

## Where the open proposals live

`scripts/quality/proposals/<category>/<YYYY-MM-DD>_<slug>_<source_task>.md`

Categories:

- `analysis_options/` — proposed analyzer-config changes
- `grep_gates/` — proposed `scripts/quality/check_*.sh` changes
- `thresholds/` — schwellwert tightenings / loosenings
- `new_gates/` — entirely new gates

Each file has `status: pending_review` until you decide. Read each one
before writing your answer. The proposal format is documented in
`scripts/quality/proposals/README.md`.

## How to write your answer

Open `answer.md` in this folder and replace the template content with your
decisions, one entry per proposal, blank-line-separated:

```
proposal_id: <slug>
decision: accepted | rejected | superseded_by:<other_slug>
notes: <free text — optional reasoning or amendments>
```

Notes:

- `proposal_id` must match the `proposal_id:` field in the proposal's
  frontmatter (same as the slug part of the filename).
- `notes:` is optional but recommended on rejections — the loop-task
  appends it as a `## Decision` section in the proposal file so future
  agents see why.
- If you want to skip a proposal this round, simply omit it from the
  answer; the loop-task only acts on proposals that appear.

## What happens after you save

1. The orchestrator detects the non-template answer.
2. It launches a fresh session on this task (the `NEW_SESSION_REQUIRED`
   sentinel triggers `run_fresh_session_with_answer` — research §3).
3. The session reads each decision, applies accepted proposals, bumps each
   proposal's `status:` field, and commits the change set.
4. The session runs `python3 scripts/quality/reset_proposals_loop.py`,
   which restores this folder to the awaiting-answer state for the next
   round.

## See also

- `scripts/quality/proposals/README.md` — proposal-file format spec.
- `requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-14_impl_apply-quality-rule-proposals-loop/goal.md` — the loop-task's full goal and round-execution playbook.
"""


def _read_frontmatter_lines(path: Path) -> tuple[list[str], list[str]]:
    """Split `path` into (frontmatter_lines, body_lines).

    The frontmatter is the block between the first two `---` lines. If the
    file does not start with `---`, both lists are empty / the whole file is
    treated as body.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].startswith("---"):
        return [], lines
    end = None
    for i in range(1, len(lines)):
        if lines[i].startswith("---"):
            end = i
            break
    if end is None:
        return [], lines
    return lines[: end + 1], lines[end + 1 :]


def _reset_goal_md(goal_path: Path) -> None:
    """Force `status: pending` and clear `session_id` in `goal_path` frontmatter."""
    fm, body = _read_frontmatter_lines(goal_path)
    if not fm:
        raise SystemExit(f"goal.md at {goal_path} has no YAML frontmatter")

    new_fm: list[str] = []
    saw_status = False
    saw_session_id = False
    for line in fm:
        if line.startswith("status:"):
            new_fm.append("status: pending\n")
            saw_status = True
        elif line.startswith("session_id:"):
            new_fm.append('session_id: ""\n')
            saw_session_id = True
        else:
            new_fm.append(line)

    if not saw_status:
        raise SystemExit(f"goal.md at {goal_path} missing `status:` field")
    if not saw_session_id:
        # Why insert before closing fence: keep frontmatter shape stable; absence
        # would only happen if a future schema change removed the field.
        for i in range(len(new_fm) - 1, -1, -1):
            if new_fm[i].startswith("---"):
                new_fm.insert(i, 'session_id: ""\n')
                break

    goal_path.write_text("".join(new_fm) + "".join(body), encoding="utf-8")


def _recreate_pending_feedback(task_id: str, account: str) -> None:
    if not TEMPLATE_ANSWER.is_file():
        raise SystemExit(f"missing template: {TEMPLATE_ANSWER}")

    PENDING_FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

    asked_at_local = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    question_text = QUESTION_TEMPLATE.format(
        task_id=task_id,
        account=account,
        asked_at=asked_at_local,
    )
    (PENDING_FEEDBACK_DIR / "question.md").write_text(question_text, encoding="utf-8")

    shutil.copyfile(TEMPLATE_ANSWER, PENDING_FEEDBACK_DIR / "answer.md")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--account",
        default=QUESTION_ACCOUNT,
        help=f"Account name written into question.md (default: {QUESTION_ACCOUNT}).",
    )
    args = parser.parse_args(argv)

    if not LOOP_TASK_GOAL.is_file():
        print(f"ERROR: loop-task goal.md not found at {LOOP_TASK_GOAL}", file=sys.stderr)
        return 1

    try:
        _reset_goal_md(LOOP_TASK_GOAL)
        _recreate_pending_feedback(LOOP_TASK_ID, args.account)
    except SystemExit as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Reset complete. {LOOP_TASK_ID} is awaiting the next answer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
