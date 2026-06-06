---
task_id: TASK-PROC-002-07
audit_date: 2026-05-16
scope: test/unit/ + test/widget/
total_test_files: 159
total_test_calls: 1096
---

# Test Hygiene Audit — REQ-PROC-002 AC-05 & AC-06

## Method

Mechanical scan of `test/unit/**/*.dart` and `test/widget/**/*.dart`:

- **AC-05 (naming)**: Extract every `test('...')` / `testWidgets('...')` name (handling embedded quotes), then classify each as `behaviour`, `method_only`, or `ambiguous` using keyword heuristics.
- **AC-06 (isolation)**: Grep regex for `HttpClient(`, `package:http`, `package:dio`, `File(`, `Directory(`, `Platform.environment`, `DateTime.now(`, `Clock.now(`, `MethodChannel(`, `setMockMethodCallHandler(`. Lines beginning with `//`, `///`, `*` excluded. Each hit manually reviewed in context for (a) problematic, (b) acceptable, (c) ambiguous.

Raw extraction scripts and JSON outputs are transient under `/tmp/audit/` — not committed; the audit is reproducible by running the regex set against the test tree at this commit.

## AC-05 — Naming Audit

| Classification | Count |
|---|---|
| Behaviour-describing | 979 |
| Method-only style (`testFoo`, `Foo test`) | **0** |
| Ambiguous / borderline | 117 |

### Method-only (a clear AC-05 violation): **none**

No tests use the `testFoo` / `Foo test` / `it works` patterns that AC-05 explicitly flags.

### Borderline: 117 cases use `method_condition_outcome` snake_case

Example sample (representative — full list in scan output):

| File | Test name |
|---|---|
| `test/unit/core/domain/entities/questionnaire_plan/choice_options_test.dart:10` | `create_validInput_returnsInstanceWithCorrectValues` |
| `test/unit/core/domain/entities/questionnaire_plan/choice_options_test.dart:26` | `create_emptyChoicesUuids_throwsException` |
| `test/unit/core/domain/entities/questionnaire_plan/choice_test.dart:110` | `fromJson_validJson_returnsInstanceWithCorrectValues` |
| `test/unit/core/domain/entities/questionnaire_plan/question_json_test.dart:204` | `fromJson_ClosedLikert_missingLikertOptions_throwsMissingLikertOptionsException` |
| `test/unit/core/domain/failures/failures_test.dart:13` | `equality_sameVersion_returnsTrue` |
| `test/unit/core/design_system/molecules/list_item_test.dart:180` | `respects theme` |
| `test/widget/core/widgets/layout/default_detail_placeholder_test.dart:69` | `centers content` |

Per goal.md note ("borderline cases for the user to decide"): these names *do* describe behaviour — the `_returnsX` / `_throwsY` suffix is an outcome — but they're structured around the method under test rather than a free-form behaviour sentence. The two short widget names (`respects theme`, `centers content`) are concise behaviour descriptions, not method names. **Not flagged as problematic.**

### AC-05 verdict: 0 problematic findings

## AC-06 — Isolation Audit

Raw matches:

| Pattern | Hits |
|---|---|
| `HttpClient(` | 0 |
| `package:http` | 0 |
| `package:dio` | 0 |
| `File(` | 1 |
| `Directory(` | 0 |
| `Platform.environment` | 0 |
| `DateTime.now(` | 4 |
| `Clock.now(` | 0 |
| `MethodChannel(` / `setMockMethodCallHandler(` | 4 |

### Per-hit review

1. **`File(`** — `test/unit/features/client/data_receive/presentation/qr_recognition_pipeline_ffi_test.dart:119`
   ```dart
   if (!Platform.isWindows ||
       !File('build/windows/x64/runner/Release/flutter_zxing.dll').existsSync()) {
     print('Skipping FFI tests: flutter_zxing.dll not found');
     return;
   }
   ```
   **Classification: (b) acceptable.** Pre-condition guard that skips when the build artifact is absent. The test gates itself on Windows + dll existence and exits cleanly otherwise — no environmental dependence on test outcome, only on whether the test runs at all. The FFI target is by nature a Windows-binary integration check; the alternative would be moving it under `integration_test/`, which is out of scope for AC-06.

2. **`DateTime.now()`** — `test/unit/core/domain/entities/questionnaire_plan/questionnaire_plan_create_test.dart:139`
   ```dart
   test('should set startDate to DateTime.now() if startDate is not provided', () {
   ```
   **False positive** — match is inside the test name string, not in test code. The test body asserts only `startDate, isNotNull`; no wall-clock dependence.

3. **`DateTime.now()`** — `test/unit/features/therapist/data_receive/presentation/bloc/therapist_receive_bloc_test.dart:250`
   ```dart
   final now = DateTime.now();
   final timestamps = List.generate(6, (i) => now.subtract(Duration(milliseconds: i * 400)));
   ```
   **Classification: (b) acceptable.** `now` is a base for relative timestamps; the assertion checks `currentScanRate ≈ 2.0`, which is a function of *relative* spacing (6 timestamps in 3 s). The wall-clock value cancels out — the test outcome does not depend on when the test runs.

4. **`DateTime.now()`** — `test/widget/features/therapist/data_receive/presentation/screens/therapist_receive_screen_test.dart:574`
   Same pattern as (3): `now` used to build a list of relative-spaced timestamps for a fake `TherapistReceiveScanning` state. **Classification: (b) acceptable.**

5. **`DateTime.now()`** — `test/widget/features/therapist/plan_templates/presentation/widgets/plan_details_form_test.dart:70`
   ```dart
   expect(capturedStartDate, isNotNull); // Default start date is DateTime.now()
   ```
   **False positive** — match is in an end-of-line comment.

6. **`MethodChannel(...)` + `setMockMethodCallHandler(...)`** — `test/widget/features/therapist/data_receive/presentation/screens/therapist_receive_screen_test.dart:1021,1022,1055,1056`
   Two installations of `TestDefaultBinaryMessenger.setMockMethodCallHandler` on `MethodChannel('dev.moodtracker.screen_capturer_qr')`. **Classification: (b) acceptable** — this is the standard mock pattern AC-06 explicitly permits.

### AC-06 verdict: 0 problematic findings

## Volume Decision

Total problematic findings across AC-05 and AC-06: **0**.

Per goal.md acceptance criteria: "If zero findings: that fact is recorded explicitly." This is that record.

No inline fixes are needed; no backfill-creator follow-on task is needed.

## Notes for the Future

- The `method_condition_outcome` snake_case naming convention is widespread in `questionnaire_plan/` and `failures/`. It is borderline per AC-05; if the project later decides to enforce free-form behaviour sentences, those 117 names would need renames. That decision is *not* made by this audit.
- The two `DateTime.now()`-as-relative-reference patterns (cases 3 and 4 above) would become problematic if a future change made the assertion depend on the absolute wall-clock value. If clock injection (`Clock`/`DateTime Function()`) lands in those SUTs, the test sites should switch over for symmetry — but no current breakage justifies opening that work now.
- The FFI test (case 1) is the only test in scope that reaches the real filesystem. Its skip-guard structure is the right pattern; if other FFI/binary tests appear, they should follow the same shape.
