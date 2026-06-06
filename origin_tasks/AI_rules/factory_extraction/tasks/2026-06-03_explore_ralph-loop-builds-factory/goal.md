---
task_id: TASK-PROC-066-02
type: explore
parent_requirement: REQ-PROC-066
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 5
impact_reason: I5-ENAB
status: pending
effort: L
created: 2026-06-03
expected_tool_calls: 35
skill_chain_depth: 2
synthesis_dependent: true
synthesis_justification: "Must hold the Ralph-loop discovery mechanism, the factory/project boundary, the target factory's persona model, and multi-bundle extendability simultaneously to judge whether loop-driven build-out is sound"
after: [TASK-PROC-065-06-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore how self-perpetuating Ralph-loop tasks can drive the build-out of the extracted Software Factory project: what the discovery agent reads against the factory's own artifacts (personas incl. a factory-provider persona, requirements, skills), how the loop bootstraps and terminates, and how this feeds the extraction plan."
release_description: ""
opus_recommended: true   # reason: cross-cutting design exploration — couples the Ralph-loop discovery mechanism, the factory/project boundary, a new persona model, and multi-bundle extendability; trade-offs must be reasoned about together
writes_requirements: true
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Explore Using Ralph-Loop Tasks to Build the Software Factory

## Objective

We do not yet know:
- Whether the self-perpetuating "Ralph Loop" (a task whose last step spawns an Opus agent to discover the next piece of work and create the follow-up task — see TASK-PROC-065-06-01) is a viable engine for *building out the extracted Software Factory project itself*, as opposed to building a product app.
- What the discovery agent would read when the "project" under construction **is** the factory: the factory's own personas, its own requirements, its own skill/agent/script inventory, coverage gaps in its own process requirements.
- How the loop **bootstraps** — what the very first seed task and loop-context file look like when starting a fresh factory repository that is still mostly empty.
- How the loop **terminates gracefully** when the factory is "complete enough" — and what "complete enough" even means for a factory that is meant to keep growing.
- How the factory's intended **persona model** (see the seed below: solo-developer / Flutter-user / Claude-Code-user, plus a *software-factory-provider* persona) shapes what the discovery agent treats as "remaining work."
- How the requirement that *all artifacts a consuming project needs must be present in the factory project* turns into discoverable, loop-creatable work items.

This exploration should surface answers and trade-offs, and produce a proposal specific enough that the downstream extraction exploration (TASK-PROC-066-01) can decide whether — and how — to use loop-driven build-out as part of the extraction plan.

## Background

The developer's vision is to extract the Software Factory into its own independently-versioned repository (the subject of TASK-PROC-066-01). Separately, the project is designing a self-perpetuating task-creation skill — the "Ralph Loop" — that, combined with the autonomous orchestrator (REQ-PROC-041), chains unattended work by discovering and creating the next task before completing (TASK-PROC-065-06-01).

This task explores the intersection: **once the Ralph-loop mechanism exists, can it be pointed at the factory project to autonomously grow the factory toward its target state?** It must not re-design the loop mechanism (that is TASK-PROC-065-06-01's job) — it consumes that design and asks how it applies when the work-product is the factory.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-06-03_00_user_initial_input.md`

Read it as a seed bed, not a spec. In particular, the persona questions it raises (one combined persona vs. three; how a software-factory-provider persona is expressed; how extendability and multi-bundle slimness work) are **open questions to explore, not decisions to ratify**.

Current requirements: ../requirements.md (none yet for this exploration-only area; REQ-PROC-066 is defined inline by its tasks)

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

Start from the predecessor's output: read what TASK-PROC-065-06-01 concluded about the loop's discovery signals, loop-context file, deduplication, and cascade-safety. Only then ask how each of those changes when the project being built is the factory.

## Seeds

1. **The bootstrap problem** — A freshly-extracted factory repo is nearly empty. A discovery agent reading "what remains" against an empty project sees almost nothing *or* everything. What is the first seed task? What does the initial loop-context file (end goal + termination condition) say when the end goal is "a complete, self-contained factory"? Is there a hand-authored backlog the loop consumes first before it switches to true discovery?

2. **What does "remaining work" mean for a factory?** — For a product app, the discovery agent reads requirement-coverage gaps, unblocked tasks, incomplete ACs. For the factory, the equivalents are the factory's *own* process requirements, its skill/agent inventory, the artifact-completeness rule (every artifact a consuming project needs must exist in the factory). What signals give the best signal-to-noise ratio here, and how do they differ from the product-app signals the predecessor task designed for?

3. **The personas as the loop's compass** — The seed proposes the factory's personas: a solo "maker" (broader than "developer" — also doing PM, UX/UI, etc.; persona focus = team size and available time), a Flutter user, a Claude-Code user, and a *software-factory-provider* persona (serve diverse personas; do no harm to people or planet; keep the factory slim across team sizes / technologies / LLM providers via bundles; let many contributors extend it; collapse contributed personas into a few). Could these personas function as the loop's compass — the discovery agent asking "which persona need is least served?" to choose the next task? What breaks if so?

4. **One combined persona vs. three (the extendability tension)** — The seed asks whether the three consumer personas should collapse into one. Explore the consequence for the loop and for extendability: if they are separate, the discovery agent can target gaps per-persona; if combined, targeting is coarser but the model is simpler. How does the factory-provider persona's "collapse added personas into a few" mechanism interact with a loop that might otherwise spawn persona-specific work indefinitely?

5. **Slimness under multiplication (bundles)** — The provider persona wants the factory to stay slim even while serving multiple team sizes, technologies, and LLM providers — possibly via bundles. If the Ralph loop is the thing adding capability over time, what keeps it from bloating the factory? Is there a discovery-time check ("does this work item belong in core or a bundle?") that the loop must apply? Does bundle-awareness belong in the loop-context file?

6. **Termination vs. perpetual growth** — A factory is arguably never "done." The predecessor's loop terminates "when no more work is found." For a factory meant to keep growing, what is a sane termination condition for a *single autonomous run* (vs. the factory's lifetime)? Time-box? Bundle-scope? A milestone in the loop-context end goal?

7. **Relationship to the extraction plan (the ordering)** — This task blocks TASK-PROC-066-01. What exactly should the extraction exploration receive from this one? A recommendation to use / not use loop-driven build-out? A bootstrap backlog? A persona model? Be explicit about the handoff so the downstream task is not left guessing.

8. **Prior art** — The release-orchestration chain (REQ-PROC-035 SEC-05, `scripts/tasks/create_orchestration_task.py`) is an existing plan-driven self-perpetuating loop. The Ralph loop is discovery-driven. Building a factory might want *both*: a plan-driven phase (consume a bootstrap backlog) then a discovery-driven phase. Is a hybrid the right shape for factory build-out?

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus, `opus_recommended: true`). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — prior art on self-bootstrapping toolchains, agent-driven repo scaffolding, "the system that builds itself" patterns — always delegate to a spawned `general-purpose` agent with a focused question framed as a question, never run WebSearch inline. The subagent returns a distilled summary; raw web content stays in its context.

## Output

A future implementer (and specifically the executor of TASK-PROC-066-01) reading this exploration should understand:

1. Whether loop-driven build-out of the factory is recommended, with rationale and the alternatives considered.
2. The bootstrap design: first seed task, initial loop-context file, and whether a hand-authored backlog precedes true discovery.
3. The discovery signals appropriate when the project being built is the factory itself.
4. How the factory's persona model (including the factory-provider persona) informs work discovery — and a framed, undecided answer to the one-vs-three-persona and bundle/slimness questions.
5. A sane single-run termination condition for a project that is intended to keep growing.
6. A clear statement of what is handed off to the extraction exploration (TASK-PROC-066-01).
7. The decisions that require user input, framed clearly enough to decide.

The output is honest about what remains uncertain and what was not investigated.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-065-06-01 | pending | Explores the Ralph-loop / perpetuating-task-creation skill. This task consumes its output (discovery signals, loop-context file, cascade-safety) and must wait for it. Hard predecessor (`after`). |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-065-06-01](../../../requirements_management/epic_task_lifecycle/feat_perpetuating_task_creation/tasks/2026-06-02_explore_perpetuating-task-creation-skill/goal.md) | Predecessor — defines the Ralph-loop mechanism this task applies to factory build-out; executor should read its synthesis first. |
| [TASK-PROC-066-01](../2026-05-28_explore_software-factory-extraction/goal.md) | Dependent — the software-factory extraction exploration is blocked by this task (`after: [TASK-PROC-066-02]`); this task's output feeds its extraction plan. |
