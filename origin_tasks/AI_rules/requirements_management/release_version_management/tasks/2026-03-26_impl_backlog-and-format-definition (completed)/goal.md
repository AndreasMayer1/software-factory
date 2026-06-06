---
task_id: TASK-PROC-034-09
type: impl
parent_requirement: REQ-PROC-034
urgency: 4
urgency_reason: U4-PLAN
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-03-26
started: 2026-03-26
effort: M
created: 2026-03-26
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-02]
scope_description: "Create RELEASE_BACKLOG.md and update RELEASES.md format"
release_description: ""
requirements_version:
  commit: "b25b8f25"
  file: ../requirements.md
---

# Implementation Task: Create RELEASE_BACKLOG.md and Update RELEASES.md Format

## Requirement Reference
- **Requirement**: ../requirements.md (REQ-PROC-034)
- **Status**: Not Started

## Goal

Create the new `RELEASE_BACKLOG.md` file at `requirements_tasks/RELEASE_BACKLOG.md` with initial packages derived from the existing RELEASES.md scope boundaries. Update `RELEASES.md` to the new format (version→packages mapping with `packages:` lists instead of detailed `scope_boundaries.includes`).

## Scope Overview

**Affected files**:
- NEW: `requirements_tasks/RELEASE_BACKLOG.md`
- UPDATE: `requirements_tasks/RELEASES.md`

### In Scope
- Define initial packages from existing RELEASES.md scope items (one or more packages per release)
- Write RELEASE_BACKLOG.md with correct YAML schema per REQ-PROC-034 SEC-01
- Update RELEASES.md entries to include `packages:` lists per REQ-PROC-034 SEC-02
- Remove detailed `scope_boundaries.includes` from RELEASES.md (content moves to package descriptions)
- Preserve `scope_boundaries.excludes` in RELEASES.md
- Order packages in backlog by priority (user confirms order)

### Out of Scope
- Migrating `target_release` fields in requirements/tasks (separate task)
- Updating skills or scripts (separate task)
- Creating the `release-plan` skill

## Acceptance Criteria

- [ ] RELEASE_BACKLOG.md exists at `requirements_tasks/RELEASE_BACKLOG.md`
- [ ] Every package has: id, source (type + ref + scope), description, priority_within_source, status, assigned_release
- [ ] Package IDs are max 4 words, human-readable, unique
- [ ] Every existing release in RELEASES.md has at least one package in RELEASE_BACKLOG.md
- [ ] RELEASES.md entries have `packages:` lists referencing package IDs
- [ ] Backlog package order reflects user-confirmed priority
- [ ] RELEASES.md retains `scope_boundaries.excludes` per release (not removed during format migration)
- [ ] YAML is valid and parseable

## Dependencies
None — this task can start immediately.

## Notes
- The user must confirm the package breakdown before writing files. Present the proposed packages and get approval.
- For releases with multiple scope items, propose logical package groupings rather than 1:1 mapping.
- Flow-based packages (from FLOW-003, FLOW-004 etc.) should have `source.type: flow` and `priority_within_source` set. Requirement-based packages use `source.type: requirement`.
