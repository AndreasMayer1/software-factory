---
task_id: TASK-PROC-069-03
type: impl
parent_requirement: REQ-PROC-069
urgency: 3
urgency_reason: U3-FIX
impact: 4
impact_reason: I4-PAIN
status: completed
completed: 2026-06-05
effort: M
created: 2026-06-05
started: 2026-06-05
expected_tool_calls: 40
skill_chain_depth: 3
after: ["TASK-PROC-069-02"]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03, AC-05, AC-06]
  sections: []
scope_description: "Shrink claude-route to a pure router (B1 seam); migrate all 14 caller files; audit automated paths for AC-06"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: fe63ab47
  file: ../requirements.md
---

# Goal: Shrink `claude-route` and Migrate All Callers

## Objective

Complete the B1 clean seam by removing the pre-flight steps from `claude-route` (now that `task-start` owns them — TASK-PROC-069-02) and updating every file that references `claude-route` as the execution entry point. This is the second half of the "both, separated" split: task-start = pre-flight, claude-route = pure router.

## Requirements Summary

REQ-PROC-069 AC-03 requires exactly one component to own routing (distinct from pre-flight). AC-05 requires each execution skill to still fail loudly on a missing/off-schema goal.md when invoked directly. AC-06 requires that no automated execution path reaches an execution skill without passing through task-start's gating.

For complete requirements at task creation time:
```
git show fe63ab47:requirements_tasks/process/AI_rules/workflows/task_execution_entry/requirements.md
```

Current requirements: ../requirements.md

Design synthesis (MANDATORY read before starting):
`tasks/2026-06-05_explore_task-start-wrapper (completed)/plans_and_protocols/2026-06-05_01_synthesis_task-start-design.md`
— especially §2 (exact boundary), §5 (what changes in claude-route), §6 (full 14-file migration surface).

## Scope

### In Scope

**claude-route changes** (via `claude-modify-skill`):
- Remove Mode-A steps 1, 2, 2a, 2b from `claude-route/SKILL.md` (now owned by task-start P1–P3)
- Remove Mode B (interactive disambiguation — now owned by task-start P0)
- Remove Mode C (next-task selection — now owned by task-start P0)
- Keep only: read INDEX, match type+content→skill, verification-task shortcut, opus-check, "→ Using `skill`" + invoke
- Narrow `claude-route/contract.yaml` required-input to "a validated, in_progress goal.md path"

**14-file migration surface** (synthesis §6 — grounded 2026-06-05):
1. `CLAUDE.md §4 "Default Workflow"` — replace `claude-route` reference with exact new wording from synthesis §6
2. `.claude/skills/INDEX.md` — re-describe claude-route as internal router
3. `.claude/factory_flows.md` — update entry-point flow reference
4. `.claude/skills/claude-route/SKILL.md` + `contract.yaml` — (covered above)
5. `.claude/skills/claude-automated-mode/SKILL.md` — any remaining claude-route references after TASK-PROC-069-02 (L148–157 already updated in that task; verify no others)
6. `.claude/skills/task-resolve/SKILL.md` — update route fallback reference
7. `.claude/skills/task-derive-from-requ/SKILL.md` — update entry-point mention
8. `.claude/skills/task-complete/SKILL.md` — update entry-point mention
9. `.claude/skills/verify-quality/SKILL.md` — update entry-point mention
10. `.claude/skills/task-create-code/SKILL.md` — update entry-point mention
11. `.claude/schemas/goal_metadata.yaml` + `pending_question.yaml` — update doc/comment refs
12. `scripts/automation/orchestrate.py` — audit resume paths (L1610, L2121) for AC-06 (see below)
13. `scripts/automation/terminate_session.sh` — update reference
14. `scripts/optimize/create_optimize_cycle_task.py` + `scripts/tests/test_next_tasks.py` — update references

**AC-06 automated path audit** (`orchestrate.py`):
- Read lines around L1610 and L2121 (the resume paths grounded in synthesis §9 uncertainty)
- Confirm every automated execution path reaches an execution skill via task-start, not directly
- If a path bypasses task-start: update it; if it's already correct: document in plans_and_protocols

**Verification section** (< 3 impl tasks, so no separate verification task):
- After all changes, run `grep -rn "claude-route" .claude/ scripts/ CLAUDE.md` and confirm only internal/comment references remain (no entry-point invocations that should now be task-start)
- Run `python3 scripts/quality/validate_against_schema.py` on any schema files touched
- Confirm 9 defense-in-depth pre-checks still present in execution skills (AC-05): spot-check code-simple, code-complex, code-test

### Out of Scope

- Authoring task-start skill itself — TASK-PROC-069-02 (must complete first)
- Removing the 9 defense-in-depth REQ-PROC-044 entry pre-checks from execution skills — deliberately kept (decision D-C)
- Any changes to `create_orchestration_task.py` routing table — that governs task *creation*, not execution

## Acceptance Criteria

- [x] `claude-route/SKILL.md` contains only routing logic (no frontmatter validation, no in_progress marking, no selection/disambiguation); its single input is a validated in_progress goal.md path
- [x] `claude-route/contract.yaml` required-input narrowed accordingly
- [x] All 14 migration-surface files updated: no file names `claude-route` as the user-facing execution entry point
- [x] `orchestrate.py` resume paths (around L1610, L2121) confirmed or updated to route through task-start
- [x] `grep -rn "claude-route" .claude/ scripts/ CLAUDE.md` shows only internal router descriptions, no entry-point invocations
- [x] 9 REQ-PROC-044 defense-in-depth pre-checks confirmed present in execution skills (AC-05 spot-check)
- [x] All skill edits made via `claude-modify-skill`

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-069-02 | pending | task-start must exist before claude-route can be shrunk |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-069-02](../2026-06-05_impl_author-task-start-skill/goal.md) | Predecessor — task-start must be authored first; this task removes the pre-flight steps from claude-route that task-start now owns |
| [TASK-PROC-069-01](../2026-06-05_explore_task-start-wrapper%20(completed)/goal.md) | Predecessor — read synthesis §2/§5/§6 before implementing |

## Notes

The synthesis §9 "uncertain" item about orchestrate.py resume paths is a concrete deliverable of this task's AC-06 audit — resolve it (confirm or fix) and document the finding in plans_and_protocols. Do not leave it uncertain after this task completes.
