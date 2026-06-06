---
task_id: TASK-PROC-027-19
type: impl
parent_requirement: REQ-PROC-027
urgency: 4
urgency_reason: U4-IMPL
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-02-14
completed: 2026-02-21
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: >
  Create user flow FLOW-002 for the "Instruct Client on Protocol" scenario category
  (distribution.instruct_client). Bridges therapist-side instruction scenarios
  (SCEN-001-03 gold standard) and client-side reception scenarios (SCEN-002-04 gold standard)
  with the existing digital transfer requirements in epic_data_transfer (REQ-FUNC-007).
  Requires analysis phase with user review checkpoint before flow creation begins.
requirements_version:
  commit: edb2b1e
  file: ../requirements.md
---

# Goal: Create User Flow for "Instruct Client on Protocol"

## Objective

Create user flow FLOW-002 that covers the "Instruct Client on Protocol" scenario category
(SCENARIO_INDEX stage `distribution.instruct_client`). This is the moment a therapist
distributes a protocol to a client — physically or digitally — and instructs them on how
to use it.

**Critical constraint**: This is the **first user flow created using the new workflow**
(create-user-flow skill + cross-referencing READMEs). The process itself is being tested
for the first time. See TASK-PROC-010-16 for the follow-up review of this workflow.

**This is NOT just**: implementing what `epic_data_transfer` requirements specify, nor
just serving what the user needs scenarios describe. The goal is to **synthesize both**
into a flow that reflects what the app experience should feel like in the real therapy
session moment.

---

## Background: The Tension to Resolve

The existing requirements in `epic_data_transfer` (REQ-FUNC-007) were created based on
Figma designs that preceded the personas. They describe the digital transfer mechanics
(QR beam, file export, pairing) in technical detail but without grounding in the
emotional/contextual reality of the therapy session.

The user needs scenarios (`instruct_client_on_protocol`) describe the **analog status quo**:
therapist hands paper protocol across the table, walks through columns, discusses barriers
like "what if I forget a day?" or "what if someone sees it?". The scenarios were created
without the digital implementation in mind.

The user flow must bridge these two worlds: the therapist's session moment (instructing
the client on a protocol) AND the app-side digital transfer mechanics — revealing what
the app should actually support in this situation.

---

## Mandatory Pre-Creation Analysis Phase

**IMPORTANT**: Before invoking the `create-user-flow` skill, you MUST complete a
structured analysis. The analysis output goes into `plans_and_protocols/` and requires
user review/approval before proceeding.

### Step 1: Read All Relevant Scenarios (parallel reads)

**Therapist-side (instruct_client_on_protocol)**:
- `requirements_user_needs/personas/dr_sarah/scenarios/instruct_client_on_protocol/scenario.md` (SCEN-001-03, gold standard)
- `requirements_user_needs/personas/prof_dr_weber/scenarios/instruct_client_on_protocol/scenario.md` (SCEN-011-03)
- `requirements_user_needs/personas/dr_med_turan/scenarios/instruct_client_on_protocol/scenario.md` (SCEN-012-03)

**Client-side (receive_protocol_homework)**:
- `requirements_user_needs/personas/max_client/scenarios/receive_protocol_homework/scenario.md` (SCEN-002-04, gold standard)
- `requirements_user_needs/personas/sophie_structure_seeker/scenarios/receive_protocol_homework/scenario.md` (SCEN-010-03)
- `requirements_user_needs/personas/jana_high_strung/scenarios/receive_protocol_homework/scenario.md` (SCEN-014-03)
- `requirements_user_needs/personas/elias_skeptical_guardian/scenarios/receive_protocol_homework/scenario.md` (SCEN-009-01)
- `requirements_user_needs/personas/lena_depth_seeker/scenarios/receive_protocol_homework/scenario.md` (SCEN-016-01)

**Requirements**:
- `requirements_tasks/functional/shared/epic_data_transfer/requirements.md` (REQ-FUNC-007)
- `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/requirements.md` (REQ-FUNC-007-01)
- `requirements_tasks/functional/shared/epic_data_transfer/feat_plan_receiving/requirements.md`

### Step 2: Analyze and Document

Write a structured analysis to `plans_and_protocols/2026-02-14_01_analysis_requirements_vs_user_needs.md` covering:

1. **What the requirements assume** about the session moment (explicit or implicit)
2. **What the scenarios describe** as the real session context
3. **Gaps**: Requirements that have no user needs grounding
4. **Tensions**: Requirements that conflict with how the session actually works
5. **Missing**: User need moments that the requirements don't address
6. **Synthesis recommendations**: What the flow should emphasize, what should be an exception,
   what the "happy path" should look like from a real therapist's perspective

### Step 3: USER REVIEW CHECKPOINT

**STOP HERE**. Present the analysis to the user and ask for feedback. The user wants
to review this analysis before the flow is created, so it can be improved incrementally.

Only proceed to flow creation after explicit user approval.

---

## Flow Creation Phase (after user review)

After user approval of the analysis, invoke the `create-user-flow` skill to create
the flow. Provide the skill with:

- Flow name: "Instruct Client on Protocol" → folder: `instruct_client_on_protocol`
- Flow ID: FLOW-002 (next available per id_registry)
- Serving scenarios: All 8 scenarios listed above (both therapist and client sides)
- Evidence level: grounded (based on 3 therapist gold scenarios + 5 client scenarios)
- Epic link: REQ-FUNC-007 (epic_data_transfer)
- Feature links: REQ-FUNC-007-01 (feat_therapist_transfer_ui) + feat_plan_receiving

**Key design decisions for the flow** (based on analysis synthesis):
- The happy path must reflect a REAL therapy session flow, not just a feature walkthrough
- The flow spans BOTH therapist and client perspectives (unlike most flows which are
  single-persona)
- The analog instruction moment (therapist explains protocol) is just as important as
  the digital transfer — do not collapse the instruction into "click button"
- Include the emotional context: therapist's limited session time, client's cognitive
  state at handover, privacy barriers

---

## Scope

### In Scope
- User flow FLOW-002 file at `requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md`
- Bidirectional references: all 8 scenarios updated with `implements_flows`
- Epic/feature bidirectional references (epic_data_transfer YAML `user_needs` field)
- Analysis document in `plans_and_protocols/`
- User review checkpoint between analysis and creation

### Out of Scope
- Creating new scenarios (use existing instruct_client_on_protocol + receive_protocol_homework)
- Modifying the requirements in epic_data_transfer (flow creation does not change requirements)
- Implementation of the flow in code (this is a user needs artifact only)
- Client-side feat_plan_receiving requirements (may be noted as gaps but not defined here)

---

## Acceptance Criteria

- [ ] Analysis document in plans_and_protocols/ covers gaps, tensions, and synthesis
- [ ] User has reviewed and approved the analysis (documented in protocol file)
- [ ] User flow FLOW-002 created at `requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md`
- [ ] Flow uses exception model with numbered exceptions per README_5
- [ ] Flow is technology-neutral per README_15
- [ ] All 8 scenarios updated with bidirectional `implements_flows` references
- [ ] `epic_data_transfer/requirements.md` has `user_needs.implements_flows` updated
- [ ] `feat_therapist_transfer_ui/requirements.md` has `user_needs.implements_flows` updated
- [ ] Flow `review_status: draft` with `review_history` entry added
- [ ] ID registry regenerated after flow creation

---

## Key References

| Document | Why |
|----------|-----|
| `requirements_user_needs/SCENARIO_INDEX.md` | Stage: distribution.instruct_client |
| `requirements_user_needs/README_5_USER_FLOW_DEFINITION.md` | Flow template and exception model |
| `requirements_user_needs/README_8_CROSS-REFERENCING_SYSTEMS.md` | Bidirectional links |
| `requirements_user_needs/README_13_CROSS_REFERENCE_NOTATION.md` | YAML reference format |
| `requirements_user_needs/README_14_DEVIATION_DOCUMENTATION.md` | Documenting deviations |
| `requirements_user_needs/README_15_TECHNOLOGY_NEUTRALITY.md` | Technology-agnostic language |
| `.claude/skills/create-user-flow/skill.md` | Skill to invoke for creation phase |

---

## Notes

- Gold standard therapist scenario: SCEN-001-03 (Dr. Sarah, approved)
- Gold standard client scenario: SCEN-002-04 (Max, approved)
- All instruct_client_on_protocol therapist scenarios currently have `review_status: draft` —
  warn during creation but proceed (per skill guidelines)
- The analysis phase is the most critical part. Rushing to flow creation without it
  risks creating a flow that reflects the Figma prototype rather than real user needs.
- Follow-up task TASK-PROC-010-16 will review this task's protocols and update the
  create-user-flow workflow if needed.

Current requirements:
```
git show edb2b1e:requirements_tasks/process/AI_rules/requirements_management/user_needs_content/requirements.md
```
