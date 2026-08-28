# 068-26 — Option A driver plan (resolves the _02 blocker)

Date: 2026-07-14 · resolves `2026-07-14_02_blocker_oracle-vs-degenerate-unit.md`

## Why (recap)

`fixed_layers=[persona, scenario]` resolves to 2 spans. Span 0 (persona↔scenario) is adjacent-fixed
→ **zero authoring pairs**. `plan_chain` forces one unit per span, so span 0's unit is mandatory but
has nothing to author; the mechanism's default disposition for it is **ESCALATED**, and the strict
all-DONE harvest oracle then refuses to harvest → materialization never lands. Option A drives span 0
to **DONE truthfully** so the oracle certifies. (Verified locally in the _02 blocker: certifying the
already-approved persona↔scenario boundary passes the content gate `minimality=ok, naturalness=pass`
and reaches DONE.)

## The driver prompt the deployed run must issue (4 steps)

1. **Plan.** `backfill_orchestration.py plan harness_materialization_derivation_spec.incopy.json <chain_state>`.
2. **Span 0 — `persona-scenario-fixed` → DONE (certify the approved boundary; author nothing net-new).**
   - `enrich` the unit with `--layer-pair persona_scenario --target-paths <seeded scenario.md file(s)>`.
   - The child **actually applies `drift_rubric.md`** to the already-approved (068-11) scenario body →
     real drift score + real sha256.
   - `complete <unit> done --naturalness-report <report>`; commit.
   - Rationale: the persona↔scenario boundary is already approved, so certifying it coherent is
     truthful, needs no mechanism change, and yields DONE (not ESCALATED).
3. **Span 1 — `materialization-from-scenario` → DONE (author the one anchor).**
   - `enrich` with `--layer-pair scenario_materialization --target-paths <product_materialization.md>`.
   - Author via **`ux-write-materialization`** (the brownfield precondition confirm-the-user-facing-set
     checkpoint fires here); apply the rubric; `complete <unit> done`; commit.
   - **STOP** — do NOT author `flow_requirement` / `requirement_task` (those are 068-12 and below).
4. **Harvest.** Chain drains all-DONE → `--acceptance-oracle chainstate` certifies complete → build-mode
   harvests the net-new `product_materialization.md` into `test_harness_app/`.

## Notes

- `layer_pair=None` on span 1 in the planned ChainState is expected; the driver names the skill.
- Ensure the in-copy `unit_task_req_path` bucket exists in the seeded copy for unit-task filing.
- Span 0's DONE deviates from the mechanism's documented ESCALATED-skip intent — this is a deliberate
  in-scope workaround; the durable fix (make the mechanism complete degenerate zero-pair spans as DONE)
  is a separate mechanism task (see the prevention note).
