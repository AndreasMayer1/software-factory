# Phase 1 Investigation Protocol
**Task**: TASK-PROC-042-01 — Intelligent Task Ordering Design
**Date**: 2026-04-22
**Status**: Phase 1 complete, Phase 2 (Opus design) pending

---

## Sources Reviewed

- `requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md` (REQ-PROC-042)
- `scripts/next_tasks.py` — current ordering logic (full file, 692 lines)
- `.claude/skills/INDEX.md` — complete skill inventory
- `.claude/skills/task-create/skill.md` — task types + frontmatter schema
- `.claude/skills/task-create-impl/skill.md` — impl task creation
- `.claude/skills/ux-write-persona/skill.md` — persona task type
- `.claude/skills/ux-write-scenario/skill.md` — scenario task type
- `.claude/skills/ux-create-flow/skill.md` — flow task router
- `.claude/skills/ui-create-scribble/skill.md` — scribble design tasks
- `.claude/skills/release/skill.md` — release execution (terminal)
- `.claude/skills/code-run-integration/skill.md` — integration test runs
- `.claude/skills/requ-derive-from-flow/skill.md` — gap-analysis creates explore tasks
- `.claude/skills/task-create-impl-orchestrator/skill.md` — orchestration explore tasks
- `.claude/skills/requ-verify-flow-coverage/skill.md` — verification tasks
- `.claude/factory_flows.md` — full pipeline diagram
- Live backlog survey: `grep -rh "^type:" requirements_tasks/`

---

## Finding 1: Complete Task Type Taxonomy

### Standard `type` field values (from task-create template)

| Type | Who creates it | What it produces |
|------|---------------|-----------------|
| `impl` | task-create-impl, task-create | Code, docs, skills, design artifacts |
| `explore` | task-create + requ-explore, requ-derive-from-flow | requirements.md, design docs, analyses |
| `bugfix` | task-create + code-bugfix | code fix |
| `define` | task-create | feature requirements (epic breakdown) |
| `review` | task-create | review findings |
| `analyze` | task-create | analysis documents |

### Special frontmatter flags that modify type semantics

| Flag | Effect on ordering | Set by |
|------|-------------------|--------|
| `writes_requirements: true` | Elevates above ALL other tasks (even current-release impls) | `requ-derive-from-flow`, manual |
| `verification_task: true` | Flow coverage gate task; must not inherit target_package | `requ-derive-from-flow` (Phase 4.5) |
| `source_gap: [gap-id]` | Created by requ-derive-from-flow; package determined later | `requ-derive-from-flow` |
| `cascade_type: user_needs` | Multi-pass cascade task; ordering crosses multiple passes | `task-create` (manual) |
| `opus_recommended: true` | Signals Opus should be used; no direct ordering effect | various |

### Actual type values found in live backlog (from grep)
- `impl` (195), `explore` (113) — dominant
- `bugfix` (3), `define` (2), `analyze` (6), `review` (1) — minority
- Non-standard artifacts in plans_and_protocols/: `plan`, `protocol`, `audit_report`, etc. — these are NOT task goal.md files, they are protocol documents
- `verification_task: true` — 6 instances in project

---

## Finding 2: Complete Artifact Layer Hierarchy

Ordered from most upstream to most downstream:

### Layer 0: Factory/Process (cross-cutting prerequisites)
- **Path pattern**: `requirements_tasks/process/AI_rules/*/tasks/`
  - Also: `requirements_tasks/process/documentation_rules/*/tasks/`
- **Artifact produced**: skills (.claude/skills/), CLAUDE.md, scripts, doc/ guidelines
- **Skills**: requ-explore, task-resolve, code-simple, code-complex, code-test
- **Key property**: Often prerequisites for product layers, but has no fixed position in product hierarchy. Some (e.g. `writes_requirements: true`) are critical-path above even Layer 7 tasks.
- **Ordering signal**: `writes_requirements: true` flag → always first

### Layer 1: Persona
- **Path pattern**: `requirements_user_needs/personas/*/tasks/`
- **Artifact produced**: `persona.md`
- **Skills**: ux-write-persona
- **Ordering note**: Very upstream; no current examples in open backlog

### Layer 2: Scenario
- **Path pattern**: `requirements_user_needs/personas/*/scenarios/*/tasks/`
- **Artifact produced**: `scenario.md`
- **Skills**: ux-write-scenario
- **Ordering note**: Depends on Layer 1 (persona must exist/be approved)

### Layer 3: User Flow
- **Path pattern**: `requirements_user_needs/user_flows/*/tasks/`
- **Artifact produced**: `flow.md` (with multi-status state machine: draft → in_review → aligned → approved)
- **Skills**: ux-create-flow → ux-flow-draft / ux-flow-complete / ux-flow-approve
- **Ordering note**: Depends on Layer 2 (scenario must exist); can be worked in parallel across different flows

### Layer 4a: Requirement Derivation (gap analysis)
- **Path pattern**: anywhere (functional/, proc/, etc.) with `source_gap:` frontmatter
- **Frontmatter flags**: `writes_requirements: true`, `source_gap: [gap-id]`
- **Artifact produced**: `requirements.md` for a specific gap
- **Skills**: requ-derive-from-flow creates the goal.md; requ-explore executes it
- **Ordering note**: These are the MOST critical-path explore tasks; currently handled by `writes_requirements: true` flag

### Layer 4b: Flow Coverage Verification
- **Path pattern**: anywhere with `verification_task: true` + `verification_bundle:` frontmatter
- **Artifact produced**: gap coverage assessment; triggers requirement updates
- **Skills**: requ-verify-flow-coverage
- **Ordering note**: After ALL bundle explore tasks (Layer 4a) complete; blocks on them via `after:` list

### Layer 5: Standard Requirement Exploration
- **Path pattern**: any — `requirements_tasks/functional/*/tasks/`, `requirements_tasks/non-functional/*/tasks/`, `requirements_tasks/process/*/tasks/`
- **Artifact produced**: `requirements.md`, design docs
- **Skills**: requ-explore (via task-create + claude-route)
- **Ordering note**: Should precede impl tasks for the same requirement

### Layer 6: UI Scribble Design
- **Path pattern**: `[requirement-path]/scribbles/v{n}/` — NOT a standard task folder with goal.md
- **Note**: Scribbles are spawned from within code-simple/code-complex, not as standalone task folders. Not represented in next_tasks.py scan. May become a task type if ever created as standalone goal.md.
- **Skills**: ui-create-scribble, ui-verify-flutter, ui-improve-flutter
- **Ordering note**: Between Layer 5 and Layer 7; scribble approval gates implementation

### Layer 7: Code Implementation
- **Path pattern**: `requirements_tasks/functional/*/tasks/` (mostly), also non-functional
- **Artifact produced**: `lib/**/*.dart`
- **Skills**: code-simple, code-complex
- **Ordering note**: After Layer 5 (requirements defined); after Layer 6 (scribble approved, if applicable)

### Layer 8: Testing
- **Path pattern**: same as Layer 7 or adjacent tasks/ folder
- **Artifact produced**: `test/**/*.dart`, integration test files
- **Skills**: code-test, code-run-integration
- **Ordering note**: After Layer 7 (implementation exists); integration tests after unit/widget tests

### Layer 9: Release (terminal — NOT a goal.md task type)
- **Note**: Release is invoked as a skill directly, not as a task in the backlog
- **Skills**: release, requ-prep-release, release-plan
- **Ordering note**: Terminal; only when all package tasks complete

### Layer 0b: Orchestration Tasks (special)
- **Path pattern**: `requirements_tasks/process/AI_rules/*/tasks/` (REQ-PROC-035)
- **Frontmatter**: no special flags, but scope is "create the next impl task"
- **Skills**: task-create-impl-orchestrator creates these
- **Ordering note**: Explore type; treated as layer 0 by path

---

## Finding 3: Current next_tasks.py Sort Key Analysis

Current sort key (5 components, applied in order):
```python
(writes_req_rank, is_next, type_rank, req_not_active, -priority_score)
```

1. `writes_requirements` (0 if true, 1 if false) — critical-path explores first
2. `is_next` (0 if in current package/release, 1 otherwise) — current release first
3. `type_rank` (0 if explore, 1 if impl) — explore before impl within scope
4. `req_not_active` (0 if req has completed tasks, 1 if not) — continue in-progress requirements
5. `-priority_score` (urgency × 10 + impact) — tiebreaker

**What the sort key cannot express:**
- Layer ordering (e.g. "persona tasks before scenario tasks before flow tasks before requirement tasks")
- Within-layer ordering beyond explore/impl distinction (e.g. "verification task after all bundle explores")
- Artifact-type dependencies (e.g. "a flow task blocks the flow-derivation explore task for the same flow")
- The difference between a "writes_requirements process task" and "a process task with no current-release package"

---

## Finding 4: Key Gaps in Current System

1. **No path-based layer inference**: The script doesn't use folder paths to infer artifact layer. It only uses `type` field and explicit frontmatter flags.

2. **`writes_requirements` is the only cross-type signal**: Other layer relationships (persona > scenario > flow > requirements) are not expressed.

3. **No heuristic dependency detection**: When a new task is created, nothing proposes `after:` entries based on folder path patterns.

4. **`target_package` gap for process tasks**: Process/factory tasks often lack `target_package`, making them rank after ALL release-scoped tasks unless they have `writes_requirements: true`.

5. **Explore/impl distinction is too coarse**: The sort key assumes "all explores before all impls", but this only holds within the same artifact layer. An impl task at Layer 5 (a process doc) should precede an explore task at Layer 7 (if that explore is forward-looking research with no current consumer).

6. **No portable rule set**: All logic is Python code in next_tasks.py.

---

## Finding 5: What "Portability" Really Means

The goal.md requires a "portable" design. Based on analysis:

- The **evaluation engine** (Python script) should be project-agnostic: it reads a rule file + task metadata, applies rules, returns a ranked list
- The **rule file** describes THIS project's conventions: folder patterns, layer names, special flags
- Moving to a new project = writing a new rule file (not modifying the engine)

Key project-specific elements that belong in the rule file:
- Folder path → layer mapping (glob patterns)
- Layer ordering (which layer is upstream of which)
- Special flags and their priority effects
- Within-layer ordering rules (e.g. explore before impl)

Project-agnostic elements that belong in the engine:
- Rule file parsing
- Layer classification from path
- Dependency resolution (after/awaiting)
- Ranking algorithm that applies rule weights

---

## Questions for Opus (Phase 2)

1. What format for the rule file is most readable AND editable by an LLM? (YAML with anchors? TOML? a simple DSL?)
2. How granular should the layer taxonomy be? Should `define`, `analyze`, `review` be their own layers or fold into `explore`?
3. Where does the rule file live? (`.claude/task_ordering_rules.yaml`? `requirements_tasks/ordering_rules.yaml`?)
4. How does the evaluation engine handle tasks that match multiple layers? (priority order of rules?)
5. What is the minimal change to `next_tasks.py` that adds path-based layer inference while keeping the existing sort key as fallback?
6. Design for the "update ordering rules" skill: when is it triggered, how does it validate changes?
7. How should `verification_task: true` tasks be ordered relative to the bundle explores they verify?

---

## Status

Phase 1 complete. Ready for Opus design phase.
