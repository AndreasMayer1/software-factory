---
name: holistic_optimizer_synthesis_round3
description: >
  Round-3 synthesis for TASK-PROC-006-20. Incorporates the developer's round-3
  feedback (2026-05-31_05_feedback.md): adds simulation-based fast evaluation as a
  complement to the slow statistical evaluation contract (inspired by skill-creator
  simulation, TASK-PROC-055-06); corrects the session-storage model (CCS = shared,
  not account-local); softens the 4 MB budget to a no-new-task start-gate; proposes
  an activity-gated weekly self-run trigger; confirms contract constants as tuning;
  drops B4 from the normative set. Web-research on simulation/replay eval in §5.
created: 2026-05-31
type: design_synthesis
author: claude-opus
task: TASK-PROC-006-20
session: 97dbf4eb-4a12-4f8a-ab78-d7c1fa2b12fa
supersedes_nothing: true   # additive to round-1 (_02) and round-2 (_04)
references:
  - 2026-05-30_02_synthesis_round1.md
  - 2026-05-30_04_synthesis_round2.md
  - 2026-05-31_05_feedback.md
  - TASK-PROC-055-06 (daymade skills eval — pending; source of the simulation pointer)
  - REQ-PROC-004 (interactive brainstorming), REQ-PROC-059 (LLM-work principles)
---

# Holistic Optimizer Analysis — Round-3 Synthesis

> Rounds 1–2 (`_02`, `_04`) stand. Round-3 adds the **simulation idea** (the big
> new content, §2), corrects four round-2 details the developer flagged (§1), and
> answers the open weekly-trigger question (§3). Load-bearing new content: **§2**.

---

## 0. What changed since round-2

| Ref (from `_05`) | Developer input | Round-3 section |
|---|---|---|
| Simulation | "Simulation like skill-creator does it (TASK-PROC-055-06)… could make measuring improvements easier. We probably can't use the skill 1:1." | **§2** |
| Sessions | "No — we're using CCS. All sessions are stored in a **shared** folder." (corrects round-2 §3 / round-4 §1.4 "account-local") | §1.1 |
| Budget | "4 MB is **not a hard cut**. The session/task that exceeds it can complete, but if size > 4 MB **no new task** must be started." | §1.2 |
| Weekly trigger | "How do we trigger it weekly? A date in the `awaits` field respected by `next_tasks.py`? (every week = every week *work is done*; weeks can be skipped if the project isn't touched.)" | §3 |
| Ideation | "I love your ideation results!" | more in §4 |
| Contract constants | "yes" (they are tuning constants) | §1.4 (confirmed) |
| B4 | "developer-review capacity as a budget? **No, not now.** Maybe future." | §1.3 |
| — | "Good round. We need another one!" | this doc |

---

## 1. Corrections to round-2

### 1.1 Sessions are SHARED (CCS), not account-local — a meaningful simplification

Round-2 §3 and round-4 §1.4 both assumed session JSONL is per-account and not
shared, forcing the budget ledger (and any DuckDB/replay analytics) to be
"best-effort, account-local." **This is wrong.** CCS stores all sessions in a
shared folder (`/home/vscode/.ccs/shared/context-groups/default/projects/<project>/
<uuid>.jsonl`, as CLAUDE.md itself documents). Consequences:

- **The session-byte budget ledger (§1.2) is COMPLETE and authoritative**, not
  best-effort. It sees every account's optimizer sessions. The "err conservative /
  over-count" hedge from round-2 §3 is unnecessary.
- **Replay-based simulation (§2) becomes genuinely feasible**: real logged tasks
  from all accounts are available on disk to replay against a changed skill.
- The round-4 §1.4 "DuckDB-over-JSONL is account-local" caveat is **retired**; a
  query over the shared folder is a complete cross-account history (still subject to
  retention/rotation, but not to account-locality).

This correction is recorded so the downstream `requ-explore` does not re-import the
stale account-local assumption.

### 1.2 The 4 MB budget is a soft start-gate, not a hard kill (replaces round-2 §3's mid-task breaker)

Round-2 modelled G-INV-4 as cumulative cap + a velocity breaker that *aborts* a
running session. The developer's rule is gentler and cleaner:

> A task/session already running **completes** even if it pushes the weekly total
> over 4 MB. But once weekly optimizer session-bytes **> 4 MB, no *new* optimizer
> task is started** until the week re-arms.

So G-INV-4 enforcement is a **pre-start check**, not an interrupt:

- Before the trigger (§3) creates a new `type: optimize` cycle task — and before an
  unblocked optimizer-produced task is allowed to start — a script reads the shared
  session folder, sums this ISO-week's optimizer session bytes, and **refuses to
  start a new one if the sum already exceeds 4 MB**. In-flight work is never killed.
- This is the SRE error-budget "freeze new change when budget spent" pattern
  (round-1 §8.2), applied at *task admission* rather than mid-flight. It is also
  trivially deterministic (a `stat` sum + a comparison) and never destabilises a
  running session.
- The round-2 "cost-velocity / no-progress breaker" is **demoted**: it is no longer
  the budget mechanism. It may survive only as an independent runaway-loop safety
  (abort a single session that loops with no progress) — a separate concern from the
  weekly budget, and optional.

`4 MB` and `per-ISO-week` are the developer's numbers (tuning constants); the
start-gate mechanism is normative.

### 1.3 B4 dropped from the normative set

Developer-review capacity as an explicit third budget — **not now** (maybe later).
Removed from round-2's normative recommendations; parked as a future idea. The
proposal cap (G-INV-5) and the low-unblock-rate self-throttle still exist and
already give the developer indirect protection.

### 1.4 Contract tuning constants — confirmed

`min_evidence`, `eval_window`, `effect_floor`, `expires` (round-2 §2.2) are
script-owned tuning constants. Confirmed; no change.

---

## 2. Simulation-based fast evaluation (the round-3 idea)

### 2.1 The problem it attacks

Round-2 §9 admitted the loop's deepest weakness honestly: for a low-volume factory,
real-world events are so sparse that **most improvements will sit "unproven" or be
credited only "directional, unattributed"** — the statistical contract is correct
but slow, and for rarely-used skills it may never resolve. The developer's pointer
to skill-creator's *simulation* is the missing fast path: don't only wait for the
world to exercise the change — **exercise it yourself, offline, against
representative scenarios, and read a signal in minutes.**

### 2.2 What simulation means here (adapting skill-creator, not copying it)

"We probably can't use the skill 1:1" is right — skill-creator simulates a skill to
*validate it works during authoring*; we need it to *measure whether an edit is an
improvement*. The adaptation:

- **A scenario set per skill/stage** — a small, versioned collection of
  representative task inputs (the "wind tunnel"). Two sources, now both feasible
  because sessions are shared (§1.1):
  1. **Replay** of real logged tasks that exercised the skill (authentic, no
     synthesis risk).
  2. **Synthetic scenarios** generated to cover edge cases the replay set misses
     (coverage, at the cost of representativeness — §5/Q3 bounds this).
- **A run**: execute the *changed* skill (and, for A/B, the *old* skill) against the
  scenario set.
- **A deterministic score**: a structural rubric / test / analyzer over the outputs
  — never single-LLM "is it better?" as the sole judge (REQ-PROC-006 AC-08,
  G-INV-3). Pairwise old-vs-new on identical inputs is the cleanest comparison.

### 2.3 How simulation reshapes the evaluation contract (round-2 §2)

Simulation becomes a **first-class validation method**, often the *primary* one,
with the statistical contract demoted to slow confirmation:

```yaml
validation:
  method: simulation            # NEW primary method (was: before_after_rate)
  scenario_set: scenarios/<skill>/   # versioned, deny-listed (§4 B7)
  split: {train: 0.6, held_out: 0.4} # §5.1 skill-creator firewall: tune on train,
  verdict_from: held_out             #   emit the verdict from held-out ONLY (anti-Goodhart)
  comparison: pairwise_old_vs_new    # old vs new skill on identical inputs
  repeats: 3                          # average out stochasticity (§5.2)
  score:                              # deterministic ladder (§5.2) — multi-dimension
    quality: structural_rubric        #   assertions/rubric; pass threshold spelled out
    cost: {tokens, latency}           #   a "better but 3× costlier" edit is net-worse (§5.1)
  fast_verdict_on: landing           # signal available immediately, not in weeks
  real_confirmation:                 # the slow contract becomes a HOLDBACK confirmer
    method: before_after_rate         # round-2 §2.2, now secondary
    role: catch_sim_to_real_gap       # confirm or flag; recalibrate on divergence (§5.4)
    min_evidence: <event count>        # §7.1 round-2 — but no longer blocking
  expires_on: [model_upgrade, eval_drift, date]   # §5.1/§5.4 — verdicts are not permanent
```

So the lifecycle becomes **two-tier**:
1. **Fast (simulation) verdict** — gates whether the improvement ships at all
   (cheap, offline, at landing). Most improvements get judged *here*.
2. **Slow (real) confirmation** — the round-2 statistical contract runs as a
   *holdback confirmer* on real usage; its job is now narrower: **catch the
   sim-to-real gap** (the sim said "better" but production disagrees). It no longer
   needs to be the sole gate, which dissolves the round-2 §9 "everything is unproven
   for months" pessimism for the common case.

This is the right division of labour: simulation gives *speed and attribution* (you
control the inputs → clean A/B), the real holdback gives *validity* (catches
overfitting to the scenario set).

### 2.4 The honest catch — sim-to-real gap

Simulation can lie: an edit that scores better on the scenario set can be worse in
production (overfitting to the eval, distribution shift, a scenario set that has
rotted). Therefore:

- The real holdback (§2.3 tier 2) is **necessary, not optional** — it is what keeps
  the sim honest. Simulation replaces "wait for slow statistics *to gate*," not
  "ever look at reality."
- The scenario set must be **versioned, on the deny-list (the optimizer cannot edit
  its own test set — §4 B7), and refreshed from real replays** when a real
  regression slips through (every escaped bug becomes a new scenario — the CI-test
  discipline, §4).

(Web research §5/Q4 quantifies and sources these failure modes.)

---

## 3. The weekly self-run trigger — answering the open question

The developer asked *how* to fire weekly, floated a date-aware `awaits` field, and
crucially clarified: **"every week" means every week that work is actually done —
untouched weeks are skipped.** That clarification points away from a wall-clock
timer and toward an **activity-gated** trigger.

### 3.1 Recommended: activity-gated ISO-week check (no timer, no new field)

`run_monitors.py` already runs **only on `task-complete`** — i.e. only when project
work happens. Piggyback the weekly trigger there:

- `state.json` gains `last_self_run_iso_week` (e.g. `"2026-W22"`).
- On each task-complete sweep: if `current_iso_week != last_self_run_iso_week` AND
  events exist AND the §1.2 budget gate is open → create one `type: optimize` cycle
  task and set `last_self_run_iso_week = current_iso_week`.
- **Untouched weeks self-skip**: no task-complete → no sweep → no trigger. Exactly
  the developer's "weeks can be skipped if the project isn't touched." No cron, no
  wall-clock, no daemon.

This is deterministic, needs no scheduler, and reuses the existing hook — the
cheapest possible mechanism (REQ-PROC-059 a/c).

### 3.2 The date-aware `awaits` field — a more general alternative (framed, not chosen)

The developer's idea (`awaiting: ["after:YYYY-MM-DD"]` respected by
`next_tasks.py`) is real and *more general* — it would let any task be time-gated,
not just the optimizer. But it is (a) wall-clock, not activity-gated, so it would
fire on the first task-complete after the date even in an otherwise-untouched week —
acceptable, but less precise than 3.1 for this purpose; and (b) a broader change to
the ordering engine (`claude-modify-ordering-rules` territory).

**Recommendation:** use 3.1 (state.json ISO-week) for the optimizer now. Treat the
date-await field as a **separate, optional general capability** the developer may
add later if other tasks want time-gating — not coupled to this redesign. Framed in
§6 as a small decision.

---

## 4. More ideation (round-3) — simulation opens new blind spots

Applying inversion + cross-domain again (REQ-PROC-004), now to the simulation layer:

- **B7 — the scenario set itself becomes a Goodhart target.** If the optimizer can
  edit the set that grades it, it games the sim. → *Mitigation:* the scenario set is
  **on the deny-list** (the optimizer may *propose* additions through the human
  gate, never self-edit) — the exact meta-recursion boundary of round-2 §2.5, now
  extended to test fixtures.
- **B8 — simulation costs the very budget it protects.** Running scenarios burns
  session bytes (the 4 MB, §1.2). A rich sim that eats the weekly budget is
  self-defeating. → *Mitigation:* keep the scenario set **small and the scoring
  deterministic** (rubric/analyzer, not an LLM panel); count simulation bytes inside
  the §1.2 ledger; cap sim cost as a fraction of the weekly budget. Simulation must
  be *cheaper* than the slow signal it replaces, or it is not worth it.
- **B9 — scenario-set rot.** A set frozen at authoring drifts from how the skill is
  actually used. → *Mitigation:* refresh from real replays (now feasible, §1.1);
  give each scenario set an `expires`/review date like proxies (round-2 §2.2).
- **B10 — simulation is impossible for some skills.** Skills whose effect is
  inherently in the real world (e.g. a commit-message skill, a release skill) have no
  meaningful offline scenario. → *Mitigation:* honest scoping — those skills fall
  back to the slow statistical contract (round-2) or a one-time structural check;
  simulation is *added where it fits*, not forced everywhere.

**Cross-domain mappings (mechanisms to steal):**
- **Wind tunnel / flight simulator.** Test the design cheaply in sim before the
  expensive real flight — *but* the sim is trusted only to the degree it has been
  validated against real flights. That validation loop = the §2.4 real holdback. A
  sim no one calibrates against reality is theatre.
- **CI regression suite.** The scenario set *is* a regression test suite for skills.
  Treat it as one: versioned, protected, and **grown every time a real regression
  escapes** ("every escaped bug becomes a test"). This is REQ-PROC-059 (f) "the
  feedback loop is the product" — the cheapest durable asset the optimizer can build.
- **Vaccine: challenge trial vs field efficacy.** A fast proxy (challenge/sim) reads
  out in days; true field efficacy takes months. Mature programs use **both** and
  never let the fast proxy fully replace the slow truth — exactly the two-tier
  verdict (§2.3).

**Integration picture (the eval stack this round completes):**
`detect friction (monitors)` → `consolidate (script)` → `propose (auto-blocked)` →
**`fast verdict (simulation on replayed+synthetic scenarios)`** → ship on pass →
**`slow confirmation (statistical contract on real holdback)`** → credit/revert.
Simulation is the new fast inner loop; the statistical contract is the slow outer
loop that keeps it honest.

---

## 5. Web-research integration — simulation / replay-based evaluation

A focused `general-purpose` agent researched skill-creator simulation, offline/
replay eval, synthetic scenarios, and the sim-to-real gap. It found the **exact
skill-creator mechanism**, which makes §2 concrete, and surfaced one discipline
(the held-out split) important enough to elevate. Primary sources: Anthropic
`skills/skill-creator/SKILL.md`; Datadog *Offline evaluation for AI agents*;
promptfoo docs; langwatch/scenario; arXiv 2509.19364; LiveCodeBench/Goodeye.

### 5.1 What skill-creator actually does (Q1) — the primitive to adapt

- **Paired with/baseline run on identical inputs.** For each of 2–3 realistic test
  prompts in `evals/evals.json` (prompt + expected_output + files), skill-creator
  spawns two subagents simultaneously — one with the new skill, one **baseline (no
  skill for a new skill; the *previous version* for an improvement)** — then a
  `grader.md` subagent emits `grading.json {text, passed, evidence}`. *This paired
  old-vs-new on the same inputs is the cleanest "is this edit an improvement?"
  primitive — it controls for everything except the change.* (Confirms §2.2's
  `comparison: pairwise_old_vs_new`.)
- **Quantitative aggregate.** `benchmark.json` reports pass-rate per assertion **plus
  timing and token usage (mean ± stddev) and a delta vs baseline.** → score quality
  **and cost/latency/tokens together** — "5% better but 3× costlier is net-worse."
  This ties simulation directly to the 4 MB budget (B8): a sim must report its own
  token cost.
- **Held-out split — the Goodhart firewall (elevate to normative).** Description
  optimization uses ~20 trigger queries split **60% train / 40% held-out**, evaluates
  each candidate **3× for stability**, iterates **≤5 times**, and selects
  `best_description` **by the held-out test score, not the train score.** This
  transplants directly: iterate the skill edit against the tuning slice, **emit the
  verdict from the frozen held-out slice only.** It is the cheapest defense against
  the optimizer overfitting its own scenario set (B7) — adopt it explicitly in §2.
- **Re-run all evals on every model upgrade** — "skills that worked on the previous
  model sometimes behave differently." → a model bump is an **eval-invalidating
  event**; scenario verdicts expire on model change (adds to B9's `expires`).

### 5.2 Offline / replay eval (Q2)

- **Three components:** annotated test data (core + edge), traced task code,
  evaluators. **Start 20–50 cases.** Use the **cheap-to-expensive ladder**:
  deterministic checks → heuristics → LLM-judge *only* when needed. (Keeps the sim
  cheap — B8 — and keeps single-LLM judgement off the critical path, AC-08/G-INV-3.)
- **Trajectory replay:** capture every prompt/tool-call/response/error as structured
  JSON, then replay real production traces against the new version — "you cannot
  replay what you didn't record." **Implication for us:** to make §2.2's replay
  source real, the factory must **log full task trajectories now** (the shared
  session JSONL, §1.1, is most of this already). Offline evals run *before deploy*;
  online evals run *continuously on prod traces*.
- **Closed-loop growth:** mine production failures into labelled cases appended
  permanently — the suite "grows every week from real failures." This is exactly the
  B9 refresh-from-replay / "every escaped bug becomes a test" discipline, sourced.
- **Trustworthiness:** repeat each case and average (stochastic agents — "noise
  dressed as signal" otherwise); score multiple dimensions; **validate the judge
  against known-score cases**; a **judge panel** de-biases single-judge error
  (promptfoo).

### 5.3 Synthetic scenarios (Q3)

- Synthetic/simulated-user generation **fills cold-starts and edge/adversarial
  coverage** the logs lack (LangWatch `scenario`: an LLM user-simulator drives turns,
  a judge ends early on violation). *But* **simulated users explore plausible-to-an-
  LLM paths, not necessarily real-user paths** — coverage ≠ representativeness;
  **weight synthetic scenarios by real-world prevalence** so pass-counts don't
  inflate. Replay-first, synthesize-only-for-gaps (confirms §2.2 priority order).

### 5.4 Sim-to-real gap (Q4) — the validity discipline

- **Goodhart on a static set is proven, not theoretical:** LiveCodeBench gave
  "scientific proof of Goodhart's Law" by mining fresh post-cutoff problems and
  exposing massive overfitting; static sets silently become contaminated. → keep a
  **never-optimized-against held-out slice** and **refresh from recent production.**
- **Offline ≠ field (arXiv 2509.19364):** "a single prompt elicits different
  responses depending on whether it's accessed statelessly (offline) or through a
  logged-in session (field)." The offline verdict is a **gate, never the proof.**
- **Calibrate continuously:** periodically correlate the offline verdict against the
  eventual online outcome; when they diverge, treat it as **eval drift** and
  recalibrate the scenario set / judge. This *is* the §2.4 real-holdback role, made
  into a standing recalibration loop.

### 5.5 Net effect on §2

Four things sharpen and one is elevated:
1. The sim primitive = **paired old-vs-new on identical inputs, 3× repeated**, scored
   on **quality + cost + latency + tokens** with a delta (§2.2 made concrete).
2. **Held-out 60/40 split, verdict from the held-out slice only** — elevated to a
   normative anti-Goodhart firewall (strengthens B7).
3. **Replay requires trajectory logging now**; closed-loop growth from prod failures
   (B9, sourced).
4. **Judge calibration + panel + repeat-and-average** are standing requirements; the
   cheap deterministic-first ladder keeps sim inside the budget (B8).
5. **Model upgrades and eval drift both expire verdicts** — calibration is continuous
   (extends B9; §2.4 becomes a recalibration loop, not a one-off check).

---

## 6. Decisions & small judgements (round-3)

### 6.1 Developer's to decide
- **Weekly-trigger mechanism:** activity-gated state.json ISO-week (§3.1,
  recommended) vs the more general date-aware `awaits` field (§3.2). *Recommendation:
  3.1 now; 3.2 as a separate optional feature later.*
- **Simulation scenario sets:** confirm they are **deny-listed** (B7), seeded from
  real replays + a few synthetics, with an `expires`/review date (B9).
- **Simulation cost cap:** what fraction of the 4 MB/week may simulation consume
  (B8)? *Recommendation: a small fixed sub-cap so sim never crowds out delivery.*

### 6.2 Settled by the feedback (no longer open)
- 4 MB = soft start-gate, not hard kill (§1.2). ✓
- Sessions are shared; ledger authoritative (§1.1). ✓
- B4 (review-capacity budget) dropped (§1.3). ✓
- Contract constants are tuning constants (§1.4). ✓

---

## 7. Honest uncertainty (round-3)

- **Sim-to-real gap is unavoidable.** A simulation verdict is *necessary but not
  sufficient*; without the real holdback (§2.4) the loop can confidently ship
  regressions that please the scenario set. Simulation buys speed, not truth.
- **Building & maintaining scenario sets is itself meta-work** — subject to the very
  subordination guardrail (G-INV-5) and budget (G-INV-4) the loop is bound by. If the
  scenario-set upkeep grows large, it competes with delivery; it must stay lean (B8).
- **Some skills can't be simulated** (B10); for those the slow statistical contract
  (round-2) remains the only option, with all its sparsity limits.
- **Shared-session correction widens the design space** (replay, complete ledger,
  cross-account analytics) but those files are still subject to retention/rotation —
  the ledger is authoritative *for what is on disk*, and very old history may be
  pruned. Not a blocker for a weekly budget; worth noting for long-window analytics.
- **The proxy set and now the scenario sets are both unbuilt and unvalidated** — the
  empirical question (do these actually track app quality?) is still open, now with
  *two* measurement instruments to validate against reality, not one.

---

## 8. Updated handoff

Additive to round-1 §9 and round-2 §10:

1. **`requ-explore` on REQ-PROC-006 / 059** — now also makes normative: **simulation
   as a first-class validation method** with the statistical contract as a real
   holdback confirmer (§2.3); the **shared-session model** (drop account-local
   caveat, §1.1); the **soft 4 MB start-gate** (§1.2, replacing the mid-task
   breaker); the **activity-gated weekly trigger** (§3.1); **scenario sets on the
   deny-list** (B7). Remove B4 from scope.
2. **`task-derive-from-requ`** — adds tasks: the **simulation harness** (scenario set
   format, replay loader from the shared session folder, pairwise runner,
   deterministic scorer); the **session-byte budget start-gate** (§1.2, now
   authoritative); the **`last_self_run_iso_week` weekly trigger** (§3.1); scenario
   refresh-from-replay (B9). Plus everything from rounds 1–2.
3. **Test Run 1 (drain & baseline)** then **Test Run 2 (optimizer on itself)** — now
   each also exercises the **simulation fast-verdict path**, with the real holdback
   running behind it; both witnessed via REQ-PROC-004's pause (round-2 §5.2–5.3).

Developer decisions in §6.1 should be resolved before step 1 finalizes the amendments.
