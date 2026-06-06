---
id: REQ-PROC-032-04
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
      name: Optional multimodal input seed
      description: Phase 0 in skill.md checks inputs/ folder for sketch/reference
        images before Phase 1; passes them as vision context to Phase 1 agent if present;
        absent = Phase 1 unchanged
    - id: AC-02
      name: Optional draft generators
      description: draft_generator field in goal.md YAML (claude_design | stitch |
        none); Phase 1 conditionally delegates to external tool for first-draft HTML;
        output is always standard scribble format; default none = current behavior
    - id: AC-03
      name: Diff-based regeneration
      description: Phase 4 feedback classification includes 'affects screen X' vs
        'affects all'; metadata.yaml screen_versions map tracks per-screen version
        numbers; unaffected screens copied verbatim on targeted regeneration
    - id: AC-04
      name: Flow-based screen ordering
      description: metadata.yaml includes flow_positions[] array; Phase 1 reads parent
        user flow to determine canonical screen order before numbering; skill.md documents
        the algorithm
    - id: AC-05
      name: Cross-requirement iteration protocol
      description: Phase 4 Haiku impact check covers (a) implemented requirements,
        (b) approved scribbles referencing the changed rule, (c) scribbles using shared
        components that reference the rule; metadata.yaml stale_since and pending_rules[]
        fields documented
    - id: AC-06
      name: Flow-level composite index
      description: scripts/generate_flow_scribble_index.py generates requirements_user_needs/user_flows/<flow>/scribble_index.html
        by iframing approved scribble screens in flow-step order; Phase 5a in skill.md
        triggers it after approval when a flow reference exists
    - id: AC-07
      name: Component library
      description: requirements_tasks/_scribble_components/ exists with components.js
        and >=4 seed components (c_navigation_bar, c_app_bar, c_filled_button, c_mood_entry_card);
        maintenance protocol documented in SKETCHES_README.md
    - id: AC-08
      name: Developer viewing documented
      description: 'SKETCHES_README.md documents how to serve scribbles locally using
        the devcontainer''s python3 -m http.server started in the background (non-blocking),
        the URL pattern for opening individual screens and the flow composite index,
        and how to stop the server when done; flow_positions[] metadata format (fields:
        flow_id, screen_file, step_number, requirement_id) documented so developers
        know how to populate it'
    - id: AC-09
      name: Multi-breakpoint scribbles from persona device classes
      description: Personas declare the device classes they predominantly use; a requirement's
        required breakpoint set is the union across its served personas. Scribbles
        are generated per required breakpoint, and a screen whose layout is genuinely
        identical across breakpoints is generated once and marked as shared rather
        than duplicated.
    - id: AC-10
      name: Structured inspiration inputs
      description: 'A requirement''s inputs/ folder may contain inspiration references
        annotated with a per-aspect use/ignore matrix (e.g. use layout: true, use
        colors: false) plus an optional scope and note. ui-scribble-generator patterns
        the scribble after the used aspects, ignores the ignored aspects in favor
        of project conventions, and annotates each affected screen with the inspiration
        source.'
    - id: AC-11
      name: Reviewer pre-brief before generation
      description: Before the first expensive generation, the scribble workflow produces
        a concise pre-brief (≤300 words) stating which screens will be generated,
        personas and rules applied, what is out of scope this round, the information-model
        boundary, and any open assumptions. The developer can approve, adjust (regenerate
        the pre-brief), or reject scope (routing to requ-explore); the approved pre-brief
        is retained as a version artifact. A bounded number of pre-brief iterations
        is enforced before escalation.
    - id: AC-12
      name: Cross-feature consistency check
      description: When a scribble belongs to a feature that shares a user flow with
        other features that have their own scribbles, a consistency check flags divergent
        component choices for the same role across the sibling scribbles (e.g. one
        uses a FilledButton for primary confirmation, another a TextButton) for human
        resolution.
    - id: AC-13
      name: Automated visual validation after implementation
      description: A visual-validation capability compares integration-test screenshots
        of the implemented Flutter screens against the approved scribble and the re-derive
        sources (tokens, accessibility, persona sizing), producing an advisory findings
        report. It uses a vision-capable model, reads per-locked-item verification
        seeds emitted in flutter_handoff.yaml, and does not block by default. Its
        scope is distinct from ui-verify-flutter (code-only structural match) and
        ui-improve-flutter (human-driven polish).
    - id: AC-14
      name: Contributing-requirements and participating-flows discovery
      description: A scribble's contributing_requirements (the primary owning requirement
        plus cross-cutting requirements) and participating_flows are discovered automatically
        from its feature_path, the requirements_matrix, and a UI-scope heuristic,
        and written into the existing scribble_metadata.yaml fields (no new frontmatter
        fields are introduced — these fields already exist in the scribble metadata
        schema). Where discovery is ambiguous, the ambiguity is flagged for human
        review rather than the field being silently left empty. A consistency lint
        requires the primary contributing requirement to correspond to the scribble's
        feature_path.
  sections:
    - id: SEC-12
      name: Flow-Aware Scribble Generation
      heading: '## Flow-Aware Scribble Generation'
    - id: SEC-13
      name: Flow-Level Composite Index
      heading: '## Flow-Level Composite Index'
    - id: SEC-14
      name: Component Library
      heading: '## Component Library'
    - id: SEC-17
      name: Scribble Content Extensions
      heading: '## Scribble Content Extensions'
---

# Scribble Content Extensions

> **Implementation tasks:** This feature's ACs were implemented before REQ-PROC-032 was restructured into an epic (TASK-PROC-032-34, zero spec change), so it has no `tasks/` folder of its own. Some (if not all) of its implementing tasks live in the epic-level tasks folder `requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/` (the completed `scribble-*` batch). Only the genuinely-new features (F05–F07) carry their own derived `tasks/`.


## Scribble Content Extensions

Several content capabilities extend what a scribble can represent and how cheaply it can be reviewed. [AC-09..AC-14]

- **Multi-breakpoint generation.** Personas declare the device classes they predominantly use; a requirement's required breakpoint set is the union across its served personas. Scribbles are generated per required breakpoint; a screen whose layout is genuinely identical across breakpoints is generated once and marked shared, never duplicated. [AC-09]
- **Structured inspiration inputs.** A requirement's `inputs/` folder may carry inspiration references annotated with a per-aspect use/ignore matrix (use layout / ignore colors, etc.), an optional screen scope, and a free-text note. The generator patterns the scribble after the used aspects, ignores the rest in favour of project conventions, and annotates each affected screen with its inspiration source. [AC-10]
- **Reviewer pre-brief.** Before the first expensive generation, the workflow emits a concise pre-brief (≤300 words: screens to be generated, personas and rules applied, out-of-scope items, information-model boundary, open assumptions). The developer approves, adjusts (regenerating the pre-brief, bounded before escalation), or rejects scope (routing to `requ-explore`); the approved pre-brief is retained as a version artifact. [AC-11]
- **Cross-feature consistency check.** When a scribble's feature shares a user flow with sibling features that have their own scribbles, divergent component choices for the same role across siblings are flagged for human resolution. [AC-12]
- **Automated visual validation.** A visual-validation capability compares integration-test screenshots of the implemented screens against the approved scribble and the re-derive sources, producing an advisory (non-blocking) findings report using a vision-capable model and per-locked-item verification seeds emitted in `flutter_handoff.yaml`. Its scope is distinct from `ui-verify-flutter` (code-only structural match) and `ui-improve-flutter` (human-driven polish). [AC-13]
- **Contributing-requirements and participating-flows discovery.** A scribble's `contributing_requirements` (the primary owning requirement plus cross-cutting requirements) and `participating_flows` are discovered automatically — from the scribble's `feature_path`, the requirements matrix, and a UI-scope heuristic — and written into the existing `scribble_metadata.yaml` fields. No new frontmatter fields are introduced; these fields already exist in the scribble metadata schema. Where discovery is ambiguous, the ambiguity is flagged for human review rather than the field being silently emptied. A consistency lint requires the primary contributing requirement to correspond to the scribble's `feature_path`. [AC-14]

