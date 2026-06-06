---
task_id: TASK-PROC-032-09
type: impl
parent_requirement: REQ-PROC-032
urgency: 2
urgency_reason: U2-OPP
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-27
completed: 2026-05-27
session_completed_at: 2026-05-27T12:02:47Z
effort: M
created: 2026-05-26
after: [TASK-PROC-055-02, TASK-PROC-055-03, TASK-PROC-055-04]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Improve ui-create-scribble skill: flow scope filter, impossible-state gate, impl-notes input, and han-inspired patterns from TASK-PROC-055-02/03/04"
release_description: ""
opus_recommended: false
requirements_version:
  commit: b58e7cca
  file: ../requirements.md
session_id: 3ba6c213-cc16-477d-9e58-fe4e1d32e651
session_account: gmail2
---
# Goal: Improve ui-create-scribble — Flow Scope, Impossible States, han Patterns

## Objective

Update the `ui-create-scribble` skill to address four structural gaps identified in the
TASK-PROC-032-08 analysis of TASK-FUNC-007-01-05's scribble output, and to incorporate
any applicable han-inspired patterns from TASK-PROC-055-02/03/04 once those are complete.

All skill edits MUST go through `claude-modify-skill` (syncs INDEX.md + factory_flows.md).

## Requirements Summary

Analysis source: `tasks/2026-05-26_analyze_scribble-quality-task-func-007-01-05/plans_and_protocols/2026-05-26_01_analysis_scribble-quality.md`

Han-inspiration sources (read after after-tasks complete):
- TASK-PROC-055-02: YAGNI evidence gate → screen-state evidence test
- TASK-PROC-055-03: sizing-before-dispatch → pre-generation screen count estimate
- TASK-PROC-055-04: adversarial-validator pilot → Phase 2 information-model challenger

Current requirements: ../requirements.md

## Scope

### In Scope

**1. Flow scope filter (High)**

Phase 1 currently reads the full user flow for step ordering but does not filter to
the steps that belong to the current requirement. Fix: pass the full flow as read-only
context to Phase 1 agent, but restrict screen generation to the `steps[]` list from
`requirements.md`'s `user_needs.implements_flows[].steps` field. Exception paths are
in-scope only if covered by the requirement's own ACs/sections.

**2. Impossible-state gate (High)**

Phase 1 agent does not reason about what information is available on each app side
before designing screens. Fix:
- Phase 1 pre-generation step: agent reads the flow's Domain Concepts section and any
  requirement section describing channel/system model; derives an explicit
  "unavailable information" list; each screen state must be consistent with that list.
- Phase 2 auto-review: add checklist item — "for every non-trivial state panel, is the
  data required to render it available on this app side?"

**3. Implementation notes input (Medium)**

Phase 1 and Phase 2 do not read `implementation_notes.md` if present next to a flow.
Fix: both phases check the flow folder for `implementation_notes.md` before generating
or reviewing; if found, treat it as authoritative technical context alongside flow.md.

**4. han-inspired patterns (read after-tasks first)**

Read the protocols of TASK-PROC-055-02, TASK-PROC-055-03, TASK-PROC-055-04 before
deciding how to apply their patterns to the scribble skill. Likely applications:

- **From TASK-PROC-055-02 (YAGNI gate)**: Phase 2 should ask for each screen state:
  "Is there evidence in the requirement or flow that this state can occur AND that the
  system has the data to render it?" States failing the evidence gate are flagged, not
  silently generated.
- **From TASK-PROC-055-03 (sizing)**: Before Phase 1 generates screens, announce the
  expected screen count band (small: 1–3, medium: 4–7, large: 8+) based on the number
  of ACs + flow steps in scope. Calibrate Phase 2 iteration depth to that band.
- **From TASK-PROC-055-04 (adversarial-validator pilot)**: If the pilot agent is active
  in code-complex, consider wiring it optionally into Phase 2 of the scribble workflow
  as a challenger step for impossible states and flow-coverage gaps. Only if the pilot
  showed measurable signal (OR-5 re-test) and the agent is self-contained.

**5. Secondary improvements (Medium/Low)**

- flow_positions: require `exception_id` annotation for exception-path screens
- Domain class name cross-reference in component mapping when domain classes exist
- Auto-promote component candidates appearing in ≥3 screens to `provisional` status
  after Phase 2

### Out of Scope

- Answering the pending question for TASK-FUNC-007-01-05 (that is the user's decision)
- Fixing the stale zone letter labels in `transfer_detection_zone.dart` comments
  (separate small task; no skill changes needed)
- Adding a tablet-resolution variant (Low priority; defer to a follow-up)

## Acceptance Criteria

- [x] Phase 1 prompt uses `steps[]` filter to scope screen generation; full flow
      remains available as context
- [x] Phase 1 pre-generation step derives "unavailable information" list from Domain
      Concepts + requirement channel model
- [x] Phase 2 checklist includes information-model consistency check per state panel
- [x] Phase 1 and Phase 2 read `implementation_notes.md` from flow folder if present
- [x] han patterns from TASK-PROC-055-02/03/04 are applied where signal was confirmed;
      inapplicable patterns are explicitly noted with reason in the protocol
- [x] All edits done via `claude-modify-skill`
- [x] At least one existing scribble (re-run or manual check) validates the new Phase 1
      pre-generation step catches an impossible state that the old version would have missed

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-055-02 | pending | YAGNI gate → evidence-based screen-state check |
| TASK-PROC-055-03 | pending | Sizing → pre-generation screen count + iteration depth |
| TASK-PROC-055-04 | pending | Adversarial-validator pilot → optional Phase 2 challenger |
| TASK-PROC-032-08 | completed | Analysis that identified all gaps above |

## Notes

Read `tasks/2026-05-26_analyze_scribble-quality-task-func-007-01-05/plans_and_protocols/2026-05-26_01_analysis_scribble-quality.md`
in full before starting. All proposals are documented there with priority and rationale.

The TASK-PROC-055 after-tasks are blocking because their han-derived patterns may change
the shape of improvements 1–3 (e.g., the YAGNI gate and the impossible-state gate are
closely related). Implement both together to avoid two rounds of `claude-modify-skill`
on the same skill file.
