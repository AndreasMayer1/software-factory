# Context Gather — Orchestrator State JSON Consolidation

Gathered from live codebase on 2026-04-30 for Opus planner.

---

# orchestrate.py — PersistentState dataclass (lines 303–319)

```python
303	@dataclass
304	class PersistentState:
305	    """State that survives across orchestrator restarts (written to state.json).
306	
307	    Why: splitting persistent state (survives restarts) from in-memory run accumulators
308	    (RunData) makes it clear what is serialised to disk and prevents accidentally
309	    persisting transient data like disabled_accounts (which should reset each run).
310	    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
311	            feat_session_orchestrator/tasks/2026-04-10_impl_implement-orchestrator-monitoring-improvements/
312	            plans_and_protocols/2026-04-10_02_plan_rewrite-architecture.md#3-state-management
313	    """
314	    account_index: int = 0
315	    run_count: int = 0
316	    start_time: "str | None" = None        # ISO string
317	    paused_tasks: list = field(default_factory=list)
318	    rate_limited_until: dict = field(default_factory=dict)   # account -> ISO datetime string
319	    question_fingerprints: dict = field(default_factory=dict)  # task_id -> {words: list, preview: str}
```

---

# orchestrate.py — load_state() (lines 322–338)

```python
322	def load_state(path: str, deps: "OrchestratorDeps") -> PersistentState:
323	    """Load state.json; merge missing keys with defaults. Start fresh on error."""
324	    if deps.file_exists(path):
325	        try:
326	            raw = deps.read_file(path)
327	            data = json.loads(raw)
328	            return PersistentState(
329	                account_index=data.get("account_index", 0),
330	                run_count=data.get("run_count", 0),
331	                start_time=data.get("start_time", None),
332	                paused_tasks=data.get("paused_tasks", []),
333	                rate_limited_until=data.get("rate_limited_until", {}),
334	                question_fingerprints=data.get("question_fingerprints", {}),
335	            )
336	        except (json.JSONDecodeError, OSError) as e:
337	            print(f"[orchestrator {_ts()}] WARNING: state.json corrupt or unreadable ({e}), starting fresh")
338	    return PersistentState()
```

---

# orchestrate.py — save_state() (lines 341–356)

```python
341	def save_state(path: str, state: PersistentState, deps: "OrchestratorDeps") -> None:
342	    """Atomic write via tmp + os.replace to avoid partial writes on crash."""
343	    tmp = path + ".tmp"
344	    try:
345	        deps.makedirs(os.path.dirname(path))
346	        data = dataclasses.asdict(state)
347	        content = json.dumps(data, indent=2)
348	        deps.write_file(tmp, content)
349	        os.replace(tmp, path)
350	    except TypeError as e:
351	        # Why: PersistentState.question_fingerprints stores words as list (JSON-safe),
352	        # but a future caller might accidentally pass a set. Catch TypeError explicitly
353	        # so the error is clear rather than silently failing.
354	        print(f"[orchestrator {_ts()}] WARNING: state contains non-serialisable value ({e}), not saving")
355	    except OSError as e:
356	        print(f"[orchestrator {_ts()}] WARNING: could not save state ({e})")
```

---

# orchestrate.py — SENTINEL_STOP constant + stop-requested check (lines 53–54, 1550–1560)

Sentinel constants (lines 53–54):
```python
53	SENTINEL_AUTOMATED = os.path.join(AUTOMATION_DIR, ".automated_mode")
54	SENTINEL_STOP = os.path.join(AUTOMATION_DIR, ".stop-requested")
```

Stop-conditions check — `_check_stop_conditions` method (lines 1543–1560):
```python
1543	    def _check_stop_conditions(
1544	        self,
1545	        args: argparse.Namespace,
1546	        stop_flag: dict,
1547	        stop_at: "datetime | None",
1548	        sessions_launched: int,
1549	    ) -> "tuple[bool, str]":
1550	        """Check all stop conditions. Returns (should_stop, reason). No I/O."""
1551	        if stop_flag["requested"]:
1552	            return True, "manual"
1553	        if self.deps.file_exists(SENTINEL_STOP):
1554	            return True, "manual"
1555	        if stop_at and self.deps.get_now_local() >= stop_at:
1556	            return True, "scheduled"
1557	        if args.max_tasks is not None and sessions_launched >= args.max_tasks:
1558	            print(f"[orchestrator {_ts()}] Reached --max-tasks {args.max_tasks}, stopping")
1559	            return True, "max_tasks"
1560	        return False, ""
```

Also checked in hung-detection loop (line 708–711):
```python
708	        # (a) Graceful stop requested
709	        if stop_flag["requested"]:
710	            reason = "stop_requested"
711	            break
```

---

# orchestrate.py — SIGTERM/SIGINT signal handler registration (lines 2268–2280)

```python
2268	def setup_signals(stop_flag: dict) -> None:
2269	    """Register SIGTERM and SIGINT handlers to set stop_flag["requested"].
2270	
2271	    Why: dict-based stop_flag (not a global bool) allows mutation from a lambda
2272	    without needing 'global' keyword — compatible with signal handler constraints.
2273	    Source: plan section 10.
2274	    """
2275	    def handler(signum, frame):
2276	        stop_flag["requested"] = True
2277	        print(f"\n[orchestrator {_ts()}] Signal {signum} received — stopping after current session")
2278	
2279	    signal.signal(signal.SIGTERM, handler)
2280	    signal.signal(signal.SIGINT, handler)
```

Signal setup is called from main() at line 2327:
```python
2325	    # Why: dict container allows lambda signal handler to mutate the flag
2326	    stop_flag = {"requested": False}
2327	    setup_signals(stop_flag)
```

---

# orchestrate.py — main() startup block: .automated_mode sentinel + start_time (lines 2365–2377)

```python
2365	    # Create sentinel: marks this process as running in automated mode
2366	    deps.makedirs(AUTOMATION_DIR)
2367	    try:
2368	        deps.write_file(SENTINEL_AUTOMATED, str(deps.getpid()))
2369	    except OSError as e:
2370	        print(f"[orchestrator {_ts()}] WARNING: could not create .automated_mode sentinel ({e})")
2371	
2372	    # Always reset start_time on each new launch so state.json reflects the current run
2373	    start_time = deps.get_now_local()
2374	    state.start_time = start_time.isoformat()
2375	    save_state(STATE_PATH, state, deps)
2376	
2377	    run_data = RunData(start_time=start_time)
```

---

# orchestrate.py — main() finally: block (lines 2400–2430)

```python
2400	    finally:
2401	        stop_time = deps.get_now_local()
2402	        run_data.stop_time = stop_time
2403	        report_path = write_report(REPORTS_DIR, run_data, accounts, FEEDBACK_DIR, deps)
2404	        # write_health_summary receives the exact path returned by write_report,
2405	        # fixing the pre-rewrite minute-rollover bug.
2406	        write_health_summary(
2407	            report_path,
2408	            run_data,
2409	            run_data.initial_in_progress,
2410	            deps,
2411	        )
2412	        # AC-24: git commit report + question.md files on stop (non-fatal)
2413	        stop_str = stop_time.strftime("%Y-%m-%d %H:%M")
2414	        stop_reason = run_data.stop_reason
2415	        git_commit_best_effort(
2416	            [report_path, "automation/pending_feedback/*/question.md"],
2417	            f"chore(automation): session report {stop_str} [{stop_reason}]",
2418	            deps,
2419	        )
2420	        # Clean up sentinels (best-effort)
2421	        unlink_if_exists(SENTINEL_AUTOMATED)
2422	        unlink_if_exists(SENTINEL_STOP)
2423	        save_state(STATE_PATH, state, deps)
2424	        print(f"[orchestrator {_ts()}] Stopped. Reason: {stop_reason}")
2425	        # Release lock
2426	        try:
2427	            fcntl.flock(lock_fd, fcntl.LOCK_UN)
2428	            lock_fd.close()
2429	        except OSError:
2430	            pass
```

---

# orchestrate.py — rate_limit_sleep() function (lines 99–124)

```python
 99	def rate_limit_sleep(total_secs: float, stop_flag: dict, reset_dt: "datetime | None" = None) -> None:
100	    """Sleep during a rate-limit window, emitting a heartbeat log line every 15 minutes.
101	
102	    Keeps orchestrate.log fresh so sleep_when_autorun_done.ps1 does not mistake an
103	    intentional wait for a crashed process (which uses a 30-minute staleness threshold).
104	    """
105	    deadline = time.monotonic() + total_secs
106	    next_heartbeat = time.monotonic() + _RATE_LIMIT_HEARTBEAT_SECS
107	    # Convert UTC reset time to local for display — reset_dt is stored as UTC in state.json
108	    reset_local = reset_dt.astimezone() if reset_dt else None
109	    reset_info = f" (resets {reset_local.strftime('%Y-%m-%d %H:%M %Z')})" if reset_local else ""
110	    while not stop_flag["requested"]:
111	        remaining = deadline - time.monotonic()
112	        if remaining <= 0:
113	            break
114	        now_mono = time.monotonic()
115	        if now_mono >= next_heartbeat:
116	            remaining_min = remaining / 60
117	            print(
118	                f"[orchestrator {_ts()}] Still waiting for rate-limit reset{reset_info} — "
119	                f"{remaining_min:.0f} min remaining",
120	                flush=True,
121	            )
122	            next_heartbeat = now_mono + _RATE_LIMIT_HEARTBEAT_SECS
123	        tick = min(30, remaining, next_heartbeat - now_mono)
124	        time.sleep(tick)
```

Rate-limit sleep call sites:
- Line 1820: Resume path — all accounts exhausted for a resume
  ```python
  rate_limit_sleep(wait_secs, stop_flag, reset_dt=wait_until)
  ```
- Line 2014: Normal session path — all accounts rate-limited
  ```python
  rate_limit_sleep(wait_secs, stop_flag, reset_dt=wait_until)
  ```

Context around call site at line 2007–2016 (`_get_next_account` method):
```python
2007	        if wait_until is not None:
2008	            wait_secs = (wait_until - self.deps.get_now_utc()).total_seconds()
2009	            if wait_secs > 0:
2010	                print(
2011	                    f"[orchestrator {_ts()}] All accounts rate-limited. "
2012	                    f"Waiting {wait_secs:.0f}s until {wait_until}"
2013	                )
2014	                rate_limit_sleep(wait_secs, stop_flag, reset_dt=wait_until)
2015	            # After sleeping, re-enter loop to re-check stop conditions and pick account
2016	            return None, True
```

---

# orchestrate.py — session launch block: subprocess.Popen (lines 666–696)

`run_session_with_hung_detection` (lines 666–696):
```python
666	def run_session_with_hung_detection(
667	    cmd: list,
668	    env: dict,
669	    session_uuid: str,
670	    hung_check_interval: int,
671	    hung_timeout_secs: int,
672	    session_timeout_secs: int,
673	    stop_flag: dict,
674	    deps: "OrchestratorDeps",
675	) -> subprocess.CompletedProcess:
676	    """Launch cmd via Popen and poll for hung-session conditions.
677	
678	    Why: subprocess.run() blocks indefinitely — a hung claude session (no output,
679	    no child processes, JSONL stale) would block the orchestrator forever.
680	    This wrapper polls every hung_check_interval seconds and kills the process when:
681	    - stop_flag is set (graceful shutdown)
682	    - elapsed >= session_timeout_secs (hard ceiling, default 4 h)
683	    - JSONL mtime frozen AND no child processes for >= hung_timeout_secs (hung)
684	    Child process presence is the key signal: the 13-hour incident showed a session
685	    with stale JSONL but active dart/bash children — it was genuinely working.
686	    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
687	            feat_session_orchestrator/tasks/2026-04-24_impl_hung-session-detection/
688	            plans_and_protocols/2026-04-24_01_plan_hung-session-detection.md
689	    """
690	    proc = deps.popen_subprocess(
691	        cmd,
692	        stdout=subprocess.PIPE,
693	        stderr=subprocess.STDOUT,
694	        text=True,
695	        env=env,
696	    )
```

`run_normal_session` — builds cmd and calls run_session_with_hung_detection (lines 543–579):
```python
543	def run_normal_session(
544	    env: dict,
545	    session_uuid: str,
546	    hung_check_interval: int,
547	    hung_timeout_secs: int,
548	    session_timeout_secs: int,
549	    stop_flag: dict,
550	    deps: "OrchestratorDeps",
551	) -> subprocess.CompletedProcess:
552	    """Launch a new claude session with pre-assigned UUID.

553	    Why: --session-id names the JSONL file with the pre-assigned UUID so we can
554	    locate the session storage later. -p auto-exits after completing the prompt.
555	    Task filtering (skip tasks awaiting answers) is handled by the routing skill
556	    via scripts/is_awaiting_answer.py — not injected here.
557	    Source: goal.md Technical Notes — confirmed via exploration.
558	    """
559	    cmd = [
560	        "claude",
561	        "--dangerously-skip-permissions",
562	        "--session-id",
563	        session_uuid,
564	        "-p",
565	        (
566	            "Invoke the claude-automated-mode skill immediately "
567	            "(CLAUDE_AUTOMATED_MODE=1 is active and automation/.automated_mode exists). "
568	            "Then do next task."
569	        ),
570	    ]
571	    try:
572	        return run_session_with_hung_detection(
573	            cmd, env, session_uuid,
574	            hung_check_interval, hung_timeout_secs, session_timeout_secs,
575	            stop_flag, deps,
576	        )
577	    except OSError as e:
578	        raise OSError(f"claude binary not found in PATH: {e}") from e
```

Production wiring — `subprocess.Popen` injected into deps at line 2332:
```python
2331	    deps = OrchestratorDeps(
2332	        run_subprocess=subprocess.run,
2333	        popen_subprocess=subprocess.Popen,
...
2344	    )
```

---

# orchestrate.py — save_state() call sites (all line numbers)

| Line  | Context |
|-------|---------|
| 2375  | main() startup — after resetting start_time |
| 1702  | (search context needed — within run_loop or similar) |
| 1890  | resume path — after disabling perm-error account |
| 1903  | resume path — after recording rate-limit |
| 1925  | resume path — after generic resume failure |
| 1930  | resume path — success, run_count++ |
| 2095  | normal session — after disabling perm-error account |
| 2120  | normal session — after recording rate-limit and rotating account |
| 2133  | normal session — success, account round-robin + run_count++ |
| 2423  | finally block — cleanup on stop |

Full grep output for reference:
```
1702:            save_state(STATE_PATH, state, self.deps)
1890:            save_state(STATE_PATH, state, self.deps)
1903:            save_state(STATE_PATH, state, self.deps)
1925:            save_state(STATE_PATH, state, self.deps)
1930:            save_state(STATE_PATH, state, self.deps)
2095:            save_state(STATE_PATH, state, self.deps)
2120:            save_state(STATE_PATH, state, self.deps)
2133:        save_state(STATE_PATH, state, self.deps)
2375:    save_state(STATE_PATH, state, deps)
2423:        save_state(STATE_PATH, state, deps)
```

---

# sleep_when_autorun_done.ps1 — FULL FILE (lines 1–497)

```powershell
  1	<#
  2	.SYNOPSIS
  3	    Puts the PC to sleep once the autorun orchestrator finishes.
  4	
  5	.DESCRIPTION
  6	    Watches the orchestrator (scripts/automation/orchestrate.py) from Windows and
  7	    suspends the host once it stops. Optionally schedules a Windows wake-up task
  8	    so the PC comes back at a chosen time (e.g. for the next nightly run).
  9	
 10	    Detection strategy (cross-platform  -  works for WSL2 and Docker devcontainers):
 11	
 12	      1. Sentinel file `automation/.automated_mode`
 13	         - Cleanly removed on graceful stop (orchestrate.py line 2006)
 14	         - Strongest "definitely stopped" signal
 15	      2. Log activity on `automation/orchestrate.log`
 16	         - mtime newer than -LogStaleMinutes => "still running"
 17	         - Catches the SIGKILL case where the sentinel never gets cleaned up
 18	      3. Final log line  "[orchestrator] Stopped. Reason: ..."
 19	         - Used to surface the stop reason to the user (max-tasks, signal, etc.)
 20	
 21	    The script never reads container PIDs from the host (PID namespaces make that
 22	    unreliable across WSL/Docker), so it works regardless of the dev container backend.
 23	
 24	.PARAMETER ProjectPath
 25	    Windows path to the flutter_app folder.
 26	    Default: parent of the script's own directory (resolved via $PSScriptRoot or $MyInvocation.MyCommand.Path).
 27	
 28	.PARAMETER WakeBeforeResetMinutes
 29	    Wake the PC this many minutes BEFORE the earliest rate-limit reset
 30	    (read from automation/state.json -> rate_limited_until). Default 5.
 31	
 32	    Behaviour after the orchestrator stops:
 33	      - state.json has rate-limited accounts  -> wake = (earliest reset) - N min
 34	      - no rate-limited accounts             -> no wake task (just sleep)
 35	      - earliest reset already in the past   -> no wake task (would fire immediately)
 36	
 37	.PARAMETER NoWake
 38	    Disable the wake-up logic entirely; always sleep without scheduling a wake task.
 39	
 40	.PARAMETER PollSeconds
 41	    Poll interval. Default 60.
 42	
 43	.PARAMETER LogStaleMinutes
 44	    Treat the orchestrator as "no longer active" if orchestrate.log has not been
 45	    written for this many minutes (covers SIGKILL where the sentinel persists).
 46	    Default 30.
 47	
 48	.PARAMETER WakeTaskName
 49	    Name of the scheduled task that wakes the PC. Default "AutorunWakePC".
 50	
 51	.PARAMETER Hibernate
 52	    Hibernate (S4) instead of sleep (S3). Slower wake but zero power draw.
 53	
 54	.PARAMETER DryRun
 55	    Print what would happen, then exit instead of actually suspending.
 56	
 57	.PARAMETER Quiet
 58	    Suppress per-poll status lines (still prints start/stop summaries).
 59	
 60	.PARAMETER LogFile
 61	    Append all output to this log file (in addition to console).
 62	
 63	.EXAMPLE
 64	    # Default: sleep when done, auto-wake 5 min before earliest rate-limit reset
 65	    .\scripts\sleep_when_autorun_done.ps1
 66	
 67	.EXAMPLE
 68	    # Wake 10 min before the earliest reset (more buffer for orchestrator restart)
 69	    .\scripts\sleep_when_autorun_done.ps1 -WakeBeforeResetMinutes 10
 70	
 71	.EXAMPLE
 72	    # Just sleep, never wake automatically
 73	    .\scripts\sleep_when_autorun_done.ps1 -NoWake
 74	
 75	.EXAMPLE
 76	    # Hibernate + dry-run to verify behaviour before committing
 77	    .\scripts\sleep_when_autorun_done.ps1 -Hibernate -DryRun
 78	
 79	.NOTES
 80	    Wake-up requires:
 80	      - Administrator rights to register the scheduled task
 81	      - "Allow wake timers" enabled in Power Options (powercfg /waketimers to inspect)
 82	      - Hardware support for wake from sleep (most modern PCs)
 83	#>
 84	
 85	[CmdletBinding()]
 86	param(
 87	    [string] $ProjectPath             = "",
 88	    [int]    $WakeBeforeResetMinutes  = 5,
 89	    [switch] $NoWake,
 90	    [int]    $PollSeconds             = 60,
 91	    [int]    $LogStaleMinutes         = 30,
 92	    [string] $WakeTaskName            = "AutorunWakePC",
 93	    [switch] $Hibernate,
 94	    [switch] $DryRun,
 95	    [switch] $Quiet,
 96	    [string] $LogFile                 = ""
 97	)
 98	
 99	Set-StrictMode -Version Latest
100	$ErrorActionPreference = "Stop"
101	
102	# Resolve ProjectPath — $PSScriptRoot can be empty when launched via a Windows shortcut;
103	# fall back to $MyInvocation.MyCommand.Path which is always populated with -File.
104	if (-not $ProjectPath) {
105	    $scriptDir = if ($PSScriptRoot) { $PSScriptRoot }
106	                 elseif ($MyInvocation.MyCommand.Path) { Split-Path $MyInvocation.MyCommand.Path -Parent }
107	                 else { $null }
108	    if ($scriptDir) { $ProjectPath = Split-Path $scriptDir -Parent }
109	}
110	if (-not $ProjectPath) {
111	    Write-Error "Cannot determine ProjectPath automatically. Pass -ProjectPath explicitly."
112	    exit 1
113	}
114	
115	# -- Paths ---------------------------------------------------------------------
116	
117	$automationDir   = Join-Path $ProjectPath "automation"
118	$sentinelPath    = Join-Path $automationDir ".automated_mode"
119	$stopRequestPath = Join-Path $automationDir ".stop-requested"
120	$orchestrateLog  = Join-Path $automationDir "orchestrate.log"
121	$reportsDir      = Join-Path $automationDir "reports"
122	$statePath       = Join-Path $automationDir "state.json"
123	
124	# -- Logging -------------------------------------------------------------------
125	
126	function Write-Log {
127	    param([string]$Message, [switch]$Status)
128	    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
129	    if (-not ($Status -and $Quiet)) {
130	        Write-Host $line
131	    }
132	    if ($LogFile) {
133	        Add-Content -LiteralPath $LogFile -Value $line
134	    }
135	}
136	
137	# -- Detection -----------------------------------------------------------------
138	
139	function Test-SentinelPresent {
140	    return (Test-Path -LiteralPath $sentinelPath)
141	}
142	
143	function Get-LogMTime {
144	    if (-not (Test-Path -LiteralPath $orchestrateLog)) { return $null }
145		return (Get-Item -LiteralPath $orchestrateLog).LastWriteTime
146	}
147	
148	function Test-LogActive {
149	    $mtime = Get-LogMTime
150	    if ($null -eq $mtime) { return $false }
151	    $ageMinutes = ((Get-Date) - $mtime).TotalMinutes
152	    return ($ageMinutes -lt $LogStaleMinutes)
153	}
154	
155	# Why: combine sentinel + log-activity. Sentinel disappears on graceful stop;
156	# the activity check catches SIGKILL where the sentinel persists.
157	function Test-OrchestratorActive {
158	    if (-not (Test-SentinelPresent)) { return $false }
159	    return (Test-LogActive)
160	}
161	
162	function Get-LastLogLine {
163	    if (-not (Test-Path -LiteralPath $orchestrateLog)) { return "" }
164	    try { return (Get-Content -LiteralPath $orchestrateLog -Tail 1 -ErrorAction Stop) }
165	    catch { return "" }
166	}
167	
168	function Invoke-TimezoneCheck {
169	    param(
170	        [string]   $LogLine,   # last line of orchestrate.log
171	        [datetime] $HostNow    # host clock snapshot (passed in, not re-read, for consistency)
172	    )
173	    # Parse [orchestrator HH:MM:SS] from the log line
174	    if (-not ($LogLine -match '^\[orchestrator (\d{2}):(\d{2}):(\d{2})\]')) { return }
175	
176	    $h = [int]$Matches[1]; $m = [int]$Matches[2]; $s = [int]$Matches[3]
177	    # Reconstruct on today's date so we can diff against host time
178	    $logTime = Get-Date -Year $HostNow.Year -Month $HostNow.Month -Day $HostNow.Day `
179	                        -Hour $h -Minute $m -Second $s -Millisecond 0
180	
181	    $diffMin = ($HostNow - $logTime).TotalMinutes
182	    # Clamp into [-720, +720] to handle entries that straddle midnight
183	    if ($diffMin -gt  720) { $diffMin -= 1440 }
184	    if ($diffMin -lt -720) { $diffMin += 1440 }
185	
186	    if ([math]::Abs($diffMin) -gt 30) {
187	        Write-Log "ERROR: Container timezone does not match host OS timezone!"
188	        Write-Log ("  Container log time : {0:D2}:{1:D2}:{2:D2}" -f $h, $m, $s)
189	        Write-Log ("  Host OS time       : {0}" -f $HostNow.ToString("HH:mm:ss"))
190	        $sign = if ($diffMin -ge 0) { "+" } else { "" }
191	        Write-Log ("  Difference         : {0}{1:N0} min" -f $sign, $diffMin)
192	        Write-Log "  Fix: set the TZ env-var in the dev container to match the host (e.g. TZ=Europe/Berlin)."
193	    }
194	}
195	
196	function Get-StopReason {
197	    if (-not (Test-Path -LiteralPath $orchestrateLog)) { return $null }
198	    try {
199	        $tail = Get-Content -LiteralPath $orchestrateLog -Tail 50 -ErrorAction Stop
200	        $stopLine = $tail | Where-Object { $_ -match 'Stopped\. Reason:' } | Select-Object -Last 1
201	        if ($stopLine) { return $stopLine }
202	        $maxLine  = $tail | Where-Object { $_ -match 'Reached --max-tasks' } | Select-Object -Last 1
203	        if ($maxLine)  { return $maxLine  }
204	        return $null
205	    } catch { return $null }
206	}
207	
208	function Get-LatestReportName {
209	    if (-not (Test-Path -LiteralPath $reportsDir)) { return $null }
210	    $latest = Get-ChildItem -LiteralPath $reportsDir -Filter "*.md" -ErrorAction SilentlyContinue |
211	              Sort-Object LastWriteTime -Descending | Select-Object -First 1
212	    if ($latest) { return $latest.Name }
213	    return $null
214	}
215	
216	# Why: state.json -> rate_limited_until is the orchestrator's source of truth for
217	# when each account becomes usable again. Disabled (no-access) accounts live only
218	# in the orchestrator's in-memory state, so they never appear here  -  meaning we
219	# automatically pick the earliest reset across only the *working but limited*
220	# accounts. Stale entries (reset already in the past) are filtered: the orchestrator
221	# only purges them on the next attempt to use that account, so they linger in
222	# state.json and would otherwise mask a still-active limit on another account.
223	#
224	# Returns hashtable @{
225	#   Earliest    = [datetime?]                  # earliest *future* reset
226	#   Active      = @{ name = [datetime] }       # accounts still rate-limited (future)
227	#   Stale       = @{ name = [datetime] }       # entries whose reset is already past
228	# }
229	function Get-RateLimitState {
230	    param([string]$Path = $statePath)
231	    if (-not (Test-Path -LiteralPath $Path)) {
232	        return @{ Earliest = $null; Active = @{}; Stale = @{} }
233	    }
234	    try {
235	        $json = Get-Content -LiteralPath $Path -Raw -ErrorAction Stop | ConvertFrom-Json
236	    } catch {
237	        Write-Log "WARNING: state.json could not be parsed: $($_.Exception.Message)"
238	        return @{ Earliest = $null; Active = @{}; Stale = @{} }
239	    }
240	
241	    if (-not ($json.PSObject.Properties['rate_limited_until'])) {
242	        return @{ Earliest = $null; Active = @{}; Stale = @{} }
243	    }
244	
245	    $now      = Get-Date
246	    $active   = @{}
247	    $stale    = @{}
248	    $earliest = $null
249	
250	    foreach ($prop in $json.rate_limited_until.PSObject.Properties) {
251	        $accountName = $prop.Name
252	        $isoStr      = [string]$prop.Value
253	        try {
254	            # RoundtripKind preserves the UTC offset from the ISO string (state.json stores UTC).
255	            # .ToLocalTime() converts to local so that comparisons against Get-Date (local Kind)
256	            # and the wake-up arithmetic on $earliest are all in the same timezone.
257	            $dt = ([datetime]::Parse(
258	                $isoStr,
259	                [System.Globalization.CultureInfo]::InvariantCulture,
260	                [System.Globalization.DateTimeStyles]::RoundtripKind
261	            )).ToLocalTime()
262	        } catch {
263	            Write-Log "WARNING: rate_limited_until[$accountName] not parseable: $isoStr"
264	            continue
265	        }
266	
267	        if ($dt -le $now) {
268	            # Already past  -  orchestrator hasn't purged it yet but the account is usable
269	            $stale[$accountName] = $dt
270	            continue
271	        }
272	
273	        $active[$accountName] = $dt
274	        if ($null -eq $earliest -or $dt -lt $earliest) { $earliest = $dt }
275	    }
276	
277	    return @{ Earliest = $earliest; Active = $active; Stale = $stale }
278	}
279	
280	# -- Privileges + wake-task ----------------------------------------------------
281	
282	function Test-IsAdmin {
283	    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
284	    $principal = New-Object Security.Principal.WindowsPrincipal($id)
285	    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
286	}
287	
288	function Register-WakeTask {
289	    param([datetime]$WakeAt)
290	
291	    if (-not (Test-IsAdmin)) {
292	        throw "Wake-up requires admin rights to register a SYSTEM scheduled task. Re-run PowerShell as Administrator, or pass -NoWake."
293	    }
294	
295	    $action   = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c rem autorun-wake"
296	    $trigger  = New-ScheduledTaskTrigger -Once -At $WakeAt
297	    $settings = New-ScheduledTaskSettingsSet `
298	                    -WakeToRun `
299	                    -StartWhenAvailable `
300	                    -AllowStartIfOnBatteries `
301	                    -DontStopIfGoingOnBatteries
302	    # Why: SYSTEM/ServiceAccount fires even when no interactive session exists (required
303	    # for wake-from-sleep); Interactive logon is silently skipped while the PC sleeps.
304	    $principal = New-ScheduledTaskPrincipal `
305	                    -UserId "SYSTEM" `
306	                    -LogonType ServiceAccount `
307	                    -RunLevel Highest
308	
309	    Register-ScheduledTask `
310	        -TaskName  $WakeTaskName `
311	        -Action    $action `
312	        -Trigger   $trigger `
313	        -Settings  $settings `
314	        -Principal $principal `
315	        -Force | Out-Null
316	
317	    Write-Log ("Wake task '{0}' registered for {1}." -f $WakeTaskName, $WakeAt.ToString("yyyy-MM-dd HH:mm:ss"))
318	}
319	
320	# -- Suspend -------------------------------------------------------------------
321	
322	# Why: Win32 API via System.Windows.Forms is reliable; rundll32 powrprof
323	# silently ignores its parameters in many Windows builds.
324	function Invoke-SystemSleep {
325	    param([switch]$UseHibernate)
326	
327	    Add-Type -AssemblyName System.Windows.Forms
328	    $state = if ($UseHibernate) {
329	        [System.Windows.Forms.PowerState]::Hibernate
330	    } else {
331	        [System.Windows.Forms.PowerState]::Suspend
332	    }
333	    # SetSuspendState(state, force=false, disableWakeEvent=false)
334	    # disableWakeEvent MUST be false for scheduled wake tasks to fire.
335	    [void][System.Windows.Forms.Application]::SetSuspendState($state, $false, $false)
336	}
337	
338	# -- Main ----------------------------------------------------------------------
339	
340	if (-not $env:PESTER_TESTING) {
341	
342	# Validate paths early
343	if (-not (Test-Path -LiteralPath $automationDir)) {
344	    throw "Automation directory not found: $automationDir (check -ProjectPath)"
345	}
346	
347	# Validate admin up-front when wake-up is possible (we don't yet know if state.json
348	# will have rate limits, but failing early is better than after the orchestrator stops)
349	if (-not $NoWake -and -not (Test-IsAdmin)) {
350	    throw "Wake-up is enabled by default and needs Administrator. Re-run elevated, or pass -NoWake."
351	}
352	
353	Write-Log "--- sleep_when_autorun_done --------------------------"
354	Write-Log "Project       : $ProjectPath"
355	Write-Log "Poll interval : ${PollSeconds}s"
356	Write-Log "Log-stale     : ${LogStaleMinutes} min (treats no log activity as 'done')"
357	Write-Log ("Suspend mode  : {0}" -f $(if ($Hibernate) { "Hibernate (S4)" } else { "Sleep (S3)" }))
358	if ($NoWake) {
359	    Write-Log "Wake-up       : disabled (-NoWake)"
360	} else {
361	    Write-Log "Wake-up       : auto, ${WakeBeforeResetMinutes} min before earliest rate-limit reset"
362	}
363	if ($DryRun) { Write-Log "Mode          : DRY RUN (no actual suspend)" }
364	Write-Log ""
365	
366	# Wait for orchestrator to start (covers "I started this script first")
367	$waitedForStart = $false
368	while (-not (Test-OrchestratorActive)) {
369	    if (-not $waitedForStart) {
370	        Write-Log "Orchestrator not active yet  -  waiting for it to start..."
371	        $waitedForStart = $true
372	    }
373	    Start-Sleep -Seconds $PollSeconds
374	}
375	
376	Write-Log "Orchestrator is active. Polling..."
377	
378	# Track when stop is requested so we can show it during polling
379	$stopRequestedAnnounced = $false
380	
381	# Timezone-mismatch check state.
382	# Strategy: watch for the 2nd new log write after startup. On the 2nd write, compare the
383	# log timestamp against the host clock. We use the 2nd write (not the 1st) so that a
384	# wake-from-sleep event — where the script sees an old pre-sleep entry as "new" — does
385	# not trigger a false alarm. Between entry-1 and entry-2 observations we check whether
386	# the host clock jumped by more than 3x the poll interval; if it did, the laptop slept
387	# and we reset the state to treat the current entry as the new entry-1.
388	$tzBaselineMTime  = Get-LogMTime   # mtime at monitoring start — only writes AFTER this count
389	$tzEntry1MTime    = $null          # mtime at first new write
390	$tzEntry1HostTime = $null          # host clock when entry-1 was observed
391	$tzCheckDone      = $false
392	$tzSleepThreshold = [math]::Max(3 * $PollSeconds, 180)   # seconds; at least 3 min
393	
394	# Poll until orchestrator stops
395	while (Test-OrchestratorActive) {
396	    $lastLine = Get-LastLogLine
397	    $mtime    = Get-LogMTime
398	    $ageSec   = if ($mtime) { [int]((Get-Date) - $mtime).TotalSeconds } else { -1 }
399	
400	    if ((Test-Path -LiteralPath $stopRequestPath) -and -not $stopRequestedAnnounced) {
401	        Write-Log "Stop already requested  -  orchestrator will exit after current session."
402	        $stopRequestedAnnounced = $true
403	    }
404	
405	    # -- Timezone check (runs at most once per invocation) --
406	    if (-not $tzCheckDone -and $null -ne $mtime -and $mtime -ne $tzBaselineMTime) {
407	        if ($null -eq $tzEntry1MTime) {
408	            # First new write observed — store it, wait for the next one
409	            $tzEntry1MTime    = $mtime
410	            $tzEntry1HostTime = Get-Date
411	        } elseif ($mtime -ne $tzEntry1MTime) {
412	            $hostNow = Get-Date
413	            $gapSec  = ($hostNow - $tzEntry1HostTime).TotalSeconds
414	            if ($gapSec -gt $tzSleepThreshold) {
415	                # Host clock jumped too much — laptop probably slept between the two
416	                # observations. Reset so this write becomes the new entry-1.
417	                Write-Log ("TZ-check: host gap {0:N0}s since entry-1 — likely woke from sleep, resetting observation." -f $gapSec)
418	                $tzEntry1MTime    = $mtime
419	                $tzEntry1HostTime = $hostNow
420	            } else {
421	                Invoke-TimezoneCheck -LogLine $lastLine -HostNow $hostNow
422	                $tzCheckDone = $true
423	            }
424	        }
425	    }
426	
427	    Write-Log -Status ("running (log age {0}s)  -  {1}" -f $ageSec, $lastLine)
428	    Start-Sleep -Seconds $PollSeconds
429	}
430	
431	# -- Done ----------------------------------------------------------------------
432	
433	Write-Log ""
434	Write-Log "Orchestrator stopped."
435	
436	$stopReason = Get-StopReason
437	if ($stopReason) { Write-Log ("Stop reason   : {0}" -f $stopReason) }
438	
439	$report = Get-LatestReportName
440	if ($report)     { Write-Log ("Latest report : {0}" -f $report) }
441	
442	# Derive wake-up time from rate-limit state and schedule before suspend so the timer
443	# is armed even if sleep is interrupted.
444	if (-not $NoWake) {
445	    $rl = Get-RateLimitState
446	
447	    # Stale entries are not actionable but useful to surface for debugging
448	    foreach ($name in ($rl.Stale.Keys | Sort-Object)) {
449	        $resetAt = $rl.Stale[$name].ToLocalTime()
450	        Write-Log ("Rate-limit    : {0} -> stale (reset {1} already past, account usable)" -f `
451	                   $name, $resetAt.ToString("yyyy-MM-dd HH:mm:ss"))
452	    }
453	
454	    if ($rl.Active.Count -eq 0) {
455	        Write-Log "Wake-up       : skipped  -  no actively rate-limited accounts (none waiting in state.json)"
456	    } else {
457	        foreach ($name in ($rl.Active.Keys | Sort-Object)) {
458	            $resetAt = $rl.Active[$name].ToLocalTime()
459	            Write-Log ("Rate-limited  : {0} -> resets {1}" -f $name, $resetAt.ToString("yyyy-MM-dd HH:mm:ss"))
460	        }
461	
462	        $earliestLocal = $rl.Earliest
463	        $wakeAt        = $earliestLocal.AddMinutes(-$WakeBeforeResetMinutes)
464	        $now           = Get-Date
465	
466	        if ($wakeAt -le $now) {
467	            # earliest reset is so soon that subtracting the buffer puts wake in the past;
468	            # wake immediately (i.e. don't sleep at all) rather than missing the window.
469	            Write-Log ("Wake-up       : earliest reset is in {0:N0} sec  -  too close to sleep, skipping suspend" -f `
470	                       ($earliestLocal - $now).TotalSeconds)
471	            return
472	        }
473	
474	        $sleepMinutes = [int]([math]::Round(($wakeAt - $now).TotalMinutes))
475	        Write-Log ("Wake-up       : earliest reset {0} -> waking at {1} (sleeping ~{2} min)" -f `
476	                   $earliestLocal.ToString("yyyy-MM-dd HH:mm:ss"), `
477	                   $wakeAt.ToString("yyyy-MM-dd HH:mm:ss"), `
478	                   $sleepMinutes)
479	        Register-WakeTask -WakeAt $wakeAt
480	    }
481	}
482	
483	if ($DryRun) {
484	    Write-Log "DRY RUN  -  would suspend now. Exiting."
485	    return
486	}
487	
488	Write-Log "Suspending in 5s... (Ctrl+C to abort)"
489	Start-Sleep -Seconds 5
490	
491	Invoke-SystemSleep -UseHibernate:$Hibernate
492	
493	# Execution resumes here when the PC wakes up
494	Write-Log "Resumed from suspend."
495	
496	} # end if (-not $env:PESTER_TESTING)
```

---

# claude-autorun skill — FULL FILE (.claude/skills/claude-autorun/skill.md)

```markdown
---
name: claude-autorun
description: Start, stop, or check status of the automation orchestrator
tools: [Bash, Read]
model: inherit
---

You control the autonomous task execution orchestrator (`scripts/automation/orchestrate.py`).

Detect action from user message: `start` / `stop` / `status`.

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

4. Start log monitoring: schedule a cron job (every 15 min, recurring) with this prompt:
   > Read automation/MONITORING_CRITERIA.md, then read automation/orchestrate.log (tail ~200 lines). Apply the criteria from MONITORING_CRITERIA.md and report: (1) any CRITICAL or WARNING anomalies found, (2) current progress summary (sessions since last check, tasks completed). If CRITICAL unrecoverable errors are detected (crash/PID dead without clean stop, resume loop 3+ times, all accounts disabled, 5+ consecutive no-progress sessions, malformed question.md, same question repeated), stop the orchestrator immediately: run `touch automation/.stop-requested` and report "Orchestrator stop requested due to: [reason]". If the log contains "Stopped. Reason:", read the file `automation/.monitoring_cron_id` to get the cron job ID, then call CronDelete with that ID to cancel further checks.

   After CronCreate returns the job ID, immediately persist it:
   ```bash
   echo "<job-id>" > automation/.monitoring_cron_id
   ```

5. Confirm: "Orchestrator started (PID: XXXX). Log monitoring active every 15 min (cron ID: YYYY) — will auto-stop when orchestrator finishes. Use `/autorun status` to check progress or `/autorun stop` to stop after the current session."

## Action: stop

1. ```bash
   test -f automation/.stop-requested && echo "EXISTS" || echo "NOT_EXISTS"
   ```
2. If EXISTS → "Stop already requested — will stop after current session."
3. If NOT_EXISTS:
   ```bash
   touch automation/.stop-requested
   ```
   Confirm: "Stop signal sent. Orchestrator finishes current session, writes report, then exits."

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
   test -f automation/.stop-requested && echo "STOP_PENDING" || echo "NO_STOP"
   ```
2. Read the latest report file (if path found above).
3. Summarise:
   - Running or stopped (from PID check above)
   - Sessions completed in last run (from report header)
   - Pending feedback: list task IDs (from question.md paths), or "none"
   - Stop signal active: yes/no
```

---

# test_orchestrate.py — Import block and module structure (lines 1–80)

```python
  1	"""
  2	test_orchestrate.py — Test suite for scripts/automation/orchestrate.py
  3	
  4	~150 tests across 8 categories (A–H) following the architecture defined in:
  5	requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
  6	feat_session_orchestrator/tasks/2026-04-10_impl_implement-orchestrator-monitoring-improvements/
  7	plans_and_protocols/2026-04-10_02_plan_rewrite-architecture.md#6-test-architecture
  8	"""
  9	
 10	import argparse
 11	import json
 12	import os
 13	import subprocess
 14	import sys
 15	import tempfile
 16	import types
 17	from datetime import datetime, timedelta, timezone
 18	from unittest import mock
 19	from unittest.mock import MagicMock
 20	
 21	# Add scripts/automation to sys.path so we can import orchestrate without installation
 22	sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
 23	
 24	from orchestrate import (
 25	    OrchestratorDeps,
 26	    Orchestrator,
 27	    PersistentState,
 28	    RunData,
 29	    SessionRecord,
 30	    _find_in_progress_without_session_id,
 31	    _jaccard,
 32	    answer_is_empty,
 33	    check_and_update_question_fingerprint,
 34	    compute_question_fingerprint,
 35	    find_answered_feedback,
 36	    find_resumable_session,
 37	    get_unanswered_questions,
 38	    git_commit_best_effort,
 39	    load_state,
 40	    next_available_account,
 41	    parse_rate_limit_reset,
 42	    run_session_with_hung_detection,
 43	    save_state,
 44	    strip_hook_footer,
 45	    write_report,
 46	    write_health_summary,
 47	)
 48	
 49	
 50	# ---------------------------------------------------------------------------
 51	# Fixtures / helpers
 52	# ---------------------------------------------------------------------------
 53	
 54	def _fake_completed(returncode=0, stdout="", stderr=""):
 55	    """Create a fake subprocess.CompletedProcess."""
 56	    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)
 57	
 58	
 59	def _make_immediately_exiting_proc(returncode=0, stdout=""):
 60	    """Return a mock Popen-style object that appears to exit immediately on first poll."""
 61	    proc = MagicMock()
 62	    proc.poll.return_value = returncode  # non-None → process already exited
 63	    proc.communicate.return_value = (stdout, "")
 64	    proc.pid = 11111
 65	    return proc
 66	
 67	
 68	def make_deps(**overrides) -> OrchestratorDeps:
 69	    """Return OrchestratorDeps with safe no-op defaults. Override as needed."""
 70	    defaults = dict(
 71	        run_subprocess=lambda *a, **kw: _fake_completed(),
 72	        # Why: popen_subprocess default returns a process that "exits" immediately
 73	        # (poll() returns 0) so existing tests that don't care about hung-detection
 74	        # continue to work without modification. Tests that exercise hung-detection
 75	        # supply their own popen_subprocess via make_deps(popen_subprocess=...).
 76	        popen_subprocess=lambda *a, **kw: _make_immediately_exiting_proc(),
 77	        read_file=lambda p: "",
 78	        write_file=lambda p, c: None,
 79	        file_exists=lambda p: False,
 80	        list_dir=lambda p: [],
```

---

# test_orchestrate.py — TestLoadState and TestSaveState classes (lines 348–486)

```python
348	# ---------------------------------------------------------------------------
349	# Category B: State management (~15 tests)
350	# ---------------------------------------------------------------------------
351	
352	
353	class TestLoadState:
354	    def test_missing_file_returns_default(self):
355	        deps = make_deps(file_exists=lambda p: False)
356	        state = load_state("/fake/state.json", deps)
357	        assert isinstance(state, PersistentState)
358	        assert state.account_index == 0
359	        assert state.run_count == 0
360	        assert state.paused_tasks == []
361	        assert state.rate_limited_until == {}
362	        assert state.question_fingerprints == {}
363	
364	    def test_valid_json_loads_fields(self):
365	        data = {
366	            "account_index": 2,
367	            "run_count": 7,
368	            "start_time": "2026-01-01T00:00:00",
369	            "paused_tasks": ["TASK-1"],
370	            "rate_limited_until": {"web": "2026-01-01T01:00:00"},
371	            "question_fingerprints": {"TASK-1": {"words": ["hello"], "preview": "hello"}},
372	        }
373	        deps = make_deps(
374	            file_exists=lambda p: True,
375	            read_file=lambda p: json.dumps(data),
376	        )
377	        state = load_state("/fake/state.json", deps)
378	        assert state.account_index == 2
379	        assert state.run_count == 7
380	        assert state.paused_tasks == ["TASK-1"]
381	        assert state.rate_limited_until == {"web": "2026-01-01T01:00:00"}
382	        assert "TASK-1" in state.question_fingerprints
383	
384	    def test_missing_keys_filled_with_defaults(self):
385	        data = {"account_index": 1}  # missing all other keys
386	        deps = make_deps(
387	            file_exists=lambda p: True,
388	            read_file=lambda p: json.dumps(data),
389	        )
390	        state = load_state("/fake/state.json", deps)
391	        assert state.account_index == 1
392	        assert state.run_count == 0
393	        assert state.paused_tasks == []
394	
395	    def test_question_fingerprints_absent_defaults_to_empty_dict(self):
396	        data = {"account_index": 0, "run_count": 0}
397	        deps = make_deps(
398	            file_exists=lambda p: True,
399	            read_file=lambda p: json.dumps(data),
400	        )
401	        state = load_state("/fake/state.json", deps)
402	        assert state.question_fingerprints == {}
403	
404	    def test_corrupt_json_returns_default(self, capsys):
405	        deps = make_deps(
406	            file_exists=lambda p: True,
407	            read_file=lambda p: "NOT VALID JSON {{{",
408	        )
409	        state = load_state("/fake/state.json", deps)
410	        assert state.account_index == 0
411	        captured = capsys.readouterr()
412	        assert "WARNING" in captured.out
413	
414	    def test_start_time_preserved(self):
415	        data = {"start_time": "2026-03-15T08:00:00"}
416	        deps = make_deps(
417	            file_exists=lambda p: True,
418	            read_file=lambda p: json.dumps(data),
419	        )
420	        state = load_state("/fake/state.json", deps)
421	        assert state.start_time == "2026-03-15T08:00:00"
422	
423	
424	class TestSaveState:
425	    def test_writes_json_to_path(self, tmp_path):
426	        path = str(tmp_path / "state.json")
427	        deps = make_deps(
428	            makedirs=lambda p: os.makedirs(p, exist_ok=True),
429	            write_file=lambda p, c: open(p, "w").write(c),
430	        )
431	        state = PersistentState(account_index=3, run_count=5)
432	        save_state(path, state, deps)
433	        with open(path) as f:
434	            data = json.loads(f.read())
435	        assert data["account_index"] == 3
436	        assert data["run_count"] == 5
437	
438	    def test_atomic_write_uses_tmp_file(self):
439	        written_paths = []
440	
441	        def fake_write(p, c):
442	            written_paths.append(p)
443	
444	        deps = make_deps(
445	            write_file=fake_write,
446	            makedirs=lambda p: None,
447	        )
448	        # We call save_state; os.replace will fail since paths are fake,
449	        # but we can verify the tmp path was attempted
450	        import unittest.mock as mock
451	        with mock.patch("os.replace"):
452	            save_state("/fake/state.json", PersistentState(), deps)
453	        assert any(".tmp" in p for p in written_paths)
454	
455	    def test_type_error_logs_warning_and_does_not_crash(self, capsys):
456	        # Inject a set (not JSON-serialisable) via question_fingerprints
457	        import unittest.mock as mock
458	        import dataclasses
459	
460	        state = PersistentState()
461	        # Directly put a set to trigger TypeError in json.dumps
462	        state.question_fingerprints = {"bad": {"words": {1, 2, 3}}}  # set not serialisable
463	
464	        written = []
465	
466	        def fake_write(p, c):
467	            written.append(c)
468	
469	        deps = make_deps(write_file=fake_write, makedirs=lambda p: None)
470	        # json.dumps will raise TypeError for a set
471	        with mock.patch("os.replace"):
472	            save_state("/fake/state.json", state, deps)
473	        captured = capsys.readouterr()
474	        assert "WARNING" in captured.out
475	        # Should not crash; written should be empty (write never called after TypeError)
476	        assert written == []
477	
478	    def test_os_error_logs_warning_and_does_not_crash(self, capsys):
479	        def raise_os_error(p, c):
480	            raise OSError("disk full")
481	
482	        deps = make_deps(write_file=raise_os_error, makedirs=lambda p: None)
483	        save_state("/fake/state.json", PersistentState(), deps)
484	        captured = capsys.readouterr()
485	        assert "WARNING" in captured.out
486	```

---

# test_orchestrate.py — Last 30 lines (lines 2963–2993)

```python
2963	    def test_heartbeat_not_emitted_before_15_minutes(self, capsys):
2964	        """No heartbeat is printed when less than 15 minutes have elapsed."""
2965	        import time as time_module
2966	
2967	        proc = _make_mock_proc(poll_returns=[None, 0])
2968	
2969	        deps = make_deps(
2970	            popen_subprocess=lambda *a, **kw: proc,
2971	            run_subprocess=lambda *a, **kw: _fake_completed(returncode=0, stdout=""),
2972	            sleep=lambda s: None,
2973	            get_mtime=lambda p: None,
2974	        )
2975	        stop_flag = {"requested": False}
2976	
2977	        # 899 seconds — just under the 900 s (15 min) threshold
2978	        monotonic_values = iter([0, 899, 899])
2979	        with mock.patch.object(time_module, "monotonic", side_effect=lambda: next(monotonic_values)):
2980	        	result = run_session_with_hung_detection(
2981	                cmd=["claude", "-p", "test"],
2982	                env={},
2983	                session_uuid="ffffffff-0000-0000-0000-000000000000",
2984	                hung_check_interval=0,
2985	                hung_timeout_secs=99999,
2986	                session_timeout_secs=99999,
2987	                stop_flag=stop_flag,
2988	                deps=deps,
2989	            )
2990	
2991	        assert result.returncode == 0
2992	        out = capsys.readouterr().out
2993	        assert "Still waiting" not in out
```

---

# automation/state.json — Current content

```json
{
  "account_index": 0,
  "run_count": 86,
  "start_time": "2026-04-29T21:19:36.107854",
  "paused_tasks": [],
  "rate_limited_until": {
    "gmail": "2026-04-29T23:05:00+00:00",
    "web": "2026-04-30T19:05:00+00:00",
    "gmail2": "2026-04-29T22:35:00+00:00"
  },
  "question_fingerprints": {
    "TASK-FUNC-007-14": {
      "words": ["sec08","5","notification","in_progress","mark","complete","16","pending","are","action","status","protocol","100","followup","tasks","7","reqfunc00703","written","blocked","no","a","completing","and","once","via","field","content","all","core","what","absent","write","as","matrix","still","ac0708101112","should","option","then","not_covered","ran","awaiting","finish","remains","ac0813","taskfunc00203","reqfunc00702","only","now","done","20260410","label","keep","gaps","before","reqfunc017","deliverables","body","of","4","i","needed","confirm","foundation","gap","it","for","taskfunc00714","is","task","those","1","3","stubs","pass","items","2","delivery","requverifyflowcoverage","partial","reqfunc002","the","final","report","can","question","was","reqfunc00701","bundles","updated","until","on","remaining","system","means","f2","verification","assessed","tracked","10","taskfunc01702","needs","reqfunc014","closure","identified","closes","reqfunc00706","two","reqfunc00707","taskfunc01405","added","f1","open","coverage","remediation","run","by","covered","b","to"],
      "preview": "pending question what was done taskfunc00714 ran requverifyflowcoverage for the core protocol delivery notification system bundles as of 20260410 the coverage report is complete and the matrix is updated covered no action needed gap 1 reqfunc00701 100 gap 3 reqfunc00702 100 gap 5 reqfunc017 7 100 ad"
    },
    "TASK-PROC-027-01": {
      "words": ["spontaneouscapture","b","misses","that","additional","capturespontaneous","4","only","batch","write","emotional","started","if","3","selfuser","angle","completed","pure","in","task","therapist","scen00802","as","overall","she","it","exists","any","gap","massively","generate","workingmemory","never","the","client","tool","option","uses","more","like","current","a","first","presents","add","capture_data_spontaneously","variant","record","2","discovers","new","failure","permanence","tries","1520","notes","was","scenarios","pending","total","sophies","next","mode","86","out","asis","is","welcome","entirely","moment","core","again","event","vs","this","each","can","exceeding","done","reach","blocking","from","exist","opens","window","rather","profile","object","should","context","sophie_structure_seeker","present","sight","mechanic","possibly","files","scenario_indexmd","for","continue","category","on","jana","adhd","scenario","or","halfdone","with","than","3second","forgot","sophie","morning","generation","has","focus","an","capture_data_spontaneously__harm_reduction","goes","and","but","question","please","to","your","days","of","mark","capture","be","created","6","then","review","far","davids","something","stopped","streakbreaking","what","separate","overwrite","differs","complete","20260419","draft","shameaftergap","vastly","state","not","doesnt","idea","existing","none","one","choice","happen","app","shamedriven","status","objective","exceeded","would","taskproc02701","tracker","are","forgetting","missing","titled","20260207","answermd","her","capture_data_spontaneously__black_book","appforgetting","tracked","target","spontaneous","ac1","have"],
      "preview": "pending question task context taskproc02701 continue scenario generation batch 4 has status pending never started it was created on 20260207 with this objective complete batch 4 write capturespontaneous scenarios for jana and sophie add additional scenarios to reach 1520 total current state as of 20"
    },
    "TASK-PROC-042-09": {
      "words": ["the","task","phase","claudeskills","3","do","then","add","all","context","including","yet","others","skillfile","mode","been","for","pick","claudeskillstaskcreatecodeskillmd","skills","replace","up","please","options","editing","are","and","samepackage","reference","where","editwrite","a","directory","blocked","what","has","entry","run","plan","resume","5c","goalmd","with","325","logic","step","5a","note","code","how","requderivefromflowskillmd","but","ready","2","at","session","execute","from","claudeskillsrequderivefromflowskillmd","propose_afterpy","section","table","write","allow","call","update","portably","acceptance","taskproc04209","planned","criteria","updateconfig","additive","execution","wire","grant","requested","manually","nonbreaking","via","it","claudeskillstaskcreateskillmd","script","taskcreate","files","question","writing","steps","because","into","was","skill","same","batchagent","needs","handles","creation","no","complete","stopped","implements","skip","manual","requirements_tasksprocessai_rulesrequirements_managementtask_orderingtasks20260422_impl_wireproposeafterintotaskcreateskillsplans_and_protocols20260423_01_plan_proposeafterwiringmd","changes","invocation","already","further","decisions","that","autoaccept","pending","saved","not","granted","proposals","rule","instructions","in","heuristics","taskcreatecodeskillmd","is","between","claude","happen","permission","will","this","requires","require","three","1","to","just","invoke","taskcreateskillmd","automatically","edit","automated","42"],
      "preview": "pending question context task taskproc04209 wire propose_afterpy into taskcreate skills is ready to execute the plan is complete and saved at requirements_tasksprocessai_rulesrequirements_managementtask_orderingtasks20260422_impl_wireproposeafterintotaskcreateskillsplans_and_protocols20260423_01_pla"
    },
    "TASK-PROC-035-11": {
      "words": ["chunk","your","configurable","5","m","size","domaindata","create","bidirectional","task","on","business","has","defines","layers","transfer","architecturedriven","then","option","ensures","question","priority_within_source","that","ordering","by","with","order","approved","databeam","depend","follows","running","uses","domainbeforepresentation","pending","ranking","impl","automationpending_feedbacktaskproc03511answermd","verify","phase","covers","choice","picked","null","plans","orchestration","chain","999","ac06","packages","existing","2","implementation","model","ac07","creation","layering","reverse","first","notes","ac141516","6","should","context","zeroparameter","says","discovery","was","following","edit","new","rationale","release_backlog","reflects","please","which","within","dependency","execution","task_creation_planmd","4","release","qr","1","before","receive","however","backlog","them","already","adaptive","next","0","any","mode","tasks","covered","validation","no","a","3","effort","b","in","data","crosslayer","conflict","missing","timebased","pairing","taskcreatecode","settings","detection","priority","reqfunc007","the","001","send","needed","presentation","as","scanner","domain","exist","does","s","pipeline","or","plan","not","follow","sequence","and","layer","release_backlogmd","for"],
      "preview": "pending question context running taskcreatecode in zeroparameter mode for release 001 the approved task creation plan task_creation_planmd defines the following execution order for 001 1 transfer data model domain data crosslayer 2 transfer pairing domain data 3 qr transfer receive domain presentati"
    }
  }
}
```
