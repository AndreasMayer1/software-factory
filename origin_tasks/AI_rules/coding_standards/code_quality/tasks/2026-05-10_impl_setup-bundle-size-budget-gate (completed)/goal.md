---
task_id: TASK-PROC-046-05
type: impl
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-PROC
status: completed
effort: S
created: 2026-05-10
started: 2026-05-18
completed: 2026-05-18
session_completed_at: 2026-05-18T11:13:48Z
after: [TASK-PROC-049-08]  # canon-bootstrap T7 must complete first; see .claude/task_ordering_priority_override.txt
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-09]
  sections: []
scope_description: "Add a release-pre-flight script that runs flutter build apk --analyze-size and flutter build appbundle --analyze-size, parses the JSON, and asserts the per-ABI APK ≤ 30 MB and AAB ≤ 50 MB thresholds."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: b0ba0188-7687-4fe7-b1c5-36e37638e923
session_account: web
---
# Goal: Set up bundle-size budget gate (AC-09)

## Objective

REQ-PROC-046 AC-09 caps per-ABI APK at 30 MB and AAB at 50 MB. Currently nothing measures or enforces this. This task creates the script that runs the size analysis, asserts the thresholds, and archives the JSON for trend visibility across releases.

## Requirements Summary

REQ-PROC-046 AC-09 (bundle-size budget). G8 in the gate table; per-release-candidate cadence.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Add a script (e.g. `scripts/quality/check_bundle_size.py` or `.ps1` if Windows-host execution is preferred) that:
  1. Runs `flutter build apk --analyze-size --target-platform=android-arm64`
  2. Runs `flutter build appbundle --analyze-size`
  3. Reads the resulting `*-code-size-analysis_*.json` files
  4. Asserts APK ≤ 30 MB and AAB ≤ 50 MB
  5. Exits 0 on pass, non-zero with a detailed contributor breakdown on fail
  6. Archives the JSON to a release-artifacts location (e.g. `releases/[version]/size_analysis/`)
- Run the script against current code and record the baseline (APK and AAB sizes) in `plans_and_protocols/`.
- Note the script in the release pre-flight (the CLAUDE.md update is TASK-PROC-046-06; just ensure the script's path is stable).

### Out of Scope

- Reducing the bundle size if it currently exceeds the thresholds. If the baseline exceeds 30 / 50 MB, that creates a remediation task; this task only sets up measurement.
- Per-architecture variants beyond `android-arm64`. That can be added later if needed.
- iOS / Windows bundle-size measurement. AC-09 names the Android budgets specifically.

## Acceptance Criteria

- [x] The bundle-size script exists, runs successfully, and produces a clear pass/fail output.
- [x] Baseline APK and AAB sizes are recorded in `plans_and_protocols/`.
- [x] If baseline exceeds the thresholds, a remediation task is created with the contributor breakdown. _(n/a — baseline 25.97 MB APK / 22.66 MB AAB, both under budget; see `2026-05-18_02_protocol.md`)_
- [x] The size-analysis JSON archive location is documented (so `release-begin-impl` or similar can find it).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
