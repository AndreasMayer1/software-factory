---
task_id: TASK-PROC-053-04
type: impl
parent_requirement: REQ-PROC-053
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-05-26
completed: 2026-05-27
session_completed_at: 2026-05-27T06:57:33Z
effort: M
created: 2026-05-26
after: [TASK-PROC-053-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-07]
  sections: []
scope_description: "Wire doc-lookup-dependencies checkpoint into all code-producing skills and agents"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: db92ca63
  file: ../requirements.md
session_id: 55d45ce6-3315-4efa-b3d1-0419b24b5fc3
session_account: gmail2
---
# Goal — Tier 2: Wire doc-lookup-dependencies into code-producing chains

## Objective

Add the `doc-lookup-dependencies` checkpoint (from TASK-PROC-053-03) into
every code-producing skill and agent, at the step closest to where code is written.

## Scope

### In Scope

Per synthesis §4.7 (one checkpoint placement decision per chain):

- `code-simple` SKILL.md — checkpoint in implementation-engineer step
- `code-complex` SKILL.md — checkpoint per batch (plan pre-warm optional)
- `code-test` SKILL.md — checkpoint in test-engineer Phase 2
- `code-bugfix` SKILL.md — checkpoint inline; add `Skill` tool to tool list
  (user feedback D2: option A — grow Skill tool on code-bugfix)
- `implementation-engineer.md` — per-agent invocation pattern
- `test-engineer.md` — per-agent invocation pattern

### Out of Scope

- Gate-failure → lookup edge wiring (Tier 4 task).
- Per-technology tables (Tier 3 task).

## Design Reference

Synthesis §3 (chain map) and §4.7 (checkpoint placement per chain).
User feedback: code-bugfix gets Skill tool (option A).

## Acceptance Criteria

- [x] All six chains (C1–C5 + agents) have exactly one checkpoint
- [x] code-bugfix has Skill tool added
- [x] Each checkpoint invokes doc-lookup-dependencies at the right step
- [x] No chain has duplicate checkpoints (skill + agent both firing)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-053-03 | pending | doc-lookup-dependencies skill must exist |
