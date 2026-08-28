---
id: REQ-PROC-068-03
status: defined
market_research_refs: [] # No relevant findings identified
trackable_items:
  acceptance_criteria:
    - id: AC-01
    - id: AC-02
    - id: AC-03
---
# Library Browse

> **Role (two-tree split — REQ-PROC-068):** this is an *instrument-feature spec* — it states the coupling this
> feature must carry. The product-level definition (screen behaviour, layout, copy) is authored in
> `test_harness_app/requirements_*` via the factory skill chain; it is not duplicated here.

## Overview
A list view of all rated items, filterable and searchable, and the contributor of a recent-ratings summary
card onto the home dashboard. It is **cascade dependent #1**: its design draws from the dashboard's
composition contract, so a dashboard interaction-model change ripples into this feature's scribble even though
its own requirement is unchanged.

## Purpose
P-F is only a *cross-feature* cascade if at least two dependents draw from the shared surface. Library Browse
is one such dependent — a believable, data-bound list that both stands alone (browse the collection) and
renders a summary onto the dashboard, making the cascade real rather than intra-feature.

## Behavior
- Shows all rated items as rows (title, type, rating, date); empty state when none exist.
- Supports filtering by type and a text search over titles/tags.
- Contributes a **recent-ratings card** to the dashboard via the dashboard composition contract; that card's
  rendered surface depends on the dashboard's interaction affordances.
- Selecting a row opens that rating in the rating entry form for editing.

## Examples
No prior implementation — new fixture app. The recent-ratings card is the concrete coupling point: it is
specified against the dashboard contract (feat_home_dashboard AC-03), so the cascade log can record this
feature as touched when the dashboard interaction model changes.

## Developer Guidelines

### Key Decisions
- The dashboard card is rendered **through the dashboard composition contract**, not as an independent screen
  fragment — this is what makes the dashboard change cascade here.
- This feature's *own* requirement does **not** change during the scripted P-E/P-F run; it goes stale only via
  the dashboard dependency. That asymmetry is the point (a dependent stales without a self-edit).

### Common Pitfalls
- Duplicating the dashboard card's layout independently (not via the contract) would break the cascade — the
  card must depend on the dashboard surface so a contract change reaches it.

## Related Requirements
- [Epic: Skill-Test Playground](../requirements.md)
- [feat_home_dashboard](../feat_home_dashboard/requirements.md) — the surface this feature renders onto
- [feat_rating_entry_form](../feat_rating_entry_form/requirements.md) — opened from a row

## Acceptance Criteria
- [ ] AC-01: All rated items are listed with title, type, rating, and date, with an empty state when none
  exist.
- [ ] AC-02: The list can be filtered by type and searched by text over titles and tags.
- [ ] AC-03: A recent-ratings card is contributed to the dashboard through the dashboard composition contract
  (so a dashboard interaction-model change reaches this feature).
