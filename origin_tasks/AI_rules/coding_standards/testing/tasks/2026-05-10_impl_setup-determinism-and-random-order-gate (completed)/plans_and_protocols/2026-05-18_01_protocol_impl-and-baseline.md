---
date: 2026-05-18
session_id: d53af15a-43e6-420c-b7c7-81b54f706096
session_account: web
commit: 05b15097
type: protocol
---

# Protocol — TASK-PROC-002-03 implementation and baseline

## Deliverable

- **Script path** (stable): `scripts/quality/check_test_determinism.sh`
- **Exit codes**: `0` all runs passed · `1` any run failed · `2` invocation error
- **Phases**:
  1. one `flutter test --test-randomize-ordering-seed=<seed>` run with a locally generated 30-bit seed (printed and reproducible via `SEED=<n> scripts/quality/check_test_determinism.sh`)
  2. `${CONSECUTIVE:-10}` consecutive default-order `flutter test` runs
- **Logs**: one file per run under `${LOG_DIR:-/tmp/check_test_determinism}/`

The script is intentionally self-contained (no dependency on `_lib.sh` exclusions) because the gate scope is the whole `flutter test` suite, not a path-filtered subset.

## Why a shell script (not Python)

Both options were listed in the goal. Shell was chosen because:

- The script's only job is to invoke `flutter test` 11 times and aggregate exit codes — no parsing of structured input beyond grep over the per-run logs.
- The peer release-pre-flight gates in `scripts/quality/` (`check_no_debug_artifacts.sh`, `check_weak_crypto.sh`, `check_suppression_justification.sh`) are also shell. Matching their shape keeps the family coherent.
- Avoids pulling the script into the Python G1–G5 gate set (which would itself fail on a script that exists solely to invoke another long-running tool).

## Baseline — 2026-05-18 22:30Z @ 05b15097

Ran `scripts/quality/check_test_determinism.sh` once against `develop` head.

| Phase | Run | Result | Failing tests |
|---|---|---|---|
| 1   | random seed=803611806 | FAIL (-8) | 8 |
| 2   | 1/10 | FAIL (-8) | 8 |
| 2   | 2/10 | FAIL (-8) | 8 |
| 2   | 3/10 | FAIL (-8) | 8 |
| 2   | 4/10 | FAIL (-8) | 8 |
| 2   | 5/10 | FAIL (-8) | 8 |
| 2   | 6/10 | FAIL (-8) | 8 |
| 2   | 7/10 | FAIL (-8) | 8 |
| 2   | 8/10 | FAIL (-8) | 8 |
| 2   | 9/10 | FAIL (-8) | 8 |
| 2   | 10/10 | FAIL (-8) | 8 |

Per-run logs preserved at `/tmp/check_test_determinism/phase{1_random_seed_803611806,2_consec_NN}.log` for this session; not committed (transient build artifacts).

**Diagnosis**: identical 8-test set fails across all 11 runs and across the random-order run. This is **not a flake** — the failures are deterministic and order-independent. The current `develop` HEAD has a consistent, pre-existing test breakage in one file. Phase 2's job (detect non-determinism) found zero non-determinism; Phase 1's job (detect order dependence) found zero order dependence.

### Consistent-failure set (all 11 runs)

File: `test/unit/core/domain/services/questionnaire_plan/choice_service_test.dart`

1. `createChoice should return Left(CreateChoiceFailure) when choice creation fails`
2. `createChoice should return Right(void) when choice is created successfully`
3. `deleteChoice should return Left(ChoiceNotFoundFailure) when choice to delete is not found`
4. `deleteChoice should return Left(DeleteChoiceFailure) when choice deletion fails`
5. `deleteChoice should return Right(void) when choice is deleted successfully`
6. `updateChoice should return Left(ChoiceNotFoundFailure) when choice to update is not found`
7. `updateChoice should return Left(UpdateChoiceFailure) when choice update fails`
8. `updateChoice should return Right(void) when choice is updated successfully`

The Expected/Actual excerpts indicate a `Right<Failure,Unit>` vs `Left<Failure,Unit>` mismatch in every case — the service has changed contract or the mock setup is no longer aligned with the implementation. The whole file's `Either<Failure, Unit>` matcher set has the same shape, suggesting a single-cause regression rather than eight independent bugs.

### No flakes detected

A flake would manifest as a test that fails in some of the 11 runs but not others. Across `phase2_consec_01..10.log` the failing-name set is **identical** in every run (same 8 names, same 8 counts), and `phase1_random_seed_803611806.log` also shows the same 8 — so:

- **TQ4 independence**: PASS — random ordering changed nothing.
- **TQ4 determinism**: PASS for behaviour (same set every run), FAIL for AC-04 (the 8 failures persist).

### Recommended next steps

Remediation is **out of scope** for TASK-PROC-002-03 (the goal explicitly excludes fixing existing flakes). Two items follow:

1. **Open a bugfix task** targeting `choice_service_test.dart` — the failures are deterministic so the fix is mechanical: align mocks with the current `ChoiceService` contract, or restore the contract if a recent change broke it inadvertently. Investigation should begin with `git log -p lib/core/domain/services/questionnaire_plan/choice_service.dart` and the matching test file.
2. **Until the bugfix lands, AC-04 cannot be marked satisfied** at the release-pre-flight level. The gate script itself is complete and correct; the suite-side precondition is not. TASK-PROC-046-06 (which wires gates into the pre-flight checklist) should reference `check_test_determinism.sh` and accept that the first release attempt will block on this.

## Release pre-flight wiring

Per the goal's "Out of Scope" and the cross-reference to TASK-PROC-046-06, this task does NOT modify CLAUDE.md or any pre-flight orchestrator. The contract is solely:

- Script path is stable at `scripts/quality/check_test_determinism.sh`.
- Exit codes follow the project-wide gate convention (`0`/`1`/`2`).
- TASK-PROC-046-06 will reference the path; nothing here will move.

## Acceptance criteria — status

- [x] The determinism + random-order script exists, runs successfully, and produces a clear pass/fail output with seed information on failure.
- [x] Baseline output is recorded in `plans_and_protocols/` (this file).
- [x] Failing tests listed with a recommended next step (consistent failures, not flakes; bugfix recommended for `choice_service_test.dart`).
- [x] The script's path is stable and noted in the protocol (`scripts/quality/check_test_determinism.sh`).
