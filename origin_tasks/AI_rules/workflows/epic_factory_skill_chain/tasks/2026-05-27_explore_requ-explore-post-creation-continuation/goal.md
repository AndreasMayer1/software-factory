---
task_id: TASK-PROC-063-02
type: explore
parent_requirement: REQ-PROC-063
urgency: 3
urgency_reason: U3-FIX
impact: 4
impact_reason: I4-PAIN
status: pending
effort: S
created: 2026-05-27
after: [TASK-PROC-063-01, TASK-PROC-045-08]
awaiting: ["process-AI-rules-restructure"]
awaiting_note: "Parked. TASK-PROC-063-01 discovered REQ-PROC-063 placement is blocked by REQ-PROC-045's process/ carve-out. TASK-PROC-045-08 will modify REQ-PROC-045 to remove the carve-out and define stricter epic-content rules. After that, follow-up impl tasks must restructure process/AI_rules/ before REQ-PROC-063 (and therefore this task) can be cleanly placed. Unblock once those restructure tasks complete and REQ-PROC-063's home folder exists."
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore what requ-explore should do after creating a requirement — heuristic vs. prompt, session-reuse tradeoffs, and skill chain continuation"
release_description: ""
opus_recommended: true   # reason: cross-cutting trade-off analysis (session cost, skill chaining, heuristic design)
writes_requirements: true
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Explore Post-Creation Continuation in requ-explore

## Objective

`requ-explore` currently ends after writing a requirement and completing its quality gate, leaving the factory chain broken. The next step — whether to call `task-derive-from-requ`, create a single impl/explore task, or do nothing — is never triggered. This exploration should define the decision logic, determine how to minimize unnecessary developer prompts, and clarify when the current (context-rich but expensive) session should do the work vs. when a fresh session is better.

The outcome feeds REQ-PROC-063 (epic_factory_skill_chain) as one of the chain-break cases that the epic must cover, and produces concrete design decisions for the `requ-explore` skill.

## Background

`requ-explore` currently ends with `task-complete`. No follow-up is triggered. This breaks the factory chain: the developer must manually identify and invoke the next step.

This task is blocked on TASK-PROC-063-01, which defines the epic structure and establishes where this output belongs within REQ-PROC-063 (or a sub-requirement).

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-27_00_user_initial_input.md`

Read it as a seed bed, not a spec.

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **What signals does the freshly-created requirement already carry?** Effort size, presence of trackable_items/ACs, requirement type (feature vs. epic vs. process), whether `task-derive-from-requ` would be valid — can these drive an automatic decision tree without asking the developer?

2. **When is asking the right answer?** The goal is *minimum necessary* prompts, not zero prompts. Are there ambiguous cases where a single well-framed question is better than a wrong automatic choice? What is the cost of a wrong automatic choice?

3. **Session context as a first-class resource.** The session that just created the requirement holds reasoning, tradeoffs, and intent that aren't captured in any file. When is it worth spending token budget to act on that context immediately, and when does the cost outweigh the benefit? Is there a lightweight way to capture that context into `plans_and_protocols/` so a fresh session can start near-warm?

4. **What are the distinct post-creation exit paths?** Map them: single-AC requirement → direct impl task; multi-AC requirement → task-derive-from-requ; epic/placeholder → define task or nothing; explore-that-produced-a-requirement → the new requirement's own explore continuation; already has tasks. Verify against real examples from the task archive.

5. **How do related skills handle this?** Look at `task-create`'s redirect logic (AC-10), `requ-derive-from-flow`'s continuation, and `release-begin-impl`'s phase handoff for patterns to reuse or adapt.

6. **What should the implementing skill change look like?** Draft the new exit-phase logic for `requ-explore` and, if applicable, the sub-requirement text within REQ-PROC-063 that governs it.

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities, what others have tried — use web search. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Raw web content inflates the gathering agent's context window fast with irrelevant results; the subagent returns only a distilled summary while the raw content stays in its own context.

Frame search queries as questions rather than keyword bags — this produces more useful results (e.g. *"how do LLM-driven workflow tools handle chaining decisions without over-prompting?"* rather than *"LLM workflow chaining"*). When a snippet is insufficient, instruct the subagent to use WebFetch to read the full page before summarising.

## Output

A synthesis that a future implementer (modifying the `requ-explore` skill and contributing to REQ-PROC-063) can act on directly:
- A clear decision tree or rule set for the post-creation exit path
- A recommendation on when to ask vs. act automatically
- A recommendation on session-reuse vs. fresh-session, with any lightweight context-capture mechanism needed to bridge the gap
- Draft skill logic or requirement text for the REQ-PROC-063 sub-requirement that governs this behavior
- An explicit list of edge cases and how to handle them

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-063-01 | completed | Exploration completed 2026-05-28; deferred REQ-PROC-063 and surfaced the carve-out blocker. See `(completed)/plans_and_protocols/2026-05-28_01_synthesis.md`. |
| TASK-PROC-045-08 | pending | Modifies REQ-PROC-045 to remove the process/ carve-out and define stricter epic-content rules. Real prerequisite for this task. |
| process/AI_rules restructure | not yet created | Downstream impl tasks under updated REQ-PROC-045 that physically restructure process/AI_rules/ into the new shape. REQ-PROC-063 can only be placed cleanly after these complete; this task can only run after REQ-PROC-063 exists. |
