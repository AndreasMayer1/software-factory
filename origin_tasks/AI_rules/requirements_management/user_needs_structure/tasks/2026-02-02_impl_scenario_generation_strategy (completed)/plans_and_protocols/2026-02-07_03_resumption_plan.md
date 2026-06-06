# Resumption Plan: Batch Scenario Generation (Phase 3)

**Task**: TASK-PROC-010-10
**Date**: 2026-02-07
**Agent**: claude-sonnet-4-5-20250929
**Status**: Ready to execute

---

## Context: Why We're Resuming Now

The task was paused on 2026-02-05 due to critical data quality issues discovered during Phase 1-2. The blocking tasks are now complete:

✅ **TASK-PROC-010-11** (completed 2026-02-06): Fixed persona-scenario mismatches
- Max's scenarios kept with Max (depression), cleaned up ADHD language
- Max's partner renamed from "Sophie" to "Emma" to avoid confusion
- German text converted to English throughout
- Protocol names made concrete (e.g., "Angstprotokoll", "Stimmungsprotokoll")

✅ **TASK-PROC-010-12** (completed 2026-02-06): Created SCENARIO_INDEX.md
- Category-based organization by data flow stages
- Canonical naming conventions defined
- New YAML fields: `category`, `gold_status`
- Coverage matrix showing gaps across personas

---

## Current Gold Standards (User-Approved References)

From SCENARIO_INDEX.md and verified with scenario file checks:

| Scenario ID | Persona | Folder | Category | Outcome | Use For |
|-------------|---------|--------|----------|---------|---------|
| SCEN-001-01 | Dr. Sarah | prepare_protocol_for_client | creation.prepare_protocol | success | Therapist protocol preparation |
| SCEN-001-02 | Dr. Sarah | review_protocol_with_client | analysis.review_collaboratively | success | Therapist-client data review |
| SCEN-002-01 | Max | brain_dump_at_night | capture.spontaneous | failure | Client spontaneous capture (not gold in index) |
| SCEN-002-02 | Max | forgotten_protocol_transfer | analysis.transfer_to_therapist | failure | Client transfer failure |
| SCEN-002-03 | Max | prepare_for_therapy_session | analysis.prepare_for_session | partial | Client pre-session prep |
| SCEN-010-01 | Sophie | successful_protocol_handover | analysis.transfer_to_therapist | success | Client transfer success |

**Note**: SCEN-002-01 is NOT marked as gold_status in the index, so it should not be used as a reference yet.

---

## Original Scope (From goal.md)

Generate scenarios for these personas only (not all 12+ personas):
- **Therapists**: Prof. Dr. Weber, Dr. med. Turan
- **Clients**: Jana, Sophie (Sophie already has SCEN-010-01)

**Estimated scenarios to create**: ~15-20 total

---

## Revised Batch Generation Strategy (Category-Based)

Following the scenario index approach, generate by category rather than by persona:

### Batch 1: `creation.prepare_protocol` - Therapist Protocol Preparation
- **Gold standard**: SCEN-001-01 (Dr. Sarah - prepare_protocol_for_client)
- **Generate for**: Prof. Dr. Weber, Dr. med. Turan
- **Canonical folder name**: `prepare_protocol_for_client`
- **Expected scenarios**: 2 (one per therapist)

### Batch 2: `analysis.review_collaboratively` - Therapist-Client Data Review
- **Gold standard**: SCEN-001-02 (Dr. Sarah - review_protocol_with_client)
- **Generate for**: Prof. Dr. Weber, Dr. med. Turan
- **Canonical folder name**: `review_data_collaboratively`
- **Expected scenarios**: 2 (one per therapist)

### Batch 3: `analysis.prepare_for_session` - Client Pre-Session Prep
- **Gold standard**: SCEN-002-03 (Max - prepare_for_therapy_session)
- **Generate for**: Jana, Sophie
- **Canonical folder name**: `prepare_for_therapy_session`
- **Expected scenarios**: 2 (one per client)

### Batch 4: `capture.spontaneous` - Client Spontaneous Data Capture
- **Gold standard**: Need to verify if SCEN-002-01 is ready, or create new gold
- **Generate for**: Jana, Sophie (if applicable)
- **Canonical folder name**: `capture_data_spontaneously`
- **Expected scenarios**: 1-2 (depends on gold standard status and user guidance)

### Batch 5: `analysis.transfer_to_therapist` - Client Data Transfer
- **Gold standards**:
  - Success: SCEN-010-01 (Sophie - successful_protocol_handover) ⭐
  - Failure: SCEN-002-02 (Max - forgotten_protocol_transfer) ⭐
- **Generate for**: Jana (needs at least one transfer scenario)
- **Canonical folder name**: `transfer_data_to_therapist`
- **Variant suffix**: Use `__success` or `__failure` if same persona needs both
- **Expected scenarios**: 1-2 for Jana (at least one outcome variant)

### Batch 6: `capture.routine` - Routine Data Entry
- **Gold standard**: NONE - needs to be created first
- **Applicable to**: All client/self_user personas
- **Status**: DEFER until user decides if this should be in scope
- **Note**: This is a gap identified in scenario index but not in original goal.md

---

## Execution Approach

For each batch:

1. **Identify gold standard**: Confirm it exists and has `gold_status: true`
2. **Read gold standard**: Understand quality level, structure, persona-specific richness
3. **Check persona details**: Read persona.md for each target persona to understand their unique context, conditions, and challenges
4. **Use create-scenario skill**: Generate scenario with proper metadata
   - Include `category` field (dot notation)
   - Set `gold_status: false` (only user can mark as gold)
5. **Review for quality**:
   - Three-act structure present
   - Persona-specific (not generic)
   - Status quo focus (no app features)
   - Concrete protocol names specified
   - English-only (no German)
   - Proper YAML frontmatter
6. **Present to user**: Show generated scenario, get approval before continuing to next batch

---

## Quality Checklist (From 2026-02-03_02_opus_verification_analysis.md)

Every generated scenario must have:
- ✅ Three-act structure (Context & Inciting Incident / Rising Action / Resolution & Reflection)
- ✅ Persona-specific details (not generic)
- ✅ Concrete protocol names (e.g., "Angstprotokoll", not "the protocol")
- ✅ Status quo focus (how it works TODAY without the app)
- ✅ Proper emotional depth
- ✅ Complete YAML frontmatter with `category` and `gold_status` fields
- ✅ English-only (no German sprinkles)
- ✅ Evidence level notation (🟡 for proto-persona)

---

## Decision Points

**Q1**: Should we generate scenarios for categories not in the original scope (e.g., `capture.routine`, `self_review_and_reflect`)?
- **Original scope**: Only personas Prof. Weber, Dr. Turan, Jana, Sophie
- **Recommendation**: Stick to original scope for now, expand later if user requests

**Q2**: What about SCEN-002-01 (brain_dump_at_night)? It's not marked as gold in the index.
- **Status**: Not gold_status: true in SCENARIO_INDEX.md
- **Recommendation**: Do NOT use as reference until user confirms it should be gold

**Q3**: Should we rename existing scenario folders to match canonical names?
- **From scenario index**: "Renaming deferred — scenarios keep current folder names until batch generation phase"
- **Recommendation**: Do NOT rename existing folders; only NEW scenarios use canonical names

**Q4**: Should Jana get both success and failure variants of transfer scenario?
- **Recommendation**: Start with one (either success or failure based on Jana's persona traits), then ask user if they want both variants

---

## Next Steps (Immediate)

1. ✅ Update goal.md status: paused → in_progress
2. ✅ Create this resumption plan
3. ⏭️ Read Prof. Dr. Weber persona
4. ⏭️ Read Dr. med. Turan persona
5. ⏭️ Execute Batch 1: Generate `prepare_protocol_for_client` for Prof. Weber
6. ⏭️ Execute Batch 1: Generate `prepare_protocol_for_client` for Dr. Turan
7. ⏭️ Review both, present to user for approval
8. ⏭️ Continue with Batch 2 after user approval

---

## Success Criteria

- All generated scenarios match gold standard quality
- Each scenario has unique, persona-specific details (not copy-paste)
- User approves each batch before continuing
- All YAML metadata is complete and correct
- Scenario index can be updated with new instances

**Estimated effort for Phase 3**: 2-4 hours (depends on user review cycles)
