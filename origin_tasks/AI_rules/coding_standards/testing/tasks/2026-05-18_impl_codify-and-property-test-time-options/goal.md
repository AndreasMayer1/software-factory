---
task_id: TASK-PROC-002-19
type: impl
parent_requirement: REQ-PROC-002
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-PROC
status: pending
effort: M
created: 2026-05-18
after: [TASK-PROC-002-02, TASK-PROC-002-04]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03]
  sections: []
scope_description: "Backfill property test for codify and property test time options (REQ-PROC-002 AC-03)."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 2c52ed48
  file: ../../requirements.md
---
# Goal: Codify and property test time options

## Objective

Codify the allowed combinations of `(timeInputType, timeLabels)` *before* writing the property test — currently nonsensical combinations (e.g. `None` + non-empty `timeLabels`) are silently accepted. Enforce the documented combinations in the factory. Then add a `glados` property test covering (e) JSON round-trip and (f) `timeLabels` list-preservation (identity + length preserved across encode/decode).

Implicit-invariant cluster — invariant codification precedes the property test (per inventory).

## Requirements Summary

REQ-PROC-002 AC-03: every value object and entity with non-trivial invariants must have at least one property-based test using `glados` exercising the relevant invariant.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Target type / source: `lib/core/domain/entities/questionnaire_plan_entities/time_options.dart`
- Property-test categories covered: see Objective above.
- Generators required: any.oneOf(TimeInputType.values), any.list of label combinations
- Test file under `test/unit/` following the test-folder layout in `doc/testing/`.
- Use stable, descriptive test names per REQ-PROC-002 AC-05 (describe the behaviour under verification).

### Out of Scope

- Other types in the inventory — each has its own backfill task.
- Mutation testing (REQ-PROC-002 AC-02) — handled per release candidate.
- Strengthening the existing example-based tests — keep them as-is; property tests strengthen, not replace.

## Acceptance Criteria

- [ ] At least one `glados` (or `Glados<T>`) property test exists for the target type, exercising each invariant listed in the Objective.
- [ ] The generator spans the documented invariant range (per REQ-PROC-002 AC-03 pitfall: narrow generators that miss boundaries fail the gate).
- [ ] Boundary-violation rejection is verified using `throwsA(...)` (REQ-PROC-002 AC-01).
- [ ] Test name describes behaviour, not method invoked (REQ-PROC-002 AC-05).
- [ ] `flutter test` passes locally with `--test-randomize-ordering-seed=random`.
- [ ] Invariant codified in source (factory validator + doc-comment) BEFORE property test is written; the codification decision is made explicit and matches `create` / `fromJson` paths.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-002-02 | completed | `glados` is installed as a dev dependency |
| TASK-PROC-002-04 | completed | Inventory of value objects produced |

## Notes

Generator hints (from inventory):
- any.oneOf(TimeInputType.values), any.list of label combinations

See the inventory at `requirements_tasks/process/AI_rules/coding_standards/testing/tasks/2026-05-10_analyze_inventory-value-objects-needing-property-tests (completed)/plans_and_protocols/value_objects_inventory.md` for the full invariant analysis.

Keep the existing example-based tests; the property test strengthens them by spanning the input space, not replacing them.
