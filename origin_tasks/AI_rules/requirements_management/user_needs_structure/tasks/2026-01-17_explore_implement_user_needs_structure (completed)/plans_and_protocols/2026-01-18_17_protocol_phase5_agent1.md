# Protocol: Phase 5 Agent 1 - Cross-Reference System Implementation

**Date**: 2026-01-18
**Agent ID**: cross-reference-agent-2026-01-18-001
**Phase**: 5 (Integration & Tooling)
**Agent Role**: Agent 1 - Cross-Reference Bidirectional System (Documentation)
**Status**: IN_PROGRESS

---

## Objective

Define and document the complete bidirectional cross-reference system between user needs and requirements_tasks:
1. Update README.md Section 13 with practical bidirectional examples
2. Define standard YAML integration for epic/feature requirements.md
3. Create examples for two existing epics
4. Add cross-reference validation rules to README.md

---

## Plan Reference

Following plan: `plans_and_protocols/2026-01-18_16_opus_plan_phase5.md`
- Section: Agent 1 (lines 70-161)

---

## Execution Log

### Step 1: Context Gathering (COMPLETE)

**Files Read**:
- ✅ `plans_and_protocols/2026-01-18_16_opus_plan_phase5.md` - Agent 1 specification
- ✅ `goal.md` - Task objective and scope
- ✅ `requirements_user_needs/README.md` - Current Section 13 (lines 2348-2497)
- ✅ `requirements_tasks/functional/therapist/epic_plan_management/requirements.md` - Epic example 1
- ✅ `requirements_tasks/functional/client/epic_data_input/requirements.md` - Epic example 2
- ✅ `requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows/quick_night_entry/flow.md` - Flow example (FLOW-002-01-01)

**Key Findings**:
- Current Section 13 (Cross-Reference Notation) has notation format and basic examples
- Missing: Practical bidirectional examples (flow → epic AND epic → flow)
- Missing: YAML specification for epic/feature requirements.md `user_needs` field
- Missing: Validation rules documentation
- Two epics identified for examples:
  - `REQ-FUNC-014`: Therapist Plan Management (XL effort, in_progress)
  - `REQ-FUNC-002`: Client Data Input (L effort, defined)
- One user flow exists: `FLOW-002-01-01` (Quick Night Entry for Max/Client)

### Step 2: README.md Section 13 Enhancement (IN_PROGRESS)

**Current Section 13 Structure**:
```
## 13. Cross-Reference Notation
  - Notation Format
  - Examples
  - Usage Patterns
  - Cross-Reference Validation
```

**Planned Additions**:
1. **New subsection**: "13.1 Bidirectional Cross-References" (after "Notation Format")
   - Example: From user flows to epics (in flow.md)
   - Example: From epics to user flows (in requirements.md YAML)

2. **New subsection**: "13.2 YAML Integration for Epics/Features" (after bidirectional examples)
   - Full `user_needs` field specification
   - All field definitions (implements_flows, addresses_scenarios, personas_served, deviations)

3. **Enhancement**: Expand "Cross-Reference Validation" with specific rules

**Next Actions**:
- [ ] Read full Section 13 to determine exact insertion points
- [ ] Draft bidirectional examples subsection
- [ ] Draft YAML specification subsection
- [ ] Draft validation rules enhancement
- [ ] Update README.md with all changes

---

## Decisions & Trade-offs

### Decision 1: Section Structure
**Choice**: Add subsections 13.1 and 13.2 instead of replacing Section 13
**Reason**: Preserve existing notation format documentation while adding practical guidance
**Trade-off**: Section 13 becomes longer, but more comprehensive

### Decision 2: Epic Selection for Examples
**Choice**: Use therapist/epic_plan_management and client/epic_data_input
**Reason**: Plan suggests these in lines 142-144; they represent different stakeholders
**Trade-off**: These epics may not perfectly align with existing flows (FLOW-002-01-01 is about quick entry, not plan management)
**Mitigation**: Use hypothetical cross-references with notes explaining they're examples

---

## Blockers & Issues

None yet.

---

## Quality Criteria Checklist

From plan (lines 156-160):
- [ ] README.md Section 13 has bidirectional examples
- [ ] YAML specification complete with all fields documented
- [ ] At least 2 epic/feature files updated with example user_needs section
- [ ] Validation rules documented

---

## Files Modified

(Will be updated as work progresses)

- [ ] `requirements_user_needs/README.md` - Section 13 enhancement
- [ ] `requirements_tasks/functional/therapist/epic_plan_management/requirements.md` - Add user_needs YAML
- [ ] `requirements_tasks/functional/client/epic_data_input/requirements.md` - Add user_needs YAML

---

## Next Steps

1. Read full Section 13 to understand current content
2. Draft new subsections
3. Update README.md
4. Update epic requirements.md files with example user_needs YAML
5. Mark protocol as COMPLETE

---

### Step 2: README.md Section 13 Enhancement (COMPLETE)

**Actions Taken**:
1. ✅ Read full Section 13 (lines 2348-2423) to understand current content
2. ✅ Added new subsection "Bidirectional Cross-References in Practice"
   - Example: From user flows to epics (flow.md table format)
   - Example: From epics to user flows (requirements.md YAML format)
3. ✅ Added new subsection "YAML Integration for Epic/Feature Requirements"
   - Full `user_needs` field specification with all subfields
   - Field definitions (implements_flows, addresses_scenarios, personas_served, deviations)
   - Examples by epic type (user-facing, system/infrastructure, no direct user needs)
4. ✅ Enhanced "Cross-Reference Validation" subsection
   - 5 validation rules defined (existence, bidirectional consistency, review status, coverage consistency, step range)
   - Validation scripts responsibilities documented
   - Example validation output provided

**Files Modified**:
- `requirements_user_needs/README.md` - Section 13 enhanced with ~220 new lines

### Step 3: Epic Requirements.md Updates (COMPLETE)

**Epic 1: Client Data Input (REQ-FUNC-002)**
- ✅ Added `user_needs` YAML section
- References: FLOW-002-01-01 (Quick Night Entry)
- Coverage: partial (step 2 only - entry screen exists)
- Addresses: SCEN-002-01 (Brain Dump at Night)
- Serves: PERSONA-002 (Max - Client)

**Epic 2: Therapist Plan Management (REQ-FUNC-014)**
- ✅ Added `user_needs` YAML section
- References: FLOW-001-01-01 (example - flow doesn't exist yet)
- Coverage: not_started
- Addresses: SCEN-001-01 (example scenario to be created)
- Serves: PERSONA-001 (example therapist persona to be created)
- Includes example deviation to demonstrate format

**Note**: Epic 2 uses hypothetical references to demonstrate the cross-reference pattern for future implementation. This is intentional and documented in the notes field.

**Files Modified**:
- `requirements_tasks/functional/client/epic_data_input/requirements.md` - Added user_needs YAML
- `requirements_tasks/functional/therapist/epic_plan_management/requirements.md` - Added user_needs YAML with example structure

---

## Summary

### Work Completed

**README.md Section 13 Enhancements**:
1. **Bidirectional Cross-References in Practice** - Shows practical examples of how flows and epics reference each other
2. **YAML Integration for Epic/Feature Requirements** - Complete specification of the `user_needs` field structure
3. **Cross-Reference Validation** - 5 validation rules with severity levels and script responsibilities

**Epic Cross-Reference Examples**:
1. **REQ-FUNC-002 (Client Data Input)** - Real cross-reference to FLOW-002-01-01
2. **REQ-FUNC-014 (Therapist Plan Management)** - Example cross-reference structure (flows to be created)

### Quality Criteria Status

From plan (lines 156-160):
- ✅ README.md Section 13 has bidirectional examples
- ✅ YAML specification complete with all fields documented
- ✅ At least 2 epic/feature files updated with example user_needs section
- ✅ Validation rules documented

### Files Modified

1. `requirements_user_needs/README.md` - Section 13 enhanced (~220 lines added)
2. `requirements_tasks/functional/client/epic_data_input/requirements.md` - user_needs YAML added
3. `requirements_tasks/functional/therapist/epic_plan_management/requirements.md` - user_needs YAML added
4. `plans_and_protocols/2026-01-18_17_protocol_phase5_agent1.md` - This protocol file

### Decisions & Trade-offs

**Decision 1: Hypothetical References in Epic 2**
- **Choice**: Used non-existent FLOW-001-01-01 as example in therapist epic
- **Reason**: No therapist flows exist yet, but need to demonstrate the pattern
- **Documentation**: Clearly marked as example in YAML notes field
- **Value**: Shows complete structure including deviations field

**Decision 2: Coverage Values**
- **REQ-FUNC-002**: Set to "partial" because only basic entry screen exists (Step 2), not voice-to-text (Steps 3-7)
- **REQ-FUNC-014**: Set to "not_started" because it's a hypothetical example
- **Rationale**: Honest assessment enables accurate tracking

**Decision 3: Validation Rule Severity**
- **ERROR**: Broken references (files don't exist) - hard failures
- **WARNING**: Status mismatches, non-approved flows - soft failures
- **Rationale**: Allows development to proceed while flagging potential issues

### Next Steps

This agent's work is complete. Remaining Phase 5 agents:
- **Agent 2**: Create new skill.md files (create-persona, create-scenario, create-user-flow)
- **Agent 3**: Enhance existing skills (setup-task, verify-quality, explore-requirements)
- **Agent 4**: Define validation script enhancements and create follow-up task

---

**Status**: COMPLETE
**Agent ID**: cross-reference-agent-2026-01-18-001
**Completion Time**: 2026-01-18
**All Quality Criteria Met**: YES
