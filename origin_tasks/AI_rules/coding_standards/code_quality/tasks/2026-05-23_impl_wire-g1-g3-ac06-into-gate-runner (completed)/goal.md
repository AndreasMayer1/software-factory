---
task_id: TASK-PROC-046-20
type: impl
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-05-25
completed: 2026-05-25
session_completed_at: 2026-05-25T19:07:50Z
effort: S
created: 2026-05-23
after: [TASK-PROC-046-19]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03, AC-06]
  sections: []
scope_description: "Wire flutter analyze (G1), flutter test (G3), and a dedicated AC-06 check (unawaited futures, bare catch, non-Error throws) into check_quality_gates.sh so the pre-commit hook enforces them — not just the verify-quality skill. Currently the pre-commit hook only runs the custom scripts, missing the analyzer and tests entirely."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 8e1bba39
  file: ../../requirements.md
session_id: 557a82d0-047e-41c8-b4d6-f945f3b37113
session_account: gmail
---
# Goal: Wire G1, G3, and AC-06 into Gate Runner

## Objective

Add `flutter analyze` (G1), `flutter test` (G3), and a dedicated AC-06 enforcement check to `check_quality_gates.sh` so the pre-commit hook enforces them. Currently these gates are only run by the `verify-quality` skill (step 3.2), not by the pre-commit hook which only calls `check_quality_gates.sh`.

## Requirements Summary

REQ-PROC-046 defines G1 (source hygiene), G3 (test correctness), and AC-06 (no unawaited futures, no bare catch, no non-Error throws) as per-change gates. The verify-quality skill runs them, but the pre-commit hook — the real artifact-blocking guard — skips them because they're not in `check_quality_gates.sh`.

For complete requirements at task creation time:
```
git show 8e1bba39:requirements_tasks/process/AI_rules/coding_standards/code_quality/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope
- Add `flutter analyze` invocation to `check_quality_gates.sh` (G1)
- Add `flutter test` invocation to `check_quality_gates.sh` (G3)
- Create `scripts/quality/check_ac06_error_handling.sh` (or `.py`) for AC-06:
  - Detect unawaited `Future` expressions outside `unawaited()` wrappers
  - Detect bare `catch` without `on Type` in persistence/encryption/transfer code
  - Detect `throw` of non-Error/non-Exception values
- Wire AC-06 check into `check_quality_gates.sh`
- Consider performance: `flutter test` takes ~55s — add a `--quick` flag to skip it for the pre-commit hook, or document the tradeoff

### Out of Scope
- G6 (accessibility) — covered by widget test backfill tasks
- G7/G8 (performance/bundle) — release-cadence only
- Fixing any violations these new checks find (baseline should be green from TASK-PROC-046-19)

## Acceptance Criteria

- [x] `check_quality_gates.sh` runs `flutter analyze` and fails on non-zero errors/warnings
- [x] `check_quality_gates.sh` runs `flutter test` and fails on test failures
- [x] AC-06 check script exists and is wired into `check_quality_gates.sh`
- [x] Pre-commit hook now enforces G1, G3, and AC-06 (not just custom scripts)
- [x] Performance impact documented (total gate run time with/without flutter test)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-19 | pending | Baseline must be green first — otherwise G3 blocks every commit |
