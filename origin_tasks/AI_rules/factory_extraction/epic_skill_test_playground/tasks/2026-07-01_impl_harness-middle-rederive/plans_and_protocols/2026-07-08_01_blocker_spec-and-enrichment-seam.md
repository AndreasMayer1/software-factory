# Blocker — TASK-PROC-068-12 harness middle re-derivation

Date: 2026-07-08 · session 5fe1aaac-1062-485d-9679-703b41153248 · model Opus 4.8 · automated mode

## What this task asks

Re-derive the harness **flow** and **requirement** layers from the approved anchors
(personas maya/PERSONA-002 + theo/PERSONA-001, scenarios SCEN-002-01 + SCEN-001-01) via the
**fixed** layer-derivation mechanism, using the real authoring skills (`ux-create-flow`,
`requ-derive-from-flow`/`requ-explore`), with the wired AC-02 density + AC-03 naturalness gates,
all content under `test_harness_app/requirements_*` (two-tree split). Goal names
`layer-derivation-start` as the entry skill.

## Current harness state (verified)

- Anchors present: `test_harness_app/requirements_user_needs/personas/{maya,theo}/…` +
  their two `scenario.md` files. Middle (flows, requirements) is **empty** — no `user_flows/`,
  no harness `requirements_tasks/`. Ready to derive.

## Blockers found (mechanism read: backfill_orchestration.py, anchor_span_engine.py,
## coverage_delta.py, fixpoint_loop.py)

### B1 — `layer-derivation-start` requires a `spec_path` (+ `chain_state_path`) that the goal does not supply
The skill's only inputs are a spec JSON and a chain-state output path. The goal provides neither,
and does not state: `fixed_layers`, the `span_units`/`boundaries`, `preloaded_answers_ref`,
`unit_task_req_id`, `unit_task_req_path`, or `unit_task_covers_acs`. All must be decided before the
run can start.

### B2 — the `layer_pair`/`authoring_skill` enrichment seam is UNWIRED (load-bearing)
`plan_chain` builds each `UnitEntry` with `layer_pair=None`, `target_artifact_paths=()`
(only `unit_id`, `direction`, `anchor_demand_ids` are set). The function that attaches
`layer_pair` (→ the authoring skill via `AUTHORING_SKILL_BY_PAIR`) and the on-disk target paths is
`enrich_directive`, which is called **nowhere** in the control skills and has **no CLI subcommand**
(CLI = `plan | next | complete | resolve | status`). So the documented flow
`plan → next → create first unit task` returns a directive with `layer_pair: null`,
`authoring_skill: null`, `target_artifact_paths: []` — the created unit task cannot know which skill
to run. This is a wiring gap analogous to the orphaned content gates that TASK-PROC-071-05-05 was
created to fix; the "fixed mechanism" this task depends on still cannot dispatch a unit end-to-end
via the skill alone.

### B3 — a 2-layer derivation (flow AND requirement) does not map onto the one-unit-per-span /
### one-`layer_pair`-per-unit model
`plan_chain` creates one unit per resolved span (positional), and each unit carries exactly one
`layer_pair` (one authoring boundary). Deriving both `scenario→flow` and `flow→requirement` is two
boundaries. No `fixed_layers` config yields exactly those two units cleanly:
- `["scenario"]` → spans `persona↔scenario` (REVERSE — would *derive persona*, unwanted) and
  `scenario↔code` (FORWARD, internal layers flow+requirement+**task** — overshoots past requirement
  into task/code, which the goal scopes OUT).
- `["persona","scenario"]` → `persona↔scenario` (BIDIRECTIONAL, no internal layers — no-op unit) and
  `scenario↔code` (same overshoot to task).
Requirement cannot be a `fixed_layer` (it is the derivation target, not yet authored). So the shape
must be decided: two sequential single-boundary runs, or one chain with a stop-at-requirement rule
the current mechanism does not express.

### B4 — anchor scenarios declare `implements_flows: []` → flow-demand coverage IDs undefined
The coverage model is set-difference on IDs (`required − satisfied`). For `scenario→flow` FORWARD
the required flow IDs are not present in the anchors (both scenarios: `implements_flows: []`). Either
(a) the flow-demand IDs are author-chosen up front (e.g. the epic's FLOW-HARNESS-01/02/03), or
(b) the run is pure FORWARD/organic where `ux-create-flow` invents flow IDs and back-references them
and coverage closes on the scenarios' populated `implements_flows`. The boundary `anchor_kind` +
`anchor` demand list depends on which.

### B5 — `unit_task_req_id` / `unit_task_req_path` (factory tree) unspecified
The unit tasks the run creates must be filed under a factory-tree requirement (they are process
tasks running authoring skills). The goal does not say which. Candidates:
`epic_layer_derivation/feat_backfill_orchestration` (where real-run unit tasks conceptually belong)
vs `epic_skill_test_playground` REQ-PROC-068.

## Why I did not fabricate a spec and fire autorun

068-07's failure mode was exactly "author into the harness tree via a bypassing/mis-scoped driver."
Guessing `fixed_layers`/boundaries/`unit_task_req_*` and starting an autorun chain risks writing
non-conformant content into `test_harness_app/` and mis-firing the chain. B2 in particular means the
skill's happy path cannot currently dispatch a unit — a plausible predecessor-fix requirement, not a
run-time guess. Escalating per CLAUDE.md ("ask the user when not sure"; "stick to the plan — when it
does not work, ask").
