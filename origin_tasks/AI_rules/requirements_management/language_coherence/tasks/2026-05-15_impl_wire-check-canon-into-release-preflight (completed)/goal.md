---
task_id: TASK-PROC-049-09
type: impl
parent_requirement: REQ-PROC-049
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: completed
started: 2026-05-16
completed: 2026-05-16
session_completed_at: 2026-05-16T14:37:33Z
effort: S
created: 2026-05-15
after: [TASK-PROC-049-06]  # only hard dep is check_canon.py existing (T5); T6/T7 are parallel concerns
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-05]
  sections: []
target_package: ""
scope_description: "Extend scripts/release/check_release_preconditions.py to invoke check_canon.py and fail-close on non-zero exit"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 5747c0c2
  file: ../../requirements.md
session_id: 5696def7-a92a-4447-bc1c-3de36a64ea50
session_account: gmail2
---

# Goal: Wire check_canon.py into release pre-flight

## Objective

Make canon drift block a release. Extend `scripts/release/check_release_preconditions.py` to invoke `scripts/user_needs/check_canon.py` and fail-close (non-zero exit propagates) on any non-zero return.

## Background

Design references:

- `2026-05-15_10_final_decisions.md` §2 row T8 (this task scope).
- `2026-05-15_08_opus_synthesis_v3.md` §5.1 (check_canon CLI / exit codes).
- CLAUDE.md §11 — `scripts/release/check_release_preconditions.py` is the existing release-precondition gate.

For complete requirements at task creation time:
```
git show 5747c0c2:requirements_tasks/process/AI_rules/requirements_management/language_coherence/requirements.md
```

Current requirements: ../../requirements.md

## Requirements Summary

Covers AC-05 — the canon drift check becomes a release-blocking pass/fail signal.

## Scope

### In Scope

Use the `claude-write-script` skill to:

- Add a call to `python3 scripts/user_needs/check_canon.py` inside `scripts/release/check_release_preconditions.py`.
- On non-zero exit from `check_canon.py`, the pre-flight script must:
  - Print the canon-check output (or a clear summary).
  - Return a non-zero exit code so `execute_release.py` will refuse to proceed.
- The invocation should pass `--json` if the precondition script already consumes structured output from its sub-checks; otherwise plain run is fine.
- Update CLAUDE.md §11 Generated Files / Scripts Reference if the precondition script's description changes meaningfully. (T7 already adds the canon check script entry; this task only needs to revise the precondition script's description if the wording becomes stale.)

### Out of Scope

- Implementing `check_canon.py` itself (T5 / TASK-PROC-049-06).
- Modifying `execute_release.py` (the precondition script is the gate).
- Adding new release gates beyond canon.

## Acceptance Criteria

- [x] `scripts/release/check_release_preconditions.py` invokes `check_canon.py`.
- [x] Non-zero exit from `check_canon.py` propagates to a non-zero exit from the precondition script.
- [x] Pre-flight output includes a clear "canon coherence: PASS / FAIL" line.
- [x] No regressions in existing precondition checks (active release, no pending tasks, clean branch, tests pass, version not yet bumped).
- [x] CLAUDE.md §11 Generated Files / Scripts Reference updated if the precondition script's description needs revision.

## Implementing Skill

`claude-write-script` (MANDATORY per CLAUDE.md for script modification).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-049-07 | pending | Caller-skill wiring must be in place so callers actually maintain canon coherence; otherwise pre-flight will fail-close immediately and block all releases. |

## Notes

- T7 (TASK-PROC-049-08) is NOT a hard dependency for this task — they can run in parallel. T7 owns README/CLAUDE.md/cross-refs; this task owns release-script wiring. Listed dependency is only T6 (TASK-PROC-049-07) because the skills must be wired before the gate goes live, otherwise the first release after this task would fail catastrophically.
- The release-precondition script is the canonical place to add canon-drift blocking. Do not add the check in other places.
