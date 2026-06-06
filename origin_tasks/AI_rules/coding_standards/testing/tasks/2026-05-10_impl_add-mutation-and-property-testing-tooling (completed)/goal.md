---
task_id: TASK-PROC-002-02
type: impl
parent_requirement: REQ-PROC-002
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-10
started: 2026-05-18
completed: 2026-05-18
session_completed_at: 2026-05-18T20:18:39Z
after: [TASK-PROC-049-08]  # canon-bootstrap T7 must complete first; see .claude/task_ordering_priority_override.txt
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-03]
  sections: []
scope_description: "Add mutation_test (or dart_mutant) and glados as dev dependencies, configure mutation_test for lcov-scoped runs over the AC-04 critical paths, configure diff-only mode for per-change use, document conventions and the surviving-mutant register format in doc/testing/."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: ab7949d8-3b22-42db-be65-d91db57d2381
session_account: gmail
---
# Goal: Add mutation testing and property-based testing tooling

## Objective

REQ-PROC-002 AC-02 (mutation kill rate ≥ 80 % on safety-critical paths) and AC-03 (property-based tests on value objects with non-trivial invariants) require tooling that does not currently exist in the project. This task adds the dev dependencies, configures them for the project's specific needs (lcov-scoped mutation runs on AC-04 paths; `glados` integration with `package:test`), and documents the conventions so subsequent tasks (running mutation tests, writing property tests) have a stable foundation.

## Requirements Summary

REQ-PROC-002 AC-02: mutation kill rate ≥ 80 % on critical paths via `mutation_test` or `dart_mutant`, scoped via lcov.
REQ-PROC-002 AC-03: property-based tests via `glados` for value objects with non-trivial invariants.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Evaluate `mutation_test` (pub.dev) vs. `dart_mutant` (dartmutant.dev). Pick one based on:
  - Runtime cost on the project's test suite
  - Whether lcov-scoped runs work reliably
  - Whether diff-only mode works reliably
  - AST-aware vs. regex-based mutation operators
  Document the choice and rationale in `doc/testing/`.
- Add the chosen tool to `pubspec.yaml` under `dev_dependencies`.
- Configure mutation rules (the operator set: arithmetic, comparison, boolean, null-safety) appropriate for the project's domain logic.
- Wire mutation testing to the AC-04 critical-paths list (depends on TASK-PROC-046-04 if available, else use a placeholder).
- Add `glados` to `pubspec.yaml` under `dev_dependencies`.
- Document the property-test conventions (where they live in `test/`, how they use `Glados<T>` vs. `test()`, generator selection patterns).
- Establish the surviving-mutant register format: a `doc/testing/surviving_mutants.md` (or similar) table where each surviving mutant is recorded with `id | path | line | mutation | rationale | follow-up task`.
- Run a baseline mutation test on the AC-04 paths (or a sample if the full run is too long) and record the baseline kill rate in `plans_and_protocols/`.
- Run `flutter pub get` and verify the test suite still passes after adding the dependencies.

### Out of Scope

- Addressing surviving mutants on the critical paths. That's separate remediation work, sized once the baseline is known.
- Writing missing property-based tests. Inventory is TASK-PROC-002-04; the writing is downstream backfill.
- Mutation-testing other parts of `lib/` outside the AC-04 scope.

## Acceptance Criteria

- [x] One of `mutation_test` or `dart_mutant` is chosen with documented rationale; added to `dev_dependencies` in `pubspec.yaml`.
- [x] `glados` is added to `dev_dependencies` in `pubspec.yaml`.
- [x] Mutation tooling is configured for lcov-scoped runs against the AC-04 path list and for diff-only runs in development.
- [x] `doc/testing/` documents: the tooling choice and rationale, the property-test conventions, the surviving-mutant register format.
- [x] A baseline mutation kill rate on the AC-04 paths is recorded in `plans_and_protocols/`.
- [x] `flutter test` continues to pass; `flutter pub get` succeeds with the new dependencies.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-04 | pending (recommended) | Critical-paths list informs mutation lcov filter. If unavailable, use a placeholder list and update once TASK-PROC-046-04 lands. |

## Notes

The two tools have different trade-offs: `mutation_test` is mature, supports diff-only mode out of the box, and has detailed documentation. `dart_mutant` is faster (Rust + parallelism) and AST-aware (cleaner mutation operators) but newer. For a solo dev, runtime cost matters — pick whichever the actual baseline run prefers.
