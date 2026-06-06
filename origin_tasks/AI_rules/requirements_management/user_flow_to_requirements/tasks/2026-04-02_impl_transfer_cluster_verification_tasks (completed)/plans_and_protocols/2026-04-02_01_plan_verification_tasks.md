# Plan: Create Transfer Cluster Verification Tasks

**Task**: TASK-PROC-030-05
**Date**: 2026-04-02
**Status**: COMPLETED

---

## Key Decisions

### target_package Not Used for Bundle Grouping
Most exploration tasks don't have `target_package` (assigned by `release-plan`, which runs only after all requirements exist). Phase 4.5 had a bug referencing `target_package` — fixed as part of this task to use the matrix "Suggested Package" column instead.

### Max 6 Verification Tasks with Equal Distribution
11 raw bundles from the matrix were merged into 6 verification tasks using:
- Sort by pending task count (ascending), then urgency (descending), then lowest gap# for ties
- Divide sorted list into 6 consecutive equal-sized groups
- This ensures early checkpoints run when fast bundles complete; later checkpoints when slow bundles complete

---

## Final Bundle Groups → 6 Verification Tasks

| V# | Task ID | Bundles | Gaps | Foundations | Unblocks when... |
|----|---------|---------|------|-------------|-----------------|
| V1 | TASK-FUNC-007-13 | Phase 2 Edge Cases + Remote Sessions | #6, #12 | — | Immediately (all done) |
| V2 | TASK-FUNC-007-14 | Core Protocol Delivery + Notification System | #1–#5, #7, #16 | F1, F2 | After #1,#2,#5,#7 done |
| V3 | TASK-FUNC-007-15 | Edge Cases & Resilience + Scope & Privacy Controls | #9,#11,#13,#14 | F3 | After #9,#11,#14 done |
| V4 | TASK-FUNC-007-16 | Core QR Transfer + Core File Transfer | #8,#10,#15,#21 | — | After all 4 done |
| V5 | TASK-FUNC-007-17 | Audio Export + Scope Controls & Interrupted Transfer | #17,#18,#20 | — | After all 3 done |
| V6 | TASK-FUNC-007-18 | Print Path | #19 | — | After #19 done |

---

## Changes Made

1. **6 verification goal.md files created** in `requirements_tasks/functional/shared/epic_data_transfer/tasks/`
2. **Pipeline Status table updated** in `requirements_user_needs/user_flows/_clusters/flexible_data_transfer/requirements_matrix.md` — V1–V6 rows added with status "created"
3. **Phase 4.5 fixed** in `.claude/skills/requ-derive-from-flow/skill.md`:
   - Replaced `target_package` grouping with "Suggested Package column" grouping
   - Added max-6 cap with equal-distribution algorithm
   - Updated Gap→Requirement Mapping table to include a Bundle column
   - Updated `verification_bundle` frontmatter to YAML list (supports multiple bundles)
   - Updated Key Principle #12 to clarify verification bundling never uses `target_package`
