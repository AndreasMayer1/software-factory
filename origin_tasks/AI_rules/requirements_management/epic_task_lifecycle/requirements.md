---
id: REQ-PROC-065
status: active
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
effort: XXL
stakeholder: developer
created: 2026-06-02
after: []
blocks: []
market_research_refs: [] # No relevant findings — internal process tooling
personas_served: [PERSONA-004]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "feat_task_creation/requirements.md has status: defined or status: active"
    - id: AC-02
      text: "feat_task_creation_code/requirements.md has status: defined or status: active"
    - id: AC-03
      text: "feat_task_creation_from_requirement/requirements.md has status: defined or status: active"
    - id: AC-04
      text: "feat_task_state_machine/requirements.md has status: defined or status: active"
    - id: AC-05
      text: "feat_task_completion/requirements.md has status: defined or status: active"
    - id: AC-06
      text: "feat_perpetuating_task_creation/requirements.md has status: defined or status: active"
---

# Epic: Task Lifecycle

## Overview

All mechanisms by which tasks are created, progress through their state machine, and are completed in the Software Factory — covering the skills that produce task workspaces, the state model governing their lifecycle, and the skills that close them.

## Purpose

Tasks are the unit of work in the factory. As of 2026-06-02, the skills that create and complete tasks (`task-create`, `task-create-code`, `task-derive-from-requ`, `task-complete`, `task-complete-bugfix`) were authored without formal requirements. This epic gives the task lifecycle a governed home: new capabilities are written as full requirements, and the existing skills are documented incrementally as their placeholder features are promoted. Having this home also prevents the task state machine — currently defined in a single AC buried in REQ-PROC-008 — from drifting without a clear owner.

## Scope

**Included:**
- Skills that produce task workspaces (`task-create`, `task-create-code`, `task-derive-from-requ`, and future creation variants)
- The task state machine: valid states and valid transitions
- Skills that close tasks (`task-complete`, `task-complete-bugfix`)
- Lifecycle extension mechanisms (e.g. self-perpetuating task creation)

**Excluded:**
- Task ordering and prioritization → REQ-PROC-042
- Decomposition planning strategy for `task-derive-from-requ` → REQ-PROC-058
- Automated session orchestration → REQ-PROC-041
- What tasks implement (owned by functional/non-functional requirements)

## Features

- [`feat_task_creation`](feat_task_creation/requirements.md) — `task-create` skill *(placeholder — requirements not yet written)*
- [`feat_task_creation_code`](feat_task_creation_code/requirements.md) — `task-create-code` skill *(placeholder)*
- [`feat_task_creation_from_requirement`](feat_task_creation_from_requirement/requirements.md) — `task-derive-from-requ` skill, creation-mechanism aspects (planning strategy → REQ-PROC-058) *(placeholder)*
- [`feat_task_state_machine`](feat_task_state_machine/requirements.md) — valid states, valid transitions, lifecycle rules *(placeholder)*
- [`feat_task_completion`](feat_task_completion/requirements.md) — `task-complete` + `task-complete-bugfix` skills *(placeholder)*
- [`feat_perpetuating_task_creation`](feat_perpetuating_task_creation/requirements.md) — skill that wraps `task-create` and embeds a work-discovery step, enabling a self-perpetuating automation loop

## Cross-Feature Invariants

1. **Unique IDs** — every task has a unique, atomically-allocated task ID (`allocate_task_id.py`); no two tasks share an ID.
2. **Requirement anchor** — every task created by a skill in this epic has a valid `parent_requirement` referencing an existing `requirements.md`.
3. **State monotonicity** — once `completed`, a task is never moved back to `pending` or `in_progress`.
4. **Single task-create delegation** — skills that create tasks MUST call `task-create` or `task-create-code` internally; no skill constructs `goal.md` independently.
5. **Standing tasks never complete** — a standing / loop-task (Recurrence Mechanism 3 below) never enters `completed`; it recurs by resetting from `in_progress` to `pending` (or by re-arming a `not_before` gate). This is what keeps it consistent with Invariant 3: monotonicity forbids `completed → pending`, never `in_progress → pending`.

## Recurrence Mechanisms

Some tasks create their own successor or recur rather than running once. Four mechanisms exist, each answering "how does a task recur?" differently:

1. **Plan-driven chain** — release orchestration (REQ-PROC-035 SEC-05): each `/autorun` session creates one impl task from a predefined plan, perpetuating via *two-slot alternation* (the terminal predecessor's folder slot is overwritten; at most two orchestration folders are ever live). In production.
2. **Discovery-driven chain** — `feat_perpetuating_task_creation`: an Opus discovery agent scans for remaining work and creates one new follow-up folder per round.
3. **Same-folder reset (standing / loop-task)** — one permanent folder reset to `pending` each round, never completed (exemplar TASK-PROC-046-16; the monthly dependency decision/review).
4. **Calendar gate** — the `not_before` eligibility primitive (`feat_task_state_machine`): governs *when* a standing task becomes eligible again (e.g. monthly), independent of *how* it recurs.

**Invariant**: no new recurrence mechanism is introduced, and no existing one is changed, without reconciling against these four; the mechanisms do not contradict one another.

**Open decision — owned by this epic**: whether the four converge onto a single shared substrate (folder-slot reuse, the `after:` chain that blocks premature execution, the one-task-per-session bound, the `not_before` gate) or remain deliberately separate with documented boundaries. Recommended direction, not yet ratified: *share the mechanical substrate, keep the triggers distinct.* The efforts that must conform once this resolves: TASK-PROC-065-04-01 (date-gate design), TASK-PROC-065-01-01 (standing-task support in `task-create`), TASK-PROC-065-06-01 (perpetuating-task explore).

## Dependencies

- REQ-PROC-042: Intelligent Task Ordering — governs which task is picked next; this epic governs creation and completion
- REQ-PROC-058: Implementation Task Planning — owns the planning strategy of `task-derive-from-requ`; this epic owns its creation-mechanism aspects
- REQ-PROC-041: Autonomous Task Execution — sessions consume tasks produced by this epic's skills; `feat_perpetuating_task_creation` extends the automation loop
