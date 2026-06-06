# Plan: Update Implementation Skills for Persona Awareness + Sketch Gate

## Objective
Add persona-reading and sketch gate checks to code-simple and code-complex skills, plus persona-design validation to quality checker.

## Changes

### 1. code-simple/skill.md
- Add persona-reading step in Step 2 "Read & Assess" (conditional: only for UI/Presentation tasks)
- Add sketch gate check before Step 3 "Implement" (conditional: only if Presentation Layer changes)

### 2. code-complex/skill.md
- Add persona-reading guidance in Step 2 "Plan" phase (passed to architecture-advisor)
- Add sketch gate check guidance in Step 2 "Plan" phase

### 3. quality-checker.md
- Add persona-design validation checks in Phase 1 (if presentation layer changes)
- Validates persona identification, trait scans, DDR checks

## Implementation Details

**Persona-reading step** (to add to both skills):
```
If task involves Presentation Layer:
  1. Read goal.md for `personas_served` field
  2. If present, review doc/presentation/design/persona_design_bridge.md
     before implementing UI changes
  3. Consider trait categories relevant to this screen/component
```

**Sketch gate** (to add to both skills):
```
If Presentation Layer changes:
  1. Check goal.md for `skip_sketch: true`
  2. If absent: check [requirement]/sketches/ for status: approved
  3. If no approved sketch: invoke ui-create-sketch first
  4. If approved exists: continue, reference sketch in implementation
```

**Quality checker additions**:
- Check if Presentation Layer has design rules that reference persona traits
- Flag missing persona identification in design decisions
- Verify DDR (Design Decision Record) exists if multiple persona considerations

## Effort: ~20 lines across 3 files
