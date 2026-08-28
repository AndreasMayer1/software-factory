---
task_id: TASK-PROC-068-31
type: impl
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-07-17
started: 2026-07-18
completed: 2026-07-18
session_completed_at: 2026-07-18T13:30:47Z
expected_tool_calls: 35
skill_chain_depth: 2
after: [TASK-PROC-068-30]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-20, AC-21]
  sections: []
egp:
  - { ac: AC-20, archetype: F, referent: "a real sequence of maintenance (build/maintain) runs observed to keep earlier runs' referenced commits reachable in the harness git after restore-from-persisted-history" }
  - { ac: AC-21, archetype: X, referent: "the absence of harness-specific handling across all non-playground factory mechanisms" }
consequence: HIGH
scope_description: "Maintenance-mode persistent harness git via a git bundle: restore-on-deploy (bundle restore replaces fresh git init) + persist-on-harvest (export advanced history back to the persisted bundle). Test mode unchanged."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: edddd25f
  file: ../../requirements.md
session_id: 202535c9-d3d7-47af-a5f0-d9e787274937
session_account: gmail2
---
# Goal: Persistent harness git — restore-on-deploy + persist-on-harvest (maintenance mode)

## Objective

Replace the fresh `git init` baseline for **maintenance-mode** (`build`/`maintain`) playground runs with
a **persistent git bundle** round-trip, so a commit reference a run records (a materialization artifact's
provenance commit, a task's pinned requirements version) stays reachable in every later run.

Two halves:
1. **Restore-on-deploy** — a maintenance-mode run's deployed copy initializes its git repository by
   restoring from the harness's **persisted bundle** (kept with the harness in the container project)
   rather than a fresh empty repository.
2. **Persist-on-harvest** — on harvest, the copy's advanced history is exported back to the bundle and
   persisted with the harness in the container project.

## Requirements Summary

Covers REQ-PROC-068 **AC-20** (restore-on-deploy / persist-on-harvest so referenced commits stay
reachable across runs; test-mode excluded) and **AC-21** (encapsulation invariant — this handling lives
entirely inside the playground deploy/harvest mechanism). The design is **fixed** — do NOT re-open it.

For complete requirements at task creation time:
```
git show edddd25f:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```
Current requirements: ../../requirements.md

Fixed design (authoritative): `../2026-07-17_explore_persistent-harness-git (completed)/plans_and_protocols/2026-07-17_01_protocol_persistent-harness-git-design.md`

## Scope

### In Scope
- `scripts/playground/workspace.py` `init_workspace_git()` (currently `git init -q` at ~line 136) and the
  maintenance-mode deploy path `scripts/playground/build.py` Step 3 (~line 570): add a
  **restore-from-persisted-bundle** variant used for maintenance-mode runs.
- `scripts/playground/build.py` COMPLETE/harvest branch (`_gate_harvest` ~line 666 / `harvest_authored`
  ~line 393): on harvest, **export** the deployed copy's advanced history to a git bundle and persist it
  with the harness in the container project.
- The persisted-bundle storage location + naming convention (with the harness in the container project,
  never an OS temp dir; consistent with AC-13's out-of-project copy convention).

### Out of Scope
- **Harvest compaction** (preserve-referenced / squash-unreferenced / immutable-once-persisted) —
  delivered by the sibling task `persistent-harness-git-harvest-compaction` (this task's successor).
- **TEST mode** (`scripts/playground/run_skeleton.py`): keeps the throwaway `git init` and clean-reset
  contract (AC-07). Do **NOT** touch it — a test-mode run carries no persisted history.
- Any provenance-contract change (REQ-PROC-074/075): the backward-pointing-commit-reference shape is
  unchanged; only the persistence mechanism underneath the harness git changes.

## Acceptance Criteria

- [x] AC-20 — EGP: F (a real sequence of maintenance runs observed to keep earlier runs' referenced commits reachable in the harness git after restore-from-persisted-history); consequence: HIGH
- [x] AC-21 — EGP: X (the absence of harness-specific handling across all non-playground factory mechanisms); consequence: MEDIUM

## Verification (folded into the sibling verify task)

Verified end-to-end by `verify-persistent-harness-git` (covers AC-20/AC-21/AC-11) — a real ≥2-run
maintenance sequence observed to keep an earlier run's referenced commit reachable (stable hash) after
restore. Oracle-independence: referent = real deploy-run-harvest behaviour, never the persist code's own
output.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-30 | pending | Edits `build.py`'s COMPLETE/harvest branch (vacuous-aware classification + pre-flight); this task also edits that branch (persist-on-harvest) → must not be concurrent |
| TASK-PROC-068-28 | completed | Fixed the persistent-harness-git design this task realizes |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-30](../2026-07-15_impl_harvestability-preflight-and-vacuous-classification/goal.md) | Predecessor — shares `build.py`'s COMPLETE/harvest branch; execute after it to avoid concurrent edits |
| [TASK-PROC-068-28](../2026-07-17_explore_persistent-harness-git%20%28completed%29/goal.md) | Source of the fixed design (protocol) |

## Notes

- **Encapsulation (AC-21)**: ALL persistent-git handling lives inside `scripts/playground/`. No other
  factory mechanism (skills, scripts outside the playground, quality gates, orchestration) may grow
  harness-specific handling — every other mechanism operates on the harness as on any real project. This
  extends the same de-hardcoding precedent landed at commit 969e3c70.
- Route every `scripts/**` edit via the `claude-write-script` skill; run `scripts/quality/check_python_gates.sh`
  before declaring complete (REQ-PROC-051). Do NOT hand-edit quality gates.
- Backward-reference constraint (why persist, not rewrite): a provenance field always points *backward*
  to an already-existing commit, so a referenced commit's hash must stay stable forever — the compaction
  successor enforces this; this task must not rewrite already-persisted history.
