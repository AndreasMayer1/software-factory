---
id: REQ-PROC-032-01
status: active
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
effort: M
stakeholder: developer
created: 2026-02-28
updated: '2026-06-06'
after: []
blocks: []
market_research_refs: []
trackable_items:
  acceptance_criteria:
    - id: AC-01
      name: Scribble format defined
      description: HTML/CSS chosen; per-screen files + index.html; scribbles are structural
        wireframes only (screens, components, content) — NOT colors, spacing, or visual
        fidelity
    - id: AC-02
      name: AI scribble rules established
      description: MUST/MUST-NOT rules enumerated; T1/T2 rules read from doc/ before
        generation
    - id: AC-03
      name: Storage location defined
      description: Co-located next to requirements.md in scribbles/ subfolder; committed
        to git
    - id: AC-04
      name: Organization structure defined
      description: 'Version folders (v1/, v2/); per-screen HTML files; index.html;
        metadata.yaml with design_decisions: field'
    - id: AC-05
      name: Scribble storage mirrors lib/features/
      description: Scribbles live under requirements_tasks/scribbles/<feature_path>,
        where the path mirrors lib/features/ (and lib/core/ → _core/) 1:1 by name
        and hierarchy; the existing scribble resides at its mirrored location, not
        at any legacy path. A parity check flags any divergence between the scribble
        tree and the lib/features/ tree (a scribble with no matching feature, or a
        feature path that the scribble metadata's feature_path does not resolve to).
        ui-scribble-generator, ui-scribble-iterate, and the consumers (ui-verify-flutter,
        the code-simple / code-complex Sketch Gate) locate a requirement's scribble
        through its feature_path mirror rather than a hard-coded co-located path.
  sections:
    - id: SEC-02
      name: Scribble Definition
      heading: '## Scribble Definition'
    - id: SEC-03
      name: Scribble Format
      heading: '## Scribble Format'
    - id: SEC-04
      name: AI Behavior Rules for Scribble Generation
      heading: '## AI Behavior Rules for Scribble Generation'
    - id: SEC-05
      name: Storage and Organization
      heading: '## Storage and Organization'
---

# Scribble Core Artifact

> **Implementation tasks:** This feature's ACs were implemented before REQ-PROC-032 was restructured into an epic (TASK-PROC-032-34, zero spec change), so it has no `tasks/` folder of its own. Some (if not all) of its implementing tasks live in the epic-level tasks folder `requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/` (the completed `scribble-*` batch). Only the genuinely-new features (F05–F07) carry their own derived `tasks/`.


## Scribble Definition

A **UI scribble** is a structural wireframe that answers exactly three questions for the screens in scope: [AC-01]

1. **Which screens exist?** — Every screen or step in the flow has a dedicated file.
2. **What does each screen display?** — Labels, headings, data fields, and their hierarchy.
3. **Which Flutter components are used?** — Every element maps to a named Flutter widget.

A scribble does NOT attempt to replicate the visual appearance of the final app. Colors, exact spacing, and visual polish are intentionally excluded. The real app will look different from the scribble — that is expected and correct.

**A scribble IS:**
- Wireframe quality (labeled boxes, placeholder grey/white colors, no styling detail)
- Flutter-component-annotated (every element maps to a named Flutter widget)
- Persona-constraint-aware (accessibility, cognitive, motor constraints annotated)
- A structural design record

**A scribble is NOT:**
- A pixel-perfect mockup
- A design specification for colors or spacing
- A runnable prototype
- Production Flutter code
- A prediction of what the final app will look like


## Scribble Format

**Decision**: HTML/CSS is the primary scribble format. Each screen is a separate HTML file. [AC-01]

**File structure per scribble version**:
```
scribbles/v1/
  index.html                   ← lists all screens, shows flow sequence
  01_home_night_mode.html      ← one file per screen
  02_quick_entry.html
  03_voice_input_active.html
  04_entry_saved.html
  metadata.yaml
  feedback.md                  ← developer feedback from this version
```

**Why HTML/CSS**:
- Viewable in any browser without a Flutter build
- Well-represented in AI training data → fewer errors → faster iteration
- HTML element semantics (button, input, select) map naturally to Flutter widgets
- Fully disposable: no architecture overhead, no build system
- Per-screen files keep each panel manageable and reviewable independently

**`index.html`** must contain:
- Title of the requirement and version number
- Ordered list of screens with links to each file
- Brief description of each screen's purpose

**Exception — Flutter code for animation testing**:
When the developer needs to validate a specific animation (transition duration, easing curve), a minimal Flutter widget scribble may be used — only the animated component, no BLoC, no routing, no state management. This code is disposable (not committed, not production).

**Not used**:
- SVG: harder for AI to generate meaningfully, no semantic structure
- ASCII art: insufficient fidelity for element hierarchy
- Markdown: cannot express spatial layout
- Flutter widget trees for layout review: AI generates more errors, iteration is 2-3x slower


## AI Behavior Rules for Scribble Generation

These rules constrain what the AI produces when generating scribbles. [AC-02]

### Before generating

The AI MUST read:
1. All relevant T1/T2 design rules from `doc/presentation/` (and `doc/presentation/design/` when available)
2. The requirement's `user_needs` YAML to identify which personas are served
3. The identified personas' key constraints (motor, cognitive, environmental, timing — per REQ-PROC-026 trait categories)

### MUST DO

1. Generate ALL screens or steps of the flow scope as separate HTML files
2. Create an `index.html` listing all screens in order with links and descriptions
3. Use semantic HTML elements that correspond to Flutter widget equivalents (see SEC-09)
4. Label every element with its role (e.g., "Email Input", "Submit Button", "Error Message")
5. Apply T1/T2 design rules from `doc/presentation/`
6. Apply persona constraints for the personas served (e.g., 48dp+ targets for motor constraints)
7. Show element hierarchy through nesting and visual grouping
8. Include state variants when relevant (default, error, loading, empty)
9. Include a component mapping comment block at the top of each screen file
10. Complete quickly — structure and element choice over pixel-perfect styling
11. Use wireframe-level presentation: grey/white placeholder backgrounds, no brand colors

### MUST NOT

1. Implement JavaScript event handlers, form submission, or client-side logic
2. Add state management, BLoC events, or data binding
3. Connect to real APIs or mock backend data
4. Use complex CSS animations (unless this IS an animation test)
5. Hard-code brand colors or attempt to replicate Material Design 3 color scheme
6. Generate Dart/Flutter code in scribble files
7. Require a Flutter build to view the result
8. Silently change design rules — all rule changes go through the Rule Update Protocol (SEC-07)
9. Reference design token names for spacing values — exact token mapping is the implementation's job


## Storage and Organization

**Decision**: Scribbles live co-located with the requirement they document, committed to git. [AC-03, AC-04]

**Path**: `requirements_tasks/[category]/[requirement]/scribbles/`

**Why co-located**: An approved scribble is a requirement artifact. It captures the accepted structural design. It belongs next to the `requirements.md` that defines that feature.

**Why committed to git**: Design evolution is part of project history. Approved scribbles serve as reference during implementation. Rejected versions explain why decisions were made.

**Version structure**:
```
requirements_tasks/
  [category]/
    [requirement]/
      requirements.md
      scribbles/
        v1/
          index.html
          01_[screen_name].html
          02_[screen_name].html
          metadata.yaml           # status: superseded
          feedback.md             # feedback that led to v2
        v2/
          index.html
          01_[screen_name].html
          02_[screen_name].html
          metadata.yaml           # status: approved
        flutter_review/           # created by ui-verify-flutter after implementation
          comparison.md
```

**`metadata.yaml` format**:
```yaml
version: v2
date: 2026-03-01
status: approved            # draft | superseded | approved
requirement: REQ-[ID]
screens_covered:
  - 01_home_night_mode: "Home screen with night mode active"
  - 02_quick_entry: "Quick entry screen for voice input trigger"
personas_applied:
  - PERSONA-002 (Max): blank-field paralysis → structured prompts used
  - PERSONA-007 (Hanna): dark mode → true black backgrounds
rules_applied:
  - T1: touch targets ≥ 48dp (doc/presentation/design/t1_touch_targets.md)
  - T1: dark mode backgrounds (doc/presentation/design/t1_dark_mode.md)
flutter_component_mapping:
  button.primary: ElevatedButton (FilledButton in M3)
  button.secondary: OutlinedButton
  text_input: TextField with OutlineInputBorder
  card: Card with Material3 surfaceVariant
  list_item: ListTile
  bottom_nav: NavigationBar (M3)
  app_bar: AppBar with Material3 surface tint
new_rules_anchored: []     # filled after rule update protocol if rules were added
design_decisions:          # decisions NOT derivable from requirements or rules
  - decision: "Mood input uses slider, not discrete buttons"
    reason: "Feels more natural for continuous mood assessment — reduces anchoring bias"
    applies_to: [01_mood_entry.html]
```

**Versioning rule**: Each AI generation creates a new version folder. Old versions remain in git history. Only the most recent `status: approved` folder is the reference for implementation.

**`design_decisions:` field**: This section in `metadata.yaml` captures design choices that are not derivable from requirements, personas, or T1/T2/T3 rules. It is read by the auto-review agent when generating the next version to preserve continuity of decisions across context windows. [AC-04]

**Storage layout mirrors `lib/features/`**: Scribbles live under `requirements_tasks/scribbles/<feature_path>`, where `<feature_path>` mirrors the `lib/features/` tree 1:1 by name and hierarchy (and `lib/core/` maps to `_core/`). A scribble's `feature_path` metadata field resolves to exactly one node in that tree, and the existing scribble resides at its mirrored location rather than at any legacy co-located path. A **parity check** flags divergence in either direction — a scribble whose `feature_path` has no matching `lib/features/` node, or a feature path that no scribble covers where one is expected. The generation, iteration, and consumption skills (`ui-scribble-generator`, `ui-scribble-iterate`, `ui-verify-flutter`, and the `code-simple` / `code-complex` Sketch Gate) locate a requirement's scribble through this `feature_path` mirror, not through a hard-coded `[category]/[requirement]/scribbles/` path. [AC-05]

> The `feature_path` mirror is the authoritative scribble location; the co-located path described above is the historical layout that the mirror supersedes.

