# Design-Thinking Iteration 3 — final pass

**Task:** TASK-PROC-032-10 · **Date:** 2026-05-28 · **Model:** Opus 4.7
**Input:** `2026-05-28_05_feedback.md` (round-3 user feedback)
**Output to:** this file. §10 finalizes the impl-task seed plan.

> Methodology: address each round-3 feedback point with concrete proposals; then a deep dive on the scribble-location / multi-requirement-contribution problem the user raised; then a third truly-divergent ideation round (per the user's explicit request); then the final decision matrix and the impl-task seed plan.

---

## 1. Round-3 input summary

User stance: **approve everything unless explicitly stated otherwise.**

Explicit calls / reversals:
- **C1 reversed**: Position **A** (all 15 items locked-high) — not Position C. Drift-risk argument: code is disposable; requirements must be the source of truth; hybrid drift accumulates and can't be reconstructed when requirements evolve.
- **C2 confirmed**: three named agents, but **blocked by a new skill** — we need `claude-create-agent` first (parallel to `claude-create-skill`); naming scheme + `allowed_tools` heuristic + when-to-create-agent rule must be codified.
- **C3 reversed**: pre-brief and cross-feature consistency are **adopted now**, not deferred. Pre-brief needs explicit content spec + iteration model.
- **Persona embodiment**: keep, but **variable count** (LLM decides per scribble, not capped at 3); LLM should read persona + scenarios + flow (not just persona); also makes sense as a **dedicated agent**; **Sonnet first** (escalate to Opus only if quality insufficient).
- **Visual validation MUST use Opus** — Sonnet insufficient for the vision step.
- **Flow navigation lock**: user recalled the existing flow scribble index — natural home for flow navigation.
- New strategic topic: **scribble location across split requirements** (§5).
- Request: another ideation round (§6).
- Request: seed all impl tasks now, even if execution is deferred (§10).

---

## 2. Position A confirmed — implications

The user's argument distilled:

> "Code is disposable; the real source of truth must always be the requirements. The goal: even if the code is completely deleted, the agent could rewrite everything from scratch based on the requirements and the result would have the same behavior. But the more we *do not* define in the scribble, the more likely it is that we have a drift at one point — implementation results actually vary from code change to code change because not everything is defined in the requirements."

This is a robustness-over-flexibility decision. It means:

1. **All 15 L-items are locked-high.** The graded "Locked-recommended" tier from iteration-2 §1.4 is dropped. The CONTRACT BLOCK has one tier on the locked side.
2. **`ui-verify-flutter`'s `locked_deviation` is always a coder bug.** No `locked_unclear` middle category. If the coder needs to deviate, the *scribble* is iterated (not the implementation silently). This adds friction by design.
3. **The acceptable mechanism for legitimate deviation** is: the coder pauses, raises the issue via the back-pressure protocol (REQ-PROC-046 cycle), and either (a) the scribble is re-iterated or (b) the deviation is documented in `design_decisions:` AND the scribble v(n+1) is regenerated to reflect it. Either way, the scribble and the implementation never silently diverge.
4. **Coder-side iteration cost goes up.** A copy tweak ("this label is too long for the FAB") now requires a scribble revision rather than a discretionary in-Flutter rewrite. Trade accepted.

Honest counter-cost: the developer reviewing scribbles must invest the effort to get copy / sizing / dialog patterns *right at scribble time*, because correction-in-Flutter is no longer a low-friction path. Iteration 3 §6.1 (approval traceability) and the Phase-0.5 pre-brief (§4.1) are accommodations for this added scribble-time investment.

**No change required to the §4.3 (Q2 contract-explicit) architecture** — only the absence of the dual-tier markup. Net cleaner.

---

## 3. New skill — `claude-create-agent`

### 3.1 The user's framing

> "Before we create new agents, we actually have to think about how to name them. ... maybe we can just use the same naming scheme we use for skills. I don't know. ... Also the new skill needs to set the allowed tools, for example. So we need a heuristic or some way to determine which rules must be allowed for this agent. ... it would be nice to have ... rules or heuristics when we want to create agents and when not. ... Maybe you can spawn an agent that actually has the goal to create the first draft of such an agent skill. And maybe that ... is also first doing a web search to check if there are some recommendations about how to write agents, when to use agents, stuff like that."

### 3.2 Proposed two-phase impl task (NEW-SKILL)

**Phase A — research agent** (background `general-purpose` agent, ~1 hour):
- Web search: Anthropic Claude Code agent docs; "leaked-system-prompts" repo for agent definitions; Han's full agent collection (already cloned to `/tmp/han`); LangChain/LlamaIndex agent design patterns; published papers on multi-agent prompt engineering 2024-2026; arXiv on prompt specialization (`2510.07772`, `2301.12726`, the ones Han cites).
- Distil into a research doc (placed in the NEW-SKILL task's `plans_and_protocols/`):
  - Naming patterns (verb-domain vs role-noun; collision avoidance with built-ins, han-imports, project skills)
  - `allowed_tools` heuristics by agent intent (read-only / analysis / transformation / full-spectrum)
  - When-to-create-agent decision tree (signals that justify a new agent vs. extending an existing skill)
  - Required structural sections (frontmatter, ≤50-token role identity, Domain Vocabulary, Anti-Patterns, Protocols, Output Format, Rules)
  - Anti-patterns in agent design (e.g., Self-Evaluation Bias per Han doc 2; Vocabulary Stuffing; Tool Over-Allocation; Role Identity Bloat)

**Phase B — author the skill** (using `claude-create-skill`):
- The skill takes a draft intent ("I want an agent for X") and produces a fully-formed agent file plus a CHECKLIST the user reviews before the file is written.
- Sections of the produced agent file: per the research doc's required-sections list.
- Naming check: refuse if name collides with built-in Claude Code agent names (Architect, Plan, Explore, etc.), with `.claude/agents/` existing names, or with han-imported names.
- `allowed_tools` check: refuse `*` unless the user provides an explicit justification; default suggestions per intent class.
- When-to-create-agent gate: skill asks the user 3-5 disqualifying questions ("does an existing agent already cover this with vocabulary added?", "is this a one-off task that doesn't need recurring activation?", "could a skill with a tighter prompt do the same job?"); if the user can't answer satisfactorily, the skill refuses and recommends extending an existing agent or skill instead.

### 3.3 Why this is a blocker

D16 (three scribble agents) and D18 (persona-embodiment-reviewer) both **create new agents**. Doing them before `claude-create-agent` exists means re-deriving the naming + allowed_tools + structure decisions ad-hoc, and risks creating agents that later need to be re-shaped when the skill lands. Sequencing: **NEW-SKILL first → Q1-AGENTS after.**

(The existing `han-adversarial-validator.md` was a direct port-of-text, so it didn't go through `claude-create-skill`-equivalent; it carries Han's already-shaped structure. New agents must go through the new skill.)

### 3.4 Sizing this task

NEW-SKILL is **M effort**. Phase A is a single background agent run (~1 hour); Phase B is a `claude-create-skill` invocation with a richer-than-usual draft (the skill itself is non-trivial because it embeds heuristics and a refusal gate). Re-test risk: low (new skill; no existing dispatch behavior changed).

---

## 4. Refinements per round-3 feedback

### 4.1 Pre-brief content spec + iteration model

**Content (forbidden + required):**

REQUIRED in a pre-brief (≤300 words total):
- Date + requirement ID + parent flow ID (if any)
- **Screens to be generated**: ordered list, one-line purpose each
- **Personas applied**: each with their primary constraint stated in one line
- **Applied rules**: T1/T2 rule IDs grouped by which screens they apply to
- **Inspiration** (if `inputs/inspiration.yaml` present): file → use_for aspects → applies_to_screens
- **Out of scope**: explicit list of flow steps / screens / inspiration aspects that will NOT be generated this round
- **Open assumptions**: at most 3 — only if Phase-0 detected ambiguity
- **Information-model boundary**: derived from Domain Concepts (the L13 list)

FORBIDDEN in a pre-brief:
- Visual / styling description (it doesn't exist yet)
- Specific component choices (that's Phase 1's job)
- Layout descriptions
- Lengthy persona prose (one line per persona, not a paragraph)
- Any "anticipated finding" — pre-brief is the *frame*, not the work

**Iteration model:**

1. Phase 0.5 generates pre-brief → pauses
2. User reviews; three valid responses:
   - **Approve** → Phase 1 proceeds with pre-brief as pinned read-only context
   - **Adjust** → user edits the pre-brief directly OR replies inline; the pre-brief is regenerated reflecting changes; iteration counter increments
   - **Reject scope** → user signals the requirement itself is ambiguous; the skill halts and recommends `requ-explore` on the parent requirement
3. **Cap: 3 pre-brief iterations.** On iteration 4, the skill writes to `automation/pending_feedback/<TASK-ID>/question.md` per REQ-PROC-046 back-pressure protocol and halts. This matches the existing 5-cycle quality gate model but tighter (pre-brief is upstream of the expensive Phase-1 generation; we want to bail faster).
4. Approved pre-brief is committed as `pre_brief.md` in `scribbles/v{n}/` (it's a permanent design-record artifact, sibling to `metadata.yaml`).

**Why limit verbosity to ≤300 words**: the user explicitly warned "we don't want to overload the user with too much information early on." 300 words is roughly 1 minute to read; that's the cost ceiling for a pre-Phase-1 review.

### 4.2 Persona embodiment refinements

User points: variable count, read scenarios + flow (not just persona), dedicated agent, Sonnet first.

**Variable count**: the embodiment agent decides how many personas to embody, in two steps:
1. Read `metadata.yaml.personas_applied` (full list)
2. For each persona, decide: "is this persona *materially affected* by the design choices in this scribble?" Materially affected = the design choices either help or hinder the persona's primary task in a way that other personas wouldn't experience. If yes → embody. If no → skip with one-line justification.

Anti-pattern guard: **Embodied-Without-Material-Cause** — the agent must cite a specific persona-trait constraint AND a specific screen element to justify embodying. Pure "this persona is in the list, so I'll walk it" is rejected.

**Reading scope:** for each materially-affected persona, the agent reads:
- The persona's `persona.md` (always)
- The persona's primary scenario(s) at `requirements_user_needs/personas/<name>/scenarios/<scenario>/scenario.md` — these often describe a *pre-product* world (what the user was doing before the app existed) and are valuable empathy input
- The parent flow's `flow.md` Domain Concepts section (already in context from Phase 1; re-read for embodiment lens)

The agent does NOT read every scenario in the persona folder (token cost; not all scenarios are relevant). The scenario(s) to read are determined by name-matching to the requirement / flow or by the persona's "primary scenarios" field if it exists.

**Dedicated agent: YES.** Scope is tight, vocabulary is rich, output format is structured. Name proposal: **`persona-embodiment-reviewer`** (project-wide reusability — `ux-write-scenario` and `ux-validate-rule` could also invoke it). Lives at `.claude/agents/persona-embodiment-reviewer.md`. Created via `claude-create-agent` (blocks D22).

**Sonnet first**, as the user requested. The dedicated-agent prompt's specialization (rich Domain Vocabulary, tight Anti-Pattern guards) is the lever for getting Sonnet quality; if results are insufficient after pilot use, the agent's `model:` frontmatter can be upgraded to opus in a single-line edit.

### 4.3 Visual validation MUST use Opus

User: "Visual-validation Must use Opus. Sonnet is not strong enough to actually do good visual validation."

Accepted. Practical implication for D12 (the new `ui-visual-validate` skill):
- The vision-comparison agent uses `model: opus` explicitly
- Per-feature cost is non-trivial; gate behind explicit invocation OR run on a release-cadence schedule (not per-PR)
- Output is advisory (writes to `scribbles/flutter_review/visual_comparison.md`); the developer decides whether to act
- May be promoted to a CI gate once false-positive rate is measured

### 4.4 Flow navigation lock — placement

User: "We still have somewhere this flow scribble index, right? ... Maybe that's also where we could place this flow navigation. But of course it must be then findable or the LLM that later implements it has to know where to look for it."

Confirmed: REQ-PROC-032 AC-18 / SEC-13 specifies `scripts/generate_flow_scribble_index.py` writes `requirements_user_needs/user_flows/<flow>/scribble_index.html` aggregating approved scribble screens for a flow.

Two artifacts per flow:
- `scribble_index.html` (human-readable, exists) — gains a "Flow Navigation" section header rendering the navigation graph as a simple diagram + table
- **NEW** `flow_navigation.yaml` (machine-readable, sibling file) — authoritative; consumed by `ui-create-scribble` Phase 1, `ui-verify-flutter` Phase 3, and the implementation-engineer (via the Sketch Gate)

`flutter_handoff.yaml` includes a top-level field `flow_navigation_source: requirements_user_needs/user_flows/<flow>/flow_navigation.yaml` pointing to the YAML; consumers know where to look.

Schema sketch:
```yaml
# requirements_user_needs/user_flows/<flow>/flow_navigation.yaml
flow_id: FLOW-NNN
edges:
  - from: 01_dialog_structure
    to: 02_client_selected_local
    trigger: "select client"
    back_policy: "keeps 01 in stack"
    contributing_requirement: REQ-FUNC-007-01
  - from: 02_client_selected_local
    to: 04_pairing_overlay
    trigger: "pair required"
    back_policy: "modal — back returns to 02"
    contributing_requirement: REQ-FUNC-007-01
escape_paths:
  - from: any
    to: home
    trigger: "system back"
```

This is a Q2-CONTRACT deliverable.

---

## 5. Deep dive — scribble location and multi-requirement contribution

### 5.1 The user's problem (rephrased precisely)

A screen often embodies multiple requirements:
- Transfer feature (REQ-FUNC-007-XX) drives the main user task
- Security feature (REQ-NFUNC-XXX) contributes encryption UI elements (e.g. a "your file is encrypted" badge, a key-rotation prompt)
- Data-integrity requirement might contribute a warning surface

If scribbles live per-feature, two questions arise:
- **P1 Location**: which feature's folder owns the scribble?
- **P2 Input completeness**: does the Phase-1 agent see all contributing requirements, or only the "owning" one?

### 5.2 Three perspectives on the same product

| Perspective | Slices by | Granularity |
|---|---|---|
| Requirements | *Concern* (transfer logic, encryption, networking, persistence, ...) | Functional area |
| Flows | *User journey* (first-pairing, daily entry, transfer handoff, ...) | Sequence of user intents |
| Screens | *Intersection* — each screen embodies multiple concerns and participates in one or more flows | UI unit |

Each perspective is a valid first-class lens. Today the scribble framework collapses one of them — screens — into a property of a requirement (the "owning" feature). That's the source of P1's ambiguity.

### 5.3 Three location options reviewed

**Option A — Per feature (current state).** Scribbles live under the feature's folder. The "primary owner" of a shared screen is implicit — the feature whose impl task triggered the scribble.
- Pro: minimal restructure; matches impl-task ownership; co-locates scribble with the feature's requirements.md
- Con: primary-owner rule is implicit; cross-feature contributions are invisible to the Phase-1 agent unless explicitly listed; doesn't solve P2 alone

**Option B — Per user flow.** Each flow owns scribbles for screens participating in that flow.
- Pro: flows have well-defined screen sets; per-flow scribble index already exists as precedent
- Con (user's own caveat, important): "the user flow does not define how a screen must look. It just defines a part — only the relevant part — of the screen." A screen participating in two flows means duplication or referencing. Flows are journey-perspective; screens need concern-perspective inputs.
- Verdict: fundamentally misaligned with what scribbles actually need to capture

**Option C — Per-screen catalogue (new top-level entity).** Screens become first-class entities at `requirements_user_needs/screens/<screen_id>/` with metadata declaring contributing_requirements + participating_flows + scribble subfolder.
- Pro: cleanest conceptual match — "screens are the intersection"; supports multi-flow / multi-requirement naturally; future-proof
- Con: major restructure; user just reorganized requirements folder; significant migration cost; impl-task-to-scribble linkage becomes indirect

### 5.4 Recommended evolution — Phase A now, Phase B if pain demands

**Phase A (now, lightest-touch):** keep Option A (per-feature scribbles). Solve P2 explicitly with a `contributing_requirements:` declaration. Document P1's primary-owner rule explicitly.

**`contributing_requirements:` in `metadata.yaml`** — the load-bearing addition:
```yaml
contributing_requirements:
  - id: REQ-FUNC-007-01
    role: primary           # drives the user task; defines location of this scribble folder
  - id: REQ-NFUNC-018-02
    role: cross_cutting     # contributes UI elements (e.g. encryption badge)
    applies_to_screens: [02_client_selected_local, 05_transfer_active_local]
  - id: REQ-NFUNC-005
    role: cross_cutting
    applies_to_screens: [05_transfer_active_local]
```

The Phase-1 agent reads **all** contributing requirements, not just the primary. Cross-cutting requirements are scoped: only the listed screens consume them. Verifier and visual-validation do the same.

**Primary-owner rule** (codified in SKETCHES_README):

> The primary owner of a scribble is the feature whose user task the screen serves. When multiple user tasks of equal weight are served, the feature listed FIRST in the parent flow's `participating_requirements` field is the primary owner. When there is genuinely no primary task (rare — usually "this is shared chrome / cross-cutting infrastructure"), the scribble lives in `requirements_tasks/_shared_scribbles/<flow_or_chrome_name>/` with `role: shared_chrome` in metadata.

Discovery of cross-cutting contributors: at scribble-task creation time, the user lists them (manual, robust first version). A future enhancement could auto-discover by grepping the parent flow's `implementation_notes.md` and any requirement whose `implements_flows` references the same flow step.

**Phase B (deferred, evidence-gated):** re-evaluate moving to Option C only when ≥2 separate scribble tasks have been blocked because we couldn't decide on the primary feature owner. Without that evidence, the restructure cost isn't justified. Recorded as a deferred decision in TASK-PROC-032 backlog.

### 5.5 Flow scribble index — extended responsibilities

The existing per-flow scribble index becomes the canonical "all UI material for this flow" entry point. Each scribble's `metadata.yaml` gains:
```yaml
participating_flows:
  - flow_id: FLOW-NNN
    contributes_steps: [3, 4, 5]
  - flow_id: FLOW-MMM
    contributes_steps: [2]
```

`flow_positions` (already exists per AC-16) is kept for screen-level positioning within a flow; `participating_flows` is the scribble-level summary.

The index script reads `participating_flows` from each approved scribble's metadata, aggregates, and renders both the scribble grid (existing) and the flow_navigation diagram (§4.4). Co-located with `flow_navigation.yaml`.

### 5.6 What this means for the impl tasks

All Phase-A work bundles into **Q2-CONTRACT**:
- Add `contributing_requirements:` to `metadata.yaml` schema (small)
- Add `participating_flows:` to `metadata.yaml` schema (small)
- Update Phase-1 agent prompt to read all contributing requirements (small)
- Update `ui-verify-flutter` to read all contributing requirements (small)
- Document primary-owner rule in SKETCHES_README (small)
- Create `_shared_scribbles/` directory + README (small)
- Update flow scribble index script for new fields (small)

Net Phase-A effort: small additions on top of Q2-CONTRACT. No new bundle.

Phase B (Option C) — deferred decision, recorded only.

---

## 6. Round-3 ideation (six more candidates)

Per user request — divergent expansion, framed as design-thinking questions.

### 6.1 Approval traceability aggregator
**Q**: each version's `feedback.md` captures decisions made that cycle; when a scribble is approved, should an aggregated `APPROVAL_TRAIL.md` exist summarising the decision history (rejected alternatives, key trade-offs, the "why" behind locks) in a single file future iterators can read?
**Why**: prevents rediscovering rejected alternatives; gives the next iteration a starting point that includes the *reasoning* not just the *output*.
**Cost**: S (aggregation script triggered at approval). **Decision: defer to backlog — small standalone task.**

### 6.2 Live single-screen Flutter preview
**Q**: should scribble approval optionally trigger a one-screen Flutter scaffold (widget tree only, no BLoC, no routing) so the developer can SEE actual Flutter rendering before approving v(n+1)?
**Why**: closes the "HTML wireframe ≠ real Flutter" perceptual gap. Catches "looks fine in HTML, terrible in Flutter" cases.
**Cost**: M-L. Risk: scope creep ("but also wire the behavior").
**Decision: defer to backlog** — revisit only if Position-A friction surfaces "we keep finding visual issues only in Flutter."

### 6.3 Inter-version diff report
**Q**: between v(n) and v(n+1), should the auto-reviewer emit a semantic diff ("added screens / removed screens / restructured hierarchy / changed copy / rule-application changes") rather than rely on git-diff over HTML?
**Why**: feedback round more efficient; reviewer focuses on intentional changes vs. re-reading everything.
**Cost**: S-M. **Decision: adopt** — fits with Q1-AGENTS auto-reviewer (cheap addition).

### 6.4 A/B variant generation for controversial decisions
**Q**: when Phase 1 must make a controversial design choice (e.g., slider vs discrete buttons for mood input — already captured in `design_decisions:`), should it generate both alternatives as v1A and v1B for the affected screen, with rationale, and let the user pick?
**Why**: surfaces trade-offs visually rather than in prose.
**Cost**: M. Risk: explodes generation cost if applied indiscriminately. Trigger: only when the agent identifies a `design_decision` with multiple defensible alternatives.
**Decision: defer to backlog** — niche trigger; worth ~6 months of usage data before committing.

### 6.5 Persona-conflict marker + DDR auto-link
**Q**: when two personas have conflicting visual/interaction needs on the same screen (e.g., PERSONA-X needs data density, PERSONA-Y needs minimalism), should the scribble mark the conflict point inline with an annotation linking to a Design Decision Record (REQ-PROC-026 DDR pattern)?
**Why**: makes value trade-offs visible at scribble time; reviewer sees the conflict instead of finding the wrong-feeling design.
**Cost**: S-M (Phase-1 detection + annotation; optionally invokes `vcd-log-tradeoff`).
**Decision: adopt** — integrates naturally with persona-embodiment-reviewer (D18) since that agent already reasons per-persona.

### 6.6 Scribble-to-integration-test traceability
**Q**: should each locked-in L-item declare what integration test would verify it? (L1 screen list → screen-existence smoke; L9 required states → state-walk test; L10 navigation patterns → nav test). Phase 5 emits a `verification_seeds.yaml` consumed by the integration-test step.
**Why**: closes the loop between scribble commitments and automated verification. The visual-validation skill (D12) reads this for its checklist.
**Cost**: M (Phase-5 emission + downstream consumer). Risk: mechanically-scaffolded tests can be low-value if not thoughtfully refined — emit as *suggestions*, not as final tests.
**Decision: adopt** — feeds D12 visual-validation; bundle into VISUAL-VALIDATE.

### 6.7 Iteration-3 surprise candidate: "review brief" for v(n+1) auto-review
**Q**: should the auto-reviewer's output for v(n+1) include a structured "what the reviewer should focus on this round" section? Currently auto-review produces a regenerated scribble; the human reviewer must figure out what changed and what to critique.
**Why**: parallels the pre-brief (§4.1) but at the *review* boundary instead of the *generate* boundary. Tightens the feedback loop.
**Cost**: S. Fits into the auto-reviewer agent.
**Decision: adopt** — bundle into Q1-AGENTS.

### 6.8 Iteration-3 surprise candidate: rule-application audit log
**Q**: when Phase 1 applies a T1/T2 rule, should it emit an inline trace (`<!-- t1_touch_targets applied: 48dp on .btn-primary, .btn-secondary, .icon-button -->`)? The trace makes rule application *verifiable by inspection* — auto-reviewer and verifier can check whether every claimed-application is actually visible.
**Why**: today the `rules_applied` list in `metadata.yaml` is a claim; nothing verifies it. The audit trace makes claims falsifiable.
**Cost**: S-M (Phase-1 prompt addition + Phase-2 verification step).
**Decision: adopt** — bundle into Q2-CONTRACT (it's a contract-integrity feature).

---

## 7. Final decision matrix (round-3 consolidated)

| # | Decision | Status | Bundle |
|---|---|---|---|
| D1 | Q2 contract-explicit posture (B1–B5) | Adopt | Q2-CONTRACT |
| D2 | Lock-tier split | **Position A** (user reversal) | Q2-CONTRACT |
| D3 | Q1 inspirational UX-protocol ports (A–F) | Adopt all six | Q1-AGENTS |
| D4 | No agent import for Han UX agent | Confirmed | (decided) |
| D5 | Execution order Q2 → Q1 | Confirmed (now: NEW-SKILL → Q1; Q2 parallel) | (decided) |
| D6 | L8 sizing as named token reference | Adopt | Q2-CONTRACT |
| D7 | L15 a11y intent locked | Adopt | Q2-CONTRACT |
| D8 | `design_decisions:` in `flutter_handoff.yaml` | Adopt | Q2-CONTRACT |
| D9 | Domain Vocabulary port (six existing agents) | Adopt | DOMAIN-VOCAB |
| D10 | Accept honest research gaps | Confirmed | (decided) |
| D11 | Verifier scope restriction (locked-only) | Adopt | Q2-CONTRACT |
| D12 | Visual-validation skill (Opus) | Adopt — Opus required | VISUAL-VALIDATE |
| D13 | Multi-breakpoint (persona device_classes) | Adopt | BREAKPOINTS |
| D14 | Reviewer-focused CONTRACT BLOCK | Adopt | Q2-CONTRACT |
| D15 | Structured inspiration inputs | Adopt | INSPIRATION |
| D16 | Three named scribble agents | Adopt; **blocked-by D22** | Q1-AGENTS |
| D17 | Reviewer pre-brief (§4.1 spec) | Adopt | PREBRIEF |
| D18 | Persona embodiment — variable count, scenarios+flows, dedicated agent (`persona-embodiment-reviewer`, Sonnet) | Adopt; **blocked-by D22** | Q1-AGENTS |
| D19 | Cross-feature consistency check | Adopt | CROSS-FEATURE |
| D20 | Flow-navigation lock (`flow_navigation.yaml` + index extension) | Adopt | Q2-CONTRACT |
| D21 | Iteration fatigue detection | Adopt | Q1-AGENTS |
| D22 | **`claude-create-agent` skill (research + draft)** | Adopt — **prerequisite for Q1-AGENTS** | NEW-SKILL |
| D23 | Approval traceability aggregator | Defer to backlog | DEFERRED-LIST |
| D24 | Live Flutter preview | Defer to backlog | DEFERRED-LIST |
| D25 | Inter-version diff report | Adopt | Q1-AGENTS |
| D26 | A/B variant generation | Defer to backlog | DEFERRED-LIST |
| D27 | Persona-conflict marker + DDR auto-link | Adopt | Q1-AGENTS |
| D28 | Scribble-to-integration-test traceability (`verification_seeds.yaml`) | Adopt | VISUAL-VALIDATE |
| D29 | `contributing_requirements` + primary-owner rule + `_shared_scribbles/` (§5.4) | Adopt | Q2-CONTRACT |
| D30 | `participating_flows` field in metadata + flow scribble index extension (§5.5) | Adopt | Q2-CONTRACT |
| D31 | Auto-review "review brief" for v(n+1) (§6.7) | Adopt | Q1-AGENTS |
| D32 | Rule-application audit log (`<!-- t1_X applied: ... -->`) (§6.8) | Adopt | Q2-CONTRACT |

---

## 8. Impl-task seed plan (9 bundles, dependency-ordered)

Per the user's request, all approved bundles are seeded as `task-create`-formatted goal.md files. Execution is deferred — the seeds make the work resumable later without re-deriving the plan.

| Order | Task | Bundle ID | Effort | Blocked-by | Decisions covered |
|---|---|---|---|---|---|
| 1 | Create `claude-create-agent` skill (research + draft) | NEW-SKILL | M | — | D22 |
| 2 | Make scribble–coder contract explicit (Q2 architecture) | Q2-CONTRACT | M-L | — | D1, D2, D6, D7, D8, D11, D14, D20, D29, D30, D32 |
| 3 | Port Domain Vocabulary + Anti-Patterns to existing 6 agents | DOMAIN-VOCAB | S | — | D9 |
| 4 | Create scribble-specific agents + UX-protocol ports + new auto-review features | Q1-AGENTS | L | NEW-SKILL | D3, D16, D18, D21, D25, D27, D31 |
| 5 | Create `ui-visual-validate` skill (Opus, integration-test screenshots) | VISUAL-VALIDATE | M-L | — | D12, D28 |
| 6 | Multi-breakpoint scribbles via persona `device_classes` | BREAKPOINTS | M | — | D13 |
| 7 | Structured inspiration inputs (`inputs/inspiration.yaml`) | INSPIRATION | M | — | D15 |
| 8 | Reviewer pre-brief (Phase 0.5) with iteration model | PREBRIEF | S-M | — | D17 |
| 9 | Cross-feature consistency check (Haiku Phase-2 step) | CROSS-FEATURE | S | — | D19 |

**Parallelism**: Q2-CONTRACT and NEW-SKILL run in parallel; everything else parallel to Q2-CONTRACT. Q1-AGENTS waits for NEW-SKILL.

**Deferred (recorded, not seeded as tasks)**:
- D23 Approval traceability aggregator
- D24 Live Flutter preview
- D26 A/B variant generation
- Phase-B scribble-location restructure (Option C)

These live as bullets in the TASK-PROC-032 backlog (or REQ-PROC-032 trackable items) for future revisitation. Trigger condition for each is documented.

---

## 9. Honest gaps in iteration 3

- **`claude-create-agent` skill quality** is unmeasured until its first agent is created. Mitigation: the research-first phase shapes the skill; first real use (creating `scribble-generator`) is the validation event.
- **Position A friction cost** is unmeasured. After the first 2-3 Position-A scribble-iteration cycles, observe whether the "re-iterate scribble for every copy tweak" cost is acceptable. If not, **Position C is revisitable** as a follow-up (it's only a tier-marker addition to the existing locked-in list; not a rewrite).
- **`participating_flows` discovery** in §5.5: requires the user to populate manually at scribble-task creation time. Auto-discovery (greppy) is a follow-up if manual proves error-prone.
- **Persona embodiment with variable count** could under-cover if the LLM is conservative. Mitigation in §4.2: anti-pattern guard + auto-reviewer cross-checks the exclusion justification.
- **`flow_navigation.yaml` schema** is sketched, not authored. Q2-CONTRACT task must include a worked example for a real flow (likely FLOW-002 transfer) to validate the schema before locking it in.
- **The 9-bundle plan is substantial.** Realistic execution span is multiple weeks; not every bundle will reach implementation soon. The seeding ensures the work survives context expiration.
- **Three-iteration design-thinking cycle ends here.** Further iteration would yield diminishing returns relative to what's already on the table. If novel angles surface during impl, those are new exploration tasks, not extensions of this one.

---

## 10. Next steps

1. Create the 9 impl-task seeds via `task-create` skill (one invocation per bundle; each produces a `goal.md` with the bundle's decisions enumerated as ACs).
2. Update REQ-PROC-032 trackable items with the deferred decisions (D23/D24/D26 + Phase-B Option C) as backlog notes.
3. Verify the four exploration ACs from this task's `goal.md`:
   - [x] Exploration produced at least one synthesis round → three rounds delivered (synthesis + iteration 2 + iteration 3)
   - [x] The synthesis defines the problem space in terms not fully known at task creation → "contract-locality" framing + multi-requirement-contribution problem (§5) — neither was anticipated
   - [x] Decisions requiring user input are identified and framed clearly enough → 32 decisions in §7 with status; user resolved all blocking ones
   - [x] The output is honest about what remains uncertain → §9 + previous-iteration uncertainty sections
4. Invoke `task-complete` on TASK-PROC-032-10.
