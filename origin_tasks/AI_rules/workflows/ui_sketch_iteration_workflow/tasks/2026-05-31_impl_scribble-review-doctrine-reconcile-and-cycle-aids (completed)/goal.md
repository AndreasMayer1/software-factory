---
task_id: TASK-PROC-032-12
type: impl
parent_requirement: REQ-PROC-032-03
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-31
completed: 2026-05-31
session_completed_at: 2026-05-31T15:39:15Z
effort: L
created: 2026-05-31
after: [TASK-PROC-044-01-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-12, AC-13, AC-14]
  sections: []
scope_description: "Reconcile the heuristics review doctrine (de-provisionalize), add even-version auto-review brief + structural diff, persona-conflict surfacing, and an iteration-fatigue rail."
release_description: ""
opus_recommended: false
requirements_version:
  commit: b58e7cca
  file: ../requirements.md
session_id: 923f7c3f-6d7b-421c-a96d-9f579526711e
session_account: web
---
# Goal: Scribble review doctrine reconcile and cycle aids

## Objective

- doc/presentation/heuristics/: remove the PROVISIONAL marker; reconcile the Nielsen /
  Universal Design / microinteraction / dark-pattern / motion-as-function checks with the
  Q1 design (TASK-PROC-032-10 iterations 1–4) and confirm no double-ownership with
  persona-walker or rule-reviewer. ui-scribble-heuristics-reviewer then applies it as
  canonical (drop the "PROVISIONAL" caveat in the agent). [AC-28]
- ui-scribble-auto-review (claude-modify-skill): after even-version regeneration, produce an
  auto-review brief (what to focus on) + an inter-version structural diff; the diff is
  viewable via a toggle in the scribble HTML that highlights changed elements; the brief
  links to the diff. [AC-29]
- persona-conflict surfacing: when persona-walker/heuristics review finds a screen-level
  two-persona conflict, mark the conflict point and link a DDR — or route upstream via the
  revision channel when resolution implies a flow/VCD change. [AC-30]
- ui-scribble-iterate (claude-modify-skill): add an iteration-fatigue rail (past a version
  threshold without convergence → recommend pausing to run requ-explore on the underlying
  requirement). [AC-31]

## Requirements Summary

Covers AC-28 (de-provisionalize heuristics corpus, canonical application), AC-29 (even-version
auto-review brief + structural diff toggle), AC-30 (persona-conflict surfacing + DDR/upstream
routing), AC-31 (iteration-fatigue rail).

For complete requirements at task creation time:
```
git show b58e7cca:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- doc/presentation/heuristics/ reconciliation + de-provisionalization.
- ui-scribble-heuristics-reviewer agent edit (drop PROVISIONAL caveat).
- ui-scribble-auto-review edits (brief + structural diff toggle).
- persona-conflict surfacing in persona-walker/heuristics review.
- ui-scribble-iterate iteration-fatigue rail.

### Out of Scope
- Contract doctrine / producer surfacing (TASK-PROC-032-11).

## Acceptance Criteria

- [x] AC-28: Heuristics corpus de-provisionalized, reconciled, no double-ownership; applied canonically.
- [x] AC-29: Even-version auto-review brief + inter-version structural diff toggle present.
- [x] AC-30: Screen-level two-persona conflicts marked and linked to a DDR or routed upstream.
- [x] AC-31: Iteration-fatigue rail recommends pausing past a non-convergence version threshold.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Edits to existing skills go through `claude-modify-skill`; agent edits through `claude-modify-agent`.
