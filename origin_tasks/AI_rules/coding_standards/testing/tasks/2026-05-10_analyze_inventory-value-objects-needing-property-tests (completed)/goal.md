---
task_id: TASK-PROC-002-04
type: analyze
parent_requirement: REQ-PROC-002
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-PROC
status: completed
effort: S
created: 2026-05-10
started: 2026-05-16
completed: 2026-05-16
session_completed_at: 2026-05-16T15:48:11Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03]
  sections: []
scope_description: "Walk lib/core/domain/ and lib/features/*/domain/ to enumerate value objects and entities, classify each by which of the six invariant categories applies (bounded range, enum totality, length/format, ordering, round-trip, algebraic laws), and list those that need property-based tests."
release_description: ""
opus_recommended: true  # promoted after context_limit_no_entitlement
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: 7df6dfd1-226b-4c01-8d33-7ce959e31412
session_account: web
---

# Goal: Inventory value objects needing property-based tests (TQ3)

## Objective

REQ-PROC-002 AC-03 names six categories of "non-trivial invariants" that require property-based tests. The set of types in `lib/core/domain/` and `lib/features/*/domain/` matching one or more of those categories is currently unknown. This task produces the inventory: every value object / entity → invariant categories that apply → existing property tests (if any) → backfill effort.

## Requirements Summary

REQ-PROC-002 AC-03. The six categories: (a) bounded numeric range, (b) enum totality, (c) string length/format, (d) ordering/comparison, (e) serialization round-trip, (f) algebraic laws on aggregates.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Walk `lib/core/domain/` and `lib/features/*/domain/`. For each Dart class, identify whether it is a value object / entity / aggregate.
- For each candidate type, classify against the six categories. A type may match zero (no property test needed), one, or multiple categories.
- For each type that matches at least one category, check `test/unit/.../[type]_test.dart` for existing `Glados<T>` test bodies that exercise that category's invariant.
- Output `plans_and_protocols/value_objects_inventory.md` with a table: type | path | categories | existing property tests | gap.
- For each gap, estimate effort (S / M / L) for writing the missing property tests.
- Surface any types where the invariant is implicit / undocumented — those need their invariants codified before property tests can be written meaningfully.

### Out of Scope

- Writing the missing property tests. That's the backfill work, scoped from this inventory.
- Refactoring types whose invariants are unclear. Just flag them.
- Inventory of types outside the domain folders (data models, presentation models). Those typically have less interesting invariants; out of scope here.

## Acceptance Criteria

- [x] `plans_and_protocols/value_objects_inventory.md` lists every domain type in scope with category classifications.
- [x] Existing property-test coverage is cross-referenced (yes / no per category).
- [x] Effort estimate is given for each gap.
- [x] Total effort is summarized at the top so the user can decide whether to backfill in one task or break it up.
- [x] Types with implicit / undocumented invariants are flagged separately for invariant-codification work.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-002-02 | not blocking | Glados need not be installed to do the inventory; classification is the output |

## Notes

A type with *only* trivial invariants (e.g. an immutable wrapper around a `String` with no constraints) does not require a property test. The classification step is the value of this task.

Use `codegraph` to walk the domain folders if available; otherwise grep for `class.*extends Equatable` (common pattern), `final.*=`, etc.
