# Plan: Orchestrator Monitoring Improvements (AC-17–AC-26)

**Task**: TASK-PROC-041-01-05
**Date**: 2026-04-10
**File under change**: `scripts/automation/orchestrate.py` + `.gitignore`

---

## 1. Current State Analysis

Key functions in `orchestrate.py` relevant to each AC, with line numbers:

| Function | Lines | Relevance |
|---|---|---|
| `answer_is_empty()` | 241–243 | AC-20: needs whitespace check |
| `get_unanswered_questions()` | 245–261 | AC-26: called in unanswered guard — add fingerprint check here |
| `next_available_account()` | 534–575 | AC-19: `min()` on empty sequence crashes on line 572–574 |
| `find_resumable_session()` | 362–424 | AC-22: scan for no-session_id tasks before calling this |
| `write_report()` | 589–669 | Report additions for AC-21, AC-22, AC-26 |
| `write_health_summary()` | 672–756 | Report additions (alternative hook point — see §4) |
| `main()` — top section | 843–889 | AC-25 lock + AC-23 git commit on start |
| `main()` — feedback resume path | 908–952 | AC-21: increment resume count |
| `main()` — unanswered question guard | 960–964 | AC-26: fingerprint check |
| `main()` — in-progress resume section | 972–1095 | AC-21: increment resume count; AC-22: skip/log no-session_id |
| `main()` — normal session pre-flight | 1099–1126 | AC-18: empty output → `queue_empty` |
| `main()` — `finally` block | 1218–1237 | AC-24: git commit on stop; AC-25: lock release |
| `run_data` init dict | 880–885 | Add `resume_attempt_counts`, `skipped_no_session_id`, `exhausted_resume_tasks`, `repeated_questions` |

---

## 2. Change Map (per AC)

### AC-18: Empty queue → stop with `queue_empty`

**Where**: `main()`, normal-session pre-flight, after `next_result = subprocess.run(...)` (line ~1103)

**Current logic**: checks `if task_ids_in_output and not runnable:` (all-blocked case).

**New logic**: add a check *before* that, immediately after `task_ids_in_output` is computed:
```python
if not task_ids_in_output:
    stop_reason = "queue_empty"
    print("[orchestrator] No tasks in queue — stopping")
    break
```
Insert at approximately line 1111 (between `task_ids_in_output = re.findall(...)` and `runnable = [...]`).

**Log messages (verbatim from MONITORING_CRITERIA.md S11)**:
```
[orchestrator] No tasks in queue — stopping
[orchestrator] Stopped. Reason: queue_empty
```
The second message is produced by the existing `finally` block's `print(f"[orchestrator] Stopped. Reason: {stop_reason}")`.

**Dependencies**: none.

---

### AC-19: All accounts permanently disabled → graceful stop

**Where**: `next_available_account()` function, lines 571–575.

**Problem**: when all accounts are in `disabled_accounts` (not rate-limited, just disabled), the `for` loop skips all of them and falls through to `min(...)` on an **empty** `rate_limited.values()` — `ValueError`.

**Fix**: detect this state before calling `min()`:
```python
# All accounts exhausted — find earliest reset time
remaining_rate_limited = {
    k: v for k, v in rate_limited.items()
    if not (disabled_accounts and k in disabled_accounts)
}
if not remaining_rate_limited:
    # All accounts are permanently disabled — nothing to wait for
    return None, None
earliest = min(datetime.fromisoformat(t) for t in remaining_rate_limited.values())
return accounts[state["account_index"] % len(accounts)], earliest
```

**Handle in `main()`**: In the normal session section (line ~1129), after calling `next_available_account()`:
```python
if account is None:
    stop_reason = "all_accounts_disabled"
    print("[orchestrator] All accounts are permanently disabled — stopping")
    break
```
Also add the same sentinel check in the resume account fallback path (line ~998).

**Log messages**: `[orchestrator] All accounts are permanently disabled — stopping`

**Dependencies**: none (self-contained).

---

### AC-20: Whitespace-only `answer.md` treated as empty

**Where**: `answer_is_empty()` function, lines 241–243.

**New implementation**:
```python
def answer_is_empty(answer_path: str) -> bool:
    """Return True if answer.md does not exist, is zero-byte, or contains only whitespace."""
    if not os.path.exists(answer_path):
        return True
    if os.path.getsize(answer_path) == 0:
        return True
    try:
        with open(answer_path) as f:
            content = f.read()
        if content.strip() == "":
            # Log happens in caller context — can't log task_id from here.
            # Log in get_unanswered_questions() instead (see below).
            return True
    except OSError:
        pass
    return False
```

**Log message (verbatim from MONITORING_CRITERIA.md S20)**:
```
[orchestrator] WARNING: answer.md for <task_id> contains only whitespace — treating as unanswered
```

The log must include `task_id`. Since `answer_is_empty()` has no task_id, add the logging call in `get_unanswered_questions()` where `task_dir.name` (= task_id) is available. Specifically, after the `answer_is_empty(answer_path)` check returns True, check whether the file exists and is non-empty (i.e. the whitespace case) and log there.

**Alternative (simpler)**: add a separate helper `_is_whitespace_only(path)` called only where task_id is in scope. But the simplest approach: in `get_unanswered_questions()`, after `if os.path.exists(question_path) and answer_is_empty(answer_path):`, check:
```python
if os.path.exists(answer_path) and os.path.getsize(answer_path) > 0:
    print(f"[orchestrator] WARNING: answer.md for {task_dir.name} contains only whitespace — treating as unanswered")
```

**Dependencies**: none.

---

### AC-21: Max 3 resume attempts per session_id

**Where**: Two resume paths in `main()`.

**New fields in `run_data` init** (line ~880):
```python
run_data: dict = {
    ...
    "resume_attempt_counts": {},      # {session_id: int}
    "exhausted_resume_tasks": [],     # [{task_id, session_id}]
    ...
}
```

**In answered-feedback resume path** (line ~922, before `run_resume_session()`):
```python
session_id = item["session_id"]
attempt = run_data["resume_attempt_counts"].get(session_id, 0) + 1
run_data["resume_attempt_counts"][session_id] = attempt
if attempt > 3:
    print(f"[orchestrator] WARNING: resume of {item['task_id']} exhausted 3 attempts — giving up this run")
    run_data["exhausted_resume_tasks"].append({"task_id": item["task_id"], "session_id": session_id})
    run_data.setdefault("exhausted_resume_ids", set()).add(session_id)
    continue
```

**In in-progress resume path** (line ~1024, before `run_resume_session()`):
Same pattern using `resumable["session_id"]` and `resumable["task_id"]`.

**Log message (verbatim from MONITORING_CRITERIA.md S8)**:
```
[orchestrator] WARNING: resume of <task_id> exhausted 3 attempts — giving up this run
```

**Dependencies**: none (independent of AC-22).

---

### AC-22: In-progress task without session_id — skip and log

**Where**: `main()`, between the unanswered-question guard and the `find_resumable_session()` call (line ~971).

**New section**:
```python
# === Scan for in-progress tasks without session_id ===
in_progress_no_sid = _find_in_progress_without_session_id(PROJECT_ROOT)
for tid in in_progress_no_sid:
    if tid not in run_data.get("skipped_no_session_id", []):
        print(f"[orchestrator] WARNING: {tid} is in_progress but has no session_id — skipping (may have been started manually)")
        run_data.setdefault("skipped_no_session_id", []).append(tid)
```

**New helper function** (add before `main()`):
```python
def _find_in_progress_without_session_id(project_root: str) -> list:
    """Return task IDs that are in_progress but have no session_id in frontmatter."""
    req_dir = os.path.join(project_root, "requirements_tasks")
    result = subprocess.run(
        ["grep", "-rl", "^status: in_progress", req_dir],
        capture_output=True, text=True,
    )
    found = []
    for path in result.stdout.strip().splitlines():
        if not path.endswith("goal.md"):
            continue
        fm = read_yaml_frontmatter(path)
        if fm.get("status") != "in_progress":
            continue
        if not fm.get("session_id", "").strip():
            found.append(fm.get("task_id", path))
    return found
```

**New `run_data` field**: `"skipped_no_session_id": []` (list of task_id strings).

**Log message (verbatim from MONITORING_CRITERIA.md S7)**:
```
[orchestrator] WARNING: <task_id> is in_progress but has no session_id — skipping (may have been started manually)
```

**Dependencies**: Must run before `find_resumable_session()` (which already skips no-session_id tasks via the `if not session_id: continue` guard in that function, lines 403–404).

---

### AC-23: Git commit on start (answers)

**Where**: `main()`, after `cleanup_old_artifacts()` and before the `while True:` loop (approximately line ~893, after `run_data["initial_in_progress"]` is set).

**New helper function** (add to helpers section, after `unlink_if_exists()`):
```python
def git_commit_best_effort(files: list, message: str) -> None:
    """Stage and commit files. Non-fatal — logs WARNING on failure.
    
    files: list of glob patterns or exact paths (resolved relative to PROJECT_ROOT).
    """
    import glob as glob_mod
    expanded = []
    for pattern in files:
        expanded.extend(glob_mod.glob(os.path.join(PROJECT_ROOT, pattern)))
    if not expanded:
        return
    try:
        subprocess.run(["git", "add"] + expanded, cwd=PROJECT_ROOT, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_ROOT, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"[orchestrator] WARNING: git commit failed ({e})")
```

**Call on start** (after `run_data["initial_in_progress"] = ...`):
```python
now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
git_commit_best_effort(
    ["automation/pending_feedback/*/answer.md"],
    f"chore(automation): record user answers {now_str}",
)
```

Note: `glob.glob()` resolves the wildcard — if no answer.md files exist, the list is empty and the function returns early without running git.

**Dependencies**: requires `import glob` — add to stdlib imports at top of file.

---

### AC-24: Git commit on stop (report + questions)

**Where**: `main()` `finally` block, after `write_health_summary()` call (line ~1232), before `unlink_if_exists()` calls.

**Call**:
```python
stop_str = stop_time.strftime("%Y-%m-%d %H:%M")
git_commit_best_effort(
    [report_path, "automation/pending_feedback/*/question.md"],
    f"chore(automation): session report {stop_str} [{stop_reason}]",
)
```

Note: `report_path` is a full absolute path — pass it directly in the list alongside the glob pattern. The helper must handle mixed absolute paths and glob patterns.

**Refinement to `git_commit_best_effort()`**: do not call `os.path.join(PROJECT_ROOT, pattern)` if `pattern` is already absolute:
```python
for pattern in files:
    if os.path.isabs(pattern):
        expanded.extend(glob_mod.glob(pattern))
    else:
        expanded.extend(glob_mod.glob(os.path.join(PROJECT_ROOT, pattern)))
```

**Dependencies**: AC-23 (same helper function). Implement AC-23 first.

---

### AC-25: Lock file using `fcntl.flock`

**Where**: `main()`, at the very top, before `parse_args()` call equivalent — specifically as the first statements after the `args = parse_args()` / `accounts = ...` lines, but before writing `.automated_mode` sentinel.

**Exact location**: Insert after line 855 (`setup_signals(stop_flag)`) and before line 857 (`state = load_state(STATE_PATH)`).

Actually, per goal.md spec: "before writing `.automated_mode`". The sentinel is written at line 868. So insert lock acquisition between line 855 and 857 (after signal setup, before state load).

**New imports at top of file**: add `import fcntl` and `import glob` (for AC-23) to the stdlib imports block (line 17–26).

**Lock acquisition**:
```python
lock_path = os.path.join(AUTOMATION_DIR, ".orchestrator.lock")
os.makedirs(AUTOMATION_DIR, exist_ok=True)
lock_fd = open(lock_path, "w")
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print(f"[orchestrator] ERROR: orchestrator already running (PID {lock_fd.read() or '?'}) — aborting")
    lock_fd.close()
    sys.exit(1)
```

**Note**: The lock file won't contain the PID at acquisition time. Simplify the error message to match MONITORING_CRITERIA.md S16 exactly — the criteria show:
```
[orchestrator] ERROR: orchestrator already running (PID <N>) — aborting
```
Write the current PID into the lock file after acquiring it, so the blocking instance reads a stale PID (or use a simpler message). Best approach: write PID after `flock` succeeds, but the error message for the blocking instance won't have the running PID easily. Keep it simple and match the criteria's spirit:
```
[orchestrator] ERROR: orchestrator already running — aborting
```
(The criteria description says pattern is `[orchestrator] ERROR: orchestrator already running (PID <N>) — aborting` but that PID is the running instance's PID which requires reading the file. Write PID on acquire and read on BlockingIOError.)

**Full implementation**:
```python
lock_path = os.path.join(AUTOMATION_DIR, ".orchestrator.lock")
os.makedirs(AUTOMATION_DIR, exist_ok=True)
lock_fd = open(lock_path, "w")
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    lock_fd.write(str(os.getpid()))
    lock_fd.flush()
except BlockingIOError:
    try:
        with open(lock_path) as f:
            running_pid = f.read().strip()
    except OSError:
        running_pid = "?"
    print(f"[orchestrator] ERROR: orchestrator already running (PID {running_pid}) — aborting")
    lock_fd.close()
    sys.exit(1)
```

**Release in `finally` block** (after all other finally work, as the last action):
```python
try:
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    lock_fd.close()
except OSError:
    pass
```

**Dependencies**: `fcntl` import. `lock_fd` must be declared before the `try:` block in `main()` so it's accessible in `finally`.

---

### AC-26: Same-question detection (Jaccard similarity)

**New functions** (add after `answer_is_empty()`, before `get_unanswered_questions()`):

```python
def compute_question_fingerprint(text: str) -> dict:
    """Normalize text and return word set + preview for Jaccard comparison."""
    normalized = re.sub(r'[^\w\s]', '', text.lower())
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    words = set(normalized.split())
    return {"words": list(words), "preview": normalized[:300]}


def check_and_update_question_fingerprint(
    task_id: str, question_body: str, state: dict, run_data: dict
) -> None:
    """Compare new question fingerprint with stored one; log if Jaccard >= 0.60."""
    new_fp = compute_question_fingerprint(question_body)
    new_words = set(new_fp["words"])
    
    fingerprints = state.setdefault("question_fingerprints", {})
    existing = fingerprints.get(task_id)
    
    if existing:
        old_words = set(existing.get("words", []))
        if old_words or new_words:
            intersection = len(old_words & new_words)
            union = len(old_words | new_words)
            similarity = intersection / union if union > 0 else 0.0
            if similarity >= 0.60:
                print(f"[orchestrator] WARNING: {task_id} appears to be asking the same question again "
                      f"(similarity {similarity:.2f}) — possible loop")
                run_data.setdefault("repeated_questions", []).append({
                    "task_id": task_id,
                    "similarity": round(similarity, 2),
                })
    
    # Update fingerprint (words stored as list for JSON serialization)
    fingerprints[task_id] = {"words": list(new_words), "preview": new_fp["preview"]}
```

**Call site**: in `main()`, in the unanswered-question guard section (line ~960–964), after logging the unanswered tasks. For each unanswered task, read its `question.md` body and call the fingerprint check:

```python
unanswered = get_unanswered_questions(FEEDBACK_DIR)
if unanswered:
    task_ids = [q["task_id"] for q in unanswered]
    print(f"[orchestrator] Note: unanswered questions for {', '.join(task_ids)} — "
          f"these tasks are skipped; other tasks will continue.")
    # AC-26: check for repeated questions
    for q in unanswered:
        q_path = os.path.join(FEEDBACK_DIR, q["task_id"], "question.md")
        try:
            with open(q_path) as f:
                raw = f.read()
            parts = raw.split("---", 2)
            body = parts[2].strip() if len(parts) >= 3 else raw.strip()
            check_and_update_question_fingerprint(q["task_id"], body, state, run_data)
        except OSError:
            pass
```

**State persistence**: `state["question_fingerprints"]` is written by `save_state()` at end of each iteration and in `finally` — no extra action needed. Must add `"question_fingerprints": {}` to `load_state()` defaults dict (line 131–136).

**Log message (verbatim from MONITORING_CRITERIA.md S9)**:
```
[orchestrator] WARNING: <task_id> appears to be asking the same question again (similarity 0.XX) — possible loop
```

**Dependencies**: none for the functions; call site depends on unanswered guard (already exists).

---

### Report Additions (AC-21, AC-22, AC-26)

**Where**: `write_health_summary()` is the best hook — it already appends sections to the report. Add three new sections before the "### Overall Health" verdict.

**New sections to add in `write_health_summary()`** (pass `run_data` which already contains all three new lists):

```python
# --- Skipped (no session_id) ---
skipped_no_sid = run_data.get("skipped_no_session_id", [])
if skipped_no_sid:
    lines.append("### Skipped Tasks (no session_id)")
    lines.append("")
    for tid in skipped_no_sid:
        lines.append(f"- {tid}: in_progress but no session_id — skipped")
    lines.append("")

# --- Exhausted Resumes ---
exhausted = run_data.get("exhausted_resume_tasks", [])
if exhausted:
    lines.append("### Exhausted Resumes")
    lines.append("")
    for entry in exhausted:
        lines.append(f"- {entry['task_id']}: resume exhausted 3 attempts (session {entry['session_id']})")
    lines.append("")

# --- Repeated Questions ---
repeated = run_data.get("repeated_questions", [])
if repeated:
    lines.append("### Repeated Questions")
    lines.append("")
    for entry in repeated:
        lines.append(f"- {entry['task_id']}: similarity {entry['similarity']} — possible loop")
    lines.append("")
```

---

### `.gitignore` Update

**Current state** (from reading `.gitignore` lines 54–65):
```
automation/pending_feedback/*/question.md
automation/pending_feedback/*/answer.md
automation/reports/
automation/session_outputs/
automation/answered_feedback/*/
automation/orchestrate.log
automation/state.json
automation/.automated_mode
automation/.stop-requested
automation/.last_monitor_check
```

**Required final state** (per goal.md):

Ignored (must be present):
- `automation/session_outputs/` ✅ already present
- `automation/state.json` ✅ already present
- `automation/orchestrate.log` ✅ already present
- `automation/.automated_mode` ✅ already present
- `automation/.stop-requested` ✅ already present
- `automation/.orchestrator.lock` ❌ MISSING — add this

Not ignored (must NOT be ignored):
- `automation/reports/` ❌ currently ignored as `automation/reports/` — REMOVE this line
- `automation/pending_feedback/` ❌ `automation/pending_feedback/*/question.md` and `automation/pending_feedback/*/answer.md` are ignored — REMOVE both lines

**Changes**:
1. Remove line: `automation/pending_feedback/*/question.md`
2. Remove line: `automation/pending_feedback/*/answer.md`
3. Remove line: `automation/reports/`
4. Add line: `automation/.orchestrator.lock`

**Note**: `automation/answered_feedback/*/` and `automation/.last_monitor_check` have no explicit requirement — leave as-is (they are volatile runtime artifacts).

---

## 3. New Functions to Add

| Function | Signature | Purpose |
|---|---|---|
| `git_commit_best_effort` | `(files: list[str], message: str) -> None` | Git add + commit, non-fatal |
| `_find_in_progress_without_session_id` | `(project_root: str) -> list[str]` | Find in_progress tasks missing session_id |
| `compute_question_fingerprint` | `(text: str) -> dict` | Normalize and word-set a question body |
| `check_and_update_question_fingerprint` | `(task_id: str, question_body: str, state: dict, run_data: dict) -> None` | Jaccard compare + state update |

---

## 4. Exact Log Message Strings (verbatim from MONITORING_CRITERIA.md)

These strings must match exactly (the monitoring LLM scans for them by pattern):

| AC | Log message |
|---|---|
| AC-18 | `[orchestrator] No tasks in queue — stopping` |
| AC-19 | `[orchestrator] All accounts are permanently disabled — stopping` |
| AC-20 | `[orchestrator] WARNING: answer.md for <task_id> contains only whitespace — treating as unanswered` |
| AC-21 | `[orchestrator] WARNING: resume of <task_id> exhausted 3 attempts — giving up this run` |
| AC-22 | `[orchestrator] WARNING: <task_id> is in_progress but has no session_id — skipping (may have been started manually)` |
| AC-25 | `[orchestrator] ERROR: orchestrator already running (PID <N>) — aborting` |
| AC-26 | `[orchestrator] WARNING: <task_id> appears to be asking the same question again (similarity 0.XX) — possible loop` |

Note: AC-18 also produces `[orchestrator] Stopped. Reason: queue_empty` via the existing `finally` block.

---

## 5. Implementation Order

The following ordering minimizes risk and respects dependencies:

1. **AC-25** (lock file) — first, to protect all subsequent testing; self-contained; requires only new imports
2. **AC-19** (accounts disabled fix) — crash fix; entirely in `next_available_account()` plus 2 call sites; no dependencies
3. **AC-20** (whitespace answer.md) — simple fix; entirely in `answer_is_empty()` + `get_unanswered_questions()`; no dependencies
4. **AC-18** (empty queue stop) — one insertion in main loop; no dependencies
5. **AC-22** (no-session_id skip) — new helper + `run_data` field + main loop section; no dependencies on other new ACs
6. **AC-21** (resume attempt limit) — two insertion points in main loop; uses `run_data["exhausted_resume_ids"]` (already exists); no dependencies on other new ACs
7. **AC-23** (git commit on start) — new helper `git_commit_best_effort()` + call; requires `import glob`
8. **AC-24** (git commit on stop) — one call in `finally`; depends on AC-23 (same helper)
9. **AC-26** (same-question Jaccard) — two new functions + call site + state field; most complex, do last
10. **Report additions** — add to `write_health_summary()` after all `run_data` fields are finalized
11. **`.gitignore` update** — independent; do alongside or after code changes

---

## 6. Test Strategy

### Existing tests
No Python test files exist in `scripts/`. `python3 -m pytest scripts/` will find nothing. No existing tests to run.

### New tests needed
The goal.md acceptance criteria states: "All existing tests pass (run `python3 -m pytest scripts/` if tests exist)". Since none exist, no test run is required, but manual smoke tests should be documented:

**Smoke-test checklist for implementer**:

1. **AC-18**: Run with empty `requirements_tasks/` (or mock `next_tasks.py` to return empty output) → confirm `stop_reason = "queue_empty"` in log and report.

2. **AC-19**: Set all accounts in `disabled_accounts` in `run_data` → confirm `next_available_account()` returns `(None, None)` without raising `ValueError`.

3. **AC-20**: Create `automation/pending_feedback/TASK-X/answer.md` with content `"   \n  "` → confirm log prints whitespace warning and task is treated as unanswered.

4. **AC-21**: Mock `run_resume_session()` to always return non-zero → confirm after 3 calls the task is added to `exhausted_resume_tasks` and the 4th call is skipped.

5. **AC-22**: Create a goal.md with `status: in_progress` but no `session_id:` field → confirm WARNING log with task_id appears each loop iteration (deduplicated by checking if already in `skipped_no_session_id`).

6. **AC-23/24**: Run orchestrator normally → confirm two git commits appear: one at start with answer files, one at stop with report + question files.

7. **AC-25**: Start orchestrator, then try to start a second instance in another terminal → second instance should print ERROR and exit immediately.

8. **AC-26**: Place the same question text (or very similar) in `pending_feedback/TASK-X/question.md` across two loop iterations (state persisted) → confirm WARNING log with similarity ≥ 0.60.

### Unit-testable functions (if tests are added later)
- `compute_question_fingerprint()`: pure function, easy to unit test
- `next_available_account()` with all-disabled scenario: deterministic
- `answer_is_empty()` with whitespace file: deterministic

---

## 7. Risk Notes

### R1: `lock_fd` variable scope in `finally`
`lock_fd` is assigned inside `main()` before the `try:` block. The `finally` block references it. If the lock acquisition raises `BlockingIOError` and `sys.exit(1)` is called, the `finally` block of the outer `try` (the main loop try) is NOT entered — `sys.exit()` unwinds correctly. But `lock_fd` must be declared before the `try:` block in `main()` (it is, since the lock code runs before `try:`). Safe.

### R2: `glob` module name collision
`orchestrate.py` uses a local variable named `uuid` (line 299: `uuid = entry.name.removesuffix(".txt")`). Adding `import glob` at the top is safe — no naming collision with existing code. The module-level `import uuid` already exists; the local variable `uuid` in `cleanup_old_artifacts()` shadows the module temporarily, which is a pre-existing issue not introduced by this task.

### R3: `state["question_fingerprints"]` and JSON serialization
Word sets must be stored as lists in `state.json`. `compute_question_fingerprint()` already returns `{"words": list(words), ...}`. `check_and_update_question_fingerprint()` must convert `existing.get("words", [])` to `set()` when loading — this is handled in the implementation above.

### R4: `.gitignore` change affects git commit behavior (AC-23/24)
Removing `automation/reports/` and `automation/pending_feedback/*/question.md` from `.gitignore` means these files become trackable. The AC-24 commit will include the report. The AC-23 commit will include answer files (currently ignored — after the change they're trackable). This is intentional per the AC requirements.

### R5: `git commit` in `finally` block (AC-24)
If the orchestrator exits via SIGKILL, the `finally` block does not run, so the report is never committed. This is acceptable — it matches the existing behavior for sentinel cleanup.

### R6: Empty `git add` list (AC-23 start commit)
If no `answer.md` files exist at start, `glob.glob()` returns an empty list, `git_commit_best_effort()` returns early. Safe.

### R7: AC-22 deduplication across loop iterations
The no-session_id scan runs every loop iteration. Without deduplication, the same task would be logged every loop. Deduplication: check `if tid not in run_data["skipped_no_session_id"]:` before logging and appending. The implementation above handles this correctly.

### R8: `next_available_account()` with `disabled_accounts=None`
The function signature is `disabled_accounts: set = None`. When filtering `remaining_rate_limited` for the all-disabled crash fix, must guard against `disabled_accounts` being `None`:
```python
remaining_rate_limited = {
    k: v for k, v in rate_limited.items()
    if not (disabled_accounts and k in disabled_accounts)
}
```
The `disabled_accounts and` short-circuit handles `None` correctly.

---

## 8. Summary of All `run_data` Field Additions

```python
run_data: dict = {
    "start_time": start_time,
    "sessions": [],
    "accounts_used": set(),
    "exhausted_resume_ids": set(),
    # New fields:
    "resume_attempt_counts": {},      # AC-21: {session_id: int}
    "exhausted_resume_tasks": [],     # AC-21: [{task_id, session_id}]
    "skipped_no_session_id": [],      # AC-22: [task_id]
    "repeated_questions": [],         # AC-26: [{task_id, similarity}]
}
```

## 9. Summary of `load_state()` Defaults Addition

Add `"question_fingerprints": {}` to the `defaults` dict in `load_state()` (for AC-26 state persistence).
