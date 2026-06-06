---
task_id: TASK-PROC-046-19
type: impl
parent_requirement: REQ-PROC-046
urgency: 3
urgency_reason: U3-PROCESS
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-05-25
session_completed_at: 2026-05-25T18:32:53Z
effort: L
created: 2026-05-23
started: 2026-05-25
after: [TASK-PROC-046-18]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-05, AC-11, AC-12]
  sections: []
scope_description: "Fix all pre-existing violations detected by check_quality_gates.sh on the current codebase (~160 violations across complexity, type-naming, arch-imports, direct-styling, test-smells, folder-taxonomy, suppression-justification, debug-artifacts). Where TASK-PROC-046-18 revealed a false positive (gate bug), file a proposal under scripts/quality/proposals/ instead of changing code. Goal: check_quality_gates.sh exits 0 on the existing codebase."
release_description: ""
opus_recommended: true   # reason: ~160 violations across 8 gate categories, multi-file architectural changes, requires judgment on code vs gate-rule fixes
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 8e1bba39
  file: ../../requirements.md
session_id: bac851cb-2a1a-4457-b4b6-c0e6970a5dab
session_account: gmail
---
# Goal: Fix Pre-Existing Baseline Violations

## Objective

Make `check_quality_gates.sh` exit 0 on the existing codebase. Currently it reports ~160 violations across 8 gate categories that pre-date the gate scripts. These were never cleaned up after TASK-PROC-046-14 created the scripts.

## Requirements Summary

REQ-PROC-046 AC-10 states code that fails any active quality gate is never declared complete. The gates exist and run, but the baseline was never brought to green. This creates a "broken windows" situation where every commit must bypass the gates.

For complete requirements at task creation time:
```
git show 8e1bba39:requirements_tasks/process/AI_rules/coding_standards/code_quality/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

Current violation counts (as of 2026-05-23):

| Gate | Violations | Category |
|---|---|---|
| AC02 complexity | 99 | params > 4, SLOC > 50, cyclomatic > 20 |
| type-naming | 22 | Private `_State` classes and others |
| no-direct-styling | 14 | Inline TextStyle/Colors in features |
| arch-imports | 13 | `package:flutter/foundation.dart` in domain |
| test-smells | 9 | `expect(x.length, N)` should use `hasLength(N)` |
| AC11 suppression-justification | 6 | `// ignore:` without justification |
| AC12 no-debug-artifacts | 5 | `debugPrint` without `[DIAG-*]` prefix |
| folder-taxonomy | 3 | `usecases/` not in allowlist |

For each violation:
- If TASK-PROC-046-18 confirmed it's a **true violation**: fix the code
- If TASK-PROC-046-18 revealed it's a **false positive**: file a proposal under `scripts/quality/proposals/` to fix the gate script, and apply the script fix

### Out of Scope
- G1 (flutter analyze) — already green per TASK-PROC-046-03
- G3 (flutter test) — already green
- Changing gate thresholds without a proposal
- Performance/bundle-size gates (G7, G8)

## Acceptance Criteria

- [x] `bash scripts/quality/check_quality_gates.sh` exits 0 with zero violations
- [x] No code changes that alter user-visible behavior (pure cleanup/refactor)
- [x] False-positive gate bugs filed as proposals in `scripts/quality/proposals/`
- [x] All existing tests still pass after cleanup
- [x] CLAUDE.md updated: section removed

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-18 | pending | Must confirm gate correctness before fixing violations |

## Notes

This task may need to be split into sub-tasks if the violation count remains high after false positives are removed. The complexity violations (99) are the largest category — many are entity constructors with > 4 parameters, which may require a proposal to adjust the threshold for constructors/copyWith methods rather than restructuring stable domain code.
