# Plan: skills_used: Protocol Instrumentation (IMPL-H)

Date: 2026-05-28  
Task: TASK-PROC-006-13

## Design

### Where skills_used: lives
YAML frontmatter at top of `plans_and_protocols/*_protocol.md`. Initialized to
`skills_used: []` by **claude-log** when creating a new protocol file.
Populated at end-of-task by **task-complete** (canonical writer).

### How it is populated
`task-complete` step 3.4b: the agent executing task-complete can see Skill tool
calls in its session context — it lists all skills invoked during the session.
Best-effort; at minimum includes `task-complete` and `claude-commit`.

### Monitor Stage 2 enablement
`monitor_skill_change_first_use.py`:
- `_STAGE2_ENABLED = True`
- `_parse_skills_used(content) -> list[str]`: parse frontmatter YAML
- `_stage2_used_skills(now) -> set[str]`: find recent protocol files via git,
  parse skills_used, map names to `.claude/skills/<name>/SKILL.md` paths

### Files changed
1. `scripts/optimize/monitor_skill_change_first_use.py` — Stage 2 implementation
2. `scripts/tests/test_monitor_skill_change_first_use.py` — test updates
3. `.claude/skills/claude-log/SKILL.md` — init frontmatter on create
4. `.claude/skills/task-complete/SKILL.md` — step 3.4b to write skills_used:

## Fixture test
This task's own protocol.md (written by task-complete) is the fixture: it will
contain `skills_used:` including `task-complete` and `claude-log`. When the
post-commit monitor sweep runs, Stage 2 fires for those edited skill paths.
