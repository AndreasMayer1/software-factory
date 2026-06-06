---
task_id: TASK-PROC-066-03
type: explore
parent_requirement: REQ-PROC-066
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 5
impact_reason: I5-ENAB
status: in_progress
effort: L
created: 2026-06-05
started: 2026-06-05
expected_tool_calls: 40
skill_chain_depth: 3
synthesis_dependent: true
synthesis_justification: "Must hold three things at once — the full general skill-test-playground vision (exercises all factory skills over time), the minimal now-slice that validates the scribble-gate redesign (P-E/P-F triggers + a validation-heavy form), and the web/tech-agnostic-handoff constraint — and shape one epic + features so the now-slice is a faithful subset of the eventual whole. Splitting loses the whole↔slice coherence that is the point."
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Author the requirements for a cheap, coupling-rich web (React/Angular) test-fixture app that is the seed of a future GENERAL skill-test playground for the whole Software Factory: ONE epic for the full playground vision + FEATURES for the slice needed now to validate the scribble-gate workflow redesign (TASK-PROC-032-29). Requirements written with all factory skills in mind so the playground can grow later."
release_description: ""
opus_recommended: true   # reason: explicit decision/design task + non-splittable synthesis — the general-playground vision, the minimal validation slice, and the tech-agnostic constraint must be reasoned about together so the now-features are a clean subset of the eventual epic
writes_requirements: true
requirements_version:
  commit: ""
  file: ../requirements.md
session_id: d5dfeecc-7307-461f-99c1-d21dc54671fa
session_account: gmail
---
# Goal: Author the Requirements for the Skill-Test Playground (Epic + Now-Slice Features)

## Objective

We need a cheap place to *run the factory on*. Iterating the scribble-gate workflow redesign
(TASK-PROC-032-29) against the real Flutter app costs a full release decomposition per loop; a small consumer
project makes each loop 10–100× cheaper. The developer wants that consumer to be more than a throwaway: it
should be the **seed of a general skill-test playground** for the *whole* Software Factory — a project we keep,
grow, and use to exercise factory skills as they evolve.

This task does not build the app. It **authors the requirements** for it — and the central unknown is the
*shape*: how to write **ONE epic** that captures the full general-playground vision (in principle able to
exercise every factory skill over time) while carving out **FEATURES** for only the slice we need *now* — just
enough to validate the scribble-gate redesign — such that the now-features are a faithful **subset** of the
eventual whole, not a throwaway that has to be rewritten when the playground grows.

Open questions this exploration must enter:
- **What is the general playground, as a product?** The developer's seed is a *personal, offline movie/book
  rating app* (an individual's private notes on their own ratings). Is that the right vehicle to exercise the
  *whole* factory, or does the general vision need a richer product surface? What makes a product a good
  *factory exerciser* (varied flows, personas, a design system, data-bound forms, cross-feature surfaces)
  rather than just a believable app?
- **What is the minimal now-slice?** The redesign needs the fixture to trigger the two hard cases the whole
  redesign exists for: **P-E** (a mid-release requirement edit that staleness-invalidates an approved
  scribble) and **P-F** (a cross-feature UI cascade — a shared dashboard/entry surface whose change ripples
  into dependent features' scribbles even though their requirements are unchanged), plus **one
  validation-heavy form** to exercise the domain→design ordering (T4). What is the smallest set of features
  that *structurally* contains all three? (`06_backpressure_T2` argues: complexity must live in the
  *couplings*, not the feature count — a "less complicated" app is the wrong playground.)
- **How do we write requirements "with all skills in mind"?** The full top-down chain (persona → scenario →
  flow → requirement → scribble → code) must be runnable on this product. What does each factory skill need
  from the playground's requirements to have something real to chew on — and how do we author the epic so
  those hooks exist without bloating the now-slice?
- **What does a web (React/Angular) target force?** The fixture is web, not Flutter. This is the forcing
  function for tech-agnosticism: the scribble→code hand-off contract must split *design-intent* (tech-neutral)
  from *target-binding* (Flutter widgets vs React/Angular components), and the factory/project boundary must
  be labelled as skills are exercised. What web-side surface (toolchain, quality gates, `doc/` guidelines)
  does the factory not yet have, and how much of that is in scope for the now-slice vs deferred?

## Background

The redesign task TASK-PROC-032-29 concluded (after the 2026-06-05 feedback round) that the scribble-gate
workflow should make its first real run on a **cheap, coupling-rich fixture**, *then* migrate release 0.0.1 —
with full factory extraction (TASK-PROC-066-01) deferred. The developer chose the fixture to be a **web
(React/Angular)** app and asked that it be the **starting point of a future general skill-test playground**,
with requirements authored now, **with all skills in mind**, as an **epic + now-slice features**.

**Primary substrate (read first)** — the redesign synthesis, which sets the fixture's purpose, the
coupling-rich requirement, and the web/tech-agnostic implication:
- `../../../workflows/ui_sketch_iteration_workflow/tasks/2026-06-04_explore_redesign-implementation-workflow-scribble-gate/plans_and_protocols/2026-06-05_06_backpressure_T2_extraction-and-playground.md`
  — why the playground must be coupling-rich (P-E/P-F), why "less complicated" is the wrong target, the
  Flutter-vs-web trade-off.
- `…/2026-06-05_10_synthesis_next-steps-plan.md` — STEP B (the fixture) in the plan; §4-Q2 records the web
  decision and its tech-agnostic implications (hand-off contract split; boundary labelling pulled earlier).
- `…/2026-06-05_08_backpressure_T4_domain-before-design.md` — the validation-heavy-form rationale (why one
  data-bound form belongs in the now-slice).

The developer's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-06-05_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time: no `requirements.md` exists yet for this area
(`REQ-PROC-066` is the factory-extraction parent; this task co-locates here and writes new requirements).

Current requirements: ../requirements.md

## How to Approach This

Use design thinking — empathize before defining, diverge before converging, let questions lead, iterate. A
single pass will not be enough. The hardest move is the **whole↔slice** one: design the general-playground
epic and the now-slice features *together*, so the now-features are a clean subset, not a stub that gets
thrown away. Ground the product choice in what makes a good *factory exerciser*, not in what makes a believable
app.

Author the requirements through the sanctioned path — this is `requ-explore` work (epic first, then the
now-slice features). Do not hand-write `requirements.md`; route through `requ-explore`. If personas/scenarios/
flows are needed for the playground product, they go through the user-needs chain (`ux-write-persona` /
`ux-write-scenario` / `ux-create-flow`) — but keep the now-slice minimal.

## Seeds

1. **Whole vs slice — the central tension.** What belongs in the *epic* (the general playground: every skill
   should eventually have something to bite on) versus the *now-features* (only the scribble-gate validation)?
   Where is the line such that the now-features are a strict subset of the eventual whole?

2. **What makes a good factory exerciser?** A personal offline movie/book rating app is the developer's seed.
   Stress it: does it naturally produce varied flows, multiple personas, a design system, data-bound validated
   forms, and *shared cross-feature surfaces* (a dashboard)? If not, what minimal product shape does?

3. **Engineering the couplings on purpose (P-E and P-F).** The now-slice must *structurally* contain a shared
   dashboard/entry surface that 2–3 dependent features draw from (fires P-F) and at least one requirement
   designed to be edited mid-stream (fires P-E). How do you specify these in requirements so the cascade and
   the staleness path actually trigger — and so the L5 width-breaker (T3) can be observed and its threshold N
   measured?

4. **The validation-heavy form (T4).** One feature should be a complex, multi-field, multi-format,
   validated form — to test the domain→design ordering and whether requirement-precision (a data-point table)
   suffices or domain-code-first is needed. What is the smallest such form that is still genuinely hard?

5. **Web target & tech-agnosticism.** What does choosing React/Angular force on the factory now — the
   design-intent/target-binding split in the hand-off, a web `doc/` surface, web quality gates? What is in
   scope for the now-slice vs deferred to when the playground grows / to extraction (TASK-PROC-066-01)?

6. **"All skills in mind."** Walk the factory skill graph (`scripts/factory/render_factory_map.py`) and, for
   each skill, ask: what would this playground need so that skill has something real to run on *eventually*?
   Capture those as epic-level hooks without pulling them into the now-slice.

7. **Where do the playground's product requirements ultimately live?** Co-located here under
   `factory_extraction` for now (developer decision) — but is that the right long-term home for a *product*
   epic (vs. a dedicated tree)? Surface the trade-off; it interacts with the factory/project boundary that
   TASK-PROC-066-01 will draw.

## Execution Model

Gather raw material — read the redesign substrate, the developer's seed, and the factory skill graph — then
synthesize iteratively. Author via `requ-explore` (epic → now-slice features). Expect to define a small set of
personas/scenarios/flows for the playground product; keep them minimal and coupling-focused.

The session's model is fixed at launch (Opus — `opus_recommended: true`). No mid-session model switching.

**Web research**: if a seed needs external prior art (e.g. how others build minimal apps to test codegen/
design pipelines, or React vs Angular for a tiny offline app), delegate to a spawned `general-purpose` agent
with a focused question framed as a question; never run WebSearch inline.

**Task-ordering (developer directive 2026-06-05):** every task this task or its decomposition creates (the
playground feature/build tasks, any derived impl tasks, the T-B2/T-B3 fixture tasks) MUST be appended to
`.claude/task_ordering_priority_override.txt` — they carry no `target_package`, so they will not surface in
`next_tasks.py` otherwise.

## Output

A future implementer (or `requ-derive-from-flow` / `release-begin-impl` run) must be able to read the output
and stand up the playground without replaying this session. "Done" looks like:
- **One epic requirement** for the general skill-test playground — its product concept, the personas/flows it
  will host, and the per-skill "hooks" that let the full factory eventually exercise it.
- **Now-slice feature requirements** — the minimal set that structurally triggers P-E (mid-release edit), P-F
  (cross-feature cascade via a shared dashboard/entry surface), and a validation-heavy form (T4) — authored as
  a clean subset of the epic.
- A clear statement of the **web/tech-agnostic implications** captured as requirements/constraints (hand-off
  design-intent vs target-binding; what web-side factory surface is in scope now vs deferred).
- The now-slice requirements MUST specify the **six measurement probes** the workflow emits when run on the
  fixture — stall report, cascade log, salvage diff, facet-tag audit, fixture↔release behaviour log, and a
  graph-stats dump — so the redesign's empirical questions are answerable *by construction*. (Rationale and the
  exact metrics: the redesign task's `…/2026-06-05_12_contingency_branch-plans.md` §0.6 + "Fixture
  instrumentation".) The fixture is an **instrumented** app, not just an app.
- Honest identification of what remains uncertain and the decisions the developer still needs to make.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain
- [ ] The user has approved the final synthesis and stated what to do next
- [ ] The action stated by the user as the next step was performed successfully

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies. Independent of the redesign-requirements work (STEP A) by developer decision — may start anytime. The redesign synthesis is read as substrate but does not block. |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-29](../../../workflows/ui_sketch_iteration_workflow/tasks/2026-06-04_explore_redesign-implementation-workflow-scribble-gate/goal.md) | Source — its synthesis (`06`, `08`, `10`) sets this fixture's purpose, the coupling-rich requirement (P-E/P-F), the validation-form rationale, and the web/tech-agnostic implication. |
| [TASK-PROC-066-01](../2026-05-28_explore_software-factory-extraction/goal.md) | Sibling — the playground is the test consumer for the factory this task will extract; the factory/project boundary it draws interacts with Seed 5/7. Coordinate, don't duplicate. |
| [TASK-PROC-066-02](../2026-06-03_explore_ralph-loop-builds-factory/goal.md) | Sibling — Ralph-loop factory build-out; the playground could become its run target. |
