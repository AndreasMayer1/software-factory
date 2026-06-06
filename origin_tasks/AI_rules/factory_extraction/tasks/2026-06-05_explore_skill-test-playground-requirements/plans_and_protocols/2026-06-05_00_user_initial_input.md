# User initial input (verbatim seed)

This task was prompted by the developer during the redesign-synthesis task TASK-PROC-032-29, immediately after
deciding the scribble-gate workflow's first run would be on a cheap, coupling-rich fixture (fixture-first) built
as a **web (React/Angular)** app.

The developer's unedited words:

---

> i want "Build the cheap, COUPLING-RICH test fixture" to be the starting point of the future general skill
> test hplayground. for now we only build it to test the workflow that we're currently working on. but we need
> to write the requirements for it with all skills in mind. so we need an exploration task to create those
> requirements. it'll be an epic (for everything) + features for the parts we need now.

---

Decisions the developer made when this task was created (2026-06-05, via the redesign task's decision prompts):

- **Sequencing**: fixture-first — build the coupling-rich fixture, validate the redesigned workflow on it,
  then migrate release 0.0.1; full factory extraction deferred.
- **Fixture technology**: **web (React/Angular)** — chosen over a Flutter in-repo fixture. *This implies
  tech-agnosticism is in scope now*: the scribble→code hand-off contract must separate design-intent from the
  target-binding (Flutter widgets vs React/Angular components), and factory/project boundary labelling moves
  earlier (see redesign task file `10_synthesis_next-steps-plan.md` §4-Q2).
- **Placement**: co-locate this exploration task under `process/AI_rules/factory_extraction/`.
- **Ordering**: independent of the redesign-requirements work (STEP A) — may start anytime, no hard `after`.

Read this as a seed bed, not a spec.
