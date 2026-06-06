---
task_id: TASK-PROC-010-09
type: impl
parent_requirement: REQ-PROC-010
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-02-01
effort: L
created: 2026-02-01
after:
  - TASK-PROC-010-08  # Exploration task that produced the plan
awaiting: []
covers:
  acceptance_criteria: []
  sections:
    - SEC-02  # Folder Structure
    - SEC-05  # User Flow Definition
    - SEC-06  # Meta Information Standards
    - SEC-07  # Cross-referencing System
    - SEC-08  # Skill Modifications
scope_description: "Implement shared user flows structure: update folder layout, READMEs, skills, scripts, and migrate existing content"
requirements_version:
  commit: 08f8e76
  file: ../requirements.md
related_exploration:
  task: TASK-PROC-010-08
  plan: ../2026-02-01_explore_shared_user_flows/plans_and_protocols/2026-02-01_01_plan_shared_flows.md
---

# Goal: Implement Shared User Flows Structure

## Objective

Implement the architectural changes designed in TASK-PROC-010-08 to restructure user flows from a nested persona-specific model to a shared model where flows live in `requirements_user_needs/user_flows/` and are referenced by multiple scenarios.

## Background

See the detailed exploration and design in:
`../2026-02-01_explore_shared_user_flows/plans_and_protocols/2026-02-01_01_plan_shared_flows.md`

### Key Design Decisions (Summary)

1. **Flow location**: New `user_flows/` folder at `requirements_user_needs/user_flows/`
2. **Flow IDs**: Simplified from `FLOW-NNN-NN-NN` to `FLOW-NNN` (sequential)
3. **Bidirectional references**:
   - Scenarios have `implements_flows` YAML field
   - Flows have `serves_scenarios` YAML field
4. **Information flow**: Content flows ONE-WAY down (Personas → Scenarios → Flows → Features)
5. **Cross-references**: Bidirectional for traceability, but NO automatic content propagation upward

## Scope

### In Scope

1. **Folder structure changes**
2. **README documentation updates**
3. **Skill modifications**
4. **Script updates**
5. **Existing content migration**
6. **CHANGE_PROPAGATION.md updates**

### Out of Scope

- Creating new user flows (separate content task)
- Creating new scenarios (separate content task)
- Modifying existing persona content

## Implementation Checklist

### Phase 1: Folder Structure

- [ ] Create `requirements_user_needs/user_flows/` directory
- [ ] Verify structure matches plan

### Phase 2: README Updates

KEEP THE INFORMATION DENSITY HIGH, don't document changes, don't explain to much, focus on stating rules.

Update the following files in `requirements_user_needs/`:

- [ ] **README_2_FOLDER_STRUCTURE.md**
  - Replace folder diagram to show `user_flows/` at top level alongside `personas/`
  - Update naming conventions section
  - Update integration explanation

- [ ] **README_5_USER_FLOW_DEFINITION.md**
  - Update template YAML: `serves_scenarios` replaces `scenario_id`
  - Update "Scenario" section to "Scenarios Served" table format
  - Add section: "Flows Serving Multiple Scenarios"
  - Update all path examples (flows now in `user_flows/` not under scenarios)

- [ ] **README_7_META_INFO_STANDARDS.md**
  - Update Flow ID generation: `FLOW-NNN` (sequential, 3-digit)
  - Add `implements_flows` field spec for scenarios
  - Add `serves_scenarios` field spec for flows
  - Remove hierarchical ID encoding explanation

- [ ] **README_8_CROSS-REFERENCING_SYSTEMS.md**
  - Update Scenario → Flow reference format
  - Update Flow → Scenario reference format
  - Add bidirectional validation rules
  - Clarify: references are bidirectional, content flow is one-way

- [ ] **README_13_CROSS_REFERENCE_NOTATION.md**
  - Update Flow ID format examples (FLOW-NNN)
  - Update path examples

- [ ] **CHANGE_PROPAGATION.md**
  - Add section: "Content Flow vs. Reference Flow"
  - Clarify: content flows DOWN only (Personas → Scenarios → Flows → Features)
  - Clarify: cross-references are bidirectional for traceability
  - Clarify: changes to flows NEVER auto-modify scenarios
  - Add: manual review prompts for downstream dependencies

### Phase 3: Skill Updates

KEEP THE INFORMATION DENSITY HIGH, don't document changes, don't explain to much, focus on stating rules.

Update skills in `.claude/skills/`:

- [ ] **create-user-flow/skill.md** (MAJOR CHANGES)
  - Change folder creation path to `requirements_user_needs/user_flows/[flow_name]/`
  - Change ID generation: count flows in `user_flows/`, generate FLOW-NNN
  - Add: "Which scenario(s) will this flow serve?" (allow multiple)
  - Populate `serves_scenarios` array in flow YAML
  - Update referenced scenarios: add `implements_flows` entry
  - Update all path references and examples

- [ ] **create-scenario/skill.md**
  - REMOVE: `user_flows/` subfolder creation (flows no longer live under scenarios)
  - ADD: "Which existing flows serve this scenario?" prompt
  - ADD: Populate `implements_flows` YAML field if flows selected
  - ADD: Update selected flows to add this scenario to `serves_scenarios`

- [ ] **modify-user-needs/skill.md**
  - Update impact analysis for bidirectional flow-scenario references
  - When modifying flow: identify all scenarios in `serves_scenarios` for review notification
  - When modifying scenario: validate flows in `implements_flows` still appropriate
  - ADD: validation for cross-reference consistency
  - CLARIFY: no auto-modification of upstream content

- [ ] **explore-requirements/skill.md**
  - Section 1.6 "Map User Needs": search new `user_flows/` location
  - Update grep patterns for user needs discovery

- [ ] **setup-task/skill.md**
  - Update "User Needs Reference Check" section
  - Update flow ID format expectations (FLOW-NNN)
  - Update path references for flows

### Phase 4: Script Updates

- [ ] **scripts/merge_user_needs.ps1**
  - Add `user_flows/` folder to processing paths
  - Update section ordering: Personas → Scenarios → User Flows
  - Test output includes flows section

- [ ] **scripts/generate_user_needs_status.py** (if exists)
  - Add validation: flows in `implements_flows` exist in `user_flows/`
  - Add validation: scenarios in `serves_scenarios` exist in `personas/`
  - Add validation: bidirectional consistency
  - Add warning: orphan flows (unreferenced)
  - Add warning: orphan scenarios (no flows)

### Phase 5: Content Migration

Migrate existing flow (FLOW-002-01-01 → FLOW-001):

- [ ] Create target directory:
  ```bash
  mkdir -p requirements_user_needs/user_flows/quick_night_entry
  ```

- [ ] Move flow file (preserve git history):
  ```bash
  git mv "requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows/quick_night_entry/flow.md" \
         "requirements_user_needs/user_flows/quick_night_entry/flow.md"
  ```

- [ ] Update flow YAML frontmatter:
  - Change `flow_id: FLOW-002-01-01` → `flow_id: FLOW-001`
  - Remove `scenario_id: SCEN-002-01`
  - Add `serves_scenarios` array with SCEN-002-01 entry
  - Add `version: "1.0"` if missing

- [ ] Update flow markdown:
  - Change "## Scenario" section to "## Scenarios Served" table
  - Update all relative paths to scenarios (now `../personas/...`)

- [ ] Update scenario YAML (`brain_dump_at_night/scenario.md`):
  - Add `implements_flows` field with FLOW-001 entry

- [ ] Update scenario markdown:
  - Update "## User Flows" section to reference new location

- [ ] Remove empty directories:
  ```bash
  rmdir "requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows/quick_night_entry"
  rmdir "requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows"
  ```

- [ ] Check other scenarios: Remove empty `user_flows/` folders if they exist

### Phase 6: Validation

- [ ] Run `scripts/merge_user_needs.ps1 -NoCommit` - verify output includes flows section
- [ ] Verify all README files are internally consistent
- [ ] Verify all skill files have consistent path references
- [ ] Manually test `create-user-flow` skill (dry run or actual test)
- [ ] Manually test `create-scenario` skill (verify no `user_flows/` folder created)
- [ ] Verify no broken cross-references in migrated content
- [ ] Run STATUS script if available

## Acceptance Criteria

- [ ] `requirements_user_needs/user_flows/` folder exists with migrated flow
- [ ] All 6 README files updated with consistent new structure
- [ ] All 5 skills updated with new paths and ID formats
- [ ] Merge script produces correct output with flows section
- [ ] Existing flow migrated with git history preserved
- [ ] Scenario references updated bidirectionally
- [ ] CHANGE_PROPAGATION.md clarifies one-way content flow
- [ ] No broken cross-references anywhere
- [ ] User approves final implementation

## YAML Field Specifications

### Scenario `implements_flows` Field

```yaml
implements_flows:
  - flow_id: FLOW-001
    relationship: primary | alternative | supporting
    coverage: full | partial | minimal
    notes: "Optional clarification"
```

### Flow `serves_scenarios` Field

```yaml
serves_scenarios:
  - scenario_id: SCEN-002-01
    persona_id: PERSONA-002
    persona_name: "Max (Client)"
    scenario_name: "Brain Dump at Night"
```

## Notes

- **Git history**: Use `git mv` for migration to preserve history
- **Atomic changes**: Update both sides of bidirectional references together
- **Test incrementally**: Validate after each phase before proceeding
- **Information flow reminder**: Content flows DOWN only; cross-references are for traceability

## References

- Exploration plan: `../2026-02-01_explore_shared_user_flows/plans_and_protocols/2026-02-01_01_plan_shared_flows.md`
- Parent requirement: `../requirements.md` (REQ-PROC-010)
