# Prior Findings — Seed Material for the Exploration

Carried forward from the conversation that led to this task. **Treat as starting points, not conclusions.** The exploration is free to discard, reorder, or invert any of these.

## Quantitative context (motivation strength)

- `scripts/automation/orchestrate.py` — **3328 lines** (single file)
- `scripts/automation/tests/test_orchestrate.py` — **5031 lines**
- Total Python in this repo under no `doc/` governance: **~8 359 lines** (orchestrator + its tests; further Python in `scripts/tasks/`, `scripts/requirements/`, `scripts/artifacts/`, `scripts/user_needs/`, `scripts/release/`, `scripts/windows/` not counted here)
- `doc/` currently has 8 categories — all about Dart in `lib/`, `test/`, `integration_test/`. Zero Python guidance.

## Proposed initial scope (the agent's suggestion)

`doc/python/` mirroring the Dart `doc/architecture/`, `doc/testing/`, `doc/linter/` pattern but narrower. Five files were suggested as the minimum starting set:

| File | Content (proposed) |
|---|---|
| `doc/python/README.md` | Index, table of contents, "when this applies" |
| `doc/python/style.md` | `ruff` config + formatting rules + line length + naming |
| `doc/python/type_hints.md` | Mandatory return-type annotations, `mypy` config |
| `doc/python/dependency_injection.md` | The `OrchestratorDeps` pattern + when/how to use it + frozen-clock testing rule |
| `doc/python/testing.md` | Pytest conventions, fakes via Deps over `mock.patch`, fixture design |
| `doc/python/architecture.md` | Module-layout rules, when/how to split files |
| `doc/python/error_handling.md` | (Optional) Exception types, retry vs raise, logging semantics |

The exploration should decide whether 5 / 6 / 7 files is right, and whether some collapse (e.g. style + type_hints into one).

## Patterns already in use in `scripts/automation/orchestrate.py` that deserve to become project canon

These emerged organically during the conversation's refactors. They are NOT codified anywhere today.

### Dependency injection via dataclass-of-callables

`OrchestratorDeps` is a dataclass of callables (one per side-effect: `run_subprocess`, `read_file`, `write_file`, `get_now_utc`, `get_now_local`, `sleep`, `getpid`, ...). Tests substitute fakes per boundary. Better than `@patch("subprocess.run")` because it scopes to one function and doesn't leak into unrelated code.

Rule worth encoding: **every side-effecting operation in `scripts/automation/` and similar long-lived Python must go through a Deps dataclass.** When you find yourself wanting to mock at module level, the right move is to add the callable to the Deps.

### Frozen-clock testing

Tests must read time via `deps.get_now_utc` / `deps.get_now_local`, never `datetime.now()`. The Deps default is real `datetime.now`, but tests inject a frozen value.

The exploration should call out: we already had a bug here. `next_available_account` previously used real `datetime.now(timezone.utc)` directly. As soon as wall-clock advanced past hardcoded test dates (2026-05-16 in `TestProcessAnsweredFeedbackRateLimitedAccountSwitch`), three tests started failing. We fixed it by threading `now_utc` through the call chain. The rule needs to be explicit so this doesn't recur.

### Context manager for invariant cleanup

`active_session(state, uuid, deps)` is a `@contextmanager` that sets `state.active_session = uuid`, saves, runs the block, and clears+saves in `finally`. Five launch sites previously hand-rolled this set/save/launch/clear/save pattern. If the launch raised, the clear was skipped → orphan in `state.json`.

Rule worth encoding: **invariants that must hold across try/except boundaries belong in a context manager, not hand-rolled at every call site.**

### Small helper methods on dataclasses for dual-tracking invariants

`RunData.mark_exhausted(*, session_id, task_id=None)` adds to both `exhausted_resume_ids: set` and `exhausted_resume_tasks: list` in one call. Previously every caller had to `.add()` to the set AND `.append()` to the list, and forgetting one was the root cause of a real bug (TASK-PROC-046-03 incident 2026-05-16).

Rule worth encoding: **when two parallel fields encode one conceptual fact, the mutation should be a single method, not a calling-convention.**

### Enum over bool when there are 3+ outcomes

`PromoteResult` enum (`PROMOTED` / `ALREADY_AT_MAX` / `NO_PROMOTABLE_FIELD` / `UNREADABLE`) replaced a `bool` return whose `False` conflated three distinct cases. Callers can now branch on the specific reason, and the log messages already differ per case.

Rule worth encoding: **bool returns are only honest when the answer really is yes/no.** Three or more outcomes → enum.

### Small factory for record construction

`make_session_record(*, account, task_id, is_resume, deps, **extra)` builds the common-shape dict that all 5 session-launch sites need, with variant fields passed as `**extra`. Reduces 6-line dict literals to 4-line keyword calls and keeps the common fields canonical.

Open question for the exploration: should this be a `@dataclass class SessionRecord` instead of a dict? Probably yes if any callsite ever consumes it via attribute access; the current code uses `.get()` and indexing.

## Anti-patterns observed in the codebase

Worth calling out by name so future contributors / agents stay clear of them.

### Hand-rolled YAML parsing across multiple functions

Three functions (`update_goal_session_fields`, `_promote_task_to_opus_for_context_limit`, `_rewrite_question_session_id`) each contain their own line-by-line frontmatter parser with `in_frontmatter` / `fm_ended` state machines. They share a bug surface — a fix to one doesn't propagate to the others. PyYAML is a one-import dependency that handles edge cases.

Rule worth encoding: **don't hand-parse YAML.** If a hard constraint (e.g. preserving comments) forces it, centralize the parser in one helper and reuse.

### `print()` for internal logging

Every status / debug message in the orchestrator uses `print(f"[orchestrator {_ts()}] ...")`. This is the public protocol consumed by `sleep_when_autorun_done.ps1` and the monitoring cron — so it's not purely an anti-pattern. But it conflates "user-visible status" with "internal debug" and there's no way to filter by level.

Open question for the exploration: keep `print()` as the user-facing protocol (with a `_print_status` helper for that) AND add proper `logging` for internal debug? Or accept the current cost?

### `bool` return when there are 3+ outcomes

(See `PromoteResult` above — already fixed in code, deserves to become a documented rule.)

### Sessions_launched counter that bumped on errors

Before today's fix: rate-limit, perm-error, context-overflow all bumped `sessions_launched` (the `--max-tasks` counter). Effect: a few unlucky early failures could exhaust the budget before any real work. New policy: only `result.returncode == 0` bumps the counter.

The semantic rule that emerged: **don't double-charge for infrastructure failure.** Whatever a "session" or "attempt" or "slot" tracks, the spec should be explicit about whether errors count, and the implementation should match. The previous code had three different paths in the same file with three different behaviors.

### Pre-launch bookkeeping duplicated across launch sites

Five launch sites used to hand-roll the same `{"start": deps.get_now_local(), "account": account, "task_id": ..., "is_resume": ...}` dict. The `make_session_record` factory now centralizes the common fields. The duplication still exists for the surrounding code (build_env, generate uuid, register_session_in_goal, active_session). Worth a "session launch helper" only if a 6th site appears.

## Open meta-questions for the exploration

These came up in the conversation but were intentionally deferred:

1. **Should REQ-PROC-046 (Dart code quality) be made explicitly Dart-only in its title and "When This Requirement Applies" section?** Today it's implicitly Dart by the paths it cites. A new Python sibling makes the implicit scoping confusing.

2. **Should `coding_standards/` get a shared parent `requirements.md`** that says "code quality requirements may be scoped per language; see `code_quality/` (Dart) and `python_code_quality/` (Python)"? Or is that bureaucratic?

3. **Renaming question**: should `code_quality/` be renamed to `code_quality_dart/` for symmetry? Cost: a folder rename + every task_id under it stays valid (they reference REQ-PROC-046 by ID, not path), but the path change touches `requirements_version.file` references in goal.md files.

4. **Does Python's `testing/` need a parallel?** Currently `coding_standards/testing/` is implicitly Dart. The Python tests have very different conventions (Deps injection, frozen clocks) and the rules don't transfer cleanly. Either rename existing → `testing_dart/` + add `testing_python/`, or scope-extend with sections.

5. **Tooling integration**: should the Python rules also produce a `pyproject.toml` with `ruff` + `mypy` config? That's a deliverable that lives outside `doc/`. The exploration should decide whether tooling config goes in this requirement's scope or a sibling tooling task.

6. **What about `scripts/tasks/`, `scripts/requirements/`, etc.?** They're also Python and currently uncovered. Should the Python rules cover ALL Python in the repo, or only the long-lived orchestrator?

7. **Back-pressure equivalent**: REQ-PROC-046 has a "back-pressure protocol" (LLM cannot declare a change complete while any gate fails, 5-cycle bound, etc.) — should the Python rules adopt the same protocol, or is it too heavyweight for the orchestrator's scope?

## Concrete deliverables the user expects (if the exploration converges)

When asked "Want me to draft those?" referring to the `doc/python/` files, the user said yes (then redirected to creating this task instead so the work has a proper home). So when the exploration completes, the next-stage tasks should include:

- An `impl` task to author `doc/python/` files per the exploration's chosen structure
- Possibly an `impl` task to update or restructure REQ-PROC-046 + sibling requirements
- Possibly an `impl` task to add `pyproject.toml` + `ruff` / `mypy` config to the repo

The exploration's job is to decide which of those is in / out of scope and produce concrete next-step goal.md files (or leave them for `requ-derive-from-flow` equivalent).
