# Design-Thinking Iteration 2 — addressing feedback + further improvements

**Task:** TASK-PROC-032-10 · **Date:** 2026-05-27 · **Model:** Opus 4.7
**Input:** `2026-05-27_03_feedback.md` (user feedback on the round-1 synthesis)
**Output to:** this file. Recommendations in §4 become candidate impl-task seeds.

> Methodology note: this round is the design-thinking divergent expansion. §1 responds to each user feedback point with a concrete proposal (or a sharp counter-question). §2 expands beyond the user's points into adjacent improvements the synthesis context now makes visible. §3 maps couplings (what can be done independently). §4 surfaces decisions.

---

## 1. Responses to the seven feedback points

### 1.1 "Things not covered by scribbles don't get a serious evaluation — or skip the evaluation; that would be more honest"

**Agreed and sharpened.** The current `ui-verify-flutter` taxonomy (`match | deviation | token_violation | rule_violation | missing_element | acceptable`) silently *evaluates against the scribble even for things the scribble does not commit to*. This is dishonest in two directions:

- It can flag a `token_violation` against a scribble that *deliberately omitted* token specification → coder gets blamed for re-deriving a token they were required to re-derive.
- It can flag `acceptable` when the coder made a reasonable derivation → the verdict says "OK" but conveys no signal about whether the derivation matches `doc/` rules.

**Proposed reshape of `ui-verify-flutter` Phase 3 + classification.** Two changes:

**Change-A: Restrict verifier scope to the locked-in list.** Phase 3 only evaluates items L1–L15 (per §4.1 + §4.5 of synthesis). Items D1–D8 are *out of scope* of this verifier — the verifier does not produce findings against them. The taxonomy collapses to:

| New classification | Meaning |
|---|---|
| `locked_match` | Locked-in item implemented as scribble shows |
| `locked_deviation` | Locked-in item differs from scribble (coder bug, must fix) |
| `locked_missing` | Locked-in item absent in implementation (coder bug, must fix) |
| `locked_unclear` | Locked-in item ambiguous — needs developer clarification |
| `out_of_contract` | Item is on the re-derive side — verifier does not opine; re-derive items are the job of `ui-improve-flutter` and the visual-validation check (see §1.2) |

The `token_violation` / `rule_violation` categories disappear from *this* verifier. They move to either `ui-improve-flutter` (token compliance + visual polish) or to a new screenshot-based validator (see §1.2). This is more honest *and* more focused: each verifier has a single contract.

**Change-B: Skip evaluation entirely for re-derive items.** The verifier reports `out_of_contract` once per re-derive item it would have evaluated, with the comment "Re-derive item — see `doc/presentation/...` for the source of truth; check with `ui-improve-flutter` or the visual-validation step." Reviewers know what was NOT checked.

**Cost:** small — rewriting `ui-verify-flutter` Phase 4 report template + Phase 5 handoff. Re-test risk: low (verifier is read-only; finding *fewer* things is safer than finding more).

### 1.2 "Visual validation via screenshots in integration tests"

**Strong feature idea — proposing it as a new skill, not an extension of ui-verify-flutter.** Two ingredients:

**Ingredient I — integration test produces screenshots.** Flutter's `integration_test` package supports `flutter test integration_test/foo_test.dart --screenshot=out_dir`. Each named test pumps the widget tree, drives to a target state, and emits a PNG. Already partially supported in our stack (we have `integration_test/`); we'd need a per-screen golden-screenshot test scaffold + an output convention (e.g. `integration_test/screenshots/<feature>/<screen>_<breakpoint>.png`).

**Ingredient II — vision-validation skill.** New skill (working name `ui-visual-validate`) that:

1. Runs the integration-test screenshot pipeline.
2. For each `<screen>_<breakpoint>.png` produced, opens the corresponding scribble screen HTML in a headless-Chromium snapshot (or skips this and uses the scribble HTML directly as the reference).
3. Spawns a vision-capable agent (Claude Sonnet 4.6 / Opus 4.7 with multimodal input) that compares the screenshot against the scribble + `doc/presentation/` token rules + persona constraints. Outputs structured findings:
   - **Token violations**: hardcoded values where a token name was expected (cross-reference `tokens.json`).
   - **Accessibility implementation gaps**: contrast ratios, focus indicators visible, semantic-HTML-equivalent widgets (these are *D3 implementation* items per §4.5 — exactly the re-derive items `ui-verify-flutter` no longer checks).
   - **Persona-implementation drift**: e.g. a 48dp constraint became 40dp due to a parent widget's padding.
   - **Visual polish issues**: alignment, spacing inconsistency, typography hierarchy.
4. Writes findings to `scribbles/flutter_review/visual_comparison.md` (sibling to `comparison.md` from `ui-verify-flutter`).

**Why this is "needed anyway"**: we have no automated post-implementation visual check today. `ui-improve-flutter` is human-screenshot-driven (developer-provides). An integration-test-driven loop catches drift over time *without human intervention* and runs in CI.

**Scope discipline**: the new skill must NOT replace `ui-improve-flutter` (which handles human-driven polish iteration). It is the *automated* counterpart that runs every CI cycle. `ui-improve-flutter` continues for active polish work.

**Cost / risk**: M effort (new skill + scaffold + per-feature golden tests). Major dependency: vision-capable agent on the verification path adds non-trivial token cost — gate behind explicit invocation or a `visual_validate: true` flag. Re-test risk: low (additive; existing flow unaffected).

**Open Q**: do we want this as a CI-gate (blocks merge on regression) or as an advisory check (writes a report; human decides)? Recommendation: advisory at first; promote to gate after we've seen the false-positive rate.

### 1.3 "We need scribbles for mobile + desktop + maybe medium — three breakpoints"

**Yes — and the rule can be persona-driven.** Three building blocks:

**Block 1 — declare device-class coverage on each persona.** Each persona's `persona.md` gains a `device_classes:` field listing which device classes they predominantly use. Concretely:

```yaml
# requirements_user_needs/personas/<name>/persona.md (frontmatter)
device_classes: [mobile]          # default for most personas
# or
device_classes: [desktop]         # for therapist personas
# or
device_classes: [mobile, desktop] # explicit if persona uses both
```

**Block 2 — per requirement, compute the union.** When `ui-create-scribble` reads the requirement, it computes `union(persona.device_classes for persona in personas_served)`. The result is the *required breakpoint set* for this feature. Typically:

- Mobile-only personas → mobile scribble only (current default; no change).
- Therapist-only requirements → desktop scribble only.
- Mixed (rare for app, frequent for shared flows) → both scribbles required.

**Block 3 — robust "do I need a separate scribble at breakpoint X?" rule.** Two-part rule:

1. **Hard rule (always do it)**: when the device-class set has ≥2 distinct entries → generate per-breakpoint scribbles.
2. **Soft rule (skip when identical)**: a screen with `same_as: mobile` annotation in its `flow_positions` entry indicates "this screen's layout is identical at desktop and medium; do not regenerate." The auto-review (Phase 2) verifies that the identical-claim is actually true (e.g. modal dialog widths really are the same constrained width across breakpoints).

For the modal-dialog case the user raised: a confirmation modal has a fixed max-width (e.g. 560dp) — it renders the same on mobile, medium, and desktop. The screen file is generated once; mobile/desktop scribbles both reference it with `same_as: mobile`.

**Phase 1 prompt change**: extend the MUST-DO list with: "Read `device_classes` of each persona in `personas_served`. Generate the per-screen HTML in a folder structure: `scribbles/v{n}/mobile/`, `scribbles/v{n}/desktop/`, `scribbles/v{n}/medium/` as needed. For screens whose layout is genuinely identical across breakpoints, emit a single file in the smallest-required breakpoint and add `same_as_other_breakpoints: true` to its `flow_positions` entry."

**Cost / risk**: M. Existing scribbles default to mobile; backwards-compatible. New scribble work for therapist-touching features may take ~1.5× current scribble effort.

**Robustness check on the user's heuristic**: "therapist personas use a PC, all others use mobile" — this is approximately true today but is *implicit*. Encoding it as a `device_classes:` field on each persona makes it (a) explicit, (b) auditable, (c) revisable when a persona's usage changes.

### 1.4 "Fourteen things on one side is more than expected — is the current scribble scope correct, or should we iterate more on Flutter implementation?"

**Honest re-examination.** The original scribble framing was "structural wireframe for IA only." The current 15-item list expanded over time as the skill matured (Phase-1 MUST-DOs grew from 5 to 15 steps). Three honest positions:

**Position A (status quo, defended).** Keep all 15 locks. Rationale: the items beyond IA (L4 copy, L8 sizing, L11 dialog patterns, L14 design decisions, L15 a11y intent) carry *persona-driven constraints* that survive only if anchored at scribble time. Copy text in particular is impossible to defer — a coder cannot re-derive a privacy-safe label for PERSONA-009 from `doc/` alone; it's a persona judgment call that belongs at design time. Web research §4.5 confirms this aligns with mainstream practice.

**Position B (slim back to true IA).** Drop L4, L8, L11, L14, L15. Scribble locks only: screen list, widget choices, hierarchy, required states, navigation patterns, component-library usage, information-model boundary. Everything else is iteratively decided in Flutter. Rationale: smaller scribble = less to maintain, less to get wrong, more honest about what HTML can show. Cost: lose the early audit; copy / a11y issues surface later (after Flutter implementation already committed). The pattern that comes back is "we keep finding persona issues in Flutter" — exactly the iteration cost that motivated scribbles in the first place.

**Position C (hybrid — graded confidence).** Keep all 15 locks BUT split them into two confidence tiers:

| Tier | Items | Status when implementing |
|---|---|---|
| **Locked-high** | L1 (screens), L2 (widgets), L3 (hierarchy), L9 (required states), L10 (nav), L11 (dialog), L12 (components), L13 (info-model) | Implement as shown; deviation requires explicit task to revise scribble |
| **Locked-recommended** | L4 (copy), L5 (canon), L6 (personas), L7 (rules), L8 (sizing-as-token), L14 (decisions), L15 (a11y intent) | Implement as shown by default; coder may propose alternatives during implementation if developer confirms; deviation tracked in `comparison.md` for next-version iteration |

**Recommendation: Position C.** This honors the user's "iterate more on Flutter for some aspects" while keeping the persona-driven items at scribble-time (where they are cheapest to debate). The CONTRACT BLOCK (B2) gains the tier label per item. `ui-verify-flutter` treats Locked-recommended deviations as `locked_unclear` rather than `locked_deviation` — surfacing for review rather than auto-flagging as bug.

This is a substantive refinement to §4.1 of the synthesis. **Question for user**: confirm Position C as the proposed split? Or commit to Position A (status quo, all locks high-confidence) or Position B (slim back to IA)?

### 1.5 "CONTRACT BLOCK at the top of index.html — yes, and also for the human reviewer"

**Approved + extended.** The CONTRACT BLOCK now has two readers — coder (downstream) and reviewer (during scribble approval). Both need different framings:

```
SCRIBBLE CONTRACT — what this scribble commits to and what it does not
=======================================================================

FOR THE HUMAN REVIEWER:
  Please critique these decisions — they will be implemented as shown:
    • Screen list and order
    • Widget choices (FilledButton vs OutlinedButton, dialog types, etc.)
    • Information hierarchy and grouping
    • Copy text (labels, headings, button text, error messages)
    • Required screen states (empty / loading / error)
    • Navigation and dialog patterns
    • Persona constraints applied (see metadata.yaml.personas_applied)
    • Accessibility intent (semantic elements, ARIA roles, alt-text)

  Please DO NOT critique these — they will be handled in Flutter implementation:
    • Exact colors (resolved from doc/presentation/ + tokens.json)
    • Exact spacing values (resolved from token registry)
    • Animation timing and curves
    • Hover / focus / pressed states
    • Responsive breakpoint mechanics
    • BLoC events and behavior wiring
    • Accessibility *implementation* (focus order, screen-reader announcements, WCAG verification)
    → If you see a color/spacing/animation issue, it is NOT a scribble defect.
      Note it for the Flutter implementation step.

FOR THE FLUTTER CODER (downstream):
  Implement the LOCKED items as shown above; consult metadata.yaml + flutter_handoff.yaml
  for per-element specifics. RE-DERIVE the deferred items from doc/presentation/, tokens.json,
  and doc/presentation/accessibility_guidelines.md. The verifier (ui-verify-flutter) will
  only check the LOCKED items; the visual-validation step (ui-visual-validate or
  ui-improve-flutter) handles the RE-DERIVE side.

See: requirements_tasks/SKETCHES_README.md#what-a-scribble-commits-to
```

**Reviewer-focused framing matters because:** without it, a developer reviewing a scribble can spend cycles critiquing color choices that the scribble explicitly does not commit to. The contract block re-channels their attention to the locked items.

Cost / risk: zero — text-only generation by Phase-1.

### 1.6 "Inspiration as seed / example / strict concept — Figma screens, web patterns — with structured 'use this aspect / don't use this aspect' annotation"

**Extending Phase 0 (Multimodal Seed) into a Structured Inspiration Inputs block.** Current Phase 0 supports `inputs/sketch.{png,jpg,pdf}` and `inputs/reference.{png,jpg}` as vision context — single file per kind, no per-aspect guidance. Proposal:

**New Phase 0 contract**: the task/requirement folder may contain an `inputs/inspiration.yaml` with structured per-reference annotations, plus arbitrary image files referenced by name.

```yaml
# inputs/inspiration.yaml
references:
  - file: figma_login_layout.png
    type: figma_export
    weight: high           # high = treat as strict concept; medium = inspiration; low = mood board only
    use_for:
      layout: true
      component_choices: true
      screen_order: true
      copy_text: false       # don't reuse the labels — they aren't ours
      color_scheme: false    # ignore — we have our own tokens
      spacing_values: false  # ignore — we use the token registry
      typography: false      # ignore — Material 3 type scale
    note: "Strong reference for the two-column structure and the right-rail summary placement.
           The submit button is in a sticky footer; we should keep that pattern."

  - file: cool_dropdown_pattern.png
    type: web_screenshot
    weight: medium
    use_for:
      interaction_pattern: true   # apply the dropdown collapse-on-scroll behavior
      layout: false
      color_scheme: false
    applies_to_screens: [03_filter_overlay]   # explicit scope
    note: "Just the way the toolbar collapses on scroll. Apply only to screen 03."

  - file: hand_drawn_sketch.jpg
    type: sketch
    weight: medium
    use_for:
      layout: true
      hierarchy_idea: true
    note: "Rough sketch of the dashboard layout; treat as suggestion, not constraint."
```

**Phase 1 prompt change**: if `inputs/inspiration.yaml` exists, pass it to the Phase-1 agent alongside the requirement context. The agent reads each reference image (vision input), reads the YAML for which aspects to use, and produces a scribble that:

- For `use_for: true` aspects: actively patterns the scribble after the reference.
- For `use_for: false` aspects: explicitly ignores the reference's choices and uses project-standard conventions.
- For each screen affected by an inspiration: add an HTML comment `<!-- inspiration: <file>#<aspect>=true -->` providing traceability.

**Why structured (`true`/`false` per aspect)**: free-text notes are interpreted unevenly. The matrix forces a deliberate decision per dimension. The `note:` field carries the qualitative gloss that doesn't fit the matrix.

**Defaults**: if `inputs/inspiration.yaml` is absent but image files exist, fall back to current Phase-0 behavior (treat as undirected vision seed). The YAML is opt-in.

**Cost / risk**: M effort (Phase-1 prompt + schema documentation in SKETCHES_README + a small validator script for the YAML). Re-test risk: low (additive).

### 1.7 "Domain Vocabulary is at agent level, not skill level — sad. Would a scribble *agent* (or specialized agent called by the skill) make sense? Or vocabulary in skills?"

**Sharp observation. Recommended path: create specialized agents for the high-LLM-activation phases of `ui-create-scribble`.** Three options re-stated, then the recommendation:

**Option (a) — Convert `ui-create-scribble` to an agent.** Reject. Skills are orchestrators (they have phases, they invoke other skills, they pause for human approval); agents are single-purpose LLM-activation units. Mixing the two collapses control flow into prompt text and loses workflow-level concerns (phase ordering, version management, user-approval gates).

**Option (b) — Add specialized agents called by the skill for specific phases. ✓ RECOMMENDED.** Today the skill spawns *unnamed* sub-agents per phase ("Spawn a new agent with the following task: ..."). These inherit the orchestrator's model and have zero Domain Vocabulary. By promoting them to named agents in `.claude/agents/`, we activate the LLM specialization mechanic.

**Option (c) — Add Domain Vocabulary to the skill file.** Mostly reject. Skill files are loaded into the orchestrator's context; vocabulary there activates the *orchestrator's* embedding clusters, not the spawned agent's. The activation needs to live where the heavy LLM work happens — in the agent prompt, not the orchestrator prompt.

**Concrete proposal — three new agents in `.claude/agents/`:**

| Agent | Purpose | Domain Vocabulary anchors | Model |
|---|---|---|---|
| `scribble-generator` | Phase 1 (generate v1, v3, …) | wireframe fidelity, structural commitment, component mapping, persona-constraint enforcement, T1/T2 rule application, information-model boundary, exception path, Domain Concepts traceability, M3 widget hierarchy, canon labels, dialog action ordering, copy persona-language audit | sonnet (with opus override when goal.md says so) |
| `scribble-auto-reviewer` | Phase 2 (auto-review odd→even versions) | YAGNI state-evidence gate, locked-in commitment, re-derive deferral, exception coverage, persona-trait verification, T1/T2 application audit, information-model consistency, anti-pattern guards (Aesthetic Critique, Invented User, Persona of One, Guideline Stuffing) | sonnet |
| `scribble-ux-protocol-reviewer` | NEW — Phase 2b extension (the Han-inspired UX-protocol lens; runs alongside auto-reviewer) | Nielsen heuristics (10), Universal Design (Mace 7), affordance & signifier, microinteraction loop (Saffer trigger/rules/feedback/loops), dark-pattern taxonomy, Fitts/Hick, motion-as-function, Question Log methodology, jobs-to-be-done | sonnet |

Each agent gets its own `## Domain Vocabulary`, `## Anti-Patterns`, and protocol structure (paralleling Han's design). The skill becomes thinner — it orchestrates, the agents activate.

**Cost / risk**: M effort (three agent files; skill rewrite to spawn the named agents; smoke test). Re-test risk: low-medium — change in dispatch behavior triggers a re-test of one representative scribble generation.

**Question for user**: confirm three named agents (generator + auto-reviewer + ux-protocol-reviewer)? Or only two (skip the ux-protocol-reviewer until we have evidence it adds value beyond the auto-reviewer)?

Caveat: this is *additional* effort beyond the contract-explicit work (Q2 / §4.3). If we do this, we are touching the skill twice (once for contract block + once for agent split). Recommendation: schedule together to minimize churn.

---

## 2. Additional improvements (design-thinking divergent expansion)

Five candidates surfaced by the synthesis context and the feedback. Each is a candidate impl-task seed; the user picks which to take forward.

### 2.1 Reviewer pre-brief (Phase 0.5)

**Idea**: before Phase 1 generates anything, spend ~30 seconds producing a *pre-brief* — a one-page document listing "what we are about to generate" and "what we are about to NOT cover." Present to user before running the expensive Phase-1 generation. User confirms / corrects.

**Why valuable**: today, the most common waste is generating v1 → user sees fundamental scope mismatch → regenerate from scratch (cost: 2× generation). A 30-second pre-brief catches scope mismatch before any HTML is written. Aligns with design-thinking "frame the problem" stage.

**Cost**: S. Risk: low (additive). Could be invoked behind a `pre_brief: true` flag in goal.md.

### 2.2 Persona embodiment in auto-review

**Idea**: Phase 2 auto-review currently checks rules abstractly ("does the screen apply T1 touch targets?"). Instead, *embody each persona* and walk through the screens: "I am PERSONA-002 Max with cognitive paralysis. Looking at screen 01, what blocks me? What works? What's confusing?" Three rounds, one per primary persona.

**Why valuable**: rule-based checks catch what rules already encode. Embodied review catches gaps the rules haven't yet articulated. Aligns with the user's vision: "the AI produces UI that matches my vision — respecting the design system, applying correct information architecture, *and grounding decisions in persona constraints*."

**Cost**: M. Risk: medium — could surface false-positives (embodied agent over-empathizes). Counter: cap at 3 personas; require evidence-cite (screen + element + persona constraint).

### 2.3 Cross-feature consistency check

**Idea**: when a new scribble is generated for feature X that shares a flow (FLOW-NNN) with existing features Y/Z, run a Haiku agent that compares component choices across all sibling scribbles. Flag inconsistencies like "Feature X uses [FilledButton] for primary confirmation; Feature Y on the same flow uses [TextButton] — intentional?"

**Why valuable**: visual / interaction consistency is hard to maintain across requirements that share a flow. Currently no check exists. Cheap to add (Haiku, single comparison run, narrow scope).

**Cost**: S. Risk: low.

### 2.4 Flow navigation as a locked structural commitment

**Idea**: currently `navigation_pattern` (L10) is per-screen ("primary destination → NavigationBar; detail → AppBar+Back; modal → no nav"). But the *flow's* navigation graph (where the user can go from each screen, escape paths, back-stack policy) is also a structural commitment. Add a `flow_navigation:` block to `metadata.yaml` and `flutter_handoff.yaml`:

```yaml
flow_navigation:
  - from: 01_dialog_structure
    to: 02_client_selected_local
    trigger: "select client"
    back_policy: "keeps 01 in stack"
  - from: 02_client_selected_local
    to: 04_pairing_overlay
    trigger: "pair required"
    back_policy: "modal — back returns to 02"
  escape_paths:
    - from: any
      to: home
      trigger: "system back"
```

**Why valuable**: implementation-engineer needs the back-stack policy to wire `GoRouter` correctly. Today this is inferred from the flow document; surfacing it in the handoff makes it explicit and verifiable.

**Cost**: M. Risk: low.

### 2.5 Iteration fatigue detection

**Idea**: if a scribble has been iterated v1 → v4+ and the user is still finding gaps, the auto-review detects this pattern and surfaces a meta-finding: "You've iterated 4 times; the requirement may be ambiguous; recommend pausing scribble work and running `requ-explore` on REQ-XXX to clarify the underlying requirement."

**Why valuable**: prevents perpetual iteration on a scribble when the requirement itself is the actual ambiguity source. A meta-protective rail.

**Cost**: S. Risk: low. Threshold tuning needed (4? 5? 6 iterations?) — start at 4.

---

## 3. Coupling analysis (what can be done independently)

| Improvement | Touches | Independent? | Best schedule with |
|---|---|---|---|
| §1.1 Verifier scope restriction | `ui-verify-flutter` Phase 3/4 only | ✓ Independent | Q2 contract work (B5) |
| §1.2 Visual-validation skill | NEW skill + `integration_test/` + new agent | ✓ Independent — new skill | Standalone |
| §1.3 Multi-breakpoint scribbles | `persona.md` schema, `ui-create-scribble` Phase 1, scribble folder structure | ✓ Independent — but touches persona schema | Standalone or with §1.6 (both Phase-1 changes) |
| §1.4 Position-C tiered locks | `ui-create-scribble` Phase 1 (CONTRACT BLOCK), `ui-verify-flutter` classification | Coupled with Q2 (contract-explicit) | Bundle with Q2 work |
| §1.5 Reviewer-focused CONTRACT BLOCK | `ui-create-scribble` Phase 1 (CONTRACT BLOCK template) | Coupled with Q2 | Bundle with Q2 work |
| §1.6 Structured inspiration inputs | `ui-create-scribble` Phase 0 + schema doc | ✓ Independent | Standalone or with §1.3 |
| §1.7 Three named agents | 3 new agent files + `ui-create-scribble` skill spawn calls | Couples with Q1 (inspirational UX protocol ports) | Bundle with Q1 work; could also bundle with Q2 to touch skill once |
| §2.1 Reviewer pre-brief | `ui-create-scribble` Phase 0/0.5 | ✓ Independent | Standalone |
| §2.2 Persona embodiment | Phase 2 auto-reviewer agent prompt | Couples with §1.7 (auto-reviewer agent) | Bundle with §1.7 |
| §2.3 Cross-feature consistency | New Haiku check in Phase 2 or Phase 5 | ✓ Independent | Standalone |
| §2.4 Flow navigation lock | `metadata.yaml` schema + `flutter_handoff.yaml` + Phase-1 generation | Couples with Q2 (handoff yaml block edit) | Bundle with Q2 |
| §2.5 Iteration fatigue detection | Phase 2 auto-reviewer | Couples with §1.7 (auto-reviewer agent) | Bundle with §1.7 |

**Bundling logic** to minimize skill-touch churn:

- **Bundle Q2-CONTRACT**: §4.3 B1–B5 (synthesis) + §1.1 verifier-scope restriction + §1.4 tiered locks + §1.5 reviewer-focused CONTRACT BLOCK + §2.4 flow-navigation lock. One impl task; touches `ui-create-scribble` Phase 1 + 5, `ui-verify-flutter` Phase 3/4, SKETCHES_README, `flutter_handoff.yaml` template, `code-simple`/`code-complex` Sketch Gate.
- **Bundle Q1-AGENTS-AND-PROTOCOLS**: §1.7 three named agents + Q1 inspirational protocol ports (Question Log + Nielsen + Affordance + Dark Pattern + Anti-Pattern guards) + §2.2 persona embodiment + §2.5 iteration fatigue. One impl task; touches `.claude/agents/` (three new files) + `ui-create-scribble` Phase 1/2/2b skill prompts.
- **Bundle FEATURES**: §1.2 visual-validation skill + §1.3 multi-breakpoint + §1.6 inspiration inputs. Three independent features; recommend scheduling as separate impl tasks but in any order.
- **Bundle TOOLING**: §2.1 reviewer pre-brief + §2.3 cross-feature consistency. Two small independent features.

This collapses 13 candidates into ~4 impl tasks of bounded scope.

---

## 4. Decision matrix (updated for round 2)

Combining round-1 §7 decisions with round-2 additions:

| # | Decision | Recommendation | Independent? |
|---|---|---|---|
| D1 | Q2 contract-explicit posture (B1–B5) | **Adopt** | Bundle Q2-CONTRACT |
| D2 | L1–L15 / D1–D8 split + tier (Position C) | **Adopt** Position C | Bundle Q2-CONTRACT |
| D3 | Q1 inspirational UX-protocol ports (A–F) | **Adopt** A+B+C; D+E+F as second pass | Bundle Q1-AGENTS |
| D4 | "No agent import" for Han UX agent | **Confirm** | (decided) |
| D5 | Execution order Q2 → Q1 | **Confirm** | (decided) |
| D6 | L8 sizing as named token reference | **Adopt** | Bundle Q2-CONTRACT |
| D7 | L15 a11y intent locked | **Adopt** | Bundle Q2-CONTRACT |
| D8 | `design_decisions:` in `flutter_handoff.yaml` | **Adopt** | Bundle Q2-CONTRACT |
| D9 | Domain Vocabulary port (six existing agents) | **Adopt** as standalone | Standalone |
| D10 | Accept honest research gaps; no further research | **Confirm** | (decided) |
| **D11** | **§1.1 Verifier scope restriction (locked-only)** | **Adopt** | Bundle Q2-CONTRACT |
| **D12** | **§1.2 Visual-validation skill (integration-test screenshots + vision agent)** | **Adopt** as new skill; advisory at first, not a CI gate | Standalone (new skill) |
| **D13** | **§1.3 Multi-breakpoint scribbles (persona-driven device_classes)** | **Adopt** | Standalone or with §1.6 |
| **D14** | **§1.5 Reviewer-focused CONTRACT BLOCK** | **Adopt** | Bundle Q2-CONTRACT |
| **D15** | **§1.6 Structured inspiration inputs (`inputs/inspiration.yaml`)** | **Adopt** | Standalone |
| **D16** | **§1.7 Three named scribble agents (generator + auto-reviewer + ux-protocol-reviewer)** | **Adopt all three**, or scope back to two (generator + auto-reviewer; defer ux-protocol-reviewer pending pilot evidence) | Bundle Q1-AGENTS |
| **D17** | **§2.1 Reviewer pre-brief (Phase 0.5)** | **Defer** to a separate small task — independent value, not blocking | Standalone |
| **D18** | **§2.2 Persona embodiment in auto-review** | **Adopt** with cap of 3 personas | Bundle Q1-AGENTS |
| **D19** | **§2.3 Cross-feature consistency check** | **Defer** — value real but low until we have ≥3 features sharing a flow | Standalone |
| **D20** | **§2.4 Flow-navigation lock in handoff yaml** | **Adopt** | Bundle Q2-CONTRACT |
| **D21** | **§2.5 Iteration fatigue detection** | **Adopt** with threshold = 4 versions | Bundle Q1-AGENTS |

**Bundled impl tasks** (proposed):

1. **Bundle Q2-CONTRACT** — covers D1, D2, D6, D7, D8, D11, D14, D20. Effort: M. Touches: `ui-create-scribble` (Phase 1 CONTRACT BLOCK template, Phase 5 handoff yaml), `ui-verify-flutter` (Phase 3/4 reshape), `SKETCHES_README.md` (new contract section), `flutter_handoff.yaml` template (`contract:` + `flow_navigation:` + `design_decisions:` blocks), `code-simple` + `code-complex` Sketch Gate. Risk: low-medium (skill-text edits + verifier behavior change).
2. **Bundle Q1-AGENTS** — covers D3, D16, D18, D21. Effort: M-L. Touches: three new files in `.claude/agents/`, `ui-create-scribble` skill rewrite to invoke named agents, prompt additions for UX-protocol ports + persona embodiment + iteration-fatigue detection. Risk: medium (dispatch change → re-test).
3. **Bundle FEATURES** — D12 (visual-validation skill), D13 (multi-breakpoint), D15 (inspiration inputs). Three independent impl tasks. Effort: M each.
4. **Bundle DOMAIN-VOCAB** — D9. Effort: S. Touches: six agent files (Domain Vocabulary + Anti-Patterns).
5. **Deferred** — D17 (pre-brief, standalone S task), D19 (consistency, standalone S task) — schedule when bandwidth allows.

---

## 5. Honest gaps in this iteration

- **Visual-validation skill (§1.2)** is the biggest unknown. Vision-agent latency, false-positive rate, token cost — all unmeasured. The proposed "advisory first, gate later" pattern is the right de-risking, but the actual rate-of-return is genuinely uncertain. Pilot in a single feature before scaling.
- **Position C tiered locks (§1.4)** has no empirical basis — the split between "locked-high" and "locked-recommended" reflects judgment, not measurement. The split will likely need adjustment after 2-3 implementation cycles.
- **Three named agents (§1.7)** carries a coordination tax — when Phase 1 and Phase 2 each have specialized vocab, the contract between them (what does Phase 2 expect to find in a Phase 1 output?) becomes a new artifact to maintain. Worth doing for the LLM-activation gains but not free.
- **Multi-breakpoint scribbles (§1.3)** complexity-explosion risk: if a feature has 9 screens × 3 breakpoints × 2 versions per iteration, that's 54 HTML files per scribble version. Mitigation: aggressive `same_as` reuse + the per-screen versioning already in `metadata.yaml`.
- **Persona embodiment (§2.2)** risk: the auto-reviewer agent may *invent* persona behaviors not grounded in `persona.md`. Mitigation: require the auto-reviewer to cite specific persona constraints from `persona.md` for every embodied finding (anti-pattern guard: "Invented Persona").

---

## 6. Question for user before completing

Bundle plan in §4 is the proposal. Three specific calls:

**Call 1**: Confirm Position C (tiered locks) for §1.4? Or stay at Position A (status quo) / move to Position B (slim to IA only)?

**Call 2**: §1.7 three named agents OR scope back to two (skip ux-protocol-reviewer until adversarial-validator pilot reports back)? Recommendation: do all three together since we're touching the skill anyway.

**Call 3**: D17 (pre-brief) + D19 (cross-feature consistency) — defer as recommended, or include in the first wave? Recommendation: defer; they don't block anything and the first wave is already substantial.

After your calls on these three, the synthesis is complete and we can finalize the task.
