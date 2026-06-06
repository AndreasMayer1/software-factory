---
task_id: TASK-PROC-002-25
type: impl
parent_requirement: REQ-PROC-002
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-DOCS
status: completed
started: 2026-05-25
completed: 2026-05-25
session_completed_at: 2026-05-25T13:29:01Z
effort: S
created: 2026-05-23
after: [TASK-PROC-046-18]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-08]
  sections: []
scope_description: "Write the authoritative test-quality gate documentation in doc/testing/ covering TQ1-TQ4 thresholds, the property-test inventory rule, and the deterministic-run policy. Ensure consistency with REQ-PROC-002 requirements.md and the scripts that implement the gates."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 2c52ed48
  file: ../../requirements.md
session_id: 7ea79f31-211a-40db-aa55-f2a64411e20e
session_account: gmail
---
# Goal: Document Test-Quality Gates in doc/testing/

## Objective

Create the authoritative documentation for test-quality gates (TQ1-TQ4) in `doc/testing/` so that a contributor or LLM agent can determine, without asking, what "a good test" means in measurable terms. This fulfills REQ-PROC-002 AC-08.

## Requirements Summary

REQ-PROC-002 AC-08: "The active set of test-quality gates, the mutation-kill-rate threshold, the property-test inventory rule, and the deterministic-run policy are documented in a single authoritative location consistent with this requirement (`doc/testing/`) so that a contributor or LLM agent can determine, without asking, what 'a good test' means in measurable terms."

For complete requirements at task creation time:
```
git show 2c52ed48:requirements_tasks/process/AI_rules/coding_standards/testing/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope
- Create/update `doc/testing/test_quality_gates.md` (or similar) covering:
  - TQ1: Assertion strength — what check_test_smells.py enforces, pass condition
  - TQ2: Mutation kill rate — >=80% on safety-critical paths, scoping rules, tooling
  - TQ3: Property-based invariant tests — qualifying types, required test presence
  - TQ4: Independence & determinism — random ordering, consecutive run policy
- Reference the implementing scripts (`scripts/quality/check_test_smells.py`, `check_test_determinism.sh`)
- Ensure consistency with REQ-PROC-002 requirements.md and CLAUDE.md gate table

### Out of Scope
- Modifying gate scripts
- Modifying requirements.md
- G1-G8 code-quality gates (those belong to REQ-PROC-046)

## Acceptance Criteria

- [x] `doc/testing/` contains a file documenting TQ1-TQ4 gates
- [x] Each gate: purpose, tool, pass condition, cadence
- [x] Content is consistent with REQ-PROC-002 requirements.md
- [x] Content is consistent with the actual scripts in `scripts/quality/`
- [x] CLAUDE.md gate table references this doc

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-18 | pending | Gate script correctness must be confirmed before documenting behavior |
