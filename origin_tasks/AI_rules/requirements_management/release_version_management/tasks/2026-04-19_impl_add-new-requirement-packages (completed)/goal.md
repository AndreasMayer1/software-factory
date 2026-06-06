---
task_id: TASK-PROC-034-14
type: impl
parent_requirement: REQ-PROC-034
urgency: 5
urgency_reason: U5-BLOCK
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-04-19
session_completed_at: 2026-04-19T16:25:58Z
effort: S
created: 2026-04-19
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01]
scope_description: "Add three new packages to RELEASE_BACKLOG.md for requirements that have no existing package match: Voice Transcription, App Donations, Therapeutic Materials"
release_description: "All requirement ACs have a corresponding backlog package for release planning."
opus_recommended: false
worktree_path: ""
requirements_version:
  commit: 178339b8
  file: ../requirements.md
---

# Goal: Add New Packages to RELEASE_BACKLOG.md for Unmatched Requirements

## Objective

Run `release-plan → Action 4` to add three new package entries to `requirements_tasks/RELEASE_BACKLOG.md`. These packages were assigned to requirements during `requ-assign-packages` (2026-04-19) but don't yet exist in the backlog.

## Requirements Summary

REQ-PROC-034 requires every `target_package` value to exist in RELEASE_BACKLOG.md.

Current requirements: ../requirements.md

## Scope

### In Scope
Add the three packages below to RELEASE_BACKLOG.md with `status: planned`, `assigned_release: null`, and an appropriate position in the backlog.

### Out of Scope
Assigning the new packages to specific release versions (that is a separate release-plan step).

## Packages to Add

| Package Name | Source Requirement | Notes |
|---|---|---|
| `"Voice Transcription"` | REQ-FUNC-007-11 (all 9 ACs) | On-device speech-to-text for voice-recorded entries; depends on REQ-FUNC-007-05 (client data model) and REQ-FUNC-007-10 (file transfer protocol) |
| `"App Donations"` | feat_donations (all 7 ACs) | Voluntary IAP / URL-based donation; post-MVP, low priority |
| `"Therapeutic Materials"` | feat_education (all 3 ACs) | Therapist-attached PDFs/audio/links in plans; post-MVP |

## Acceptance Criteria

- [ ] `"Voice Transcription"` entry exists in RELEASE_BACKLOG.md with `status: planned`
- [ ] `"App Donations"` entry exists in RELEASE_BACKLOG.md with `status: planned`
- [ ] `"Therapeutic Materials"` entry exists in RELEASE_BACKLOG.md with `status: planned`
- [ ] `python3 scripts/sync_requirement_packages.py` reports no unassigned items for REQ-FUNC-007-11, feat_donations, feat_education

## Notes

Triggered by: `requ-assign-packages` skill — Step 3 no-match list (2026-04-19 session).
Also see: TASK-PROC-034-13 (unformalized flow chunk labels — separate but related).
