# Plan: Per-flow navigation captured (TASK-PROC-032-23)

Date: 2026-06-01
Session: da204bc1-a946-4efd-a6ce-262f1855c037

## Goal

AC-38: Capture per-flow screen-to-screen navigation in `flow_navigation.yaml` inside each
participating user-flow folder. `ui-scribble-handoff-emitter` emits/maintains it;
`flutter_handoff.yaml` points to it; `ui-verify-flutter` and coding consumers read it.

## Deliverables

| File | Action | Notes |
|---|---|---|
| `.claude/schemas/flow_navigation.yaml` | CREATE | New schema for the artifact |
| `.claude/schemas/flutter_handoff.yaml` | EDIT | Add optional `flow_navigation_files` key |
| `.claude/agents/ui-scribble-handoff-emitter.md` | EDIT (via claude-modify-agent) | Add flow_navigation emission protocol |
| `.claude/agents/ui-scribble-handoff-emitter.contract.yaml` | EDIT | Add new output |
| `.claude/skills/ui-verify-flutter/SKILL.md` | EDIT (via claude-modify-skill) | Add navigation check phase |
| `.claude/skills/ui-verify-flutter/contract.yaml` | EDIT | Add flow_navigation_files as optional input |

## Design Decisions

- `flow_navigation.yaml` lives in `requirements_user_needs/user_flows/<flow_slug>/`
  (the "flow folder carries" it — AC-38)
- Emitter finds flow folder by searching for `flow.md` with matching `flow_id`
- Edges derived from `flow_positions` step ordering + COMPONENT MAPPING block triggers
- `flutter_handoff.yaml` gets a new optional `flow_navigation_files` array key
- `ui-verify-flutter` adds a Phase 1b step to discover and read `flow_navigation.yaml`
  and a navigation-check section in the comparison report

## Approach

Inline execution (no agents needed — 6 artifacts, clear shape, mechanical lookup).
