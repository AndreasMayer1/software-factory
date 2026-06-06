---
task_id: TASK-PROC-027-37
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-CTX
impact: 3
impact_reason: I3-ALIGN
status: completed
completed: 2026-04-19
session_completed_at: 2026-04-19T17:58:08Z
effort: S
created: 2026-03-31
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-04]
scope_description: "Align FLOW-002 (Instruct Client on Protocol) with FLOW-003 fast transfer consent model redesign"
release_description: ""
---

# Goal: Align FLOW-002 with FLOW-003 Fast Transfer Consent Redesign

## Context

FLOW-003 (Session Start & Data Transfer) reached content_complete on 2026-03-31.
Cross-flow impact analysis identified that FLOW-002 needs alignment.

## Known Impact (at task creation)

FLOW-003 redesigned the Transfer Speed Preference consent model:
- **Old model**: contextual prompt fires when estimated transfer duration is high (duration-triggered)
- **New model**: one-time safety-consent prompt, fires once when fast mode is first mutually available (not duration-triggered)
- **New phrasing**: "Fast mode uses quicker QR animations — some users are sensitive to fast-moving patterns. Only enable if that's OK for you."
- **Adaptive UI Rules**: fast transfer consent rule and file transfer suggestion rule are now fully separate in FLOW-003

FLOW-002 defines the Transfer Speed Preference mechanism and must be updated to reflect both the new trigger model and the rule separation.

## Source Flow

- Flow: FLOW-003 (Session Start & Data Transfer)
- Path: requirements_user_needs/user_flows/session_start_data_transfer/flow.md
- Content complete: 2026-03-31

## Steps

1. Run CONTINUE on FLOW-002 (`ux-create-flow CONTINUE MODE` or `"Do FLOW-002"`)
   - FLOW-002 is in `pending_alignment` — the `## Pending Impacts` section in flow.md lists exact changes needed
   - Address all entries in that section
2. When CONTINUE is done: signal "content complete FLOW-002" when satisfied
3. When ALL cluster flows are aligned (FLOW-002, FLOW-003, FLOW-004): run Joint Approval
