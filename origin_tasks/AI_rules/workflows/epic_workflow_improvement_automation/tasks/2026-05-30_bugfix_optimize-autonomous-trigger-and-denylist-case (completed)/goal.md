---
task_id: TASK-PROC-006-18
type: bugfix
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-05-30
started: 2026-05-30
completed: 2026-05-30
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-10]
  sections: [SEC-04]
scope_description: "Fix the deny-list filename-case mismatch that defeats AC-10 in practice (F-2 from the TASK-PROC-006-06 validation gate). F-1 (autonomous optimize-task creation) was split out — see Notes."
release_description: ""
opus_recommended: false
worktree_path: ""
requirements_version:
  commit: fadfd042
  file: ../requirements.md
---

# Goal: Ensure the AC-10 write-surface deny-list works correctly (REQ-PROC-006)

## Objective

Fix **F-2** from the TASK-PROC-006-06 validation gate.

### F-2 — Deny-list filename case mismatch defeats AC-10 in practice

`scripts/optimize/create_optimize_task.py` `DENY_LIST` listed the four protected skills
with lowercase `skill.md`, but the on-disk files are `SKILL.md`, and `match_deny_list`
was case-sensitive — so a produced task targeting `.claude/skills/claude-optimize/SKILL.md`
(real casing) would pass the deny-list. G-INV-1 (auto-block, AC-04) still contains the
harm, but the defense-in-depth control (AC-10 / SEC-04) was non-functional for the skill
entries.

## Bug Report

**Steps to reproduce:** Feed `create_optimize_task.py` a `--target-path` of
`.claude/skills/claude-optimize/SKILL.md` (real on-disk casing); observe the deny-list does
NOT reject it (lowercase `skill.md` entry, case-sensitive match).

**Expected:** The deny-list rejects any task targeting the four protected skill files
regardless of filename case.

**Actual:** Uppercase `SKILL.md` paths bypassed the deny-list.

## Resolution

- Changed the four `skill.md` DENY_LIST entries to the real on-disk `SKILL.md` casing.
- Made `match_deny_list()` case-insensitive (normalize target + pattern to lowercase,
  return the original-cased pattern for messages) so no case variant can bypass it.
- Added a case-insensitivity regression test in `scripts/tests/test_create_optimize_task.py`
  and updated the parametrized deny-list test to use the real `SKILL.md` casing.
- Python quality gates green.

## Acceptance Criteria

- [x] A task targeting any of the four protected skills' `SKILL.md` (real on-disk casing)
      is rejected by the deny-list; test uses real casing.
- [x] `match_deny_list` is case-insensitive; regression test added.
- [x] Python quality gates pass (`scripts/quality/check_python_gates.sh`).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies (after: []) |

## Notes

**F-1 split out (scope change, 2026-05-30).** This task originally also covered F-1
(autonomous optimize-task creation / dead reactive-and-periodic trigger paths). During
implementation, F-1 was found to be a **design** problem, not merely a bug (one-event-per-cycle
queue domination, preempt-all surfacing, a 247-event backlog). The developer reframed the
work: F-1 is now folded into a holistic optimizer analysis (target re-alignment + redesign)
rather than patched in isolation. F-1's first implementation is preserved in `git stash`
("F-1 autonomous optimize-cycle trigger — HELD pending optimizer analysis") and documented
in `plans_and_protocols/2026-05-30_01_protocol_f1-autonomous-trigger.md` as a starting
artifact for the redesign. This task is therefore reduced to F-2 only.

Source: TASK-PROC-006-06 validation report —
`../2026-05-27_review_validate-claude-optimize-implementation (completed)/plans_and_protocols/2026-05-30_validation_report.md`
(failure F-2).
