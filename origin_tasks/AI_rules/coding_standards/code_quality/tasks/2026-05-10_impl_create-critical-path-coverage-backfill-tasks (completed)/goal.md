---
task_id: TASK-PROC-046-09
type: impl
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-PROC
status: completed
effort: S
created: 2026-05-10
started: 2026-05-19
completed: 2026-05-19
session_completed_at: 2026-05-19T02:17:34Z
after: [TASK-PROC-046-04]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-04]
  sections: []
scope_description: "Read the baseline coverage report produced by TASK-PROC-046-04 and use the task-create skill to schedule one impl task per critical-path category whose coverage is below 90 %, each scoped to add tests bringing coverage to threshold."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: ddfafcd0-b1e9-4375-b7d4-e87832d2371e
session_account: web
---
# Goal: Create critical-path coverage backfill tasks

## Objective

TASK-PROC-046-04 produces a baseline coverage report for the safety-critical paths. Categories below the 90 % threshold need additional tests. This task converts the gap list into scheduled work: one impl task per category (or per file within a category if granularity helps), each created via `task-create` so the work appears in the queue.

## Requirements Summary

REQ-PROC-046 AC-04 (≥ 90 % line coverage on encryption / decryption, Argon2id key derivation, atomic file rotation, version migration, data-transfer serialization). The baseline coverage report (TASK-PROC-046-04 output) is the input.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Read TASK-PROC-046-04's baseline coverage record from its `plans_and_protocols/`.
- For each critical-path category whose coverage is below 90 %:
  - Quantify the gap (lines uncovered, specific functions/methods uncovered).
  - Decide granularity: one task per category if the gap is small, one task per file or per function if the category is large.
  - Invoke `task-create` skill to allocate IDs under the appropriate parent (likely REQ-FUNC-006 for encryption/key derivation, REQ-FUNC-015 for atomic rotation, REQ-FUNC-007 for transfer, etc.) with type `impl`.
  - Each created task's scope: "Bring coverage of [path] to ≥ 90 % by adding tests for [list of uncovered functions]."
  - Set `after:` to `[TASK-PROC-046-04]` and any analyzer-config dependency.
- Record the list of created task IDs in `plans_and_protocols/created_tasks.md`.
- If TASK-PROC-046-04 baseline already meets ≥ 90 % on every category: this task is a no-op. Record that fact and complete.

### Out of Scope

- Writing the tests themselves. Each created task does that.
- Lowering the threshold from 90 %. The threshold is set by REQ-PROC-046 AC-04; changing it requires a requirement update, not a backfill task.
- Mutation testing on these paths — that's REQ-PROC-002 AC-02, scheduled separately (TASK-PROC-002-06 handles surviving-mutant remediation).

## Acceptance Criteria

- [x] Every critical-path category below 90 % coverage has a corresponding scheduled task. (Vacuously satisfied — no category below 90 %.)
- [x] `plans_and_protocols/created_tasks.md` lists every created task ID with a one-line description and pointer to its goal.md. (File written with zero-task rationale.)
- [x] Each created task names the specific uncovered functions / methods to address (not a vague "improve coverage"). (Vacuously satisfied — zero tasks created.)
- [x] If baseline already met threshold, that is recorded explicitly. (See `plans_and_protocols/2026-05-19_01_protocol_no-op-baseline-passes.md`.)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-04 | pending | Provides the baseline this task acts on |

## Notes

Coverage gaps on safety-critical paths often indicate untested error branches (corruption, IV reuse, decryption failure). When creating the backfill tasks, surface this — the goal is not just "more covered lines" but "tests that exercise the failure modes that would otherwise produce silent data loss."

After backfill tasks complete, mutation testing (REQ-PROC-002 AC-02) will likely reveal whether the new tests are *strong* (kill rate ≥ 80 %) or merely *covering* (lines hit, but assertions weak). That feedback loop is intentional.
