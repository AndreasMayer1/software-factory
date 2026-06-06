# Protocol: Revision After User Feedback

**Agent**: claude-sonnet-4-6
**Date**: 2026-03-01
**Task**: TASK-PROC-032-01 (completed)

## Reason for Revision

User raised 6 gaps after initial requirement was written. Substantially revised requirements.md and added SKETCHES_README.md to address them.

## Gaps Addressed

### Q1 — Multi-screen format
**Decision**: Per-screen HTML files + index.html (not all-in-one)
- Each screen/step = one `.html` file named `NN_[screen_name].html`
- `index.html` lists all screens with links and descriptions
- Cleaner review, smaller files, easier to open specific screens

### Q2 — Relation to other workflows
- `code-simple`/`code-complex`: check for approved sketch before Presentation Layer work
- `validate-ux-rule` (REQ-PROC-026 T3): validates proposed T1/T2 rules against persona needs
- `doc-update-guidelines`: anchors approved T1/T2 rules in `doc/presentation/`
- `requ-explore`: invoked if feedback reveals a requirement gap (not a rule gap)

### Q3 — create-ui-sketch skill scope
- DOES: read requirements + personas + T1/T2 rules, generate HTML files, run Rule Update Protocol, spawn Haiku impact agent, invoke doc-update-guidelines
- DOES NOT: validate rules (validate-ux-rule), write to doc/ directly, update requirements.md, generate Flutter code, make tier decisions unilaterally

### Q4 — Sketch documentation location
- **NOT** CLAUDE.md (too low-level for orchestrator constitution)
- **NOT** doc/ (that's coding guidelines for agents)
- **YES**: `requirements_tasks/SKETCHES_README.md` — follows same pattern as `requirements_user_needs/README_*.md`
- Created: SKETCHES_README.md

### Q5 — UI rules applied to sketch generation
- Investigated current doc/presentation/ structure (accessibility, design_system, best_practices, etc.)
- Investigated REQ-PROC-026 T1/T2/T3 tier classification system
- Added to AI MUST DO: read T1/T2 rules from doc/presentation/ before generating; read persona constraints
- Feedback → Rule Update Protocol: classify tier, impact check, pause for approval, anchor

### Q6 — Side effects and rule conflicts
- T3 rule: no side effects, apply immediately
- T2/T1 rule: Haiku agent runs impact check listing affected already-implemented requirements
- Human decides tier scope
- Conflicts between personas → DDR format from REQ-PROC-026

## New ACs Added

- AC-08: Sketch documentation location defined (SKETCHES_README.md)
- AC-09: create-ui-sketch skill scope defined

## Files Written

1. `requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md` — substantially revised (v2)
2. `requirements_tasks/SKETCHES_README.md` — new file
3. This protocol file

## Status

Task remains completed. Requirements.md status: defined (will be updated to implemented once the follow-up impl tasks are done).

## Follow-up Impl Tasks Required

1. `create-ui-sketch` skill — orchestrates sketch generation
2. Update CLAUDE.md — brief reference to sketch workflow
3. Update `code-simple` and `code-complex` — add sketch gate check
4. `validate-ux-rule` skill — REQ-PROC-026 T3 (separate requirement)
5. Example sketch for one existing requirement (dogfooding)
