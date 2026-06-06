---
task_id: TASK-PROC-063-01
type: explore
parent_requirement: REQ-PROC-063
urgency: 3
urgency_reason: U3-FIX
impact: 4
impact_reason: I4-PAIN
status: completed
effort: S
created: 2026-05-27
started: 2026-05-28
completed: 2026-05-28
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore and define REQ-PROC-063: an epic requirement that formalizes the goal of a seamlessly chained, end-to-end factory skill workflow"
release_description: ""
opus_recommended: true   # reason: architectural judgment needed — epic scoping, overlap resolution, sub-requirement boundaries
writes_requirements: false   # exploration discovered the right move is to MODIFY REQ-PROC-045 first; REQ-PROC-063 deferred. See plans_and_protocols/2026-05-28_01_synthesis.md.
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Define the Factory Skill Chain Epic (REQ-PROC-063)

## Objective

`.claude/factory_flows.md` describes the complete AI Software Factory information flow in a diagram and prose, but there is no formal requirement behind it. This means there is no AC list to track whether the workflow is actually behaving correctly, no mechanism to file improvement tasks against it, and no structured place to reference from individual skill requirements that implement pieces of it.

This exploration defines REQ-PROC-063: an epic (or high-level requirement) that formalizes the goal of a seamlessly chained factory skill workflow — from the moment a user inputs information to the moment code is committed. The output is the `requirements.md` for this requirement, plus a decision on how it relates to existing per-skill requirements.

## Background

Today's `factory_flows.md` is the only artifact covering the end-to-end picture. It is:
- Not formally tracked (no requirement, no ACs, no task coverage)
- Descriptive, not normative — it describes what *is*, not what *must be*
- Not referenced by any individual skill requirement
- Occasionally stale (the file header warns "this document might not be 100% accurate")

Individual skills (requ-explore, task-create, task-derive-from-requ, release-begin-impl, …) have their own requirements, but there is no umbrella that ties them into a quality contract for the chain as a whole. Broken-chain bugs — like requ-explore ending without triggering a follow-up step — cannot be tracked or filed against anything.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-27_00_user_initial_input.md`

Read it as a seed bed, not a spec.

Current requirements location (to be created): ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **Epic vs. flat requirement?** A flat requirement with a handful of ACs covering end-to-end chain integrity may be cleaner than an epic with sub-features. An epic is justified if sub-requirements are already candidates (e.g. per-skill chain contracts). Survey the existing skill requirements and decide which structure fits better.

2. **What are the chain breaks that already exist?** Map known gaps: requ-explore ending silently, task-create not triggering follow-up, release-begin-impl handoff ambiguities. Each is a candidate AC for REQ-PROC-063 (or a pointer to a sub-requirement).

3. **How should REQ-PROC-063 reference individual skill requirements?** Should it use `blocks:` / `after:` fields? Should individual skill requirements add `part_of: REQ-PROC-063`? Or just prose references? Define the convention.

4. **What is `factory_flows.md`'s future role?** Should it stay as a diagram/overview, become a generated artifact, or be deprecated once REQ-PROC-063 and its sub-requirements exist? Is it "source of truth" or "illustration"?

5. **What does "perfect workflow" mean normatively?** Translate the informal goal into verifiable ACs. Each AC should describe an observable, testable end state of the factory (e.g. "after requ-explore creates a requirement, the skill chain continues without requiring developer intervention beyond a single confirmation prompt" — or stronger).

6. **Where do sub-tasks belong?** TASK-PROC-063-02 (requ-explore post-creation continuation) already exists as a concrete improvement task. How should the epic structure accommodate it? Define the sub-requirement boundary.

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities, what others have tried — use web search. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Raw web content inflates the gathering agent's context window fast with irrelevant results; the subagent returns only a distilled summary while the raw content stays in its own context.

Frame search queries as questions rather than keyword bags (e.g. *"how do LLM workflow orchestration systems define and track end-to-end chain quality?"*). When a snippet is insufficient, instruct the subagent to use WebFetch to read the full page before summarising.

## Output

A written `requirements.md` for REQ-PROC-063 at the proposed path, containing:
- Clear scope (epic vs. flat, what it covers, what it delegates to sub-requirements)
- Normative ACs describing observable end states of the factory workflow chain
- A decision on how sub-skill requirements are referenced
- A note on `factory_flows.md`'s ongoing role

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
