---
task_id: TASK-PROC-039-02
type: impl
parent_requirement: REQ-PROC-039
urgency: 3
urgency_reason: U3-WORKFLOW-GAP
impact: 3
impact_reason: I3-CONSISTENCY
status: completed
completed: 2026-03-28
created: 2026-03-26
started: 2026-03-28
effort: S
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "CONTINUE iteration on FLOW-002 (Instruct Client on Protocol) to address impacts identified when FLOW-004 (Flexible Data Transfer) reached content_complete"
release_description: ""
related_flows:
  - FLOW-002
  - FLOW-004
---

# Goal: Align FLOW-002 with FLOW-004 (Flexible Data Transfer)

## Context

FLOW-004 (Flexible Data Transfer) reached content_complete on 2026-03-26.
Cross-flow impact analysis identified that FLOW-002 (Instruct Client on Protocol) needs alignment.

## Known Impact (at task creation)

- **Shared notification lifecycle**: FLOW-002 Step 12 references scheduled transfer notifications. FLOW-004's "persist until done" notification lifecycle must be reconciled with FLOW-002's notification scheduling model — coexistence without suppression.
- **Global notification time mapping**: FLOW-002 establishes abstract label → clock time mapping. FLOW-004's therapist-side reminder notification (Exception 2.1) must respect these global settings. FLOW-002 should explicitly state that global time settings apply to all notification types, including transfer reminders.
- **Multi-therapist pairing model**: FLOW-002 Exception 1.1A (client switching therapist) and FLOW-004's pairing-level email configuration use the same multi-therapist model. Both flows must share consistent assumptions about how pairings are stored, keyed, and selected.
- **Audio guidance per question (Open Question 10)**: FLOW-004 explicitly supports audio file transfer, removing the transfer capacity constraint that caused FLOW-002 Open Question 10 to be deferred. The question should be revisited.

## Source Flow

- Flow: FLOW-004
- Path: `requirements_user_needs/user_flows/flexible_data_transfer/flow.md`
- Content complete: 2026-03-26

## Steps

1. Run CONTINUE on FLOW-002 (`ux-create-flow` CONTINUE MODE)
   - FLOW-004 is in `pending_alignment` — it will be auto-read as context (Step 6 sibling check)
   - Address all entries in the `## Pending Impacts` section of FLOW-002's flow.md
2. When CONTINUE is done: FLOW-002 enters `pending_alignment`

## Additional Impact from FLOW-003 (2026-03-28)

FLOW-003 (Session Start & Data Transfer) reached content_complete on 2026-03-28.
Two additional impacts identified for FLOW-002:

- **Time-based detection model**: FLOW-003 Step 5 specifies Complete button disabled until minimum transfer duration elapsed; Discard always active. FLOW-002 Step 5 and Exception 1.6 still use the old confirmation model and do not reflect this.
- **Transfer section navigation model**: FLOW-003 specifies returning users go directly to QR Transfer Screen; first-time users auto-see Transfer Detail Screen (toggle-governed). FLOW-002 Step 5 does not distinguish these navigation paths.

A `## Pending Impacts` section has been added to FLOW-002's flow.md with these impacts.

## Important: No Cascading

This task was triggered by a cross-flow impact sweep.
When completing this task, do NOT trigger another cross-flow impact sweep.
