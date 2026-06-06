---
task_id: TASK-PROC-027-10
type: explore
parent_requirement: REQ-PROC-027
urgency: 2
urgency_reason: U2-FUTURE
impact: 3
impact_reason: I3-UX
status: pending
effort: S
created: 2026-04-05
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore backup verification / paranoid mode for FLOW-011 (Backup & Migration)"
related_flows:
  - FLOW-011
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Explore: Backup Verification / Paranoid Mode

## Objective

Decide whether the app should offer an automated restore-test ("paranoid mode") that users can explicitly enable to verify that a just-created backup can be successfully restored.

## Context

FLOW-011 (Backup & Migration) currently creates a backup file and considers the flow complete. There is no verification step that confirms the backup is readable and restorable. For users who treat their mood data as important long-term records, a silent backup that turns out to be corrupt is a serious trust failure.

"Paranoid mode" would address this by automatically performing a trial restore (into a temporary sandbox) immediately after backup creation, then confirming to the user that the backup is valid. This is a user-toggled feature — the user opts in, accepts the extra time cost, and receives explicit confirmation.

This decision directly affects FLOW-011 by potentially adding:
- A post-backup verification step (conditional on the toggle being on)
- A settings touchpoint where paranoid mode is enabled/disabled
- A result screen variant: "Backup verified" vs. "Backup complete (unverified)"

## Key Questions

1. Is backup integrity a real concern for the target users, or is it too technical/niche to surface in the UI?
2. Should paranoid mode be opt-in (default off) or opt-out (default on for first backup)?
3. What should the UX look like when verification fails — is it recoverable, and what does the user do next?
4. Does the verification run in the foreground (user waits) or background (user is notified later)?
5. Is this distinct from a manual "Test restore" action, or are they the same feature?

## Out of Scope

- The technical mechanism for sandboxed restore (implementation detail).
- Backup file checksums / hash verification at the file level (lower-level integrity check; separate from a full restore test).
- Cloud backup verification (separate requirement).
