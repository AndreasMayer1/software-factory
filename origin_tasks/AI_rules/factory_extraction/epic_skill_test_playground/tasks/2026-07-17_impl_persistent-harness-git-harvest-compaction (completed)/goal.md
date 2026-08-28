---
task_id: TASK-PROC-068-32
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
session_completed_at: 2026-07-18T16:19:43Z
expected_tool_calls: 35
skill_chain_depth: 2
after: [TASK-PROC-068-30, TASK-PROC-068-31]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-20, AC-21]
  sections: []
egp:
  - { ac: AC-20, archetype: F, referent: "a real sequence of maintenance (build/maintain) runs observed to keep earlier runs' referenced commits reachable in the harness git after restore-from-persisted-history" }
  - { ac: AC-21, archetype: X, referent: "the absence of harness-specific handling across all non-playground factory mechanisms" }
consequence: HIGH
scope_description: "Harvest-time compaction of the persisted harness git bundle: preserve every referenced commit (stable hash), squash unreferenced intermediate commits, keep prior runs' persisted commits immutable."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: edddd25f
  file: ../../requirements.md
session_id: a6a7121a-4276-4d00-b537-fcd6b12d68a6
session_account: gmail2
session_last_run: 2026-07-18T16:08:51.501901+00:00
---
# Goal: Persistent harness git — harvest-time compaction (preserve-referenced / squash-unreferenced / immutable)

## Objective

Implement the **compaction policy** on the persist side of the harness git bundle (built by the
predecessor task `persistent-harness-git-restore-persist-bundle`), so the persisted history stays valid
forever while not growing unbounded:

- **Preserve every referenced commit** — any commit a harvested artifact's provenance field points to (a
  materialization artifact's provenance commit, a task's pinned requirements version) stays reachable with
  a **stable hash** in the persisted history forever.
- **Squash unreferenced intermediate commits** — commits between preserved points that nothing references
  may be compacted to bound bundle growth.
- **Prior runs' persisted commits are immutable** — a later run's compaction pass may only append +
  selectively squash the unreferenced gaps; it must never rewrite already-persisted commits.

## Requirements Summary

Covers REQ-PROC-068 **AC-20** (the compaction half: preserve-referenced, squash-unreferenced,
immutable-once-persisted) and **AC-21** (encapsulation invariant). Design is **fixed** — do NOT re-open.

For complete requirements at task creation time:
```
git show edddd25f:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```
Current requirements: ../../requirements.md

Fixed design (authoritative): `../2026-07-17_explore_persistent-harness-git (completed)/plans_and_protocols/2026-07-17_01_protocol_persistent-harness-git-design.md` (§Compaction policy, §The backward-reference constraint).

## Scope

### In Scope
- `scripts/playground/build.py` COMPLETE/harvest branch (`_gate_harvest` ~line 666 / `harvest_authored`
  ~line 393): before/at bundle export, compact the persisted history — determine the referenced-commit
  set (commits pointed to by harvested artifacts' provenance fields + tasks' pinned requirements
  versions), preserve those with stable hashes, squash only the unreferenced intermediate commits, and
  append without rewriting any commit persisted by a prior run.

### Out of Scope
- **Restore-on-deploy / persist-on-harvest bundle round-trip** — delivered by the predecessor task
  `persistent-harness-git-restore-persist-bundle` (this task builds on it).
- **TEST mode** (`run_skeleton.py`): carries no persisted history → nothing to compact. Do not touch.
- Any global squash-and-rewrite of history (rejected by the backward-reference constraint — it would
  break every existing backward reference by changing downstream commit hashes).

## Acceptance Criteria

- [x] AC-20 — EGP: F (a real sequence of maintenance runs observed to keep earlier runs' referenced commits reachable in the harness git after restore-from-persisted-history); consequence: HIGH
- [x] AC-21 — EGP: X (the absence of harness-specific handling across all non-playground factory mechanisms); consequence: MEDIUM

## Verification (folded into the sibling verify task)

Verified end-to-end by `verify-persistent-harness-git`: across a real ≥2-run maintenance sequence, a
referenced commit remains reachable (stable hash) after compaction while unreferenced intermediates are
squashed and prior-run commits are unchanged. Oracle-independence: referent = real run behaviour, never
the compaction code's own output. Metamorphic relation (F): compaction preserves referenced-commit
reachability and leaves prior-run persisted commits byte-stable.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-31 | pending | Delivers the restore/persist bundle mechanism this compaction operates on; shares the `build.py` harvest region → sequence after it |
| TASK-PROC-068-30 | pending | Also edits `build.py`'s COMPLETE/harvest branch → must not be concurrent |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-31](../2026-07-17_impl_persistent-harness-git-restore-persist-bundle/goal.md) | Predecessor — provides the persisted bundle this task compacts |
| [TASK-PROC-068-30](../2026-07-15_impl_harvestability-preflight-and-vacuous-classification/goal.md) | Shares `build.py`'s COMPLETE/harvest branch — sequence after to avoid concurrent edits |

## Notes

- **Encapsulation (AC-21)**: all compaction handling lives inside `scripts/playground/`; no other factory
  mechanism special-cases the harness.
- Route every `scripts/**` edit via `claude-write-script`; run `scripts/quality/check_python_gates.sh`
  before completing (REQ-PROC-051). Do NOT hand-edit quality gates.
- The immutability rule is the direct consequence of the backward-reference constraint — read the design
  protocol §"The backward-reference constraint" before implementing.
