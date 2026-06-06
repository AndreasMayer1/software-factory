---
task_id: TASK-PROC-034-13
type: impl
parent_requirement: REQ-PROC-034
urgency: 5
urgency_reason: U5-BLOCK
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-04-19
started: 2026-04-19
completed: 2026-04-19
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-04]
scope_description: "Formalize unmatched flow chunk labels from flexible_data_transfer, instruct_client_on_protocol, and session_start_data_transfer flows into RELEASE_BACKLOG.md packages via release-plan → Action 4b"
release_description: "All user flow release chunks have corresponding backlog packages for planning."
opus_recommended: false
worktree_path: ""
requirements_version:
  commit: 178339b8
  file: ../requirements.md
---

# Goal: Formalize Unmatched Flow Chunk Labels into RELEASE_BACKLOG.md Packages

## Objective

Run `release-plan → Action 4b` to create RELEASE_BACKLOG.md package entries for all flow chunk labels that currently have no matching package. This unblocks `requ-assign-packages` from using Signal 2 (matrix-derived chunk matching) for functional requirements.

## Requirements Summary

REQ-PROC-034 requires that every `release_scope` chunk label in user flows has a corresponding package in RELEASE_BACKLOG.md. Package names follow: max 4 words, subject-first, no timing words.

Current requirements: ../requirements.md

## Scope

### In Scope
- Add RELEASE_BACKLOG.md entries for all 10 unmatched chunk labels listed below
- Set `status: planned` and `assigned_release: null` for each new package
- Get user approval for each package name before writing

### Out of Scope
- Assigning new packages to release versions (that is release-plan → Action 5)
- Modifying existing packages

## Unmatched Chunks (from requ-assign-packages prerequisite guard run 2026-04-19)

| Chunk Label | Flow |
|---|---|
| "Scope Controls & Interrupted Transfer" | flexible_data_transfer |
| "Audio Export" | flexible_data_transfer |
| "Silent Failure Mitigations & Device Resilience" | flexible_data_transfer |
| "Returning Client & Re-transfer" | instruct_client_on_protocol |
| "Session Variants" | instruct_client_on_protocol |
| "Phase 2 Edge Cases" | instruct_client_on_protocol |
| "File Transfer" | session_start_data_transfer |
| "Setup & Pairing" | session_start_data_transfer |
| "Remote Sessions" | session_start_data_transfer |
| "Edge Cases & Resilience" | session_start_data_transfer |

## Acceptance Criteria

- [ ] All 10 chunk labels have a matching entry in RELEASE_BACKLOG.md (exact or approved fuzzy match)
- [ ] Each new entry follows naming convention: 2-4 words, subject-first, no timing/implementation jargon
- [ ] User approved each package name
- [ ] `requ-assign-packages` prerequisite guard passes without warnings after this task

## Notes

Triggered by: `requ-assign-packages` skill — Step 2 prerequisite guard (2026-04-19 session).
