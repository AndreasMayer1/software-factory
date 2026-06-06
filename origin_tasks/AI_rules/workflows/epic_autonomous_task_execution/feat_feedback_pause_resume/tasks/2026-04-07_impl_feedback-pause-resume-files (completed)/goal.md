---
task_id: TASK-PROC-041-04-01
type: impl
parent_requirement: REQ-PROC-041-04
urgency: 3
urgency_reason: U3-DEV-WORKFLOW
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-04-07
completed: 2026-04-07
effort: S
created: 2026-04-07
after: [TASK-PROC-041-02-01, TASK-PROC-041-03-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07]
  sections: []
scope_description: "Define automation/pending_feedback folder convention, question.md schema template, and add resume detection + cleanup logic to orchestrator (coordinated with TASK-PROC-041-01-01)."
release_description: ""
worktree_path: ""
requirements_version:
  commit: 69c7f72c
  file: ../requirements.md
---

# Goal: Implement Feedback Pause/Resume File Protocol

## Objective

1. Create the `automation/pending_feedback/` folder structure with a `.gitkeep` and `README.md` describing the protocol.
2. Create `automation/answered_feedback/` with `.gitkeep`.
3. Add `question.md` template at `automation/pending_feedback/TEMPLATE_question.md` showing the required frontmatter schema.
4. The orchestrator's resume detection, resume command, and post-resume cleanup (AC-04, AC-05, AC-06, AC-07) are implemented as part of TASK-PROC-041-01-01 (the orchestrator script) — this task delivers the folder structure and protocol documentation only.

## Technical Notes (from exploration)

- Resume command confirmed: `claude --dangerously-skip-permissions --resume <session-id> -p "<answer>"` with `CLAUDE_CONFIG_DIR=/home/vscode/.ccs/instances/<account>` works correctly.
- Sessions store history per-account; wrong CLAUDE_CONFIG_DIR creates a new session instead of resuming.

## Requirements Summary

REQ-PROC-041-04 at `../requirements.md`.

Current requirements: ../requirements.md

## Scope

### In Scope
- `automation/pending_feedback/` folder + `.gitkeep` + `README.md`
- `automation/answered_feedback/` folder + `.gitkeep`
- `automation/pending_feedback/TEMPLATE_question.md` — example showing required frontmatter
- `.gitignore` entry to exclude actual question/answer files from version control (they contain task-specific runtime state)

### Out of Scope
- Resume loop logic inside orchestrator.py (TASK-PROC-041-01-01)
- The CLAUDE.md rule that triggers writing question.md (TASK-PROC-041-03-01)

## Acceptance Criteria

- [ ] `automation/pending_feedback/` exists with `.gitkeep` and `README.md` explaining the protocol
- [ ] `automation/answered_feedback/` exists with `.gitkeep`
- [ ] `TEMPLATE_question.md` shows the required frontmatter: `task_id`, `session_id`, `account`, `status`, `asked_at`, `skill`
- [ ] `.gitignore` excludes `automation/pending_feedback/*/question.md` and `automation/pending_feedback/*/answer.md` (runtime files, not committed)

## Notes

- The `README.md` should be brief — it documents the file protocol for the developer who writes answer.md files manually.
