---
task_id: TASK-PROC-042-02
type: impl
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-04-22
session_completed_at: 2026-04-22T17:09:18Z
effort: S
created: 2026-04-22
started: 2026-04-22
session_id: 6871a5b4-ed73-4658-811c-6fe98631fda6
session_account: web
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-11, AC-12]
  sections: []
scope_description: "Create .claude/task_ordering_rules.yaml encoding current next_tasks.py behavior as the initial rule set, including all special flags (writes_requirements, factory_urgent, cascade_active, scribble_task), rationale: and rationale_source: fields on every ranking_signals entry, and the full layer taxonomy from the Opus design"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: f65d3fca
  file: ../requirements.md
---

# Goal: Create Task Ordering Rules YAML

## Objective

Create `.claude/task_ordering_rules.yaml` as the initial rule file for the task ordering engine. The file must encode the current `next_tasks.py` behavior as its starting point so the engine produces identical output when the rule file is first loaded.

## Requirements Summary

REQ-PROC-042 requires task ordering rules to be captured in an explicit, editable rule set (AC-02). The rule file must include `rationale:` and `rationale_source:` fields on every `ranking_signals` entry (AC-12), and introduce `factory_urgent: true` as a special flag (AC-11).

For complete requirements at task creation time:
```
git show f65d3fca:requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Full layer taxonomy (10 layers, sparse integer ordering) as specified in the Opus design (Part 1)
- All special flags: `writes_requirements`, `factory_urgent` (~-1000), `cascade_active` (~-500), `scribble_task`, `verification_task`, `opus_recommended`, `cascade_type`
- All ranking signals with `rationale:` and `rationale_source:` fields (see §10.8 and §10.1 of design doc for rationale content)
- All dependency heuristics
- Fallback behavior section
- Schema version: "1.0"

### Out of Scope
- The evaluation engine (TASK-PROC-042-03 through TASK-PROC-042-06)
- The `simulate.py` or `validate_rules.py` CLIs — those come later

## Acceptance Criteria

- [ ] `.claude/task_ordering_rules.yaml` exists and is valid YAML
- [ ] All 10 layers present with correct `order` values (0, 10, 20, 30, 40, 45, 50, 55, 60, 70)
- [ ] Special flags include `factory_urgent` (weight ~-1000) and `cascade_active` (weight ~-500)
- [ ] Every `ranking_signals` entry has `rationale:` and `rationale_source:` fields populated
- [ ] `rationale_source` for `current_package_scope` references "user decision, 2026-04-22" and §10.1 of the design doc
- [ ] `scribble_task: true` flag present with layer classification effect documented
- [ ] `schema_version: "1.0"` present in frontmatter

## Dependencies

None — this task has no predecessor tasks.

## Notes

Full design reference: `tasks/2026-04-22_explore_intelligent-task-ordering/plans_and_protocols/2026-04-22_02_opus_design.md`
- Part 1: Layer taxonomy
- Part 2: Draft rule file (use as starting template)
- §10.1–§10.9: User decisions that must be reflected in rationale fields
