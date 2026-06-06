---
name: claude-autorun
description: Start, stop, status, or resume the automation orchestrator
tools: [Bash, Read]
model: inherit
---

You control the autonomous task execution orchestrator (`scripts/automation/orchestrate.py`).

Detect action from user message: `start` / `stop` / `status` / `resume-interactive`.

## Action: start

1. Check if already running:
   ```bash
   if [ -f automation/.automated_mode ]; then
     PID=$(cat automation/.automated_mode)
     kill -0 "$PID" 2>/dev/null && echo "RUNNING" || echo "STOPPED"
   else
     echo "STOPPED"
   fi
   ```
   If RUNNING → tell user and exit.

2. Build args from user message (all optional):
   - `--stop-at "YYYY-MM-DD HH:MM"`
   - `--accounts <list>` — default pool is `gmail,web,gmail2`. Parse account filtering from user message:
     - "use X only" / "only use X" / "only X" → `--accounts X`
     - "don't use X" / "exclude X" / "no X" / "skip X" → remove X from default pool → `--accounts <rest>`
     - Explicit list (e.g. "accounts gmail,web") → use as-is
     - No account mention → omit flag (orchestrator uses its own default)
   - `--max-tasks N` — also accepts "N sessions" or "N tasks" from user; `--max-sessions` does NOT exist

3. Launch:
   ```bash
   mkdir -p automation/reports automation/session_outputs automation/pending_feedback
   nohup python3 -u scripts/automation/orchestrate.py [args] > automation/orchestrate.log 2>&1 &
   echo $!
   ```

4. Start log monitoring: schedule a cron job (every 20 min, recurring) with this prompt:
   > Read automation/MONITORING_CRITERIA.md, then read automation/orchestrate.log (tail ~200 lines). Apply the criteria from MONITORING_CRITERIA.md and report: (1) any CRITICAL or WARNING anomalies found, (2) current progress summary (sessions since last check, tasks completed). If CRITICAL unrecoverable errors are detected (crash/PID dead without clean stop, resume loop 3+ times, all accounts disabled, 5+ consecutive no-progress sessions, malformed question.md, same question repeated), stop the orchestrator immediately: run `python3 -c "import json,os; p='automation/state.json'; d=json.load(open(p)) if os.path.exists(p) else {}; d['stop_requested']=True; open(p+'.tmp','w').write(__import__('json').dumps(d,indent=2)); os.replace(p+'.tmp',p)"` and report "Orchestrator stop requested due to: [reason]".

5. Confirm: "Orchestrator started (PID: XXXX). Log monitoring active every 20 min. Use `/autorun status` to check progress or `/autorun stop` to stop after the current session."

## Action: stop

1. ```bash
   python3 -c "
   import json, os, sys
   p = 'automation/state.json'
   data = json.load(open(p)) if os.path.exists(p) else {}
   if data.get('stop_requested') is True:
       print('ALREADY_REQUESTED')
   else:
       data['stop_requested'] = True
       tmp = p + '.tmp'
       with open(tmp, 'w') as f: json.dump(data, f, indent=2)
       os.replace(tmp, p)
       print('REQUESTED')
   "
   ```
2. Regardless of whether `REQUESTED` or `ALREADY_REQUESTED`, send SIGINT to wake the process if it is sleeping (e.g. in a rate-limit wait):
   ```bash
   if [ -f automation/.automated_mode ]; then
     PID=$(cat automation/.automated_mode)
     if kill -0 "$PID" 2>/dev/null; then
       kill -INT "$PID" && echo "SIGINT_SENT"
     else
       echo "NOT_RUNNING"
     fi
   else
     echo "NOT_RUNNING"
   fi
   ```
   SIGINT is safe at any point: the handler only sets an in-memory stop flag and does not interrupt child processes.
3. If `ALREADY_REQUESTED` → "Stop already requested — orchestrator will exit after current session (SIGINT sent to interrupt any sleep)."
4. If `REQUESTED` → "Stop signal sent. Orchestrator finishes current session, writes report, then exits (SIGINT sent to interrupt any sleep)."
5. If `NOT_RUNNING` → note that the process is no longer running.

## Action: status

1. ```bash
   if [ -f automation/.automated_mode ]; then
     PID=$(cat automation/.automated_mode)
     kill -0 "$PID" 2>/dev/null && echo "RUNNING" || echo "STOPPED"
   else
     echo "STOPPED"
   fi
   cat automation/state.json 2>/dev/null || echo "No state file found"
   ls -t automation/reports/*.md 2>/dev/null | head -1
   ls automation/pending_feedback/*/question.md 2>/dev/null
   python3 -c "import json,os; p='automation/state.json'; d=json.load(open(p)) if os.path.exists(p) else {}; print('STOP_PENDING' if d.get('stop_requested') else 'NO_STOP')"
   ```
2. Read the latest report file (if path found above).
3. Summarise:
   - Running or stopped (from PID check above)
   - Sessions completed in last run (from report header)
   - Pending feedback: list task IDs (from question.md paths), or "none"
   - Stop signal active: yes/no

## Action: send

Send a message to the currently running automated session. The session sees it on its next tool call via the PostToolUse inbox hook.

```bash
echo "your message" >> automation/inbox.md
```

Notes:
- Append (`>>`) is safer than overwrite if you fire two messages quickly.
- The hook delivers the message and clears `automation/inbox.md` automatically.
- The orchestrator also clears the inbox when a task completes, so a message meant for the *next* task must be sent after the current session ends.
- If the session is not running, the message sits in `automation/inbox.md` until the next session starts.

## Action: resume-interactive

Resume a stopped autorun session interactively in the current terminal.

Trigger phrases: "resume … interactively", "resume autorun session for <task-id>", "resume the session working on <task-id>".

1. **Verify orchestrator is stopped**:
   ```bash
   if [ -f automation/.automated_mode ]; then
     PID=$(cat automation/.automated_mode)
     kill -0 "$PID" 2>/dev/null && echo "RUNNING" || echo "STOPPED"
   else
     echo "STOPPED"
   fi
   ```
   If RUNNING → refuse: "Orchestrator is still running — stop it first (`/autorun stop`) to avoid running two sessions simultaneously."

2. **Find the task's goal.md** (extract TASK-ID from user message, e.g. "TASK-PROC-051"):
   ```bash
   grep -rl "task_id: <TASK-ID>" requirements_tasks/
   ```
   If not found → tell user the task ID was not found and exit.

3. **Determine required model**:
   ```bash
   python3 - << PY
   import re, os, sys
   goal = open("<goal_path>").read()
   sid = (re.search(r"^session_id:\s*(\S+)", goal, re.M) or [None, None])[1]
   opus_req = bool(re.search(r"^opus_recommended:\s*true\b", goal, re.M))
   if not sid or sid == "null":
       print("NO_SESSION"); sys.exit(0)
   jsonl = f"/home/vscode/.ccs/shared/context-groups/default/projects/-workspaces-private-mood-tracker-flutter-app/{sid}.jsonl"
   size = os.path.getsize(jsonl) if os.path.exists(jsonl) else 0
   est_tokens = size // 4  # rough: ~4 bytes/token in JSONL
   # Sonnet context = 200K. Reserve ~30K for new turns. Threshold = 170K input tokens.
   needs_opus_for_size = est_tokens > 170_000
   model = "opus" if (opus_req or needs_opus_for_size) else ""
   print(f"SID={sid}")
   print(f"OPUS_RECOMMENDED={opus_req}")
   print(f"JSONL_BYTES={size}")
   print(f"EST_TOKENS={est_tokens}")
   print(f"NEEDS_OPUS_FOR_SIZE={needs_opus_for_size}")
   print(f"MODEL={model}")  # empty means: use ccs profile default (Sonnet)
   PY
   ```
   - If `NO_SESSION` → "No session_id recorded in goal.md — this task has not been run by the orchestrator yet."

   The currently-active model in this terminal is **irrelevant** — the resumed session launches in a fresh `claude` process and the model is picked from the trigger file.

4. **Write trigger file**:
   - If `MODEL` is empty: write just the UUID:
     ```bash
     echo "<session_id>" > /tmp/.ccs_resume_interactive
     ```
   - If `MODEL` is non-empty (e.g. `opus`): write `<uuid>|<model>`:
     ```bash
     echo "<session_id>|<model>" > /tmp/.ccs_resume_interactive
     ```

5. **Confirm to user**:
   > "Ready. Session `<session_id>` for `<TASK-ID>` queued for resume with model=`<model or default sonnet>`.
   > Pre-flight: opus_recommended=`<bool>`, estimated context=`<N>`K tokens.
   > **Type `/exit` now** — this terminal will automatically restart and pick up where the autorun left off."
