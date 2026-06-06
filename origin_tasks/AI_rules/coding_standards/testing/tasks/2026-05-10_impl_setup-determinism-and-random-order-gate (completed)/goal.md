---
task_id: TASK-PROC-002-03
type: impl
parent_requirement: REQ-PROC-002
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: S
created: 2026-05-10
started: 2026-05-18
completed: 2026-05-18
session_completed_at: 2026-05-18T20:48:41Z
after: [TASK-PROC-049-08]  # canon-bootstrap T7 must complete first; see .claude/task_ordering_priority_override.txt
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-04]
  sections: []
scope_description: "Add a release-pre-flight script that runs flutter test --test-randomize-ordering-seed=random and flutter test 10 times consecutively to detect order dependence and flakiness, exits non-zero on any failure or new flake."
release_description: ""
opus_recommended: true  # promoted after context_limit_no_entitlement
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: b88c5b83-3bdc-42a7-bf45-9240bebebed6
session_account: web
---
# Goal: Set up determinism and random-order test gate (TQ4)

## Objective

REQ-PROC-002 AC-04 says the test suite passes under random ordering and on 10 consecutive identical runs. Currently the suite runs once in default order; flakiness and order-dependence go undetected. This task adds a script to the release pre-flight that exercises both checks and surfaces any failure clearly.

## Requirements Summary

REQ-PROC-002 AC-04 (TQ4 independence + determinism). Per-release-candidate cadence.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Add a script (e.g. `scripts/quality/check_test_determinism.sh` or `.py`) that:
  1. Runs `flutter test --test-randomize-ordering-seed=random` once
  2. Runs `flutter test` 10 consecutive times against the current revision
  3. Exits 0 only if all 11 runs pass with zero failures
  4. On failure, prints a clear summary: which run failed, which test, with the seed value
- Run the script once against current code and record the baseline in `plans_and_protocols/`. If the baseline reveals existing flakes, list them so they can be investigated.
- Note the script in the release pre-flight checklist (CLAUDE.md update is TASK-PROC-046-06; just ensure the script's path is stable so that task can reference it).

### Out of Scope

- Fixing existing flakes. If the baseline reveals flakes, that creates remediation tasks.
- Per-change cadence enforcement. AC-04 is per-release-candidate; per-change is too expensive.

## Acceptance Criteria

- [x] The determinism + random-order script exists, runs successfully, and produces a clear pass/fail output with seed information on failure.
- [x] Baseline output is recorded in `plans_and_protocols/`.
- [x] If flakes exist, each is listed with a recommended next step (investigate clock dependence, investigate shared state, etc.).
- [x] The script's path is stable and noted in the protocol.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

A flake is not "tolerable" — AC-04 says the suite passes on 10 consecutive runs. If the baseline reveals flakes, remediation comes before AC-04 is satisfied. The script's job here is detection, not remediation.
