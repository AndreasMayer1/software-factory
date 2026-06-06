---
task_id: TASK-PROC-044-02-07
type: impl
parent_requirement: REQ-PROC-044-02
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-06-02
started: 2026-06-02
completed: 2026-06-02
after: [TASK-PROC-044-02-06]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Audit all existing skill and agent contracts, identify those with developer decision checkpoints, and add user_input_gates: sections validated against the schema"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: abd72adf
  file: ../requirements.md
---

# Goal: Migrate Skill Contracts to Declare User Input Gates

## Objective

Populate the `user_input_gates:` index by auditing every existing `.claude/skills/*/contract.yaml` and `.claude/agents/*.contract.yaml`, identifying skills and agents that have developer decision checkpoints (approval gates, revision loops, selection prompts, path selections, free-text inputs), and adding a `user_input_gates:` section to each. All added entries must be valid against `.claude/schemas/user_input_gate.yaml`.

## Requirements Summary

REQ-PROC-044-02 AC-07–09 define the schema, index script, and registry token for `user_input_gates:`. This task performs the adoption sweep that makes the index meaningful: without declared gates across the full contract set, `render_user_input_gates.py` only shows the two reference implementations seeded by TASK-PROC-044-02-06.

The requirement explicitly defers this migration to incremental adoption (not an AC itself), but the index only fulfills its purpose — making the complete human-in-the-loop surface visible — once all contracts with decision checkpoints have declared them.

For complete requirements at task creation time:
```
git show abd72adf:requirements_tasks/process/AI_rules/epic_factory_quality/feat_artifact_model/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- Audit all `.claude/skills/*/contract.yaml` and `.claude/agents/*.contract.yaml` for developer decision checkpoints
- For each contract with checkpoints: add a `user_input_gates:` section with entries conforming to `.claude/schemas/user_input_gate.yaml`
- Validate all added entries pass `scripts/quality/check_skill_contracts.py` (the schema lint extension from TASK-PROC-044-02-06)
- Verify `scripts/factory/render_user_input_gates.py` produces a complete, accurate index after migration

### Out of Scope

- Changing how any skill implements its checkpoints (this task declares, not redesigns)
- Creating new checkpoints or removing existing ones
- Updating SKILL.md prose (only contract.yaml is modified)

## Acceptance Criteria

- [x] Every skill and agent contract with developer decision checkpoints has a `user_input_gates:` section
- [x] All declared entries are valid per `scripts/quality/check_skill_contracts.py` (zero schema violations)
- [x] `scripts/factory/render_user_input_gates.py` runs without error and the index reflects the full migrated set

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-02-06 | pending | Schema, lint extension, and reference implementations must exist before migration begins |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-044-02-06](../2026-06-02_impl_user-input-gate-schema-and-index/goal.md) | Predecessor — provides the schema, lint, index script, and two reference implementations this task builds on |
