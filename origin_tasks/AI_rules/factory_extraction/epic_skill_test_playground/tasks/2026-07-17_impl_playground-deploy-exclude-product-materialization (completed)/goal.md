---
task_id: TASK-PROC-068-33
type: impl
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-QUALITY
impact: 3
impact_reason: I3-QUALITY
status: completed
effort: XS
created: 2026-07-17
started: 2026-07-18
completed: 2026-07-18
session_completed_at: 2026-07-17T22:24:10Z
expected_tool_calls: 12
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-11]
  sections: []
egp:
  - { ac: AC-11, archetype: F, referent: "a real build/maintain run observed to derive the harness layers in an isolated deployed copy and deposit the registry-classified product-definition artifacts into test_harness_app/, retaining them; and to retain its own factory-runtime provenance as project data" }
consequence: MEDIUM
scope_description: "Add requirements_user_needs/product_materialization to deploy.py _SUBFOLDER_EXCLUDES so the transient factory deploy does not clobber the harness's own materialization provenance (AC-11 reword tail)."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: edddd25f
  file: ../../requirements.md
session_id: 1c778277-6722-44dc-a820-86fa86b83f1a
session_account: gmail2
---
# Goal: Playground deploy — exclude product_materialization so harness retains its own provenance

## Objective

Add `requirements_user_needs/product_materialization` to `_SUBFOLDER_EXCLUDES` in
`scripts/playground/deploy.py` so the transient factory deploy does **not** overwrite the harness's own
materialization provenance — realizing the AC-11 reword's tail: the harness retains its own
factory-runtime provenance (the ideation index and ledger backing a derived decision) grounding its
product definition, as project data of the standalone harness.

This is the trivial fix surfaced during the closed exploration (TASK-PROC-068-28 protocol,
§"Follow-on IMPL tasks" #3).

## Requirements Summary

Covers REQ-PROC-068 **AC-11** (reworded tail — harness retains its own factory-runtime provenance as
project data; transient deployed factory machinery absent from `test_harness_app/`).

For complete requirements at task creation time:
```
git show edddd25f:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```
Current requirements: ../../requirements.md

## Scope

### In Scope
- `scripts/playground/deploy.py` (`_SUBFOLDER_EXCLUDES`, ~line 127): add the
  `requirements_user_needs/product_materialization` subfolder to the exclude set.

### Out of Scope
- The git-persistence mechanism (AC-20) — sibling tasks
  `persistent-harness-git-restore-persist-bundle` / `-harvest-compaction`.
- Any broader harvest-scope provenance change (068-26 `_05` materialization-provenance-harvest) —
  separate concern.

## Acceptance Criteria

- [x] AC-11 — EGP: F (a real build/maintain run observed to derive the harness layers in an isolated deployed copy and deposit the registry-classified product-definition artifacts into test_harness_app/, retaining them; and to retain its own factory-runtime provenance as project data); consequence: MEDIUM

## Verification (folded into the sibling verify task)

Verified by `verify-persistent-harness-git`: a real build/maintain run observed to retain the harness's
own product_materialization provenance in `test_harness_app/` (not clobbered by the deploy).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | Independent — does not touch `build.py`'s COMPLETE/harvest branch (after: []) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-28](../2026-07-17_explore_persistent-harness-git%20%28completed%29/goal.md) | Source — surfaced this trivial fix during the closed exploration |

## Notes

- **Encapsulation (AC-21)**: this exclude lives inside the playground deploy mechanism (`deploy.py`) —
  no other factory mechanism special-cases the harness.
- Route the `deploy.py` edit via `claude-write-script`; run `scripts/quality/check_python_gates.sh`
  before completing (REQ-PROC-051).
