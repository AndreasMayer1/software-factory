# Protocol: Final Decisions - UI Sketch Iteration Workflow

**Agent**: claude-sonnet-4-6
**Date**: 2026-03-01
**Task**: TASK-PROC-032-01
**Status**: COMPLETED

## All 7 ACs Addressed

### AC-01: Sketch Format → HTML/CSS
- Primary: Single `.html` file, inline CSS
- Exception: Minimal Flutter widget code for animation testing ONLY (not committed, disposable)
- Not used: SVG, ASCII, Markdown, Flutter widget trees for layout

### AC-02: AI Rules → MUST/MUST-NOT in skill + CLAUDE.md
- Anchor: `create-ui-sketch` skill (generation constraints) + CLAUDE.md reference
- Rules written into requirements.md SEC-03

### AC-03: Storage → Co-located `sketches/` next to requirements.md
- Path: `requirements_tasks/[category]/[requirement]/sketches/`
- Committed to git (sketches are requirement artifacts)

### AC-04: Organization → Version folders with metadata.yaml
- `v1/`, `v2/`, ... each containing `sketch.html`, `metadata.yaml`, `feedback.md`
- `metadata.yaml` tracks: status (draft/superseded/approved), token references, component mapping

### AC-05: Iteration Workflow → 8-step cycle
- Trigger → generate → browser review → feedback → rules update → regenerate → approve → implement
- Completion signal: `metadata.yaml status: approved` + developer explicit approval

### AC-06: Integration → Default ON, opt-out via `skip_sketch: true` in goal.md
- code-simple and code-complex check for approved sketch before Presentation Layer work
- Opt-out: add `skip_sketch: true` to goal.md YAML frontmatter

### AC-07: Design System Alignment → Approximate mapping + comment bridge
- CSS values approximate tokens, comments reference token names
- Component mapping block at top of HTML (HTML element → Flutter widget)
- Not exact — no build step needed

## Output File
`requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md`
- Status updated: draft → defined
- All sections completed

## Follow-up Impl Tasks Needed
1. **`create-ui-sketch` skill** — new skill to orchestrate sketch generation
2. **CLAUDE.md update** — add sketch rules reference section
3. **code-simple / code-complex update** — add sketch gate check logic
4. **Example sketch** — create example sketch for one existing requirement (dogfooding)
