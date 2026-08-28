# 🛑 SESSION HANDOFF — TASK-PROC-068-01 → next session — READ THIS FIRST, IN FULL

> Supersedes `2026-06-23_08_HANDOFF_next-session.md`. That handoff's **STEP 1 (iterate 066-06) and STEP 2
> (reconcile to REQ-PROC-073) are now DONE** — completed by the 2026-06-24 Deep ideation run on
> TASK-PROC-066-06. This handoff carries the **requirement-update + task-derivation instructions** for the
> remaining work (STEP 3–5), grounded in that run's accepted result.

## ✅ WHAT HAPPENED (2026-06-24, interactive, Opus)
A full Deep structured-ideation run deepened the playground concept (TASK-PROC-066-06) and **was developer-accepted**.
- **Run artifacts (cite by path — do NOT copy detail out; fidelity-gradient):**
  - Synthesis (the composed design): `…/tasks/2026-06-09_explore_skill-test-playground-full-scope/plans_and_protocols/2026-06-24_007_synthesis_playground-deepened.md`
  - Final report (decision + red-team): `…/2026-06-24_008_final_report.md`
  - Ledger (334 ideas, scored): `…/2026-06-24_004_ideation_ledger.yaml` (+ `.html`)
  - Indexed as **IDEATION-007**.
- **Decided design = `SOL-01`** (composition, K=1): worktree-per-invocation walking-skeleton; reuses
  `scripts/automation/orchestrate.py::_launch_claude_session` as the single child-session boundary; sealed
  versioned **EvidenceBundle** → the **un-redesigned REQ-PROC-073 oracle** via a matched-pair A/B judge; free
  per-account cost ledger under a hard `max_budget_usd` cap. The 10–100× premise is **deferred to a disproof
  spike** (the skeleton's first job, gating a stop-loss go/no-go).
- **Rubric the developer shaped:** four **knockout floors** (usefulness, feasibility, discriminating_quality,
  child_session_safety, each ≥3/5) + **token_economy 3.0 & human_time_saved 3.0 as co-equal weighted primes**.
  This is the standing lens: *minimise the mechanism's token cost AND the developer's residual time; never below
  the quality/safety floor.*
- **⚠ FOUR FIRST-BUILD GATES (accepted from the synthesize-gate red-team — bake into the impl task goals):**
  1. **SG-01** `_launch_claude_session` is NOT a clean reusable API (needs `OrchestratorDeps`+`state.json`/`inbox.md`/
     `stop_flag`; `run_session_with_hung_detection` hardcodes the *current* project's JSONL path). → Build a real
     **adapter**: extract the launch core from its orchestrator-global deps; parameterise the JSONL/observe path on
     the **child's cwd**. (Not a "thin facade".)
  2. **SG-04** worktree-per-invocation does **not** close CON-04's absolute-path cwd-escape. → **Re-instate one
     OS-level containment layer** (separate OS user / `namespace-unshare` — these ideas exist in the ledger,
     NUF-dropped for cost) so `child_session_safety` truly clears its floor.
  3. **SG-03** walking-skeleton-first cannot reach the ~100-paired-example A/B validity floor at the spike. →
     Commit a **fixture-validity path** (accumulate paired fixtures over time; pairwise win-rate + variance bands;
     scope the *skeleton-stage* verdict as **advisory** until N ≥ floor).
  4. **SG-02** verify that `claude -p --bare --output-format json` still emits `total_cost_usd` (or use non-`--bare`)
     — SP-03's whole cost ledger depends on it. Cheap; fold into the disproof spike.

---

## ➡️ STEP 3 — UPDATE REQUIREMENTS (use `requ-explore`; **EGP-align every new AC**, developer present)

> **EGP alignment is mandatory** (developer directive): the L2 rubric dimensions ARE the EGP archetypes
> (r3 §5.4). Every new/edited AC screens for its archetype; **archetype-S (safety) ACs are unconditionally
> HIGH-consequence and need explicit developer sign-off** (child-session isolation, untrusted candidate).

**3a. REQ-PROC-073 (Capability-Testing Oracle epic)** — author its features (`## Features` already lists the intent):
- `feat` Tiered rubric & Capability-Test Descriptor (L1–L4 + descriptor + fixture interface) — archetypes Q/I/F.
- `feat` Old-vs-new regression gate (matched-pair A/B, weighted+knockout aggregation, VTR admissibility) — incl. **SG-03** fixture-validity path.
- `feat` Lifecycle embedding (descriptor authored at create; regression on modify; the ASK-the-developer gate).
- `feat` Behavioural-contract testing (task-battery / chain-level for CLAUDE.md, ordering rules, orchestrator).
- The detailed mechanism is **by reference** to the r3 synthesis (`2026-06-21_04_…`, §1–§14) — copy no mechanism detail (epic-gate ≤90 lines / requ-explore fidelity rule).

**3b. REQ-PROC-068 (Skill-Test Playground substrate)** — this is where the **SOL-01 substrate** lands (068 supplies the substrate; 073 is the oracle):
- **Cross-reference AC** (was STEP 4): the playground **hosts** capability tests (the substrate relationship REQ-PROC-073 declares).
- Substrate ACs from SOL-01: child-session control/observe/reset (SP-01), deploy→run-as-cwd→git-reset + two-tree split + fixture library (SP-02), token+human-time cost model + cap/ledger (SP-03) — archetypes C (cost) + **S (child-session safety, sign-off)**.
- AC-01 structural mirror (P1) + the minimal WI-6 AC additions (`IDEA-SP05-55`/`09`).
- The **15-WI → composed-backlog fate map** is in synthesis §5 (machine-readable migration manifest) — use it verbatim for the AC set; WI-3 absorbed, WI-2 unbundled (SP-01/SP-02), WI-5 re-homed under 073, **REQ-PROC-06x dropped (reserve-then-release in id_registry, never mint)**.

**3c. Cross-references (one AC / note each, per r3 §11):**
- **REQ-PROC-044-01** — the four meta-skills author/update a descriptor and run the old-vs-new regression on modify.
- **REQ-PROC-044-04** — a capability test IS the EGP oracle for the tested artifact's declared archetypes (no new EGP mechanism).
- **REQ-PROC-044-05** — the Human-Judgment Register is the judges' calibration source + home of the ratified anchors (ADV-01 disposition: calibration is a declared 3-state stage — defer/stub/satisfy — stamped as `calibration_state`; uncalibrated = advisory).
- **REQ-PROC-055** — selective-adopt the skill-creator schemas (evals/grading/comparison/history JSON→YAML) + `THIRD_PARTY_NOTICES.md` (Q-D).

---

## ➡️ STEP 5 — DERIVE TASKS (`task-derive-from-requ` for AC-backed; `task-create` otherwise; EGP dispositions in each goal.md)

**Sequence (thin-slice, stop-loss governed — synthesis §5 build-out order):**
1. **Disproof spike** (the 10–100× premise + **SG-02** cost-capture check) — `after: []`. A controlled `claude -p` run on a known-regressing fixture; **gates go/no-go for everything below.**
2. **P1 structural mirror** (WI-1) — `test_harness_app/` → factory project (CLAUDE.md/.claude/`requirements_*`/`factory_tests/`). `after: []`. Cheap, unblocks all.
3. **P2 execution & reset protocol** (SP-01 control/isolation + SP-02 deploy/reset/fixtures) — `after: P1`. **The long pole.** Bake in **SG-01 adapter** + **SG-04 OS-containment**.
4. **Cost/ROI substrate** (SP-03) — `after: P2` (needs the cost stream). Multi-account reconciliation (ADV-02).
5. **Walking-skeleton single-cell loop** (SOL-01 first end-to-end deploy→run→reset→assess→cost) — `after: P1, P2`.
6. **Oracle integration** (SP-04 EvidenceBundle → REQ-PROC-073) — `after: P2` + 3a features authored. Bake in **SG-03** fixture-validity.
7. **EGP backfill (P3)** on the capabilities under test (e.g. `ideation-start` has no `contract.yaml`) — `after: []`, parallel.
8. **HJR query interface (P4)** — REQ-PROC-044-05 AC-03/AC-04 — parallel; judge calibration activates late.
9. **REQ-PROC-055 adoption task** (Q-D).
- **AC-07 chain ordering (MUST hold):** oracle impl/verify tasks set `after` the playground-build tasks; the extraction tasks (TASK-PROC-066-01) set `after` the **oracle-verify** task.
- **Portability (CTX-02):** classify the mechanism **factory-general** in the extraction boundary map; `test_harness_app/` is the factory's own self-test fixture; consuming projects supply their own descriptors+fixtures.

---

## ⛔ DO NOT REOPEN / CONTRADICT (carried + new)
- The REQ-PROC-073 **oracle is committed and design-complete** — integrate, do NOT redesign (CON-09).
- Unit = ANY governed instruction artifact. Regression = old-vs-new blind A/B. Descriptor authored INLINE at create.
- Cost = token consumption **and** net human time saved (co-equal), never below the discriminating-quality/safety floor.
- The four first-build gates (SG-01..04) are **accepted corrections**, not open debates — bake them in; the design *direction* is settled.

## 🧹 HOUSEKEEPING
- TASK-PROC-066-06 is being **completed + committed** this session (its ideation produced the accepted SOL-01 + reconciliation). `writes_requirements:false`, so it owes no requirement edit itself — STEP 3 above does.
- Keep **Opus** for the requirement-authoring (archetype-S sign-off) and task-derivation work.
