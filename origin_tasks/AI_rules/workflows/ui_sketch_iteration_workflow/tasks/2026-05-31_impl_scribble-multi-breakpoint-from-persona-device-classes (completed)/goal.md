---
task_id: TASK-PROC-032-13
type: impl
parent_requirement: REQ-PROC-032-04
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-06-01
completed: 2026-06-01
session_completed_at: 2026-06-01T14:23:24Z
effort: M
created: 2026-05-31
after: [TASK-PROC-044-01-01, TASK-PROC-044-02-01, TASK-PROC-044-01-04, TASK-PROC-044-01-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-09]
  sections: []
scope_description: "Derive a requirement's required breakpoint set from served personas' declared device classes; generate per breakpoint, marking layout-identical screens as shared (no duplication)."
release_description: ""
opus_recommended: false
requirements_version:
  commit: b58e7cca
  file: ../requirements.md
session_id: ffa0d566-a3a0-411b-a722-69fc1394c474
session_account: web
---
# Goal: Scribble multi-breakpoint from persona device classes

## Objective

Personas declare the device classes they predominantly use (add to persona schema/docs;
check README_* for an existing field before adding a new one). A requirement's required
breakpoint set = union across served personas. ui-scribble-generator + ui-scribble-iterate
(claude-modify-*): generate per required breakpoint; a screen whose layout is genuinely
identical across breakpoints is generated once and marked shared, never duplicated. [AC-32]

## Requirements Summary

Covers AC-32 (persona-derived device classes drive the required breakpoint set; per-breakpoint
generation with shared-layout deduplication).

For complete requirements at task creation time:
```
git show b58e7cca:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Persona device-class declaration (check README_* for an existing field first).
- ui-scribble-generator + ui-scribble-iterate edits for per-breakpoint generation + shared marking.

### Out of Scope
- Other review/contract behaviors covered by sibling tasks.

## Acceptance Criteria

- [x] AC-32: Required breakpoint set = union of served personas' device classes; per-breakpoint generation with layout-identical screens generated once and marked shared.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Edits to existing skills go through `claude-modify-skill`; agent edits through `claude-modify-agent`.
