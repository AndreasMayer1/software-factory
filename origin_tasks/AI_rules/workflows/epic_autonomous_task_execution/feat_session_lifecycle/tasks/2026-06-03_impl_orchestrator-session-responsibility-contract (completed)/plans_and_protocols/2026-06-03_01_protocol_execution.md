---
skills_used:
  - claude-route
  - task-resolve
  - claude-modify-skill
  - claude-write-script
  - claude-autorun
  - claude-log
  - task-complete
  - claude-commit
---

# Execution Protocol — TASK-PROC-041-02-02

**Date:** 2026-06-03
**Skill chain:** claude-route → task-resolve (inline) → claude-modify-skill, claude-write-script
**Mode:** interactive (CLAUDE_AUTOMATED_MODE unset; only the flagfile present)

## Trigger

Investigation of why TASK-FUNC-007-01-05 never ran to completion. Root cause of the
repeated resume "failures": on early resume (orchestrator account limit cleared 17:05,
but the reviewer subagents' limit reset 17:50) the session called `ScheduleWakeup` to
defer itself to ~17:55. Three such ~2-minute no-op resumes tripped the orchestrator's
per-run 3-attempt cap; the session-local wakeup was never honored. The session
overstepped — scheduling/limit-timing is the orchestrator's job.

## Requirement grounding (Case B gap-fill)

`feat_session_lifecycle/requirements.md` (REQ-PROC-041-02):
- Added **AC-07** (session never self-schedules; takes one of four valid exits; orchestrator owns scheduling & limit/reset timing).
- Added behavior subsection **"No Self-Scheduling (Orchestrator Owns Timing)"** with the four valid exits and the prohibition, citing the TASK-FUNC-007-01-05 incident.
- `updated: 2026-06-03`, trackable_items += AC-07.

## Deliverables

1. **`.claude/skills/claude-automated-mode/SKILL.md`** (via claude-modify-skill):
   - New section **"Responsibility Boundary — Orchestrator vs Session"** (after "The One Rule"): orchestrator-owns / session-owns split, four valid exits, explicit `ScheduleWakeup` / self-deferral / clock-reasoning prohibition.
   - Extended **"When a Spawned Agent Hits a Rate / Session Limit"** with an *on-resume* paragraph: re-attempt immediately; if still limited, re-emit + terminate; never `ScheduleWakeup`.
   - description unchanged → no INDEX.md / factory_flows.md / contract.yaml sync; no new artifact tokens or user_input_gates.

2. **`scripts/automation/orchestrate.py`** (via claude-write-script):
   - Resume prompt (~line 2994) gained a 4th branch ("if you cannot make progress now … state in one line why and terminate") + prohibition ("Do not schedule, wait, or reason about reset times — scheduling is the orchestrator's responsibility and it will resume you again").
   - Prompt-literal text change only; no control-flow/branch/return change → non-behavioral exemption, no new regression test. No existing test asserts the prompt text (tests mock `run_resume_session`).
   - **Python gates: all 5 PASS** (G1 lint, G2 type, G3 tests 1096 passed, G4 no-handrolled, G5 print).
   - No CLAUDE.md §11 change (internal automation prompt, not a generated file or grep-replacement script).

## Out of scope / follow-up

Did **not** change the orchestrator's 3-attempt exhaustion counter or early-resume
cadence. With self-scheduling removed the no-op-resume pattern should not recur; if a
hardening layer is wanted (treat a re-armed session as "deferred until T"), file a
separate feat_session_orchestrator (REQ-PROC-041-01) task.

## Session housekeeping

Per developer instruction, the automation orchestrator was stopped before commit
(`/autorun stop` → `stop_requested=true` + SIGINT; log: "Stopped. Reason: manual"
18:32:23). Unrelated working-tree changes from the orchestrator's optimize sessions
were left untouched; only this task's four paths were committed.
