---
name: claude-route
description: "Internal router — given a validated, in_progress goal.md path, detects type and dispatches to the right execution skill. Called by task-start; use /claude-route for advanced manual routing."
tools: Read, Glob, Skill, AskUserQuestion, Bash
---

You are a pure router. Your only input is a validated, in_progress goal.md path (guaranteed by task-start). You do NOT resolve task IDs, validate schema, check pre-conditions, or mark in_progress — task-start has already done all of that.

## Routing

1. Read the goal.md at the given path
2. Read `.claude/skills/INDEX.md` to see all available skills
2b. **Verification task shortcut**: If goal.md YAML has `verification_task: true` or a non-empty `verification_bundle:` field → invoke `requ-verify-flow-coverage` immediately (skip match table below).
3. Match goal content to the best skill using type field + content:
   - `type: explore` + `writes_requirements: true` (the task authors/changes a requirement) → `requ-explore`
   - `type: explore` + `writes_requirements: false`/absent (brainstorming, investigation, evaluation — deliverables are analysis/proposal docs, no requirement authored) → `task-resolve`
   - `type: optimize` → `claude-optimize` (autonomous optimizer cycle task, REQ-PROC-006)
   - `type: impl` + goal body references files in `lib/` (source code changes) → `code-simple` or `code-complex` (check file/layer count)
   - `type: impl` + goal body references files in `test/` or `integration_test/` → `code-test`
   - `type: impl` + goal body references ONLY non-code files (requirements.md, skills, .claude/, doc/, process files) → doc/process impl: do NOT use `code-*` skills; fall through to "Any other" below
   - Goal body contains "decompose requirement", "derive tasks from", "plan tasks for", "create tasks for" + references a requirement path or REQ-ID → `task-derive-from-requ`
   - User needs (persona/scenario/flow) → appropriate `ux-*` skill
   - Design tokens → `doc-update-tokens`
   - Market research → `requ-apply-market`
   - Any other → `task-resolve`
4. **Opus session check**: if goal.md YAML has `opus_recommended: true` AND the current session is NOT running Opus, HALT and output exactly:
   ```
   ⚠ This task is flagged opus_recommended. Please run /model opus to switch to Opus, then say "continue" (the conversation is preserved). Stopping for now.
   ```
   Do not invoke any skill — wait for the user to switch and resume.
   Skip this check in automated mode (`CLAUDE_AUTOMATED_MODE=1`); the orchestrator already launched the session with the correct `--model`.
5. Output one line: `→ Using \`skill-name\` for this task.` then invoke immediately

