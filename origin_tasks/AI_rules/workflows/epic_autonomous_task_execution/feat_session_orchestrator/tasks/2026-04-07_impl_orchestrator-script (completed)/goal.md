---
task_id: TASK-PROC-041-01-01
type: impl
parent_requirement: REQ-PROC-041-01
urgency: 3
urgency_reason: U3-DEV-WORKFLOW
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-04-07
effort: L
created: 2026-04-07
started: 2026-04-07
after: [TASK-PROC-041-02-01, TASK-PROC-041-03-01, TASK-PROC-041-04-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13]
  sections: []
scope_description: "Create scripts/automation/orchestrate.py with round-robin account rotation, rate-limit detection, scheduled/manual stop, per-session output capture, report generation, and feedback-resume detection."
release_description: ""
worktree_path: ""
requirements_version:
  commit: 69c7f72c
  file: ../requirements.md
---

# Goal: Implement Session Orchestrator Script

## Objective

Create `scripts/automation/orchestrate.py` — the main orchestration script that:
- Launches `claude` sessions sequentially with per-account `CLAUDE_CONFIG_DIR` rotation
- Handles rate limits (parse reset time, wait, retry with next account)
- Supports endless and scheduled (`--stop-at`) termination modes
- Responds to manual stop via `automation/.stop-requested` file or SIGTERM
- Captures and cleans session stdout (strips hook reminder footer)
- Writes per-session output to `automation/session_outputs/<uuid>.txt`
- Writes a Markdown report on termination
- Detects and resumes feedback-paused sessions when `answer.md` is present
- Persists state to `automation/state.json`

## Technical Notes (from exploration — tested and confirmed)

- **Launch command**: `claude --dangerously-skip-permissions --session-id <uuid> -p "Do next task"` with `CLAUDE_CONFIG_DIR` and `CLAUDE_AUTOMATED_MODE=1` in env
- **NOT** `ccs <account> ...` — CCS nesting fails from inside a Claude session ("Profile not configured for delegation")
- **`-p` auto-exits**: exit code 0 on success, exit code 1 on rate limit
- **Rate limit output**: exit code 1 + stdout contains "hit your limit · resets HH:MM(am/pm) (Timezone)"
- **stdout capture**: `subprocess.run(..., capture_output=True, text=True)` — response in `result.stdout`
- **Hook reminder footer** to strip: regex `\n---\n\*\*Reminder:.*` (re.DOTALL)
- **Resume**: `claude --dangerously-skip-permissions --resume <uuid> -p "<answer>"` with matching `CLAUDE_CONFIG_DIR`
- **Session storage**: `~/.ccs/instances/<account>/projects/<project>/<uuid>.jsonl`
- **`--session-id`**: confirmed to name the JSONL file with the pre-assigned UUID

## Requirements Summary

REQ-PROC-041-01 at `../requirements.md`.

Current requirements: ../requirements.md

## Scope

### In Scope
- `scripts/automation/orchestrate.py` (main script)
- `automation/state.json` (runtime state, not committed)
- `automation/session_outputs/` folder (per-session captured output)
- `automation/reports/` folder (termination reports)
- `automation/.automated_mode` sentinel file lifecycle (create on start, delete in finally)
- `automation/.stop-requested` detection

### Out of Scope
- `scripts/automation/terminate_session.sh` (TASK-PROC-041-02-01)
- CLAUDE.md rule (TASK-PROC-041-03-01)
- `automation/pending_feedback/` folder structure (TASK-PROC-041-04-01)

## Acceptance Criteria

- [ ] `scripts/automation/orchestrate.py` runs with `python3 scripts/automation/orchestrate.py`
- [ ] Accepts `--accounts <csv>` (default `gmail,web,gmail2`), `--stop-at "YYYY-MM-DD HH:MM"`, `--min-wait-seconds N`
- [ ] Each session launched via `subprocess.run(["claude", "--dangerously-skip-permissions", "--session-id", uuid, "-p", "Do next task"], capture_output=True, text=True, env=env)` with `CLAUDE_CONFIG_DIR` and `CLAUDE_AUTOMATED_MODE=1` set
- [ ] Accounts rotate round-robin; index persisted in `automation/state.json`
- [ ] Rate limit (exit code 1 + "hit your limit" in stdout) → parse reset time → wait until reset + 5 min → continue with next account
- [ ] At most one session runs at a time (subprocess.run is blocking)
- [ ] UUID pre-generated, written to active task goal.md, passed via `--session-id`
- [ ] `automation/.stop-requested` file or SIGTERM → stop after current session completes
- [ ] `--stop-at` datetime reached → stop after current session completes
- [ ] Each session stdout stripped of hook footer and saved to `automation/session_outputs/<uuid>.txt`
- [ ] Report written to `automation/reports/YYYY-MM-DD_HH-MM_report.md` on any termination (script-only, no LLM)
- [ ] State persisted to `automation/state.json`; re-read on restart
- [ ] Tasks with `answer.md` in `pending_feedback/` are resumed via `--resume <session-id>` with account from `question.md`; on normal exit, moved to `answered_feedback/`

## Report Format

```markdown
# Automation Run Report — YYYY-MM-DD HH:MM

**Started**: YYYY-MM-DD HH:MM
**Stopped**: YYYY-MM-DD HH:MM
**Stop reason**: scheduled | manual | all-accounts-exhausted
**Accounts used**: gmail, web, gmail2
**Total sessions**: N (M completed, P paused, Q failed)

---

## Session 1 — <task-id> (<account>)
**Started**: HH:MM | **Ended**: HH:MM | **Exit**: 0
<captured stdout, trimmed to first 500 chars if longer>

---
...

## Pending Feedback

- TASK-PROC-041-01: "Question text from question.md"
```

## Notes

- Use `zoneinfo` (Python 3.9+) for timezone parsing of rate limit reset time
- Signal handler for SIGTERM: `signal.signal(signal.SIGTERM, lambda s, f: setattr(state, 'stop_requested', True))`
- `automation/.automated_mode` created at script start, deleted in `finally` block
- Minimum Python version: 3.9 (available in devcontainer)
