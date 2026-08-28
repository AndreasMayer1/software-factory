# 068-26 — BLOCKER: chainstate harvest oracle ⊥ mandatory degenerate persona_scenario unit

Date: 2026-07-14 · automated session (`45b4b247`) · **no build-mode budget spent** (all
findings from local dry-runs of the deployed mechanism scripts).

## The blocker (verified end-to-end locally)

The build-mode harvest is gated by an **injected acceptance oracle**. `scripts/playground/build.py`
offers exactly one (`--acceptance-oracle chainstate`,
`scripts/playground/acceptance_oracles.py::chainstate_complete_predicate`). Its rule is **strict
all-DONE**:

> returns True only when EVERY unit is DONE … an ESCALATED unit means the chain reached a blocker
> and the derivation did NOT finish, so an all-escalated chain must report not-complete.

But the required config (`fixed_layers=[persona, scenario]`, AC-2) **structurally** resolves to two
spans (verified via `resolve_spans`):

| span | layers | direction | authoring pairs |
|------|--------|-----------|-----------------|
| 0 `persona-scenario-fixed` | persona, scenario | BIDIRECTIONAL | **[]** (adjacent-fixed — nothing internal to author) |
| 1 `materialization-from-scenario` | scenario→…→code | FORWARD | scenario_materialization, flow_requirement, requirement_task |

`plan_chain` **requires** `span_units` length == resolved-spans length (== 2), so span 0 **cannot be
dropped** (a 1-unit spec fails: `malformed spec: span_units length 1 does not match resolved spans 2`).

Span 0 has **zero authoring pairs**. The mechanism's *intended* disposition for it is **ESCALATED** —
its own unit test spells this out:
`test_backfill_orchestration.py:1061` → `complete_unit(state, "u0", ESCALATED)  # skip past span 0`.
Confirmed locally: `complete … persona-scenario-fixed done` (no report) →
`status: escalated, escalation_reason: gate_content_fail` (empty gate — nothing authored to judge).

**Consequence:** span 0 ESCALATED + span 1 DONE ⇒ oracle all-DONE = **False** ⇒ run classified
`ABANDONED` (clean exit, oracle not-finished, no blocker) ⇒ **copy preserved, harvest skipped**.
Running **without** an oracle instead yields `INCONCLUSIVE` (fail-safe) — also never harvests. So the
task's literal plan (author scenario_materialization, ESCALATE-skip span 0) **can never harvest** →
AC-1 unreachable. The task's committed plan (`_01_plan…`) noted span 0 as "degenerate" but did not
reconcile it with the harvest oracle — this is the gap.

(Note: even if harvested, `harvest_authored` only copies **net-new/modified** files vs the pre-child
baseline, so the pre-existing seeded scenario/persona bodies are never harvested regardless — only the
new `product_materialization.md` would be. AC-3/AC-4 are safe under every option below.)

## Resolution options (all keep the mechanism UNCHANGED — mechanism edits are out of scope here)

**Option A — complete span 0 as DONE truthfully (recommended).** Drive span 0 to DONE via the normal
gate: `enrich` it with `--layer-pair persona_scenario --target-paths <existing scenario.md>`, have the
child **actually apply `drift_rubric.md`** to that already-approved body → real drift score + real
sha256, `complete … done --naturalness-report …`. Verified locally this **passes** the content gate
(`minimality=ok, naturalness=pass`) and reaches `DONE`. Reading: the persona↔scenario boundary is
already approved (068-11), so certifying it coherent is truthful, authors nothing net-new, needs no
mechanism change, and lets the chainstate oracle certify complete → the single `product_materialization.md`
harvests. Downside: span 0's DONE deviates from the mechanism's documented ESCALATED-skip intent.

**Option B — no oracle + manual harvest.** Run build-mode with **no** `--acceptance-oracle`
(INCONCLUSIVE → copy preserved), then the outer session manually copies just
`requirements_user_needs/product_materialization/**` from the preserved copy into `test_harness_app/`.
Downside: bypasses the completion-gated auto-harvest the build-mode design centers on; manual harvest
step is outside the certified path (but is a single, known, auditable file).

**Option C — defer for a mechanism task.** Treat as blocked; open a separate task to make the
chainstate oracle tolerate degenerate zero-authoring-pair units (DONE-or-degenerate). Out of scope for
068-26 (mechanism change), and blocks 068-12.

## Recommendation

**Option A.** In-scope, no mechanism change, truthful, satisfies AC-1..4, unblocks 068-12. The driver
prompt would: (1) plan; (2) for span 0 — enrich `persona_scenario` + existing scenario body, apply the
drift rubric for real, complete DONE, commit; (3) for span 1 — enrich `scenario_materialization`, author
via `ux-write-materialization`, apply rubric, complete DONE, commit, and **stop** (do not author
flow_requirement/requirement_task); (4) chain drains all-DONE → oracle certifies → harvest.
