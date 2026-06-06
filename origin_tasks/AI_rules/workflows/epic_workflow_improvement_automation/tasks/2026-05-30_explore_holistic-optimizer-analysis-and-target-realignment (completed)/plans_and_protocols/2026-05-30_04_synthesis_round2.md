---
name: holistic_optimizer_synthesis_round2
description: >
  Round-2 synthesis for TASK-PROC-006-20. Incorporates the developer's feedback
  (2026-05-30_03_feedback.md): resolves D-1..D-5 with the new inputs, adds the
  central new piece — the per-proxy "improvement evaluation contract" (how much
  evidence, how long to wait, how to judge effect) with meta-recursion safety —
  operationalizes the session-size budget (4 MB/week), moves event consolidation
  into a script, sets weekly self-run cadence + two staged test runs, and surfaces
  blind spots via inversion + cross-domain ideation. Web-research on evidence
  sufficiency integrated in §7.
created: 2026-05-30
type: design_synthesis
author: claude-opus
task: TASK-PROC-006-20
session: 880db287-21ec-488a-9d15-3d3107369904
supersedes_nothing: true   # additive to round-1 (_02); reverses nothing
references:
  - 2026-05-30_02_synthesis_round1.md
  - 2026-05-30_03_feedback.md
  - requirements_tasks/process/AI_rules/workflows/interactive_brainstorming_workflow/requirements.md (REQ-PROC-004)
  - requirements_tasks/process/AI_rules/llm_work_principles/requirements.md (REQ-PROC-059)
---

# Holistic Optimizer Analysis — Round-2 Synthesis

> Round-1 (`_02`) stands; nothing here reverses it. This round answers the
> developer's feedback (`_03`), adds the missing measurement-validity layer
> (the crux of the feedback), and goes hunting for blind spots as requested. The
> load-bearing new content is **§2 (the improvement evaluation contract)** and
> **§6 (blind spots)**.

---

## 0. What changed since round-1

The developer accepted the round-1 direction but reopened the task with five
refinements and one instruction ("a lot of blind spots remain — do another
round"). The refinements, verbatim-in-intent:

| Ref | Developer input | Round-2 section |
|---|---|---|
| D-1 | Accept the model — *but* picking a proxy set is not enough: we must also pick **how to measure** the improvement and **how much evidence / how long** before judging it. Some skills run rarely; one run isn't enough. "I expect the optimizer optimizes this too, right?" | §1.1, **§2** |
| D-2 | Don't set a raw token budget. Use **session-file size**: sum of session files per week = **4 MB**. | §3 |
| D-3 | Accept the digest split — *but* could events be **consolidated earlier by a script** that combines related events? | §4 |
| D-4 | Self-run cadence: **once per week.** | §5.1 |
| D-5 | F-1 reversal **confirmed.** Wants **two staged test runs** after the refactor: (1) a normal run, then (2) the optimizer running on itself. | §5.2 |
| — | Read REQ-PROC-004 (interactive brainstorming) as inspiration for the ideation. | applied in §6; reused in §5.3 |

---

## 1. Decision resolutions (folding in the feedback)

### 1.1 D-1 — accepted, and extended

Round-1 said each Layer-2 proxy is a GQM `Goal→Question→Metric`. The developer is
right that this is **half a spec**. A metric you cannot yet *judge* is not
actionable: you need to know when you have enough evidence and what verdict the
evidence supports. Round-2 extends every proxy to a full **improvement evaluation
contract** (§2). The downstream `requ-explore` must pick, *together with* each
proxy: its validation method, its minimum-evidence threshold, and its evaluation
window — not just the metric.

On "does the optimizer optimize this too?" — **yes, but bounded** (§2.4): the
optimizer may *propose* changes to the *tuning constants* of a contract (window
lengths, thresholds) as ordinary auto-blocked tasks; it may **never** edit the
contract *schema* or the scorer that applies it. That code stays on the deny-list.
This keeps G-INV-3 (scorer ≠ scored) intact while still letting the loop refine
its own calibration through the human gate.

### 1.2 D-3, D-4, D-5 — accepted with the refinements in §4 / §5.

### 1.3 D-2 — accepted; this is a genuinely better unit than round-1's "token number" (§3).

---

## 2. The improvement evaluation contract (the central new piece)

### 2.1 The problem the feedback exposed

The whole loop rests on a hidden assumption: *that you can tell whether a landed
improvement helped.* Round-1 never specified **how**. Three facts make this hard,
and the developer named all three:

1. **Effects are slow.** A skill edit's benefit shows up only in later tasks that
   use the skill.
2. **Use is sparse.** Some skills run a few times a month; the sample accrues
   slowly or never.
3. **One observation is not evidence.** A single post-change run can improve or
   regress by chance; judging on n=1 is noise, not signal.

Without an explicit answer, the loop will do the worst thing: **judge too early,
credit lucky changes, and revert good ones** — Goodhart by impatience.

### 2.2 The contract — what each proxy must declare

Every Layer-2 proxy carries a deterministic, script-checkable contract:

```yaml
proxy: impl_backpressure_cycles_per_task
goal:    "implementation wastes few tokens per delivered AC"      # GQM Goal
question:"are tasks bouncing through many quality-gate cycles?"   # GQM Question
metric:  "median back-pressure cycles per completed task"         # GQM Metric (deterministic source)
direction: lower_is_better
validation:                       # HOW to judge (the missing half D-1 named)
  method: before_after_rate       # before_after_rate | structural_rubric | binary_check
  baseline: snapshot_at_landing   # captured when the improvement lands
  min_evidence: 12                # min post-change observations before any verdict
  eval_window: P28D               # max calendar time to accrue them (ISO-8601 duration)
  decision_rule: sequential       # see §2.3 — anytime-valid, no peeking penalty
  effect_floor: 0.15              # ignore moves smaller than this (noise band)
verdict_actions:
  improved:  credit                       # audit counts it; proxy validity reinforced
  no_effect: keep (low priority to revisit)
  regressed: propose_revert (auto-blocked task)
  insufficient_evidence_at_window_end: park as "unproven"; do not credit, do not revert
expires: 2026-09-01               # proxy itself is reviewed/retired (Goodhart hygiene)
```

`min_evidence`, `eval_window`, `effect_floor`, `expires` are **tuning constants**
(developer-owned, script-stored, refinable). The *existence* of a validation block
per proxy is **normative** — no proxy without one.

### 2.3 The lifecycle: improvements have a "pending evaluation" state

This is new and important. Today an unblocked-and-completed improvement is treated
as done. Under the contract it enters a **pending** state and accrues evidence
until either `min_evidence` observations arrive (→ verdict) or `eval_window`
elapses (→ "unproven", parked). The audit only credits *improved* verdicts. This
generalizes round-4's revert-rate "maturation window" from one metric to the whole
loop, and it is exactly what stops impatient judging.

The continuous-evaluation method (so we can check progress without the statistical
"peeking" error of repeatedly testing) is **resolved in §7**: an **mSPRT / e-value
test that stops at `Λ ≥ 1/α`**, which is anytime-valid — designed to be looked at
after every observation with no false-positive inflation. `min_evidence` is an
**event count** (≥50, or the proportions formula), not a task count — §7.1.

### 2.4 Rare-use skills — three escape hatches (no single answer)

When `min_evidence` will realistically never be reached inside `eval_window`:

1. **Borrow strength.** Pool evidence across structurally-similar units (e.g. all
   `ux-*` skills share a proxy), so a rarely-used skill inherits the group's
   signal. (Hierarchical / empirical-Bayes shrinkage — confirm in §7.)
2. **Prefer a verifiable-now validation.** For rare units, set `method:
   structural_rubric` or `binary_check` instead of `before_after_rate`: judge the
   change by a deterministic property it satisfies *at landing* (passes a rubric, a
   test, an analyzer) rather than by a slow downstream rate. This trades "did it
   help on average" for "is it correct by construction" — weaker, but available.
3. **Accept long windows honestly.** Some improvements are simply *unproven for
   months*. The "unproven" parking state is a first-class, honest outcome — not a
   failure. The audit reports the count of unproven changes so the developer sees
   how much of the loop's output is unvalidated.

### 2.5 Meta-recursion safety (answering "the optimizer optimizes this too")

Letting the loop improve its own measurement is a **reward-tampering attractor**
(round-1 §8.4: Anthropic found models editing their own reward mechanism). The safe
boundary:

| The optimizer MAY (auto-blocked proposal, human unblocks) | The optimizer MUST NOT (deny-list) |
|---|---|
| propose new tuning-constant values (`min_evidence`, `eval_window`, `effect_floor`, `expires`) | edit the contract *schema* or the verdict logic |
| propose a new proxy (with a full contract) | edit `audit.py` / the scorer |
| propose retiring an expired proxy | edit its own selection / consumption code without the gate |

So: the optimizer can sharpen the *dials* of its own measurement through the human
gate; it can never rewrite the *ruler*. This is the only way "yes, it optimizes
this too" stays compatible with G-INV-3.

---

## 3. Session-size budget — D-2 operationalized

The developer's unit is better than round-1's abstract token number because it is
**deterministically measurable from the filesystem**: session JSONL files have a
size; bytes ≈ tokens to first order; no billing API needed.

**G-INV-4 restated:** optimizer meta-work consumes **≤ 4 MB of session-file size
per ISO week** (4 MB is the developer's number; a tuning constant).

**Why attribution is tractable here (better than round-1 §5.4 feared):** the
orchestrator launches **one session per task**. A `type: optimize` cycle task and
each unblocked optimizer-*produced* improvement task therefore each run in their
*own* session = their own JSONL file. The ledger is simply:

```
weekly_optimizer_bytes = Σ size(session_file)  for sessions whose task_id is a
                         type:optimize cycle task OR an optimizer-produced task,
                         within the current ISO week.
```

This is a deterministic script (REQ-PROC-059 a) over the session-log directory.

**Caveats (honest):**
- **Account-local** (round-4 §1.4): session files are per-account, not committed.
  The ledger sums the *current account's* files and is best-effort; it must err
  conservative (over-count → trip early). For a *guardrail* this is acceptable; the
  budget is a safety brake, not an accounting system.
- **Two-layer enforcement** (round-1 §8.3): a **cumulative** cap (≤ 4 MB/week →
  freeze) *and* a **velocity / no-progress** breaker (abort if a single cycle's file
  balloons or repeats with no progress), so a runaway session trips before the
  weekly total notices.

**The freeze (SRE error-budget pattern, round-1 §8.2):** at the cap the loop stops
creating cycle tasks and emits one `budget_frozen` digest; it does not nag, it
stops. Re-arms at the ISO-week boundary.

---

## 4. Script-based early consolidation — D-3

The developer is right and it is the cleaner design: **consolidate in a
deterministic combiner script, not in the LLM step.** Round-1 put consolidation in
the consumer; round-2 moves it upstream.

**`consolidate_events.py`** (new, runs inside `run_monitors.py` after the monitors,
before any consumer ever sees the queue):

- Groups events by an **equivalence key** (default: `event_type` + optimization
  *subject*, where subject for `skill_changed_and_used` is the skill path with the
  per-commit sha stripped).
- Collapses each group into **one digest event** carrying `count`, the list of
  commits/fingerprints, and the highest confidence in the group.
- Is idempotent and order-independent; re-running never double-merges.

Effect on the live backlog: 207 `skill_changed_and_used` events → ~one per distinct
skill (~90), and after Stage-2 evidence upgrades, the high-signal ones rise to the
top. The consumer (`select_candidate.py`) then sees a clean, already-deduped queue —
its one-pick-per-run rule stops being a problem because the queue is small.

This also subsumes round-1 §3.3's "per-file granularity" change: rather than
rewrite each monitor's emission, the combiner does the collapsing in one tested
place. (Lower-risk; one script to verify instead of four monitors.)

The equivalence-key choice is the one design judgement (per-skill? per-skill-per-
dimension?) — flagged in §8 as a small impl decision, not a developer value call.

---

## 5. Cadence and the two staged test runs — D-4, D-5

### 5.1 Weekly self-run cadence (D-4)

The autonomous cycle runs **at most once per ISO week**. This replaces round-1's
"every N completions" debounce with a calendar trigger, and it aligns three things
onto one clock: the 4 MB/week budget (§3), the weekly billing window, and the
self-run cadence. The periodic-counter monitor is repurposed (or replaced) by a
once-per-week gate: a cycle task is created only if none ran this ISO week.

### 5.2 Two staged, developer-witnessed test runs (D-5)

Both run **after** the refactor (consolidation, subordinate trigger, contracts,
budget ledger) lands, and both are bounded by the §3 kill-switch.

- **Test Run 1 — "drain & baseline" (normal operation).** The optimizer runs once
  on the real (consolidated) backlog: produces ranked, capped proposals; the
  developer reviews and unblocks/declines. *Purpose:* prove the loop runs end-to-end
  at all (recall `total_runs == 0` today) and **establish the proxy baselines** the
  contracts need. *Entry:* refactor complete, `runs.tsv` empty. *Exit/success:* a
  non-empty `runs.tsv`, a clean first audit, baselines snapshotted, ≤ 4 MB spent,
  developer satisfied with proposal quality.
- **Test Run 2 — "optimizer on itself."** The higher-cadence self-experiment from
  round-1 §5.2, now explicitly the *second* witnessed run, restricted to the
  optimizer's own non-deny-listed surface. *Entry:* Test Run 1 passed + baselines
  exist. *Exit:* OEC improves AND no guardrail (delivery throughput, 4 MB budget,
  quality gates) regresses (round-1 §8.4); any breach aborts.

### 5.3 Reuse REQ-PROC-004's pause mechanism to "witness" the runs

The developer wants to *observe* the test runs. REQ-PROC-004 already specifies the
exact mechanism: the agent writes `awaiting_user_review.md` and **file-watch
pauses** until the developer appends `APPROVED` / `ITERATE`. The two test runs
should reuse this verbatim — pause after producing proposals (Run 1) and after the
self-experiment's verdict (Run 2), so the developer inspects before anything is
credited or the next stage proceeds. No new infrastructure; it is the factory's
existing human-gate primitive.

---

## 6. Blind spots (ideation pass — inversion + cross-domain, per REQ-PROC-004)

The developer asked for blind spots and pointed at the brainstorming workflow. Two
of its mandated techniques surface the most:

### 6.1 Inversion — "what would make this optimizer worse than nothing?"

- **B1 — Plausible-but-wrong proposals, trusted and slowly harmful.** The developer
  unblocks a reasonable-looking change; it degrades quality slowly; the revert
  signal lags weeks. → *Mitigation:* the §2 contract's `regressed → propose_revert`
  lifecycle, plus a bias toward `structural_rubric`/`binary_check` validations that
  prove correctness at landing rather than trusting a slow rate.
- **B2 — Optimizing the measurable, ignoring the unmeasurable.** The most important
  quality dimensions may be the hardest to proxy; the loop drifts toward whatever
  has a cheap metric. → *Mitigation:* **explicitly scope the optimizer to the
  proxy-able surface only.** Un-proxied stages are out of scope (a human backlog
  owns them). The audit must *report the un-proxied surface* so its blind spot is
  visible, not hidden.
- **B3 — Self-amplifying churn.** Every improvement is a skill edit, which fires
  `skill_changed_and_used`, which generates work *about the improvement* — a loop
  optimizing its own edits. → *Mitigation:* the combiner (§4) and a **cooldown that
  excludes optimizer-authored commits** from the skill-change monitor for a window.
- **B4 — The developer's review capacity is the real scarce resource.** If the loop
  proposes faster than the developer reviews, the *review queue* starves, not the
  autorun queue. → *Mitigation:* treat **developer-review capacity as a third budget**
  alongside tokens and meta-work; the proposal cap (G-INV-5) and the low-unblock-rate
  self-throttle (round-1 §3.5) are its enforcement; the digest (D-3) is its relief.
- **B5 — Confounded attribution.** Many things change each week; crediting a proxy
  move to one optimizer change is confounded. → *Mitigation:* one-change-at-a-time
  discipline for the *self-experiment* (Run 2); for routine operation, accept weak
  attribution and lean on the contract's `effect_floor` + sequential rule to avoid
  over-claiming (recipe in §7).
- **B6 — Cold start.** Zero runs, zero baselines; the first contracts have nothing
  to compare against. → *Mitigation:* Test Run 1 exists precisely to mint baselines
  before any verdict is possible.

### 6.2 Cross-domain mappings (mechanisms worth stealing)

- **Immune system / homeostasis.** A useful response in measured doses; *autoimmune*
  (attacks healthy tissue) when overactive. The budget + subordination + cooldown are
  the regulatory brake. *Principle:* default to **under-reacting**; a quiet optimizer
  is safer than a busy one.
- **Central-bank policy lag.** Steer a lagging target (app quality) via leading
  indicators with a deliberate, respected **policy lag** (the `eval_window`).
  Overcorrecting before the lag elapses is the classic failure — exactly B1. The
  contract's window *is* the mandated lag.
- **TDD / "feedback loop is the product" (REQ-PROC-059 f).** Don't trust an "is it
  better?" judgement; encode the expected effect as a falsifiable check *up front*.
  The evaluation contract is literally a test written for the improvement before it
  is credited.
- **Portfolio allocation under a fixed budget.** With 4 MB/week, the optimizer
  allocates a scarce resource across candidate improvements: **diversify, size bets
  by confidence × expected impact, never spend it all on the loudest signal.**
  Reinforces ranked-batch + cap over first-match.

### 6.3 An integration the feedback implies

The optimizer and REQ-PROC-004 (brainstorming) are complementary improvement
engines: the **optimizer detects *where* friction is** (cheap, continuous,
automated); the **brainstorming workflow ideates *fixes* for a high-value friction**
(expensive, on-demand, creative, human-gated). A natural future link: when the
optimizer surfaces a high-impact friction whose fix is non-obvious, the *unblocked*
improvement task can be routed through REQ-PROC-004 instead of a single-shot edit.
Flagged as a future integration, not v1 (it costs tokens — weigh against the budget).

---

## 7. Web-research integration — evidence sufficiency & sequential evaluation

A focused `general-purpose` agent researched evidence sufficiency, sequential
evaluation, sparse/rare signal, and attribution. The findings make the §2 contract
**concrete and deterministic** — they supply the actual numbers and stopping rule
that §2.3 deferred. Sources are primary/practitioner (Wald SPRT; Johari/Pekelis/
Walsh mSPRT *arXiv:1512.04922*; Howard/Ramdas confidence sequences *Ann. Stat.
2021*; Evan Miller; Kohavi *Trustworthy OCE 2020*; CUSUM literature; empirical-Bayes
small-area work).

### 7.1 How much evidence — count **events, not observations** (fills `min_evidence`)

- **Rule of ~50 events per arm** to reliably detect a halving of a rate. With an 8%
  trigger rate that is ~625 observations. The denominator that matters is the number
  of times the changed path actually *fired*, not the number of tasks that ran.
- **Sanity formula** (Evan Miller): `n ≈ 16·p₀(1−p₀)/δ²` per arm for α=0.05 / 80%
  power, where δ is the minimum effect you'd act on. Use `p₀=0.5` when unknown
  (conservative — largest n). Example: a back-pressure-rate drop 0.30→0.15 needs
  `16·0.30·0.70/0.15² ≈ 150` tasks/arm.
- **Decision:** `min_evidence` in the §2.2 contract is an **event count = max(50,
  16·p₀(1−p₀)/δ²)**, not a task count. This is the single most important correction
  the research forces on round-1.

### 7.2 The honest continuous rule — anytime-valid, no peeking penalty (fills `decision_rule: sequential`)

- **The peeking penalty is real and large:** naïve repeated significance testing at
  a nominal 5% gives a **~26% actual false-positive rate** (Evan Miller). You may
  *not* read a fixed-horizon p-value mid-stream.
- **Deployable fix — mSPRT / e-values** (Optimizely Stats Engine method): maintain a
  running statistic `Λ_t` that mixes the likelihood ratio over a prior on the
  alternative (so you needn't guess the exact effect, fixing plain SPRT's weakness).
  **Stop & declare *improved* the first time `Λ_t ≥ 1/α`** (α=0.05 → threshold 20),
  equivalently when the always-valid p-value ≤ 0.05. This guarantee **holds at every
  observation**, so the factory can check after every task with zero peeking penalty.
  The cost is a sample-size premium vs an oracle fixed-n test — anytime-validity buys
  the *right to look early*, not free certainty.
- **Decision:** the §2.2 `decision_rule: sequential` = an **mSPRT/e-value test, stop
  at `Λ ≥ 1/α`**. The contract may be evaluated continuously and honestly.

### 7.3 Rare-use & slow drift (fills §2.4)

- **Empirical-Bayes / hierarchical shrinkage** to borrow strength: estimate a
  rarely-used skill's effect as a shrinkage blend of its own thin data and the
  all-skills baseline — "particularly useful for rare events." **Caveat:** shrinkage
  biases toward the pool, so use it for a **directional read only, never to declare a
  strong per-unit win** (a genuinely-different rare skill is pulled toward average).
  This bounds §2.4's "borrow strength" escape hatch.
- **CUSUM for slow degradation** of an already-shipped change: a one-sided CUSUM
  (slack `k=δ/2`, alarm `h`) detects shifts as small as **0.5σ** (vs ~2σ for a
  Shewhart chart) and is explicitly recommended "when data points are infrequent."
  → this is the detector for `verdict_actions.regressed` on a landed change (B1).
- **Lead with leading indicators:** when the lagging outcome is too sparse to ever
  signal in a practical window, instrument the highest-frequency proxy that still
  correlates and set the window from the **event rate, not the calendar**. Confirms
  round-1's leading-indicator emphasis and §2.4 escape (2).

### 7.4 Attribution (hardens B5)

- **One-change-at-a-time or you cannot learn** (Kohavi): bundling several process
  changes in one window makes the move uninterpretable by construction.
- **For a single-unit factory** (one developer): a **randomized weekly switchback**
  (rule on/off by week, randomized) or a **small permanent holdback** (occasionally
  route a task through the old workflow) creates the concurrent control that a naïve
  before/after lacks. Switchback is invalid when the change has lasting carryover
  (most tooling changes do — you can't un-learn a better skill), so **holdback is the
  better fit** for this factory.
- **Decision — attribution gate:** a contract verdict is only **credited** if no
  other change to the same metric landed in its window; otherwise the verdict is
  **downgraded to "directional, unattributed."** This is enforced in the self-run
  (Run 2, one-change-at-a-time) and recorded honestly in routine operation.

### 7.5 The concrete per-proxy rule (what the impl task implements)

> `min_evidence` = event count `max(50, 16·p₀(1−p₀)/δ²)` · `eval_window` =
> `ceil(min_evidence / (daily_task_rate × trigger_rate))`, capped (~P60D) →
> sparsity-escape to a leading proxy or EB-shrinkage directional read ·
> `decision_rule` = mSPRT/e-value, stop at `Λ ≥ 1/α` · slow-drift watch = one-sided
> CUSUM · verdict honored only under one-change-at-a-time **or** a holdback, else
> "directional, unattributed."

All of these are deterministic and script-ownable (REQ-PROC-059 a) — no LLM judgement
on the evaluation path, preserving G-INV-3.

---

## 8. Decisions & small impl judgements

### 8.1 Still genuinely the developer's to decide
- **D-2 number confirmed: 4 MB/week.** (Captured. Tuning constant.)
- **Contract tuning constants** (`min_evidence`, `eval_window`, `effect_floor`,
  `expires`) — initial values per proxy. *Recommendation:* set conservative defaults
  in the downstream `requ-explore` (e.g. `min_evidence: 8–12`, `eval_window: P28D`)
  and let Test Run 1 + later self-runs refine them.
- **B4 — make developer-review capacity an explicit budget?** *Recommendation:* yes,
  as a soft cap (max open optimizer proposals at once = WIP limit), since it directly
  protects the developer's time.

### 8.2 Small impl judgements (not value calls — settle in the impl tasks)
- The combiner's **equivalence key** (per-skill vs per-skill-per-dimension) — §4.
- Whether the weekly trigger is a calendar gate or a repurposed periodic counter — §5.1.
- Borrow-strength grouping (which skills are "similar") — §2.4, informed by §7.

---

## 9. Honest uncertainty (round-2)

- **The contract makes the loop slower to "prove" itself — by design.** Most
  improvements will sit "pending" or "unproven" for weeks. That is correct, but it
  means the audit's "improved" count will be small early on. The developer should
  expect a long, quiet validation period, not fast green numbers.
- **Borrow-strength assumes similar skills behave similarly** — false if a group is
  heterogeneous. Use it cautiously; §7 should bound when pooling is valid.
- **Account-local budget ledger** (§3) cannot see other accounts' sessions. Acceptable
  for a brake; not an accounting system.
- **Attribution stays weak in routine operation** (B5). Strong attribution only in the
  one-change-at-a-time self-experiment. The loop will often *not know for certain*
  which change moved a proxy — and must not pretend otherwise.
- **The proxy set is still unbuilt and unvalidated.** Everything above is scaffolding
  for measurement; whether the chosen proxies actually ladder to app quality remains
  the open empirical question from round-1 §7, now with a contract to test it.
- **The required event counts may be unreachable for this factory's volume.** §7.1's
  ~50-events / `16·p₀(1−p₀)/δ²` floors are sobering: a low-volume single-developer
  factory may *never* accrue enough events for many proxies inside any reasonable
  window. The honest consequence is that **most routine improvements will be credited
  "directional, unattributed" at best**, and strong statistical verdicts will be the
  exception (reserved for high-frequency proxies and the one-change self-run). The
  loop's value is then more "surface friction + propose + human-judge" than "prove
  improvement statistically" — the contract keeps us from *over*-claiming, but cannot
  manufacture signal that the volume doesn't contain.
- **Anytime-validity and shrinkage cost precision** (§7): wider intervals, a
  sample-size premium, and bias toward the pool. They buy the right to look early and
  to get *some* signal on rare units — not free certainty.

---

## 10. Updated handoff

Unchanged in shape from round-1 §9; round-2 adds to each step:

1. **`requ-explore` on REQ-PROC-006 / 059** — now also makes normative: the
   per-proxy **evaluation contract** (§2), the **session-size budget unit** (§3,
   G-INV-4 in MB/week), the **meta-recursion boundary** (§2.5, extends the
   deny-list), and **developer-review capacity as a budget** (B4).
2. **`task-derive-from-requ`** — adds tasks: `consolidate_events.py` combiner (§4),
   the **evaluation-contract engine + pending/verdict lifecycle** (§2.3), the
   **session-byte budget ledger + freeze + velocity breaker** (§3), the weekly
   trigger (§5.1), and the optimizer-commit cooldown (B3). Plus everything from
   round-1 §9 step 2.
3. **Test Run 1 (drain & baseline)** then **Test Run 2 (optimizer on itself)** (§5.2),
   both reusing REQ-PROC-004's file-watch pause so the developer witnesses them (§5.3).

Developer decisions in §8.1 should be resolved before step 1 finalizes the amendments.
