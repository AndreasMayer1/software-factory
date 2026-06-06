# Architecture Design: orchestrate.py Rewrite

**Date**: 2026-04-10
**Author**: Opus (planning phase)
**Status**: For review — design document only, no code written

---

## Objective

Redesign `scripts/automation/orchestrate.py` (currently 1241 lines) so that every piece of
business logic lives in a pure or easily-mockable function/class, decoupled from I/O and
subprocess calls. The rewrite must:

- Preserve all existing behaviour exactly (same CLI, same exit codes, same log messages)
- Incorporate all new ACs (AC-18 through AC-26) from the current task
- Enable practical unit tests without monkey-patching `subprocess.run` globally
- Remain a single file (or a trivially small package) — no over-engineering

---

## Analysis Summary

### Current structure

| Layer | What lives there | Problem |
|---|---|---|
| Module-level constants | `PROJECT_ROOT`, paths, regex patterns | Fine — no change needed |
| Pure helpers | `interruptible_sleep`, `strip_hook_footer`, `parse_rate_limit_reset`, `answer_is_empty`, `read_yaml_frontmatter` | Already testable — keep as-is |
| I/O helpers | `load_state`, `save_state`, `write_session_output`, `write_report`, `write_health_summary`, `cleanup_old_artifacts`, `update_goal_session_fields` | Mix file I/O with logic — extractable |
| Subprocess helpers | `run_normal_session`, `run_resume_session`, `find_active_task_goal`, `find_resumable_session`, `snapshot_in_progress_tasks` | Subprocess calls embedded — hard to mock |
| Feedback helpers | `find_answered_feedback`, `get_unanswered_questions`, `new_question_written_for` | File I/O only — testable with temp dirs |
| Account management | `next_available_account`, `build_env` | Pure logic — already testable |
| Main loop (`main()`) | 400 lines doing EVERYTHING | Untestable monolith |

### Root testability problems

1. `main()` has no seams — it calls `subprocess.run`, `os.makedirs`, `open()`, signal handlers,
   and the main loop all inline with no injection points.
2. The main loop mixes policy decisions ("should I resume?", "is queue empty?") with I/O actions
   ("write state", "write report") — you cannot test policy without triggering I/O.
3. `find_resumable_session` and `snapshot_in_progress_tasks` call `subprocess.run(["grep", ...])` —
   these can be replaced with pure Python `os.walk` + file reading, removing the subprocess
   dependency entirely and making them testable with temp directories.
4. `disabled_accounts` is a bare `set` inside `run_data` dict, mutated across the loop — not
   encapsulated.

### Scope of new ACs (AC-18–AC-26)

| AC | Type | Where it fits |
|---|---|---|
| AC-18 | Queue check (empty output) | Pre-flight decision in loop step |
| AC-19 | Account pool graceful stop | `next_available_account()` fix + loop handler |
| AC-20 | Whitespace answer fix | `answer_is_empty()` fix |
| AC-21 | Resume attempt limit | New state tracking in `RunState` |
| AC-22 | No-session-id skip + log | New scan before `find_resumable_session` |
| AC-23 | Git commit on start | New `git_commit_best_effort()` helper |
| AC-24 | Git commit on stop | Call in `finally` block |
| AC-25 | `fcntl` lock | Startup guard in `main()` |
| AC-26 | Jaccard question similarity | Two new pure functions |

---

## 1. Module Structure

The rewrite stays in **one file**: `scripts/automation/orchestrate.py`.

Internal organisation into clearly delimited sections (separated by `# ---` comment banners):

```
Section 1: Imports + constants          (unchanged)
Section 2: Pure utility functions       (pure Python, no I/O, no subprocess)
Section 3: I/O adapters                 (file read/write; injectable via dataclass)
Section 4: Subprocess adapters          (subprocess calls; injectable via dataclass)
Section 5: Domain logic / RunState      (business rules, operating on plain data)
Section 6: Main loop decomposition      (named step functions, thin orchestration)
Section 7: Entry point (main)           (wiring only — no logic)
```

The test file can import any section independently because nothing at module level has
side effects.

---

## 2. Dependency Injection Pattern

### The problem with global patching

`@patch("subprocess.run")` in a test patches globally and leaks into unrelated code.
`@patch("os.path.exists")` breaks the test framework itself.

### The solution: `OrchestratorDeps` dataclass

```python
@dataclass
class OrchestratorDeps:
    """Injectable I/O and subprocess boundaries. Tests substitute fake implementations."""
    # Subprocess
    run_subprocess: Callable[..., subprocess.CompletedProcess]  # default: subprocess.run
    run_grep: Callable[[str, str], list[str]]  # grep for in_progress tasks → list of paths

    # Filesystem
    read_file: Callable[[str], str]                  # default: open(path).read()
    write_file: Callable[[str, str], None]            # default: open(path, 'w').write(content)
    file_exists: Callable[[str], bool]               # default: os.path.exists
    list_dir: Callable[[str], list[os.DirEntry]]     # default: list(os.scandir(path))
    makedirs: Callable[[str], None]                  # default: os.makedirs(path, exist_ok=True)
    glob_files: Callable[[str], list[str]]           # default: glob.glob(pattern)

    # System
    get_now_utc: Callable[[], datetime]              # default: lambda: datetime.now(timezone.utc)
    get_now_local: Callable[[], datetime]            # default: datetime.now
    sleep: Callable[[float], None]                   # default: time.sleep
    getpid: Callable[[], int]                        # default: os.getpid
```

**Why a dataclass, not a class hierarchy**: The orchestrator is a single-concern script. A
dataclass of callables gives 100% mockability without the ceremony of abstract base classes.
Tests instantiate `OrchestratorDeps` with lambda substitutions for each boundary they care
about.

**Production wiring** (in `main()`):

```python
deps = OrchestratorDeps(
    run_subprocess=subprocess.run,
    run_grep=_grep_in_progress_goal_paths,
    read_file=lambda p: open(p).read(),
    write_file=lambda p, c: open(p, 'w').write(c),
    file_exists=os.path.exists,
    list_dir=lambda p: list(os.scandir(p)),
    makedirs=lambda p: os.makedirs(p, exist_ok=True),
    glob_files=glob.glob,
    get_now_utc=lambda: datetime.now(timezone.utc),
    get_now_local=datetime.now,
    sleep=time.sleep,
    getpid=os.getpid,
)
```

Test wiring (example):

```python
deps = OrchestratorDeps(
    run_subprocess=lambda cmd, **kw: FakeResult(returncode=0, stdout="ok"),
    run_grep=lambda req_dir: ["/fake/goal.md"],
    read_file=lambda p: FAKE_FILES[p],
    ...
)
```

### Why NOT pass `deps` everywhere as a parameter

Passing `deps` as a parameter to every function creates noisy signatures. Instead, the
`Orchestrator` class (Section 5) holds `deps` as an instance attribute. Functions in Sections
2 and 4 that need I/O are either pure (no injection needed) or methods of `Orchestrator`.

---

## 3. State Management

### Two state objects, clearly separated

**`PersistentState`** — what lives in `state.json`, survives restarts:

```python
@dataclass
class PersistentState:
    account_index: int = 0
    run_count: int = 0
    start_time: str | None = None       # ISO string
    paused_tasks: list = field(default_factory=list)
    rate_limited_until: dict = field(default_factory=dict)   # account -> ISO datetime string
    question_fingerprints: dict = field(default_factory=dict)  # task_id -> {words: list, preview: str}
```

`load_state(path, deps)` returns `PersistentState`, `save_state(path, state, deps)` writes it.
Both use atomic write (tmp + replace). Tests can pass fake `deps.read_file` / `deps.write_file`.

**`RunData`** — in-memory accumulator for the current run (never written to state.json):

```python
@dataclass
class RunData:
    start_time: datetime
    sessions: list[SessionRecord] = field(default_factory=list)
    accounts_used: set[str] = field(default_factory=set)
    disabled_accounts: set[str] = field(default_factory=set)
    exhausted_resume_ids: set[str] = field(default_factory=set)
    resume_attempt_counts: dict[str, int] = field(default_factory=dict)   # session_id -> count (AC-21)
    exhausted_resume_tasks: list[str] = field(default_factory=list)        # AC-21 report
    skipped_no_session_id: list[str] = field(default_factory=list)         # AC-22 report
    repeated_questions: list[dict] = field(default_factory=list)           # AC-26 report
    initial_in_progress: dict = field(default_factory=dict)                # task_id -> goal_path
    stop_time: datetime | None = None
    stop_reason: str = "manual"
```

`SessionRecord` is a small typed dataclass replacing the current ad-hoc dicts:

```python
@dataclass
class SessionRecord:
    start: datetime
    end: datetime | None = None
    account: str = ""
    task_id: str = "unknown"
    session_uuid: str = ""
    is_resume: bool = False
    exit_code: int | None = None
    output_excerpt: str = ""
    rate_limited: bool = False
    reset_at: str | None = None
```

**Why typed dataclasses over dicts**: Attribute access catches typos at development time;
`dataclasses.asdict()` provides dict serialisation when needed for report generation.

---

## 4. Main Loop Decomposition

The current `while True:` loop is 400 lines with 6 different code paths interleaved.
The rewrite decomposes it into named step functions, each with a clear contract:

```
LoopDecision = Literal["continue", "break", "skip_to_next_iter"]
```

### Step functions (all methods on `Orchestrator`):

#### `check_stop_conditions(state, run_data, args) -> tuple[bool, str]`
Checks: `stop_flag`, `.stop-requested` sentinel, `--stop-at`, `--max-tasks`.
Returns `(should_stop, reason)`. Pure — no I/O, testable with frozen time.

#### `process_answered_feedback(state, run_data, args) -> LoopDecision`
Calls `find_answered_feedback()`, runs one resume session, updates `run_data`, saves state.
Returns `"continue"` if an answer was processed (loop restarts), `"skip_to_next_iter"` otherwise.

#### `scan_unanswered_questions(run_data) -> list[UnansweredQuestion]`
Returns list of tasks with `question.md` but no `answer.md`. Logs them. No side effects on
`run_data` — caller decides whether to stop.

#### `scan_in_progress_without_session_id(run_data) -> list[str]`  ← new for AC-22
Finds all `in_progress` tasks with no `session_id`. Logs each one. Appends to
`run_data.skipped_no_session_id`. Returns list of task_ids to exclude from resumable search.

#### `process_in_progress_resume(state, run_data, args) -> LoopDecision`
Calls `find_resumable_session()`, applies AC-21 attempt counting, runs resume session, handles
perm error / rate limit / generic failure. Returns `"continue"` if a resume was processed.

#### `run_preflight_queue_check(state, run_data) -> tuple[bool, str | None]`  ← AC-18 + existing
Calls `next_tasks.py`, filters with `is_awaiting_answer.py`. Returns:
- `(True, None)` if runnable tasks exist
- `(False, "all_tasks_awaiting_answer")` if tasks exist but all are blocked
- `(False, "queue_empty")` if `next_tasks.py` returns no tasks at all  ← AC-18

#### `wait_for_account_if_needed(state, run_data, accounts, args) -> tuple[str | None, bool]`  ← AC-19
Calls `next_available_account()`. Returns `(account, False)` if available now, or `(None, True)`
if a sleep was needed (caller re-enters loop). Handles `None, None` sentinel from AC-19 fix
by returning `(None, False)` with `stop_reason = "all_accounts_disabled"`.

#### `run_normal_session_step(state, run_data, account, args) -> LoopDecision`
Generates UUID, updates `goal.md`, launches session, handles perm error / rate limit / success.

### The rewritten loop (pseudocode):

```python
def run_loop(self, state, run_data, accounts, args):
    while True:
        stop, reason = self.check_stop_conditions(state, run_data, args)
        if stop:
            run_data.stop_reason = reason
            break

        decision = self.process_answered_feedback(state, run_data, args)
        if decision == "continue":
            continue

        unanswered = self.scan_unanswered_questions(run_data)
        self.scan_in_progress_without_session_id(run_data)  # AC-22 — always scan

        decision = self.process_in_progress_resume(state, run_data, args, unanswered)
        if decision == "continue":
            continue

        ok, stop_reason = self.run_preflight_queue_check(state, run_data)
        if not ok:
            run_data.stop_reason = stop_reason
            break

        account, waited = self.wait_for_account_if_needed(state, run_data, accounts, args)
        if waited:
            continue
        if account is None:
            run_data.stop_reason = "all_accounts_disabled"
            break

        decision = self.run_normal_session_step(state, run_data, account, args)
        # decision is always "continue" after a normal session
```

The loop body is now ~25 lines. Every decision path is in a named, independently testable
method.

---

## 5. New Functions from AC-17–AC-26

### `git_commit_best_effort(files: list[str], message: str, deps: OrchestratorDeps) -> None`  (AC-23, AC-24)

Pure subprocess call. Non-fatal: catches all exceptions and logs WARNING.

```
git add <each file that exists>
git commit -m <message>
```

Placed in Section 4 (subprocess adapters). Testable by injecting a fake `run_subprocess`.

### `_find_in_progress_without_session_id(project_root, deps) -> list[str]`  (AC-22)

Scans `requirements_tasks/` for `goal.md` files with `status: in_progress` and no `session_id`
field (or `session_id: ""`). Returns list of `task_id` values. Uses `deps.run_grep` (or pure
Python file walk — see migration note below). Placed in Section 3 (I/O adapters).

### `compute_question_fingerprint(text: str) -> dict`  (AC-26)

Pure function — no I/O, no subprocess.

```python
def compute_question_fingerprint(text: str) -> dict:
    normalized = re.sub(r'[^\w\s]', '', text.lower())
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    words = set(normalized.split())
    return {"words": list(words), "preview": normalized[:300]}
```

Placed in Section 2 (pure utilities). Zero dependencies. Trivially unit-tested.

### `check_and_update_question_fingerprint(task_id, question_body, state, run_data, deps) -> None`  (AC-26)

Loads existing fingerprint from `state.question_fingerprints[task_id]`, computes Jaccard
similarity, logs WARNING if ≥ 0.60, appends to `run_data.repeated_questions`, updates
fingerprint in state. Placed in Section 5 (domain logic). Testable with fake `PersistentState`
and `RunData` instances.

**Jaccard implementation**:
```python
def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0
```

### Answer whitespace fix — `answer_is_empty()`  (AC-20)

Extend existing function: after the size-zero check, open the file and check
`content.strip() == ""`. Log WARNING. This is a one-line extension to an existing pure-ish
function. No structural change needed.

### `next_available_account()` fix  (AC-19)

When all accounts are in `disabled_accounts` AND `rate_limited` is empty, the current code
calls `min()` on an empty sequence → `ValueError`. Fix: detect this before the `min()` call.

```python
available_rate_times = {
    acct: t for acct, t in rate_limited.items()
    if acct not in (disabled_accounts or set())
}
if not available_rate_times:
    return None, None   # sentinel: all accounts gone permanently
earliest = min(datetime.fromisoformat(t) for t in available_rate_times.values())
...
```

The caller interprets `(None, None)` as `stop_reason = "all_accounts_disabled"`.

---

## 6. Test Architecture

### Test file location

`scripts/automation/tests/test_orchestrate.py`

One file is sufficient for ~150 test functions. If it grows beyond ~500 lines, split by concern:
- `test_pure_utils.py` — pure computation functions
- `test_state.py` — `PersistentState` load/save
- `test_loop_steps.py` — loop step methods
- `test_integration.py` — full `run_loop()` with fake subprocess

### What to mock

| What | How |
|---|---|
| `subprocess.run` | Inject via `deps.run_subprocess` — return `FakeResult(returncode, stdout)` |
| `grep` for in_progress tasks | Inject via `deps.run_grep` — return list of paths |
| File reads | Inject via `deps.read_file` — return dict lookup |
| File writes | Inject via `deps.write_file` — append to list for assertion |
| `os.path.exists` / `os.scandir` | Inject via `deps.file_exists` / `deps.list_dir` |
| `datetime.now()` | Inject via `deps.get_now_local` / `deps.get_now_utc` |
| `time.sleep` | Inject via `deps.sleep` — record calls |

### Test categories and approximate counts

#### Category A: Pure utility functions (Section 2) — ~25 tests

- `parse_rate_limit_reset`: timezone parsing, missing regex match, day-rollover edge case
- `strip_hook_footer`: with/without footer, multi-line footer
- `compute_question_fingerprint`: normalization, word set, preview truncation
- `_jaccard`: empty sets, identical sets, partial overlap, threshold boundary
- `answer_is_empty`: non-existent file, zero bytes, whitespace-only (AC-20), real content

#### Category B: State management — ~15 tests

- `load_state`: missing file, corrupt JSON, missing keys filled with defaults,
  `question_fingerprints` key present/absent
- `save_state`: atomic write (tmp + replace), OSError handling
- `PersistentState` serialisation round-trip (sets stored as lists for JSON)

#### Category C: Account management — ~15 tests

- `next_available_account`: all available, some rate-limited, all rate-limited (wait),
  one disabled + others available, all disabled + none rate-limited → `(None, None)` (AC-19),
  corrupt reset time, rate limit window cleared

#### Category D: Feedback helpers — ~20 tests

- `find_answered_feedback`: empty dir, malformed frontmatter, empty answer, whitespace answer
- `get_unanswered_questions`: mixed answered/unanswered
- `new_question_written_for`: present/absent, whitespace answer treated as absent
- `check_and_update_question_fingerprint`: no prior fingerprint, similarity < 0.60, ≥ 0.60
  (AC-26), state update, `run_data.repeated_questions` populated

#### Category E: Loop step methods — ~40 tests

- `check_stop_conditions`: each stop condition independently (flag, sentinel, schedule, max_tasks)
- `process_answered_feedback`: none found, one found + successful, rate-limited resume,
  perm error resume, resume attempt count increment (AC-21), max attempts exceeded (AC-21)
- `scan_in_progress_without_session_id`: zero found, one found (log + report), multiple (AC-22)
- `process_in_progress_resume`: none resumable, resumable + success, perm error, rate limit,
  generic failure, attempt limit hit (AC-21), account switch for blocked stored account
- `run_preflight_queue_check`: no tasks at all (AC-18 queue_empty), all blocked, some runnable
- `wait_for_account_if_needed`: account available, all rate-limited (sleep), all disabled (AC-19)
- `run_normal_session_step`: success, perm error, rate limit

#### Category F: Git helpers — ~10 tests

- `git_commit_best_effort`: success, git not found, nothing to commit, glob finds files (AC-23/24)

#### Category G: Report / health summary — ~15 tests

- `write_report`: sections present, new sections (skipped no session_id, exhausted resumes,
  repeated questions), pending feedback section
- `write_health_summary`: no initial tasks, tasks completed, tasks stuck, verdict logic

#### Category H: Integration (full loop) — ~10 tests

These run `run_loop()` with a fully fake `OrchestratorDeps` that simulates:
- Normal progression: 3 sessions complete → `max_tasks` stop
- Queue empty detection (AC-18)
- All accounts disabled (AC-19)
- Resume attempt limit (AC-21)
- Same question fingerprint detection (AC-26)

**Coverage target**: 90%+ line coverage on the module (excluding `main()` entry point and
module-level constants). The entry point `main()` is excluded from coverage requirements because
it only wires together already-tested components.

**Test runner**: `python3 -m pytest scripts/automation/tests/ -v`

No new dependencies required — `pytest` is already available in the devcontainer.

---

## 7. Migration Strategy

### Option analysis

**Option A** — AC-18–AC-26 changes on old code first, then rewrite separately  
Pro: current task closes quickly; rewrite is cleanly scoped.  
Con: implements the new ACs twice (once in old code, once in rewrite). High risk of
introducing bugs during the second implementation. Wastes effort.

**Option B** — Rewrite first (incorporating all new ACs), then verify ACs pass  ← RECOMMENDED  
Pro: each AC is implemented exactly once in the clean architecture. Tests verify all ACs
simultaneously. No dual-maintenance period.  
Con: the task scope is larger than originally stated in `goal.md` — requires user approval.

**Option C** — Incremental rewrite: restructure then add ACs as commits  
Pro: git history is more readable.  
Con: intermediate commits leave ACs partially implemented — no clean "all ACs pass" checkpoint
until the end.

### Recommendation: Option B

The rewrite should be done **within the current task** (TASK-PROC-041-01-05), replacing the
scope of "implement AC-18–AC-26 as patches" with "rewrite the file implementing all ACs".

**Justification**:
- The new ACs (AC-18–AC-26) are simple enough that implementing them in the patching style
  is straightforward — but patching the monolith makes them harder to test and verify.
- The rewrite itself is estimated at ~3–4 hours of focused work; the test suite is the bulk.
- The `goal.md` ACs are all verifiable via the new test suite. The acceptance criteria do not
  change; only the implementation approach is cleaner.

**If the user wants to split**: create a new task for the rewrite and close this task with
only the AC-18–AC-26 patches applied to the old code. This is less efficient but respects
task scope.

---

## 8. Risk Assessment

### Risk 1 — Behaviour divergence in the rewrite (HIGH)

The current code has subtle behaviour in the main loop that is only visible through careful
reading: the feedback resume path uses `item["account"]` (original account) not the round-robin
account; the resume path for in-progress tasks switches accounts if the stored one is blocked;
`sessions_launched` is incremented differently across paths.

**Mitigation**: Before writing a single line of rewrite, create a comprehensive characterisation
test suite that runs against the _current_ code. These tests document the exact existing
behaviour. The rewrite passes when all characterisation tests pass.

**Specific areas to characterise**:
- `sessions_launched` counting under perm error vs. rate limit vs. success
- Account rotation after rate limit on resume (does index advance?)
- `min_wait_seconds` applied only on success paths
- `run_count` vs `sessions_launched` — are they the same counter?

### Risk 2 — `grep`-based file scanning replaced with Python walk (MEDIUM)

`find_resumable_session` and `snapshot_in_progress_tasks` call `subprocess.run(["grep", "-rl", ...])`.
The rewrite proposes replacing these with pure Python `os.walk` + file reading to eliminate the
subprocess dependency. This risks:
- Performance regression (Python walk is slower for large repos)
- Missed files if the grep regex is subtly different

**Mitigation**: Keep the grep-based approach as the production implementation but inject it via
`deps.run_grep`. Tests can substitute a lambda that returns a hardcoded path list. No need to
replace grep with Python walk — just make it injectable.

### Risk 3 — `fcntl` lock file interaction with tests (LOW)

AC-25 uses `fcntl.flock` which is OS-level. Tests that exercise `main()` cannot easily mock
this without subprocess isolation.

**Mitigation**: The lock acquisition is in `main()` only, which is excluded from unit test
coverage requirements. Integration tests that need to call `main()` directly should use
`/tmp/test_orchestrator.lock` (set via a test-only constant) or skip the lock step via a
test-mode flag (a single `_skip_lock: bool = False` parameter on `main()` is acceptable for
test isolation without polluting the production interface).

### Risk 4 — JSON serialisation of sets (AC-26) (LOW)

`question_fingerprints` stores word sets. Python `set` is not JSON-serialisable. The current
`save_state` uses `json.dump` directly. If a set accidentally enters the state dict, `save_state`
will crash silently (it catches `OSError` but not `TypeError`).

**Mitigation**: `PersistentState` explicitly serialises `question_fingerprints.words` as `list`
on save and deserialises back to `set` on load. Add a `TypeError` catch to `save_state` that
logs a clear error message. Add a unit test that round-trips a fingerprint through JSON.

### Risk 5 — Report filename collision in `finally` block (LOW)

The current `main()` generates the report filename inside `write_report()` and then
reconstructs it (using `datetime.now()` again) to call `write_health_summary()`. If the
minute ticks over between the two calls, the health summary is appended to a non-existent
file.

**Mitigation**: `write_report()` should return the path it wrote to. `write_health_summary()`
receives that path directly. This is a pre-existing bug that the rewrite fixes for free.

---

## 9. File Map

### Files created/modified

| File | Change |
|---|---|
| `scripts/automation/orchestrate.py` | Complete rewrite (same filename) |
| `scripts/automation/tests/__init__.py` | New (empty — makes it a package for pytest) |
| `scripts/automation/tests/test_orchestrate.py` | New — full test suite |
| `.gitignore` | Add `automation/.orchestrator.lock` entry (AC-25 scope) |

### Files NOT touched

| File | Why |
|---|---|
| `.claude/skills/claude-autorun` | Already updated in TASK-PROC-041-01-04 |
| `automation/MONITORING_CRITERIA.md` | Already written in TASK-PROC-041-01-04 |
| `scripts/next_tasks.py` | External dependency — not changed |
| `scripts/is_awaiting_answer.py` | External dependency — not changed |

---

## 10. Execution Plan

This is a design document. The user must decide whether to:

**Path A**: Proceed with the rewrite within TASK-PROC-041-01-05 (current task).
- Extend `goal.md` scope note with a comment that implementation approach changed to rewrite.
- Implementation engineer reads this document and `goal.md`, implements rewrite + tests.
- Verify all ACs from `goal.md` pass in the new test suite.

**Path B**: Close TASK-PROC-041-01-05 with patch-only changes, create a new task for the rewrite.
- Create new task under `feat_session_orchestrator/tasks/` with this document as its plan.
- Implementation of AC-18–AC-26 happens in both tasks (once as patches, once in rewrite).

### If Path A is chosen — single agent, two phases

**Phase 1: Implementation agent**
1. Read this document and `goal.md` in full.
2. Read existing `orchestrate.py` carefully — note all subtle behaviours for characterisation.
3. Write characterisation tests for current behaviour (run against current file, all must pass).
4. Implement rewrite in `orchestrate.py` (Sections 1–7 as above).
5. Implement all AC-18–AC-26 within the rewrite.
6. Run `python3 -m pytest scripts/automation/tests/ -v` — all must pass.
7. Manual smoke test: `python3 scripts/automation/orchestrate.py --help` exits 0.
8. Verify log messages exactly match MONITORING_CRITERIA.md patterns.
9. Update `.gitignore`.

**Phase 2: Quality check** (via `verify-quality` skill)
- Check all AC-18–AC-26 acceptance criteria against implementation.
- Verify WHY comments present for: `OrchestratorDeps` design, `_jaccard` function,
  `next_available_account` fix (AC-19 edge case), `fcntl` lock.
- Run test coverage report: `python3 -m pytest scripts/automation/tests/ --cov=scripts/automation/orchestrate --cov-report=term`.

---

## 11. WHY Comment Requirements

The following non-obvious decisions in the rewrite require WHY comments:

| Location | WHY comment needed |
|---|---|
| `OrchestratorDeps` class | Why a dataclass of callables vs. ABC or global patch |
| `PersistentState` / `RunData` split | Why two state objects vs. one unified dict |
| `_jaccard` function | Threshold 0.60 choice, why Jaccard over edit distance |
| `next_available_account` sentinel `(None, None)` | AC-19 fix rationale |
| `fcntl.flock` block | Why non-blocking mode, why not `lockfile` library |
| `write_report` returning path | Why it returns path (fixes the filename-collision bug) |
| Characterisation tests section header | Why these tests run against the old code first |

---

*Design document complete. No code was written. Review and approve before implementation begins.*
