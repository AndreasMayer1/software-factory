---
task_id: TASK-PROC-032-26
type: impl
parent_requirement: REQ-PROC-032-04
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-31
started: 2026-06-01
completed: 2026-06-02
session_completed_at: 2026-06-01T23:15:14Z
after: [TASK-PROC-044-01-01, TASK-PROC-044-02-01, TASK-PROC-044-01-04, TASK-PROC-044-01-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-14]
  sections: []
scope_description: "A discovery script (via claude-write-script) auto-discovers a scribble's contributing_requirements (primary + cross-cutting) and participating_flows from feature_path, the requirements matrix, and a UI-scope heuristic, and writes them into the EXISTING scribble_metadata.yaml fields (no new frontmatter); ambiguities flagged for human review; wire into ui-scribble-generator; add a consistency lint requiring the primary contributing requirement to match feature_path."
release_description: ""
opus_recommended: false
requirements_version:
  commit: 6ece1dc7
  file: ../requirements.md
session_id: 948c1786-a147-4abd-a873-2bea7709a8b9
session_account: gmail2
---
# Goal: Contributing-requirements and participating-flows discovery

## Objective

Auto-discover a scribble's `contributing_requirements` (the primary owning requirement plus
cross-cutting requirements) and `participating_flows` from its `feature_path`, the requirements
matrix, and a UI-scope heuristic, and write them into the EXISTING `scribble_metadata.yaml`
fields. No new frontmatter fields are introduced — these fields already exist in
`.claude/schemas/scribble_metadata.yaml`. Where discovery is ambiguous, the ambiguity is flagged
for human review rather than the field being silently left empty. A consistency lint requires the
primary contributing requirement to correspond to the scribble's `feature_path`. [AC-41]

This is a STANDALONE task.

## Requirements Summary

Covers AC-41: automatic discovery of `contributing_requirements` (primary + cross-cutting) and
`participating_flows` from `feature_path` + requirements matrix + UI-scope heuristic, written into
the existing `scribble_metadata.yaml` fields (no new frontmatter); ambiguity flagged for human
review; a consistency lint requires the primary contributing requirement to match `feature_path`.

For complete requirements at task creation time:
```
git show 6ece1dc7:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- A discovery script (created via `claude-write-script`) that derives `contributing_requirements`
  (primary owner + cross-cutting) and `participating_flows` from `feature_path`, the requirements
  matrix, and a UI-scope heuristic.
- Write the discovered values into the EXISTING `scribble_metadata.yaml` fields (no new
  frontmatter fields — they already exist in `.claude/schemas/scribble_metadata.yaml`).
- Flag ambiguous discovery for human review rather than silently emptying the field.
- Wire the script into `ui-scribble-generator`.
- A consistency lint requiring the primary contributing requirement to correspond to the
  scribble's `feature_path`; run it and fix violations.

### Out of Scope
- Introducing any new `scribble_metadata.yaml` frontmatter field (explicitly forbidden — D41/D42
  stay dropped).
- Per-flow navigation (AC-38), walk validation (AC-39), approval trail (AC-40), storage mirror
  (AC-37) — sibling tasks.

## Acceptance Criteria

- [x] AC-41: `contributing_requirements` and `participating_flows` are discovered automatically from `feature_path` + requirements matrix + UI-scope heuristic and written into the existing `scribble_metadata.yaml` fields (no new frontmatter); ambiguity is flagged for human review; a consistency lint requires the primary contributing requirement to match the `feature_path`.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| (orchestrator-wired) | — | `after: claude-modify-agent` to be added by the orchestrator (this task wires the script into the `ui-scribble-generator` agent). |

## Notes

STANDALONE task. Edits the `ui-scribble-generator` AGENT (to wire in the discovery script), so the
orchestrator will add `after: claude-modify-agent`. Create the discovery script and the consistency
lint via `claude-write-script`. Use `claude-modify-agent` / `claude-modify-skill` as appropriate.
The `contributing_requirements` and `participating_flows` fields ALREADY exist in
`.claude/schemas/scribble_metadata.yaml` — do not add new frontmatter fields. Keep the edited
agent/skill `contract.yaml` in sync (REQ-PROC-044 mechanism).
