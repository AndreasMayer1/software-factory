# Requirements Migration Plan

**Date**: 2026-01-09
**Task**: TASK-PROC-009-02
**Agent**: Factory Orchestrator

## Objective

Migrate all 37 requirements.md files to include standardized YAML frontmatter with IDs, priority scores, status values, and trackable_items.

## Prerequisites (Completed)

- ✅ ID registry created (`requirements_tasks/_meta/id_registry.md`)
- ✅ Validation script available (`scripts/validate_meta.py`)
- ✅ Meta-migrator agent created (`.claude/agents/meta-migrator.md`)

## Migration Strategy

### Batch Processing Approach

Process files in three batches by category for efficient workflow:

#### Batch 1: Process Requirements (9 files)
- **Status**: Most are `implemented` (already in use)
- **Complexity**: Low - mainly bookkeeping metadata
- **IDs**: REQ-PROC-001 to REQ-PROC-009

#### Batch 2: Non-Functional Requirements (14 files)
- **Status**: Mix of `defined` and `in_progress`
- **Complexity**: Medium - design system components
- **IDs**: REQ-NFUNC-001 to REQ-NFUNC-014

#### Batch 3: Functional Requirements (14 files)
- **Status**: Varies based on task presence
- **Complexity**: High - may have 8+ acceptance criteria
- **IDs**: REQ-FUNC-001 to REQ-FUNC-014

### Escalation Strategy

Meta-migrator uses Haiku by default but escalates to Sonnet when:
- Files with 8+ acceptance criteria
- Complex dependency chains
- Unclear priority assignment
- Validation errors encountered
- Non-standard content structure

### Validation Checkpoints

After each batch:
1. Run `python scripts/validate_meta.py --verbose`
2. Fix any errors before proceeding
3. Commit changes with descriptive message

## Implementation Plan

### Phase 1: Process Requirements
**Files**: 9
**Expected Duration**: Quick (most are simple metadata)
**Agent**: meta-migrator (Haiku)

**Action**: Spawn meta-migrator agent with:
- Task: Migrate all requirements.md files in `requirements_tasks/process/`
- Model: Haiku
- Instructions: Process requirements are `implemented`, use priority codes U5-PROC, I5-ENAB

### Phase 2: Non-Functional Requirements
**Files**: 14
**Expected Duration**: Medium
**Agent**: meta-migrator (Haiku → Sonnet if needed)

**Action**: Spawn meta-migrator agent with:
- Task: Migrate all requirements.md files in `requirements_tasks/non-functional/`
- Model: Haiku (escalate if complex)
- Instructions: Design system components, assess status based on tasks

### Phase 3: Functional Requirements
**Files**: 14
**Expected Duration**: Longer (complex features)
**Agent**: meta-migrator (likely Sonnet for some)

**Action**: Spawn meta-migrator agent with:
- Task: Migrate all requirements.md files in `requirements_tasks/functional/`
- Model: Haiku (escalate for 8+ AC)
- Instructions: Feature requirements, check task folders for status

### Phase 4: Final Validation
**Action**: Run comprehensive validation
- Validate all 37 files
- Check ID uniqueness
- Verify covers references
- Generate coverage report (should show 0% initially as tasks not migrated yet)

## Expected Outcomes

After completion:
- ✅ All 37 requirements.md have valid YAML frontmatter
- ✅ All IDs match the registry
- ✅ All files have trackable_items (AC or sections)
- ✅ Validation passes on all files
- ✅ No duplicate IDs
- ✅ Coverage report shows 0% (correct - tasks migration is Task 3)

## Rollback Plan

If issues occur:
1. Git has all changes tracked
2. Can revert individual files: `git checkout <file>`
3. Validation script catches issues early
4. Batch approach limits blast radius

## Notes

- Total files: 37
- Tools ready: ✅
- Agent ready: ✅
- Ready to proceed: ✅
