---
task_id: TASK-PROC-027-38
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-CTX
impact: 3
impact_reason: I3-ALIGN
status: pending
effort: S
created: 2026-03-31
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-04]
scope_description: "Align FLOW-004 (Flexible Data Transfer) with FLOW-003 non-color redundancy and WCAG success animation annotation"
release_description: ""
---

# Goal: Align FLOW-004 with FLOW-003 Accessibility Constraints

## Context

FLOW-003 (Session Start & Data Transfer) reached content_complete on 2026-03-31.
Cross-flow impact analysis identified that FLOW-004 needs alignment.

FLOW-004 also has an existing Pending Impact from FLOW-002 (success animation WCAG 2.3.1 annotation).
Both sets of impacts should be addressed in the same CONTINUE pass.

## Known Impacts (at task creation)

**From FLOW-002 (already in Pending Impacts before this task)**:
- Step 6 success animation: WCAG 2.3.1 annotation (≤3Hz, no strobing) + OS Reduce Motion static fallback

**From FLOW-003 (new)**:
- Step 9 / Adaptive UI Rules: non-color redundancy constraint — color cannot be sole data encoding in Client Data View visualization; secondary encodings required (text labels, patterns, shapes)
- Transfer Detail Screen description: note that fast transfer preference toggle is present as shared component but not applicable in FLOW-004 file-export context

## Source Flow

- Flow: FLOW-003 (Session Start & Data Transfer)
- Path: requirements_user_needs/user_flows/session_start_data_transfer/flow.md
- Content complete: 2026-03-31

## Steps

1. Run CONTINUE on FLOW-004 (`ux-create-flow CONTINUE MODE` or `"Do FLOW-004"`)
   - FLOW-004 is in `in_review` with a `## Pending Impacts` section — address all entries
   - This is also Pass 3 of the TASK-PROC-027-36 accessibility cascade (FLOW-004 was the last remaining flow)
2. When CONTINUE is done: signal "content complete FLOW-004" when satisfied
3. When ALL cluster flows are aligned (FLOW-002, FLOW-003, FLOW-004): run Joint Approval
