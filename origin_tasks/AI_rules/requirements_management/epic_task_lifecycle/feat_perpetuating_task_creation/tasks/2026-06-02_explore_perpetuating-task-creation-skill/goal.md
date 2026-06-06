---
task_id: TASK-PROC-065-06-01
type: explore
parent_requirement: REQ-PROC-065-06
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-06-02
expected_tool_calls: 30
skill_chain_depth: 2
synthesis_dependent: true
synthesis_justification: "Design must hold task-create internals, automated-mode rules, duplicate-prevention, Opus-agent budget, and cascade-safety simultaneously"
after: [TASK-PROC-004-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
writes_requirements: true
opus_recommended: true   # reason: explicit design task — evaluate approaches, architectural trade-offs across task-create internals, automation loop, and cascade-safety invariants
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Explore Implementation of the Perpetuating Task Creation Skill

## Objective

How should the "Ralph Loop" skill be designed and implemented? The core question is how a wrapper around `task-create` can embed a durable work-discovery step in `goal.md` such that: the executing Opus agent reliably runs it before completing, the discovery is meaningful (finds real remaining work, not noise), duplicates are prevented, and the automation loop remains safe and bounded.

## Background

The developer described a self-perpetuating automation pattern: when a task created with this skill completes, it first spawns an Opus agent to scan remaining project work and create the next task — then finishes. Combined with the autonomous session orchestrator (REQ-PROC-041), this enables unattended work chaining without manual task queuing.

The skill must be a wrapper (not a reimplementation) around `task-create`. No new task type is introduced. The follow-up task can be impl, explore, or any existing type — determined by what the agent finds.

The user's unedited initial thinking is preserved in:
`plans_and_protocols/2026-06-02_00_user_initial_input.md`

Read it as a seed bed, not a spec.

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **What does the discovery agent read?** — Which project signals (requirements coverage gaps, unblocked tasks, incomplete ACs, orphaned implementations, blocked items) give the Opus agent the best signal-to-noise ratio for "what remains"? What is the minimal set that avoids flooding the agent with irrelevant context?

2. **Loop context file design** — The skill must create a loop context file (end goal + termination condition + origin task ID) that every task in the chain references via `ralph_loop_context` in YAML frontmatter. Where should this file live? What format? How does the skill ensure the field is faithfully propagated to every follow-up task the discovery agent creates?

3. **Deduplication with loop preservation** — The queue may already contain tasks covering the same gap. A simple no-op would kill the loop. The required behavior: (a) perpetuating duplicate → no-op; (b) standard duplicate, pending → upgrade it to perpetuating; (c) standard duplicate, in_progress → create a sequenced perpetuating follow-up with `after: [that_task_id]`. What's the most practical way to implement the "upgrade" path — what does injecting a Work Discovery section into an existing goal.md look like?

4. **Cascade safety** — Follow-up tasks are themselves perpetuating (the loop is intentionally self-continuing). The safety invariant is linearity: exactly one follow-up per discovery run, never branching. What mechanism enforces this? How does the loop terminate gracefully when no more work is found?

5. **Automated-mode interaction** — The discovery agent spawns inside a session already running under `CLAUDE_AUTOMATED_MODE=1`. Does this violate any budget or account-rotation constraints? Are any additional guardrails needed for the automated context?

6. **Prior art: the release orchestration chain (REQ-PROC-035 SEC-05)** — The project ALREADY runs a working self-perpetuating task-creating loop: `scripts/tasks/create_orchestration_task.py` creates exactly one impl task per `/autorun` session and perpetuates itself via **two-slot alternation** (it overwrites the terminal predecessor's folder slot — at most two orchestration folders are ever live). This is *plan-driven* perpetuation (from a predefined `task_creation_plan.md`), whereas the Ralph Loop is *discovery-driven*. They are two members of one family. What can this design borrow (folder-slot reuse, the after-chain that blocks premature execution, the "one task per session" bound)? Should the two converge on a shared primitive, or stay deliberately separate (plan- vs. discovery-driven)? At minimum, do not design a mechanism that conflicts with the one already in production. Cross-cutting: the sibling effort TASK-PROC-065-01-01 (standing-task support in task-create) is surveying the SAME three recurring mechanisms — coordinate the boundary statements so the epic tells one coherent story.

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — best practices, prior art — always delegate to a spawned `general-purpose` agent with a focused question; never run WebSearch inline.

## Output

A self-contained design proposal covering: skill name and invocation convention, the exact text of the Work Discovery section to embed in `goal.md`, the signals the discovery agent reads, the duplicate-prevention check, the cascade-safety invariant, and any automated-mode constraints. Open decisions requiring user input must be framed clearly enough for the user to decide. An implementer should be able to build the skill from this proposal without re-deriving the design reasoning.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-004-02 | pending | Explores/implements the structured ideation workflow (skill vs. agent vs. protocol). Runs before this task chain so the Ralph-loop and downstream explorations benefit from the ideation mechanism. Hard predecessor (`after`). |
