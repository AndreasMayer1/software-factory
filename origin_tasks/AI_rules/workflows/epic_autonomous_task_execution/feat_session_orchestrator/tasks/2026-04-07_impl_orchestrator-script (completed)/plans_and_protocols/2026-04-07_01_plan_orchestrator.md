# Plan: Implement Session Orchestrator Script

**Task**: TASK-PROC-041-01-01
**Date**: 2026-04-07
**File to create**: `scripts/automation/orchestrate.py`
**Target size**: ~300-350 lines (single file, stdlib only, Python 3.9+)

---

## 1. Scope of Work

**Single file**: `scripts/automation/orchestrate.py`

**Directories created at runtime** (script creates them if missing):
- `automation/session_outputs/`
- `automation/reports/`

**State file** (created at runtime, not committed): `automation/state.json`

**Sentinel files** (created/deleted at runtime, not committed):
- `automation/.automated_mode` — created on start, deleted in `finally`
- `automation/.stop-requested` — detected (not created), deleted in `finally`

---

## 2. Module Structure

The script is a single file with no classes. All state is in a plain dict loaded from / saved to `state.json`. This keeps it readable and easy for the implementation engineer to follow.

### Top-level functions (in call order)

```
parse_args()                → argparse.Namespace
load_state(path) → dict      # reads state.json if exists; merges defaults
save_state(path, state)      # atomic write via tmp + rename
find_answered_feedback(root) → list[dict]
    # scans automation/pending_feedback/*/
    # returns list of {task_id, session_id, account, answer_content, folder_path}
    # only includes dirs with BOTH question.md AND answer.md
read_yaml_frontmatter(path) → dict
    # extracts YAML block between --- delimiters (no external library)
    # returns dict of frontmatter fields
find_active_task_goal(root) → str | None
    # grep -rl "status: in_progress" requirements_tasks/
    # returns first matching goal.md path
update_goal_session_fields(goal_path, session_id, account)
    # reads goal.md, rewrites session_id and session_account in frontmatter
    # uses line-by-line rewrite to avoid YAML library dependency
parse_rate_limit_reset(stdout) → datetime | None
    # regex: r'resets (\d{1,2}:\d{2}(?:am|pm)) \(([^)]+)\)'
    # returns UTC-aware datetime of reset + 5 min buffer, or None if not found
strip_hook_footer(text) → str
    # re.sub(r'\n---\n\*\*Reminder:.*', '', text, flags=re.DOTALL)
write_session_output(outputs_dir, session_uuid, cleaned_stdout)
    # writes automation/session_outputs/<uuid>.txt
should_stop(args, state, stop_flag) → bool
    # checks: stop_flag set | .stop-requested exists | stop_at reached
write_report(reports_dir, run_data)
    # generates automation/reports/YYYY-MM-DD_HH-MM_report.md
    # run_data: {start_time, stop_time, stop_reason, accounts_used, sessions[]}
    # sessions[]: {index, task_id, account, start, end, exit_code, output_excerpt}
    # also appends pending_feedback listing at end
run_resume_session(env_base, session_id, account, answer_content, ccs_root)
    # builds env with CLAUDE_CONFIG_DIR for the given account
    # subprocess.run(["claude", "--dangerously-skip-permissions", "--resume",
    #                 session_id, "-p", answer_content], ...)
    # returns subprocess.CompletedProcess
run_normal_session(env_base, session_uuid, ccs_root, account)
    # builds env with CLAUDE_CONFIG_DIR for the given account
    # subprocess.run(["claude", "--dangerously-skip-permissions",
    #                 "--session-id", session_uuid, "-p", "Do next task"], ...)
    # returns subprocess.CompletedProcess
main()
    # orchestration loop — see section 4
```

---

## 3. State Management

### `automation/state.json` schema

```json
{
  "account_index": 0,
  "run_count": 0,
  "start_time": "2026-04-07T09:00:00Z",
  "paused_tasks": []
}
```

**Fields**:
- `account_index` (int): Next account to use in round-robin. Persisted so restart picks up where it left off.
- `run_count` (int): Total sessions launched (for report).
- `start_time` (ISO 8601 UTC string): When this orchestrator invocation started. Reset on fresh start only if no valid state exists.
- `paused_tasks` (list[str]): Task IDs currently in `pending_feedback/` without an answer yet. Updated after each feedback scan.

**Load strategy**: If `state.json` exists and is valid JSON, load it and fill any missing keys with defaults. If file is missing or corrupt, start fresh.

**Save strategy**: After every state mutation. Use atomic write: write to `state.json.tmp`, then `os.replace(tmp, state.json)` to avoid partial writes on crash.

---

## 4. Main Loop Design

```
main():
    parse args
    set up SIGTERM + SIGINT handlers → set stop_flag = True
    load state from automation/state.json
    create automation/session_outputs/ and automation/reports/ if missing
    create automation/.automated_mode sentinel
    record start_time in state (only if not already set, for restart case)
    save state

    run_data = {start_time, sessions: [], accounts_used: set()}
    stop_reason = "manual"

    try:
        loop:
            # === Pre-session stop check ===
            if should_stop(args, state, stop_flag):
                stop_reason = determine_stop_reason(...)
                break

            # === Feedback resume check (highest priority) ===
            answered = find_answered_feedback("automation/pending_feedback")
            if answered:
                item = answered[0]  # process one at a time
                account = item["account"]
                env = build_env(account, ccs_root)
                
                session_record = {start: now(), account, task_id: item["task_id"], is_resume: True}
                result = run_resume_session(env, item["session_id"], account, item["answer_content"], ccs_root)
                session_record["end"] = now()
                session_record["exit_code"] = result.returncode
                
                cleaned = strip_hook_footer(result.stdout)
                write_session_output(outputs_dir, item["session_id"], cleaned)
                session_record["output_excerpt"] = cleaned[:500]
                run_data["sessions"].append(session_record)
                run_data["accounts_used"].add(account)
                
                # Handle outcome
                if result.returncode == 0 and not new_question_written_for(item["task_id"]):
                    # Move to answered_feedback/
                    shutil.move(item["folder_path"], "automation/answered_feedback/" + item["task_id"])
                # else: leave in pending_feedback (new question or failure)
                
                state["run_count"] += 1
                save_state(...)
                
                if args.min_wait_seconds > 0:
                    time.sleep(args.min_wait_seconds)
                continue

            # === Normal session ===
            session_uuid = str(uuid.uuid4())
            account = accounts[state["account_index"] % len(accounts)]
            
            # AC-07: write to active task goal.md
            goal_path = find_active_task_goal(project_root)
            if goal_path:
                update_goal_session_fields(goal_path, session_uuid, account)
            
            env = build_env(account, ccs_root)
            
            session_record = {start: now(), account, session_uuid, task_id: "unknown", is_resume: False}
            result = run_normal_session(env, session_uuid, ccs_root, account)
            session_record["end"] = now()
            session_record["exit_code"] = result.returncode
            
            cleaned = strip_hook_footer(result.stdout)
            write_session_output(outputs_dir, session_uuid, cleaned)
            session_record["output_excerpt"] = cleaned[:500]
            run_data["sessions"].append(session_record)
            run_data["accounts_used"].add(account)
            
            # Rate limit detection
            if result.returncode != 0 and "hit your limit" in result.stdout:
                reset_dt = parse_rate_limit_reset(result.stdout)
                session_record["rate_limited"] = True
                session_record["reset_at"] = reset_dt.isoformat() if reset_dt else None
                
                # Rotate to next account — do NOT advance index yet
                # (exhausted account stays at current index, next iteration tries the next)
                next_index = (state["account_index"] + 1) % len(accounts)
                state["account_index"] = next_index
                save_state(...)
                
                # Check if all accounts are exhausted
                # (tracked via rate_limited_until dict in state)
                # Update exhausted map: state["rate_limited_until"][account] = reset_dt
                handle_all_accounts_exhausted_case(state, accounts, reset_dt)
                
                continue  # no min_wait_seconds sleep — already waited or will wait above

            # Success — advance account index
            state["account_index"] = (state["account_index"] + 1) % len(accounts)
            state["run_count"] += 1
            save_state(...)

            if args.min_wait_seconds > 0:
                time.sleep(args.min_wait_seconds)

    except KeyboardInterrupt:
        stop_reason = "manual"
    finally:
        stop_time = now()
        run_data["stop_time"] = stop_time
        run_data["stop_reason"] = stop_reason
        write_report(reports_dir, run_data, accounts, "automation/pending_feedback")
        # Clean up sentinels
        unlink_if_exists("automation/.automated_mode")
        unlink_if_exists("automation/.stop-requested")
        save_state(state_path, state)
```

---

## 5. Rate Limit Wait Logic

### Single account rate-limited

When one account hits the rate limit:
1. Parse reset time from stdout with `parse_rate_limit_reset()`
2. Record `state["rate_limited_until"][account] = reset_iso_str` (add this field to state schema)
3. Advance `account_index` to next account
4. Save state
5. Continue loop immediately (next iteration picks next account)

### All accounts exhausted simultaneously

Before launching a new session, check if the next account is also rate-limited:

```python
def next_available_account(accounts, state) -> tuple[str, datetime | None]:
    """
    Returns (account_name, wait_until) where wait_until is None if the account
    is available now, or a datetime if all accounts are exhausted and the script
    must wait until that time.
    """
    now_utc = datetime.now(timezone.utc)
    rate_limited = state.get("rate_limited_until", {})
    
    # Try each account starting from current index
    for i in range(len(accounts)):
        idx = (state["account_index"] + i) % len(accounts)
        acct = accounts[idx]
        if acct not in rate_limited:
            return acct, None
        reset_str = rate_limited[acct]
        reset_dt = datetime.fromisoformat(reset_str)
        if now_utc >= reset_dt:
            # Reset window cleared — remove from exhausted map
            del state["rate_limited_until"][acct]
            state["account_index"] = idx
            return acct, None
    
    # All accounts exhausted — find earliest reset
    earliest = min(
        datetime.fromisoformat(t) for t in rate_limited.values()
    )
    return accounts[state["account_index"] % len(accounts)], earliest
```

When `wait_until` is not None:
```python
wait_secs = (wait_until - datetime.now(timezone.utc)).total_seconds()
if wait_secs > 0:
    print(f"All accounts rate-limited. Waiting {wait_secs:.0f}s until {wait_until}")
    time.sleep(wait_secs)
```

---

## 6. Rate Limit Reset Time Parsing

```python
import re
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

RATE_LIMIT_PATTERN = re.compile(
    r'resets (\d{1,2}:\d{2}(?:am|pm)) \(([^)]+)\)',
    re.IGNORECASE
)

def parse_rate_limit_reset(stdout: str) -> datetime | None:
    match = RATE_LIMIT_PATTERN.search(stdout)
    if not match:
        return None
    
    time_str, tz_name = match.group(1), match.group(2)
    
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = timezone.utc
    
    # Parse the time component (no date — assume today, handle midnight rollover)
    now_local = datetime.now(tz)
    reset_time = datetime.strptime(time_str.upper(), "%I:%M%p").replace(
        year=now_local.year,
        month=now_local.month,
        day=now_local.day,
        tzinfo=tz
    )
    
    # If reset_time is already past (rare edge case), add 1 day
    if reset_time <= now_local:
        reset_time += timedelta(days=1)
    
    # Add 5 min buffer, convert to UTC
    return (reset_time + timedelta(minutes=5)).astimezone(timezone.utc)
```

**Edge case**: If `zoneinfo` can't find the timezone (e.g. non-IANA name), fall back to UTC. This is safe — it may wait slightly longer than needed, but won't crash.

---

## 7. Feedback Resume Logic

### Scanning for answered feedback

```python
def find_answered_feedback(feedback_dir: str) -> list[dict]:
    results = []
    if not os.path.isdir(feedback_dir):
        return results
    
    for task_dir in os.scandir(feedback_dir):
        if not task_dir.is_dir():
            continue
        question_path = os.path.join(task_dir.path, "question.md")
        answer_path = os.path.join(task_dir.path, "answer.md")
        
        if not (os.path.exists(question_path) and os.path.exists(answer_path)):
            continue
        
        frontmatter = read_yaml_frontmatter(question_path)
        if not frontmatter.get("session_id") or not frontmatter.get("account"):
            continue  # skip malformed entries
        
        with open(answer_path) as f:
            answer_content = f.read().strip()
        
        results.append({
            "task_id": frontmatter.get("task_id", task_dir.name),
            "session_id": frontmatter["session_id"],
            "account": frontmatter["account"],
            "answer_content": answer_content,
            "folder_path": task_dir.path,
        })
    
    return results
```

### Detecting new question.md after resume

After `run_resume_session()` returns, check if a new `question.md` appeared in the same task's folder:

```python
def new_question_written_for(task_id: str, feedback_dir: str) -> bool:
    task_dir = os.path.join(feedback_dir, task_id)
    question_path = os.path.join(task_dir, "question.md")
    answer_path = os.path.join(task_dir, "answer.md")
    # New question if question.md exists but answer.md does NOT
    return os.path.exists(question_path) and not os.path.exists(answer_path)
```

### Move to answered_feedback

```python
import shutil

src = item["folder_path"]  # e.g. automation/pending_feedback/TASK-PROC-041-01
dst = os.path.join("automation/answered_feedback", item["task_id"])
if os.path.exists(dst):
    shutil.rmtree(dst)  # overwrite if already exists
shutil.move(src, dst)
```

---

## 8. Active Task Goal.md Update (AC-07)

### Finding the active task

```python
import subprocess

def find_active_task_goal(project_root: str) -> str | None:
    result = subprocess.run(
        ["grep", "-rl", "status: in_progress", os.path.join(project_root, "requirements_tasks")],
        capture_output=True, text=True
    )
    paths = [p for p in result.stdout.strip().splitlines() if p.endswith("goal.md")]
    return paths[0] if paths else None
```

### Updating the frontmatter

Use line-by-line approach — no YAML library needed:

```python
def update_goal_session_fields(goal_path: str, session_id: str, account: str):
    with open(goal_path) as f:
        lines = f.readlines()
    
    new_lines = []
    in_frontmatter = False
    fm_ended = False
    fm_start = False
    session_id_written = False
    session_account_written = False
    
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_frontmatter = True
            new_lines.append(line)
            continue
        if in_frontmatter and not fm_ended and line.strip() == "---":
            # Inject fields before closing --- if not already present
            if not session_id_written:
                new_lines.append(f"session_id: {session_id}\n")
            if not session_account_written:
                new_lines.append(f"session_account: {account}\n")
            in_frontmatter = False
            fm_ended = True
            new_lines.append(line)
            continue
        if in_frontmatter:
            if line.startswith("session_id:"):
                new_lines.append(f"session_id: {session_id}\n")
                session_id_written = True
                continue
            if line.startswith("session_account:"):
                new_lines.append(f"session_account: {account}\n")
                session_account_written = True
                continue
        new_lines.append(line)
    
    with open(goal_path, "w") as f:
        f.writelines(new_lines)
```

---

## 9. YAML Frontmatter Parser

No external YAML library. Simple line-by-line extraction (sufficient for flat key: value frontmatter):

```python
def read_yaml_frontmatter(path: str) -> dict:
    result = {}
    with open(path) as f:
        lines = f.readlines()
    
    if not lines or lines[0].strip() != "---":
        return result
    
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    
    return result
```

**Limitation**: This only handles scalar values. That is sufficient — `question.md` frontmatter only has scalar fields (`task_id`, `session_id`, `account`, `status`, `asked_at`, `skill`).

---

## 10. Signal Handling

```python
import signal

stop_flag = {"requested": False}  # mutable container for lambda

def setup_signals():
    def handler(signum, frame):
        stop_flag["requested"] = True
        print(f"\n[orchestrator] Signal {signum} received — stopping after current session")
    
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)
```

Use a dict (not a module-level bool) to allow mutation from the lambda without `global`.

---

## 11. Stop Condition Check

```python
from datetime import datetime

def should_stop(args, stop_flag: dict, stop_at: datetime | None) -> tuple[bool, str]:
    """Returns (should_stop, reason)"""
    if stop_flag["requested"]:
        return True, "manual"
    if os.path.exists("automation/.stop-requested"):
        return True, "manual"
    if stop_at and datetime.now() >= stop_at:
        return True, "scheduled"
    return False, ""
```

`stop_at` is parsed from `args.stop_at` at startup:
```python
stop_at = None
if args.stop_at:
    stop_at = datetime.strptime(args.stop_at, "%Y-%m-%d %H:%M")
```

---

## 12. Report Generation

```python
def write_report(reports_dir: str, run_data: dict, accounts: list[str], feedback_dir: str):
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H-%M_report.md")
    path = os.path.join(reports_dir, filename)
    
    sessions = run_data["sessions"]
    completed = sum(1 for s in sessions if s["exit_code"] == 0)
    paused = sum(1 for s in sessions if s.get("rate_limited"))
    failed = len(sessions) - completed - paused
    
    lines = [
        f"# Automation Run Report — {run_data['start_time'].strftime('%Y-%m-%d %H:%M')}",
        "",
        f"**Started**: {run_data['start_time'].strftime('%Y-%m-%d %H:%M')}",
        f"**Stopped**: {run_data['stop_time'].strftime('%Y-%m-%d %H:%M')}",
        f"**Stop reason**: {run_data['stop_reason']}",
        f"**Accounts used**: {', '.join(sorted(run_data['accounts_used']))}",
        f"**Total sessions**: {len(sessions)} ({completed} completed, {paused} paused, {failed} failed)",
        "",
        "---",
    ]
    
    for i, s in enumerate(sessions, 1):
        task_label = s.get("task_id", "unknown")
        account = s.get("account", "?")
        start_str = s["start"].strftime("%H:%M") if s.get("start") else "?"
        end_str = s["end"].strftime("%H:%M") if s.get("end") else "?"
        exit_code = s.get("exit_code", "?")
        excerpt = s.get("output_excerpt", "")
        if len(excerpt) > 500:
            excerpt = excerpt[:500] + "\n[... truncated]"
        
        lines += [
            "",
            f"## Session {i} — {task_label} ({account})",
            f"**Started**: {start_str} | **Ended**: {end_str} | **Exit**: {exit_code}",
            excerpt,
            "",
            "---",
        ]
    
    # Pending feedback section
    pending = []
    if os.path.isdir(feedback_dir):
        for task_dir in os.scandir(feedback_dir):
            if not task_dir.is_dir():
                continue
            question_path = os.path.join(task_dir.path, "question.md")
            answer_path = os.path.join(task_dir.path, "answer.md")
            if os.path.exists(question_path) and not os.path.exists(answer_path):
                with open(question_path) as f:
                    content = f.read()
                # Extract question body (after frontmatter)
                parts = content.split("---", 2)
                body = parts[2].strip() if len(parts) >= 3 else content.strip()
                first_line = body.splitlines()[0] if body.splitlines() else "(no text)"
                fm = read_yaml_frontmatter(question_path)
                pending.append((fm.get("task_id", task_dir.name), first_line))
    
    if pending:
        lines += ["", "## Pending Feedback", ""]
        for task_id, question in pending:
            lines.append(f'- {task_id}: "{question}"')
    
    os.makedirs(reports_dir, exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    
    print(f"[orchestrator] Report written to {path}")
```

---

## 13. CLI Argument Parsing

```python
def parse_args():
    parser = argparse.ArgumentParser(
        description="Orchestrate sequential claude sessions with account rotation"
    )
    parser.add_argument(
        "--accounts",
        default="gmail,web,gmail2",
        help="Comma-separated list of CCS account names (default: gmail,web,gmail2)"
    )
    parser.add_argument(
        "--stop-at",
        metavar="YYYY-MM-DD HH:MM",
        default=None,
        help="Stop after current session once this datetime is reached (local time)"
    )
    parser.add_argument(
        "--min-wait-seconds",
        type=int,
        default=0,
        metavar="N",
        help="Minimum seconds to wait between sessions (default: 0)"
    )
    return parser.parse_args()
```

Accounts parsed as: `accounts = [a.strip() for a in args.accounts.split(",") if a.strip()]`

---

## 14. Environment / Path Conventions

All paths are resolved relative to the project root. The script detects the project root as the parent of the `scripts/` directory containing the script itself:

```python
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# scripts/automation/orchestrate.py → scripts/ → project_root
CCS_ROOT = "/home/vscode/.ccs/instances"
AUTOMATION_DIR = os.path.join(PROJECT_ROOT, "automation")
STATE_PATH = os.path.join(AUTOMATION_DIR, "state.json")
FEEDBACK_DIR = os.path.join(AUTOMATION_DIR, "pending_feedback")
ANSWERED_DIR = os.path.join(AUTOMATION_DIR, "answered_feedback")
OUTPUTS_DIR = os.path.join(AUTOMATION_DIR, "session_outputs")
REPORTS_DIR = os.path.join(AUTOMATION_DIR, "reports")
SENTINEL_AUTOMATED = os.path.join(AUTOMATION_DIR, ".automated_mode")
SENTINEL_STOP = os.path.join(AUTOMATION_DIR, ".stop-requested")
```

`build_env(account)`:
```python
def build_env(account: str) -> dict:
    return {
        **os.environ,
        "CLAUDE_AUTOMATED_MODE": "1",
        "CLAUDE_CONFIG_DIR": f"{CCS_ROOT}/{account}",
    }
```

---

## 15. Error Handling Strategy

| Situation | Handling |
|---|---|
| `state.json` corrupt / missing | Log warning, start fresh (don't crash) |
| `goal.md` not found (no in_progress task) | Log warning, skip frontmatter update, continue |
| `goal.md` update fails | Log warning, do NOT abort session — session UUID is still passed via `--session-id` |
| `parse_rate_limit_reset` returns None | Log "could not parse reset time", sleep 65 min (hardcoded fallback buffer), rotate account |
| `ZoneInfo` lookup fails | Fall back to UTC, log warning |
| `find_answered_feedback` finds malformed question.md | Skip that entry, log warning |
| `shutil.move` to answered_feedback fails | Log error, leave in pending_feedback (safe — will try again next run) |
| All accounts exhausted | Sleep until earliest reset_at (see section 6) |
| subprocess.run raises OSError (claude not found) | Re-raise with message "claude binary not found in PATH" |
| SIGTERM during sleep | `stop_flag["requested"]` is set; loop exits cleanly after sleep |

**General principle**: Non-fatal errors are logged with `[orchestrator] WARNING:` prefix and execution continues. Fatal errors (e.g., `claude` not found) raise immediately.

---

## 16. Testing Considerations

This is a pure Python infrastructure script. No unit tests required for the initial implementation. The acceptance criteria are verified by manual integration testing (run the script, observe behavior). However:

- Each function is written to be independently testable (pure inputs/outputs where possible)
- `parse_rate_limit_reset()` and `read_yaml_frontmatter()` are pure functions with no side effects — easy to unit test if needed later
- The main loop is separated from all I/O helpers

---

## 17. Complete File Skeleton (for implementation engineer)

```python
#!/usr/bin/env python3
"""
scripts/automation/orchestrate.py

Session orchestrator for unattended Claude Code batch processing.
Launches sequential claude sessions with per-account CLAUDE_CONFIG_DIR rotation.

Python 3.9+ required. No external dependencies (stdlib only, uses zoneinfo).
"""

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# --- Constants ---
PROJECT_ROOT = ...
AUTOMATION_DIR = ...
# (see section 14 for all constants)

# --- Helpers ---
def read_yaml_frontmatter(path): ...
def parse_args(): ...
def load_state(path): ...
def save_state(path, state): ...
def build_env(account): ...
def strip_hook_footer(text): ...
def write_session_output(outputs_dir, session_uuid, content): ...
def parse_rate_limit_reset(stdout): ...
def find_active_task_goal(project_root): ...
def update_goal_session_fields(goal_path, session_id, account): ...
def find_answered_feedback(feedback_dir): ...
def new_question_written_for(task_id, feedback_dir): ...
def next_available_account(accounts, state): ...
def should_stop(stop_flag, stop_at): ...
def write_report(reports_dir, run_data, accounts, feedback_dir): ...
def run_normal_session(env, session_uuid): ...
def run_resume_session(env, session_id, answer_content): ...
def setup_signals(stop_flag): ...

# --- Entry point ---
def main(): ...

if __name__ == "__main__":
    main()
```

---

## 18. Risks and Potential Issues

1. **Rate limit message format changes**: The regex `r'resets (\d{1,2}:\d{2}(?:am|pm)) \(([^)]+)\)'` is brittle. If Anthropic changes the format, parsing fails silently (fallback: 65-min sleep). The fallback is safe but inefficient.

2. **Multiple in_progress tasks**: `find_active_task_goal()` returns only the first match. This is correct behavior — at most one task should be in_progress, but if multiple are, the script picks one consistently.

3. **answer.md written while session is running**: Extremely unlikely (sequential execution), but harmless — answered feedback is processed at the start of the next loop iteration.

4. **`.stop-requested` file not cleaned up after crash**: Cleaned in `finally` block. If the script is SIGKILL'd (not SIGTERM), the sentinel persists. On next run, it will be detected immediately and prevent a session from starting. The user must delete it manually. This is acceptable behavior and should be documented in the script's docstring.

5. **`session_outputs/` disk usage**: No cleanup logic. Files accumulate over time. Out of scope for this task — can be addressed later.

6. **Account index drift on restart**: State is saved after every session. If the script crashes mid-session (after launching subprocess but before saving state), the account index is not advanced. This means the next run retries the same account — safe and correct.
