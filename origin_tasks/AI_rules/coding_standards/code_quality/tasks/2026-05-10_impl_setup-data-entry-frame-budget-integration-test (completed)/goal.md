---
task_id: TASK-PROC-046-10
type: impl
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-10
started: 2026-05-18
completed: 2026-05-18
session_completed_at: 2026-05-18T11:46:30Z
after: [TASK-PROC-049-08]  # canon-bootstrap T7 must complete first; see .claude/task_ordering_priority_override.txt
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-08]
  sections: []
scope_description: "Set up an integration test on the primary data-entry screen using IntegrationTestWidgetsFlutterBinding.traceAction() that asserts average_frame_build_time_millis ≤ 16 ms and missed_frame_build_budget_count == 0 on the Galaxy A40."
release_description: ""
opus_recommended: true  # promoted after context_limit_no_entitlement
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: ba8d97e8-1290-4db4-b7fb-77a70d3c2ffe
session_account: gmail2
---
# Goal: Set up data-entry frame-budget integration test (G7 dynamic)

## Recommended Skill

**Use `code-complex` skill for this task.** The integration test is real Dart code under `integration_test/perf/` that wraps a representative interaction sequence and asserts on timeline metrics. The skill's plan-and-approve gate ensures the chosen interaction sequence is the right one (i.e. the actual primary data-entry surface as the persona uses it) before the test is written.

## Objective

REQ-PROC-046 AC-08 has two surfaces. Cold-start (TTFR ≤ 3 000 ms on the A40) is calibrated by TASK-PROC-046-02. The other surface — frame budget during data-entry interaction — has no measurement infrastructure today: AC-08 names `average_frame_build_time_millis` ≤ 16 ms and `missed_frame_build_budget_count` == 0, but no integration test produces those numbers. This task sets up that test.

## Requirements Summary

REQ-PROC-046 AC-08, frame-budget portion. Data-entry interaction must run within frame budget on the A40 reference device. Measurement mechanism: `IntegrationTestWidgetsFlutterBinding.traceAction()` writing `{reportKey}_summary.timeline_summary.json`.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Identify the primary data-entry screen — likely the journal-entry / mood-entry composer that PERSONA-015 names as the user's most-frequent action surface. If multiple candidates exist, pick the one a typical user reaches first after launch.
- Add an integration test under `integration_test/perf/` (or whatever folder convention is established) that:
  1. Uses `IntegrationTestWidgetsFlutterBinding.ensureInitialized()`
  2. Pumps the app to the data-entry screen
  3. Wraps a representative interaction sequence (open form → type into a text field → select a mood → submit) inside `binding.traceAction(() async { … }, reportKey: 'data_entry_frame_budget')`
  4. After the action, asserts that the resulting `_summary.timeline_summary.json` satisfies `average_frame_build_time_millis ≤ 16` and `missed_frame_build_budget_count == 0`
- Configure the test to be runnable both on a physical A40 device (`flutter drive --target=integration_test/perf/data_entry_frame_budget_test.dart --profile`) and (optionally) on an Android emulator approximating the A40's profile.
- Document the run command and expected outputs in `doc/testing/` so the gate is reproducible.
- Run the test once on the A40 against the current code; archive the resulting `*_summary.timeline_summary.json` and the raw `*_timeline.json` in `plans_and_protocols/` as the baseline.
- If baseline fails (build time > 16 ms or missed-budget > 0), record the offending interaction in the protocol — do *not* relax the threshold without evidence the threshold is wrong; first investigate the regression.

### Out of Scope

- Cold-start measurement — TASK-PROC-046-02 owns that.
- Frame-budget measurement on screens other than the primary data-entry surface. Other screens may eventually need their own per-flow gate; this task is the first.
- Performance optimisation if the baseline fails. That becomes a remediation task created from the protocol output.
- iOS / Windows frame-budget testing. AC-08 names the A40 explicitly; cross-platform expansion is separate work.

## Acceptance Criteria

- [x] Integration test file exists under `integration_test/perf/` and is runnable via `flutter drive`.
- [x] The test wraps a representative data-entry interaction in `traceAction()`.
- [x] The test asserts `average_frame_build_time_millis` ≤ 16 and `missed_frame_build_budget_count` == 0.
- [ ] Baseline run on the physical A40 is recorded in `plans_and_protocols/`; raw timeline JSONs are archived. *(Deferred to TASK-PROC-046-15 — requires physical A40 on Windows host; plan §7 split decision.)*
- [x] `doc/testing/` documents the run command, expected outputs, and how to interpret a failure.
- [ ] If baseline fails, the offending interaction is identified and a remediation task is created (do not silently relax the threshold). *(Deferred to TASK-PROC-046-15 — only relevant after the baseline run; remediation task creation is part of TASK-PROC-046-15's scope.)*

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Galaxy A40 physical device | Available | Same instrument as TASK-PROC-046-02 |

## Notes

The 16 ms threshold is the Flutter 60 fps frame budget. On the A40's display (60 Hz Super AMOLED), this is the right target. If the A40 misses 16 ms regularly during data entry, that is a real regression — the persona's "users in fragile states make quick entries" is the value at stake.

`traceAction()` writes outputs under `build/integration_response_data/`; capture those as part of the baseline archive. The test's assertions parse the JSON in the same test process — the integration test is self-contained, no external script needed.

Worth noting the interaction with REQ-PROC-002 AC-04 (test determinism): performance integration tests are inherently more variable than unit tests. The 10-consecutive-runs determinism gate may need a relaxed bound for tests under `integration_test/perf/` (e.g. allow ≤ 1 timeout failure per 10 runs). Surface this trade-off in the protocol if it bites.
