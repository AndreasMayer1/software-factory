---
task_id: TASK-PROC-006-08
type: impl
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-28
started: 2026-05-28
completed: 2026-05-28
session_completed_at: 2026-05-28T00:18:36Z
after: [TASK-PROC-006-07]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-05]
  sections: [SEC-01]
scope_description: "Implement scripts/optimize/monitor_repeated_question.py, monitor_skill_change_reverted.py, monitor_skill_change_first_use.py (Stage 1), monitor_periodic_counter.py, and scripts/optimize/run_monitors.py. All standalone pure-Python; total runtime <2s; idempotent per cooldown window."
release_description: ""
opus_recommended: true   # reason: multi-script standalone-exec contract + G-INV-2 invariant
writes_requirements: false
worktree_path: ""
target_package: "claude-optimize"
backlog_id: IMPL-C
requirements_version:
  commit: eabdeaf0
  file: ../requirements.md
session_id: 8cad6c68-bfc3-421d-8029-467558e1da39
session_account: gmail2
---
# Goal: Monitor Scripts and Runner (IMPL-C)

## Objective

Build the cheap structural-signal monitors that detect improvement-candidate
events. They run as plain Python after every successful `task-complete`
invocation (wired by IMPL-F), write JSON event files to
`.factory/optimize/events/`, and are not callable as tools by any agent (G-INV-2).

## Requirements Summary

Reference: REQ-PROC-006 §"Monitor-Based Detection", §"Monitor Taxonomy" (SEC-01),
G-INV-2 (commit eabdeaf0). The taxonomy table names four monitors with their
signals, confidence levels, event types, and cooldown windows.

For complete requirements at task creation time:
```
git show eabdeaf0:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- `scripts/optimize/monitor_repeated_question.py` — fires when the same pending-question fingerprint repeats ≥3 times; 14-day cooldown.
- `scripts/optimize/monitor_skill_change_reverted.py` — fires when a skill file edited then substantially undone within 48 hours.
- `scripts/optimize/monitor_skill_change_first_use.py` — Stage 1 only (fires on skill-file commit alone). Stage 2 enabled after IMPL-H (TASK-PROC-006-13) lands the `skills_used:` protocol field; ship a TODO comment pointing to IMPL-H and a no-op Stage 2 code path.
- `scripts/optimize/monitor_periodic_counter.py` — fires after N completed tasks since last optimize run (default N=10 from state.json).
- `scripts/optimize/run_monitors.py` — orchestrator: invokes all four monitors sequentially, aggregates exit codes, total runtime target <2 seconds.
- Each monitor consumes only committed project-local sources (runs.tsv, git history, protocol files, question fingerprints). No session-JSONL reads in routine operation.
- Each monitor is idempotent: refuses to write a duplicate event for the same trigger within its cooldown window.

### Out of Scope

- Wiring run_monitors.py into task-complete (IMPL-F / TASK-PROC-006-11).
- Stage 2 logic for first-use (depends on IMPL-H).
- The producer skill that consumes events (IMPL-E / TASK-PROC-006-10).

## Acceptance Criteria

- [x] Four monitor scripts and one runner exist under `scripts/optimize/`.
- [x] No monitor is registered as a callable tool in any skill or agent definition (grep .claude/skills/**/SKILL.md for the monitor names — must not appear as `tools:` entries).
- [x] No monitor reads session JSONL in routine operation (verified by inspection: no paths under `.ccs/`, `~/.claude/`, or any per-account memory tree).
- [x] Each monitor writes a structured JSON event file to `.factory/optimize/events/` when fired (schema documented inline at the top of run_monitors.py).
- [x] Idempotency: running each monitor twice within the cooldown window writes only one event (covered by a unit test per monitor).
- [x] run_monitors.py completes in <2 seconds on an empty event queue (measured by a microbenchmark in the test suite or a CLI flag).

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TASK-PROC-006-07 (IMPL-B) | pending | Needs `.factory/optimize/events/` directory + runs.tsv stub |

## Notes

Concept docs (for context): round-4 synthesis §6 IMPL-C; round-3 architecture
for monitor design. The "Stage 1 only" approach for first-use is explicit in
SEC-01: "Both stages are valid operational modes."

G-INV-2 (monitors not on any tool surface) is a hard constraint — there is no
configuration that exposes them as tools. The test plan must include a static
grep check.
