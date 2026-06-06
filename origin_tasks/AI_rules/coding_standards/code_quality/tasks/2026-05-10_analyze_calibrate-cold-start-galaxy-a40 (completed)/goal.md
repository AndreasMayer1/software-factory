---
task_id: TASK-PROC-046-02
type: analyze
parent_requirement: REQ-PROC-046
urgency: 3
urgency_reason: U3-PROCESS
impact: 4
impact_reason: I4-QUAL
status: completed
effort: S
created: 2026-05-10
started: 2026-05-15
completed: 2026-05-16
session_completed_at: 2026-05-16T09:45:35Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-08]
  sections: []
scope_description: "Measure cold-start time on the Samsung Galaxy A40 reference device, calibrate AC-08's 3 000 ms threshold against actual measurements, document the methodology"
release_description: ""
opus_recommended: false
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: 805864fb-88f9-479b-a36d-5e56086d103e
session_account: gmail2
---

# Goal: Calibrate AC-08 Cold-Start Threshold Against Galaxy A40

## Objective

REQ-PROC-046 AC-08 currently asserts that cold-start time-to-first-rasterized-frame on the Samsung Galaxy A40 is ≤ 3 000 ms. The 3 000 ms value is a *reasoned estimate* (derived from Google Play's "slow" classification of ≥ 5 s minus headroom for older hardware) — it has not been measured on the actual A40. Until it is measured, AC-08 is not evaluable: the gate cannot fail meaningfully because there is no calibrated reference, and it cannot pass meaningfully because we have no idea where the device actually lands.

This task closes that gap: measure cold-start on the A40, decide a calibrated threshold based on the measurements, document the methodology, and update AC-08 with the calibrated value.

## Requirements Summary

REQ-PROC-046 AC-08 (current text):
> "On the project's reference test device — Samsung Galaxy A40 (Android, Exynos 7904, 4 GB RAM, released 2019) — cold-start time-to-first-rasterized-frame is ≤ 3 000 ms (measured via `flutter run --trace-startup --profile` reading `timeToFirstFrameRasterizedMicros` from `build/start_up_info.json`); during data-entry interaction in integration tests, `average_frame_build_time_millis` ≤ 16 ms and `missed_frame_build_budget_count` is 0 across the measured action."

The measurement methodology and the 3 000 ms cold-start figure are the parts of AC-08 this task calibrates. The frame-budget portion (16 ms average, zero missed-budget events) is *not* in scope here — it is calibrated separately when the data-entry integration test is implemented.

For complete requirements at task creation time:
```
git show HEAD:requirements_tasks/process/AI_rules/coding_standards/code_quality/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

- Build the app in `--profile` mode targeted at `android-arm64` (the A40's ABI).
- Establish a controlled cold-start condition on the A40: app force-stopped, OS process killed, page cache flushed where possible, screen on, device on charger, airplane mode where stable.
- Run `flutter run --trace-startup --profile -d <a40-device-id>` at least 10 times under controlled cold-start conditions; capture `build/start_up_info.json` after each run.
- Extract `timeToFirstFrameRasterizedMicros` per run; compute median, p95, max, and standard deviation across runs.
- Decide a calibrated threshold using a documented rule (e.g. p95 + 30 % headroom, rounded up to the next 250 ms).
- Update REQ-PROC-046 AC-08 with the calibrated value and a one-line rationale.
- Document the methodology (device prep, run count, statistical rule) in `doc/testing/` so future re-calibration is reproducible.
- Archive the raw `start_up_info.json` files and the analysis spreadsheet in this task's `plans_and_protocols/` so the measurement can be audited.

### Out of Scope

- Frame-budget portion of AC-08 (data-entry interaction). That depends on a data-entry integration test that does not yet exist.
- Calibrating G7 against any device other than the A40.
- Optimising the app to *make* it hit a particular threshold. The goal is to set the threshold honestly based on what the app currently does; performance optimisation is separate work.
- Bundle-size gate (G8 / AC-09). Different gate, different task.

## Acceptance Criteria

- [x] The app has been run ≥ 10 times in cold-start condition on the physical Galaxy A40 with `--trace-startup --profile`; raw `start_up_info.json` files are archived in `plans_and_protocols/`.
- [x] Statistics (median, p95, max, std dev) are computed and recorded in `plans_and_protocols/`.
- [x] A calibrated threshold value is decided, with the chosen statistical rule (e.g. p95 + 30 % headroom) and rationale documented.
- [x] REQ-PROC-046 AC-08 is updated with the calibrated value (replacing the current 3 000 ms placeholder); the prose elsewhere in the document referring to "3 000 ms" is updated consistently.
- [x] The measurement methodology — device-prep checklist, run count, statistical rule — is documented in `doc/testing/` (a new section or new file) so a future re-calibration produces a comparable number.
- [x] If the calibrated threshold differs materially from 3 000 ms (say, by more than ±500 ms), the cause is noted in the protocol (e.g. "A40 is faster than expected because Exynos 7904 is mid-tier, not low-end; the persona's 2017/2 GB worst-case still warrants the looser global commitment but the gate threshold reflects the test device").

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Galaxy A40 physical device | Available | Owned by app provider |
| App buildable in `--profile` mode | Likely OK | If not, this surfaces a separate issue |
| ADB / Flutter device tooling | Available | Standard Flutter dev setup |

## Notes

**Why a single device, not a fleet**: PERSONA-004 names a worst-case device profile (2017 Android, 2 GB RAM) but the app provider does not have one to test on. The A40 is the *available test instrument*, not the worst-supported device. The calibration should reflect the A40's measurements; the persona's broader commitment to even-older devices remains an architectural goal, not a gate threshold.

**Why ≥ 10 runs and a statistical rule**: cold-start time has substantial variance run-to-run (page cache state, JIT compilation, OS scheduling, thermal state). A single measurement is not a number; a distribution is. The p95-plus-headroom rule errs on the side of letting through occasionally-slow runs without flapping.

**Avoid the optimisation trap**: this task is *not* "make the app start in 3 000 ms." It is "find out what the app currently does, then set the gate to the honest reality." If the measurement shows 4 200 ms, the threshold becomes 4 500 ms or so — and a separate future task can address the regression, with the gate visible during that work.

**Update propagation**: when AC-08 is updated, the references to "3 000 ms" in the Examples and Developer Guidelines sections of REQ-PROC-046 must be updated too. The Reference Test Device section should remain factually correct (A40 specs are unchanged).
