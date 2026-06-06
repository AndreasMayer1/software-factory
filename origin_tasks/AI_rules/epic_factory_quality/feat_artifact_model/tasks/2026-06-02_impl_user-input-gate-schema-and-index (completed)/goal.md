---
task_id: TASK-PROC-044-02-06
type: impl
parent_requirement: REQ-PROC-044-02
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: S
created: 2026-06-02
started: 2026-06-02
completed: 2026-06-02
after: [TASK-PROC-041-04-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-07, AC-08, AC-09]
  sections: []
scope_description: "Create user_input_gate schema, render_user_input_gates.py index script, add user-input-gate registry token, extend contract lint to validate user_input_gates entries"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: abd72adf
  file: ../requirements.md
---

# Goal: User Input Gate Schema, Index Script, and Registry Token

## Objective

Make every developer-decision checkpoint declared in skill and agent contracts discoverable and validated. This means creating the schema that defines what a `user_input_gates` entry must look like, the registry token that names the class, the script that renders the flat index of all declared gates, and the lint extension that rejects malformed entries.

## Requirements Summary

REQ-PROC-044-02 AC-07–09 (added 2026-06-02) define a governed contract field `user_input_gates:` for skill and agent contracts. Three deliverables are required:

- **AC-07**: `.claude/schemas/user_input_gate.yaml` — schema for a gate entry; contract lint enforces it
- **AC-08**: `scripts/factory/render_user_input_gates.py` — renders the flat index from all contracts
- **AC-09**: `user-input-gate` token in `.factory/registry/artifacts.yaml`

For complete requirements at task creation time:
```
git show abd72adf:requirements_tasks/process/AI_rules/epic_factory_quality/feat_artifact_model/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `.claude/schemas/user_input_gate.yaml`: JSON Schema (YAML format) with required fields `phase`, `description`, `decision_kind` (enum: `approval`, `revision`, `selection`, `path-selection`, `free-text`), `required` (enum: `always`, `conditional`)
- `scripts/factory/render_user_input_gates.py`: reads all `.claude/skills/*/contract.yaml` and `.claude/agents/*.contract.yaml`, collects `user_input_gates` entries, writes a Markdown table (columns: skill, phase, description, decision_kind, required); exits non-zero on schema violation
- `.factory/registry/artifacts.yaml`: append `user-input-gate` token (category: `factory-skills`, path: `.claude/schemas/user_input_gate.yaml`)
- `scripts/quality/check_skill_contracts.py`: extend to validate any `user_input_gates` section against the schema — malformed entry is a FAIL, same severity as an unresolved `produces:` token
- Two existing contracts already mention approval gates in prose (`ux-write-persona`, `ux-write-scenario` quality_criteria): add `user_input_gates:` sections to both as the reference implementation
- `.claude/skills/claude-create-skill/SKILL.md` and `.claude/skills/claude-modify-skill/SKILL.md` updated so their Artifact-Establishment Gate also covers `user_input_gates:` entries — validating each entry against `.claude/schemas/user_input_gate.yaml` before writing to a contract, using the same interactive/automated branching already established for token registration

### Out of Scope
- Migrating all 37+ skills that have approval gates (adoption is incremental; the two reference implementations above seed the index)
- Changes to how existing `produces:` / `derived_from:` lint works
- Interactive-mode `feedback-checkpoint` authoring (TASK-PROC-041-04-03)

## Acceptance Criteria

- [x] AC-07: `.claude/schemas/user_input_gate.yaml` exists and the contract lint rejects any `user_input_gates` entry missing a required field or using an out-of-vocabulary value
- [x] AC-08: `scripts/factory/render_user_input_gates.py` runs without error and produces a Markdown table listing all declared gates across skill and agent contracts
- [x] AC-09: `user-input-gate` token is present in `.factory/registry/artifacts.yaml` with correct category and path
- [x] AC-10: Both `claude-create-skill/SKILL.md` and `claude-modify-skill/SKILL.md` guide authors to validate `user_input_gates:` entries against the schema before writing to a contract, consistent with how the Artifact-Establishment Gate handles `produces:` tokens

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-041-04-03 | pending | Adds `feedback-checkpoint` registry token in the same session — read that work first to stay consistent with the registry append pattern |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-041-04-03](../../../../workflows/epic_autonomous_task_execution/feat_feedback_pause_resume/tasks/2026-06-02_impl_archive-answered-feedback-to-task-protocols/goal.md) | Predecessor — also appends a registry token; run before this task to avoid registry conflicts |
| [TASK-PROC-044-02-02](../2026-05-31_impl_artifact-token-resolve-lint%20(completed)/goal.md) | Predecessor — created the contract lint this task extends |

## Notes

Standalone-override: user explicitly requested this task for AC-07–09 rather than routing through task-derive-from-requ. The remaining ACs (AC-01–06) are already covered by completed tasks.

The `render_user_input_gates.py` script follows the same tier-B pattern as `scripts/quality/check_skill_contracts.py` and `scripts/factory/render_factory_map.py`. Read those for the code style and tier annotation convention before writing.
