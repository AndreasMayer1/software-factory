---
task_id: TASK-PROC-068-30
type: impl
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-07-15
started: 2026-07-18
completed: 2026-07-18
session_completed_at: 2026-07-18T10:22:07Z
expected_tool_calls: 55
skill_chain_depth: 4
synthesis_dependent: true
synthesis_justification: "Must hold the build-mode run-classification (AC-18/19), the plan-time harvestability pre-flight reusing the mechanism's span/disposition/oracle, and the resume-revalidated stamp together so a doomed spec fails loudly before a deployed run without weakening the real-abandonment guarantee."
after: [TASK-PROC-071-06-10]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-18, AC-19, AC-22]
  sections: []
egp:
  - { ac: AC-18, archetype: F, referent: "a real build/maintain run's observed termination mode + acceptance-oracle result + presence/absence of a recorded blocker artifact + per-unit structural degeneracy, checked against the outcome the playground classifies and reports for it" }
  - { ac: AC-19, archetype: F, referent: "a real run with no injected acceptance oracle (must not harvest/report success), a real run with a degenerate span observed counted vacuous-complete by the oracle, and a real run whose child holds an in-flight background agent at -p return (must not be a clean complete exit)" }
  - { ac: AC-22, archetype: F, referent: "a real doomed spec (incl. an all-degenerate spec) observed to fail the pre-flight at plan time and consume no deployed run, and a real resume observed to re-validate the pre-flight verdict before reaching harvest, checked against what the deployed run would actually classify" }
consequence: HIGH
scope_description: "Realize the vacuous-aware build-mode run classification (AC-18/19) and the plan-time harvestability pre-flight with a resume-revalidated stamp (AC-22), reusing the mechanism's span resolution + vacuous-complete disposition + injected oracle predicate, and reusing the Task-1 linter as the pre-flight check. Rejects all-degenerate/doomed specs before any deployed run."
release_description: ""
opus_recommended: true   # reason: HIGH-consequence AC-18/19/22 at the harvest seam + synthesis across classification/pre-flight/resume held at once
writes_requirements: false
requirements_version:
  commit: c2d94b7c
  file: ../../requirements.md
session_id: 8643b646-1927-4d5f-bbbe-397915bc9775
session_account: web
---
# Goal: Harvestability pre-flight + vacuous-aware run classification (playground build-mode)

## Objective

Implement the playground half of the degenerate-span harvest fix (developer-approved SOL-01,
IDEATION-023): make the build-mode run classification **vacuous-aware** (a degenerate no-op span is never
"abandoned"/blamed) and add a **plan-time harvestability pre-flight** that turns "plan-success ≠
harvestable" into a loud plan-time failure before any deployed run is spent — reusing the vacuous-complete
disposition and spec-authoring linter delivered by TASK-PROC-071-06-10.

## Requirements Summary

Covers REQ-PROC-068 **AC-18** (abandoned = real-authoring under-finish only), **AC-19** ("finished" =
real spans authored ∧ degenerate spans vacuous-complete; oracle counts vacuous-complete), **AC-22**
(harvestability pre-flight, resume-revalidated stamp, all-degenerate rejection). See `../../requirements.md`.

For complete requirements at task creation time:
```
git show c2d94b7c:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```
Current requirements: ../../requirements.md

## Scope

### In Scope
- `scripts/playground/build.py`: vacuous-aware run classification — **abandoned** only when a unit with
  real authoring pairs is left non-terminal; **complete** when every real span is at an authored terminal
  and every degenerate span is vacuous-complete (the oracle from TASK-PROC-071-06-10 already counts
  vacuous-complete). AC-19's no-oracle / background-agent-in-flight guarantees unchanged.
- A shared **planner-oracle pre-flight module**: reuse `resolve_spans` + per-span disposition typing +
  the injected acceptance-oracle predicate to predict, over the best-case terminal, whether the spec can
  EVER be certified complete. Fail a doomed spec at plan time with a **distinct doomed-spec exit code**,
  consuming no deployed run.
- **Doomed classes** rejected at plan time: an all-degenerate spec (every span a zero-pair no-op — R1);
  a spec with a real span that can never reach an authored terminal (e.g. no authoring skill registered
  for its pair — ADV-sg-02).
- Persist the pre-flight verdict as a **harvestable stamp re-validated on `-start` AND every resume**
  (ADV-sg / ADV-06) — no start or resume path reaches harvest without a current positive pre-flight.
- Reuse TASK-PROC-071-06-10's teaching linter AS the pre-flight check (author-time == plan-time).
- Retire the 068-26 / 068-12 Option-A per-task workaround (hand-certifying span-0 to DONE) — document its
  removal once this and TASK-PROC-071-06-10 land.

### Out of Scope
- The vacuous-complete disposition, oracle DONE∪VACUOUS, persisted-state/test migration, and the
  derive-not-author authoring surface — delivered by TASK-PROC-071-06-10 (this task depends on it).
- The materialization-provenance-harvest gap (068-26 `_05`) — separate concern.

## Acceptance Criteria

- [x] AC-18 — EGP: F (a real run's termination mode + oracle result + recorded-blocker presence + per-unit structural degeneracy, checked against the playground classification); consequence: HIGH
- [x] AC-19 — EGP: F (a real run with no oracle; a real run with a degenerate span counted vacuous-complete; a real run with an in-flight background agent at -p return); consequence: HIGH
- [x] AC-22 — EGP: F (a real doomed/all-degenerate spec observed to fail pre-flight and consume no deployed run, and a real resume observed to re-validate the verdict before harvest); consequence: HIGH

## Verification (folded in — < 3 impl tasks per requirement)

EGP-bearing ACs; oracle-independence (referent = real run behaviour, NOT the predictor's own output):
a real doomed spec (incl. all-degenerate) observed to fail the pre-flight at plan time and consume no
deployed run; a real resume observed to re-validate the stamp before harvest; the predicted verdict
checked against the ACTUAL deployed-run classification. consequence: HIGH (gate-computed floor, never
self-rated).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-071-06-10 | pending | Delivers the vacuous-complete disposition, oracle DONE∪VACUOUS, and the linter this pre-flight reuses |
| TASK-PROC-068-27 | in_progress | Design + requirement grounding (this task realizes its SOL-01) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-071-06-10](../../../epic_layer_derivation/feat_backfill_orchestration/tasks/2026-07-15_impl_vacuous-span-disposition-and-spec-authoring/goal.md) | Predecessor — delivers the disposition + linter this task reuses |
| [TASK-PROC-068-27](../2026-07-14_explore_fix-degenerate-span-harvest-and-spec-authoring/goal.md) | Design task that grounded AC-18/19/22; concept in its `2026-07-15_004_synthesis.md` |

## Notes

FIRST PHASE — read the concept for design fidelity: `../2026-07-14_explore_fix-degenerate-span-harvest-and-spec-authoring/plans_and_protocols/2026-07-15_004_synthesis.md` §SP-2/§SP-3. The AC text is AUTHORITATIVE; the concept grounds the HOW only where the AC is silent; on conflict the AC wins — record the divergence.

Gate/mechanism discipline: route `scripts/**` edits via `claude-write-script`; skill edits via `claude-modify-skill`. Do NOT hand-edit quality gates.
