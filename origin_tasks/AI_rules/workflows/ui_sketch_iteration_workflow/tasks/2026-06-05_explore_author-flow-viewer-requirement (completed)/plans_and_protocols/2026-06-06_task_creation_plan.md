---
requirement: REQ-PROC-032-07
requirements_version: 85ed6d20
created: 2026-06-06
mode: full
---

# Task Creation Plan for REQ-PROC-032-07

## Tasks

- task_name: "implement PROP-14 embedded flow-viewer sidebar in scribble generator"
  req_path: "requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_embedded_flow_viewer/requirements.md"
  requirements_version: "85ed6d20"
  covers_acs: [AC-01, AC-02, AC-03, AC-04]
  effort: S
  layer: scripts
  after: []
  task_type: impl
  opus_recommended: false
  target_package: ""
  implementation_notes: |
    Implement the PROP-14 flow-viewer sidebar in the scribble generator helper script.

    AC-01: Add a 'Show User Flows' toggle button to the generated index.html that opens a
    sidebar panel with one tab per flow listed in the scribble's flow_positions metadata.
    Toggle absent when no flows are associated with the scribble.

    AC-02: Add logic to the generator helper script that copies or symlinks canonical user
    flow Markdown files (from requirements_user_needs/user_flows/) into the scribble
    artifact directory. The LLM must never re-emit flow content — the canonical source file
    is the viewer's input.

    AC-03: Bundle a single pinned client-side Markdown renderer JS file (marked-class) in
    the scribble artifact. MANDATORY: the renderer must be developer-authorized under
    REQ-PROC-060 AC-01 before being added. Escalate via pending_feedback if not yet
    authorized — do not self-add.

    AC-04: Add JavaScript logic to the sidebar that reads flow_positions.step_number
    mappings and highlights matched flow text passages in a distinct colour; non-matched
    passages rendered at reduced opacity. Graceful degradation when step numbers absent.

    Skill: claude-write-script (the generator helper script lives in scripts/).

    Verification (embedded — no separate task required, < 3 impl tasks):
    - Toggle renders in index.html when flow_positions contains flow references; absent otherwise
    - Flow content in viewer sourced from canonical flow file (no LLM re-emission verified)
    - Renderer JS is pinned and bundled; developer REQ-PROC-060 authorization recorded in commit/protocol
    - Highlighting correctly maps step numbers to flow passages; graceful degradation when absent
    - All Python quality gates pass (ruff, mypy, pytest) per REQ-PROC-051

## Coverage Matrix

| AC    | Task(s)                                    | Package    |
|-------|--------------------------------------------|------------|
| AC-01 | implement-flow-viewer-sidebar              | (unassigned) |
| AC-02 | implement-flow-viewer-sidebar              | (unassigned) |
| AC-03 | implement-flow-viewer-sidebar              | (unassigned) |
| AC-04 | implement-flow-viewer-sidebar              | (unassigned) |

## Notes

- < 3 impl tasks: no separate verification task; verification section embedded in impl task above
- AC-03 carries a hard gate (REQ-PROC-060 developer authorization) that the impl task must honor
- target_package unassigned: factory/process tooling task carries no target_package per developer
  directive (will be appended to task_ordering_priority_override.txt after creation)
