---
name: code-bugfix
description: Bugfix workflow — slim (scripts) or worktree (Flutter/Dart)
tools: [Bash, Read, Edit, Write, Skill]
model: inherit
---

You run bugfix work in either **slim mode** (scripts/non-Flutter) or **worktree mode** (Flutter/Dart).

**Prerequisite**: Task folder with goal.md exists (type: bugfix).

## Entry pre-check (REQ-PROC-044 Wave 2)

Runtime guard for the required input in `contract.yaml` — fail loudly if the bugfix goal.md is missing or off-schema.
```bash
GOAL_PATH="${1:?code-bugfix requires the task goal.md path}"
[ -f "${GOAL_PATH}" ] || { echo "ERR: missing goal.md at ${GOAL_PATH} — run task-create first (required input per contract.yaml)"; exit 2; }
python3 scripts/quality/validate_against_schema.py "${GOAL_PATH}" .claude/schemas/goal_metadata.yaml || exit 2
```

## Mode Detection

**Slim mode** is selected when **any** of these is true (first match wins):
1. goal.md frontmatter contains `fix_mode: slim`
2. goal.md frontmatter contains `fix_mode:` absent/empty AND all files to be changed are in `scripts/`, `.claude/`, or any non-Dart/non-Flutter path

**Default (worktree mode)** when changed files include anything in `lib/`, `test/`, or `integration_test/`.

If it is unclear from the goal whether files are Dart or not, ask the user before proceeding.

---

## Slim Mode (no worktree, no flutter pub get)

Use when the fix is entirely in scripts, skill files, Python, shell, or other non-Flutter files.

1. **Read context**: Read goal.md and latest file in plans_and_protocols/ (if any).

2. **Apply fix** directly in the main working tree — no branch, no worktree.
   - **Doc-lookup checkpoint** (AC-07 / REQ-PROC-053): before editing code, invoke `doc-lookup-dependencies` for any API surface being changed:
     ```
     doc-lookup-dependencies --technology <package-id> --api-surface <dotted.path> --pinned-version <from-pubspec.lock> [--trigger <reason>]
     ```
   - Follow CLAUDE.md bugfix conventions (`[DIAG-*]` prints, `// TEMPORARY:` on debug scaffolding)

3. **Write protocol**: Save a brief fix summary to `plans_and_protocols/[date]_01_protocol_<name>.md`.

4. **Run tests** if applicable (e.g. `python3 -m pytest scripts/` or relevant test command).

5. **Remind**: When fix is confirmed, invoke `task-complete-bugfix` (no worktree to clean up — it will skip that step).

---

## Worktree Mode — First Run (worktree_path is empty or missing)

Use when the fix involves Dart/Flutter files.

`worktree_path:` in goal.md YAML is the persistence key.
- Empty / missing → **first run** → create worktree, write path
- Set → **resume run** → reuse existing worktree

1. **Read context**: Read goal.md and latest file in plans_and_protocols/.

2. **Extract task ID** from goal.md frontmatter (`task_id`).

3. **Create worktree**:
   ```bash
   git worktree add ../bugfix-<task-id> -b bugfix/<task-id> develop
   ```

4. **Run `flutter pub get` in the worktree** (needed so `dart analyze` works — `.dart_tool/` is not tracked by git):
   ```bash
   cd ../bugfix-<task-id> && flutter pub get
   ```

5. **Write worktree path to goal.md** — update the `worktree_path:` field:
   ```yaml
   worktree_path: "../bugfix-<task-id>"
   ```
   Use the Edit tool to set the exact relative path. This survives session restarts.

6. **Report**:
   - Worktree path and branch name
   - Remind: follow CLAUDE.md bugfix conventions (`[DIAG-*]` prints, `// TEMPORARY:` on all debug scaffolding)
   - Remind: when fix is confirmed, invoke `task-complete-bugfix` to clean up and close
   - Suggest rename: `Tipp: Session umbenennen mit /rename bugfix: <task-id> <short-description>`

## Worktree Mode — Resume Run (worktree_path is already set)

1. **Read goal.md** — get `worktree_path` and `task_id`.

2. **Verify worktree still exists**:
   ```bash
   git worktree list | grep <task-id>
   ```
   If missing (was pruned/removed), re-create it:
   ```bash
   git worktree add <worktree_path> -b bugfix/<task-id> develop
   ```

3. **Summarize prior attempts**: Read ALL files in plans_and_protocols/ chronologically. Build a concise summary of:
   - What hypotheses were tested
   - What was changed and what the outcome was
   - Where the investigation was blocked

4. **Collect new information**: Ask the user:
   > "Here's what was tried so far: [summary]. What new logs, observations, or instructions do you have for this session?"

   If the user provides new logs, save them to `plans_and_protocols/[date]_logs_[short-name].md`.

5. **Plan**: Analyze the situation and produce an updated fix plan. Include:
   - Bug report from goal.md (Steps to reproduce, Expected/Actual behavior)
   - Prior attempts summary
   - New logs / user input
   - Relevant code areas identified in previous sessions

   Write the plan to `plans_and_protocols/[date]_##_plan_<name>.md`. If strategic planning is needed and the session is not on Opus, recommend the user switch via `/model opus` before continuing.

6. **Execute plan** in the existing worktree (path from step 1).
   - **Doc-lookup checkpoint** (AC-07 / REQ-PROC-053): before editing code, invoke `doc-lookup-dependencies` for any API surface being changed:
     ```
     doc-lookup-dependencies --technology <package-id> --api-surface <dotted.path> --pinned-version <from-pubspec.lock> [--trigger <reason>]
     ```
     Prior-session lookups in `lookup_log.jsonl` are deduplicated automatically.
   - All changes go in the worktree branch, not in the main working tree
   - Follow CLAUDE.md bugfix conventions (`[DIAG-*]` prints, `// TEMPORARY:` blocks)

7. **After implementation**: Run tests from within the worktree directory.

8. **Remind**: When fix is confirmed, invoke `task-complete-bugfix` to clean up and close.
