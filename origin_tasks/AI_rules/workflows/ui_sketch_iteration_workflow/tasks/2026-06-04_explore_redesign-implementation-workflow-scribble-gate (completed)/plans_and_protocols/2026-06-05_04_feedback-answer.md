# Feedback Answer — direct responses to 2026-06-05_03_feedback.md

Task: TASK-PROC-032-29. Date: 2026-06-05. Responds point-by-point to the developer's feedback on the
Round-1 synthesis (`2026-06-04_02_round_1_synthesis.md`). Each point is answered crisply here; the
*systematic two-level back-pressure* the developer requested lives in the per-topic reports
(`05`–`09`), and the recommended sequencing lives in `10_synthesis_next-steps-plan.md`.

The five open topics, the two confirmed decisions, and where each is handled:

| # | Feedback topic | Verdict in one line | Deep report |
|---|----------------|---------------------|-------------|
| T1 | Migrating the existing 0.0.1 tasks | Don't delete-all-and-rerun. The redesign already contains the migration tool (the SCI audit) — reconcile, don't rebuild. | `05` |
| T2 | Do factory-extraction + a test playground first? | Split the two motives. A *cheap test vehicle* is high-value and should come first; *full extraction* should not — it inverts urgency and extracts a moving target. | `06` |
| T3 | Is forbidding recursion at L3 (and L5) safe? | L3: safe **iff** coverage is complete — the recursion lives in the task graph, not the single check. L5 is **not** the same — it *is* recursive; it needs a width breaker, not a depth rule. | `07` |
| T4 | Build domain entities before scribbles? | Yes, but **conditionally** (only data-bound scribbles) and the floor is requirement-precision, not code. This adds a third layer: domain → design → presentation-code. | `08` |
| T5 | Encapsulation/single-responsibility vs token-efficiency, made explicit | Tokens win **except where the encapsulation loss creates correctness risk** (D-0 is the proof it already did). Standardise a skill-design trade-off record as an AC. | `09` |
| D-2 | Gate scope = per-design-unit | **Confirmed by developer.** Folded in as settled. | — |
| D-3 | Skill names + task-start wrapper | **Confirmed.** Names approved; the `task-start` wrapper over `claude-route` is its own task — removed from this redesign's scope. | — |

---

## T1 — "How do we migrate the existing 0.0.1 tasks? Delete all and re-run? Costs a lot of tokens."

**Short answer: no delete-all.** The "delete everything and re-run `release-begin-impl`" option is a false
dichotomy — it destroys work the *new* model would itself have produced (pure-domain coding tasks are valid
under the new model; they are created in Wave 1), and it pays full re-decomposition tokens to rediscover
that. There is a third option, and the redesign already built the tool for it:

- The redesign's **SCI audit** (`§4.2` of Round-1) is exactly a detector for "which existing coding tasks
  were authored blind to a scribble." Run it against the *existing* 0.0.1 plan and it tells you precisely
  which entries are invalid — not "all of them."
- The **per-design-unit** scope you just confirmed (D-2) means salvage is unit-by-unit: pure-domain units
  keep their coding tasks wholesale; only Presentation units whose code was decomposed before any scribble
  are quarantined.
- The **flow→scribble coverage report** (PROP-9) answers your "we can't be sure enough scribble tasks exist"
  directly — it lists the missing scribble tasks for 0.0.1 as a gap report, cheaply.

So migration = **a one-time scripted reconcile**, not a re-run. But there is a prior question that T2 raises:
*should 0.0.1 be the workflow's debut at all?* See `05` and `10`.

## T2 — "Do the factory-extraction first (huge effort)? Build a movie/book-rating web app as a test playground?"

I think you are right about the *need* and I want to push back on the *means*. The proposal bundles two
separable motives:

1. **"develop the factory skills on a much better level"** — via full extraction into its own repo.
2. **"a mechanism that lets us test them" cheaply** — via a small offline web app.

These come apart. You can have (2) without (1). A cheap test vehicle does **not** require multi-repo
extraction; extraction has its own large unknowns (plugin mechanism, CLAUDE.md composition, update channel)
and a dependency chain (`TASK-PROC-066-01 after TASK-PROC-066-02`, the Ralph-loop study). Putting extraction
first inverts urgency: the scribble-gate redesign is **U4-BLOCKING**; extraction is **U2-PROC-IMPROVEMENT**.
And it extracts a *moving target* — the workflow we are still redesigning. Stabilise-then-extract.

Two sharper points (full argument in `06`):
- **A "less complicated" playground is the wrong playground.** A simple offline movie-rating app may be too
  simple to trigger the exact mechanisms the redesign exists to test — the cross-feature UI cascade (P-F,
  the dashboard case) and the mid-release requirement edit (P-E). If the fixture can't exercise SCI and the
  lazy-wavefront cascade, it validates the easy 80% and misses the 20% that motivated all this.
- **The right test vehicle is small in tokens but rich in couplings.** Recommendation: a minimal fixture —
  possibly not a full app, just 3–4 toy requirements that *share a flow and an entry surface* and a scripted
  mid-stream edit — engineered to fire P-E and P-F on purpose.

**Net recommendation:** build the cheap test vehicle **first** (before rolling onto 0.0.1); defer full
extraction until the workflow is validated. Detail and the decision framing in `10`.

## T3 — "Seam owner is depth-1, the source check does not recurse — is it safe to forbid recursion? (also L5)"

Two different questions hide in this one sentence, and they have *different* answers:

- **L3 (forbids recursion): safe — but conditionally.** The single source-check doesn't recurse, but the
  recursion isn't gone; it lives **at the task-graph level**. Every Presentation requirement gets its own
  scribble and its own depth-1 source-check, so a transitive gap (A needs an entry B owns, B's definition
  depends on C) is caught when *C's own* scribble runs. Depth-1-per-task × universal-coverage = transitive
  closure across tasks. This is safe **iff** coverage is complete (PROP-9). If some Presentation requirement
  has no source-check, forbidding recursion leaves a real hole. → Make the coverage guarantee an explicit
  asserted precondition of the no-recursion rule.
- **L5 (cascade) is NOT the same and does NOT forbid recursion.** The lazy-wavefront cascade *is* recursive —
  it advances hop-by-hop across approvals, bounded by a visited-set. Lumping it with L3 is the trap. Its open
  question isn't "is depth-1 enough"; it's **termination + blast-radius**. The visited-set already guarantees
  no infinite loop; the unmeasured part is *wave width*. → Add a width circuit-breaker (escalate at N
  dependents), exactly as PROP-10 says "bounded recovery, never unbounded auto-create."

Full reasoning in `07`.

## T4 — "Would scribble creation be easier if the domain entities already existed? (complex form with many validated fields)"

Yes — and this is a good catch that *sharpens* the design rather than contradicting it. The scribble gate
sits between **design and Presentation-code**, not between domain-code and design. Domain code is upstream of
both. So your instinct gives a clean three-layer ordering that doesn't break the gate:

> **domain-code → design (scribble) → presentation-code**

But two refinements (full argument in `08`):
- **Conditional, not universal.** Only scribbles that depict *data-bound* UI (forms, validation, lists of
  domain entities) benefit. A navigational screen or a confirmation dialog gains nothing — forcing
  domain-before-scribble everywhere re-introduces the serialisation cost the per-design-unit gate exists to
  avoid.
- **The floor is requirement-precision, not code.** Often what the scribble author needs is a *precise
  definition* of the data points (names, types, validation rules) — which belongs in the **requirement**, and
  exists before any code. If a "complex form" is painful to scribble, the first question is whether the
  requirement defined the data model precisely enough. Code-first is the *secondary* mechanism, for genuinely
  complex domains where constraints are only discovered in implementation.

Concretely: add a **conditional ordering edge** — a data-bound scribble task gets an `after` (or soft-pref)
edge on the domain task(s) of its design-unit — and a requirement-completeness expectation that data-bound
Presentation requirements carry a precise data-point definition before the scribble runs.

## T5 — "Are the skill phases encapsulated enough / single-responsibility? Token-efficiency is more important — but make the trade-off explicit in the requirement."

Agreed on the principle, with one correction to "token-efficiency is more important": it wins **except where
the encapsulation loss creates a correctness risk** — and we already have proof it can. D-0 (the
`create_orchestration_task.py` L276 routing string `ui-create-scribble` that matches no real skill) is an
encapsulation/clarity failure that went undetected. So the rule is *tokens win unless clarity loss risks
correctness*, not *tokens always win*.

Concretely (full argument in `09`):
- The weakest seam in the redesign is `task-derive-from-requ` gaining a `--scope {presentation,code}` flag —
  a `--scope` flag is the classic "two skills hiding in one coat" smell. Here token-efficiency genuinely
  favours one skill (shared requirement-read + plan-format machinery), so keep it one skill — but **record
  the trade-off**.
- Propose a standardised **skill-design trade-off record** (an AC in REQ-PROC-035), analogous to the existing
  `vcd-log-tradeoff` for persona-value conflicts: every skill states its single responsibility in one
  sentence; where it carries more for token reasons, the requirement records *what encapsulation was
  sacrificed and why tokens won*. Make it auditable against `.factory/registry/artifacts.yaml` (every skill
  maps artifacts-in → artifacts-out).

## D-2 / D-3 — confirmed, folded in

- **D-2 (gate scope = per-design-unit):** accepted as settled. All consistency mechanisms (SCI edges,
  cascade neighbourhood) already assume the design-unit map; nothing changes.
- **D-3 (names + task-start):** `release-begin-impl → [gate] → release-derive-code → release-finalize-impl`
  accepted. The `task-start`-wraps-`claude-route` work is a **separate task** (developer: "consider it done")
  and is **removed from this redesign's scope** — Round-1 §8's last table row and D-3's second clause no
  longer apply here.

---

### What this answer changes about the Round-1 synthesis
1. Adds a **migration model** for 0.0.1 (reconcile-not-rebuild) that Round-1 didn't cover (clean-rerun-decision
   only covered the *pilot* artifacts, not the whole release). → `05`.
2. Adds a **sequencing recommendation** (cheap test vehicle before 0.0.1; extraction deferred) that reframes
   *where* the redesign first runs. → `06`, `10`.
3. Hardens L3 with an **explicit coverage precondition** and separates L5 with a **width breaker**. → `07`.
4. Adds a **third ordering layer** (domain → design → presentation-code) with a conditional edge. → `08`.
5. Adds a **skill-design trade-off record** as a first-class, auditable requirement artifact. → `09`.
