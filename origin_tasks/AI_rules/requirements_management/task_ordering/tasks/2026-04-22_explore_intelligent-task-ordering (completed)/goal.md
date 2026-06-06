---
task_id: TASK-PROC-042-01
type: explore
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-04-23
started: 2026-04-22
effort: L
created: 2026-04-22
after: []
awaiting: []
target_package: "Task Ordering Engine"
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06]
  sections: []
scope_description: "Explore all factors that influence sensible task ordering; design a portable, dynamic rule-set approach; identify remaining open questions and challenges"
---

# Exploration Task: Intelligent Task Ordering Design

## Objective

Design a **portable, dynamic, token-efficient** system that enables the Software Factory to automatically determine the correct next task to work on — without requiring a human or LLM to review the full task list.

The exploration must identify:
1. All factors that influence task ordering (known and unknown)
2. A viable architecture for a dynamic rule set
3. How to detect dependencies heuristically at task creation time
4. What a portable evaluation engine looks like
5. What new challenges this approach introduces

---

## Context: Why This Is Hard

### The current state

`next_tasks.py` uses a fixed sort key:
```
(writes_requirements, is_next_package, explore_before_impl, req_in_progress, -priority)
```

This works for the current task mix but has accumulated patches over time. It encodes ordering logic as Python code, making it brittle: every new insight requires a code change, and the logic is not portable to other projects.

### The fundamental tension

Task ordering involves two competing concerns:

**Sequencing** — some tasks must precede others because they produce artifacts that later tasks consume:
- Personas before scenarios
- Scenarios before flows  
- Flows before requirements
- Requirements before implementation tasks
- Implementation tasks before integration/release

**Priority** — within tasks that are "ready to start", some are more urgent than others (release scope, urgency score, risk, etc.)

The current system handles priority reasonably well but handles sequencing poorly — relying on manually set `after`/`awaiting` fields that are often incomplete.

---

## Known Factors That Influence Ordering

### 1. Artifact layer (upstream → downstream)

The project has a clear artifact hierarchy. Tasks at an upstream layer generally must complete before downstream tasks can start:

```
Process/Factory tasks  ← cross-cutting; often prerequisites for everything
Persona writing
  ↓
Scenario writing
  ↓
User Flow writing/editing
  ↓
Requirements exploration (writes requirements from flows)  ← writes_requirements: true
  ↓
Implementation task creation (explores that create impl tasks)
  ↓
Code implementation
  ↓
Testing / validation
```

**Key question**: Is this hierarchy always linear, or are there lateral dependencies (e.g. a code impl that also requires a process task to complete first)?

### 2. Release / package assignment

Tasks assigned to the current release package should be prioritized over tasks for future releases. Currently handled via `target_package` → `is_next_package`.

**Gap**: Many tasks (especially process/exploration tasks) have no `target_package`. The script falls back to treating them as lower priority, but this is imprecise. Some package-less tasks (e.g. `writes_requirements: true` explores) are actually highest priority.

### 3. Task type within layer

Within the same artifact layer, the current heuristic "explore before impl" exists because:
- Explores that write requirements must precede impls (captured by `writes_requirements`)
- Explores that create impl tasks should precede those impl tasks

But not all explores precede impls. Some explores are forward-looking research with no current impl consumer.

**Gap**: The explore/impl distinction is too coarse. What matters is whether the explore *produces something that a pending impl needs*.

### 4. Urgency × impact score

The classic priority signal. Currently used as the tiebreaker. Is this the right role for it, or should it influence earlier in the sort?

### 5. Explicit dependencies (`after`, `awaiting`)

When a task explicitly declares a dependency, this should be respected. Currently working correctly.

**Gap**: Many implicit dependencies exist and are never declared. See the "heuristic detection" section below.

### 6. Factory/process prerequisites

Some process tasks (e.g. a skill that enables a new workflow) must complete before any product tasks that use that workflow. Currently these have no special priority signal — they compete on urgency score alone.

**Unknown factor**: Are there other cross-cutting prerequisites not yet visible in the current task mix?

---

## The Portability Problem

The current ordering logic is baked into `next_tasks.py` as Python sort keys. This means:

- It only works for projects using this exact folder structure and frontmatter schema
- Updating the rules requires changing Python code
- No single source of truth for "what the rules are"

### Proposed architecture: external rule set

The ordering logic should be expressed in a **declarative rule file** (e.g. YAML or TOML) that:

1. Defines **artifact layers** (ordered from upstream to downstream) — expressed as folder path patterns or task type signals
2. Defines **within-layer ordering** (e.g. explore before impl, or priority-score-first)
3. Defines **cross-layer rules** (upstream layer tasks precede downstream layer tasks)
4. Defines **special flags** and their effect (e.g. `writes_requirements` → always first)
5. Is **readable and editable** by a skill or LLM without touching Python

The evaluation engine (`next_tasks.py` or a replacement) reads this rule file and applies it. The engine itself is project-agnostic.

### Questions to answer

- What format is most readable for an LLM editing the rule set? (YAML, TOML, a custom DSL?)
- How do path patterns work portably? (glob patterns? regex? named layers?)
- What happens when a task matches multiple layers? (priority ordering between rules)
- How do we version the rule set? (should it be in `requirements_tasks/` or `.claude/`?)

---

## Heuristic Dependency Detection at Creation Time

### The problem

When a new task is created, it should automatically declare dependencies on tasks it will consume. But doing this correctly requires knowing:
- What artifact layer the new task is at
- What existing tasks produce artifacts that layer depends on

Doing this with an LLM on every task creation is prohibitively expensive.

### The folder-path heuristic

A task's folder path is a strong, cheap signal for its artifact layer:

| Path pattern | Artifact type produced |
|---|---|
| `requirements_user_needs/personas/*/tasks/` | Persona |
| `requirements_user_needs/.../scenarios/*/tasks/` | Scenario |
| `requirements_user_needs/user_flows/*/tasks/` | User Flow |
| `requirements_tasks/functional/*/epic_*/tasks/` | Requirement / Feature |
| `requirements_tasks/functional/*/tasks/` (impl) | Code |
| `requirements_tasks/process/AI_rules/*/tasks/` | Process / Factory |
| `requirements_tasks/non-functional/*/tasks/` | NFR / Design System |

A script (not an LLM) can:
1. Classify the new task's layer from its path
2. Find existing open tasks at upstream layers
3. Propose `after` entries (for human/skill review, not auto-applied blindly)

### Open questions

- How granular should the layer taxonomy be? (e.g. is "scenario" one layer or should sub-types like `capture.spontaneous` vs `analysis.self_reflect` matter?)
- What if an upstream task is already completed? (should be ignored as a dependency)
- What if there are many upstream open tasks? (offer a filtered, prioritized list)
- Should the heuristic suggest `after` entries only, or also `awaiting` entries?

---

## The Skill Question

For the rule set to stay current as the factory evolves, a skill is needed that can:
1. Review the current rule set
2. Understand a new task type or ordering need (from a description or by inspecting new tasks)
3. Propose an update to the rule set
4. Apply the approved update

This is analogous to how `claude-modify-skill` updates skill files — but for the ordering rule set.

**Design questions for the skill:**
- When is it triggered? (after a new task type is introduced? periodically? on demand?)
- How does it validate that the rule change doesn't break existing ordering expectations?
- Should it run a simulation against the current task list to preview the effect?

---

## Task Types Not Currently in the Backlog

The exploration must look beyond the current open task list. Based on the skill inventory, these task types exist but have no current representatives in the backlog:

- **UI scribble tasks** (`ui-create-scribble`) — design artifacts, precede Flutter impl
- **Persona writing tasks** (`ux-write-persona`) — very upstream
- **Scenario writing tasks** (`ux-write-scenario`) — upstream of flows
- **Flow approval tasks** (`ux-flow-approve`) — gate for requirement derivation
- **Value trade-off records** (`vcd-log-tradeoff`) — design decisions, no clear layer
- **Release execution tasks** (`release`) — terminal, must be last
- **Integration test tasks** (`code-run-integration`) — after impl, before release

These must be considered in the layer taxonomy even if no current tasks exist for them.

---

## Deliverables

- [ ] Complete taxonomy of task artifact layers (with folder path patterns)
- [ ] Draft ordering rule set in proposed format (with rationale for each rule)
- [ ] Design for the evaluation engine (how rules are applied to produce a ranked list)
- [ ] Heuristic dependency detection algorithm (path-based, scriptable)
- [ ] Design for the "update ordering rules" skill
- [ ] Identified open questions and risks not covered above
- [ ] Assessment of portability: what assumptions does the design make about project structure?

## Skills to Use

- `claude-switch-opus` for the design phase (complex trade-off reasoning)
- `requ-explore` if the requirement needs to be expanded during exploration
- No implementation — this is design and specification only

## References

- Current script: `scripts/next_tasks.py`
- Related work: `requirements_tasks/process/AI_rules/requirements_management/release_version_management/tasks/2026-04-22_explore_next-task-prioritization-fix (completed)/`
- Skill inventory: `.claude/skills/INDEX.md`
- Artifact hierarchy: `requirements_user_needs/README.md`
