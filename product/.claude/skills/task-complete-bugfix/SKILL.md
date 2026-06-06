---
name: task-complete-bugfix
description: Clean up debug artifacts and close a bugfix task
tools: "*"
model: inherit
---

Close a bugfix task: remove temporary debug code, verify quality, complete task, and merge worktree if applicable.

## Steps

1. **Locate task**: resolve argument to task folder under `requirements_tasks/`. Read `goal.md` + `plans_and_protocols/` to understand what was added temporarily.

2. **Find changed files** — only files the bugfix branch itself touched (not files from newer develop commits):
   ```bash
   git -C <worktree_path> diff --name-only $(git -C <worktree_path> merge-base HEAD develop)..HEAD
   ```
   Read `worktree_path` from goal.md frontmatter. Run this from the **main workspace**, not the worktree.

3. **Scan for temporary artifacts** in changed files. Classify each finding:

   | Marker | Scope to remove | Action |
   |---|---|---|
   | `debugPrint(...)` with `[DIAG-*]` prefix | The single statement | **REMOVE** |
   | `// TEMPORARY:` comment | Comment + entire annotated block (route def, GoRoute, ActionGroup, screen file, function, etc. — up to closing delimiter at same indent level) | **REMOVE** |
   | Whole files that are exclusively debug scaffolding | Delete file | **REMOVE** |
   | Imports only used by removed code | The import line | **REMOVE** |
   | `debugPrint` in catch blocks (no `[DIAG-*]`) | — | **KEEP** |
   | WHY comments on bug fixes | — | **KEEP** |
   | The actual bug fix code | — | **KEEP** |

4. **Present findings**: list every REMOVE item with file:line and scope. Ask: "Proceed with these removals?"

5. **Wait for user approval**.

6. **Apply removals** using full absolute paths (files live in the worktree, not the main workspace):
   e.g. `<worktree_path>/lib/main.dart`, not `lib/main.dart`.
   Clean up unused imports last.

7. **Verify** (sequential, all commands run from within the worktree: `cd <worktree_path>`):
   - `dart fix --apply`
   - `dart analyze [changed files]`
   - `flutter test test/unit/ `
   - `flutter test test/widget/ `
   Fix issues before continuing.
   Pre-existing test failures (same failures on develop) do not block completion.

8. **Invoke `task-complete` skill** for the task — from **within the worktree** (`cd <worktree_path>`).
   The skill updates goal.md and runs Python scripts there; these changes get committed in step 9a and land in develop via the merge.

9. **Worktree cleanup** (skip if `worktree_path` in goal.md is empty):
   Use `worktree_path` and `task_id` from goal.md frontmatter.
   a. Commit all changes in worktree — this is a worktree-scoped exception where `claude-commit` cannot be used (it commits in the main working tree). Use raw git:
      ```
      git -C <worktree_path> add -A
      git -C <worktree_path> commit -m "fix: [description] refs [task_folder]"
      ```
      (For all other commits outside a worktree, use the `claude-commit` skill.)
      (skip if worktree is already clean)
   b. **Switch to main workspace**, then merge into develop:
      ```bash
      git merge --no-ff bugfix/<task-id>
      ```
      **If merge fails** ("your local changes would be overwritten"): STOP. Do NOT stash.
      Tell the user: "The merge is blocked by uncommitted changes in the main working tree. Please commit or stash those changes first, then re-invoke `task-complete-bugfix`."
      Wait for the user to resolve the conflict. Never auto-stash.
   c. Remove worktree:
      ```bash
      git worktree remove <worktree_path>
      ```
   d. Delete branch:
      ```bash
      git branch -d bugfix/<task-id>
      ```
