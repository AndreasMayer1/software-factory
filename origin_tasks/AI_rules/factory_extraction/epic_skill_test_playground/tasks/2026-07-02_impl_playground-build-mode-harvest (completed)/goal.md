---
task_id: TASK-PROC-068-18
type: impl
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-07-03
session_completed_at: 2026-07-03T19:35:20Z
effort: M
created: 2026-07-02
started: 2026-07-03
expected_tool_calls: 45
skill_chain_depth: 2
after: [TASK-PROC-068-16, TASK-PROC-041-01-12, TASK-PROC-071-06-06]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-11]
  sections: []
egp:
  - { ac: AC-11, archetype: F, referent: "a real build/maintain run observed to derive the harness layers in an isolated deployed copy and deposit the registry-classified product-definition artifacts into test_harness_app/, retaining them" }
consequence: MEDIUM
scope_description: "Playground build/maintain run: derive the harness's own layers in an isolated deployed copy, then harvest the registry-classified product-definition artifacts back into test_harness_app/, retaining the derived layers (no reset), discarding the transient machinery."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: 18c7d415
  file: ../requirements.md
session_id: 9593db43-e956-4c9a-99a3-66b04cd1418f
session_account: web
---
# Goal: Playground build/maintain run + artifact harvest

## Objective

Add a **build/maintain** run mode to the playground (distinct from the test-and-reset mode, AC-07): it
derives the harness's **own** product-definition layers **inside an isolated deployed copy** of the whole
factory (so the derivation runs as its own project), then **harvests** the resulting product-definition
artifacts back into the persistent `test_harness_app/` tree, **retaining** the derived layers rather than
resetting them. This realizes **REQ-PROC-068 AC-11** and is how the harness's middle layers are actually
produced/maintained (consumed by TASK-PROC-068-12).

## Requirements Summary

**REQ-PROC-068 AC-11**: a build/maintain run derives in an isolated deployed copy and places the
product-definition artifacts — the categories the factory artifact registry
(`.factory/registry/artifacts.yaml`) designates as product definition: **user-needs** (personas/scenarios/
flows), **requirements**, **scribbles**, and **app source** — into `test_harness_app/`; the derived layers
persist (distinct from the test-mode reset); transient deployed machinery is absent from `test_harness_app/`.

For complete requirements at task creation time:
```
git show 18c7d415:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```
Current requirements: ../requirements.md

## Scope

### In Scope
- A build/maintain run path in `scripts/playground/` (alongside deploy/reset/launch) that:
  1. deploys the whole factory into an **isolated** copy (reuse T-B's whole-factory deploy + containment;
     the derivation must run as its own project);
  2. starts a contained session inside that copy that runs the derivation (which, per T-C/T-E, writes the
     copy's own layers and drives the copy's own autorun);
  3. **harvests** back: copy the artifacts whose `.factory/registry/artifacts.yaml` **category** is a
     product-definition category (`user-needs`, `requirements`, `scribble`, `source-code`) from the copy
     into `test_harness_app/`; leave factory-machinery categories (`factory-skills`, `scripts`,
     `automation`, `factory-runtime`, `doc`, …) behind;
  4. does **not** reset the derived layers (retain them); discard only the transient deployed machinery.
- The harvest classification is driven by the registry categories — not a hand-maintained file list.
- Prove a real build/maintain run deposits the registry-classified product-def artifacts into
  `test_harness_app/` and retains them (AC-11 EGP-F referent). Python gates green.

### Out of Scope
- The test-and-reset mode (existing, AC-07) — build mode is additive, not a replacement.
- The whole-factory deploy internals (T-B), orchestrator relocatability (T-E), derivation project-
  relativity (T-C) — consumed here, not re-implemented.
- Running the actual harness-middle derivation for the current anchors (that is TASK-PROC-068-12's run).

## Acceptance Criteria

- [x] AC-11 — EGP: F (a real build/maintain run observed to derive in an isolated deployed copy and deposit the registry-classified product-definition artifacts into test_harness_app/, retaining them); consequence: MEDIUM — evidence: `plans_and_protocols/2026-07-03_02_evidence_ac11-functional-proof.md`

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-16 (T-B) | completed | Whole-factory deploy into the isolated copy |
| TASK-PROC-041-01-12 (T-E) | completed | Relocatable orchestrator — derivation drives the copy's own autorun |
| TASK-PROC-071-06-06 (T-C) | completed | Project-relative derivation — authors the copy's own layers |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-12](../2026-07-01_impl_harness-middle-rederive/goal.md) | Consumer — uses build mode to derive the harness middle (rewired to depend on this task) |

## Notes

**Standalone override (developer-authorized, interactive, 2026-07-02):** REQ-PROC-068 has uncovered ACs;
`task-create` §3c redirect skipped by developer authorization.

**Registry-driven harvest:** identify what to copy back via `.factory/registry/artifacts.yaml` categories
(product-definition = `user-needs` + `requirements` + `scribble` + `source-code`), so factory growth is
classified automatically rather than by a brittle file list.

**RECURSIVE OVERRIDE-REGISTRATION STANDING RULE (developer, 2026-07-01):** if executing this task creates
any further tasks, add them to `.claude/task_ordering_priority_override.txt` and carry this instruction into
their `goal.md`.
