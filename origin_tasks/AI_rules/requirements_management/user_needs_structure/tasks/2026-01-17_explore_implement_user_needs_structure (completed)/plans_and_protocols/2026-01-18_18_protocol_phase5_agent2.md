# Protocol: Phase 5 Agent 2 - New Skills Creation

**Date**: 2026-01-18
**Agent ID**: skill-creation-agent-2026-01-18-002
**Phase**: 5 (Integration & Tooling)
**Agent Role**: Agent 2 - New Skills Creation
**Status**: IN_PROGRESS

---

## Objective

Create complete skill.md files for three new user needs management skills:
1. create-persona
2. create-scenario
3. create-user-flow

---

## Plan Reference

Following plan: `plans_and_protocols/2026-01-18_16_opus_plan_phase5.md`
- Section: Agent 2 (lines 164-458)

---

## Execution Log

### Step 1: Context Gathering (COMPLETE)

**Files Read**:
- ✅ `plans_and_protocols/2026-01-18_16_opus_plan_phase5.md` - Agent 2 specification
- ✅ `goal.md` - Task objective and scope
- ✅ `.claude/skills/setup-task/skill.md` - Existing skill pattern reference
- ✅ `requirements_user_needs/README.md` - Sections with templates (persona, scenario, flow)

**Key Findings**:
- Existing skills follow pattern: YAML frontmatter → Role statement → Purpose → Workflow sections
- README.md contains complete templates for all three artifact types:
  - Persona template: lines 469-636
  - Scenario template: lines 764-874
  - User flow template: lines 1239-1399
- All templates include YAML frontmatter with unique IDs
- Review status workflow: always starts as "draft"
- Evidence level system: grounded | proto_persona | hypothesis (with visual markers 🟢🟡🔴)

### Step 2: Create create-persona skill (COMPLETE)

**Created**: `.claude/skills/create-persona/skill.md`

Following plan specification (lines 170-247):
- ✅ YAML header with name, description, tools, model
- ✅ Role statement: "You are a persona creation specialist"
- ✅ Workflow sections: Gather info → Generate ID → Read templates → Create structure → Generate file → Validate → Output
- ✅ ID generation logic: Count existing personas to get next PERSONA-XXX number
- ✅ Always starts with review_status: draft
- ✅ Evidence level markers explained (🟢🟡🔴)
- ✅ All sections from README template included
- ✅ Special considerations for mental health personas
- ✅ Environmental constraints guidance

### Step 3: Create create-scenario skill (COMPLETE)

**Created**: `.claude/skills/create-scenario/skill.md`

Following plan specification (lines 249-344):
- ✅ YAML header with name, description, tools, model
- ✅ Role statement: "You are a scenario creation specialist"
- ✅ Parent persona validation with review_status check
- ✅ ID generation logic: SCEN-[PERSONA]-[SEQUENCE]
- ✅ Three-act structure enforced (Context → Interaction/Resistance → Result/Feeling)
- ✅ Technology neutrality validation with examples
- ✅ State-of-the-art elements (privacy glitch, imperfection, internal monologue)
- ✅ Always starts with review_status: draft
- ✅ Special considerations for mental health scenarios

### Step 4: Create create-user-flow skill (COMPLETE)

**Created**: `.claude/skills/create-user-flow/skill.md`

Following plan specification (lines 346-450):
- ✅ YAML header with name, description, tools, model
- ✅ Role statement: "You are a user flow creation specialist"
- ✅ Parent scenario validation with review_status check
- ✅ ID generation logic: FLOW-[PERSONA]-[SCENARIO]-[SEQUENCE]
- ✅ Happy path table with optional Environment column
- ✅ Exception model (numbered exceptions per step)
- ✅ Technology agnosticism validation with examples
- ✅ Local-first edge cases (corruption, storage full, app kill)
- ✅ Adaptive UI rules documented
- ✅ Bidirectional epic/feature links
- ✅ Always starts with review_status: draft, implementation_status: not_started
- ✅ Privacy-sensitive flow guidance (Environment column)

---

## Files Created

1. ✅ `.claude/skills/create-persona/skill.md` (198 lines)
2. ✅ `.claude/skills/create-scenario/skill.md` (363 lines)
3. ✅ `.claude/skills/create-user-flow/skill.md` (455 lines)

---

## Quality Criteria Checklist

From plan (lines 452-457):
- ✅ Three new skill.md files created
- ✅ Each skill follows existing skill patterns (YAML header, workflow sections)
- ✅ ID generation logic documented
- ✅ Review status workflow enforced (always starts as draft)
- ✅ Technology neutrality checks included (for flows/scenarios)

---

## Summary

### Work Completed

**Three New Skills Created**:

1. **create-persona** - Creates new persona files with:
   - Unique PERSONA-XXX ID generation
   - Complete YAML frontmatter (persona_id, role, evidence_level, review_status, etc.)
   - All required content sections from README template
   - Evidence level markers (🟢🟡🔴)
   - Special guidance for mental health personas
   - Environmental constraints documentation
   - PCD considerations

2. **create-scenario** - Creates new scenario files with:
   - Unique SCEN-[PERSONA]-[SEQUENCE] ID generation
   - Parent persona validation and review_status check
   - Three-act structure enforcement (Context → Interaction/Resistance → Result/Feeling)
   - Technology neutrality validation with forbidden/allowed examples
   - State-of-the-art elements (privacy glitch, imperfection, internal monologue)
   - Special considerations for mental health scenarios
   - Distinction guidance (scenario vs. user flow)

3. **create-user-flow** - Creates new user flow files with:
   - Unique FLOW-[PERSONA]-[SCENARIO]-[SEQUENCE] ID generation
   - Parent scenario validation and review_status check
   - Happy path table (basic + environment column variant)
   - Exception model (numbered exceptions per step with recovery paths)
   - Technology agnosticism validation with examples
   - Local-first edge cases (database corruption, storage full, app kill, accidental deletion)
   - Adaptive UI rules (mood-based, crisis state, first-time user)
   - Bidirectional epic/feature cross-references
   - Privacy-sensitive flow guidance (Environment column usage)

### Quality Criteria Status

From plan (lines 452-457):
- ✅ Three new skill.md files created
- ✅ Each skill follows existing skill patterns (YAML header, workflow sections)
- ✅ ID generation logic documented
- ✅ Review status workflow enforced (always starts as draft)
- ✅ Technology neutrality checks included (for flows/scenarios)

### Design Decisions

**Decision 1: Detailed Workflow Steps**
- **Choice**: Include verbose, step-by-step instructions in each skill
- **Reason**: User needs skills should be usable by non-experts; clarity over brevity
- **Trade-off**: Longer files, but more self-documenting

**Decision 2: Technology Neutrality Validation**
- **Choice**: Include explicit "Forbidden vs. Allowed" examples in scenario and flow skills
- **Reason**: Technology creep is common mistake; examples prevent it
- **Trade-off**: Slightly longer skills, but prevents future rework

**Decision 3: Mental Health Specific Guidance**
- **Choice**: Add special considerations sections for mental health context
- **Reason**: This app's domain has unique requirements (energy budget, shame threshold, privacy)
- **Trade-off**: Skills slightly domain-specific, but necessary for quality

**Decision 4: Evidence Level Markers**
- **Choice**: Include visual emoji markers (🟢🟡🔴) in persona skill
- **Reason**: Matches README.md convention, makes evidence levels scannable
- **Trade-off**: Emojis may not render in all editors, but accepted by project

**Decision 5: Bidirectional Link Emphasis**
- **Choice**: User flow skill prominently mentions epic/feature cross-references
- **Reason**: Complements Agent 1's work (epic YAML user_needs field)
- **Trade-off**: None, this is required integration

### Files Modified

1. `.claude/skills/create-persona/skill.md` - Created
2. `.claude/skills/create-scenario/skill.md` - Created
3. `.claude/skills/create-user-flow/skill.md` - Created
4. `plans_and_protocols/2026-01-18_18_protocol_phase5_agent2.md` - This protocol file

### Next Steps

This agent's work is complete. Remaining Phase 5 agents:
- **Agent 3**: Enhance existing skills (setup-task, verify-quality, explore-requirements)
- **Agent 4**: Define validation script enhancements and create follow-up task

---

**Status**: COMPLETE
**Agent ID**: skill-creation-agent-2026-01-18-002
**Completion Time**: 2026-01-18
**All Quality Criteria Met**: YES
