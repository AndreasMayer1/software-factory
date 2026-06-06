---
id: REQ-PROC-032-06
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
      name: Severity-driven iteration stop and non-convergence circuit-breaker
      description: A scribble is converged when the latest review round (auto or developer-provided)
        contains no finding with severity ≥ MEDIUM. If severity ≥ MEDIUM findings
        persist across a defined number of consecutive auto-review rounds without
        being resolved, ui-scribble-iterate escalates to requ-explore rather than
        continuing indefinitely. No version-count ceiling or complexity-score threshold
        applies — severity governs whether iteration continues.
    - id: AC-02
      name: Flat un-nestable JSON script carrier renders nothing
      description: 'Every generated scribble screen carries its reviewer/coder detail
        in a single flat, un-nestable <script type="application/json" id="review-data">
        block rather than in HTML comments. Because <script> content is never rendered
        by the browser, no portion of the reviewer/coder detail is ever visible as
        page text; and because the carrier is a flat JSON document rather than nestable
        HTML comments, the comment-nesting render leak (R2§1: an inner <!-- … -->
        closes the outer block early and leaks the remainder as wall-of-text) is structurally
        impossible — there is no nesting construct to break. No generated scribble
        carries multi-line reviewer or coder detail in an HTML comment block.'
    - id: AC-03
      name: JSON carrier is the single dual-audience contract document
      description: 'The review-data JSON carrier is the single machine-readable source
        consumed by BOTH audiences — the findings-overlay script that renders the
        human review layer (AC-59) and the coder/LLM that implements the screen —
        with no second copy of the same detail elsewhere in the screen. Its schema
        carries, per screen and per element: the component mapping (HTML element →
        Flutter widget), the accessibility intent (semantic role, accessible-name
        obligation, alt-text obligation), the rule-application audit trace pairing
        each applied T1/T2 rule to a concrete element (the AC-27 trace, now carried
        in this block), and the per-element reviewer detail (what to critique, locked-in
        vs re-derive framing). Both audiences read the same keys; the carrier is emitted
        by ui-scribble-generator from the SKETCHES_README contract, not hand-authored
        per scribble.'
    - id: AC-04
      name: Visible human-facing review layer distinct from the machine carrier
      description: 'Each rendered scribble presents a human-readable review layer
        — formatted, with headings and progressive disclosure — that surfaces the
        reviewer-relevant subset of the review-data carrier so a human reviewer sees
        review guidance without reading raw JSON. This human layer is distinct from
        the machine JSON carrier (AC-57): the JSON block remains terse and machine-shaped
        and is never expanded for human readability, and the human layer is derived
        from the carrier rather than being a separately authored duplicate. (PROP-1.)'
    - id: AC-05
      name: Script-rendered findings overlay over the JSON carrier
      description: 'A findings-overlay script reads the review-data JSON carrier and
        renders, on each scribble screen, an overlay comprising three awareness layers:
        a per-screen findings count badge, per-element markers bound to the elements
        the findings anchor to (clickable to reveal the finding), and a gate prompt
        instructing the reviewer to read the findings before adding feedback. The
        overlay is script-rendered from the carrier (no per-screen hand authoring)
        and composes with per-reviewer finding provenance (AC-60). (PROP-13C.)'
    - id: AC-06
      name: Per-reviewer findings persisted and attributable
      description: Each scribble reviewer's raw findings are persisted to a per-reviewer
        file in the scribble task's plans_and_protocols/ folder before they are merged
        into the auto-review brief, so that a finding is attributable to the reviewer
        that raised it and the per-reviewer record survives across versions rather
        than being discarded at merge. This persistence is the provenance source the
        findings overlay (AC-59) draws on and the basis for weak-link-reviewer analysis.
        (PROP-4.)
    - id: AC-07
      name: Reusable, authored-once review-guide component
      description: A single review-guide component exists once under requirements_tasks/_scribble_components/
        and is referenced by scribbles rather than regenerated per screen or duplicated
        per version. It carries the static review guidance — the UX-review checklist
        (personas, value-trade-off decisions, flow fit, component choice, interaction
        principles with external reference links) behind progressive disclosure, an
        out-of-scope flat bullet list, and a short note on how T1–T3 rules are formed
        — content that does not vary by screen. A scribble references this one component;
        it is not copied into each screen file. (PROP-3.)
    - id: AC-08
      name: Script-generated small-multiples state variants without drift
      description: A screen's required state variants (e.g. empty, loading, error,
        filled) are generated by a script from a single source screen as small-multiples
        that highlight only the changed region, so there is no full-copy of the screen
        per state and therefore no full-copy drift when the base screen changes. Each
        generated variant retains its per-state semantics — the state it represents
        and the element(s) it modifies are identified — and each variant is visually
        anchored to the element it changes. (PROP-5.)
    - id: AC-09
      name: Sequential auto-reviewer execution
      description: The auto-review phase runs each reviewer agent sequentially — one
        completes before the next starts. No parallel fan-out of reviewer agents occurs.
        At most one reviewer is in flight at any time, bounding the scope of a session-limit
        hit to a single incomplete agent rather than requiring all agents to restart.
    - id: AC-10
      name: Gate-on-convergence default cadence
      description: 'The default cadence for the human review gate is auto-to-converged:
        the gate fires only when the auto-review round finds no severity ≥ MEDIUM
        finding. Alternative cadence policies (every, after:[N], gate-at-v1) exist
        as named overrides configurable per invocation; the default is not overridden
        absent explicit configuration.'
    - id: AC-11
      name: Selective reviewer skip on low-severity rounds (PROP-7)
      description: A reviewer whose previous round produced no severity ≥ MEDIUM finding
        is skip-eligible in the next auto-review round; its agent is omitted to reduce
        token cost. Skip-eligibility is overridden when developer feedback incorporated
        since the last run touches that reviewer's declared scope. The skip applies
        per-round, not permanently.
    - id: AC-12
      name: question.md carries decision-asks only (PROP-6)
      description: The Phase-3 developer-feedback gate emits a question.md that contains
        only the decision-asks for that round. Orientation content (what the scribble
        covers, what changed) lives in the scribble. The fix-recap (issues the auto-review
        resolved) is absent from question.md; it lives in auto_review_brief.md and
        the per-reviewer finding files.
  sections:
    - id: SEC-19
      name: Scribble Carrier Format and Human Review Layer
      heading: '## Scribble Carrier Format and Human Review Layer'
    - id: SEC-20
      name: Auto-Review Control Model
      heading: '## Auto-Review Control Model'
---

# Carrier And Auto Review


## Scribble Carrier Format and Human Review Layer

A scribble has two readers of the same screen: a **machine** (the coder/LLM that implements it, and the scripts that render review aids) and a **human** (the reviewer at the approval gate). Both need the same underlying detail — which element maps to which widget, which rule was applied where, what to critique — but they need it in different shapes. How that detail is *carried* in the artifact is one shared locus, so the carrier format and the human review layer are defined together here. [AC-02..AC-08]

**One carrier, two audiences, zero leak.** Each scribble screen carries its reviewer/coder detail in a single flat, un-nestable `<script type="application/json" id="review-data">` block — not in HTML comments. This fixes a concrete grounded defect and removes its possibility at once. The previous carrier wrapped reviewer detail in one large `<!-- … -->` block and then emitted inline `<!-- a11y-intent: … -->` comments inside it; because HTML comments cannot nest, the parser closed the outer block at the first inner `-->` and leaked everything after it as visible, unstyled wall-of-text, including the literal trailing `-->` (R2§1, line-grounded on `02_handover_send.{tablet,desktop}.html`). A `<script type="application/json">` block renders nothing, so no detail can ever appear as page text; and it is a flat JSON document with no nesting construct to break, so the comment-nesting leak is **structurally impossible**, not merely avoided by careful authoring. This is the carrier that makes the human review layer (PROP-1) implementable and the leak impossible in the same change. [AC-02]

**The carrier is the single dual-audience contract document.** The `review-data` JSON is the one machine-readable source both audiences read — the findings-overlay script that builds the human review layer, and the coder/LLM that implements the screen — with no second copy of the same detail elsewhere on the screen. Its schema carries, per screen and per element:

- the **component mapping** (HTML element → Flutter widget) the coder consumes;
- the **accessibility intent** (semantic role identity, accessible-name obligation, alt-text obligation) — the locked-in a11y facet (cf. the Scribble–Coder Contract);
- the **rule-application audit trace** pairing each applied T1/T2 rule to the concrete element it shaped — the REQ-PROC-032-03 AC-11 trace, now carried in this block rather than in comments;
- the **per-element reviewer detail** (what to critique, with locked-in vs re-derive framing).

The block stays terse and machine-shaped; it is emitted by `ui-scribble-generator` from the `SKETCHES_README` contract, not hand-authored per scribble. [AC-03]

**The human review layer is rendered, distinct, and derived from the carrier (PROP-1).** Each rendered scribble presents a human-readable review layer — formatted, with headings and progressive disclosure — surfacing the reviewer-relevant subset of the carrier so a reviewer sees review guidance without reading raw JSON. It is *distinct* from the JSON block (which is never expanded for human readability) and *derived* from it (not a separately authored duplicate that could drift). This is the second half of the dual-audience design: the terse machine block for the coder/overlay script, the rendered panel for the human. [AC-04]

**A script renders a findings overlay over the carrier (PROP-13C).** A findings-overlay script reads the same `review-data` carrier and renders, per screen, three awareness layers: a **findings count badge**, **per-element markers** bound to the elements that findings anchor to (clickable to reveal the finding), and a **gate prompt** telling the reviewer to read findings before adding feedback. The overlay is script-rendered from the carrier — no per-screen hand authoring — and composes with per-reviewer provenance. [AC-05]

**Per-reviewer findings are persisted and attributable (PROP-4).** Each reviewer (rule, persona-walk, heuristics, cross-feature, per-flow walk) writes its raw findings to a per-reviewer file in the scribble task's `plans_and_protocols/` folder *before* the merge into the auto-review brief, so a finding is attributable to the reviewer that raised it and the record survives across versions instead of being discarded at merge. This persisted record is the provenance the overlay (AC-05) draws on and the basis for weak-link-reviewer analysis; it also satisfies the file-based-memory rule that every reviewing agent persists its findings. [AC-06]

**The review guide is one reusable component, not per-screen prose (PROP-3).** The static review guidance does not vary by screen, so it lives once as a review-guide component under `requirements_tasks/_scribble_components/` and is *referenced* by scribbles rather than regenerated per screen or duplicated per version. It carries the UX-review checklist (personas, value-trade-off decisions, flow fit, component choice, interaction principles with external reference links) behind progressive disclosure, an out-of-scope flat bullet list, and a short note on how T1–T3 rules are formed. A scribble references this single component; the guidance is not copied into each screen file. [AC-07]

**State variants are script-generated small-multiples without drift (PROP-5).** A screen's required state variants (e.g. empty, loading, error, filled) are generated by a script from a single source screen as **small-multiples** that highlight only the changed region — so there is no full copy of the screen per state, and therefore no full-copy drift when the base screen changes. Each variant retains its per-state semantics: the state it represents and the element(s) it modifies are identified, and each variant is visually anchored to the element it changes. [AC-08]


## Auto-Review Control Model

The auto-review phase orchestrates specialist reviewer agents and controls when the human review gate fires. The model is defined by five properties: sequential execution, severity-driven convergence, a gate-on-convergence default cadence, round-by-round selective reviewer skip, and a `question.md` trimmed to decision-asks only. [AC-01, AC-09, AC-10, AC-11, AC-12]

**Sequential execution.** Each reviewer agent completes before the next starts. No parallel fan-out of reviewer agents occurs. If a session or token limit is reached mid-run, at most one reviewer is left incomplete; the remaining reviewers resume from that point rather than the entire set needing to restart. [AC-09]

**Convergence and severity-driven iteration stop.** A scribble is converged when the latest review round (auto or developer-provided) contains no finding with `severity ≥ MEDIUM`. `LOW`-only findings constitute a converged state. When `severity ≥ MEDIUM` findings persist across a defined number of consecutive auto-review rounds without resolution, `ui-scribble-iterate` escalates to `requ-explore` — the likely cause is requirement ambiguity, not a quality gap the reviewers can close. No version-count ceiling or complexity metric applies; severity alone governs whether iteration continues. [AC-01]

**Default cadence: gate on convergence.** The human review gate fires only when the scribble has converged — when the auto-review round finds no `severity ≥ MEDIUM` finding. Alternative cadences (`every`, `after:[N]`, `gate-at-v1`) exist as named overrides configurable per invocation; the default is `auto-to:[converged]`. [AC-10]

**Selective reviewer skip (PROP-7).** On a subsequent auto-review round, a reviewer whose previous round produced no `severity ≥ MEDIUM` finding is skip-eligible for that round, reducing token cost. Skip-eligibility is overridden whenever developer feedback incorporated since the last run touches that reviewer's declared scope. The skip applies per-round, not permanently. [AC-11]

**Developer gate content — `question.md` carries decision-asks only (PROP-6).** The Phase-3 gate emits a `question.md` containing only the decision-asks for that round. Orientation content lives in the scribble; the fix-recap lives in `auto_review_brief.md` and the per-reviewer finding files. [AC-12]

