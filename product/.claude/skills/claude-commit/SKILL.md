---
name: claude-commit
description: Write a compliant git commit message and commit staged changes. THIS SKILL MUST BE USED TO COMMIT CHANGES.
tools: [Bash, Read]
model: inherit
---

You write a git commit message that follows this project's conventions, then commit staged changes.

## Steps

1. Run `git diff --staged` to review what is staged
1b. **Collect lookup stats** (skip silently on any error):
   ```bash
   GOAL=$(grep -rl "^status: in_progress" requirements_tasks/ --include="goal.md" 2>/dev/null | head -1)
   LOG="${GOAL%goal.md}plans_and_protocols/lookup_log.jsonl"
   [ -s "$LOG" ] && python3 -c "
   import json, collections, sys
   decisions = collections.Counter()
   for line in open(sys.argv[1]):
       line = line.strip()
       if line:
           decisions[json.loads(line).get('decision', '')] += 1
   looked = decisions.get('looked_up', 0)
   skipped = sum(decisions[k] for k in decisions if k.startswith('skipped'))
   fallbacks = decisions.get('fallback_websearch', 0)
   parts = []
   if looked: parts.append(f'{looked} looked_up')
   if skipped: parts.append(f'{skipped} skipped')
   if fallbacks: parts.append(f'{fallbacks} fallback')
   if parts: print('Lookups: ' + ', '.join(parts))
   " "$LOG" 2>/dev/null
   ```
   Save the output line (if any) to include in the commit body.
2. Determine `type` and `scope` from the tables below
3. Draft subject line — imperative mood, lowercase after colon, ≤ 72 chars, no period
4. Add body only if the *why* is non-obvious (blank line before body). If step 1b produced a lookup summary, always append it as a trailing line in the body.
5. Run `git commit -m "..."` — **NEVER chain `git add && git commit`**
6. **Post-commit check**: Run `git status` and review unstaged/untracked files
   - Ignore files clearly unrelated to the current task (different feature, different scripts, pre-existing changes)
   - If any related files were missed (e.g. stale deleted paths, renamed folders not fully staged, generated files): stage them and make a follow-up commit using the same scope + `chore` type
   - If nothing relevant remains: output "Working tree clean for this task."
7. **Optimizer events**: Run `git ls-files --others --exclude-standard .factory/optimize/events/`
   - If any files are listed: `git add .factory/optimize/events/` then commit: `chore(optimize): collect pending skill-change events`

## Type Selection

Prefer standard Conventional Commits types. Use project-specific types only for non-code factory artifacts.

| Type | Use when | Do NOT use when |
|------|----------|-----------------|
| `feat` | Adding or changing a capability, artifact, or behavior — code, skills, scripts, design rules, new task files | just removing or cleaning up |
| `fix` | Something was broken; this restores correct behavior | adding a new capability alongside the fix (use `feat`) |
| `refactor` | Code restructure with no behavior change | anything that changes what the app does |
| `test` | Test files only | production code is also touched |
| `docs` | Documentation only — merged docs, README, guidelines | requirements artifacts (use `requ`) |
| `chore` | Removing, renaming, updating deps, cleanup — nothing new is added | something new is added (use `feat`) |
| `build` | Build system, CI, pubspec, generated plugin files | |
| `requ` | Requirements artifacts: `requirements.md`, task frontmatter, `RELEASES.md` | task `goal.md` / protocol files (use `feat` or `chore`) |
| `task` | Task lifecycle only: creating or completing a `goal.md` task file | implementing the task's work (use `feat`) |
| `explore` | Committing the output of an exploration task (protocol, findings doc) | |

**Removed types** (do not use):
- `impl` → use `feat` with a TASK-ID scope
- `meta` → use `chore` with scope `skills`, `claude`, or `infra`

**Decision shortcuts:**
- "I added/changed something" → `feat`
- "I deleted/cleaned up something" → `chore`
- "I changed a requirements file" → `requ`
- "I created a task goal.md" → `task`
- "Something was wrong and now it's right" → `fix`

## Scope Selection

| Situation | Scope |
|-----------|-------|
| Work belongs to a single TASK-* | TASK-ID (e.g. `TASK-FUNC-007-02`) |
| Platform-specific change | `android` / `windows` / `linux` |
| Feature area | `infra`, `data-transfer`, `proc`, `skills`, `next_tasks`, `test` |
| Factory tooling (skills, CLAUDE.md) | `skills` or `claude` |
| Cross-cutting / no clear owner | omit scope |

## Rules

- Imperative: "add", "fix", "remove" — **not** "added", "fixes"
- TASK-ID goes in scope, **not** appended to the end of the subject
- Breaking change: add `!` after type/scope + `BREAKING CHANGE:` footer
- Never use `--no-verify`

## Examples

```
feat(TASK-FUNC-007-02): implement QR scan pipeline
fix(android): map nv21 and jpeg to correct image format
chore(skills): remove deprecated task-rollover skill
chore(automation): pause session for TASK-PROC-035-17 — requ-explore
chore: rename post-push to pre-push
refactor(test): enforce unit/widget folder structure
docs: update merged requirements.md
requ: add CodeGraph integration (REQ-PROC-038)
task: create TASK-PROC-038-01 — integrate CodeGraph into skills
feat(skills): add bugfix skill
build: update generated Flutter plugin files
explore(TASK-PROC-037-01): analyze personas for external communication gaps
```
