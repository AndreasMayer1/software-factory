---
task_id: TASK-PROC-068-29
type: explore
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-BLOCKING
impact: 3
impact_reason: I3-QUALITY
status: completed
effort: S
created: 2026-07-17
started: 2026-07-17
completed: 2026-07-17
session_completed_at: 2026-07-17T21:37:30Z
expected_tool_calls: 20
skill_chain_depth: 1
after: [TASK-PROC-068-27]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Decompose REQ-PROC-068 AC-20 (persistent harness git), AC-21 (encapsulation invariant), and the reworded AC-11 into impl tasks via task-derive-from-requ; design already fixed by TASK-PROC-068-28."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: c2d94b7c
  file: ../requirements.md
session_id: e36f67b3-2b12-4c87-9092-98b02b08e73b
session_account: gmail
---
# Goal: Derive Impl Tasks for Persistent Harness Git (AC-20, AC-21, reworded AC-11)

## Objective

Derive the implementation tasks that realize REQ-PROC-068 AC-20 (persistent harness git), AC-21
(encapsulation invariant), and the reworded AC-11, by running the `task-derive-from-requ` skill. The
design is already fixed — see the TASK-PROC-068-28 protocol at
`requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-07-17_explore_persistent-harness-git (completed)/plans_and_protocols/2026-07-17_01_protocol_persistent-harness-git-design.md`.
Expected impl tasks: (1) `workspace.py` maintenance-mode git restore/persist via a git bundle replacing
the fresh `git init`; (2) harvest compaction (preserve every referenced commit + squash unreferenced
intermediate commits; prior runs' commits immutable); (3) trivial `deploy.py` `_SUBFOLDER_EXCLUDES` add
of `requirements_user_needs/product_materialization`. Test mode keeps the throwaway `git init` — do not
change it.

## Background

TASK-PROC-068-28 (completed) designed the persistent-harness-git mechanism and landed the corresponding
requirement edits (AC-20, AC-21, reworded AC-11) in REQ-PROC-068. This task does not re-design anything —
it is a pure decomposition step: run `task-derive-from-requ` against the now-fixed requirement to emit
the concrete impl task(s) that build the mechanism.

This task is sequenced `after: [TASK-PROC-068-27]` because TASK-PROC-068-27 is itself an EXPLORE/design
task that will emit its own impl task(s) touching `build.py`'s COMPLETE/harvest branch (the degenerate-
span harvest fix). The persistent-git harvest-compaction impl task this task emits also touches that same
COMPLETE/harvest branch. Sequencing this task after TASK-PROC-068-27 (rather than after its as-yet-
unminted impl children) ensures the 068-27 impl task(s) exist in the task graph by the time this task
runs and derives its own `after:` chain — see Acceptance Criteria below.

For complete requirements at task creation time:
```
git show c2d94b7c:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Run `task-derive-from-requ` scoped to AC-20, AC-21, and AC-11 (reworded) of REQ-PROC-068. Do not
re-open the design — treat the TASK-PROC-068-28 protocol as authoritative for what the impl tasks must
build. Focus effort on correct decomposition, sizing, and dependency wiring (especially the `build.py`
COMPLETE-branch concurrency constraint below), not on redesigning the mechanism.

## Execution Model

`task-derive-from-requ` owns the decomposition mechanics (coverage matrix, verification task, sizing).
This task's job is to invoke it correctly-scoped and verify its output satisfies the Acceptance Criteria.

## Output

Impl task(s) created under this requirement's `tasks/` folder, each appended to
`.claude/task_ordering_priority_override.txt` per the RECURSIVE OVERRIDE RULE (see Notes), with correct
`after:` wiring so the shared `build.py` COMPLETE/harvest branch is never edited concurrently by two
in-flight tasks.

## Acceptance Criteria

- [x] Impl tasks emitted via `task-derive-from-requ` for AC-20, AC-21, and the reworded AC-11.
      (TASK-PROC-068-31 restore/persist, -32 compaction, -33 deploy exclude, -34 verify.)
- [x] Every emitted impl task (and any children) is appended to
      `.claude/task_ordering_priority_override.txt` on creation (RECURSIVE OVERRIDE RULE).
      (068-31/32/33/34 appended.)
- [x] Every emitted impl task that edits `build.py`'s COMPLETE/harvest branch carries an `after:`
      referencing TASK-PROC-068-27's build.py-mechanism impl task(s) — NOT merely the 068-27 explore
      task — so the shared `build.py` COMPLETE branch is never edited concurrently. (Those 068-27 impl
      task IDs will exist by the time this task runs.)
      (068-31 after [068-30]; 068-32 after [068-30, 068-31]. 068-30 is 068-27's build.py impl task.)
- [x] The `deploy.py` exclude impl task may be independent (`after: []`) since it doesn't touch the
      COMPLETE branch. (068-33 after: [].)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-27 | pending | Design/impl chain for the degenerate-span harvest fix; also touches `build.py`'s COMPLETE branch — must land (its impl task IDs must exist) before this task derives its own `after:` wiring |
| TASK-PROC-068-28 | completed | Fixed the persistent-harness-git design this task decomposes into impl tasks |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-27](../2026-07-14_explore_fix-degenerate-span-harvest-and-spec-authoring/goal.md) | Predecessor — its impl task(s) also touch `build.py`'s COMPLETE/harvest branch; this task's emitted impl tasks must sequence after them |
| [TASK-PROC-068-28](../2026-07-17_explore_persistent-harness-git%20%28completed%29/goal.md) | Source of the fixed design (protocol referenced in the Objective) that this task decomposes |

## Notes

- Coordinator/derivation task, covers-empty process task (no `target_package`) — surfaces only via the
  priority override.
- RECURSIVE OVERRIDE RULE: every impl task this task emits (and their children) MUST be appended to
  `.claude/task_ordering_priority_override.txt` on creation.
- Do NOT run `task-derive-from-requ` at task-creation time and do NOT create the impl tasks now — this
  task only schedules that work for later. Leave `status: pending` so it is picked up in order after
  TASK-PROC-068-27.
