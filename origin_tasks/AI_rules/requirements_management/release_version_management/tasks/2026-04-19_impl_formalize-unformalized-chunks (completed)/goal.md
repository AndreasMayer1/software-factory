---
task_id: TASK-PROC-034-15
type: impl
parent_requirement: REQ-PROC-034
urgency: 5
urgency_reason: U5-BLOCK
impact: 4
impact_reason: I4-SCOPE
status: completed
completed: 2026-04-19
started: 2026-04-19
effort: S
created: 2026-04-19
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-04]
target_package: ""
scope_description: "Formalize 3 unformalized flow release_scope chunks into proper RELEASE_BACKLOG.md packages via release-plan Action 4b"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 3e9fba52
  file: ../requirements.md
---

# Goal: Formalize Unformalized Release Chunks

## Objective

Run `release-plan → Action 4b` to formalize the following flow `release_scope` chunks that have no matching entry in RELEASE_BACKLOG.md:

1. **"Core Protocol Delivery"** (FLOW-002 — Instruct Client on Protocol)
2. **"Client & Privacy Edge Cases"** (FLOW-002 — Instruct Client on Protocol)
3. **"Core File Transfer"** (FLOW-004 — Flexible Data Transfer)

## Requirements Summary

REQ-PROC-034 SEC-04 requires that all flow `release_scope` chunks are formalized as backlog packages before requirements can be assigned packages. Without formal packages for these chunks, future `requ-assign-packages` runs cannot assign packages to requirements derived from FLOW-002 and FLOW-004.

Current requirements: ../requirements.md

## Scope

### In Scope
- Run `release-plan → Action 4b` interactively
- Propose and confirm package names, descriptions, and version assignments for the 3 chunks
- Update RELEASE_BACKLOG.md with the new entries
- Commit the changes

### Out of Scope
- Assigning requirements to these new packages (that happens in the subsequent `requ-assign-packages` run)

## Acceptance Criteria

- [ ] "Core Protocol Delivery" (FLOW-002) has a formal RELEASE_BACKLOG.md entry
- [ ] "Client & Privacy Edge Cases" (FLOW-002) has a formal RELEASE_BACKLOG.md entry
- [ ] "Core File Transfer" (FLOW-004) has a formal RELEASE_BACKLOG.md entry
- [ ] RELEASE_BACKLOG.md committed

## Notes

Detected during `requ-assign-packages` prerequisite guard on 2026-04-19.
