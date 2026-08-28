# 068-26 — Harness materialization derived + harvested + verified (task deliverable met)

Date: 2026-07-19 · automated session `45b4b247` · resumed after developer chose **Option B**
(mechanism built by TASK-PROC-068-32/33/34/35, all `completed`).

## Outcome

`test_harness_app/requirements_user_needs/product_materialization/product_materialization.md`
(**MAT-001**) authored via the real `ux-write-materialization` path inside a deployed build-mode copy,
forward from the approved scenarios, and harvested back. **All four ACs verified (evidence below).**

## How it ran

Deployed build-mode run `1a39da4c` (`python3 -m scripts.playground.build`, then
`build_resume.py resume`), driver `driver_prompt_materialization.txt`, model `claude-sonnet-5`,
oracle `chainstate`, `fixed_layers=[persona, scenario]`. Child derivation session cost **$3.27**,
ran 441 s, exited cleanly (rc=0).

**The original Option-A workaround is retired.** The mechanism now grants span-0
(`persona-scenario-fixed`, zero authoring pairs) the new terminal **`VACUOUS_COMPLETE`** from its own
structural proof, and `acceptance_oracles` accepts it
(`completed_terminals = (DONE, VACUOUS_COMPLETE)`). The driver's span-0 certification branch is dead
code — no longer needed.

Both earlier blockers are confirmed fixed in the deployed factory:
- **Deploy leak** — `deploy.py::_SUBFOLDER_EXCLUDES` now excludes
  `requirements_user_needs/product_materialization/`; verified the flutter app's MAT-002 no longer
  appears in the copy (it did before, byte-identical).
- **Provenance across harvest** — the copy's git history is restored from
  `test_harness_app/.playground_harness_git/harness.bundle` at deploy, and `retain_ideation_provenance`
  scalpel-retains the referenced ideation index entry + ledger + task folder.

## AC verification (evidence)

- **AC-1 ✅** — provenance resolves under the sanctioned deployed-copy semantics (the check is only ever
  invoked inside a deployed copy — developer's Option-B answer). Replicated it: seeded a copy of
  `test_harness_app`, `restore_workspace_git(...harness.bundle)`, then `check()`:
  `commit 6c7d2b7 reachable: True` →
  `OK IDEATION-024 @ 6c7d2b7 -> requirements_tasks/functional/materialization_layer/tasks/2026-07-19_impl_derive-materialization-anchor/plans_and_protocols/2026-07-19_001_ideation_ledger.yaml (2 scenario ref(s) resolved)`.
  (From the *host* the check reports `commit not reachable` — expected and by design; host-side git
  access was deliberately NOT built.)
- **AC-2 ✅** — deployed build-mode run, `fixed_layers=[persona, scenario]`, materialization authored
  **forward** from the scenarios via the `scenario_materialization` boundary; ideation topic recorded as
  "product form / medium for a private, local-first movie/mood logging app (harness materialization
  derivation)"; 2 scenario refs resolved = SCEN-001-01 + SCEN-002-01.
- **AC-3 ✅** — only the materialization layer: no `user_flows/` directory exists, no `requirements.md`
  authored. The single `requirements_tasks/.../2026-07-19_impl_derive-materialization-anchor/` folder is
  the **retained ideation provenance** (goal.md + ledger + synthesis) that 068-35 deliberately retains —
  not a derived task-layer artifact.
- **AC-4 ✅** — all product content under `test_harness_app/` (`requirements_user_needs/product_materialization/`,
  `requirements_tasks/`, retained `.factory/ideation/`, `.playground_harness_git/`). Two-tree split intact;
  content is genuinely harness-derived (quick-note vs. detailed-record, offline, the two seeded personas),
  not the flutter app's.

## Honest caveat

The run's own gate classified the outcome **`abandoned`** (the child exited cleanly without marking the
span-1 unit DONE in its ChainState), yet the artifact was authored, harvested (registry
`harvested: 2`), and independently verified above. The workspace was subsequently cleaned up, so the
final ChainState is not inspectable. **Not re-run deliberately**: a fresh run would now seed the
existing `product_materialization.md`, flipping `ux-write-materialization` into UPDATE/supersession mode
and producing a spurious MAT-002 — strictly worse than the correct MAT-001 already in place. The
deliverable is correct and verified; the residual gap is the chain's own bookkeeping, worth a follow-up
if the `abandoned`-yet-harvested combination is unexpected for the new gate.
