---
task_id: TASK-PROC-041-02
type: explore
parent_requirement: REQ-PROC-041
urgency: 3
urgency_reason: U3-DEV-WORKFLOW
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-04-07
started: 2026-04-07
completed: 2026-04-07
after: [TASK-PROC-041-01-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-02, SEC-03, SEC-04, SEC-05, SEC-06]
scope_description: "End-to-end integration test of the full autonomous task execution system using dummy tasks, with LLM evaluation of results and iterative auto-fixing until clean."
release_description: ""
worktree_path: ""
requirements_version:
  commit: 69c7f72c
  file: ../requirements.md
---

# Goal: Integration Test — Autonomous Task Execution System

## Objective

Validate that the full autonomous task execution system (REQ-PROC-041) works end-to-end by running the orchestrator against purpose-built dummy tasks, evaluating the results with a lightweight LLM agent, and iterating until everything passes cleanly.

This task produces a `findings.md` confirming the confirmed-working state of the system, or documents what required fixing.

## Scope

### In Scope

1. **Dummy task setup**: Create 3 dummy impl tasks with `urgency: 5`, `impact: 5` and trivial goals, so `next_tasks.py` surfaces them at the top of the queue ahead of all real work. Each task should be self-contained and verifiable by script (no Flutter build required):
   - Dummy Task A (normal completion): goal = write `automation/test_outputs/dummy_a.txt` with content `"DUMMY_A_DONE"`
   - Dummy Task B (normal completion): goal = write `automation/test_outputs/dummy_b.txt` with content `"DUMMY_B_DONE"`
   - Dummy Task C (feedback-gate test): goal = ask the user one question via `AskUserQuestion` (to verify the automated-mode feedback gate fires, writes `question.md`, and terminates instead of blocking)

2. **Orchestrator run**: Run `python3 scripts/automation/orchestrate.py --max-tasks 3 --accounts gmail,web,gmail2` and let it process all 3 dummy tasks.

3. **Evaluation** (after run completes): Spawn a Haiku agent to evaluate the run:
   - Did all 3 sessions start and exit cleanly?
   - Did tasks A and B write their expected output files?
   - Did task C write `automation/pending_feedback/<TASK-ID>/question.md` and terminate without blocking?
   - Does the report file (`automation/reports/`) exist and contain correct per-session entries?
   - Are session output files present in `automation/session_outputs/`?

4. **Auto-fix loop**: If evaluation finds issues, the agent fixes them (edit orchestrator script, CLAUDE.md rule, or skill) and re-runs. Maximum 3 iterations. On each iteration, record what was broken and what fix was applied in `plans_and_protocols/iteration_log.md`.

5. **Findings**: Write `plans_and_protocols/findings.md` documenting:
   - Final pass/fail status per test scenario
   - Any fixes applied and why they were needed
   - The confirmed-working orchestrator invocation
   - Any known limitations or edge cases discovered

### Out of Scope

- Testing with real tasks from the backlog (use dummy tasks only — no risk to actual work)
- Testing all possible rate limit scenarios (only happy path + feedback gate)
- Performance or load testing

## Acceptance Criteria

- [ ] 3 dummy tasks created with urgency/impact=5, appear at top of `python3 scripts/next_tasks.py` output
- [ ] Orchestrator runs without crashing and processes all 3 dummy tasks sequentially
- [ ] Dummy tasks A and B produce their expected output files
- [ ] Dummy task C writes `question.md` to `automation/pending_feedback/` and the session exits — does NOT block waiting for terminal input
- [ ] Run report exists at `automation/reports/` and contains entries for all 3 sessions
- [ ] Session outputs exist at `automation/session_outputs/` for all 3 sessions
- [ ] Haiku evaluation agent produces a structured pass/fail verdict
- [ ] `plans_and_protocols/findings.md` written with confirmed-working invocation and any issues found

## Notes

### Dummy Task Design

Dummy tasks must be:
- Located under a dedicated `automation/test_tasks/` folder (not under real requirements)
- Marked with `status: pending` and a note that they are test-only (delete after validation)
- Given a `scope_description: "INTEGRATION TEST DUMMY — delete after TASK-PROC-041-02 completes"`

### Evaluation Agent Prompt (Haiku)

```
You are evaluating the results of an automated task execution system test run.

Read:
1. automation/reports/ — the most recent report file
2. automation/session_outputs/ — the 3 most recent session output files  
3. automation/pending_feedback/ — check if question.md exists for the feedback-gate dummy task
4. automation/test_outputs/ — check if dummy_a.txt and dummy_b.txt exist with correct content

For each criterion, output PASS or FAIL with one sentence of evidence.
Then output overall: PASS (all criteria met) or FAIL (list which criteria failed).
```

### Auto-Fix Guidance

Common issues to look for and fix:
- Orchestrator doesn't find any tasks (next_tasks.py output parsing wrong)
- CLAUDE.md rule not loaded (check `--bare` flag not accidentally present)
- Session exits with non-zero code that isn't rate limit (check error output)
- `question.md` not written before termination (CLAUDE.md rule wording needs adjustment)
- Hook reminder footer not stripped from session outputs

### Cleanup After Test

After this task completes, delete:
- `automation/test_tasks/` folder (dummy tasks)
- `automation/test_outputs/` folder
- `automation/session_outputs/` (test sessions)
- `automation/reports/` (test reports)
- `automation/pending_feedback/` contents from test run

Keep: `plans_and_protocols/findings.md` and `plans_and_protocols/iteration_log.md`
