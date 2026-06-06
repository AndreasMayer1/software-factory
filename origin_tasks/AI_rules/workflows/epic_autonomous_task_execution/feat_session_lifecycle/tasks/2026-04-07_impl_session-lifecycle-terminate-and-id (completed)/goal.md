---
task_id: TASK-PROC-041-02-01
type: impl
parent_requirement: REQ-PROC-041-02
urgency: 3
urgency_reason: U3-DEV-WORKFLOW
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-04-07
started: 2026-04-07
completed: 2026-04-07
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06]
  sections: []
scope_description: "Create terminate_session.sh, update claude-route skill to write session_id/session_account to goal.md in automated mode, document pre-assigned UUID pattern."
release_description: ""
worktree_path: ""
requirements_version:
  commit: 69c7f72c
  file: ../requirements.md
---

# Goal: Implement Session Lifecycle — Termination Script and Session ID Writing

## Objective

1. Create `scripts/automation/terminate_session.sh` — kills the current Claude Code process cleanly (SIGTERM to the parent process group).
2. Update the `claude-route` skill (`.claude/skills/claude-route/skill.md`): when `CLAUDE_AUTOMATED_MODE=1` is set, write `session_id` and `session_account` to the active task's goal.md frontmatter when marking it `in_progress`.

## Technical Notes (from exploration)

- Session launch confirmed: `claude --dangerously-skip-permissions --session-id <uuid> -p "..."` exits automatically (exit code 0). The `-p` flag is mandatory.
- Account switching: set `CLAUDE_CONFIG_DIR=/home/vscode/.ccs/instances/<account>` in subprocess env.
- Sessions stored at: `~/.ccs/instances/<account>/projects/<project>/<uuid>.jsonl`

## Requirements Summary

REQ-PROC-041-02 at `../requirements.md`.

Current requirements: ../requirements.md

## Scope

### In Scope
- `scripts/automation/terminate_session.sh` — SIGTERM to process group; must not kill unrelated claude sessions
- `.claude/skills/claude-route/skill.md` — add automated-mode block: read `session_id`/`session_account` from env/context, write to goal.md frontmatter
- The `session_id` value is passed in via `CLAUDE_SESSION_ID` env (set by orchestrator before launch alongside `CLAUDE_CONFIG_DIR`)

### Out of Scope
- The orchestrator that generates UUIDs and sets env vars (TASK-PROC-041-01-01)
- Automated-mode CLAUDE.md rules (TASK-PROC-041-03-01)

## Acceptance Criteria

- [ ] `scripts/automation/terminate_session.sh` exists; when run inside a Claude session, exits that session process cleanly (exit code 0)
- [ ] Script uses `kill -TERM` to the process group, not `pkill claude` (avoids killing unrelated sessions)
- [ ] `claude-route` skill writes `session_id` and `session_account` to goal.md when `CLAUDE_AUTOMATED_MODE=1` is detected, as part of the `in_progress` status update step
- [ ] `session_completed_at` timestamp written to goal.md by the skill when a session exits normally

## Notes

- The orchestrator sets `CLAUDE_SESSION_ID=<uuid>` and `CLAUDE_SESSION_ACCOUNT=<account>` in the subprocess env so the AI can read them inside the session.
- `terminate_session.sh` should target `$$` (current shell PID) or the parent process group — test which approach exits cleanly without leaving orphan processes.
