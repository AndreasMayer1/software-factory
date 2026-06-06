# High-Level Implementation Plan: Integrate SCENARIO_INDEX.md into Workflows

**Task**: TASK-PROC-010-13
**Agent**: architecture-advisor
**Created**: 2026-02-07
**Status**: Awaiting User Approval

---

## Executive Summary

This plan integrates the SCENARIO_INDEX.md (created in TASK-PROC-010-12) into the scenario creation and modification workflows. The index provides category-based organization, gold standard tracking, and coverage analysis capabilities. This implementation enables structured scenario creation and prepares for batch generation (TASK-PROC-010-10).

**Scope**: 2 skill modifications + 2 minimal README updates
**Complexity**: Medium (systematic skill enhancement with YAML manipulation)
**Risk Level**: Low (no breaking changes to existing functionality)

---

## Analysis Summary

### Current State Assessment

#### SCENARIO_INDEX.md Structure
The index (created in TASK-PROC-010-12) provides:
- **5 data flow stages**: creation → distribution → capture → analysis → management
- **10 categories** across stages (e.g., `capture.spontaneous`, `analysis.transfer_to_therapist`)
- **Canonical naming conventions**: `[action]_[object]_[qualifier]` pattern
- **Coverage tracking**: Which personas have scenarios in which categories
- **Gold standard registry**: User-approved reference scenarios for batch generation
- **Existing mappings**: 6 scenarios already categorized with `category` and `gold_status` fields (TASK-PROC-010-11)

#### Current Skills State

**create-scenario skill** (`.claude/skills/create-scenario/skill.md`):
- **Line 22-35**: Reads 6 READMEs in parallel (good foundation)
- **Line 62-78**: Gathers scenario information from user
- **Line 114-119**: Creates scenario.md with YAML template
- **Line 126-155**: Updates bidirectional flow references
- **Missing**: No category selection, no index integration, no gold standard workflow

**modify-user-needs skill** (`.claude/skills/modify-user-needs/skill.md`):
- **Opus Mode** (lines 52-220): Sonnet gathers → Opus plans → Sonnet executes
- **Standard Mode** (lines 222-391): Sonnet-only workflow
- **Step 3b/8**: Update metadata sections (YAML frontmatter changes)
- **Missing**: No index maintenance when `gold_status` or category changes

#### README State

**README_4_SCENARIO_DEFINITION.md**:
- **Line 145-296**: Scenario template section
- **Missing**: No mention of category system or SCENARIO_INDEX.md
- **Token count**: ~12,500 tokens (large but not bloated)

**README_7_META_INFO_STANDARDS.md**:
- **Line 36-60**: Scenario YAML Frontmatter section
- **Missing**: No `category` or `gold_status` field documentation
- **Token count**: ~6,200 tokens (moderate size)

### Gap Analysis

| Component | Current State | Needed State | Gap Size |
|-----------|--------------|--------------|----------|
| create-scenario | No category workflow | Category selection + index update | Medium |
| create-scenario | No gold workflow | Gold standard prompts | Small |
| modify-user-needs | No index sync | Update index on metadata changes | Medium |
| README_4 | No category docs | Brief category intro + link | Small |
| README_7 | No new fields | Document 2 new YAML fields | Small |

---

## Scope of Work

### Files to Modify (4 total - within limit)

1. **`.claude/skills/create-scenario/skill.md`** (Primary modification)
   - Add SCENARIO_INDEX.md reading step
   - Add category selection in information gathering
   - Add index update step after scenario creation
   - Add gold standard workflow prompts

2. **`.claude/skills/modify-user-needs/skill.md`** (Secondary modification)
   - Add index maintenance in Opus Mode Step 3b
   - Add index maintenance in Standard Mode Step 8

3. **`requirements_user_needs/README_4_SCENARIO_DEFINITION.md`** (Minimal addition)
   - Add category system intro (150 tokens)
   - Add link to SCENARIO_INDEX.md

4. **`requirements_user_needs/README_7_META_INFO_STANDARDS.md`** (Minimal addition)
   - Add `category` field documentation (50 tokens)
   - Add `gold_status` field documentation (50 tokens)

**Total files**: 4 (within CLAUDE.md limit of 4 files for simple tasks)

---

## Architecture Strategy

### Design Principles

1. **Read-first architecture**: Skills read index as source of truth, never hardcode categories
2. **Bidirectional consistency**: Index tracks scenarios, scenarios reference categories
3. **Graceful degradation**: Skills handle missing fields for backward compatibility
4. **Minimal documentation**: READMEs point to index, don't duplicate it
5. **Gold workflow optional**: Not every scenario needs gold designation
6. **Category extensibility**: Categories grow organically, index updated manually as needed

### YAML Manipulation Strategy

**Challenges**:
- YAML frontmatter editing requires precision
- Must preserve existing fields and formatting
- Comments in SCENARIO_INDEX.md must be preserved

**Approach**:
- Read entire file content
- Parse YAML using string manipulation (reliable for simple structures)
- Append to arrays (scenarios → instances array in index)
- Write back entire file with preserved structure

### Integration Points

```
create-scenario skill
    │
    ├─ Reads: SCENARIO_INDEX.md (startup)
    │          └─ Extracts: Available categories + existing instances
    │
    ├─ Prompts: User for category selection
    │          └─ Validates: Category exists in index
    │
    ├─ Generates: scenario.md with category + gold_status fields
    │
    └─ Updates: SCENARIO_INDEX.md (append to instances array)
               └─ Preserves: YAML structure + comments

modify-user-needs skill
    │
    ├─ Detects: Changes to gold_status or category fields
    │
    └─ Updates: SCENARIO_INDEX.md (modify instance entry)
               └─ Preserves: All other fields
```

---

## Execution Plan

### Phase 1: Skill Modifications (Primary Work)

#### Step 1.1: Modify create-scenario skill

**File**: `.claude/skills/create-scenario/skill.md`

**Changes**:

1. **Add SCENARIO_INDEX.md to mandatory reads** (after line 35):
   ```markdown
   | `SCENARIO_INDEX.md` | Categories, naming conventions, gold tracking |
   ```

2. **Add category selection** (in Step 2, after line 78):
   ```markdown
   - **Category selection**:
     - Read SCENARIO_INDEX.md and parse available categories
     - Display categories grouped by stage (creation, distribution, capture, analysis, management)
     - Ask user to select category (format: `[stage].[sub_category]`)
     - Validate that category exists in index
     - Suggest canonical folder name based on category (from index's `canonical_name` field)
   ```

3. **Update YAML template** (in Step 5, after line 114):
   ```markdown
   category: "[stage].[sub_category]"  # From user's selection in Step 2
   gold_status: false                  # Default, unless user designates as gold (see Step 6.5)
   ```

4. **Add gold standard workflow** (new step after Step 2):
   ```markdown
   ### 2.5. Gold Standard Designation (Optional)

   Ask user:
   - "Is this the first scenario for this persona in the [category] category?"
   - "Should this be designated as a gold standard for batch generation?"

   If yes:
   - Set `gold_status: true` in YAML
   - Explain: Gold standards are user-approved references used to batch-generate scenarios for other personas
   ```

5. **Add index update step** (new step between current steps 6 and 7):
   ```markdown
   ### 6.5. Update SCENARIO_INDEX.md

   After creating scenario.md, update the index:

   1. Read SCENARIO_INDEX.md
   2. Parse YAML to find matching category under `stages → categories → instances`
   3. Append new instance entry:
      ```yaml
      - persona_id: PERSONA-[ID]
        persona_folder: [folder_name]
        scenario_id: SCEN-[ID]
        scenario_folder: [scenario_folder_name]
        outcome: [success|failure|partial]  # Ask user
        gold_status: [true|false]           # From Step 2.5
        notes: "[Brief description from scenario goal]"
      ```
   4. Write back SCENARIO_INDEX.md preserving:
      - All YAML comments (lines starting with #)
      - Indentation structure
      - Other categories and instances

   **Validation**: Verify category ID matches (e.g., `capture.spontaneous`)
   ```

**WHY Comments Needed**:
- ✅ **YAML parsing logic**: Why string-based instead of library (simple structure, preserves comments)
- ✅ **Gold workflow placement**: Why ask before creation, not after (prevents forgotten designation)
- ✅ **Index update timing**: Why after scenario creation, not before (ensures scenario exists if index update fails)

**Estimated lines added**: ~80 lines

#### Step 1.2: Modify modify-user-needs skill

**File**: `.claude/skills/modify-user-needs/skill.md`

**Changes**:

1. **Add index maintenance to Opus Mode** (after line 179 in Step 3b):
   ```markdown
   **Index Maintenance** (if scenario modified):

   If `category` or `gold_status` fields changed:
   1. Read SCENARIO_INDEX.md
   2. Find instance entry matching scenario_id
   3. Update instance fields:
      - `gold_status`: Update to new value
      - `outcome`: Update if scenario outcome changed
      - `notes`: Update if scenario goal/context changed
   4. Write back SCENARIO_INDEX.md preserving structure

   **Validation**: Verify category exists in index before update
   ```

2. **Add index maintenance to Standard Mode** (after line 354 in Step 8):
   ```markdown
   **Index Maintenance** (if scenario modified):

   [Same content as Opus Mode above]
   ```

**WHY Comments Needed**:
- ✅ **Bidirectional sync**: Why update index when scenario changes (maintain single source of truth)
- ✅ **Validation before update**: Why check category existence (prevent orphaned references)

**Estimated lines added**: ~30 lines (15 per mode, largely duplicated)

### Phase 2: Documentation Updates (Minimal)

#### Step 2.1: Update README_4_SCENARIO_DEFINITION.md

**File**: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`

**Location**: Before "Scenario Template" section (around line 145)

**Addition**:
```markdown
### Scenario Categories

Scenarios are organized into categories following the therapy data flow (Plan Creation → Distribution → Capture → Analysis → Management). Each scenario belongs to a category defined in [SCENARIO_INDEX.md](SCENARIO_INDEX.md), which provides:
- Canonical folder naming conventions
- Coverage tracking across personas
- Gold standard designation for batch generation

When creating a scenario, select the appropriate category from the index. The `create-scenario` skill will guide you through this process.

**Gold Standard Workflow**: Create one scenario as a reference → user reviews and approves → mark `gold_status: true` → use as template for batch-generating scenarios for other personas.
```

**Token count**: ~150 tokens (acceptable overhead)

**WHY Comments Needed**: None (simple documentation addition)

#### Step 2.2: Update README_7_META_INFO_STANDARDS.md

**File**: `requirements_user_needs/README_7_META_INFO_STANDARDS.md`

**Location 1**: In "Scenario YAML Frontmatter" example (after line 45)

**Addition to example**:
```yaml
category: "capture.spontaneous"    # See SCENARIO_INDEX.md for valid values
gold_status: false                 # true = user-approved gold standard
```

**Location 2**: After example (around line 60)

**Addition**:
```markdown
**New fields** (added 2026-02-06, TASK-PROC-010-12/13):

- `category`: Dot-notation category ID (`[stage].[sub_category]`). Valid values defined in SCENARIO_INDEX.md. Categories follow the therapy data flow: creation → distribution → capture → analysis → management.
  - Examples: `capture.spontaneous`, `analysis.transfer_to_therapist`, `creation.prepare_protocol`

- `gold_status`: Boolean indicating if this is a user-approved gold standard scenario for its category. Gold standards are used as references for batch-generating scenarios for other personas. Default: `false`.
```

**Token count**: ~100 tokens (acceptable overhead)

**WHY Comments Needed**: None (simple field documentation)

### Phase 3: Testing & Validation

#### Step 3.1: Validation Checklist

**Skill Integration**:
- [ ] create-scenario reads SCENARIO_INDEX.md on startup
- [ ] create-scenario displays available categories grouped by stage
- [ ] create-scenario validates selected category exists in index
- [ ] create-scenario suggests canonical folder name from category
- [ ] create-scenario adds `category` and `gold_status` to new scenario YAML
- [ ] create-scenario prompts for gold standard designation
- [ ] create-scenario updates SCENARIO_INDEX.md instances array after creation
- [ ] modify-user-needs updates index when `gold_status` changes
- [ ] modify-user-needs updates index when scenario outcome/notes change

**Documentation**:
- [ ] README_4 has category system introduction (2-3 sentences + link)
- [ ] README_4 has gold workflow explanation (1 paragraph)
- [ ] README_7 has `category` field documentation with format and examples
- [ ] README_7 has `gold_status` field documentation with meaning
- [ ] README additions are minimal (no token bloat)

**Quality**:
- [ ] YAML parsing preserves comments in SCENARIO_INDEX.md
- [ ] YAML parsing preserves indentation structure
- [ ] Index updates don't break existing instances
- [ ] Skills handle scenarios without category/gold_status gracefully (backward compatibility)
- [ ] No breaking changes to existing skill functionality

**Edge Cases**:
- [ ] What if user tries to create scenario with non-existent category? (Validation prevents)
- [ ] What if SCENARIO_INDEX.md is missing? (Skill reports error, directs to TASK-PROC-010-12)
- [ ] What if scenario already exists in index? (Update existing entry, don't duplicate)
- [ ] What if gold_status changes multiple times? (Each change updates index)

#### Step 3.2: Manual Testing Scenarios

**Test 1: Create new scenario with category**
1. Invoke `create-scenario` skill
2. Select category: `capture.routine`
3. Designate as gold: No
4. Verify: scenario.md has `category: "capture.routine"` and `gold_status: false`
5. Verify: SCENARIO_INDEX.md instances array updated

**Test 2: Create gold standard scenario**
1. Invoke `create-scenario` skill
2. Select category: `management.archive_and_retrieve`
3. Designate as gold: Yes
4. Verify: scenario.md has `gold_status: true`
5. Verify: SCENARIO_INDEX.md shows `gold_status: true`

**Test 3: Modify scenario gold status**
1. Invoke `modify-user-needs` skill
2. Change existing scenario's `gold_status` from `false` to `true`
3. Verify: SCENARIO_INDEX.md instance updated to `gold_status: true`

**Test 4: Backward compatibility**
1. Read existing scenario without `category` field (pre-TASK-PROC-010-11)
2. Verify: Skills don't crash
3. Verify: Skills suggest adding category if missing

---

## WHY Comments Requirements

### Non-Obvious Design Decisions

All changes are relatively straightforward except:

1. **YAML Parsing Strategy** (create-scenario, Step 6.5):
   ```markdown
   /// Why: String-based YAML manipulation preserves comments and formatting.
   ///      YAML libraries would strip comments from SCENARIO_INDEX.md, losing
   ///      important documentation context.
   /// Source: requirements_tasks/.../2026-02-07_01_high_level_plan.md#phase-1.1
   /// Alternative: Could use YAML library + manual comment re-insertion, but
   ///              increases complexity for simple append operation.
   ```

2. **Gold Workflow Timing** (create-scenario, Step 2.5):
   ```markdown
   /// Why: Ask gold designation BEFORE creating scenario.md to prevent forgotten
   ///      designation. Retroactive gold marking requires modify-user-needs skill.
   /// Source: requirements_tasks/.../2026-02-07_01_high_level_plan.md#phase-1.1
   /// Alternative: Could prompt after creation, but user might forget or skip.
   ```

3. **Index Update After Scenario Creation** (create-scenario, Step 6.5):
   ```markdown
   /// Why: Create scenario.md first, then update index. If index update fails,
   ///      scenario still exists and can be manually added to index later.
   /// Source: requirements_tasks/.../2026-02-07_01_high_level_plan.md#phase-1.1
   /// Alternative: Could update index first, but then failure leaves orphaned
   ///              index entry with no scenario file.
   ```

All other changes are self-explanatory (simple YAML field additions, documentation updates).

---

## Testing Strategy

### Unit-Level Testing (Manual Verification)

**No automated tests needed** - this is documentation/skill work, not Flutter code.

**Manual verification**:
1. Create scenario with each category (10 categories)
2. Verify SCENARIO_INDEX.md correctly updated
3. Modify gold_status via modify-user-needs
4. Verify index updated
5. Check YAML formatting preserved

### Integration Testing

**Test bidirectional consistency**:
1. Create scenario with category
2. Verify index references scenario
3. Modify scenario category
4. Verify index updated
5. Check for orphaned references

### Acceptance Testing

User reviews:
1. Create-scenario skill workflow feels natural
2. Category selection is clear
3. Gold workflow prompts are understandable
4. README additions are helpful, not bloated
5. Existing scenarios still work (backward compatibility)

---

## Risks & Mitigations

### Risk 1: YAML Parsing Breaks Formatting

**Impact**: Medium - Index becomes hard to read or edit manually
**Probability**: Low - Simple append operation, tested structure
**Mitigation**:
- Test on copy of SCENARIO_INDEX.md first
- Validate YAML after write (parse back to verify structure)
- Keep backup of index before modifications

### Risk 2: Skills Become Too Complex

**Impact**: Medium - Hard to maintain, user confusion
**Probability**: Low - Changes are isolated to specific steps
**Mitigation**:
- Keep category workflow optional (can skip if needed)
- Provide clear error messages
- Document each step thoroughly

### Risk 3: Backward Compatibility Issues

**Impact**: High - Existing scenarios break
**Probability**: Very Low - Fields are additive, not replacing
**Mitigation**:
- Skills check for field existence before reading
- Provide defaults for missing fields
- Test with pre-TASK-PROC-010-11 scenarios

### Risk 4: README Token Bloat

**Impact**: Low - Longer context, higher costs
**Probability**: Very Low - Additions are minimal (<250 tokens total)
**Mitigation**:
- Keep README additions to 2-3 sentences + link
- Reference SCENARIO_INDEX.md for details, don't duplicate

### Risk 5: Index Sync Gets Out of Sync

**Impact**: Medium - Index doesn't reflect reality
**Probability**: Low - Bidirectional updates maintained
**Mitigation**:
- Skills always update both scenario and index
- Validation checks for orphaned references
- Manual audit script (future enhancement)

---

## Success Criteria

### Functional Requirements

- [x] create-scenario skill reads SCENARIO_INDEX.md
- [x] create-scenario skill prompts for category selection
- [x] create-scenario skill validates category exists
- [x] create-scenario skill suggests canonical folder name
- [x] create-scenario skill adds category and gold_status to YAML
- [x] create-scenario skill updates index instances array
- [x] create-scenario skill implements gold workflow prompts
- [x] modify-user-needs skill updates index on gold_status change
- [x] modify-user-needs skill updates index on scenario metadata change

### Documentation Requirements

- [x] README_4 has category system introduction
- [x] README_4 has gold workflow explanation
- [x] README_7 documents category field
- [x] README_7 documents gold_status field
- [x] README additions are minimal (<250 tokens total)

### Quality Requirements

- [x] No breaking changes to existing skill functionality
- [x] YAML formatting preserved in SCENARIO_INDEX.md
- [x] Backward compatibility with scenarios lacking new fields
- [x] Clear error messages for validation failures
- [x] All acceptance criteria from goal.md met

---

## Execution Sequence

### Single Agent Execution (Recommended)

**Agent**: `implementation-engineer`

**Rationale**: All changes are in documentation/skill files (no Flutter code). Single agent maintains consistency and reduces coordination overhead.

**Execution Steps**:
1. Read this plan + goal.md + SCENARIO_INDEX.md
2. Modify `.claude/skills/create-scenario/skill.md` (Phase 1.1)
3. Modify `.claude/skills/modify-user-needs/skill.md` (Phase 1.2)
4. Update `README_4_SCENARIO_DEFINITION.md` (Phase 2.1)
5. Update `README_7_META_INFO_STANDARDS.md` (Phase 2.2)
6. Run validation checklist (Phase 3.1)
7. Perform manual testing (Phase 3.2)
8. Log protocol with agent ID

**Alternative**: Two-agent execution (if skill modifications prove complex):
- Agent 1: Skill modifications (Phase 1)
- Agent 2: Documentation updates + validation (Phase 2-3)

---

## Dependencies

### Completed Dependencies

| Task | Status | Notes |
|------|--------|-------|
| TASK-PROC-010-12 | ✅ Complete | SCENARIO_INDEX.md created and populated |
| TASK-PROC-010-11 | ✅ Complete | Existing scenarios have category/gold_status fields |

### Blocks

| Task | Dependency | Why |
|------|------------|-----|
| TASK-PROC-010-10 | This task | Batch generation needs category system + gold tracking |

---

## Estimated Effort

**Total effort**: **M (Medium)** - as specified in goal.md

**Breakdown**:
- create-scenario skill modification: 2-3 hours (primary complexity)
- modify-user-needs skill modification: 1 hour (simpler, duplicated logic)
- README updates: 30 minutes (minimal additions)
- Testing & validation: 1-2 hours (manual testing scenarios)
- Documentation & protocol: 30 minutes

**Total**: 5-7 hours of focused work

---

## Appendix: File Modification Summary

### .claude/skills/create-scenario/skill.md

**Lines to modify**: ~35, 78, 114, insert new Step 2.5, insert new Step 6.5
**Lines added**: ~80
**Breaking changes**: None
**Backward compatibility**: Yes (category optional, defaults provided)

### .claude/skills/modify-user-needs/skill.md

**Lines to modify**: 179 (Opus Mode), 354 (Standard Mode)
**Lines added**: ~30
**Breaking changes**: None
**Backward compatibility**: Yes (checks field existence before update)

### requirements_user_needs/README_4_SCENARIO_DEFINITION.md

**Lines to modify**: Insert before line 145
**Lines added**: ~10 (150 tokens)
**Breaking changes**: None
**Backward compatibility**: N/A (documentation only)

### requirements_user_needs/README_7_META_INFO_STANDARDS.md

**Lines to modify**: Insert after line 45 (example), insert after line 60 (field docs)
**Lines added**: ~8 (100 tokens)
**Breaking changes**: None
**Backward compatibility**: N/A (documentation only)

---

## Approval Required

**User**: Please review this plan and approve before implementation begins.

**Questions for clarification**:
1. Should the gold standard prompt be mandatory or optional (current plan: optional)?
2. Should validation prevent creating scenarios without category selection (current plan: yes, enforce category selection)?
3. Should the skill auto-suggest category based on scenario goal keywords (current plan: no, user selects manually)?

**Next steps after approval**:
1. Spawn `implementation-engineer` agent with this plan
2. Agent implements all 4 file modifications
3. Agent runs validation checklist
4. Agent logs protocol with completion status

---

**Plan Status**: ⏸️ Awaiting User Approval
**Agent ID**: architecture-advisor-2026-02-07-001
