---
task_id: TASK-PROC-058-05
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
session_completed_at: 2026-05-25T19:18:46Z
after: [TASK-PROC-058-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-10, AC-11, AC-13]
  sections: [SEC-03]
scope_description: "Update task-create-code skill: redirect to task-derive-from-requ (AC-10), plan-driven mode with file-analysis refinement (AC-11, AC-15), requirements_version stale-plan check (AC-12 consumer), preserve WHAT-not-HOW (AC-13)."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: e680b5e9
  file: ../../requirements.md
session_id: ccbc2765-5e77-4d98-98fa-180a71a387f9
session_account: web
---
# Goal: Update task-create-code skill — redirect, plan-driven mode, stale-plan check

## Objective

Update `.claude/skills/task-create-code/SKILL.md` to support the REQ-PROC-058 workflow: redirect from standalone mode when uncovered ACs exist; refine sizing via file analysis in plan-driven mode; detect stale plans via requirements_version; preserve the WHAT-not-HOW principle.

## Requirements Summary

REQ-PROC-058 brings task-create-code under its governance. AC-10 (redirect), AC-11 (plan-driven mode with refinement), AC-13 (WHAT not HOW preservation), AC-15 (estimate-upstream / refine-downstream) all apply.

For complete requirements at task creation time:
```
git show e680b5e9:requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

1. **Redirect logic (AC-10)** — same as task-create:
   - Trigger: standalone mode + parent requirement has ACs + task type is impl/verify
   - Exempt: bugfix, explore, define, analyze, review
   - Behavior: redirect to task-derive-from-requ; user can override

2. **Plan-driven mode refinements (AC-11, AC-15)**:
   - Phase 0A already exists — extend to handle additional plan fields per REQ-PROC-058 SEC-04 (requirements_version, etc.)
   - Phase 1 (requirement read): still happens to populate goal.md body with Goal/AC text — DO NOT skip even in plan-driven mode (the read is needed for body content, not for analysis)
   - Phase 2 (file analysis): always runs for code tasks, even in plan-driven mode (refines plan's rough estimate)
   - Escalation: if file analysis reveals task is significantly larger than plan estimated (e.g., Large → Split NOW), report back; interactive mode asks user; automated mode writes question.md

3. **Stale plan check (AC-12 consumer side)**:
   - At Phase 0A, after parsing plan, compare plan's `requirements_version` against current git hash of requirements.md
   - If different: warn "Plan was created against commit X, but requirements.md is now at commit Y. Plan may be stale."
   - Interactive: ask user — proceed / abort / re-plan
   - Automated: write question.md and stop

4. **Preserve AC-13 (WHAT not HOW)**:
   - Existing behavior is correct — goal.md body describes WHAT, not concrete code changes
   - Verify the skill text continues to enforce this (no regression from new fields)

5. **Update Phase 4.1 (Present)**: skip per-task user confirmation in plan-driven mode (plan was approved at the planning level)

6. **Update propose_after.py invocation**: in plan-driven mode, restrict to `requirement_then_implementation` heuristic only (plan's `after:` is authoritative for cross-task dependencies); standalone mode keeps full heuristic set

### Out of Scope

- The plan format definition itself (defined in TASK-PROC-058-02)
- task-create updates (separate task TASK-PROC-058-04)
- Phase 6 (plan conformance check) — already exists, just verify it handles the new field set

## Acceptance Criteria

- [x] Redirect logic implemented per AC-10
- [x] Plan-driven mode supports requirements_version + all SEC-04 fields
- [x] File analysis (Phase 2) runs in plan-driven mode and can escalate on mismatch
- [x] Stale plan check (requirements_version comparison) implemented; warns/blocks appropriately
- [x] Phase 4.1 per-task confirmation skipped in plan-driven mode
- [x] propose_after.py invocation correctly scoped (heuristic mode flag based on plan-driven vs standalone)
- [x] AC-13 (WHAT not HOW) preserved — no regression
- [x] Skill body updated via `claude-modify-skill` (mandatory)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-058-02 | pending | Plan format must be defined |

## Notes

Per REQ-PROC-058 AC-15: file analysis is the "refine downstream" step for code tasks. Plan provides rough estimate (S1-S4), task-create-code refines with file-level detail (S/M/L). The two are complementary.

Mandatory: use `claude-modify-skill` per CLAUDE.md.

If propose_after.py needs a new `--heuristic` flag (currently uses full set), that's a separate small change — use `claude-write-script` per CLAUDE.md.
