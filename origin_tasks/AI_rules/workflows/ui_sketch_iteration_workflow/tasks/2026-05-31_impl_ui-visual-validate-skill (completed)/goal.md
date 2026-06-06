---
task_id: TASK-PROC-032-19
type: impl
parent_requirement: REQ-PROC-032-04
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2026-05-31
started: 2026-06-01
completed: 2026-06-01
session_completed_at: 2026-06-01T14:47:49Z
after: [TASK-PROC-032-11, TASK-PROC-044-01-01, TASK-PROC-044-02-01, TASK-PROC-044-01-04, TASK-PROC-044-01-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-13]
  sections: []
scope_description: "Create the new ui-visual-validate skill (and vision agent if warranted) that compares integration-test screenshots against the approved scribble + re-derive sources; add verification_seeds emission to the handoff emitter."
release_description: ""
opus_recommended: true  # reason: new skill design + vision-capable model (Opus) + agent-creation judgment
requirements_version:
  commit: b58e7cca
  file: ../requirements.md
session_id: d8679440-66db-462f-b299-577c2b8d99f0
session_account: web
---
# Goal: ui-visual-validate skill

## Objective

New skill ui-visual-validate via claude-create-skill (and claude-create-agent for its vision
agent if one is warranted — evaluate via the agent-creation rubric). Compares integration-test
screenshots of implemented Flutter screens against the approved scribble + re-derive sources
(tokens, accessibility, persona sizing). Advisory (non-blocking) findings report. Uses a
vision-capable model (Opus). Reads per-locked-item `verification_seeds:` emitted in
flutter_handoff.yaml — add that emission to ui-scribble-handoff-emitter as part of this task
(the R3-collapse: verification_seeds live INSIDE flutter_handoff, not a separate file). Scope
is distinct from ui-verify-flutter (code-only structural) and ui-improve-flutter (human polish).
after task 1 for flutter_handoff schema coherence. [AC-36]

## Requirements Summary

Covers AC-36 (new ui-visual-validate skill: vision-based advisory screenshot-vs-scribble
comparison reading per-locked-item verification_seeds from flutter_handoff.yaml).

For complete requirements at task creation time:
```
git show b58e7cca:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- New ui-visual-validate skill (claude-create-skill) + vision agent if warranted (claude-create-agent).
- verification_seeds emission added to ui-scribble-handoff-emitter (inside flutter_handoff.yaml).
- Advisory (non-blocking) findings report using a vision-capable model (Opus).

### Out of Scope
- ui-verify-flutter (code-only structural) and ui-improve-flutter (human polish) — distinct scopes.

## Acceptance Criteria

- [x] AC-36: ui-visual-validate skill exists; compares integration-test screenshots against approved scribble + re-derive sources; advisory non-blocking report; reads per-locked-item verification_seeds emitted in flutter_handoff.yaml; scope distinct from ui-verify-flutter / ui-improve-flutter.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-11 | pending | flutter_handoff schema coherence — contract block must exist first |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-11](../2026-05-31_impl_scribble-contract-doctrine-and-producer-surfacing/goal.md) | Predecessor — establishes flutter_handoff schema this task extends with verification_seeds |

## Notes

New skill via `claude-create-skill`; new agent (if warranted) via `claude-create-agent`.
