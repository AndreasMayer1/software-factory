---
name: task-complete
description: Mark a task as completed after verification. THIS SKILL MUST BE USED TO COMPLETE TASKS.
tools: ["Bash", "Read", "Edit", "AskUserQuestion"]
---

You verify a task is complete and mark it as such.

**User invokes**: "Use task-complete skill for [task_path]"

## Entry pre-check (REQ-PROC-044 Wave 2)

Runtime guard for the required input in `contract.yaml` — fail loudly if the task goal.md is missing or off-schema before any completion mutation runs.
```bash
GOAL_PATH="${1:?task-complete requires the task goal.md path}"
[ -f "${GOAL_PATH}" ] || { echo "ERR: missing goal.md at ${GOAL_PATH} (required input per contract.yaml)"; exit 2; }
python3 scripts/quality/validate_against_schema.py "${GOAL_PATH}" .claude/schemas/goal_metadata.yaml || exit 2
```

**You execute**:

1. **Detect Change Type**: Determine if this is a docs-only change to optimize verification:
   ```bash
   git diff --name-only
   ```

   **Docs-only criteria** (ALL changed files must match):
   - `*.md` files in `requirements_tasks/`, `requirements_user_needs/`, or `doc/`
   - OR files in `plans_and_protocols/`
   - AND NO files in `lib/`, `test/`, or `scripts/*.dart`

   Set verification mode:
   - **Docs-only mode**: Lightweight verification (token saver)
   - **Code change mode**: Full verification

2. **Verify Goal**:

   **If docs-only mode**:
   - Read goal.md briefly to understand what was expected
   - Verify expected files were modified (using git diff output)
   - Quick sanity check (no obvious missing pieces)

   **If code change mode**:
   - Read goal.md in detail
   - Verify implementation matches goal thoroughly
   - Check all required changes are in place
   - Verify no obvious bugs or missing pieces

2a. **Block on quality gates** (code change mode only):
   - Invoke the `verify-quality` skill. It runs the per-change gate set
     and the quality-checker agent, applies the five-cycle back-pressure
     protocol, and exits non-zero on RED.
   - If `verify-quality` returns RED: STOP. Do **not** mark the task
     completed. Report the failing gates to the caller. The five-cycle
     counter remains in `plans_and_protocols/cycle_state.json`.
   - The hard rule comes from REQ-PROC-046 AC-10 (inherited by REQ-PROC-002
     AC-07 and REQ-PROC-052 AC-09): code that fails any active gate is
     never declared complete.
   - Bypass: only when the user has explicitly authorized `SKIP_QUALITY_GATES=1`
     for this task. Record the bypass in the commit message.

2b. **Quality-rule proposal reminder** (REQ-PROC-046, TASK-PROC-046-13):
   - Check whether this task touched quality-gate definitions:
     ```bash
     git diff --name-only HEAD 2>/dev/null | grep -E '^(analysis_options\.yaml|scripts/quality/check_.*\.(sh|py)|scripts/quality/_complexity_analyzer/)' | head
     ```
   - **Exempt tasks** — skip this check entirely:
     - `TASK-PROC-046-16` (the proposals-application loop-task — it LEGITIMATELY edits gates).
     - Any task whose `goal.md` explicitly carries `quality_gate_authority: true` in frontmatter (escape hatch for user-approved gate work).
   - **If any match AND task is not exempt**: warn — do NOT block:
     > "This task modified quality-gate definitions (analyzer config or gate scripts). REQ-PROC-046 Developer Guidelines forbids autonomous gate edits — these changes should normally be filed as a proposal under `scripts/quality/proposals/<category>/` and flow through TASK-PROC-046-16. If this edit is the legitimate consequence of an already-accepted proposal, ensure the corresponding proposal file's `status:` is set to `accepted` in the same commit. Otherwise, revert the gate edit and file a proposal."
   - The reminder is informational. `task-complete` continues. The agent is expected to act on the warning.

3. **Start an Agent and tell it to execute**:

   3.1. **Update goal.md YAML Frontmatter**:
      - Read the current goal.md file
      - Update the YAML frontmatter:
      - Set `status: completed`
      - Set `completed: YYYY-MM-DD` (today's date)
      - Use Edit tool to make the changes
      - If `CLAUDE_AUTOMATED_MODE=1` is set (check via Bash: `echo $CLAUDE_AUTOMATED_MODE`), also write `session_completed_at: YYYY-MM-DDTHH:MM:SSZ` (current UTC timestamp via Bash: `date -u +%Y-%m-%dT%H:%M:%SZ`) to the goal.md frontmatter. Add after `completed:` line.

   3.2. **Check Requirement Status Propagation**:
      - Read the parent requirement's `requirements.md` YAML frontmatter

      **CASE A — Requirement already has `status: active`**:
      - Leave as `active`. Living documents do not transition out of this state.
      - Log: "Requirement is active (living document) — no status change."

      **CASE B — Requirement has `status: in_progress` (or other transitional status)**:

      Step 1: Does `requirements.md` have `trackable_items.acceptance_criteria`?

      **YES** → Check coverage:
      - List all goal.md files in the requirement's `tasks/` folder
      - Collect all completed tasks (status: completed) and their `covers.acceptance_criteria`
      - Check if every AC in `trackable_items.acceptance_criteria` is covered by ≥1 completed task
      - IF all ACs covered → set requirement `status: implemented`, update `updated: YYYY-MM-DD`
      - IF any AC uncovered → leave as `in_progress`, log which ACs are missing

      **NO** (no acceptance criteria / pre-migration) →
      - Warn: "Requirement [id] has no acceptance criteria — cannot auto-verify."
      - Ask user: "All work for [requirement name] is done? Manually confirm to set implemented. (y/n)"
      - IF confirmed → set `status: implemented`, update `updated: YYYY-MM-DD`
      - IF not confirmed → leave unchanged

   3.2b. **Package Description Freshness** (skip if no release-assigned package):
      - Read `target_package` from goal.md frontmatter — if absent: skip
      - Read `requirements_tasks/RELEASE_BACKLOG.md`, find the package entry
      - If package `assigned_release` is `null`: skip (backlog-only packages don't need this check)
      - Show current description to user via AskUserQuestion: "Package '[id]' description: '[description]' — still accurate after this work?" with options "Still accurate" / "Needs update"
      - If "Needs update": ask for corrected text, edit the `description` field in RELEASE_BACKLOG.md

   3.3. **Run Validation**:
      ```bash
      python scripts/requirements/validate_meta.py
      ```
      - If validation fails, report issues but continue

   3.4b. **Write `skills_used:` to protocol.md** (IMPL-H / TASK-PROC-006-13):
      - Find the task's most recent `plans_and_protocols/*_protocol.md`
      - If none exists, skip this step
      - Read the file; if YAML frontmatter is absent, prepend `---\nskills_used: []\n---\n\n` to the file
      - Build the skills list (best-effort) by looking at Skill tool calls visible in your current session context:
        - Include every skill that was actually invoked in this session
        - Always include at minimum: `task-complete`, `claude-commit`
        - Include `claude-log` if a protocol.md exists
        - Include `task-start` and `claude-route` if this task was started via normal routing
        - Include `verify-quality` if verification was run (docs-only mode was false)
        - Include `claude-automated-mode` if `CLAUDE_AUTOMATED_MODE=1`
      - Update the `skills_used:` value in the frontmatter using this YAML list format:
        ```yaml
        skills_used:
          - skill-name-1
          - skill-name-2
        ```
      - Write the updated file (preserve all existing content below the frontmatter)

   3.4. **Regenerate Status Overview**:
      ```bash
      python scripts/artifacts/generate_status_overview.py --full
      ```

   3.5. **Mark Folder Complete** (legacy compatibility): Run the complete_task script:
      ```bash
      python3 scripts/tasks/complete_task.py "[task_path]"
      ```
      Note: this script renames the task folder (adds "(completed)" suffix) — stage the renamed folder path, not the original, when committing.

   3.6. **Clean up autorun pending_feedback** (if applicable):
      Check whether the orchestrator left a feedback folder for this task:
      ```bash
      ls automation/pending_feedback/<TASK-ID>/ 2>/dev/null
      ```
      If it exists, the orchestrator will archive it automatically on the next resume. In
      interactive mode, simply delete it (the answer has already been acted on):
      ```bash
      rm -rf automation/pending_feedback/<TASK-ID>
      ```
      This is a no-op when the task was never run via autorun.

4. **Report**: Confirm the task has been marked as completed with summary of:
   - Verification mode used (docs-only or code change)
   - Updated goal.md status
   - Whether requirement status was updated
   - Validation results
   - Status overview regenerated

5. **Capture interactive steering decisions** (REQ-PROC-044-03 — run in the MAIN session; do NOT delegate to the step-3 agent, this needs the session's own conversation context):

   Skip this entire step when `CLAUDE_AUTOMATED_MODE=1` (automated mode already captures steered decisions via the orchestrator's `_archive_feedback_checkpoint`).

   Review the interactive session for **developer-steered** decisions — points where the developer modified, redirected, or rejected a skill or agent proposal rather than approving it as-is. Plain approvals (the developer accepted the proposal unchanged) capture nothing.

   For each steered decision — no `AskUserQuestion`, no approval gate; write the file directly:
   - Write the developer's words **verbatim** into a unique scratch file from `mktemp` (under `/tmp`, OUTSIDE the working tree so the Commit step never stages it, and unique so multiple steered decisions don't clobber one another). Use a quoted heredoc so arbitrary content — quotes, special chars — is preserved as exact bytes with no shell expansion. Remove the scratch file after the writer runs.
   - The writer lands `<date>_feedback-checkpoint.md` (`_NN`-suffixed for multiple) in the task's `plans_and_protocols/`, so the Commit step below stages it:
     ```bash
     ANSWER_FILE=$(mktemp)
     cat > "$ANSWER_FILE" <<'VERBATIM_EOF'
     <developer steering words, verbatim — exact bytes, no rephrasing>
     VERBATIM_EOF
     python3 scripts/tasks/create_feedback_checkpoint.py \
       --skill "<skill that hit the gate>" \
       --decision "<revised|redirected|rejected>" \
       --task-id "<TASK-ID from goal.md>" \
       --protocols-dir "<task dir>/plans_and_protocols" \
       --answer-file "$ANSWER_FILE" \
       --question-text "<one line: what was proposed>" \
       --rationale-text "<the 'why' the produced artifact does not itself record>"
     rm -f "$ANSWER_FILE"
     ```

6. **Commit**: Use `claude-commit` skill to stage and commit all changes.

7. **Run Monitor Sweep** (post-commit; wired by IMPL-F / TASK-PROC-006-11):

   Skip this step if `SKIP_QUALITY_GATES=1` is set — that env var marks back-out
   paths, WIP escalation commits, and force-complete scenarios; running monitors
   on incomplete or rolled-back tasks would feed spurious events. This is the
   intentional skip condition for `--force`-equivalent runs.

   Otherwise, invoke the sweep after the commit completes:
   ```bash
   python3 scripts/optimize/run_monitors.py 2>/tmp/run_monitors_stderr.txt
   echo "monitor-sweep-exit: $?"
   cat /tmp/run_monitors_stderr.txt
   ```

   Capture the exit code. If non-zero, log the exit code and stderr to the
   terminal, then **continue** — a monitor crash must not abort task-complete or
   trigger a re-run. The sweep is best-effort; one skipped tick is acceptable
   because monitors are idempotent (REQ-PROC-006 AC-02).

**Output**: "Task [name] verified and marked as completed ([mode] verification). [Requirement status update if applicable]"

---
