---
task_id: TASK-PROC-008-07
type: bugfix
parent_requirement: REQ-PROC-008
urgency: 1
urgency_reason: U1-TEST
impact: 1
impact_reason: I1-TEST
status: completed
completed: 2026-03-15
effort: XS
created: 2026-03-15
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Test run of the code-bugfix skill and worktree workflow"
release_description: ""
worktree_path: "../bugfix-TASK-PROC-008-07"
requirements_version:
  commit: 9f3bd21
  file: ../requirements.md
---

# Goal: Ensure that worktree-based bugfix workflow functions correctly

## Objective

This is a **test task** to verify that the `code-bugfix` skill correctly:
1. Creates a git worktree at `../bugfix-<task-id>`
2. Writes the `worktree_path` back into this goal.md
3. The worktree branch is created from `develop`

No actual bug needs to be fixed. The task is complete once the worktree is created and the path is persisted.

## Bug Report

**Steps to reproduce:**
1. Run `code-bugfix` skill on a bugfix task for the first time

**Expected behavior:**
Worktree is created at `../bugfix-TASK-PROC-008-07` and `worktree_path` in goal.md is updated.

**Actual behavior:**
Not yet verified — this is the test run.

**Environment:** Linux dev container / WSL2

**Logs:** N/A

## Requirements Summary

This task tests the `code-bugfix` skill defined in `.claude/skills/code-bugfix/`.

Current requirements: ../requirements.md

## Scope

### In Scope
- Running `code-bugfix` first-run flow
- Verifying worktree creation
- Verifying `worktree_path` persistence in goal.md

### Out of Scope
- Any actual code changes
- Full bugfix cycle (task-complete-bugfix)

## Acceptance Criteria

- [ ] Worktree exists at `../bugfix-TASK-PROC-008-07`
- [ ] `worktree_path` field in this goal.md is set to the correct path
- [ ] Branch `bugfix/TASK-PROC-008-07` exists in the worktree

## Notes

Test task — can be cleaned up after verification.
