# Agent A Diff Summary — Shrink claude-route to Pure Router

**Task**: TASK-PROC-069-03
**Date**: 2026-06-05
**Files changed**: 3

---

## 1. `.claude/skills/claude-route/SKILL.md`

### Removed entirely
- **"Input: task ID given" block** — the grep-search-then-locate flow for `task_id:` in frontmatter. This is now task-start P0 (reference resolution).
- **"Mode A" steps 1–2b** — reading goal.md frontmatter, adding missing metadata, marking `status: in_progress`, writing `started:` date, and writing `session_id`/`session_account` in automated mode. These are now task-start P1–P3.
- **"Mode B: interactive"** — the `/claude-route` free-text disambiguation flow (read INDEX.md, ask user, narrow via AskUserQuestion). This is now task-start P0 free-text routing.
- **"Mode C: next task"** — the `next_tasks.py` invocation, UNCOVERED ACs branch, and in_progress/awaiting loop. This is now task-start P0 "next task".

### Kept (unchanged)
- Step 3: Read `.claude/skills/INDEX.md`
- Step 3b: Verification task shortcut (`verification_task: true` or `verification_bundle:` → `requ-verify-flow-coverage`)
- Step 4: Full match table (all branches — `type: explore`, `type: impl`, code/test/non-code variants, decompose, ux-*, tokens, market, fallback)
- Step 5: Opus session check (`opus_recommended: true` → halt + message; skip in automated mode)
- Step 6: Output `→ Using \`skill-name\`` then invoke

### Changed
- **Frontmatter description**: from "Routes to the right skill — from goal.md path or user description. MUST BE CALLED WHEN USER STATES DO [TASK-ID], NEVER SKIP IT" → "Internal router — given a validated, in_progress goal.md path, detects type and dispatches to the right execution skill. Called by task-start; use /claude-route for advanced manual routing."
- **Preamble**: New opening paragraph makes the contract explicit: pure router, input guaranteed valid+in_progress by task-start, no ID resolution/validation/gating done here.
- **Structure**: Collapsed from 4 named sections (Input / Mode A / Mode B / Mode C) to a single flat "## Routing" section with steps 1, 3, 3b, 4, 5, 6.

---

## 2. `.claude/skills/claude-route/contract.yaml`

### Changed
- **purpose**: Rewritten to reflect internal-router role. Old: "Route a task or request to the correct skill. Accepts a goal.md path, a task ID, or an interactive description. Marks the task in_progress, records session metadata in automated mode, and invokes the matched skill." New: "Internal router: given a validated, in_progress goal.md path (guaranteed by task-start), detect task type and dispatch to the correct execution skill. Pre-flight work (schema validation, pre-condition gates, in_progress marking) is NOT done here — task-start owns that."
- **derived_from.required[goal].source**: Changed from `external` to `skill:task-start` (the goal now arrives from task-start, not from the user directly).
- **produces**: Changed from `conditional` block (updating goal status to in_progress) to `{}` (no produces — claude-route no longer writes to goal.md).
- **quality_criteria**: Removed "Task status is updated to in_progress before the skill is invoked" and "In automated mode, session_id and session_account are written to goal.md." Added "Input goal.md is already validated and in_progress (guaranteed by task-start)."
- **user_input_gates**: Reduced from 4 entries (Mode B interactive, Mode C UNCOVERED ACs, Mode C in_progress resume, Mode A Opus check) to 1 entry (Opus session check only).
- **side_effects**: Changed from `[write to goal.md: status in_progress, started date, session metadata]` to `[]` (empty — no writes).
- **preconditions**: Changed from "User has provided a goal.md path, a TASK-ID, or a clear task description" to "goal.md path is provided (validated, status is in_progress — guaranteed by task-start)."
- **may_invoke**: Added `claude-optimize` (was missing from old contract).

---

## 3. `.claude/skills/INDEX.md`

### Changed
- **"Not sure?" row** in the Quick Reference table: skill column changed from `claude-route` / `/claude-route` to `task-start` / `/task-start`. Rationale: Mode B (interactive disambiguation) has been removed from claude-route; task-start is now the user-facing entry point for all task execution including free-text descriptions.

---

## Success check results

| Check | Command | Result |
|-------|---------|--------|
| Mode B/C/task ID removed | `grep -c "Mode B\|Mode C\|Input: task ID" SKILL.md` | 0 |
| validate_against_schema/awaiting removed | `grep -c "validate_against_schema\|awaiting" SKILL.md` | 0 (the 2 `in_progress` hits are in description/preamble stating task-start owns it — correct) |
| INDEX reference kept (step 3) | `grep -c "INDEX" SKILL.md` | 1 |
| Opus lines kept (step 5) | `grep "opus" SKILL.md` | Present (step 5 intact) |
| Not sure? row updated | `grep "Not sure" INDEX.md` | task-start / /task-start |
