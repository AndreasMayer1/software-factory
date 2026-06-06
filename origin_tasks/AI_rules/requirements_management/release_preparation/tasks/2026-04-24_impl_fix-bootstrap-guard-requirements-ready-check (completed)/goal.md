---
task_id: TASK-PROC-035-05
type: impl
parent_requirement: REQ-PROC-035
urgency: 4
urgency_reason: U4-PLAN
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-04-24
started: 2026-04-24
completed: 2026-04-24
after: []
awaiting: []
awaiting_note: ""
target_package: "Transfer Data Model"
covers:
  acceptance_criteria: []
  sections: [SEC-05]
scope_description: "Fix the bootstrap guard in claude-automated-mode: replace the empty-task-list check with a deterministic script (check_requirements_ready.py) that verifies at least one writes_requirements:true task was completed and none are currently pending. Update SEC-05 wording and monitoring criteria."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: b1ea3b31
  file: ../requirements.md
---

# Goal: Fix Bootstrap Guard — Requirements-Ready Script

## Objective

The bootstrap rule in `claude-automated-mode` (Case A) never fires in a mature project because
Case D (any runnable tasks exist) permanently preempts it. The root cause is that the guard checks
for an empty task list, but unrelated process/maintenance explore tasks always keep the list
non-empty.

Implement the recommended fix from TASK-PROC-035-04: replace the empty-task-list check with a
deterministic Python script `check_requirements_ready.py` that verifies requirements are actually
ready before allowing impl task creation.

## Background

See TASK-PROC-035-04 findings:
`requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-04-24_explore_investigate-bootstrap-vs-orchestrator-interaction (completed)/plans_and_protocols/2026-04-24_01_protocol_findings.md`

Key findings:
- Case A fires only when task list is empty — never happens in mature project
- Git evidence: chain broke after TASK-PROC-035-03 (2026-04-22); TASK-PROC-042 tasks blocked Case A
- Fix: Case A should fire when `check_requirements_ready.py` exits 0, regardless of other task types
- The check must be a deterministic script (not LLM-evaluated)

## Scope

### In Scope

1. **Write `scripts/check_requirements_ready.py`**:
   - Exit 0 (ready): at least one task with `writes_requirements: true` has `status: completed`
     AND no task with `writes_requirements: true` has `status: pending` or `in_progress`
   - Exit 1 (not ready): print human-readable reason
   - The script should be release-aware if possible (filter by tasks whose parent requirement is
     assigned to the active release), but a global check is acceptable as a first implementation
   - Edge case: if NO `writes_requirements: true` task has EVER been created, exit 1 with message
     "No requirements-authoring tasks found — requirements may not have been formally authored"

2. **Update `claude-automated-mode/skill.md` Case A**:
   - Replace the current condition ("task list is empty — no numbered task lines found")
   - New condition: `python3 scripts/check_requirements_ready.py` exits 0 AND output contains
     "UNCOVERED ACs"
   - Keep inner bootstrap logic (duplicate check + create orchestration task + terminate) unchanged

3. **Update `requirements_tasks/process/AI_rules/requirements_management/release_preparation/requirements.md` SEC-05**:
   - Replace guard paragraph wording per TASK-PROC-035-04 section 4.2
   - Fix stale naming: replace `task-create-impl` with `task-create-code`

4. **Update `automation/MONITORING_CRITERIA.md`**:
   - S11: append note about expected behaviour when writes_requirements tasks are pending
   - S21: append note that bootstrap may fire even with explore tasks in queue (as long as none
     have `writes_requirements: true` pending)

### Out of Scope

- Making the script release-scoped (global check is sufficient for v1)
- Handling "grandfathered" requirements authored before the `writes_requirements` flag existed
  (document as a known limitation in the script's docstring)
- Changing `next_tasks.py` ranking logic
- Changing `task-create-code-orchestrator` skill (manual path creates tasks directly, no guard needed)

## Acceptance Criteria

- [ ] `scripts/check_requirements_ready.py` exists and exits 0/1 correctly based on writes_requirements task states
- [ ] Script prints a clear reason on exit 1
- [ ] `claude-automated-mode` Case A calls the script instead of checking for an empty task list
- [ ] Case A still checks for "UNCOVERED ACs" in `next_tasks.py` output (unchanged)
- [ ] Case A inner logic (duplicate check, create orchestration task, terminate) unchanged
- [ ] REQ-PROC-035 SEC-05 guard paragraph updated with correct wording
- [ ] `task-create-impl` renamed to `task-create-code` in SEC-05
- [ ] `MONITORING_CRITERIA.md` S11 and S21 updated with post-fix behaviour notes

## Notes

The grandfathered-requirements edge case (requirements authored before `writes_requirements` flag
existed) is a known limitation. Document it in the script as a TODO comment. It can be addressed
in a follow-up task if needed.
