---
id: REQ-PROC-065-06
status: defined
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
effort: M
stakeholder: developer
created: 2026-06-02
after: [REQ-PROC-041-01]
blocks: []
market_research_refs: [] # No relevant findings — internal process tooling
personas_served: [PERSONA-004]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "A skill exists in `.claude/skills/` that wraps `task-create` internally and appends a Work Discovery section to every task `goal.md` it produces; the skill does not reimplement task metadata construction independently"
    - id: AC-02
      text: "Every task produced by this skill contains a Work Discovery section in `goal.md` that instructs the executing agent to spawn an Opus-model background agent before calling `task-complete`; the agent reads project state and identifies remaining work"
    - id: AC-03
      text: "When the work-discovery agent finds remaining work, it creates a follow-up task using the standard task-lifecycle skills (`task-create` or `task-create-code`); the follow-up task type (impl, explore, etc.) is chosen by the agent; no new task type is introduced"
    - id: AC-04
      text: "When the work-discovery agent finds no remaining work, it writes a documented no-op note to `plans_and_protocols/` and the original task completes without creating a follow-up task"
    - id: AC-05
      text: "The follow-up task produced by the work-discovery agent is itself a perpetuating task (created with this same skill), so the loop continues until the discovery agent finds no remaining work; the task type (impl, explore, etc.) is determined by the agent and uses only existing types — no new task type is introduced"
    - id: AC-06
      text: "The work-discovery agent preserves loop continuity when encountering equivalent existing work: (a) if an equivalent perpetuating task exists, it writes a no-op — the loop continues through that task; (b) if an equivalent non-perpetuating task exists with status: pending, it upgrades that task to perpetuating rather than creating a duplicate; (c) if an equivalent non-perpetuating task exists with status: in_progress, it creates a new perpetuating task sequenced after the in_progress task (`after: [that_task_id]`); the loop is never silently terminated by a deduplication check"
    - id: AC-07
      text: "The skill and its work-discovery step behave correctly under `CLAUDE_AUTOMATED_MODE=1`: the agent follows all automated-mode rules and the created follow-up task enters the normal task queue without bypassing existing gates"
    - id: AC-08
      text: "The skill creates a loop context file alongside the first task workspace; the file contains: (a) the end goal — a human-readable statement of what the loop is working toward; (b) a measurable termination condition — an objective, verifiable test for when no remaining work exists within the loop's domain; (c) the origin task ID; the skill prompts the user for (a) and (b) and does not proceed without both"
    - id: AC-09
      text: "Every task in the chain — the first task and every follow-up created by the discovery agent — carries a `ralph_loop_context` YAML field in `goal.md` pointing to the loop context file; the discovery agent reads this file before scanning for work on each iteration"
    - id: AC-10
      text: "The discovery agent evaluates the termination condition from the loop context file before creating any follow-up task; if the condition is met, it writes a no-op noting the condition as the reason and the loop ends gracefully"
    - id: AC-11
      text: "The goal.md of every task in the chain contains an explicit scope statement specific enough for the discovery agent to determine with certainty whether any candidate piece of work falls within the current task's domain; the skill prompts the user for this scope at creation time and does not proceed without it"
    - id: AC-12
      text: "Every task in the chain is fully self-contained: a cold agent with no prior session history can orient itself completely by reading only the task's `goal.md` and the loop context file, without reading any prior task in the chain"
---

# Perpetuating Task Creation Skill

## Overview

A skill that wraps `task-create` and embeds a Work Discovery section in every task workspace it produces. When the task is executed and the main work is done, the agent spawns an Opus-model sub-agent that scans project state for remaining work — creating the next task if found, documenting a no-op if not. Combined with the autonomous session orchestrator (REQ-PROC-041), this creates a self-perpetuating automation loop.

## Purpose

The autonomous task orchestrator (REQ-PROC-041) runs tasks sequentially. Without a mechanism to automatically queue the next unit of work, the developer must manually identify and create follow-up tasks after each automated session. This skill closes that gap: by embedding work-discovery into the task's own goal, the automation loop becomes self-sustaining.

The Opus model is specified for the discovery agent because identifying the right next task requires synthesizing signals across requirements coverage, task status, blocked items, and open gaps — maximum reasoning power justifies the model cost relative to the automation value.

Initiated by developer request on 2026-06-02 (see `tasks/2026-06-02_explore_perpetuating-task-creation-skill/`).

## Behavior

When invoked, the skill prompts the user for two required inputs — the **end goal** (what the loop is working toward) and a **measurable termination condition** (the objective test for when no remaining work exists within the loop's domain). It will not proceed without both. It then creates two artifacts: the task workspace (via `task-create`) and a **loop context file** stored alongside it containing the end goal, termination condition, and origin task ID.

Every task in the chain carries a `ralph_loop_context` YAML field pointing to this file. When the executing agent completes its main work and reaches the **Work Discovery** section in `goal.md`, it spawns an Opus-model background agent that:
1. Reads the loop context file
2. Evaluates the termination condition — if met, writes a no-op and the loop ends gracefully
3. If not met: scans project state (requirements coverage, task queue, blocked items, open gaps) within the loop's domain
4. Applies deduplication logic (AC-06) to avoid redundant tasks
5. Creates the next perpetuating task, inheriting the `ralph_loop_context` reference

The follow-up task type (impl, explore, etc.) is determined by the agent using existing types — no new type is introduced. The chain is linear: exactly one follow-up per discovery run, never branching.

## Developer Guidelines

### Key Decisions

- The skill wraps `task-create` — it does not reimplement goal.md construction. The internal delegation is non-negotiable (Cross-Feature Invariant 4 of REQ-PROC-065).
- Opus model for the discovery agent is a hard constraint (developer-specified). Cost is accepted as justified by the automation value.
- The loop context file is the single source of truth for the loop's end goal and termination condition — it must be created at loop start and referenced by every task in the chain. Without it, cold sessions have no way to determine scope or stopping criterion.
- Follow-up tasks ARE perpetuating — the loop continues until the termination condition is met. The chain is linear (one follow-up per task), never branching.
- Each task in the chain must be self-contained: a cold agent reading only `goal.md` + the loop context file must be able to fully orient itself.

### Common Pitfalls

- A discovery agent that creates more than one follow-up task per run causes branching cascade — exactly one follow-up task (or a no-op) is the correct outcome per discovery run.
- Omitting the `ralph_loop_context` field from a follow-up task severs the chain — the next discovery agent has no context file to read and cannot evaluate the termination condition.
- Skipping the duplicate check in an automated loop rapidly fills the queue with redundant tasks that block genuine work.
- Running the discovery agent in the foreground (blocking) keeps the session alive past the 5-minute cache TTL unnecessarily — spawn it as a background agent per CLAUDE.md §2.

## Related Requirements

- REQ-PROC-065: Task Lifecycle (parent epic)
- REQ-PROC-041: Autonomous Task Execution — the infrastructure this feature extends; `feat_perpetuating_task_creation` completes the loop the session orchestrator runs
- REQ-PROC-041-01: Session Orchestrator — the "Do next task" session that picks up tasks created by this skill
- REQ-PROC-058: Implementation Task Planning — `task-derive-from-requ` is a parallel creation path; this skill is orthogonal to it

## References

- Base skill: `.claude/skills/task-create/SKILL.md`
- Exploration task: `tasks/2026-06-02_explore_perpetuating-task-creation-skill/goal.md`
