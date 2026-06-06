---
task_id: TASK-PROC-053-06
type: impl
parent_requirement: REQ-PROC-053
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-05-27
completed: 2026-05-27
session_completed_at: 2026-05-27T07:07:51Z
effort: M
created: 2026-05-26
after: [TASK-PROC-053-04]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-05]
  sections: []
scope_description: "Wire gate-failure → lookup edge into orchestrator skills and update CLAUDE.md budget framework"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: db92ca63
  file: ../requirements.md
session_id: 5b43d644-46d0-4b04-b2b3-dd07b00ed545
session_account: web

---
# Goal — Tier 4: Gate-failure → lookup edge + CLAUDE.md budget framework

## Objective

Close the feedback loop between quality gate failures and documentation lookups,
and document the per-task lookup budget framework.

## Scope

### In Scope

Per synthesis §7 and §8:

1. **Gate-failure → lookup edge** — when `quality-checker` reports a failure
   matching deprecation / unknown-symbol / signature-mismatch / SP-gate categories,
   the orchestrating skill prepends a `doc-lookup-dependencies` call before the
   fix re-spawn. Wire into: `code-simple` (step 5), `code-complex` (step 6),
   `code-test` (step 5). See synthesis §7.2 for the failure-category → trigger table.

2. **CLAUDE.md §7/§8 update** — add the lookup-budget framework (§8.2 bands,
   §8.3 cap-driven escalation). D6: no Opus scaling.

### Out of Scope

- Measurement / analytics (Tier 5).
- `verify-quality` itself does NOT call `doc-lookup-dependencies` (§7.4).

## Design Reference

Synthesis §7 (gate-failure interaction) and §8 (budget) in TASK-PROC-053-02 plans_and_protocols.

## Acceptance Criteria

- [x] Three orchestrator skills updated with failure-category classification and pre-fix lookup step
- [x] CLAUDE.md §7/§8 updated with budget bands and cap-driven escalation
- [x] No changes to verify-quality itself

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-053-04 | pending | Per-skill checkpoints must be wired first |
