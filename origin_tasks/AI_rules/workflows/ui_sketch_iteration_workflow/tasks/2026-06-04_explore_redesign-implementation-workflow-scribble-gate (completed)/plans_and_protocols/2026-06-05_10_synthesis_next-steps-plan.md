# Synthesis & Recommended Next Steps — after the 2026-06-05 feedback round

Task: TASK-PROC-032-29. Date: 2026-06-05.
This is the second-level synthesis the developer asked for ("create another document that synthesizes again:
i want a plan that recommends next steps"). It folds in the five topic reports (`05`–`09`), the two confirmed
decisions, and the full substrate (Round-1 synthesis `02` + eval Round-1/Round-2 records), and converts them
into an ordered plan with explicit developer decision points.

---

## 1. The one insight that reorders everything

The feedback contains **two coupled questions disguised as five separate ones**:

- **T1** asks *how* to migrate 0.0.1 to the new workflow.
- **T2** asks *whether to build a cheap test vehicle (and/or extract the factory) first*.

These are the same decision seen twice: **where does the redesigned workflow make its first real run?**
Three candidates — and they are mutually exclusive as a *first* target:

1. **Straight onto 0.0.1** (migrate the real release). Highest stakes, highest token cost per iteration,
   debugs the workflow and the release simultaneously.
2. **On a cheap, coupling-rich fixture first**, then migrate 0.0.1 with a *known-good* workflow. (Recommended.)
3. **Behind a full factory extraction** (T2's literal proposal). Inverts urgency (extraction is U2; this
   redesign is U4-BLOCKING) and extracts a moving target.

Everything else in the feedback (T3 recursion, T4 domain-first, T5 encapsulation) are *refinements to the
design* that are true regardless of which target is chosen. So the plan is: **lock the design refinements,
then make the one sequencing call, then execute in the order that call implies.**

## 2. Verdicts carried from the topic reports (the settled design refinements)

| Topic | Verdict (what to build) | Report |
|-------|-------------------------|--------|
| **T3 — recursion** | L3 no-recursion is safe **iff** a coverage assertion holds (recursion lives in the task graph). Add the assertion. L5 is *recursive* — add a **width circuit-breaker** (escalate at N dependents), honouring PROP-10's "bounded recovery." Three depth-1 guards (G3/L3 forbid; L5 allows) — don't conflate. | `07` |
| **T4 — domain-first** | Add a **third layer**: domain-code → design → presentation-code. Mechanism is two-part: **(floor)** data-bound Presentation requirements carry a precise data-point definition before their scribble; **(conditional)** a soft-pref/`after` edge from data-bound scribble → its design-unit's domain task. Not universal. | `08` |
| **T5 — encapsulation** | Principle: **tokens win unless clarity loss risks correctness** (D-0 is the proof of the exception). Make "encapsulated enough" the **artifact-in→artifact-out registry test**. Standardise a **skill-design trade-off record** as an AC in REQ-PROC-035/058; write the records for the redesign's cuts. | `09` |
| **D-2** | Gate scope = **per-design-unit** — confirmed. | — |
| **D-3** | Names `begin → derive-code → finalize` confirmed; `task-start` wrapper is a **separate task**, out of scope here. | — |

These fold into the Round-1 §8 change-list and its S1→S4 staging without restructuring it — they *add* ACs,
they don't move the spine.

## 3. The recommended sequence

**Recommendation: candidate (2) — fixture-first.** Rationale in `06`: cheap iteration is strategically
dominant when many iterations are expected (the goal itself says "a single pass will not be enough"); a
validated workflow makes the 0.0.1 migration low-risk; full extraction is deferred (don't extract a moving
target, don't invert urgency).

```
STEP 0  (now)  — this synthesis + developer decisions §4               [no code]
                  ↓
STEP A         — Finalize the redesign REQUIREMENTS (requ-explore)     [cheap, no code]
                  S1: REQ-PROC-035/-058 — two-wave split + scribble gate + release-derive-code
                      + skill-design trade-off-record AC (T5)
                  S2: REQ-PROC-032 — SCI + loopback-as-task + lazy-wavefront cascade
                      + L3 coverage assertion + L5 width-breaker (T3)
                      + entry-context spine (PROP-8) + coverage/ordering (PROP-9/11)
                      + domain→design layer & data-bound edge (T4)
                  S3: generator carrier-format change (comment-leak fix + PROP-1 + findings overlay)
                  S4: PROP-14 flow viewer  [gated on the dependency-admission decision D-5]
                  ↓
STEP B         — Build the cheap, COUPLING-RICH test fixture            [decision §4-Q2]
                  Engineered to fire P-E (mid-release edit) and P-F (cross-feature cascade):
                  a tiny consumer with a shared dashboard/entry surface + 2-3 dependent feature
                  screens + one validation-heavy form (to also test T4) + a scripted mid-stream edit.
                  Job = validate the redesign, NOT be a product.
                  ↓
STEP C         — Implement the redesigned skills, validating each on the fixture  [cheap iterations]
                  Order within: S1 (structural spine) → S2 (consistency layer) → S3 (∥) → S4 (last).
                  Fix D-0 (the ui-create-scribble routing bug) as the very first concrete change.
                  ↓
STEP D         — Migrate 0.0.1 via SCI-audit RECONCILE (not delete-all)  [now low-risk]
                  scripts/release/migrate_plan_to_two_wave.py: classify entries →
                  keep scribble + pure-domain → coverage-report the missing scribbles →
                  quarantine blind presentation-code on SCI edges → developer sign-off report.
                  ↓
STEP E  (later) — Factory extraction (TASK-PROC-066-01)                  [DEFERRED]
                  Extract a known-good factory. The fixture from B informs tech-agnosticism;
                  the factory/project boundary labels accumulated during C feed 066-01.
```

### Why this order and not the developer's literal proposal
- **Extraction is deferred, not dropped.** It is real and valuable, but doing it *first* (T2's literal
  framing) inverts urgency and forces re-editing extracted artifacts as the redesign lands. After C, the
  factory is stable and extraction extracts a known-good thing. (`06` §Level-1.)
- **The fixture replaces "movie-rating app" with "coupling-rich fixture."** A "less complicated" app risks
  being too flat to fire P-E/P-F — the exact mechanisms the redesign exists for. The fixture's complexity must
  live in its *couplings*, not its feature count. (`06` §"the non-obvious move".)
- **0.0.1 migration moves to the end and becomes a reconcile.** Debuting on 0.0.1 (candidate 1) means
  debugging the workflow and the release at once; doing it after C means a validated workflow + a scripted
  reconcile that *keeps* valid work instead of the token-heavy delete-all. (`05`.)

## 4. Decisions the developer still owns (framed to decide)

**Q1 — Sequencing (the load-bearing call).** → **DECIDED 2026-06-05: candidate (2), fixture-first.** Build a
coupling-rich test fixture, validate the redesigned skills on it, then migrate 0.0.1 via SCI-reconcile;
extraction (STEP E) follows. The plan executes in STEP A → B → C → D order.

**Q2 — Fixture technology.** → **DECIDED 2026-06-05: web (React/Angular).**
*Implication that must now be carried (the lean in `06` was "web only if extraction is imminent"):* choosing
a **web** fixture means **tech-agnosticism is in scope now, not deferred to STEP E.** Concretely this changes
two things upstream:
  1. **The scribble→code hand-off contract (S1/§6 of `02`) must be authored tech-agnostically from the start**
     — `flutter_handoff.yaml` splits into *design-intent* (tech-neutral) + a *target-binding* layer
     (Flutter widgets OR React/Angular components). The web fixture is the forcing function that gets this
     contract right; do not let it stay Flutter-shaped.
  2. **The factory/project boundary labelling (the STEP-E feeder) becomes a STEP-A/C deliverable, not a
     by-product** — every new/changed skill must be labelled factory-vs-project as it is designed, because the
     web fixture is effectively a second consumer project and will immediately expose any Flutter-coupling in
     the "factory" skills. This pulls part of TASK-PROC-066-01's boundary work earlier (coordinate, don't
     duplicate).
  3. **Cost note (`06`):** the web fixture adds a toolchain + a `doc/` surface the factory lacks for web
     (lint/test/build gates, web architecture guidelines). Budget this into STEP B; it is the price of
     proving tech-agnosticism now. Keep the fixture minimal in feature count to contain it.

**Q3 — T4 data-point definition home.** Precise data-point definitions for data-bound forms live in the
**requirement** (clean RE-DERIVE separation; scribble reads the spec) vs. require the **domain code** first
(adds a domain-code→scribble staleness edge SCI must then model). *Lean: structured data-point table in the
requirement, code-first only for discovery-heavy domains.* (`08`.)

**Q4 — T5 trade-off-record scope.** Adopt the skill-design trade-off record as an AC, required only for
*fused-responsibility* skills (single-responsibility skills carry just the one-sentence statement)? *Lean:
yes, fused-only, to avoid boilerplate.* (`09`.)

**Q5 — L5 width-breaker threshold N.** Accept that N is a guess until a real cascade runs (the fixture in
STEP B is designed to produce one and measure it)? The *breaker's existence* is the safety guarantee; the
*value* is tunable. (`07`.)

**Carried forward unchanged from Round-1 §9:** D-1 (confirm the bisection as a hard requirement), D-4 (SCI
generative-blocks/referential-flags table, esp. whether `ui-verify-flutter` hard-blocks on a stale scribble),
D-5 (PROP-14 Markdown→HTML dependency-admission), D-6 (accept the S1→S4 staging).

## 5. Honest statement of what is still uncertain
- **Fixture fidelity (the biggest risk in the plan).** A minimal fixture may be *too* minimal to reproduce
  P-F faithfully — giving false confidence. Mitigation: model the fixture on the *actual* 0.0.1
  dashboard→feature dependency so it is minimal but representative. If even that under-represents the real
  cascade, STEP D will surface gaps the fixture missed — accept this as residual risk, not a plan defect.
- **Net token economics of fixture-first** depend on iteration count: large per-run saving, but a fixed
  fixture-setup cost (and, for a web fixture, ongoing toolchain maintenance). Pays off iff we genuinely
  iterate — which the design's own "single pass won't be enough" predicts.
- **0.0.1 activation state** (STEP D): if the release is already activated with a live orchestration chain,
  the reconcile is more delicate than the plan-only case and needs its own mini-design (`05` residual).
- **SCI rot-graph completeness:** T4 adds a domain-code→scribble edge and T5's registry test may need
  extending to model `task_type` routing contracts (the D-0 locus). Both are "specify carefully in S1/S2,"
  not blockers.
- All Round-1 §10 residuals stand (liveness under SCI; cascade width unmeasured; `--scope` clean
  separability; flutter_handoff.yaml sufficiency).

## 6. Acceptance-criteria status for this task (goal.md)
- [x] At least one synthesis round — Round-1 (`02`) + this feedback round (`04`–`10`).
- [x] Defines the problem space in terms not known at creation — the **single-sequencing-decision** reframing
  of T1+T2 (§1); the **domain→design→presentation-code third layer** (T4); the **tokens-win-unless-correctness**
  bounded principle + artifact-registry encapsulation test (T5); the **three-depth-1-guards** distinction and
  the **L3 coverage-assertion / L5 width-breaker** split (T3).
- [x] Decisions requiring user input identified and framed — §4 Q1–Q5 + carried D-1/D-4/D-5/D-6.
- [x] Honest about what remains uncertain — §5.
- [x] **The user has approved the final synthesis and stated what to do next** — 2026-06-05: Q1 = fixture-first,
  Q2 = web (React/Angular). Next step = **STEP A** (finalize the redesign requirements via `requ-explore`,
  S1→S4), with the tech-agnostic hand-off contract and factory/project boundary labelling pulled in per §4-Q2.
- [ ] **The next step stated by the user was performed** — STEP A not yet kicked off (developer stepped away
  / "brb"); awaiting go-ahead to start the S1 `requ-explore` work. Q3/Q4/Q5 + carried D-1/D-4/D-5/D-6 should
  be resolved at the head of STEP A.
