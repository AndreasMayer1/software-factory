---
id: REQ-PROC-068-05
status: defined
market_research_refs: [] # No relevant findings identified
trackable_items:
  acceptance_criteria:
    - id: AC-01
    - id: AC-02
    - id: AC-03
    - id: AC-04
    - id: AC-05
    - id: AC-06
---
# Measurement Instrumentation

## Overview
The cross-cutting requirement that the playground is an **instrumented** fixture: running a factory workflow
against it emits six measurement artifacts that answer the redesign's empirical questions by construction
rather than by manual archaeology.

## Purpose
"Measure on the fixture" is hand-wavy unless the fixture and the workflow actually emit the numbers. The
redesign's contingency plan (`…/2026-06-05_12_contingency_branch-plans.md` §"Fixture instrumentation")
pre-registers six metrics with thresholds; this requirement makes the six artifacts a build-time obligation so
the stall fraction, cascade width, salvage fraction, fixture↔release fidelity, facet-tag accuracy, and leading
graph indicators are all observable. Without them the playground validates nothing measurable.

## Behavior
A complete workflow run against the playground (scripted P-E edit + P-F cascade) produces, as persisted
artifacts:

| # | Artifact | Content | Emitted by |
|---|---|---|---|
| 1 | stall report | blocked coding tasks + each task's design-unit, on the scripted mid-release edit | SCI audit / release-finalize-impl |
| 2 | cascade log | per origin: dependents touched per hop, visited-set, per refresh "did the outward surface move?" | lazy-wavefront detector |
| 3 | salvage diff | the quarantine→re-derive diff, persisted per re-derived task | release-derive-code |
| 4 | fixture↔release behaviour log | which cascade/staleness behaviours were/weren't seen on the fixture vs 0.0.1 | STEP-D reconcile |
| 5 | facet-tag audit | auto-tag vs human-confirmed tag per AC | requ-explore / decomposition |
| 6 | graph-stats dump | per-unit coding-task count, entry-graph hub in-degree, `both`-tag share | computed from the design-unit map + entry-reference graph |

## Examples
No prior implementation — new fixture app. The probes are emitted by the *workflow* acting on the fixture, not
by the fixture's own UI; the playground's coupling structure (the dashboard hub + the edit-designated rating
rule) is what gives each probe non-trivial data to record.

## Developer Guidelines

### Key Decisions
- The six artifacts are an obligation on the **playground + workflow run together**, not on the app's runtime
  behaviour — they are produced during the factory's processing of the fixture.
- Artifact #6 (graph-stats dump) is computable **before any scribble runs** (start of the build), so the
  leading indicators can pre-arm the redesign's branch decisions.

### Common Pitfalls
- Treating instrumentation as an afterthought (manual measurement post-hoc) would defeat the purpose — the
  artifacts must be emitted by construction during the run.

## Related Requirements
- [Epic: Skill-Test Playground](../requirements.md)
- [feat_home_dashboard](../feat_home_dashboard/requirements.md) — cascade log source (#2)
- [feat_rating_entry_form](../feat_rating_entry_form/requirements.md) — stall report source (#1)

## Acceptance Criteria
- [ ] AC-01: A workflow run on the scripted mid-release edit emits a **stall report** listing blocked coding
  tasks with each task's design-unit.
- [ ] AC-02: A cascade origin emits a **cascade log** recording dependents touched per hop, the visited-set,
  and per refresh whether the outward surface moved.
- [ ] AC-03: Each re-derived task persists a **salvage diff** (quarantine→re-derive).
- [ ] AC-04: The STEP-D reconcile emits a **fixture↔release behaviour log** of which cascade/staleness
  behaviours were and were not seen on the fixture.
- [ ] AC-05: Decomposition emits a **facet-tag audit** of auto-tag vs human-confirmed tag per AC.
- [ ] AC-06: A **graph-stats dump** (per-unit coding-task count, entry-graph hub in-degree, `both`-tag share)
  is produced from the design-unit map and entry-reference graph at the start of the build.
