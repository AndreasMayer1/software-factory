---
task_id: TASK-PROC-041-04-02
type: impl
parent_requirement: REQ-PROC-041-04
urgency: 3
urgency_reason: U3-BLOCK
impact: 4
impact_reason: I4-FLOW
status: completed
completed: 2026-04-22
effort: M
created: 2026-04-22
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-04, AC-05]
  sections: []
scope_description: "Fix empty session_id in question.md/goal.md when session bypasses claude-route; add NEW_SESSION_REQUIRED resume path in orchestrator"
release_description: ""
opus_recommended: false
worktree_path: ""
requirements_version:
  commit: 4aa0668a
  file: ../requirements.md
---

# Goal: Fix session_id in question.md and goal.md

## Objective

Fix a bug where automated sessions that bypass `claude-route` write `question.md`
with `session_id: ""`, causing `find_answered_feedback` in `orchestrate.py` to
reject the question as malformed. This triggers a CRITICAL monitoring alert and
loops indefinitely.

Root cause: `claude-route` is the only place that writes `session_id` to
`goal.md`. If a session identifies and handles a task without going through
`claude-route`, `goal.md` stays `status: pending` with no `session_id` field.
The `claude-automated-mode` skill reads `SESSION_ID` from `goal.md` via grep —
getting an empty string — and writes `session_id: ""` to `question.md`.

Plan: `automation/plans/2026-04-22_01_opus_plan_session_id_fix.md`

## Requirements Summary

REQ-PROC-041-04 AC-01 requires that `question.md` always contains a valid
`session_id`. AC-04 requires the orchestrator to detect answered questions.
AC-05 requires the orchestrator to resume using that `session_id`.

All three are violated when `session_id` is empty.

```
git show 4aa0668a:requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/feat_feedback_pause_resume/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

1. **`scripts/automation/terminate_session.sh`** — add Python patch call before
   `kill -TERM`: scans `pending_feedback/*/question.md` for empty `session_id`,
   patches with `$CLAUDE_SESSION_ID` from env; patches corresponding `goal.md`
   to add `session_id` and set `status: in_progress` if still `pending`.
   If `$CLAUDE_SESSION_ID` is also empty: writes `session_id: "NEW_SESSION_REQUIRED"`.

2. **`scripts/automation/orchestrate.py`**:
   - `find_answered_feedback`: accept `"NEW_SESSION_REQUIRED"` as valid session_id
     (not malformed); add `requires_fresh_session` flag to returned dict.
   - Answered-feedback handler: if `requires_fresh_session`, launch new normal
     session with goal.md path + answer as context instead of `--resume`.

3. **`.claude/skills/claude-automated-mode/skill.md`** — add mandatory
   pre-question assertion: check that an in_progress task with `session_id` exists
   before writing `question.md`; instruct to call `claude-route` first if not.

### Out of Scope

- Enforcing that `claude-route` is always called (structural; would require
  orchestrator pre-selection of task)
- One-task-per-session enforcement
- REQ-PROC-041-02 AC-03 (orchestrator pre-writing session_id before launch) —
  separate task if needed

## Acceptance Criteria

- [ ] `terminate_session.sh` patches empty `session_id` in `question.md` from
  `$CLAUDE_SESSION_ID` before killing the process
- [ ] `terminate_session.sh` also writes `session_id` to the corresponding
  `goal.md` and sets `status: in_progress` if still `pending`
- [ ] If `$CLAUDE_SESSION_ID` is empty, `"NEW_SESSION_REQUIRED"` is written
- [ ] `find_answered_feedback` accepts `"NEW_SESSION_REQUIRED"` without logging
  "malformed" warning; sets `requires_fresh_session: True`
- [ ] Orchestrator launches fresh session (not `--resume`) when
  `requires_fresh_session` is true, passing goal.md path and answer as context
- [ ] `claude-automated-mode` skill asserts in_progress + session_id before
  question.md write; prints actionable error if precondition fails
- [ ] Existing TASK-PROC-027-01 `question.md` can be repaired manually using
  the same patch logic (manual test)

## Notes

- Discovered via production incident: Session 9 (2026-04-19, 19:37–19:53)
  completed TASK-PROC-027-14 and TASK-PROC-039-01, then self-selected
  TASK-PROC-027-01 without calling `claude-route`, leading to empty `session_id`.
- The `terminate_session.sh` approach requires zero new LLM compliance because
  the script is already called reliably at the end of every question-writing exit.
- Full Opus analysis: `automation/plans/2026-04-22_01_opus_plan_session_id_fix.md`
