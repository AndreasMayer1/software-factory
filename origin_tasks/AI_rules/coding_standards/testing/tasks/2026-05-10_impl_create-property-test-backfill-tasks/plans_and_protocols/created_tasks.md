# Created tasks from TASK-PROC-002-05

Date: 2026-05-18

Source inventory: `requirements_tasks/process/AI_rules/coding_standards/testing/tasks/2026-05-10_analyze_inventory-value-objects-needing-property-tests (completed)/plans_and_protocols/value_objects_inventory.md`

## Allocated task IDs

| Task ID | Slug | Effort | Cluster | One-line description |
|---|---|---|---|---|
| TASK-PROC-002-10 | `property-test-likert-options` | S | C1 | Property test for `LikertOptions`: bounded range `[2,10]` + JSON round-trip + boundary rejection. |
| TASK-PROC-002-11 | `property-test-contact` | S | C1 | Property test for `Contact`: `scannerTier` range `[1,3]` + non-empty `therapistId`/`name`. |
| TASK-PROC-002-12 | `property-test-pairing-identity` | S | C1 | Property test for `PairingIdentity`: non-empty UUID + Equatable identity. |
| TASK-PROC-002-13 | `property-test-choice` | S | C1 | Property test for `Choice`: non-empty `text`/`questionUuid` + JSON round-trip. |
| TASK-PROC-002-14 | `property-test-scanner-tier-parameters` | M | C1 | Property test for `ScannerTierParameters`: positive-int field asserts + `forTier` totality. |
| TASK-PROC-002-15 | `property-test-transfer-chunk` | M | C1 | Property test for `TransferChunk`: uint16 header range + `fromBytes(toBytes(x)) == x` + `fromBase64QrString(toBase64QrString(x)) == x`. |
| TASK-PROC-002-16 | `property-test-scanner-hardware-tier` | S | C1 | Property test for `ScannerHardwareTier`: enum totality + `pairingTierCode` mapping invariant. |
| TASK-PROC-002-17 | `property-test-enum-totality-batch` | S | C2 | Property test batch covering totality + round-trip for 7 enums: `QuestionType`, `TimeInputType`, `TimeIntervalType`, `TimeLabelType`, `TransferChannel`, `ScopeVariant`, `TransferDetectionZone`. |
| TASK-PROC-002-18 | `codify-and-property-test-time-interval` | L | implicit | Codify `TimeInterval` invariants (weekdays range, duration non-negative, per-type field-presence) THEN add property test for type totality + JSON round-trip. |
| TASK-PROC-002-19 | `codify-and-property-test-time-options` | M | implicit | Codify `(timeInputType, timeLabels)` valid combinations in `TimeOptions` THEN add property test for JSON round-trip + list preservation. |
| TASK-PROC-002-20 | `codify-and-property-test-question` | L | implicit | Codify per-`QuestionType` invariant matrix in `Question.create` THEN add property test for type-switch totality + JSON round-trip per variant. |
| TASK-PROC-002-21 | `codify-and-property-test-questionnaire` | L | implicit | Codify `Questionnaire` invariants (`questionUuids` empty acceptability, `shortLabel` length cap) THEN add property test for non-empty fields + JSON round-trip + `BuiltList` preservation. |
| TASK-PROC-002-22 | `codify-and-property-test-questionnaire-plan` | L | implicit | Align `QuestionnairePlan` `create`/`fromJson` invariants + enforce `endDate >= startDate` THEN add property test for ordering + JSON round-trip + list preservation. |
| TASK-PROC-002-23 | `property-test-choice-options` | M | C3 | Property test for `ChoiceOptions`: non-empty `choicesUuids` + JSON round-trip + `copyWith` identity law. |
| TASK-PROC-002-24 | `property-test-transfer-bundle-assemble` | L | C3 | Property test for `TransferBundle.assemble`: private-entry idempotence-of-filter + scope-variant monotonicity + duplicate-free output + QR-channel rejection. |

## Batching rationale

Per the inventory's Recommendation, the 17 qualifying types group into three coherent clusters. Cluster 1 (bounded numeric / simple round-trip, 7 types) is split one task per type because each test is independent and short. Cluster 2 (7 enums) is collapsed into a single batched task because one parameterised property test file per enum is overkill — they all use the same `any.oneOf(EnumName.values)` pattern. Cluster 3 (aggregate algebraic-laws) is partially absorbed into the implicit-invariant tasks (Question, Questionnaire, QuestionnairePlan, TimeInterval, TimeOptions are implicit-invariant *and* in cluster 3); only `ChoiceOptions` and `TransferBundle.assemble` remain as standalone cluster-3 tasks.

## Implicit-invariant tasks (higher effort)

Tasks 18–22 are flagged separately because the property test cannot be written until the underlying invariant is codified in source. Per the inventory: "writing a property test against an unwritten invariant is worse than writing no property test, because it cements the current accidental behaviour as the contract." Each of these tasks carries an extra acceptance criterion: invariant codification must land before the property test is written.

## Marginal entries not promoted

Per inventory, `OwnershipContext` and `TrackingEntry` have comprehensive example coverage already and are not promoted to property-test tasks. This omission is deliberate; revisit only if the example tests stop reflecting the contract or if cluster (1) backfills find Glados configuration cheap enough that adding them is near-free.

## Inventory had gaps?

Yes — 17 qualifying types, 15 tasks created (5 implicit-invariant L/M + 10 vanilla S/M/L; cluster-2 enums batched into a single S task). 2 marginal entries omitted deliberately. Zero-gap edge case is therefore not triggered.

## Dependency wiring

All 15 created tasks set `after: [TASK-PROC-002-02, TASK-PROC-002-04]` per this task's goal.md scope. Both predecessors are `completed`, so all 15 are immediately ready to be picked up by `next_tasks.py`.
