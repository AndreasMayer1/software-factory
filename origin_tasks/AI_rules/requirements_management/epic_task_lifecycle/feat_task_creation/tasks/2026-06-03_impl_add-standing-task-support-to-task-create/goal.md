---
task_id: TASK-PROC-065-01-01
type: impl
parent_requirement: REQ-PROC-065-01
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-06-03
expected_tool_calls: 30
skill_chain_depth: 3
synthesis_dependent: true
synthesis_justification: "must hold task-create, task-complete's commit-coupling, the not_before date-gate, and the perpetuating-task feature simultaneously to design one coherent standing-task capability"
after: [TASK-PROC-065-04-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Add first-class standing-task (permanent loop-task) support to the task-create skill, generalizing the hand-rolled TASK-PROC-046-16 pattern and covering both reset-triggered and calendar-triggered (monthly) recurrence"
release_description: ""
opus_recommended: true   # reason: cross-cutting skill change — must reconcile task-create, task-complete commit-coupling, not_before, and perpetuating-task semantics at once
writes_requirements: true
requirements_version:
  commit: b4e3add6
  file: ../requirements.md
---

# Goal: Add Standing-Task Support to the `task-create` Skill

## Objective

Make **standing tasks** (a.k.a. permanent loop-tasks) a first-class output of the
`task-create` skill, so the pattern currently hand-rolled per instance can be created
declaratively. A standing task lives in **one permanent folder** that is never renamed
with a `(completed)` suffix and never auto-deleted; instead of transitioning to
`completed`, each round **resets the task back to `status: pending`** to run again.

The capability must support **two recurrence modes**:

1. **Reset-triggered** (the existing exemplar, TASK-PROC-046-16 — the quality-rule
   proposals loop): the round ends by running a reset script that restores
   `status: pending`, clears session fields, and re-creates the `pending_feedback`
   question/answer pair. The next round fires when its trigger (filed proposals + a
   filled `answer.md`, picked up by the orchestrator) recurs.
2. **Calendar-triggered** (the new monthly dependency-upgrade review — see TASK-PROC-061-10):
   the round ends by re-arming the task's `not_before:` date to the next cycle (e.g. the
   1st of next month), so the orchestrator runs it again on/after that date. This mode
   consumes the `not_before` date-gate primitive (TASK-PROC-065-04-01).

## Background

The project already runs **three different hand-rolled recurring-task mechanisms** — the
fragmentation this task exists to address. The design MUST survey all three and state
explicitly whether the new capability subsumes, wraps, or merely coexists with each:

1. **Same-folder reset (standing)** — **TASK-PROC-046-16**
   (`.../code_quality/tasks/2026-05-14_impl_apply-quality-rule-proposals-loop/`): one
   permanent folder, bespoke `scripts/quality/reset_proposals_loop.py`, never marked
   `completed`. Also **TASK-PROC-061-08** (monthly decision task, reset each cycle) and
   **TASK-PROC-061-10** (planned monthly review, calendar re-arm).
2. **Two-slot alternation chain** — the **release orchestration chain**
   (REQ-PROC-035 SEC-05, `scripts/tasks/create_orchestration_task.py`): each `/autorun`
   session creates exactly one impl (coding) task, then perpetuates itself by
   **overwriting the terminal predecessor's folder slot** — at most two orchestration
   folders are ever live ("a fresh folder, never a third one").
3. **Work-discovery new-folder chain** — **feat_perpetuating_task_creation**
   (REQ-PROC-065-06): spawns a brand-new follow-up folder each round via an Opus
   discovery agent.

These are three answers to one question ("how does a task recur?"). The standing-task
capability should at minimum not become a fourth incompatible mechanism; ideally it
provides the shared primitive the others can be expressed in terms of.

Without skill support, every standing task re-derives: the permanent-folder convention,
the "never complete" semantics, the reset/re-arm mechanism, and the interaction with
`task-complete` (which is coupled to commit and would otherwise force completion +
folder proliferation — the proliferation the developer rejected in
`2026-05-14_feedback_03.md`). This task centralizes that into `task-create`.

REQ-PROC-065-01 is currently a placeholder whose reopen trigger is "a task modifies the
skill's core behavior, metadata format, or output structure." This task meets that
trigger, so authoring the requirement is in scope.

For complete requirements at task creation time:
```
git show b4e3add6:requirements_tasks/process/AI_rules/requirements_management/epic_task_lifecycle/feat_task_creation/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- **Author REQ-PROC-065-01 via `requ-explore`** (the placeholder's reopen trigger is met):
  define standing-task semantics, the declaration mechanism, the two recurrence modes,
  and the `task-complete` interaction.
- **Modify the `task-create` skill via `claude-modify-skill`** to emit standing-task
  scaffolding when requested: the permanent-folder convention, the `status`-reset (not
  `completed`) lifecycle, a frontmatter marker (e.g. `standing: true` + `recurrence:
  reset | calendar`), and the matching reset/re-arm wiring.
- Provide/standardize the **reset mechanism** (generalize `reset_proposals_loop.py` rather
  than copy it per task; any `scripts/` work routes through `claude-write-script`).
- For **calendar** recurrence: wire the re-arm to the `not_before` primitive
  (TASK-PROC-065-04-01) so the monthly upgrade review (TASK-PROC-061-10) consumes it.
- Document how a standing task coexists with `task-complete`'s commit coupling.

### Out of Scope
- Implementing the `not_before` engine support itself (separate impl task from the
  TASK-PROC-065-04-01 design).
- Migrating existing hand-rolled loop-tasks (TASK-PROC-046-16, TASK-PROC-061-08) onto the
  new mechanism — follow-up tasks; this task only adds the capability (optionally one
  reference conversion as proof).
- The `feat_perpetuating_task_creation` (REQ-PROC-065-06) work-discovery loop — that
  spawns NEW folders and is a sibling mechanism, not this same-folder reuse pattern.

## Design Decisions to Resolve (during requ-explore)
- How is "standing" declared at creation — a frontmatter attribute on existing types, or
  a new task `type`? (Lean: attribute, to avoid a new type per the skill's own rule.)
- What stops `task-complete` from terminalizing a standing task — a guard in
  `task-complete`, or does the standing task simply never call it (reset instead)?
- Single generalized reset script vs. per-task scripts; where it lives.
- Exact relationship/boundary vs. BOTH other recurring mechanisms — the release
  orchestration two-slot alternation chain (REQ-PROC-035 SEC-05) and
  `feat_perpetuating_task_creation` (REQ-PROC-065-06) — so the three loop concepts are
  not conflated, and so this does not become a fourth incompatible mechanism. Decide
  whether the release chain could be re-expressed on the shared primitive or stays
  independent.

## Acceptance Criteria

- [ ] REQ-PROC-065-01 authored via `requ-explore` covering standing-task semantics and both recurrence modes
- [ ] `task-create` (modified via `claude-modify-skill`) can emit a standing task: permanent folder, reset-based lifecycle, standing frontmatter marker
- [ ] Reset-triggered mode supported (generalizes the TASK-PROC-046-16 pattern; no bespoke per-task reset logic required)
- [ ] Calendar-triggered mode supported and wired to the `not_before` primitive, sufficient for the monthly upgrade review (TASK-PROC-061-10)
- [ ] `task-complete` interaction documented so a standing task never terminalizes / proliferates folders
- [ ] All three existing recurring mechanisms surveyed (046-16 reset, release orchestration two-slot alternation REQ-PROC-035 SEC-05, perpetuating REQ-PROC-065-06); boundary/unification with each stated explicitly

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-065-04-01 | pending | Date-gate design; calendar recurrence consumes its `not_before` primitive (this task `after:` it) |
| `not_before` primitive **implementation** task | not yet created | Calendar mode needs the engine support; wire into `after:` once that impl task exists |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-065-04-01](../../feat_task_state_machine/tasks/2026-06-03_explore_design-not-before-date-gate-primitive/goal.md) | Predecessor — supplies the `not_before` primitive used by calendar-mode standing tasks |
| [TASK-PROC-061-10](../../../../ai_tool_management/dependency_lifecycle/tasks/2026-06-03_impl_migrate-monthly-review-to-local-standing-task/goal.md) | Consumer — creates the monthly upgrade-review standing task this capability must support |
| [TASK-PROC-046-16](../../../../coding_standards/code_quality/tasks/2026-05-14_impl_apply-quality-rule-proposals-loop/goal.md) | Exemplar — the hand-rolled permanent loop-task this task generalizes |
| REQ-PROC-035 SEC-05 / `scripts/tasks/create_orchestration_task.py` | Prior art — the release orchestration two-slot alternation chain that creates coding tasks; must be reconciled with the shared primitive |

## Notes

The `feat_perpetuating_task_creation` feature (REQ-PROC-065-06) is the *work-discovery*
loop variant (spawns new follow-up folders). This task is the *same-folder reuse* variant.
Both belong to the task-lifecycle epic; keep their boundary explicit so future agents do
not conflate "standing/loop-task" with "perpetuating task."
