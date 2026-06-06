---
task_id: TASK-PROC-006-02
type: explore
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-05-27
session_completed_at: 2026-05-27T20:59:44Z
effort: XL
created: 2026-05-01
session_id: 08e0c996-7fdf-4b10-abbe-15896c158562
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-02]
scope_description: "Open-ended design thinking exploration for a complete redesign of the claude-optimize skill — no predetermined answer, iterative discovery of what optimization means and how it should work in this factory"
release_description: ""
opus_recommended: true   # reason: cross-cutting design space; requires synthesis across personas, factory mechanics, LLM system design, and strategic trade-offs; urgency 4 + impact 5
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: fadfd042
  file: ../requirements.md
---

# Goal: Explore the Problem Space for a Redesigned claude-optimize Skill

## Objective

The `claude-optimize` skill exists today as a stub. The right way to redesign it is not known yet. This task is about discovering the problem before proposing a solution.

Do not treat the notes below as a specification or a checklist. They are seeds — places where curiosity might begin. The exploration itself should surface what actually matters. Some seeds will lead nowhere. Others will open doors to questions that were not anticipated. Both outcomes are valuable.

The expected output is not a filled-in template. It is a living synthesis of whatever the exploration uncovers — insights, contradictions, open questions, promising directions, and decisions that need to be made before any implementation can begin.

## Background

REQ-PROC-006 describes a system for automatically identifying workflow improvement areas and updating workflows accordingly. The current skill is considered "implemented" but does almost nothing meaningful. Before redesigning it, we need to understand the problem properly.

The user's unedited initial thinking that prompted this task — hunches, directions, and questions in raw form — is preserved in:
`plans_and_protocols/2026-05-01_00_user_initial_input.md`

Read it as a seed bed, not a spec. It contains things worth following up on and things that may turn out not to matter.

For context on the requirement at task creation time:
```
git show fadfd042:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — not as rigid phases but as a mindset:

**Empathize before defining.** Understand the system and the people in it before forming hypotheses. Read what exists. Observe patterns. Ask "what is actually happening?" before asking "what should happen?"

**Diverge before converging.** Generate many possible directions before evaluating any of them. The goal during exploration is breadth, not correctness.

**Let questions lead.** Every answer should produce more questions. If exploration feels like it is converging too early, go wider.

**Iterate.** A single pass through the material will not be enough. Findings from one area will change how another area looks. Come back to earlier material with new context.

**Surface surprises.** The most valuable discoveries are the ones that were not anticipated. If something unexpected comes up — a constraint, a contradiction, a data source that wasn't known about — that is important.

## Seeds for Exploration

These are not tasks to complete. They are entry points. Follow the ones that seem most generative. Abandon the ones that lead nowhere. Add new ones as they emerge.

**What does the system already know about itself?**
The factory produces a trail of artifacts as it works. What exactly is in that trail? Committed files are one part — but what about session logs, the CCS folder, local storage that never gets committed? What data exists that could serve as signal for an improvement system? What does the system *not* know about itself that would be useful to know?

**What is "better"?**
Better for whom? Better on what timescale? Better according to what evidence? Start from personas (who is this factory for, what do they actually need?) and requirements (what is the factory supposed to do?), then reason outward. Do not start from the skill itself.

**What does an improvement system need to be trustworthy?**
How would you know that an improvement the skill made actually helped? How would you know it made things worse? Without an answer to this, any change the skill makes is essentially a guess. What would a feedback loop look like here?

**What is the skill's relationship with time?**
Optimization implies a "before" and "after." What window of history is relevant? How does the skill look back without being overwhelmed? How does it know whether something it noticed last time has already been acted on?

**Who is in the loop, and when?**
The skill could propose changes and wait for approval. It could apply changes directly. It could do research and produce a report. It could do nothing and schedule a future check. Each of these implies a different architecture. What factors should determine which mode is appropriate for a given situation?

**What is the difference between broken and suboptimal?**
Sometimes a skill does something clearly wrong. Sometimes it just does something that could be done better. These might need very different responses. Can the system tell them apart? Should it treat them differently?

**What is the skill's relationship with other skills?**
The skill does not exist in isolation. It modifies skills that are used by other workflows. Changes ripple. How does the skill reason about this? Are there changes it should refuse to make without broader analysis?

**What can be learned from outside this project?**
Self-improving systems, prompt optimization, software factory patterns, LLM workflow design — practitioners share experiences publicly. What has been tried? What failed? What worked under what conditions?

**What constraints exist that are not obvious?**
Permissions. Context window limits. Token cost. The structure of the task graph. The way `next_tasks.py` surfaces work. Things that seem simple may turn out to be surprisingly constrained. Discover the constraints before designing around assumptions.

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities, what others have tried — use web search. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Raw web content inflates the gathering agent's context window fast with irrelevant results; the subagent returns only a distilled summary while the raw content stays in its own context.

Frame search queries as questions rather than keyword bags — this produces more useful results (e.g. *"how do self-improving LLM systems detect diminishing returns?"* rather than *"LLM self-improvement diminishing returns"*). When a snippet is insufficient, instruct the subagent to use WebFetch to read the full page before summarising.

## Output

Whatever the exploration uncovers. At minimum, the synthesis document(s) in `plans_and_protocols/` should give a future implementer enough to understand:

- What the problem actually is (which may be different from how it was initially framed)
- What directions seem promising and why
- What was ruled out and why
- What decisions still need to be made by the user before implementation can begin
- What REQ-PROC-006 should say if it were written today

## Acceptance Criteria

- [x] Exploration produced at least one Opus synthesis round (four rounds: 2026-05-07_01, _03, 2026-05-16_05, _08)
- [x] The synthesis defines the problem space in terms that were not fully known at task creation (task-producer reframe; monitor/event architecture; `.factory/optimize/` state; self-improvement guardrails)
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide (D1–D11, R1–R6, N-D-1–N-D-10 — all answered by the user)
- [x] The output is honest about what remains uncertain (round-3 §6 U-1–U-7; round-4 Part 9)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
