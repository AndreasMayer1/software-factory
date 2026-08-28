# 068-12 — derivation specs (pre-authored) + run plan

Date: 2026-07-14 · interactive session · **specs pre-authored + plan-validated; no run executed**

## Ordering (enforced by `after:` + the materialization precondition)

```
068-26 (materialization anchor)  ─blocks→  068-12 (flows, then requirements)
```

068-12 is `after:`-gated on 068-26, and `layer-derivation-start`'s materialization precondition
(074-03-04) will independently refuse to start 068-12's flow derivation until the materialization
anchor exists. So 068-26 must land first.

## Key mechanism finding (affects both phases)

The materialization layer now sits **between** scenario and flow, and the `materialization_flow`
boundary has **no authoring-skill mapping** (`AUTHORING_SKILL_BY_PAIR` — confirmed). Consequences:
- **No `fixed_layers` config yields flow authoring from spine adjacency** — scenario's lower neighbour
  is now materialization, not flow, so `scenario_flow` never arises as a resolved pair, and
  `materialization_flow` is filtered out. Flows must be authored via the **explicit (vestigial-but-valid)
  `scenario_flow` boundary** supplied in the spec, with the driver prompt naming `ux-create-flow`
  (`layer_pair=None` — the exact pattern the known-good 2026-07-10 flow run used). Materialization
  grounding is still enforced *inside* `ux-flow-draft` (presence gate + Step 8b), independent of the
  spine boundary.
- Because units are positional per resolved span and `fixed_layers=[persona, scenario]` yields only
  **2 spans**, one spec cannot hold both the 2 flow units and the requirement units. **068-12 therefore
  runs in two phases** (two build-mode runs), which also matches the proven single-layer precedent.

## Phase 1 — flows (spec pre-authored + plan-validated) ✅

File: `harness_flow_derivation_spec.incopy.json` (this folder). `fixed_layers=[persona, scenario]` →
2 spans → 2 units:
- `persona-scenario-fixed` (span 0, degenerate persona↔scenario — **zero authoring pairs**).
- `flows-from-scenarios` (span 1, forward; `scenario_flow` boundary, anchors `[SCEN-001-01, SCEN-002-01]`
  → authors `FLOW-001` + `FLOW-002` via the coverage loop; `layer_pair=None`, driver-prompt-scoped).

`plan` → **2 units, planned**.

**Degenerate-span-0 handling (Option A — same fix as 068-26's _02 blocker).** Span 0 MUST be driven to
**DONE**, not ESCALATED, or the strict all-DONE harvest oracle refuses to harvest (this is the exact bug
068-26 hit; corrected here proactively). An earlier draft of this spec put a `scenario_flow` boundary on
span 0's unit — wrong: span 0 is persona↔scenario, so its unit certifies `persona_scenario`.

**Run prerequisites (handled by the 068-12 session, not pre-done here) — driver prompt:**
1. plan.
2. span 0 `persona-scenario-fixed` → **DONE**: enrich `persona_scenario` + the seeded scenario body,
   apply `drift_rubric.md` for real, `complete done`, commit (certifies the approved 068-11 boundary;
   authors nothing net-new).
3. span 1 `flows-from-scenarios` → **DONE**: enrich `scenario_flow`, author both flows via
   `ux-create-flow` (coverage loop over both scenario anchors), apply rubric, `complete done`, commit,
   and **stop** before `flow_requirement`.
4. all-DONE → chainstate oracle certifies → harvest `FLOW-001`/`FLOW-002`.
- The `unit_task_req_path` bucket (`requirements_tasks/functional/flow_layer`, `REQ-HARNESS-01`) was
  removed in the reset — recreate the empty scaffolding bucket in the seeded copy so unit-task folders
  can be filed (`REQ-HARNESS-01` satisfies `allocate_task_id`'s `^REQ-[A-Z]+-\d` pattern).

## Phase 2 — requirements (config sketched; spec finalized once flows exist)

Deliberately NOT pre-authored as a runnable spec: `flow_requirement` derivation needs the flows from
Phase 1 to exist as its input anchors, so the exact anchors/units are decided against the real flows.
Intended config (dry-run-checked for span shape):
- `fixed_layers=[persona, scenario, flow]` → 3 spans; the `flow→…→code` forward span has mapped pairs
  `[flow_requirement, requirement_task]`. Supply `flow_requirement` units anchored on `FLOW-001`/`FLOW-002`;
  driver prompt scopes to `flow_requirement` (`requ-derive-from-flow` + `requ-explore`) and stops before
  `requirement_task` (tasks are out of scope). Target a `requirements_layer` unit-task bucket
  (e.g. `REQ-HARNESS-02`, matching the id pattern).
- Note: with `flow` fixed, the `scenario→materialization→flow` span lists `scenario_materialization` —
  harmless because the precondition finds materialization already present (from 068-26) and does not
  re-author it; the driver prompt authors only `flow_requirement`.

## Status

- Phase-1 flow spec: **pre-authored + plan-validated**, ready for the 068-12 flow run.
- Phase-2 requirement spec: config sketched, finalized at run time once flows exist.
- No budget spent, no run executed.
