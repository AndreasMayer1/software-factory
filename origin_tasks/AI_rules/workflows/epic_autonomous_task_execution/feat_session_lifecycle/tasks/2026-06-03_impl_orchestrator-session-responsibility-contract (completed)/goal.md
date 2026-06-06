---
task_id: TASK-PROC-041-02-02
type: impl
parent_requirement: REQ-PROC-041-02
urgency: 3
urgency_reason: U3-PROC
impact: 3
impact_reason: I3-ENAB
status: completed
effort: S
created: 2026-06-03
started: 2026-06-03
completed: 2026-06-03
expected_tool_calls: 25
skill_chain_depth: 3
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-07]
  sections: []
scope_description: "Encode the orchestrator↔session responsibility boundary so sessions never self-schedule; the orchestrator owns all scheduling and limit/reset timing."
release_description: ""
opus_recommended: false
requirements_version:
  commit: a9eb6506
  file: ../requirements.md
---

# Goal: Define the orchestrator↔session responsibility contract (no session self-scheduling)

## Objective

Encode an explicit responsibility boundary between the automation orchestrator
(`scripts/automation/orchestrate.py`) and the Claude sessions it launches and resumes,
so a session can never overstep into scheduling/timing decisions that are the
orchestrator's alone.

The session's only valid exits are:
1. `task-complete` (work is done),
2. write `question.md` for a genuine human decision, then terminate,
3. re-emit a rate/session-limit line verbatim, then terminate,
4. state in one line why it cannot make progress now, then terminate.

A session MUST NOT call `ScheduleWakeup`, set a future wakeup, "wait out" a limit, or
reason about reset clocks. Scheduling, rate-limit/reset timing, account rotation, and
*when* a task runs or resumes belong exclusively to the orchestrator.

## Background

Root-cause incident — **TASK-FUNC-007-01-05** (ui-scribble-iterate pilot):

- The reviewer subagents hit a session limit that reset at **17:50**.
- The orchestrator's *account* limit cleared at **17:05**, so it resumed the task early
  (17:05 / 17:12 / 17:17).
- On each early resume the session checked the clock, saw it was before 17:50, declined
  to re-spawn the reviewers, and called `ScheduleWakeup` to defer itself to ~17:55.
- Those were ~2-minute no-op resumes. The orchestrator counted three of them as resume
  attempts and tripped its per-run cap:
  `WARNING: resume of TASK-FUNC-007-01-05 exhausted 3 attempts — giving up this run`.
- The session's own 17:55 wakeup was a session-local timer the orchestrator never
  honored once it abandoned the task; the account then rate-limited until 22:05.

The session overstepped: it second-guessed the orchestrator's timing instead of simply
reporting status and terminating. The existing `claude-automated-mode` rate-limit rule
already says the right thing for the *original-spawn* case (re-emit + terminate), but it
does not cover the *resume* case, and nothing in the resume prompt or the skill forbids
self-scheduling.

For complete requirements at task creation time:
```
git show a9eb6506:requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/feat_session_lifecycle/requirements.md
```

Current requirements: ../requirements.md (AC-07 + "No Self-Scheduling" behavior section
were added as part of this task's grounding.)

## Scope

### In Scope

1. **`.claude/skills/claude-automated-mode/SKILL.md`** (edit via `claude-modify-skill`):
   - Add an explicit **"Responsibility boundary — orchestrator vs session"** section:
     orchestrator owns scheduling / limit timing / account rotation / when to run &
     resume; session owns task work + reporting *why* it cannot proceed; session never
     self-schedules.
   - Extend **"When a Spawned Agent Hits a Rate / Session Limit"** to also cover the
     **resume** case: if the session is resumed but a limit it depends on is still active
     (or it otherwise cannot advance yet), it re-emits the limit line / states the blocker
     and terminates — it does NOT call `ScheduleWakeup`.

2. **`scripts/automation/orchestrate.py`** (edit via `claude-write-script`):
   - The resume prompt (~line 2994). Add a 4th explicit branch and a prohibition:
     *"Do not schedule, wait, or reason about reset times — scheduling is the
     orchestrator's responsibility. If you cannot make progress now, state why in one line
     and terminate."*

3. Keep the two surfaces consistent with the AC-07 wording in `requirements.md`.

### Out of Scope

- Changing the orchestrator's 3-attempt resume-exhaustion counter or its early-resume
  cadence. The primary fix is removing the session's self-scheduling. Whether a session
  that re-armed itself should be treated as "deferred until T" rather than a consumed
  attempt is noted below as a follow-up consideration, not implemented here.
- Any Dart/`lib/` change. This is a process/automation/docs task.

## Acceptance Criteria

- [x] `claude-automated-mode/SKILL.md` has an explicit orchestrator-vs-session
      responsibility-boundary section, modified via `claude-modify-skill`.
- [x] The skill's rate-limit rule explicitly covers the resume case and forbids
      `ScheduleWakeup` / self-deferral.
- [x] The `orchestrate.py` resume prompt names the 4th exit and prohibits
      self-scheduling/clock-reasoning, edited via `claude-write-script` (Python gates pass).
- [x] Both surfaces are consistent with REQ-PROC-041-02 AC-07.
- [x] No `ScheduleWakeup`/self-scheduling instruction remains reachable for automated
      sessions in the touched files.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Follow-up consideration (not in scope): the orchestrator could treat a session that
exits having explicitly re-armed a future wakeup as "deferred until T" rather than a
consumed resume attempt. With self-scheduling removed this should no longer occur, but
if a hardening layer is wanted, file it as a separate `feat_session_orchestrator`
(REQ-PROC-041-01) task.
