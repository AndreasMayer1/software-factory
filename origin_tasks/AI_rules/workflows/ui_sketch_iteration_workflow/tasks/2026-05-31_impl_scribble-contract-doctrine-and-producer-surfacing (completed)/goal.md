---
task_id: TASK-PROC-032-11
type: impl
parent_requirement: REQ-PROC-032-03
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-31
completed: 2026-05-31
session_completed_at: 2026-05-31T15:25:40Z
effort: L
created: 2026-05-31
after: [TASK-PROC-044-01-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-05, AC-06, AC-07, AC-10, AC-11]
  sections: []
scope_description: "Author the single-source scribble contract doctrine (LOCKED-IN / RE-DERIVE) and wire the producers (generator + handoff-emitter) to emit it."
release_description: ""
opus_recommended: false
requirements_version:
  commit: b58e7cca
  file: ../requirements.md
session_id: d149022d-36fa-4c06-bb05-a0964933b989
session_account: web
---
# Goal: Scribble contract doctrine and producer surfacing

## Objective

Author the single-source contract doctrine and wire the producers to emit it.

- SKETCHES_README.md: add "What a Scribble Commits To" section with the two disjoint
  sets LOCKED-IN (L1–L15) and RE-DERIVE (D1–D8) per REQ-PROC-032 SEC-15. This is the
  ONLY place the enumerated lists live (no restatement elsewhere). [AC-21]
- ui-scribble-generator agent (claude-modify-agent): emit a CONTRACT BLOCK at the top of
  index.html + a compact per-screen variant, dual reviewer/coder framing, verbatim from
  the SKETCHES_README contract. [AC-22] Change persona-derived sizing from literal
  `min-height:48px` to a NAMED TOKEN reference (e.g. var(--min-tap-target)); the literal
  resolves from the token registry. Add accessibility-INTENT to generated output (semantic
  element, ARIA role identity, alt-text obligation, accessible-name); keep a11y
  IMPLEMENTATION deferred. [AC-26] Emit a machine-readable rule-application audit trace
  (which T1/T2 rule applied to which element). [AC-27]
- ui-scribble-handoff-emitter agent (claude-modify-agent): add a top-level `contract:`
  block (locked_in / re_derive item keys + source pointer to SKETCHES_README) to
  flutter_handoff.yaml, AND a `design_decisions:` block propagating the scribble metadata
  `design_decisions` to the coder (D8 / amended AC-23). Update
  .claude/schemas/flutter_handoff.yaml to validate both blocks. [AC-23]

Verification: open a generated scribble, confirm CONTRACT BLOCK present with both framings;
confirm flutter_handoff.yaml validates against the updated schema with the contract +
design_decisions blocks.

## Requirements Summary

Covers AC-21 (single-source contract doctrine in SKETCHES_README), AC-22 (CONTRACT BLOCK
in generated scribble), AC-23 (contract block in flutter_handoff.yaml + schema), AC-26
(accessibility-intent + named-token sizing in generated output), AC-27 (machine-readable
rule-application audit trace).

For complete requirements at task creation time:
```
git show b58e7cca:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- SKETCHES_README.md contract doctrine section (L1–L15 / D1–D8).
- ui-scribble-generator agent edits (CONTRACT BLOCK, named-token sizing, a11y-intent, audit trace).
- ui-scribble-handoff-emitter agent edit (`contract:` block) + flutter_handoff schema update.

### Out of Scope
- Downstream consumers honoring the contract (Sketch Gate, ui-verify-flutter) — TASK-PROC-032-12.
- Accessibility IMPLEMENTATION (deferred — only intent is in scope here).

## Acceptance Criteria

- [x] AC-21: SKETCHES_README contains the single-source LOCKED-IN / RE-DERIVE doctrine; no restatement elsewhere.
- [x] AC-22: Generated scribble emits a CONTRACT BLOCK (index-level + per-screen) with dual reviewer/coder framing.
- [x] AC-23: flutter_handoff.yaml carries a top-level `contract:` block validated by the updated schema.
- [x] AC-26: Generated output uses named-token sizing and carries accessibility-intent.
- [x] AC-27: Generated output emits a machine-readable rule-application audit trace.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Edits to existing skills go through `claude-modify-skill`; agent edits through `claude-modify-agent`.
Producers already exist (shipped by REQ-PROC-044) — this task EDITS them, it does not recreate them.
