---
task_id: TASK-PROC-041-01-06
type: bugfix
parent_requirement: REQ-PROC-041-01
urgency: 4
urgency_reason: U4-BLOCK
impact: 3
impact_reason: I3-DEV
status: completed
completed: 2026-04-10
effort: S
created: 2026-04-10
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-21, AC-23]
  sections: []
scope_description: "Fix infinite loop printing 'resume exhausted' message and diagnose git commit failure for answered feedback"
release_description: ""
worktree_path: "../bugfix-TASK-PROC-041-01-06"
requirements_version:
  commit: fa4fc195
  file: ../requirements.md
---

# Goal: Ensure that AC-21 and AC-23 of REQ-PROC-041-01 work correctly

## Objective

Fix two bugs in `scripts/automation/orchestrate.py`:

1. **Infinite loop bug (AC-21)**: After TASK-FUNC-007-10 exhausted 3 resume attempts, the log message `WARNING: resume of TASK-FUNC-007-10 exhausted 3 attempts — giving up this run` was printed ~2,600+ times in a tight loop. The orchestrator never stopped or moved on — it kept spinning indefinitely.

2. **Git commit failure (AC-23)**: The orchestrator failed to commit answered feedback on startup with: `git commit failed (Command '['git', 'commit', '-m', 'chore(automation): record user answers 2026-04-10 19:00']' returned non-zero exit status 1.)`. Identify why the commit failed (likely nothing staged, empty commit, or detached HEAD) and make the failure handling robust.

## Bug Report

**Steps to reproduce (Bug 1 — infinite loop):**
1. Have a task in `pending_feedback/` with both `question.md` and `answer.md`
2. Start the orchestrator
3. The orchestrator resumes the task 3 times; each time the session writes a new `question.md` instead of completing
4. After 3 failed resume attempts, the orchestrator enters an infinite loop printing the "exhausted 3 attempts" warning

**Expected behavior:**
After logging the warning once, the orchestrator skips the stuck task for the rest of the run and continues processing other tasks (or stops cleanly if there are none).

**Actual behavior:**
The "exhausted 3 attempts" warning is printed thousands of times in a tight loop. The orchestrator never terminates or moves on.

**Steps to reproduce (Bug 2 — git commit failure):**
1. Have answered feedback (answer.md present) in `automation/pending_feedback/`
2. Start the orchestrator
3. Observe: `WARNING: git commit failed` in the log at startup

**Expected behavior (AC-23):**
A git commit is made containing the `answer.md` files. Non-fatal if git fails, but failure should be logged once clearly.

**Actual behavior:**
The commit fails with exit code 1. The reason is unknown but likely one of: nothing to stage (files already tracked/committed), empty commit attempted, or git state issue.

**Logs:**
```
[orchestrator] WARNING: git commit failed (Command '['git', 'commit', '-m', 'chore(automation): record user answers 2026-04-10 19:00']' returned non-zero exit status 1.)
[orchestrator] Resuming TASK-FUNC-007-10 with account gmail
[orchestrator] TASK-FUNC-007-10 left in pending_feedback (new question or failure)
[orchestrator] Resuming TASK-FUNC-007-10 with account gmail
[orchestrator] TASK-FUNC-007-10 left in pending_feedback (new question or failure)
[orchestrator] Resuming TASK-FUNC-007-10 with account gmail
[orchestrator] TASK-FUNC-007-10 left in pending_feedback (new question or failure)
[orchestrator] WARNING: resume of TASK-FUNC-007-10 exhausted 3 attempts — giving up this run
[orchestrator] WARNING: resume of TASK-FUNC-007-10 exhausted 3 attempts — giving up this run
... (repeated ~2600 times)
```

**Environment:** WSL2, orchestrator PID 87519, develop branch

## Requirements Summary

REQ-PROC-041-01 (Session Orchestrator) defines the orchestrator behavior. The relevant ACs:

- **AC-21**: After 3 failed resume attempts for the same session_id, log a warning, skip the session for the remainder of the run, and include the stuck task in the run report.
- **AC-23**: On orchestrator start, git commit any new `answer.md` files in `automation/pending_feedback/`; non-fatal if git fails (log WARNING).

Current requirements: ../requirements.md

## Scope

### In Scope
- Fix the infinite loop after resume exhaustion (AC-21)
- Fix or harden the git commit logic for answered feedback (AC-23)
- Ensure the orchestrator terminates cleanly or continues to next task after giving up on a stuck task

### Out of Scope
- Why TASK-FUNC-007-10's sessions kept writing new questions (separate concern)
- Changing the 3-attempt limit
- Adding new orchestrator features

## Acceptance Criteria

- [ ] After 3 failed resume attempts, the orchestrator logs the warning exactly once and moves on (no loop)
- [ ] The orchestrator terminates cleanly or processes remaining tasks after giving up on the stuck task
- [ ] The git commit for `answer.md` files either succeeds or fails gracefully with a single WARNING log line (no crash, no loop)
- [ ] The git commit code handles the "nothing to commit" case without treating it as an error

## Notes

The infinite loop strongly suggests that the "giving up" check is inside the main session loop but the `break`/`continue`/return after logging is missing or unreachable. Read the orchestrator loop carefully around the resume-exhaustion path.
