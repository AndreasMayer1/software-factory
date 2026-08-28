# 068-12 — Phase 1 (flows) execution protocol

Date: 2026-07-19 · automated session `df7046c8` (gmail2) · model Opus (orchestrator)

## Pre-flight state verified this session

- Predecessors all `completed` (12 in `after:`, incl. 071-05-05 mechanism fix, 068-11 anchors,
  068-21/22/23 build-mode resumability, 068-26 materialization anchor).
- Harness anchors present: PERSONA-001 (theo), PERSONA-002 (maya); SCEN-001-01
  (detailed_entry_after_movie/theo), SCEN-002-01 (quick_rating_after_movie/maya).
- Materialization anchor **MAT-001** present in `test_harness_app/requirements_user_needs/product_materialization/`
  (harvested by 068-26). Its presence unblocks the materialization precondition that the 2026-07-14
  reset note (04) expected to BLOCK on — that block is now resolved (materialization exists), so the
  Phase-1 flow run proceeds without the reverse-derive escalation.
- No flows yet in `test_harness_app` (reset by 04). Run registry `.playground_runs` empty → fresh run.

## Spec decision — use the PROVEN 2026-07-10 flow driver/spec, not the untested plan-05 combined spec

Plan 05 pre-authored `harness_flow_derivation_spec.incopy.json` (degenerate `persona-scenario-fixed`
span-0 + one `flows-from-scenarios` unit with both anchors) but it was **never run**. The
2026-07-10 execute-deployed-derivation-resumability run
(`.../feat_backfill_orchestration/tasks/2026-07-10_impl_execute-deployed-derivation-resumability-run/`)
used a **proven** spec: two per-scenario `scenario_flow` units (`flow-scen-001`, `flow-scen-002`),
no degenerate span-0 — and it harvested conformant FLOW-001/FLOW-002 end-to-end (later reset).

Chosen: the proven two-unit spec. Rationale:
- Demonstrated conformant harvest end-to-end via the same `backfill_orchestration.py` direct-drive
  pattern build.py expects.
- It has **no degenerate span-0**, so it sidesteps the exact all-DONE-harvest-oracle bug 068-26 hit
  (span-0 must reach DONE/VACUOUS_COMPLETE or harvest refuses). Two flow units → both DONE →
  CHAIN-COMPLETE → harvest. Clean.
- Faithful to plan-05 intent, which itself cites "the exact pattern the known-good 2026-07-10 flow
  run used" for the `ux-create-flow` + `layer_pair=None`(→`scenario_flow`) handling.
- Materialization-awareness is enforced inside `ux-flow-draft` (074-02-02 presence gate) independent
  of the spine boundary; MAT-001 is seeded, so flows author `authored_against_materialization` refs.

## Run shape (Phase 1 — flows)

- Wrapper: `PYTHONPATH=. python3 -m scripts.playground.build`
  - `--target-project-dir <abs>/test_harness_app` (seed source + harvest target)
  - `--host-project-dir <abs>/flutter_app` (deploy source)
  - `--model claude-sonnet-5` · `--max-budget-usd 8` (068-26 precedent: cost $3.27 of $8)
  - `--acceptance-oracle chainstate --chain-state-path .layerderiv/chain_state.json`
  - `--fixed-layers persona,scenario`
  - `--prompt "$(cat .../driver_prompt_flows.txt)"`
- Driver: `driver_prompt_flows.txt` (this folder) — verbatim adaptation of the proven
  `driver_prompt_v2.txt`; drives `backfill_orchestration.py` directly (NOT `layer-derivation-start`,
  which would create unit-tasks + dispatch autorun — unwanted headless).
- Completion: chainstate all-DONE → build.py harvests net-new `user_flows/**` into `test_harness_app`
  and discards the copy. Any other outcome preserves the copy → resume via `playground-build-resume`.

## Phase 2 (requirements) — deferred to after Phase-1 harvest verified

`flow_requirement` derivation needs the real flows as anchors; spec finalized once FLOW-001/002 exist.
Intended: `fixed_layers=[persona,scenario,flow]`, `flow_requirement` units on FLOW-001/002 via
`requ-derive-from-flow`+`requ-explore`, target `REQ-HARNESS-02` / `requirements_tasks/functional/requirement_layer`,
stop before `requirement_task`.

## Known residual (carried, not blocking the run)

- Flows are authored `review_status: draft` (autonomous). The 071-06-09/071-06-08 developer-review
  gate ("developer reviews harvested flows before 068-12 accepted") is a completion-acceptance
  concern noted for `task-complete`, not a run blocker.

## Run status log

- 2026-07-19 ~13:29 (session df7046c8): Phase-1 build-mode run `8e1487ef` LAUNCHED and confirmed
  running (registry `.playground_runs/8e1487ef*.json` → `status: running`; child claude session
  authoring flows; ~3.5 min elapsed). Detached run survives session teardown; build.py harvests
  autonomously on chainstate-complete. Session terminates per responsibility boundary (cannot advance
  until run completes); orchestrator resumes to re-check. On resume: if `user_flows/**` harvested into
  test_harness_app and registry `outcome: complete/harvested` → verify + start Phase 2; if run
  preserved (any non-complete outcome) → re-attach via `playground-build-resume`.

## CORRECTION — first run (8e1487ef) was malformed; spec changed to plan-05 shape

The first launch used the 2026-07-10 PROVEN spec (two per-scenario `scenario_flow` units). Empirically
that spec is INVALID post-materialization-layer: `fixed_layers=[persona,scenario]` resolves to exactly
2 spans → [bidirectional persona↔scenario (VACUOUS), forward scenario→…]. Positional zip mapped my
first unit `flow-scen-001` (SCEN-001-01) onto the VACUOUS span (`vacuous_proof:zero_authoring_pairs`),
authoring NO flow for SCEN-001-01, and only `flow-scen-002` (SCEN-002-01) onto the forward span. Run
would have produced ≤1 flow, orphaning SCEN-001-01. Verified by inspecting the copy's chain_state and
by a scratch `plan` run.

Aborted run 8e1487ef (killed build.py + child, removed copy + registry entries — nothing harvested,
harness tree clean). Switched to **plan-05's spec**: 2 units = `persona-scenario-fixed` (auto-vacuous)
+ single forward `flows-from-scenarios` carrying BOTH anchors [SCEN-001-01, SCEN-002-01]. Scratch `plan`
confirms: forward unit `layer_pair:None`, both anchors, status pending. Driver rewritten
(`driver_prompt_flows.txt`) to author BOTH flows in that one forward unit, then record both target
paths + `--layer-pair scenario_flow` in ONE enrich call (enrich overwrites all fields), and write the
naturalness report keyed `scenario_flow` with the COMPOSITE `body_fingerprint([FLOW1,FLOW2])` (computed
via the module's own helper so it matches the gate's recompute) and drift = max of the two. The
`complete` CLI gate checks only density+drift per boundary (no coverage-closure step), so this is
sufficient. Relaunching as run #2.

- 2026-07-19 ~13:38 (session df7046c8): Phase-1 run #2 `274b7ad8` LAUNCHED with corrected plan-05
  driver (copy playground_ws_274b7ad8; log /tmp/068-12_phase1_flows_run2.log). Detached; harvests
  autonomously on chainstate-complete → net-new user_flows/** into test_harness_app. Session
  terminates (cannot advance until run completes). ON RESUME: check
  `find test_harness_app/requirements_user_needs/user_flows -name flow.md` for FLOW-001
  (detailed_entry_after_movie) + FLOW-002 (quick_rating_after_movie); check registry
  /workspaces/private_mood_tracker/.playground_runs/274b7ad8*.json outcome; if both flows harvested
  & conformant → start Phase 2 (requirements). If run still running → re-check. If preserved/failed →
  inspect copy chain_state + log.
