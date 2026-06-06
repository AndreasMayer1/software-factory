# Back-pressure report — T2: do factory-extraction + a test playground first?

Task: TASK-PROC-032-29. Date: 2026-06-05.
Developer's words: *"should we do …factory_extraction…goal.md first (which is a huge effort) but it would
also allow us to develop the factory skills on a much better level and also would allow us to create a
mechanism that allows us to test them. i would suggest to create a simple angular/react web app for example
a personal movie rating app (only offline …) that is the testing playground. less complicated and much less
token costs per skill workflow run."*

Grounded against `TASK-PROC-066-01` (the extraction explore task): it is `status: pending`, effort **L**,
urgency **U2-PROC-IMPROVEMENT**, and `after: [TASK-PROC-066-02]` (a Ralph-loop study). This redesign task is
urgency **U4-BLOCKING**. The asymmetry matters and is used below.

---

## Level 1 — the topic as a whole

### The rationale being pressured
*"Extract the factory first → we develop the skills at a better level and get a cheap test playground (a
small web app) → each workflow run costs far fewer tokens → we iterate the redesign cheaply."*

This is two claims welded together: **(A)** full extraction makes the skills better, and **(B)** a small
consumer app is a cheap test vehicle. They must be evaluated separately because they have opposite
cost/risk profiles.

### What speaks against it — claim A (extract first)
1. **Urgency inversion.** Extraction is U2 and L-effort with a hard predecessor (Ralph-loop study). The
   scribble-gate redesign is U4-BLOCKING. Sequencing the blocking item *behind* a larger non-blocking item
   is a scheduling anti-pattern — it maximises time-to-value-at-risk.
2. **Extracting a moving target.** The factory's *content* is what this redesign is changing (new skills,
   renamed skills, new orchestration terminal, new audits). Extract now and you immediately re-edit the
   extracted artifacts — paying the extraction cost twice (once to move, once to change). The extraction
   task's own Seed 5 ("ordering dilemma") already worries about commuting with *one* restructuring; adding a
   live workflow redesign on top makes the merge worse, not better.
3. **Extraction has independent large unknowns** (its own Seeds 2–7: CLAUDE.md composition, plugin
   capabilities, update channel, tech-agnostic config). None of these block the redesign. Front-loading them
   front-loads risk that is orthogonal to the problem at hand.
4. **"Better level" is partly circular.** You cannot extract a *good* factory until the workflow it encodes
   is good. The redesign is the thing that makes the workflow good. So "extract to make skills better" has
   the dependency backwards: **stabilise the workflow, then extract a known-good factory.**

### What speaks *for* it — and must be conceded
1. **The cheap-iteration argument (claim B) is genuinely strong.** Iterating the redesign against the real
   Flutter app means a full real release decomposition per run — very expensive. A toy consumer is 10–100×
   cheaper per loop. If we expect *many* redesign iterations (the goal itself says "a single pass will not be
   enough"), cheap iteration is strategically dominant.
2. **Extraction would force the factory/project boundary** — and that boundary is exactly what is fuzzy in
   the redesign (is `release-derive-code` factory or project? the scribble gate? the SCI audit? — clearly
   factory). Clarifying it would de-risk the redesign's own AC-anchoring (which spans REQ-PROC-032/035/058).
3. **A web (React/Angular) consumer stress-tests technology-agnosticism.** The scribble workflow currently
   terminates in `flutter_handoff.yaml`. If it must also serve a React app, the handoff contract is forced to
   separate "design intent" from "Flutter widget mapping" — which is the *right* shape and which the
   redesign's §6 hand-off model would otherwise leave Flutter-shaped by default.

### How to do it differently
**Decouple A from B.** Claim B's value (cheap iteration) does **not** require claim A (multi-repo
extraction). You can get a cheap test vehicle *inside this repo* with none of extraction's unknowns:

- **A minimal in-repo fixture release** — a handful of toy requirements under a sandbox path, run through
  the real skills, deleted/reset freely. No new repo, no CLAUDE.md split, no distribution mechanism.
- The vehicle's job is *validation of the redesign*, not *being a product*. It does not need personas,
  market research, or a real domain — it needs the *structural couplings* the redesign must handle.

### How to improve it — the non-obvious move
**A "less complicated" playground is the wrong playground.** This is the key push-back. The whole reason the
redesign exists is to handle the *hard* cases:
- **P-F** — cross-feature UI cascade (the dashboard whose interaction model changes and ripples into every
  feature that shows data on it),
- **P-E** — mid-release requirement edit invalidating an approved scribble,
- deep flow coupling / shared entry surfaces (the design-unit notion itself).

A "simple offline movie-rating app" risks being too flat to contain any of these. If the fixture can't fire
SCI re-violation or the lazy-wavefront cascade, you validate the easy 80% of the redesign and never touch the
20% that motivated it — and you'd discover the gaps later, on 0.0.1, at full cost. **So the fixture must be
small in tokens but deliberately rich in couplings:**

> Engineer the fixture *to trigger P-E and P-F on purpose* — e.g. a tiny app with a "home dashboard" screen
> that 2–3 feature screens draw entry from (shared entry surface → forces the design-unit map and the L5
> cascade), plus a scripted mid-stream edit to one requirement (forces SCI + the scribble-refresh L6 path).
> That is ~4–5 requirements, not a product.

If a *movie/book-rating* framing makes the fixture easier to reason about, fine — but the acceptance test for
the fixture is "does it exercise the cascade and the stale-scribble path," not "is it a believable app."

### Net position
- **Do (B-minimal) first:** a cheap, coupling-rich test vehicle, before rolling the redesign onto 0.0.1.
- **Defer (A):** full extraction comes *after* the redesigned workflow is validated — extract a known-good
  factory. The fixture built for (B) can later *inform* extraction's tech-agnosticism work, but does not
  block it and is not blocked by it.
- This also de-risks T1: 0.0.1 gets migrated by a *validated* workflow, not a debuting one.

---

## Level 2 — chapter by chapter

### "do the factory_extraction first (which is a huge effort)"
- **Pressure:** "huge effort" + U2 + hard predecessor (066-02) vs. a U4-BLOCKING redesign = inverted
  scheduling. Also extracts a target the redesign is actively moving.
- **Verdict:** no. Defer extraction; do not gate the redesign on it.

### "it would allow us to develop the factory skills on a much better level"
- **Pressure:** circular — the redesign is what makes the skills good; extraction can't precede the thing it
  would extract well. Boundary-clarification value is real but obtainable incrementally (label each new/
  changed skill factory-vs-project as you design it, feeding 066-01 later) without extracting now.
- **Verdict:** capture the boundary labels as a by-product of this redesign; hand them to 066-01. Don't
  extract.

### "create a mechanism that allows us to test them"
- **Pressure:** strongly agree with the *need*; reject the claim that extraction is its prerequisite. A test
  mechanism is an in-repo fixture + reset script, not a repo split.
- **Verdict:** yes to a test mechanism, now, in-repo.

### "a simple angular/react web app … personal movie rating app (offline)"
- **Pressure, three threads:**
  - *Tech choice (React/Angular):* upside = forces tech-agnostic handoff; downside = a whole new toolchain,
    quality gates, and `doc/` surface the factory doesn't yet have for web. Big new maintenance surface for a
    test fixture.
  - *"simple/offline":* the danger flagged above — too simple to exercise P-E/P-F. **The fixture's
    complexity must live in its couplings, not its feature count.**
  - *"a whole app":* even a toy app needs the full top-down chain (flow → requirement → scribble) authored
    before one scribble runs — non-trivial fixed setup cost that the "much less token cost" claim omits.
- **Verdict:** prefer the **smallest fixture that triggers the cascades**, framed as a movie/book app only if
  that aids reasoning. Decide Flutter-fixture-in-repo (cheapest, no new toolchain, but doesn't test
  tech-agnosticism) vs. web-fixture (tests agnosticism, new surface) — this is a developer decision; see
  `10` and the closing question.

### "less complicated and much less token costs per skill workflow run"
- **Pressure:** *per-run* cost is genuinely much lower — true and important. But there is a *fixed* setup
  cost (authoring the fixture's flows/requirements) and, for a web app, an ongoing maintenance cost (second
  toolchain). Net saving = (per-run saving × number of iterations) − fixed setup − maintenance. It pays off
  precisely because we expect many iterations.
- **Verdict:** the economics favour a fixture **iff** it stays minimal (low fixed cost) and we genuinely
  iterate. Keep it minimal; resist it growing into a product.

---

## Residual uncertainty (honest)
- **Flutter-fixture vs. web-fixture is a real fork with no dominant answer.** A Flutter fixture is cheapest
  and reuses all existing gates but cannot test the tech-agnostic handoff (which only matters if extraction
  is actually coming). A web fixture tests agnosticism but adds a toolchain the factory must then support.
  Choosing depends on how committed the extraction goal is — which is itself the thing we're deferring.
  Circular enough that it needs the developer's call (`10`, closing question).
- **Whether a minimal fixture can *faithfully* reproduce P-F** is unproven — the dashboard cascade may need a
  certain amount of real feature richness before the entry-surface coupling behaves like the real case. If
  the minimal fixture is too minimal, it gives false confidence. Mitigation: design the fixture against the
  *actual* 0.0.1 cascade shape (use a real dashboard→feature dependency as the template), so it's minimal but
  representative.
- **Sequencing risk if the developer wants extraction soon regardless:** if extraction is imminent for
  reasons outside this redesign, doing the redesign first means re-touching extracted artifacts. The
  recommendation assumes extraction is genuinely deferrable; if it is not, the boundary-labelling by-product
  becomes load-bearing and should be elevated from "by-product" to an explicit deliverable.
