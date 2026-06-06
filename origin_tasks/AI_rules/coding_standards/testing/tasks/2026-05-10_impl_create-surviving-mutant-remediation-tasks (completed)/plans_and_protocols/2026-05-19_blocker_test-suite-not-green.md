# Blocker: Test suite must be green before mutation baseline run

Task: TASK-PROC-002-06
Date: 2026-05-19
Author: claude (automated, session 9eccf6e7-bd30-4b4a-a8b0-39a177877a6e)
Plan it blocks: 2026-05-18_01_plan.md §"Strategy" step 1

## Finding

Per `2026-05-18_01_plan.md`, this task must produce the full mutation baseline
(`dart run mutation_test test/mutation/critical_paths_config.xml --coverage …`)
before any survivor classification is possible. Mutation testing requires a
green baseline: every mutation runs `flutter test` and is "detected" when the
suite returns non-zero.

`flutter test` on develop @ HEAD is not green:

- Elapsed: ~66 s
- Result: `Some tests failed.` (exit 1)
- Counts on final line: `+1182 ~2 -8` — 8 failing tests, 2 skipped

Failing test files (deduplicated from the run log at `/tmp/flutter_test_full.log`):

| Test file | Notes |
|---|---|
| `test/unit/core/data/models/pairing_qr_payload_test.dart` | `ArgumentError`-empty-input cases |
| `test/unit/core/design_system/molecules/error_display_test.dart` | Multiple ErrorDisplay cases (semantics, retry button, icons) |
| `test/unit/core/domain/entities/pairing_identity_test.dart` | `PairingIdentity` empty uuid `ArgumentError` |
| `test/unit/core/domain/entities/questionnaire_plan/likert_options_test.dart` | `LikertOptions.fromJson` invalid type |
| `test/unit/core/domain/entities/questionnaire_plan/questionnaire_plan_json_test.dart` | `ArgumentError` for missing field |
| `test/unit/core/domain/entities/questionnaire_plan/question_json_test.dart` | Invalid `questionType`, nested `TimeOptions` |
| `test/unit/core/domain/entities/questionnaire_plan/time_input_type_test.dart` | Converter `ArgumentError` for unknown value |
| `test/unit/core/domain/entities/questionnaire_plan/time_interval_json_test.dart` | `ArgumentError` for invalid `TimeIntervalType` |
| `test/unit/core/domain/entities/questionnaire_plan/time_interval_type_test.dart` | Converter `ArgumentError` for unknown value |
| `test/unit/core/domain/entities/questionnaire_plan/time_label_type_test.dart` | Converter `ArgumentError` for unknown value |
| `test/unit/core/domain/entities/tracking_entry_entities/tracking_entry_test.dart` | `TrackingEntry.create` empty uuid `ArgumentError` |
| `test/unit/features/therapist/data_transfer/domain/value_objects/scanner_tier_parameters_test.dart` | `AssertionError` for invalid `chunkSizeBytes` / `displayFpsTarget` / `scanIntervalMs` |
| `test/unit/features/therapist/data_transfer/domain/value_objects/transfer_chunk_test.dart` | `fromBytes` `ArgumentError` on short/empty input — **on the critical-path config** |
| `test/widget/features/therapist/data_transfer/presentation/widgets/in_person_tab_content_test.dart` | `DataBeamError` state widget |
| `test/widget/minimal_resolution_test.dart` | `AppLocalizations` resolution |

The pattern across most failures: tests that expect `ArgumentError` /
`AssertionError` for boundary conditions no longer trigger. This correlates
with the in-flight uncommitted entity edits visible in `git status` —
`contact.dart`, `plan_evaluation_input.dart`, `choice.dart`, `question.dart`,
`questionnaire.dart`, `questionnaire_plan.dart`, both v1 and current versions,
plus `transfer_chunk.dart` (a critical-path file). These edits look like a
parallel impl task in progress; they are not the work of this task.

`transfer_chunk.dart` is in `critical_paths_config.xml` and has failing tests,
so the mutation baseline would mis-classify its mutants as "killed by the
ambient test-suite failure" rather than by genuine assertion strength.

## Why this blocks the task

1. The full mutation baseline (Strategy step 1) cannot be honestly executed
   while the suite is red. Every mutation will look "killed" by the pre-existing
   `-8` count regardless of whether the surviving-mutant assertion was strong.
2. The classification step (Strategy step 2) needs trustworthy survivor data;
   garbage-in, garbage-out makes the created remediation tasks meaningless.
3. Running ~34 mutations × ~66 s `flutter test` each ≈ ~37 minutes of compute
   on data that is known a priori to be unsound.

The "no-survivor fallback" (Strategy §"No-survivor fallback") cannot be invoked
either — it requires a clean full run reporting 0 survivors, which we do not
have.

## Options

**Option A — Block this task on a green-test prerequisite, return to it later.**
Mark TASK-PROC-002-06 `pending` with `awaiting: ["green-test-suite"]`.
Resume when develop's `flutter test` is green. Most aligned with the goal:
produces real remediation tasks from a sound baseline. Cost: latency.

**Option B — Split this task. Run the full mutation baseline as a separate
task once tests are green, and keep -06 as the clustering/task-creation step
after that.** Create a new sibling task `2026-05-19_impl_run-full-mutation-baseline`
under the same requirement; add it to -06's `after:`. Cleaner audit trail than
A; same blocker condition.

**Option C — Complete -06 as a no-op now and rely on the per-release-candidate
full run** (documented in `doc/testing/mutation_testing.md` §"Full critical-path
run") to produce surviving-mutant data when the suite is green again. The
register procedure in `doc/testing/surviving_mutants.md` already covers the
add-rationale-or-task workflow ad-hoc per release cycle, so no chain is needed.
Risk: the explicit "remediation chain" that REQ-PROC-002 envisions never fires
as a discrete activity; survivors are handled in-line during each release.

**Option D — Force the full mutation run now, ignoring the pre-existing
failures, and triage manually.** Cost: ~37 min compute + significant noise in
the output (every line that wasn't already covered will appear as "killed");
result is misleading documentation. Not recommended.

## Recommendation

**Option B**: split off a baseline-run task, keep -06 as the clustering step.
Reasoning:

- Honours both TASK-PROC-002-02's explicit deferral ("first release-candidate
  cycle … or the surviving-mutant remediation task chain") and the goal of -06
  ("read the baseline mutation report produced by TASK-PROC-002-02") by making
  the baseline production an explicit, schedulable step rather than a hidden
  precondition.
- Lets the green-test work proceed independently — no new dependency between
  -06 and the entity-test stabilisation work currently in flight.
- The baseline-run task is small and standalone: green-suite check, run, commit
  the report into `plans_and_protocols/`, done.

## Open question for human

Which option do you want? B is recommended, but A or C are also reasonable
trade-offs depending on how much you want this chain to feel "live" vs.
"per-release". D is not recommended.
