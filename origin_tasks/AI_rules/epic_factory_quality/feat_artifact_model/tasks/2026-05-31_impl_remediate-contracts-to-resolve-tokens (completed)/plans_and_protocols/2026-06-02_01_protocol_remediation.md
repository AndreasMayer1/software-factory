---
task_id: TASK-PROC-044-02-03
session_id: 024e6dea-be68-4b65-9d5f-d67828b57b6e
agent_id: main-session
date: 2026-06-02
skills_used: [task-resolve]
---

# Protocol: Remediate contracts to resolve to registry tokens

## Findings

Ran the resolve lint: **449 unbaselined violations** across 66 skill contracts and 9 agent contracts.

The registry exists at `.factory/registry/artifacts.yaml` with ~50 tokens.

## Root Cause

All existing `contract.yaml` files use literal file paths (e.g. `automation/state.json`) in
their `produces`/`derived_from` fields. The registry expects those values to be token KEYS
(e.g. `automation-state`). No contracts have been updated yet since TASK-PROC-044-02-01
created the registry.

## Strategy

Three categories of violations:

1. **Token substitution** (~420 violations): path maps to an existing token → replace
   `path: <literal>` with `path: <token-name>` in each contract
2. **Remove from contract** (~10 items): too-generic or external entries that have no
   meaningful artifact token (e.g. `<any file relevant to the question>`, external JSONL files,
   in-memory results, CLI command strings)
3. **New tokens needed** (~19 violations, 7 token types): paths with no existing token that
   represent genuine artifact types requiring developer ratification

## New tokens proposed (pending ratification)

| Proposed token | Path | Category |
|---|---|---|
| `automation-sentinel` | `automation/.automated_mode` | automation |
| `automation-criteria` | `automation/MONITORING_CRITERIA.md` | automation |
| `automation-cron` | `automation/.monitoring_cron_id` | automation |
| `automation-log` | `automation/orchestrate.log` | automation |
| `devcontainer` | `.devcontainer/devcontainer.json` | new: environment |
| `pubspec` | `pubspec.yaml`, `pubspec.lock` | new: environment |
| `schema` | `.claude/schemas/*.yaml` | factory-skills |

## Implementation plan

**Phase 1** (this session): Run a batch transformation script on all contracts:
- Skill contracts: replace `path:` values in produces/derived_from blocks
- Agent contracts: replace plain string list items in produces/derived_from/consumes
- Remove unresolvable entries (generic, external, in-memory)

**Phase 2** (this session): Escalate via pending_feedback for new token approval (7 tokens).

**Phase 3** (after developer approval): Add new tokens to registry, fix remaining ~19 violations,
verify zero, complete task.

## Key mapping decisions

- `automation/pending_feedback/TEMPLATE_answer.md` → `pending-answer` (same family)
- `requirements_user_needs/README_*.md` → `guideline` (process guidelines)
- `requirements_user_needs/CHANGE_PROPAGATION.md` → `guideline` (process guideline)
- `requirements.md` (root) → `requirements` (requirements content family)
- `requirements_tasks/_meta/dependency_map.md` → `id-registry` (meta artifact)
- `.claude/task_ordering_rules.yaml.proposed` → `task-ordering` (same artifact family)
- `doc/` directories → `guideline` (all doc content)
- `<deliverable path from goal.md>` → `protocol` (task-resolve produces work artifacts)
- `<target artifact> (inline ##...)` → `value-tradeoff` (vcd-log primary output)
- `lib/** test/**` (combined single string) → `source` (approximate)
- `requirements_tasks/**` (broad glob) → `requirements` (approximate)
- `requirements_user_needs/**` (broad glob) → `persona` (approximate)
- `pubspec.lock` → `pubspec` (same new token as pubspec.yaml)
- `requirements_tasks/SKETCHES_README.md` → `guideline`
- `.claude/schemas/*.yaml` → `schema` (new token)

## Items to remove from contracts

- `<any file relevant to the question>` (claude-ask — genuinely dynamic)
- `/home/vscode/.ccs/instances/*/agent-*.jsonl` (claude-resume-agent — external)
- `<output file path from task notification>` (claude-resume-agent — too generic)
- `external web sources` (opus-advisor — not a file)
- `inline analysis` (opus-advisor — not a file)
- `git diff --name-only` (quality-checker — CLI output, not a file)
- `STATUS line` (quality-checker — not a file)
- `flow_context (passed by caller as string)` (ui-scribble-generator — runtime param)
- `flow_scope (passed by caller as array)` (ui-scribble-generator — runtime param)
- `implementation_notes content (passed by caller as string, optional)` (ui-scribble-generator — param)
