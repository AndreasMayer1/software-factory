---
task_id: TASK-PROC-032-15
type: impl
parent_requirement: REQ-PROC-032-04
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-05-31
started: 2026-05-31
completed: 2026-05-31
session_completed_at: 2026-05-31T14:56:38Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-11]
  sections: []
scope_description: "Add a Phase 0.5 pre-brief to ui-scribble-iterate before first generation, with developer approve/adjust/reject-scope handling and a retained pre-brief version artifact."
release_description: ""
opus_recommended: false
requirements_version:
  commit: b58e7cca
  file: ../requirements.md
session_id: 43f5d1e9-ab74-4c13-ad83-1f7deeac2e1c
session_account: gmail
---
# Goal: Scribble reviewer pre-brief (Phase 0.5)

## Objective

ui-scribble-iterate (claude-modify-skill): add a Phase 0.5 pre-brief before first generation
(≤300 words: screens to be generated, personas+rules applied, out-of-scope, information-model
boundary, open assumptions). Developer approves / adjusts (regenerate, bounded before
escalation) / rejects-scope (route to requ-explore). Retain the approved pre-brief as a
version artifact. Document the ≤300-word content spec + iteration model in SKETCHES_README. [AC-34]

## Requirements Summary

Covers AC-34 (Phase 0.5 pre-brief gate: content spec, approve/adjust/reject-scope handling,
retained version artifact, SKETCHES_README documentation).

For complete requirements at task creation time:
```
git show b58e7cca:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- ui-scribble-iterate Phase 0.5 pre-brief (≤300-word spec, developer gate, retained artifact).
- SKETCHES_README documentation of the content spec + iteration model.

### Out of Scope
- Generation/review behaviors covered by sibling tasks.

## Acceptance Criteria

- [x] AC-34: Phase 0.5 pre-brief (≤300 words) precedes first generation; developer can approve/adjust/reject-scope; approved pre-brief retained as a version artifact; spec documented in SKETCHES_README.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Skill edits through `claude-modify-skill`.
