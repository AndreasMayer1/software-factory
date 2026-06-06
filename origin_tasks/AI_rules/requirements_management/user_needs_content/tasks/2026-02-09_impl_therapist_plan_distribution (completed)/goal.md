---
task_id: TASK-PROC-027-11
type: impl
parent_requirement: REQ-PROC-027
urgency: 4
urgency_reason: U4-IMPL (inherited - blocks user flow design for plan distribution)
impact: 4
impact_reason: I4-QUAL (inherited - completes critical gap in scenario coverage)
status: completed
completed: 2026-02-14
effort: M
created: 2026-02-09
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Create three standalone therapist-side plan distribution scenarios to close the gap identified in SCENARIO_INDEX.md"
requirements_version:
  commit: edb2b1e
  file: ../requirements.md
---

# Goal: Create Standalone Therapist-Side Plan Distribution Scenarios

## Objective

Create three new standalone scenarios under category `distribution.instruct_client` (canonical name: `instruct_client_on_protocol`) for the therapist-side perspective of plan handover. This closes a critical gap identified in SCENARIO_INDEX.md line 161-163.

**Context**: Currently, plan distribution (Planübergabe) scenarios exist only from the client perspective:
- 5 client scenarios: `receive_protocol_homework` (Max, Sophie, Jana, Elias, Lena)
- 0 therapist scenarios: The handover is currently embedded in Act 3 of `prepare_protocol_for_client` scenarios

SCENARIO_INDEX.md explicitly flags this as a gap: *"Currently embedded in SCEN-001-01 Act 3, not standalone"*

## Requirements Summary

Create three scenarios that extract and expand the handover moment from existing `prepare_protocol_for_client` scenarios, giving each therapist's unique handover style its own story. USE CREATE SCENARIO SKILL FOR EACH.

1. **Dr. Sarah** - The didactic handover (10 min session time)
2. **Prof. Dr. Weber** - The ritual handover (analog invitation)
3. **Dr. med. Turan** - The efficient medical handover (90 seconds)

For complete requirements at task creation time:
```
git show edb2b1e:requirements_tasks/process/AI_rules/requirements_management/user_needs_content/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

**Three new scenario files to create:**

1. **Dr. Sarah** (`requirements_user_needs/personas/dr_sarah/scenarios/instruct_client_on_protocol/scenario.md`)
   - Extract and expand Act 3 from SCEN-001-01
   - The didactic handover: Psychoeducation, column-by-column explanation, barrier discussion
   - Anna's White Sheet Syndrome, privacy concerns
   - 10 minutes of session time
   - Counterpart to Max's SCEN-002-04 (`receive_protocol_homework`)
   - Gold standard candidate for therapist-side distribution

2. **Prof. Dr. Weber** (`requirements_user_needs/personas/prof_dr_weber/scenarios/instruct_client_on_protocol/scenario.md`)
   - Extract and expand from SCEN-011-01
   - The ritual handover: "This is an invitation, not homework"
   - The handwritten page as transitional object
   - Lena's ambivalence about structured tracking
   - Counterpart to Lena's SCEN-016-01 (`receive_protocol_homework`)

3. **Dr. med. Turan** (`requirements_user_needs/personas/dr_med_turan/scenarios/instruct_client_on_protocol/scenario.md`)
   - Extract and expand from SCEN-012-01
   - The 90-second medical handover
   - Safety net instruction (agitation/SI)
   - Herr Berger's "jacket pocket" moment
   - 4 minutes of appointment time

**Updates to existing files:**

4. **SCENARIO_INDEX.md**:
   - Add three new instances under `distribution.instruct_client` category (lines 125-163)
   - Remove the gap entry (current lines 161-163)
   - Assign scenario IDs following existing pattern
   - Set gold_status appropriately (Dr. Sarah likely gold standard)

5. **Existing prepare_protocol scenarios** (SCEN-001-01, SCEN-011-01, SCEN-012-01):
   - Add reference in Act 3 to new standalone scenario
   - Format: "Full handover story: see SCEN-XXX-XX"
   - Keep Act 3 as summary/preview, not deleted

### Out of Scope

- Creating client-side counterparts (those already exist)
- Creating scenarios for other personas (only the three listed)
- Modifying scenario structure/templates (this is content creation, not structure change)
- Creating user flows (that happens after scenarios are complete)

## Acceptance Criteria

- [ ] Three new scenario files created with full three-act structure following scenario template
- [ ] Each scenario has unique scenario_id assigned (SCEN-001-XX, SCEN-011-XX, SCEN-012-XX)
- [ ] Each reveals unique design implications for therapist→client protocol handover in "Design Implications" section
- [ ] SCENARIO_INDEX.md updated: three instances added under `distribution.instruct_client`, gap entry removed
- [ ] Existing `prepare_protocol_for_client` scenarios updated with cross-references to new scenarios
- [ ] All files follow naming convention: `instruct_client_on_protocol` (canonical name from index)
- [ ] Gold standard assigned appropriately (Dr. Sarah likely candidate based on existing pattern)

## Design Implications to Surface

Each scenario should reveal unique requirements for the digital handover:

- **Dr. Sarah**: Template-based instruction generation, barrier discussion prompts, privacy guidance
- **Prof. Dr. Weber**: Ritual/symbolic handover, analog-to-digital bridge, invitation framing vs. homework framing
- **Dr. med. Turan**: Speed-optimized handover, medication-specific safety instructions, minimal time footprint

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| SCEN-001-01 | completed | Source for Dr. Sarah scenario |
| SCEN-011-01 | approved | Source for Prof. Weber scenario |
| SCEN-012-01 | approved | Source for Dr. Turan scenario |
| SCENARIO_INDEX.md | exists | Index structure already defines category |

## Notes

**Why this matters**: The client-side handover scenarios (5 existing) can't be properly designed into user flows without understanding the therapist-side of the same interaction. This creates a complete picture of the handover moment from both perspectives.

**Relationship to user flows**: Once these scenarios exist, user flows for plan distribution can be designed that serve BOTH sides of the interaction (therapist instructing + client receiving).

**Opus recommended**: Given the need to extract narrative structure from existing Act 3 sections and expand them into full three-act scenarios while preserving clinical authenticity, using Opus for scenario writing would be appropriate, the create scenario skill automatically switches to opus at the right time.

**Accidentially created opus plan**: 2026-02-09_01_opus_plan was created by accident. Read it to get context.