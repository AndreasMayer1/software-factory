---
task_id: TASK-PROC-041-01
type: explore
parent_requirement: REQ-PROC-041
urgency: 3
urgency_reason: U3-DEV-WORKFLOW
impact: 5
impact_reason: I5-ENAB
status: completed
effort: XL
created: 2026-04-05
started: 2026-04-06
completed: 2026-04-07
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-02, SEC-03, SEC-04, SEC-05, SEC-06]
scope_description: "Research and prototype the technical unknowns of the Autonomous Task Execution system; produce 4 complete implementable feature requirements replacing the current placeholders"
release_description: ""
worktree_path: ""
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Define Autonomous Task Execution — Feature Requirements

## Objective

Fully define the 4 placeholder feature requirements for REQ-PROC-041 (Autonomous Task Execution) by:

1. **Researching** every technical unknown listed below
2. **Prototyping** where hands-on validation is needed (run test sessions, inspect output)
3. **Deciding** the concrete design for each feature
4. **Writing** complete, implementable `requirements.md` files for each feature folder, replacing the current `status: placeholder` stubs

The output of this task is 4 complete feature requirements, ready for implementation tasks to be created against them.

## Requirements Summary

Parent epic: REQ-PROC-041 — Autonomous Task Execution
Path: `requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/requirements.md`

The epic defines an orchestration system that:
- Starts independent CCS sessions sequentially (never parallel, never subagents)
- Rotates between accounts (gmail, web) to handle 5-hour rate limits
- Pauses gracefully when a session needs user feedback (defers, does not skip)
- Terminates when a session completes
- Supports resumption of paused sessions with injected user answers

Current requirements: ../requirements.md

## Scope

### In Scope

**Research questions to answer:**

1. **CCS session lifecycle** — Does `ccs <account> --dangerously-skip-permissions -p "<prompt>"` auto-exit when the prompt is handled and the task completes? Or does it remain open? Test with a simple prompt and a "Do Next Task" prompt. Document exact behavior.

2. **Rate limit detection** — Can remaining API quota be queried programmatically?
   - Try: `/usage` command output inside a session, Claude Code CLI flags, REST API endpoints
   - If yes → describe the mechanism for the orchestrator to use
   - If no → document the time-based fallback heuristic (rotate accounts every N minutes)

3. **Session ID discovery** — How can a running Claude Code session reliably find its own session ID?
   - Claude Code stores sessions in `~/.claude/projects/<hashed-path>/`
   - With multiple sessions open, "newest folder" is unreliable
   - Explore: environment variables set by CCS/claude, reading the JSONL filename, Haiku agent inspection, or other mechanism
   - Choose the most reliable approach and document the exact method

4. **CCS resume syntax** — What is the exact CLI syntax to resume a session with a specific account?
   - Expected: `ccs <account> --dangerously-skip-permissions --resume <session-id> -p "<feedback>"`
   - Verify actual flags and document

5. **Feedback gate termination** — What is the best mechanism for a session to execute a self-termination script when a skill feedback gate fires?
   - Option A: CLAUDE.md rule ("In automated mode, when user feedback is required, write the question to `automation/pending_feedback/<task-id>/question.md` and run `scripts/automation/terminate_session.sh`")
   - Option B: Claude Code hooks (post-tool or stop hooks)
   - Option C: Other mechanism
   - Evaluate reliability for each option (does the AI follow CLAUDE.md rules consistently? ~80% required)

6. **Feedback file structure** — Design the file/folder conventions:
   - Where are pending questions stored?
   - Format of the question file (markdown with structured fields: task-id, session-id, question text, context)
   - Where does the user write answers?
   - How does the orchestrator detect a question has been answered?
   - Proposed structure to evaluate: `automation/pending_feedback/<TASK-ID>/question.md` + `answer.md`

7. **Account rotation timing** — Is a 30–45 minute interval between task sessions sufficient?
   - Consider: some tasks are token-heavy (Opus usage), some are light
   - Consider: the 5-hour window resets to the nearest past hour
   - Recommend a concrete interval or a detection-based strategy

8. **Orchestrator script design** — Should the orchestrator be Python, shell, or another language?
   - Must work within the devcontainer (Linux, bash available, python3 available)
   - Must be able to: spawn subprocesses, detect process exit, read/write files, wait N minutes
   - Evaluate: process management, signal handling, restart after reboot/reconnect

**Feature requirements to produce:**

- `feat_session_orchestrator/requirements.md` — Script that starts CCS sessions, rotates accounts, runs sequentially
- `feat_session_lifecycle/requirements.md` — Termination mechanics (completion + feedback gate), session ID tracking
- `feat_automated_mode/requirements.md` — Automated-mode flag, CLAUDE.md rules, non-blocking skill behavior
- `feat_feedback_pause_resume/requirements.md` — Feedback storage structure, resume with injected answers

### Out of Scope

- Implementing any of the features (implementation tasks come after this exploration)
- Changes to the app codebase (`lib/`)
- Parallel session execution design
- Changes to task prioritization logic

## Acceptance Criteria

- [ ] All 8 research questions answered with concrete, tested conclusions
- [ ] CCS session lifecycle behavior documented (auto-exit or stays open)
- [ ] Rate limit detection approach decided and documented
- [ ] Session ID discovery method decided, tested, and documented
- [ ] Feedback gate termination mechanism decided and documented
- [ ] Feedback file structure designed with exact folder/file paths
- [ ] Account rotation interval recommendation made with rationale
- [ ] Orchestrator script language and design decided
- [ ] `feat_session_orchestrator/requirements.md` complete (status: defined, implementable)
- [ ] `feat_session_lifecycle/requirements.md` complete (status: defined, implementable)
- [ ] `feat_automated_mode/requirements.md` complete (status: defined, implementable)
- [ ] `feat_feedback_pause_resume/requirements.md` complete (status: defined, implementable)
- [ ] Original user voice transcript preserved verbatim in `plans_and_protocols/2026-04-05_01_transcript_original.md`

## Dependencies

None — this is an exploration task with no code dependencies.

## Notes

- Research comes before design. Validate assumptions (especially CCS lifecycle and session ID) before committing to a design.
- For prototyping, prefer running actual CCS sessions with trivial prompts rather than guessing behavior.
- The Haiku model is recommended for any agent spawned during research (token efficiency).
- The automated-mode flag is the single most important design decision — all other features depend on it being reliable and unambiguous.
- When writing feature requirements: follow the requ-explore skill's feature format (WHAT/WHY, not HOW; end-state ACs; no transition language).
