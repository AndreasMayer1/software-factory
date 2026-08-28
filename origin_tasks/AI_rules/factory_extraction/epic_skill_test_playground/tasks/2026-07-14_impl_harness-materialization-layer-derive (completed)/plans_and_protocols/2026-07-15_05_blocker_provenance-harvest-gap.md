# 068-26 — BLOCKER (Option A run attempted): two build-mode integration gaps make AC-1 unreachable

Date: 2026-07-15 · automated session `45b4b247` · Option A launched, first run torn down at session
exit (barely reached span-0 enrich — **negligible budget**). Contaminated copy `playground_ws_5b8122e2`
destroyed + its run record marked `abandoned`.

## What ran
Launched `python3 -m scripts.playground.build … --acceptance-oracle chainstate` with the Option-A
driver (`driver_prompt_materialization.txt`). Deploy+seed succeeded; the child session started the
chain and enriched span-0, then the wrapper was torn down when the prior session process exited
(no completion record — the "stopped" notification). Inspecting the preserved copy surfaced two
blockers the task plan did not anticipate.

## Blocker 1 — deploy leaks the flutter app's materialization into the harness copy (workaroundable)
`scripts/playground/deploy.py::_SUBFOLDER_EXCLUDES` excludes `requirements_user_needs/personas`,
`…/user_flows`, `…/_meta/project` — but **NOT** `requirements_user_needs/product_materialization/`
(that path post-dates the exclude list). So `deploy_candidate` overlays the **flutter app's own**
`product_materialization.md` (MAT-002, mood-tracker, `decided_by: IDEATION-022`, refs FLOW-001..004)
into the seeded harness copy. Verified: the copy's file is byte-identical to
`requirements_user_needs/product_materialization/product_materialization.md` and is in the pre-child
baseline snapshot. Effect: `ux-write-materialization` Mode-Detection would see it and run in
**UPDATE/supersession** mode against a foreign MAT id, and the child's in-copy provenance check would
pass on the leaked flutter artifact rather than a real harness one. (Personas/scenarios seed correctly
— only `product_materialization/` leaks.) **Workaround (in driver, in-scope):** delete the leaked
`product_materialization.md` in SETUP so authoring runs CREATE. But Blocker 2 is not workaroundable.

## Blocker 2 — materialization provenance cannot resolve post-harvest (fundamental)
AC-1 requires `check_materialization_provenance.py` to print `OK` for the harvested harness artifact.
That check (`scripts/user_needs/check_materialization_provenance.py`) is **hardwired to the flutter_app
repo**: `ROOT = parents[2]` → resolves `decided_by: IDEATION-NNN @ <sha>` against
`flutter_app/.factory/ideation/index.yaml` AND `git cat-file -e <sha>` in **flutter_app** git. It has
no `--index`/`--repo` flag (only `--artifact`). But:
- The child authors materialization **inside the ephemeral copy**, whose ideation ledger + index entry
  live in the **copy's** `.factory/ideation/` and whose commit sha is in the **copy's own fresh git
  repo** (`init_workspace_git`) — unreachable from flutter_app.
- Harvest copies **only** product-definition categories (`user-needs, requirements, scribble,
  source-code`). `.factory/ideation/` is factory-runtime → **never harvested**; the copy is discarded
  on COMPLETE.
- `test_harness_app/` has **no** `.factory` of its own.

Net: a harvested `product_materialization.md` carries `decided_by: IDEATION-NNN @ <sha>` whose ledger
and commit exist only in the discarded copy → the host-side provenance check returns `MISSING`
(ideation id not indexed / commit unreachable). **AC-1 is unsatisfiable by pure build-mode harvest.**

## Options for the developer
- **A — outer-session ideation (in-scope, more complex):** run the medium-selection ideation **here in
  flutter_app** (this session), committing the ledger + `.factory/ideation` index entry referencing the
  **harness** scenarios, yielding `IDEATION-NNN @ <sha>` reachable in flutter_app. Feed that id/sha to
  the child; child authors materialization with that `decided_by` + deletes the leaked flutter file
  (Blocker 1). Post-harvest the host check resolves. Keeps the mechanism unchanged; adds host-side
  ideation + a more elaborate driver. Risk: the ideation ledger references `test_harness_app/...`
  scenario paths (the regex matches the substring), acceptable but slightly unusual.
- **B — extend harvest to carry provenance (mechanism change, out of scope here):** make build-mode
  also harvest/rebase the ideation ledger + index entry into the host and rewrite the commit ref.
  Needs its own task under REQ-PROC-068/074; also fix `deploy.py` to exclude `product_materialization/`
  (Blocker 1). Blocks 068-26 meanwhile.
- **C — relax AC-1 for the harness:** accept a harness materialization whose provenance is
  `authored` but whose IDEATION pointer is not host-resolvable (test fixture), and drop the
  `check_materialization_provenance OK` gate from AC-1. Requirement edit (route via the proper flow).

## Recommendation
**A** if the developer wants the artifact now with resolvable provenance and no mechanism change; **B**
if build-mode should genuinely carry provenance across the harvest (the more correct long-term fix, but
a separate mechanism task). Blocker 1 must be fixed under A (driver delete) or B (deploy exclude)
regardless.
