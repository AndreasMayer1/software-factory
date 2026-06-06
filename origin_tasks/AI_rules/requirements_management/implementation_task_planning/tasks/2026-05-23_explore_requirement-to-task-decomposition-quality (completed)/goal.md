---
task_id: TASK-PROC-058-01
type: explore
parent_requirement: REQ-PROC-058
urgency: 3
urgency_reason: U3-PROCESS
impact: 5
impact_reason: I5-TRUST
status: completed
started: 2026-05-23
completed: 2026-05-24
effort: L
created: 2026-05-23
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore and design a skill/process for quality-assured decomposition of requirements into implementation tasks — ensuring full AC coverage, verification tasks, and integration with existing workflows."
release_description: ""
opus_recommended: true   # reason: cross-cutting explore spanning multiple skills, workflows, and architectural layers; requires trade-off judgment on skill boundaries
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
---

# Goal: Requirement-to-Task Decomposition Quality

## Objective

When a requirement exists and implementation tasks are created from it, the current process has no quality gate ensuring that (a) every AC is covered by at least one task, (b) a verification/testing task exists to confirm the requirement was actually implemented, and (c) the decomposition strategy is sound (correct ordering, right granularity, cross-requirement interactions considered). This exploration should define what "quality-assured task decomposition" means and design a skill or process extension that enforces it.

The triggering incident: REQ-PROC-046 had 13 ACs and 14+ tasks were created, yet AC-03 and AC-06 had zero task coverage, the ~160 pre-existing violations from newly created gate scripts were never addressed, and no verification task existed. The requirement was treated as "mostly done" while structural gaps remained invisible.

## Background

Today's task creation landscape:
- **`task-create`**: Generic skill for any task type (explore, impl, bugfix, etc.). Handles folder creation, ID allocation, metadata. Does NOT analyze requirement coverage or plan decomposition.
- **`task-create-code`**: Specialized for Dart code tasks (`lib/`, `test/`, `integration_test/`). Bridges functional requirements to implementation. Does NOT handle process/doc/script tasks.
- **`requ-derive-from-flow`**: Derives requirement gaps from user flows, then creates goal.md files. Works top-down from user needs, not from existing requirements.
- **`requ-explore`**: Creates/modifies requirements. Does NOT create implementation tasks.
- **`product-intake`**: Routes new info through the product structure (persona → scenario → flow → requirement). Upstream of task creation.

The gap: after a requirement is written (by `requ-explore` or manually), and before tasks are created, there is no structured process that:
1. Analyzes the requirement holistically (all ACs, all sections, interactions with other requirements)
2. Creates an implementation plan (what to build, in what order, what depends on what)
3. Ensures complete coverage (every AC has at least one task)
4. Includes verification (how do we know the requirement is actually met?)
5. Considers the existing codebase and infrastructure

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-23_00_user_initial_input.md`

Read it as a seed bed, not a spec.

Current requirements: ../../requirements.md (does not exist yet — this explore task will write it)

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **Workflow inventory**: What are all the paths that lead to "I need implementation tasks for this requirement"? At minimum: (a) freshly written requirement via requ-explore, same session continues to task creation; (b) existing requirement with discovered gap, ad-hoc task creation; (c) dedicated explore task whose goal is to create implementation tasks for an existing requirement (like TASK-PROC-046-01 did for REQ-PROC-046); (d) product-intake flow landing on a requirement that needs decomposition; (e) release planning identifying unimplemented requirements. What others exist? Which are most common? Which are most error-prone?

2. **Skill boundary question**: Should this be a new standalone skill (`task-plan-from-requirement`?) or an extension of `task-create`? `task-create` is already complex and handles many concerns. But adding decomposition logic to it risks bloating a skill that also handles simple one-off task creation. Conversely, a new skill means another entry point users must know about. What's the right boundary? Consider: `task-create-code` already split off for Dart-specific concerns — is the same pattern right here?

3. **Information gathering before decomposition**: What information is needed to create a good task plan? The requirement text alone is insufficient — you also need: related requirements that interact, existing code/scripts that will be touched, existing tasks (to avoid duplication), infrastructure constraints. How deep should this gathering go? What's the minimum viable information set vs. analysis paralysis?

4. **The plan-vs-task granularity tension**: The plan must be detailed enough to ensure coverage but not so detailed that it duplicates the work the tasks will do. A spike/explore task is valid when uncertainty is high. How do we decide when to plan in detail vs. when to create a spike? What signals indicate the right granularity? Consider: REQ-PROC-046 created 14 tasks but missed coverage — was the granularity wrong, or was the coverage check missing?

5. **Verification as a first-class concern**: Every requirement decomposition should include at least one verification task (or verification step in the final task). What does verification look like for different requirement types? Code requirements: tests + gate checks. Process requirements: audit tasks. Documentation requirements: review tasks. How do we ensure verification is not forgotten? Is it a mandatory field in the decomposition output?

6. **Coverage matrix**: At decomposition time, produce a coverage matrix showing AC → task mapping. Any AC without a task is a hard error. Any AC with only one task and no verification path is a warning. This is similar to what `scripts/requirements/coverage_report.py` does after the fact — but the check should happen *at decomposition time*, not after tasks are already created and half-completed.

7. **Interaction with existing skills**: How does this relate to `requ-derive-from-flow` (which creates requirement-update goal.md files from flow analysis)? To `release-begin-impl` (which creates orchestration tasks for a release)? To the automation orchestrator (which picks and executes tasks)? The new skill must fit cleanly into these existing flows without creating parallel paths or contradictions.

8. **The REQ-PROC-046 post-mortem as a test case**: Use the actual incident as a concrete test case. What would the skill have caught? What would it have produced differently? Walk through the incident step by step and validate the proposed design against it.

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise).

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities, what others have tried — use web search. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Raw web content inflates the gathering agent's context window fast with irrelevant results; the subagent returns only a distilled summary while the raw content stays in its own context.

Frame search queries as questions rather than keyword bags — this produces more useful results.

## Output

A future implementer should understand:
- What the skill does and when it's invoked
- How it fits into existing workflows (not a replacement, an addition)
- What quality checks it enforces (coverage, verification, ordering)
- Whether it's a new skill or an extension of task-create
- What the minimum viable version looks like vs. the full vision
- A draft requirements.md for REQ-PROC-058

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] Results of TASK-PROC-001-02 (REQ-PROC-001) are incorporated/referenced as well
- [x] creation of any kind of task is incorporated
