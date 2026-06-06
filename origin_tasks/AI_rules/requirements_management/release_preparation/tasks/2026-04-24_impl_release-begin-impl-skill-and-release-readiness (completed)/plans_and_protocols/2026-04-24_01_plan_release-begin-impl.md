# Plan: release-begin-impl Skill + Release Readiness Refactor

Date: 2026-04-24
Task: TASK-PROC-035-06

## Approach

5 parallel agents, no agent commits. Main session commits in 5 groups after all agents complete. Vision verification inline at the end.

## Agent Assignments

| Agent | ACs | Deliverables |
|---|---|---|
| Agent 1 | AC-3, AC-10 | Fix `create_orchestration_task.py` `_GOAL_TEMPLATE` + verify |
| Agent 2 | AC-1 | Rename skill dir + extend Phase 6 |
| Agent 3 | AC-2 | Delete `task-create-code-orchestrator/` |
| Agent 4 | AC-4, AC-5 | `scripts/release_readiness.py` (tested) + `release-status` skill |
| Agent 5 | AC-6–9 | INDEX.md, factory_flows.md, RELEASES.md, REQ-PROC-035, REQ-PROC-036, release/skill.md |

## Commit Strategy (post-agents, inline)

1. `scripts/create_orchestration_task.py` fix
2. `.claude/skills/release-begin-impl/` rename+extend
3. `.claude/skills/task-create-code-orchestrator/` deletion
4. `scripts/release_readiness.py` + `.claude/skills/release-status/`
5. INDEX.md, factory_flows.md, RELEASES.md, requirements updates

## Status

- [ ] Agents launched
- [ ] Agent 1 done
- [ ] Agent 2 done
- [ ] Agent 3 done
- [ ] Agent 4 done
- [ ] Agent 5 done
- [ ] Commits done
- [ ] Vision verification passed
