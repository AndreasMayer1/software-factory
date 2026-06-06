---
task_id: TASK-PROC-002-06
type: impl
parent_requirement: REQ-PROC-002
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: S
created: 2026-05-10
started: 2026-05-23
completed: 2026-05-23
session_completed_at: 2026-05-23T20:58:57Z
after: [TASK-PROC-002-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02]
  sections: []
scope_description: "Read the baseline mutation report produced by TASK-PROC-002-02 and use the task-create skill to schedule one impl task per surviving-mutant cluster on safety-critical paths, each scoped to strengthen the assertions that should have killed the mutant."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: 9eccf6e7-bd30-4b4a-a8b0-39a177877a6e
session_account: gmail2
---
# Goal: Create surviving-mutant remediation tasks

## Objective

TASK-PROC-002-02 produces a baseline mutation kill rate on the safety-critical paths and a list of surviving mutants. Surviving mutants signal weak tests: the test suite covers the line but does not detect a deliberate regression on it. This task converts surviving mutants into scheduled remediation work: one impl task per cluster of related mutants, each scoped to strengthen the relevant assertions until the cluster is killed (or, where genuinely benign, recorded as such in the surviving-mutant register).

## Requirements Summary

REQ-PROC-002 AC-02 (≥ 80 % mutation kill rate on safety-critical paths). The baseline report (TASK-PROC-002-02 output) is the input.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Read TASK-PROC-002-02's baseline output from its `plans_and_protocols/`.
- Cluster surviving mutants by file and category (e.g. all surviving boolean-literal mutations in `lib/core/data/encryption/`; all surviving comparison-operator mutations in `lib/core/data/migration/`).
- For each cluster (or single mutant if isolated):
  - Decide whether the mutant is genuinely benign (no observable behaviour change — e.g. logging, debug-only path). If so, record it in `doc/testing/surviving_mutants.md` with rationale; no remediation task needed.
  - If not benign: invoke `task-create` to allocate IDs under the owning feature requirement (REQ-FUNC-006 for encryption, REQ-FUNC-015 for storage, REQ-FUNC-007 for transfer), with type `impl`.
  - Each created task's scope: "Strengthen assertions in [test file] to kill surviving mutants in [source file] of category [boolean-literal / comparison / arithmetic / null-safety]."
  - Set `after:` to `[TASK-PROC-002-02]`.
- Record created task IDs in `plans_and_protocols/created_tasks.md`.
- If baseline kill rate is already ≥ 80 % across all critical paths and no clusters need remediation: no-op, record fact, complete.

### Out of Scope

- Strengthening the assertions. Each created task does that.
- Lowering the 80 % threshold. The threshold is set by REQ-PROC-002 AC-02.
- Coverage gap remediation — a different angle, owned by TASK-PROC-046-09.

## Acceptance Criteria

- [x] Every surviving-mutant cluster on a safety-critical path is classified as either remediation-needed or benign-with-rationale.
- [x] Benign mutants are recorded in `doc/testing/surviving_mutants.md` with explicit rationale.
- [x] Remediation-needed clusters have a corresponding scheduled task.
- [x] `plans_and_protocols/created_tasks.md` lists every created task ID with one-line descriptions.
- [x] Each created task names specific surviving mutants (file:line, category) and which assertion in the test file is too weak.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-002-02 | pending | Provides the baseline this task acts on |

## Notes

The pattern "surviving mutant → strengthen assertion" is the canonical mutation-testing feedback loop. The remediation is rarely "add another test"; it is more often "the existing test asserts something weak (e.g. `expect(result, isNotNull)`) and needs to assert something specific (e.g. `expect(result.iv, isNot(equals(originalIv)))`)."

A surviving mutant being declared "benign" is a deliberate choice with consequences: the next time mutation runs, the same mutant will survive again. The register entry must be specific enough that future runs can match it (file:line, mutation kind, rationale) and be re-evaluated when the surrounding code changes.
