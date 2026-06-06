---
task_id: TASK-PROC-027-34
type: explore
parent_requirement: REQ-PROC-027
urgency: 2
urgency_reason: U2-NICE
impact: 3
impact_reason: I3-UX
status: pending
effort: M
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: "Explore and define the Therapy End / Patient Handover flow — the transition from therapist-guided tracking to patient self-management"
requirements_version:
  commit: 981a53a
  file: ../requirements.md
---

# Goal: Explore Therapy End / Patient Handover Flow

## Objective

Define the user flow for the end of a therapy relationship: what happens when a patient's formal therapy ends and they transition to self-managed tracking. This is a gap identified during the Gemini scenario consolidation (TASK-PROC-027-20) — the declined scenario *"The Discharge Folder"* (Dr. Sarah, PERSONA-001) surfaced a real feature need that has no analog in the current flow inventory.

## Background

When therapy ends today, the patient simply keeps their paper stack (or doesn't). A digital app needs an equivalent structured handover moment:

- A curated **end-of-therapy package** that the therapist composes and the patient takes away
- May include: session summary, skill cards, self-care plan, data export in an accessible format
- The patient transitions from "guided user" (therapist sets the protocol) to "self-user" (patient sets their own protocol)
- The app's role shifts from a clinical data capture tool to a personal self-monitoring tool

This is **not** a simple data export — it is a meaningful UX transition moment that needs its own flow.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Declined scenario: *The Discharge Folder* (Dr. Sarah perspective)
- Protocol note: `plans_and_protocols/2026-03-02_01_protocol_evaluation.md` — Consolidation Addendum
- Related flow area: FLOW-020 (if it exists) or a new flow to be defined

## Questions to Answer

1. **Who initiates the handover?** Therapist only, or can patient request it?
2. **What is included?** What data does the therapist select vs. what is automatic?
3. **What does the patient receive?** A snapshot export? A new "self-user mode"?
4. **What persists and what ends?** Does the therapist lose access after handover? Does the tracking protocol revert to a default?
5. **Is there a grace period?** Can the patient re-contact the therapist digitally after therapy ends?
6. **Relevant personas**: Dr. Sarah (PERSONA-001) initiates; which client personas experience this? Max (PERSONA-002), Sophie (PERSONA-010), Jana (PERSONA-014)?
7. **Overlap with existing flows**: How does this relate to the existing data management flows (FLOW-011, FLOW-013, FLOW-016)?

## Deliverables

- [ ] Flow definition document (user flow artifact) in `requirements_user_needs/flows/`
- [ ] Identification of any new scenarios warranted by this flow (or confirmation that existing scenarios cover the patient experience)
- [ ] Any new requirements surfaced (NFRs, data model implications, access control implications)
- [ ] Assessment of whether a corresponding *patient-side* scenario is needed (the client's experience of therapy ending)

## Skills

- Use `ux-create-flow` to define the flow once the exploration is complete
- Use `requ-explore` if the scope expands beyond flow definition

## Acceptance Criteria

- [ ] Flow defined and documented following the project's flow standards
- [ ] FLOW_INDEX updated with new flow
- [ ] Open questions above answered or explicitly deferred with reasoning
- [ ] Any new scenario needs identified and filed as follow-up tasks
