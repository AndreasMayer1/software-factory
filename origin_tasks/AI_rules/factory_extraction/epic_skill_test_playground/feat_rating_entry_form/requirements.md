---
id: REQ-PROC-068-02
status: defined
market_research_refs: [] # No relevant findings identified
trackable_items:
  acceptance_criteria:
    - id: AC-01
    - id: AC-02
    - id: AC-03
    - id: AC-04
    - id: AC-05
---
# Rating Entry Form

> **Role (two-tree split — REQ-PROC-068):** this is an *instrument-feature spec* — it states the coupling this
> feature must carry (T4 + the P-E edit target). The product-level definition, **including the data-point
> table below**, is authored in `test_harness_app/requirements_*` via the factory skill chain; the table is
> reproduced here only as the coupling reference and relocates to the project tree when that requirement is
> authored (it must not be duplicated long-term).

## Overview
The screen for adding or editing a rating of a movie or book: a multi-field, multi-format, validated form
backed by a domain Rating value-object. It is the playground's **validation-heavy form** (exercises the
domain→design ordering, T4) and the **target of the scripted mid-release requirement edit** (P-E).

## Purpose
The redesign needs two things only a genuinely hard data-bound form provides: (1) a case to test whether a
precise **data-point definition in the requirement** suffices for the scribble author or whether the domain
code must exist first (T4, `…/2026-06-05_08_backpressure_T4_domain-before-design.md`); and (2) an approved
scribble that a mid-release requirement edit can **staleness-invalidate** (P-E). A rating form with several
formats and validation rules is the smallest such form that is still genuinely hard.

## Behavior
- The form captures the data points below; each is validated before the rating can be saved, and an invalid
  field shows an inline error.
- Saving a valid form persists the rating locally; an existing rating can be re-opened and edited.
- The form serves two personas with conflicting values — the **Archivist** (wants completeness) and the
  **Quick-Logger** (wants speed); required vs. optional fields are the locus of that trade-off.

### Data points (the precision floor — T4)
| Field | Type | Format / validation | Required |
|---|---|---|---|
| Title | text | non-empty, ≤ 200 chars | yes |
| Type | enum | one of {movie, book} | yes |
| Rating | scale | **see AC-04 (the edit-designated rule)** | yes |
| Date consumed | date | a valid date, not in the future | yes |
| Tags | list of text | each ≤ 30 chars, no duplicates, ≤ 10 tags | no |
| Review | long text | ≤ 2000 chars | no |

## Examples
No prior implementation — new fixture app. The Rating value-object carries its own non-Presentation validation
ACs, which is the detector for "data-bound" that makes the conditional domain-before-scribble edge applicable
(T4 report §"data-bound detector").

## Developer Guidelines

### Key Decisions
- The data-point table above is authored **in this requirement** (the precision floor) so the scribble is
  derivable from the requirement, not from implemented code *(design-intent stays tech-neutral)*.
- The **Rating scale** field (AC-04) is the **edit-designated requirement**: after its scribble is approved,
  this rule is changed (granularity changes) to fire the SCI staleness path. Any valid implementation must
  keep the scale rule isolated enough that editing it invalidates only the affected scribble.

### Common Pitfalls
- Under-specifying the data points here would force the scribble author to read code — eroding the RE-DERIVE
  separation the redesign depends on. The table must be precise enough to scribble from alone.

## Related Requirements
- [Epic: Skill-Test Playground](../requirements.md)
- [feat_home_dashboard](../feat_home_dashboard/requirements.md) — reached via the dashboard quick-add
- [feat_measurement_instrumentation](../feat_measurement_instrumentation/requirements.md) — stall report on the edit

## Acceptance Criteria
- [ ] AC-01: A rating capturing title, type, rating, date consumed, tags, and review can be added and saved
  when all fields are valid.
- [ ] AC-02: Every field validates against the data-point table before save, and an invalid field displays an
  inline error message.
- [ ] AC-03: An existing rating can be re-opened and edited.
- [ ] AC-04: The rating scale is governed by a single, isolated rule whose edit invalidates only this form's
  approved scribble (the P-E edit target).
- [ ] AC-05: Required vs. optional fields reflect the Archivist/Quick-Logger value trade-off (completeness vs.
  speed).
