# Value Object & Entity Inventory for AC-03 Property-Test Coverage

Task: TASK-PROC-002-04
Requirement: REQ-PROC-002 AC-03
Date: 2026-05-16

## Summary

- Total domain types inspected: 36 (current versions only; v1 mirrors excluded — see "v1 versioned mirrors" section)
- Types requiring property tests (>=1 category matches): 17
- Types with zero matches (out of scope for AC-03): 19
- Types with implicit/undocumented invariants flagged: 5
- Existing `Glados<T>` property tests in `test/unit/`: 0 (confirmed by `grep -r "Glados\|glados" test/`)
- Total backfill effort: 8 x S + 6 x M + 3 x L. Estimated wall-time at the upper bound: ~10–12 h of focused work. **Recommendation: split into three sub-tasks** (see Recommendation below).

## Recommendation

The 17 qualifying types fall into three coherent clusters that are best executed as three follow-up `impl` sub-tasks. (1) **Bounded-numeric + simple round-trip cluster** (8 x S): `LikertOptions`, `Contact`, `PairingIdentity`, `Choice`, `ScannerTierParameters`, `TransferChunk` (header invariants), `TransferDetectionSnapshot`, `ScannerHardwareTier`. Generators are trivial (`any.intInRange`, `any.nonEmptyString`); each test is < 30 min. (2) **Enum totality cluster** (4 x S, can collapse into 1 file): `QuestionType`, `TimeInputType`, `TimeIntervalType`, `TimeLabelType`, `TransferChannel`, `ScopeVariant`, `TransferDetectionZone` — one parameterised property test per enum proves both encode/decode round-trip and unknown-variant rejection. (3) **Aggregate algebraic-laws cluster** (3 x L + 2 x M): `QuestionnairePlan`, `Questionnaire`, `Question`, `TimeInterval`, `TimeOptions`, `ChoiceOptions`, `TransferBundle.assemble`. These need custom generators (nested `BuiltList<String>`, valid `QuestionType` + matching options pair, scope-variant + entry-set combinations) and verify multi-field invariants. Splitting these into clusters lets a single back-pressure cycle stay within reasonable scope per cycle.

If a single task is required, group by cluster within the task to keep cognitive load manageable.

## Inventory

| Type | Path | Kind | Categories | Existing tests | Gap | Effort |
|---|---|---|---|---|---|---|
| `LikertOptions` | `lib/core/domain/entities/questionnaire_plan_entities/likert_options.dart` | VO | a, e | `test/unit/core/domain/entities/questionnaire_plan/likert_options_test.dart` (example-based; no Glados) | bounded range [2,10] + JSON round-trip + boundary rejection | S |
| `Contact` | `lib/core/domain/entities/contact.dart` | Entity | a, c | `test/unit/core/domain/entities/contact_test.dart` | `scannerTier` in [1,3] + non-empty `therapistId`/`name` constraints | S |
| `PairingIdentity` | `lib/core/domain/entities/pairing_identity.dart` | VO | c | `test/unit/core/domain/entities/pairing_identity_test.dart` | non-empty uuid invariant; also Equatable identity property | S |
| `Choice` | `lib/core/domain/entities/questionnaire_plan_entities/choice.dart` | Entity | c, e | `test/unit/core/domain/entities/questionnaire_plan/choice_test.dart` | non-empty `text`/`questionUuid` + JSON round-trip (note: `toJson` includes `dataVersion`, may need round-trip caveat) | S |
| `QuestionType` | `lib/core/domain/entities/questionnaire_plan_entities/question_type.dart` | Enum + JSON converter | b, e | none directly (exercised indirectly via `question_json_test.dart`) | totality: all 7 variants round-trip; unknown JSON throws | S |
| `TimeInputType` | `lib/core/domain/entities/questionnaire_plan_entities/time_input_type.dart` | Enum + JSON converter | b, e | `test/unit/core/domain/entities/questionnaire_plan/time_input_type_test.dart` | totality + unknown rejection | S |
| `TimeIntervalType` | `lib/core/domain/entities/questionnaire_plan_entities/time_interval_type.dart` | Enum + JSON converter | b, e | `test/unit/core/domain/entities/questionnaire_plan/time_interval_type_test.dart` | totality + null/unknown rejection | S |
| `TimeLabelType` | `lib/core/domain/entities/questionnaire_plan_entities/time_label_type.dart` | Enum + JSON converter | b, e | `test/unit/core/domain/entities/questionnaire_plan/time_label_type_test.dart` | totality + unknown rejection | S |
| `TransferChannel` | `lib/features/therapist/data_transfer/domain/entities/tracking_entry_entities/transfer_bundle.dart` (actually `lib/core/...`) | Enum | b | none directly | totality (only 2 variants — trivial, fold into bundle test) | S |
| `ScopeVariant` | `lib/core/domain/entities/tracking_entry_entities/transfer_bundle.dart` | Enum | b | exercised via `transfer_bundle_test.dart` | totality — every variant must produce a defined assemble output | S |
| `TransferDetectionZone` | `lib/features/therapist/data_transfer/domain/value_objects/transfer_detection_zone.dart` | Enum | b | none directly (exercised via model tests) | totality — all 5 zones must be reachable / classifiable | S |
| `ScannerHardwareTier` | `lib/features/therapist/data_transfer/domain/value_objects/scanner_hardware_tier.dart` | Enum | b, d? | `test/unit/features/therapist/data_transfer/domain/value_objects/scanner_hardware_tier_test.dart` | totality + `pairingTierCode` total mapping (only values 2/3 emitted — invariant) | S |
| `ScannerTierParameters` | `lib/features/therapist/data_transfer/domain/value_objects/scanner_tier_parameters.dart` | VO | a | `test/unit/features/therapist/data_transfer/domain/value_objects/scanner_tier_parameters_test.dart` | positive-int asserts on `chunkSizeBytes`/`displayFpsTarget`/`scanIntervalMs`; `forTier` totality (3 enum -> defined params) | M |
| `TransferChunk` | `lib/features/therapist/data_transfer/domain/value_objects/transfer_chunk.dart` | VO | a, c, e | `test/unit/features/therapist/data_transfer/domain/value_objects/transfer_chunk_test.dart` | header uint16 range invariants (0..65535), payload length, **`fromBytes(toBytes(x)) == x`**, **`fromBase64QrString(toBase64QrString(x)) == x`** | M |
| `TimeInterval` | `lib/core/domain/entities/questionnaire_plan_entities/time_interval.dart` | VO | b, e | `time_interval_test.dart`, `time_interval_json_test.dart`, `time_interval_from_v1_test.dart` | JSON round-trip across all `TimeIntervalType` variants + `TimeOfDay` h/m bounds + weekday-list value bounds | M |
| `TimeOptions` | `lib/core/domain/entities/questionnaire_plan_entities/time_options.dart` | VO | e, f | `time_options_json_test.dart`, `time_options_constructor_test.dart` | JSON round-trip; `timeLabels` list preservation (algebraic: identity, length preserved across encode/decode) | M |
| `ChoiceOptions` | `lib/core/domain/entities/questionnaire_plan_entities/choice_options.dart` | VO | c, e, f | `choice_options_test.dart` | non-empty `choicesUuids` invariant + JSON round-trip + `copyWith` identity law | M |
| `Question` | `lib/core/domain/entities/questionnaire_plan_entities/question.dart` | Entity | b, c, e | `question_test.dart`, `question_create_test.dart`, `question_json_test.dart` | (b) `QuestionType`-switch totality on `create` / `fromJson`: each variant either accepts a required nested options or throws a typed exception; (c) non-empty fields; (e) JSON round-trip per variant | L |
| `Questionnaire` | `lib/core/domain/entities/questionnaire_plan_entities/questionnaire.dart` | Aggregate | c, e, f | `questionnaire_*_test.dart` family | non-empty name/description; JSON round-trip; `BuiltList<String>` questionUuids preservation across copyWith/round-trip (algebraic) | L |
| `QuestionnairePlan` | `lib/core/domain/entities/questionnaire_plan_entities/questionnaire_plan.dart` | Aggregate | c, e, f | `questionnaire_plan_*_test.dart` family | non-empty name; `endDate >= startDate` invariant; JSON round-trip; questionnaireUuids list preservation | L |
| `TransferBundle` | `lib/core/domain/entities/tracking_entry_entities/transfer_bundle.dart` | Aggregate (computation output VO) | f | `transfer_bundle_test.dart` (AC-02, scope variants) | (f) algebraic invariants on `assemble`: (1) `assemble(... isPrivate=true ...).entryRefs` is always empty for private entries regardless of `ScopeVariant` (idempotence-of-filter); (2) `defaultScope.entryRefs subset of widened.entryRefs subset of all-candidate-uuids` (monotonicity); (3) `entryRefs` is duplicate-free given duplicate-free input; (4) QR-channel rejection invariant: any non-empty `voiceRecordingRefs` with `TransferChannel.qr` always throws | L |

## Types out of scope (no AC-03 category matches)

- `AppRole` (`lib/core/domain/entities/app_role.dart`): closed set of 2 string values with an `ArgumentError` on unknown — already exhaustively testable by example; only 2 input values means a property test adds no coverage over the existing example. (Trivially borderline (b), but excluded as the input space is finite-size-2.)
- `ActionGroup` (`lib/core/domain/entities/action_group.dart`): immutable container, no validation, no serialization. Property tests would assert structural invariants of a `List<ActionItem>` it does not own.
- `ActionItem` (`lib/core/domain/entities/action_item.dart`): mixed invariants enforced by `assert` (action-type/route consistency), but the class holds `IconData` and `VoidCallback` — non-serializable, non-`Comparable`. The `assert` constraint is fully covered by the 4 enum-driven combinations in the existing widget tests; property testing yields no benefit over enumeration.
- `ActionType` (`lib/core/domain/entities/action_type.dart`): pure enum with 3 variants and no serialization. Trivially total — example tests suffice.
- `AnswerEntry` / `QuestionnaireEvaluationData` / `PlanEvaluationInput` (`lib/core/domain/entities/plan_evaluation_input.dart`): presentation-input DTOs; no validation, no serialization, no aggregate operations of their own. Equality-via-`props` is covered by an existing test.
- `version_constants.dart` (both current and v1): a single `const int` value. Not a type.
- `OwnershipContext` sealed hierarchy (`lib/core/domain/entities/tracking_entry_entities/ownership_context.dart`): the type *does* satisfy (b) enum totality (sealed = closed) and (e) round-trip — but tests for both are already comprehensive via examples in `ownership_context_test.dart`. **Marginal**: a property test for `fromJson(toJson(x)) == x` across the two variants would be cheap (S). Re-classify as in-scope if backfilling cluster (2) — listed in Notes for backfill author.
- `TrackingEntry` (`lib/core/domain/entities/tracking_entry_entities/tracking_entry.dart`): has (e) round-trip + (c) non-empty uuid, **but** the round-trip property is already exercised exhaustively in `tracking_entry_test.dart` and the field count is small enough that example tests are stronger than a Glados generator (each field is independently meaningful). **Marginal**: include in cluster (1) if a comprehensive `fromJson(toJson(x)) == x` Glados test is desired; otherwise the existing examples cover the invariant adequately.
- Exception classes in `exceptions.dart`, `failures.dart`, and all `*_failures.dart`: typed exceptions/failures with constant or single-string-message constructors. No invariants beyond `message` field equality. Out of scope.
- `SchemaVersionFailure` (`lib/features/therapist/data_transfer/domain/failures/transfer_failures.dart`): single `version: int` field; no documented bound (any int accepted at construction — the rejection logic is at the caller's site). Out of scope by itself.

## Implicit invariants — needs codification first

These types have invariants that *should* be enforced by the constructor / factory but are currently undocumented or only partially enforced. Codify before writing the property test, otherwise the property test will codify whatever the current implementation happens to do.

- `TimeInterval` (`lib/core/domain/entities/questionnaire_plan_entities/time_interval.dart`): no factory validation. `weekdays` is `List<int>?` with no value-range check (ISO 1..7? 0..6? duplicates allowed?). `interval` is `Duration?` with no non-negative check. `userDefinedIdentifier` empty-string acceptability is unspecified. Per-`type` field-presence invariants (e.g. `SpecificTime` requires `startTime`) are undocumented in code. **Action: codify the invariants in `time_interval.dart` doc-comment + `factory TimeInterval.create` validators before the L-effort property test, or the property test will encode "anything goes".**
- `TimeOptions` (`lib/core/domain/entities/questionnaire_plan_entities/time_options.dart`): no constructor validation. Combinations of `(timeInputType, timeLabels)` that are nonsensical (e.g. `None` + non-empty `timeLabels`) are silently accepted. **Action: codify allowed combinations.**
- `Questionnaire` (`lib/core/domain/entities/questionnaire_plan_entities/questionnaire.dart`): the commented-out `questionUuids.isEmpty` guard in `create` is suspicious — invariant unclear. `shortLabel` length cap (~12 chars per WHY comment) is documented in prose but not enforced. **Action: decide whether empty `questionUuids` is valid and whether `shortLabel` has a hard cap, then either enforce or document the absence of the constraint.**
- `QuestionnairePlan` (`lib/core/domain/entities/questionnaire_plan_entities/questionnaire_plan.dart`): same pattern — `questionnaireUuids.isEmpty` guard commented out in `create` but enforced in `fromJson`. Inconsistent invariant between construction paths. **Action: align `create` and `fromJson` invariants.**
- `Question` (`lib/core/domain/entities/questionnaire_plan_entities/question.dart`): the per-`QuestionType` branch logic in `create` contains a dead-code condition (`if (choiceOptions == null && timeOptions == null && likertOptions == null && timeInputType == null)` after positive checks have already returned). The actual invariant matrix needs to be documented before a property test enumerates it across all 7 `QuestionType` variants. **Action: rewrite the `create` validation as an explicit invariant table.**

## v1 versioned mirrors

The `lib/core/domain/entities/questionnaire_plan_entities/v1/` folder mirrors the current entities as a frozen v1 wire format. Classifications apply identically to the v1 mirrors (confirmed by spot-check: v1 `LikertOptions.create` carries the same `[2,10]` bound as the current version). Property tests for v1 would be useful **only** if a future migration changes the v2 invariants — at which point the v1 `fromJson` must still accept legacy data. For now the v1 mirrors are exercised by example via the `*_from_v1_test.dart` family, which is sufficient to lock the wire format. Re-evaluate when the v3 schema lands.

## Notes for the backfill author

- TASK-PROC-002-02 (Glados install) is a precursor to writing the actual `Glados<T>` tests but not to this inventory. Confirmed zero `Glados`/`glados` references currently exist in `test/`.
- Conventional unit tests already exercise some invariants by example (e.g. `*_json_test.dart`, `*_test.dart` families under `test/unit/core/domain/entities/questionnaire_plan/`). **Property tests strengthen them by spanning the input space, not replacing the example tests.** Keep the example tests.
- Generators required (non-trivial):
  - `any.intInRange(2, 10)` for `LikertOptions`
  - `any.intInRange(1, 3)` for `Contact.scannerTier`
  - `any.intInRange(0, 65535)` for `TransferChunk` header fields; a `Uint8List` generator via `any.list(any.intInRange(0,255)).map(Uint8List.fromList)` for payload
  - `any.combine` for `(QuestionType, matching-options)` pair generator in `Question`
  - `any.list(any.nonEmptyString)` for `BuiltList<String>` aggregate fields
  - `any.oneOf` over enum value lists for enum-totality tests
- The two **marginal** entries (`OwnershipContext`, `TrackingEntry`) above can be added to cluster (1) cheaply if Glados is already configured for that cluster — they raise the qualifying count to 19 with minimal extra effort.
- The five **Implicit invariants** entries are blockers: writing a property test against an unwritten invariant is worse than writing no property test, because it cements the current accidental behaviour as the contract. Treat invariant codification as a sibling task (likely `requ-explore` against REQ-PROC-002 or a domain refactor task) that must complete before cluster (3) starts.
- `TransferChunk` round-trip is the highest-value property in the inventory: it crosses a wire format boundary (base64url over QR), exactly the kind of cross-encoding pair where example tests miss subtle byte-level regressions.
