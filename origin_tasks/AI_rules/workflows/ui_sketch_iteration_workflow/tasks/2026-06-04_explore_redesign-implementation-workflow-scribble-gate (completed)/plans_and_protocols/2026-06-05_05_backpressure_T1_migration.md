# Back-pressure report — T1: migrating the existing release 0.0.1 tasks

Task: TASK-PROC-032-29. Date: 2026-06-05.
Developer's words: *"once the new skill process is implemented, how do we migrate the currently existing
tasks? release-begin-impl was called for release 0.0.1, task-derive-from-requ completed for that release.
there are even one or two coding tasks already started. additionally we can't be sure that enough scribble
tasks exist for 0.0.1. delete all tasks and start release-begin-impl again? costs a lot of tokens."*

Grounded state at time of writing: `releases/0.0.1/` exists but holds only `size_analysis/` (no activated
release manifest visible); started/`in_progress` Presentation-coupled coding tasks include
`feat_therapist_transfer_ui/.../impl_client-send-screen-scribble` and
`feat_plan_export/.../impl_plan-export-qr-screen`. The clean-rerun-decision (`01_…`) only waived
backward-compat for the **pilot** TASK-FUNC-007-01-05 artifacts — **not** for the whole 0.0.1 release. So
0.0.1 migration is a genuine, un-answered gap.

---

## Level 1 — the topic as a whole

### The rationale being pressured
The implicit rationale behind "delete all and re-run `release-begin-impl`" is: *the old plan was authored
under the old (blind) model, so it is all suspect; the cleanest correctness guarantee is to throw it away and
regenerate under the new two-wave model.*

### What speaks against it
1. **It destroys valid work.** Under the new model, Wave 1 itself creates pure-domain coding tasks (no
   scribble) and the scribble tasks. A blanket delete throws away exactly the artifacts the new model would
   re-create identically — you pay full re-decomposition tokens to rediscover the same answer.
2. **It conflates "authored blind" with "wrong."** A coding task is only invalidated by the new model if it
   is *Presentation-coupled* **and** was decomposed before its scribble existed. Pure-domain tasks were never
   gated on a scribble — they are correct as-is. Most of a release's task count is often domain/infra.
3. **"Costs a lot of tokens" is the developer's own stated objection** — and delete-all is the
   most-tokens option. The framing already contains the refutation.
4. **It is not even necessary for correctness.** The redesign ships a *standing detector* for precisely this
   rot: the SCI audit (Round-1 §4.2). Correctness is achieved by *detecting and quarantining* the bad
   entries, not by destroying the good ones.

### How to do it differently
Reframe migration from *"re-run the producer"* to *"run the auditor + reconcile the delta."* The new model's
SCI audit + flow→scribble coverage report (PROP-9) are exactly a migration toolkit when pointed at an
existing plan:

- **Classify** every existing 0.0.1 plan entry into `{scribble, pure-domain-code, presentation-code}` (the
  `task_type` field + the design-unit map already carry enough signal).
- **Keep** all `scribble` and `pure-domain-code` entries untouched.
- **Coverage-check** (PROP-9): list Presentation requirements with no scribble task → *create only the
  missing scribble tasks*. This is the direct answer to "we can't be sure enough scribble tasks exist."
- **Quarantine** `presentation-code` entries authored before their scribble: do **not** delete; set them
  blocked/`awaiting` on the (new or existing) scribble task via the SCI edge. When the scribble approves,
  `release-derive-code` re-derives them — and a diff against the quarantined entry shows whether the original
  decomposition survived (often it largely does; the scribble rarely changes the *existence* of a screen,
  only its details).

### How to improve it further
- **Make migration a first-class, scripted, idempotent step**, not a manual judgement call —
  `scripts/release/migrate_plan_to_two_wave.py` (proposed) that emits a reconciliation report (kept /
  created / quarantined) for developer sign-off before mutating anything. One-time, auditable, cheap.
- **Tie it to the SCI audit so it is not bespoke:** migration is just "the SCI audit, run once against a
  pre-redesign plan, with a create-missing-scribbles step bolted on." Same detector, reused.

### The prior question the developer didn't ask but should
*Should 0.0.1 be where the new workflow makes its debut at all?* Debuting an unproven workflow on the real
release couples two risks (workflow bugs × release pressure). T2/`10` recommend validating on a cheap
fixture first, then migrating 0.0.1 with a *known-good* workflow. That makes the migration low-risk: you are
no longer simultaneously debugging the workflow and migrating the release.

---

## Level 2 — chapter by chapter (each clause of the feedback)

### "release-begin-impl was called for 0.0.1"
- **Pressure:** was the release ever *activated* (Phase 6) and an orchestration chain spawned? Grounded check:
  `releases/0.0.1/` shows only `size_analysis/` — no activated manifest. If the release is **not** activated,
  the only artifact is the *plan*; there is no running chain to unwind, and discarding/regenerating the plan
  is cheap. The expensive case (a live chain mid-flight) may not even apply.
- **Action:** the migration script's first step is *detect activation state* and branch (plan-only reconcile
  vs. live-chain reconcile).

### "task-derive-from-requ completed for that release"
- **Pressure:** the plan is a *structured file*, not opaque state. Reclassification is a parse + label pass,
  not an LLM re-decomposition. The expensive thing (deciding `covers_acs`, `effort`, grouping) was already
  paid once and is mostly reusable.
- **Action:** treat the existing plan as input to reconcile, not garbage to discard. Only Presentation-code
  groupings get re-derived (post-scribble); scribble + domain groupings are kept verbatim.

### "there are even one or two coding tasks already started"
- **Pressure:** these are the only genuinely expensive artifacts. Decide per task:
  - *pure-domain* → **keep, no change** (never gated on a scribble).
  - *Presentation-coupled, scribble exists & approved* → **keep**; verify against the approved scribble (SCI
    audit). If consistent, done; if not, it's a scribble-refresh / L6 case.
  - *Presentation-coupled, no approved scribble* → **SCI violation**. Don't delete — *pause* and block on a
    scribble task. Partial work may still be salvageable once the scribble lands.
- **Action:** the started tasks get individual SCI verdicts, not a blanket fate. The grounded candidates
  (`impl_client-send-screen-scribble`, `impl_plan-export-qr-screen`) are both Presentation — they are the
  first SCI test cases.

### "we can't be sure enough scribble tasks exist for 0.0.1"
- **Pressure:** this is *exactly* the gap PROP-9's flow→scribble coverage report was designed to surface.
  Uncertainty here is a missing report, not a reason to rebuild.
- **Action:** run the coverage report on 0.0.1 → deterministic list of missing scribble tasks → create only
  those. The uncertainty dissolves into a checklist.

### "delete all tasks and start release-begin-impl again? costs a lot of tokens."
- **Pressure:** this is the false dichotomy. The hidden third option (scripted reconcile) is both cheaper
  and *more* correct (it preserves audited-good work and quarantines only audited-bad work). Delete-all is
  strictly dominated.
- **Action:** adopt reconcile-not-rebuild as the migration model; spec the script; gate its report on
  developer sign-off.

---

## Residual uncertainty (honest)
- **How much Presentation-code decomposition actually survives re-derivation** is unknown until measured —
  the quarantine→re-derive→diff loop assumes the scribble rarely changes a screen's *existence*; if 0.0.1
  scribbles turn out to restructure flows heavily, the salvage rate drops and the token saving over
  delete-all narrows. The reconcile is still safer (no valid work destroyed), but the token win is unproven.
- **Live-chain mid-flight reconcile** (if 0.0.1 *is* activated) is more delicate than plan-only and is
  un-designed here — it depends on whether the orchestration chain can be paused and re-seeded without losing
  `after`-edge integrity. Needs its own mini-design if activation turns out to be true.
- Whether to migrate 0.0.1 *at all* before the workflow is validated is the T2 coupling — see `10`.
