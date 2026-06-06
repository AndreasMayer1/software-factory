---
id: REQ-PROC-041-04
status: defined
stakeholder: developer
created: 2026-04-06
parent: REQ-PROC-041
after: [REQ-PROC-041-02, REQ-PROC-041-03]
blocks: []
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
    - id: AC-04
    - id: AC-05
    - id: AC-06
    - id: AC-07
    - id: AC-08
    - id: AC-09
---

# Feedback Pause and Resume

## Overview

A file-based protocol for capturing pending user-feedback questions when an automated session pauses, and for resuming the session with the user's answer injected as the next prompt.

## Purpose

Unattended sessions inevitably reach decision points that require developer judgment. Skipping these decisions produces incorrect outputs; blocking indefinitely prevents the next task from running. This feature provides a structured handoff: the session captures the question and exits cleanly; the developer answers at their convenience; the orchestrator resumes the session with the answer injected, as if the developer had typed it at the terminal.

The post-resume cleanup behavior (AC-06, AC-09) archives each answered Q&A pair into the answering task's own `plans_and_protocols/` folder rather than a global `answered_feedback/` dump. This keeps the `pending_feedback/` folder as a clean inbox and makes developer decisions discoverable and persistent alongside the task they shaped — visible to the factory optimizer and to anyone tracing why a decision was made. The full rationale, including the audience analysis and the alternative options considered, is in:

`requirements_tasks/process/AI_rules/epic_factory_quality/feat_artifact_model/tasks/2026-06-01_explore_interactive-feedback-checkpoint-artifact (completed)/plans_and_protocols/2026-06-02_01_synthesis.md`

## Scope

**Included:**
- File and folder conventions for pending feedback (`automation/pending_feedback/<TASK-ID>/`)
- Schema for `question.md` (machine-readable frontmatter + human-readable question body)
- Developer writes `answer.md` in the same folder to signal readiness to resume
- Orchestrator resume command construction and execution
- Post-resume cleanup: archiving answered Q&A as a `feedback-checkpoint` file in the task's `plans_and_protocols/` and deleting the `pending_feedback/<TASK-ID>/` folder

**Excluded:**
- Session termination mechanics (REQ-PROC-041-02 provides `terminate_session.sh`)
- Detecting that automated mode is active (REQ-PROC-041-03)
- Orchestrator session-start loop (REQ-PROC-041-01)

## Behavior

### When a Feedback Gate Fires (Automated Mode)

The AI writes `automation/pending_feedback/<TASK-ID>/question.md` with all context needed to understand the question, then runs `bash scripts/automation/terminate_session.sh`. The session exits. The orchestrator detects the exit and checks for new `question.md` files.

### Developer Reviews and Answers

The developer reads `question.md`, writes their answer to `automation/pending_feedback/<TASK-ID>/answer.md` (free-form text), and does nothing else. No manual command is needed; the next orchestrator run detects `answer.md`.

### Orchestrator Resumes the Session

On the next run (or when the orchestrator is manually restarted), it detects tasks with both `question.md` and `answer.md`. For each, it constructs:

```python
env = {**os.environ, "CLAUDE_CONFIG_DIR": f"/home/vscode/.ccs/instances/{account}",
       "CLAUDE_AUTOMATED_MODE": "1"}
subprocess.run(["claude", "--dangerously-skip-permissions",
                "--resume", session_id,
                "-p", answer_content], env=env)
```

The `<account>` and `<session-id>` are read from `question.md` frontmatter. The session resumes at the point it paused, with the answer as the first new user message.

### Post-Resume Cleanup

When a resumed session exits normally (process exit code 0, no new `question.md` written), the orchestrator moves `automation/pending_feedback/<TASK-ID>/` to `automation/answered_feedback/<TASK-ID>/`. This preserves the feedback history while keeping the `pending_feedback/` folder free of resolved items.

## File Schema

### `automation/pending_feedback/<TASK-ID>/question.md`

```yaml
---
task_id: TASK-PROC-041-01
session_id: f47ac10b-58cc-4372-a567-0e02b2c3d479
account: gmail
status: awaiting_answer
asked_at: 2026-04-06T09:14:22Z
skill: requ-explore
---

# Pending Question

[Human-readable question text and relevant context. Written by the AI to give the developer enough
information to answer without resuming the session or reading the JSONL history.]
```

### `automation/pending_feedback/<TASK-ID>/answer.md`

Free-form text written by the developer. No frontmatter required. The entire file content is passed as the `-p` prompt on resume.

## Acceptance Criteria

- [ ] AC-01: When a feedback gate fires in automated mode, the AI writes `automation/pending_feedback/<TASK-ID>/question.md` with frontmatter fields: `task_id`, `session_id`, `account`, `status: awaiting_answer`, `asked_at` (ISO 8601), and `skill` (the skill that triggered the gate)
- [ ] AC-02: The question body in `question.md` contains enough context for the developer to answer without consulting any other file
- [ ] AC-03: The developer signals readiness to resume by creating `automation/pending_feedback/<TASK-ID>/answer.md`; no other action is required
- [ ] AC-04: The orchestrator detects the presence of `answer.md` and adds the corresponding task to the resume queue on its next iteration
- [ ] AC-05: The orchestrator resumes the session using `claude --dangerously-skip-permissions --resume <session-id> -p "<answer content>"` with `CLAUDE_CONFIG_DIR=/home/vscode/.ccs/instances/<account>` in the subprocess environment, where `account` and `session-id` are read from `question.md` frontmatter
- [ ] AC-06: When a resumed session exits normally (no new `question.md` written), the orchestrator: (1) merges `question.md` and `answer.md` into a single `feedback-checkpoint` file written to the task's `plans_and_protocols/` folder, named `YYYY-MM-DD_feedback-checkpoint[_NN].md` (where `_NN` is a zero-padded counter added only when a same-day file already exists), with a YAML envelope (fields: `skill`, `mode: automated`, `decision`, `task_id`, `captured_at`) and free-form body sections `# Question`, `# Developer Answer` (verbatim), and `# Rationale Captured`; (2) deletes the `automation/pending_feedback/<TASK-ID>/` folder. The `answered_feedback/` folder is no longer used for new entries; existing entries remain as-is.
- [ ] AC-07: A task that generates a new `question.md` after resume (because the answer prompted further questions) remains in `pending_feedback/` and is re-queued on the next orchestrator iteration
- [ ] AC-08: Before invoking `scripts/automation/terminate_session.sh`, the automated session commits all changes that were caused by the work on the task (including the freshly written `question.md` and the copied `answer.md`). The commit uses the `claude-commit` skill with type `chore`, scope `automation`, and a subject of the form `pause session for <TASK-ID> — <skill>` (where `<skill>` is the name of the skill that triggered the pause). Pre-existing uncommitted changes from before the session started are out of scope and MUST NOT be swept into this commit. A `git status` cleanliness check is explicitly NOT required because such pre-existing changes may legitimately remain in the working tree.
- [ ] AC-09: The resume prompt injected by the orchestrator (the `-p` argument to `claude --resume`) is prefixed with a one-line preamble that gives the path of the archived `feedback-checkpoint` file, so the resumed session can locate the answer record without accessing `pending_feedback/`. Example preamble: `[Answer archived at: requirements_tasks/.../plans_and_protocols/YYYY-MM-DD_feedback-checkpoint[_NN].md]`

## Developer Guidelines

### Key Decisions

- `answer.md` is free-form plain text, not YAML. The developer writes naturally; the orchestrator passes the raw content verbatim as the resume prompt. No parsing required.
- The `<TASK-ID>` folder name under `pending_feedback/` matches the `task_id` from goal.md frontmatter. This makes it human-navigable without tooling.
- The `account` field in `question.md` records the account that created the session. Session storage is shared across accounts via symlinks (`projects/` → `~/.ccs/shared/context-groups/default/projects`), so the orchestrator can resume with any available account if the original is rate-limited or has no access.
- The `answered_feedback/` folder is deprecated for new entries. Existing entries remain and are not automatically cleaned up. New answered feedback is archived directly into the answering task's `plans_and_protocols/` folder as a `feedback-checkpoint` file (see AC-06).

### Common Pitfalls

- Empty `answer.md`: If the developer creates `answer.md` but leaves it empty, the resume prompt is an empty string. The orchestrator should log a warning and skip resumption if `answer.md` is empty or contains only whitespace.
- Multiple `question.md` files for the same task: Can occur if a session wrote a question, was never resumed, and then was resumed manually (outside the orchestrator) and wrote another question. The orchestrator should treat the presence of `question.md` + absent `answer.md` as "still paused" regardless of how many times it has been written.
- Stale `pending_feedback/` after manual resolution: If the developer resolves a feedback question manually (by resuming the session themselves), the `pending_feedback/<TASK-ID>/` folder is never cleaned up by the orchestrator. The developer should delete it manually, or the orchestrator should detect that the session was already resumed (e.g., goal.md status is `completed`) and run the archival step.
- Session work left uncommitted when pausing: If the session writes `question.md` and terminates without committing the work it produced before pausing, those changes accumulate across sessions and dirty the tree (multiple sessions, multiple tasks, all unresolved). AC-08 prevents this: the session-pause commit covers every change caused by the task's work, leaving only pre-existing untouched changes behind.

## Related Requirements

- REQ-PROC-041-01 (Session Orchestrator): Monitors `pending_feedback/`, constructs resume commands, and runs the feedback-checkpoint archival step before resuming (AC-06, AC-09). Its AC-23 and AC-24 commit `answer.md`, `question.md`, and the run report — files under `automation/` only. **AC-08 of this requirement complements them by committing the rest of the task-caused changes (which fall outside the orchestrator's scope) at the session side.**
- REQ-PROC-041-02 (Session Lifecycle): Provides `terminate_session.sh` called immediately after `question.md` is written
- REQ-PROC-041-03 (Automated Mode): Provides CLAUDE.md rule that triggers the `question.md` write + termination sequence
- REQ-PROC-044-03 (Interactive Feedback Capture): Interactive-mode twin — captures developer steering decisions during interactive skill sessions as `feedback-checkpoint` artifacts; same file format, `mode: interactive`

## References

- Epic: `requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/requirements.md`
- Claude CLI `--resume` flag: `claude --help`
- CCS account session storage: `~/.ccs/instances/<account>/projects/<project>/`
