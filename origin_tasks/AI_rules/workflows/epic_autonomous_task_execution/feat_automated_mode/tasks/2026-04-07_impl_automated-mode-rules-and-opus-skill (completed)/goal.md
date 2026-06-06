---
task_id: TASK-PROC-041-03-01
type: impl
parent_requirement: REQ-PROC-041-03
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
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-05, AC-06]
  sections: []
scope_description: "Add CLAUDE.md automated-mode rules (dual-signal detection, no-AskUserQuestion, terminate on feedback gate) and adapt claude-switch-opus skill to skip pause in automated mode."
release_description: ""
worktree_path: ""
requirements_version:
  commit: 69c7f72c
  file: ../requirements.md
---

# Goal: Implement Automated Mode Rules and Adapt Opus Skill

## Objective

1. Add the automated-mode behavioral rule to `CLAUDE.md` (root level): when both `CLAUDE_AUTOMATED_MODE=1` and `automation/.automated_mode` exist, the AI must not call `AskUserQuestion`; instead it writes the question to `automation/pending_feedback/<TASK-ID>/question.md` and runs `bash scripts/automation/terminate_session.sh`.
2. Modify `.claude/skills/claude-switch-opus/skill.md`: detect automated mode (check `automation/.automated_mode` exists), skip the end-of-skill pause/wait, and emit a completion message (`"Opus processing complete — returning to Sonnet."`) instead.
3. Create the sentinel file management note in CLAUDE.md: both signals (env var AND file) must be present.

## Requirements Summary

REQ-PROC-041-03 defines the automated-mode flag system. The single-source requirement file is at `../requirements.md`.

Current requirements: ../requirements.md

## Scope

### In Scope
- `CLAUDE.md` — add `## Automated Mode` section with the dual-signal rule
- `.claude/skills/claude-switch-opus/skill.md` — add automated-mode check at end of skill
- `automation/.automated_mode` — the skill creates this file path is referenced (not created by this task; the orchestrator creates it)

### Out of Scope
- `scripts/automation/terminate_session.sh` — created by TASK-PROC-041-02-01
- `scripts/automation/orchestrate.py` — created by TASK-PROC-041-01-01
- Any other skills beyond claude-switch-opus (they don't currently pause for user input)

## Acceptance Criteria

- [ ] CLAUDE.md contains a `## Automated Mode` section with rule: "When `CLAUDE_AUTOMATED_MODE=1` is set AND `automation/.automated_mode` exists, you are in automated mode. In automated mode: (a) do not call AskUserQuestion — instead write the question to `automation/pending_feedback/<TASK-ID>/question.md` and run `bash scripts/automation/terminate_session.sh`; (b) all skills continue execution without pausing for user input"
- [ ] CLAUDE.md rule explicitly states that BOTH signals must be present (not just one)
- [ ] `claude-switch-opus` skill checks for `automation/.automated_mode` at its end step; when present, skips pause and emits `"Opus processing complete — returning to Sonnet."`
- [ ] Manual (interactive) sessions with neither signal active are unaffected

## Notes

- The CLAUDE.md rule uses natural language — the AI reads it as part of the system prompt. Keep it concise and unambiguous.
- For claude-switch-opus: check file existence via a Bash step in the skill instructions, not via code.
- The `<TASK-ID>` in the rule refers to the current task being executed (readable from goal.md frontmatter at runtime).
