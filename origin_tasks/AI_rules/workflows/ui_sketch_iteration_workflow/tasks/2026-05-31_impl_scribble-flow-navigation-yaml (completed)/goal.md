---
task_id: TASK-PROC-032-23
type: impl
parent_requirement: REQ-PROC-032-03
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-06-01
completed: 2026-06-02
session_completed_at: 2026-06-02T00:17:21Z
effort: M
created: 2026-05-31
after: [TASK-PROC-044-01-01, TASK-PROC-044-02-01, TASK-PROC-044-01-04, TASK-PROC-044-01-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-15]
  sections: []
scope_description: "ui-scribble-handoff-emitter emits and maintains a per-flow flow_navigation.yaml (edges, triggers, escape paths, back-stack policy) in each participating flow folder; add a schema; flutter_handoff.yaml points to it; ui-verify-flutter and the coding consumer read it to verify and implement navigation."
release_description: ""
opus_recommended: false
requirements_version:
  commit: 6ece1dc7
  file: ../requirements.md
session_id: da204bc1-a946-4efd-a6ce-262f1855c037
session_account: web
---
# Goal: Per-flow navigation captured (flow_navigation.yaml)

## Objective

For each user flow a scribble participates in, capture that flow's screen-to-screen navigation
in a `flow_navigation.yaml` in the flow folder: edges (which screen leads to which), the trigger
for each edge, escape paths, and the back-stack policy. `ui-scribble-handoff-emitter` emits and
keeps this file current; `flutter_handoff.yaml` points to the relevant `flow_navigation.yaml`
file(s); `ui-verify-flutter` and the coding consumer read it to verify and implement navigation. [AC-38]

## Requirements Summary

Covers AC-38: per-flow `flow_navigation.yaml` describing edges/triggers/escape-paths/back-stack;
emitted and kept current by `ui-scribble-handoff-emitter`; `flutter_handoff.yaml` points to it;
consumed by `ui-verify-flutter` and the coding consumer.

For complete requirements at task creation time:
```
git show 6ece1dc7:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `ui-scribble-handoff-emitter` emits and maintains `flow_navigation.yaml` in each participating
  flow's folder (edges, per-edge trigger, escape paths, back-stack policy).
- A schema for `flow_navigation.yaml` under `.claude/schemas/`.
- `flutter_handoff.yaml` points to the relevant `flow_navigation.yaml` file(s); update
  `.claude/schemas/flutter_handoff.yaml` accordingly.
- `ui-verify-flutter` and the coding consumer read `flow_navigation.yaml` to verify and
  implement navigation.

### Out of Scope
- Per-flow walk validation (AC-39), approval trail (AC-40), storage mirror (AC-37),
  discovery (AC-41) — sibling tasks.

## Acceptance Criteria

- [x] AC-38: Each participating flow folder carries a `flow_navigation.yaml` (edges, triggers, escape paths, back-stack policy); `ui-scribble-handoff-emitter` emits and keeps it current; `flutter_handoff.yaml` points to the relevant file(s); `ui-verify-flutter` and the coding consumer read it.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| (orchestrator-wired) | — | `after: claude-modify-agent` to be added by the orchestrator (this task edits the `ui-scribble-handoff-emitter` agent). |

## Notes

Edits the `ui-scribble-handoff-emitter` AGENT, so the orchestrator will add
`after: claude-modify-agent`. Use `claude-modify-agent` / `claude-modify-skill` as appropriate.
Keep the edited agent/skill `contract.yaml` in sync (REQ-PROC-044 mechanism).
