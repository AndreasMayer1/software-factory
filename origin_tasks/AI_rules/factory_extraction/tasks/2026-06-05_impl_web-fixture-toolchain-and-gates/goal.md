---
task_id: TASK-PROC-066-04
type: impl
parent_requirement: REQ-PROC-066
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUALITY
status: in_progress
effort: L
created: 2026-06-05
started: 2026-06-05
expected_tool_calls: 40
skill_chain_depth: 2
after: [TASK-PROC-066-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Stand up the web (React/Angular) toolchain, doc/ guideline surface, and quality gates the factory lacks for web — the host for the coupling-rich skill-test fixture. Routes through REQ-PROC-060 dependency-admission (large dependency addition)."
release_description: ""
opus_recommended: false   #
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../requirements.md
session_id: 844c58cd-b9da-4ede-8f30-5dee62ff8937
session_account: gmail2

---
# Goal: Web (React/Angular) Fixture Toolchain, doc/ Surface & Quality Gates

## Objective

Stand up the web toolchain that hosts the skill-test fixture (manifest task **T-B1**). The fixture decision
(redesign Q2) chose a **web** target to force tech-agnosticism, but the factory currently has no web-side
surface. This task creates it:
- The **React or Angular** project scaffold for the fixture (final framework choice confirmed with T-B0's
  playground requirements).
- The web-side **`doc/` guideline surface** (web architecture/component conventions analogous to the Flutter
  `doc/` rules) the factory needs to govern web work.
- Web **quality gates** (lint / test / build) analogous to the Dart gates, wired so the fixture's code is
  governed like the rest of the project.

**Dependency-admission:** standing up React/Angular is a large new top-level dependency set → this MUST route
through the **REQ-PROC-060 dependency-admission gate** (developer-authorized; do not self-add). See
`doc/process/dependency_admission_gate.md`.

## Background

T-B1 of the scribble-gate redesign manifest. The fixture's purpose, the web/tech-agnostic implication, and the
cost note ("a toolchain + doc/ surface the factory lacks for web") are in the redesign task:
`../../../workflows/ui_sketch_iteration_workflow/tasks/2026-06-04_explore_redesign-implementation-workflow-scribble-gate/plans_and_protocols/2026-06-05_06_backpressure_T2_extraction-and-playground.md`
and `…/2026-06-05_13_implementation-task-manifest.md` (row T-B1). The playground requirements that pin the
framework choice come from TASK-PROC-066-03 (T-B0).

Current requirements: ../requirements.md (none yet for REQ-PROC-066 — this area is exploratory; the playground
epic/features authored by TASK-PROC-066-03 govern the fixture's product scope).

## Scope

### In Scope
- Web project scaffold, web `doc/` guidelines, web quality gates, dependency-admission for the toolchain.

### Out of Scope
- The fixture's feature code (that is T-B2, derived from T-B0's requirements via the new workflow).
- The six measurement probes (T-B3).

## Acceptance Criteria

- [ ] Web toolchain scaffolded; framework matches T-B0's playground requirements
- [ ] Web `doc/` guideline surface created
- [ ] Web quality gates (lint/test/build) wired and green on the scaffold
- [ ] All new dependencies passed the REQ-PROC-060 dependency-admission gate (developer-authorized)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-066-03 | pending | T-B0 — the playground requirements pin the framework choice and the fixture's scope. |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-066-03](2026-06-05_explore_skill-test-playground-requirements/goal.md) | Predecessor — playground epic/feature requirements; pins framework + fixture scope. |
| [TASK-PROC-032-29](../../../workflows/ui_sketch_iteration_workflow/tasks/2026-06-04_explore_redesign-implementation-workflow-scribble-gate/goal.md) | Source — redesign manifest row T-B1; Q2 web decision. |

## Notes

Framework (React vs Angular) to be confirmed against T-B0's playground requirements before scaffolding.
