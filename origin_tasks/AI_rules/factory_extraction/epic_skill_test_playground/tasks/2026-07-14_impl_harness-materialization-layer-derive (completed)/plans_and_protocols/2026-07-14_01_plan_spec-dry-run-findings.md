# 068-26 — materialization spec dry-run + code-anchor findings (no budget spent)

Date: 2026-07-14 · interactive session · **plan-only dry-runs, no deployed run executed**

## Decision: forward derivation from scenarios (Option A) — `code` dropped

068-26 authors the harness materialization anchor **forward from the approved scenarios**
(`fixed_layers = [persona, scenario]`, `scenario_materialization → ux-write-materialization`), so that
068-12 can later derive flows/requirements against it. An earlier draft fixed `code` as a bottom anchor
to test a bidirectional hinge; that was dropped after investigation (below).

## Why `code` was dropped — it is a hollow anchor here (verified against REQ-PROC-071 / 074-03)

The developer's original instinct — "a brownfield derivation should read the code to understand what
the app does" — matches the mechanism's stated *ambition* but not what it actually does:

1. **No `code` anchor extractor exists.** Only three anchor kinds are registered
   (`explicit_test_targets`, `materialization`, `flow_coverage`); an unregistered kind raises. Nothing
   reads `test_harness_app/src`.
2. **The reverse-derivation-over-existing-product feature is deferred/unbuilt.** `feat_artifact_mutation`
   (REQ-PROC-071-07) is `status: defined`, has no `tasks/` folder, and sits under the epic's "Additive
   Remainder (Deferred)". Only forward derivation is implemented today.
3. **By design the mechanism never comprehends source.** Even the deferred reverse spec anchors on
   *explicit test targets* / *existing requirement artifacts*, not parsed code. "What the app does"
   enters as human-authored personas/scenarios — the 074-03-04 precondition's brownfield *signal* is the
   scenario corpus, not the code. (This is coherent with the factory's top-down model: code is the
   output of intent, never the source of truth for intent.)

Consequence: putting `code` in `fixed_layers` only flipped a span's direction label to `bidirectional`
with an **empty** bottom anchor (no code demand, no code reader) — it fed no real code in. So it bought
nothing for materialization authoring, which is derived from the scenarios regardless. → Option A.

## Dry-run of the Option A spec ✅

`harness_materialization_derivation_spec.incopy.json` (`fixed_layers=[persona, scenario]`) →
`backfill_orchestration.py plan` → **2 units, planned**:
- `persona-scenario-fixed` — `direction: bidirectional` (degenerate; both anchors fixed, nothing
  internal).
- `materialization-from-scenario` — `direction: forward`, anchors `[SCEN-001-01, SCEN-002-01]`, boundary
  `scenario_materialization`. `layer_pair=None` (the span has multiple mapped pairs; a single-boundary
  unit is driver-prompt-scoped — the proven known-good pattern). Authoring is scoped to materialization
  by the driver prompt.

## Enforcement — the precondition is the guardrail

Layer derivation refuses to start without the mandatory materialization layer present — the
materialization precondition (074-03-04) in `layer-derivation-start` AND `-resume`, run before planning
on every invocation. So **068-12 cannot begin flow derivation without materialization present**
(guardrail-enforced ordering, why 068-26 blocks 068-12), and **068-26 itself uses that precondition's
brownfield branch** (missing + scenario corpus present → confirm the user-facing set → author) as its
sanctioned entry. The requirement/task pairs cannot spill (they derive from flows, which do not exist).

## Run requirement (for when 068-26 executes — NOT done here)

- Driver prompt: child runs `layer-derivation-start` with this spec, authors `scenario_materialization`
  via `ux-write-materialization`, and stops. `layer_pair=None` is expected.
- Ensure the in-copy `unit_task_req_path` bucket exists in the seeded copy for unit-task filing.

## Status

Spec authored + plan-validated (Option A, forward). Code-anchor question fully investigated and
resolved (dropped, with rationale). **No blocking decision outstanding.** No budget spent, no run
executed — the deployed run + its driver prompt are 068-26's execution.
