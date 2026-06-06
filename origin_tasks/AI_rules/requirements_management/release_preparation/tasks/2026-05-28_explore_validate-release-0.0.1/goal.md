---
task_id: TASK-PROC-035-20
type: explore
parent_requirement: REQ-PROC-035
urgency: 4
urgency_reason: U4-PLAN
impact: 4
impact_reason: I4-QUAL
status: pending
effort: XS
created: 2026-05-28
after: ["TASK-PROC-035-17"]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Orchestration: run structural validation for release 0.0.1 (all packages covered)."
target_release: "0.0.1"
release_description: ""
task_type: "validate"
orchestration_task: true
plan_path: "requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-04-25_explore_release-begin-impl-0.0.1 (completed)/task_creation_plan.md"
opus_recommended: false
requirements_version:
  commit: a57fca07
  file: ../requirements.md
---

# Goal: Structural Validation for Release 0.0.1

## Objective

Run structural validation for release 0.0.1: AC coverage, after-chains,
target_package, opus_recommended flags. Write `validation_report.md`. Call `task-complete`.

All packages for release 0.0.1 are now covered by implementation tasks.
This task performs automated quality checks before the user runs `/release-begin-impl-finalize`.

## Acceptance Criteria

- [ ] Run `python3 scripts/artifacts/generate_status_overview.py --release 0.0.1` and verify ≥1 non-terminal impl task exists per package. If ANY package has 0 impl tasks: write `validation_report.md` with a PREMATURE_TRIGGER section (list missing packages, count of tasks created vs expected from plan_path), then STOP — do NOT proceed to the remaining ACs. Call `task-complete`.
- [ ] Run `python3 scripts/tasks/check_task_against_plan.py` for each impl task in release 0.0.1; write results to `validation_report.md`
- [ ] Run `python3 scripts/tasks/reconcile_after_chains.py --release 0.0.1` (detect only, no --apply); append findings to `validation_report.md`
- [ ] Verify all impl tasks have `target_package` set; list any missing in `validation_report.md`
- [ ] Write `validation_report.md` to the explore task folder for release 0.0.1 (path from RELEASES.md)
- [ ] Call `task-complete` on this validation orchestration task (TASK-PROC-035-20)

## Notes

`validation_report.md` is the handoff document for the next step.

**If all packages have impl tasks (normal case)**: the report is the handoff for `/release-begin-impl-finalize`. Every failure entry must include: task ID, expected vs. actual value, and remediation command. Semantic correctness is NOT in scope — that belongs to `release-begin-impl-finalize` Phase 3.

**If this task was triggered prematurely (PREMATURE_TRIGGER in report)**: the orchestration chain was broken. The impl tasks were never created. Do NOT run `/release-begin-impl-finalize`. Instead: check `plan_path` for the approved task creation plan, then either (a) re-run `python3 scripts/tasks/create_orchestration_task.py --plan-path <plan_path>` to restart the chain, or (b) run `/release-begin-impl` again for the same release (choose "Resume" when prompted).
