---
task_id: TASK-PROC-010-10
type: impl
parent_requirement: REQ-PROC-010
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-02-02
paused_date: 2026-02-05
paused_reason: "Discovered critical data quality issues during Phase 1-2 (persona mismatches, naming conflicts). Must complete TASK-PROC-010-11 and TASK-PROC-010-12 before resuming Phase 3."
completed: 2026-02-07
after: []
awaiting: [TASK-PROC-010-11, TASK-PROC-010-12]
covers:
  acceptance_criteria: []
  sections:
    - SEC-04  # Scenario Definition
    - SEC-09  # Writing Guidelines
scope_description: "Implement Option F (Example-Driven Batch Generation) for efficient scenario creation as recommended in exploration findings"
requirements_version:
  commit: 08f8e76
  file: ../requirements.md
---

# Goal: Implement Scenario Generation Strategy (Option F)

## Objective

Implement the **Example-Driven Batch Generation** approach (Option F) for creating persona scenarios efficiently, as recommended in the exploration findings.

This task implements the strategy for AI-authored scenarios that optimizes for quality and review efficiency rather than writing effort.

## Background

**Exploration findings**: [2026-02-01_explore_efficient_scenario_creation/plans_and_protocols/2026-02-01_01_exploration_findings.md](../2026-02-01_explore_efficient_scenario_creation/plans_and_protocols/2026-02-01_01_exploration_findings.md)

**Key insight**: For AI-authored scenarios, writing effort is trivial. The real challenge is ensuring consistent quality while minimizing human review burden. Option F uses example-driven batch generation instead of creating archetype files.

## Requirements Summary

From the exploration findings, Option F requires:

1. **Verify/create gold standard example scenarios** (~4-6 examples total)
   - At least one therapist example per goal pattern
   - At least one client example per goal pattern

2. **Generate remaining scenarios in batches** by goal pattern
   - All therapist scenarios (3 personas × ~5 patterns = ~15 scenarios)
   - All client scenarios (4+ personas × ~5 patterns = ~20+ scenarios)

3. **No new folder structures or archetype files**
   - Keep existing structure unchanged
   - Use examples as implicit pattern guides

For complete exploration findings at task creation time:
```
git show 08f8e76:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/2026-02-01_explore_efficient_scenario_creation/plans_and_protocols/2026-02-01_01_exploration_findings.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

1. **Verify existing example quality**:
   - Dr. Sarah's "prepare protocol" scenario
   - Dr. Sarah's "review with client" scenario
   - Max's "brain dump at night" scenario
   - Max's "forgotten protocol transfer" scenario

2. **Create missing example scenarios** (if needed):
   - One client "prepare for session" scenario
   - One client "share with therapist" scenario

3. **Batch generate scenarios** for:
   - Prof. Dr. Weber (therapist): ~5 scenarios
   - Dr. med. Turan (therapist): ~5 scenarios
   - Jana (client): ~5 scenarios
   - Sophie (client): ~5 scenarios

4. **Review batches** for quality and consistency

5. **Optional: Add brief note to README_4** about AI scenario generation

### Out of Scope

- Creating scenario archetype files (explicitly rejected in favor of Option F)
- Modifying folder structure
- Creating new skills (existing skills are sufficient)
- Generating scenarios for personas not yet created

## Acceptance Criteria

- [ ] All existing example scenarios are verified for quality
- [ ] Missing example scenarios are created (if any gaps identified)
- [ ] All scenarios generated for Prof. Dr. Weber (5 scenarios)
- [ ] All scenarios generated for Dr. med. Turan (5 scenarios)
- [ ] All scenarios generated for Jana (5 scenarios)
- [ ] All scenarios generated for Sophie (5 scenarios)
- [ ] Each batch reviewed for quality and consistency
- [ ] All generated scenarios follow the three-act structure
- [ ] All generated scenarios maintain status quo focus (no app features)
- [ ] All generated scenarios have proper YAML frontmatter
- [ ] Optional: README_4 updated with brief AI generation note

## Implementation Approach

**Phase 1: Example Verification** (30 min)
1. Review existing example scenarios
2. Identify any quality issues
3. Determine if additional examples needed

**Phase 2: Example Creation** (if needed, ~1-2 hours)
1. Create missing client example scenarios
2. Ensure examples cover the goal patterns

**Phase 3: Batch Generation** (~1-2 hours)
1. **Batch 1**: All therapist "prepare homework" scenarios
   - Generate: Prof. Weber, Dr. Turan
   - Review together for consistency

2. **Batch 2**: All therapist "review with client" scenarios
   - Generate: Prof. Weber, Dr. Turan
   - Review together

3. **Batch 3**: All client scenarios
   - Generate: Jana (BPD), Sophie (ADHD) scenarios
   - Review together by goal pattern

**Phase 4: Quality Review** (1-2 hours)
1. Review all generated scenarios against examples
2. Verify persona-specific richness
3. Check YAML metadata completeness

**Phase 5: Documentation** (30 min)
1. Optionally add brief note to README_4
2. Update this task with completion notes

## Task Status: PAUSED

**Current Progress** (as of 2026-02-05):
- ✅ **Phase 1 COMPLETED**: Example verification done
  - Opus analysis completed: `plans_and_protocols/2026-02-03_02_opus_verification_analysis.md`
  - 8 defects identified and fixed
  - 4 original gold standards verified and corrected
- ✅ **Phase 2 COMPLETED**: Missing examples created
  - SCEN-002-03: Max prepares for session (created)
  - SCEN-010-01: Sophie successful handover (created)
  - Total gold standards: 6 scenarios
- ⏸️ **Phase 3 BLOCKED**: Waiting for data quality fixes
  - TASK-PROC-010-11: Fix persona-scenario mismatches (in progress)
  - TASK-PROC-010-12: Create scenario index (pending)

**Why Paused**:
During Phase 1 verification, critical data quality issues were discovered:
1. Persona mismatches: Max scenarios show ADHD traits but Max has Depression (not ADHD)
2. Naming conflicts: Max's partner named "Sophie" conflicts with Sophie persona
3. Language inconsistency: Mixed German/English creates readability issues
4. Missing scenario index: Need systematic naming to prevent chaos during batch generation

**Blocking Tasks**:
1. **TASK-PROC-010-11** (Fix persona-scenario mismatches): Must complete before batch generation
2. **TASK-PROC-010-12** (Create scenario index): Provides naming conventions for batch generation

## HOW TO RESUME (For Future Session)

**When TASK-PROC-010-11 and TASK-PROC-010-12 are complete:**

### Step 1: Verify Prerequisites
Read these files to understand what changed:
- `../2026-02-05_impl_fix_persona_scenario_mismatches/plans_and_protocols/` - What was fixed
- `../2026-02-05_explore_scenario_index_naming/plans_and_protocols/` - Scenario index and naming rules
- `requirements_user_needs/SCENARIO_INDEX.md` (if created) - Canonical scenario names

### Step 2: Identify Current Gold Standards
After fixes, the gold standards will be:
- **Therapist scenarios** (2):
  - Dr. Sarah: prepare_protocol_for_client
  - Dr. Sarah: review_protocol_with_client
- **Client scenarios** (4+):
  - Max: prepare_for_therapy_session (Depression-specific)
  - Sophie: successful_protocol_handover (ADHD-specific)
  - Sophie: ??? (might have gained ADHD scenarios from Max)
  - Check: Did brain_dump and forgotten_protocol move to Sophie?

### Step 3: Resume at Phase 3 - Batch Generation
Execute batch generation using the scenario index naming conventions:

**Batch 1: Therapist "Prepare Homework" Scenarios**
- Reference: SCEN-001-01 (Dr. Sarah prepare_protocol_for_client)
- Generate for: Prof. Dr. Weber, Dr. med. Turan
- Use create-scenario skill with gold standard reference
- Review both together for cross-persona consistency

**Batch 2: Therapist "Review with Client" Scenarios**
- Reference: SCEN-001-02 (Dr. Sarah review_protocol_with_client)
- Generate for: Prof. Dr. Weber, Dr. med. Turan
- Review both together

**Batch 3: Client "Prepare for Session" Scenarios**
- Reference: SCEN-002-03 (Max prepare_for_therapy_session)
- Generate for: Jana, Sophie (if Sophie doesn't already have one)
- Review by persona differences (BPD vs ADHD vs Depression)

**Batch 4: Client "Successful Handover" Scenarios**
- Reference: SCEN-010-01 (Sophie successful_protocol_handover)
- Generate for: Max, Jana (if they need successful versions)
- Review together

**Batch 5: Additional Client Scenarios** (if applicable)
- If brain_dump/forgotten_protocol moved to Sophie, generate equivalents for other clients
- Check scenario index for required patterns

### Step 4: Quality Review
For each generated scenario:
- Verify against Opus checklist: `plans_and_protocols/2026-02-03_02_opus_verification_analysis.md`
- Check naming matches scenario index
- Verify persona-specific traits (not generic)
- Confirm all template sections present
- English-only (no German sprinkles)
- Concrete protocol names specified

### Step 5: User Review Checkpoint
After each batch, pause for user review before continuing.

### Step 6: Complete Task
- Update acceptance criteria checkboxes
- Document any deviations from original plan
- Note lessons learned for future scenario generation

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-010-09 | completed | Exploration findings complete |
| **TASK-PROC-010-11** | **in-progress** | **BLOCKING** - Must complete before resuming Phase 3 |
| **TASK-PROC-010-12** | **pending** | **BLOCKING** - Scenario index needed for batch generation |
| Existing personas | exists | Dr. Sarah, Prof. Weber, Dr. Turan, Max, Jana, Sophie |
| Existing example scenarios | exists | 6 gold standards (after fixes) |

## Notes

**Estimated total effort**: 6-9 hours
- Example verification/creation: 2-3 hours
- Batch generation: 1-2 hours
- Quality review: 2-3 hours
- Documentation: 1 hour

**Success metric**: All personas have complete scenario coverage with consistent quality, generated efficiently using example-driven approach.

---

## Context from TASK-PROC-010-12 (Scenario Index — completed 2026-02-06)

**Reference**: `requirements_user_needs/SCENARIO_INDEX.md`
**Design document**: `../2026-02-05_explore_scenario_index_naming (completed)/plans_and_protocols/2026-02-06_04_final_scenario_index.md`

### How the Scenario Index Changes Batch Generation

The Scenario Index introduces a **category-based approach** to batch generation. Instead of generating "by persona" (all scenarios for Prof. Weber, then all for Dr. Turan), generate **by category** (all `prepare_protocol_for_client` across therapist personas, then all `review_data_collaboratively`, etc.).

**Revised Phase 3 approach**:
1. Pick a category from the index (e.g., `capture.spontaneous`)
2. Identify the gold standard instance (e.g., SCEN-002-01, Max's brain dump — ⭐ in the index)
3. Check `applicable_roles` to know which personas need this category
4. Generate scenario for each applicable persona, adapting the gold standard
5. Use the `canonical_name` as folder name for each new scenario
6. Update SCENARIO_INDEX.md with new instances after each batch

### Gold Standard Workflow (NEW — integrates with batch generation)

1. **Create** scenario for ONE persona in a category
2. **User reviews** and provides feedback
3. **User marks** `gold_status: true` in scenario YAML
4. **AI adapts** gold scenario for all other relevant personas
5. **Index updated** with new instances

This means: Do NOT batch-generate until the gold standard for that category is approved. The workflow is sequential per category, not parallel across all categories.

### New Scenario Metadata Fields (add to all generated scenarios)

Every new scenario's YAML frontmatter must include:

```yaml
category: "capture.spontaneous"     # dot-notation from SCENARIO_INDEX.md
gold_status: false                  # only true after explicit user approval
```

### Coverage Matrix as Generation Checklist

The coverage matrix in SCENARIO_INDEX.md shows exactly what needs to be generated:

| Symbol | Meaning | Action |
|--------|---------|--------|
| ⭐ | Gold standard exists | Use as reference for batch generation |
| 🔲 | Applicable but missing | Generate scenario |
| ─ | Not applicable | Skip |

Currently ~12 cells marked 🔲 = scenarios to generate. Most impactful gaps:
- `routine_data_entry` — no gold standard yet, affects all client/self_user personas
- `self_review_and_reflect` — no gold standard yet, core self_user scenario

### Naming Convention (use for all new scenarios)

**Folder name** = canonical_name from index (e.g., `capture_data_spontaneously`)
**Variant suffix** (if same persona has multiple): `__[qualifier]` (double underscore)
**Outcome**: In YAML metadata only, NOT in folder name

### Process Integration with create-scenario Skill

When using the create-scenario skill for batch generation:
1. Skill reads SCENARIO_INDEX.md YAML to get canonical name
2. Validates folder name matches canonical_name
3. Pre-populates `category` field in YAML
4. After creation, updates SCENARIO_INDEX.md instances array

### Updated Batching Strategy

Replace the original batching (by persona) with batching by category:

**Batch 1**: `creation.prepare_protocol` — therapist personas (Prof. Weber, Dr. Turan)
**Batch 2**: `analysis.review_collaboratively` — therapist personas
**Batch 3**: `capture.spontaneous` — client personas (Jana, Sophie if applicable)
**Batch 4**: `analysis.prepare_for_session` — client personas
**Batch 5**: `analysis.transfer_to_therapist` — client personas
**Batch 6**: `capture.routine` — needs gold standard first, then all client/self_user
**Batch 7**: `analysis.self_reflect` — needs gold standard first, then self_user personas

Each batch: generate → user review → mark gold if first of category → continue.
