# Round 1 Evaluation — Scribble Workflow Live Pilot (TASK-FUNC-007-01-05 v2)

Date: 2026-06-04
Task: TASK-PROC-032-28 (evaluation), observing TASK-FUNC-007-01-05 at the v2 Phase-3 gate.
Inputs: developer feedback (`2026-06-04_01_feedback_phase3-gate.md`), live inspection of
`requirements_tasks/scribbles/therapist/data_transfer/v2/` (index.html + 02_handover_send.desktop.html),
`automation/pending_feedback/TASK-FUNC-007-01-05/question.md`, and an orchestrator–developer discussion.

This record is self-contained: a future `impl` task can act on the Proposals section without
replaying the session.

---

## 1. Grounded observations (facts established this round)

F1–F6 came from inspecting the artifacts against the written feedback; F7 is a process observation; F8–F16
surfaced in the live discussion that extended past it. All are grounded in named files/line numbers.

- **F1 — Reviewer-facing detail lives in HTML comments.** The `COMPONENT MAPPING`, `PERSONAS APPLIED`,
  `RULES APPLIED`, `SCREEN CONTRACT`, `RULE AUDIT TRACE` blocks on each screen are `<!-- … -->` comments.
  They do **not** render in a browser. The developer's quoted "unreadable text above the scribbles" was
  read from source. Header of that block addresses **both** `REVIEWER:` and `CODER:` audiences.
- **F2 — Per-reviewer findings are not persisted.** The pilot task's `plans_and_protocols/` holds only the
  merged `2026-06-03_02_protocol_auto-review-v1.md` and the merged `auto_review_brief.md`. No separate
  rule-reviewer / persona-walker / heuristics-reviewer / cross-feature output files exist. (Directly relevant
  to this task's Seed 3 — "which reviewer is the weak link" cannot currently be answered from artifacts.)
- **F3 — Container is named but entry context is absent.** `index.html` and the screen barlabel
  ("[Dialog · Vor Ort tab]") state the container, but no screen shows the UI the dialog is opened *from*.
- **F4 — State variants render as detached `.panel` blocks** stacked below the main frame, visually
  disconnected from the element they modify.
- **F5 — `question.md` partially duplicates** `auto_review_brief.md` and the per-element comments (the "14
  fixes" recap), while also carrying genuine gate-level decision asks (RQ1, D1, D2, D3, A/B).
- **F6 — Flow-step mapping already exists** in the generator output (`index.html`: "FLOW-002 steps
  [1,2,3,4,5,8]"), so a reviewer guide that points to specific flow steps is feasible without new data.
- **F7 — `claude-route` was skipped** when the developer said "do TASK-PROC-032-28". The task was already
  `in_progress`, so no harm — but the skill's state-transition side-effect was bypassed silently.
- **F8 — Entry context is known to the generator but not propagated, and not reviewed.** The generator
  *receives* full `flow_context` (agent line 45), uses it for "preconditions" (lines 51, 93), and deliberately
  classifies the container (primary / detail / modal-overlay, line 153 + nav table 203–213). But that
  awareness is transient: `flow_positions` persists only `step_number` (not predecessor screen / entry
  surface), the entry context is dropped after reasoning, and the only artifact trace is the hand-typed
  barlabel `[Dialog · Vor Ort tab]`. No reviewer rubric (rule / persona / heuristics) checks container
  appropriateness against the entry surface + content size, and auto-review's documented inputs (SKILL.md
  line 10) are scribble path + requirement path — `flow_context` is **not** an input to the review phase.
  **Consequence**: the container choice is asserted by the generator and never independently checked — a
  wrong container (e.g. a bottom sheet taller than ⅓ screen height) would pass review silently. This makes
  C1 a **correctness** gap, not only a human-readability one.
- **F9 — The scribble workflow reads no router / app-shell / existing entry-screen.** The only `lib/` touches
  are a domain-class presence check (`ui-scribble-generator` L174) and a feature-directory existence check
  (`ui-scribble-iterate` L26). Nothing inspects the GoRouter config, the app shell, or any existing
  entry-point screen. So four concrete entry/exit facts are unknowable to the workflow: entry-surface *type*
  (1st-level nav / app-bar button / contextual), entry-point *multiplicity* (single vs N routes), back/close
  *destination*, and consistency with the *built* router. The flow (FLOW-002) carries the back-destination
  partially (Step 8: dismiss → "Delivery Complete") and multiplicity partially (Exception 1.1 alternate
  entry), but the generator extracts neither. (Basis for PROP-8.)
- **F10 — Brownfield inversion + no scribble-coverage/basis model.** The scribble process is new; only ~2
  scribble version dirs exist (this pilot), while basic screens are already implemented and awaiting
  refinement. So the real pipeline is *implemented → retro-scribble*, not *scribble → build*. There is **no
  check** that a screen's opener (its entry basis) has a scribble, and **no flow→scribble coverage report**.
  `check_scribble_parity.py` only mirrors scribble dirs ↔ `lib/features/` dirs (AC-37, storage parity) — it
  says nothing about flow-step coverage or entry-basis presence. Scribbles are created ad-hoc per
  requirement (`task-derive-from-requ`); an opener's scribble appears only when the opener's *requirement*
  is independently scheduled — nothing auto-creates the basis.
  **Not brownfield-only**: greenfield is also fragile — the generator can assume an opener that never gets
  built/scribbled, a referenced sibling can be renamed/deleted on regeneration, a back/close destination can
  point to a screen that left the set, a Tier-2 screenshot path can go stale. The entry-reference graph rots
  because every artifact in it regenerates independently → a standing validate+recover mechanism is needed,
  not a one-time basis gate (see PROP-10).
- **F11 — The "basics" are demonstrably NOT covered, and creation isn't automatic.** Proven via the most
  foundational case (main navigation):
  - Main nav exists as **REQ-NFUNC-011** under `non-functional/ui_ux_design_system/navigation_patterns/
    main_navigation/` — a cross-cutting **design-system** requirement, NOT pulled into the flow-derived
    functional requirement (REQ-FUNC-007-01). Flows don't contain nav chrome, and the flow→requirement
    derivation never owns the nav *shell*. (Premise corrected — and **refined by F12**: only the nav
    *mechanism* is NFUNC; the feature's *entry point* is functional.)
  - REQ-NFUNC-011 is `status: implemented` but has **no scribble and no scribble task** — only a Jan-2026
    explore task. It was built before the scribble process existed; nothing flags the gap.
  - **Scribble-task creation is not automatic**: `task-derive-from-requ` routes by an explicit `task_type`
    set in the decomposition plan; there is **no rule** "Presentation-scope AC ⇒ scribble task." Coverage
    depends on plan-author memory; for pre-scribble implemented requirements the trigger never fires.
  - **Nuance**: main nav may not need a per-screen scribble — it may be adequately covered by the
    `c_navigation_bar` component. The real missing keystone is an **app-shell / navigation-map** artifact
    declaring primary destinations + where each feature's entry hangs, so PROP-8 Tier-1 resolution has a
    canonical target instead of every feature scribble re-guessing its location.
- **F12 — Functional requirements own *internal* entry but not the *outer launch seam*; ownership of the
  seam is unassigned.** Refines F11's nav discussion. The distinction:
  - Nav *mechanism* + *rules* (NavigationBar component; what qualifies for a destination, ranking, overflow)
    → correctly NFUNC design-system.
  - A *feature's own entry point* → must be owned by the **functional** requirement (developer's principle).
  - **Evidence it half-works**: REQ-FUNC-007-01 §7.3 "Entry Point" owns the *internal* path (delivery
    interface ← client selection ← transfer dialog tabs) and the container (§1.1 Dialog Type, §1.2 close).
  - **Evidence of the gap**: §7.3 stops at its own dialog boundary. How the **transfer dialog itself** is
    launched from the rest of the app (client list? session screen? FAB? nav destination? how many launch
    points?) is unspecified. That outer launch seam is exactly the entry context the scribble *invents*
    ("[Dialog · Vor Ort tab]" with no requirement source) and the LLM reviewers cannot check (F8).
  - **Boundary problem**: the launch surface usually belongs to a *neighboring* functional requirement
    (client management / session). The entry point spans a requirement boundary and **no rule assigns
    ownership of the seam** — each feature documents its inside and assumes someone else documents the door.
  - **Routing consequence**: when a scribble cannot *source* its entry from a requirement, that is a
    **requirement gap → `requ-explore`** (the feedback-classifier's "requirement gap" category), NOT a
    scribble-generator patch. Missing entry must route upstream, not get invented in the HTML.
- **F13 — `requ-derive-from-flow` is the correct *early* detection point and already has ~80% of the
  machinery; only the entry-seam *trigger* is missing.** Detection of missing "basics" requirements should
  happen at requirement-derivation time (earliest), not at scribble time. The skill already has:
  - **`foundation_gap`** category (SKILL.md L258): "a technical/architectural *prerequisite* that one or more
    flow gaps depend on" — the correct home for the app-shell/launch-surface basis.
  - **Implicit-requirement detection** (L143): "UI components that imply requirements not captured in
    explicit gaps."
  - A thorough **already-covered** check (Glob + keyword-grep + coverage-lookup) before marking `new_needed`
    — won't duplicate an existing basics requirement.
  - It has legitimate **requirement-creation power** → resolves the PROP-11 R4 governance concern (this *is*
    the sanctioned authoring path; goal.md → `requ-explore`).
  - **The gap**: nothing *triggers* on the entry-seam. The skill keys off explicit flow gaps + "UI components
    that imply requirements"; the launch seam (F12) is neither — it's an **absence** (the flow omits nav
    chrome by design; the door nobody drew isn't a visible component), so it slips past both detectors.
    `foundation_gap` is the right bucket but no rule routes the seam into it.
- **F14 — Entry-seam/basis detection is a *global* property; `requ-derive-from-flow` has a hard ceiling, and
  the two-tier split already exists in the tooling.** `requ-derive-from-flow` sees only its cluster at a time
  when other clusters' requirements are unwritten pending tasks, so it *cannot* reliably answer "does any
  requirement own this launch surface?" nor dedup (N flows each independently needing "the app shell"). It
  already knows this limit: L41–43 pull related flows into a **cluster analysis**; L58 warns "*deriving now
  will miss cross-flow requirements*." But clustering reaches only *related* flows — the app shell is shared
  across *unrelated* clusters (whole-app). The global reconciliation home already exists:
  **`requ-verify-flow-coverage --all`** consumes the **Foundation Gaps table** + **Cross-Flow metadata**
  (L72), runs post-derivation, and verifies against *written* requirements (L104/137/162) — matching the
  "only available after write-requ tasks executed" condition. Therefore detection must be **two-tier**:
  - **Tier A (local/early/provisional)** — `requ-derive-from-flow` raises the entry-seam as a
    `foundation_gap` **tagged Cross-Flow**. Must NOT dedup or confirm ownership (can't see other clusters).
  - **Tier B (global/authoritative)** — `requ-verify-flow-coverage --all` **dedups** the N independent
    app-shell requests into ONE launch-map requirement and **confirms ownership against the assembled set** —
    the only point with whole-graph view. The temporal ordering is why it is post-derivation `--all`.
  This lifts PROP-11's basis-ordering to the **requirement** level: feature requirements needing the launch
  surface take a foundation dependency on the app-shell requirement so it is written first.
- **F15 — Requirement *modification* never triggers scribble regeneration; the scribble silently goes stale,
  breaking the "single normative source" contract.** SKETCHES_README §33 ("What a Scribble Commits To") makes
  the scribble the **single normative source** for LOCKED-IN items (copy L4, widgets, screen list, hierarchy).
  Yet: `requ-explore` modifying a UI requirement creates **no** scribble task; `check_scribble_parity.py`
  detects only orphaned paths (scribble dir ↔ `lib/features/` node), NOT requirement-content drift;
  `stale_since` exists in the metadata schema but nothing sets it on change. So a post-release flow that edits
  a UI requirement leaves the scribble stale and the implementation contract lying. "Always vs. large-only" is
  a false dichotomy: *whether* to regenerate = always (on any LOCKED-IN change); *how much* = scoped to the
  changed screens/ACs (scoped regeneration already exists — auto-review L32). Size governs scope, never trigger.
- **F16 — Gate cadence is hardwired lockstep; the gate has only two outcomes; auto-review findings are not
  surfaced for the human to read.** `ui-scribble-iterate` (L96–98) fixes `v1 gen → v2 auto-review → user gate
  → v3 gen → v4 auto-review → user gate …`. Three things are fused that should be decoupled: the version
  counter, the reviewer-per-version (odd=gen, even=auto-review), and the gate cadence (human asked at every
  even version). Phase-3 offers only **feedback | approve** — no "run another auto-review", no "auto + my
  feedback", no configurable first-gate placement, and the human **never sees raw v1** (auto-review always
  precedes the first gate). Consequences and resolutions:
  - **No vision in the iteration loop**: all visual validators (`ui-verify-flutter`, `ui-visual-validate`,
    `ui-improve-flutter`) run **post-implementation** (built screens ↔ approved scribble); `ui-create-scribble-
    improve` is meta-tuning of the generator (wireframe *fidelity*, not content). So scribble iteration is
    100% document/rule-based; there is no autonomous content-iteration engine. Iteration-count must be
    review-driven, not vision-driven.
  - **Iteration-count control** (developer-refined): NO complexity ceiling. `severity ≥ MEDIUM` (auto-review
    already tags HIGH/MEDIUM/LOW + YAGNI gate) is the self-terminating stop signal for auto *and* manual
    review. Keep ONE non-convergence **circuit-breaker** (generalize v6 fatigue): if MEDIUM+ gaps persist,
    it means requirement ambiguity → **escalate to `requ-explore`**, not silently cap. Drop the complexity
    metric entirely (kills the "define complex" problem).
  - **Findings visibility** (anti-duplicate-work): because auto-review always runs before the human gate, the
    human must be made aware of its findings or he re-reports them. Build a **script-rendered overlay layer**:
    findings authored once (`auto_review_brief.md` / per-reviewer files) with a machine-readable `anchor:`
    field → script binds a clickable marker per anchored element → click shows the finding. Feasible by
    extending two existing patterns (`components.js` DOM-injection; the diff-toggle overlay script). Awareness
    ≠ availability, so THREE layers: (1) visible per-screen finding **count/badge**, (2) element **markers**,
    (3) Phase-3 **gate prompt** "read findings before adding feedback." Composes with PROP-4 (overlay shows
    reviewer provenance); single-source per §33.

---

## 2. Developer-feedback assessment (agree / differ)

Legend: ✅ agree · 🔶 agree-with-reframe · ❌ differ.

| # | Feedback | Verdict | Note |
|---|----------|---------|------|
| C1 | No entry context — can't judge container fit | ✅ | F3. Orientation-first is the biggest single readability win; deepened to a correctness gap by F8/F9. |
| C2 | v1 diff toggle good; needs per-element overlays explaining *what/why* changed | 🔶 | Valuable half = anchored change-rationale overlays (→ PROP-13C). Discard half = "checkbox must be a toggle switch" (meta-tooling chrome, low value). |
| C3 | `COMPONENT MAPPING` block unreadable; needs headings, line breaks, user-vs-system distinction | 🔶 | Root cause is F1 (it's a comment, dual-audience). Fix = **audience separation**, not formatting. Developer mistaking a static element→widget *mapping* for an interaction *sequence* is itself evidence of the labeling failure. |
| C4 | Multiple states per page — unclear where they attach / whether they replace main; maybe copy full scribble per variant | 🔶 | Agree it's confusing (F4). Differ on remedy: full-copy-per-variant causes **drift + token cost**. Prefer script-generated small-multiples showing only the changed region. Developer already flagged the cost and asked for a scripted option. |
| C5 | Reviewer guide on index: open flow A/B (steps shown), requirement on demand, UX-review checklist (personas/VSD/flows/components/ISO+Nielsen, links, English) as progressive-disclosure **reusable component**; out-of-scope as flat bullets; explain how T1–T3 rules form (prefer generic rules; warn of conflicts → follow-up questions) | ✅ | Most actionable item. "Reusable, not regenerated each run" = token saving + consistency. Feasible per F6. |
| C6 | Per-page descriptions hard to read; lead with flow-position ("where are we?") + relation to siblings | ✅ | Consistent orientation-first theme. |
| C7 | Information-model boundary is review-critical but appears last | ✅ | Move up. |
| C8 | Meta-thesis: good for LLM, bad for humans — humans need order, formatting, context | 🔶 | Sharpen to: **two audiences with opposite needs**; current artifact conflates them. Solution = human-facing rendered review layer + terse machine comment layer, not "make it prettier." |
| P1 | Pro session limit too low to reach gate 3; cache lost on resume; "nothing we can do" | 🔶 | Cache-TTL loss is unavoidable. Total **cost** is not fixed: auto-review fan-out (4 reviewers + per-flow walk, each re-reading flows/requirements) is the driver; phases can be made independently resumable; gate can choose which reviewers run. |
| P2 | No reviewer-agent files visible; would be useful for review | ✅ | F2 confirms. Also serves this task's own Seed 3. |
| P3 | `question.md` too long; put review-critical info in the scribble, else delete to save tokens | 🔶 | Not binary. **Route by audience**: orientation → into scribble; decision-asks (RQ1/D1/D2/D3, A/B) → stay but trimmed to *just the asks*; the "14 fixes" recap → delete (duplicates brief + comments). |

---

## 3. Root-cause synthesis

The findings cluster into **five roots, not one**. The first was visible in the original written feedback;
roots 2–5 surfaced in the live discussion and are deeper.

1. **Audience confusion (readability).** The artifact was optimized for the LLM coder/reviewer agents; the
   human reviewer inherits machine-shaped output — terse, comment-buried (F1), unordered, context-free. Fix =
   a human-facing rendered review layer separate from the terse machine-comment layer, plus orientation-first
   ordering. (F1, C3, C6–C8 → PROP-1/2/3/5/6/13C.)
2. **Entry context is asserted, never sourced or checked (correctness).** The generator knows the flow
   location, drops it (F8), and the workflow reads no router/app-shell at all (F9) — so container fit is
   asserted and never independently reviewed, by an LLM reviewer or a human. Entry references must be *sourced
   from the requirement* and *resolvable* (sibling scribble / screenshot / open decision). (F3/F8/F9/F12 →
   PROP-2/8.)
3. **No basis/coverage model; the launch seam is an unassigned, late-detected requirement gap.** There is no
   model of which screens need scribbles, the most foundational basis (nav) is provably uncovered with no
   auto-creation (F10/F11), and the feature's outer launch seam is owned by no requirement (F12). Detection
   belongs upstream and is inherently two-tier because ownership is a *global* property a single cluster can't
   see (F13/F14). (F10–F14 → PROP-9/11.)
4. **The dependency graph and the scribble↔requirement link both rot (lifecycle).** Entry references go stale
   as artifacts regenerate independently (F10 tail), and a requirement modification never regenerates its
   scribble — silently breaking the §33 single-normative-source contract (F15). Needs standing validate+recover
   and a change-triggered regeneration. (F10/F15 → PROP-10/12.)
5. **Rigid control + discarded reasoning (transparency).** Gate cadence is hardwired lockstep with a
   two-outcome gate (F16), auto-review findings are invisible to the human (F16), and per-reviewer reasoning is
   discarded at merge (F2). Fix = review-severity-driven iteration, configurable cadence, a findings overlay,
   and per-reviewer persistence. (F2/F16 → PROP-4/7/13.)

**The entry-context spine** (how roots 2–4 connect): scribble invents entry context → LLM reviewers blind too
(F8) → workflow reads no router (F9) → needs resolvable references (PROP-8) → references need a basis (F10) →
the basis isn't guaranteed and the foundational one is provably uncovered (F11) → the seam is an unassigned
requirement gap detected too late (F12–F14) → and the whole reference graph rots (F10/F15), so it needs
standing validate+recover (PROP-10/12).

**Cross-cutting meta-theme**: almost every fix anchors to machinery that *already exists* — `foundation_gap`
+ Cross-Flow metadata (`requ-derive-from-flow` / `requ-verify-flow-coverage --all`), `components.js` +
diff-toggle script, `c_navigation_bar`, `task_ordering_rules`, `contributing_requirements`, scoped
regeneration (auto-review L32). These are **enhancements, not new subsystems**.

---

## 4. Improvement proposals (for a future impl task)

Each: skill · behavior · current → desired · anchor. Numbers are stable (F-findings reference them).

**Reading map** (proposals grouped by theme):
- *Readability & human review layer*: PROP-1, PROP-2, PROP-3, PROP-5, PROP-6, PROP-13(C).
- *Entry context · basis · coverage · ordering*: PROP-2, PROP-8, PROP-9, **PROP-11** (the consolidated
  executable spec — read PROP-8/9/10 for *rationale*, PROP-11 for the actionable R1–R4 + G1–G4 *rules*).
- *Lifecycle / integrity*: PROP-10, PROP-12.
- *Iteration control & transparency*: PROP-4, PROP-7, PROP-13.
- *Routing (separate, see §5)*: PROP-R1, PROP-R2.

### PROP-1 — Audience-separated review layer (addresses C3, C8, F1)
- **Skill**: `ui-scribble-generator`.
- **Current**: reviewer + coder detail jammed into one `<!-- -->` block per screen; invisible in browser.
- **Desired**: render a **visible, formatted review panel** per screen (collapsible / progressive
  disclosure) carrying the reviewer-relevant subset with headings and explicit *user-action vs system-action*
  labeling where an interaction sequence is shown. Keep a separate **terse machine comment** block for the
  coder/LLM (component mapping, rule-audit trace) — do not expand that for human readability.
- **Anchor**: REQ-PROC-032 — section governing scribble screen structure / contract block (verify exact AC).

### PROP-2 — Orientation-first ordering + entry-context as a reviewable correctness fact (addresses C1, C6, C7, F3, F8)
- **Skills**: `ui-scribble-generator` (emit) · `ui-scribble-auto-review` + reviewers (check).
- **Current**: descriptions lead with screen title + AC list; info-model boundary last; entry context is
  known to the generator but dropped after reasoning (`flow_positions` keeps only `step_number`); container
  choice is asserted and never independently reviewed (F8).
- **Desired** — this is a **correctness** fix, not only readability:
  1. **Emit entry context**: every screen + index entry **leads with flow-position** ("FLOW-002 Step 5 of
     [1,2,3,4,5,8]; opened from <entry surface>; container: <Dialog/…> because <rationale>") and sibling
     relation; persist predecessor step/screen + entry surface + container rationale in `flow_positions`
     (not just `step_number`); surface the **information-model boundary** near the top of `index.html`.
  2. **Review the container**: add a reviewer check — "navigation/container pattern is appropriate for the
     entry surface and the content size" — to rule-reviewer (or heuristics-reviewer).
  3. **Ground the check**: pass `flow_context` explicitly as an input to the auto-review phase (today it is
     not — SKILL.md line 10), so the container check is grounded, not guessed.
- **Anchor**: REQ-PROC-032 — index/screen description spec + auto-review reviewer rubric.

### PROP-3 — Reviewer guide as reusable component (addresses C5)
- **Skill**: `ui-scribble-generator` (consumes) + a new shared component under
  `requirements_tasks/_scribble_components/` (authored once).
- **Current**: `index.html` has header + out-of-scope, but no review instructions.
- **Desired**: a **reusable, non-regenerated** review-guide component embedded into `index.html`:
  (a) "open FLOW-A/B, steps X/Y/Z are these screens; requirement M on demand"; (b) UX-review checklist
  (personas, VSD decisions, flow fit, component choice, ISO/Nielsen interaction principles, with English
  external links) behind **progressive disclosure**; (c) out-of-scope as a **flat bullet list** (not disclosed);
  (d) a short note on **how T1–T3 rules are formed** — prefer generic rules; warn that new rules may conflict
  with existing ones and that a check may raise follow-up questions.
- **Anchor**: REQ-PROC-032 — review-gate / index requirements. (Component lives in `_scribble_components/`.)

### PROP-4 — Persist per-reviewer findings (addresses P2, F2; serves Seed 3)
- **Skill**: `ui-scribble-auto-review`.
- **Current**: only the merged brief/protocol is written; individual reviewer outputs are discarded.
- **Desired**: each reviewer (rule, persona-walk, heuristics, cross-feature, per-flow walk) writes its raw
  findings to a per-reviewer file in the task's `plans_and_protocols/` before merge — enabling weak-link
  detection and developer transparency. (Also satisfies the CLAUDE.md file-based-memory rule that every
  agent persists findings.)
- **Anchor**: REQ-PROC-032 — auto-review phase; cross-ref CLAUDE.md §1 file-based memory.

### PROP-5 — Script-generated state variants (addresses C4, F4)
- **Skill**: `ui-scribble-generator` + a helper script.
- **Current**: states are LLM-authored detached `.panel` blocks below the frame.
- **Desired**: generate state variants as **small-multiples** from a single source, highlighting only the
  changed region (avoids full-copy drift and token cost). Visually anchor each variant to the element it
  modifies.
- **Anchor**: REQ-PROC-032 — required-states depiction. (Note: scripted approach — coordinate with the
  generator agent's output contract.)

### PROP-6 — Trim `question.md`; route info by audience (addresses P3, F5)
- **Skill**: `ui-scribble-iterate` (Phase-3 gate emitter).
- **Current**: gate `question.md` recaps all 14 fixes (duplicate) + carries decision asks.
- **Desired**: `question.md` keeps **only** the decision asks (RQ1/D1/D2/D3, A/B), trimmed; move orientation
  into the scribble; delete the fix recap (lives in `auto_review_brief.md` + per-element comments).
- **Anchor**: REQ-PROC-032 — Phase-3 user-feedback gate content.

### PROP-7 — Lower auto-review token cost (addresses P1)
- **Skill**: `ui-scribble-auto-review` / `ui-scribble-iterate`.
- **Current**: all reviewers + per-flow walk run every round, each re-reading flows/requirements; resume
  re-reads heavy context.
- **Desired**: make phases independently resumable (persist intermediate state — PROP-4 helps); let the gate
  choose which reviewers run on later rounds rather than always all five. The Pro cache-TTL loss on session
  reset stays unavoidable; this targets total token cost, which is not fixed.
- **Anchor**: REQ-PROC-032 — auto-review orchestration. (Uncertain — see §6.)

### PROP-8 — Entry/exit information-model completeness + bounded reconciliation (addresses F9)
- **Skills**: `ui-scribble-generator` (emit) · reviewers (check) · optional targeted router read.
- **Current (F9)**: the workflow reads **no** router / app-shell / existing entry-screen. Four entry/exit
  facts are unverified: (a) entry-surface *type* (1st-level nav vs app-bar button vs contextual), (b)
  entry-point *multiplicity* (single vs N routes), (c) back/close *destination*, (d) consistency with the
  *built* router. The flow (FLOW-002) carries (c) partially (Step 8: dismiss → "Delivery Complete") and (b)
  partially (Exception 1.1 alternate entry), but the generator does not extract/render them — scribble 02
  shows only a header-X → "zone detection" (M10), never the back destination.
- **Desired**:
  1. **Emit** entry-surface type, entry-point multiplicity (as an explicit design decision when >1), and the
     back/close **destination** as required information-model fields on each screen; extract (c)/(b) from the
     flow where present.
  2. **Emit a resolvable entry reference** (three-tier — concrete, low-cost sources that already exist):
     - **Tier 1 — sibling scribble**: link to the opener screen = the scribble screen at the *predecessor*
       flow step. `flow_positions` already records `step_number` + `requirement_id` per screen; this is the
       `ui-scribble-cross-feature-checker` substrate (sibling scribbles sharing a flow).
     - **Tier 2 — integration-test screenshot** (if the opener is already built): embed/reference the real
       screenshot at `<opener-requirement-path>/scribbles/flutter_review/screenshots/NN_<name>.{png,jpg}`
       — the same artifacts `ui-visual-validate` consumes. Cross-requirement lookup via
       `flow_positions.requirement_id` (caveat: opener must have been scribbled/implemented under its own
       requirement for the path to resolve).
     - **Tier 3 — open design decision**: greenfield, no opener yet → surface entry choice as a decision,
       do not invent it.
  3. **Review**: reviewer asserts these fields + the entry reference are present and internally consistent.
  4. **Bounded reconciliation**: *only when the entry screen already exists in `lib/`*, a **narrow** check
     that the scribble's claimed entry matches the actual router (or its Tier-2 screenshot) — NOT a general
     `lib/` read. Greenfield features skip this (Tier 3).
- **Requirement-source precondition (from F12)**: an entry reference must be *sourced from the requirement*,
  not invented by the generator. A functional requirement must specify its feature's **outer entry point(s)**
  (launch surface from the rest of the app), and ownership of the cross-feature launch seam must be assigned
  (likely a requirement-quality rule — flag for `requ-explore` / requirements-structure). If the requirement
  lacks the entry, the generator MUST treat it as a **requirement gap → `requ-explore`** (Tier-3 + classifier
  "requirement gap"), NOT fabricate the entry in HTML. This is upstream of PROP-8's tier resolution.
- **Boundary note**: deliberately does NOT pull router/implementation detail into the wireframe wholesale —
  preserves the RE-DERIVE (D1–D8) wireframe/implementation separation. Entry-surface type, multiplicity, and
  back-destination are information-architecture facts (they decide whether the container is even valid), not
  cosmetic implementation detail, so they belong in the design artifact.
- **Anchor**: REQ-PROC-032 — information-model boundary + auto-review reviewer rubric.

### PROP-9 — Scribble coverage as a first-class concept; basis presence graded, not blocking (addresses F10)
- **Skills/scripts**: new flow→scribble coverage report · `ui-scribble-iterate` (gate annotation) ·
  task-ordering rules (soft preference) · NOT `check_scribble_parity.py` (that stays storage-mirror only).
- **Current (F10)**: no model of which flow steps/screens need scribbles, no entry-basis check, brownfield
  inversion (implemented-first). Basis creation is implicit and unscheduled.
- **Desired** — make coverage explicit and degrade gracefully instead of hard-blocking:
  1. **Flow→scribble coverage report** (analog of `requ-verify-flow-coverage`): for each flow, list which
     steps/requirements have a scribble vs not; for each scribble's entry references, resolve PROP-8 tiers
     and flag **true Tier-3 gaps** (no opener scribble AND opener not built). Advisory.
  2. **Gate annotation, not a block**: an entry resolving only to Tier-3 MUST be surfaced at the Phase-3
     gate as an explicit "designing before opener exists" decision — developer consciously accepts it.
  3. **Soft ordering preference**: `next_tasks` / task-ordering prefers openers-before-openees, but does
     **not** hard-block (flows have back-edges/cross-links → strict topo order can deadlock on cycles).
- **Why not a hard "basis-first" block** (recommendation, decision is the developer's):
  - Brownfield: the existing implementation's **screenshot is a valid basis** (PROP-8 Tier 2) — blocking on
    a missing *scribble* would block work whose basis already exists.
  - Cycles in the navigation graph make strict ordering undeadlockable only by accident.
  - PROP-8's three tiers already degrade; missing Tier-1 ≠ missing basis.
  - Narrow exception where "do them first" is right: a **pure-greenfield critical entry-path chain** (opener
    neither scribbled nor built) — handled by the gate annotation forcing a conscious call, not a blanket block.
- **Open ownership question (developer decision, see §7)**: who creates the basis — (a) demand-driven
  auto-spawn of opener scribble tasks, (b) coverage-report-driven manual scheduling, or (c) screenshot-anchored
  brownfield (no opener scribble required). Recommendation: **(c) + (b)** — anchor on whatever exists, make
  gaps visible, schedule deliberately; reserve (a) for pure-greenfield chains.
- **Anchor**: REQ-PROC-032 — coverage/ordering (likely a new AC; flag for `requ-explore`).
- **Extension (from F11)** — three additions the coverage model must include:
  1. **Span both requirement trees**: coverage must check functional flow-derived requirements AND the
     non-functional `ui_ux_design_system/navigation_patterns/*` (and similar chrome-owning) requirements. A
     functional-only coverage check misses the nav shell entirely (REQ-NFUNC-011 has zero scribble coverage
     today and nothing flagged it).
  2. **Presentation-scope ⇒ scribble-coverage signal**: any requirement (either tree) with Presentation
     scope that lacks a scribble should be surfaced by the coverage report; consider having
     `task-derive-from-requ` auto-flag a scribble task (or at least a coverage entry) for Presentation-scope
     ACs rather than relying on plan-author memory. Graded per this proposal — surface, don't hard-block.
     Includes a **retroactive backfill** path for pre-scribble implemented requirements (e.g. REQ-NFUNC-011).
  3. **App-shell / navigation-map keystone**: designate one canonical artifact (a navigation-map scribble or
     an extension of `c_navigation_bar`) that declares primary destinations + each feature's entry point.
     This becomes the authoritative PROP-8 Tier-1 target for "opened from a nav destination," so feature
     scribbles resolve entry context against it instead of re-deriving location. Open question: component-level
     coverage (`c_navigation_bar`) vs. a dedicated app-shell screen scribble — developer decision.

### PROP-10 — Mode-independent entry-reference integrity check + bounded recovery (extends PROP-8/PROP-9)
- **Skills**: `ui-scribble-cross-feature-checker` (dangling cross-refs — already owns sibling consistency) ·
  `ui-scribble-auto-review` (validate per run) · `ui-scribble-iterate` (recovery routing via `pending_feedback`).
- **Principle**: brownfield is NOT the only fragile mode. The entry-reference graph rots in any mode because
  every artifact regenerates independently. So validate + recover **every generation+review**, not once.
- **Check (every run)**: each entry reference resolves to exactly one *live* tier (Tier-1 target exists /
  Tier-2 screenshot path exists / Tier-3 explicitly flagged); each back/close destination names a screen
  present in the flow+scribble set; container choice consistent with the resolved entry. Dangling/ambiguous → fail.
- **Recovery (bounded — default annotate + surface; never silent; never unbounded auto-create)**:
  - dangling Tier-1 (opener scribble vanished) → downgrade to Tier-2/3 + add gate item;
  - renamed/moved sibling → re-resolve via `flow_positions`, else flag;
  - unresolvable at all → route to `pending_feedback` with a *specific* recovery question (reuse existing
    back-pressure machinery — do NOT invent a new halt);
  - heavier moves (spawn opener-scribble task) are **proposed, not auto-performed** (guards the PROP-9(a) cascade).
- **Caveats**: dangling-cross-ref detection belongs in `ui-scribble-cross-feature-checker`; human escalation
  reuses `pending_feedback`, not a parallel mechanism.
- **Anchor**: REQ-PROC-032 — auto-review integrity + cross-feature checker; reuse `pending_feedback`.

### PROP-11 — Scribble coverage & ordering mechanism (consolidates PROP-8/9/10 into an actionable spec)
Developer-specified rules (R1–R4) + the guardrails (G1–G4) that make them executable. PROP-8/9/10 carry the
*rationale*; this is the executable distillation.

**R1 — Auto-create a scribble task for every UI requirement.**
- Trigger: requirement specifies **renderable screens/components**.
- **G1 (scope guard)**: exclude pure rule/token/pattern requirements (e.g. REQ-NFUNC-011 §2 nav-eligibility
  rules) — they need no wireframe; covered by design-system docs + components (`c_navigation_bar`).
- Where: `task-derive-from-requ` auto-sets `task_type: scribble` for qualifying requirements instead of
  relying on plan-author memory.

**R2 — Order scribble tasks via `after` so the basis exists at execution; retroactively re-wire existing tasks.**
- **G2 (cycle guard — make-or-break)**: only the **primary entry path** edge (is-entered-from, along the
  flow's forward direction) is an `after` ordering edge. Back/close and cross-navigation edges are **NOT**
  ordering edges. Without this, back-edges create `A after B` ∧ `B after A` → unresolvable cycle.
- Machinery: `after` frontmatter + `.claude/task_ordering_rules.yaml` (`claude-modify-ordering-rules`);
  retroactive re-wiring is a `task-repair-meta` pass.

**R3 — Resolve each basis; create a blocking task when absent.**
Resolution branch per direct opener:
1. opener has a scribble → use it (Tier-1).
2. else opener implemented → fresh integration-test screenshot exists → use it (Tier-2);
   stale/missing → **create integration-test screenshot task** that BLOCKS this scribble.
3. else (not implemented, no scribble) → **create basis scribble task** that BLOCKS this scribble.
- **G3 (cascade guard)**: block on the **direct** opener only (depth-1), never the transitive upstream chain
  — brownfield would otherwise spawn a blocking wave.
- **G4 (staleness guard, from PROP-10)**: a screenshot used as basis must be validated current, else treated
  as missing (→ branch 2 screenshot task).

**R4 — Create missing "basics" requirements (without them the feature can't be used).**
- **Detect EARLY, in `requ-derive-from-flow`** (F13) — earliest point, and it already owns requirement
  creation (no governance problem: this is the sanctioned authoring path, not silent auto-creation).
- **Two-tier detection (F14 — `requ-derive-from-flow` has a global-knowledge ceiling)**:
  - **Tier A (local/provisional)** — `requ-derive-from-flow`: for each screen a flow touches, verify a
    requirement owns its *outer* entry point; if none, raise a **`foundation_gap` tagged Cross-Flow** (L258
    category exists). Must NOT dedup/confirm — it can't see other clusters' unwritten requirements.
  - **Tier B (global/authoritative)** — `requ-verify-flow-coverage --all`: dedup the N independent app-shell
    requests into ONE launch-map requirement + confirm ownership against the *assembled, written* requirement
    set (consumes Foundation Gaps + Cross-Flow metadata; runs post-derivation).
- **Layering of detectors** (earliest → backstop): Tier A (provisional, derivation) → Tier B (authoritative,
  post-write global) → PROP-8 scribble-time requirement-source check (final backstop for seams still missed).
- **Requirement-level ordering**: feature requirements needing the launch surface take a foundation
  dependency on the app-shell requirement so it is written first.
- Likely shape: ONE functional requirement owning the **app-shell / feature-launch map** (F12 seam owner +
  PROP-9 keystone) — the canonical basis all entry references resolve against.

**Anchor**: REQ-PROC-032 (coverage/ordering — new ACs; flag `requ-explore`) + task-ordering rules +
`task-derive-from-requ` + requirement-quality rule for entry-seam ownership (F12).

### PROP-12 — Scribble staleness & regeneration trigger on requirement change (addresses F15)
- **Skills/scripts**: `requ-explore` / `task-derive-from-requ` (trigger) · `check_scribble_parity.py` or new
  staleness check (safety net) · `ui-scribble-iterate` (scoped regen) · `ui-verify-flutter` (impl-drift, post-release).
- **Current (F15)**: requirement modification → no scribble task; no content-drift detection; scribble goes
  silently stale, breaking the §33 single-normative-source contract.
- **Desired**:
  1. **Trigger (always, on LOCKED-IN change)**: when `requ-explore`/`task-derive-from-requ` modifies a
     requirement, detect whether the change touches LOCKED-IN Presentation content; if so, set the affected
     scribble `stale_since: <commit>` and create a **scoped** regeneration task (after the requirement write).
     RE-DERIVE/backend-only changes do not trigger.
  2. **Scope = change size** (auto-review L32 partial regen): regenerate only changed screens/ACs, copy the
     rest — bounds cost without violating the contract. Size governs scope, never *whether*.
  3. **Safety net**: a staleness check compares each scribble's `contributing_requirements` commit against the
     current requirement; drift with no open regen task → flag stale (extends `check_scribble_parity.py`,
     which today only catches orphaned paths).
  4. **Released-app loop (3 coupled artifacts)**: requirement → scoped scribble regen → `ui-verify-flutter`
     detects implementation now diverges from the new scribble → impl update task. Each edge gets a drift detector.
- **Anchor**: REQ-PROC-032 — scribble lifecycle/staleness; SKETCHES_README §33 contract.

### PROP-13 — Decoupled iteration control + script-rendered findings overlay (addresses F16)
- **Skills/scripts**: `ui-scribble-iterate` (cadence/stop) · `ui-scribble-auto-review` (severity stop + anchor
  field) · `components.js` / new overlay script · Phase-3 gate prompt.
- **A. Decouple cadence** from the version counter. Gate outcomes become `approve | feedback | run another
  auto-review | auto-review + my feedback`. Cadence via a small set of **named policies** (not free-form, to
  preserve convergence guarantees): `every` (current), `after:[1]`, `auto-to:[N]`, `gate-at-v1` (review raw
  generation). Caveat: "run another auto-review" is only valuable if an **input changed** (requirement edit,
  newly-anchored rule) — ties to PROP-12; a pure repeat is convergent/no-op.
- **B. Review-driven stop (no complexity ceiling)**: iterate while latest review (auto OR manual) yields
  `severity ≥ MEDIUM`; LOW-only ⇒ converged ⇒ gate/approve. One fixed **non-convergence circuit-breaker**
  (generalized v6 fatigue) escalates persistent MEDIUM+ gaps to `requ-explore`. No complexity metric.
- **C. Findings overlay (anti-duplicate-work)**: findings authored once with a machine-readable `anchor:`
  (CSS selector / id) → script binds clickable markers → click overlay. THREE awareness layers: per-screen
  finding **count badge** + element **markers** + Phase-3 **gate prompt** "read findings first." Extends
  `components.js` + diff-toggle patterns; composes with PROP-4 (provenance); single-source per §33.
- **Anchor**: REQ-PROC-032 — iteration orchestration + Phase-3 gate + auto-review finding schema.

---

## 5. Workflow UX finding — routing-skill enforcement (separate from scribble skills)

**Observation (F7)**: `claude-route` was skipped on "do TASK-PROC-032-28". Harmless here only because the
task was already `in_progress`. The skill's real obligation is not just dispatch — it sets `status: in_progress`
+ `started:`, which the status overview, next-task selection, and blocked-task detection depend on.

**Two complementary fixes (recommend both):**

- **PROP-R1 — Behavior: make the state transition unconditional.** `claude-route` should always perform the
  status bookkeeping, then decide whether to dispatch a workflow **or short-circuit to "continue in-session"**
  for interactive-explore tasks. Bookkeeping always fires; only dispatch is conditional. This closes the actual
  hole (the orchestrator rationalizing "routing is pointless for this interactive task" and freelancing).
  *Load-bearing fix.*
- **PROP-R2 — Rename `claude-route` → `task-start`.** Gives a lifecycle bracket symmetric with the existing
  mandatory `task-complete`: `task-create → task-start → … → task-complete`. The verb "start" *describes* the
  `in_progress` transition, slotting into the `task-*` family. **Caveat**: `claude-route` also routes freeform
  *descriptions* (not just task IDs) to a skill; the renamed skill's description must keep advertising that
  mode so users with no task yet still reach for it. Rename touches CLAUDE.md, `factory_flows.md`, INDEX.md,
  sibling skills, and any hooks — must go via `claude-modify-skill`; do as its own small task.
- **Honest weighting**: name alone = better affordance, same escape hatch. Behavior alone = correct but
  forgettable. Do both. PROP-R1 is the one that actually prevents recurrence.

---

## 6. What remains uncertain

- **Convergence (Seed 4)**: only one round observed; cannot yet say whether the *pilot* scribble converges,
  plateaus, or oscillates. Needs ≥1 more pilot round (v3) — note that is executing TASK-FUNC-007-01-05 (the
  specimen), separate from this evaluation.
- **Auto-review signal ratio (Seed 2)**: of the 14 v2 fixes, how many the developer would have caught
  independently is not yet measured — the developer's feedback this round was about *workflow/readability*,
  not about the 14 content fixes. Open.
- **Weak-link reviewer (Seed 3)**: **unanswerable from current artifacts** until PROP-4 persists per-reviewer
  output. This is itself a finding.
- **PROP-7 scope**: whether selectively skipping reviewers on later rounds risks missing regressions is
  unverified — needs a deliberate decision, not an assumption.
- **PROP-5 feasibility**: whether small-multiples can be script-generated without losing the LLM's
  per-state semantic annotations is unproven.
- **PROP-11 / F14 Tier-B dedup feasibility**: whether `requ-verify-flow-coverage --all` can reliably dedup N
  independent app-shell `foundation_gap`s into one requirement (vs. mis-merging distinct needs) is unproven.
- **PROP-13C `anchor:` stability**: whether findings can carry element anchors that survive regeneration
  (selectors/ids change when screens are redrawn) is untested.
- **PROP-13A cadence-policy set**: which named policies to support and how each interacts with the convergence
  circuit-breaker is undesigned.

---

## 7. Open decisions for the developer

**Scope note**: This task evaluates **workflow performance only**. It does NOT collect v2 *content*
feedback and does NOT make the v2 A/B approval call — that approval belongs to the pilot task
TASK-FUNC-007-01-05 and is out of scope here. The developer was explicit: "I do not provide content
feedback in here." The proposals in §4–§5 are the output; the decisions below are about *those*.

**Resolved by the developer in this session** (now design inputs, not open questions):
- Auto-create scribble tasks for UI requirements → **yes** (PROP-11 R1, with the G1 scope guard).
- Order via `after` + retroactive re-wiring → **yes** (PROP-11 R2, requires the G2 primary-path-only cycle rule).
- Create missing basis scribbles / use integration-test screenshots / else create a blocking screenshot task
  → **yes** (PROP-11 R3, with G3 depth-1 + G4 staleness guards).
- Create missing "basics" requirements → **yes, but governed** (PROP-11 R4 — routes through `requ-explore` /
  `product-intake`, never silent).
- Iteration count → **review-severity-driven, no complexity ceiling** (PROP-13 B); keep the escalating
  circuit-breaker.

**Still genuinely open:**
1. **Which proposals become impl tasks, and in what order?** Highest-value cluster is the entry-context
   spine: PROP-8 + PROP-11 (coverage/ordering/basis) + PROP-4 (per-reviewer persistence). Confirm sequencing.
2. **Nav-coverage granularity**: is `c_navigation_bar` (component) sufficient, or do we commit to the single
   **app-shell / feature-launch-map requirement** (PROP-11 R4)? Leaning toward the latter as the keystone.
3. **Rename `claude-route` → `task-start`?** (PROP-R2) — go / no-go. (PROP-R1 recommended regardless.)
4. **PROP-7 (selective reviewers)**: accept the regression risk of skipping reviewers on later rounds, or
   keep all reviewers every round?
5. **Gate-cadence policy set (PROP-13 A)**: which named policies to support (`every` / `after:[1]` /
   `auto-to:[N]` / `gate-at-v1`) and which is the default.

(RQ1 / D1 / D2 / D3 from `question.md` are pilot-task decisions, not evaluation-task outputs — tracked there.)
