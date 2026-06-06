---
task_id: TASK-PROC-061-17
type: impl
parent_requirement: REQ-PROC-061
urgency: 3
urgency_reason: U3-MAINTENANCE
impact: 2
impact_reason: I2-DEV
status: pending
effort: S
created: 2026-06-03
after: [TASK-PROC-061-07]
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Bump qr 3.0.2→4.0.0 (dev dependency); migrate two test files to new QrCode/QrErrorCorrectLevel API"
release_description: ""
opus_recommended: false
---
# Goal: Bump qr 3.0.2 → 4.0.0 (dev dependency migration)

## Objective

Apply the approved bump: `qr` from `3.0.2` to `4.0.0`. This is a dev dependency only. Two test files use the `qr` package API and must be migrated to the v4 API.

## Background

Decision rationale: `plans_and_protocols/2026-06-03_01_decisions.md` in TASK-PROC-061-07.

## Breaking Changes Confirmed (from TASK-PROC-061-07 investigation)

- `QrErrorCorrectLevel` converted to a proper Dart enum. Value names changed (e.g. `.M` → `.medium`, `.H` → `.high`, `.L` → `.low`, `.Q` → `.quartile`)
- `QrCode` made `final class`; all mutation methods removed
- `QrImage` declared `final class`
- `QrCode.fromData(...)` constructor: verify if signature changed
- Dart SDK minimum bumped to `^3.11.0` — must verify against project's Flutter SDK's bundled Dart

## Affected Files

1. `test/unit/features/therapist/data_transfer/data/services/plan_serialization_service_test.dart`
   - Uses `QrErrorCorrectLevel.M`, `QrErrorCorrectLevel.H` → update to `.medium`, `.high`

2. `test/unit/features/client/data_receive/presentation/qr_recognition_pipeline_ffi_test.dart`
   - Uses `QrCode.fromData(data, errorCorrectLevel: QrErrorCorrectLevel.M)` → verify new constructor signature
   - Uses `QrImage(qrCode)` → verify still valid in v4

**Note:** These are test files only. No production `lib/` code uses the `qr` package directly.

## Steps

1. Pre-check: verify that the project's Flutter SDK bundles Dart `>=3.11.0` (`dart --version`)
2. Update `pubspec.yaml`: `qr: any` → `qr: ^4.0.0`
3. Run `flutter pub get`
4. Read `qr` 4.0.0 package's API (via `flutter pub deps` or package source) to confirm exact constructor and enum signatures
5. Update the two test files:
   - Replace `QrErrorCorrectLevel.M` → `QrErrorCorrectLevel.medium`, `QrErrorCorrectLevel.H` → `QrErrorCorrectLevel.high` (and any other enum value references)
   - Update `QrCode.fromData(...)` constructor call if signature changed
6. Run `dart analyze` — must be clean
7. Run tests for these two files: `flutter test test/unit/features/therapist/data_transfer/data/services/plan_serialization_service_test.dart test/unit/features/client/data_receive/presentation/qr_recognition_pipeline_ffi_test.dart`
8. Run full `flutter test` suite
9. Run quality gates

## Acceptance Criteria

- [ ] `qr` bumped to `^4.0.0` in `pubspec.yaml` and resolved in `pubspec.lock`
- [ ] Both test files compile and pass with the v4 API
- [ ] `QrErrorCorrectLevel` enum values use new lowercase names throughout
- [ ] `dart analyze` reports no new issues
- [ ] All existing tests pass
- [ ] Quality gates green
