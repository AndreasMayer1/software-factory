---
task_id: TASK-PROC-008-08
type: impl
parent_requirement: REQ-PROC-008
urgency: 2
urgency_reason: U2-QOL
impact: 2
impact_reason: I2-DEV
status: completed
completed: 2026-04-10
effort: S
created: 2026-04-10
started: 2026-04-10
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Add slim script-fix mode to code-bugfix skill that skips worktree creation"
release_description: ""
worktree_path: ""
requirements_version:
  commit: fadfd042
  file: ../requirements.md
---

# Goal: Add Slim Script-Fix Mode to code-bugfix Skill

## Objective

Extend the `.claude/skills/code-bugfix` skill with a lightweight "slim mode" for fixing scripts and non-Flutter files that don't require a git worktree or `flutter pub get`. When a bugfix is purely in a Python/shell script (or any non-Dart file), the full worktree workflow is unnecessary overhead.

## Scope

### In Scope
- Add a `slim: true` flag (or similar trigger) to the skill or task goal.md to activate slim mode
- In slim mode: skip worktree creation, skip `flutter pub get`, work directly in the main working tree
- In slim mode: skip the `worktree_path` field update in goal.md
- In slim mode: still write protocol to `plans_and_protocols/`, still run tests, still remind to use `task-complete-bugfix`
- Define the trigger: either a frontmatter field in goal.md (`fix_mode: slim`) or detected automatically when all changed files are non-Dart

### Out of Scope
- Changing the existing full worktree mode behavior
- Merging or removing the worktree mode

## Acceptance Criteria

- [ ] The code-bugfix skill detects or accepts a "slim mode" signal
- [ ] In slim mode, no worktree is created and no `flutter pub get` is run
- [ ] In slim mode, the fix is applied directly to the file in the main working tree
- [ ] Protocol is still written to `plans_and_protocols/`
- [ ] The skill documents the two modes clearly so future sessions can choose correctly
- [ ] `task-complete-bugfix` still works after a slim-mode fix (no worktree to clean up)

## Notes

Triggered by: a script bugfix (TASK-PROC-041-01-06) that went through full worktree setup unnecessarily because the bug was in a Python file with no Dart involvement.

The slim mode should be the default for any fix in `scripts/`, `.claude/`, or other non-Flutter folders.
