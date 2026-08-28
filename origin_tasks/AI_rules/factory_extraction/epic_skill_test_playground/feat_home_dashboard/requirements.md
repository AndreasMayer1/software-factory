---
id: REQ-PROC-068-01
status: defined
market_research_refs: [] # No relevant findings identified
trackable_items:
  acceptance_criteria:
    - id: AC-01
    - id: AC-02
    - id: AC-03
    - id: AC-04
---
# Home Dashboard

> **Role (two-tree split — REQ-PROC-068):** this is an *instrument-feature spec* — it states the coupling this
> feature must carry. The product-level definition (screen behaviour, layout, copy) is authored in
> `test_harness_app/requirements_*` via the factory skill chain; it is not duplicated here.

## Overview
The single entry surface of the playground app: a home screen that summarises the user's own rating activity
and is the launch point for every other feature. It is deliberately a **hub** — the structural origin of the
cross-feature UI cascade (P-F) the workflow redesign exists to handle.

## Purpose
The redesign must be validated against a real cross-feature cascade: a shared surface whose interaction model
changes and ripples into dependent features whose own requirements are unchanged. A summary dashboard is the
natural, believable carrier of that coupling in a personal media-rating app, and gives `requ-derive-from-flow`
a genuine shared entry surface to build a design-unit map around.

## Behavior
- The dashboard composes a set of **cards** contributed by dependent features (a recent-ratings card from the
  library, a stats card from insights) plus a **quick-add entry point** to the rating form.
- Dependent features register their card/entry through a published **composition contract**: each card
  declares the surface it renders into and the interaction affordances it relies on.
- When no ratings exist, the dashboard shows an empty state inviting the first rating.
- The dashboard is the only screen reachable on launch; all other screens are reached from it.

## Examples
No prior implementation exists — this is a new fixture app (web target). The dashboard is modelled on the
shape of the real 0.0.1 dashboard→feature dependency so the cascade is minimal but representative
(`…/2026-06-05_06_backpressure_T2_extraction-and-playground.md`, residual-uncertainty note on fidelity).

## Developer Guidelines

### Key Decisions
- The dashboard owns a **composition contract** that dependent features depend on; the contract is the
  coupling. A change to the dashboard's interaction model (e.g. cards becoming tap-to-expand or reorderable)
  is the **scripted P-F cascade origin** and must move the outward surface that dependents render into.
- The dashboard is **tech-agnostic in design-intent**: its scribble describes the surface and affordances, not
  a Flutter or React widget tree *(see epic Cross-Feature Invariants)*.

### Common Pitfalls
- A dashboard that merely *links* to features (no shared rendered surface) would not fire P-F — the wrong end
  state. Dependents must render *onto* the dashboard via the contract, so a contract change cascades.

## Related Requirements
- [Epic: Skill-Test Playground](../requirements.md)
- [feat_library_browse](../feat_library_browse/requirements.md) — cascade dependent
- [feat_collection_insights](../feat_collection_insights/requirements.md) — cascade dependent
- [feat_measurement_instrumentation](../feat_measurement_instrumentation/requirements.md) — records the cascade

## Acceptance Criteria
- [ ] AC-01: The app opens to a single home dashboard that is the launch point for every other feature.
- [ ] AC-02: The dashboard composes cards/entries contributed by at least two dependent features plus a
  quick-add entry to the rating form.
- [ ] AC-03: Dependent features render onto the dashboard through a published composition contract that
  declares the surface and interaction affordances each relies on.
- [ ] AC-04: A change to the dashboard's interaction model changes the outward surface dependents render into
  (the cascade is observable, not merely navigational).
