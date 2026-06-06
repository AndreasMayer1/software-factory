# Opus Schema Analysis — state.json Consolidation

**Task**: TASK-PROC-041-01-09
**Author**: Opus (via claude-switch-opus)
**Date**: 2026-04-30

---

## 1. Consumer Needs Matrix

| Consumer | Genuinely needs from state.json | Why state.json (not log/sentinel) |
|----------|--------------------------------|-----------------------------------|
| **PS1 sleep script** | Is orchestrator actively running? (primary stop signal) | log-mtime fallback has 30 min delay; sentinel persists on SIGKILL |
| **PS1 sleep script** | Is orchestrator blocked in a rate-limit sleep? (early-exit trigger) | Cannot be inferred from log without parsing; rate_limited_until alone doesn't say "sleeping now" |
| **PS1 sleep script** | When will the rate-limit sleep end? (wake-up scheduling) | Already reads rate_limited_until for this; `next_wake_time` is a pre-computed shortcut |
| **Developer (manual)** | Current operational state at a glance | state.json is human-readable; log is verbose |
| **Developer (manual)** | Which account is active? | Helpful for debugging; not available elsewhere without reading the log |
| **Developer (manual)** | Why did the last run stop? | Currently requires grepping the log |
| **claude-autorun skill** | Was a stop already requested? | Currently checks `.stop-requested` sentinel; should read state.json instead |
| **claude-autorun skill** | Is the orchestrator running? | Checks PID via `.automated_mode`; could be complemented by `is_running` |
| **claude-autorun skill** | What account/session is active now? | Only needed for status display |
| **Monitoring LLM cron** | When will each account's rate limit reset? | Already reads `rate_limited_until` — the only field it actually needs |
| **Monitoring LLM cron** | Is the orchestrator stuck (not making progress)? | Infers from log; state.json is secondary |
| **Future tooling** | Structured, typed snapshot of orchestrator state | Prefer explicit fields over log parsing |

**Key insight**: The PS1 script is the only consumer with a real-time liveness requirement (it polls every 60s and must not wait 30 min). All other consumers can tolerate stale data or read logs. This means only `is_running` and `rate_limit_reached` + `next_wake_time` provide genuine new value over what already exists. The other proposed fields are useful but not urgent.

---

## 2. Field-by-Field Analysis

### Existing Fields

#### `account_index` (int)
- **Who reads it**: Orchestrator itself on restart (to resume with the same account rotation position).
- **Can it be derived?** No — it's a counter that must survive restarts.
- **Edge cases**: Stale value after accounts list changes length (bounded by modulo in `accounts_from_state`; safe).
- **Verdict**: KEEP — functional, not observability.

#### `run_count` (int)
- **Who reads it**: Orchestrator (increments each session). Developer (progress check).
- **Can it be derived?** Partially from reports, but not accurately across restarts.
- **Edge cases**: Monotonically increasing; never stale in a harmful way.
- **Verdict**: KEEP — functional counter.

#### `start_time` (str, naive ISO)
- **Who reads it**: Orchestrator (computes duration). Developer. PS1 (indirectly for TZ check via log timestamps).
- **Bug**: Written as naive datetime (no offset). PS1's `RoundtripKind` parser treats naive strings as `DateTimeKind.Unspecified`, and `.ToLocalTime()` on that kind incorrectly treats it as UTC on Windows. This is a latent bug whenever the container TZ != UTC.
- **Fix needed**: Write as aware ISO (with offset). The plan's `get_now_local` change to `lambda: datetime.now().astimezone()` correctly addresses this.
- **Verdict**: KEEP + MODIFY (add timezone offset).

#### `paused_tasks` (list)
- **Who reads it**: Orchestrator on restart — determines which tasks were suspended mid-session and need special handling.
- **Can it be derived?** No — it's transient operational state that only the orchestrator knows.
- **Is it "observability"?** No. It's internal orchestrator logic state.
- **Does it belong in state.json?** YES — it must survive restarts, so it correctly lives here. It is not external-facing observability, but neither is `account_index`. Both are functional restart-state. The distinction between "observability" and "functional state" is not a reason to move fields out of state.json; it is only a reason not to add new fields that serve no consumer.
- **Verdict**: KEEP — necessary functional restart state.

#### `rate_limited_until` (dict: account -> ISO datetime str, UTC with offset)
- **Who reads it**: PS1 script (to schedule wake-up time). Monitoring LLM cron (to know when to next check). Orchestrator itself (to determine which accounts are available on restart).
- **Can it be derived?** No — set when a rate-limit event occurs and must survive restarts.
- **Relationship to proposed `rate_limit_reached` + `next_wake_time`**: See dedicated analysis in Section 3.
- **Edge cases**: Stale entries (past reset times) linger until the orchestrator next tries that account. PS1 already filters stale entries. This is acceptable.
- **Verdict**: KEEP — used by multiple consumers for real decisions. Proposed new fields complement but do not replace it.

#### `question_fingerprints` (dict: task_id -> {words: list, preview: str})
- **Who reads it**: Orchestrator only — used to detect duplicate questions and avoid asking the user the same thing twice (de-duplication logic).
- **Is it "observability"?** No. It is internal deduplication state.
- **Does it belong in state.json?** This is the most debatable field. Arguments:
  - **For staying**: It must survive restarts. It's already here and works. Moving it requires migration logic.
  - **Against staying**: It is complex, large, internal-only data. state.json is becoming a mixed bag of "runtime observability" (for external tools) and "internal orchestrator memory" (for the orchestrator itself). Mixing these two concerns increases the size of the file external tools must parse and risks confusion.
  - **Practical size concern**: With many tasks, this dict grows. External tools must parse and ignore it.
- **Verdict**: KEEP IN state.json for now — the cost of separation (migration, new file, two saves) exceeds the benefit at current scale. However, add a comment in the code that it is internal state and may move to `automation/fingerprints.json` if the file grows unwieldy. Do NOT move it as part of this task.

---

### Proposed New Fields

#### `is_running` (bool)
- **Who reads it**: PS1 script (primary stop-detection signal, replacing 30-min log-stale heuristic). Developer. claude-autorun status.
- **Can it be derived?** Theoretically from `.automated_mode` + log mtime. But that's what we're replacing — it has the 30-min SIGKILL delay.
- **Edge cases**:
  - **Crash without finally block (SIGKILL)**: `is_running` stays `true` — same failure mode as `.automated_mode` sentinel. The log-mtime fallback in PS1 handles this.
  - **Race at startup**: Written `true` before sessions start. Safe — PS1 will see `true` and wait.
  - **Race at shutdown**: Written `false` in `finally`. If crash before `finally`, stays `true`. PS1 falls back to log-mtime stale check.
- **Does it serve a real need?** YES — it is the key field this entire task is built around. The PS1 script's primary consumer need (react in under 60s instead of 30 min) can only be met with this field.
- **Verdict**: ADD — essential. Core justification for the task.

#### `active_session` (str | null)
- **Who reads it**: Developer (which Claude session is running?). claude-autorun status display. Future dashboards.
- **Can it be derived?** Only from session_outputs dir listing, which is indirect and not real-time.
- **Edge cases**: Stale (crash without finally): session UUID remains set. Harmless for observability.
- **Does it serve a real need?** Moderate. Useful for developer debugging, not critical. The PS1 script does not use it.
- **Risk of complexity**: Each session call site (there are 3) needs set/clear wrapping. The plan's Step 10 handles this correctly with per-call-site wrappers.
- **Verdict**: ADD — useful observability. Low risk, helps developer understand what's happening without reading the log.

#### `stop_requested` (bool)
- **Who reads it**: Orchestrator (polls state.json to detect external stop requests, replacing `.stop-requested` sentinel). PS1 script (announces "stop requested" in polling loop). claude-autorun stop/status.
- **Can it be derived?** Currently from `.stop-requested` sentinel. The goal is to replace that sentinel.
- **Edge cases**:
  - External write race: `claude-autorun stop` and orchestrator both write state.json. Plan uses atomic write (`.tmp` + `os.replace`) for both. Last writer wins. Race window is one polling cycle (~60s). Acceptable — same as current sentinel behaviour.
  - **Critical issue**: The plan proposes `_read_external_stop_request()` re-reads state.json from disk on each `_check_stop_conditions` call. This is correct but adds disk I/O to every polling iteration. At 30-60s intervals, this is negligible.
  - **Restart semantics**: The plan clears `stop_requested = False` at startup. This is correct — a stale stop request from a previous run should not prevent the next run.
- **Does it serve a real need?** YES — removes a sentinel file entirely, simplifies the model.
- **Verdict**: ADD — essential for AC-38. Eliminates `.stop-requested` sentinel.

#### `rate_limit_reached` (bool)
- **Who reads it**: PS1 script — when `true`, exits the polling loop immediately and proceeds to suspend PC + schedule wake. Without this, PS1 must wait until `is_running` flips `false` (which happens only after the rate-limit sleep ends, which could be hours).
- **Can it be derived?** Not without parsing `rate_limited_until` vs current time AND knowing the orchestrator is actively sleeping (not just that some accounts have future reset times). The `rate_limited_until` dict can have future entries even when the orchestrator is not currently sleeping (e.g., one account is rate-limited but another is available).
- **Edge cases**: Crash while `rate_limit_reached=true` — stays `true`. PS1 would try to schedule wake from `next_wake_time`. If `next_wake_time` is valid, this is actually the correct behavior (the orchestrator was going to wake up anyway).
- **Does it serve a real need?** YES — this is the second key field. Without it, the PS1 script cannot distinguish "all accounts rate-limited, sleeping for 8 hours" from "actively running sessions".
- **Verdict**: ADD — essential for AC-37.

#### `next_wake_time` (str | null)
- **Who reads it**: PS1 script only (to schedule PC wake-up task at the right time when `rate_limit_reached=true`).
- **Can it be derived?** From `rate_limited_until`: take the earliest future reset time. The PS1 script's `Get-RateLimitState` already does exactly this. So `next_wake_time` IS derivable.
- **Should it be stored even though derivable?** Arguments:
  - **For storing**: The orchestrator knows the exact sleep target (it may use a different calculation than "earliest reset"). Storing it avoids re-implementing the calculation in PS1. Reduces PS1 complexity. The plan already has `rate_limit_sleep` setting this value.
  - **Against storing**: `Get-RateLimitState` already correctly derives the earliest wake time. Adding `next_wake_time` creates a second source of truth — if they diverge, which wins?
  - **Decision**: `next_wake_time` provides a pre-computed, orchestrator-authoritative value that the PS1 script can use directly without reimplementing the calculation. The risk of divergence is low because `rate_limited_until` and `next_wake_time` are set in the same code path. The PS1 plan uses `next_wake_time` when `rate_limit_reached=true` and falls back to `Get-RateLimitState` otherwise. This is correct layering.
- **Verdict**: ADD — justified by reducing PS1 complexity and making the orchestrator's intent explicit. Note in implementation: if derivation diverges from `rate_limited_until`, the explicitly-set `next_wake_time` takes precedence.

#### `timezone` (str | null)
- **Who reads it**: Developer (to interpret timestamps). Future tooling. Monitoring LLM.
- **Can it be derived?** Not from state.json itself (timestamps have offsets, but IANA name is not recoverable from offset alone — e.g., `+02:00` is ambiguous across dozens of timezones).
- **Edge cases**: Container TZ changes between runs. The plan refreshes on every `save_state()` call — correct.
- **Does it serve a real need?** Moderate. Timestamps with offsets (`+02:00`) are already unambiguous for time math; IANA name adds human readability ("Europe/Berlin" vs "+02:00"). Useful for dashboards and debugging.
- **Verdict**: ADD — low cost, genuine value for human readability and future tooling.

---

## 3. Specific Questions

### Does `question_fingerprints` belong in state.json or a separate file?

**Verdict: KEEP in state.json for this task.** Rationale: it must survive restarts, the data is currently manageable in size, and the migration cost (new file, two-path save, update all load/save callers) is not justified by the benefit. Add a code comment flagging it as a candidate for extraction to `automation/fingerprints.json` if it grows.

### Does `paused_tasks` belong here?

**Verdict: YES, it belongs in state.json.** It is functional restart-state, not observability. The concern would be if it confused external consumers — but it is a simple list and external consumers can ignore unknown fields.

### Should `rate_limited_until` stay alongside `rate_limit_reached` + `next_wake_time`?

**Verdict: YES, keep all three.** They serve different purposes:

| Field | Who needs it | When |
|-------|-------------|------|
| `rate_limited_until` | Orchestrator restart (knows which accounts are available), PS1 wake scheduling (fallback), Monitoring LLM | Always — functional |
| `rate_limit_reached` | PS1 (immediate signal: "currently sleeping") | Runtime only |
| `next_wake_time` | PS1 (pre-computed wake target) | Only when `rate_limit_reached=true` |

There is no redundancy conflict. `rate_limited_until` says "these accounts are limited until T". `rate_limit_reached` says "I am currently in a sleep waiting for them". `next_wake_time` says "I will wake at T_wake". These are distinct facts.

### Should `stop_reason` (why last run stopped) be added?

**Analysis**: Currently, the developer must grep the log for "Stopped. Reason:". The `run_data.stop_reason` is already tracked in-memory. Writing it to state.json would make it accessible without log parsing.

**Who genuinely needs it**: Developer (why did the last run stop?). claude-autorun status (could display it). PS1 (currently uses `Get-StopReason` which reads the log tail — state.json would be simpler).

**Verdict: ADD — recommended.** The orchestrator already has `run_data.stop_reason`. Writing it to `state.json` at shutdown costs one line. Value is clear. Implementation: set `state.stop_reason = run_data.stop_reason` before the final `save_state()` in the `finally` block. Type: `str | null`, default `null`. Values: `"manual"`, `"scheduled"`, `"max_tasks"`, `"error"`, or `null` (still running). **This is a recommendation beyond the current plan — see Section 5.**

### Should `current_account` (which account is active now) be added?

**Analysis**: The developer wants to know which account is being used in the current session. Currently derivable from `account_index` + knowing the accounts list, but the accounts list is not in state.json.

**Who genuinely needs it**: Developer (debugging). claude-autorun status.

**Verdict: SKIP for this task.** `active_session` (the UUID) is more useful than `current_account` (the account name) because it lets you find the session output file. If account name is needed, the log always has it. Adding `current_account` requires writing it at the same call sites as `active_session` — more complexity for marginal gain. The monitoring cron does not need it. Leave it for a future iteration.

### Should `session_count_this_run` be added?

**Analysis**: The developer wants to know how many sessions have run in the current orchestrator invocation. Currently only in the log and report.

**Who genuinely needs it**: Developer (quick progress check without reading a report). claude-autorun status.

**Verdict: SKIP for this task.** `run_count` is a global counter that already serves a similar purpose. `session_count_this_run` would reset at each orchestrator start — which is useful but orthogonal to the core observability goal here. The report file already has this. Low priority compared to the core fields. Can be added in a follow-up.

### Is there anything else missing?

**`last_session_result`** (str | null): Did the last session complete successfully, raise a question, or error? This would help the monitoring LLM and developer without reading the log. Example values: `"completed"`, `"question_raised"`, `"error"`, `"resumed"`. **Verdict: Useful but out of scope for this task.** The report file covers this.

**`orchestrator_version`** or `schema_version` (int): A version number for the state.json schema. Allows consumers to detect incompatible schema changes. **Verdict: Worth adding long-term, but not needed now.** No breaking schema changes are planned beyond the additive fields in this task. External consumers already guard with `.get(field, default)`.

---

## 4. Recommended Final Schema

```json
{
  "account_index": 0,
  "run_count": 86,
  "start_time": "2026-04-30T21:19:36.107854+02:00",
  "paused_tasks": [],
  "rate_limited_until": {
    "gmail": "2026-04-29T23:05:00+02:00",
    "web": "2026-04-30T19:05:00+02:00",
    "gmail2": "2026-04-29T22:35:00+02:00"
  },
  "question_fingerprints": {},
  "is_running": false,
  "active_session": null,
  "stop_requested": false,
  "rate_limit_reached": false,
  "next_wake_time": null,
  "timezone": "Europe/Berlin",
  "stop_reason": null
}
```

| Field | Type | Default | Justification |
|-------|------|---------|---------------|
| `account_index` | int | 0 | Functional restart-state: resume account rotation position |
| `run_count` | int | 0 | Functional counter: total sessions across all runs |
| `start_time` | str (ISO+offset) \| null | null | Functional: current run start time; **fix**: add timezone offset |
| `paused_tasks` | list | [] | Functional restart-state: tasks suspended mid-session |
| `rate_limited_until` | dict | {} | Functional + observability: per-account reset times for restart and wake scheduling |
| `question_fingerprints` | dict | {} | Internal: deduplication state; survives restarts |
| `is_running` | bool | false | **Primary observability**: PS1 stop-detection without 30-min delay |
| `active_session` | str \| null | null | Observability: which session UUID is executing (for log correlation) |
| `stop_requested` | bool | false | Signal: replaces `.stop-requested` sentinel file (AC-38) |
| `rate_limit_reached` | bool | false | **Observability**: PS1 early-exit signal — "sleeping, not done" |
| `next_wake_time` | str (ISO+offset) \| null | null | Observability: pre-computed wake target when rate_limit_reached=true |
| `timezone` | str \| null | null | Human-readability: IANA name for timestamp interpretation |
| `stop_reason` | str \| null | null | **Recommended addition**: last stop reason without log grep |

---

## 5. Naming Convention Validation

**Question**: goal.md uses camelCase (`isRunning`, `stopRequested`); the plan uses snake_case (`is_running`, `stop_requested`).

**Verdict: snake_case is correct.** All existing keys in state.json use snake_case (`account_index`, `run_count`, `rate_limited_until`, `question_fingerprints`). The Python dataclass uses snake_case. The PowerShell `ConvertFrom-Json` cmdlet maps JSON keys directly to property names, and PS1 code already uses `$json.rate_limited_until` — so `$json.is_running` is natural. camelCase in goal.md was illustrative, not prescriptive. The plan's choice is correct.

---

## Changes to Implementation Plan

Comparing against `/workspaces/private_mood_tracker/flutter_app/requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/feat_session_orchestrator/tasks/2026-04-30_impl_orchestrator-state-json-consolidation/plans_and_protocols/2026-04-30_01_plan_state-json-consolidation.md`:

### Fields to ADD beyond the plan

**`stop_reason` (str | null, default null)**

The plan does not include this field. It is recommended because:
1. `run_data.stop_reason` is already tracked in-memory (set at KeyboardInterrupt, in `check_stop_conditions`, etc.)
2. The PS1 script's `Get-StopReason` function reads the log tail — `state.json["stop_reason"]` would be cleaner and faster
3. The monitoring LLM and developer would benefit from knowing why the last run stopped without log grep
4. Implementation cost: one line in the `finally` block before `save_state()`

**Implementation addition** (in `finally` block, just before `save_state`):
```python
state.stop_reason = run_data.stop_reason  # "manual", "scheduled", "max_tasks", or "error"
```
Add `stop_reason: "str | None" = None` to `PersistentState` dataclass.
Clear to `null` at startup (like `stop_requested`): `state.stop_reason = None`.

### Fields to KEEP as proposed (no changes)

- `is_running` — essential, keep as designed
- `active_session` — keep as designed
- `stop_requested` — keep as designed
- `rate_limit_reached` — keep as designed
- `next_wake_time` — keep as designed, rationale validated above
- `timezone` — keep as designed

### Fields to REMOVE from plan

None. All proposed fields serve genuine consumer needs.

### Design decisions validated

| Decision in plan | Verdict |
|-----------------|---------|
| D1: snake_case naming | CONFIRMED CORRECT |
| D2: Aware local datetime with offset | CONFIRMED CORRECT |
| D3: Fix `get_now_local` default | CONFIRMED NECESSARY |
| D4: No migration for `start_time` (reset on startup) | CONFIRMED CORRECT |
| D5: `rate_limited_until` switch to local offset | CONFIRMED CORRECT — `.ToLocalTime()` is idempotent on local-time inputs in PS1 |
| D6: Re-read state.json for `stop_requested` | CONFIRMED CORRECT — necessary for out-of-band writes |
| D7: Pester tests (manual execution on Windows) | CONFIRMED PRAGMATIC — no alternative in Linux dev container |
| D8: Retain `.automated_mode` sentinel | CONFIRMED CORRECT — PID-based liveness check is separate concern |

### One correction to plan

**Phase 2b, Step 1**: The plan says "remove `$stopRequestPath` variable (line 119)". Also remove its use in the polling loop at line 401:
```powershell
if ((Test-Path -LiteralPath $stopRequestPath) -and -not $stopRequestedAnnounced) {
```
This line reads the `.stop-requested` sentinel. It must be replaced with a `state.json["stop_requested"]` check via `Get-OrchestratorState`. The plan does mention this in Step 4 (update polling loop) but does not explicitly call out removing the `Test-Path $stopRequestPath` check. The impl agent must remove ALL references, not just the variable declaration.

### `question_fingerprints` — no action

Confirmed: keep in state.json for this task. Do not add extraction to a separate file.
