---
task_id: TASK-PROC-057-01
type: explore
parent_requirement: REQ-PROC-057
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 5
impact_reason: I5-ENAB
status: pending
effort: L
created: 2026-05-26
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Define the apex software-factory purpose requirement (north star + continuous-improvement loop), grounded in PERSONA-015"
release_description: ""
opus_recommended: true   # reason: apex/cross-cutting explore spanning all factory requirements + explicit decide-approach (new requirement vs broaden REQ-PROC-044) + trade-off framing
writes_requirements: true
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Define the Software Factory's Purpose & Continuous-Improvement Loop

## Objective

The factory has a clear north star in the user's mind — *produce very good app outcomes with the least possible sustainable effort* — but no requirement states it. We do not yet know the right shape for capturing it: what exactly the apex requirement should assert, how to make it verifiable rather than aspirational, where it should live, and how it relates to the requirements that already own the individual "good outcome" dimensions. This exploration should discover that shape and produce the requirement.

It must also resolve two specific decisions (see Decisions to Resolve).

## Background

The user's north star: *"a software factory that leads to very good outcomes with the least possible effort"* — where "good outcomes" spans dev & app security, code quality/maintainability, app performance, UX, and testing. Today this purpose is **implicit and scattered**: it lives partly in CLAUDE.md (the constitution) and partly across a constellation of quality requirements, but no single requirement states it. CLAUDE.md is the constitution (how we operate) and is **not** a place for requirements — so the purpose deserves a real requirement.

The grounding already exists: **PERSONA-015 (App Provider / The Creator)**, `evidence_level: grounded`, approved. Its Jobs-to-Be-Done, Decision Principle #5 ("minimum effective dose"), and sustainability constraints (solo dev, longevity over velocity, no team to delegate to) are the factory's north star one level up: the factory is the App Provider's *instrument* to serve the user personas sustainably, just as the app is the user personas' instrument.

The "good outcomes" themselves are already owned by child requirements — the apex must **reference, not redefine** them:
- Dev & app security, supply chain → REQ-PROC-052, REQ-PROC-056
- Code quality / maintainability → REQ-PROC-046, REQ-PROC-051
- Testing → REQ-PROC-002, REQ-PROC-005
- UX & performance → `non-functional/ui_ux_design_system/*`, `non-functional/` performance requirements
- Factory-machine integrity → REQ-PROC-044
- Continuous improvement automation → REQ-PROC-006
- External tooling input channel → REQ-PROC-055

This task was spun off from the han plugin evaluation (TASK-PROC-055-01); its synthesis report and the reframed REQ-PROC-055 are useful prior context.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-26_00_user_initial_input.md`

Read it as a seed bed, not a spec.

A requirement ID has been pre-allocated: **REQ-PROC-057** (reserve marker at `requirements_tasks/process/AI_rules/.reserve-REQ-PROC-057`). Use it when writing `requirements.md` and delete the marker afterward — UNLESS the broaden-REQ-PROC-044 decision below is taken, in which case release (delete) the marker without writing a new requirement.

## How to Approach This

Use design thinking — empathize before defining, diverge before converging, let questions lead, iterate. A single pass will not be enough. Surface surprises.

## Seeds

These are lenses, not a to-do list.

1. **What does the apex actually assert that the children do not?** The risk is an empty restatement of the constitution. What is the *unique* content — the purpose, the effort/risk axis, the improvement loop, the trade-off discipline — that has no other home?

2. **How do you make a "north star" verifiable instead of aspirational mush?** Explore governance-property ACs, e.g.: every factory capability/skill traces to a PERSONA-015 value or a child quality requirement; any factory change that trades an outcome dimension for speed/effort records a trade-off (VCD/VTR); the improvement loop has named input channels and a minimum-effective-dose gate. Which of these survive the end-state test?

3. **New requirement vs. broaden REQ-PROC-044?** REQ-PROC-044 ("Software Factory Quality Properties") already covers factory-*machine* integrity (reliability, transparency, maintainability, robustness, determinism) with `stakeholder: app_provider`. Is the apex a new requirement with 044 as a child, or should 044 be broadened to *become* the apex? What are the costs of each (scope-creep of an active req vs. an extra layer)?

4. **What is the continuous-improvement loop, exactly?** Its input channels appear to be: retrospectives (`claude-optimize`), metrics-based improvement (REQ-PROC-006), and external tooling (REQ-PROC-055). Is that the complete set? Is there a missing channel (e.g. incident/defect feedback, doc-update-guidelines)? How does "least effort" get measured or bounded at all?

5. **Where is the boundary between this requirement and the CLAUDE.md constitution?** The constitution says *how we operate*; the requirement should state *the binding purpose and verifiable properties*. What, if anything, should move out of CLAUDE.md into the requirement — and what must stay in the constitution?

6. **Where should it live, and what is the parent/child wiring?** Proposed home: `requirements_tasks/process/AI_rules/factory_purpose/`. Which existing requirements become children/contributors, and how is that expressed without creating brittle bidirectional churn?

## Decisions to Resolve (must be settled before completion)

1. **New apex requirement OR broaden REQ-PROC-044.** Make the call explicitly and record the reasoning. If "broaden 044": release the pre-allocated REQ-PROC-057 marker, broaden 044 via `requ-explore`, and treat that as the apex.

2. **Adapt REQ-PROC-055.** Its User Story already ladders up to the factory purpose, but the parent link must be wired once the apex exists (reference the apex as parent/contributor relationship). Update REQ-PROC-055 accordingly as part of this work.

## Execution Model

Gather raw material — read the App Provider persona in full, the child requirements above, REQ-PROC-044, REQ-PROC-006, the reframed REQ-PROC-055, and CLAUDE.md. Synthesize iteratively.

The session's model is fixed at launch — `opus_recommended: true`, run with Opus.

**Web research** (only if useful — e.g. how others express a "definition of done / north star" for AI dev pipelines): delegate to a spawned `general-purpose` agent with a focused question; never run WebSearch inline.

## Output

A written synthesis (in `plans_and_protocols/`) and the resulting requirement: either a new REQ-PROC-057 at `factory_purpose/requirements.md`, or a broadened REQ-PROC-044 — with the decision and reasoning recorded. REQ-PROC-055 adapted to sit under the apex. A future reader should understand the factory's purpose, the improvement loop, and how every child requirement contributes, without re-deriving it.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
