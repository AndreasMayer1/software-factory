# Protocol: Implementation of next_tasks.py Prioritization Fix

**Date**: 2026-04-22
**Agent**: implementation-engineer (claude-sonnet-4-6)
**Status**: COMPLETE

## What was found on arrival

All changes to `scripts/next_tasks.py` were already applied:
- `writes_requirements` field loaded in `load_tasks()` (line 239)
- WHY comment + updated sort key in `rank_tasks()` (lines 345-353)
- WHY comment + updated sort key in `rank_tasks_by_package()` (lines 369-377)
- Docstring updated to reflect 5-tier ranking (lines 5-11)

Both templates in `.claude/skills/requ-derive-from-flow/skill.md` already had `writes_requirements: true`:
- Line 530 (exploration task template)
- Line 677 (verification task template)

## What was implemented in this session

### Step 3: `scripts/validate_meta.py`

Added validation for `writes_requirements` field in `validate_tasks()` after the blocked-task check (lines 554-569):
- Accepts `true`/`false` (boolean only; errors on non-boolean)
- Warns if `writes_requirements: true` is set on a non-explore task (semantic mismatch)
- Does not flag absence of the field (it is optional, defaults to false)

### Step 4: Audit of other requirement-writing skills

Grep result: `requ-apply-market` — no task creation, no explore template. `requ-verify-flow-coverage` — creates tasks but delegates to `requ-derive-from-flow` templates (already updated). No other skills need changes.

### Step 6: `task-create` skill documentation

Added `writes_requirements: false` with explanatory comment to the goal.md frontmatter template in `.claude/skills/task-create/skill.md`, so users creating manual explore tasks know the flag exists.

## Verification results

`python3 scripts/next_tasks.py` output (top task):
```
1. [TASK-FUNC-007-04-08] spike-cleanup
   Release: unassigned | Type: impl | Status: pending | Priority: 22 | Req: REQ-FUNC-007-04
```

`TASK-FUNC-007-04-08` (impl spike-cleanup for "Adaptive Scanner Settings") is now rank 1, confirming the fix works. Forward-looking explores (TASK-PROC-027-34, etc.) are correctly ranked below.

`python3 scripts/validate_meta.py` — no new errors or warnings from `writes_requirements`. Pre-existing errors/warnings (103 errors, 230 warnings) are unrelated to this change.

## Files modified

- `/workspaces/private_mood_tracker/flutter_app/scripts/validate_meta.py` — added `writes_requirements` validation
- `/workspaces/private_mood_tracker/flutter_app/.claude/skills/task-create/skill.md` — added `writes_requirements` to frontmatter template

## Files confirmed already correct (no changes needed)

- `/workspaces/private_mood_tracker/flutter_app/scripts/next_tasks.py`
- `/workspaces/private_mood_tracker/flutter_app/.claude/skills/requ-derive-from-flow/skill.md`
