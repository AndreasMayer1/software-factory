# Protocol: Phase 1 Implementation — Data-Entry Frame-Budget Integration Test

**Date**: 2026-05-18
**Agent ID**: a1e4933dc7ca73179
**Task**: TASK-PROC-046-10
**Phase**: 1 (test source + documentation; no device run)

---

## Files Created

| File | Status | Notes |
|------|--------|-------|
| `integration_test/perf/data_entry_frame_budget_test.dart` | NEW | ~180 lines; WHY comments per plan §3.1 |
| `integration_test/perf/README.md` | NEW | ~55 lines |
| `test_driver/integration_test.dart` | NEW (was absent) | Standard 3-line flutter drive shim |
| `doc/testing/frame_budget_measurement_methodology.md` | NEW | ~160 lines |
| `doc/testing/README.md` | MODIFIED | +1 row for frame_budget_measurement_methodology.md |

Total: 4 new files, 1 modified.

---

## `test_driver/integration_test.dart` Status

**Was absent** — created as new. The `test_driver/` directory did not exist in the repo.
Created both the directory and the standard 3-line `integrationDriver()` shim.

---

## Actual Widget Keys Discovered vs. Plan Assumption

**Plan assumption** (§4): `ValueKey('likert_<question_id>')` from `data_input_detail_view.dart`.

**Actual key** (confirmed by source inspection of
`lib/features/client/data_input/presentation/organisms/data_input_detail_view.dart` line 60):
```dart
key: ValueKey('likert_${question.id}'),
```

**Match**: confirmed. The plan's assumption was correct.

**Question IDs** (from `DataInputBloc._onLoadQuestions` — hardcoded dummy data):
- First question: `id: '1'` → key `ValueKey('likert_1')`
- Second question: `id: '2'` → key `ValueKey('likert_2')`

The test uses `find.byKey(const ValueKey('likert_1'))` and
`find.byKey(const ValueKey('likert_2'))` directly. No deviation needed.

**QuestionCard key**: the cards themselves use `ValueKey(question.id)` (e.g.
`ValueKey('1')`), not named keys. This is not the Likert input key — correct per plan.

---

## `dart analyze` Result

```
dart analyze integration_test/perf/data_entry_frame_budget_test.dart
```

**Exit code: 0**

Remaining issues: 19 `info`-level style hints (line length in doc comments,
`cascade_invocations` on `getIt.registerSingleton` calls with differing generic
type parameters — cascade is not applicable here). No warnings, no errors.

Resolved before final analyze pass:
- `unused_import` (get_it.dart — removed)
- `unnecessary_cast` on `ensureInitialized()` return value
- `unused_local_variable` (questionCardFinder)
- `avoid_dynamic_calls` (cast summary to `Map<String, dynamic>?`)
- `avoid_types_on_closure_parameters` (removed `WidgetTester` annotation)
- `directives_ordering` (moved go_router import to correct alphabetical position)

---

## Phase 2 Follow-Up Task

**Task ID**: TASK-PROC-046-15
**Folder**: `requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-18_impl_a40-baseline-run-for-data-entry-frame-budget/`
**after**: [TASK-PROC-046-10]
**awaiting**: ["physical A40 attached on Windows host"]
**Status**: pending (blocked on physical device)

The plan (§7) was updated with a footer noting the task ID.

---

## Deviations from Plan

| # | Deviation | Justification |
|---|-----------|---------------|
| 1 | `test_driver/` directory and `integration_test.dart` created fresh (was not pre-existing) | Plan §3.3 said "create only if absent" — this is consistent |
| 2 | Test uses minimal router (only `/` and `/client/data-input` routes) rather than full suite router | The perf test does not need therapist routes; a minimal router reduces setup complexity and failure surface |
| 3 | `pumpUntil` implemented as inline while-loop (not as helper function call) | `pumpUntilFound` helper exists in `integration_test/helpers/pump_helpers.dart` but importing that helper would add a dependency from the perf test to the suite's helpers folder — against the isolation requirement in plan §6. Inline loop is equivalent. |
| 4 | `ensureInitialized()` cast removed (cast was unnecessary — `ensureInitialized()` on `IntegrationTestWidgetsFlutterBinding` already returns `IntegrationTestWidgetsFlutterBinding`) | Analyzer flagged as `unnecessary_cast`; removed per lint rules |

No deviations affect the test's correctness, gate coverage, or plan §2 AC assignments.

---

## Phase 1 AC Status

| AC | Description | Status |
|----|-------------|--------|
| AC-G1 | Integration test file exists under `integration_test/perf/` | DONE |
| AC-G2 | Test wraps representative interaction in `traceAction()` | DONE |
| AC-G3 | Test asserts ≤ 16 ms average and 0 missed budget | DONE |
| AC-G4 | Baseline run on A40 archived | DEFERRED → TASK-PROC-046-15 |
| AC-G5 | `doc/testing/` documents run command, outputs, failure interpretation | DONE |
| AC-G6 | If baseline fails, remediation task created | DEFERRED → TASK-PROC-046-15 |
