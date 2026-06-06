# Contingency / branch plans — what we do per empirical outcome

Task: TASK-PROC-032-29. Date: 2026-06-05.
Answers the developer question: *do we have different alternative plans depending on the outcomes of the
empirical validations?* Yes. This document gives, for each of the five empirical items (`11` §D), the
**measurement**, **Plan A** (the designed path if it validates), the **trigger** that flips us off Plan A, and
the **alternative plan(s)** with pros/cons. It closes with the **compound-failure** case (what makes the core
model itself pivot) and an honest **abort/rethink** line.

## 0. Why the contingencies are cheap (the strategic frame)

Fixture-first (Q1) was chosen so every empirical question is answered on a **throwaway web fixture at STEP B/C**
— *before* the 0.0.1 commitment at STEP D. So for E1/E2/E5 the cost of "Plan B" is **one more fixture
iteration**, not a redone release. E3/E4 are the two that can only be fully confirmed at STEP D (on real
0.0.1) — those are the ones worth the most caution. The branch structure below is therefore not symmetric:
fixture-stage failures are cheap pivots; STEP-D-stage failures are the ones that could cost real rework.

| # | Empirical item | Measured at | Cheap-pivot? |
|---|----------------|-------------|--------------|
| E1 | Liveness/throughput under SCI | STEP B/C (fixture P-E run) | ✅ fixture |
| E2 | Cascade width / breaker N | STEP B/C (fixture P-F run) | ✅ fixture |
| E3 | Presentation-code salvage rate | STEP D (real 0.0.1 reconcile) | ⚠️ release-stage |
| E4 | Fixture fidelity to real P-F | STEP D (gap between fixture & 0.0.1) | ⚠️ release-stage |
| E5 | AC facet-tagging accuracy | STEP B/C (fixture ACs) | ✅ fixture |

## 0.6 Pre-registered decision metrics & thresholds (commit these BEFORE running the fixture)

Pre-registering thresholds *before* the fixture run is deliberate: it stops the end-of-STEP-C review from
rationalising whatever number we happen to get ("looks fine"). Each item has **one decision metric**, a
**green/amber/red** band, and the branch a **red** triggers. Numbers are starting bands — tune only with a
written reason, never after seeing the result.

| # | Decision metric (one number) | 🟢 Green (Plan A) | 🟡 Amber (watch / minor knob) | 🔴 Red (trigger branch) |
|---|------------------------------|------------------|------------------------------|------------------------|
| E1 | **stall fraction** = blocked coding tasks ÷ total release coding tasks after one mid-release edit; **+** cross-unit-leak (bool) | ≤ 15% **and** no cross-unit leak | 15–40% **or** leak only into directly-coupled units | > 40% **or** leak into unrelated units → E1-B1, then B2 |
| E2 | **max wavefront width** = dependents touched by one origin change; **+** propagation ratio = refreshes that move their own outward surface | width ≤ 3 **and** ratio < 0.2 | width 3–7 **or** ratio 0.2–0.5 | width > 7 **or** ratio > 0.5 → E2-B3 if hub-concentrated, else B2 |
| E3 | **median surviving-decomposition fraction** across re-derived Presentation-code tasks (diff) | ≥ 70% | 40–70% | < 40% → E3-B1 (delete-and-re-derive) |
| E4 | **surprise count** = real-0.0.1 cascade/staleness behaviours the fixture never produced | 0 | 1–2 minor (cosmetic) | ≥ 1 structural / tech-binding → E4-B2, B3 |
| E5 | **mis-tag rate** on a human-audited sample of fixture ACs | ≤ 5% | 5–20% | > 20% → E5-B3 (conservative collapse) default |

**Amber policy:** stay on Plan A but apply the cheapest knob (E1-B1 lower-effort granularity tweak; E2-B1
lower N; E5-B3 as a safe default) and re-measure on the next fixture iteration. Only **red** forces a branch.

## 0.7 Risk register — likelihood × impact, with a leading indicator (cheaper signal seen *before* the full run)

The leading indicators are computable from the **design-unit map + entry-reference graph alone** (no cascade
run needed) — so we get an early read at the *start* of STEP B, before the expensive scenarios execute.

| # | Likelihood | Impact if red | Leading indicator (compute early) | Early read meaning |
|---|-----------|---------------|-----------------------------------|--------------------|
| E1 | Low–Med | High (throttles releases) | max coding-tasks in any single design-unit | one fat unit ⇒ an edit there stalls a lot ⇒ pre-emptively split it |
| E2 | **Med–High** (dashboards are hubs) | High (task spam / wide rework) | in-degree of the most-referenced screen (the hub) in the entry-reference graph | high hub in-degree ⇒ expect wide cascades ⇒ pre-emptively consider E2-B3 |
| E3 | Low (and near-moot for 0.0.1) | Low (token cost only) | how often scribble approval changes screen count vs plan | frequent screen-count change ⇒ expect low salvage |
| E4 | **Med** (web↔Flutter gap) | High (release-stage surprise) | structural similarity of fixture entry-graph to 0.0.1's (hub in-degree, depth) | low similarity ⇒ fixture may not represent 0.0.1 ⇒ plan E4-B3 early |
| E5 | Low–Med | Med (wrong-wave assignment) | fraction of ACs the heuristic marks `both` | high `both` share ⇒ heuristic strained ⇒ default to E5-B3 |

**Read of the register:** the two to watch are **E2** (likely, because the fixture deliberately builds a
dashboard hub) and **E4** (the web↔Flutter fidelity gap from the Q2 decision). Both have a cheap leading
indicator we can compute at the *start* of STEP B — so we can pre-arm E2-B3 / E4-B3 instead of discovering
them late.

---

## E1 — Liveness/throughput under SCI

**Measure:** in the fixture's scripted mid-release edit (P-E), how far does the coding-task stall propagate?
Count: coding tasks blocked / total coding tasks in the release, and whether the block stays inside the edited
design-unit or crosses into others.

**Plan A (validates — stall stays local to the edited design-unit):** keep the per-design-unit hard SCI gate
exactly as designed. This is the expected case (per-design-unit scoping + facet split bound the blast radius).

**Trigger off Plan A:** a single edit blocks a large fraction of the release, or stalls cross unfold into
unrelated units.

**Alternatives:**
- **B1 — Finer gate granularity (per-screen, not per-design-unit).** *Pro:* maximal parallelism; only the
  screens actually touched stall. *Con:* more `after`-edges and book-keeping; the design-unit abstraction
  partly dissolves. *When:* if the stall is wide *because* design-units are coarse.
- **B2 — Soft-SCI / "provisional coding."** Allow a coding task to proceed against a stale scribble, but mark
  its output `provisional` and force a mandatory re-verify when the scribble refreshes. *Pro:* liveness — work
  never blocks. *Con:* surrenders SCI's core guarantee (no code written against a stale design); re-work risk
  if the refresh changes the design. This is a **philosophical fork** — SCI as hard invariant vs advisory.
  *When:* only if hard-SCI provably throttles real releases and the team accepts re-work risk.
- **B3 — Accept the serialization (do nothing).** *Pro:* keeps correctness absolute, zero new mechanism.
  *Con:* slow releases when edits are frequent. *When:* if releases are small enough that the stall is
  tolerable.

**Recommended branch order:** B1 first (cheap, keeps correctness), B2 only if B1 insufficient and liveness is
genuinely release-threatening. B3 is the null option if measurements show stalls are rare anyway.

---

## E2 — Cascade width / breaker N value

**Measure:** in the fixture's dashboard change (P-F), the per-hop dependent count and total wavefront width;
how often a refresh moves a dependent's *own* outward surface (the thing that propagates the wave).

**Plan A (validates — waves are narrow; most refreshes are entry-context-only and die out):** keep the lazy
per-hop wavefront + visited-set + two-stage breaker (N1=3/N2=7). Tune N to the observed width.

**Trigger off Plan A:** waves are consistently wide; refreshes routinely move outward surfaces so the wave
doesn't die; the breaker fires on normal edits (not just pathological ones).

**Alternatives:**
- **B1 — Lower N + earlier human escalation.** *Pro:* keeps a human in the loop on wide cascades; minimal
  change. *Con:* more developer interrupts. *When:* waves are wide but rare.
- **B2 — Bounded batch cascade.** Instead of per-hop task creation, compute the whole affected set at approval
  with one bounded BFS, and create a single consolidated refresh task. *Pro:* one review, fewer tasks, the
  developer sees the whole blast radius at once. *Con:* reintroduces a (bounded, one-shot) graph computation
  — the very thing the lazy wavefront avoided to dodge graph-rot; only safe because it is computed live and
  discarded. *When:* waves are wide *and* per-hop task spam is the main pain.
- **B3 — Re-cluster design-units.** If features cascade into each other constantly, the design-unit boundaries
  are wrong: merge the heavily-coupled features into ONE design-unit so the cascade becomes *intra-unit* and
  is handled inside a single scribble session (no cross-task wavefront at all). *Pro:* removes the cascade
  class entirely for those features. *Con:* larger scribble sessions (more tokens per session); the
  design-unit map must be re-derived. *When:* cascades cluster around a few hub features (e.g. the dashboard).

**Recommended branch order:** B3 is the most principled if the cascade concentrates on a hub (the dashboard
*is* a hub — strong candidate for "dashboard + its tightly-bound feature entries = one design-unit"); B2 if
cascades are diffuse; B1 as the always-available safety net.

---

## E3 — Presentation-code salvage rate  (low stakes for 0.0.1; matters for later releases)

**Measure:** when a quarantined Presentation-code task is re-derived post-scribble, what fraction of the
original decomposition survives (diff). *Note (from `11` A1):* for **0.0.1 this is nearly moot** — the
affected tasks are un-started `pending` (nothing to salvage, just blocked), and the bulk is already completed.
This empirical only bites on **future** releases that decompose Presentation-code blind and quarantine it.

**Plan A (validates — high salvage; scribbles rarely change a screen's existence):** keep
quarantine→re-derive→diff; the diff is cheap and the salvage saves tokens.

**Trigger off Plan A:** low salvage — scribbles routinely restructure screens/flows, so the old decomposition
is mostly discarded.

**Alternatives:**
- **B1 — Drop quarantine; delete-and-re-derive blind entries.** *Pro:* if salvage is low, the diff machinery
  isn't worth maintaining — just discard blind entries and derive fresh from the approved scribble. *Con:*
  loses any partial reuse. *When:* salvage measurably low.
- **B2 — Reframe low salvage as success, not failure.** Low salvage *validates the redesign's premise* — it
  means scribbles ARE catching design problems before code, which is the whole point. So a low number is a
  signal to tune the *process* (decompose Presentation-code later/less speculatively), not to add machinery.

**Recommended:** this barely branches the plan. Default to B1 if low; otherwise keep Plan A. Either way it
doesn't threaten the architecture.

---

## E4 — Fixture fidelity to the real P-F  (the release-stage risk worth most caution)

**Measure:** at STEP D, does 0.0.1's real reconcile surface cascade/staleness behaviours the fixture never
showed? Gap = fixture missed something real. Sharpened by the **tech-agnosticism risk**: the fixture is *web*
(Q2) and 0.0.1 is *Flutter* — a Flutter release's entry-surface coupling may differ from what the web fixture
exercised.

**Plan A (validates — fixture behaviour transfers to 0.0.1):** trust the workflow; STEP D reconcile proceeds
as a routine task-set reconcile (`11` A1).

**Trigger off Plan A:** STEP D exposes cascade or staleness behaviour the fixture never produced.

**Alternatives:**
- **B1 — Second, richer fixture iteration before trusting later releases.** *Pro:* cheap re-test of the
  specific behaviour that surprised us. *Con:* another fixture cycle. *When:* the surprise is a
  *generalisable* workflow gap.
- **B2 — Treat 0.0.1 as the real fixture: gated, observe-everything reconcile.** Run STEP D in a careful mode
  (small batch, full logging, human gate at each cascade) and tune the workflow on real data — effectively
  merging STEP C and D for 0.0.1. *Pro:* the most realistic validation possible; no synthetic-fidelity gap.
  *Con:* slower, higher-touch on the real release. *When:* the fixture proves structurally unable to
  reproduce a Flutter-specific behaviour.
- **B3 — Add a minimal Flutter fixture for the Flutter-specific behaviours.** *Pro:* directly closes the
  web↔Flutter gap. *Con:* a second fixture toolchain (the cost we deferred in Q2). *When:* the gap is
  specifically tech-binding-related (router/app-shell entry semantics), not general workflow.

**Recommended:** B2 is the pragmatic default (0.0.1 is small; gated reconcile is feasible and maximally real).
Escalate to B3 only if the gap is provably a Flutter-binding issue the web fixture *cannot* express — which
also feeds the tech-agnostic hand-off contract design (a useful by-product either way).

---

## E5 — AC facet-tagging accuracy

**Measure:** on the fixture's ACs, the mis-classification rate of the auto `{presentation|behaviour|both}`
heuristic (false-presentation over-serialises; false-behaviour under-covers the gate).

**Plan A (validates — high accuracy):** auto-tag + light human spot-check at the gate.

**Trigger off Plan A:** mis-tag rate high enough that wrong-wave assignment is common.

**Alternatives:**
- **B1 — Mandatory human confirmation of every facet tag at `requ-explore` time.** *Pro:* reliable. *Con:*
  developer effort on every AC. *When:* heuristic is unreliable but `both` is common (can't simplify away).
- **B2 — Make facet tagging a required manual field (no auto-guess).** *Pro:* no false confidence from a bad
  heuristic. *Con:* shifts all the work to authoring. *When:* the heuristic is worse than useless.
- **B3 — Conservative binary collapse.** Drop `both`; when ambiguous, default to `presentation` (i.e. it goes
  through the scribble/gate). *Pro:* fail-safe — ambiguity errs toward *more* design review, never less; kills
  the "define both" problem. *Con:* slightly over-serialises (some behaviour-only ACs ride through the gate
  needlessly). *When:* `both` turns out rare and the cost of over-inclusion is low.

**Recommended:** B3 is attractive — it converts a measurement risk into a safe default (ambiguity → more
review). Use B1 only if `both` is genuinely common and over-inclusion is too costly.

---

## Compound failure — when the *core model* pivots (not just a knob)

The branches above are mostly local knobs. Two compound outcomes would force a deeper rethink:

- **E1-wide AND E2-wide together** (mid-release edits stall widely *and* cascades fan out widely): this means
  the **per-design-unit gate is the wrong abstraction** — coupling is too dense for units to contain it. Pivot:
  either (a) **re-cluster aggressively** (E2-B3) until units are coupling-closed, or (b) **switch SCI from hard
  to soft** (E1-B2) and lean on provisional-code + mandatory re-verify. These are mutually reinforcing: dense
  coupling is exactly where a hard gate hurts most. This is the one scenario where the redesign's central
  invariant (SCI as a hard, per-unit gate) is genuinely in question — and the fixture is built to reveal it
  *before* 0.0.1.
- **E4-fail AND it's tech-binding-specific** (web fixture can't represent Flutter entry semantics): pivot to a
  dual-fixture validation (E4-B3) and treat the web/Flutter split as a first-class hand-off-contract concern —
  which also de-risks the eventual extraction (STEP E). Cost: the Q2 "defer Flutter fixture" decision partially
  reverses.

In both compound cases the **decision point is at the end of STEP C** (fixture validation review) — before any
0.0.1 commitment. That review is the natural gate to choose Plan A vs a pivot.

## Honest abort/rethink line

If, on the fixture, **hard-SCI cannot be made live even after re-clustering (E2-B3) and finer granularity
(E1-B1)**, and soft-SCI (E1-B2) is unacceptable on correctness grounds, then the scribble *hard gate* premise
itself is wrong for this codebase's coupling density — and the honest move is to revert to a **continuously-
enforced advisory** (scribbles always current, flagged when stale, but never *blocking* code) rather than a
gate. That is the true bottom of the design space; everything above tries to avoid reaching it, and the
fixture exists to tell us cheaply whether we have to.

## Branch reversibility & commit-by (one-way doors)

Not all branches are equal to back out of. Knowing which are one-way doors tells us which to defer longest.

| Branch | Reversible? | Why / commit-by |
|--------|-------------|-----------------|
| E1-B1 finer granularity | ✅ config | swappable gate-scope setting; revert anytime |
| **E1-B2 soft-SCI / provisional code** | ⚠️ **near one-way** | once code is written provisionally against stale designs, that code exists and the correctness contract is relaxed; reverting means re-auditing all provisional output. **Commit-by: only after E1-B1 exhausted, with explicit developer sign-off.** |
| E2-B1 lower N | ✅ config | threshold value; revert anytime |
| E2-B2 batch cascade | ✅ swappable | alternative algorithm behind the same detector interface |
| **E2-B3 re-cluster design-units** | ⚠️ costly-reversible | rewrites the design-unit map; everything downstream (gate scope, SCI edges, cascade neighbourhood) keys off it. Reversible but a full re-derive. **Commit-by: at STEP A/B when the map is first authored — cheapest to get right then.** |
| E3-B1 delete-and-re-derive | ✅ | per-task choice |
| E4-B2 0.0.1-as-fixture | ✅ process mode | a way of running STEP D, not a permanent change |
| **E4-B3 add Flutter fixture** | ➕ additive | new artifact + toolchain; reverses the Q2 "defer Flutter fixture" call. Reversible by abandonment but the toolchain cost is sunk. |
| E5-B3 binary collapse | ✅ | re-introduce `both` later; fail-safe meanwhile |

**Rule of thumb:** the only genuinely dangerous door is **E1-B2 (soft-SCI)** — it trades away the redesign's
core correctness guarantee. Everything else is config, swappable, or costly-but-reversible. So the design
should keep E1-B2 *possible* (a soft-SCI mode) but *gated behind sign-off*, never the silent default.

## Fixture instrumentation — what STEP B must emit to make these metrics measurable

"Measure on the fixture" is hand-wavy unless the fixture/workflow actually *emits* the numbers. These probes
must be **built into the fixture's requirements** — i.e. they are an explicit input to **TASK-PROC-066-03**
(the playground-requirements task), not an afterthought. The fixture is not just an app; it is an
**instrumented** app.

| Metric | Probe the workflow must emit | Where |
|--------|------------------------------|-------|
| E1 stall fraction + cross-unit leak | a **stall report** on the scripted mid-release edit: list of blocked coding tasks + each task's design-unit | SCI audit output / `release-finalize-impl` audit |
| E2 width + propagation ratio | a **cascade log** per origin: dependents touched per hop, visited-set, and per refresh a flag "did outward surface move?" | lazy-wavefront detector (PROP-10 integrity check) |
| E3 salvage fraction | the **quarantine→re-derive diff** persisted per re-derived task | `release-derive-code` |
| E4 surprise count | a **fixture-vs-0.0.1 behaviour log** at STEP D (which cascade/staleness behaviours were/weren't seen on the fixture) | STEP-D reconcile report |
| E5 mis-tag rate | a **facet-tag audit file**: auto-tag vs human-confirmed tag per AC | `requ-explore` / decomposition |
| Leading indicators (all) | a **graph-stats dump**: per-unit coding-task count, entry-graph hub in-degree, `both`-tag share | computed from the design-unit map + entry-reference graph at the *start* of STEP B |

**Action:** add an AC to TASK-PROC-066-03's eventual requirements — *"the playground and the workflow run
against it MUST emit the six measurement artifacts above"* — so the empirical questions are answerable by
construction, not by manual archaeology.

## Branch interactions (don't pull two levers that fight)

- **E1-B1 (finer granularity) vs E2-B3 (re-cluster coarser):** opposite directions on granularity. If *both*
  go red (the compound case), **prefer E2-B3** — in densely-coupled space, splitting finer just multiplies
  `after`-edges and cascade hops, whereas re-clustering makes the coupling *intra-unit* and removes it from the
  cross-task machinery entirely. Do not do both at once.
- **E1-B2 (soft-SCI) softens E2's urgency:** if code never blocks (provisional), cascade *width* stops
  threatening liveness — but at the correctness cost E1-B2 carries. So E1-B2 partially substitutes for E2
  work; don't invest in heavy E2 machinery *and* adopt soft-SCI.
- **E4-B3 (Flutter fixture) feeds STEP E:** building it is also the tech-agnostic hand-off-contract work the
  extraction needs — so if forced, scope it to double as extraction input, not throwaway.

## Decision points (summary)

| When | Review | Choose |
|------|--------|--------|
| **Start of STEP B** | Leading-indicator read (graph stats, no run needed) | pre-arm E2-B3 / E4-B3 if hub in-degree / low fixture-0.0.1 similarity already flag them |
| End of STEP C | Fixture validation review (against §0.6 pre-registered thresholds) | Plan A vs E1/E2/E5 branches; compound-failure pivot check; **E1-B2 only with sign-off** |
| During STEP D | Real 0.0.1 reconcile | E3 (salvage) + E4 (fidelity) branches |
| Before STEP E | Extraction readiness | whether E4-B3 (web↔Flutter) forced dual-fixture / hand-off-contract work |
