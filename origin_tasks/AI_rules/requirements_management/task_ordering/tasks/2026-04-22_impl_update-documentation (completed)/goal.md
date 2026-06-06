---
task_id: TASK-PROC-042-11
type: impl
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
effort: XS
created: 2026-04-22
started: 2026-04-23
completed: 2026-04-23
session_completed_at: 2026-04-23T19:18:35Z
session_id: 74b6f017-ef4c-4997-930d-124173825752
session_account: gmail
after: [TASK-PROC-042-10]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Update CLAUDE.md §10 to reference scripts/task_ordering/ and .claude/task_ordering_rules.yaml; update factory_flows.md to reflect new task-ordering path; update INDEX.md to include claude-modify-ordering-rules skill"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: f65d3fca
  file: ../requirements.md
---

# Goal: Update Documentation

## Objective

Final documentation pass after all implementation tasks are complete. Update the three reference documents that need to reflect the new task ordering infrastructure.

## Requirements Summary

Cross-cutting documentation update to keep CLAUDE.md, factory_flows.md, and INDEX.md in sync with the new ordering system.

For complete requirements at task creation time:
```
git show f65d3fca:requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `CLAUDE.md §10` (Generated Files table): add row for `scripts/task_ordering/` module and note for `.claude/task_ordering_rules.yaml`; add `scripts/propose_after.py` as a query script
- `.claude/factory_flows.md`: update the task-ordering section to reflect the new rule-file-driven flow; add `claude-modify-ordering-rules` as a skill in the factory flow
- `.claude/skills/INDEX.md`: add entry for `claude-modify-ordering-rules` with correct description and layer classification

### Out of Scope
- Any code changes — this task is documentation only

## Acceptance Criteria

- [ ] CLAUDE.md §10 table includes `scripts/task_ordering/` and `.claude/task_ordering_rules.yaml`
- [ ] CLAUDE.md §10 table includes `scripts/propose_after.py` as a query script
- [ ] `factory_flows.md` reflects the rule-file-driven ordering flow
- [ ] `INDEX.md` includes `claude-modify-ordering-rules` skill entry
- [ ] `.claude/task_ordering_priority_override.txt` is deleted (bootstrap override no longer needed)

## Dependencies

| Dependency | Notes |
|---|---|
| TASK-PROC-042-10 | Skill must exist before INDEX.md can be updated |
