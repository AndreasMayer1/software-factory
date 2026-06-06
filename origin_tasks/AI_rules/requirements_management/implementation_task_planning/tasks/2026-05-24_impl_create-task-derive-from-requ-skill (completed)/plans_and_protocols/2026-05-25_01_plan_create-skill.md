# Plan: Create task-derive-from-requ Skill

Date: 2026-05-25
Task: TASK-PROC-058-02

## Deliverables

1. `.claude/skills/task-derive-from-requ/SKILL.md` — the 6-phase decomposition skill
2. Update `.claude/skills/claude-route/SKILL.md` — add detection pattern for "decompose requirement" goal shapes
3. Update `.claude/skills/INDEX.md` — add new skill entry in task-* section

## Design Decisions

### No new scripts in this task
The skill references existing scripts: `coverage_report.py`, `parse_task_creation_plan.py`, `create_orchestration_task.py`, `allocate_task_id.py`, `propose_after.py`. Supporting scripts (`plan_validate.py`, `coverage_matrix.py`) are candidates for future extraction but not blocking — the skill can operate with inline logic + existing scripts.

### Skill body target: ~120 lines
The skill is complex (6 phases, 2 modes, automated mode). Token efficiency requires tight writing. Tables over prose. No examples when pattern is clear from rules.

### Mode selection is automatic
Quick mode: 1-2 tasks, ≤ 1 code task, user names ACs explicitly. Full mode: default for ≥ 3 uncovered ACs or new requirements with zero tasks.

### Agent strategy
- Phase 1: Gather agent for > 3 related requirements
- Phase 5: Orchestration task (via create_orchestration_task.py) for > 6 tasks or automated mode

### claude-route integration
Add detection before the "Any other → task-resolve" fallback:
- Goal body contains "decompose", "derive tasks", "plan tasks for", "create tasks for" + references a requirement path → `task-derive-from-requ`

## Implementation Steps

1. Create `.claude/skills/task-derive-from-requ/` directory
2. Write SKILL.md with all 6 phases, mode selection, automated mode, cross-ref gate
3. Update claude-route SKILL.md — add detection pattern at step 4
4. Update INDEX.md — add entry in task-* section
5. Verify: skill file exists, INDEX.md entry present, claude-route pattern present
