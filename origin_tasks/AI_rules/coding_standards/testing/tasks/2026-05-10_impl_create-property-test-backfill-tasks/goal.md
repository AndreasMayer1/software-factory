---
task_id: TASK-PROC-002-05
type: impl
parent_requirement: REQ-PROC-002
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-PROC
status: completed
effort: S
created: 2026-05-10
started: 2026-05-18
completed: 2026-05-18
session_completed_at: 2026-05-18T21:43:40Z
after: [TASK-PROC-002-02, TASK-PROC-002-04]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03]
  sections: []
scope_description: "Read the value-objects inventory produced by TASK-PROC-002-04 and use the task-create skill to schedule one impl task per type-and-category gap, each scoped to add a glados property test exercising the relevant invariant."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: 4be59bec-fc30-48cf-b592-7a379da24d37
session_account: gmail
---
# Goal: Create property-test backfill tasks from value-objects inventory

## Objective

TASK-PROC-002-04 produces an inventory of value objects with non-trivial invariants and the categories of property tests they need. This task converts the gap list into scheduled work: one impl task per type-and-category gap (or per logical batch), each created via `task-create` so the work appears in the queue alongside other ready work.

## Requirements Summary

REQ-PROC-002 AC-03 (every value object with non-trivial invariants has at least one `glados` property test exercising the relevant invariant). The inventory (TASK-PROC-002-04 output) is the input.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Read `plans_and_protocols/value_objects_inventory.md` from TASK-PROC-002-04.
- For each row representing a (type, invariant-category) gap:
  - Decide batching: one task per type if it has many uncovered categories; one task per category across types if a category is uniform across many types (e.g. round-trip serialization on five DTOs).
  - Invoke `task-create` to allocate IDs under the type's owning requirement (domain types live under feature requirements; cross-cutting domain primitives may belong under a shared requirement), with type `impl`.
  - Each created task's scope: "Add `glados` property test for [type] exercising [invariant category]."
  - Set `after:` to `[TASK-PROC-002-02]` (glados must be installed) and `[TASK-PROC-002-04]` (this inventory).
- Surface "implicit-invariant" types from the inventory: types whose invariants need codification before property tests can be written. Create a separate task per such type whose scope is "codify invariants for [type] and add property tests." These have higher effort than vanilla property-test additions.
- Record created task IDs in `plans_and_protocols/created_tasks.md`.
- If the inventory contains zero gaps: no-op, record fact, complete.

### Out of Scope

- Writing the property tests. Each created task does that.
- Adding `glados` to the project — TASK-PROC-002-02 owns that; this task assumes it has landed.
- Property tests for non-domain types (data models, presentation models). Out of scope per AC-03.

## Acceptance Criteria

- [ ] Every (type, category) gap in the inventory has a corresponding scheduled task (or is bundled into a batch task with rationale).
- [ ] `plans_and_protocols/created_tasks.md` lists every created task ID with one-line descriptions.
- [ ] Implicit-invariant types are flagged as separate, higher-effort tasks rather than bundled with vanilla property-test additions.
- [ ] Each created task names the specific generator (`any.intInRange(...)`, `any.string`, etc.) appropriate for the type.
- [ ] If inventory contained zero gaps, that is recorded explicitly.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-002-02 | pending | glados must be available as a dependency |
| TASK-PROC-002-04 | pending | Provides the inventory this task acts on |

## Notes

For implicit-invariant types, codifying the invariant is itself a design decision (e.g. "is mood score really bounded to ±5, or is that a UI affordance only?"). The task that codifies the invariant should pause for user input if the answer is non-obvious — do not invent invariants the persona has not committed to.

After this task lands a wave of property tests, mutation testing (REQ-PROC-002 AC-02) will reveal whether the property generators span the input space adequately. Narrow generators that miss boundaries will show up as surviving mutants — a useful feedback signal.
