# YAML frontmatter helper — follow-up note (2026-05-18)

Status: informational follow-up (not a task). Filed adjacent to
`requirements.md` for the next consumer of `scripts/util/yaml_frontmatter.py`
or the eventual orchestrator-split task.

Agent ID at time of writing: most recent on-disk session agent file is
`agent-a2d5c5b713d412a1c` under
`/home/vscode/.ccs/shared/context-groups/default/projects/-workspaces-private-mood-tracker-flutter-app/029f4726-5c08-41ef-9cc4-e20da1031c78/subagents/`.
The current session is running on a fresh account after the previous attempt
hit a rate limit; this session's own jsonl was not yet flushed at write time.

## Background

TASK-PROC-051-04 (`2026-05-17_impl_scripts-cleanup-to-gates-passing`) closed
with a known gotcha: `scripts/util/yaml_frontmatter.py::read_frontmatter`
crashed with `OSError: [Errno 36] File name too long (ENAMETOOLONG)` whenever
a raw text argument exceeded `NAME_MAX` (~255 bytes on most filesystems).
Agents A/B/C in Phase 1 all worked around it by calling the helper's
private `_split_frontmatter` + `_parse_yaml_block` directly instead of the
public `read_frontmatter` API.

## Fix (Job 1)

Picked **Option A** — wrap `candidate.exists()` in `try / except OSError`.

Rationale for A over B (typing-clean Path-only entry point):
1. Smallest surface-area change — no API signature shift, no caller migration.
2. Mirrors the intent of the original dispatch ("string that looks like a
   real file path? read it; otherwise treat as text"). The `OSError` branch
   simply means "this string is not a usable path".
3. `errno.ENAMETOOLONG` is not the only path-probe failure mode worth
   surviving (e.g. embedded NUL bytes raise `ValueError` historically and
   `OSError` on newer Pythons; permission errors on parents). A bare
   `except OSError` catches the entire class without enumerating errnos.
4. Option B (typing-clean) is still possible later — this fix does not block
   it.

Code change: `scripts/util/yaml_frontmatter.py`, function `read_frontmatter`,
the `else` branch (when `source` is a `str`). The `Path(source).exists()`
call is now guarded:

```python
candidate = Path(source)
try:
    is_existing_file = candidate.exists() and candidate.is_file()
except OSError:
    is_existing_file = False
if is_existing_file:
    path = candidate
    text = candidate.read_text(encoding="utf-8")
else:
    text = source
```

Inline WHY comment added explaining `ENAMETOOLONG` and pointing here.

Per the task brief, **existing caller workarounds were intentionally left in
place** as defensive code. A future task may simplify them once this fix is
proven in production.

## Regression test

Added `test_read_frontmatter_long_text_no_enametoolong` at the bottom of
`scripts/tests/test_yaml_frontmatter.py` (test #11). It passes a 1000+ byte
text string with valid frontmatter and asserts both no exception is raised
and the parsed metadata / body are correct.

## Gate run after fix

```
PASS   G1 lint
PASS   G2 type
PASS   G3 tests        (574 passed, 1 skipped)
PASS   G4 no-handrolled
PASS   G5 print-discip.

All Python quality gates PASSED.
```

`uv run pytest scripts/tests/test_yaml_frontmatter.py -x` reports
`11 passed in 1.20s`.

## Job 2 — orchestrator-split task lookup

**No existing task found** for splitting `scripts/automation/orchestrate.py`
into multiple files.

Search performed:
- `grep -rn "orchestrate" requirements_tasks/ --include="goal.md"` — all hits
  reference the orchestrator as context, none propose splitting it.
- `grep -rln -iE "split.*orchestr|orchestr.*split|modulariz.*orchestr|refactor.*orchestrate\.py|orchestrate\.py.*refactor|break.*orchestrate"` —
  only the closed TASK-PROC-051-04 goal.md (which explicitly *excludes* the
  split as out-of-scope) and the prior explore-task user-input note.
- `find requirements_tasks -type d -name "*orchestr*"` — only existing
  feat folders and completed tasks, no split task.
- Inspected `requirements_tasks/process/AI_rules/workflows/orchestrator_workflow/`
  and `…/epic_autonomous_task_execution/feat_session_orchestrator/`: no
  matching goal.md.
- Confirmed in
  `…/python_code_quality/tasks/2026-05-17_explore_define-python-code-quality-rules (completed)/plans_and_protocols/2026-05-17_00_user_initial_input.md`
  line 19:
  > "The user then asked whether the orchestrator should be split into
  > multiple files… They chose to scope the present task to the rules
  > first; **the split is a separate downstream task that should consume
  > these rules.**"

The split was deferred. No follow-up task has been created in
`requirements_tasks/`. **Recommended follow-up**: create a task (most
plausible home: `requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/feat_session_orchestrator/tasks/`,
or a new `feat_orchestrator_modularization/`) — but task creation requires
user input per project rules, so this note flags it without acting.

## Hand-off note for whoever takes the split

When extracting modules from `orchestrate.py`, the three hand-rolled YAML
sites flagged in TASK-PROC-051-04 (`update_goal_session_fields`,
`_promote_task_to_opus_for_context_limit`, `_rewrite_question_session_id`)
can now use `read_frontmatter(text)` directly, without the
`_split_frontmatter` + `_parse_yaml_block` private-API workaround — the
ENAMETOOLONG bug fixed here was the only reason they existed. Same applies
to any new call site in any newly extracted module.
