---
task_id: TASK-PROC-040-01
type: impl
parent_requirement: REQ-PROC-040
urgency: 3
urgency_reason: U3-WORKFLOW-GAP
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-03-27
completed: 2026-03-27
effort: L
created: 2026-03-27
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-03]
scope_description: "Refactor ux-create-flow skill: explicit state machine table + split into 4 focused sub-skills"
release_description: ""
worktree_path: ""
requirements_version:
  commit: uncommitted
  file: ../requirements.md
---

# Goal: Refactor ux-create-flow — Explicit State Machine + Skill Split

## Objective

The `ux-create-flow` skill (`.claude/skills/ux-create-flow/skill.md`) has grown to 583 lines and contains an implicit state machine scattered across its 4 operational modes. This causes errors: AI agents must mentally reconstruct the full state graph from prose, and guard conditions are duplicated with subtle differences.

This task refactors the skill in two coordinated steps:

1. **Extract the state machine**: Create a single canonical state transition table (states, triggers, guards, actions) as the authoritative reference — replacing the scattered prose logic.

2. **Split into 4 focused skills**:
   - `ux-create-flow` — dispatcher only (~35 lines): mode detection + state machine table
   - `ux-flow-draft` — NEW + CONTINUE authoring (~180 lines): guidelines reading, flow creation/iteration, shared steps 6–12
   - `ux-flow-complete` — content complete workflow (~130 lines): CC-0 through CC-G
   - `ux-flow-approve` — joint approval workflow (~55 lines): JA-A through JA-D

## Requirements Summary

REQ-PROC-040 (OR-3, OR-4, OR-6) requires that:
- Flow lifecycle is deterministic, reversible, and auditable (OR-3)
- Cross-flow consistency is tracked and never silently discarded (OR-4)
- Cluster approval ensures mutual consistency (OR-6)

The current monolithic skill undermines these outcomes by embedding state logic in prose. An explicit state machine and focused sub-skills directly implement OR-3/OR-4/OR-6.

Current requirements: ../requirements.md

## Scope

### In Scope
- Rewrite `.claude/skills/ux-create-flow/skill.md` as a pure dispatcher
- Create `.claude/skills/ux-flow-draft/skill.md`
- Create `.claude/skills/ux-flow-complete/skill.md`
- Create `.claude/skills/ux-flow-approve/skill.md`
- Update `.claude/skills/INDEX.md`
- Check `.claude/factory_flows.md` for diagram impact

### Out of Scope
- Changes to the README files in `requirements_user_needs/`
- Changes to flow content or existing flow.md files
- Changes to other skills that reference `ux-create-flow`

## Acceptance Criteria

- [ ] `ux-create-flow` is ≤ 45 lines and contains only mode detection + state machine table + dispatch instructions
- [ ] `ux-flow-draft` contains all authoring logic (NEW + CONTINUE + steps 6–12), ≤ 200 lines
- [ ] `ux-flow-complete` contains CC-0 through CC-G, ≤ 140 lines
- [ ] `ux-flow-approve` contains JA-A through JA-D, ≤ 60 lines
- [ ] State machine table is the single canonical source for all status transitions — no transition logic remains as prose outside the table
- [ ] No logic is duplicated across skills
- [ ] All 4 skills registered in `INDEX.md`
- [ ] `factory_flows.md` checked; updated if needed

## Notes

Opus plan with full analysis and step-by-step execution instructions is in `plans_and_protocols/`.
