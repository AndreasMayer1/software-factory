# Baseline Coverage — TASK-PROC-046-04

Date: 2026-05-16  
Agent: main session  
lcov produced by: `flutter test --coverage` (all unit tests, full suite)

## Gate result: PASS (91.6% ≥ 90.0%)

```
scripts/quality/check_critical_path_coverage.py --no-run
```

## Per-category results

### 1. Encryption / decryption — DORMANT (0/0)
Not yet implemented. Gate contribution: zero.

### 2. Argon2id key derivation — DORMANT (0/0)
Not yet implemented. Gate contribution: zero.

### 3. Atomic file rotation — DORMANT (0/0)
Not yet implemented. Gate contribution: zero.

### 4. Version migration — 96.6% (28/29 lines)

| File | Hit | Total | % |
|------|-----|-------|---|
| lib/core/domain/services/questionnaire_plan/plan_migration_service.dart | 11 | 11 | 100.0% |
| lib/core/domain/services/questionnaire_plan/serialization_utils.dart | 17 | 18 | 94.4% |

One uncovered line in serialization_utils.dart. The file has 18 executable lines
and 17 are hit. The missing line is likely a branch edge in the `switch` default
case (UnsupportedDataVersionFailure) or the outer `catch`. Coverage is 94.4% —
well above the 90% threshold.

### 5. Data-transfer serialization pipeline — 90.6% (125/138 lines)

| File | Hit | Total | % |
|------|-----|-------|---|
| lib/features/therapist/data_transfer/domain/services/plan_transfer_pipeline.dart | 83 | 96 | 86.5% |
| lib/features/therapist/data_transfer/data/services/plan_serialization_service.dart | 5 | 5 | 100.0% |
| lib/features/therapist/data_transfer/data/services/plan_import_service.dart | 12 | 12 | 100.0% |
| lib/features/therapist/data_transfer/domain/value_objects/transfer_chunk.dart | 25 | 25 | 100.0% |

`plan_transfer_pipeline.dart` is the **at-risk file**: 86.5% per-file (83/96),
which pulls the category to 90.6% only because the other three files are at
100%. The category passes the 90% threshold by 0.6 percentage points (1
line). This file is the canonical transfer codec and deserves attention.

13 uncovered lines in plan_transfer_pipeline.dart. These are likely error/edge
paths in the chunk reassembly and sequence-validation logic. The gate still
passes because the category threshold is applied at the aggregate level, but
this file should be prioritised for test coverage improvement.

## Overall: 91.6% (153/167 lines across implemented categories)

**Gate: PASS** — no remediation tasks required.

## Risk note

`plan_transfer_pipeline.dart` at 86.5% per-file is within 3.5 points of the
per-file floor one might expect. If new executable lines are added without
accompanying tests, the category could drop below 90%. Recommended: bring this
file to ≥ 90% per-file in the next testing task (TASK-PROC-002-02 or a
dedicated coverage task).

## Script invocation (for TASK-PROC-046-06 CLAUDE.md reference)

```bash
# Evaluate against a fresh test run:
python3 scripts/quality/check_critical_path_coverage.py

# Evaluate against an existing lcov.info (skip re-running tests):
python3 scripts/quality/check_critical_path_coverage.py --no-run
# or:
python3 scripts/quality/check_critical_path_coverage.py --lcov coverage/lcov.info

# Custom doc path:
python3 scripts/quality/check_critical_path_coverage.py --doc doc/testing/critical_paths.md
```

Script location: `scripts/quality/check_critical_path_coverage.py`  
Path doc: `doc/testing/critical_paths.md`  
Exit codes: 0 = pass, 1 = fail, 2 = invocation error
