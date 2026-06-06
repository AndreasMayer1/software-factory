---
task_id: TASK-PROC-032-22
type: impl
parent_requirement: REQ-PROC-032-01
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-06-02
session_completed_at: 2026-06-02T00:32:21Z
effort: M
created: 2026-05-31
started: 2026-06-01
after: [TASK-PROC-044-01-01, TASK-NFUNC-021-01, TASK-PROC-044-02-01, TASK-PROC-044-01-04, TASK-PROC-044-01-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-05]
  sections: []
scope_description: "Move the existing scribble to requirements_tasks/scribbles/<feature_path> (mirrors lib/features/ 1:1 by name/hierarchy; lib/core/ -> _core/); update path-discovery in ui-scribble-generator + ui-scribble-iterate, ui-verify-flutter, and the code-simple/code-complex Sketch Gate to locate scribbles via the feature_path mirror; add a parity lint (via claude-write-script); add a SKETCHES_README folder-structure section; run the lint and fix divergence."
release_description: ""
opus_recommended: false
requirements_version:
  commit: 6ece1dc7
  file: ../requirements.md
session_id: 45854d4b-4cf7-403f-9e88-036cbda58866
session_account: gmail
---
# Goal: Scribble storage mirrors lib/features/

## Objective

Make the scribble storage layout mirror `lib/features/` 1:1. Scribbles live under
`requirements_tasks/scribbles/<feature_path>`, where `<feature_path>` mirrors the
`lib/features/` tree by name and hierarchy (and `lib/core/` maps to `_core/`). A scribble's
`feature_path` metadata field resolves to exactly one node in that tree, and the existing
scribble resides at its mirrored location rather than at any legacy co-located
`[category]/[requirement]/scribbles/` path. [AC-37]

## Requirements Summary

Covers AC-37: scribbles live at `requirements_tasks/scribbles/<feature_path>` mirroring
`lib/features/` (and `_core/`); the existing scribble is migrated there; a parity check flags
divergence in either direction; `ui-scribble-generator`, `ui-scribble-iterate`, and the
consumers (`ui-verify-flutter`, the `code-simple`/`code-complex` Sketch Gate) locate a
requirement's scribble through the `feature_path` mirror, not a hard-coded co-located path.

For complete requirements at task creation time:
```
git show 6ece1dc7:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `git mv` the existing scribble to its mirrored location under `requirements_tasks/scribbles/<feature_path>`.
- Path-discovery edits in `ui-scribble-generator` and `ui-scribble-iterate`.
- Path-discovery edits in `ui-verify-flutter`.
- Path-discovery edits in the `code-simple` / `code-complex` Sketch Gate.
- A parity lint (created via `claude-write-script`) flagging divergence in either direction:
  a scribble whose `feature_path` has no matching `lib/features/` node, or an expected
  feature path with no covering scribble.
- A folder-structure section in `requirements_tasks/SKETCHES_README.md`.
- Run the parity lint and fix any divergence it reports (enforcement creates remediation —
  the cleanup is part of this task; confirm no stale duplicate scribble docs remain at the old path).

### Out of Scope
- Per-flow navigation, walk validation, approval trail, contributing-requirements discovery
  (sibling tasks).
- The `lib/features/` structure/naming policy itself (defined by the prerequisite policy task;
  this task enforces parity against it).

## Acceptance Criteria

- [x] AC-37: Scribbles live under `requirements_tasks/scribbles/<feature_path>` mirroring `lib/features/` (and `lib/core/` -> `_core/`) 1:1; the existing scribble is at its mirrored location, not a legacy path; a parity check flags divergence in either direction; the generation, iteration, and consumption skills locate scribbles via the `feature_path` mirror.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| (orchestrator-wired) | — | `after: claude-modify-agent` to be added by the orchestrator (this task edits `ui-scribble-*` agents). |
| (orchestrator-wired) | — | `after: lib-features-policy` (P0) to be added by the orchestrator (parity is checked against the `lib/features/` structure policy, which must exist first). |

## Notes

Edits `ui-scribble-*` AGENTS, so the orchestrator will add `after: claude-modify-agent`. Parity
is checked against the `lib/features/` structure policy, so the orchestrator will add
`after: <lib-features-policy task>` (P0). Use `claude-modify-agent` for agent edits and
`claude-modify-skill` for skill edits once those skills exist. Keep each edited skill/agent
`contract.yaml` in sync (REQ-PROC-044 mechanism). Create the parity lint via `claude-write-script`.
