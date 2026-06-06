# Plan Overview: TASK-PROC-035-08
## Distributed Release Pipeline Redesign

Date: 2026-04-25 | Status: planning

Source of truth: `tasks/2026-04-25_explore_release-active-status-analysis (completed)/plans_and_protocols/protocol.md`

---

## Execution Strategy

5 parallel planning agents → per-group plan files → sequential implementation agents.

## Groups

| Group | Deliverables | Dependencies | Plan file |
|-------|-------------|--------------|-----------|
| 1 | 7 new Python scripts | none | plan_group1.md |
| 2 | create_orchestration_task.py changes + release-begin-impl rewrite | Group 1 scripts must exist | plan_group2.md |
| 3 | Orchestration task template + task-create-code zero-mode | Group 2 must be done | plan_group3.md |
| 4 | release-begin-impl-finalize (new) + claude-automated-mode simplification | Groups 1-3 done | plan_group4.md |
| 5 | CLAUDE.md §7 context-window rule | none | plan_group5.md |

## Implementation Order

```
Phase A: Groups 1 + 5 in parallel (both independent)
Phase B: Group 2 (after Group 1)
Phase C: Group 3 (after Group 2)
Phase D: Group 4 (after Groups 1-3)
```

## Verification Checklist (from goal.md)

- V1: Unit verification per Group 1 script
- V2: Regression — existing autorun Case D unchanged
- V3: Integration — Phase 6 dry-run sequence
- V4: Chain integrity (3-step ACs)
- V5: Skill structure check release-begin-impl-finalize
- V6: Transition safety Case A guard
- V7: CLAUDE.md rule present
