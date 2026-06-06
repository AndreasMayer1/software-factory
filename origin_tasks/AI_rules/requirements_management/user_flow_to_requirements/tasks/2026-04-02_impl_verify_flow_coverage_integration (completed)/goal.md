---
task_id: TASK-PROC-030-04
type: impl
parent_requirement: REQ-PROC-030
urgency: 3
urgency_reason: U3-WORKFLOW-GAP
impact: 4
impact_reason: I4-PAIN
status: completed
started: 2026-04-02
completed: 2026-04-02
effort: M
created: 2026-04-02
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Integrate flow–requirement coverage verification into the derive-from-flow pipeline: add Phase 4.5 to requ-derive-from-flow (emit verification tasks per bundle), rewrite requ-verify-flow-coverage with Opus-based multi-phase verification, update claude-route to dispatch verification tasks."
release_description: ""
requirements_version:
  commit: e9382676
  file: ../requirements.md
---

# Goal: Integrate Flow–Requirement Coverage Verification into the Pipeline

## Objective

Extend the flow→requirements derivation pipeline with an automated verification step
so that coverage gaps are caught without relying on the user to manually invoke the
verification skill.

## Requirements Summary

REQ-PROC-030 defines the `requ-derive-from-flow` skill and the pipeline from approved
user flows to exploration goal.md tasks. This task extends that pipeline by:
1. Making `requ-derive-from-flow` emit **verification tasks** per bundle (Phase 4.5)
2. Rewriting `requ-verify-flow-coverage` into a full Opus-based multi-phase skill
3. Updating `claude-route` to detect and dispatch verification goal.md files

Current requirements: ../requirements.md

## Scope

### In Scope
- Add Phase 4.5 to `requ-derive-from-flow`: group created tasks by `target_package`
  (bundle), create one verification goal.md per bundle with `depends_on` set to all
  exploration task IDs in that bundle
- Rewrite `requ-verify-flow-coverage` with:
  - Phase 0: Context resolution (bundle mode from goal.md vs. standalone invocation)
  - Phase 1: Per-gap Sonnet agents — read flow excerpt + requirement, produce structured behavior checklist
  - Phase 2: Opus synthesis — cross-cutting coherence, intentional deviation detection, remediation categorization
  - Phase 3: Report with quantitative metrics (behavior coverage ratio, AC coverage, cross-reference completeness)
  - Phase 4: User-gated remediation — propose updates, handle intentional deviations, execute approved changes
- Update `claude-route` to detect `verification_bundle` frontmatter field → dispatch to `requ-verify-flow-coverage`
- Update `INDEX.md` description for `requ-verify-flow-coverage`

### Out of Scope
- Changes to `next_tasks.py` — `depends_on` blocking already works correctly
- Changes to `task-create` — verification tasks use the regular explore task type
- Writing actual requirements content — this task is about the skill infrastructure only

## Acceptance Criteria

- [ ] `requ-derive-from-flow` Phase 4.5 creates verification tasks with correct `depends_on` lists covering all bundle exploration task IDs
- [ ] Verification tasks are blocked by `next_tasks.py` until all bundle exploration tasks are completed
- [ ] `requ-verify-flow-coverage` handles both bundle mode (invoked from goal.md) and standalone mode (user command)
- [ ] Per-gap agents read only the specific flow excerpt referenced in the gap, not full flows
- [ ] Opus synthesis phase identifies cross-cutting coherence issues
- [ ] Report includes quantitative behavior coverage ratio per gap and per bundle
- [ ] Remediation phase is user-gated and distinguishes intentional deviations from gaps
- [ ] `claude-route` dispatches verification goal.md files to `requ-verify-flow-coverage` (not `requ-explore`)
- [ ] Both modified skills stay within 100-line token budget

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Plan already written by Opus:
`plans_and_protocols/2026-04-02_01_opus_plan_verify_flow_coverage_integration.md`

Key architectural decision: use `depends_on` (not priority tricks) to enforce
bundle-task → verify ordering. The existing `next_tasks.py` `_is_blocked()` logic
handles this without any script changes.
