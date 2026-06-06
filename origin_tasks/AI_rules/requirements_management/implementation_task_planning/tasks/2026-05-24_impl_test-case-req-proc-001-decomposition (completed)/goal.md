---
task_id: TASK-PROC-058-07
type: impl
parent_requirement: REQ-PROC-058
urgency: 3
urgency_reason: U3-SPRINT
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-24
started: 2026-05-25
completed: 2026-05-26
session_completed_at: 2026-05-26T12:58:05Z
after: [TASK-PROC-058-02, TASK-PROC-058-03, TASK-PROC-058-04, TASK-PROC-058-05, TASK-PROC-045-07]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-09, AC-17]
  sections: []
scope_description: "Real-world validation of task-derive-from-requ by re-planning REQ-PROC-001 (which has known gaps: AC-04 and AC-07 zero-coverage, no verification task). Validates coverage matrix, verification task generation, sizing signals, incremental decomposition, and cross-reference check on a live requirement. Fixes the REQ-PROC-001 gaps."
release_description: ""
opus_recommended: true   # reason: real-world test, judgment needed on edge cases that surface
writes_requirements: false
requirements_version:
  commit: e680b5e9
  file: ../../requirements.md
session_id: 60d42e81-7a35-434b-87dd-1e6f3f73bec8
session_account: gmail2
---
# Goal: Test case — run task-derive-from-requ on REQ-PROC-001

## Objective

Validate the task-derive-from-requ skill against a real, known-imperfect requirement: REQ-PROC-001 (Context Window). REQ-PROC-001 has 8 ACs, 7 existing impl tasks, AC-04 and AC-07 with zero coverage, and no verification task. This is the canonical test case identified during REQ-PROC-058 exploration.

**This task MUST be run in a fresh session** (per user instruction). The execution validates the new mechanism end-to-end and fixes the REQ-PROC-001 gaps as a byproduct.

## Requirements Summary

REQ-PROC-058 introduces task-derive-from-requ to prevent the coverage-gap pattern that REQ-PROC-046 and REQ-PROC-001 both exhibit. This task is the first real test of whether the new skill actually catches and fixes these gaps in practice.

For complete requirements at task creation time:
```
git show e680b5e9:requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

1. **Run task-derive-from-requ on REQ-PROC-001** in a fresh session
   - Target: `requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md`
   - Mode: full (REQ-PROC-001 has multiple uncovered ACs, fits full-mode trigger)

2. **Validate the skill's outputs**:
   - Coverage matrix: must surface AC-04 and AC-07 as uncovered
   - Existing tasks: must surface the 7 existing impl tasks; covers: repair workflow if any have empty covers:
   - Verification task: must be proposed (none exists today)
   - Cross-reference completeness gate (AC-17): must run; identify any missing cross-refs

3. **Fix the REQ-PROC-001 gaps** via the task-derive-from-requ workflow:
   - Approved plan creates tasks for AC-04 and AC-07
   - Verification task is created
   - Any cross-reference gaps surfaced are fixed (via spawned requ-explore agent)

4. **Document findings**:
   - Did the skill surface the gaps correctly?
   - Did the cross-reference gate work in practice?
   - Did the spawn-requ-explore-agent pattern (AC-17) succeed?
   - Did the orchestration task pattern fire (depends on task count)?
   - Any edge cases or unexpected behavior?
   - Produce `plans_and_protocols/test_case_findings.md`

5. **Feed findings back**: any issues found update either REQ-PROC-058 (via requ-explore) or the skill implementation (via bugfix task)

### Out of Scope

- Running on feat_qr_data_transfer (secondary test case — could be a follow-up if time allows)
- Performance benchmarking
- Migration of all existing requirements with gaps (separate effort)

## Acceptance Criteria

- [x] task-derive-from-requ executed on REQ-PROC-001 in a fresh session
- [x] Coverage matrix correctly identifies the current uncovered AC (AC-07; AC-04 was already covered by TASK-PROC-001-10 before this run started — see Finding A in test_case_findings.md)
- [x] Existing-task covers: are repaired if any have empty fields (TASK-PROC-001-01 legacy, TASK-PROC-001-02 explore — both legitimately empty, documented in protocol)
- [x] Verification task is proposed and created (TASK-PROC-001-12)
- [x] Cross-reference completeness gate runs; any gaps are detected, classified, and fixed (2 semantic links added, 7 ignored; commits 8c0eaa33 + d48e352c)
- [x] AC-04 and AC-07 gaps in REQ-PROC-001 are closed (AC-04 already covered by TASK-PROC-001-10; AC-07 closed by new TASK-PROC-001-11)
- [x] Findings documented in `plans_and_protocols/2026-05-26_test_case_findings.md`
- [x] Any skill bugs found are reported (TASK-PROC-058-08 covers Findings D, E, F, G, H)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-058-02 | pending | task-derive-from-requ skill core must exist |
| TASK-PROC-058-03 | pending | Cross-ref completeness gate (AC-17) must exist |
| TASK-PROC-058-04 | pending | task-create plan-driven mode must exist |
| TASK-PROC-058-05 | pending | task-create-code plan-driven mode must exist |
| REQ-PROC-045 impl tasks | not yet created | Cross-ref keyword-grep script — see awaiting_note |

## Notes

User explicitly requested this be run in a FRESH session. Do not start it from within another task's session.

This task is both:
- A test (validates the skill works end-to-end against a real requirement)
- A fix (closes the REQ-PROC-001 gaps that surfaced during REQ-PROC-058 exploration)

The awaiting field is non-empty because the test depends on REQ-PROC-045's cross-ref mechanism being implemented. Once REQ-PROC-045 impl tasks are created and the script lands, this task can be unblocked. Until then, the cross-ref check may use the inline fallback documented in TASK-PROC-058-03.

If issues surface, surface them — this IS the validation step the user has been asking for. Honest findings (positive OR negative) are the deliverable.
