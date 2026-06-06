---
task_id: TASK-PROC-034-17
type: impl
parent_requirement: REQ-PROC-034
urgency: 5
urgency_reason: U5-BLOCK
impact: 4
impact_reason: I4-PLAN
status: completed
completed: 2026-04-20
effort: XS
created: 2026-04-20
started: 2026-04-20
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01]
scope_description: "Formalize FLOW-004 'Notification System' chunk as a RELEASE_BACKLOG.md package entry via release-plan → Action 4b"
release_description: "Adds missing file-transfer notification package to release backlog for complete FLOW-004 coverage."
opus_recommended: false
worktree_path: ""
requirements_version:
  commit: 3e9fba52
  file: ../requirements.md
---

# Goal: Formalize FLOW-004 "Notification System" Release Package

## Objective

Run `release-plan → Action 4b` to add a formalized package entry to `requirements_tasks/RELEASE_BACKLOG.md` for the FLOW-004 chunk labelled **"Notification System"**.

This chunk was identified as unformalized during `requ-assign-packages` execution: it exists in `requirements_user_needs/user_flows/flexible_data_transfer/flow.md` `release_scope` but has no matching package in the backlog, blocking full package assignment for FLOW-004 requirements.

## Requirements Summary

REQ-PROC-034 governs the release package backlog lifecycle. All flow release_scope chunks must be formalized as backlog packages before `requ-assign-packages` can assign them to requirements.

For complete requirements at task creation time:
```
git show 3e9fba52:requirements_tasks/process/AI_rules/requirements_management/release_version_management/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Add a new package entry in `requirements_tasks/RELEASE_BACKLOG.md` YAML frontmatter for the "Notification System" chunk from FLOW-004 (flexible_data_transfer)
- Chunk covers: Exceptions 2.1 (notification not received + therapist-side reminder) and 2.2 (notification scheduling constraints + meta-reminder); plan-configured notification timing and instruction text; Notification Lifecycle domain concept implementation
- Follow package naming rules (≤4 words, role-subject convention)
- Set `status: planned`, `assigned_release: null`, source `type: flow`, `ref: FLOW-004`

### Out of Scope
- Assigning this package to a release version (that is release-plan Action 4c / release-plan skill)
- Modifying any other FLOW-004 packages already in the backlog

## Acceptance Criteria

- [ ] A new package entry exists in RELEASE_BACKLOG.md YAML for FLOW-004 "Notification System" chunk
- [ ] Package name follows naming rules (≤4 words, descriptive of content, not timing)
- [ ] `source.type: flow`, `source.ref: FLOW-004`, `source.scope` accurately describes the chunk
- [ ] `status: planned`, `assigned_release: null`
- [ ] `requ-assign-packages` can now fuzzy-match this chunk label to a backlog package

## Notes

This task was auto-created by `requ-assign-packages` prerequisite guard on 2026-04-20.
The chunk "Notification System" appears in FLOW-004 `release_scope` at priority 2.
The nearest existing package is "Transfer Notifications" (0.0.1, REQ-FUNC-007) but that covers QR-transfer reminders, not FLOW-004 file-transfer notification lifecycle.
