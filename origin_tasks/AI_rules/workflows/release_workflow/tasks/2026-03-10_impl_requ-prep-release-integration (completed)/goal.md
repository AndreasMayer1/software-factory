---
task_id: TASK-PROC-036-06
type: impl
parent_requirement: REQ-PROC-036
urgency: 3
urgency_reason: U3-PROC
impact: 3
impact_reason: I3-ENAB
status: completed
completed: 2026-03-10
effort: XS
created: 2026-03-10
after: []
awaiting: []
awaiting_note: ""
release_description: "Track active release status in RELEASES.md via requ-prep-release skill"
covers:
  acceptance_criteria: []
  sections: [SEC-06]
target_package: "Transfer Data Model"
scope_description: "Update requ-prep-release skill to set status: active in RELEASES.md when preparation is approved."
requirements_version:
  commit: 8aeefd9
  file: ../requirements.md
---

# Goal: requ-prep-release Integration

## Objective

Update the `requ-prep-release` skill so that it sets the prepared release's `status` in RELEASES.md from `planned` to `active` when the user approves the preparation. This makes RELEASES.md the single source of truth for "which release is currently being worked on."

## Requirements Summary

Covers SEC-06 (requ-prep-release Integration) of REQ-PROC-036.

Lifecycle:
- `planned` → `active`: set by `requ-prep-release` after user approval
- `active` → `released`: set by `/release` skill after successful release
- Only one release may be `active` at a time

Current requirements: ../requirements.md

## Scope

### In Scope
- Read `requ-prep-release` skill at `.claude/skills/requ-prep-release/skill.md`
- Add a final step: after user approves preparation, update `status: planned` → `status: active` for the target release in RELEASES.md
- Add a guard: if another release already has `status: active`, warn the user and ask for confirmation before overwriting
- Use `claude-modify-skill` to apply the change

### Out of Scope
- The `/release` skill setting `status: released` (that is part of TASK-PROC-036-01)
- Any UI or reporting changes

## Acceptance Criteria

- [ ] `requ-prep-release` sets `status: active` in RELEASES.md after user approval
- [ ] Skill warns if another release is already `active` before proceeding
- [ ] Only one release has `status: active` at a time after the skill completes
- [ ] Change is applied via `claude-modify-skill` (not manual edit)

## Dependencies

None — standalone change to an existing skill.

## Notes

- Read the current `requ-prep-release` skill first to understand where the approval step occurs.
- This is a small XS change but is a prerequisite for the pre-flight script (TASK-PROC-036-02).
