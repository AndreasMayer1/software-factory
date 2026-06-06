---
task_id: TASK-PROC-066-01
type: explore
parent_requirement: REQ-PROC-066
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 5
impact_reason: I5-ENAB
status: pending
effort: L
created: 2026-05-28
after: [TASK-PROC-066-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore how to extract the Software Factory into its own repository: define factory/project boundaries, research distribution mechanisms (Claude Code plugins, update pipelines, CLAUDE.md composition), determine ordering relative to process/ restructuring (TASK-PROC-045-09), and produce an actionable extraction plan."
release_description: ""
opus_recommended: true   # reason: cross-cutting architectural exploration spanning process structure, distribution mechanisms, multi-repo design, toolchain research, and multiple trade-off decisions
writes_requirements: true
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Explore Software Factory Extraction into a Standalone Repository

## Objective

We do not yet know:
- What exactly constitutes the "Software Factory" vs. what is app-specific (the boundary is blurry in many places)
- How the factory would be distributed to and consumed by a project (plugin? submodule? package? script sync?)
- What the Claude Code plugin mechanism can actually provide — and whether it covers skills, hooks, and CLAUDE.md fragments in one go
- How CLAUDE.md (currently a mix of factory constitution and project context) would be split and composed
- Whether the process/ folder restructuring (TASK-PROC-045-09) must complete before extraction begins, or whether the two can proceed in parallel
- How to handle technology-specific guidelines (e.g. Flutter-specific doc/ rules vs. general design-token concepts) — factory vs. project, and how factory parts remain configurable
- Whether other AI toolchains (Cursor, Windsurf, plain API agents) can consume the same package

This exploration should surface the answers, surface the trade-offs, and produce a plan that is specific enough for implementation to begin.

## Background

The Software Factory — skills, agents, hooks, scripts, process requirements, CLAUDE.md constitution — currently lives inside the Mood Tracker app repository. This is pragmatically correct today: the factory grew from this project and is tightly coupled to it.

The developer's vision is decoupling: the factory becomes its own repository, independently versioned and maintained. Any project (starting with this one) can then *use* the factory as a dependency with an explicit update mechanism. The factory adapts to the project's technology and domain, not the other way around.

A free-form vision document with the developer's initial thinking is at:
`requirements_tasks/beyond_this_app/software_factory_extraction/requirement_draft.md`

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-28_00_user_initial_input.md`

Read it as a seed bed, not a spec.

### Related work in flight

| Task | Status | Relationship |
|---|---|---|
| TASK-PROC-045-09 | pending | Defines the migration roadmap for restructuring `process/` and `non-functional/` folders. Creates clean module boundaries — potentially a prerequisite for extraction. |
| TASK-PROC-057-01 | pending | Defines the factory's apex purpose requirement. The resulting requirement should migrate to the factory repo once extraction happens. |

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

Start with the boundary question: walk the actual repository and map each significant folder/file to "factory" or "project-specific" or "entangled." Only after the boundary is understood can distribution mechanisms be evaluated meaningfully.

## Seeds

1. **The boundary question**: Walk the actual repo structure folder by folder. For each significant folder/file, ask: would a new project (say, a web app or a CLI tool) need this? If yes, it's factory. If it references Flutter, Dart, or app domain, it might be project-specific. What's left in the "can't tell" pile — and what does that pile reveal about how tightly coupled the factory and the app actually are?

2. **The CLAUDE.md problem**: CLAUDE.md currently mixes factory constitution (how we work, skill rules, quality gates) with project context (architecture stack, domain info, folder map, custom prompt sections). Claude Code reads exactly one CLAUDE.md per project. Is there a native composition mechanism (imports, fragments, plugin-contributed sections)? If not, what generation step would produce a composed CLAUDE.md at project setup time — and can that step also work for other AI toolchains?

3. **The scripts entanglement**: Skills call scripts in `scripts/`. Some scripts are factory tooling (task management, requirement management, ID allocation, release scripts). Others are project-specific (bundle size checks, app-quality gates, Windows integration test launcher). Can the boundary be drawn at the folder level, or are the two mixed within subfolders? What would `scripts/` look like split across two repos?

4. **The Claude Code plugin architecture**: What exactly can a Claude Code plugin provide today? Skills and agents (`.claude/` content)? Hooks? CLAUDE.md fragments? Custom slash commands? What is the update/versioning model? Is there a registry? Read the actual docs and source — do not rely on training-data assumptions. Delegate this web research to a subagent.

5. **The ordering dilemma**: The process/ folder restructuring (TASK-PROC-045-09) will move things around. The factory extraction will also move things. Do these two operations commute — can they run independently and merge cleanly? Or does one need to land before the other to avoid double-work? What is the minimum restructuring that must happen before extraction becomes tractable?

6. **Technology-specific vs. technology-general guidelines**: `doc/` contains both general design principles (design tokens, clean architecture) and Flutter-specific rules (specific lint rules, package choices, Dart idioms). The general parts feel like factory content; the Flutter-specific parts feel like project content. But design-token rules, for example, are both general *and* need to reference the project's specific token file paths. How does the factory express "you must have design tokens" without encoding Flutter-specific paths? What's the configurability model?

7. **Update mechanism and versioning**: Once the factory is a separate repo, how does a project get updates? Git submodule brings the full history but requires manual update steps. A published package (pub.dev? npm?) has a versioning contract but requires a registry. A simple script that copies files from a factory branch is the lowest-friction option but has no conflict detection. What does "breaking change" mean for a factory update — and how would a project know it needs to do migration work?

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus, `opus_recommended: true`). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — Claude Code plugin architecture, other AI tool extension mechanisms, multi-repo distribution patterns — delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Raw web content inflates the gathering agent's context window fast with irrelevant results; the subagent returns only a distilled summary while the raw content stays in its own context.

Frame search queries as questions rather than keyword bags (e.g. *"what can a Claude Code MCP plugin provide — skills, hooks, CLAUDE.md fragments?"* rather than *"Claude Code plugin capabilities"*).

## Output

A future implementer reading the output of this exploration should understand:

1. A clear boundary map: which artifacts belong to the factory, which are project-specific, and which are entangled (with a plan for each entangled item).
2. A recommended distribution mechanism with rationale — and the alternatives that were considered and rejected.
3. A recommended CLAUDE.md composition strategy.
4. A clear answer to the ordering question: restructuring first, extraction first, or interleaved — with the dependency chain spelled out.
5. The configurability model for technology-specific vs. technology-general guidelines.
6. A list of decisions requiring developer input, framed clearly enough to decide without additional research.
7. A draft extraction plan: the sequence of work, rough effort estimates, and blockers.

The output is honest about what remains uncertain and what was not investigated.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-066-02 | pending | Explores whether/how the Ralph-loop mechanism can drive factory build-out. Hard predecessor (`after`) — its output feeds this extraction plan. |
| TASK-PROC-045-09 | pending | Defines process/ restructuring roadmap. Exploration should assess whether extraction must wait for this or can proceed in parallel. Not a hard blocker for the exploration itself. |
| TASK-PROC-057-01 | pending | Factory purpose definition. Outputs of that task (apex requirement) should inform the factory repo's scope. Coordinate, do not duplicate. |
