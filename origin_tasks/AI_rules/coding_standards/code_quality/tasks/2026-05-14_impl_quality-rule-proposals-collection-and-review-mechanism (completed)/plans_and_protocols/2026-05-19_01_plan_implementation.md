# Plan — Quality-rule proposals collection + permanent loop-task

Task: TASK-PROC-046-13
Date: 2026-05-19
Loop task ID (allocated): **TASK-PROC-046-16**

## Why this design

User's revised design (`2026-05-14_feedback_03.md` Allgemeines 1):

- The user rejected the per-round-new-task design because `task-complete` is
  coupled to commit; creating a new folder every round adds clutter.
- One physical loop-task folder lives forever. After each round a reset script
  re-populates the `pending_feedback/<TASK_ID>/` Q&A files and resets the goal
  back to `status: pending`.
- The `question.md` is generic — it does NOT duplicate per-proposal content.
  It only points at `scripts/quality/proposals/` and at the answer-format spec.
- AI proposes; user reviews; AI applies decisions. Goodhart's-Law protection
  (REQ-PROC-046 Developer Guidelines) preserved.

## Pieces and order

1. **Part A** — `scripts/quality/proposals/{analysis_options,grep_gates,thresholds,new_gates}/`
   with a per-folder `README.md` and a top-level `README.md` documenting the
   proposal-file format.
2. **Part B** — Permanent loop-task folder
   `requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-14_impl_apply-quality-rule-proposals-loop/`
   with generic `goal.md` (TASK-PROC-046-16, `status: pending`) and an empty
   `plans_and_protocols/`.
3. **Part C** — `automation/pending_feedback/TASK-PROC-046-16/question.md`
   (generic reference body, `session_id: NEW_SESSION_REQUIRED`,
   `account: gmail2`) and `answer.md` (verbatim copy of `TEMPLATE_answer.md`).
4. **Part D** — `scripts/quality/reset_proposals_loop.py`. Re-creates the
   `pending_feedback/<LOOP_TASK_ID>/` folder from the templates, resets the
   loop-task `goal.md` `status` back to `pending`, clears `session_id`. Does
   NOT commit; the caller (the loop-task's last AC) commits.
5. **Part E** — CLAUDE.md gets a new section (§Quality-Rule Improvement
   Proposals) instructing AI agents to file proposals instead of autonomously
   editing gates. `task-complete` skill gets a check-and-remind step.

## Account choice for the Q&A pair

The orchestrator requires `account` to be a real account name (research §3).
The current automation session is running on `gmail2` (`session_account: gmail2`
in this task's goal.md), so we pre-populate `account: gmail2` in the loop
question.md. The orchestrator will spin up a fresh session under that account
when the developer fills `answer.md`.

## Commit semantics (clarification)

Per goal.md "Notes": the loop-task's last AC commits the round's changes
(analyzer config / gate scripts edits + updated proposal `status:` fields +
the archived answer). The reset script's outputs (new question.md +
template answer.md) are committed in the NEXT round. The intentional
trade-off avoids `task-complete` coupling problems.

## Files produced by this task

```
scripts/quality/proposals/
  README.md
  analysis_options/README.md
  grep_gates/README.md
  thresholds/README.md
  new_gates/README.md
scripts/quality/reset_proposals_loop.py
requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/
  2026-05-14_impl_apply-quality-rule-proposals-loop/
    goal.md
    plans_and_protocols/.gitkeep
automation/pending_feedback/TASK-PROC-046-16/
  question.md
  answer.md
CLAUDE.md                                 (modified)
.claude/skills/task-complete/skill.md     (modified — via claude-modify-skill)
```

## Smoke test (documentation only, executed mentally)

End-to-end documented in `2026-05-19_02_protocol_smoke_test.md`.
