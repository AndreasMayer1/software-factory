---
id: REQ-PROC-032-03
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
      name: Three-skill workflow scope defined
      description: ui-create-sketch, ui-verify-flutter, ui-improve-flutter scopes
        are documented and non-overlapping
    - id: AC-02
      name: Post-implementation verification defined
      description: ui-verify-flutter structural check and ui-improve-flutter visual
        polish are defined as the mandatory post-implementation steps
    - id: AC-03
      name: Cost management for Flutter iteration defined
      description: ui-improve-flutter caps at 5 files/session; one targeted fix agent
        per file; agent scope minimization documented
    - id: AC-04
      name: Flutter handoff YAML
      description: Phase 5 emits scribbles/v{n}/flutter_handoff.yaml with per-element
        html_selector→flutter_widget→material3_variant→persona_constraints[]→rules_applied[];
        ui-verify-flutter updated to consume it as primary source
    - id: AC-05
      name: Scribble–coder contract is single-sourced
      description: 'SKETCHES_README.md contains a ''What a Scribble Commits To'' section
        that enumerates two disjoint sets: LOCKED-IN (screen list+order, Flutter widget
        choices, information hierarchy, copy text, canon labels, personas-applied+constraint,
        T1/T2 rules cited, persona-derived sizing as named token references, required
        states empty/loading/error, navigation pattern, dialog pattern, component-library
        usage, information-model boundary, design decisions, accessibility intent)
        and RE-DERIVE (exact token values, colors, accessibility implementation, animation
        curves/timing, responsive breakpoint mechanics, hover/focus/pressed states,
        BLoC/behavior wiring, cross-persona constraints not visible in the scribble).
        This section is the single normative source; no other artifact restates the
        two lists.'
    - id: AC-06
      name: CONTRACT BLOCK present in scribble output
      description: 'Every generated scribble''s index.html (and a compact per-screen
        variant) carries a CONTRACT BLOCK with dual framing: a reviewer-facing part
        (''critique these locked-in decisions; do not critique the re-derive items'')
        and a coder-facing part (''implement locked-in as shown; re-derive the rest
        from doc/ + tokens.json''). ui-scribble-generator emits it verbatim from the
        SKETCHES_README contract; it is not hand-authored per scribble. The per-screen
        machine-readable detail underlying this dual framing is carried in the screen''s
        review-data JSON carrier (AC-56, AC-57); the reviewer-facing framing is surfaced
        through the rendered human review layer (AC-58).'
    - id: AC-07
      name: Contract block in flutter_handoff.yaml
      description: 'flutter_handoff.yaml carries a top-level contract: block listing
        the locked_in and re_derive item keys plus a source pointer to the SKETCHES_README
        contract section, and a design_decisions: block propagating the scribble metadata''s
        design_decisions (the choices not derivable from requirements, personas, or
        rules) so the implementer sees them. ui-scribble-handoff-emitter produces
        both blocks; .claude/schemas/flutter_handoff.yaml validates them.'
    - id: AC-08
      name: Coding consumers honor the contract
      description: When code-simple or code-complex begins a Presentation-layer task
        with an approved scribble, the Sketch Gate directs the implementer to read
        flutter_handoff.yaml's contract block, implement the locked-in items as shown,
        and re-derive the re_derive items from doc/presentation/ and tokens.json regardless
        of whether the scribble depicts them.
    - id: AC-09
      name: Verifier scope anchored to the contract
      description: 'ui-verify-flutter evaluates only locked-in items against the scribble:
        a divergence on a locked-in item is reported as a coder defect; a re-derive
        item is reported as out_of_contract (not opined on against the scribble).
        The classification taxonomy makes the contract boundary explicit in every
        finding.'
    - id: AC-10
      name: Persona sizing as token reference; accessibility intent locked
      description: Generated scribbles express persona-derived sizing constraints
        as named token references (e.g. a min-tap-target token) rather than literal
        pixel values; the literal resolves from the token registry. Accessibility
        INTENT (semantic element choice, ARIA role identity, alt-text obligation,
        accessible-name presence) is part of the locked-in set and is present in generated
        scribbles; accessibility IMPLEMENTATION (focus order, announcements, WCAG
        verification) remains a re-derive item.
    - id: AC-11
      name: Rule-application audit trace
      description: Each generated scribble screen carries a machine-readable trace
        of which T1/T2 rule was applied to which element, so that rule-reviewer and
        a human can verify every claimed rule application against a concrete element
        rather than a metadata assertion alone. This trace is carried in the screen's
        review-data JSON carrier (AC-57).
    - id: AC-12
      name: Heuristics corpus reconciled and canonical
      description: 'doc/presentation/heuristics/ no longer carries a PROVISIONAL marker:
        its Nielsen, Universal Design, microinteraction, dark-pattern, and motion-as-function
        checks are reconciled with the Q1 scribble-review design and aligned with
        the surfaces owned by persona-walker and rule-reviewer (no double-ownership).
        ui-scribble-heuristics-reviewer applies it as canonical doctrine.'
    - id: AC-13
      name: Auto-review brief and inter-version diff
      description: After regenerating an even version, ui-scribble-auto-review produces
        (a) an auto-review brief telling the reviewer what to focus on this round,
        and (b) an inter-version structural diff between the prior and new version;
        the diff is viewable via a toggle in the scribble HTML that visually highlights
        changed elements. The brief links to the diff. The findings this brief draws
        on are surfaced on the screens through the script-rendered findings overlay
        over the review-data carrier (AC-59), backed by per-reviewer finding provenance
        (AC-60).
    - id: AC-14
      name: Persona-conflict surfacing with DDR link
      description: When the persona-walker or heuristics review surfaces a screen-level
        conflict between two personas' needs, the scribble marks the conflict point
        and links it to a Design Decision Record (or routes it upstream via the revision
        channel when the resolution implies a flow or VCD change) rather than silently
        choosing one persona.
    - id: AC-15
      name: Per-flow navigation captured
      description: 'For each user flow a scribble participates in, the flow folder
        carries a flow_navigation.yaml describing that flow''s screen-to-screen navigation:
        edges (which screen leads to which), the trigger for each edge, escape paths,
        and the back-stack policy. ui-scribble-handoff-emitter emits and keeps this
        file current; flutter_handoff.yaml points to the relevant flow_navigation.yaml
        file(s); ui-verify-flutter and the coding consumer read it to verify and implement
        navigation.'
    - id: AC-16
      name: Per-flow walk validation before approval
      description: Before a scribble version is approved, ui-scribble-auto-review
        walks the scribble's screens in each participating flow's step order and verifies
        that each step's intent is supported by a screen and its elements. A step
        whose intent is unsupported because the flow itself is flawed is routed upstream
        through the revision channel rather than patched in the scribble. The auto-review
        brief carries, per participating flow, one-line human walk instructions (which
        file to open and which screens to view in which order).
    - id: AC-17
      name: Approval trail aggregated across versions
      description: On approval, an APPROVAL_TRAIL.md for the scribble aggregates the
        decision history across all versions — the alternatives that were rejected,
        the key trade-offs, and the rationale behind locked decisions — synthesized
        from the per-version feedback.md, the auto-review briefs, and the inter-version
        diffs. ui-scribble-approve-handoff emits it as an approval-time artifact.
  sections:
    - id: SEC-11
      name: Three-Skill Workflow
      heading: '## Three-Skill Workflow'
    - id: SEC-15
      name: Scribble–Coder Contract
      heading: '## Scribble–Coder Contract'
    - id: SEC-16
      name: Scribble Review Doctrine
      heading: '## Scribble Review Doctrine'
---

# Handoff Skills And Contract

> **Implementation tasks:** This feature's ACs were implemented before REQ-PROC-032 was restructured into an epic (TASK-PROC-032-34, zero spec change), so it has no `tasks/` folder of its own. Some (if not all) of its implementing tasks live in the epic-level tasks folder `requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/` (the completed `scribble-*` batch). Only the genuinely-new features (F05–F07) carry their own derived `tasks/`.


## Three-Skill Workflow

The UI design iteration process is split across three skills with distinct, non-overlapping scopes. [AC-01, AC-02, AC-03]

### ui-create-sketch — Structural Scribble Generation

**When**: Before any Flutter implementation begins. [AC-01]

**Purpose**: Generate and iterate structural HTML wireframe scribbles.

**The skill DOES**:
1. Read `requirements.md`, relevant personas, and all T1/T2 rules before generating
2. Spawn a dedicated fresh-context agent per scribble version (prevents context overflow)
3. Generate per-screen HTML files + `index.html` for the requirement's UI scope
4. Create `metadata.yaml` with applied rules, personas, component mapping, and `design_decisions:`
5. Create `feedback.md` template
6. After every odd version (v1, v3, …): spawn a fresh agent to auto-review against ACs, personas, and T1/T2 rules and regenerate as the next even version
7. When user feedback is received: run the Rule Update Protocol (SEC-07)
8. When T1/T2 rules are involved: spawn a Haiku agent for impact check
9. When a rule is approved: invoke `doc-update-guidelines` to anchor it
10. Create the next scribble version after rules are anchored
11. Update `metadata.yaml` to `status: approved` when developer approves
12. Report: "Scribble approved. Proceed to implementation. After implementation, use `ui-verify-flutter` to check structural match, then `ui-improve-flutter` for visual polish."

**The skill DOES NOT**:
- Validate that proposed rules match persona needs (that's `ux-validate-rule`)
- Write to `doc/presentation/` directly (that's `doc-update-guidelines`)
- Update `requirements.md` (that's `requ-explore`)
- Generate Dart/Flutter implementation code
- Make tier classification decisions unilaterally — always presents for human approval
- Proceed past a T1/T2 rule identification without human sign-off

### ui-verify-flutter — Structural Verification After Implementation

**When**: After Flutter implementation is complete, before visual polish. [AC-02]

**Purpose**: Verify that the Flutter implementation structurally matches the approved scribble.

**The skill DOES**:
1. Find the approved scribble and list all scribble screens
2. For each screen: identify matching Flutter widget file(s) via CodeGraph, then verify component mapping
3. Check persona constraints (touch targets, copy safety, accessibility flags) in the implementation
4. Write a structured comparison report to `scribbles/flutter_review/comparison.md`
5. Classify each finding: `match` | `deviation` | `token_violation` | `rule_violation` | `missing_element` | `acceptable`
6. Report findings and recommend `ui-improve-flutter` if non-acceptable deviations exist

**The skill DOES NOT**:
- Modify any source file (read-only)
- Classify new T1/T2 rules (reports deviations; classification is human's decision)
- Attempt visual verification (no screenshot tooling assumed)

**Scope discipline**: If >5 screens, spawn a separate agent per screen — pass only that screen's HTML + its Flutter file(s), not the full codebase.

### ui-improve-flutter — Visual Polish Iteration

**When**: After `ui-verify-flutter` completes, or any time visual quality needs improvement. [AC-02, AC-03]

**Purpose**: Iterate the visual quality of implemented Flutter screens — colors, spacing, proportions, component polish. Never changes behavior.

**The skill DOES**:
1. Load only the screen file(s) in scope — never the full codebase
2. Read `tokens.json`, relevant T1/T2 rules, and persona motor/cognitive constraints
3. Scan for: token violations (hardcoded values), sizing inconsistencies, missing `Semantics` widgets, alignment issues
4. If user provides a screenshot: analyze with Claude vision for visual hierarchy, contrast, alignment
5. Group proposals: (a) token compliance, (b) accessibility, (c) visual polish
6. Apply (a) and (b) automatically on approval; ask separately for (c)
7. Spawn one targeted fix agent per file with minimal context (single file + rule + instruction)
8. Run `flutter test` + check for failures after each batch; revert and report if tests fail
9. Run `dart fix --apply` before committing

**The skill DOES NOT**:
- Change behavior, routing, BLoC, domain, or data layer files — presentation only
- Load files outside the feature being improved

**Cost management** [AC-03]:
- Maximum 5 files per session — stops and reports if limit would be exceeded
- One targeted fix agent per file, never more than 3 files per fix agent
- Agents receive only: single file + specific rule or token reference + exact instruction

---


## Scribble–Coder Contract

A scribble is a **contract** between the design step and the implementation step: it commits to some decisions and explicitly defers others. Earlier versions of this workflow left that contract implicit, which produced silent failures — a coder could under-implement a committed decision (e.g. persona-safe copy) or over-fit to a deferred one (e.g. placeholder colors). The contract is therefore made explicit and single-sourced. [AC-05..AC-11]

**Single source of truth.** The canonical, enumerated contract lives in one place — the "What a Scribble Commits To" section of `requirements_tasks/SKETCHES_README.md` — and no other artifact restates the two lists. It defines two disjoint sets:

- **LOCKED-IN** — the scribble commits to these; the implementer reproduces them as shown: screen list and order; Flutter widget choices; information hierarchy; copy text; canon labels; personas applied and the specific constraint each enforces; T1/T2 rules cited; persona-derived sizing expressed as named token references; required screen states (empty / loading / error); navigation pattern; dialog pattern; component-library usage; information-model boundary; design decisions; and **accessibility intent** (semantic element choice, ARIA role identity, alt-text obligation, accessible-name presence).
- **RE-DERIVE** — the scribble deliberately does not commit to these; the implementer derives them from `doc/presentation/` and the token registry regardless of what the scribble depicts: exact token values; colors; **accessibility implementation** (focus order, screen-reader announcements, WCAG verification); animation curves and timing; responsive breakpoint mechanics; hover/focus/pressed visual states; BLoC and behaviour wiring; and cross-persona constraints not visible in the scribble.

**Two refinements over the naive split** (grounded in how mainstream design-to-code tools draw the line):
- Persona-derived sizing is locked as a *named token reference*, not a literal pixel value — the literal resolves from the registry, so the registry stays the single source of dimensional truth. [AC-10]
- Accessibility *intent* is locked while accessibility *implementation* is deferred — the scribble commits to "this is a button with an accessible name", not to the focus-order wiring. [AC-10]

**The contract is surfaced at every boundary where it is consumed:**
- In the scribble itself, as a CONTRACT BLOCK with dual reviewer/coder framing, emitted by `ui-scribble-generator`. [AC-06]
- In `flutter_handoff.yaml`, as a `contract:` block emitted by `ui-scribble-handoff-emitter` and validated by `.claude/schemas/flutter_handoff.yaml`; the same handoff also carries a `design_decisions:` block that propagates the scribble metadata's `design_decisions` (choices not derivable from requirements, personas, or T1/T2/T3 rules) to the implementer, so a locked decision such as "mood input uses a slider, not discrete buttons" reaches the coder rather than living only in `metadata.yaml`. [AC-07]
- At the coding consumer, via the Sketch Gate in `code-simple` / `code-complex`. [AC-08]
- At verification, via `ui-verify-flutter`'s contract-anchored classification: a locked-in divergence is a coder defect; a re-derive item is `out_of_contract`. [AC-09]

A generated scribble also carries a machine-readable **rule-application audit trace** — which T1/T2 rule was applied to which element — so every claimed rule application is verifiable against a concrete element, not just asserted in metadata. [AC-11]

**Per-flow navigation is part of the handoff.** A scribble shows screens; the *navigation between them* is captured per flow. For each user flow a scribble participates in, the flow folder carries a `flow_navigation.yaml` describing that flow's edges (which screen leads to which), each edge's trigger, escape paths, and the back-stack policy. `ui-scribble-handoff-emitter` emits and maintains this file; `flutter_handoff.yaml` points to the relevant `flow_navigation.yaml` file(s); `ui-verify-flutter` and the coding consumer read it so navigation is verified and implemented from a declared source rather than inferred from screen order. [AC-15]

**The approval is itself a documented decision.** On approval, an `APPROVAL_TRAIL.md` for the scribble aggregates the decision history across all versions — the alternatives that were rejected, the key trade-offs, and the rationale behind the locked decisions — synthesized from the per-version `feedback.md`, the auto-review briefs, and the inter-version diffs. `ui-scribble-approve-handoff` emits it as an approval-time artifact, so the "why" behind the final design survives beyond the version folders. [AC-17]


## Scribble Review Doctrine

Scribble review is performed by three reviewer agents with disjoint, declared scopes, an orchestration-level fatigue rail, and a per-flow walk validation before approval. [AC-12..AC-14, REQ-PROC-032-06 AC-01, AC-16]

- **`ui-scribble-rule-reviewer`** — owns T1/T2 design-rule specifics (the dp values, confirmation-placement wording).
- **`ui-scribble-persona-walker`** — embodies each applied persona and verifies that persona's PRIMARY constraint is enforced in the actual HTML, not merely cited in a comment.
- **`ui-scribble-heuristics-reviewer`** — applies the project's UX-heuristics corpus (`doc/presentation/heuristics/`: Nielsen's usability heuristics, the Universal Design principles, Saffer microinteraction completeness, dark-pattern detection, motion-as-function) at wireframe level. This corpus is **canonical** (no PROVISIONAL marker) and reconciled so it never re-checks concerns owned by the persona-walker, the rule-reviewer, or the accessibility guidelines. [AC-12]

The auto-review step (`ui-scribble-auto-review`) produces, after each even-version regeneration, an **auto-review brief** (what the reviewer should focus on this round) and an **inter-version diff** between the prior and new version, viewable through a toggle in the scribble HTML that highlights changed elements; the brief links to the diff. [AC-13]

When review surfaces a screen-level **conflict between two personas' needs**, the conflict point is marked and linked to a Design Decision Record — or routed upstream through the revision channel when its resolution implies a flow or value-trade-off change — rather than silently resolved. [AC-14]

`ui-scribble-iterate` carries a **severity-driven iteration rail and a non-convergence circuit-breaker**: iteration continues while the latest review round contains a `severity ≥ MEDIUM` finding; when MEDIUM-or-higher findings persist across a defined number of consecutive auto-review rounds without resolution, `ui-scribble-iterate` escalates to `requ-explore` rather than continuing. No version-count ceiling or complexity metric applies. [REQ-PROC-032-06 AC-01]

**Per-flow walk validation before approval.** Beyond per-screen review, the scribble is validated against each flow it participates in *as a walk*. Before approval, `ui-scribble-auto-review` walks the scribble's screens in each participating flow's step order and verifies that every step's intent is supported by a screen and its elements. When a step's intent is unsupported because the flow itself is flawed (a missing or contradictory step), the gap is routed upstream through the revision channel rather than patched into the scribble. The auto-review brief carries, per participating flow, one-line **human walk instructions** — which file to open and which screens to view in which order — so a reviewer can repeat the walk. [AC-16]

