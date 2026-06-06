---
task_id: TASK-PROC-058-04
type: impl
parent_requirement: REQ-PROC-058
urgency: 4
urgency_reason: U4-DEP
impact: 4
impact_reason: I4-ENAB
status: completed
effort: M
created: 2026-05-24
started: 2026-05-25
completed: 2026-05-25
session_completed_at: 2026-05-25T14:00:00Z
after: [TASK-PROC-058-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-10, AC-11]
  sections: []
scope_description: "Update task-create skill: add redirect to task-derive-from-requ when requirement has uncovered ACs (AC-10); add plan-driven mode that accepts pre-computed values from a plan (AC-11)."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: e680b5e9
  file: ../../requirements.md
session_id: 37fe32ed-ddf4-4326-94c4-7df1c284972a
session_account: gmail
---
# Goal: Update task-create skill — redirect and plan-driven mode

## Objective

Update `.claude/skills/task-create/SKILL.md` to:
1. Redirect to task-derive-from-requ when invoked on a requirement with uncovered ACs (impl/verify tasks only; bugfix/explore/define exempt)
2. Add plan-driven mode that accepts pre-computed values from a task creation plan, skipping redundant analysis

## Requirements Summary

REQ-PROC-058 AC-10 mandates the redirect; AC-11 mandates plan-driven mode. Together they ensure task-create either redirects to the holistic gate (task-derive-from-requ) or operates as a workspace creator with pre-computed values.

For complete requirements at task creation time:
```
git show e680b5e9:requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

1. **Redirect logic (AC-10)** in task-create:
   - Trigger condition: invocation is in standalone mode (not from task-derive-from-requ, not plan-driven) AND parent_requirement has `trackable_items.acceptance_criteria` AND task type is impl OR verify
   - Exempt task types: bugfix, explore, define, analyze, review
   - Behavior: print redirect message ("This requirement has N uncovered ACs. Routing to task-derive-from-requ for holistic decomposition.") and invoke task-derive-from-requ skill
   - User can override (skip redirect) with explicit flag/answer; override is logged

2. **Plan-driven mode (AC-11)** in task-create:
   - Input: plan entry values (covers_acs, effort, layer, after, opus_recommended, target_package, scope description)
   - Skip: Phase 3b coverage-asking, Phase 3.4 package prompting (use plan value), user confirmation at Phase 4
   - Use plan values directly for goal.md frontmatter
   - File-level analysis is NOT applicable for non-code tasks (task-create handles non-code)

3. **Detection of caller**: skill needs to know if it's being called standalone or by task-derive-from-requ. Use an input flag or environment variable convention.

### Out of Scope

- task-create-code updates (separate task TASK-PROC-058-05)
- The plan format itself (defined in TASK-PROC-058-02)
- All other task-create behavior — preserve existing functionality

## Acceptance Criteria

- [x] Redirect logic implemented per AC-10; exemptions correctly applied
- [x] Plan-driven mode accepts all required plan fields and skips redundant phases
- [x] task-create still works in standalone mode for requirements without ACs and for exempt task types
- [x] Skill body documents both modes clearly
- [x] Use `claude-modify-skill` skill for the modification (mandatory per CLAUDE.md)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-058-02 | pending | Plan format must be defined |

## Notes

Per REQ-PROC-058 AC-15 (no redundant recomputation): in plan-driven mode, task-create trusts the plan's coverage and AC selection — does NOT re-ask the user. The plan IS the user's decision.

Mandatory: use `claude-modify-skill` per CLAUDE.md ("THIS SKILL MUST BE USED TO MODIFY EXISTING SKILLS, no modification without it is allowed").
