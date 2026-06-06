# High-Level Implementation Plan: Goal.md (Tasks) Migration
**Agent**: architecture-advisor
**Agent ID**: claude-sonnet-4-5-20250929
**Date**: 2026-01-10
**Task**: TASK-PROC-009-03

## Executive Summary

This plan outlines the strategy for migrating all 49 goal.md files to include standardized YAML frontmatter with unique task IDs, priority scores, status values, and covers field linking to parent requirement trackable_items.

**Complexity**: HIGH (meta-migration affecting 49 files)
**Risk Level**: MEDIUM (validation tooling exists, but manual review required)
**Recommended Approach**: Incremental migration by requirement, using meta-migrator agent

---

## 1. Scope Analysis

### Files to Migrate
- **Total**: 49 goal.md files across the project
- **Already Migrated**: 4 files (TASK-PROC-009-01 through TASK-PROC-009-04 have proper frontmatter)
- **Remaining**: 45 files need migration
- **Partially Migrated**: ~27 files have git versioning metadata but no YAML frontmatter

### Current State of goal.md Files

Based on analysis, goal.md files fall into 3 categories:

1. **Fully Migrated (4 files)**:
   - Have complete YAML frontmatter with task_id, covers, etc.
   - Example: `2026-01-09_impl_meta_info_task_migration/goal.md`

2. **Partially Migrated (~27 files)**:
   - Have git versioning metadata block (3 dashes, requirements source)
   - NO proper YAML frontmatter
   - Example: `2026-01-04_impl_phase1-domain-data/goal.md`

3. **Unmigrated (~18 files)**:
   - No metadata at all
   - Plain markdown content only

### Task Distribution by Parent Requirement

Based on ID registry and file paths:
- **REQ-PROC-001**: 1 task (context window)
- **REQ-PROC-002**: 1 task (testing standards)
- **REQ-PROC-003**: 1 task (writer mode)
- **REQ-PROC-004**: 1 task (brainstorming)
- **REQ-PROC-005**: ~12 tasks (testing workflow pilots)
- **REQ-PROC-006**: 1 task (workflow improvement)
- **REQ-PROC-007**: 1 task (guideline updates)
- **REQ-PROC-008**: 3 tasks (orchestrator workflow)
- **REQ-PROC-009**: 5 tasks (requirements structure) - partially done
- **REQ-NFUNC-010**: 1 task (in-detail navigation)
- **REQ-NFUNC-011**: 1 task (main navigation)
- **REQ-NFUNC-014**: ~10 tasks (responsive layout)
- **REQ-FUNC-005**: 5 tasks (plan evaluation view)
- **REQ-FUNC-014**: 1 task (therapist plan management)

---

## 2. Migration Strategy

### Approach: Incremental by Requirement

**Rationale**: Processing all tasks for one requirement together allows:
- Loading parent requirement's trackable_items once
- Determining logical task numbering (TASK-XXX-01, -02, etc.)
- Validating covers references immediately
- Cleaner protocol logging

### Batch Processing Order

Process in this order (easiest → hardest):

1. **PROC Requirements** (high confidence, mostly completed tasks)
   - REQ-PROC-001 through REQ-PROC-009
   - ~27 tasks total
   - Most have clear status (completed/in_progress)

2. **NFUNC Requirements** (navigation tasks, well-documented)
   - REQ-NFUNC-010, REQ-NFUNC-011, REQ-NFUNC-014
   - ~12 tasks total
   - Clear folder structure indicates status

3. **FUNC Requirements** (feature tasks, may need judgment)
   - REQ-FUNC-005, REQ-FUNC-014
   - ~6 tasks total
   - May need clarification on covers mapping

### Use of meta-migrator Agent

**YES** - Use the meta-migrator agent created in TASK-PROC-009-01.

**Model Selection**:
- **Haiku (default)**: For straightforward tasks with clear scope
- **Sonnet (escalate)**: When encountering:
  - Unclear covers mapping (can't determine which AC/SEC the task addresses)
  - Complex validation errors
  - Ambiguous status determination
  - Priority justification unclear

**Workflow per Requirement**:
1. Main orchestrator identifies next requirement to process
2. Spawn meta-migrator with:
   - Parent requirement path
   - List of all task folders for that requirement
3. Meta-migrator reads parent's trackable_items
4. For each task:
   - Read existing goal.md
   - Determine task number (sequential within requirement)
   - Map task scope to covers (AC/SEC IDs)
   - Generate frontmatter
   - Validate
5. Meta-migrator reports back any escalation needs
6. Review and approve
7. Run validation script
8. Move to next requirement

---

## 3. Task ID Generation Strategy

### Format
```
TASK-[CATEGORY]-[REQ_NUM]-[TASK_NUM]
```

Example: `TASK-PROC-005-01`, `TASK-FUNC-005-03`

### Sequential Numbering Rules

1. **Within Each Requirement**: Tasks numbered 01, 02, 03, etc.
2. **Chronological Order**: Based on folder date prefix
3. **Completed vs Active**: No distinction in numbering (chronological wins)
4. **Superseded Tasks**: Still get IDs (marked as cancelled)

### Handling Existing IDs

The 4 tasks that already have IDs (TASK-PROC-009-01 through -04) should:
- **Keep their existing IDs** (immutability principle)
- Be used as reference for numbering subsequent tasks in REQ-PROC-009
- Next task in REQ-PROC-009 would be TASK-PROC-009-05

### Sub-Task Numbering

For nested tasks (like `2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot_2/`):
- **Option A**: Use extended format `TASK-PROC-005-01-01` (sub-task)
- **Option B**: Treat as separate tasks `TASK-PROC-005-11, -12, etc.`

**RECOMMENDATION**: Option B (separate tasks)
- Validation script supports both formats
- Simpler to track
- Sub-tasks are still full tasks with own goals

---

## 4. Status Mapping Strategy

### Determine Status Based On

1. **Folder Name Pattern**:
   - Ends with `_(completed)` → `status: completed`
   - Ends with `_(superseded)` → `status: cancelled`
   - No suffix → check next factors

2. **Protocol Files**:
   - Recent protocol files (within 7 days) → `status: in_progress`
   - Old protocol (30+ days) → review manually

3. **Goal Content**:
   - Contains "COMPLETED" or similar markers → `status: completed`
   - Contains blockers/issues → `status: blocked`

4. **Default**:
   - If unclear → `status: pending` (conservative choice)

### Status Value Options
- `pending`: Not started, waiting
- `ready`: Ready to start (dependencies met)
- `in_progress`: Currently being worked on
- `blocked`: Cannot proceed (dependency/issue)
- `review`: Implementation done, awaiting review
- `completed`: Fully done
- `cancelled`: Superseded or abandoned

### Completed Date

For `status: completed` tasks:
- **Extract from**: Folder date if marked as completed
- **Extract from**: Last protocol file date
- **Extract from**: Git commit date of folder (if available)
- **Default**: Leave blank if uncertain

---

## 5. Priority Inheritance Strategy

### Default: Inherit from Parent Requirement

Most tasks should inherit urgency/impact from their parent requirement:

```yaml
parent_requirement: REQ-PROC-005
urgency: 4              # Same as parent
urgency_reason: U4-DEP  # Same as parent
impact: 5               # Same as parent
impact_reason: I5-ENAB  # Same as parent
```

### Override Only When Justified

Override parent priority when:
- **Task is exploratory** (lower urgency/impact)
- **Task is critical blocker** for parent (higher urgency)
- **Task addresses specific sub-goal** with different priority

When overriding, add comment in frontmatter:
```yaml
urgency: 3              # Lower than parent (exploration only)
urgency_reason: U3-SPRINT
# Override rationale: Exploratory task, not blocking implementation
```

---

## 6. covers Field Mapping Strategy

### The Challenge

This is the HARDEST part of migration. For each task, we must determine:
- Which acceptance criteria (AC-XX) does it implement?
- Which sections (SEC-XX) does it address?

### Mapping Process

1. **Read Parent Requirement**:
   - Load trackable_items from parent requirements.md
   - List all available AC-XX and SEC-XX IDs

2. **Analyze Task Goal**:
   - Read goal.md content
   - Identify keywords, scope statements
   - Look for explicit references to AC/sections

3. **Determine Coverage**:
   - **Full Implementation**: Lists specific ACs implemented
   - **Partial Implementation**: Lists ACs partially addressed
   - **Section-Based**: If no specific ACs, reference sections (SEC-XX)
   - **Exploratory Tasks**: May have empty covers (no AC implemented)

### Example Mappings

**Implementation Task (specific AC)**:
```yaml
covers:
  acceptance_criteria: [AC-01, AC-02]
  sections: []
scope_description: "Implement data interface and shortLabel field"
```

**Exploratory Task (section-based)**:
```yaml
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-03]
scope_description: "Explore and document current implementation patterns"
```

**Foundation Task (broad)**:
```yaml
covers:
  acceptance_criteria: []
  sections: [SEC-12, SEC-11]
scope_description: "Create validation scripts and ID registry"
```

### Escalation Triggers

If meta-migrator cannot determine covers:
- Goal content is vague
- Multiple possible AC matches
- Task seems out of scope for parent requirement
→ **ESCALATE to Sonnet** or **ASK USER**

---

## 7. Requirements Version Linking

### Git Commit Hash

Every task must reference the requirements version at task creation:

```yaml
requirements_version:
  commit: 1d3a2f9
  file: ../requirements.md
```

### Determining Commit Hash

For existing tasks:
1. **Check existing metadata**: Some tasks already have this (from previous migration)
2. **Use folder date**: Find commit closest to task folder date
3. **Use pre-migration commit**: Fallback to `1d3a2f9` (the pre-git-migration snapshot)

### For New Tasks (Going Forward)

New tasks created after this migration:
- Use current HEAD commit hash
- Documented in setup-task skill

---

## 8. Validation Strategy

### Validation Points

1. **After Each File**: Run validation on single file
2. **After Each Requirement**: Run validation on all files in that requirement
3. **After Full Migration**: Final validation pass

### Validation Script

Use existing `scripts/validate_meta.py`:

```bash
python scripts/validate_meta.py --verbose
```

### Validation Checks

The script validates:
- ✓ YAML frontmatter structure
- ✓ task_id format (TASK-XXX-XXX-XX)
- ✓ Unique task_id (no duplicates)
- ✓ parent_requirement exists
- ✓ covers references point to existing trackable_items
- ✓ Required fields present

### Error Handling

When validation fails:
1. Meta-migrator reports error
2. Fix immediately before proceeding
3. Re-run validation
4. If complex → escalate to Sonnet
5. If unclear → ask user

---

## 9. Scope Boundaries

### IN SCOPE

- ✓ Adding YAML frontmatter to all 49 goal.md files
- ✓ Generating unique task_ids
- ✓ Mapping covers to parent trackable_items
- ✓ Setting appropriate status values
- ✓ Setting priority (inherited or justified override)
- ✓ Running validation after each batch
- ✓ Documenting mapping decisions in protocol

### OUT OF SCOPE

- ✗ Modifying task content (only add frontmatter)
- ✗ Creating new tasks
- ✗ Changing requirements.md files (already done in TASK-PROC-009-02)
- ✗ Updating parent requirement metadata
- ✗ Removing meta-migrator agent (done after completion)

---

## 10. File Change Analysis

### Maximum Files per Session

**RECOMMENDATION**: Process 5-7 tasks per session
- Each task = 1 file (goal.md)
- Allows focused review
- Prevents overwhelming context

### Should We Split This Task?

**ANALYSIS**:
- 49 files is large
- But each file is small (add frontmatter only)
- Meta-migrator agent handles heavy lifting
- Main task = coordination and review

**DECISION**: **NO SPLIT NEEDED**, but use incremental approach:
- Process by requirement (natural batches)
- Commit after each requirement
- Protocol after each batch
- Can pause/resume between requirements

### Files Modified

For each task:
- `requirements_tasks/.../goal.md` (add frontmatter)

No other files changed in this task.

---

## 11. WHY Comments Requirements

### Do We Need WHY Comments?

**ANALYSIS**: This is a meta-migration task (documentation, not code)

**WHY Comments NOT NEEDED** because:
- No code files modified
- YAML frontmatter is self-documenting
- Validation script enforces structure
- Protocol files explain mapping decisions

**EXCEPTION**: If we modify validation script or create helper scripts:
- Add WHY comments for non-obvious logic
- Explain priority assignment heuristics
- Document covers mapping algorithms

---

## 12. Testing Strategy

### Validation Testing

1. **Unit Validation**: After each file
   ```bash
   python scripts/validate_meta.py --verbose
   ```

2. **Batch Validation**: After each requirement
   - Confirm all tasks in that requirement pass
   - Check coverage report

3. **Final Validation**: After full migration
   - All 49 files pass
   - No errors
   - Only warnings for non-critical issues

### Coverage Report Testing

After migration, run coverage report:
```bash
python scripts/coverage_report.py
```

Expected output:
- Shows which AC/SEC are covered by tasks
- Identifies uncovered requirements
- Validates covers references

### Manual Review

For each batch:
- Review generated frontmatter
- Verify task_id sequential numbering
- Check covers mapping makes sense
- Confirm status matches folder state

---

## 13. Risk Analysis

### High Risks

1. **Incorrect covers Mapping**
   - **Impact**: Tasks linked to wrong AC/SEC
   - **Mitigation**: Manual review, user confirmation for unclear cases
   - **Recovery**: Easy to fix (just edit YAML)

2. **Duplicate task_id**
   - **Impact**: Validation failure
   - **Mitigation**: Careful sequential numbering, validation after each file
   - **Recovery**: Renumber conflicting IDs

3. **Lost Context**
   - **Impact**: Cannot determine what task was for
   - **Mitigation**: Read full goal.md content, check folder name
   - **Recovery**: Ask user if still unclear

### Medium Risks

1. **Status Misclassification**
   - **Impact**: Task marked completed but actually pending
   - **Mitigation**: Conservative defaults (prefer pending over completed)
   - **Recovery**: Easy to fix later

2. **Priority Mismatch**
   - **Impact**: Task has wrong urgency/impact
   - **Mitigation**: Inherit from parent by default
   - **Recovery**: Easy to adjust

### Low Risks

1. **Validation Script Bugs**
   - **Impact**: False positives/negatives
   - **Mitigation**: Script tested in TASK-PROC-009-01
   - **Recovery**: Fix script, re-validate

---

## 14. Execution Workflow

### Phase 1: Preparation
1. Review this plan with user
2. Get approval to proceed
3. Ensure validation script works
4. Test meta-migrator on 1-2 files

### Phase 2: Migration (Per Requirement)

For each requirement in processing order:

1. **Setup**:
   - Load requirement requirements.md
   - Extract trackable_items
   - List all task folders

2. **Spawn meta-migrator**:
   - Provide parent requirement path
   - Provide task folder list
   - Set model (Haiku default)

3. **Meta-migrator Actions**:
   - Read each goal.md
   - Generate task_id (sequential)
   - Determine covers (AC/SEC mapping)
   - Set status based on folder
   - Inherit priority from parent
   - Generate YAML frontmatter
   - Add to goal.md
   - Validate

4. **Review**:
   - Check generated frontmatter
   - Verify covers make sense
   - Approve or request changes

5. **Validate**:
   - Run validation script
   - Fix any errors
   - Re-validate until clean

6. **Protocol**:
   - Log which tasks migrated
   - Note any escalations
   - Document decisions

7. **Commit** (optional, per requirement):
   - Clean atomic commit
   - Reference TASK-PROC-009-03

### Phase 3: Final Validation
1. Run validation on all 49 files
2. Generate coverage report
3. Review for completeness
4. Document final statistics

### Phase 4: Cleanup
1. Update protocol with final stats
2. Mark task as completed
3. **DO NOT remove meta-migrator yet** (goal.md says to remove after validation)

---

## 15. Success Criteria

All acceptance criteria from goal.md:

- [ ] All 49 goal.md have valid YAML frontmatter
- [ ] All task_ids follow correct format (TASK-[REQ-ID]-[NN])
- [ ] All `covers` references point to existing trackable_items
- [ ] Validation script passes on all files
- [ ] Coverage report correctly shows coverage percentages
- [ ] Completed tasks have `completed` status and date
- [ ] **meta-migrator agent removed** (cleanup after migration complete)

Additional success criteria:
- [ ] No duplicate task_ids
- [ ] Sequential numbering within each requirement
- [ ] Status values match folder state
- [ ] Priority inheritance documented
- [ ] Protocol documents all mapping decisions

---

## 16. Estimated Effort

### Time per Task File

Based on goal.md estimate (~10 minutes per file):
- Simple task (clear scope): 5-7 minutes
- Complex task (unclear covers): 10-15 minutes
- Average: ~10 minutes

### Total Time

- 45 remaining tasks × 10 min = **~450 minutes = 7.5 hours**
- With meta-migrator automation: **~3-4 hours** (review + fixes)

### Breakdown by Phase

- Preparation: 30 minutes
- PROC requirements migration: 2 hours
- NFUNC requirements migration: 1 hour
- FUNC requirements migration: 0.5 hour
- Final validation: 30 minutes
- Cleanup and documentation: 30 minutes

**Total**: ~4.5 hours (with automation)

---

## 17. Dependencies

### Upstream Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-009-01 | ✓ Completed | ID registry, validation script |
| TASK-PROC-009-02 | ✓ Completed | Requirements have trackable_items |
| meta-migrator agent | ✓ Available | Created in TASK-PROC-009-01 |

All dependencies MET. Ready to proceed.

### Downstream Dependencies

| Blocked Task | Depends On | Impact |
|--------------|------------|--------|
| Coverage reporting | This task | Cannot show task coverage without frontmatter |
| Task lifecycle management | This task | Cannot track task status/progress |
| Future task creation | This task | Template needs to follow same format |

---

## 18. Alternatives Considered

### Alternative 1: Manual Migration
**Rejected**: Too error-prone, 49 files × 10 min = 8+ hours

### Alternative 2: Fully Automated Script
**Rejected**: Covers mapping requires judgment, cannot be fully automated

### Alternative 3: Split into Multiple Tasks
**Rejected**: Overhead of task management > benefit of splitting

### Alternative 4: Process All Files at Once (No Batching)
**Rejected**: Too many files to review at once, high error risk

**CHOSEN APPROACH**: Incremental migration by requirement, using meta-migrator agent with human review

---

## 19. Next Steps (After Approval)

1. **User Reviews This Plan**
2. **User Approves** (or requests changes)
3. **Spawn implementation-engineer Agent**
   - Provide this plan
   - Provide goal.md
   - Execute Phase 1 (Preparation)
4. **Begin Migration**
   - Start with REQ-PROC-001
   - Follow workflow in Section 14

---

## 20. Open Questions for User

Before proceeding, clarify:

1. **Sub-Task Numbering**: Confirm using separate task IDs (Option B) for nested tasks?
2. **Commit Strategy**: Commit after each requirement, or one final commit?
3. **Escalation Threshold**: When should meta-migrator ask user vs. make best guess?
4. **Status Conservative**: Prefer `pending` or `completed` when uncertain?
5. **Priority Overrides**: Allow meta-migrator to override parent priority, or always ask?

---

## Appendix A: Meta-Migrator Capabilities

From `.claude/agents/meta-migrator.md`:

**Strengths**:
- YAML frontmatter generation
- ID registry lookup
- Validation script integration
- Priority assignment guidelines
- Model: Haiku (fast, efficient)

**Escalation Triggers** (switches to Sonnet or asks user):
- 8+ acceptance criteria
- Complex dependency chains
- Validation errors
- Unclear priority assignment
- Ambiguous trackable_items extraction

**Lifecycle**: Temporary agent, remove after TASK-PROC-009-03 completion

---

## Appendix B: Example Frontmatter Template

For reference, the target frontmatter format:

```yaml
---
task_id: TASK-PROC-005-01
type: impl
parent_requirement: REQ-PROC-005
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2025-10-20
completed: 2025-11-03
depends_on: []
blocked_by: []
covers:
  acceptance_criteria: [AC-01, AC-03]
  sections: []
scope_description: "Implement enhanced testing workflow pilot"
requirements_version:
  commit: 1d3a2f9
  file: ../requirements.md
---
```

---

**END OF PLAN**

**Status**: Ready for user review
**Next Action**: Wait for user approval, then spawn implementation-engineer
