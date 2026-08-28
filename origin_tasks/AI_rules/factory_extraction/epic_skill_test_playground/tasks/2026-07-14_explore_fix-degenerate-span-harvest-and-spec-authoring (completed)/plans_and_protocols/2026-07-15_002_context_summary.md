# GATHER — Context Summary (IDEATION, embedded in requ-explore)

Topic: how the layer-derivation build-mode pipeline should treat a **degenerate zero-authoring-pair
span** so a legitimately-complete chain harvests — and the coupled AC-18/19, pre-flight, and
spec-authoring questions.

## Prior art (from the ideation index — context, not law)
- **IDEATION-003** (`…/2026-06-09_explore_brownfield-layer-derivation-mechanism`): both-ends spans
  with ≥2 empty layers converge by folding a hinge seam; imperfect matches are **DOCUMENTED, not
  escalated**; "fixpoint-or-bounded-escalate". Directly relevant: it already established that an
  empty/degenerate boundary should not automatically be an *escalation* — the mechanism distinguishes
  "nothing to reconcile / document it" from "blocked". Our degenerate zero-pair span is the extreme
  case (an adjacent-fixed span with *nothing internal* to author).
- **IDEATION-017** (`…/2026-07-10_explore_anchor-product-kind-detection-gap`): reframed a precondition
  as an out-of-band gate; adversarial finding **ADV-sg-06 = a precondition checked only at `-start`,
  never re-validated on resume**. Relevant to the pre-flight question: a harvestability check must be
  positioned so resume paths cannot skip it.

## The mechanism (verified from scripts + the 068-26 blockers)

**Span resolution** (`scripts/factory/layer_derivation/anchor_span_engine.py`): `resolve_spans(fixed_layers)`
turns the fixed-layer set into ordered spans. `fixed_layers=[persona, scenario]` resolves to **2** spans:
- span 0 `persona-scenario-fixed` — BIDIRECTIONAL, adjacent-fixed, **zero authoring pairs** (nothing
  internal to fill between two adjacent fixed layers).
- span 1 `materialization-from-scenario` — FORWARD, real authoring pairs.

The engine already carries a derivability screen: `screen_derivability` / `DerivabilityResult` /
`DerivabilityError` fires when a boundary extractor returns an **empty required-elements set**
("the anchor cannot define a coverage target"). This is *adjacent-but-different* from a zero-pair
span: it's about an anchor with nothing to satisfy, detected **before** authoring. The degenerate
zero-pair span is the case where the *span itself* has no internal layer to author.

**Planning** (`backfill_orchestration.py`): `plan_chain(spans, span_units, …)` **requires**
`len(span_units) == len(spans)` (else `malformed spec: span_units length N does not match resolved
spans M`, exit 2). So a 2-span resolution forces a unit for span 0 — it **cannot be dropped** in a spec.

**Unit disposition**: `UnitStatus ∈ {PENDING, IN_PROGRESS, DONE, ESCALATED}`. `complete_unit` forces a
DONE without a passing content gate to `ESCALATED('gate_content_fail')`; a caller-initiated ESCALATE
records `'missing_answer'`. Span 0 has an **empty gate** (nothing authored to judge) → completing it
lands `ESCALATED('gate_content_fail')`. The mechanism's own unit test documents this as the intended
"skip past span 0" (`test_backfill_orchestration.py:1061 → complete_unit(state,"u0",ESCALATED)`).

**Harvest oracle** (`scripts/playground/acceptance_oracles.py::chainstate_complete_predicate`): the ONE
injected oracle `build.py` offers. Rule = **strict all-DONE** — `all(unit.status is DONE)`. An ESCALATED
unit ⇒ predicate False. Comment: "an ESCALATED unit means the chain reached a blocker and the derivation
did NOT finish". Missing chain-state file ⇒ False.

**Run classification** (REQ-PROC-068 AC-18): {complete, interrupted, blocked, abandoned}. A clean child
exit + oracle "not-finished" + **no** recorded blocker/escalation artifact ⇒ **abandoned** = "a run
failure attributable to the completion guidance of the skill under test". AC-19: no oracle ⇒ "cannot
certify complete" ⇒ INCONCLUSIVE (never harvests, never reports success).

## The defect (verified end-to-end locally in 068-26)
span 0 ESCALATED + span 1 DONE ⇒ strict all-DONE oracle = False ⇒ run classified **abandoned** ⇒ copy
preserved, **harvest skipped**. A chain that **plans fine can never harvest**. Two truthfulness problems:
1. **Mis-blame**: AC-18 "abandoned" blames the *skill under test's completion guidance*, but here the
   chain had a **mandatory no-op span** the *spec structure* forced — the skill under test did nothing
   wrong. AC-18 is HIGH-consequence EGP-F.
2. **"plan-success ≠ harvestable"**: the spec author (an LLM) got a clean `plan_chain` and reasonably
   assumed the chain could complete; the un-harvestability only surfaced after a deployed run was spent.

Per-task **Option-A workaround** (068-26, 068-12 `_03`): drive span 0 to DONE truthfully by enriching the
already-approved persona↔scenario boundary and applying the drift rubric for real. Works, no mechanism
change, but must be repeated per spec — the root cause, the missing plan-time guardrail, and the missing
authoring guidance remain.

## Adjacent (out-of-scope) finding
068-26 `_05` blocker: harvested-materialization **provenance** cannot resolve post-harvest
(`check_materialization_provenance.py` is hardwired to flutter_app). Separate concern from the
degenerate-span/harvest defect — noted, not owned by this task.

## Spec-authoring surface (question 4)
The spec is a JSON `{fixed_layers, span_units, unit_task_req_id, unit_task_req_path, …}` authored by an
**LLM**, not the developer. `layer-derivation-start` is the entry skill; `layer-derivation-resume` /
`-status` exist. There is **no governed template or guidance** teaching the span↔unit mapping or the
degenerate-span rule. Developer directive: guidance belongs in the **skill/mechanism layer, NOT `doc/`**
(product-level only).

## Information Map
- Mechanism: `scripts/factory/layer_derivation/anchor_span_engine.py` (resolve_spans, screen_derivability,
  DerivabilityError), `…/backfill_orchestration.py` (plan_chain, complete_unit, UnitStatus, load_chain,
  spec parsing/CLI, exit codes 0/2/3/4/5).
- Oracle: `scripts/playground/acceptance_oracles.py` (chainstate_complete_predicate, strict all-DONE).
- Wrapper: `scripts/playground/build.py` (injected completion predicate, run classification/registry/harvest).
- Requirements: REQ-PROC-068 (AC-14..AC-19 — completion/harvest/classification; AC-18/19 HIGH EGP-F);
  REQ-PROC-071 epic + features (`feat_anchor_span_engine`=071-04, `feat_backfill_orchestration`=071-06).
- Skills: `layer-derivation-start`, `layer-derivation-resume`, `layer-derivation-status`.
- Discovery: 068-26 `_02` (blocker), `_03` (Option-A workaround), `_05` (adjacent provenance gap).
