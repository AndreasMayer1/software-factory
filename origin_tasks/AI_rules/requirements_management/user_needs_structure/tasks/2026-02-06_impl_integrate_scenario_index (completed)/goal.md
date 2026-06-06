---
task_id: TASK-PROC-010-13
type: impl
parent_requirement: REQ-PROC-010
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-02-06
completed: 2026-02-07
after: [TASK-PROC-010-12]
awaiting: []
blocks: [TASK-PROC-010-10]
covers:
  acceptance_criteria: []
  sections:
    - SEC-04  # Scenario Definition (category system integration)
    - SEC-06  # Meta Information Standards (new metadata fields)
    - SEC-08  # Skill Modifications (create-scenario, modify-user-needs)
scope_description: "Integrate SCENARIO_INDEX.md into create-scenario and modify-user-needs skills, add minimal README references, implement gold standard workflow"
requirements_version:
  commit: 08f8e76
  file: ../requirements.md
---

# Goal: Integrate SCENARIO_INDEX.md into Workflows and Skills

## Objective

Integrate the SCENARIO_INDEX.md (created in TASK-PROC-010-12) into the scenario creation and modification workflows, enabling:
1. Category-based scenario organization and naming
2. Gold standard workflow for batch generation
3. Automated index maintenance when scenarios are created or modified
4. Minimal but sufficient documentation in READMEs

This unblocks TASK-PROC-010-10 (batch scenario generation) which depends on the category system and gold standard tracking.

## Requirements Summary

From the parent requirement (REQ-PROC-010: User Needs Structure Enhancement):
- SEC-04: Scenario Definition guidelines and template
- SEC-06: Meta Information Standards (YAML frontmatter, IDs, evidence markers)
- SEC-08: Skill Modifications (create-persona, create-scenario, create-user-flow, modify-user-needs)

**Context**: TASK-PROC-010-12 created the SCENARIO_INDEX.md as the central registry for:
- Canonical category names and data flow stages
- Coverage tracking (which personas have which scenario types)
- Gold standard tracking (user-approved reference scenarios for batch generation)
- Naming conventions (action_object_qualifier format)

The index document itself is complete and approved. This task integrates it into the development workflow.

For complete requirements at task creation time:
```
git show 08f8e76:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

1. **Modify create-scenario skill** (`.claude/skills/create-scenario/skill.md`):
   - Read SCENARIO_INDEX.md before creating scenarios
   - Suggest canonical folder name based on category
   - Validate category assignment against index
   - Add `category` and `gold_status` fields to scenario YAML frontmatter
   - Update SCENARIO_INDEX.md instances array with new scenario
   - Implement gold standard workflow prompts

2. **Modify modify-user-needs skill** (`.claude/skills/modify-user-needs/skill.md`):
   - When `gold_status` changes in a scenario, update SCENARIO_INDEX.md accordingly
   - When scenario metadata changes (outcome, notes), update index entry

3. **Update README_4_SCENARIO_DEFINITION.md**:
   - Add brief (2-3 sentence) reference to SCENARIO_INDEX.md near the template section
   - Explain category system in 1 paragraph
   - Link to SCENARIO_INDEX.md for details
   - **Keep additions minimal** - no token bloat

4. **Update README_7_META_INFO_STANDARDS.md**:
   - Document `category` field in Scenario YAML Frontmatter section
   - Document `gold_status` field in Scenario YAML Frontmatter section
   - Include category format and values table
   - **Keep additions minimal** - reference index for full category list

5. **Document gold standard workflow**:
   - Add gold workflow section to create-scenario skill
   - Explain: create one → user approves → mark gold → batch generate others
   - Implement prompts in create-scenario to ask if scenario should be gold

### Out of Scope

- Renaming existing scenario folders (already handled by TASK-PROC-010-11)
- Batch generation of scenarios (separate task: TASK-PROC-010-10)
- Creating new categories (grow organically as needed—index is extensible)
- Modifying other skills beyond create-scenario and modify-user-needs
- Adding category/gold_status to existing scenarios (done in TASK-PROC-010-11)

## Acceptance Criteria

### Skills Integration
- [ ] create-scenario skill reads SCENARIO_INDEX.md on startup
- [ ] create-scenario skill suggests canonical folder name based on selected category
- [ ] create-scenario skill validates that chosen category exists in index
- [ ] create-scenario skill adds `category` and `gold_status` fields to new scenario YAML
- [ ] create-scenario skill updates SCENARIO_INDEX.md instances array after creation
- [ ] create-scenario skill prompts user about gold standard designation
- [ ] modify-user-needs skill updates SCENARIO_INDEX.md when gold_status changes
- [ ] modify-user-needs skill updates index entry when scenario outcome/notes change

### Documentation
- [ ] README_4 has brief (2-3 sentence) link to SCENARIO_INDEX.md near template
- [ ] README_4 has 1 paragraph explaining category system
- [ ] README_7 documents `category` field with format and example values
- [ ] README_7 documents `gold_status` field with true/false meaning
- [ ] README additions are minimal (no unnecessary token bloat)

### Gold Standard Workflow
- [ ] create-scenario skill documents gold workflow process (create → approve → mark → batch)
- [ ] create-scenario skill prompts: "Is this the first scenario in its category? Should it be marked as gold standard?"
- [ ] Gold workflow is integrated into skill's step-by-step process

### Quality Validation
- [ ] All skill modifications follow existing skill structure and conventions
- [ ] YAML parsing/writing preserves existing formatting and fields
- [ ] Index updates preserve YAML structure and comments
- [ ] No breaking changes to existing create-scenario or modify-user-needs functionality

## Implementation Approach

**Phase 1: Skill Modifications** (primary work)

1. **Update create-scenario skill**:
   - Add step to read SCENARIO_INDEX.md after reading READMEs (Step 1)
   - Parse YAML frontmatter to extract available categories
   - In Step 2 (Gather Information), add category selection:
     - Display available categories grouped by stage
     - Suggest canonical name based on selected category
     - Validate that category exists in index
   - In Step 5 (Generate scenario.md), add to template:
     ```yaml
     category: "[stage].[sub_category]"  # from user's selection
     gold_status: false                  # default, unless user designates as gold
     ```
   - Add new Step 6.5 (Update Index):
     - Read SCENARIO_INDEX.md
     - Find matching category in stages → categories → instances
     - Append new instance entry
     - Write back SCENARIO_INDEX.md
   - Add gold standard prompts:
     - "Is this the first scenario for this persona in the [category] category?"
     - "Should this be designated as a gold standard for batch generation?"

2. **Update modify-user-needs skill**:
   - In Opus Mode Step 3b (Update Metadata), add index maintenance:
     - If `gold_status` changed: Update corresponding instance in SCENARIO_INDEX.md
     - If scenario `outcome` or `notes` changed: Update index entry
   - In Standard Mode Step 8 (Update Metadata), add same index maintenance

**Phase 2: Documentation** (minimal additions)

1. **Update README_4_SCENARIO_DEFINITION.md**:
   - Find "Scenario Template" section (around line 129)
   - Add before template:
     ```markdown
     ### Scenario Categories

     Scenarios are organized into categories following the therapy data flow (Plan Creation → Distribution → Capture → Analysis → Management). Each scenario belongs to a category defined in [SCENARIO_INDEX.md](SCENARIO_INDEX.md), which provides:
     - Canonical folder naming conventions
     - Coverage tracking across personas
     - Gold standard designation for batch generation

     When creating a scenario, select the appropriate category from the index. The `create-scenario` skill will guide you through this.
     ```

2. **Update README_7_META_INFO_STANDARDS.md**:
   - Find "Scenario YAML Frontmatter" section (around line 38)
   - Add two new fields to the example:
     ```yaml
     category: "capture.spontaneous"    # See SCENARIO_INDEX.md for valid values
     gold_status: false                 # true = user-approved gold standard
     ```
   - Add field descriptions after the example:
     ```markdown
     - `category`: Dot-notation category ID (`[stage].[sub_category]`). Valid values defined in SCENARIO_INDEX.md. Categories follow the therapy data flow: creation, distribution, capture, analysis, management.
     - `gold_status`: Boolean indicating if this is a user-approved gold standard scenario for its category. Gold standards are used as references for batch-generating scenarios for other personas. Default: `false`.
     ```

**Phase 3: Testing & Validation**

1. Test create-scenario skill with index integration
2. Test modify-user-needs skill with index updates
3. Verify README additions are clear and minimal
4. Check that existing skill functionality remains intact

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-010-12 | completed | SCENARIO_INDEX.md created and placed at requirements_user_needs/SCENARIO_INDEX.md |
| TASK-PROC-010-11 | completed | Existing scenarios have category and gold_status fields added |

## Notes

**Design Principles**:
1. **Minimal documentation burden**: Keep README additions as short as possible—SCENARIO_INDEX.md is the detailed reference
2. **Skill integration first**: The primary value is in the skills using the index, not in documenting it extensively
3. **Backward compatibility**: Existing scenarios without category/gold_status should still work (skills handle gracefully)
4. **Extensible categories**: Skills should not hardcode category lists—always read from index
5. **Gold workflow is optional**: Not every scenario needs to be gold standard—batch generation can happen later

**Token Optimization**:
- README_4 addition: ~150 tokens (brief paragraph + link)
- README_7 addition: ~100 tokens (two field definitions + category reference)
- Total README additions: ~250 tokens (acceptable overhead for critical functionality)

**Gold Standard Workflow Details** (from TASK-PROC-010-12 findings):
1. Create scenario for ONE persona in a category (e.g., Max's "capture_data_spontaneously")
2. User reviews and provides feedback
3. User marks `gold_status: true` in YAML (manually or via skill)
4. AI adapts gold scenario for other relevant personas in batch generation
5. Index tracks gold status for coverage analysis

This workflow ensures every batch-generated scenario has a user-approved reference, maintaining quality at scale.
