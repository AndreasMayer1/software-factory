---
skill: task-resolve
mode: automated
decision: ""
task_id: TASK-PROC-068-26
captured_at: 2026-07-15
---

# Question

---
task_id: TASK-PROC-068-26
session_id: 45b4b247-f46f-4843-a9c4-128a9db225a4
account: web
status: awaiting_answer
asked_at: 2026-07-14T19:04:56Z
skill: task-resolve
---

# Pending Question

Full investigation (verified locally, **no build-mode budget spent**):
`plans_and_protocols/2026-07-14_02_blocker_oracle-vs-degenerate-unit.md`

**Blocker (one line):** the only build-mode harvest oracle (`chainstate`) requires **all** chain
units `DONE`, but the required config `fixed_layers=[persona,scenario]` structurally forces a
degenerate `persona-scenario` span-unit whose intended disposition is `ESCALATED` (nothing to
author) — so the run is classified `ABANDONED` and **never harvests**. The task's committed plan
(ESCALATE-skip span 0 + author only scenario_materialization) therefore can never satisfy AC-1.
Span 0 cannot be dropped (`plan_chain` requires span_units == 2 resolved spans). Mechanism changes
are out of scope for this task.

**Which resolution should the run use?** (all keep the mechanism unchanged; AC-3/AC-4 stay safe
because harvest only copies net-new files, i.e. just `product_materialization.md`)

- **A (recommended):** drive span 0 to `DONE` truthfully — `enrich` it with `--layer-pair
  persona_scenario` + an existing approved `scenario.md` body, actually apply `drift_rubric.md` to
  that body (real drift + sha256), `complete … done`. Verified locally: passes the content gate →
  chain reaches all-DONE → chainstate oracle certifies → `product_materialization.md` harvests.
  In-scope, no mechanism change, truthful. Downside: span 0's `DONE` deviates from the mechanism's
  documented `ESCALATED`-skip intent for degenerate units.
- **B:** run with **no** `--acceptance-oracle` (copy preserved), then manually harvest just
  `product_materialization/**` from the preserved copy. Downside: bypasses the completion-gated
  auto-harvest the design centers on.
- **C:** defer — open a separate mechanism task to make the oracle tolerate degenerate
  zero-authoring units. Downside: leaves 068-26 (and its dependent 068-12) blocked.

# Developer Answer

Option A

# Rationale Captured

(Automated archival — no rationale extracted.)
