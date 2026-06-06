---
id: REQ-PROC-041-03
status: defined
stakeholder: developer
created: 2026-04-06
updated: 2026-04-25
parent: REQ-PROC-041
after: []
blocks:
  - REQ-PROC-041-04
  - REQ-PROC-041-02
  - REQ-PROC-041-01
market_research_refs: [] # No relevant findings identified
user_needs:
  implements_flows: []
  addresses_scenarios: []
  personas_served: [PERSONA-004]
trackable_items:
  acceptance_criteria:
    - id: AC-01
    - id: AC-02
    - id: AC-03
    - id: AC-05
    - id: AC-06
    - id: AC-07
    - id: AC-08
    - id: AC-09
---

# Automated Mode

## Overview

A single, unambiguous flag that distinguishes automated Claude Code sessions from manual (interactive) sessions, combined with CLAUDE.md rules that adapt AI behavior in automated mode: skills must not block waiting for terminal input, and feedback gates must defer rather than wait indefinitely.

## Purpose

Without a mode flag, the AI cannot distinguish between a session where the developer is present (and can answer questions) and an unattended automated session (where blocking indefinitely or asking terminal questions is not viable). This feature establishes the single authoritative signal for all automated-mode behavioral adaptations.

## Scope

**Included:**
- The `CLAUDE_AUTOMATED_MODE=1` environment variable as the authoritative automated-mode signal
- The sentinel file `automation/.automated_mode` as the secondary, AI-readable signal
- CLAUDE.md rules governing AI behavior when automated mode is active
- Ensuring manual (interactive) sessions are completely unaffected

**Excluded:**
- Orchestrator launch mechanics (REQ-PROC-041-01)
- Session termination scripts (REQ-PROC-041-02)
- Feedback question storage and resume (REQ-PROC-041-04)

## Behavior

### Mode Detection

A session is in automated mode when both conditions hold:
1. The environment variable `CLAUDE_AUTOMATED_MODE=1` is set (injected by the orchestrator)
2. The sentinel file `automation/.automated_mode` exists in the project root

Using two signals makes detection robust: the env var prevents accidental automation when the file is left over from a previous run; the file gives the AI a tool-readable check without needing to execute a Bash command for every check.

### CLAUDE.md Rules in Automated Mode

When `CLAUDE_AUTOMATED_MODE=1` is active, the following rules apply to all skills and AI behavior:

**No blocking for terminal input**: No skill may emit a prompt and wait for keyboard input. Skills that present choices (e.g. AskUserQuestion) must use the file-based feedback mechanism (REQ-PROC-041-04) instead.

**No AskUserQuestion calls**: In automated mode, `AskUserQuestion` is not available. If a skill would normally call it, the AI writes the question to `automation/pending_feedback/<TASK-ID>/question.md` and runs `bash scripts/automation/terminate_session.sh`.

**Bootstrap cases at session start**: The bootstrap check applies only two cases:
- **Case D** (default): When `next_tasks.py` returns runnable tasks, the bootstrap proceeds to execute them. No orchestration task creation logic runs.
- **Case C** (chain complete): When the task queue is empty AND a validation orchestration task for the active release has `status: completed` AND no unanswered `question.md` files exist in `automation/pending_feedback/`, the bootstrap writes `automation/release_status/<version>_complete.md` and recommends running `/release-begin-impl-finalize` then `/release`.

Orchestration task creation (formerly Cases A and B) is handled exclusively by `create_orchestration_task.py` within the self-perpetuating chain. The `claude-automated-mode` bootstrap does not create orchestration tasks.

### Manual Sessions

When `CLAUDE_AUTOMATED_MODE=1` is absent (or `automation/.automated_mode` does not exist), all behavior is identical to the current interactive behavior. No skills are affected; feedback gates prompt the user as before.

## Acceptance Criteria

- [ ] AC-01: The orchestrator injects `CLAUDE_AUTOMATED_MODE=1` into the environment of every CCS session it launches
- [ ] AC-02: The orchestrator creates `automation/.automated_mode` before starting a run and deletes it after the run completes (or on SIGTERM/SIGINT)
- [ ] AC-03: CLAUDE.md contains a rule: "When `CLAUDE_AUTOMATED_MODE=1` is set and `automation/.automated_mode` exists, you are in automated mode. In automated mode: (a) do not call AskUserQuestion; instead write the question to `automation/pending_feedback/<TASK-ID>/question.md` and run `bash scripts/automation/terminate_session.sh`; (b) all skills continue execution without pausing for user input"
- [ ] AC-05: No existing skill or workflow step is changed in behavior when `CLAUDE_AUTOMATED_MODE` is absent
- [ ] AC-06: The CLAUDE.md rule explicitly states that `automation/.automated_mode` must be checked (not just the env var) to prevent accidental automated-mode activation from a stale sentinel file
- **AC-07**: The `claude-automated-mode` bootstrap does not create orchestration tasks or impl tasks. Orchestration task creation is handled exclusively by the self-perpetuating chain: each orchestration task calls `scripts/create_orchestration_task.py` as part of its own acceptance criteria, creating the next orchestration task or a validation task when all packages are covered. When `next_tasks.py` returns runnable tasks, the bootstrap proceeds to execute them without any additional orchestration task creation logic (Case D — default path).
- **AC-08**: `scripts/find_orchestration_tasks.py --status <comma-list>` detects pending or in-progress orchestration tasks by matching two structural criteria: the `target_release` field is set AND the `scope_description` begins with "Orchestration:". The script is used by `create_orchestration_task.py`'s internal duplicate-check step before creating a new orchestration task. No grep-based orchestration task detection exists in `claude-automated-mode`.
- **AC-09**: When all packages in `RELEASE_BACKLOG.md` for the active release are covered (each has at least one non-terminal impl task) AND all such impl tasks have `status: completed` AND no unanswered `question.md` files exist in `automation/pending_feedback/`, the bootstrap writes `automation/release_status/<version>_complete.md` with: release version, date, package count, impl task count, and next recommended action (`release` skill). This file distinguishes end-of-release `queue_empty` from a cold-start `queue_empty`.

## Developer Guidelines

### Key Decisions

- Two-signal detection (env var + file) is intentional. The env var alone would activate automated mode whenever a developer manually exports it. The file alone would activate it if the file is left over from a previous crashed run. Both together prevent both failure modes.
- The CLAUDE.md rule is the primary enforcement mechanism. The AI model reads CLAUDE.md as part of the system prompt on every session start (without `--bare`). Estimated compliance rate for CLAUDE.md rules is ~80% — acceptable per the requirement author's stated threshold.
- Skills that present choices (e.g. `AskUserQuestion`) are governed by the CLAUDE.md rule in automated mode: write the question file and call `terminate_session.sh` rather than blocking.
- The sentinel file path `automation/.automated_mode` uses a dot prefix to be invisible in standard `ls` output, reducing cognitive noise in the project tree.

### Common Pitfalls

- Using only the env var: If a developer accidentally exports `CLAUDE_AUTOMATED_MODE=1` in their shell profile, all manual sessions would behave as automated sessions. The file check prevents this.
- Forgetting to delete `automation/.automated_mode` after a run: The orchestrator must delete this file in a `finally` block (Python) or trap (shell) to ensure it is removed even on crashes or interruptions.
- Adding automated-mode checks in skills as conditional code: The CLAUDE.md rule governs AI behavior. Skills should not contain Python/Dart-style `if AUTOMATED_MODE` conditionals — the AI itself reads the rule and adapts its tool call sequence.

## Related Requirements

- REQ-PROC-041-01 (Session Orchestrator): Injects env var and manages sentinel file
- REQ-PROC-041-02 (Session Lifecycle): Provides `terminate_session.sh` called by the CLAUDE.md rule
- REQ-PROC-041-04 (Feedback Pause & Resume): Provides the `pending_feedback/` write target referenced in the CLAUDE.md rule

## References

- Epic: `requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/requirements.md`
- CLAUDE.md — project-level AI rules file that contains the automated-mode behavioral rules
