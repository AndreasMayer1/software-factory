---
task_id: TASK-PROC-068-21
type: impl
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-07-09
completed: 2026-07-09
session_completed_at: 2026-07-09T14:11:20Z
effort: L
created: 2026-07-09
expected_tool_calls: 45
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-13, AC-14, AC-17]
  sections: []
egp:
  - { ac: AC-13, archetype: F, referent: "a real build/maintain run observed to create its isolated deployed copy at the configured out-of-project location as its own git repository, not in an OS temp directory" }
  - { ac: AC-14, archetype: F, referent: "a real interrupted build/maintain run observed to preserve the isolated copy and perform no harvest, and a real completed run observed to harvest then discard" }
  - { ac: AC-17, not_applicable: true, reason: "checkable by inspecting that the resumable-run machinery is parameterized by an injected completion predicate rather than hard-coded to layer-derivation" }
consequence: HIGH
scope_description: "build.py resumable wrapper: parent-dir git-init workspace (AC-13), completion-gated harvest with preserve-by-default (AC-14), and an injected completion-predicate seam (AC-17)."
release_description: ""
opus_recommended: true   # reason: cross-cutting invariant — build.py, workspace.py, and worktree_root.py must change with awareness of all three at once; AC-14 is HIGH-consequence
writes_requirements: false
requirements_version:
  commit: 3a51041e
  file: ../requirements.md
session_id: d5b03ce0-cddb-4f2a-9a79-9429f3ad2571
session_account: gmail
---
# Goal: build.py resumable wrapper — parent-dir git-init workspace, completion-gated harvest, completion-predicate seam

## Objective

Change `scripts/playground/build.py::run_build_mode` so the isolated deployed copy is created via the EXISTING
parent-dir git-init workspace convention (`scripts/playground/workspace.py::create_workspace` +
`init_workspace_git`, out-of-project root resolved by `scripts/dev_env/worktree_root.py` +
`worktree.config.json`) instead of `tempfile.mkdtemp()` [AC-13]. Gate the harvest+discard: `harvest_authored` +
workspace teardown run ONLY when an explicit completion predicate over the copy returns complete AND
`result.succeeded` AND `result.reason == 'exited'`; on ANY non-complete termination preserve the copy and skip
harvest entirely — preserve-by-default, discard-only-on-verified-complete, skip-harvest-on-incomplete [AC-14].
Write the registry status=running + durable copy path BEFORE launch (a tree-wide limit can kill the wrapper
before the gate — ADV-synthesize-gate-02). Parameterize the wrapper by an INJECTED completion predicate so
layer-derivation (ChainState complete) is one instance, not the hard-coded case [AC-17]. Preserve harvest
snapshot-diff scoping (REQ-PROC-068-19) and never git-reset (C1).

FIRST PHASE: read
`../../tasks/2026-07-08_explore_build-mode-resumability/plans_and_protocols/2026-07-09_006_synthesis_v2.md`
§SP-1/§SP-3 for design fidelity; AC text is authoritative.

AC-14 is HIGH-consequence (archetype F) — its verification (folded into the next task, TASK-PROC-068-22) must
use a subject-independent oracle: a real interrupted run observed to preserve+skip, and a real completed run
observed to harvest+discard (real-artifact worktree diff, not `f(x)==x`).

## Requirements Summary

REQ-PROC-068 (Skill-Test Playground) AC-13, AC-14, AC-17 — build-mode resumability: durable out-of-project
git-backed copy, completion-gated harvest, and an injected-completion-predicate seam. Design source
(developer-approved SOL-02): `2026-07-09_006_synthesis_v2.md`.

For complete requirements at task creation time:
```
git show 3a51041e:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `scripts/playground/build.py::run_build_mode` — replace `tempfile.mkdtemp()` with the parent-dir git-init
  workspace convention (`workspace.py::create_workspace` + `init_workspace_git`, out-of-project root via
  `worktree_root.py` + `worktree.config.json`).
- A completion-gate around harvest+discard: harvest only on verified complete + succeeded + `reason=='exited'`;
  preserve + skip harvest on any other termination.
- Writing run-registry `status=running` + durable copy path BEFORE launch.
- An injected completion-predicate parameter so the gate is not hard-coded to layer-derivation's ChainState.

### Out of Scope
- The run registry's cold-session re-attach/resume behavior and the `playground-build-resume` skill — T2
  (TASK-PROC-068-22).
- End-to-end verification across AC-13..AC-17 — folded into T2.
- REQ-PROC-071-06 AC-08 real-limit derivation-resumability proof — T3.

## Acceptance Criteria

- [x] AC-13 — EGP: F (a real build/maintain run observed to create its isolated deployed copy at the configured out-of-project location as its own git repository, not in an OS temp directory); consequence: MEDIUM
- [x] AC-14 — EGP: F (a real interrupted build/maintain run observed to preserve the isolated copy and perform no harvest, and a real completed run observed to harvest then discard); consequence: HIGH
- [x] AC-17 — EGP: not-bearing (checkable by inspecting that the resumable-run machinery is parameterized by an injected completion predicate rather than hard-coded to layer-derivation)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Created via the `2026-07-09_008_task_creation_plan.md` (plan-driven mode, automated session — confirmations
auto-accepted per `CLAUDE_AUTOMATED_MODE=1`). This is task 1 of a 3-task sequential chain: T1 (this task, ID
TASK-PROC-068-21) → T2 (TASK-PROC-068-22, `after: [TASK-PROC-068-21]`) → T3 (`after: [TASK-PROC-068-21,
TASK-PROC-068-22]`).
