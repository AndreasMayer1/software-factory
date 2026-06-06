---
task_id: TASK-PROC-046-18
type: impl
parent_requirement: REQ-PROC-046
urgency: 3
urgency_reason: U3-PROCESS
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-05-25
session_completed_at: 2026-05-25T11:10:37Z
started: 2026-05-24
effort: M
created: 2026-05-23
after: [TASK-PROC-046-14]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-05, AC-11, AC-12]
  sections: []
scope_description: "Write pytest tests in scripts/tests/ for each of the 12 scripts/quality/check_*.sh and check_*.py gate scripts. Each test provides a synthetic Dart snippet that should PASS and one that should FAIL, asserts exit code and output. Key validations: type-naming must accept Flutter's standard _FooState pattern (currently 22 false positives suspected); folder-taxonomy must have usecases/ in the allowlist or explicitly reject it; complexity thresholds match REQ-PROC-046 AC-02 definitions. Goal: every gate script has at least one true-positive and one true-negative test case."
release_description: ""
opus_recommended: true  # promoted after context_limit_no_entitlement
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 8e1bba39
  file: ../../requirements.md
session_id: 7d1120e9-44c3-44e1-b3b9-d698945955fa
session_account: gmail2
---
# Goal: Validate Gate Scripts with Positive/Negative Test Cases

## Objective

Write pytest tests for each of the 12 custom quality gate scripts under `scripts/quality/check_*.sh` and `check_*.py`. Currently none of these scripts have tests — false positives and false negatives go undetected. Before fixing ~160 pre-existing violations (TASK-PROC-046-19), we must confirm the gate scripts are correct.

## Requirements Summary

REQ-PROC-046 defines 8 gates (G1-G8) with 13 acceptance criteria. The custom gate scripts were created by TASK-PROC-046-14 as DCM replacements. They are wired into `check_quality_gates.sh` and enforced by the pre-commit hook, but have zero test coverage.

For complete requirements at task creation time:
```
git show 8e1bba39:requirements_tasks/process/AI_rules/coding_standards/code_quality/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope
- Write pytest tests in `scripts/tests/` for each gate script:
  - `check_complexity.py` (G2)
  - `check_type_naming.sh`
  - `check_architectural_imports.sh` (G4)
  - `check_no_direct_styling.sh`
  - `check_suppression_justification.sh` (G5)
  - `check_no_debug_artifacts.sh`
  - `check_test_smells.py` (TQ1)
  - `check_folder_taxonomy.sh`
  - `check_no_network_io.sh` (SP1)
  - `check_no_telemetry_sdks.py` (SP2)
  - `check_no_hardcoded_secrets.sh` (SP3)
  - `check_weak_crypto.sh` (SP4)
- Each test: at least one synthetic input that should PASS and one that should FAIL
- Validate known suspected false positives:
  - type-naming: Flutter's `_FooState` private State classes (22 current hits — likely false positive)
  - folder-taxonomy: `usecases/` folder (3 current hits — check if allowlist needs update)
  - complexity: verify thresholds match AC-02 (cyclomatic <= 20, params <= 4, SLOC <= 50, nesting <= 5)

### Out of Scope
- Fixing violations in application code (that's TASK-PROC-046-19)
- Modifying gate scripts (file proposals under `scripts/quality/proposals/` if bugs found)
- G1 (flutter analyze), G3 (flutter test), G6 (accessibility), G7 (performance), G8 (bundle size) — these use Flutter tooling, not custom scripts

## Acceptance Criteria

- [x] Every `scripts/quality/check_*.sh` and `check_*.py` has a corresponding `scripts/tests/test_check_*.py`
- [x] Each test has at least one true-positive (violation detected) and one true-negative (clean code passes)
- [x] Tests for `check_type_naming.sh` verify that Flutter's `_FooState` pattern is handled correctly
- [x] Tests for `check_folder_taxonomy.sh` verify `usecases/` handling
- [x] Tests for `check_complexity.py` verify thresholds match AC-02
- [x] All new tests pass: `python3 -m pytest scripts/tests/test_check_*.py`
- [x] False positives documented as proposals in `scripts/quality/proposals/`

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-14 | completed | Gate scripts must exist |

## Quality Gate Bypass Authorization

Pre-existing dart validation errors in files **not modified by this task** are authorized for bypass. If `verify-quality` reports RED on gates for files this task did not touch, use `SKIP_QUALITY_GATES=1` and note in the commit message that all failures are pre-existing.

Known pre-existing failures covered: suppression-justification (`plan_templates_bloc.dart`, `therapist_clients_bloc.dart`), no-debug-artifacts (`data_beam_scanner_screen.dart`, `lib/main.dart`), complexity/arch-imports/type-naming/no-direct-styling/test-smells/folder-taxonomy in various unmodified files.

These will be fixed by TASK-PROC-046-19. Bypass applies **only** if the failing files are pre-existing and unmodified by this task.

## Notes

The results of this task directly inform TASK-PROC-046-19 (fix baseline violations). If tests reveal that some of the ~160 "violations" are actually false positives from buggy scripts, the true violation count will be lower and the fix scope smaller.
