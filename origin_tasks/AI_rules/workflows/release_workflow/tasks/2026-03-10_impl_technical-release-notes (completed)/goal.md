---
task_id: TASK-PROC-036-03
type: impl
parent_requirement: REQ-PROC-036
urgency: 3
urgency_reason: U3-PROC
impact: 3
impact_reason: I3-QUAL
status: completed
completed: 2026-03-10
effort: S
created: 2026-03-10
after: [TASK-PROC-036-05]
awaiting: []
awaiting_note: ""
release_description: "Auto-generate technical release notes from completed task descriptions"
covers:
  acceptance_criteria: []
  sections: [SEC-03]
target_package: "Transfer Data Model"
scope_description: "Script or skill logic that reads release_description from completed impl tasks and writes release_notes_technical.md."
requirements_version:
  commit: 8aeefd9
  file: ../requirements.md
---

# Goal: Technical Release Notes Generation

## Objective

Implement the logic (as a PowerShell script or embedded in the release skill) that reads the `release_description` field from all completed `impl`-type tasks assigned to the active release and generates `releases/[version]/release_notes_technical.md` in Keep-a-Changelog format.

## Requirements Summary

Covers SEC-03 (Technical Release Notes) of REQ-PROC-036.

Current requirements: ../requirements.md

## Scope

### In Scope
- Script or inline skill logic to:
  - Find all goal.md files with `target_release` matching the active release
  - Filter: `type: impl`, `status: completed`, category `functional/` or `non-functional/` only (exclude `process/`)
  - Read `release_description` from each; warn if field is missing
  - Group by category prefix (feat → Features, fix → Fixes, etc.) — or by requirement category if no commit prefix is available
  - Write `releases/[version]/release_notes_technical.md`
- Format: Keep-a-Changelog style, English

### Out of Scope
- Marketing release notes (TASK-PROC-036-04)
- Git commit parsing (we use task metadata, not commits)

## Acceptance Criteria

- [ ] `releases/[version]/release_notes_technical.md` is generated correctly
- [ ] Only `functional/` and `non-functional/` impl tasks are included
- [ ] Tasks missing `release_description` are listed as a warning (not silently skipped)
- [ ] Format follows Keep-a-Changelog structure
- [ ] Language is English

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-036-05 | pending | Tasks must have release_description field populated |
