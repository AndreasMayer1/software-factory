---
task_id: TASK-PROC-041-01-04
type: explore
parent_requirement: REQ-PROC-041-01
urgency: 4
urgency_reason: U4-DEV-PRODUCTIVITY
impact: 4
impact_reason: I4-QUALITY
status: completed
completed: 2026-04-10
effort: M
created: 2026-04-10
started: 2026-04-10
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Define expected orchestrator behavior and monitoring criteria for all edge cases; decide where to document so the monitoring LLM knows what to check"
release_description: ""
requirements_version:
  commit: 97f1418d
  file: ../requirements.md
---

# Goal: Define Orchestrator Monitoring Criteria and Expected Behavior

## Objective

The automation orchestrator now has a monitoring mechanism (cron-based LLM check every 15 min via `claude-autorun` skill). However, during today's run we failed to detect that sessions were being wasted re-asking the same question — because we had no objective criteria for what "working correctly" looks like.

This task defines:
1. What constitutes correct orchestrator behavior for every significant scenario
2. What constitutes a warning / anomaly worth flagging
3. Where to document these criteria so the monitoring LLM can use them reliably

## Background

### What happened today (2026-04-10)
- Session 1: completed TASK-FUNC-007-14 verification, wrote `question.md` awaiting user answer
- Session 2: correctly worked on a different task (TASK-FUNC-017-02) — completed ✓
- Session 3: gmail2 perm error — correctly handled ✓
- Sessions 4 & 5: **both landed on TASK-FUNC-007-14 again**, re-asked the same question, wasted slots
- Monitoring did not flag this as abnormal — because there were no criteria defining it as abnormal

### Root cause of the wasted sessions (already fixed)
The orchestrator correctly logged "TASK-FUNC-007-14 skipped (unanswered question)" but did NOT pass this information to the session prompt. The Claude agent then picked up the highest-priority in_progress task anyway. Fixed in `run_normal_session()` — blocked task IDs are now injected into the session prompt.

### What's still missing
Criteria that the monitoring LLM can use to evaluate whether a run is healthy.

## Scope

### In Scope
- Define expected behavior for each orchestrator state/scenario:
  - Normal task progression
  - Task with pending question (blocked)
  - Session that exits 0 but task remains in_progress
  - Resume path (in_progress task with session_id)
  - Rate limit / account perm error
  - max-tasks reached
  - All accounts exhausted
- Define anomaly signals (what the monitoring LLM should flag)
- Decide WHERE to document: options include:
  - In the `claude-autorun` skill itself (loaded each monitoring check)
  - In a dedicated `automation/MONITORING_CRITERIA.md` file
  - As additional ACs in `REQ-PROC-041-01`
  - In the cron prompt directly
- Evaluate tradeoffs of each location (token cost, discoverability, freshness)
- Produce a concrete recommendation with rationale

### Out of Scope
- Implementing any new orchestrator features
- Changing monitoring frequency or mechanism

## Acceptance Criteria

- [ ] All significant orchestrator scenarios documented with expected behavior
- [ ] Anomaly signals defined (what monitoring LLM should flag vs. ignore)
- [ ] Decision made on where to document criteria (with rationale)
- [ ] Requirements updated to reflect new monitoring AC (if applicable)
- [ ] Recommendation presented to user before any requirements are modified
