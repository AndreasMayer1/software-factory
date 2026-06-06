---
task_id: TASK-PROC-061-10
type: impl
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-06-03
expected_tool_calls: 22
skill_chain_depth: 2
after: [TASK-PROC-065-04-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-12]   # AC-12 transferred from superseded TASK-PROC-061-09 (decision-task reset folds into the local standing task)
  sections: []
scope_description: "Migrate the monthly dependency review from the remote cron routine to a local standing task that runs flutter pub outdated against the real solver; retire the cron; update REQ-PROC-061 AC-01"
release_description: ""
opus_recommended: false  # procedural migration once the date-gate primitive exists; prefer splitting over escalating if scope grows
writes_requirements: true
requirements_version:
  commit: 804bcfc0
  file: ../requirements.md
---

# Goal: Migrate the Monthly Dependency Review to a Local Standing Task

## Objective

Replace the remote `monthly-dep-review` cron routine — which fires in a cloud container
**without the Flutter SDK** and therefore proposes pub.dev `Latest` versions instead of
solver-`Resolvable` ones — with a **local standing task** that runs the real
`flutter pub outdated` in the devcontainer (where `/sdks/flutter` exists) and re-arms
itself monthly via the `not_before:` date-gate primitive. Then retire the cron and update
REQ-PROC-061 AC-01 so the requirement describes the new mechanism.

This is the fix for the root cause behind the TASK-PROC-061-05 escalation, where 7 of 16
proposed bump targets were unreachable because the "target" column was pub.dev `Latest`,
never validated against an actual `pub solve`.

## Requirements Summary

REQ-PROC-061 AC-01 requires a monthly review that "runs `flutter pub outdated` ... and
produces a grouped update proposal," triggered by "a calendar mechanism ... it does not
depend on the agent remembering to check." The current implementation (the
`monthly-dep-review` cron, set up by the completed `2026-05-26_impl_monthly-review-schedule`
task) cannot actually run `flutter pub outdated` — it has no Flutter SDK in its cloud
environment — so it violates the spirit of AC-01 (`Resolvable` is never computed). This
task makes the implementation conform: the calendar trigger becomes a `not_before`-gated
standing task that the local orchestrator runs where the toolchain is present.

For complete requirements at task creation time:
```
git show 804bcfc0:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- **Update REQ-PROC-061 AC-01 via `requ-explore`**: state that the review runs in an
  environment where the Flutter toolchain is available, so `Resolvable` (not just
  `Latest`) versions are evaluated, and that the calendar trigger is realised as a
  `not_before`-gated standing local task. (Requirement change → must route through
  `requ-explore`, not edited inline.)
- **Create the local standing review task** that: runs `flutter pub outdated` +
  the Python-manifest outdated check; evaluates candidates against REQ-PROC-056 DG1–DG4;
  writes the proposal to `automation/dependency_reviews/YYYY-MM/` reporting the
  **`Resolvable`** target column; resets the decision task to `pending` (AC-12); and
  **re-arms itself** by setting `not_before` to the 1st of the next month.
- **Retire the remote `monthly-dep-review` cron** (CronDelete) and update
  `automation/dependency_reviews/README.md` to describe the new local mechanism.
- Reconcile with the pending `2026-06-02_impl_update-cron-to-reset-decision-task` (see
  Related Tasks) — its decision-task-reset logic moves into the local standing task; the
  cron-specific work is dropped if the cron is retired.

### Out of Scope
- Designing the `not_before` primitive or its field semantics — that is
  TASK-PROC-065-04-01 (explore) and its implementation task.
- Implementing the `not_before` engine support in `next_tasks.py` /
  `orchestrate.py` / `generate_status_overview.py` — separate impl task once the AC lands.
- The actual dependency bumps for any month (those are autonomous-bump tasks like
  TASK-PROC-061-05).

## Acceptance Criteria

- [ ] REQ-PROC-061 AC-01 updated via `requ-explore` to describe local, toolchain-present
      execution evaluating `Resolvable` versions, triggered by a `not_before` standing task
- [ ] Local standing review task exists, runs real `flutter pub outdated`, and writes a
      proposal whose target column is solver-`Resolvable`
- [ ] Standing task re-arms itself to the 1st of next month via `not_before`
- [ ] Standing task resets the decision task to `pending` (preserves AC-12 behaviour)
- [ ] Remote `monthly-dep-review` cron retired; `automation/dependency_reviews/README.md`
      updated to the new mechanism
- [ ] `2026-06-02_impl_update-cron-to-reset-decision-task` reconciled (folded in or
      superseded, recorded in protocol)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-065-04-01 | pending | Date-gate primitive must be designed first (this task `after:` it) |
| `not_before` primitive **implementation** task | not yet created | Hard prerequisite — wire into `after:` once that impl task exists (created from the explore's AC) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-065-04-01](../../../../requirements_management/epic_task_lifecycle/feat_task_state_machine/tasks/2026-06-03_explore_design-not-before-date-gate-primitive/goal.md) | Predecessor — designs the `not_before` primitive this migration consumes |
| [update-cron-to-reset-decision-task](../2026-06-02_impl_update-cron-to-reset-decision-task/goal.md) | Scope boundary — that task patches the cron; this task retires the cron and moves the decision-task reset into the local standing task. Reconcile before completing. |

## Notes

The cron was registered via the `schedule` skill (CronCreate); retire it with CronDelete.
Keep the per-release dependency sweep (AC-03, `scripts/release/check_dependency_sweep.py`)
untouched — it is the safety backstop if a monthly run slips due to orchestrator dormancy.
