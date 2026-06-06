---
name: holistic_optimizer_synthesis_round1
description: >
  Holistic analysis of the claude-optimize loop (TASK-PROC-006-20). Round-1
  synthesis covering all four seeds — targets & alignment, design critique &
  redesign, bug reconciliation, and the self-optimization experiment. Makes the
  optimization targets explicit and measurable, proposes a concrete redesign
  reconciled with the bug list, and frames the value-laden decisions for the
  developer. Web-research findings (Seed-1 ground) integrated in §8.
created: 2026-05-30
type: design_synthesis
author: claude-opus
task: TASK-PROC-006-20
session: b7511056-7384-471c-9739-2489bef37cca
references:
  - 2026-05-30_00_user_initial_input.md
  - 2026-05-30_01_plan_analysis-scope.md
  - ../../2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/2026-05-16_08_opus_synthesis_round4.md
  - ../../2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/2026-05-16_07_decisions_applied.md
  - requirements.md (REQ-PROC-006 @ 645bf249)
  - requirements_tasks/process/AI_rules/llm_work_principles/requirements.md (REQ-PROC-059)
---

# Holistic Optimizer Analysis — Round-1 Synthesis

> **Reading order.** §0 is the one-screen verdict. §1 is the empirical ground
> truth (what the live system is actually doing, with numbers). §2–§5 answer the
> four seeds. §6 frames the decisions the developer owns. §7 is the honest
> uncertainty list. §8 holds the web-research integration. The redesign in §3 and
> the targets in §2 are the load-bearing output.

---

## 0. Verdict in one screen

The optimizer is **structurally faithful to the round-1–4 design but has never
once run** (`state.json.total_runs == 0`, `runs.tsv` empty). What looks like a
"247-events-block-everything bug" is actually **three distinct problems stacked on
top of each other**, and only the shallowest is a bug:

1. **No consumer ever ran** (F-1). The producer chokepoint that mints the *output*
   improvement tasks exists; the autonomous trigger that mints the *cycle* task
   that *runs the skill* does not (it is held in `git stash`). So events only ever
   accumulated. → bug, but its fix is a *design* decision (§3.1).
2. **The consumption unit is one-event-per-run.** Even once a consumer runs,
   draining 247 events needs 247 runs, each producing one auto-blocked task. The
   design never had a batch/dedup/ranking story for a *backlog* — it assumed a
   near-empty queue. → design gap (§3.2).
3. **The targets the loop optimizes toward are the wrong altitude.** The two audit
   metrics (`user-unblock-rate`, `revert-rate`) measure whether the *loop* is
   healthy, not whether the *factory* is delivering a good app cheaply. There is
   no north-star ladder, no token-budget guardrail, and no meta-work-subordination
   guardrail anywhere in the implemented design. The "247 events is fine, it just
   runs 200 times" failure mode is **invisible to every current metric** — that is
   the real lesson of the backlog. → the crux (§2).

The developer's instinct is correct: **targets first.** A redesign that fixes (1)
and (2) without (3) would just drain 247 events efficiently — and still be aimed
at the wrong thing.

---

## 1. Ground truth — what the live system is actually doing

Measured from the repository at task start, not inferred from the design docs.

| Observation | Value | Source |
|---|---|---|
| Optimizer runs ever executed | **0** | `state.json.total_runs`, `runs.tsv` (header only) |
| Events queued | **247** | `ls .factory/optimize/events/` |
| — `skill_changed_and_used` | **207** | filename scan |
| — `high_read_file` | **40** | filename scan |
| — `repeated_question` / `skill_change_reverted` / `periodic` | **0** | filename scan |
| Audit runs ever executed | 0 (header-only `audit_history.tsv`) | `audit_history.tsv` |
| Autonomous cycle-trigger in `run_monitors.py` | **absent** (held in `git stash@{0}`) | stash inspection |

### 1.1 Why 207 `skill_changed_and_used` events

`monitor_skill_change_first_use.detect()` emits **one event per (skill_path,
commit)** for every skill file edited inside a rolling 48h window, idempotent on
the fingerprint `path@sha`. Two compounding facts produced 207:

- **Nothing ever consumed them.** With a working consumer, each run deletes the
  selected event and the queue stays shallow. With `total_runs == 0`, every event
  ever emitted is still present (subject only to the 30-day prune, which has not
  yet bitten because the oldest event is 2026-05-28).
- **The factory was bulk-editing skills.** Almost every skill shows ~2 events: one
  for `SKILL.md`, one for the newly-added `contract.yaml`. `code-complex` shows 10,
  `code-simple` 7 — these are skills edited in many separate commits inside the
  window. The monitor faithfully recorded each (path, commit) pair. This is **not a
  dedup bug** — the fingerprint correctly deduplicates *within* a (path, sha); it is
  the absence of any *consolidation across commits to the same file*.

**Conclusion:** the event explosion is `monitor design × no-consumer`, exactly as
the plan (`_01`) hypothesized. The monitor's emission granularity (per-commit) is
wrong for a backlog: a developer who edits `code-complex/SKILL.md` ten times in two
days has produced **one** thing worth optimizing ("is code-complex healthy after
all this churn?"), not ten.

### 1.2 The two-chokepoint confusion

There are **two different "create a task" responsibilities** and the requirement
text conflates them:

- `create_optimize_task.py` — mints the **output** (the auto-blocked *improvement*
  proposal, `awaiting: ["user-unblock"]`). This exists and is tested.
- `create_optimize_cycle_task.py` — *would* mint the **autonomous cycle task**
  (`type: optimize`, `awaiting: []`) that the orchestrator picks up to *run the
  producer skill*. This is referenced by the stashed `run_monitors.py` diff but the
  module body itself is not even in the stash (untracked). This is F-1.

REQ-PROC-006 §"Monitor-Based Detection" says *"`create_optimize_task.py` creates an
optimize task"* — which is wrong on its face: that script creates the auto-blocked
*proposal*, not the cycle task. The redesign must name these two roles distinctly.

---

## 2. Seed 1 — Targets & alignment (the crux)

### 2.1 The diagnosis

The north-star the developer named is **app quality, produced efficiently within a
fixed weekly token budget**. The implemented loop measures neither. Its ten audit
criteria (`audit.py::build_rubric`) are *all* loop-hygiene proxies:

> unblock-band, revert-low, bugfix-first, no-op-streak-bounded, dimension-diversity,
> periodic-not-dominant, denylist-clean, task-folders-present, auto-block-applied,
> unblock-latency.

Every one of these can be green while the factory ships nothing and burns its whole
token budget on meta-work. The 247-event backlog is the proof: under the stashed
preempt-all trigger, the loop would have **preempted all product delivery to run
200+ times**, and the audit score would have happily climbed (diversity up,
unblock-rate computable, no denylist hits). *The metric cannot see the harm.*

This is a textbook **altitude mismatch**: the loop optimizes a process it can
directly manipulate (its own run hygiene) instead of the outcome it exists to serve
(a good app, cheaply). It is also a latent **Goodhart/reward-hacking attractor** —
the round-4 synthesis added G-INV-1/2/3 precisely to stop the loop gaming a metric,
but those guardrails protect against *self-scoring manipulation*, not against
*optimizing the wrong (if honestly-measured) thing*.

### 2.2 The target structure that fits

The developer already articulated the right shape ("every part works toward the end
goal, but in its own scope"). Formalized, that is a **three-layer objective model**:

```
            NORTH STAR  (distal, lagging, not directly actionable)
                 │   app quality delivered per token spent
        ┌────────┴────────┐
   PER-STAGE LEADING        TWO HARD GUARDRAILS (constraints, not goals)
   INDICATORS (proxies      • weekly token budget  (must-not-exceed)
   that ladder up)          • meta-work subordination (must-not-starve delivery)
```

**Layer 1 — North star (lagging, not a tuning target).** "App quality per token."
It is deliberately distal: you cannot optimize it per-run because it only becomes
measurable at release cadence (defects found, rework, release readiness) and per
billing-week (tokens spent vs work shipped). It is the *direction*, audited slowly,
never a per-cycle objective. This matches the round-4 instinct that revert-rate is
"slow cadence" — but revert-rate is still loop-local; the true lagging indicator is
**factory-local** (see 2.4).

**Layer 2 — Per-stage leading indicators (the new work).** Each factory stage emits
artifacts consumed downstream. A *valid* proxy for a stage is one where "the
artifact is better by this proxy" reliably means "less rework downstream." The
optimizer's job is to detect **degradation in these leading indicators** and propose
fixes. Candidate proxies, by stage, all computable deterministically from artifacts
already in the repo:

| Stage | Leading indicator (proxy) | Deterministic source | Ladders up because… |
|---|---|---|---|
| Requirements | AC end-state compliance (no transition-language ACs); flow-coverage gaps | `check_ac_coverage.py`, `requ-verify-flow-coverage`, grep for transition verbs | bad ACs → wrong impl → rework |
| Task derivation | tasks with empty `covers`; dependency-metadata repair rate | `generate_status_overview.py`, `task-repair-meta` runs | mis-wired deps → blocked/duplicated work |
| Implementation | quality-gate back-pressure cycles per task (G1–G8/TQ/SP); reopened tasks | `cycle_state.json`, git reopen signals | high cycles → wasted token spend per delivered AC |
| Presentation | scribble→flutter handoff rejection rate; ui-verify mismatch rate | scribble review artifacts | rejected UI → re-implementation |
| Cross-cutting (the loop's own home) | `pending_feedback` re-ask rate; skill-edit→revert rate | existing monitors | churn → instability |

This table is **illustrative, not normative** — the deliverable of the downstream
`requ-explore` is to pick the *minimum* set that (a) is cheap to compute and (b) has
a defensible ladder-up argument. YAGNI applies hard here: a proxy with no evidence
it moves the north-star is noise.

**Layer 3 — Two hard guardrails (constraints).** Per round-4's own framing,
guardrails are *hard constraints, not goals* (like G-INV-1/2/3). Two new ones:

- **G-INV-4 — Token budget.** The optimizer (and its produced/self-run work) must
  operate inside a declared weekly token budget. Made deterministic by a budget
  ledger + kill-switch (§4.3). Violating it is *unrecoverable within the week* (the
  week's delivery capacity is already spent) → by REQ-PROC-059 principle (c)'s
  irreversibility threshold, this belongs in a **hook/script gate**, not a prompt.
- **G-INV-5 — Meta-work subordination.** Meta-work (optimizer cycle tasks +
  optimizer-produced improvement tasks, once unblocked) must not preempt product
  delivery. Made deterministic by a **capacity cap** (§3.2) — e.g. optimizer work
  may consume at most X% of completed tasks in any rolling window, and an optimize
  cycle task may **never** outrank release-scoped product work. This directly
  reverses the stashed F-1 "preempt-all" surfacing.

### 2.3 Requirement-level vs tuning-constant

Following the round-4 precedent (the *mechanism* is normative; the *numbers* are
script-owned and refinable):

| Becomes requirement-level (normative, in REQ-PROC-006 / 059) | Stays a tuning constant (script-owned) |
|---|---|
| The three-layer model exists (north-star + leading indicators + guardrails) | Which specific proxies are tracked |
| G-INV-4 (token budget is a hard constraint with a kill-switch) | The weekly token number |
| G-INV-5 (meta-work may not starve delivery; cycle tasks never outrank product) | The capacity-cap % and window length |
| Leading indicators must be deterministic (extends G-INV-3 to all targets) | Band edges, thresholds, cadences |
| The audit scores against north-star-laddered indicators, not only loop hygiene | The exact rubric criteria |

### 2.4 What changes in the audit

The audit rubric stays deterministic (G-INV-3) but **gains a north-star-laddered
half**. Concretely: keep the loop-hygiene criteria (they catch loop *malfunction*),
but add criteria sourced from the Layer-2 leading indicators and the Layer-3
guardrails — e.g. "token budget not exceeded this week," "meta-work share under
cap," "at least one tracked leading indicator improved since an unblocked optimizer
task landed." This is the only way an audit can answer the developer's real
question: *"is the optimizer making the factory better, or just busier?"*

---

## 3. Seed 2 — Design critique & redesign

Five design issues, each with a concrete proposal. All reconciled with the bug
list in §4.

### 3.1 Autonomous trigger (F-1) — *keep preempting? No.*

**Current/stashed design:** `run_monitors.py` mints a `type: optimize` cycle task
when events exist; `next_tasks.py` surfaces it **ahead of the priority override**
(preempt-all). The developer's seed input already half-reversed this: *"the
priority-override will be disabled once the scribble redesign is done… the surfacing
design should target normal ranking, not a permanent override bypass."*

**Proposal:** keep the autonomous trigger (the loop must run unattended) but
**subordinate it** (G-INV-5):

- The cycle task is created with `awaiting: []` and `type: optimize` as stashed, but
  it is surfaced **below release-scoped product work**, not above. It runs when the
  queue would otherwise be idle, or under an explicit small meta-work budget — never
  by preempting delivery.
- Add a **debounce**: at most one cycle task per N completed tasks *or* per M hours,
  whichever is longer, so a burst of task-completes cannot spawn a burst of cycles.
- The cycle task is **bounded**: one run consumes a *batch* (see 3.2), commits, and
  exits. It does not loop.

This re-frames F-1 from "revive the stash as-built" to "revive the stash with
subordinate surfacing + debounce." The stash is the *starting artifact*, not the
answer.

### 3.2 One-event-per-cycle → ranked batch consumption

**Current design:** `select_candidate.py` returns exactly one event; one run = one
proposal. With a backlog this means N runs for N events and N auto-blocked tasks in
the developer's review queue. That is queue domination on *both* sides — it
dominates the autorun queue (cycle tasks) *and* the human review queue (proposals).

**Proposal — consolidate, then rank, then cap:**

1. **Consolidate before selecting.** Collapse events to their optimization *subject*
   (e.g. all `skill_changed_and_used` events for `code-complex/*` within the window
   → one candidate "review code-complex after churn"). This alone turns 207 →
   ~roughly the number of distinct skills touched (~90), and is the right semantic
   unit. Consolidation is deterministic and belongs in a script (REQ-PROC-059 (a)).
2. **Rank, don't just first-match.** Keep bugfix-strictly-first (AC-07), but within
   optimization rank by confidence × staleness × (leading-indicator impact, once
   §2 lands). Low-confidence Stage-1 `skill_changed_and_used` events should rank
   *below* high-signal events and below periodic alignment checks.
3. **Cap proposals per window (G-INV-5).** The loop produces at most K auto-blocked
   proposals per rolling window regardless of backlog depth. Excess candidates are
   left in the queue (or summarized into a single "backlog is deep" digest), not
   minted into K′ separate review tasks. This is the meta-work-subordination
   guardrail made operational on the human-review side.

**Open sub-question:** is "one auto-blocked task per friction" still the right unit,
or should a run emit **one digest** proposing the top-K frictions for the developer
to triage in a single review? The digest reduces review-queue domination and token
cost, at the cost of the clean one-task-per-friction traceability round-4 valued.
This is a framed decision (§6, D-3).

### 3.3 Unbounded event accumulation

**Current:** 30-day prune + per-(path,sha) idempotency are the only bounds. With no
consumer and wide commit-window scans, the queue grew to 247.

**Proposal:** three independent bounds, defense-in-depth:
- **Consolidation** (3.2.1) bounds *distinct candidates* structurally.
- **A hard queue ceiling**: if `events/` exceeds a ceiling, the monitor stops
  emitting low-confidence events and writes a single `queue_saturated` event instead
  (a signal that the loop is behind, not 200 more items).
- **Shorten/condition the commit-window scan**: the per-commit emission granularity
  (1.1) is replaced by per-file-per-window (one event per skill file per scan
  window, upgraded by Stage-2 evidence), so ten commits to one file → one event.

### 3.4 Stage-2 `skills_used:` trigger gap (confirmed bug)

`task-complete` step 3.4b writes `skills_used:` **only** into a file matching
`*_protocol.md`; `monitor_skill_change_first_use._stage2_used_skills()` likewise
only scans basenames containing `protocol`. Any task whose `plans_and_protocols/`
deliverable is named otherwise (e.g. this very task writes `*_synthesis_*.md`)
**silently skips** the `skills_used:` write, so skill-change events never get their
confidence upgraded from Low→Medium and rot at Stage-1. This is why 207 events are
all low-confidence Stage-1.

**Proposal:** decouple `skills_used:` capture from the protocol-filename convention.
Either (a) `task-complete` writes `skills_used:` to a dedicated, conventionally-named
file (e.g. `plans_and_protocols/skills_used.yaml`) regardless of what the narrative
deliverable is called, or (b) the writer targets the *most recent* `*.md` in
`plans_and_protocols/` and the monitor scans the same. (a) is cleaner and
script-enforceable. Folds into the redesign as a bugfix proposal.

### 3.5 Is auto-block + manual-unblock worth its token cost?

The developer raised this directly. Analysis:

- **Keep it (recommended).** G-INV-1 is the load-bearing reward-hacking guardrail
  (round-4 Part 3, arXiv 2512.23760). Its token cost is small (the developer reads a
  one-line objective and unblocks). The *real* cost was never the auto-block — it was
  the **volume** of proposals (3.2). Fix the volume (consolidation + cap) and
  auto-block is cheap.
- **But measure it.** `user-unblock-rate` already exists to detect calibration. Add
  a guardrail: if unblock-rate falls below the band for K windows, the loop is
  producing noise — it should *reduce* its proposal rate (back-pressure on itself),
  not keep minting. This makes the manual-unblock gate self-throttling.

---

## 4. Seed 3 — Bug reconciliation

| Bug | Status | Disposition in the redesign |
|---|---|---|
| **F-1** autonomous trigger absent | open (stashed) | **Survives, transformed.** Revive with subordinate surfacing + debounce (§3.1), not preempt-all. |
| **F-2** deny-list case mismatch | fixed (314ba714) | done; case-insensitive `match_deny_list` verified in code. |
| **F-3** audit `--monitor` exit-code | open, minor | **Survives.** A real defect (exit-code discrepancy) but orthogonal to the redesign; fold into the audit-skill changes (§2.4) as a small bugfix. Low priority. |
| **F-4** IMPL-I / TASK-PROC-044 dependency gate | open (TASK-PROC-006-19 explore) | **Survives, does not block.** Feeds the leading-indicator work (§2.2) — TASK-PROC-044 observability is a natural Layer-2 source. Keep as-is. |
| **skills_used Stage-2 gap** (new) | open | **Survives as bugfix** (§3.4). Root cause of the all-Stage-1 backlog. |
| **event explosion** (new) | open | **Obviated by design** (§3.2/§3.3): consolidation + per-file granularity + ceiling. Not a standalone bug to patch — a design change. |

**Which bugs are obviated vs survive:** the event explosion is *obviated* (it
disappears once consolidation + a working consumer exist). F-1, F-3, F-4 and the
skills_used gap *survive* the redesign and need explicit work — but F-1's *shape*
changes (subordinate, not preempt).

---

## 5. Seed 4 — Efficacy & the self-optimization experiment

### 5.1 Can the optimizer demonstrably improve toward its targets?

Honest answer: **not yet provable, because it has never run.** With `total_runs ==
0` there is zero evidence either way. Before any "runs on itself" experiment, the
loop must clear a **floor**: drain the current backlog *once*, under the redesigned
consumption rules, and produce a non-empty `runs.tsv` + first audit. Without that
floor the experiment has no baseline.

### 5.2 The controlled experiment design

A before/after controlled experiment, with the optimizer pointed at its **own
machinery** at higher cadence (the developer's request — "more frequently now while
it is young"):

- **Hypothesis:** running the optimizer on itself measurably improves the Layer-2
  leading indicators of the optimizer's own stage (cross-cutting row in §2.2: re-ask
  rate, skill-edit→revert rate) without breaching the guardrails.
- **Baseline (B0):** after the one-time backlog drain (5.1), snapshot the audit
  score, the leading indicators, and the week-to-date token spend.
- **Intervention:** raise the optimizer cadence for a fixed, bounded experiment
  window (e.g. one billing-week or N cycle tasks, whichever first), restricted to
  optimization-targets within the optimizer's own surface — *except* the deny-list,
  which still protects `claude-optimize/SKILL.md` itself (self-modification stays
  blocked; G-INV via deny-list).
- **Measurement:** re-snapshot the same metrics. Success = leading indicators
  improved OR held while unblock-rate stayed in band, AND no guardrail breach.
  Failure = any guardrail breach, unblock-rate out of band, or a revert of an
  optimizer-produced self-change.
- **Guardrail metrics that ABORT the experiment** (not just score it): token
  kill-switch tripped (§4.3 → 5.3), meta-work share over cap, or two consecutive
  reverts of optimizer self-changes.

### 5.3 The token kill-switch (hard requirement for the experiment)

A deterministic budget ledger + circuit breaker, script-owned (REQ-PROC-059 a/c):

- A ledger accumulates token spend attributable to optimizer cycle tasks + unblocked
  optimizer-produced tasks within the current billing-week.
- **Soft cap** (e.g. 50% of the week's meta-work budget): the loop stops creating
  *new* cycle tasks and emits a `budget_soft_cap` digest instead of proposals.
- **Hard cap** (the kill-switch, e.g. 100% of the meta-work budget): a gate refuses
  to create or route any `type: optimize` task for the rest of the week; the
  experiment aborts and writes a `budget_kill_switch` record. Because over-spend is
  unrecoverable within the week (G-INV-4), the hard cap is a **hook/script gate**,
  not a prompt instruction.
- The exact token numbers are tuning constants (developer owns them — §6, D-2); the
  *existence* of soft cap + hard cap + abort is normative.

### 5.4 Honest caveat on measurability

Token attribution is imperfect: the harness bills at the session level, and an
automated session may interleave optimizer work with other tasks. The ledger will be
**best-effort and conservative** (over-attribute to the optimizer rather than under),
mirroring the round-4 "runs.tsv canonical, JSONL best-effort" stance. The kill-switch
must therefore err toward stopping early. This is a real limit, stated plainly.

---

## 6. Decisions the developer owns (framed, not assumed)

These are value-laden; the analysis cannot settle them. Each is framed so the
developer can decide, with a recommendation.

- **D-1 — North-star operationalization.** Adopt the three-layer model (§2.2) and
  the *illustrative* Layer-2 proxy set, or a narrower set? *Recommendation:* adopt
  the model normatively; let the downstream `requ-explore` pick the **minimum**
  evidence-backed proxy set (YAGNI), starting with 2–3 stages, not all five.

- **D-2 — The weekly token budget number(s).** What is the weekly token budget, and
  what fraction of it may meta-work (the optimizer) consume? *Recommendation:* the
  developer sets both; the loop enforces them via §5.3. Without a number the
  guardrail G-INV-4 cannot be made deterministic.

- **D-3 — Proposal unit: one-task-per-friction vs one digest-per-run.** Keep the
  clean one-auto-blocked-task-per-friction model (round-4), or switch to a single
  ranked digest per run to cut review-queue domination and token cost?
  *Recommendation:* digest for *low-confidence* optimization candidates, individual
  tasks for *bugfix* candidates (preserves traceability where it matters most).

- **D-4 — Self-run aggressiveness.** How aggressive is "more frequently now while
  young"? Cadence multiplier and experiment-window length? *Recommendation:* one
  bounded experiment window (one billing-week or N=20 cycle tasks, whichever first),
  hard-capped by the kill-switch, restricted to the optimizer's own non-deny-listed
  surface.

- **D-5 — F-1 surfacing reversal.** Confirm the reversal from preempt-all to
  subordinate-below-product-work (§3.1). *Recommendation:* confirm — it is required
  by G-INV-5 and consistent with the developer's own "normal ranking" seed input.

---

## 7. Honest uncertainty

- **No runtime evidence at all.** Every efficacy claim is a prediction; `total_runs
  == 0`. The §5.1 floor (one real drain) must happen before the experiment, or there
  is nothing to measure against.
- **Leading-indicator validity is unproven.** The §2.2 proxies are *plausible*
  ladders, not measured ones. A proxy that doesn't actually move the north-star is
  worse than no proxy (Goodhart). The downstream work must keep each proxy on
  probation until evidence shows it correlates with reduced rework.
- **Token attribution is best-effort** (§5.4). The kill-switch protects the budget
  but cannot perfectly attribute spend.
- **Consolidation semantics need care.** Collapsing events by "subject" (§3.2.1) is
  the right idea but the exact equivalence key (per-skill? per-skill-per-dimension?)
  affects both recall and queue depth; needs a small design pass in the impl task.
- **Web-research integrated (§8); refinements applied, not reversed.** External
  prior-art sharpened four mechanisms (GQM proxy-validity, budget-freeze
  subordination, cost-velocity breaker, OEC auto-abort) but the token-budget dollar
  thresholds in that literature are illustrative — the developer's actual weekly
  number (D-2) is the only authoritative input.

---

## 8. Web-research integration (Seed-1 ground)

A focused `general-purpose` agent researched the four genuinely-new questions
(objective laddering, meta-work subordination, token-budget guardrails,
self-experimentation safety). The findings **validate the §2–§5 structure and
sharpen four mechanisms**. Sources are primary where it matters (Basili GQM,
Amplitude/Reforge, Google SRE Workbook, METR, Anthropic, Kohavi); the token-budget
dollar thresholds come from 2026 practitioner blogs and are illustrative, not
authoritative.

### 8.1 Objective laddering — adopt GQM as the anti-Goodhart device (sharpens §2.2)

The strongest finding: **GQM (Goal-Question-Metric)** gives the missing validity
test for Layer-2 proxies. The *Question* layer is the anti-Goodhart guard — a metric
is legitimate **only if it answers an explicit chartered Question that ladders to
the Goal**; "always a purpose with the defined measurement" (Basili/van Solingen).
This is stronger than my §2.2 table, which listed proxies without their Questions.

**Adopt:** every Layer-2 proxy must be written as `Goal → Question → Metric`, not
as a bare metric. Example: *Goal: implementation stage wastes few tokens per
delivered AC. Question: are tasks bouncing through many quality-gate cycles before
landing? Metric: median back-pressure cycles per completed task (`cycle_state.json`).*
A proxy with no chartered Question is dropped.

The **North-Star + 3–5 input-metric** frame (Amplitude/Reforge) confirms the
altitude split (§2.2 Layer-1 vs Layer-2) and the cap: **≤3–5 proxies per stage**,
and "inputs that don't drive the output are discarded quickly." This is exactly the
§7 probation stance, now with a source. **Validity = falsifiability**: keep a proxy
only while evidence shows moving it moves the north-star; **give each proxy an
expiry/review date** (Goodhart literature — proxy decay is normal; surrogation
appeared in ≥70% of failed OKR efforts).

**New concrete rule for §2:** *pair every throughput/speed proxy with a quality
counter-proxy* (volume + NPS, speed + quality). For the optimizer this means: never
track "proposals produced" without also tracking "proposals reverted/rejected."
The existing unblock-rate + revert-rate pair is already an instance of this — it
should be the *template* for every stage, not an exception.

### 8.2 Meta-work subordination — budget with an auto-trip, not a nag (sharpens §2.2 G-INV-5, §3.2)

Google SRE's **50% toil cap** is the closest prior art to G-INV-5, with one
critical honest caveat the agent surfaced: **the % cap is advisory unless you attach
a tracked metric *and* a defined consequence.** SRE makes it real two ways worth
stealing:

- **Redirect-on-breach:** when ops work exceeds the cap, the overflow *bounces back*
  to whoever creates it. Optimizer analog: when meta-work exceeds its cap, the loop
  **stops creating cycle tasks and emits a digest** (§3.2.3) rather than continuing
  to mint — the overflow is "redirected" to a single human-triage item.
- **Error-budget freeze-switch:** budget = 1 − SLO; while budget remains, work
  proceeds freely; **once spent, all change freezes** (binary, automatic, not a
  nag). This is the template for G-INV-4/5 enforcement: model both the token budget
  and the meta-work cap as **budgets with an automatic freeze trip point**, not as
  soft guidance. Plus a **hard WIP limit** on simultaneously-open optimizer tasks.

This directly resolves an ambiguity in §2.2: G-INV-5 must be encoded as a *budget
with a freeze*, and the redesign's "cap K proposals per window" (§3.2.3) is that
freeze made concrete.

### 8.3 Token guardrail — add a cost-velocity breaker (sharpens §5.3)

The canonical agent-budget stack is **multi-layer**: (1) per-request ceiling +
turn counter, (2) total budget cap, (3) **cost-velocity circuit breaker**, (4)
cost-routing fallback, (5) alerts. My §5.3 had only the cumulative soft/hard cap —
it is missing layer (3). The agent's sharpest point: **a single total cap lets a
fast loop burn the budget before the cap notices**; the breaker must also fire on
*pattern* — "2–3 consecutive identical/near-identical tool calls with no progress,"
cost velocity, or monotonically growing context (AgentGuard, METR-adjacent).

**Add to §5.3:** a velocity breaker (e.g. trip if optimizer token-spend-rate exceeds
$X/hour-equivalent, or on repeated no-progress cycle tasks) **in addition to** the
cumulative soft/hard caps. The kill-switch tracks *time + tokens + tool-pattern
together*, and never relies on the agent "deciding it's done."

### 8.4 Self-experimentation — OEC + auto-abort guardrails; scorer ≠ scored (sharpens §5.2)

The reward-hacking evidence is concrete and supports keeping G-INV-1/2/3 *and*
hardening the self-run:

- METR (Jun 2025): frontier agents reward-hack at **30.4% on RE-Bench** (up to
  100% per task), modifying tests/scoring or accessing answer keys. Anthropic
  (2024): models edited their own reward mechanism **45/32,768 trials (~0.14%)**.
- The defense is exactly the §5.2 design plus two additions: **(a) keep
  metric-computation write-protected and separate from the artifact under
  optimization** (the deny-list already protects `claude-optimize/SKILL.md` and
  `audit.py` lives in `scripts/optimize/` — confirm both stay deny-listed during the
  self-run); **(b) manually review suspiciously-high self-scores and *exclude*
  (don't credit) hacked wins** rather than trusting the score.
- **Kohavi's OEC + guardrails** formalizes §5.2's success/abort criteria: ship/credit
  the self-change only when the **OEC improves AND no guardrail regresses**;
  guardrails (primary-delivery throughput, token spend, quality gates) **auto-abort**
  the experiment even when the headline metric looks good. This is the precise
  framing for §5.2's "guardrail metrics that ABORT."

### 8.5 Net effect on the proposal

Nothing in §2–§5 is reversed; four things are added and now sourced:
1. GQM `Goal→Question→Metric` form is **mandatory** for every Layer-2 proxy, with an
   expiry date and a paired counter-proxy (§8.1).
2. G-INV-4/5 are encoded as **budgets with an automatic freeze trip**, with
   redirect-on-breach and a WIP limit (§8.2).
3. The token kill-switch gains a **cost-velocity + no-progress-pattern breaker**
   alongside the cumulative caps (§8.3).
4. The self-run is governed by an **OEC + auto-abort guardrails**, with the scorer
   kept write-protected and hacked wins excluded (§8.4).

---

## 9. Handoff — what happens after this synthesis

This synthesis is sized to feed, in order:

1. **`requ-explore` on REQ-PROC-006 (+ possibly REQ-PROC-059)** — to make normative:
   the three-layer target model, G-INV-4 (token budget), G-INV-5 (meta-work
   subordination), the deterministic-leading-indicator constraint, and the audit's
   north-star-laddered half (§2.3 table, left column).
2. **`task-derive-from-requ`** — to mint the redesign tasks: consolidation +
   ranked-batch consumer (§3.2), per-file monitor granularity + queue ceiling
   (§3.3), skills_used decoupling bugfix (§3.4), subordinate F-1 trigger (§3.1), the
   token-budget ledger + kill-switch (§5.3), F-3 audit exit-code bugfix, and the
   audit-rubric extension (§2.4).
3. **The self-optimization experiment** (§5) — only after the §5.1 floor drain and
   the kill-switch exist.

The value-laden decisions (§6) should be resolved by the developer **before**
step 1 finalizes the requirement amendments.
