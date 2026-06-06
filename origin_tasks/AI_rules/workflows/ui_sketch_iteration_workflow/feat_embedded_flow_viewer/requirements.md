---
id: REQ-PROC-032-07
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
      name: Embedded flow-viewer sidebar
      description: The scribble's index.html contains a 'Show User Flows' toggle that
        opens a sidebar panel; the panel presents one tab per user flow listed in
        the scribble's flow_positions metadata; selecting a tab renders that flow's
        content inline. When no user flows are associated with the scribble, the toggle
        is absent.
    - id: AC-02
      name: Script-driven flow content — no LLM re-emission
      description: Flow content displayed by the flow viewer is sourced by a generator
        helper script that copies or symlinks the canonical user flow Markdown files
        into the scribble artifact directory. No LLM agent reads flow source files
        and re-emits their content as HTML in the scribble. The single normative copy
        — the canonical flow source — is what the viewer renders.
    - id: AC-03
      name: 'Markdown renderer: developer-authorized, client-side vendored, pinned'
      description: The flow viewer renders Markdown to HTML using a single pinned,
        client-side, vendored JavaScript renderer bundled within the scribble artifact
        directory. The renderer is not added without recorded developer pre-authorization
        under REQ-PROC-060 AC-01. The recommended approach is a single-file pinned
        client-side renderer (the marked-class of libraries), preferred over a build-step
        approach because it keeps the scribble artifact self-contained and zero-build.
        The pinned renderer file is not updated without a fresh REQ-PROC-060 admission
        evaluation.
    - id: AC-04
      name: Flow-passage colour-highlighting from flow_positions (conditional)
      description: When the scribble's flow_positions metadata names specific step
        numbers for a flow, the flow viewer highlights the text passages corresponding
        to those step numbers in a distinct colour. The highlighting is derived mechanically
        from flow_positions.step_number mappings — no LLM re-read of the flow is performed.
        Passages not mapped to any scribble step are rendered at reduced opacity.
        When step numbers are absent or no per-step text anchors can be resolved,
        the viewer renders unhighlighted flow text.
  sections:
    - id: SEC-21
      name: Embedded Flow-Viewer Sidebar
      heading: '## Embedded Flow-Viewer Sidebar'
---

# Embedded Flow Viewer


## Embedded Flow-Viewer Sidebar

The scribble provides inline access to the user flow(s) it participates in, so a reviewer can read flow intent alongside the scribble screens without leaving the browser tab. [AC-01..AC-04]

**Flow viewer toggle.** Each scribble's `index.html` carries a "Show User Flows" toggle button. Activating it opens a sidebar panel; the panel presents one tab per user flow listed in the scribble's `flow_positions` metadata. Selecting a tab renders that flow's Markdown content as HTML inline. When no flows are associated with the scribble, the toggle is absent. [AC-01]

**Script-driven sourcing — no LLM re-emission.** Flow content is injected by the generator helper script that already runs during scribble creation. The script copies or symlinks the canonical user flow Markdown files (from `requirements_user_needs/user_flows/`) into the scribble artifact directory. No LLM agent reads the flow files and re-emits their content as HTML; the single normative copy — the canonical flow source — is what the viewer renders. This enforces both the single-source constraint (no second normative copy of flow content) and the token-minimisation constraint (no per-generation re-read of large flow documents). [AC-02]

**Markdown→HTML renderer — developer-authorized, client-side vendored, pinned.** Flows are authored in Markdown; the viewer requires a Markdown-to-HTML renderer. Because adding a renderer constitutes a dependency admission under REQ-PROC-060, an agent must not include the renderer without recorded developer pre-authorization. The recommended approach — a single pinned static JS file bundled inside the scribble artifact (the `marked`-class of libraries) — keeps the scribble self-contained and zero-build; the alternative (build-step MD→HTML baking) avoids shipping a JS file but adds a build dependency and produces a static, non-live rendering. The developer's authorization records the chosen approach and the specific pinned file; the renderer is not updated without a fresh admission evaluation. [AC-03]

**Flow-passage colour-highlighting from flow_positions (conditional).** When a scribble's `flow_positions` metadata maps specific step numbers to screens, the viewer highlights the flow text passages corresponding to those step numbers in a distinct colour, so a reviewer immediately sees which flow steps are in scope for the screens being reviewed. The highlighting is derived mechanically from `flow_positions.step_number` mappings — no LLM re-read of the flow is performed. Passages not mapped to any scribble step are rendered at reduced opacity. When step numbers are absent from `flow_positions`, or when no text anchors can be resolved for the listed steps, the viewer renders unhighlighted flow text (graceful degradation). [AC-04]

