# Round 2 Evaluation — Scribble Workflow Live Pilot (developer feedback batch on Round 1)

Date: 2026-06-04
Task: TASK-PROC-032-28 (evaluation), observing TASK-FUNC-007-01-05.
Inputs:
- Developer feedback file `2026-06-04_03_feedback.md` (responds to Round 1 findings F1, F3, F15, F16 and open decisions §7).
- A developer-supplied browser screenshot of `02_handover_send.tablet.html` (rendered view).
- Live re-inspection of `requirements_tasks/scribbles/therapist/data_transfer/v2/` and
  `requirements_tasks/_scribble_components/components.js`.
- Grounding reads of `release-begin-impl` / `release-begin-impl-finalize` SKILL.md.

This record is self-contained: a future `impl`/design task can act on it without replaying the session.
It **corrects** one Round-1 finding (F1), **records** developer resolutions to Round-1 open decisions,
**adds** new proposals, and **frames** a major scope expansion the developer mandated: a complete rethink of
the implementation workflow, not a patch.

---

## 1. CORRECTION to Round 1 — F1 was wrong (grounded)

**Round-1 F1 claimed**: the `COMPONENT MAPPING / PERSONAS APPLIED / RULES APPLIED / SCREEN CONTRACT /
RULE AUDIT TRACE` blocks are `<!-- … -->` comments that "do not render in a browser," and the developer's
"unreadable text above the scribbles" was therefore "read from source."

**That is false.** The developer disputed it and supplied a browser screenshot. Verified against the files:

- **Root cause — nested HTML comments leak into the render.** The generator wraps reviewer detail in one big
  `<!-- COMPONENT MAPPING … PERSONAS … RULES … -->` block (e.g. `02_handover_send.tablet.html` L41 opens it),
  but inside that block it ALSO emits inline `<!-- a11y-intent: … -->` comments (L53–L60).
  **HTML comments cannot nest.** The parser terminates the outer block at the *first* `-->` — the L53 inline
  a11y comment. Everything after it (L54→L84: rest of COMPONENT MAPPING, DOMAIN CLASSES, PERSONAS APPLIED,
  RULES APPLIED) renders as **visible, unstyled wall-of-text**, including the literal trailing `-->` the
  screenshot shows.
- **Not a viewer quirk.** `components.js` only resolves `<div data-component="…">` placeholders (fetch +
  `replaceWith`); it does NOT inject comment content. So the visible text is pure browser comment-nesting
  behaviour, reproducible in any browser.
- **Scope**: every screen file that places inline a11y/component comments inside the big block is affected —
  desktop too (`02_handover_send.desktop.html` leaks from L61). Opener/closer counts are *balanced* per file
  (28/28 etc.), which is why a naive count check misses it; the defect is structural (nesting), not count.
- **Plus `index.html`** independently renders a large block of *intentionally visible* dense prose (meta,
  note, per-screen descriptions, personas/rules, carried decisions, info-model boundary). That is the other
  half of "unreadable text above the scribbles" — legitimately rendered, but a wall.

**Consequence for Round-1 analysis**: the readability root cause (Root #1) is *strengthened and re-aimed*. It
is not merely "human inherits machine-shaped comment-buried output." It is two concrete defects:
1. **A rendering bug** — reviewer detail meant to be hidden leaks into the page via comment nesting.
2. **A dual-audience design gap** — even when correctly hidden, there is no *human-facing rendered* review
   layer; and `index.html`'s visible prose is an unstructured wall.

This corrects PROP-1's premise: PROP-1 must FIRST fix the comment-nesting leak (or stop using nested comments
entirely — e.g. a single `data-*`-attribute or a dedicated non-rendered `<script type="text/plain">` block),
THEN add the human-facing rendered review layer. Anchor unchanged (REQ-PROC-032 screen-structure/contract AC).

---

## 2. Developer resolutions to Round-1 open decisions (now design inputs)

These close items from Round-1 §7 and adjust proposals.

- **claude-route vs task-start (Round-1 §7 Q3 / PROP-R2)** — **Keep BOTH, separated.** `claude-route` is still
  needed for user requests that have no task. Introduce **`task-start`**, which *calls* `claude-route`. So
  PROP-R2 is no longer a rename — it is a **new wrapper skill** `task-start` layered over `claude-route`.
  PROP-R1 (unconditional status bookkeeping) still applies; the bookkeeping (`status: in_progress`,
  `started:`) belongs in whichever skill owns the task-ID entry path — clarify ownership between `task-start`
  and `claude-route` when implementing.

- **PROP-7 selective reviewers (Round-1 §7 Q4)** — **Accept skipping, but only under firm rules, and make
  execution sequential.** Two hard requirements:
  1. **Firm skip rule**: an auto-review agent may be skipped on a later iteration *only when* it produced
     nothing substantial in the previous iteration. The skip is overridden (agent runs again) when developer
     feedback triggers substantial rework. Define "substantial" concretely (ties to PROP-13B severity:
     a reviewer that returned no `severity ≥ MEDIUM` finding last round is skip-eligible next round, unless
     its scope was touched by new feedback).
  2. **Sequential, NOT parallel execution** (new hard constraint): reviewers must run one at a time. Rationale
     — if the session/token limit is hit mid-run, only the single in-flight agent is left incomplete; with
     parallel fan-out, a limit hit forces ALL agents to restart. This directly contradicts any
     "spawn all reviewers in parallel" design and must be encoded in `ui-scribble-auto-review`.
  - **Note**: constraint (2) interacts with the CLAUDE.md long-running-agent cache rule — sequential reviewers
    extend wall-clock time, so background execution + heartbeat discipline matters more, not less.

- **PROP-13A gate cadence default (Round-1 §7 Q5)** — **Default = gate the human only when auto-review has
  converged** (no substantial improvements left), i.e. the `auto-to:[converged]` policy, NOT `every`. The
  developer's stated default: the user is asked for review only once the automatic reviews find no more
  substantial improvements — assuming the auto-reviews did not surface anything grave enough to require
  flow/requirement changes (if they did, that escalates upstream per PROP-13B circuit-breaker). The developer
  believes this single default suffices; the other named policies (`every`, `after:[1]`, `gate-at-v1`) become
  optional overrides, not required. (Developer flagged mild uncertainty about whether the question was fully
  understood — treat "converged-default" as the confirmed design intent.)

- **F3 extension — entry context absence also hides DIMENSIONS.** Beyond "can't judge container fit," not
  seeing the entry context means **the size of the container is invisible** — e.g. for a dialog, how large the
  dialog is. Only relevant when a screen has **multiple possible container sizes** (e.g. several dialog sizes).
  Extends PROP-2: when the container is size-variant, the emitted entry-context fact must include the chosen
  size/dimension and its rationale, and the reviewer must check size-appropriateness, not just pattern-type.

---

## 3. New proposals from this feedback

### PROP-14 — Script-driven user-flow viewer embedded in the scribble (new)
- **Source**: developer feedback ("Was mega praktisch wäre, wäre, wenn die Userflows auch in dem HTML
  angezeigt werden würden").
- **Desired**: a **"Show User Flows"** toggle in the scribble HTML that opens a **sidebar**, with **tabs** to
  pick which flow to view; the flow content is shown inline.
- **Hard constraints (developer-specified)**:
  1. **Script-driven, NOT LLM-generated.** A script must **copy** the user-flow source files into / link them
     for the viewer. The LLM must NOT read the flow files and re-emit HTML from them (avoids drift + token cost
     + a second normative copy). This is a token-minimisation AND single-source requirement.
  2. **Needs a Markdown→HTML rendering technology** (flows are Markdown). Selecting/installing one is a
     **dependency-admission decision** (REQ-PROC-060) — must be developer-authorized, not self-added. Options
     to evaluate: a vendored client-side MD renderer (e.g. a single static JS lib) vs. a build-time MD→HTML
     step in the generator's helper script. Client-side keeps the artifact self-contained and zero-build;
     build-time avoids shipping a JS dependency. Flag for the redesign.
- **Cherry-on-top (nice-to-have)**: highlight, in colour, the passages of the flow that are **relevant to the
  scribbled screens**, so the reviewer immediately sees which flow steps matter here. Feasible substrate exists
  — `flow_positions` already records `step_number`, and `index.html` already states "FLOW-002 steps
  [1,2,3,4,5,8]"; a script can map those step numbers to flow-text anchors. (Round-1 F6 established this.)
- **Anchor**: REQ-PROC-032 — index/review-layer; coordinate with PROP-3 (reusable review-guide component) and
  the dependency gate.
- **Open**: which MD-render technology, and client-side-vendor vs build-step — developer decision.

---

## 4. MAJOR SCOPE EXPANSION — "Rethink the whole implementation workflow" (developer mandate)

The developer's headline instruction: *"we must not simply press these new functions into the existing
workflow — we must completely rethink the complete workflow, i.e. all skills involved."* This elevates several
Round-1 proposals (PROP-8/9/10/11/12) from "scribble-skill enhancements" to a **cross-skill workflow
redesign** spanning the top-down chain (`requ-derive-from-flow` → `task-derive-from-requ` →
`release-begin-impl`/`-finalize` → scribble skills → coding tasks). This section frames the problem set; it is
**not** a design — the design is the next, dedicated effort.

### Grounding of the current pipeline (what exists today)
- `release-begin-impl`: scope-verify → holistic task plan → activate release → Phase 2c uses
  `task-derive-from-requ` (run in autorun agents) to create **all** tasks for in-scope requirements, including
  **coding tasks**. → `release-begin-impl-finalize`: coverage audit, after-chain reconciliation, semantic
  validation, user gate.
- So today: **coding tasks are created up front**, before any scribble exists or is approved. This is exactly
  what the developer wants to invert.

### The redesign problem set (developer-stated sub-problems)

**P-A — Scribbles get their own layer, executed before coding tasks exist.**
- Desired order: define user flow → derive tasks that *adjust requirements* → on "Begin Implementation",
  **first create ONLY the scribble tasks** (nothing else) → developer executes the scribble tasks → **only when
  all scribble tasks are complete AND scribbles are approved** are the coding/implementation tasks created.
- Rationale: reviewing the UI may reveal changes needed elsewhere — at the requirement level, or even the
  user-flow level. If coding tasks were already created, they'd be invalidated. So coding tasks must not exist
  until the scribbles are locked.
- Implication: the scribble layer is a **hard gate** between requirement-derivation and code-task creation.

**P-B — Split "Begin Implementation" into 2–3 skills, with names that convey ordering.**
- The single `release-begin-impl` must be decomposed so that no one skill carries all complexity, and so the
  scribble gate sits between phases. Likely shape:
  - Skill 1 (keeps the name "Begin Implementation"): scope-verify + create **scribble tasks only**.
  - Skill 2 (post-scribble-approval): create the **coding/implementation tasks** now that scribbles are locked.
  - Possibly Skill 3: handle the loopback path (re-derive after a flow/requirement change — see P-C).
- **Naming challenge (developer-flagged)**: only the first is "Begin Implementation"; the later skills run
  *during* an already-begun implementation, so their names must make the call-order and relationships obvious
  (cf. the `task-start`/`task-complete` lifecycle bracket pattern).

**P-C — Loopback / incremental-change handling (the hard part).**
- At the scribble-approval gate the developer may decide the **user flow** itself needs adjustment → the whole
  chain re-runs from the adjusted flow: tasks that adjust requirements are created again. **Open question the
  developer raised explicitly**: on such a re-run, are **new scribble tasks** created again, or are the
  existing (un-approved) scribbles updated in place? What is the best process for incremental changes when the
  previous run's scribbles were never approved?
- The scribble skill also loops back at other points — e.g. when it finds the **entry is missing in another
  requirement** (Round-1 F12/PROP-8 requirement-source check). All these loopbacks must be designed coherently:
  which skill owns each loopback, where the boundaries are, and whether each loopback **creates new tasks**
  (e.g. a requirement-adjustment task or a flow-adjustment task) or is handled in-session.

**P-D — Token / session-content minimisation across the whole chain (re-examine the cut points).**
- Stated goal: minimise **total** token usage of the whole process → read information **as rarely twice as
  possible**; but simultaneously keep each session from holding too much → each session should hold **only the
  information it actually needs**. This forces new session boundaries via **agents or new tasks** (new tasks run
  in fresh sessions). The design question is **where to make the cut**.
- The developer explicitly asks to **re-examine existing skills under this lens**, naming `requ-derive-from-flow`
  (Round-1 PROP-11 R4 / F13 proposed changes to it). Verify whether those proposed changes still make sense given
  the redesign, or whether a different split is better. (This is the same "which files are read by which session"
  analysis done in the prior skill design — apply it whole-chain.)

**P-E — F15 extension: WHEN do scribble adjustments happen, and the requirement↔scribble discrepancy window.**
- The session that *adjusts requirements* (`requ-explore` workflow) is already token-heavy, and most of those
  tokens are irrelevant to adjusting the scribble. So adjusting the scribble inline is wrong → **auto-create a
  separate scribble-adjustment task**.
- **But that opens a discrepancy window**: between the requirement change and the scribble-adjustment task
  executing, requirements and scribbles disagree — violating the §33 single-normative-source contract during
  that window. Developer's open questions:
  1. Is **transparency** enough (record the staleness as a requirement/metadata flag), or does it cause
     downstream problems?
  2. **Other readers of requirements that depend on correct scribbles** must block on the stale scribble:
     e.g. another scribble task that reads the requirement and finds the scribble stale must **block and put
     the scribble-adjustment task in its `after` field** so the fix runs first. Are there other such readers?
     The main one identified: **coding tasks** that read requirements newer than the scribbles.
  3. **When can a coding task exist that reads requirements newer than its scribbles?** This can happen when,
     *during implementation for a release*, requirements (or flows) are adjusted because something proved
     unworkable technically. → The redesign must define how the scribble layer stays consistent when
     requirements change mid-release. (This is why P-A's "coding tasks only after scribble approval" is
     necessary but not sufficient — mid-release requirement edits re-open the gap.)
- This extends PROP-12 (staleness trigger) with the **discrepancy-window governance** problem: blocking edges,
  transparency flags, and the set of requirement-readers that must respect scribble staleness.

**P-F — F16 extension: cross-requirement scribble cascade.**
- Round-1 F16 routing said "requirement ambiguity → escalate to `requ-explore`." Developer raises the harder
  case: a requirement change that affects scribbles of **another** requirement.
- **Worked example (developer's)**: a Dashboard requirement shows information and offers entry points to open
  details / perform actions. Those details/actions belong to **other** feature requirements, not the dashboard
  requirement. If the dashboard's interaction model changes fundamentally, every feature that surfaces data or
  actions on the dashboard may need scribble changes — **because their entry points changed** — even though
  those features' **requirements are unchanged**.
- So the cascade is **scribble-level / UI-level, not requirement-level**: requirements stay valid, but the
  entry-context (PROP-8) of dependent feature scribbles is now stale. **Open question**: how is such a cascade
  resolved, and how are **multi-step** cascades (a change rippling through several dependent scribbles, each
  triggering further dependents) detected and ordered? This is the entry-reference-graph rot (Round-1 F10/PROP-10)
  seen from the *requirement-change* direction, and it needs the dependency model PROP-10 proposed — but applied
  across requirement boundaries, driven by **shared flows / shared entry surfaces**, not shared requirements.

### Why this is one coherent problem, not six patches
P-A/P-B set the *task-lifecycle ordering* (scribble layer before code). P-C/P-E/P-F are all the *loopback &
consistency* problem from three angles (flow re-adjust, requirement-change staleness window, cross-requirement
UI cascade). P-D is the *session-boundary / token* constraint that any solution must satisfy. The Round-1
entry-context spine (F8→F15) is the technical substrate; this section is the **process/orchestration layer**
on top of it. The developer is explicit that these must be designed together.

---

## 5. Updated open-decisions ledger (supersedes Round-1 §7 where noted)

**Now resolved (design inputs, were open in Round 1):**
- Q3 claude-route/task-start → **both, separated; `task-start` wraps `claude-route`** (§2).
- Q4 PROP-7 selective reviewers → **skip-when-nothing-substantial + MANDATORY sequential execution** (§2).
- Q5 PROP-13A cadence → **default = gate only on auto-review convergence** (§2).
- F3 → extended to include container **dimension** visibility (§2).

**Newly open (raised this round — for the workflow-redesign effort):**
1. **Scribble-layer task ordering (P-A)**: confirm "Begin Implementation creates scribble tasks only; coding
   tasks created only post-approval." (Developer stated as intent — confirm as a hard requirement.)
2. **Begin-Implementation split (P-B)**: 2 skills or 3? Names that convey call-order. Where exactly are the
   boundaries?
3. **Loopback task model (P-C)**: on a flow/requirement re-adjust at the scribble gate, are NEW scribble tasks
   created or existing un-approved scribbles updated in place? Same question for the entry-missing loopback.
4. **Session/token cut points (P-D)**: where to split sessions (agent vs new task) across the redesigned chain;
   re-validate the Round-1 changes proposed to `requ-derive-from-flow`.
5. **Discrepancy-window governance (P-E)**: transparency flag vs blocking `after` edges; enumerate the full set
   of requirement-readers that must respect scribble staleness; handle mid-release requirement edits.
6. **Cross-requirement cascade resolution (P-F)**: how to detect, order, and resolve multi-step UI cascades
   driven by shared entry surfaces when a requirement changes but dependents' requirements do not.
7. **PROP-14 dependency**: which Markdown→HTML technology, client-side-vendored vs build-step (REQ-PROC-060).

**Process decision for the developer (meta):** this has grown past "improve the scribble skills" into a
full implementation-workflow redesign. Recommended next step: a **dedicated architecture/design task**
(architecture-advisor-led) that takes §4's P-A…P-F as its problem statement and the Round-1 PROPs as its
technical substrate, and produces the new skill topology + task-lifecycle + session-cut design — BEFORE any
impl task touches individual skills. Confirm whether to spin that up now or accumulate one more pilot round
first.

---

## 6. What remains uncertain (carried + new)

- Carried from Round 1: convergence rate (Seed 4), auto-review signal ratio (Seed 2), weak-link reviewer
  (Seed 3 — still unanswerable until PROP-4 persists per-reviewer output), PROP-5 small-multiples feasibility,
  PROP-13C anchor stability, PROP-11/F14 Tier-B dedup feasibility.
- New: whether the scribble-layer hard gate (P-A) deadlocks against mid-release requirement edits (P-E) — the
  two constraints are in tension and the resolution is undesigned.
- New: whether the cross-requirement cascade (P-F) can be made tractable without a global UI-dependency graph
  that itself becomes a maintenance burden.
- New: PROP-14 — whether colour-highlighting flow passages can be driven purely by `flow_positions` step
  numbers without an LLM re-reading the flow (the developer's hard constraint).

---

## 7. The comment-nesting render leak — FOLDED INTO THE REDESIGN (developer decision)

The **comment-nesting render leak (§1)** is a concrete, isolatable bug: `ui-scribble-generator` nests inline
`<!-- … -->` comments inside the big reviewer block, and HTML comments cannot nest, so reviewer detail leaks
into the rendered page. The minimal fix is to stop nesting (single flat comment, or move reviewer detail out
of HTML comments into a non-rendered carrier the generator controls).

**Developer decision (2026-06-04)**: do NOT spin this off as a standalone fix. **Fold it into the redesign**,
where it is addressed alongside PROP-1's human-facing rendered review layer — the leak and the dual-audience
gap share the same locus (how reviewer detail is carried in the artifact), so a single coherent design should
own both rather than a quick patch followed by a re-design. The redesign task therefore inherits this as a
concrete, must-fix sub-item (not merely a design abstraction). Anchor: REQ-PROC-032 screen-structure/contract AC.
