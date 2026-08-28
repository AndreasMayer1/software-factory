---
task: TASK-PROC-068-10 (iteration 2 of loop PROC-068-playground-captest-loop)
session: 970697fe-b232-417b-99f7-3d0a00bc64c7
account: gmail2
date: 2026-06-30
model: Opus 4.8
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - task-resolve
  - claude-log
  - task-complete
  - claude-commit
---

# Protocol — Iteration 2: one capability-test run over the playground harness + Work Discovery

## Part 1 — The capability-test run (AC-1, AC-2)

### Fixture discovered (loop "discover" step)

- **Governed artifact under test:** `test_harness_app/requirements_user_needs/user_flows/FLOW-HARNESS-01_add_rating/flow.md`
  (the 068-07 layer-derivation-generated harness flow; covered_by REQ-HARNESS-FORM).
- **Why this artifact:** small (16 lines), self-contained, and `covered_by: REQ-HARNESS-FORM`
  whose AC-02 states "Title and rating are required; the remaining fields are optional" — giving a
  ground-truth constraint against which a controlled in-scope defect can be injected and known.
- **No natural git old-vs-new pair exists:** every harness governed artifact was created in a single
  commit (849a39a5, TASK-PROC-068-07), so the matched pair had to be **produced** — exactly the goal's
  discover step ("run a factory skill to produce a revised version … against the version 068-07 generated").

### Matched pair formed (the factory capability exercised)

The factory capability under test = a **flow-revision** of the 068-07 artifact. Two versions of the same
governed flow, both judged fresh under the current model (regression-gate framing, REQ-PROC-073-01):

- **OLD (clean, = 068-07 version):** Quick-Logger branch reads *"fills only the required minimum (speed)"*
  → faithful to the form contract (required minimum = title **+** rating).
- **NEW (defective revision):** Quick-Logger branch reads *"enters only a title and saves immediately
  (speed)"* → omits **rating**, which the same document's body declares required.

**Ground truth (known by construction):** NEW carries one injected defect of demonstrated-scope kind
**#2 — instruction-following semantic contradiction** (the branch asserts a successful save through a
state the form's required-fields clause forbids; also breaks the `covered_by: REQ-HARNESS-FORM` contract).
OLD is clean.

### Oracle run (REQ-PROC-073-01 procedure — disproof-spike recipe)

Blind A/B `claude -p --output-format json --model opus` judge, no diff/hint, both full files given as
Version A / Version B, prompt asking for the single most significant quality difference + which is better
+ why. **Swap-and-average:** two runs, A/B order swapped to control position bias. Runner: `/tmp/captest/`
(throwaway, per spike reproducibility recipe). Config dir: `/home/vscode/.ccs/instances/gmail`.

| Run | A / B | Judge picked better | Detected the defect? |
|-----|-------|---------------------|----------------------|
| run1 | A=OLD(clean), B=NEW(defect) | **A** (clean) ✅ correct | **YES** — named Quick-Logger "title only" branch contradicting the "title + rating required" clause two lines above; flagged broken happy-path + broken `covered_by` traceability |
| run2 | A=NEW(defect), B=OLD(clean) | **B** (clean) ✅ correct | **YES** — same mechanism, same conclusion |

**DETECTION outcome: ✅ unanimous (2/2), position-robust (always preferred the clean version regardless
of A/B slot → no position bias), mechanism-precise** (identified the exact injected contradiction and its
two downstream consequences — internal consistency + coverage-integrity — not merely "a wording diff").

### Real cost

| Metric | Value |
|--------|-------|
| Total cost (sum of 2 runs) | **$0.131** (run1 $0.0658 + run2 $0.0648) |
| API duration (sum) | **~24.7 s** (run1 12.5s + run2 12.2s) |
| Human attention | **0** (fully automated) |
| Per-run tokens | in≈2.87k, out≈0.75–0.79k |

(Lower than the disproof spike's $0.55 / 37s — the harness flow is 16 lines vs. the spike's 435-line skill.)

### Interpretation (bounded by the caveats below)

The oracle correctly detected and mechanism-explained one in-scope (kind #2) defect over a harness
governed artifact, position-robust, for $0.13 / ~25 s / zero human attention. This is **one** qualitative
demonstration over the playground — consistent with, and bounded by, the maturity walk's demonstrated
scope. It is **not** a statistical reliability claim (see caveat 1) and does not extend the demonstrated
defect-kind set (caveat 3).

## Part 2 — The five mandatory ADVISORY caveats (carried forward VERBATIM)

The capability-tester / oracle whose verdict this run consumes established only a **qualitative,
advisory** discriminating scope. These five caveats accompany the verdict above and MUST accompany every
downstream use of it. Source: `…/feat_regression_gate/tasks/2026-06-27_verify_discriminating-maturity-walk (completed)/plans_and_protocols/2026-06-27_02_verdict_maturity-walk.md` §"Mandatory advisory caveats".

1. **Corpus N=3 ≪ floor_n=100.** Demonstrated scope is qualitative, not statistical — the oracle *can*
   detect defects of the demonstrated kinds, not how reliably it does so at scale.
2. **Pairs above the termination point are not authoritative.** Future corpus pairs ruled "too hard"
   sit outside the demonstrated scope.
3. **Demonstrated scope is the demonstrated *set*, not a generalized capability claim.** Verdicts on
   defect kinds outside { control-flow contract violation; instruction-following semantic
   contradiction } remain advisory until extended by additional walks.
4. **Calibration (REQ-PROC-044-05) is not established.** Even within scope, verdicts are not
   Human-Judgment-Register-calibrated and cannot displace human judgment on consequential decisions.
5. **Artifact-level oracle, not behavioural.** The oracle judges artifact text without executing it;
   the stronger behavioural oracle is not exercised and its discriminating scope must be established
   separately.

> The detection verdict above is **advisory** and does not displace human judgment. The injected defect
> was of demonstrated kind #2 (within scope); this run neither generalizes the scope nor establishes
> statistical reliability or calibration.

## Part 3 — Work Discovery (AC-02)

### A. Orient & test termination FIRST (AC-10, AC-17)

Loop ridge (from `…/2026-06-30_impl_autonomous-test-runs-ralph (completed)/plans_and_protocols/loop_context.md`):
- end_goal: autonomously discover/author/run capability tests over the playground harness, driving its
  capability-testing coverage toward completeness, every verdict under the five ADVISORY caveats.
- termination_condition: no remaining in-scope, externally-justified capability-test work over the
  playground (next_tasks.py surfaces no externally-justified unblocked candidate) OR `iteration ≥ loop_ceiling`.
- iteration = **2**, loop_ceiling = **12** → 2 < 12, ceiling not reached.

**Termination evaluated against real project state → see value gate (C).**

### B. Minimized signals scanned (AC-18)

- `next_tasks.py` (top candidates) — see decision below.
- Sibling terminal-batch tasks: **TASK-PROC-068-09** (verify gate, `after: [068-07, 068-08]`) and
  **TASK-PROC-068-03** (finalize terminus, `after: [068-09]`).

### C. Value gate — decide WHETHER to author (AC-20) → **NO-OP (apoptosis default)**

The single external value signal that justified iteration 1's authoring was the **terminal-batch
mandate**: verify gate **TASK-PROC-068-09 AC-2** requires "≥1 autonomous capability-test run driven over
the playground via the perpetuating mechanism." **That mandate is now satisfied by THIS run** — the ≥1
landed capability-test run exists (Part 1 above). With the verify gate's requirement met, there is **no
remaining external value signal** (no requirement priority, no active-release scope, no persona need)
that justifies authoring a *further* capability-test run over the harness:

- Authoring another run purely to grow harness capability-test coverage would be a **self-referential
  coverage-delta**, which the value gate (AC-20) explicitly forbids as a justification.
- The natural next step in the batch is the **verify gate (068-09)** confirming this landed run, then the
  **finalize terminus (068-03)** — both already exist; neither is a capability-test run this loop should author.

→ The termination condition's spirit is met: **no externally-justified capability-test work remains** for
the loop to author. Resolve to the documented **no-op (apoptosis default)** — the loop ends gracefully
here. (Per AC-06 a dedup check never silently ends the loop; this is a *value-gate* no-op with the reason
recorded, not a silent termination.)

### D. Deduplicate (AC-06)

Not reached for authoring (value gate resolved to no-op). For completeness: 068-09 is a verify gate and
068-03 a finalize terminus — neither is an equivalent perpetuating capability-test-run task, so no dedup
upgrade/sequence path applies. No follow-up authored.

### E–F. Author follow-up

**Skipped** — value gate resolved to no-op. No follow-up task authored.

### G. Record & complete

Basin row appended to loop_context.md (no-op, reason: external mandate satisfied by this run → no further
externally-justified work). Task closed via `task-complete`.
