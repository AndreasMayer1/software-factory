# Plan: PII-bearing toString() Redaction and Tests

**Task**: TASK-PROC-052-03
**Requirement**: REQ-PROC-052 AC-05, AC-06
**Date**: 2026-05-18
**Author**: architecture-advisor

---

## 1. PII-Bearing Type Inventory

The walk covered `lib/core/domain/` and `lib/features/*/domain/`. A type is PII-bearing if it carries user-entered free-text — content the user (client or therapist) types or speaks-to-text — as a field on the in-memory domain object. The judgement is conservative: anything that *could* one day hold typed user prose is included; pure numeric / identifier / enum / structural fields are excluded.

| # | File | Class | PII-bearing fields | Existing `toString()`? | Non-PII metadata available for redacted form |
|---|------|-------|-------------------|------------------------|----------------------------------------------|
| 1 | `lib/core/domain/entities/contact.dart` | `Contact` | `name` (therapist or client display name, user-entered) | No (only inherited `Equatable.toString`, which does emit props) | `therapistId`, `createdAt`, `name.length`, `scannerTier`, `encryptedTransferKey.length` |
| 2 | `lib/core/domain/entities/questionnaire_plan_entities/questionnaire_plan.dart` | `QuestionnairePlan` (v2) | `name`, `therapistNotes`, `clientInstructions` | No | `uuid`, `dataVersion`, `startDate`, `endDate`, `questionnaireUuids.length`, lengths of the three text fields |
| 3 | `lib/core/domain/entities/questionnaire_plan_entities/questionnaire.dart` | `Questionnaire` (v2) | `name`, `shortLabel`, `description` | No | `uuid`, `questionUuids.length`, `timeInterval` (structural enum), `remindersEnabled` |
| 4 | `lib/core/domain/entities/questionnaire_plan_entities/question.dart` | `Question` (v2) | `shortLabel`, `questionText` | No | `uuid`, `questionType`, presence-flags for `likertOptions` / `choiceOptions` / `timeOptions` / `timeInputType` |
| 5 | `lib/core/domain/entities/questionnaire_plan_entities/choice.dart` | `Choice` (v2) | `text` (the displayed answer label — author-entered by therapist) | No | `uuid`, `questionUuid`, `text.length` |
| 6 | `lib/core/domain/entities/questionnaire_plan_entities/v1/questionnaire_plan.dart` | `QuestionnairePlan` (v1) | `name`, `description` | No | `uuid`, `startDate`, `endDate`, `questionnaireUuids.length`, length of `description` |
| 7 | `lib/core/domain/entities/questionnaire_plan_entities/v1/questionnaire.dart` | `Questionnaire` (v1) | `name`, `description` | No | `uuid`, `questionUuids.length`, `timeInterval`, `remindersEnabled` |
| 8 | `lib/core/domain/entities/questionnaire_plan_entities/v1/question.dart` | `Question` (v1) | `shortLabel`, `questionText` | No | `uuid`, `questionType`, option-presence flags |
| 9 | `lib/core/domain/entities/questionnaire_plan_entities/v1/choice.dart` | `Choice` (v1) | `text` | No | `uuid`, `questionUuid`, `text.length` |
| 10 | `lib/core/domain/entities/plan_evaluation_input.dart` | `QuestionnaireEvaluationData` | `name`, `shortLabel` | No | `questionnaireUuid`, `answers.length` |
| 11 | `lib/core/domain/entities/plan_evaluation_input.dart` | `AnswerEntry` | `value` (when `value is String` it is a user-entered free-text answer; for int/Likert/index types it is not PII but cannot be distinguished structurally at the type level — treat as PII to be safe) | No | `questionUuid`, `recordedAt`, `endedAt`, `value.runtimeType`, `isDurationEvent`; for String values, `(value as String).length` |

### Types explicitly considered and excluded (with rationale)

These exist in `lib/core/domain/` or look superficially like candidates but do NOT bear user-entered free-text:

- **`TrackingEntry`** (`tracking_entry_entities/tracking_entry.dart`) — holds only `uuid`, structural booleans, dates, foreign-key UUIDs (`sourcePlanUuid`, `filledQuestionnaireUuid`), and the `OwnershipContext`. The actual user content lives in a separately-keyed answer payload referenced by `filledQuestionnaireUuid`. Equatable's default `toString` therefore already emits only safe fields. **No override needed.** *(Documented note: when a future "filled answer payload" domain type is introduced, it MUST be added to the PII inventory before merge.)*
- **`OwnershipContext` / `TherapistAssignedContext` / `ClientCreatedContext`** — only `PairingIdentity` (a UUID) and an `isPrivate` boolean. Safe by construction.
- **`PairingIdentity`** — single `uuid` field. Equatable's `toString` is already safe.
- **`TransferBundle`** — only UUIDs, enums, counts. Safe by construction.
- **`TransferChunk`** (feature: `data_transfer`) — opaque encrypted bytes (`payload`) plus integer header fields. The payload is *user data after encryption*; the redaction concern is the unencrypted form. As stored on the type it is already opaque ciphertext bytes (`Uint8List`); Equatable's default would print byte counts. However, to defend against an accidental `debugPrint('$chunk')` that dumps full hex, **we also add a redacted toString here** (defensive — bytes-as-hex could still aid attacker correlation). **Add this type to the inventory** — see updated entry #12 below.
- **`ChoiceOptions`, `LikertOptions`, `TimeOptions`, `TimeInterval`** — only enum, int, and UUID-string fields. Safe by construction. No override needed.
- **`ActionItem`, `ActionGroup`** — `title` is a hard-coded UI navigation label (e.g. "Add entry"), not user-entered. Not PII.
- **Failures / Exceptions** (`*_failures.dart`, `exceptions.dart`) — `message` fields are developer-authored error strings, never user content. Not PII.
- **Presentation-layer state classes** (`*State`, `*Event` under `lib/features/**/presentation/bloc/`) — out of scope for this task per `goal.md` ("walk `lib/core/domain/` and `lib/features/*/domain/`"). If they end up carrying domain instances, the domain type's redacted `toString()` is what protects them transitively.
- **`ScannerHardwareTier`, `ScannerTierParameters`, `TransferDetectionSnapshot`, `TransferDetectionZone`, `TransferDetectionModel`** — numeric tuning parameters and detection-state structs. No user text.

### Addendum entry #12

| # | File | Class | PII-bearing fields | Existing `toString()`? | Non-PII metadata available |
|---|------|-------|-------------------|------------------------|----------------------------|
| 12 | `lib/features/therapist/data_transfer/domain/value_objects/transfer_chunk.dart` | `TransferChunk` | `payload` (encrypted bytes, but bytes-as-hex could still leak correlation signal) | No | `sequenceId`, `totalChunkCount`, `chunkIndex`, `payload.length` |

**Total PII-bearing types covered: 12** (10 textual + 1 String/Object value (`AnswerEntry`) + 1 defensive byte-payload (`TransferChunk`)).

---

## 2. Per-Type `toString()` Design

Single consistent pattern: `ClassName(<id-or-discriminator>, <structural fields>, <lengths only for text>)`. **Rule: only structural metadata (ids, UUIDs, dates, enum names, counts, lengths) is emitted; never user content; for free-text strings, expose only `.length` (and `null` vs present for nullable text fields).**

| # | Class | Redacted `toString()` form |
|---|-------|---------------------------|
| 1 | `Contact` | `Contact(therapistId: $therapistId, createdAt: ${createdAt.toIso8601String()}, nameLength: ${name.length}, scannerTier: $scannerTier, encryptedTransferKeyByteLength: ${encryptedTransferKey.length})` |
| 2 | `QuestionnairePlan` (v2) | `QuestionnairePlan(uuid: $uuid, dataVersion: $dataVersion, startDate: ${startDate?.toIso8601String()}, endDate: ${endDate?.toIso8601String()}, questionnaireCount: ${questionnaireUuids.length}, nameLength: ${name.length}, therapistNotesLength: ${therapistNotes?.length}, clientInstructionsLength: ${clientInstructions?.length})` |
| 3 | `Questionnaire` (v2) | `Questionnaire(uuid: $uuid, questionCount: ${questionUuids.length}, timeInterval: ${timeInterval.type}, remindersEnabled: $remindersEnabled, nameLength: ${name.length}, shortLabelLength: ${shortLabel.length}, descriptionLength: ${description.length})` |
| 4 | `Question` (v2) | `Question(uuid: $uuid, questionType: $questionType, hasLikertOptions: ${likertOptions != null}, hasChoiceOptions: ${choiceOptions != null}, hasTimeOptions: ${timeOptions != null}, timeInputType: $timeInputType, shortLabelLength: ${shortLabel.length}, questionTextLength: ${questionText.length})` |
| 5 | `Choice` (v2) | `Choice(uuid: $uuid, questionUuid: $questionUuid, textLength: ${text.length})` |
| 6 | `QuestionnairePlan` (v1) | `QuestionnairePlan.v1(uuid: $uuid, startDate: ${startDate?.toIso8601String()}, endDate: ${endDate?.toIso8601String()}, questionnaireCount: ${questionnaireUuids.length}, nameLength: ${name.length}, descriptionLength: ${description?.length})` |
| 7 | `Questionnaire` (v1) | `Questionnaire.v1(uuid: $uuid, questionCount: ${questionUuids.length}, timeInterval: ${timeInterval.type}, remindersEnabled: $remindersEnabled, nameLength: ${name.length}, descriptionLength: ${description.length})` |
| 8 | `Question` (v1) | `Question.v1(uuid: $uuid, questionType: $questionType, hasLikertOptions: ${likertOptions != null}, hasChoiceOptions: ${choiceOptions != null}, hasTimeOptions: ${timeOptions != null}, timeInputType: $timeInputType, shortLabelLength: ${shortLabel.length}, questionTextLength: ${questionText.length})` |
| 9 | `Choice` (v1) | `Choice.v1(uuid: $uuid, questionUuid: $questionUuid, textLength: ${text.length})` |
| 10 | `QuestionnaireEvaluationData` | `QuestionnaireEvaluationData(questionnaireUuid: $questionnaireUuid, answerCount: ${answers.length}, nameLength: ${name.length}, shortLabelLength: ${shortLabel.length})` |
| 11 | `AnswerEntry` | `AnswerEntry(questionUuid: $questionUuid, recordedAt: ${recordedAt.toIso8601String()}, endedAt: ${endedAt?.toIso8601String()}, valueType: ${value.runtimeType}, valueStringLength: ${value is String ? (value as String).length : null}, isDurationEvent: $isDurationEvent)` |
| 12 | `TransferChunk` | `TransferChunk(sequenceId: $sequenceId, chunkIndex: $chunkIndex, totalChunkCount: $totalChunkCount, payloadByteLength: ${payload.length})` |

**Pattern invariants enforced (developer / reviewer checklist):**

- Never emit a `String` field directly. For each `String` (or `String?`) PII field, emit `${field.length}` (or `${field?.length}`) under a name suffixed `…Length`.
- Never emit `Object value` directly; emit `value.runtimeType` + a nullable length-when-string.
- Never emit raw byte buffers (`Uint8List`, `List<int>`) directly; emit `${bytes.length}`.
- UUIDs, ISO-8601 dates, enum names, integer counts, and booleans are safe and may appear verbatim.
- The order is: identity (uuid / discriminator) → structural metadata → lengths (always last).

---

## 3. Test Plan

### File structure

One redaction-focused test file per type, mirroring `lib/` layout under `test/unit/`. Rationale: existing convention (e.g. `question_create_test.dart`, `question_json_test.dart`, `question_copy_equality_test.dart`) shows the codebase prefers one test file per concern. Adding a separate `*_tostring_redaction_test.dart` keeps each file focused and grep-able.

**A single consolidated `pii_redaction_test.dart` is NOT recommended** because (a) it would import 12 entities across two layers, (b) it would split test failure attribution from the type under test, and (c) it would break the mirror-of-`lib/` convention.

| # | Test file (new) |
|---|-----------------|
| 1 | `test/unit/core/domain/entities/contact_tostring_redaction_test.dart` |
| 2 | `test/unit/core/domain/entities/questionnaire_plan/questionnaire_plan_tostring_redaction_test.dart` |
| 3 | `test/unit/core/domain/entities/questionnaire_plan/questionnaire_tostring_redaction_test.dart` |
| 4 | `test/unit/core/domain/entities/questionnaire_plan/question_tostring_redaction_test.dart` |
| 5 | `test/unit/core/domain/entities/questionnaire_plan/choice_tostring_redaction_test.dart` |
| 6 | `test/unit/core/domain/entities/questionnaire_plan/v1/questionnaire_plan_v1_tostring_redaction_test.dart` |
| 7 | `test/unit/core/domain/entities/questionnaire_plan/v1/questionnaire_v1_tostring_redaction_test.dart` |
| 8 | `test/unit/core/domain/entities/questionnaire_plan/v1/question_v1_tostring_redaction_test.dart` |
| 9 | `test/unit/core/domain/entities/questionnaire_plan/v1/choice_v1_tostring_redaction_test.dart` |
| 10 | `test/unit/core/domain/entities/plan_evaluation_input_tostring_redaction_test.dart` (covers `QuestionnaireEvaluationData` + `AnswerEntry`) |
| 11 | (covered in row 10) |
| 12 | `test/unit/features/therapist/data_transfer/domain/value_objects/transfer_chunk_tostring_redaction_test.dart` |

**Total new test files: 11.**

### Sentinel rule (applies to every test file)

```dart
const String _kSentinel = '__SENTINEL_CONTENT_DO_NOT_LEAK__';
```

For each PII-bearing field on the type:

1. Construct an instance where ONLY that field is set to `_kSentinel` (or in the `AnswerEntry` case, `value: _kSentinel`) and the other PII fields are set to neutral non-sentinel placeholders such as `'x'`.
2. Assert `expect(instance.toString(), isNot(contains(_kSentinel)));`
3. Assert `expect(instance.toString(), contains(<known structural field>));` — e.g. the `uuid` for entity types, the `therapistId` for `Contact`, the `sequenceId` for `TransferChunk`.

For multi-PII-field types (e.g. `QuestionnairePlan` has three: `name`, `therapistNotes`, `clientInstructions`) the test runs the sentinel-only construction once per field — so a single field that accidentally leaks is detectable in isolation rather than masked by a different field passing.

Additionally, a "kitchen-sink" test sets every PII field to `_kSentinel` simultaneously and asserts the sentinel is absent — this catches a regression where one field accidentally interpolates another (unlikely but cheap to check).

Each test file groups assertions inside a single `group('PII redaction — ToString')` with one `test(...)` per PII field plus the kitchen-sink one.

### Worked test-file skeleton (for the implementing agent to follow verbatim)

```dart
// test/unit/core/domain/entities/questionnaire_plan/choice_tostring_redaction_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mood_tracker/core/domain/entities/questionnaire_plan_entities/choice.dart';

void main() {
  const sentinel = '__SENTINEL_CONTENT_DO_NOT_LEAK__';

  group('Choice PII redaction — toString()', () {
    test('does not leak `text`', () {
      final c = Choice(
        uuid: 'choice-uuid-1',
        text: sentinel,
        questionUuid: 'q-uuid-1',
      );
      final s = c.toString();
      expect(s, isNot(contains(sentinel)));
      expect(s, contains('choice-uuid-1'));        // structural id present
      expect(s, contains('q-uuid-1'));             // structural ref present
      expect(s, contains('textLength: ${sentinel.length}'));
    });

    test('kitchen-sink — every PII field set to sentinel', () {
      final c = Choice(
        uuid: 'choice-uuid-2',
        text: sentinel,
        questionUuid: 'q-uuid-2',
      );
      expect(c.toString(), isNot(contains(sentinel)));
    });
  });
}
```

The other 10 test files follow the identical skeleton, adjusted for the type's PII-field list.

---

## 4. Doc Note

`doc/architecture/logging.md` already exists and already contains a "Sensitive Data Prohibition" section. The redaction convention belongs there as a new subsection, because it is the *structural defense* that makes that prohibition enforceable. We do not need a new file.

**Proposed insertion** — append after the existing "Sensitive Data Prohibition" section, before "Testing":

```markdown
---

## Structural PII Redaction in Domain Types (REQ-PROC-052 AC-05)

The logger discipline above (call sites do not pass user content) is reinforced by a
type-level structural defense: every domain type that holds user-entered mental-health
content overrides `toString()` to return a redacted form that exposes only structural
metadata (UUIDs, ISO-8601 dates, enum names, counts, and field *lengths*) — never the
user content itself.

This means `debugPrint('$entry')` or string interpolation of a domain instance is
safe by construction, even when call-site discipline slips.

### Convention

For each PII-bearing class, the override pattern is:

\`\`\`dart
@override
String toString() =>
    'ClassName(uuid: $uuid, createdAt: ${createdAt.toIso8601String()}, '
    'contentLength: ${content.length})';
\`\`\`

- Identity / discriminator field first (`uuid`, foreign-key id, or sequence number)
- Structural metadata next (dates, enum names, counts, booleans)
- Lengths last, named `<field>Length` for free-text fields — never the field itself
- Never emit `Object` values, raw byte buffers, or `String` PII fields verbatim

### Test contract

Every PII-bearing class is paired with a `*_tostring_redaction_test.dart` file under
`test/unit/...` that:

1. Defines a sentinel string `__SENTINEL_CONTENT_DO_NOT_LEAK__` (this sentinel does
   not naturally appear in any redacted output, so the substring test is robust)
2. Constructs an instance with the sentinel placed in each PII field individually
   (one test per field, plus a kitchen-sink test with the sentinel in all PII fields
   simultaneously)
3. Asserts `instance.toString()` does NOT contain the sentinel
4. Asserts `instance.toString()` DOES contain expected structural metadata
   (the `uuid` or other id)

### When adding a new domain type

If the new type carries any user-entered free-text field (typed user prose, free-text
answers, names, notes, descriptions, custom choice text), you MUST:

1. Add a redacted `toString()` following the pattern above
2. Add a `*_tostring_redaction_test.dart` file following the same sentinel contract
3. Add the type to the inventory in
   `requirements_tasks/process/AI_rules/coding_standards/privacy_and_security/tasks/2026-05-10_impl_pii-tostring-redaction-and-tests/plans_and_protocols/2026-05-18_01_plan_pii_tostring_redaction.md`
   (this plan file) so future audits see the type was considered

A missed type is a logging-exposure bug — `toString()` is implicitly invoked by
`'$x'`, `print(x)`, `debugPrint('$x')`, and every IDE inspector. The structural
defense only works if every PII type participates.
```

---

## 5. File-Change List and Batch Grouping

All implementation work is in the **domain layer** (`lib/core/domain/` and one feature value-object). There is no data-layer or presentation-layer change — only domain type overrides + their unit tests + one doc edit. The ≤3-source-file-per-batch cap is applied; batches grouped to minimise re-running tests across unrelated areas.

### Batch A — Core entities (3 source files)
| Source file | Test file |
|-------------|-----------|
| `lib/core/domain/entities/contact.dart` | `test/unit/core/domain/entities/contact_tostring_redaction_test.dart` |
| `lib/core/domain/entities/plan_evaluation_input.dart` (two classes: `QuestionnaireEvaluationData`, `AnswerEntry` — same file) | `test/unit/core/domain/entities/plan_evaluation_input_tostring_redaction_test.dart` |
| `lib/features/therapist/data_transfer/domain/value_objects/transfer_chunk.dart` | `test/unit/features/therapist/data_transfer/domain/value_objects/transfer_chunk_tostring_redaction_test.dart` |

### Batch B — Questionnaire plan v2 (3 source files)
| Source file | Test file |
|-------------|-----------|
| `lib/core/domain/entities/questionnaire_plan_entities/questionnaire_plan.dart` | `test/unit/core/domain/entities/questionnaire_plan/questionnaire_plan_tostring_redaction_test.dart` |
| `lib/core/domain/entities/questionnaire_plan_entities/questionnaire.dart` | `test/unit/core/domain/entities/questionnaire_plan/questionnaire_tostring_redaction_test.dart` |
| `lib/core/domain/entities/questionnaire_plan_entities/question.dart` | `test/unit/core/domain/entities/questionnaire_plan/question_tostring_redaction_test.dart` |

### Batch C — Choice v2 + Plan v1 + Questionnaire v1 (3 source files)
| Source file | Test file |
|-------------|-----------|
| `lib/core/domain/entities/questionnaire_plan_entities/choice.dart` | `test/unit/core/domain/entities/questionnaire_plan/choice_tostring_redaction_test.dart` |
| `lib/core/domain/entities/questionnaire_plan_entities/v1/questionnaire_plan.dart` | `test/unit/core/domain/entities/questionnaire_plan/v1/questionnaire_plan_v1_tostring_redaction_test.dart` |
| `lib/core/domain/entities/questionnaire_plan_entities/v1/questionnaire.dart` | `test/unit/core/domain/entities/questionnaire_plan/v1/questionnaire_v1_tostring_redaction_test.dart` |

### Batch D — Question v1 + Choice v1 + doc note (2 source files + 1 doc)
| Source file | Test file |
|-------------|-----------|
| `lib/core/domain/entities/questionnaire_plan_entities/v1/question.dart` | `test/unit/core/domain/entities/questionnaire_plan/v1/question_v1_tostring_redaction_test.dart` |
| `lib/core/domain/entities/questionnaire_plan_entities/v1/choice.dart` | `test/unit/core/domain/entities/questionnaire_plan/v1/choice_v1_tostring_redaction_test.dart` |
| `doc/architecture/logging.md` (edit — append the new section from §4) | — |

**Total: 4 batches, 11 source files touched, 11 new test files created, 1 doc file edited.**

Order within each batch: edit source → add test → run `flutter test test/unit/core/domain/entities/...` for the batch's tests → fix any failure → proceed to next batch.

After all four batches: full unit-test run as the final verification (`flutter test test/unit`).

---

## 6. Risks and Edge Cases

1. **`Equatable.toString` baseline behaviour.** Several types extend `Equatable`. By default `Equatable.toString()` *does* emit the `props` list, which on most of our types includes only `uuid` and is therefore safe — but on `Contact` it returns `Contact(therapistId, name, encryptedTransferKey, createdAt, scannerTier)` (props includes `name` — a leak). And on `QuestionnaireEvaluationData` props includes `name`. So before the override is added, the baseline IS leaking. The override replaces this — explicitly re-tested by the sentinel.

2. **`stringify`-style mechanisms.** Equatable has a `stringify` getter that controls toString behaviour. After our override, that getter is moot for these types. No interaction with Freezed (none of the affected types use Freezed — confirmed by grep: no `*.freezed.dart` companions for these source files, only for presentation-layer events). **No partial-class explicit-override gymnastics needed.**

3. **Existing call sites that parse `toString()` output.** Grep on `.toString()` over `lib/` and `test/` should be done by the implementing agent before edit. Initial scan turned up no call site that parses the output of any of these 12 types' `toString()` — they are typically rendered for diagnostics or in test failure messages only. If a call site DOES parse output, it is a pre-existing fragility that we will surface.

4. **Test-fixture impact.** Some existing tests may have expectations like `expect(plan.toString(), contains('Plan A'))` (asserting the *old* leaky behaviour). Grep these out before editing — if found, replace with structural assertions (`contains('uuid:')`, `contains('nameLength: 6')`) and call out the change in the protocol.

5. **`AnswerEntry.value` is `Object`, not `String`.** The redaction strategy emits `value.runtimeType` and conditionally `(value as String).length`. The sentinel test must construct two cases: `value: sentinel` (String case) AND `value: 5` (int / Likert case). The int case asserts the toString contains `valueType: int` and that no integer-format-like leakage occurs. This is unusual enough to warrant a `/// Why:` comment.

6. **`TransferChunk.payload` is encrypted ciphertext** — not user content per se. The defensive redaction is still warranted because `Uint8List`'s default toString prints all bytes as a comma-separated decimal list, which is verbose and could correlate transfers. Worth a `/// Why:` comment explaining "defence-in-depth even though contents are encrypted".

7. **`Contact.name` is therapist/client display name** — clearly identifying-information PII per AC-05 (the requirement names "personal identifiers: user names, therapist names" as forbidden in logging). Confirmed in scope.

8. **JSON serialization is out of scope.** All `toJson` methods continue to include the user-content fields — that is *correct* because JSON is for persistence and QR transfer, not logging. The redaction is `toString()`-only. Verified.

9. **`Equatable.props` is unchanged.** Equality continues to use `props`. Only `toString` is overridden. No risk to `==` semantics or `hashCode`.

10. **WHY-comment hooks for the implementing agent.** Attach a `/// Why: ... Source: requirements_tasks/process/AI_rules/coding_standards/privacy_and_security/requirements.md#ac-05` comment on:
    - `AnswerEntry.toString()` — non-obvious because `value` is `Object`, not `String`; conditional-length disclosure rule needs explanation
    - `TransferChunk.toString()` — non-obvious because payload is already-encrypted; the reason for redacting anyway is defence-in-depth and reducing diagnostic-log noise
    - `Contact.toString()` — non-obvious because the previous Equatable default was leaking `name` via `props`; the comment should call out that this is the SP5 defence and that `name` MUST NOT appear in any future modification
    - Every other override (8 cases) is "obvious one-line redaction following a documented project convention" — no WHY comment required per CLAUDE.md §5

---

## 7. Acceptance-Criteria Mapping

From `goal.md`:

| Acceptance criterion | Deliverable |
|---|---|
| Every type identified as PII-bearing has an overridden `toString()` returning a redacted form. | §2 — 12 redacted toString overrides, one per inventoried type. §5 — batches A–D. |
| Each type has a unit test asserting the sentinel-content rule. | §3 — 11 new test files (10 covers 11 because `plan_evaluation_input` contains two types). |
| All redaction tests pass. | §5 — full `flutter test test/unit` after batch D. |
| `doc/testing/` (or `doc/architecture/logging.md`) documents the redaction convention so future types know to follow it. | §4 — new "Structural PII Redaction in Domain Types" section appended to `doc/architecture/logging.md`. |
| No existing code that calls `toString()` on these types is broken by the change. | §6 risk 3 + 4 — pre-edit grep over `.toString()` and string-interpolation call sites; replace any structural assertions in existing tests. |

From REQ-PROC-052:

| Requirement AC | Deliverable |
|---|---|
| AC-05 (PII redaction in `toString()`) | §2, §3, §4 (the structural defense) |
| AC-06 (logger calls never pass un-redacted domain instances) | This task lays the groundwork — once §2 lands, AC-06's runtime exposure surface is materially smaller. AC-06's lint / grep gate is a sibling task (TASK-PROC-052-04 if it exists; otherwise out of scope here per goal.md "Out of Scope"). |

---

## 8. Open Questions for the Implementing Agent

1. **Should `AnswerEntry.value`'s String case also include the runtimeType?** Recommendation: yes — `valueType: String, valueStringLength: 27` is more informative than just `valueStringLength: 27`. Plan reflects this.
2. **`Questionnaire.timeInterval.toString()` — does its current default leak anything?** `TimeInterval` only has enum + numeric fields per inspection, so the default is structural. But the override on `Questionnaire` interpolates only `timeInterval.type` (the enum), not the full object — safer and more readable in logs. If a future audit needs more detail, it can be added.
3. **Do we re-run all of `flutter test` or only `test/unit`?** Per `doc/testing/`, the unit folder is sufficient for this domain-only change; widget and integration tests do not exercise these `toString()`s. Plan says `flutter test test/unit` as the verification gate.

---

Agent ID: da9c38f6818df287
