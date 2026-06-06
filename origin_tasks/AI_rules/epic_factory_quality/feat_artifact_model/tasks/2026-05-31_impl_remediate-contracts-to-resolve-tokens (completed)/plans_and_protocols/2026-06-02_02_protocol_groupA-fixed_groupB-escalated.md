---
task_id: TASK-PROC-044-02-03
session_id: 8763f2da-6d20-4603-aeac-a2531f8775cd
agent_id: main-session
date: 2026-06-02
skills_used: [task-resolve, claude-automated-mode]
---

# Protocol: Group A fixed mechanically, Group B escalated for token ratification

## Starting state

Prior session (024e6dea) ran the bulk path→token substitution across 71 contract
files (uncommitted in working tree) but terminated before resolving the residual
violations. On entry the resolve lint reported **87 unbaselined violations**:
- 73 contract-side (`produces:` / `derived_from:` / `consumes:`) — in scope (AC-02)
- 14 agent-name — OUT of scope (AC-03, owned by REQ-PROC-044-01 rename work)

## Root cause of the 73 contract violations — two groups

### Group A (63 violations): lost space before inline `#` annotation
The prior session's bulk transform replaced `path: <literal>  # comment` with
`<token># comment` — collapsing the two spaces before `#`. Without whitespace before
`#`, YAML does not treat it as a comment, so the parsed value became the literal
string `"<token># comment"` instead of `"<token>"`. Every prefix was a valid registry
token (goal, guideline, source, protocol, plan, test, …); only the spacing was wrong.

**Fix (mechanical, no new tokens):**
```
perl -i -pe 's/(- |: )([a-z][a-z0-9-]*)#/$1$2  #/g' \
  .claude/skills/*/contract.yaml .claude/agents/*.contract.yaml
```
Restored the two-space gap before `#` (matching the original style). Verified all 22
unique token prefixes resolve to registry tokens before applying. Result: 73 → 10.

### Group B (10 violations): genuinely-new tokens — REQUIRES establishment gate
These are literal filesystem paths with no existing registry token. Per AC-02 and
REQ-PROC-044-01's establishment gate (requirements.md §Behavior: "an authoring skill
eagerly proposes a registry entry the developer ratifies … before authoring
proceeds"), new tokens MUST be developer-ratified — no silent appends. In automated
mode this is a `pending_feedback` escalation.

| # | Literal path | Contract(s) | Proposed token | Category |
|---|---|---|---|---|
| 1 | `automation/.automated_mode` | claude-automated-mode, claude-autorun | `automation-sentinel` | automation |
| 2 | `automation/orchestrate.log` | claude-autorun | `automation-log` | automation |
| 3 | `automation/MONITORING_CRITERIA.md` | claude-autorun | `automation-criteria` | automation |
| 4 | `automation/.monitoring_cron_id` | claude-autorun | `automation-cron` | automation |
| 5 | `.devcontainer/devcontainer.json` | claude-install-os-tool | `devcontainer` | environment (NEW category) |
| 6 | `pubspec.yaml` | code-complex | `pubspec` | environment (NEW category) |
| 7 | `.claude/schemas/flutter_handoff.yaml` | ui-scribble-handoff-emitter | `schema` (or remove line — see note) | factory-skills |
| 8 | `.claude/schemas/flow_navigation.yaml` | ui-scribble-handoff-emitter | `schema` (or remove line — see note) | factory-skills |

Note on #7/#8: in `ui-scribble-handoff-emitter` these appear as bare `derived_from`
list items, but they are the *schemas* of the artifacts the agent produces
(`handoff`, `flow-navigation`), not upstream artifacts it consumes. Two honest
resolutions: (a) add a `schema` token and keep them, or (b) drop the two lines
(the schema relationship is already implied by the produced tokens). Presented to
the developer as a choice in the escalation.

## Status at escalation
- Lint: 10 contract violations remaining (all Group B), 14 agent-name (out of scope).
- Escalated via `automation/pending_feedback/TASK-PROC-044-02-03/question.md`.
- Cannot complete the task until tokens are ratified; resuming session will add the
  approved tokens to `.factory/registry/artifacts.yaml`, fix the 10 contract entries,
  verify zero contract-side violations, and complete.
