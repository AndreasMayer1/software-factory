---
task_id: TASK-PROC-042-06
type: impl
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
effort: S
created: 2026-04-22
started: 2026-04-22
completed: 2026-04-22
session_completed_at: 2026-04-22T18:09:44Z
session_id: df8d71b8-5982-4797-a573-9ba7f7398798
session_account: gmail
after: [TASK-PROC-042-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-05]
  sections: []
scope_description: "Wire layer_order ranking signal into the ranker using classify_layer(); run regression test comparing new output against current next_tasks.py output on the live backlog; document and accept any intentional ordering shifts"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: f65d3fca
  file: ../requirements.md
---

# Goal: Activate layer_order Ranking Signal

## Objective

Wire the `layer_order` signal into `ranker.py` so the ranking tuple uses `classify_layer()` to determine each task's layer position. Run a regression comparison against the current backlog. This is Phase C of the migration — the first behavioral change.

## Requirements Summary

AC-01 requires automatic ordering without LLM. AC-05 requires layer inference from path. This task activates those signals in the live ranker.

For complete requirements at task creation time:
```
git show f65d3fca:requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Wire `layer_order` signal: `lambda t: t['_layer']['order']` (after `classify_layer()` runs)
- Wire `layer_intra_type_rank` signal: 0 for explore, 1 for impl/bugfix (within applicable layers)
- Wire `special_flags_weight` signal: sum of matching special_flags weights from rule file (replaces hardcoded `writes_requirements` check)
- Wire `cascade_active` and `factory_urgent` flag weights
- Run `python3 scripts/next_tasks.py` on live backlog, compare output to pre-change output
- For any task that shifts position: document whether the shift is intentional (correct) or a regression

### Out of Scope
- `simulate.py` (TASK-PROC-042-07) — that is a separate tool; this task does the regression manually

## Acceptance Criteria

- [ ] `layer_order` signal active in ranking tuple
- [ ] `special_flags_weight` reads from rule file (not hardcoded)
- [ ] `cascade_active: true` tasks receive weight ~-500 boost
- [ ] `factory_urgent: true` tasks receive weight ~-1000 boost
- [ ] Regression comparison documented: list of tasks that shifted and explanation for each
- [ ] No unintentional regressions (all shifts are accepted as correct improvements)

## Dependencies

| Dependency | Notes |
|---|---|
| TASK-PROC-042-05 | classifier.py must exist and be correct |

## Notes

Full design reference: Part 3.1 Phase C, Part 3.2 ranker.py pseudocode
