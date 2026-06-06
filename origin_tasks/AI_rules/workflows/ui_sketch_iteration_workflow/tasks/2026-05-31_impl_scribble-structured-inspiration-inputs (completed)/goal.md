---
task_id: TASK-PROC-032-14
type: impl
parent_requirement: REQ-PROC-032-04
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-06-01
completed: 2026-06-01
session_completed_at: 2026-06-01T19:13:13Z
effort: M
created: 2026-05-31
after: [TASK-PROC-044-01-01, TASK-PROC-044-02-01, TASK-PROC-044-01-04, TASK-PROC-044-01-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-10]
  sections: []
scope_description: "Define an inputs/inspiration.yaml convention with a per-reference use/ignore matrix; ui-scribble-generator Phase 0 patterns scribbles after used aspects and annotates affected screens."
release_description: ""
opus_recommended: false
requirements_version:
  commit: b58e7cca
  file: ../requirements.md
session_id: 6945adcf-5dd0-44ac-9d70-f9398a9dbe51
session_account: gmail2

---
# Goal: Scribble structured inspiration inputs

## Objective

Define inputs/inspiration.yaml convention: per-reference use/ignore matrix (use layout:true,
use colors:false, …), optional screen scope, free-text note. ui-scribble-generator Phase 0
(claude-modify-agent): pattern the scribble after used aspects, ignore the rest in favor of
project conventions, annotate each affected screen with its inspiration source. Document the
convention in SKETCHES_README. [AC-33]

## Requirements Summary

Covers AC-33 (structured inspiration inputs convention + Phase 0 application + per-screen
annotation + SKETCHES_README documentation).

For complete requirements at task creation time:
```
git show b58e7cca:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- inputs/inspiration.yaml convention (use/ignore matrix, screen scope, note).
- ui-scribble-generator Phase 0 edit (apply used aspects, annotate affected screens).
- SKETCHES_README documentation of the convention.

### Out of Scope
- Other Phase-0 multimodal seed behaviors not related to structured inspiration.

## Acceptance Criteria

- [x] AC-33: inputs/inspiration.yaml convention defined; Phase 0 patterns after used aspects, ignores the rest, annotates affected screens; convention documented in SKETCHES_README.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Agent edits through `claude-modify-agent`.
