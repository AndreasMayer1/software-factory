---
task_id: TASK-PROC-061-09
type: impl
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: superseded
superseded_by: TASK-PROC-061-10
superseded_date: 2026-06-03
superseded_reason: "Cron is being retired (it runs without the Flutter SDK and proposes Latest, not Resolvable). The decision-task reset (AC-12) moves into the local standing review task built by TASK-PROC-061-10. Patching a soon-to-be-retired cron is throwaway work."
effort: S
created: 2026-06-02
expected_tool_calls: 15
writes_requirements: false
covers:
  acceptance_criteria: []   # AC-12 coverage transferred to TASK-PROC-061-10 (see superseded_reason)
  sections: []
scope_description: "Update monthly-dep-review cron routine to reset the standing decision task (TASK-PROC-061-08) to pending after writing its proposal"
release_description: ""
opus_recommended: false
after: []
requirements_version:
  commit: 676c488f
  file: ../requirements.md
---

# Goal: Update Monthly Review Cron to Reset the Decision Task

> **⚠ SUPERSEDED 2026-06-03 by TASK-PROC-061-10.** Do not execute this task.
> The `monthly-dep-review` cron this task would patch is being **retired**: it fires in a
> cloud container without the Flutter SDK and proposes pub.dev `Latest` instead of
> solver-`Resolvable` versions (root cause of the TASK-PROC-061-05 escalation). The
> AC-12 behaviour this task targets — resetting the decision task to `pending` each cycle
> — is folded into the **local standing review task** built by
> `../2026-06-03_impl_migrate-monthly-review-to-local-standing-task/goal.md`.
> **Interim coverage note:** AC-12 stays unimplemented until the migration lands (gated on
> the `not_before` primitive, TASK-PROC-065-04-01). If that chain proves slow and an
> interim AC-12 fix is wanted, the developer can revive this task as a stop-gap cron patch.

## Objective

Update the `monthly-dep-review` Claude Code cron routine
(routine ID: `trig_01B9kRzpFAbiFSTvfN4K2Dng`, managed at https://claude.ai/code/routines/trig_01B9kRzpFAbiFSTvfN4K2Dng)
so that after it writes `automation/dependency_reviews/YYYY-MM/proposal.md`, it also sets
`TASK-PROC-061-08` to `status: pending` in its `goal.md` frontmatter and commits that change.

This implements REQ-PROC-061 AC-12: the decision task is reset to pending automatically
each cycle — the developer does not need to remember.

## Requirements Summary

AC-12 (added 2026-06-02): after each monthly batch review, the designated reusable decision
task in `dependency_lifecycle/tasks/` is set to `status: pending` by the agent that completes
the review.

Current gap: the `monthly-dep-review` cron (set up by TASK-PROC-061-02) writes the proposal
and commits it, but does NOT reset the decision task. The standing task
`2026-06-02_explore_review-monthly-dep-proposal-and-authorize/goal.md` (TASK-PROC-061-08)
was created by this session but the cron has no instruction to reset it monthly.

For complete requirements at task creation time:
```
git show 676c488f:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- Update the `monthly-dep-review` routine prompt (via the `schedule` skill or direct API)
  to add a final step after writing the proposal:
  1. Edit `requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/tasks/2026-06-02_explore_review-monthly-dep-proposal-and-authorize/goal.md`
     — set `status: pending` in YAML frontmatter
  2. Commit the change with a message like `chore(REQ-PROC-061): reset decision task to pending for YYYY-MM cycle`
- Update `automation/dependency_reviews/README.md` to document that the cron also resets the decision task

### Out of Scope

- Changing any other aspect of the cron's behavior
- Modifying how the proposal is written or evaluated
- Changes to `lib/`, `test/`, or `integration_test/`

## Acceptance Criteria

- [ ] The `monthly-dep-review` cron routine prompt includes the step to set TASK-PROC-061-08 to `status: pending` after writing the proposal
- [ ] The routine commits the status reset as a separate step (or appended to the proposal commit)
- [ ] `automation/dependency_reviews/README.md` documents the task-reset behavior
- [ ] The routine ID and manage-at URL are preserved in the updated protocol

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-061-08 | pending | The standing task must exist before the cron can reference it by path |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-061-02](../2026-05-26_impl_monthly-review-schedule%20(completed)/goal.md) | Predecessor — this task was set up by TASK-PROC-061-02; update builds on that work |
| [TASK-PROC-061-08](../2026-06-02_explore_review-monthly-dep-proposal-and-authorize/goal.md) | Target — the decision task that this cron update will reset to pending each cycle |
| [TASK-PROC-061-10](../2026-06-03_impl_migrate-monthly-review-to-local-standing-task/goal.md) | Supersedes this task — retires the cron and folds the decision-task reset (AC-12) into the local standing review task |

## Notes

The cron routine uses `schedule` skill conventions. Use `schedule` skill to update the routine,
or use the Claude AI routines web interface if the skill does not support in-place prompt editing.
The routine's model (claude-sonnet-4-6) and cron expression (`0 9 1 * *`) should not change.
