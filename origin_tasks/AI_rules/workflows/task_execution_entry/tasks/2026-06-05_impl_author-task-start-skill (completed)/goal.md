---
task_id: TASK-PROC-069-02
type: impl
parent_requirement: REQ-PROC-069
urgency: 3
urgency_reason: U3-FIX
impact: 4
impact_reason: I4-PAIN
status: completed
started: 2026-06-05
completed: 2026-06-05
effort: M
created: 2026-06-05
expected_tool_calls: 25
skill_chain_depth: 3
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-06]
  sections: []
scope_description: "Author the task-start skill: phases P0–P4, all pre-condition gates, CLAUDE.md §4 + claude-automated-mode updates"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: fe63ab47
  file: ../requirements.md
---

# Goal: Author the `task-start` Skill

## Objective

Create `.claude/skills/task-start/` as the canonical single entry point for executing any already-created task (REQ-PROC-069 AC-01). The skill implements the four phases from the design synthesis and updates every document that names the current entry point.

## Requirements Summary

REQ-PROC-069 (Task Execution Entry Point) governs a canonical `task-start` skill that runs universal pre-flight before any execution skill is invoked:
- Reference resolution (path / TASK-ID / "next task" / free-text)
- Pre-condition gating (schema-valid goal.md, not completed, not awaiting answer, after-deps done)
- Mark in_progress + session identity (automated mode)
- Delegate to `claude-route` for type-detection + dispatch

For complete requirements at task creation time:
```
git show fe63ab47:requirements_tasks/process/AI_rules/workflows/task_execution_entry/requirements.md
```

Current requirements: ../requirements.md

Design synthesis (MANDATORY read before implementing):
`tasks/2026-06-05_explore_task-start-wrapper (completed)/plans_and_protocols/2026-06-05_01_synthesis_task-start-design.md`

## Scope

### In Scope

- Create `.claude/skills/task-start/SKILL.md` via `claude-create-skill` with phases P0–P4 per synthesis §1
- Update `CLAUDE.md §4 "Default Workflow"` to name `task-start` as the entry point (exact new wording in synthesis §6)
- Update `.claude/skills/claude-automated-mode/SKILL.md` L148–157 to re-point from `claude-route` to `task-start` (load-bearing ordering constraint — synthesis §4)
- Add `task-start` to `.claude/skills/INDEX.md` and re-describe `claude-route` as internal router
- Update `.claude/factory_flows.md` entry-point flow reference

All skill edits via `claude-modify-skill`; new skill via `claude-create-skill`.

### Out of Scope

- Shrinking `claude-route` (removing its Mode-A pre-steps / Modes B/C) — that is TASK-PROC-069-03 (must follow this task)
- Updating the remaining 9 migration-surface files listed in synthesis §6 — covered by TASK-PROC-069-03
- Auditing `orchestrate.py` automated paths — TASK-PROC-069-03

## Acceptance Criteria

- [x] `.claude/skills/task-start/SKILL.md` exists and implements phases P0–P4 per synthesis §1
- [x] Phase P0 resolves all four reference forms: goal.md path, TASK-ID, "next task" (→ next_tasks.py selection loop), free-text (→ interactive disambiguation)
- [x] Phase P1 runs `validate_against_schema.py` and halts loudly on schema failure
- [x] Phase P2 gates: status≠completed (warn+confirm / skip), awaiting: empty (hard-block / skip), after: deps done (warn+confirm / skip); failure policies match synthesis §3 table
- [x] Phase P3 marks `in_progress` + `started:` when status is pending/absent; in automated mode also writes `session_id` + `session_account` before any pending_feedback escalation (synthesis §4 load-bearing ordering)
- [x] Phase P4 delegates to `claude-route <validated-goal.md-path>` — not back to task-start
- [x] `CLAUDE.md §4 "Default Workflow"` names `task-start` as the entry point (using the exact proposed wording from synthesis §6)
- [x] `claude-automated-mode` SKILL.md L148–157 reference updated from `claude-route` to `task-start`
- [x] `INDEX.md` lists `task-start`; `claude-route` described as internal router
- [x] `factory_flows.md` entry-point reference updated

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-069-01 | completed | Design synthesis; read before implementing |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-069-01](../2026-06-05_explore_task-start-wrapper%20(completed)/goal.md) | Predecessor — read synthesis before implementing |
| [TASK-PROC-069-03](../2026-06-05_impl_shrink-claude-route-migrate-callers/goal.md) | Successor — shrinks claude-route + migrates remaining callers; must run after this task |

## Notes

The design synthesis at `plans_and_protocols/2026-06-05_01_synthesis_task-start-design.md` (in the completed explore task) is the authoritative HOW. Key invariants to carry into the implementation:
- **Ordering** (AC-04): `in_progress` + session identity BEFORE any pending_feedback write
- **Verify, don't pass context** (REQ-PROC-069 Developer Guidelines): parse frontmatter for gating only; execution skills read goal.md + protocol.md themselves
- **Defense-in-depth retained** (AC-05): the 9 existing REQ-PROC-044 pre-checks in execution skills stay untouched
