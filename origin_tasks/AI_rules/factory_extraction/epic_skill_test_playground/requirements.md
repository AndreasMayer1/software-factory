---
id: REQ-PROC-068
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
# Epic: Skill-Test Playground

## Overview
A small, offline, single-user **personal media-rating & journaling app** (the developer's private notes on the
movies and books they have consumed: ratings, tags, a short review, and a home dashboard that summarises their
own activity). It exists to be the thing the Software Factory *runs on* — a cheap, coupling-rich consumer
project the factory's skills can be exercised against, far cheaper per workflow run than the real Flutter app.

## Purpose
Iterating any factory workflow against the real release costs a full release decomposition per loop. A small
consumer makes each loop 10–100× cheaper. This playground is that consumer — kept and grown over time, not a
throwaway. Its first job is to validate the scribble-gate workflow redesign (TASK-PROC-032-29); its standing
job is to give *every* factory skill something real to bite on. The product is chosen as a good **factory
exerciser** — its complexity lives in its *couplings*, not its feature count — not as a believable app.

## Scope
**Included (the product surface, grown over time):** a home dashboard, rating entry/edit, library browse,
collection insights, and the personas/flows behind them. **Excluded:** anything multi-user, online, or
networked; being a shippable product; replacing or merging with the mood-tracker. This epic is *not* directly
implementable — only its features are.

## Features
Now-slice (built first — the minimal subset that structurally contains the redesign's hard cases):
- [feat_home_dashboard](feat_home_dashboard/requirements.md) — shared entry/hub surface; origin of the
  cross-feature UI cascade (P-F).
- [feat_rating_entry_form](feat_rating_entry_form/requirements.md) — validation-heavy data-bound form
  (domain→design ordering, T4); target of the scripted mid-release edit (P-E).
- [feat_library_browse](feat_library_browse/requirements.md) — list/filter view; cascade dependent #1.
- [feat_collection_insights](feat_collection_insights/requirements.md) — derived stats card/view; cascade
  dependent #2.
- [feat_measurement_instrumentation](feat_measurement_instrumentation/requirements.md) — the six measurement
  probes the fixture + workflow must emit.

Growth (not yet built — added around the same dashboard without rewriting the now-slice): search,
recommendations-from-own-data, import/export, multiple collections, theming.

## User Needs
The playground hosts its own product personas, described here rather than minted into the mood-tracker's
user-needs tree (a fixture must not pollute the real product — see Dependencies):
- **Archivist** — values completeness and data integrity; wants every field filled, nothing lost.
- **Quick-Logger** — values low-friction speed; wants to log a rating in seconds.
Their values conflict on the entry form (completeness vs. speed) — a real VCD case. Flows (add a rating,
browse the library, review insights) all pass through the home dashboard.

## Cross-Feature Invariants
- **Shared entry surface:** the home dashboard publishes a composition contract; dependent features register a
  card/entry on it. Changing the dashboard's interaction model ripples into dependents' design even when their
  own requirements are unchanged (this is the P-F cascade, on purpose).
- **Tech-agnostic hand-off:** the scribble→code hand-off separates **design-intent** (tech-neutral) from
  **target-binding** (the web component framework). No factory artifact for this playground may assume Flutter.
- **Instrumented by construction:** running a factory workflow against this playground emits the six
  measurement probes (see feat_measurement_instrumentation) — the playground is an instrumented app.
- **Factory/project boundary:** as each skill is exercised on this second consumer, it is labelled
  factory-vs-project; those labels feed TASK-PROC-066-01 (coordinate, do not duplicate).

## Dependencies
- **Web toolchain & gates** — TASK-PROC-066-04 stands up the React/Angular toolchain, web `doc/` surface, and
  web quality gates (deferred from this epic; `after` this task). Recommended framework: React.
- **Factory extraction** — TASK-PROC-066-01 (sibling); the boundary this epic labels interacts with it.
- **Playground user-needs home** — whether to formalise the personas/flows above into a dedicated playground
  user-needs sub-tree is an open developer decision (kept out of `requirements_user_needs/` for now).

## References
- Redesign synthesis: `…/2026-06-04_explore_redesign-implementation-workflow-scribble-gate (completed)/`
  reports `06`, `08`, `10`, `12`.
- This task's synthesis: `tasks/2026-06-05_explore_skill-test-playground-requirements/plans_and_protocols/2026-06-05_01_synthesis_playground-shape.md`
