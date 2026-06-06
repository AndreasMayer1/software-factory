---
task_id: TASK-PROC-035-19
type: impl
parent_requirement: REQ-PROC-035
urgency: 4
urgency_reason: U4-DEP
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-05-24
started: 2026-05-25
completed: 2026-05-25
session_completed_at: 2026-05-25T19:35:35Z
after: [TASK-PROC-058-02, TASK-PROC-058-04, TASK-PROC-058-05]
awaiting: []
awaiting_note: ""
target_package: "Transfer Data Model"
covers:
  acceptance_criteria: []
  sections: [SEC-05, SEC-06]
scope_description: "Rewrite release-begin-impl Phase 2c to delegate per-requirement decomposition to task-derive-from-requ (per REQ-PROC-035 SEC-05/SEC-06 as updated by TASK-PROC-035-18, and REQ-PROC-058 AC-14). Phase 2c becomes an orchestrator: spawns per-requirement task-derive-from-requ agents, assembles per-requirement plans into release plan, adds release-level concerns."
release_description: ""
opus_recommended: true   # reason: novel multi-agent orchestration pattern, cross-cutting refactor of an existing release-critical skill
writes_requirements: false
requirements_version:
  commit: f58c811e
  file: ../../requirements.md
session_id: 985c56ee-0538-437c-88d0-9b5e02c10fcb
session_account: web
---
# Goal: Rewrite release-begin-impl Phase 2c as delegation orchestrator

## Objective

Replace the current monolithic Phase 2c agent in `.claude/skills/release-begin-impl/SKILL.md` with a delegation orchestrator that spawns one `task-derive-from-requ` agent per in-scope requirement, assembles per-requirement plans into the release plan, and adds release-level concerns.

This implements the changes to SEC-05 (Task Creation Process) and SEC-06 (release-begin-impl Integration) that TASK-PROC-035-18 committed to REQ-PROC-035 (commit f58c811e).

## Requirements Summary

REQ-PROC-035 SEC-05/SEC-06 now describe Phase 2c as a delegation pattern:
- One `task-derive-from-requ` agent per in-scope requirement (instead of one monolithic agent reading all)
- Each agent produces a per-requirement plan with coverage matrix, verification task, sizing signals (REQ-PROC-058 AC-01, AC-02, AC-03)
- Phase 2c assembles per-requirement plans into a release plan in the unified format (REQ-PROC-058 SEC-04)
- Phase 2c adds release-level concerns on top: package execution ordering, cross-requirement dependencies, scope completeness
- Phase 5 (user gate) presents per-requirement coverage matrices

For complete requirements at task creation time:
```
git show f58c811e:requirements_tasks/process/AI_rules/requirements_management/release_preparation/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

1. **Rewrite Phase 2c in release-begin-impl skill** (`.claude/skills/release-begin-impl/SKILL.md`):
   - Identify in-scope requirements for the release
   - Spawn one `task-derive-from-requ` agent per requirement (parallel where possible; serial fallback if context-budget concerns surface)
   - Each agent produces: per-requirement plan with coverage matrix, verification task, sizing signals, dependencies
   - Wait for all agents to complete (or escalate if any agent fails)
   - Assemble per-requirement plans into release `task_creation_plan.md` (unified format per REQ-PROC-058 SEC-04)
   - Add release-level concerns: package execution ordering, cross-requirement after-chains, scope completeness verification

2. **Cross-requirement dependency reconciliation**: after assembly, scan plans for tasks that semantically depend on tasks from other requirements (e.g., REQ-A task uses data model from REQ-B). Add explicit cross-requirement after-chains. This compensates for the loss of implicit cross-visibility that the monolithic agent had.

3. **Phase 5 user gate update**: present per-requirement coverage matrices alongside the assembled release plan; user reviews + approves at release level

4. **Plan format consumer**: ensure the assembled plan is consumable by task-create-code Phase 0A as before (no regression for the consumer side)

5. **Documentation update**: skill body explains the delegation model; cite REQ-PROC-058 for per-requirement decomposition contract

### Out of Scope

- task-derive-from-requ skill itself — TASK-PROC-058-02
- task-create / task-create-code updates — TASK-PROC-058-04, TASK-PROC-058-05
- Cross-reference completeness gate (AC-17) — TASK-PROC-058-03 (runs WITHIN task-derive-from-requ, not within release-begin-impl)
- Release-level scope completeness check (Phase 1) — already exists, no change
- Orchestration task self-perpetuating chain (Phase 6) — already exists, may need minor adjustment if plan format changed

## Acceptance Criteria

- [x] Phase 2c in `.claude/skills/release-begin-impl/SKILL.md` rewritten as delegation orchestrator
- [x] Per-requirement agent spawning works (parallel or serial as appropriate)
- [x] Each agent invocation passes requirement path + receives per-requirement plan
- [x] Release plan assembled from per-requirement plans in unified format (REQ-PROC-058 SEC-04)
- [x] Release-level concerns added on top: package ordering, cross-requirement after-chains, scope completeness
- [x] Phase 5 user gate presents per-requirement coverage matrices
- [x] task-create-code Phase 0A still consumes the assembled plan correctly (no regression)
- [x] Documentation updated in skill body
- [x] Use `claude-modify-skill` for the modification (mandatory per CLAUDE.md)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-058-02 | pending | task-derive-from-requ skill must exist to delegate to |
| TASK-PROC-058-04 | pending | task-create plan-driven mode (for assembled plan consumers) |
| TASK-PROC-058-05 | pending | task-create-code plan-driven mode (for assembled plan consumers) |

## Notes

This is the implementation half of AC-14 of REQ-PROC-058. The requirement-level change (REQ-PROC-035 SEC-05/SEC-06 prose) was done by TASK-PROC-035-18. This task implements the skill-level change.

Critical: do NOT break the release flow during the rewrite. Consider implementing the new path behind a feature flag with the old monolithic agent as fallback, then removing the fallback once validated. This is the highest-risk change in the REQ-PROC-058 family because release-begin-impl is release-critical.

Per the user's design uncertainty note: "AC-14 is particularly risky — release flow already works; we're proposing to restructure it. Defer AC-14 to a separate requirement (don't bundle the refactor with the new skill) OR implement it behind a feature flag." This task is the separate requirement-aligned task that handles it.

Mandatory: use `claude-modify-skill` per CLAUDE.md.
