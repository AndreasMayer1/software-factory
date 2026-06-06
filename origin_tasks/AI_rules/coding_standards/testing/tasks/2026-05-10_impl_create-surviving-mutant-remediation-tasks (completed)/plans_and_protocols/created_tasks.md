# Created tasks — TASK-PROC-002-06

Date: 2026-05-23

## Full mutation baseline (the input this task acted on)

Run: `dart run mutation_test test/mutation/critical_paths_config.xml
--coverage coverage/lcov.info --output build/mutation-report --format all`
(after `flutter test --coverage` on a green suite). Elapsed 0:34:54.

- 34 mutations across the 6 critical-path files
- **33 killed, 1 survived** → 97.06 % kill rate, quality rating **A**
  (well above the REQ-PROC-002 AC-02 ≥ 80 % threshold)
- 0 timeouts, 0 not-covered-by-tests

Per-file survivor breakdown (only one file had a survivor):

| File | Mutations | Survivors |
|---|---:|---:|
| plan_migration_service.dart | 1 | 0 |
| serialization_utils.dart | 1 | 0 |
| plan_transfer_pipeline.dart | 28 | **1** |
| plan_serialization_service.dart | 4 | 0 |
| plan_import_service.dart | 0 | 0 |
| transfer_chunk.dart | 0 | 0 |

`plan_import_service.dart` and `transfer_chunk.dart` produced 0 mutations under
the built-in operator set (byte-array / `Uint8List` heavy code the regex rules
don't match) — unchanged from the TASK-PROC-002-02 dry-run. Noted as a possible
future `<rules>` extension; not in scope here.

## Surviving-mutant clusters → classification

One survivor; one cluster.

| Cluster | File:line | Category | Classification | Outcome |
|---|---|---|---|---|
| Random sequence_id range | plan_transfer_pipeline.dart:66 | arithmetic `+`→`-` | remediation-needed (not benign — narrows AC-04 uint16 range) | task created + register row SM-001 |

## Created remediation tasks

| Task ID | Path | One-line description |
|---|---|---|
| TASK-FUNC-007-03-05 | requirements_tasks/functional/shared/epic_data_transfer/feat_plan_serialization/tasks/2026-05-23_impl_kill-sequence-id-range-mutant/ | Strengthen `plan_transfer_pipeline_test.dart` to assert the random `sequence_id` upper bound is the full uint16 range, killing the line-66 `+`→`-` mutant. |

## Register updates

- `doc/testing/surviving_mutants.md`: added row **SM-001** (status `tracked`,
  follow_up `TASK-FUNC-007-03-05`).

## Benign mutants recorded

None. The single survivor is remediation-needed, not benign.
