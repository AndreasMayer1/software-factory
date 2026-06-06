#!/usr/bin/env python3
"""Write an interactive-mode feedback-checkpoint file into a task's plans_and_protocols/.

Captures a developer-steered decision (the developer modified, redirected, or rejected a
skill's proposal rather than approving it as-is) as a durable artifact alongside the work it
shaped. This is the interactive counterpart of the automated-mode archival in
scripts/automation/orchestrate.py (_archive_feedback_checkpoint); both render through the shared
scripts/util/feedback_checkpoint.py so the REQ-PROC-041-04 AC-06 envelope cannot drift between
modes. mode: interactive per REQ-PROC-044-03 AC-02. Invoked by the task-complete skill in the
main session, where the full (uncompressed) session context is still available.

Unlike the automated writer, the filename omits the TASK-ID: the file is written into the
task's own plans_and_protocols/ folder, so its location already identifies the task.

Output: prints the path of the written checkpoint file to stdout (one line, no decoration),
consumed by the task-complete skill.
"""

# tier: C  # one-shot CLI, no imported callers, writes a single artifact file

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from util.feedback_checkpoint import (  # type: ignore[import-not-found]  # mypy cannot follow runtime sys.path.insert done above
    CheckpointFields,
    render_checkpoint,
    resolve_checkpoint_path,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", required=True, help="Skill that hit the steered gate.")
    parser.add_argument("--decision", required=True, help="revised | redirected | rejected.")
    parser.add_argument("--task-id", required=True, help="TASK-ID (envelope field, not filename).")
    parser.add_argument("--protocols-dir", required=True, help="Target plans_and_protocols/ folder.")
    parser.add_argument(
        "--answer-file",
        required=True,
        help="File holding the developer's verbatim steering words (read exactly, no rephrasing).",
    )
    parser.add_argument("--question-text", default="", help="What the skill/agent proposed.")
    parser.add_argument("--rationale-text", default="", help="The 'why' the artifact does not record.")
    args = parser.parse_args(argv)

    protocols_dir = args.protocols_dir
    if not os.path.isdir(protocols_dir):
        print(f"ERR: protocols-dir does not exist: {protocols_dir}", file=sys.stderr)
        return 2

    answer = Path(args.answer_file).read_text(encoding="utf-8")
    # Why: an empty verbatim answer means there is no developer decision to preserve; writing
    # the file anyway would produce a noise entry that defeats the artifact's purpose (AC-01
    # negative case — plain approvals produce no file).
    if not answer.strip():
        print("ERR: answer-file is empty; refusing to write an empty checkpoint", file=sys.stderr)
        return 2

    captured_at = datetime.now().astimezone().strftime("%Y-%m-%d")
    fields = CheckpointFields(
        skill=args.skill,
        mode="interactive",
        decision=args.decision,
        task_id=args.task_id,
        captured_at=captured_at,
        question=args.question_text,
        answer=answer,
        rationale=args.rationale_text,
    )
    out_path = resolve_checkpoint_path(protocols_dir, captured_at, os.path.exists)
    Path(out_path).write_text(render_checkpoint(fields), encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
