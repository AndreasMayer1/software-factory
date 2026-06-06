---
task_id: TASK-PROC-044-02-02
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
session_completed_at: 2026-06-01T10:51:42Z
after: [TASK-PROC-044-02-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-03]
  sections: []
scope_description: "Build a resolve-to-token lint in the per-change quality gates binding contract edges and agent names to registry tokens"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 4d4b3e26
  file: ../../requirements.md
session_id: 204d7317-a4e4-4c0d-9607-818acadda368
session_account: web
---
# Goal: Artifact-token resolve lint

## Objective

Build the lint that makes the registry authoritative: every `produces:`/`derived_from:` value
and every governed agent-name artifact-or-lens segment must resolve to a registry token, with a
graceful stop on any unresolved value or duplicate registry token.

## Requirements Summary

REQ-PROC-044-02 AC-02 (contracts resolve) and AC-03 (agent names resolve). The lint is the
backstop of the eager establishment gate — it catches anything authored outside the authoring
skills. Wired into the per-change quality gates (REQ-PROC-046) in the same family as the
boundary-contract lint (epic REQ-PROC-044 AC-08).

Current requirements: ../../requirements.md

## Scope

### In Scope
- A resolve-to-token lint (script — author via `claude-write-script`, governed by REQ-PROC-043).
- Checks: (a) every `produces:`/`derived_from:` value in every `contract.yaml` resolves to a
  registry token; (b) every governed agent-name artifact-or-lens segment (REQ-PROC-044-01 AC-01)
  resolves to a token; (c) the registry has no duplicate token (backs AC-04 no-overlap).
- Unresolved value or duplicate token → visible warning + graceful stop (non-zero exit).
- Wire into the per-change quality gate set (REQ-PROC-046).

### Out of Scope
- Creating/seeding the registry (TASK-PROC-044-02-01).
- Reconciling existing contracts so the lint passes (TASK-PROC-044-02-03).

## Acceptance Criteria

- [x] Lint resolves every `produces:`/`derived_from:` value against the registry; unresolved → graceful stop
- [x] Lint resolves every governed agent-name artifact-or-lens segment against the registry
- [x] Lint detects duplicate registry tokens and stops gracefully
- [x] Lint runs in the per-change quality gate set (REQ-PROC-046), boundary-contract-lint family

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-02-01 | pending | Registry must exist before the lint can resolve against it |

## Notes

Check (b) only goes fully green once the REQ-PROC-044-01 agent renames land; until then it
surfaces current non-conforming names — coordinate ordering with 044-01. Author the script via
`claude-write-script` (Python gates apply).
