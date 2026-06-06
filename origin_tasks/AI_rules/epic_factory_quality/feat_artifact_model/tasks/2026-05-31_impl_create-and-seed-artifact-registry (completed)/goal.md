---
task_id: TASK-PROC-044-02-01
type: impl
parent_requirement: REQ-PROC-044-02
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-31
started: 2026-06-01
completed: 2026-06-01
session_completed_at: 2026-06-01T19:09:05Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-04, AC-05, AC-06]
  sections: []
scope_description: "Create .factory/registry/artifacts.yaml and .factory/README.md; seed the initial token set under a developer review gate"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 4d4b3e26
  file: ../../requirements.md
session_id: 40e18891-b72a-4500-8d18-bf63a9cd3fd4
session_account: gmail
---
# Goal: Create and seed the artifact registry

## Objective

Establish the canonical artifact registry and the `.factory/` orientation README, and
seed the registry's initial token set under a mandatory developer review gate.

## Requirements Summary

REQ-PROC-044-02 (feat_artifact_model) defines a single source of truth for artifact
*definitions* — a node table the resolve lint and the agent-naming scheme both draw from.
This task delivers the data file and the lifecycle documentation; the lint (TASK-PROC-044-02-02)
and the establishment gate (TASK-PROC-044-01-04) consume it.

Current requirements: ../../requirements.md

## Scope

### In Scope
- `.factory/registry/artifacts.yaml` — each entry: unique `token` + filesystem `path`/glob +
  one-line `definition`; append-structured; no duplicate tokens (AC-01, AC-04 registry property).
- `.factory/README.md` — authored-vs-generated lifecycle split (`registry/` = authored canon,
  never pruned; `optimize/` + `session_logs/` = generated runtime), inventory of `.factory/`
  subfolders with owners, and the boundary that tech-dictated meta (`.claude/`, root `CLAUDE.md`)
  is OUT of `.factory/` scope (AC-05).
- Ensure the registry is committed and excluded from any `.factory` pruning configuration (AC-05).
- Seed the initial token set from the union of existing `.claude/skills/*/contract.yaml` and
  `.claude/agents/*.contract.yaml` `produces:`/`derived_from:` values, cross-checked against
  `scripts/factory/render_factory_map.py` nodes and the CLAUDE.md Information Map (AC-01, AC-06).

### Out of Scope
- The resolve lint (TASK-PROC-044-02-02).
- The establishment gate in the authoring skills (TASK-PROC-044-01-04).
- Reconciling existing contracts to the tokens (TASK-PROC-044-02-03).

## Acceptance Criteria

- [x] `.factory/registry/artifacts.yaml` exists; every entry has a unique token + path + definition; no duplicate tokens
- [x] `.factory/README.md` documents the lifecycle split + subfolder inventory + `.claude/`/`CLAUDE.md` exclusion
- [x] Registry is committed and excluded from any `.factory` pruning config
- [x] Initial token set is seeded from contracts + factory map + Information Map AND ratified by the developer (review gate — do not auto-finalize the seeded canon)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | Foundational; blocks TASK-PROC-044-02-02 and TASK-PROC-044-01-04 |

## Notes

Process/factory-tooling only; no lib/test/integration_test changes. The seeded set is canon —
the developer must ratify (confirm / rename-to-existing / reject, per token) before finalizing.
Plan: ../../../tasks/2026-05-31_explore_artifact-model-and-agent-naming (completed)/plans_and_protocols/2026-05-31_01_task_creation_plan.md
