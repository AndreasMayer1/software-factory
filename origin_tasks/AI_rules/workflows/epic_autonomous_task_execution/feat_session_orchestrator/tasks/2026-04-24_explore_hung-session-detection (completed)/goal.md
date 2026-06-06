---
task_id: TASK-PROC-041-01-07
type: explore
parent_requirement: REQ-PROC-041-01
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-RELIABILITY
status: completed
completed: 2026-04-24
started: 2026-04-24
effort: M
created: 2026-04-24
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Investigate how the orchestrator can autonomously detect and recover from hung Claude sessions"
release_description: ""
opus_recommended: true   # reason: cross-cutting explore with explicit trade-off analysis — evaluate detection approaches, decide thresholds, architectural decision for orchestrator internals
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: 3f15ce87
  file: ../requirements.md
---

# Goal: Hung Session Detection & Recovery in the Orchestrator

## Objective

Investigate how `scripts/automation/orchestrate.py` can autonomously detect when a spawned Claude session has stopped making progress (hung, not just slow), and recover from it — without relying on the LLM monitoring cron job.

The detection and recovery logic must live inside the orchestrator itself so it works even when no human or monitoring agent is watching.

## Background

**Observed incident (2026-04-24)**: Session `1ce0fdc2` (account web) was launched at 21:23 on 2026-04-23 and was still running 13+ hours later. The orchestrator log showed no activity (expected — it only logs when it acts). The session JSONL (`/home/vscode/.ccs/shared/context-groups/default/projects/.../<uuid>.jsonl`) had not grown since 10:08, but the `claude` child process (PID 67171) was alive with 4 active `dart/bash` child processes — meaning the session was genuinely working (running Flutter tests), not hung.

**Key insight**: The JSONL does not grow while Claude is waiting for tool results. Child processes under the `claude` PID are the reliable liveness indicator during tool execution.

## Scope

### In Scope
- Defining what "hung" means for an automated Claude session (vs. slow/legitimately long)
- Evaluating detection approaches: child process presence, JSONL growth rate, session timeout, combination
- Defining safe recovery: how to kill the stuck session without corrupting orchestrator state, and how to ensure the orchestrator resumes the task correctly in the next loop iteration
- Proposing concrete thresholds (e.g. "no child processes AND no JSONL growth for N minutes = hung")
- Identifying edge cases (rate-limit waits, very long tests, analysis server startup)
- Producing a requirements update for `feat_session_orchestrator/requirements.md` and an impl task goal

### Out of Scope
- LLM-based monitoring (cron job) — detection must be in-process
- Parallel session execution
- Changes to session launch or task selection logic

## Acceptance Criteria

- [ ] At least two detection approaches evaluated with pros/cons
- [ ] A recommended detection strategy with concrete thresholds documented
- [ ] Edge cases identified (long tests, rate-limit wait, dart analysis server startup)
- [ ] Recovery strategy defined: what to kill, in what order, how orchestrator state is left
- [ ] `feat_session_orchestrator/requirements.md` updated with new ACs covering the feature
- [ ] An impl task goal.md drafted (or created) to implement the chosen approach

## Notes

- Orchestrator subprocess: `subprocess.run()` or `Popen`? Check actual launch code in `scripts/automation/orchestrate.py` — timeout parameter may already be available.
- JSONL path pattern: `/home/vscode/.ccs/shared/context-groups/default/projects/-workspaces-private-mood-tracker-flutter-app/<uuid>.jsonl`
- Child process check: `ps --ppid <claude_pid>` — presence of `bash`/`dart` children = tool call in progress
- Consider: a configurable `--session-timeout` flag on the orchestrator as the hard upper bound
