---
task_id: TASK-PROC-032-07
type: impl
parent_requirement: REQ-PROC-032-04
urgency: 2
urgency_reason: U2-NICE
impact: 3
impact_reason: I3-DX
status: completed
effort: XS
created: 2026-04-26
started: 2026-06-02
completed: 2026-06-02
after: [TASK-PROC-032-06]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-08]
  sections: []
scope_description: "Document scribble local server viewing workflow and flow_positions metadata format in SKETCHES_README.md"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
---

# Goal: Impl — Scribble Viewing Documentation

## Objective

Update `requirements_tasks/SKETCHES_README.md` to document:

1. **How to view scribbles in the browser** — the CORS issue means files cannot be opened directly from the filesystem. Add a "Viewing scribbles locally" section with the python3 server one-liner and URL pattern.

2. **`flow_positions[]` metadata format** — document the fields (`flow_id`, `screen_file`, `step_number`, `requirement_id`) under the `metadata.yaml` section so developers know how to populate them when creating scribbles.

## Context

Exploration task TASK-PROC-032-06 found:
- `components.js` uses `fetch()` which is blocked on `file://` — components fall back to placeholders
- `generate_flow_scribble_index.py` (AC-18) uses absolute iframe paths that also require a server
- The fix is zero-cost: `python3 -m http.server 8080` is already in the devcontainer
- No scribbles have been created in practice yet — this docs gap will hit the first developer who tries to view one

## Deliverables

1. Add "Viewing scribbles locally" section to `SKETCHES_README.md`:
   - Explain why direct file open doesn't work (CORS, `fetch()`)
   - Document background server start (non-blocking — must not block the LLM session):
     ```bash
     python3 -m http.server 8080 &
     SERVER_PID=$!
     ```
   - URL pattern: `http://localhost:8080/requirements_tasks/[path]/scribbles/vN/index.html`
   - Note: flow composite index at `http://localhost:8080/requirements_user_needs/user_flows/<flow>/scribble_index.html`
   - Document how to stop the server when done: `kill $SERVER_PID` (or `kill $(lsof -ti:8080)`)

2. Add `flow_positions[]` format table to the `metadata.yaml` section:
   ```yaml
   flow_positions:
     - flow_id: FLOW-001
       screen_file: 01_home.html
       step_number: 3
       requirement_id: REQ-FUNC-007
   ```

## Acceptance Criteria

- [x] SKETCHES_README.md has a "Viewing scribbles locally" section with background server start, URL pattern, and stop command
- [x] `flow_positions[]` format documented in metadata.yaml section with field descriptions
- [x] AC-20 in REQ-PROC-032 is satisfied

## Notes

- REQ-PROC-032 AC-20 was added by TASK-PROC-032-06
- Phase 5a in skill.md is already correct — no skill changes needed
- This is a documentation-only task
