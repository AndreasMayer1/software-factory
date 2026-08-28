# 068-26 — Execution plan (developer chose Option A)

Date: 2026-07-15 · automated session `45b4b247` · resumed after developer answer
(`2026-07-15_04_feedback-checkpoint.md` → **Option A**).

## Decision applied
Drive the degenerate `persona-scenario-fixed` span-0 unit to **DONE truthfully** (enrich with an
existing approved `scenario.md` + a real drift-rubric verdict), so the chainstate oracle can certify
all-DONE and harvest the single `product_materialization.md`. No mechanism change.

## Run shape (deployed build-mode run)
- Wrapper: `python3 -m scripts.playground.build`
  - `--target-project-dir …/test_harness_app` (seed source + harvest target)
  - `--host-project-dir …/flutter_app` (deploy source)
  - `--model claude-sonnet-5` · `--max-budget-usd 8`
  - `--acceptance-oracle chainstate --chain-state-path .layerderiv/chain_state.json`
  - `--prompt` = `plans_and_protocols/driver_prompt_materialization.txt`
- Driver prompt drives `backfill_orchestration.py` directly (the proven flow-run pattern), NOT
  `layer-derivation-start` (which would create unit-tasks + dispatch autorun — unwanted in a headless
  child). Two chain units:
  - **span 0 `persona-scenario-fixed`** → certify DONE (Option A), no new file authored.
  - **span 1 `materialization-from-scenario`** → `enrich --layer-pair scenario_materialization`,
    author `product_materialization.md` via **real** `ux-write-materialization` (embedded ideation for
    provenance; step-8 approval gate SKIPPED — autonomous run, no `pending_feedback`), then STOP (do
    not author flow_requirement/requirement_task).
- Completion gate: chainstate all-DONE → build.py harvests **net-new** product-def files (only
  `product_materialization/**`) into `test_harness_app/` and discards the copy. Any other outcome
  (INTERRUPTED/BLOCKED/ABANDONED/INCONCLUSIVE) preserves the copy → resume via
  `playground-build-resume` or inspect.

## Escalation risks inside the child (monitored)
- `ux-write-materialization` step-8 approval + `ideation` recovery/concept-resolve could write
  `pending_feedback` inside the copy → build.py `has_recorded_blocker` → BLOCKED (no harvest). Driver
  explicitly forbids `pending_feedback` and skips approval. If BLOCKED anyway, inspect the copy's
  `automation/pending_feedback` and resume/escalate with the specific sub-blocker.
- ideation mid-run gate is skipped in automated mode (ideation-start SKILL line 411) — embedded run
  is autonomous-viable.

## Verification after harvest (AC-1..4)
1. AC-1: `python3 scripts/user_needs/check_materialization_provenance.py --artifact test_harness_app/requirements_user_needs/product_materialization/product_materialization.md` → `OK`.
2. AC-3: only `product_materialization/**` harvested (manifest `harvested_paths`); no flows/requirements/tasks.
3. AC-4: harvested paths all under `test_harness_app/requirements_*`.
4. AC-2: run manifest shows chainstate oracle certified + `fixed_layers=[persona,scenario]`.
