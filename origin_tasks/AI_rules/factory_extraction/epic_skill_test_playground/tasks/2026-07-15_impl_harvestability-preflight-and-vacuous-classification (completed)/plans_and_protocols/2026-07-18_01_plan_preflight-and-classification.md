# Plan — TASK-PROC-068-30: harvestability pre-flight + vacuous-aware run classification

Task: `../goal.md` · Covers REQ-PROC-068 AC-18, AC-19, AC-22 (all EGP-F, consequence HIGH).
Design grounding: `../../2026-07-14_explore_fix-degenerate-span-harvest-and-spec-authoring (completed)/plans_and_protocols/2026-07-15_004_synthesis.md` §SP-2/§SP-3.
Predecessor (landed): TASK-PROC-071-06-10.

## What the predecessor already delivers (do NOT re-implement)

- `backfill_orchestration.UnitStatus.VACUOUS_COMPLETE` — third terminal, granted only from the
  mechanism's structural zero-authoring-pair proof.
- `acceptance_oracles.chainstate_complete_predicate` — already counts `DONE ∪ VACUOUS_COMPLETE`.
  **AC-19's "finished" definition is therefore already satisfied**; no oracle change needed.
- `backfill_orchestration.derive_span_units` / `lint_spec` / alias `harvestability_preflight`
  (`backfill_orchestration.py:878–984`) — the derive-not-author surface + teaching linter that
  AC-22 requires the pre-flight to REUSE (author-time == plan-time, one implementation).

## Design decisions (resolved here — HIGH-consequence seam, do not re-litigate)

### D1 — AC-18 narrowing: oracle-negative + no real-authoring unit non-terminal → INCONCLUSIVE

AC-18 narrows *abandoned* to require **at least one unit with real authoring pairs left
non-terminal**. AC-19 independently states the gate **never** certifies complete without a positive
oracle result. These bind simultaneously, so a run that is oracle-negative but has no real-authoring
unit under-finished is:

- **NOT ABANDONED** — it must not be blamed on the skill under test (AC-18); and
- **NOT COMPLETE** — no positive oracle result, so it cannot be certified/harvested (AC-19).

→ it classifies **INCONCLUSIVE** (build.py's existing never-harvest / never-report-success
fail-safe). This is the only classification satisfying both ACs; recording it because a naive
reading of AC-18's "such a run is complete" sentence would invert AC-19's fail-safe direction.
In practice this state is only reachable from legacy un-migrated state (a degenerate span parked at
PENDING/ESCALATED instead of VACUOUS_COMPLETE), which is exactly what must not be harvested.

`classify_run_outcome` therefore gains an **injected structural-degeneracy inspector**
(`Callable[[str], bool]` — "is at least one real-authoring unit non-terminal?"), wired the same way
the completion predicate and blocker detector already are. build.py must stay layer-derivation-free
(AC-17: `"ChainState" not in dir(build)`) — the concrete inspector lives in `acceptance_oracles.py`
next to the existing chainstate oracle and is injected by `build.main()` / the cold-resume rebuild.

### D2 — AC-22 overrides the predecessor's all-degenerate WARNING

`lint_spec` currently reports an all-degenerate spec as a non-blocking `warning` and leaves
`predicted_harvestable=True` (synthesis residual #1 was left open). **AC-22 is authoritative** and
states an all-degenerate spec "is one such doomed spec and is rejected at plan time rather than
deployed". → change it to a blocking **error** with `predicted_harvestable=False`.
**Divergence recorded**: predecessor behaviour (warn) → AC-22 behaviour (reject). The affected
predecessor tests in `scripts/tests/test_backfill_orchestration.py` (AC-10 all-degenerate warning
assertions) must be updated to assert rejection, with the AC-22 citation in the test docstring.

### D3 — Doomed classes rejected at plan time
1. all-degenerate spec (every span zero-authoring-pair — synthesis R1);
2. a real span that can never reach an authored terminal — no authoring skill registered for its
   layer pair (ADV-sg-02). `lint_spec` does not check this yet; add it (reuse the layer→skill map
   `build_directive` already uses) so the predictor is exact over the best-case terminal.
3. existing: no spans resolved; hand-authored `span_units` arity mismatch.

### D4 — Distinct doomed-spec exit code + persisted, resume-revalidated stamp
- New exit code (distinct from generic failure) for the doomed-spec plan-time outcome; must consume
  **no deployed run** (fail before `_prepare_workspace`/deploy).
- Persist the verdict as a `harvestable` stamp in the run-registry record (alongside
  `acceptance_oracle_kind`, which is already persisted for cold-resume reconstruction).
- **Re-validate on `-start` AND on every resume path** (`build_resume.resume_run`) — recompute the
  pre-flight from the spec and refuse to reach harvest on a negative/absent verdict (ADV-sg-06).

### D5 — Retire the Option-A workaround
The 068-26 / 068-12 per-task workaround (hand-certifying span-0 to DONE) is superseded: those units
are now born `VACUOUS_COMPLETE`. Remove it and note the removal.

## Units of work

| # | Unit | Files | Gate |
|---|------|-------|------|
| U1 | D2+D3: all-degenerate → blocking error; add unreachable-authored-terminal check; update predecessor tests | `scripts/factory/layer_derivation/backfill_orchestration.py`, `scripts/tests/test_backfill_orchestration.py` | python gates |
| U2 | D1: degeneracy inspector + `classify_run_outcome` narrowing | `scripts/playground/acceptance_oracles.py`, `scripts/playground/build.py` | python gates |
| U3 | D4: pre-flight call site, doomed exit code, stamp persist + `-start` revalidation | `scripts/playground/build.py` | python gates |
| U4 | D4: resume revalidation | `scripts/playground/build_resume.py` | python gates |
| U5 | Tests for AC-18/19/22 incl. the EGP referents (doomed spec consumes no deployed run; resume revalidates before harvest; predicted verdict vs ACTUAL deployed-run classification) | `scripts/tests/test_playground_*.py` | pytest |
| U6 | D5 retire Option-A workaround; `contract.yaml` EGP disposition check | `scripts/playground/contract.yaml`, docs | — |

## U6 resolution (D5) — Option-A workaround retirement + contract-EGP correction

- **Option-A retirement (D5): documentation-only — no live code to delete.** A grep across
  `scripts/**` found no active source workaround (the "hand-certify span-0 to DONE" fix for
  068-26 / 068-12 was per-task *manual persisted-chain-state* edits, not a code path). With this
  task and TASK-PROC-071-06-10 both landed, a structurally zero-authoring-pair span-0 is born
  `VACUOUS_COMPLETE` and the chainstate oracle counts it as finished, so the manual span-0→DONE
  certification is superseded and MUST NOT be re-applied in any future 068-26/068-12 chain. This
  note is the required removal record (goal: "document its removal once this and 071-06-10 land").
- **contract.yaml EGP correction:** the U6 plan row's "contract.yaml EGP disposition check" was a
  planning misjudgment — `scripts/playground/contract.yaml` is the boundary contract for
  `containment.py`/AC-09 (archetype S), unrelated to this task's AC-18/19/22. The EGP dispositions
  for AC-18/19/22 already live in the requirement ACs (all `EGP: F`, HIGH) and the goal `egp:` block;
  no contract.yaml change is in scope. Dropped.

## Discipline
- Every `scripts/**` edit routes via the `claude-write-script` skill (project law); skill edits via
  `claude-modify-skill`. Never hand-edit quality gates.
- AC text is authoritative over the concept; divergences recorded above (D1, D2).
- Python gates: `scripts/quality/check_python_gates.sh` must be GREEN before completion.
