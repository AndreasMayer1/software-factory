# Protocol: TASK-PROC-058-08 Align Skill with Implemented Scripts

**Date**: 2026-05-26
**Agent**: inline (main session)

## Findings Summary

| Finding | File | Status |
|---------|------|--------|
| D | SKILL.md Phase 1.5.1 — wrong script name | Fix: `detect_cross_ref_gaps.py` → `check_cross_refs.py` |
| E | SKILL.md Phase 1.5.1 — wrong invocation | Fix: `--target <path> --json` → positional `<path>` (JSON default) |
| F | `check_cross_refs.py` stop-words | Fix: add User Story boilerplate ("user", "want", "story", "developer", "stakeholder") to `_STOP_WORDS` |
| G | SKILL.md Phase 5 — wrong `--task-type` values | Fix: `impl|mixed` → `implement|verify|scribble|scribble_to_flutter` |
| H | `create_orchestration_task.py` skill routing | Fix: `verify` → `task-create`; non-code `impl` → `task-create`; code `impl` → `task-create-code` |

## Pre-fix baseline

- REQ-PROC-001 without --terms: 129 candidates (terms: User, want, Story, developer)
- REQ-PROC-058 without --terms: 73 candidates (terms: Implementation, Task, Planning, Quality)

## Plan

1. Edit SKILL.md (Findings D, E, G, H-text)
2. claude-write-script for check_cross_refs.py (Finding F)
3. claude-write-script for create_orchestration_task.py (Finding H)
4. Verify: re-run check_cross_refs on REQ-PROC-001 without --terms; confirm ≤ 30 candidates, REQ-PROC-008 + REQ-PROC-058 still found
5. verify-quality → task-complete

## Routing decisions (Finding H)

In `_build_ac_block`, per-task `task_type` field → creation skill:
- `scribble` → `ui-create-scribble`
- `verify` or `verification` → `task-create`
- `scribble_to_flutter` → `task-create-code`
- `explore` → `task-create`
- `impl`/`implement` with "lib/" or "test/" or "integration_test/" in `implementation_notes` → `task-create-code`
- `impl`/`implement` (no lib refs) → `task-create`
