# Investigation Findings: UI Sketch Iteration Workflow

**Agent**: claude-sonnet-4-6
**Date**: 2026-02-28
**Task**: TASK-PROC-032-01

## Codebase Context

### Design System Structure
- **Location**: `lib/core/design_system/` (Atomic Design pattern)
- **Components**: atoms, molecules, organisms
- **Tokens**: W3C DTCG format in `lib/config/theme/tokens.json`
- **Token Tiers**: primitives (spacing, colors, fonts, durations), semantic, component-level
- **Pattern**: Material Design 3 + brand green theme (ColorScheme.fromSeed)

### Existing Architecture Patterns
- Clean Architecture (Domain, Data, Presentation layers)
- BLoC state management with Injectable/GetIt
- GoRouter for navigation (ShellRoutes)
- Material 3 components with strong accessibility focus
- Design tokens auto-generated via build script

### Related Requirements
- **REQ-PROC-026** (Persona-Design Bridge): Design system rules being established; sketches must align
- **REQ-PROC-004** (Interactive Brainstorming): Workflow for exploration tasks with interactive iteration
- **REQ-PROC-005** (Testing Workflow): Process for test implementation and validation

## Key Requirements from Goal.md

### Questions to Answer
1. **Q1 - Sketch Format**: HTML/CSS, Flutter sandbox, ASCII, SVG, or hybrid?
2. **Q2 - AI Rules**: What MUST/MUST-NOT the AI do when generating sketches?
3. **Q3 - Storage**: Inside requirement folder, top-level folder, or dev area?
4. **Q4 - Iteration Workflow**: Steps, triggers, review artifact, feedback method, completion signal?
5. **Q5 - Integration**: Gate sketch approval in simple/complex implementation skills?
6. **Q6 - Rules Location**: doc/, CLAUDE.md, new skill, or hybrid?

### Acceptance Criteria (7 total)
- AC-01: Sketch format chosen and justified
- AC-02: AI rules enumerated and located
- AC-03: Storage location decided
- AC-04: Organization structure defined
- AC-05: Iteration workflow documented
- AC-06: Integration decision made
- AC-07: Rules anchor location decided

### Blocking Note
This task blocks ALL outstanding work touching the Presentation Layer.

## Analysis

### Sketch Format Decision

**Recommendation: Hybrid approach - HTML/CSS with optional Flutter sandbox fallback**

**Rationale**:
- **HTML/CSS**:
  - Pro: Easily viewable in browser, fast AI generation, lightweight, separable from implementation, uses web semantics (buttons, forms)
  - Pro: Can be viewed without building Flutter app
  - Pro: Natural for static mockups
  - Con: Requires maintaining CSS alongside Flutter design tokens

- **Flutter Sandbox**:
  - Pro: Uses real design tokens and Material 3 components
  - Pro: Bridges directly to Flutter implementation
  - Con: Requires building/running app (slower iteration)
  - Con: More complex to generate (widget trees)
  - Pro: Could be fast with dev-only build configuration

**Hybrid Decision**:
- **Primary**: HTML/CSS format (faster iteration, more disposable)
- **Secondary**: Optional Flutter sandbox when complex interactions need visual validation
- **Bridge**: Map HTML structural decisions back to Flutter component choices via decision doc

**Justification**:
- Developer emphasized speed ("first iteration always throwaway")
- Static pictures are the goal (no interactivity)
- Multiple screens per flow are required
- HTML+CSS is fastest to generate, view, and iterate
- Design tokens can be exported from tokens.json to CSS variables for consistency

### Storage Location Decision

**Recommendation: Option B + supplementary metadata - Top-level `ui_sketches/` folder with mirrored structure**

**Structure**:
```
ui_sketches/
  [category]/
    [requirement]/
      [version]/
        - sketch.html
        - styles.css
        - metadata.yaml
        - design_decisions.md
```

**Rationale**:
- Clean separation from requirements and implementation
- Easy to bulk delete old sketches
- Parallel structure mirrors requirements for discoverability
- Metadata.yaml tracks approval status, token mappings, design decisions
- Not committed as source (can be git-ignored or stored separately)

**Alternative**: Could also store in `requirements_tasks/[category]/[requirement]/sketches/v1/` if developer prefers co-location (decision point).

### AI Behavior Rules for Sketching

**MUST DO**:
1. Generate ALL screens/steps in a flow (not just one)
2. Use clear element hierarchy and visual grouping
3. Label all interactive elements with semantic names (e.g., "Submit Button", "Email Field")
4. Show element structure via nesting/indentation
5. Reference design tokens in comments (spacing, color names)
6. Include multiple variants if relevant (e.g., normal + error state for forms)
7. Be completable quickly (speed > pixel perfection)
8. Document mapping from HTML elements to Flutter components (Button → ElevatedButton, etc.)

**MUST NOT**:
1. Implement actual click handlers or form submission
2. Create state management (BLoC, Provider, etc.)
3. Add real data binding or API integration
4. Generate responsive breakpoints (single design assumed)
5. Use complex CSS animations or transitions
6. Add accessibility attributes (beyond semantic HTML)
7. Hard-code exact spacing/padding values - reference tokens only
8. Generate production-ready code

**Rules Location**: Should live in:
- CLAUDE.md (Section 7 - Sketching Rules) as a new subsection
- New doc/ guideline: `doc/sketching_guidelines.md` (optional, for detailed developer guidance)
- New skill `create-ui-sketch` with embedded constraints

### Iteration Workflow

**Recommended Process**:

```
1. Developer: Write/update requirement + design rules
2. AI:        Generate static HTML sketch
3. Developer: Open sketch.html in browser, review
4. Developer: Identify gaps, write feedback
5. AI:        Update design rules based on feedback
6. AI:        Regenerate sketch with new rules
7. Loop:      Repeat 3-6 until developer approves
8. Developer: Mark sketch as APPROVED in metadata.yaml
9. AI:        Begin Flutter implementation using sketch as reference
```

**Triggers**:
- New requirement → Manual: "Generate sketch for [requirement]"
- Updated rules → Manual: "Regenerate sketch with updated rules"
- Rule clarification needed → User feedback + AI regenerates

**Review Artifact**:
- Primary: `sketch.html` (browser-viewable)
- Supporting: `design_decisions.md` (explains why elements are arranged as they are)
- Metadata: `metadata.yaml` (approval status, version tracking, token references)

**Feedback Method**:
- Edit `design_decisions.md` or `metadata.yaml` directly
- Inline comments in feedback message
- Verbal feedback in conversation (AI translates to rules updates)

**Completion Signal**:
- `metadata.yaml`: `approval_status: approved`
- Timestamp in metadata
- Developer affirms: "Sketch approved, ready for implementation"

### Integration with Implementation Skills

**Decision: Optional gate for Presentation Layer changes**

**Recommendation**:
- **Gate requirement**: Only for NEW UI screens or major refactors (e.g., form → wizard)
- **No gate**: For minor updates, styling tweaks, component replacements
- **Implementation**: Add optional step in code-simple/code-complex skills: "Sketch exists for this screen? [Y/N]"
- **Trigger**: Developer sets `requires_sketch: true` in task goal.md

**Rationale**:
- Sketch approval ensures alignment before expensive Flutter work (prevents rework)
- But lightweight changes don't need ceremonial approval
- Gives developer flexibility for trivial changes
- Gates only presentation layer (data/domain changes don't require sketches)

### Rules Anchor Location Decision

**Recommendation: Hybrid**

**Primary locations**:
1. **CLAUDE.md** (Section 7): High-level sketch behavior rules (MUST/MUST NOT)
   - Loaded into every agent context
   - Enforced automatically

2. **New skill**: `create-ui-sketch`
   - User invokes: "Generate sketch for [requirement]"
   - Embeds all AI generation constraints
   - Handles HTML generation, file organization, metadata creation
   - Token mapping logic

3. **New doc/ guideline** (optional): `doc/ui_sketching.md`
   - For detailed guidance on reviewing sketches
   - Best practices for layout decisions
   - Design token mapping examples
   - When NOT to use sketches

**Secondary**:
- **REQ-PROC-032 itself**: Final documented decisions serve as reference
- **Metadata in sketch folders**: Per-sketch context (which tokens were used, design rationale)

---

## Synthesis Plan: What Gets Written

### Output 1: Updated REQ-PROC-032 (requirements.md)
- Fills all 7 ACs with concrete decisions
- Sections for each decision area with justification
- Integration guidance for implementation skills
- Examples of sketch metadata structure

### Output 2: New Skill `create-ui-sketch` (future impl task)
- Orchestrates sketch generation from requirement
- Manages file structure and versioning
- Handles HTML/CSS generation with design token mapping
- Creates metadata.yaml and design_decisions.md

### Output 3: CLAUDE.md Update (future impl task)
- New section in coding standards
- MUST/MUST-NOT rules for AI sketch generation
- References to sketch rules skill

### Output 4: Optional `doc/ui_sketching.md` (future impl task)
- Detailed developer guide
- Workflow diagram
- Token mapping examples
- Anti-patterns to avoid

---

## Open Questions for User Approval

1. **Storage location**: Top-level `ui_sketches/` or co-located in requirements folder?
2. **Sketch format**: HTML/CSS as primary, or Flutter sandbox instead?
3. **Gate requirement**: Optional gate in implementation skills, or separate explicit skill?
4. **Token mapping**: Should HTML use CSS variables derived from tokens.json, or simpler comment-based?
5. **Scope**: Should initial skill/rules cover ONLY screens/layouts, or also component states?

---

## Next Steps (Phase 2)

Await user feedback on open questions, then write the complete REQ-PROC-032 requirement document with all ACs addressed.
