---
task_id: TASK-PROC-044-02-03
type: impl
parent_requirement: REQ-PROC-044-02
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-06-02
completed: 2026-06-02
session_completed_at: 2026-06-02T10:31:24Z
effort: M
created: 2026-05-31
after: [TASK-PROC-044-02-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02]
  sections: []
scope_description: "Reconcile all existing contract.yaml produces/derived_from values to registry tokens until the lint reports zero contract-side violations"
release_description: ""
opus_recommended: true  # promoted after context_limit_no_entitlement
requirements_version:
  commit: 4d4b3e26
  file: ../../requirements.md
session_id: 8763f2da-6d20-4603-aeac-a2531f8775cd
session_account: gmail
---
# Goal: Remediate contracts to resolve to registry tokens

## Objective

Drive the contract-side resolve check to zero violations: every `produces:`/`derived_from:`
value in every existing `contract.yaml` resolves to a registry token.

## Requirements Summary

REQ-PROC-044-02 AC-02. Enforcement-creates-violations remediation: the lint
(TASK-PROC-044-02-02) will flag every contract value that does not resolve; this task fixes
them all so the gate is green on `develop`.

Current requirements: ../../requirements.md

## Scope

### In Scope
- Run the resolve lint across all `.claude/skills/*/contract.yaml` and
  `.claude/agents/*.contract.yaml`.
- For each violation: reconcile to a registry token — fix typos/aliases to existing tokens, or
  add genuinely-new tokens via the establishment gate (developer-ratified).
- Repeat until the contract-side check reports zero violations.

### Out of Scope
- Agent-name violations (handled by the REQ-PROC-044-01 rename work, not here).
- Building the lint or the registry.

## Acceptance Criteria

- [x] Resolve lint reports zero contract-side (`produces:`/`derived_from:`) violations across the repo
- [x] Any new tokens added during remediation went through the establishment gate (no silent appends)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-02-02 | pending | The lint must exist to find the violations |

## Notes

Agent-name resolution (AC-03) reaches full green via the 044-01 rename work, not this task.
