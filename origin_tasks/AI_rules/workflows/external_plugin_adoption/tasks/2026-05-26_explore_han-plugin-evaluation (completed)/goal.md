---
task_id: TASK-PROC-055-01
type: explore
parent_requirement: REQ-PROC-055
urgency: 2
urgency_reason: U2-OPP
impact: 4
impact_reason: I4-ENAB
status: completed
effort: L
created: 2026-05-26
started: 2026-05-26
completed: 2026-05-26
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Evaluate the han Claude Code plugin (testdouble/han, MIT) to determine if and how it should be adopted into our factory"
release_description: ""
opus_recommended: true   # reason: cross-cutting explore — spans all factory layers (skills, agents, workflows, hooks); explicit trade-off and compare-approaches task
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Evaluate the han Claude Code Plugin for Factory Adoption

## Objective

We do not yet know whether the patterns, agents, and skills in the han Claude Code plugin (https://github.com/testdouble/han) can improve our factory — or at what cost. This exploration should produce an honest, decision-ready report that defines the problem space: what han offers, what we already have, where the overlap and gaps are, and what adoption at different levels would actually cost and risk.

The exploration must define the right *process* for reaching that answer, not just the answer itself.

## Background

Han is a Claude Code plugin by Test Double (MIT license) with 20 skills and 22 specialist agents. Its philosophy centers on evidence-first planning, YAGNI discipline, adversarial review, and sized agent rosters. We currently have ~60 skills and 6 agents organized around a factory orchestration model with established workflows, quality gates, and task lifecycle management.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-26_00_user_initial_input.md`

Read it as a seed bed, not a spec.

There is no parent requirements.md yet — this explore task will define it.

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

**Start by defining the comparison framework before doing the comparison.** The methodology itself is part of the deliverable — an ad-hoc comparison risks missing entire categories.

## Seeds

These are lenses to look through, not a to-do list. Some may lead nowhere; others may open new threads.

1. **What categories of value does han claim to add?** Planning rigor, review depth, agent specialization, YAGNI discipline — are these gaps we actually feel in our factory, or do we already address them differently?

2. **How compatible are the philosophies?** Han is stateless, YAGNI-first, adversarial-by-default. Our factory is stateful (protocol.md, task lifecycle), quality-gate-enforced, and factory-orchestrated. Where do these worldviews conflict, and where do they complement?

3. **Which han components are self-contained enough to adopt selectively?** Han's agents (22 specialist roles) vs. our agents (6 broad roles): could we add specific han agents (adversarial-validator, edge-case-explorer, concurrency-analyst) without adopting the whole system?

4. **What is the realistic migration/integration cost?** Our skills encode project-specific knowledge (quality gates, task lifecycle, Flutter/Dart conventions). Han skills are project-agnostic. How much effort to adapt, and what would break?

5. **What does MIT attribution actually require, and does it create any friction?** If we copy or adapt han's content, what attribution is legally and practically needed inside .claude/ files?

6. **What adoption levels are coherent?** Full (replace our skills/agents with han equivalents), selective (cherry-pick specific agents or patterns), inspirational (no direct copying, just inform rewrites). What does each level cost and risk?

7. **How should the report be structured to be decision-ready?** The report format is itself a design question — what sections, what level of detail, what evidence would the user need to make a confident adopt/adapt/skip decision for each component?

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch. `opus_recommended: true` — run with Opus.

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities, what others have tried — use web search. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Raw web content inflates the gathering agent's context window fast with irrelevant results; the subagent returns only a distilled summary while the raw content stays in its own context.

Frame search queries as questions rather than keyword bags — this produces more useful results (e.g. *"what patterns from han Claude Code plugin are most commonly adopted?"* rather than *"han claude code plugin adoption"*). When a snippet is insufficient, instruct the subagent to use WebFetch to read the full page before summarising.

**han source files** (fetch directly via WebFetch or gh CLI):
- Skills: `https://raw.githubusercontent.com/testdouble/han/main/plugin/skills/[name]/SKILL.md`
- Agents: `https://raw.githubusercontent.com/testdouble/han/main/plugin/agents/[name].md`
- Docs: `https://raw.githubusercontent.com/testdouble/han/main/docs/[name].md`

**Our factory source**: `.claude/skills/`, `.claude/agents/`, `.claude/factory_flows.md`, `CLAUDE.md`

## Output

A decision-ready report (written to `plans_and_protocols/`) that a future implementer could use to act without re-reading all the source material. It should:

- Define a reusable comparison framework (so future plugin evaluations can reuse the methodology)
- Provide a component-by-component map: han item → our equivalent (or gap)
- Give honest effort/risk estimates for each adoption level (full, selective, inspirational, none)
- Make a concrete recommendation with the key trade-offs stated clearly
- Identify any han items that are straightforward low-risk wins
- Flag anything that would require re-testing existing workflows

The report should be honest about uncertainty — "we don't know until we try" is a valid finding if justified.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
