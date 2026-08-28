# Blindspot register — adversarial critique of the capability-testing concept (r3)

Task TASK-PROC-068-01. Written as a deliberate self-attack on
`…_04_synthesis-r3_capability-testing-consolidated.md`: are the *right* problems solved, are *all*
problems in the space solved, and what can the concept structurally not see? Ranked by severity.
Each item marks whether it is **inherent** (a limit to state honestly), **absorbable** (add a
mechanism), or a **framing decision** (the developer's to make).

---

## Tier 1 — Fundamental blindspots (the concept cannot see these as framed)

### B1. Quis custodiet — the judge has no oracle (partly absorbable; partly inherent)
L2/L3/L4 are all open-ended LLM judgments. The concept supplies an oracle for *capabilities* but
**no oracle for the judges**. Inter-judge spot-checks catch *variance* but not *systematic bias*
(all judges share a wrong anchor and confidently agree). The whole edifice can be precisely,
reproducibly wrong. skill-creator's false-confidence guard names the symptom, not the cure.
- **Missing mechanism:** a small **human-graded calibration set** (gold judgments) the judge is
  periodically scored against, + a human audit cadence on judge outputs. Without it the test's own
  quality is unmeasured — the regress the concept was meant to end just moves up one level.

### B2. Conformance ≠ good method (largely inherent)
L1 process-conformance and the I-archetype check "did the capability do what *its own
SKILL.md/goal* says." The source of truth for "the stated method" is the artifact itself. So a
capability that **faithfully executes a bad method scores perfectly.** Method *soundness* (is the
method good?) is neither content (human at gate) nor conformance (L1) — it falls in a gap. Old-vs-new
A/B only catches it *if a human proposes the better method*. **The thing we hoped to reduce —
reliance on human authoring judgment for whether the method is right — is exactly what still
carries method-soundness.** Honest limit: the test raises the floor (no *unfaithful* execution, no
*self-inconsistent* output) but cannot certify the method is the right one.

### B3. Construct validity — toy-fixture pass may not predict real-capability good (partly inherent)
Fixtures are deliberately minimal ("enough to fire the couplings, not a believable product"). There
is **no check that passing the capability test predicts good behaviour on a real, messy release
problem.** The release-cascade has a fixture↔release fidelity probe (#4); capability *quality* has
no analogue. We may be optimising capabilities to pass a toy that doesn't represent production.
- **Partial absorption:** over time, correlate test verdicts against real-run outcomes; treat the
  test as a *hypothesis* about capability quality, not proof.

---

## Tier 2 — Coverage gaps (problems in the space r3 leaves unsolved)

### G1. No pipeline / chain-level capability test (absorbable, expensive)
Capabilities are tested in **isolation**, but factory behaviour is *chains* (task-start → route →
requ-explore[+ideation] → task-complete). A unit can be individually good and **compose badly**.
The playground's whole ethos is "complexity in the couplings" — applied to *product* features
(P-E/P-F), but there is **no analogue for capability couplings**. The single highest-value bugs are
likely at the seams, which the unit test cannot see.

### G2. The boundary excludes the highest-leverage instruction artifacts (framing decision)
"Unit = skill | agent." But behaviour also lives in **CLAUDE.md (the constitution — untested!)**,
`task_ordering_rules.yaml`, schemas, and the **automated-mode orchestrator** (`orchestrate.py` logic
+ the pending_feedback/back-pressure protocol). CLAUDE.md is the single most leverage-bearing
instruction artifact in the factory and sits outside the tested set. Is that the right cut? It is
currently *unexamined*, not *decided*.

### G3. Model-drift confound in the regression (absorbable)
The L3 reference run is frozen, but the **executor model and judge model evolve** (Opus 4.7→4.8→
Fable 5). New-vs-frozen-reference conflates *capability change* with *model change*. On a model
upgrade every reference is potentially stale and every regression signal confounded. r3 has **no
re-baseline policy** for model upgrades (re-freeze all references? keep model-pinned references?
accept the confound and annotate?). The temporal/model-version axis is unmodelled.

---

## Tier 3 — Design flaws (fixable inside the concept)

### D1. "Non-regression on every dimension" is too strict (fixable)
Most legitimate changes are *neutral* (token-efficiency refactor, typo) → costly **ties** with no
signal. Worse, a genuine **tradeoff** (improves D1, slightly costs D2) is flagged a regression and
**blocked — even when it's a good change.** A strict all-dimensions gate either blocks good
tradeoffs or trains gaming. Needs weighted/threshold scoring + a justified-tradeoff override
(recorded), not a hard per-dimension floor.

### D2. Anchor provenance is ungoverned (fixable)
The 1–5 anchors *are* a human standard of good (Q-archetype referent). Whoever authors them injects
their blindspots into the test. The factory has a **Human-Judgment Register** (REQ-PROC-044-05) for
exactly this — r3 doesn't connect anchors to it. Anchors should be registered/ratified human
judgment, not free-authored per descriptor.

### D3. The L1/L2 line is fuzzier than claimed (acknowledge + soften)
"If a script can decide it, it's L1" is presented as crisp, but many structural checks are
**necessary-not-sufficient proxies** (skill-creator's own warning: right filename, empty content).
Treating L1 passes as solid risks **false deterministic confidence**. The discriminating-check rule
helps but the boundary is a gradient, not a line.

### D4. Untrusted-candidate isolation at test time (fixable; security)
Deploying a *candidate* (buggy, or — under REQ-PROC-055 adoption — externally sourced) and running
it with harness as cwd treats the candidate as **trusted**. Blast radius if git-reset isolation is
imperfect, or if the candidate reaches outside the harness, is unaddressed. Adopted external
capabilities especially should be run as untrusted (sandbox/ref-scoped).

---

## Tier 4 — Reflexive / framing (question the concept itself)

### R1. Cost of the solution vs minimum-effective-dose (framing; possibly damning)
A four-layer + fixture-library + judge-orchestration + schema-adoption machine is a **large
maintenance surface** for a solo-maintainer factory (PERSONA-015: "minimum effective dose",
"longevity over velocity"). The *right problem* may be the cheaper "catch capability regressions
before they ship," for which a thin slice (L1 + a single blind old-vs-new A/B on the 2–3 open-ended
skills) might capture 80% of the value at 20% of the surface. **r3 never runs requ-explore's own
YAGNI evidence gate on its own ACs.** It should — several layers may not survive it yet (L4
persona-walk, the full agent role taxonomy, the EGP cross-walk) for lack of a *named* failure they
catch *today*.

### R2. Altitude — is "capability artifact" the right unit? (framing)
The user's seed was *open-ended skills*. r3 broadened to all skills+agents+classifiers. That may be
**scope creep** that dilutes the high-value core (ideation/requ-explore/product-intake). Or it may
be **too narrow** — the deeper gap is "the factory has no standing quality-feedback signal on
itself at all," of which capability-testing is one slice (alongside outcome metrics, optimizer
audit, EGP floor contracts). Worth naming the altitude explicitly rather than defaulting to it.

---

## Net assessment

**Right problems, mostly solved:** open-ended testability via assert-on-process, the explicit
fixture interface, lifecycle embedding, agents, old-vs-new A/B — the developer's stated asks are
addressed.

**But the concept's confidence outruns its foundations on three structural axes:** it has no oracle
for its own judges (B1), it cannot distinguish a faithfully-run *bad* method from a good one (B2),
and it has no evidence that toy-fixture success predicts real success (B3). These are not bugs to
patch; they are **honest limits that must be stated in the requirement** (the goal's AC: "honest
about what remains uncertain"). B1 and the model-drift/regression-strictness/anchor-governance flaws
*are* absorbable and should be folded in before the requirement is written. The two framing
questions (R1 cost, R2 altitude) should be put to the developer because they could **shrink** the
concept — which, for a minimum-effective-dose factory, might be the most valuable finding here.
