---
task_id: TASK-PROC-032-07-01
type: impl
parent_requirement: REQ-PROC-032-07
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: in_progress
effort: S
created: 2026-06-06
started: 2026-06-06
expected_tool_calls: 20
skill_chain_depth: 2
after: [TASK-PROC-032-06-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04]
  sections: [SEC-21]
scope_description: "Implement PROP-14 flow-viewer: add 'Show User Flows' sidebar to scribble index.html via generator helper script modifications — script-driven flow file sourcing, pinned client-side Markdown renderer (REQ-PROC-060 gate), and flow-passage colour-highlighting from flow_positions step numbers"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: 85ed6d20
  file: ../requirements.md
session_id: 6e828f68-5a16-4b67-82ba-f9d5c4408d67
session_account: gmail
---
# Goal: Implement PROP-14 Embedded Flow-Viewer Sidebar in Scribble Generator

## Objective

Add a "Show User Flows" sidebar to scribble `index.html` files by modifying the generator helper
script. The sidebar lets a reviewer read the participating user flow(s) inline, without leaving
the browser tab. All four ACs of REQ-PROC-032-07 must be satisfied.

## Requirements Summary

REQ-PROC-032-07 — Embedded Flow Viewer (feat of REQ-PROC-032, UI Scribble Iteration Workflow).

For complete requirements at task creation time:
```
git show 85ed6d20:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_embedded_flow_viewer/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- **AC-01**: Add a "Show User Flows" toggle button to generated `index.html`. Activating it opens a
  sidebar panel with one tab per flow listed in the scribble's `flow_positions` metadata. Selecting a
  tab renders that flow's Markdown content as HTML inline. Toggle absent when no flows associated.

- **AC-02**: Extend the generator helper script to copy or symlink canonical user flow Markdown files
  (from `requirements_user_needs/user_flows/`) into the scribble artifact directory. The LLM must
  **never** read flow files and re-emit content — the canonical source file is the viewer's input.

- **AC-03**: Bundle a single pinned client-side Markdown renderer JS file (`marked`-class library) in
  the scribble artifact. **MANDATORY pre-condition**: the renderer must be developer-authorized under
  REQ-PROC-060 AC-01 before being added. Escalate via the pending_feedback protocol (write
  `question.md`) if not yet authorized — **do not self-add the renderer**. The pinned file is not
  updated without a fresh REQ-PROC-060 evaluation.

- **AC-04**: Add JavaScript logic to the sidebar that reads `flow_positions.step_number` mappings and
  highlights matched flow text passages in a distinct colour; non-matched passages at reduced opacity.
  Graceful degradation when step numbers are absent or no text anchors resolve.

### Out of Scope

- Changes to `lib/`, `test/`, `integration_test/` (this is factory tooling, not app code)
- LLM-driven re-emission of flow content
- Selecting the specific Markdown renderer library (developer's REQ-PROC-060 decision)
- The flow composite index (`generate_flow_scribble_index.py`) — separate concern (AC-18 of parent)

## Acceptance Criteria

- [ ] Toggle renders in generated `index.html` when `flow_positions` contains flow references; absent
      when no flows are associated
- [ ] Flow content in the sidebar is sourced from the canonical flow Markdown file (no LLM re-emission
      verified via code inspection)
- [ ] Renderer JS is pinned and bundled; developer REQ-PROC-060 authorization recorded in
      task protocol or commit message
- [ ] Highlighting correctly maps `flow_positions.step_number` to flow text passages; graceful
      degradation confirmed when step numbers are absent
- [ ] All Python quality gates pass: ruff (G1), mypy (G2), pytest (G3), no hand-rolled YAML (G4),
      print() discipline (G5)

## Verification (Embedded)

This task has < 3 sibling impl tasks for REQ-PROC-032-07, so verification is embedded here rather
than a separate task. After implementation:

1. Generate a test scribble with flow_positions referencing a real flow — verify sidebar toggle appears
   and flow content renders correctly
2. Inspect generated HTML to confirm no flow text was re-emitted by the LLM
3. Confirm renderer JS is present and pinned (check file hash matches authorized version)
4. Test with flow_positions having no step numbers — confirm unhighlighted rendering
5. Run `scripts/quality/check_python_gates.sh` — confirm all 5 gates green

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-060 AC-01 authorization | external | Developer must authorize the specific renderer library before it can be bundled; impl task escalates if not yet authorized |

## Notes

- Skill: `claude-write-script` (all changes are under `scripts/`; mandatory for any `.py` edit)
- The REQ-PROC-060 gate for the renderer is a hard external blocker — the task writes a `question.md`
  to `automation/pending_feedback/TASK-PROC-032-07-01/` if authorization is not yet recorded, then
  terminates. The orchestrator resumes after developer fills `answer.md`.
- T-C18 in the implementation task manifest (TASK-PROC-032-33 substrate) maps directly to this task.
