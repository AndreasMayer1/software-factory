---
task_id: TASK-PROC-041-01-02
type: impl
parent_requirement: REQ-PROC-041-01
urgency: 3
urgency_reason: U3-WF
impact: 3
impact_reason: I3-DEV
status: completed
completed: 2026-04-08
effort: M
created: 2026-04-08
after: [TASK-PROC-041-01-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-05, AC-11, AC-12, AC-14, AC-15]
  sections: []
scope_description: "Improve orchestrate.py and claude-autorun skill: fix status check, stdout buffering, permanent account error detection, report excerpt size, start_time reset, and in_progress task resume logic"
release_description: ""
requirements_version:
  commit: 9e3c3ae7
  file: ../requirements.md
---

# Goal: Improve Session Orchestrator — Reliability & Resume

## Objective

Apply a set of targeted improvements to `scripts/automation/orchestrate.py` and `.claude/skills/claude-autorun/skill.md` based on observed failures across multiple automation runs.

The full analysis and rationale is in:
`automation/plans/2026-04-08_01_opus_plan_automation_improvements.md`

## Scope

### In Scope (Phase 1 — Quick Wins)
1. **Report excerpt size**: `cleaned[:500]` → `cleaned[:1500]` (two call sites: session record and resume record)
2. **Reset `start_time` per run**: Remove the `if not state.get("start_time"):` guard; always write current datetime
3. **Permanent account error detection**: Detect "does not have access" (non-rate-limit failure); disable account for the run; skip in `next_available_account()`
4. **Status check fix** (skill): Replace `state.json` `running` field check with PID-from-sentinel check (`cat automation/.automated_mode` → `kill -0 $PID`)
5. **Python stdout buffering fix** (skill): Launch with `python3 -u` instead of `python3`

### In Scope (Phase 2 — Core Fix)
6. **In_progress task resume**: Before launching a "Do next task" session, detect any task with `status: in_progress` + `session_id` + no pending unanswered `question.md` → resume that session via `--resume <session_id>` with a context prompt instead of starting fresh

### Out of Scope
- Changing "Do next task" / `claude-route` skill behavior
- Auto-answering questions in automated mode
- Parallel session execution
- Timeout/watchdog for hung sessions

## Acceptance Criteria

- [ ] `autorun status` correctly reports RUNNING when orchestrator PID from `.automated_mode` is alive
- [ ] `orchestrate.log` shows real-time output during a run (no buffering delay)
- [ ] An account returning "does not have access" is skipped for the rest of the run (not rotated back in)
- [ ] Report per-session excerpts show up to 1500 chars
- [ ] `state.json` `start_time` reflects the current run's start after each launch
- [ ] An in_progress task with a `session_id` is resumed via `--resume` on the next orchestrator run, not re-encountered by "Do next task"

## Implementation Notes

See `automation/plans/2026-04-08_01_opus_plan_automation_improvements.md` for:
- Full scenario map (7 scenarios A–G)
- Exact line references in `orchestrate.py`
- New `find_resumable_session()` function design
- Main loop insertion point for Phase 2

Key files:
- `scripts/automation/orchestrate.py`
- `.claude/skills/claude-autorun/skill.md`
