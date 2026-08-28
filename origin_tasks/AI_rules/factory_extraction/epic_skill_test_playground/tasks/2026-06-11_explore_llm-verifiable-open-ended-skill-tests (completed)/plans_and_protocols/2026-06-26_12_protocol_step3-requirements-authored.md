# Protocol — STEP 3 (trimmed) requirements authored

**Date:** 2026-06-26 · **Task:** TASK-PROC-068-01 · interactive, Opus · developer present.

Authored the **spike-scoped slice** only (per the orchestration-chain plan `…_11_plan…`); the full
oracle/substrate ACs are deferred to the runtime orchestration chain (T-orch1).

## What was written
- **NEW feature `feat_regression_gate` → `REQ-PROC-073-01`** (status `defined`), 3 ACs:
  - AC-01 corpus (matched git-history before/after pairs, labeled by fix task) — EGP **F**/MEDIUM.
  - AC-02 disproof spike on the **HARDEST** pair (Option A, developer-approved) — detection + real cost
    vs. manual; go/no-go stop-loss — EGP **C**/MEDIUM.
  - AC-03 discriminating-maturity gate (batch-of-3 easiest-first developer walk; authoritative only if
    in-scope AND calibration satisfied AND fixture-count ≥ floor; else advisory) — EGP **Q**/MEDIUM
    (re-tagged from F: it is an output-quality judgment against the developer's human standard).
- **Epic `REQ-PROC-073`**: AC-01 feature-existence marker (not_bearing) + `## Features` now links the
  committed feature; other 3 features stay deferred.
- **Epic `REQ-PROC-068`**: added AC-08 (cost capture — EGP **C**) and AC-09 (child-session safety,
  sharpened to bite on absolute-path/cwd escape CON-04 — EGP **S/HIGH**, developer signed off "approve
  high"). Added `## Deferred (YAGNI)` naming the `max_budget_usd` cap as deferred (AC-08 = measurement,
  not enforcement). **Retrofitted EGP dispositions on pre-existing AC-01..07** (baseline debt surfaced by
  the edit; not introduced here): AC-01/03/05/06 not_bearing (structural/location checks), AC-02 X,
  AC-04/07 F.

## Fidelity check (background agent, 58k tok) — drifts caught & fixed
- AC-02 was "clearest pair" → contradicted SOL-01 §6 (disproof spike must pick the HARDEST). Fixed to
  hardest; serve-mode (easiest) re-homed to AC-03's maturity-walk first batch. (Developer chose Option A.)
- AC-09 was silent on mechanism → a worktree-only impl would vacuously pass. Sharpened to require closing
  the absolute-path/cwd escape (forces SG-04 OS-level containment).
- AC-03 advisory predicate completed with ADV-01 calibration + SG-03 fixture-floor triggers.
- AC-08 cost-cap deferral named (not silently dropped).

## Audit state
`check_egp_audit.py`: 073-01, 073, 068 all **0 missing dispositions**. Mismatches are informational
(considered dispositions vs. the crude auto-Q heuristic), documented via `egp_auto`. Merge + id_registry
regenerated.

## Next (STEP 5, staged)
Derive **T-spike** (covers REQ-PROC-073-01 AC-02; type impl, after:[]) and **T-orch1**
(`orchestration_task: true`, after:[T-spike]) via `task-create`. Full decomposition of REQ-PROC-073-01
(AC-01 corpus, AC-03 maturity) is intentionally **deferred to T-orch1** on spike-green (stop-loss) — so
this is a deliberate partial derivation, not a coverage gap.
