---
task_id: TASK-PROC-058-09
type: verify
verification_task: true
parent_requirement: REQ-PROC-058
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-26
started: 2026-05-27
completed: 2026-05-27
session_completed_at: 2026-05-27T12:47:02Z
after: [TASK-PROC-058-08]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-09]
  sections: []
scope_description: "Second validation run of task-derive-from-requ against feat_qr_data_transfer: confirm Findings D–H are closed after TASK-PROC-058-08, and exercise the covers-repair workflow (AC-09) which was not triggered in the first run."
release_description: ""
opus_recommended: true   # reason: synthesis-dependent — cross-checks D–H fixes + AC-09 covers-repair across skill, scripts, and a live requirement simultaneously
writes_requirements: false
expected_tool_calls: 40
synthesis_dependent: true
synthesis_justification: "Cross-checks five script/skill fixes (D–H) and the covers-repair workflow (AC-09) across skill text, implemented scripts, and a live requirement (feat_qr_data_transfer) simultaneously."
requirements_version:
  commit: e680b5e9
  file: ../../requirements.md
plan_source: requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/tasks/2026-05-24_impl_test-case-req-proc-001-decomposition (completed)/plans_and_protocols/2026-05-26_test_case_findings.md
session_id: 8d4ca36c-cb5e-46ac-b8f0-caf9d79cc8b0
session_account: gmail2
---
# Goal: Second validation run of task-derive-from-requ against feat_qr_data_transfer

## Objective

Re-run the `task-derive-from-requ` skill against `feat_qr_data_transfer` — the
secondary test case identified in TASK-PROC-058-07's goal.md — after
TASK-PROC-058-08 has landed. This confirms:

1. The five integration bugs (Findings D–H) are genuinely closed and no longer
   force the skill to fall back to less-precise paths.
2. The covers-repair workflow (AC-09 of REQ-PROC-058) is exercised on real data,
   which was not possible during the first run because the two legacy
   explore tasks (TASK-PROC-001-01, -02) had legitimately empty `covers:` fields
   and correctly triggered no auto-repair.

## Requirements Summary

REQ-PROC-058 defines the `task-derive-from-requ` skill. AC-09 specifies the
incremental-decomposition / covers-repair workflow: when existing tasks have
empty `covers:` fields, the skill reads their goal.md bodies, infers coverage
from scope description and task name, and proposes `covers:` updates for user
confirmation before planning new tasks.

The first validation run (TASK-PROC-058-07) confirmed the skill works end-to-end
but did not exercise AC-09. Five concrete integration mismatches were filed as
TASK-PROC-058-08.

For complete requirements at task creation time:
```
git show e680b5e9:requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

**D-H regression check** — for each of the five fixes in TASK-PROC-058-08:

- **D** — Skill Phase 1.5.1 now references `check_cross_refs.py`: confirm the
  script is invoked by name without error.
- **E** — Invocation uses positional argument (no `--target`, no `--json`):
  confirm the call succeeds.
- **F** — Auto-derived search terms filtered through stop-words: confirm the
  candidate count for `feat_qr_data_transfer` is workable (≤ 30) without
  dropping genuine matches.
- **G** — `--task-type` values are `implement|verify|scribble|scribble_to_flutter`:
  confirm Phase 5 uses the correct values.
- **H** — `create_orchestration_task.py` routes non-code tasks to `task-create`:
  confirm routing works for any non-code tasks produced by the run.

**AC-09 covers-repair exercise** — `feat_qr_data_transfer` likely has existing
tasks with empty or partially-populated `covers:` fields (it is a code feature,
not a legacy explore requirement). The skill should detect those, infer coverage
from goal.md bodies, and propose updates. Confirm the inference and proposal
steps fire.

**End-to-end smoke test** — the full skill run (Phases 1–6) completes without
falling back due to D-H failures.

**Findings report** — write `plans_and_protocols/<date>_second_run_findings.md`
with the same structure as `2026-05-26_test_case_findings.md` from TASK-PROC-058-07:
TL;DR table, chronological account, findings (positive + bugs).

### Out of Scope

- Fixing any newly discovered bugs in-place. File follow-up tasks instead.
- Completing the full `feat_qr_data_transfer` decomposition if it would require
  extensive user interaction unrelated to this validation goal.
- Re-verifying TASK-PROC-058-07 findings that are confirmed fixed — one probe
  per finding is sufficient.

## Acceptance Criteria

- [x] `plans_and_protocols/2026-05-27_second_run_findings.md` exists with TL;DR,
      chronological account, and per-finding status (D–H each: all fixed).
- [x] Findings D and E: `check_cross_refs.py` invoked with its actual interface
      (positional arg, JSON default) without error (exit 0).
- [x] Finding F: auto-derived candidate count for `feat_qr_data_transfer` = 17
      (≤ 30), verified by direct probe.
- [x] Finding G: Phase 5 `--task-type` values match the implemented script
      (`implement` accepted, old `impl` rejected — live probe).
- [x] Finding H: non-code task routing to `task-create` confirmed via code
      inspection of `_build_ac_block` (no live non-code task created — validation
      run, see methodology note in findings).
- [x] AC-09 covers-repair: skill detected TASK-FUNC-007-12-01's empty
      `acceptance_criteria`, inferred from the goal body, and correctly declined
      auto-repair (intentional section-scope + cross-package mismatch); recorded
      in the findings report.
- [x] No newly discovered bugs (D–H all closed); two minor observations (O1, O2)
      documented inline rather than filed.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-058-08 | pending | Fixes D–H; must land before this run begins. |

## Notes

Recommended by the TASK-PROC-058-07 test case findings:
`requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/tasks/2026-05-24_impl_test-case-req-proc-001-decomposition (completed)/plans_and_protocols/2026-05-26_test_case_findings.md`
(Conclusion section).

`target_package` is intentionally omitted: `verification_task: true` keeps the
task unpackaged so it ranks alongside the impl tasks it verifies in `next_tasks.py`.
