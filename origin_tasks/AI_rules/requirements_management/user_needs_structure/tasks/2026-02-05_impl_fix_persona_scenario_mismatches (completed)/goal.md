---
task_id: TASK-PROC-010-11
type: impl
parent_requirement: REQ-PROC-010
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-02-05
completed: 2026-02-06
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections:
    - SEC-03  # Persona Definition
    - SEC-04  # Scenario Definition
scope_description: "Fix critical data quality issues discovered during scenario generation: persona-scenario mismatches (ADHD incorrectly attributed to Max instead of Sophie), naming conflicts (Max's partner named Sophie), and language inconsistencies"
requirements_version:
  commit: 08f8e76
  file: ../requirements.md
---

# Goal: Fix Persona-Scenario Mismatches and Naming Conflicts

## Objective

Fix critical data quality issues in existing personas and scenarios that were discovered during Phase 1 of TASK-PROC-010-10 (Scenario Generation Strategy):

1. **Persona-Scenario Mismatches**: Two scenarios incorrectly attribute ADHD symptoms to Max (Depression/Burnout) when they should belong to Sophie (ADHD)
2. **Naming Conflicts**: Max's partner is named "Sophie" which conflicts with PERSONA-010 (Sophie, The Structure-Seeker)
3. **Language Inconsistency**: Mixed German/English in scenarios creates readability issues
4. **Protocol Specificity**: Scenarios lack concrete protocol names (e.g., "Angstprotokoll", "Stimmungsprotokoll")

## Requirements Summary

From the parent requirement (REQ-PROC-010: User Needs Structure Enhancement):
- SEC-03: Persona Definition guidelines and template
- SEC-04: Scenario Definition guidelines and template
- SEC-09: Writing Guidelines for consistency

**Context**: During verification of gold standard scenarios for Option F (Example-Driven Batch Generation), Opus analysis identified that:
- SCEN-002-01 (brain_dump_at_night) and SCEN-002-02 (forgotten_protocol_transfer) show ADHD-specific traits (executive dysfunction, object permanence, "Wall of Awful") but are assigned to Max who has Depression/Burnout, not ADHD
- Sophie (PERSONA-010) has ADHD and these scenarios fit her profile better
- Character naming creates confusion (Max's partner "Sophie" vs Sophie persona)

For complete requirements at task creation time:
```
git show 08f8e76:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

**Phase A: Immediate Corrections** (Quick wins)
1. Rename Max's partner from "Sophie" to another name (e.g., "Emma", "Lisa", "Anna")
   - Update 2 Max scenarios: prepare_for_therapy_session, and review_protocol_with_client (where Max appears). The other scenarios do not need to be updated because they will be assigned to another persona in a later task anyways.
2. Standardize language to **English-only** in all scenarios
   - Remove German sprinkles from all scenario narratives
   - Keep German for proper nouns/therapy terms if absolutely necessary
3. Add concrete protocol names to scenarios
   - Dr. Sarah scenarios: specify "Anxiety Protocol" (Angstprotokoll)
   - Max scenarios: specify "Mood Protocol" (Stimmungsprotokoll) or appropriate protocol type
   - Sophie scenarios: specify protocol type

**Phase B: Persona Reassignment** (Complex - requires planning)
1. Move/rewrite SCEN-002-01 (brain_dump) for Sophie
   - Currently shows ADHD traits, belongs with Sophie
   - Decision: Move to Sophie and adapt, or create new Sophie version and deprecate Max version
2. Move/rewrite SCEN-002-02 (forgotten_protocol) for Sophie
   - "Forgetting" is ADHD executive dysfunction, fits Sophie better than Max
   - Max needs a depression-appropriate "successful handover" scenario instead
3. Create new Max scenarios that fit Depression/Burnout profile
   - Max needs scenarios showing: drive disturbance, physical inertia, shame, "White Sheet Syndrome", memory fog, parking lot syndrome

**Phase C: Documentation Updates**
1. Update README_3_PERSONA_DEFINITION.md: Add naming rule "No persona names for supporting characters"
2. Update README_4_SCENARIO_DEFINITION.md:
   - Change language rule to "English-only" (remove German sprinkles guidance)
   - Add protocol specificity rule
3. Create naming conventions cross-check in scenario template

### Out of Scope

- Creating scenario index (separate task: TASK-PROC-010-12)
- Batch generation of new scenarios (returns to TASK-PROC-010-10 after fixes)
- Modifying persona definitions themselves (only scenario assignments change)

## Acceptance Criteria

### Phase A: Immediate Corrections
- [ ] Max's partner renamed consistently across all 4+ scenarios (no "Sophie" references)
- [ ] All scenarios converted to English-only (no German sprinkles in narrative)
- [ ] All scenarios specify concrete protocol names (e.g., "Anxiety Protocol", "Mood Protocol")
- [ ] README_3 updated with character naming rule
- [ ] README_4 updated with English-only language rule

### Phase B: Persona Reassignment
- [ ] SCEN-002-01 (brain_dump) reassigned/rewritten for Sophie or new version created
- [ ] SCEN-002-02 (forgotten_protocol) reassigned/rewritten for Sophie or new version created
- [ ] Max has appropriate Depression-focused scenarios (not ADHD-focused)
- [ ] All scenario YAML frontmatter updated (persona_id, scenario_id if moved)
- [ ] Cross-references updated (Related Scenarios sections)

### Phase C: Documentation
- [ ] README updates committed and merged
- [ ] Protocol documented in plans_and_protocols/ with decisions made
- [ ] Gold standard scenario quality maintained after changes

## Implementation Approach

**Execution Order**:

1. **Phase A: Immediate Corrections** (1-2 hours):
   - Quick, non-controversial fixes
   - Unblocks other work
   - Implementation engineer can execute directly
   - Execute NOW

2. **⏸️ PAUSE for TASK-PROC-010-12** (Scenario Index):
   - Before Phase B, we need the scenario index to guide persona reassignment
   - TASK-PROC-010-12 will:
     - Analyze existing scenario patterns
     - Create naming conventions
     - Provide structure for how scenarios should be named/organized
   - This informs Phase B decisions (Move vs Rewrite vs Create New)

3. **Phase B: Persona Reassignment** (requires Opus, after TASK-PROC-010-12 completes):
   - Complex decision: Move vs Rewrite vs Create New
   - Need to analyze what Max scenarios should look like for Depression
   - Need to decide if Sophie gets both "successful" and "failure" handover scenarios
   - **Use opus-workflow or switch-to-opus** for strategic planning
   - **Informed by**: Scenario index naming conventions from TASK-PROC-010-12

4. **Phase C: Documentation** (30 min, after Phase B):
   - Document lessons learned
   - Update guidelines

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-010-10 | paused | Scenario generation paused pending these fixes |
| TASK-PROC-010-12 | pending | **Blocks Phase B** - must complete index before persona reassignment |
| Existing 6 gold standard scenarios | exists | 4 need fixes (Max scenarios), 2 approved (Sophie handover, Max prepare) |
| README_3_PERSONA_DEFINITION.md | exists | Needs naming rule addition |
| README_4_SCENARIO_DEFINITION.md | exists | Needs language rule change |

## Notes

**User Feedback Summary** (2026-02-05):
- Protocols vary by condition - need to track specific protocol types for app requirements
- Sophie's successful handover approved
- Max doesn't have ADHD - scenarios showing ADHD traits are misattributed
- Forgotten protocol scenario fits Sophie better (ADHD forgetfulness)
- Brain dump scenario also shows ADHD traits (Wall of Awful, executive dysfunction)
- Partner naming conflict: Max's partner is "Sophie" but we have Sophie persona
- German/English mix doesn't work well - switch to English-only
- Need scenario naming consistency across personas (will be addressed in TASK-PROC-010-12)

**Risk**: These fixes may require updating scenarios that were just approved. However, data quality is critical for using them as gold standards for batch generation.

**Execution Flow**:
1. Complete Phase A of this task (immediate corrections)
2. Pause and execute TASK-PROC-010-12 (scenario index)
3. Resume this task for Phase B (persona reassignment using index guidance)
4. Complete Phase C (documentation)
5. Return to TASK-PROC-010-10 Phase 3 (batch generation) with corrected gold standards + index

---

## Context from TASK-PROC-010-12 (Scenario Index — completed 2026-02-06)

**Reference**: `requirements_user_needs/SCENARIO_INDEX.md`
**Design document**: `../2026-02-05_explore_scenario_index_naming (completed)/plans_and_protocols/2026-02-06_04_final_scenario_index.md`

### Scenario Naming Conventions (use for Phase B renaming)

When reassigning/renaming scenarios in Phase B, use the canonical names from the Scenario Index:

| Current Folder | Problem | Canonical Name |
|---------------|---------|---------------|
| `brain_dump_at_night` | Context-based, not goal-based | `capture_data_spontaneously` |
| `forgotten_protocol_transfer` | Outcome-based name | `transfer_data_to_therapist` |
| `successful_protocol_handover` | Outcome-based + wrong synonym | `transfer_data_to_therapist` |
| `review_protocol_with_client` | Minor mismatch | `review_data_collaboratively` (or keep as-is) |

**Naming rule**: `[action]_[object]_[qualifier]` — goal-based, no outcome in name.
**Variant suffix**: When same persona has multiple of same category: `[canonical_name]__[qualifier]` (double underscore).

### New Scenario Metadata Fields (add during Phase B)

When touching scenario YAML during reassignment, add these two new fields:

```yaml
category: "capture.spontaneous"     # dot-notation: stage_id.sub_category_suffix
gold_status: false                  # true only after user explicitly approves as gold standard
```

See `SCENARIO_INDEX.md` YAML frontmatter for the full list of valid category IDs.

### Gold Standard Workflow (applies to Phase B output)

1. Create/rewrite scenario for ONE persona
2. User reviews and approves
3. User marks `gold_status: true` in YAML
4. AI adapts gold scenario for all other relevant personas in that category

**Phase B implication**: After reassigning scenarios (e.g., moving brain_dump to Sophie), the user must re-approve them as gold standards before they're used for batch generation in TASK-PROC-010-10.

### Phase C Addition: Update SCENARIO_INDEX.md

After Phase B scenario reassignment, update `requirements_user_needs/SCENARIO_INDEX.md`:
- Move instance entries to correct personas
- Update `scenario_folder` if renamed
- Update `gold_status` (set to `false` for modified scenarios pending re-approval)
- Update `outcome` and `notes` fields
