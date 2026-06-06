---
task_id: TASK-PROC-027-14
type: impl
parent_requirement: REQ-PROC-027
urgency: 4
urgency_reason: U4-IMPL
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-04-19
session_completed_at: 2026-04-19T17:43:15Z
started: 2026-03-20
effort: M
created: 2026-02-22
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: >
  Iteratively improve FLOW-003 "Session Start & Data Transfer" based on user feedback
  until the user approves it (review_status: approved). The initial flow was created
  as a draft. Each iteration: incorporate feedback → present to user → collect new
  feedback → repeat until approved.
related_flows:
  - FLOW-003
requirements_version:
  commit: edb2b1e
  file: ../requirements.md
---

# Goal: Improve & Approve User Flow — Session Start & Data Transfer (FLOW-003)

## Objective

FLOW-003 has been created as a draft. The goal is now to **iteratively improve it until the user approves it**.

Each iteration:
1. Incorporate feedback from `user_feedback/` into `flow.md`
2. Present the changed sections to the user for review
3. Collect new feedback (user adds a new feedback file to `user_feedback/`)
4. Repeat until user grants approval → set `review_status: approved` in flow.md frontmatter

**Skill to use**: `ux-update` (for each iteration)

---

## Current State

- Flow exists at: `requirements_user_needs/user_flows/session_start_data_transfer/flow.md`
- Review status: `draft`
- Pending feedback: `user_feedback/2026-03-20_feedback.md`

---

## Context

### Why this flow exists

The current `review_data_collaboratively` scenario stage (SCEN-001-02, SCEN-011-02, SCEN-012-02) and `transfer_data_to_therapist` stage (SCEN-002-02, SCEN-010-01, SCEN-014-02) document the pain of the current paper-based handover. This flow defines the digital replacement for that moment.

### Why the split (transfer ≠ analysis)

The analysis phase has significant variance per therapist/client persona combination:
- Dr. Sarah explores emotional patterns differently than Prof. Dr. Weber
- A Max session looks different from a Jana session
- Each persona pair warrants its own dedicated analysis flow

The data transfer + visualization opening is the **universal entry point** into all those analysis flows. It makes sense as a standalone, persona-agnostic foundation.

### Related flow index entries

From `requirements_user_needs/user_flows/FLOW_INDEX.md`:
- **FLOW-004 brainstorm ref** "Data Handover (Client Sends)": Transmission moment, selective transfer (therapy data ONLY; private diaries stay private), offline/QR-code "Data Beam". Mapped to `analysis.transfer_to_therapist` stage.
- **FLOW-014 brainstorm ref** "Therapist Reception & Storage": Therapist-side of the transfer moment, permanent local storage in encrypted "Patient Silo".

This new flow COMBINES both sides into a single dual-perspective flow (same structure as FLOW-002).

### Flow ID

The next available flow ID is **FLOW-003**. Register it in `FLOW_INDEX.md` when creating.

---

## Scope

### In Scope
- Incorporating feedback from `user_feedback/` files into `flow.md`
- Iterating on happy path, exceptions, adaptive UI rules, and domain concepts as directed by feedback
- Presenting changes to the user after each iteration
- Setting `review_status: approved` once the user signals approval

### Out of Scope
- Deriving requirements from the approved flow (that is the `requ-derive-from-flow` skill, run after approval)
- Modifying related scenarios or personas
- Implementation of any features described in the flow

---

## Scenarios Served

| Stage | Scenario ID | Persona | Notes |
|-------|-------------|---------|-------|
| `transfer_data_to_therapist` | SCEN-002-02 | Max (PERSONA-002) | Failure outcome — digital flow solves this |
| `transfer_data_to_therapist` | SCEN-010-01 | Sophie (PERSONA-010) | Success outcome — maps well to digital handover |
| `transfer_data_to_therapist` | SCEN-014-02 | Jana (PERSONA-014) | Check SCENARIO_INDEX for details |
| `review_data_collaboratively` | SCEN-001-02 | Dr. Sarah (PERSONA-001) | Therapist side — row-by-row scanning pain solved |
| `review_data_collaboratively` | SCEN-011-02 | Prof. Dr. Weber (PERSONA-011) | Therapist side |
| `review_data_collaboratively` | SCEN-012-02 | Dr. med. Turan (PERSONA-012) | Therapist side |

---

## Acceptance Criteria

- [x] FLOW-003 created at `requirements_user_needs/user_flows/session_start_data_transfer/flow.md`
- [x] Flow covers both client and therapist perspective (dual-perspective)
- [x] Happy path defined
- [x] Key exceptions documented
- [x] Selective data privacy documented
- [x] Flow ends at visualization open — analysis marked out of scope
- [x] `FLOW_INDEX.md` updated: FLOW-003 in "Existing Flows"
- [ ] All pending feedback from `user_feedback/` incorporated
- [ ] Flow has `review_status: approved` (user-approved after iteration)

---

## Notes

- This flow is the **universal entry point** into all future collaborative analysis flows
- Keep the transfer mechanism technology-neutral in the flow itself where possible — the QR "Data Beam" is an implementation choice, but the flow should describe the user experience, not the protocol
- The selective privacy boundary (therapy data vs. private diary) is a critical design decision — surface it explicitly in the flow
- Reference `requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md` (FLOW-002) as a structural model for dual-perspective flows
