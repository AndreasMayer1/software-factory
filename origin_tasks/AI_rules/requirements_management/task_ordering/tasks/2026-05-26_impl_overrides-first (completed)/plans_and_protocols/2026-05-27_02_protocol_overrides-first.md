# Protocol: overrides-first (TASK-PROC-042-12)

## 2026-05-27T09:20
**Agent**: claude-log (main session — task-resolve inline)
**Agent ID**: a08fa50f90df02118
**Action**: Implemented TASK-PROC-042-12 — refactored priority override logic in next_tasks.py and updated override file header.

Changes:
1. `scripts/tasks/next_tasks.py` — replaced prepend-override logic with blocking override:
   - While any non-terminal override task exists: `ranked = override_runnable` (only override tasks surfaced)
   - If all pending override tasks are blocked: print informational message (non-task-format) + sys.exit(0)
   - When all override tasks are terminal: fall through to normal ranking
2. `scripts/tests/test_next_tasks.py` — added 3 regression tests:
   - `test_override_blocks_normal_tasks`: runnable override → normal task suppressed
   - `test_override_all_blocked_no_runnable`: all-blocked → override_runnable is empty
   - `test_override_terminal_resumes_normal`: terminal override → override_nonterminal is empty
3. `.claude/task_ordering_priority_override.txt` — added 16-line behavior-description comment at top explaining blocking semantics, cleanup trigger, and orchestrator safety.

**Outcome**: PASS — G1 ✅ G2 ✅ G3 ✅ (pre-existing `test_no_session_id_when_empty` failure in unmodified `test_orchestrate.py`, caused by CLAUDE_SESSION_ID in live session env) G4 ✅ G5 ✅

**Next Step**: Invoke `doc-update-guidelines` then `task-complete`
