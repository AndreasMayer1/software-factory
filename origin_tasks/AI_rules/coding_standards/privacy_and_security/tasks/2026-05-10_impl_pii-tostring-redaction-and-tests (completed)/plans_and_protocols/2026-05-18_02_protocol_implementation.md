# Protocol: PII toString() Redaction Implementation

**Task**: TASK-PROC-052-03
**Date**: 2026-05-18
**Mode**: Automated (inline execution after subagent rate-limit)
**Status**: Implementation complete; ready for task-complete

---

## What Was Done

All four batches from `2026-05-18_01_plan_pii_tostring_redaction.md` executed
inline by the orchestrating session (the spawned implementation-engineer agent
hit a rate limit before doing any work; reverting to inline execution).

### Source files edited (11 files, 12 classes)

| Class | File | WHY comment |
|---|---|---|
| `Contact` | `lib/core/domain/entities/contact.dart` | yes — closes Equatable name leak |
| `QuestionnaireEvaluationData` | `lib/core/domain/entities/plan_evaluation_input.dart` | no — mechanical |
| `AnswerEntry` | `lib/core/domain/entities/plan_evaluation_input.dart` | yes — Object value type rule |
| `TransferChunk` | `lib/features/therapist/data_transfer/domain/value_objects/transfer_chunk.dart` | yes — defence-in-depth rationale |
| `QuestionnairePlan` (v2) | `lib/core/domain/entities/questionnaire_plan_entities/questionnaire_plan.dart` | no |
| `Questionnaire` (v2) | `lib/core/domain/entities/questionnaire_plan_entities/questionnaire.dart` | no |
| `Question` (v2) | `lib/core/domain/entities/questionnaire_plan_entities/question.dart` | no |
| `Choice` (v2) | `lib/core/domain/entities/questionnaire_plan_entities/choice.dart` | no |
| `QuestionnairePlan` (v1) | `lib/core/domain/entities/questionnaire_plan_entities/v1/questionnaire_plan.dart` | no |
| `Questionnaire` (v1) | `lib/core/domain/entities/questionnaire_plan_entities/v1/questionnaire.dart` | no |
| `Question` (v1) | `lib/core/domain/entities/questionnaire_plan_entities/v1/question.dart` | no |
| `Choice` (v1) | `lib/core/domain/entities/questionnaire_plan_entities/v1/choice.dart` | no |

### Test files created (11 new files)

- `test/unit/core/domain/entities/contact_tostring_redaction_test.dart`
- `test/unit/core/domain/entities/plan_evaluation_input_tostring_redaction_test.dart`
  (covers both `QuestionnaireEvaluationData` and `AnswerEntry`)
- `test/unit/core/domain/entities/questionnaire_plan/questionnaire_plan_tostring_redaction_test.dart`
- `test/unit/core/domain/entities/questionnaire_plan/questionnaire_tostring_redaction_test.dart`
- `test/unit/core/domain/entities/questionnaire_plan/question_tostring_redaction_test.dart`
- `test/unit/core/domain/entities/questionnaire_plan/choice_tostring_redaction_test.dart`
- `test/unit/core/domain/entities/questionnaire_plan/v1/questionnaire_plan_v1_tostring_redaction_test.dart`
- `test/unit/core/domain/entities/questionnaire_plan/v1/questionnaire_v1_tostring_redaction_test.dart`
- `test/unit/core/domain/entities/questionnaire_plan/v1/question_v1_tostring_redaction_test.dart`
- `test/unit/core/domain/entities/questionnaire_plan/v1/choice_v1_tostring_redaction_test.dart`
- `test/unit/features/therapist/data_transfer/domain/value_objects/transfer_chunk_tostring_redaction_test.dart`

### Doc note appended

`doc/architecture/logging.md` — new section "Structural PII Redaction in Domain
Types (REQ-PROC-052 AC-05)" inserted between "Sensitive Data Prohibition" and
"Testing". Describes the override convention, the sentinel-test contract, and
the procedure for adding a new PII-bearing type.

## Test Results

- Targeted run of all 11 new redaction tests: **39 tests pass, 0 fail** (3 s).
- Full `flutter test test/unit` regression: 984 pass, 8 fail.
  All 8 failures are in `test/unit/core/domain/services/questionnaire_plan/choice_service_test.dart` and are
  **pre-existing on develop** (verified by stashing this task's edits and re-running:
  same 8 failures). The failures are a Dartz `Right<Failure, Unit>` vs
  `Right<Failure, void>` type mismatch — unrelated to `toString()` and
  unrelated to any code path this task touched.

## Deviations from Plan

None of substance. Two small departures:

1. The plan's worked skeleton used a top-level `const String _kSentinel`; the
   implementation inlines `const sentinel = '...'` inside `main()` for parity
   with the surrounding codebase's existing test style (single-file scope, no
   leading underscore).
2. For `TransferChunk` the plan's "kitchen-sink" formulation is replaced with
   a payload-spelling-sentinel-ASCII test plus an empty-payload sanity test —
   the sentinel rule for a Uint8List field is structurally different from the
   String case and the chosen pair gives stronger coverage.

## Acceptance Criteria

From `goal.md`:

- [x] Every PII-bearing type has an overridden `toString()` returning a redacted form. (12 classes)
- [x] Each type has a unit test asserting the sentinel-content rule.
- [x] All redaction tests pass. (39/39 green)
- [x] `doc/architecture/logging.md` documents the redaction convention.
- [x] No existing code that calls `toString()` on these types is broken.

REQ-PROC-052 mapping:
- AC-05 (PII redaction in `toString()`): fully covered.
- AC-06 (safe logging): structural defence layer in place; logger-call-site
  grep/lint gate is out of scope per `goal.md` and remains a separate task.

## Notes for Future Sessions

- The plan file `2026-05-18_01_plan_pii_tostring_redaction.md` is the canonical
  inventory; when adding a new domain type carrying user-entered text, extend
  both the plan's inventory AND the test set (see the doc note in
  `doc/architecture/logging.md` for the procedure).
- `TrackingEntry` and the "filled questionnaire answer payload" type (not yet
  introduced) were explicitly considered and excluded — the plan notes that
  any new payload type with user text MUST be added to the inventory before
  merge.

Session ID: 33e6aab1-a0ee-40c0-b12b-ea3a59e5f6d7
