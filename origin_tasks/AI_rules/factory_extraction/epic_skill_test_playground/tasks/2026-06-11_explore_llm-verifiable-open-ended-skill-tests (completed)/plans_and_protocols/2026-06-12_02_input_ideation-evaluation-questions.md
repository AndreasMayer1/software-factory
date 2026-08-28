# INPUT — Evaluation Questions for Open-Ended Skill Performance (from the v2 Ideation Shakedown)

**Source**: TASK-PROC-004-10 (ideation workflow second-run shakedown), outcome-quality evaluation of the
TASK-PROC-066-06 run at its end-of-run gate. Full analysis:
`requirements_tasks/process/AI_rules/workflows/epic_structured_ideation/tasks/2026-06-12_explore_ideation-workflow-second-run-shakedown/plans_and_protocols/2026-06-12_02_evaluation_outcome-quality-066-06.md`

**Why it lands here**: that evaluation manually performed what this task must mechanize — judging an
open-ended skill's output without a golden answer. Two kinds of material transfer:
(§1) evaluation *questions* that generalize into rubric dimensions, and (§2) **concrete failures actually
observed on the 066-06 ledger** that a test could legitimately have failed it for — directly serving this
task's seed "what could a test fail them for, given both runs are valid? Whatever survives is a real
invariant." Each item is tagged **[DET]** (deterministically checkable, no LLM) or **[JUDGE]** (irreducible
LLM judgment), per this task's deterministic-vs-judged line-drawing goal.

---

## 1. Evaluation questions → candidate rubric dimensions

Ordered by information value per effort, as assessed in the shakedown.

1. **Counterfactual value (control-run question)** — would a plain single-pass synthesis over the same
   inputs have produced the same strategic content? In 066-06 the seed backlog already contained 6 of the
   14 final work items; the workflow's marginal value was the other 8 + the de-risk-first re-sequencing.
   A control run prices the machinery directly. **[JUDGE]** (comparing two open-ended outputs for
   strategic-content overlap) — expensive; a per-release calibration probe, not a per-run check.

2. **Effort-level marginal value** — Deep vs Standard on the same topic class: does Deep yield
   proportionally more *surviving-into-solutions* ideas and blind spots, or just more absorption?
   A natural experiment exists now: 066-05 (Deep, 114 ideas) vs 066-06 (Standard, 60 ideas), same topic
   class. **[DET]** for the ratios (recipe-edge counts per idea); **[JUDGE]** for blind-spot quality.

3. **Stability / reproducibility** — re-run divergence+synthesis on identical inputs: does tier membership
   of the ranking hold? If tiers flip run-to-run, gate decisions rest on noise. Maps directly to this
   task's golden-trace scheme (frozen topic+seed; judge asserts "at least as good", script asserts tier
   stability). **[DET]** for rank/tier comparison once two traces exist; the *tolerance band* is a design
   decision for this task.

4. **Frame / technique ROI** — which frames and techniques contributed the ideas that landed in top-tier
   solution recipes? Computable today from existing ledger `recipe` edges (e.g. was the cross-domain frame
   load-bearing or decorative? was `random_stimulus` ever in a winning recipe?). **[DET]** — pure edge
   counting; feeds frame-selection heuristics back into the skill.

5. **Gate leverage** — diff the pre-gate vs post-gate artifact set: how much did the developer's gate input
   change the output? (066-06: 5 mid-gate blind-spot findings became first-class ranked items — strong
   signal.) **[DET]** for "did gate input produce new/changed rows"; **[JUDGE]** for whether the change was
   substantive. Connects to this task's gate-as-product seed and TASK-PROC-069-05.

6. **Downstream conversion rate** — the real test of "directly convertible output": how many backlog items
   survive `task-derive-from-requ`/`task-create` unchanged vs get re-scoped/split/merged? High rework
   falsifies the skill's output-contract promise. **[DET]** (count, lagging indicator across tasks).

7. **Predictive validity of scores** — longitudinally: do high-MCDA-scored items actually get built first
   and deliver? If build order ends up driven entirely by dependencies + developer judgment, the expensive
   per-cell rating step should shrink. **[DET]** tracking, slow feedback loop.

8. **Compression fidelity** — does synthesis faithfully represent its recipe ideas, or distort/over-claim
   during clustering? Coverage checks cannot see this; only reading idea bodies against the composed
   solution can. **[JUDGE]** — a core anchored-rubric candidate (synthesis fidelity, already named in this
   task's goal.md).

9. **Mechanical honesty audit** — script-check every claim in the run's self-reported "Coverage & honesty"
   block against the ledger. The 066-06 run had a false claim there (see §2.2). The trust anchor of the
   gate must not be self-attested. **[DET]** — cheap, high-value, arguably the first test to build.

10. **Constraint discipline** — verify no idea/solution re-opens the fixed input constraints (066-06:
    passed, spot-checked against D1–D14). **[DET]** for keyword/ID-level re-litigation screens; **[JUDGE]**
    for semantic re-opening.

## 2. Observed failures on a "valid" run — what a test could have failed 066-06 for

These survived the seed's filter: 066-06 is a *valid, accepted-quality* run, and each item below is still a
legitimate failure. That makes them the strongest available anchors for rubric levels.

1. **Degenerate rating rationales** — all 126 rating cells carry the identical placeholder
   `rationale: "synthesis score"`, violating the skill contract's per-cell `<why>`. **[DET]**: assert
   rationale field non-constant across cells (entropy/uniqueness floor). Rubric anchor for a low
   "criteria soundness" level.

2. **Self-report contradicts the artifact** — synthesis honesty section claims "every solution carries
   recipe + answers + rationale"; 14/14 solution rows have **no** `rationale` field, and the soundness
   pass reported clean. **[DET]**: parse honesty-block claims, check each against ledger structure.
   This is the canonical "gate honesty" failure the goal.md dimension list anticipates.

3. **Internal contradiction between two renderings of the same decision** — the ranking table's Tier
   column and the build-order diagram disagree for 3 of 14 items (WI-11: 0 vs 1; WI-4: 1 vs 2;
   WI-13: 1 vs 0) in a deliverable claiming "executable without replaying any prior session". **[DET]**
   where structure is machine-readable; **[JUDGE]** when one rendering is prose. Anchor for an
   "artifact internal consistency" dimension.

4. **Zero rejection signal in convergence** — 60/60 ideas absorbed into recipes, 0 parked/discarded,
   all idea statuses left `open` (never transitioned), aspirational feasibility-c ideas folded in rather
   than parked. The critic mode never visibly said no. **[DET]**: absorption rate, status transitions,
   parked-list presence. Anchor for a "convergence selectivity" dimension (note: for composition topics
   the *right* threshold is a design question — 100% absorption is suspicious, not automatically wrong).

5. **Quota-shaped divergence** — technique distribution exactly identical across all 6 frames
   (2/2/2/2/1/1); no frame went deeper where it had traction. **[DET]** signal (distribution uniformity),
   **[JUDGE]** whether it harmed quality. Candidate evidence feeding a "non-redundancy / genuine
   divergence" dimension rather than a dimension itself.

6. **No problem-level discovery** — the run minted zero new `problem`/`question` rows; all P/Q rows are
   the task inputs verbatim, and the gapcheck validated coverage *against the given list* without testing
   the list itself. A credible missing dimension existed (child-session permission/safety policy) and
   nothing in the workflow could have caught it. **[JUDGE]** — "did the run challenge its frame?" is
   probably the hardest rubric dimension here; the deterministic proxy (count of origin-new problem rows)
   is gameable and should anchor only the lowest level.

## 3. Implications for this task's design (suggested, not binding)

- The **[DET] inventory above extends the "deterministic vs judged" line** beyond ideation's existing
  self-checks (post-check PASS, frame×technique counts): honesty-block verification, rationale
  non-degeneracy, cross-rendering consistency, status-transition discipline, absorption/selectivity
  ratios, recipe-edge ROI stats. All are scriptable against the ledger YAML alone — they need the run
  *artifact*, not a re-run.
- Items §1.3 (stability) and §1.1 (counterfactual) are **calibration probes**, not per-run tests — they
  cost full runs and belong in the golden-trace / periodic tier of the test scheme.
- §2.2 suggests a general principle for open-ended skill tests worth stating in the synthesis:
  **any self-reported quality claim inside the artifact is itself a test target** — assert the claim
  against the structure it describes before letting any LLM judge trust the claim.
- §1.8 (compression fidelity) and §2.6 (frame-challenge) are the two dimensions where the LLM judge is
  irreducible; both have concrete 066-06 anchors to build the 1–5 level descriptions from.
