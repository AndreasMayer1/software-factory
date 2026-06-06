# Opus Plan: Phase 5 - Integration & Tooling

**Date**: 2026-01-18
**Phase**: 5 (Integration & Tooling)
**Status**: PLANNING
**Planner**: Opus (claude-opus-4-5-20251101)

---

## Objective

Complete the user needs structure implementation by:
1. Defining bidirectional cross-reference mechanisms between user flows and epics/features
2. Integrating user needs references into epic/feature YAML format
3. Creating skill specifications for new user needs management skills
4. Enhancing existing skills to integrate user needs awareness
5. Defining validation script enhancements
6. Creating the follow-up task for skill implementation

---

## Analysis Summary

### Current State Assessment

**User Needs Infrastructure (Completed in Phase 1-4)**:
- 4 personas created (PERSONA-001 through PERSONA-004)
- 4 scenarios (SCEN-001-01, SCEN-001-02, SCEN-002-01, SCEN-003-01)
- 2 user flows (FLOW-002-01-01, FLOW-003-01-01)
- Review status system implemented with YAML tracking
- Cross-reference notation defined: `[DOC_TYPE]-[ID]#[SECTION]@[COMMIT]`
- Change propagation process documented (CHANGE_PROPAGATION.md)
- Deviation documentation format defined
- Status script exists (generate_user_needs_status.py)

**Existing Tooling Infrastructure**:
- `validate_meta.py` - Validates requirements.md and goal.md YAML
- `generate_user_needs_status.py` - Generates STATUS.md for user needs
- Skills: setup-task, verify-quality, explore-requirements, switch-to-opus, etc.
- Epic requirements.md has YAML with `trackable_items` (acceptance_criteria, sections)
- Tasks reference requirements via `covers` field

**Gap Analysis**:
1. **No user_needs field in epic/feature requirements.md** - Need YAML integration
2. **No bidirectional links** - User flows have "Related Epic/Feature" column but epics don't have user flow references
3. **New skills not yet created** - create-persona, create-scenario, create-user-flow only documented in CHANGE_PROPAGATION.md
4. **Existing skills not user-needs aware** - setup-task, verify-quality don't check user needs references
5. **validate_meta.py doesn't validate user needs** - Only checks requirements_tasks

---

## Phase 5 Requirements (from goal.md lines 118-126)

```markdown
**Phase 5: Integration & Tooling**
13. Define how cross-references work in practice:
    - From user flows to epics/features
    - From epics/features to user flows (YAML format integration)
14. Document skill modifications needed:
    - New skills: create-persona, create-scenario, create-user-flow
    - Modified skills: setup-task, verify-quality, explore-requirements
15. Define validation rules and scripts needed
16. Create a new task to implement the changes to the skills.
```

---

## Execution Plan

### Agent 1: Cross-Reference Bidirectional System (Documentation)

**Purpose**: Define and document the complete bidirectional cross-reference system between user needs and requirements_tasks.

**Steps**:

#### 1.1 Update README.md Section 13 with Implementation Details

Add practical examples of bidirectional references:

**In User Flows** (flow.md → epics/features):
```markdown
## Implementing Epics/Features

| User Flow Step | Implementing Epic/Feature | Status |
|----------------|---------------------------|--------|
| Steps 1-3: Protocol Selection | EPIC-THER-001 (Plan Management) | not_implemented |
| Step 4: Client Assignment | FEAT-THER-001-01 (Client Plan View) | partial |
| Step 5: Instructions | FEAT-THER-001-02 (Protocol Instructions) | not_implemented |
```

**In Epics/Features** (requirements.md ← user flows):
```yaml
# YAML frontmatter addition to epic/feature requirements.md
user_needs:
  implements_flows:
    - id: FLOW-001-01-01
      steps: [1, 2, 3]
      coverage: partial
      notes: "Covers protocol selection, not instructions"
    - id: FLOW-002-01-01
      steps: [4, 5]
      coverage: complete
  addresses_scenarios:
    - SCEN-001-01  # Primary scenario served
    - SCEN-001-02
  personas_served:
    - PERSONA-001  # Therapist
    - PERSONA-002  # Client
```

#### 1.2 Define Standard YAML Integration for Epic/Feature Requirements.md

Create new YAML section specification:

```yaml
# Full user_needs section specification for requirements.md
user_needs:
  # Required: Which user flows does this epic/feature implement?
  implements_flows:
    - id: FLOW-[PERSONA]-[SCENARIO]-[SEQUENCE]
      steps: [list of step numbers or "all"]
      coverage: not_started | partial | complete
      notes: "Optional explanation of what's covered vs. not"

  # Optional: Direct scenario references (when epic/feature serves multiple flows)
  addresses_scenarios: [SCEN-001-01, SCEN-001-02]

  # Optional: Personas this epic/feature primarily serves
  personas_served: [PERSONA-001, PERSONA-002]

  # Optional: Deviations from user needs (compromises made)
  deviations:
    - flow_ref: FLOW-001-01-01#step_3
      deviation: "Cannot auto-detect client from therapist calendar"
      reason: "Technical: Calendar integration out of scope for MVP"
      value_impact: low | medium | high
      mitigation: "Manual client selection added to flow"
```

#### 1.3 Create Examples for Two Existing Epics

Update these files to demonstrate the pattern:
1. `requirements_tasks/functional/therapist/epic_plan_management/requirements.md`
2. `requirements_tasks/functional/client/epic_data_input/requirements.md`

Add `user_needs` section to YAML frontmatter of each (even if flows aren't fully mapped yet, show the structure).

#### 1.4 Add Cross-Reference Validation Rules to README.md

Document validation expectations:
- `implements_flows[].id` must reference existing flow.md files
- `addresses_scenarios[]` must reference existing scenario.md files
- `personas_served[]` must reference existing persona.md files
- Warn if flow.md `review_status` is not `approved` but epic references it

**Quality Criteria**:
- [ ] README.md Section 13 has bidirectional examples
- [ ] YAML specification complete with all fields documented
- [ ] At least 2 epic/feature files updated with example user_needs section
- [ ] Validation rules documented

---

### Agent 2: Skill Specifications (New Skills)

**Purpose**: Create complete skill.md files for create-persona, create-scenario, create-user-flow.

**Steps**:

#### 2.1 Create `.claude/skills/create-persona/skill.md`

```markdown
---
name: create-persona
description: Create a new persona in requirements_user_needs/personas/
tools: Read, Write, Bash, Glob, Grep
model: inherit
---

You are a persona creation specialist.

## Purpose

Create a new persona following the structure and guidelines in requirements_user_needs/README.md.

## Workflow

### 1. Gather Information

Ask user for:
- Persona name (display name and folder name in snake_case)
- Role: therapist | client | self_user | system
- Brief archetype description
- Source information (proto-persona, interview notes, etc.)

### 2. Generate Unique ID

```bash
# Count existing personas to determine next ID
ls -la requirements_user_needs/personas/*/persona.md | wc -l
```

Next ID = PERSONA-[COUNT + 1] (zero-padded to 3 digits, e.g., PERSONA-005)

### 3. Read Templates

Read requirements_user_needs/README.md Section 3 (Persona Definition) for:
- YAML frontmatter template
- Required sections
- Writing checklist

### 4. Create Folder Structure

```
requirements_user_needs/personas/[persona_name]/
├── persona.md
└── scenarios/        # Empty, will be populated by create-scenario
```

### 5. Generate persona.md

Use template from README.md. Include:
- YAML frontmatter with all required fields
- review_status: draft (always starts as draft)
- review_history with initial entry
- All content sections (mark unknown content with 🔴 [Hypothesis])

### 6. Validate Against Checklist

Run through persona writing checklist from README.md:
- Mental model defined
- JTBD articulated
- Context described
- Tech ecosystem captured
- Anti-traits defined
- Evidence level marked

### 7. Output

"Persona created at requirements_user_needs/personas/[name]/persona.md
ID: PERSONA-[NUMBER]
Status: draft (requires user review)

Next steps:
1. Review and approve the persona
2. Use create-scenario skill to add scenarios"
```

#### 2.2 Create `.claude/skills/create-scenario/skill.md`

```markdown
---
name: create-scenario
description: Create a new scenario under an existing persona
tools: Read, Write, Bash, Glob, Grep
model: inherit
---

You are a scenario creation specialist.

## Purpose

Create a new scenario following the structure in requirements_user_needs/README.md.

## Prerequisites

- Parent persona must exist and ideally be `approved`
- If persona is not approved, warn user but allow creation

## Workflow

### 1. Validate Parent Persona

```bash
# Check persona exists
cat requirements_user_needs/personas/[persona_name]/persona.md
```

Read persona's YAML to get:
- persona_id
- review_status (warn if not approved)

### 2. Gather Information

Ask user for:
- Scenario name (descriptive, will be converted to snake_case)
- Goal description (what user wants to achieve)
- Context (when, where, triggers)
- Evidence level (grounded | proto_persona | hypothesis)

### 3. Generate Unique ID

```bash
# Count existing scenarios for this persona
ls -la requirements_user_needs/personas/[persona_name]/scenarios/*/scenario.md 2>/dev/null | wc -l
```

Next ID = SCEN-[PERSONA_NUM]-[SEQUENCE] (e.g., SCEN-001-03)

### 4. Read Templates

Read requirements_user_needs/README.md Section 4 (Scenario Definition) for:
- YAML frontmatter template
- Three-act structure
- Writing checklist

### 5. Create Folder Structure

```
requirements_user_needs/personas/[persona_name]/scenarios/[scenario_name]/
├── scenario.md
└── user_flows/      # Empty, will be populated by create-user-flow
```

### 6. Generate scenario.md

Use template from README.md. Include:
- YAML with parent persona_id reference
- review_status: draft
- Three-act structure (context → interaction → result)
- Success criteria
- Failure modes
- Technology-neutral language (no app features!)

### 7. Validate Technology Neutrality

Check that scenario.md does NOT contain:
- Specific technology references (SQLite, OLED, push notifications)
- App feature descriptions
- Implementation details

Warn if technology-specific language found.

### 8. Output

"Scenario created at requirements_user_needs/personas/[persona]/scenarios/[name]/scenario.md
ID: SCEN-[PERSONA]-[SEQUENCE]
Parent: PERSONA-[PERSONA_NUM]
Status: draft (requires user review)

Next steps:
1. Review and approve the scenario
2. Use create-user-flow skill to add user flows"
```

#### 2.3 Create `.claude/skills/create-user-flow/skill.md`

```markdown
---
name: create-user-flow
description: Create a new user flow under an existing scenario
tools: Read, Write, Bash, Glob, Grep
model: inherit
---

You are a user flow creation specialist.

## Purpose

Create a new user flow following the structure in requirements_user_needs/README.md.

## Prerequisites

- Parent scenario must exist and ideally be `approved`
- If scenario is not approved, warn user

## Workflow

### 1. Validate Parent Scenario

```bash
# Check scenario exists
cat requirements_user_needs/personas/[persona]/scenarios/[scenario]/scenario.md
```

Read scenario YAML to get:
- scenario_id
- persona_id
- review_status (warn if not approved)
- success_criteria (flow must address these)

### 2. Gather Information

Ask user for:
- Flow name (descriptive approach name, will be converted to snake_case)
- Flow approach (how does this flow solve the scenario goal?)
- Evidence level

### 3. Generate Unique ID

```bash
# Count existing flows for this scenario
ls -la requirements_user_needs/personas/[persona]/scenarios/[scenario]/user_flows/*/flow.md 2>/dev/null | wc -l
```

Next ID = FLOW-[PERSONA]-[SCENARIO]-[SEQUENCE] (e.g., FLOW-001-02-03)

### 4. Read Templates

Read requirements_user_needs/README.md Section 5 (User Flow Definition) for:
- YAML frontmatter template
- Happy path structure
- Exception model
- Environment swimlane

### 5. Create Folder Structure

```
requirements_user_needs/personas/[persona]/scenarios/[scenario]/user_flows/[flow_name]/
└── flow.md
```

### 6. Generate flow.md

Use template from README.md. Include:
- YAML with scenario_id and persona_id references
- review_status: draft
- implementation_status: not_started
- Happy path table with Environment column (if privacy-sensitive)
- Unhappy paths / exceptions
- Implementing Epics/Features section (empty initially)
- Deviation table (if flow can't fully satisfy scenario)

### 7. Check for Epic/Feature Links

Ask user:
"Which existing epics/features implement (or will implement) this flow?"

If provided, add to flow.md's "Implementing Epics/Features" section.

### 8. Validate Technology Agnosticism

User flows CAN describe interaction patterns but should NOT specify:
- Specific storage technology (SQLite, Hive, etc.)
- UI framework details (Material 3, etc.)
- Platform-specific code

Warn if technology-specific language found beyond interaction patterns.

### 9. Output

"User flow created at requirements_user_needs/personas/[p]/scenarios/[s]/user_flows/[name]/flow.md
ID: FLOW-[PERSONA]-[SCENARIO]-[SEQUENCE]
Parent Scenario: SCEN-[SCENARIO_ID]
Status: draft (requires user review)

Next steps:
1. Review and approve the flow
2. Link to implementing epics/features using cross-references"
```

**Quality Criteria**:
- [ ] Three new skill.md files created
- [ ] Each skill follows existing skill patterns (YAML header, workflow sections)
- [ ] ID generation logic documented
- [ ] Review status workflow enforced (always starts as draft)
- [ ] Technology neutrality checks included

---

### Agent 3: Skill Enhancements (Existing Skills)

**Purpose**: Document enhancements to setup-task, verify-quality, and explore-requirements skills for user needs integration.

**Steps**:

#### 3.1 Enhance `.claude/skills/setup-task/skill.md`

Add new section after "Coverage Tracking":

```markdown
### User Needs Reference Check

**NEW**: When creating tasks that implement user flows:

1. **Check if epic/feature has user_needs field**:
   - Read parent epic/feature requirements.md YAML
   - Look for `user_needs.implements_flows[]`

2. **If user_needs exists**:
   - List the flows this epic/feature implements
   - Ask: "This epic/feature implements these user flows: [list]. Does this task relate to any of them?"
   - If yes, add to goal.md:
     ```yaml
     related_flows: [FLOW-001-01-01, FLOW-002-01-01]
     ```

3. **Check flow review_status**:
   - Warn if referenced flows are not `approved`:
     ```
     Warning: FLOW-001-01-01 has review_status: draft
     Implementing non-approved flows may require rework.
     Proceed? (y/n)
     ```

4. **Suggest flow reference if missing**:
   - If epic has no user_needs field, suggest:
     ```
     Note: The parent epic has no user_needs references.
     Consider running `explore-requirements` to identify which user flows this epic serves.
     ```
```

#### 3.2 Enhance `.claude/skills/verify-quality/skill.md`

Add new section after "Check Meta Information":

```markdown
### User Needs Verification

**NEW**: Verify user needs references are valid and consistent.

1. **Check epic/feature user_needs references**:
   - Read requirements.md YAML `user_needs` field (if present)
   - For each `implements_flows[].id`:
     * Verify flow.md file exists at expected path
     * Read flow's `review_status` - warn if not `approved`
     * Verify flow's `implementation_status` matches coverage claim
   - For each `addresses_scenarios[]`:
     * Verify scenario.md file exists
     * Read scenario's `review_status`
   - For each `personas_served[]`:
     * Verify persona.md file exists

2. **Check task related_flows**:
   - If goal.md has `related_flows[]`, verify each flow exists
   - Warn if flows have been deprecated or significantly changed since task creation

3. **Cross-reference consistency check**:
   - If flow.md lists epic in "Implementing Epics/Features"
   - Then epic's requirements.md should have that flow in `user_needs.implements_flows`
   - Warn on asymmetric references

4. **Report findings**:
   - GREEN: All user needs references valid
   - YELLOW: Some references to non-approved documents
   - RED: Broken references (files don't exist)
```

#### 3.3 Enhance `.claude/skills/explore-requirements/skill.md`

Add new section in "Phase 2: Investigation":

```markdown
### 2.3 User Needs Analysis (NEW)

When exploring requirements for epics/features:

1. **Identify relevant user flows**:
   - Search requirements_user_needs/ for flows that might relate to this epic/feature
   - Use grep to find mentions of epic name or related keywords
   - List potentially relevant flows

2. **Map epic/feature to user needs hierarchy**:
   - Which personas does this epic/feature serve?
   - Which scenarios does it address?
   - Which specific user flow steps does it implement?

3. **Document in protocol**:
   ```markdown
   ## User Needs Mapping

   **Personas Served**: [list]
   **Scenarios Addressed**: [list with brief description]
   **User Flows Implemented**:
   | Flow ID | Flow Name | Steps Covered | Notes |
   |---------|-----------|---------------|-------|
   | FLOW-001-01-01 | Protocol Preparation | 1-3 | Happy path only |

   **Gaps Identified**:
   - [Flow/scenario need not covered by this epic]
   ```

4. **Suggest user_needs YAML**:
   After mapping is complete, suggest YAML to add to epic/feature requirements.md:
   ```yaml
   user_needs:
     implements_flows:
       - id: FLOW-001-01-01
         steps: [1, 2, 3]
         coverage: partial
     addresses_scenarios: [SCEN-001-01]
     personas_served: [PERSONA-001]
   ```
```

**Quality Criteria**:
- [ ] setup-task skill has user needs reference check section
- [ ] verify-quality skill has user needs verification section
- [ ] explore-requirements skill has user needs analysis section
- [ ] All enhancements follow existing skill patterns

---

### Agent 4: Validation Script Enhancements & Task Creation

**Purpose**: Define validation script enhancements and create the follow-up task for skill implementation.

**Steps**:

#### 4.1 Define validate_meta.py Enhancements

Document required enhancements to `scripts/validate_meta.py`:

**New Classes**:
```python
@dataclass
class UserNeedsMeta:
    id: str  # PERSONA-001, SCEN-001-01, FLOW-001-01-01
    path: str
    review_status: str  # draft, in_review, approved, deprecated
    parent_id: str  # For scenarios: persona_id, for flows: scenario_id
```

**New Validation Functions**:
```python
def validate_user_needs():
    """Find and validate all persona, scenario, flow files."""
    # Scan requirements_user_needs/personas/
    # Validate YAML frontmatter
    # Check ID format (PERSONA-XXX, SCEN-XXX-XX, FLOW-XXX-XX-XX)
    # Check parent references exist
    # Check review_status is valid enum

def validate_epic_user_needs_references():
    """Validate user_needs field in epic/feature requirements.md."""
    # For each requirements.md with user_needs field:
    #   - Validate implements_flows[].id references exist
    #   - Validate addresses_scenarios[] references exist
    #   - Validate personas_served[] references exist
    #   - Warn if referenced docs have review_status != approved

def validate_cross_reference_symmetry():
    """Check bidirectional references are symmetric."""
    # If flow.md lists epic in "Implementing Epics/Features"
    # Then epic's requirements.md should list flow in user_needs.implements_flows
    # Report asymmetric references as warnings
```

**Output Enhancements**:
```
=== USER NEEDS VALIDATION ===
Personas: 4 (1 approved, 3 draft)
Scenarios: 4 (2 approved, 2 in_review)
Flows: 2 (0 approved, 2 in_review)

Warnings:
  [WARN] EPIC-PLAN-MGMT references FLOW-001-01-01 which is not approved
  [WARN] FLOW-002-01-01 lists EPIC-DATA-INPUT but epic doesn't reference flow back

=== REQUIREMENTS VALIDATION ===
[existing output...]
```

#### 4.2 Define generate_user_needs_status.py Enhancements

Document required enhancements:

**New Features**:
1. **Cross-reference validation**: Check that all references in flow.md are valid
2. **Epic coverage report**: Show which epics/features implement which flows
3. **Orphan detection**: Find user flows not referenced by any epic
4. **Completion tracking**: Show percentage of flows with implementation_status = complete

**New Output Sections**:
```markdown
## Epic/Feature Coverage

| Epic/Feature | Flows Implemented | Coverage | Status |
|--------------|-------------------|----------|--------|
| EPIC-PLAN-MGMT | FLOW-001-01-01, FLOW-001-02-01 | partial | 2/5 steps |
| EPIC-DATA-INPUT | FLOW-002-01-01 | not_started | - |

## Orphan Flows (Not Referenced by Any Epic)

- FLOW-003-01-01 (Discreet Quick Log) - No epic references this flow

## Cross-Reference Warnings

- FLOW-001-01-01 references EPIC-THER-001 but epic doesn't reference flow back
```

#### 4.3 Create Follow-Up Task for Skill Implementation

Create new task folder and goal.md:

**Path**: `requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/2026-01-18_impl_user_needs_skill_integration/`

**goal.md Content**:
```markdown
---
task_id: TASK-PROC-010-02
type: impl
parent_requirement: REQ-PROC-010
urgency: 3
urgency_reason: U3-PLANNED
impact: 4
impact_reason: I4-IMPROVEMENT
status: pending
effort: L
created: 2026-01-18
depends_on: [TASK-PROC-010-01]
blocked_by: []
covers:
  sections: [SEC-05, SEC-06, SEC-07]
scope_description: "Implement user needs integration in skills and validation scripts"
requirements_version:
  commit: [CURRENT_COMMIT]
  file: ../requirements.md
---

# Goal: Implement User Needs Skill Integration

## Objective

Implement the skill modifications and validation script enhancements defined in Phase 5 planning document (2026-01-18_16_opus_plan_phase5.md).

## Scope

### In Scope

**New Skills** (create .claude/skills/[name]/skill.md):
1. create-persona - Create new persona following README templates
2. create-scenario - Create new scenario under existing persona
3. create-user-flow - Create new user flow under existing scenario

**Enhanced Skills** (modify existing skill.md files):
4. setup-task - Add user needs reference checks
5. verify-quality - Add user needs verification
6. explore-requirements - Add user needs analysis

**Validation Scripts** (modify scripts/):
7. validate_meta.py - Add user needs validation
8. generate_user_needs_status.py - Add coverage reporting

### Out of Scope

- Creating actual user needs documents (done in Phases 1-4)
- Modifying existing epic/feature requirements.md files (example only)
- Implementing modify-persona/scenario/flow skills (separate task from CHANGE_PROPAGATION.md)

## Acceptance Criteria

- [ ] Three new skill files created and functional
- [ ] Three existing skill files enhanced with user needs sections
- [ ] validate_meta.py validates user needs YAML
- [ ] validate_meta.py checks epic user_needs references
- [ ] generate_user_needs_status.py shows coverage report
- [ ] All skills tested with manual verification
- [ ] Documentation updated (CLAUDE.md if needed)

## Implementation Steps

1. Create skill files following specifications in plan
2. Test each skill with sample invocation
3. Enhance validate_meta.py with new validation functions
4. Enhance generate_user_needs_status.py with coverage report
5. Run full validation to verify no regressions
6. Update CLAUDE.md if new skill usage patterns needed

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-010-01 | in_progress | Phase 5 planning must complete first |

## References

- Skill specifications: plans_and_protocols/2026-01-18_16_opus_plan_phase5.md (Agent 2, 3)
- Validation specifications: plans_and_protocols/2026-01-18_16_opus_plan_phase5.md (Agent 4)
- Existing skill patterns: .claude/skills/setup-task/skill.md
- Existing validation: scripts/validate_meta.py
```

**Quality Criteria**:
- [ ] validate_meta.py enhancement specification complete
- [ ] generate_user_needs_status.py enhancement specification complete
- [ ] Follow-up task folder created
- [ ] goal.md has proper YAML frontmatter
- [ ] Task references this plan document

---

## Quality Criteria (Overall Phase 5)

### Documentation Quality
- [ ] README.md Section 13 has complete bidirectional examples
- [ ] YAML specification documented with all fields
- [ ] At least 2 epic/feature files updated as examples
- [ ] All cross-reference validation rules documented

### Skill Specifications Quality
- [ ] Three new skill.md files created (create-persona, create-scenario, create-user-flow)
- [ ] Three existing skills have enhancement documentation
- [ ] All skills follow consistent patterns
- [ ] Technology neutrality checks included in creation skills

### Validation Specifications Quality
- [ ] validate_meta.py enhancements fully specified
- [ ] generate_user_needs_status.py enhancements fully specified
- [ ] Expected output formats documented

### Task Quality
- [ ] Follow-up task created with proper structure
- [ ] Task references this plan
- [ ] Dependencies documented
- [ ] Acceptance criteria measurable

---

## Risks and Mitigations

### Risk 1: YAML Complexity in Epic Requirements
**Risk**: Adding user_needs field to epic requirements.md creates maintenance burden
**Mitigation**:
- Make user_needs field optional (not required for validation to pass)
- Provide clear templates and examples
- Only warn (not error) on missing references

### Risk 2: Cross-Reference Synchronization
**Risk**: Bidirectional references get out of sync (flow references epic but epic doesn't reference flow)
**Mitigation**:
- Validation script detects asymmetric references
- explore-requirements skill suggests YAML to add
- verify-quality skill checks consistency

### Risk 3: Review Status Enforcement
**Risk**: Tasks reference non-approved flows, leading to rework
**Mitigation**:
- setup-task warns when referencing non-approved flows
- verify-quality flags non-approved references
- User can override with explicit acknowledgment

### Risk 4: Skill Proliferation
**Risk**: Too many skills become hard to discover and maintain
**Mitigation**:
- New skills clearly scoped to user needs management
- Consider grouping into "user-needs-*" namespace
- Document in CLAUDE.md which skills to use when

---

## Execution Summary

| Agent | Focus | Files Modified/Created | Estimated Effort |
|-------|-------|------------------------|------------------|
| Agent 1 | Cross-reference system | README.md, 2 epic requirements.md | 1-2 hours |
| Agent 2 | New skills | 3 new skill.md files | 2-3 hours |
| Agent 3 | Skill enhancements | 3 existing skill.md files | 1-2 hours |
| Agent 4 | Validation & task | Spec docs, new task folder | 1-2 hours |

**Total Agents**: 4
**Total Estimated Effort**: 5-9 hours
**Dependencies**: Agents can run in parallel except Agent 4 (should run last to create task referencing other work)

---

## Completion Checklist

After all agents complete:

- [ ] README.md Section 13 updated with bidirectional examples
- [ ] At least 2 epic/feature requirements.md updated as examples
- [ ] `.claude/skills/create-persona/skill.md` created
- [ ] `.claude/skills/create-scenario/skill.md` created
- [ ] `.claude/skills/create-user-flow/skill.md` created
- [ ] `.claude/skills/setup-task/skill.md` enhanced
- [ ] `.claude/skills/verify-quality/skill.md` enhanced
- [ ] `.claude/skills/explore-requirements/skill.md` enhanced
- [ ] validate_meta.py enhancements specified
- [ ] generate_user_needs_status.py enhancements specified
- [ ] Follow-up implementation task created
- [ ] This plan marked complete in task status

---

**Plan Status**: READY FOR EXECUTION
**Created**: 2026-01-18
**Planner**: Opus (claude-opus-4-5-20251101)
**Next Step**: User review and approval, then execute with 4 agents
