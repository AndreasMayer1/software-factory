# Plan: Create property-test backfill tasks from value-objects inventory

Task: TASK-PROC-002-05
Date: 2026-05-18
Approach: inline (no subagent)

## Source

`requirements_tasks/process/AI_rules/coding_standards/testing/tasks/2026-05-10_analyze_inventory-value-objects-needing-property-tests (completed)/plans_and_protocols/value_objects_inventory.md`

Inventory lists 17 qualifying types (4 marginal entries deferred), grouped into three clusters plus 5 implicit-invariant types that need codification before property tests.

## Batching decision

The inventory's recommendation is followed: one task per type for clusters 1 and 3, one batched task for the cluster-2 enum totality work, and one task per implicit-invariant type (each "codify + add property tests"). This gives 15 tasks under REQ-PROC-002 (next free IDs start at TASK-PROC-002-10).

## Mapping

All 15 tasks live under the requirement that mandates them — `requirements_tasks/process/AI_rules/coding_standards/testing/` (REQ-PROC-002) — because backfilling property tests is a testing-process deliverable, not a feature change. They share `parent_requirement: REQ-PROC-002`, `covers.acceptance_criteria: [AC-03]`. The implicit-invariant tasks additionally touch domain entity code (`lib/core/domain/entities/questionnaire_plan_entities/`) but their requirement-of-record remains REQ-PROC-002 since the codification is in service of property-test coverage.

## Created tasks

| # | Task name | Effort | Cluster | Type generators |
|---|---|---|---|---|
| 1 | impl_property-test-likert-options | S | C1 | `any.intInRange(2,10)` |
| 2 | impl_property-test-contact | S | C1 | `any.intInRange(1,3)`, `any.nonEmptyString` |
| 3 | impl_property-test-pairing-identity | S | C1 | `any.nonEmptyString` |
| 4 | impl_property-test-choice | S | C1 | `any.nonEmptyString` |
| 5 | impl_property-test-scanner-tier-parameters | M | C1 | `any.positiveInt` |
| 6 | impl_property-test-transfer-chunk | M | C1 | `any.intInRange(0,65535)`, byte-list generator |
| 7 | impl_property-test-scanner-hardware-tier | S | C1 | `any.oneOf` over enum |
| 8 | impl_property-test-enum-totality-batch | S | C2 | `any.oneOf` (7 enums) |
| 9 | impl_codify-and-property-test-time-interval | L | implicit | various |
| 10 | impl_codify-and-property-test-time-options | M | implicit | various |
| 11 | impl_codify-and-property-test-question | L | implicit | `any.combine` |
| 12 | impl_codify-and-property-test-questionnaire | L | implicit | `any.list(any.nonEmptyString)` |
| 13 | impl_codify-and-property-test-questionnaire-plan | L | implicit | various |
| 14 | impl_property-test-choice-options | M | C3 | `any.list(any.nonEmptyString)` |
| 15 | impl_property-test-transfer-bundle-assemble | L | C3 | custom (entry-set + scope-variant) |

## Dependencies

All 15 tasks set `after: [TASK-PROC-002-02, TASK-PROC-002-04]` per goal.md scope. TASK-PROC-002-02 has landed (glados installed); TASK-PROC-002-04 has landed (inventory). The implicit-invariant tasks (9–13) and TransferBundle (15) have implicit dependencies on the corresponding type's existence in `lib/` — recorded in their goal.md Notes, not in `after:`.

## Marginal entries

The two marginal entries from the inventory (`OwnershipContext`, `TrackingEntry`) are not promoted to tasks. The inventory explicitly classifies them as "comprehensive example coverage already exists" — adding property tests would be coverage padding without strengthening the verification. Recorded here as a deliberate omission, not an oversight.

## Output artifacts

- 15 task folders under `requirements_tasks/process/AI_rules/coding_standards/testing/tasks/`
- `plans_and_protocols/created_tasks.md` with the list of allocated IDs and one-line descriptions
- This plan file
