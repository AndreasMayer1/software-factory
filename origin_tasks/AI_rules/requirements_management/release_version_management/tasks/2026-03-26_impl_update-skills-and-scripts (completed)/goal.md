---
task_id: TASK-PROC-034-11
type: impl
parent_requirement: REQ-PROC-034
urgency: 4
urgency_reason: U4-PLAN
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-03-26
started: 2026-03-26
effort: XL
created: 2026-03-26
after: [TASK-PROC-034-09, TASK-PROC-034-10]
awaiting: [TASK-PROC-034-10]
awaiting_note: "Migration must complete before skills/scripts can switch to target_package"
covers:
  acceptance_criteria: []
  sections: [SEC-04, SEC-05, SEC-06, SEC-07]
scope_description: "Update all skills and scripts to use target_package instead of target_release"
release_description: ""
requirements_version:
  commit: "b25b8f25"
  file: ../requirements.md
---

# Implementation Task: Update Skills and Scripts for Package-Based Model

## Requirement Reference
- **Requirement**: ../requirements.md (REQ-PROC-034)
- **Status**: Not Started

## Goal

Update all affected skills and scripts to use the package-based model (`target_package` + RELEASE_BACKLOG.md) instead of the version-based model (`target_release` + RELEASES.md versions). Also create the new `release-plan` skill.

## Scope Overview

**Affected Skills** (8 total):
1. `requ-explore` — Section 2.4: replace target_release logic with target_package, read RELEASE_BACKLOG.md
2. `task-create` — Release Version Inheritance section: replace with Package Inheritance
3. `task-create-impl` — Section 3.4: same changes as task-create
4. `requ-prep-release` — Scope check against packages instead of scope_boundaries
5. `ux-create-flow` — Step 2: add Release Scope questions. Step 6: include template. Step 10: checklist. Step 12: note NEW packages
6. `requ-derive-from-flow` — Phase 1: read Release Scope. Phase 2: Suggested Package column. Phase 4: suggested_package in goal.md
7. `release` — After release: update package statuses to released in RELEASE_BACKLOG.md
8. NEW: `release-plan` — Read backlog, assign packages to versions, update both files

**Affected Scripts** (4 total):
1. `scripts/validate_meta.py` — target_package validation against RELEASE_BACKLOG.md, package-based dependency validation
2. `scripts/generate_status_overview.py` — target_package grouping, --package flag, package-summary mode
3. `scripts/next_tasks.py` — next package logic, --package flag
4. `scripts/generate_technical_release_notes.py` — collect tasks by package from release's packages list

### In Scope
- All skill files listed above
- All script files listed above
- Creating new `release-plan` skill
- Updating dependency validation logic (package ordering + version constraints)

### Out of Scope
- Migrating data in requirements/tasks files (completed by TASK-PROC-034-10)
- Creating RELEASE_BACKLOG.md (completed by TASK-PROC-034-09)
- Updating REQ-PROC-034 itself

## Acceptance Criteria

- [ ] All 7 existing skills reference `target_package` instead of `target_release`
- [ ] All skills read RELEASE_BACKLOG.md for package lookups (not RELEASES.md for version lookups)
- [ ] `release-plan` skill exists and can assign packages to versions
- [ ] `ux-create-flow` includes Release Scope section in flow creation workflow
- [ ] `requ-derive-from-flow` carries `suggested_package` into goal.md files
- [ ] `validate_meta.py` validates `target_package` against RELEASE_BACKLOG.md
- [ ] `generate_status_overview.py` groups by package and supports `--package` flag
- [ ] `next_tasks.py` finds next package instead of next release
- [ ] `generate_technical_release_notes.py` collects tasks by package
- [ ] Dependency validation uses package priority ordering
- [ ] All scripts gracefully handle files not yet migrated (task-scope decision: accept both `target_release` and `target_package` until migration is confirmed complete, then remove `target_release` support in a follow-up)
- [ ] `validate_meta.py` accepts any package name: `target_package` is valid if the value matches any package `id` in RELEASE_BACKLOG.md — no requirement that the backlog has a `ref:` pointing back to the requirement
- [ ] Skills support direct package assignment: `requ-explore`, `task-create`, and `task-create-impl` prompt the user to select `target_package` from the RELEASE_BACKLOG.md package list when creating/updating requirements — this replaces the old version-based `target_release` input, and works for ALL requirements including those without backlog refs
- [ ] Primary package fallback documented in RELEASE_BACKLOG.md: RELEASE_BACKLOG.md format documentation notes that the first-listed package per version serves as the fallback `target_package` for cross-cutting requirements not covered by any scoped package

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-034-09 | pending | RELEASE_BACKLOG.md format must be finalized |
| TASK-PROC-034-10 | pending | Migration must complete so data matches new format |

## Notes
- This is a large task (XL effort). Consider splitting into sub-tasks during planning:
  - Sub-task A: Update skills (requ-explore, task-create, task-create-impl)
  - Sub-task B: Create release-plan skill
  - Sub-task C: Update ux-create-flow and requ-derive-from-flow
  - Sub-task D: Update scripts (validate_meta, generate_status_overview, next_tasks, generate_technical_release_notes)
  - Sub-task E: Update requ-prep-release and release skills
- During the transition period, scripts should accept both `target_release` and `target_package` fields. After full migration, `target_release` support can be removed.
- The `release-plan` skill should be designed as a simple interactive workflow: show backlog → user picks packages → assign to version → update files.
