# Prototype Artifacts — Skill Interface Contracts Mechanism

**Task:** TASK-PROC-044-02 · **Round:** 2 (prototype)
**Date:** 2026-05-29

These are prototype artifacts demonstrating the proposed skill-interface-contracts
mechanism. They live in the task workspace, NOT in production locations. The rollout
tasks (per Round 3 synthesis) will move them to:
- `.claude/skills/<name>/contract.yaml` (one per skill)
- `.claude/schemas/<artifact>.yaml` (one per shared artifact shape)
- `scripts/quality/check_skill_contracts.py` (the lint)
- `automation/pending_feedback/<TASK_ID>/revision_target.yaml` (per revision request)

---

## Files

| File | Description |
|---|---|
| `contract_ui-create-scribble.yaml` | Contract for `ui-create-scribble`: all inputs (requirements.md, personas, T1/T2 rules, optional sketches, prior scribble version), all outputs (HTML files, metadata.yaml, feedback.md, conditional flutter_handoff.yaml), may_invoke list, quality criteria |
| `contract_code-simple.yaml` | Contract for `code-simple`: goal.md as required input (produced by task-create), conditional scribble folder input (Sketch Gate), lib/ + test/ as outputs, may_invoke list including ui-create-scribble, verify-quality, task-complete |
| `contract_task-create.yaml` | Contract for `task-create`: the PRIMARY PRODUCER of goal.md consumed by every skill; declares goal.md + plans_and_protocols/ as required outputs; references goal_metadata schema |
| `schema_scribble_metadata.yaml` | JSON-Schema-ish definition of metadata.yaml (the scribble metadata file): required keys (status, version, feature_path, contributing_requirements), optional keys (personas_applied, rules_applied, flow_positions, stale_since, pending_rules, phase_2_review_notes), status enum |
| `schema_goal_metadata.yaml` | Schema for goal.md YAML frontmatter: required fields (task_id, type, parent_requirement, status, created), optional fields (effort, urgency, impact, covers, opus_recommended, target_package, etc.), with enums and patterns |
| `check_skill_contracts.py` | Lint script (≤80 lines, Python 3.10+, PyYAML only): walks contract_*.yaml files, cross-references derived_from paths against produces paths across skills, checks may_invoke references against existing SKILL.md files, exits 1 on violations with specific actionable error messages |
| `lint_demo_run.md` | Demonstration of the lint catching a real violation: clean run, injected violation (scribble folder rename), violation output with exact quoted error, revert, re-verify |
| `example_revision_target.yaml` | Demo of the bidirectional-feedback channel — hypothetical `automation/pending_feedback/TASK-FUNC-007-15/revision_target.yaml` from ui-verify-flutter requesting ui-create-scribble regenerate a scribble with corrected Flutter component |

---

## Key design decisions demonstrated

- **Contract format**: sidecar `contract.yaml` per skill (zero token cost at invocation — L3 loading per Anthropic progressive disclosure)
- **Field set**: PRINCE2-aligned 4 fields — `purpose`, `derived_from`, `produces`, `quality_criteria` — plus operational `may_invoke`, `side_effects`, `contract_version`
- **Optional vs required sub-blocks**: explicit `required:` and `optional:` within `derived_from` and `produces` (rejects OpenAI strict-mode "everything required" rigidity)
- **Shared schemas**: `.claude/schemas/<artifact>.yaml` for shapes used across multiple skills
- **source: external annotation**: opt-out marker for developer-owned inputs that bypass cross-reference checking
- **Revision channel**: nested under `pending_feedback/{TASK_ID}/` with `responder_required: human | skill | either` discriminator (Magentic pattern)
