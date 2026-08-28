---
id: REQ-PROC-068-04
status: defined
market_research_refs: [] # No relevant findings identified
trackable_items:
  acceptance_criteria:
    - id: AC-01
    - id: AC-02
    - id: AC-03
---
# Collection Insights

> **Role (two-tree split — REQ-PROC-068):** this is an *instrument-feature spec* — it states the coupling this
> feature must carry. The product-level definition (screen behaviour, layout, copy) is authored in
> `test_harness_app/requirements_*` via the factory skill chain; it is not duplicated here.

## Overview
A small set of derived statistics over the user's ratings (counts by type, rating distribution, activity over
time), surfaced as a stats card on the home dashboard and as a detail view. It is **cascade dependent #2** —
the second feature drawing from the dashboard's composition contract, which makes the P-F cascade genuinely
multi-dependent.

## Purpose
A single dependent could be dismissed as intra-feature coupling. A second, *different-shaped* dependent
(derived/aggregate data rather than a list) confirms the cascade is a true cross-feature fan-out and lets the
cascade log measure width across dependents of different kinds — the input to the L5 width-breaker threshold N
(`…/2026-06-05_07_backpressure_T3_recursion-safety.md`).

## Behavior
- Computes derived statistics from the stored ratings: count by type, distribution across the rating scale,
  and count over time.
- Surfaces a **stats card** on the dashboard via the dashboard composition contract, and a detail view reached
  from that card.
- Recomputes when ratings change; shows an empty state when there are no ratings.

## Examples
No prior implementation — new fixture app. Because its values are *derived* from the Rating domain, this
feature also exercises domain-bound derivation (a second flavour of data-binding distinct from the entry
form's input-binding).

## Developer Guidelines

### Key Decisions
- The stats card renders **through the dashboard composition contract** (same coupling mechanism as Library)
  so dashboard changes cascade here too — giving the cascade two structurally different dependents.
- Statistics are **derived**, not stored; the feature depends on the Rating domain entity, not on persisted
  aggregates.

### Common Pitfalls
- Storing pre-computed aggregates would hide the domain dependency and weaken the domain→design signal — keep
  insights derived.

## Related Requirements
- [Epic: Skill-Test Playground](../requirements.md)
- [feat_home_dashboard](../feat_home_dashboard/requirements.md) — the surface this feature renders onto
- [feat_rating_entry_form](../feat_rating_entry_form/requirements.md) — the source domain entity

## Acceptance Criteria
- [ ] AC-01: Derived statistics (count by type, rating distribution, count over time) are computed from stored
  ratings and shown in a detail view, with an empty state when none exist.
- [ ] AC-02: A stats card is contributed to the dashboard through the dashboard composition contract.
- [ ] AC-03: Statistics are derived from the Rating domain entity rather than from stored aggregates, and
  reflect changes to the underlying ratings.
