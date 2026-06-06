---
id: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: in_progress
effort: L
target_package: ""
stakeholder: app_provider
created: 2026-04-22
updated: 2026-06-04
after: []
blocks: []
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "The system automatically determines the next task to work on without requiring a human or LLM to review the full task list"
    - id: AC-02
      text: "Task ordering rules are captured in an explicit, editable rule set (not hardcoded in a script)"
    - id: AC-03
      text: "A skill exists that can update the rule set when new task types, folder structures, or prioritization needs arise"
    - id: AC-04
      text: "The rule set and its evaluation mechanism are portable — usable in projects with different folder structures and task type conventions"
    - id: AC-05
      text: "Task type and artifact layer are inferred from folder path without requiring LLM analysis at ordering time"
    - id: AC-06
      text: "Dependencies between task types are detected heuristically at task creation time, not at ordering time"
    - id: AC-07
      text: "The evaluation engine validates the rule file on load; a malformed rule file triggers a visible warning and the engine falls back to hardcoded defaults instead of failing"
    - id: AC-08
      text: "Rule changes can be dry-run against the current backlog (showing how task ordering would shift) before they are committed"
    - id: AC-09
      text: "When a new skill that produces a new task type is created, the skill-creation workflow prompts the user to register the new task type in the ordering rule set"
    - id: AC-10
      text: "In-flight cascade tasks (those that have advanced past Pass 1) are ranked above unrelated non-cascade work until all passes complete, preventing layer drift between artifact levels (personas, flows, requirements, code) due to a stalled cascade"
    - id: AC-11
      text: "A factory_urgent: true frontmatter flag exists; the ranking engine elevates tasks carrying it above ordinary unpackaged work so that urgent cross-cutting factory prerequisites are not unfairly deprioritized against current-release implementation tasks"
    - id: AC-12
      text: "Every ranking_signals entry in the rule file carries rationale: and rationale_source: fields; the rule-update skill surfaces these fields when any signal's position in the ranking tuple is proposed to change, prompting the user to confirm the change is compatible with the documented rationale before applying it"
    - id: AC-13
      text: "A guided init mode exists that analyzes a project's existing folder structure and frontmatter and produces a starter rule file draft via AI inference (using the opus-advisor agent), replacing the manual 2-4 hour onboarding process for new projects adopting the ordering engine"
---

# REQ-PROC-042: Intelligent Task Ordering

## Problem Statement

As the Software Factory grows, the `next_tasks.py` script has accumulated increasingly complex heuristics for determining what to work on next. These heuristics are hardcoded, project-specific, and fragile: each new task type or prioritization insight requires a code change. More fundamentally, the script cannot reason about the *meaning* of a task — only its metadata fields.

Meanwhile, the actual ordering logic is non-trivial. The project has a layered artifact hierarchy (Personas → Scenarios → Flows → Requirements → Tasks → Code), and tasks exist at every layer. Tasks that write upstream artifacts (requirements, flows, scenarios) must run before tasks that consume them — but this dependency is often implicit and not reflected in `after`/`awaiting` fields.

## User Need

> As the App Provider, I want tasks to be worked on in a sensible order without a human or an LLM having to review the full open task list each time to decide what comes next.

The key constraints:

- **Dynamic**: The ordering rules must be updatable as new task types, artifact layers, or workflow patterns emerge — without requiring code changes each time.
- **Portable**: The mechanism must generalize beyond this specific project. Other projects may have different folder conventions, different task type sets, or entirely different artifact hierarchies. The rule set describes *a* project's conventions; the evaluation engine is project-agnostic.
- **Token-efficient**: Dependency detection and ordering decisions must not require a full LLM pass over all open tasks on every invocation. The ordering must be deterministic and scriptable.
- **Heuristic at creation, not at ordering**: Where dependencies cannot be made explicit upfront (e.g. "this scenario is needed by some future flow"), they should be inferred by a script at task creation time based on folder-path heuristics — not re-evaluated expensively at every ordering invocation.

## Acceptance Criteria

See YAML frontmatter.

## Background: Current Mechanisms and Their Limits

### What exists today

- `after: [TASK-ID]` — explicit dependency on another task completing
- `awaiting: [ID]` — blocks on an artifact (REQ-*, FLOW-*, or descriptive placeholder like `time`)
- `writes_requirements: true` — flags critical-path requirement-writing explores (added 2026-04-22)
- `target_package` / `target_release` — maps task to release scope for priority ordering
- `urgency` × `impact` priority score

### What is missing

- No way to express "this task type always precedes that task type" as a reusable rule
- No heuristic detection of implicit dependencies at task creation time
- No portable rule set — ordering logic is baked into `next_tasks.py`
- No mechanism for the LLM/skill to update ordering rules as the factory evolves

## Artifact Hierarchy (this project)

```
App Provider Persona
  └── Scenario
        └── User Flow
              └── Requirement (REQ-*)
                    └── Task (TASK-*) — exploration or implementation
                          └── Code / Artifact
```

Process tasks (PROC) sit outside this hierarchy — they evolve the factory itself (skills, scripts, guidelines, workflows). They are often prerequisites for product tasks but have no fixed position in the product hierarchy.

## Notes

- The folder path of a task is a strong signal for its artifact layer and type. E.g.:
  - `requirements_user_needs/personas/*/tasks/` → writes personas
  - `requirements_user_needs/.../scenarios/*/tasks/` → writes scenarios
  - `requirements_user_needs/user_flows/*/tasks/` → writes or edits user flows
  - `requirements_tasks/functional/*/tasks/` → implements functional requirements (code)
  - `requirements_tasks/process/AI_rules/*/tasks/` → evolves the factory process
- This path-based inference is deterministic and cheap — no LLM needed.

## Lifecycle Constraint & Release-Scoping Contract

This section states the *model* behind the ordering signals above — why the engine is
shaped the way it is. The behaviour it describes is already implemented; the contract is
written here so it is not re-derived. Release/package assignment itself is owned by
REQ-PROC-034; this section references that mechanism rather than restating it.

**The lifecycle constraint (root of the design).** A requirement must be *authored*
before it can be *release-assigned*: deciding which release/package a requirement belongs
to needs the full cross-flow picture, which only exists once the requirement is written.
Consequently `requ-derive-from-flow` deliberately does **not** set `target_package` /
`target_release` on the requirement-authoring tasks it creates; assignment is deferred to
`release-plan` (REQ-PROC-034) after requirements exist. Requirement-authoring tasks are
therefore *structurally unscopeable-by-release* at the moment they are queued.

The ordering and gating contract follows from that constraint:

1. **Weak signal → scheduling only; strong signal → release binding.** A flow's
   `release_scope` chunk priority (1/2/3, a per-flow hint) feeds **only** the authoring
   task's scheduling `urgency`/`impact` (via `requ-derive-from-flow` Phase 3.5). It is
   **never** a release binding — it is too weak (one flow / flow-cluster) to bind a
   release. The authoritative release binding is the cross-flow `target_package`→version
   assignment, deferred to `release-plan`. `suggested_release_chunk` (and the requirement's
   `release_chunk`) is descriptive metadata only — not read by the ordering engine or by
   release readiness.

2. **Global authoring priority is intentional.** Because authoring tasks cannot be
   release-scoped, the `writes_requirements: true` special flag carries weight `-10000`,
   ranking such tasks **above** the release/package-scope signal (`is_next`) in the sort
   tuple. This is deliberate: it protects the invariant *"a requirement is authored before
   the impl tasks that consume it run."* The front-loading of a not-yet-needed authoring
   task is an accepted, low-frequency cost — authoring tasks are rare; `priority_override`
   is the manual escape hatch when a specific task should be pinned instead.

3. **Staging is the counterweight that protects shipping.** The global authoring priority
   does **not** block a release. `release_readiness.py` (`detect_stage`) only treats
   pending requirement-authoring tasks as blocking at **Stage 1**, and only while the
   release's packages are unassigned. Once packages are assigned (Stage 2+), remaining
   authoring tasks are non-blocking process work — begin-impl, active, and cut-release do
   not wait on them. A requirement-authoring task for a far-future release therefore never
   blocks the current release.

4. **Explore-task routing keys on the same signal.** `claude-route` routes an explore task
   by `writes_requirements`: `true` → `requ-explore` (it authors a requirement),
   `false`/absent → `task-resolve` (brainstorming / investigation / evaluation producing
   analysis docs). This keeps routing consistent with the ordering/readiness layers, which
   already key on `writes_requirements`.

**Essential vs accidental complexity.** Points 1–3 are *essential* — forced by the
lifecycle constraint; they cannot be "simplified away" without breaking either the
author-before-impl guarantee or the ability to ship. The one piece of *accidental*
complexity is the dual signal (`type: explore` **and** `writes_requirements`) — see
Rejected Alternatives.

## Rejected Alternatives

- **Release-scope the requirement-authoring tasks** (so ordering/gating could prefer
  current-release authoring and defer future-release authoring). **Impossible by
  construction**: the release is the *output* of authoring, not an input, and the per-flow
  chunk hint is too weak to bind a release. This is why the global-priority + staging
  pattern exists instead — do not re-propose release-scoping authoring tasks.

- **Introduce a dedicated task `type`** (e.g. `type: requ` / `type: derive`) to distinguish
  requirement-authoring explores from other explores. **Rejected** (originally by
  TASK-PROC-034-18, the task that introduced `writes_requirements`): `type` is overloaded
  across ≥5 code sites (`next_tasks.py --type`, the AC-coverage guard,
  `ranker._layer_intra_type_rank`, the ordering layers, `release_readiness.py`
  `non_impl_types`), and the metadata schema deliberately consolidated
  `define`/`review`/`analyze` *into* `explore`. The `writes_requirements` boolean is the
  chosen single-purpose signal.

- **Collapse the `type` + `writes_requirements` dual signal** into one. This is the only
  genuine accidental complexity (`writes_requirements` is the precise signal; `type:
  explore` is the overloaded one). Judged **low-ROI**: it would churn the ≥5 type-reading
  sites and their tests for a comprehension gain only. Left as-is unless a future change
  already touches those sites.

## Related Requirements

- REQ-PROC-034 (Release Package Management) — owns package/release assignment and the
  `release_scope` model; this requirement references that lifecycle, the deferred-assignment
  rule lives there.
- REQ-PROC-058 (Implementation Task Planning Quality) — owns decomposition planning and
  `claude-route`'s goal-shape routing (the explore-routing fix lives under it,
  TASK-PROC-058-10).
- REQ-PROC-041 (Session Lifecycle / Automated Orchestration) — owns the plan-driven
  orchestration chain that consumes this ordering.
- REQ-PROC-065 (Epic: Task Lifecycle) — owns task creation/state/completion; explicitly
  delegates ordering & prioritization here.

## Design Reference

Full design (layer taxonomy, draft rule file, evaluation engine, dependency heuristic, maintenance skill, portability assessment):
`tasks/2026-04-22_explore_intelligent-task-ordering/plans_and_protocols/2026-04-22_02_opus_design.md`

Key decisions summarised:
- **Rule file**: `.claude/task_ordering_rules.yaml` — YAML with comments; schema-versioned
- **Engine**: refactor `scripts/next_tasks.py` into `scripts/task_ordering/` module; rule file optional (falls back to hardcoded defaults matching current behaviour)
- **Layer taxonomy**: 10 layers (factory_process · persona · scenario · user_flow · requirement_derivation · flow_verification · requirement_exploration · ui_design · implementation · testing), sparse integer ordering (0, 10, 20, …) so new layers can be inserted without renumbering
- **Dependency heuristic**: separate `scripts/propose_after.py` CLI invoked at task-creation time; produces suggestions (never auto-applies); reverse direction (updating existing tasks when a new upstream task is created) intentionally deferred — layer_order signal handles ordering correctly even with incomplete after: fields
- **Maintenance skill**: `claude-modify-ordering-rules` — mandatory dry-run via `simulate.py` before any rule change is committed; must read and surface rationale: fields before approving signal order changes
- **Special flags in rule file**:
  - `writes_requirements: true` — weight −10000; critical-path requirement-writing explores always rank first
  - `factory_urgent: true` — weight ~−1000; urgent cross-cutting factory tasks not deprioritized against current-release impl (AC-11)
  - `cascade_active: true` — weight ~−500; set by cascade skill when task advances past Pass 1; cleared on completion; prevents layer drift (AC-10)
  - `scribble_task: true` — classifies standalone UI scribble tasks into the ui_design layer (order 55); no ranking weight
- **Ranking signal rationale**: every ranking_signals entry in the rule file carries rationale: and rationale_source: fields documenting the user intent behind each signal's position in the tuple (AC-12). Rationale for current_package_scope preceding layer_order: upstream tasks (e.g. user flow writing) require manual user involvement and are started deliberately; impl tasks run autonomously — current-release impl should be preferred in unattended operation.
- **Test task ordering**: testing layer remains at order 70 (after implementation). TDD ordering not implemented; empirical evidence shows the AI cannot reliably write meaningful tests without an existing implementation.
- **Init mode**: guided session using opus-advisor agent to analyse project structure and propose starter rule file; reduces new-project onboarding from 2–4 hours to a guided session (AC-13)
