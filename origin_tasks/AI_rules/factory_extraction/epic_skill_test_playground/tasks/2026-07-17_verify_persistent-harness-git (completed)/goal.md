---
task_id: TASK-PROC-068-34
type: verify
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-07-18
session_completed_at: 2026-07-18T19:52:34Z
effort: M
created: 2026-07-17
started: 2026-07-18
expected_tool_calls: 30
skill_chain_depth: 2
after: [TASK-PROC-068-31, TASK-PROC-068-32, TASK-PROC-068-33]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-11, AC-20, AC-21]
  sections: []
egp:
  - { ac: AC-20, archetype: F, referent: "a real sequence of maintenance (build/maintain) runs observed to keep earlier runs' referenced commits reachable in the harness git after restore-from-persisted-history" }
  - { ac: AC-21, archetype: X, referent: "the absence of harness-specific handling across all non-playground factory mechanisms" }
  - { ac: AC-11, archetype: F, referent: "a real build/maintain run observed to derive the harness layers in an isolated deployed copy and deposit the registry-classified product-definition artifacts into test_harness_app/, retaining them; and to retain its own factory-runtime provenance as project data" }
consequence: HIGH
scope_description: "Verify the persistent harness git mechanism end-to-end: referenced commits stay reachable across maintenance runs (AC-20), no non-playground mechanism special-cases the harness (AC-21), the harness retains its own factory-runtime provenance as project data (AC-11)."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: edddd25f
  file: ../../requirements.md
session_id: 69804c91-9f5e-4c63-af04-e7983ca11aeb
session_account: gmail
session_last_run: 2026-07-18T19:15:52.955650+00:00
---
# Goal: Verify persistent harness git (AC-20, AC-21, AC-11)

## Objective

Verify, end-to-end against real build/maintain behaviour, that the persistent-harness-git mechanism
delivered by TASK-PROC-068-31/32/33 satisfies REQ-PROC-068 AC-20, AC-21, and the reworded AC-11.

## Requirements Summary

Covers REQ-PROC-068 **AC-20** (persistent harness git — restore/persist + compaction), **AC-21**
(encapsulation invariant), **AC-11** (harness retains its own factory-runtime provenance as project data).

For complete requirements at task creation time:
```
git show edddd25f:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```
Current requirements: ../../requirements.md

## Scope

### In Scope
- Observe a **real sequence of ≥2 maintenance (build/maintain) runs** and verify the three ACs below.

### Out of Scope
- Implementing the mechanism (done by TASK-PROC-068-31/32/33).
- Test-mode behaviour (AC-07 clean-reset) — unchanged by this work.

## Oracle-Independence Declaration (REQ-PROC-044 §4.3 / REQ-PROC-058 AC-23)

Expected values come from **real deploy-run-harvest behaviour**, NOT from the persist/compaction code's
own output (no `f(x)==x` change-detector). Each check exercises the load-bearing operation, not a stub.

- **AC-20 [F, HIGH]** — referent: a real ≥2-run maintenance sequence. A provenance commit a first run
  records (a materialization artifact's provenance commit, a task's pinned requirements version) MUST
  still be reachable with a **stable hash** in a later run's git after restore-from-persisted-bundle.
  Metamorphic relation (F allowed): compaction preserves referenced-commit reachability across runs;
  unreferenced intermediates may be squashed; prior runs' persisted commits are byte-stable (immutable).
- **AC-11 [F, MEDIUM]** — referent: a real build/maintain run. The harness retains its own
  factory-runtime provenance (ideation index + ledger backing a derived decision) as project data in
  `test_harness_app/` after harvest, while the transient deployed factory machinery (skills, scripts,
  registries) is absent; product_materialization not clobbered by the deploy.
- **AC-21 [X, MEDIUM]** — referent: the absence of harness-specific handling across all non-playground
  factory mechanisms. Coherence/absence check: grep/diff over all NON-playground factory code (skills,
  scripts outside `scripts/playground/`, quality gates, orchestration) to confirm NONE carries
  harness-specific handling — every other mechanism operates on the harness as on any real project.
  Real-artifact absence check, not self-derived.

consequence: **HIGH** = gate-computed governing floor (max over covered ACs: AC-20 HIGH), never self-rated.

## Acceptance Criteria

- [x] AC-20 — EGP: F (a real sequence of maintenance runs observed to keep earlier runs' referenced commits reachable in the harness git after restore-from-persisted-history); consequence: HIGH — VERIFIED: 2 real runs, `plans_and_protocols/2026-07-18_04_protocol_verification-complete.md`
- [x] AC-21 — EGP: X (the absence of harness-specific handling across all non-playground factory mechanisms); consequence: MEDIUM — VERIFIED: static grep, `plans_and_protocols/2026-07-18_02_protocol_run1-and-finding.md`
- [x] AC-11 — EGP: F (a real build/maintain run observed to derive in an isolated deployed copy and deposit registry-classified product-definition artifacts into test_harness_app/, retaining them; and to retain its own factory-runtime provenance as project data); consequence: MEDIUM — VERIFIED: `plans_and_protocols/2026-07-18_04_protocol_verification-complete.md`

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-31 | pending | Restore/persist bundle mechanism (AC-20) |
| TASK-PROC-068-32 | pending | Harvest compaction (AC-20) |
| TASK-PROC-068-33 | pending | deploy.py exclude (AC-11) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-31](../2026-07-17_impl_persistent-harness-git-restore-persist-bundle/goal.md) | Verifies its restore/persist mechanism |
| [TASK-PROC-068-32](../2026-07-17_impl_persistent-harness-git-harvest-compaction/goal.md) | Verifies its compaction policy |
| [TASK-PROC-068-33](../2026-07-17_impl_playground-deploy-exclude-product-materialization/goal.md) | Verifies its provenance-retention exclude |

## Notes

- Runs after all three impl tasks complete (`after:` chain). Route any `scripts/**` helper via
  `claude-write-script`; do NOT hand-edit quality gates.
