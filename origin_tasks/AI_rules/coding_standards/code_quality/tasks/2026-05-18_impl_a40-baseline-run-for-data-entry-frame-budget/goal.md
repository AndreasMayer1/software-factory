---
task_id: TASK-PROC-046-15
type: impl
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: S
created: 2026-05-18
after: [TASK-PROC-046-10]
awaiting: ["physical A40 attached on Windows host"]
awaiting_note: "Requires Galaxy A40 device + flutter drive runner on Windows host; cannot run in devcontainer"
covers:
  acceptance_criteria: [AC-08]
  sections: []
scope_description: "Run the data-entry frame-budget integration test on the Galaxy A40, archive timeline JSONs as the baseline, and create a remediation task if the gate fails."
release_description: ""
opus_recommended: false
requirements_version:
  commit: 0ea59bdb
  file: ../../requirements.md
---

# Implementation Task: A40 Baseline Run for Data-Entry Frame-Budget Gate

## Requirement Reference
- **Requirement**: `requirements_tasks/process/AI_rules/coding_standards/code_quality/requirements.md`
- **Status**: Not Started

## Goal

This is Phase 2 of the data-entry frame-budget gate setup. Phase 1 (TASK-PROC-046-10) produced
the test source, the documentation, and the run-runbook. Phase 2 — this task — runs the test
on the physical Galaxy A40 reference device, archives the baseline evidence, and handles any
gate failure.

## Scope Overview

**Affected Layers**: None (device run + archival)

**Estimated Files**: ~2-4 archive files in `plans_and_protocols/raw/` of the Phase-1 task

**Patterns to Follow**: The cold-start calibration sibling
`2026-05-10_analyze_calibrate-cold-start-galaxy-a40` is the reference for how to archive
timeline files and record baseline numbers.

## Steps

1. Connect the Samsung Galaxy A40 to the Windows host. Confirm via `adb devices`.

2. Prepare the device per `doc/testing/frame_budget_measurement_methodology.md §Measurement Setup`:
   - Force-stop the app
   - Enable airplane mode
   - Device on charger
   - Wait 3 s

3. Run the test 3 times (minimum):
   ```
   flutter drive \
     --driver=test_driver/integration_test.dart \
     --target=integration_test/perf/data_entry_frame_budget_test.dart \
     --profile \
     -d <a40-device-id>
   ```

4. After each run, archive the output files into the **Phase-1 task's**
   `plans_and_protocols/raw/` folder (cross-task archive — same pattern as cold-start sibling):
   ```
   requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/
   2026-05-10_impl_setup-data-entry-frame-budget-integration-test/
   plans_and_protocols/raw/run_NN_timeline.json
   plans_and_protocols/raw/run_NN_summary.json
   ```

5. Record the measured numbers (`average_frame_build_time_millis`,
   `missed_frame_build_budget_count` from each run) in this task's `plans_and_protocols/`.

6. **If the gate passes** (test exits 0 on all 3 runs): record the baseline numbers and close
   this task. The Phase-1 task (TASK-PROC-046-10) was already closed at Phase-1 completion.

7. **If the gate fails** (any run has `average_frame_build_time_millis > 16.0` or
   `missed_frame_build_budget_count > 0`):
   - Record the offending interaction in this task's `plans_and_protocols/`.
   - Identify the regression source using the raw `*.timeline.json` in Flutter DevTools → Performance.
   - Create a remediation task referencing the offending frame data.
   - **Do NOT relax the 16 ms threshold** without evidence the threshold is wrong for this device.

## Context: Phase 1 / Phase 2 Split

This task exists because the integration test source (Phase 1) was written in an automated
session without a physical Galaxy A40 attached. The physical device run cannot happen in the
devcontainer. See the Phase-1 plan for full architectural rationale:

`requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/
2026-05-10_impl_setup-data-entry-frame-budget-integration-test/
plans_and_protocols/2026-05-18_01_plan_frame_budget_integration_test.md §7`

## Acceptance Criteria

- [ ] Test run at least 3 times on the physical Galaxy A40 in profile mode.
- [ ] Raw `*.timeline.json` and `*_summary.json` archived in Phase-1 task's `plans_and_protocols/raw/`.
- [ ] Measured numbers recorded in this task's `plans_and_protocols/`.
- [ ] If gate fails: remediation task created; offending interaction documented.
- [ ] If gate passes: baseline confirmed; this task closed.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-10 | after | Phase-1 test source must exist before this run |
| Galaxy A40 physical device | External | Attached to Windows host via USB |

---

**Note**: This task describes WHAT to implement, not HOW. The implementation plan is created fresh at execution time.

## Quality Gate Bypass Authorization

Pre-existing dart validation errors in files **not modified by this task** are authorized for bypass. If `verify-quality` reports RED on gates for files this task did not touch, use `SKIP_QUALITY_GATES=1` and note in the commit message that all failures are pre-existing.

Known pre-existing failures covered: suppression-justification (`plan_templates_bloc.dart`, `therapist_clients_bloc.dart`), no-debug-artifacts (`data_beam_scanner_screen.dart`, `lib/main.dart`), complexity/arch-imports/type-naming/no-direct-styling/test-smells/folder-taxonomy in various unmodified files.

These will be fixed by TASK-PROC-046-19. Bypass applies **only** if the failing files are pre-existing and unmodified by this task.
