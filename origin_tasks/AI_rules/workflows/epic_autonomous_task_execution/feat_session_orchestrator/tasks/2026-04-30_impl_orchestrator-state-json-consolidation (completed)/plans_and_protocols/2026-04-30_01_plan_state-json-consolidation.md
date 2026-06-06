# Opus Plan — Orchestrator State JSON Consolidation

**Task**: TASK-PROC-041-01-09
**Author**: Opus
**Date**: 2026-04-30

## Objective

Make `automation/state.json` the single source of truth for all orchestrator runtime state. Remove the `automation/.stop-requested` sentinel file entirely (replaced by `state.json["stop_requested"]`). Add observability fields (`is_running`, `active_session`, `rate_limit_reached`, `next_wake_time`, `timezone`) so external tools — primarily the Windows `sleep_when_autorun_done.ps1` script — can react immediately to orchestrator state changes without polling sentinel files or log mtimes.

## Analysis Summary

### Key findings from gathered context

1. **`PersistentState` dataclass** (orchestrate.py:303–319) has 6 fields, all snake_case, serialised via `dataclasses.asdict` to JSON. Existing JSON keys are all snake_case (e.g. `account_index`, `run_count`, `rate_limited_until`).

2. **Stop signalling currently uses a sentinel file** (`automation/.stop-requested`) checked at:
   - `_check_stop_conditions` line 1553 (main loop)
   - finally block line 2422 (cleanup)
   - PS1 polling display line 400

3. **`get_now_local`** defaults to `datetime.now` (NAIVE — no tzinfo). When `state.start_time = get_now_local().isoformat()` is written, the resulting ISO string has no offset (`"2026-04-29T21:19:36.107854"`). This is a latent bug for our purposes — the PS1 script uses `RoundtripKind` parsing which works fine with offset-bearing strings but treats naive strings as `Unspecified` Kind; `.ToLocalTime()` on `Unspecified` mis-treats it as UTC. We must fix this.

4. **`rate_limited_until`** is currently stored as UTC ISO strings with `+00:00` offset. PS1 parses with `RoundtripKind` then calls `.ToLocalTime()`. As long as we keep an offset (any offset — UTC or local), this stays compatible.

5. **`rate_limit_sleep`** is a module-level function called at:
   - line 1820 (resume path, all accounts exhausted)
   - line 2014 (normal session path, all accounts rate-limited)
   Both are inside Orchestrator methods (have `self`), so we can update `self.state` and call `save_state` around the call.

6. **`run_normal_session` / `run_resume_session`** are module-level functions. Set `state.active_session` at the call sites (which are inside Orchestrator methods):
   - `run_normal_session` called from line 2059 (`run_normal_session_step` method)
   - `run_resume_session` called from lines 1659, 1843

7. **Test infrastructure**: `make_deps()` helper supports dependency injection. Existing `TestLoadState` and `TestSaveState` (lines 348–486) use `file_exists`/`read_file`/`write_file` overrides — easily extendable.

8. **PS1 testing**: Pester is the standard PowerShell test framework but the script is `if (-not $env:PESTER_TESTING)`-guarded already. Pester is not installed in this Linux dev container; the PS1 script runs on the Windows host. **Decision**: skip PS1 unit tests; rely on code review + user's live `-DryRun` verification.

### Key decisions (USER REVIEW NEEDED)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| D1 | JSON key naming for new fields | **snake_case** (`is_running`, `active_session`, `stop_requested`, `rate_limit_reached`, `next_wake_time`, `timezone`) | Consistency with existing keys (`account_index`, `run_count`, `rate_limited_until`). User's examples (`isRunning`) were illustrative, not prescriptive. |
| D2 | Timestamp format | Aware local datetime with offset (e.g. `"2026-04-30T21:19:36.107854+02:00"`) | PS1 `RoundtripKind` parser handles offsets correctly; preserves wall-clock readability while remaining round-trip safe. |
| D3 | Fix `get_now_local` to return aware datetime | Yes — change default to `lambda: datetime.now().astimezone()` | Required for D2; existing call sites (`.strftime`, `.isoformat`, `.total_seconds`) all work identically on aware datetimes. |
| D4 | Migration of existing `start_time` (no offset) | Just rewrite on next save — no migration script | `start_time` is reset to current time at every orchestrator startup (line 2373), so the stale naive value is overwritten on first run. |
| D5 | `rate_limited_until` timezone | Keep storing with whatever offset `astimezone()` produces (local) — switch from `+00:00` to local | PS1 uses `.ToLocalTime()` which is idempotent on local-time inputs. |
| D6 | `stop_requested` re-read strategy | On each `_check_stop_conditions` call, re-read `state.json` from disk (small file, cheap) | An external tool (the skill, the user) updates state.json out-of-band; the orchestrator can't see those writes via in-memory `self.state`. |
| D7 | PS1 unit tests | **Write** Pester tests in `scripts/sleep_when_autorun_done.Tests.ps1` — user must run them manually on the Windows host | Pester runs on Windows; dev container is Linux. Tests are written and committed; user validates them in situ. |
| D8 | `.automated_mode` sentinel | **Retain** | Used by `claude-autorun status` for PID-based liveness check. Not in scope of this task. |

---

## Execution Plan

### Phase 1: requ-explore — author AC-34..AC-38

**Agent**: spawned via `requ-explore` skill (per user feedback: never edit requirements.md directly).

**Input**: this plan file. The agent should propose AC-34..AC-38 to the existing `feat_session_orchestrator/requirements.md` (REQ-PROC-041-01) using the AC text below.

**AC text to author** (verbatim):

```
- **AC-34**: `state.json` exposes runtime observability fields maintained by the orchestrator: `is_running` (bool, `true` at startup / `false` in `finally`), `active_session` (string UUID of the session currently being executed, `null` when idle), `stop_requested` (bool, written `false` at startup; mirrors whether a stop has been signalled — set to `true` on SIGTERM, SIGINT, or external write), `rate_limit_reached` (bool, `true` only while sleeping in `rate_limit_sleep` for a rate-limit reset), `next_wake_time` (ISO 8601 string with timezone offset of the planned resume time when `rate_limit_reached` is `true`, `null` otherwise).
- **AC-35**: All datetime values written to `state.json` by the orchestrator are aware ISO 8601 strings carrying a timezone offset (never naive). A top-level `timezone` field is written at startup and on every state save with the IANA name of the OS local timezone (e.g. `"Europe/Berlin"`, `"UTC"`). The orchestrator's `get_now_local` dependency returns aware local-timezone datetimes by default.
- **AC-36**: `scripts/sleep_when_autorun_done.ps1` uses `state.json["is_running"]` as the primary stop-detection signal. When `is_running` is absent (older orchestrator) or `state.json` is unreadable, the script falls back to the existing `.automated_mode` sentinel + `orchestrate.log` mtime heuristic. The `LogStaleMinutes` parameter is retained for the fallback path.
- **AC-37**: When `state.json["rate_limit_reached"]` is `true`, `sleep_when_autorun_done.ps1` treats the orchestrator as "paused but will resume" and proceeds to suspend the PC immediately, scheduling the wake task from `state.json["next_wake_time"]` minus `WakeBeforeResetMinutes`. It does not wait for `is_running` to become `false` first.
- **AC-38**: Stop signalling is consolidated into `state.json["stop_requested"]`. The orchestrator no longer creates, reads, or unlinks the `automation/.stop-requested` file. The `claude-autorun stop` action writes `stop_requested: true` to `state.json` (preserving all other fields) instead of touching a sentinel file. The `claude-autorun status` action reads `stop_requested` from `state.json`.
```

**Success check**: requirements.md frontmatter `trackable_items.acceptance_criteria` lists AC-34 through AC-38; AC body text is appended below AC-33.

---

### Phase 2: Two parallel implementation agents

#### Phase 2a: Implementation agent A — `orchestrate.py` + tests

**Files to modify**:
- `scripts/automation/orchestrate.py`
- `scripts/automation/tests/test_orchestrate.py`

**Step 1: Add timezone helper** (insert near other helpers, e.g. after `rate_limit_sleep` ~line 124):

```python
def _get_local_timezone_name() -> str:
    """Return the IANA name of the OS local timezone, with safe fallbacks.

    Why: state.json stores a `timezone` field so external tools can interpret
    timestamps without a separate tz lookup. zoneinfo.ZoneInfo (Python 3.9+)
    exposes `.key` on aware datetimes whose tzinfo was constructed from the
    system's localtime database. Fallback chain: TZ env var → time.tzname.
    """
    try:
        tz = datetime.now().astimezone().tzinfo
        if tz is not None and hasattr(tz, "key"):
            return tz.key
    except Exception:
        pass
    tz_env = os.environ.get("TZ", "")
    if tz_env:
        return tz_env
    try:
        import time as _time
        if _time.daylight and _time.tzname[1]:
            return _time.tzname[1]
        return _time.tzname[0] or "UTC"
    except Exception:
        return "UTC"
```

**Step 2: Update `PersistentState`** (orchestrate.py:303–319):

```python
@dataclass
class PersistentState:
    """State that survives across orchestrator restarts (written to state.json).

    Why: splitting persistent state (survives restarts) from in-memory run accumulators
    (RunData) makes it clear what is serialised to disk and prevents accidentally
    persisting transient data like disabled_accounts (which should reset each run).

    Observability fields (is_running, active_session, stop_requested,
    rate_limit_reached, next_wake_time, timezone) let external tools — notably
    sleep_when_autorun_done.ps1 — react to orchestrator state without polling
    sentinel files or log mtimes. See AC-34..AC-38.
    """
    account_index: int = 0
    run_count: int = 0
    start_time: "str | None" = None        # ISO string with offset
    paused_tasks: list = field(default_factory=list)
    rate_limited_until: dict = field(default_factory=dict)
    question_fingerprints: dict = field(default_factory=dict)
    # --- Observability fields (AC-34..AC-38) ---
    is_running: bool = False
    active_session: "str | None" = None
    stop_requested: bool = False
    rate_limit_reached: bool = False
    next_wake_time: "str | None" = None
    timezone: "str | None" = None
```

**Step 3: Update `load_state()`** (orchestrate.py:322–338) — extend `data.get(...)` calls for the 6 new fields:

```python
def load_state(path: str, deps: "OrchestratorDeps") -> PersistentState:
    """Load state.json; merge missing keys with defaults. Start fresh on error."""
    if deps.file_exists(path):
        try:
            raw = deps.read_file(path)
            data = json.loads(raw)
            return PersistentState(
                account_index=data.get("account_index", 0),
                run_count=data.get("run_count", 0),
                start_time=data.get("start_time", None),
                paused_tasks=data.get("paused_tasks", []),
                rate_limited_until=data.get("rate_limited_until", {}),
                question_fingerprints=data.get("question_fingerprints", {}),
                is_running=data.get("is_running", False),
                active_session=data.get("active_session", None),
                stop_requested=data.get("stop_requested", False),
                rate_limit_reached=data.get("rate_limit_reached", False),
                next_wake_time=data.get("next_wake_time", None),
                timezone=data.get("timezone", None),
            )
        except (json.JSONDecodeError, OSError) as e:
            print(f"[orchestrator {_ts()}] WARNING: state.json corrupt or unreadable ({e}), starting fresh")
    return PersistentState()
```

**Step 4: Update `save_state()`** (orchestrate.py:341–356) — set `timezone` on every save:

```python
def save_state(path: str, state: PersistentState, deps: "OrchestratorDeps") -> None:
    """Atomic write via tmp + os.replace to avoid partial writes on crash.

    Why: state.timezone is refreshed on every save so external readers always
    see the timezone that produced the timestamps in this file (matters if the
    container TZ changes between launches).
    """
    tmp = path + ".tmp"
    try:
        # Refresh timezone label on every save so it always reflects current OS tz
        state.timezone = _get_local_timezone_name()
        deps.makedirs(os.path.dirname(path))
        data = dataclasses.asdict(state)
        content = json.dumps(data, indent=2)
        deps.write_file(tmp, content)
        os.replace(tmp, path)
    except TypeError as e:
        print(f"[orchestrator {_ts()}] WARNING: state contains non-serialisable value ({e}), not saving")
    except OSError as e:
        print(f"[orchestrator {_ts()}] WARNING: could not save state ({e})")
```

**Step 5: Fix `get_now_local` default to return aware datetime** (orchestrate.py:2340):

```python
# Before:
get_now_local=datetime.now,
# After:
get_now_local=lambda: datetime.now().astimezone(),
```

**Step 6: Add `_read_external_stop_request` helper method on Orchestrator class** (insert near `_check_stop_conditions` at line 1543):

```python
def _read_external_stop_request(self) -> bool:
    """Re-read state.json[stop_requested] from disk without disturbing in-memory state.

    Why: an external process (claude-autorun stop, the user's editor) may set
    stop_requested=true in state.json. We must observe that write — but we
    cannot just trust self.state because self.state is our own write cache.
    Cheap (small file).
    """
    try:
        if not self.deps.file_exists(STATE_PATH):
            return False
        raw = self.deps.read_file(STATE_PATH)
        data = json.loads(raw)
        return bool(data.get("stop_requested", False))
    except (json.JSONDecodeError, OSError):
        return False
```

**Step 7: Replace sentinel check in `_check_stop_conditions`** (orchestrate.py:1553):

```python
# Before:
if self.deps.file_exists(SENTINEL_STOP):
    return True, "manual"
# After:
if self._read_external_stop_request():
    # Mirror to in-memory so subsequent checks short-circuit on stop_flag
    self.state.stop_requested = True
    return True, "manual"
```

Also update SIGTERM/SIGINT handler at line 2275–2277 to set `state.stop_requested` — but only if we have access to state. Since `setup_signals` is module-level, the cleanest approach is to leave the existing `stop_flag["requested"] = True` and additionally have `_check_stop_conditions` propagate to `state.stop_requested` whenever it returns True (so save_state on next iteration reflects it). Add inside `_check_stop_conditions` at the start:

```python
def _check_stop_conditions(self, args, stop_flag, stop_at, sessions_launched):
    if stop_flag["requested"]:
        self.state.stop_requested = True   # NEW: mirror to persistent state
        return True, "manual"
    ...
```

**Step 8: Initialise observability fields at startup** (orchestrate.py:2365–2377):

```python
    # Create sentinel: marks this process as running in automated mode
    deps.makedirs(AUTOMATION_DIR)
    try:
        deps.write_file(SENTINEL_AUTOMATED, str(deps.getpid()))
    except OSError as e:
        print(f"[orchestrator {_ts()}] WARNING: could not create .automated_mode sentinel ({e})")

    # Always reset start_time on each new launch so state.json reflects the current run
    start_time = deps.get_now_local()
    state.start_time = start_time.isoformat()
    # NEW: initialise observability fields (AC-34, AC-38)
    state.is_running = True
    state.active_session = None
    state.stop_requested = False           # clear any stale stop request from prior run
    state.rate_limit_reached = False
    state.next_wake_time = None
    save_state(STATE_PATH, state, deps)    # also writes timezone via save_state internals

    run_data = RunData(start_time=start_time)
```

**Step 9: Clear observability fields in `finally` block** (orchestrate.py:2400–2423):

Replace the `unlink_if_exists(SENTINEL_STOP)` line and update save_state context. Replace lines 2420–2423:

```python
        # Clean up sentinels (best-effort)
        unlink_if_exists(SENTINEL_AUTOMATED)
        # SENTINEL_STOP no longer used (AC-38) — replaced by state.stop_requested

        # NEW: mark not-running and clear active_session for external observers
        state.is_running = False
        state.active_session = None
        state.rate_limit_reached = False
        state.next_wake_time = None
        save_state(STATE_PATH, state, deps)
        print(f"[orchestrator {_ts()}] Stopped. Reason: {stop_reason}")
```

**Step 10: Set `active_session` around session calls**:

Three call sites — wrap each with set/clear:

(a) Resume session at line 1659 (inside Orchestrator method, has `self.state`):
```python
# Before run_resume_session call, around line 1659:
self.state.active_session = session_record["session_id"]   # use the actual UUID being launched
save_state(STATE_PATH, self.state, self.deps)
result = run_resume_session(...)
self.state.active_session = None
save_state(STATE_PATH, self.state, self.deps)
```
> **Note for impl agent**: read lines 1620–1680 to find the exact UUID variable in scope. The pattern is `session_record["session_id"]` or similar. Use whatever is currently used to populate the run record.

(b) Resume session at line 1843 — same pattern.

(c) Normal session at line 2059 (`run_normal_session_step` method):
```python
# Around line 2055 (just before result = run_normal_session(...)):
self.state.active_session = session_uuid       # use the pre-assigned UUID
save_state(STATE_PATH, self.state, self.deps)
result = run_normal_session(...)
self.state.active_session = None
save_state(STATE_PATH, self.state, self.deps)
```
> **Note for impl agent**: read lines 2020–2070 to confirm the variable name holding the UUID (likely `session_uuid` based on the cmd construction at line 562).

**Step 11: Set `rate_limit_reached` + `next_wake_time` around `rate_limit_sleep`**:

Two call sites:

(a) Line 1820 (resume path):
```python
# Before:
rate_limit_sleep(wait_secs, stop_flag, reset_dt=wait_until)
# After:
self.state.rate_limit_reached = True
self.state.next_wake_time = wait_until.astimezone().isoformat()
save_state(STATE_PATH, self.state, self.deps)
rate_limit_sleep(wait_secs, stop_flag, reset_dt=wait_until)
self.state.rate_limit_reached = False
self.state.next_wake_time = None
save_state(STATE_PATH, self.state, self.deps)
```

(b) Line 2014 (normal session path) — same pattern.

> **Important**: `wait_until` is a UTC datetime (built via `get_now_utc()`). `.astimezone()` (no arg) converts it to local-tz with offset preserved.

**Step 12: Remove `SENTINEL_STOP` constant** (orchestrate.py:54):

```python
# Before:
SENTINEL_STOP = os.path.join(AUTOMATION_DIR, ".stop-requested")
# After: delete this line entirely
```

After deletion, do a `grep -n SENTINEL_STOP scripts/automation/orchestrate.py` — must return 0 hits.

**Step 13: test_orchestrate.py — update existing tests**:

In `TestLoadState` (line 353):
- `test_missing_file_returns_default` — extend assertions:
  ```python
  assert state.is_running is False
  assert state.active_session is None
  assert state.stop_requested is False
  assert state.rate_limit_reached is False
  assert state.next_wake_time is None
  assert state.timezone is None
  ```
- Add `test_observability_fields_loaded_from_json`:
  ```python
  def test_observability_fields_loaded_from_json(self):
      data = {
          "is_running": True,
          "active_session": "abc-123",
          "stop_requested": True,
          "rate_limit_reached": True,
          "next_wake_time": "2026-04-30T22:00:00+02:00",
          "timezone": "Europe/Berlin",
      }
      deps = make_deps(file_exists=lambda p: True, read_file=lambda p: json.dumps(data))
      state = load_state("/fake/state.json", deps)
      assert state.is_running is True
      assert state.active_session == "abc-123"
      assert state.stop_requested is True
      assert state.rate_limit_reached is True
      assert state.next_wake_time == "2026-04-30T22:00:00+02:00"
      assert state.timezone == "Europe/Berlin"
  ```

In `TestSaveState` (line 424):
- Add `test_writes_observability_fields`:
  ```python
  def test_writes_observability_fields(self, tmp_path):
      path = str(tmp_path / "state.json")
      deps = make_deps(
          makedirs=lambda p: os.makedirs(p, exist_ok=True),
          write_file=lambda p, c: open(p, "w").write(c),
      )
      state = PersistentState(
          is_running=True,
          active_session="uuid-1",
          stop_requested=False,
          rate_limit_reached=True,
          next_wake_time="2026-04-30T22:00:00+02:00",
      )
      save_state(path, state, deps)
      with open(path) as f:
          data = json.loads(f.read())
      assert data["is_running"] is True
      assert data["active_session"] == "uuid-1"
      assert data["rate_limit_reached"] is True
      assert data["next_wake_time"] == "2026-04-30T22:00:00+02:00"
  ```
- Add `test_save_state_writes_timezone_field`:
  ```python
  def test_save_state_writes_timezone_field(self, tmp_path, monkeypatch):
      path = str(tmp_path / "state.json")
      monkeypatch.setattr("orchestrate._get_local_timezone_name", lambda: "Europe/Berlin")
      deps = make_deps(
          makedirs=lambda p: os.makedirs(p, exist_ok=True),
          write_file=lambda p, c: open(p, "w").write(c),
      )
      save_state(path, PersistentState(), deps)
      data = json.loads(open(path).read())
      assert data["timezone"] == "Europe/Berlin"
  ```

**Step 14: test_orchestrate.py — add new test classes**:

```python
class TestExternalStopRequest:
    """AC-38: stop_requested in state.json replaces the .stop-requested sentinel."""

    def test_check_stop_conditions_reads_state_json(self, tmp_path):
        """When state.json[stop_requested]=true, _check_stop_conditions returns (True, 'manual')."""
        # Write a state.json with stop_requested=true
        state_content = json.dumps({"stop_requested": True})

        deps = make_deps(
            file_exists=lambda p: p.endswith("state.json"),
            read_file=lambda p: state_content,
        )
        # Build a minimal Orchestrator instance — adapt to whatever constructor signature exists
        orch = Orchestrator(deps=deps, state=PersistentState())
        stop_flag = {"requested": False}
        args = argparse.Namespace(max_tasks=None)
        should_stop, reason = orch._check_stop_conditions(args, stop_flag, None, 0)
        assert should_stop is True
        assert reason == "manual"

    def test_sentinel_stop_path_no_longer_referenced(self):
        """SENTINEL_STOP constant is removed from the module."""
        import orchestrate
        assert not hasattr(orchestrate, "SENTINEL_STOP"), "SENTINEL_STOP should be removed (AC-38)"


class TestActiveSessionLifecycle:
    """AC-34: active_session is set before a session launches, cleared after."""

    def test_active_session_set_during_normal_session(self):
        """Verify the call sequence sets active_session before run_normal_session and clears after."""
        # Inspect orchestrate.py via AST or by patching save_state to record calls.
        # Implementation: spy on save_state and run_normal_session; assert ordering of state.active_session writes.
        # See test pattern in TestSaveState.test_atomic_write_uses_tmp_file for spy helper style.
        ...   # implementation agent: write a behavioural test using mocks


class TestRateLimitObservability:
    """AC-34: rate_limit_reached + next_wake_time around rate_limit_sleep."""

    def test_rate_limit_flags_set_before_sleep_cleared_after(self):
        """rate_limit_reached=true is saved before rate_limit_sleep, false after."""
        ...   # implementation agent: build using mocks of rate_limit_sleep + save_state


class TestTimezoneField:
    """AC-35: timezone field is populated."""

    def test_get_local_timezone_name_returns_string(self):
        from orchestrate import _get_local_timezone_name
        tz = _get_local_timezone_name()
        assert isinstance(tz, str)
        assert len(tz) > 0
```

> **Note for impl agent**: For tests marked `...`, write actual implementations using the existing mock patterns. Use `make_deps` overrides + `mock.patch` on `save_state` (via `with mock.patch("orchestrate.save_state") as ms`) to record call ordering. The exact body depends on what's idiomatic in the existing test file — read TestSaveState carefully and follow the same style.

**Success criteria for Phase 2a**:
- `python3 -m pytest scripts/automation/tests/test_orchestrate.py -x` passes (zero failures, zero errors)
- `grep -n "SENTINEL_STOP\|.stop-requested" scripts/automation/orchestrate.py` returns 0 hits
- New state.json after a manual run contains all 6 new fields with correct types

#### Phase 2b: Implementation agent B — `sleep_when_autorun_done.ps1`

**File**: `scripts/sleep_when_autorun_done.ps1`

**Step 1: Remove unused `$stopRequestPath` variable** (line 119):

```powershell
# Before:
$sentinelPath    = Join-Path $automationDir ".automated_mode"
$stopRequestPath = Join-Path $automationDir ".stop-requested"
$orchestrateLog  = Join-Path $automationDir "orchestrate.log"
# After:
$sentinelPath    = Join-Path $automationDir ".automated_mode"
$orchestrateLog  = Join-Path $automationDir "orchestrate.log"
```

(Then remove the line 400 reference: `if ((Test-Path -LiteralPath $stopRequestPath) -and -not $stopRequestedAnnounced)` — replace with state.json check, see Step 4.)

**Step 2: Add `Get-OrchestratorState` helper** (after `Get-RateLimitState`, ~line 279):

```powershell
# Why: state.json is the single source of truth (AC-34..AC-38). This helper
# returns a hashtable with the fields needed for stop-detection and rate-limit-aware
# sleep, with $null markers when state.json is unreadable so callers can fall back.
function Get-OrchestratorState {
    param([string]$Path = $statePath)
    $defaultMissing = @{
        Available        = $false
        IsRunning        = $null
        StopRequested    = $null
        RateLimitReached = $null
        NextWakeTime     = $null
        ActiveSession    = $null
    }
    if (-not (Test-Path -LiteralPath $Path)) { return $defaultMissing }
    try {
        $json = Get-Content -LiteralPath $Path -Raw -ErrorAction Stop | ConvertFrom-Json
    } catch {
        Write-Log "WARNING: state.json could not be parsed: $($_.Exception.Message)"
        return $defaultMissing
    }

    function _getProp($obj, $name) {
        if ($obj.PSObject.Properties[$name]) { return $obj.$name }
        return $null
    }

    $nextWakeRaw = _getProp $json 'next_wake_time'
    $nextWake = $null
    if ($nextWakeRaw) {
        try {
            $nextWake = ([datetime]::Parse(
                [string]$nextWakeRaw,
                [System.Globalization.CultureInfo]::InvariantCulture,
                [System.Globalization.DateTimeStyles]::RoundtripKind
            )).ToLocalTime()
        } catch {
            Write-Log "WARNING: next_wake_time not parseable: $nextWakeRaw"
        }
    }

    return @{
        Available        = $true
        IsRunning        = _getProp $json 'is_running'
        StopRequested    = _getProp $json 'stop_requested'
        RateLimitReached = _getProp $json 'rate_limit_reached'
        NextWakeTime     = $nextWake
        ActiveSession    = _getProp $json 'active_session'
    }
}
```

**Step 3: Update `Test-OrchestratorActive`** (lines 156–160):

```powershell
# Why: state.json["is_running"] is the authoritative signal (AC-36). The sentinel
# + log-mtime fallback is retained for older orchestrators that don't yet write
# is_running, and for cases where state.json itself is unreadable.
function Test-OrchestratorActive {
    $st = Get-OrchestratorState
    if ($st.Available -and $null -ne $st.IsRunning) {
        return [bool]$st.IsRunning
    }
    # Fallback path
    if (-not (Test-SentinelPresent)) { return $false }
    return (Test-LogActive)
}
```

**Step 4: Update polling loop** (lines 394–429) — break out early on rate-limit-reached and replace stop-pending sentinel check:

```powershell
# Poll until orchestrator stops OR enters rate-limit wait
$rateLimitBreak = $false
while (Test-OrchestratorActive) {
    $lastLine = Get-LastLogLine
    $mtime    = Get-LogMTime
    $ageSec   = if ($mtime) { [int]((Get-Date) - $mtime).TotalSeconds } else { -1 }

    # Read live state for stop-pending announcement and rate-limit early exit
    $st = Get-OrchestratorState

    if ($st.Available -and $true -eq $st.StopRequested -and -not $stopRequestedAnnounced) {
        Write-Log "Stop already requested  -  orchestrator will exit after current session."
        $stopRequestedAnnounced = $true
    }

    # AC-37: when orchestrator is just waiting for rate-limit reset, sleep PC immediately
    if ($st.Available -and $true -eq $st.RateLimitReached) {
        Write-Log "Orchestrator is waiting for rate-limit reset (state.json rate_limit_reached=true)."
        Write-Log "Proceeding to suspend PC and scheduling wake from next_wake_time."
        $rateLimitBreak = $true
        break
    }

    # -- Timezone check (unchanged, runs at most once per invocation) --
    if (-not $tzCheckDone -and $null -ne $mtime -and $mtime -ne $tzBaselineMTime) {
        # ... existing TZ-check block unchanged ...
    }

    Write-Log -Status ("running (log age {0}s)  -  {1}" -f $ageSec, $lastLine)
    Start-Sleep -Seconds $PollSeconds
}
```

> **Note for impl agent**: keep the existing TZ-check block verbatim — only add the `Get-OrchestratorState` calls and the rate-limit early-break.

**Step 5: Update wake-up scheduling** (lines 442–481) — prefer `next_wake_time` from state.json when in rate-limit-break mode:

```powershell
if (-not $NoWake) {
    $st = Get-OrchestratorState

    # AC-37: prefer next_wake_time directly when orchestrator was in rate-limit wait
    $wakeAt = $null
    $wakeSource = ""

    if ($rateLimitBreak -and $st.Available -and $null -ne $st.NextWakeTime) {
        $wakeAt = $st.NextWakeTime.AddMinutes(-$WakeBeforeResetMinutes)
        $wakeSource = "state.json next_wake_time"
    } else {
        # Original path: derive wake from rate_limited_until
        $rl = Get-RateLimitState

        foreach ($name in ($rl.Stale.Keys | Sort-Object)) {
            $resetAt = $rl.Stale[$name].ToLocalTime()
            Write-Log ("Rate-limit    : {0} -> stale (reset {1} already past, account usable)" -f `
                       $name, $resetAt.ToString("yyyy-MM-dd HH:mm:ss"))
        }

        if ($rl.Active.Count -eq 0) {
            Write-Log "Wake-up       : skipped  -  no actively rate-limited accounts (none waiting in state.json)"
        } else {
            foreach ($name in ($rl.Active.Keys | Sort-Object)) {
                $resetAt = $rl.Active[$name].ToLocalTime()
                Write-Log ("Rate-limited  : {0} -> resets {1}" -f $name, $resetAt.ToString("yyyy-MM-dd HH:mm:ss"))
            }
            $wakeAt = $rl.Earliest.AddMinutes(-$WakeBeforeResetMinutes)
            $wakeSource = "rate_limited_until earliest"
        }
    }

    if ($null -ne $wakeAt) {
        $now = Get-Date
        if ($wakeAt -le $now) {
            Write-Log ("Wake-up       : computed wake {0:N0} sec ago — too close to sleep, skipping suspend" -f `
                       (($now - $wakeAt).TotalSeconds))
            return
        }
        $sleepMinutes = [int]([math]::Round(($wakeAt - $now).TotalMinutes))
        Write-Log ("Wake-up       : source={0}, waking at {1} (sleeping ~{2} min)" -f `
                   $wakeSource, $wakeAt.ToString("yyyy-MM-dd HH:mm:ss"), $sleepMinutes)
        Register-WakeTask -WakeAt $wakeAt
    }
}
```

**Step 6: Update help-text** (lines 10–22):

```powershell
.DESCRIPTION
    Watches the orchestrator (scripts/automation/orchestrate.py) from Windows and
    suspends the host once it stops. Optionally schedules a Windows wake-up task
    so the PC comes back at a chosen time (e.g. for the next nightly run).

    Detection strategy (cross-platform — works for WSL2 and Docker devcontainers):

      1. state.json is_running flag (PRIMARY)
         - The orchestrator writes is_running=true at startup, false in finally.
         - Single source of truth; no time-based heuristic needed.
      2. state.json rate_limit_reached flag (early-exit)
         - When true, the orchestrator is just waiting for a rate-limit reset.
         - The script proceeds to suspend immediately and schedules wake from
           state.json next_wake_time.
      3. Sentinel + log-mtime fallback (legacy)
         - Used when state.json is missing/unreadable or is_running absent
           (older orchestrator). LogStaleMinutes still applies in this path.
      4. Final log line "[orchestrator] Stopped. Reason: ..."
         - Used to surface the stop reason to the user.
```

**Success criteria for Phase 2b**:
- `pwsh -Command "& { . ./scripts/sleep_when_autorun_done.ps1 -DryRun }"` does not error (parse-clean)
- `grep -n '\.stop-requested\|stopRequestPath' scripts/sleep_when_autorun_done.ps1` returns 0 hits
- `grep -n 'is_running\|rate_limit_reached\|next_wake_time' scripts/sleep_when_autorun_done.ps1` shows the new logic

**Pester test file to create**: `scripts/sleep_when_autorun_done.Tests.ps1`

Write a Pester v5 test file that:
1. Dot-sources the script with `$env:PESTER_TESTING = "1"` set (the existing guard skips main block)
2. Tests `Get-OrchestratorState`:
   - Returns `Available=$false` when state.json is missing
   - Returns `IsRunning=$true` when state.json contains `is_running: true`
   - Returns `IsRunning=$false` when state.json contains `is_running: false`
   - Returns `RateLimitReached=$true` and a parsed `NextWakeTime` when those fields are present
   - Returns `Available=$false` (no crash) when state.json is invalid JSON
3. Tests `Test-OrchestratorActive`:
   - Returns `$true` when state.json `is_running=true` (sentinel absent — state.json wins)
   - Returns `$false` when state.json `is_running=false`
   - Falls back to `$false` when state.json missing and sentinel absent

---

### Phase 3: Verification agent

**Subagent**: `quality-checker` (or `general-purpose` if quality-checker unavailable for shell scripts).

**Verification checklist**:

1. **AC coverage**:
   - [ ] AC-34: state.json has all 6 new fields (run orchestrator briefly, inspect state.json)
   - [ ] AC-35: timestamps in state.json have offsets; `timezone` field is populated
   - [ ] AC-36: PS1 reads `is_running` first; falls back when state.json missing
   - [ ] AC-37: rate-limit-reached early exit + wake from `next_wake_time`
   - [ ] AC-38: `SENTINEL_STOP` removed; orchestrator reads state.json `stop_requested`

2. **Code-level**:
   - [ ] `grep -rn "SENTINEL_STOP\|.stop-requested" scripts/automation/orchestrate.py scripts/sleep_when_autorun_done.ps1` returns 0 hits
   - [ ] No naive `datetime.now()` calls remain that feed state.json
   - [ ] All new fields appear in PersistentState dataclass with type hints + defaults
   - [ ] `dart fix --apply` is N/A (no Dart files); skip
   - [ ] WHY comments present for non-obvious blocks: `_get_local_timezone_name`, `_read_external_stop_request`, `Get-OrchestratorState`

3. **Tests**:
   - [ ] `python3 -m pytest scripts/automation/tests/test_orchestrate.py -x -v` passes
   - [ ] All new test classes have at least one passing test (no `...` placeholders in committed code)
   - [ ] Coverage of new code paths visible in pytest output

4. **PS1 syntax**:
   - [ ] Pester test file exists at `scripts/sleep_when_autorun_done.Tests.ps1` and covers the new Get-OrchestratorState function and the rate-limit early-break logic (AC-36, AC-37)
   - [ ] PS1 syntax check on Linux: `pwsh -NoProfile -Command "Get-Content scripts/sleep_when_autorun_done.ps1 | Out-Null; Write-Host OK"` exits 0
   - [ ] NOTE FOR USER: run `Invoke-Pester scripts/sleep_when_autorun_done.Tests.ps1` on the Windows host to validate the PS1 logic

5. **Doc consistency**: PS1 help-text reflects new detection strategy; `_get_local_timezone_name` docstring explains fallback chain.

**Output**: Write findings to `plans_and_protocols/2026-04-30_03_protocol_verification.md` with PASS/FAIL per item and any required fixes.

---

### Phase 4: Update `claude-autorun` skill

**File**: `.claude/skills/claude-autorun/skill.md`

**Step 1: Replace `stop` action** (current lines: action stop block):

```markdown
## Action: stop

1. ```bash
   python3 -c "
   import json, os
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
2. If `ALREADY_REQUESTED` → "Stop already requested — will stop after current session."
3. If `REQUESTED` → "Stop signal sent (state.json stop_requested=true). Orchestrator finishes current session, writes report, then exits."
```

**Step 2: Update `status` action** — replace the `.stop-requested` test:

```bash
# Before:
test -f automation/.stop-requested && echo "STOP_PENDING" || echo "NO_STOP"
# After:
python3 -c "import json,os; p='automation/state.json'; print('STOP_PENDING' if os.path.exists(p) and json.load(open(p)).get('stop_requested') else 'NO_STOP')"
```

**Step 3: Update monitoring cron prompt** (currently mentions `touch automation/.stop-requested`):

Replace:
> `... run \`touch automation/.stop-requested\` and report ...`

With:
> `... write \`stop_requested: true\` to automation/state.json (preserving other fields) and report ...`

Also include the inline Python one-liner in the prompt so the cron LLM has a concrete command to run.

**Success criteria**: `grep -n '\.stop-requested' .claude/skills/claude-autorun/skill.md` returns 0 hits.

---

### Phase 5: task-complete

Follow the standard `task-complete` skill workflow. Pre-checklist:

- [ ] All ACs in goal.md are checked off
- [ ] requirements.md updated via Phase 1 (AC-34..AC-38 visible in trackable_items)
- [ ] All Python tests passing
- [ ] PS1 parses cleanly
- [ ] Skill file updated
- [ ] No `.stop-requested` references anywhere in the codebase: `grep -rn '\.stop-requested' . --include='*.py' --include='*.ps1' --include='*.md' | grep -v plans_and_protocols/ | grep -v context_gather.md` should return 0 hits in active code

---

## Quality Criteria

- [ ] state.json after a real orchestrator run contains: `is_running`, `active_session`, `stop_requested`, `rate_limit_reached`, `next_wake_time`, `timezone`, all timestamps with offset
- [ ] `claude-autorun stop` causes the orchestrator to stop within one polling iteration without creating any sentinel file
- [ ] `sleep_when_autorun_done.ps1 -DryRun` correctly identifies a rate-limited orchestrator and proceeds to schedule wake without waiting for `is_running` to flip
- [ ] All Python tests pass; new tests cover all 6 new behaviours
- [ ] No grep hits for `.stop-requested` outside of context-gather/plan/protocol files

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Naive datetime in `state.start_time` after upgrade (if `get_now_local` change is missed somewhere) | Phase 3 verification: inspect a real state.json after orchestrator run; assert all timestamps regex-match `+\d{2}:\d{2}` or `[+-]\d{2}:\d{2}$` |
| External stop-request not seen because re-read fails on disk error | `_read_external_stop_request` returns `False` on error (current behaviour preserved); orchestrator continues running. Acceptable — same as current sentinel behaviour where filesystem error means "no stop" |
| PS1 backwards-compat broken for users with stale state.json (old orchestrator format) | `Get-OrchestratorState` returns `Available=false` and `IsRunning=$null`; `Test-OrchestratorActive` falls back to sentinel + log heuristic — no regression |
| `claude-autorun stop` race: skill updates state.json while orchestrator is also writing it | Both paths use atomic write (`.tmp` + `os.replace`); the last writer wins. The orchestrator's `_read_external_stop_request` reads on the next polling iteration, picking up the skill's write. Race window is one polling cycle (acceptable) |
| Pester tests ship without CI execution — PS1 changes have written tests but no runner in Linux dev env | Pester test file is committed; verification agent confirms the file exists and is syntactically valid; user runs `Invoke-Pester` on Windows host |
| `_get_local_timezone_name` returns unexpected name on devcontainers without TZ set | Fallback chain: `zoneinfo.key` → `$TZ` env → `time.tzname` → `"UTC"`. Last-resort `"UTC"` is always valid. Verify in tests via `monkeypatch` |

## Execution Summary (for orchestrating Sonnet)

| # | Phase | Agent | Inputs | Outputs |
|---|-------|-------|--------|---------|
| 1 | requ-explore | requ-explore skill | this plan, AC text in section "Phase 1" | requirements.md updated with AC-34..AC-38 |
| 2a | Implement orchestrator | general-purpose / implementation-engineer | this plan §Phase 2a, context_gather.md | modified orchestrate.py + test_orchestrate.py; tests pass |
| 2b | Implement PS1 | general-purpose / implementation-engineer | this plan §Phase 2b | modified sleep_when_autorun_done.ps1 |
| 3 | Verify | quality-checker / general-purpose | all changes | protocol_verification.md (PASS/FAIL) |
| 4 | Update skill | (inline by Sonnet — small change) | this plan §Phase 4 | modified claude-autorun.skill.md |
| 5 | Complete | task-complete skill | (verified work) | task closed; commits |

Phases 2a and 2b can run in parallel. All others are sequential.
