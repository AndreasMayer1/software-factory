#!/usr/bin/env python3
# ruff: noqa: RUF002, RUF003, RUF100
# RUF002 / RUF003: docstrings and comments use Unicode mathematical/typographical glyphs
# intentionally (en dash for numeric ranges like scenarios S1 to S26, set-theory symbols
# in Jaccard formulas).
# RUF100: false-positive on file-level noqa for codes ruff cannot introspect into the file body.
"""
scripts/automation/orchestrate.py

Session orchestrator for unattended Claude Code batch processing.
Launches sequential claude sessions with per-account CLAUDE_CONFIG_DIR rotation.

Python 3.9+ required. No external dependencies (stdlib only, uses zoneinfo).

TESTS:
  scripts/automation/tests/test_orchestrate.py
  Run: python3 -m pytest scripts/automation/tests/test_orchestrate.py

SPEC:
  automation/MONITORING_CRITERIA.md documents the observable log patterns
  (scenarios S1–S26) that the monitoring LLM watches for. When you add a
  new log line, a new failure mode, or a new recovery path here, please
  also add or update the corresponding scenario in that file — the monitor
  needs to know whether to treat the pattern as INFO / WARNING / CRITICAL.

NOTES:
- If the script is SIGKILL'd (not SIGTERM), the .automated_mode sentinel may persist;
  state.json will retain is_running=true. External observers should fall back to the
  log-mtime heuristic in that case. The state file is corrected on the next normal run.
- session_outputs/ files accumulate over time; cleanup_old_artifacts() runs at start.

Output:
    Streams orchestrator protocol lines of the form
    "[orchestrator <iso-timestamp>] <event>" to stdout (also mirrored to
    automation/orchestrate.log). Subcommands (status, resume-interactive,
    etc.) print human-readable status to stdout. All protocol-style lines
    are emitted through the single _proto() helper so the surface is
    greppable (REQ-PROC-051 AC-09 G5).
"""

# tier: A  # long-lived stateful orchestrator; owns invariants across try/except boundaries

# --- Section 1: Imports + constants ---

import argparse
import dataclasses
import fcntl
import glob
import json
import os
import re
import shutil
import signal
import subprocess
import sys as _sys
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, tzinfo
from enum import Enum
from pathlib import Path as _Path
from typing import Any, Callable, cast
from zoneinfo import ZoneInfo

# Why: orchestrate.py runs both as `python3 scripts/automation/orchestrate.py`
# (project-root cwd) and is imported by tests via sys.path injection of
# scripts/automation. The central YAML helper lives at scripts/util/yaml_frontmatter.py.
# Add scripts/ to sys.path so `from util.yaml_frontmatter import ...` resolves
# regardless of invocation path.
_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in _sys.path:
    _sys.path.insert(0, _SCRIPTS_DIR)

from util.feedback_checkpoint import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    CheckpointFields,
    render_checkpoint,
    resolve_checkpoint_path,
)
from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    _split_frontmatter,
    read_frontmatter,
)

# Why: __file__ is scripts/automation/orchestrate.py; two dirname() calls reach project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CCS_ROOT = "/home/vscode/.ccs/instances"
AUTOMATION_DIR = os.path.join(PROJECT_ROOT, "automation")
STATE_PATH = os.path.join(AUTOMATION_DIR, "state.json")
FEEDBACK_DIR = os.path.join(AUTOMATION_DIR, "pending_feedback")
ANSWERED_DIR = os.path.join(AUTOMATION_DIR, "answered_feedback")
ANSWER_TEMPLATE_PATH = os.path.join(FEEDBACK_DIR, "TEMPLATE_answer.md")
# Why: the template marker is the canonical "unanswered" sentinel; any answer.md whose
# stripped content starts with this line is treated as unanswered even if non-empty.
ANSWER_TEMPLATE_MARKER = "<!-- AWAITING_HUMAN_ANSWER -->"
# Why: a question.md carries this status only while it still needs a human answer. Once a
# session marks it resolved/other, the safety-net must NOT treat a later mtime bump (from
# the resolve edit itself) as a fresh follow-up question.
QUESTION_STATUS_AWAITING = "awaiting_answer"
OUTPUTS_DIR = os.path.join(AUTOMATION_DIR, "session_outputs")
REPORTS_DIR = os.path.join(AUTOMATION_DIR, "reports")
SENTINEL_AUTOMATED = os.path.join(AUTOMATION_DIR, ".automated_mode")
# Note: .stop-requested sentinel file removed in AC-38; stop signalling now uses
# state.json["stop_requested"] — see _read_external_stop_request() and PersistentState.

# Why: regex captures "resets 9pm (Europe/Berlin)" or "resets 9:00pm (Europe/Berlin)"
# from rate limit stdout — minutes are optional in the actual Claude message format.
# Groups: (1=hour, 2=optional_minutes, 3=am_pm, 4=tz_name)
RATE_LIMIT_PATTERN = re.compile(
    r"resets (\d{1,2})(?::(\d{2}))?\s*(am|pm) \(([^)]+)\)",
    re.IGNORECASE,
)

# Fallback sleep (seconds) when rate limit time cannot be parsed
RATE_LIMIT_FALLBACK_SLEEP_SECS = 65 * 60  # 65 minutes

# Permanent access error substrings — same check used in both normal and resume paths
PERM_ERROR_PATTERNS = [
    "does not have access",
    "organization does not have access",
    "has disabled Claude subscription access",
]


# --- Section 2: Pure utility functions ---


def _ts() -> str:
    """Return current local time as HH:MM:SS for log prefixes."""
    # Why: .astimezone() makes the local timezone explicit rather than relying on the
    # implicit OS default — prevents UTC display on containers with a misconfigured TZ.
    return datetime.now().astimezone().strftime("%H:%M:%S")


def _proto(message: str, *, flush: bool = False) -> None:
    """Emit one orchestrator protocol line ('[orchestrator <ts>] <message>') to stdout.

    Single named helper for protocol output so the surface is greppable
    (REQ-PROC-051 AC-09, G5 print discipline). All orchestrator-internal
    protocol/log lines route through here. Output behavior is identical
    to the previous `print(f"[orchestrator {_ts()}] ...")` pattern.
    `flush=True` forces an immediate stdout flush (used for heartbeats so
    sleep_when_autorun_done.ps1 sees fresh log mtime promptly).
    """
    # Why: keep this a thin print() wrapper rather than logging, because
    # downstream tooling (sleep_when_autorun_done.ps1, log scrapers,
    # monitoring scenarios in automation/MONITORING_CRITERIA.md) tails
    # stdout/log files line-by-line and depends on the literal prefix.
    print(f"[orchestrator {_ts()}] {message}", flush=flush)  # noqa: T201 — _proto is the protocol helper


# Per-run dedupe set for log lines that would otherwise repeat every iteration
# (e.g. "answer.md contains only whitespace" — same task, same warning, every
# loop). Reset at run start in main() so a long-lived process emits each
# warning at most once per run.
_run_log_dedupe: set[str] = set()


def _proto_once(key: str, message: str, *, flush: bool = False) -> None:
    """Emit `message` only once per run for the given dedupe `key`.

    Why: the orchestrator scans pending_feedback every iteration; tasks with
    static blockers (whitespace-only answer.md, unchanged unanswered question)
    would otherwise log identical warnings ~10x per run. Squelching duplicates
    by a caller-chosen key (e.g. "whitespace:TASK-ID") keeps the log readable
    without losing the first occurrence.
    """
    if key in _run_log_dedupe:
        return
    _run_log_dedupe.add(key)
    _proto(message, flush=flush)


def interruptible_sleep(total_secs: float, stop_flag: dict[Any, Any], poll_interval: int = 30) -> None:
    """Sleep for total_secs in poll_interval chunks, honouring stop_flag between ticks."""
    # Why: use monotonic deadline so WSL2 timer drift doesn't accumulate across 100+
    # ticks — the old `remaining -= tick` approach could overshoot by several minutes.
    deadline = time.monotonic() + total_secs
    while not stop_flag["requested"]:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        tick = min(poll_interval, remaining)
        time.sleep(tick)


# Heartbeat interval during rate-limit waits — must stay well below the 30-minute
# log-staleness threshold used by sleep_when_autorun_done.ps1.
_RATE_LIMIT_HEARTBEAT_SECS = 15 * 60  # 15 minutes


def rate_limit_sleep(
    total_secs: float,
    stop_flag: dict[Any, Any],
    reset_dt: "datetime | None" = None,
    poll_stop: "Callable[[], bool] | None" = None,
) -> None:
    """Sleep during a rate-limit window, emitting a heartbeat log line every 15 minutes.

    Keeps orchestrate.log fresh so sleep_when_autorun_done.ps1 does not mistake an
    intentional wait for a crashed process (which uses a 30-minute staleness threshold).

    When `reset_dt` is provided (the absolute UTC reset time), the remaining-time
    calculation uses wall-clock instead of the monotonic clock. On WSL2 the
    monotonic clock pauses while the Windows host is suspended, so a monotonic
    deadline would extend the wait by however long the host slept. Wall-clock
    comparison against the absolute reset time fixes that. Recomputing remaining
    as `(reset_dt - now)` each tick is also drift-free, replacing the old
    monotonic deadline whose only purpose was avoiding `remaining -= tick` drift.
    The fallback monotonic branch is kept for callers that pass only a duration.

    When `poll_stop` is provided it is called each tick to re-read the external stop
    request (state.json[stop_requested]). Why: the loop otherwise honours only the
    in-memory stop_flag, which is set by SIGINT/SIGTERM. A flag-only stop that writes
    state.json without sending a signal — e.g. the monitor's emergency auto-stop in
    claude-autorun — would otherwise not be observed until the next loop iteration,
    which never arrives during a multi-hour wait. Polling lets it take effect within
    one tick (≤30s).
    """
    use_wall_clock = reset_dt is not None
    deadline_mono: float | None = None if use_wall_clock else time.monotonic() + total_secs
    next_heartbeat = time.monotonic() + _RATE_LIMIT_HEARTBEAT_SECS
    # Convert UTC reset time to local for display — reset_dt is stored as UTC in state.json
    reset_local = reset_dt.astimezone() if reset_dt else None
    reset_info = f" (resets {reset_local.strftime('%Y-%m-%d %H:%M %Z')})" if reset_local else ""
    while not stop_flag["requested"]:
        if poll_stop is not None and poll_stop():
            # Mirror the external request into the in-memory flag so the caller's
            # subsequent check_stop_conditions() short-circuits and the loop exits.
            stop_flag["requested"] = True
            break
        if use_wall_clock:
            assert reset_dt is not None  # narrowing: use_wall_clock implies reset_dt is set
            remaining = (reset_dt - datetime.now(timezone.utc)).total_seconds()
        else:
            assert deadline_mono is not None  # narrowing: not use_wall_clock implies deadline_mono is set
            remaining = deadline_mono - time.monotonic()
        if remaining <= 0:
            break
        now_mono = time.monotonic()
        if now_mono >= next_heartbeat:
            remaining_min = remaining / 60
            _proto(
                f"Still waiting for rate-limit reset{reset_info} — "
                f"{remaining_min:.0f} min remaining",
                flush=True,
            )
            next_heartbeat = now_mono + _RATE_LIMIT_HEARTBEAT_SECS
        tick = min(30, remaining, next_heartbeat - now_mono)
        time.sleep(tick)


def _get_local_timezone_name() -> str:
    """Return the IANA name of the OS local timezone, with safe fallbacks.

    Why: state.json stores a `timezone` field so external tools (Windows
    sleep_when_autorun_done.ps1) can resolve container timestamps. The value
    MUST be an IANA name like "Europe/Berlin" — never an abbreviation like
    "CEST", which neither .NET TimeZoneInfo nor zoneinfo can resolve.
    Resolution order:
      1. tzinfo.key when astimezone() returned a ZoneInfo
      2. /etc/timezone (Debian/Ubuntu — what the devcontainer actually has)
      3. /etc/localtime symlink target (Alpine and other distros)
      4. $TZ env var (only if it looks like an IANA name, not "CEST")
      5. "UTC" — abbreviations from time.tzname are NOT used: they break
         downstream consumers and silently mask the real timezone.
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_session_orchestrator/tasks/2026-04-30_impl_orchestrator-state-json-consolidation/
            plans_and_protocols/2026-04-30_01_plan_state-json-consolidation.md#step-1
    """
    try:
        tz = datetime.now().astimezone().tzinfo
        if tz is not None and hasattr(tz, "key"):
            return cast("str", tz.key)
    except Exception:
        pass
    try:
        with open("/etc/timezone", encoding="utf-8") as f:
            name = f.read().strip()
        if name and "/" in name:
            return name
    except Exception:
        pass
    try:
        target = os.readlink("/etc/localtime")
        marker = "/zoneinfo/"
        idx = target.find(marker)
        if idx != -1:
            name = target[idx + len(marker):]
            if name and "/" in name:
                return name
    except Exception:
        pass
    tz_env = os.environ.get("TZ", "")
    # Why: only accept TZ when it looks like an IANA name (contains "/").
    # Bare abbreviations like "CEST" are not resolvable downstream.
    if tz_env and "/" in tz_env:
        return tz_env
    return "UTC"


def _format_utc_offset(offset: timedelta) -> str:
    """Format a timedelta as '+HH:MM' / '-HH:MM'.

    Pure helper, split out so it can be unit-tested without patching
    datetime.now().astimezone() (which is hard to fake because astimezone()
    consults the OS local timezone, not the input's tzinfo).
    Must produce strings parseable by sleep_when_autorun_done.ps1's regex
    `^([+-])(\\d{2}):(\\d{2})$`.
    """
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    h, m = divmod(abs(total_minutes), 60)
    return f"{sign}{h:02d}:{m:02d}"


def _get_local_timezone_offset() -> str:
    """Return the OS local UTC offset as '+HH:MM' / '-HH:MM'.

    Why: Windows PowerShell 5.1 (.NET Framework) cannot resolve IANA names like
    'Europe/Berlin' via TimeZoneInfo.FindSystemTimeZoneById — only Windows zone
    IDs ('W. Europe Standard Time'). state.json therefore also exposes the raw
    offset so sleep_when_autorun_done.ps1 can compare against the host offset
    without any zone-name resolution. Recomputed on every save_state() so it
    follows DST.
    """
    offset = datetime.now().astimezone().utcoffset() or timedelta(0)
    return _format_utc_offset(offset)


def _reset_startup_state(state: "PersistentState") -> None:
    """Reset all observability fields at run start, clearing any stale values from a prior crash.

    Why: if the orchestrator was SIGKILL'd mid-session, state.json retains the last written
    values (e.g. stop_requested=True, active_session="<uuid>", rate_limit_reached=True).
    A fresh run must clear these before entering the loop so external observers and
    check_stop_conditions do not act on stale data.
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_session_orchestrator/tasks/2026-04-30_impl_orchestrator-state-json-consolidation/
            plans_and_protocols/2026-04-30_01_plan_state-json-consolidation.md#step-7
    """
    state.is_running = True
    state.active_session = None
    state.stop_requested = False
    state.stop_reason = None
    state.rate_limit_reached = False
    state.next_wake_time = None


def strip_hook_footer(text: str) -> str:
    """Remove hook reminder footer appended by Claude Code hooks."""
    return re.sub(r"\n---\n\*\*Reminder:.*", "", text, flags=re.DOTALL)


def parse_rate_limit_reset(stdout: str) -> "datetime | None":
    """Parse reset datetime from rate limit stdout.

    Returns UTC-aware datetime of reset + 5 min buffer, or None if not found.
    Falls back to UTC if timezone name is not recognized by zoneinfo.
    """
    match = RATE_LIMIT_PATTERN.search(stdout)
    _proto(f"DEBUG: rate-limit raw stdout: {stdout!r}")
    if not match:
        return None

    hour = match.group(1)
    minute = match.group(2) or "00"
    ampm = match.group(3)
    tz_name = match.group(4)
    time_str = f"{hour}:{minute}{ampm}"

    tz: tzinfo
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        _proto(f"WARNING: unknown timezone '{tz_name}', falling back to UTC")
        tz = timezone.utc

    try:
        now_local = datetime.now(tz)
        # strptime has no timezone support — attach tz after parsing
        reset_naive = datetime.strptime(time_str.upper(), "%I:%M%p")
        reset_time = reset_naive.replace(
            year=now_local.year,
            month=now_local.month,
            day=now_local.day,
            tzinfo=tz,
        )

        # If reset_time is already past (edge case: clock just rolled over), add 1 day
        if reset_time <= now_local:
            reset_time += timedelta(days=1)

        # Add 5 min buffer, convert to UTC
        return (reset_time + timedelta(minutes=5)).astimezone(timezone.utc)
    except Exception as e:
        _proto(f"WARNING: could not parse reset time '{time_str}' ({e})")
        return None


def answer_is_empty(answer_path: str) -> bool:
    """Return True if answer.md does not exist, is zero-byte, whitespace-only, or
    contains only the TEMPLATE_answer.md placeholder content (unanswered sentinel).

    Note: whitespace-only detection (AC-20) requires reading content; the WARNING log
    must be emitted in the caller because task_id is not in scope here.
    """
    if not os.path.exists(answer_path):
        return True
    if os.path.getsize(answer_path) == 0:
        return True
    try:
        with open(answer_path) as f:
            content = f.read()
        stripped = content.strip()
        if stripped == "":
            return True
        # Why: TEMPLATE_answer.md is copied (not touch'd) when a question is written.
        # Any session reading the file before writing will see the prohibition text.
        # If the file still starts with the template marker and has no human content
        # after it, treat it as unanswered — the template text is not a real answer.
        # Why: if the file starts with the template marker, compare against the full
        # template to detect the unmodified placeholder. A human answer may prepend
        # the marker line but will always add content that differs from the template.
        if stripped.startswith(ANSWER_TEMPLATE_MARKER):
            try:
                with open(ANSWER_TEMPLATE_PATH) as tf:
                    template_stripped = tf.read().strip()
                if stripped == template_stripped:
                    return True
            except OSError:
                # Template file missing — fall through to treat as non-empty
                pass
    except OSError:
        pass
    return False


def read_yaml_frontmatter(path: str) -> dict[Any, Any]:
    """Extract YAML key:value pairs from a file's frontmatter via the central helper.

    Returns an empty dict for missing files, files without frontmatter, or
    malformed frontmatter. The legacy parser tolerated malformed input by
    returning whatever partial data it had collected; this wrapper preserves
    the "best-effort, never raise" contract by catching the FrontmatterError
    that the helper raises on non-mapping frontmatter.

    Why: migrated from a hand-rolled line-by-line parser to the central
    ruamel-backed helper as part of TASK-PROC-051-04 (REQ-PROC-051 AC-08).
    The previous parser handled scalars + inline lists + block lists at the
    top level only; the helper handles full YAML which is a superset.
    """
    try:
        doc = read_frontmatter(_Path(path))
    except (OSError, ValueError):
        return {}
    metadata = doc.metadata
    if metadata is None:
        return {}
    return dict(metadata)


def compute_question_fingerprint(text: str) -> dict[Any, Any]:
    """Normalize text and return word set + preview for Jaccard comparison.

    Normalization: lowercase, strip punctuation, collapse whitespace.
    Words stored as list for JSON serialisability; callers convert to set when comparing.
    """
    normalized = re.sub(r"[^\w\s]", "", text.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    words = set(normalized.split())
    return {"words": list(words), "preview": normalized[:300]}


def _jaccard(a: set[Any], b: set[Any]) -> float:
    """Compute Jaccard similarity between two word sets.

    Why: Jaccard similarity (|A∩B| / |A∪B|) is chosen over edit distance because
    questions are short free-form text where word overlap is a better signal of
    semantic repetition than character-level edit distance. The 0.60 threshold
    (set in check_and_update_question_fingerprint) was chosen to catch near-identical
    re-phrasings while tolerating normal variation; empty-set edge case returns 1.0
    (two empty questions are identical).
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_session_orchestrator/tasks/2026-04-10_impl_implement-orchestrator-monitoring-improvements/
            plans_and_protocols/2026-04-10_02_plan_rewrite-architecture.md#5-new-functions
    """
    if not a and not b:
        return 1.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


# --- Section 3: I/O adapters ---


@dataclass
class PersistentState:
    """State that survives across orchestrator restarts (written to state.json).

    Why: splitting persistent state (survives restarts) from in-memory run accumulators
    (RunData) makes it clear what is serialised to disk and prevents accidentally
    persisting transient data like disabled_accounts (which should reset each run).

    Observability fields (is_running, active_session, stop_requested,
    rate_limit_reached, next_wake_time, timezone, stop_reason) let external tools —
    notably sleep_when_autorun_done.ps1 — react to orchestrator state without polling
    sentinel files or log mtimes. See AC-34..AC-38.
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_session_orchestrator/tasks/2026-04-30_impl_orchestrator-state-json-consolidation/
            plans_and_protocols/2026-04-30_01_plan_state-json-consolidation.md#step-2
    """
    account_index: int = 0
    run_count: int = 0
    start_time: "str | None" = None        # ISO string with offset
    paused_tasks: list[Any] = field(default_factory=list)
    rate_limited_until: dict[Any, Any] = field(default_factory=dict)   # account -> ISO datetime string
    question_fingerprints: dict[Any, Any] = field(default_factory=dict)  # task_id -> {words: list, preview: str}
    # Note: question_fingerprints is internal deduplication state; it may move to a
    # separate automation/fingerprints.json if the dict grows unwieldy.
    # --- Observability fields (AC-34..AC-38) ---
    is_running: bool = False
    active_session: "str | None" = None
    stop_requested: bool = False
    rate_limit_reached: bool = False
    next_wake_time: "str | None" = None
    timezone: "str | None" = None
    timezone_offset: "str | None" = None   # OS local UTC offset as '+HH:MM' / '-HH:MM'; PS 5.1 fallback when IANA name cannot be resolved
    stop_reason: "str | None" = None       # last stop reason: "manual", "scheduled", "max_tasks", "error", or None


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
                timezone_offset=data.get("timezone_offset", None),
                stop_reason=data.get("stop_reason", None),
            )
        except (json.JSONDecodeError, OSError) as e:
            _proto(f"WARNING: state.json corrupt or unreadable ({e}), starting fresh")
    return PersistentState()


def save_state(path: str, state: PersistentState, deps: "OrchestratorDeps", *, startup: bool = False) -> None:
    """Atomic write via tmp + os.replace to avoid partial writes on crash.

    Why: state.timezone is refreshed on every save so external readers always
    see the timezone that produced the timestamps in this file (matters if the
    container TZ changes between launches).
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_session_orchestrator/tasks/2026-04-30_impl_orchestrator-state-json-consolidation/
            plans_and_protocols/2026-04-30_01_plan_state-json-consolidation.md#step-4
    """
    tmp = path + ".tmp"
    try:
        # Issue 6 guard: refuse to overwrite state.json mid-run when the in-
        # memory state has start_time=None. After main() startup the live state
        # always carries start_time set (line 3350 unconditionally assigns
        # start_time.isoformat()) and never re-clears it. A non-startup
        # save_state with start_time=None therefore comes from a bug (a fresh
        # PersistentState was passed instead of the live one, or the live
        # object was mutated to defaults) and would clobber valid disk state,
        # tricking the Windows sleep watcher into suspending the host mid-run.
        # Source: automation/REFACTOR_ISSUES.md Issue 6.
        if not startup and state.start_time is None:
            _proto(
                "WARNING: save_state refused — in-memory state has "
                "start_time=None mid-run (would clobber state.json with "
                "PersistentState() defaults). "
                "See automation/REFACTOR_ISSUES.md Issue 6."
            )
            return
        # Refresh timezone label on every save so it always reflects current OS tz
        state.timezone = _get_local_timezone_name()
        state.timezone_offset = _get_local_timezone_offset()
        # Preserve external stop_requested=true writes. An outside writer
        # (claude-autorun stop, a human editor) can set state.json
        # stop_requested=true while the orchestrator is mid-session — at that
        # point our in-memory copy still has False, and a blind save would
        # overwrite the disk value before check_stop_conditions ever reads it.
        # Skipped at startup (startup=True) so _reset_startup_state can clear a
        # stale stop_requested left by a previous run — without this guard the
        # disk value would be re-read and immediately restore the flag to True.
        if not state.stop_requested and not startup:
            try:
                if deps.file_exists(path):
                    on_disk = json.loads(deps.read_file(path))
                    if on_disk.get("stop_requested") is True:
                        state.stop_requested = True
            except (json.JSONDecodeError, OSError):
                pass
        deps.makedirs(os.path.dirname(path))
        data = dataclasses.asdict(state)
        content = json.dumps(data, indent=2)
        deps.write_file(tmp, content)
        # Why: WSL2 + Windows host suspend can lose buffered writes if the host
        # suspends before pdflush gets dirty pages to NTFS. Without explicit fsync,
        # state.json can revert to its pre-startup content after resume. fsync the
        # tmp file before the rename, and fsync the parent directory after, so both
        # the data and the rename reach disk before any subsequent suspend.
        # Best-effort: tests use fake write_file that doesn't create real files —
        # FileNotFoundError on os.open is caught and ignored.
        try:
            _fd = os.open(tmp, os.O_RDONLY)
            try:
                os.fsync(_fd)
            finally:
                os.close(_fd)
        except OSError:
            pass
        os.replace(tmp, path)
        try:
            _dir_fd = os.open(os.path.dirname(path) or ".", os.O_RDONLY)
            try:
                os.fsync(_dir_fd)
            finally:
                os.close(_dir_fd)
        except OSError:
            pass
    except TypeError as e:
        # Why: PersistentState.question_fingerprints stores words as list (JSON-safe),
        # but a future caller might accidentally pass a set. Catch TypeError explicitly
        # so the error is clear rather than silently failing.
        _proto(f"WARNING: state contains non-serialisable value ({e}), not saving")
    except OSError as e:
        _proto(f"WARNING: could not save state ({e})")


def _find_in_progress_without_session_id(project_root: str, deps: "OrchestratorDeps") -> "list[str]":
    """Return task IDs that are in_progress but have no session_id in frontmatter.

    Used by AC-22 to detect manually-started tasks that the orchestrator should skip.
    """
    req_dir = os.path.join(project_root, "requirements_tasks")
    result = deps.run_subprocess(
        ["grep", "-rl", "^status: in_progress", req_dir],
        capture_output=True,
        text=True,
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


def write_session_output(outputs_dir: str, session_id: str, content: str, deps: "OrchestratorDeps") -> None:
    """Write cleaned session stdout to automation/session_outputs/<uuid>.txt."""
    deps.makedirs(outputs_dir)
    path = os.path.join(outputs_dir, f"{session_id}.txt")
    try:
        deps.write_file(path, content)
    except OSError as e:
        _proto(f"WARNING: could not write session output ({e})")


def finalize_session_record(
    session_record: dict[Any, Any],
    result: "subprocess.CompletedProcess[Any]",
    output_key: str,
    account: str,
    run_data: "RunData",
    deps: "OrchestratorDeps",
    label: "str | None" = None,
) -> str:
    """Apply common post-session bookkeeping. Returns cleaned stdout.

    Why: every session-launching call site repeated the same finalization steps
    (record end+exit_code, capture hung-kill metadata, strip the hook footer,
    persist the output file, record an excerpt, register the session and the
    account). Centralizing that block keeps the three resume-shaped paths short
    and ensures they cannot drift apart.
    """
    session_record["end"] = deps.get_now_local()
    session_record["exit_code"] = result.returncode

    kill_reason = getattr(result, "kill_reason", None)
    if kill_reason:
        elapsed = getattr(result, "elapsed_secs", 0)
        if label:
            _proto(
                f"WARNING: session {label} killed "
                f"(reason: {kill_reason}) after {elapsed:.0f}s"
            )
        session_record["hung_killed"] = True
        session_record["kill_reason"] = kill_reason
        session_record["elapsed_secs"] = elapsed

    cleaned = strip_hook_footer(result.stdout)
    write_session_output(deps.outputs_dir, output_key, cleaned, deps)
    session_record["output_excerpt"] = cleaned[:1500]
    run_data.sessions.append(session_record)
    run_data.accounts_used.add(account)
    return cleaned


def classify_session_failure(result: "subprocess.CompletedProcess[Any]") -> "str | None":
    """Return the failure category of a session result, or None on success.

    Categories (checked in this order, most-permanent first):
      "perm_error"                   — account lacks access; never retry on this account
      "rate_limited"                 — rate limit hit; switch account and wait
      "prompt_too_long"              — JSONL exceeds the current model's context window; only
                                       meaningful on --resume. Treated the same as
                                       context_limit_no_entitlement: promote to Opus and reset
                                       for a fresh launch — same context-overflow problem at
                                       a different layer of the stack.
      "context_limit_no_entitlement" — Claude Code attempted to upgrade Sonnet to the 1M-context
                                       variant but the account lacks the "Extra usage" entitlement.
                                       Recoverable by promoting the task to Opus (1M baseline,
                                       no entitlement required) and relaunching fresh.
    """
    if result.returncode == 0:
        return None
    if any(p in result.stdout for p in PERM_ERROR_PATTERNS):
        return "perm_error"
    if "hit your" in result.stdout and "limit" in result.stdout:
        return "rate_limited"
    if "Prompt is too long" in result.stdout:
        return "prompt_too_long"
    if "Extra usage is required for 1M context" in result.stdout:
        return "context_limit_no_entitlement"
    return None


def apply_perm_error_to_account(
    account: str,
    state: "PersistentState",
    run_data: "RunData",
    num_accounts: int,
    deps: "OrchestratorDeps",
) -> None:
    """Disable an account for the rest of the run and rotate the index."""
    _proto(f"Account {account} has no access — disabling for this run")
    run_data.disabled_accounts.add(account)
    state.account_index = (state.account_index + 1) % max(num_accounts, 1)
    save_state(STATE_PATH, state, deps)


def apply_rate_limit_to_account(
    account: str,
    stdout: str,
    session_record: dict[Any, Any],
    state: "PersistentState",
    num_accounts: int,
    deps: "OrchestratorDeps",
) -> None:
    """Record rate-limit reset on state + session_record, rotate to next account."""
    reset_dt = parse_rate_limit_reset(stdout)
    session_record["rate_limited"] = True
    session_record["reset_at"] = reset_dt.isoformat() if reset_dt else None

    if reset_dt is None:
        _proto(
            f"WARNING: could not parse reset time, "
            f"falling back to {RATE_LIMIT_FALLBACK_SLEEP_SECS}s"
        )
        reset_dt = deps.get_now_utc() + timedelta(seconds=RATE_LIMIT_FALLBACK_SLEEP_SECS)

    state.rate_limited_until[account] = reset_dt.isoformat()
    state.account_index = (state.account_index + 1) % max(num_accounts, 1)
    save_state(STATE_PATH, state, deps)
    _proto(
        f"Account {account} rate-limited until "
        f"{reset_dt.astimezone().strftime('%Y-%m-%d %H:%M %Z')}, rotating to next account"
    )


def update_goal_session_fields(goal_path: str, session_id: str, account: str, deps: "OrchestratorDeps") -> None:
    """Rewrite session_id and session_account in goal.md YAML frontmatter.

    Why: the previous implementation hand-rolled the frontmatter boundary
    detection. After TASK-PROC-051-04 (REQ-PROC-051 AC-08) the central helper
    splits the document and this function operates on the YAML region only,
    using line-by-line text rewrites to preserve the file's existing
    formatting and comments (a full ruamel round-trip would re-flow keys and
    drop blank lines that humans rely on).

    Failure is non-fatal — the session UUID is still passed via --session-id
    on the claude CLI, so a missed update only affects later orchestrator
    iterations that look up session_id from goal.md.
    """
    try:
        raw = deps.read_file(goal_path)
        raw_yaml, body = _split_frontmatter(raw)

        if not raw_yaml:
            # No frontmatter — preserve legacy best-effort behaviour: write
            # the file unchanged. The previous implementation also skipped
            # the inject in this case (because in_frontmatter never became True).
            deps.write_file(goal_path, raw)
            return

        yaml_lines = raw_yaml.split("\n")
        new_yaml_lines: list[str] = []
        session_id_written = False
        session_account_written = False
        for line in yaml_lines:
            if line.startswith("session_id:"):
                new_yaml_lines.append(f"session_id: {session_id}")
                session_id_written = True
                continue
            if line.startswith("session_account:"):
                new_yaml_lines.append(f"session_account: {account}")
                session_account_written = True
                continue
            new_yaml_lines.append(line)

        if not session_id_written:
            new_yaml_lines.append(f"session_id: {session_id}")
        if not session_account_written:
            new_yaml_lines.append(f"session_account: {account}")

        new_yaml = "\n".join(new_yaml_lines)
        deps.write_file(goal_path, f"---\n{new_yaml}\n---\n{body}")
    except OSError as e:
        _proto(f"WARNING: could not update goal.md ({e}) — continuing anyway")


def make_session_record(
    *,
    account: str,
    task_id: "str | None",
    is_resume: bool,
    deps: "OrchestratorDeps",
    **extra: Any,
) -> dict[Any, Any]:
    """Build a session_record dict with the standard fields all launch sites share.

    Why: five launch paths used to hand-roll this dict with slightly different
    shapes (fresh_for_answered_question, recovery_from, session_uuid). Each new
    field had to be remembered at every relevant site. Centralizing the common
    fields keeps the call sites readable and the standard structure consistent
    while still allowing each path to add its own variant fields via **extra.
    """
    record = {
        "start": deps.get_now_local(),
        "account": account,
        "task_id": task_id or "unknown",
        "is_resume": is_resume,
    }
    record.update(extra)
    return record


@contextmanager
def active_session(state: "PersistentState", session_uuid: str, deps: "OrchestratorDeps") -> Iterator[None]:
    """Mark a session as active in state.json for the duration of the with-block.

    Why: state.active_session MUST be cleared after every launch — including when
    the launcher raises (KeyboardInterrupt, unhandled OSError, anything else).
    Previously, five call sites hand-rolled the set/save/launch/clear/save pattern,
    and any exception from the launcher left an orphaned UUID in state.json until
    the next orchestrator startup (where _reset_startup_state clears it). Using a
    context manager makes the clear unmissable.

    The yielded value is intentionally None — callers don't need a handle, the
    side effects on `state` are what matter.
    """
    state.active_session = session_uuid
    save_state(STATE_PATH, state, deps)
    start_mono = time.monotonic()
    try:
        yield
    finally:
        elapsed = time.monotonic() - start_mono
        # Why: external monitors (LLM monitoring loop, sleep_when_autorun_done.ps1)
        # could previously only infer session completion by counter increments on
        # the next loop iteration header. An explicit end-line makes the timeline
        # legible at a glance and distinguishes a clean exit from a silent crash.
        _proto(f"Session {session_uuid[:8]} ended (elapsed {elapsed:.0f}s)")
        state.active_session = None
        save_state(STATE_PATH, state, deps)


def register_session_in_goal(
    goal_path: "str | None",
    session_uuid: str,
    account: str,
    deps: "OrchestratorDeps",
) -> None:
    """Write session_id+account to goal.md and commit. No-op when goal_path is falsy.

    Why: every code path that launches a claude session MUST record the UUID in
    goal.md so (a) future iterations can resume it, and (b) scan_in_progress_without_session_id
    does not misclassify orchestrator-owned tasks as manual sessions. Centralizing
    this invariant prevents the bug where a new fresh-session path is added without
    remembering to update goal.md (which was previously the case for both
    requires_fresh_session and prompt_too_long recovery branches).
    """
    if not goal_path:
        return
    update_goal_session_fields(goal_path, session_uuid, account, deps)
    git_commit_best_effort(
        [goal_path],
        f"chore(automation): record session {session_uuid[:8]} in goal.md",
        deps,
    )


def _is_opus_recommended(fm: dict[Any, Any]) -> bool:
    """Read opus_recommended from YAML frontmatter, tolerating inline comments.

    Why: task-create writes `opus_recommended: true   # reason: ...` and the
    minimal frontmatter parser keeps the comment as part of the string value.
    """
    raw = fm.get("opus_recommended")
    if raw is None:
        return False
    if isinstance(raw, bool):
        return raw
    return str(raw).split("#", 1)[0].strip().lower() == "true"


def pick_next_task_for_session(deps: "OrchestratorDeps") -> "tuple[str, str, bool] | None":
    """Pre-pick the next runnable task before launching a claude session.

    Why: deciding the model upfront (Sonnet vs Opus) requires knowing the task
    before --model is set on the claude CLI. Mid-session model switching is not
    supported. Returns (goal_path, task_id, is_opus) or None if no runnable task
    can be parsed — caller falls back to the legacy "do next task" prompt.
    """
    next_result = deps.run_subprocess(
        ["python3", "scripts/tasks/next_tasks.py", "--count", "4"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    # Pattern matches "1. [TASK-XXX-NN-NN]" lines printed by next_tasks.py
    entries = re.findall(
        r"^\s*\d+\.\s+\[(TASK-[A-Z0-9\-]+)\][^\n]*\n(?:[^\n]*\n)*?\s+Path:\s+(\S+)",
        next_result.stdout,
        re.MULTILINE,
    )
    for task_id, path in entries:
        awaiting = deps.run_subprocess(
            ["python3", "scripts/tasks/is_awaiting_answer.py", "--task-id", task_id],
            capture_output=True,
            cwd=PROJECT_ROOT,
        )
        if awaiting.returncode != 0:
            continue
        abs_path = path if os.path.isabs(path) else os.path.join(PROJECT_ROOT, path)
        fm = read_yaml_frontmatter(abs_path)
        # Why: in_progress tasks belong to the resume path (find_active_task_goal +
        # find_resumable_session), never the fresh-launch path. next_tasks.py does
        # not exclude in_progress (EXCLUDED_STATUSES = TERMINAL_STATUSES | {"active"}),
        # so without this guard a manually-claimed task whose session_id was just
        # cleared could resurface here on the very next loop iteration.
        if fm.get("status") == "in_progress":
            continue
        return abs_path, task_id, _is_opus_recommended(fm)
    return None


def find_active_task_goal(project_root: str, deps: "OrchestratorDeps") -> "str | None":
    """Find the goal.md of the currently in_progress task via grep."""
    req_dir = os.path.join(project_root, "requirements_tasks")
    result = deps.run_subprocess(
        ["grep", "-rl", "^status: in_progress", req_dir],
        capture_output=True,
        text=True,
    )
    for path in result.stdout.strip().splitlines():
        if not path.endswith("goal.md"):
            continue
        fm = read_yaml_frontmatter(path)
        if fm.get("status") != "in_progress":
            continue
        # Why: skip in_progress tasks with no session_id — these were started by a
        # manual session (manual sessions never write session_id to goal.md). If we
        # returned them here, update_goal_session_fields would overwrite the empty
        # session_id with the orchestrator's new UUID, hijacking the manual session's
        # task. The earlier scan_in_progress_without_session_id only logs a warning;
        # this check is the actual block. See automation/orchestrate.log entries on
        # 2026-05-14 20:51:38 → 20:52:16 for the hijack of TASK-PROC-049-01.
        if not fm.get("session_id", "").strip():
            continue
        # Why: skip tasks waiting for a human answer — the same guard used in
        # find_resumable_in_progress_task (line 674). Without this check,
        # every fresh session launch overwrites the session_id of a pending-question
        # task, causing the new session to "own" it and re-execute it instead of
        # moving on to the next available task. Root cause of TASK-PROC-042-09
        # running three times. See automation/bugfix_plan_orchestrator_task_hijack.md
        task_id = fm.get("task_id", "")
        if task_id:
            question_path = os.path.join(FEEDBACK_DIR, task_id, "question.md")
            answer_path   = os.path.join(FEEDBACK_DIR, task_id, "answer.md")
            if os.path.exists(question_path) and answer_is_empty(answer_path):
                continue
        return cast("str | None", path)
    return None


# --- Section 4: Subprocess adapters ---


def git_commit_best_effort(
    files: "list[str]",
    message: str,
    deps: "OrchestratorDeps",
    update_dirs: "list[str] | None" = None,
) -> None:
    """Stage and commit files. Non-fatal — logs WARNING on failure.

    Why: write_report() returns the path it wrote (fixing the filename-collision bug
    from the pre-rewrite code where datetime.now() was called twice). Here we receive
    the exact path so git add is deterministic.
    Handles mixed absolute paths and glob patterns — absolute paths are globbed as-is,
    relative patterns are rooted at PROJECT_ROOT.
    update_dirs: optional list of directories to stage with `git add -u` (picks up
    modifications AND deletions of already-tracked files, e.g. report cleanup).
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_session_orchestrator/tasks/2026-04-10_impl_implement-orchestrator-monitoring-improvements/
            plans_and_protocols/2026-04-10_01_plan_orchestrator-monitoring-improvements.md#ac-23
    """
    try:
        # Stage directories with -u first (captures modifications + deletions)
        for d in (update_dirs or []):
            abs_dir = d if os.path.isabs(d) else os.path.join(PROJECT_ROOT, d)
            deps.run_subprocess(
                ["git", "add", "-u", abs_dir],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
            )

        # Stage explicit files / glob patterns
        expanded = []
        for pattern in files:
            if os.path.isabs(pattern):
                expanded.extend(deps.glob_files(pattern))
            else:
                expanded.extend(deps.glob_files(os.path.join(PROJECT_ROOT, pattern)))
        if expanded:
            deps.run_subprocess(
                ["git", "add", *expanded],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
            )

        # Nothing was staged by this call — skip diff check and commit entirely.
        if not update_dirs and not expanded:
            return

        # Why: git commit exits 1 with "nothing to commit" when files are already
        # tracked and unchanged — check staged diff first to avoid a spurious WARNING.
        staged = deps.run_subprocess(
            ["git", "diff", "--cached", "--quiet"],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
        )
        if staged.returncode == 0:
            return  # nothing staged, skip commit silently
        deps.run_subprocess(
            ["git", "commit", "-m", message],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        _proto(f"WARNING: git commit failed ({e})")
    except Exception as e:
        _proto(f"WARNING: git commit failed unexpectedly ({e})")


def run_normal_session(
    env: dict[Any, Any],
    session_uuid: str,
    hung_check_interval: int,
    hung_timeout_secs: int,
    session_timeout_secs: int,
    stop_flag: dict[Any, Any],
    deps: "OrchestratorDeps",
    model: "str | None" = None,
    task_id: "str | None" = None,
) -> subprocess.CompletedProcess[Any]:
    """Launch a new claude session with pre-assigned UUID.

    Why: --session-id names the JSONL file with the pre-assigned UUID so we can
    locate the session storage later. -p auto-exits after completing the prompt.
    The model and task are decided BEFORE launch — model switching mid-session
    forces the new model to re-read all accumulated context at full price.
    """
    do_clause = f"Then do {task_id}." if task_id else "Then do next task."
    prompt = (
        "Invoke the claude-automated-mode skill immediately "
        "(CLAUDE_AUTOMATED_MODE=1 is active and automation/.automated_mode exists). "
        + do_clause
    )
    cmd = ["claude", "--dangerously-skip-permissions"]
    if model:
        cmd.extend(["--model", model])
    cmd.extend(["--session-id", session_uuid, "-p", prompt])
    try:
        return run_session_with_hung_detection(
            cmd, env, session_uuid,
            hung_check_interval, hung_timeout_secs, session_timeout_secs,
            stop_flag, deps,
        )
    except OSError as e:
        raise OSError(f"claude binary not found in PATH: {e}") from e


def run_resume_session(
    env: dict[Any, Any],
    session_id: str,
    archive_path: str,
    hung_check_interval: int,
    hung_timeout_secs: int,
    session_timeout_secs: int,
    stop_flag: dict[Any, Any],
    deps: "OrchestratorDeps",
    model: "str | None" = None,
) -> subprocess.CompletedProcess[Any]:
    """Resume a paused claude session with the provided answer.

    Why: --resume <uuid> continues the JSONL session; -p delivers the archive path
    (feedback-checkpoint file in plans_and_protocols/) rather than the raw answer.
    Passing the archive path avoids CLI option-parsing failures when the answer starts
    with "---" (YAML frontmatter), keeps the -p argument short, and lets the session
    read the combined Q+A record with full context via the Read tool.
    The CLAUDE_CONFIG_DIR must match the original account so the session file is found.
    The model must match what the original session was launched with — the CLI does
    not infer it from the JSONL, so omitting --model falls back to the global default
    (e.g. sonnet) and an opus-sized conversation will exceed that smaller context
    window and fail with "Prompt is too long".
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_feedback_pause_resume/tasks/2026-06-02_impl_archive-answered-feedback-to-task-protocols/
            goal.md#ac-09
    """
    # Why: AC-09 preamble tells the resumed session where the archived Q+A lives,
    # so it does not attempt to read from pending_feedback/ (which will be deleted
    # after clean exit) and has a stable path for future reference.
    prompt = (
        f"[Answer archived at: {archive_path}]\n"
        f"Your pending question has been answered. "
        f"Read the archived record at {archive_path} and continue the task."
    )
    cmd = ["claude", "--dangerously-skip-permissions"]
    if model:
        cmd.extend(["--model", model])
    cmd.extend(["--resume", session_id, "-p", prompt])
    try:
        return run_session_with_hung_detection(
            cmd, env, session_id,
            hung_check_interval, hung_timeout_secs, session_timeout_secs,
            stop_flag, deps,
        )
    except OSError as e:
        raise OSError(f"claude binary not found in PATH: {e}") from e


def run_fresh_session_with_answer(
    env: dict[Any, Any],
    session_uuid: str,
    goal_path: str,
    archive_path: str,
    hung_check_interval: int,
    hung_timeout_secs: int,
    session_timeout_secs: int,
    stop_flag: dict[Any, Any],
    deps: "OrchestratorDeps",
    model: "str | None" = None,
) -> subprocess.CompletedProcess[Any]:
    """Launch a new session to continue a task whose original session had no resume UUID.

    Why: when session_id is "NEW_SESSION_REQUIRED" (written by terminate_session.sh
    when $CLAUDE_SESSION_ID was empty), there is no JSONL file to --resume.
    Instead, we start a fresh session and pass the goal.md path + the archive path
    (feedback-checkpoint file in plans_and_protocols/) so the session can read the
    archived Q+A record and proceed from where it paused.
    The archive path (not the raw answer file) is referenced to avoid CLI
    option-parsing failures when the answer starts with "---" (YAML frontmatter)
    and to point the session at the stable, combined record.
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_feedback_pause_resume/tasks/2026-06-02_impl_archive-answered-feedback-to-task-protocols/
            goal.md#ac-09
    """
    # Why: AC-09 preamble included on fresh sessions too so the session always
    # has a consistent pointer to the archived Q+A regardless of resume path.
    prompt = (
        "Invoke the claude-automated-mode skill immediately "
        "(CLAUDE_AUTOMATED_MODE=1 is active and automation/.automated_mode exists). "
        f"Then do {goal_path}. "
        "Context: a pending question was already answered. "
        f"[Answer archived at: {archive_path}]\n"
        f"Read the archived record at {archive_path} and proceed from there."
    )
    cmd = ["claude", "--dangerously-skip-permissions"]
    if model:
        cmd.extend(["--model", model])
    cmd.extend(["--session-id", session_uuid, "-p", prompt])
    try:
        return run_session_with_hung_detection(
            cmd, env, session_uuid,
            hung_check_interval, hung_timeout_secs, session_timeout_secs,
            stop_flag, deps,
        )
    except OSError as e:
        raise OSError(f"claude binary not found in PATH: {e}") from e


def _resolve_task_goal_and_model(
    task_id: str, deps: "OrchestratorDeps"
) -> "tuple[str, str | None]":
    """Find a task's goal.md path and decide its model from frontmatter.

    Returns (goal_path, model). Falls back to (task_id, None) when the file
    cannot be located — preserves prior behaviour where the prompt still includes
    a recognizable identifier.
    """
    req_dir = os.path.join(PROJECT_ROOT, "requirements_tasks")
    grep_result = deps.run_subprocess(
        ["grep", "-rl", f"^task_id: {task_id}", req_dir, "--include=goal.md"],
        capture_output=True, text=True,
    )
    goal_path = next(
        (p for p in grep_result.stdout.strip().splitlines() if p.endswith("goal.md")),
        None,
    )
    if not goal_path:
        return task_id, None
    fm = read_yaml_frontmatter(goal_path)
    model = "opus" if _is_opus_recommended(fm) else None
    return goal_path, model


def _archive_feedback_checkpoint(
    task_id: str,
    folder_path: str,
    goal_path: str,
    deps: "OrchestratorDeps",
) -> str:
    """Merge question.md + answer.md into a feedback-checkpoint file in plans_and_protocols/.

    Returns the absolute path of the written checkpoint file, or empty string on failure.

    Why: archiving before the session runs means the resumed session is told where the
    record lives (AC-09 preamble), and the record exists even if the session crashes.
    Deleting pending_feedback/ still happens only on clean exit (AC-06).
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_feedback_pause_resume/tasks/2026-06-02_impl_archive-answered-feedback-to-task-protocols/
            goal.md#acceptance-criteria
    """
    question_path = os.path.join(folder_path, "question.md")
    answer_path_inner = os.path.join(folder_path, "answer.md")

    if not (deps.file_exists(question_path) and deps.file_exists(answer_path_inner)):
        return ""

    # Why: _resolve_task_goal_and_model returns the task_id string as fallback when no
    # goal.md is found. os.path.dirname("TASK-FOO") == "" so the join resolves relative
    # to cwd, writing the checkpoint to the project root. Guard here so a missing task
    # always fails visibly rather than silently polluting the repo root.
    if not os.path.isabs(goal_path):
        return ""

    question_text = deps.read_file(question_path)
    answer_text = deps.read_file(answer_path_inner)
    fm = read_yaml_frontmatter(question_path)
    skill_name = fm.get("skill", "")
    captured_at = deps.get_now_local().strftime("%Y-%m-%d")

    # Derive plans_and_protocols/ sibling dir from goal_path
    protocols_dir = os.path.join(os.path.dirname(goal_path), "plans_and_protocols")
    deps.makedirs(protocols_dir)

    # Why: render + filename are shared with the interactive writer via
    # scripts/util/feedback_checkpoint.py so the AC-06 format cannot drift between modes.
    checkpoint_path: str = resolve_checkpoint_path(protocols_dir, captured_at, deps.file_exists)
    content = render_checkpoint(
        CheckpointFields(
            skill=skill_name,
            mode="automated",
            decision="",
            task_id=task_id,
            captured_at=captured_at,
            question=question_text,
            answer=answer_text,
            rationale="(Automated archival — no rationale extracted.)",
        )
    )
    deps.write_file(checkpoint_path, content)
    return checkpoint_path


def _rewrite_question_session_id(
    question_path: str, new_session_id: str, deps: "OrchestratorDeps"
) -> None:
    """Rewrite the session_id field in a question.md frontmatter.

    Why: when a resume permanently fails (e.g. JSONL too large for the model's
    context window), point future iterations and future orchestrator runs at the
    fresh-session path by replacing the obsolete UUID with the NEW_SESSION_REQUIRED
    sentinel. Without this, every retry would re-attempt the doomed --resume.
    """
    try:
        raw = deps.read_file(question_path)
    except OSError as e:
        _proto(f"WARNING: could not read {question_path} ({e}) — skipping rewrite")
        return

    # Why: migrated to the central helper (TASK-PROC-051-04 / REQ-PROC-051 AC-08).
    # We still do a line-by-line rewrite of the YAML region (rather than a full
    # ruamel round-trip) so the file's existing formatting and any inline
    # comments are preserved verbatim — humans curate question.md by hand.
    raw_yaml, body = _split_frontmatter(raw)

    rewrote = False
    if raw_yaml:
        yaml_lines = raw_yaml.split("\n")
        new_yaml_lines: list[str] = []
        for line in yaml_lines:
            if line.startswith("session_id:"):
                new_yaml_lines.append(f"session_id: {new_session_id}")
                rewrote = True
                continue
            new_yaml_lines.append(line)
        new_content = "---\n" + "\n".join(new_yaml_lines) + f"\n---\n{body}"
    else:
        new_content = raw

    if not rewrote:
        _proto(f"WARNING: no session_id line found in {question_path} — skipping rewrite")
        return
    try:
        deps.write_file(question_path, new_content)
    except OSError as e:
        _proto(f"WARNING: could not write {question_path} ({e})")


class PromoteResult(Enum):
    """Outcome of _promote_task_to_opus_for_context_limit.

    Why: callers used to distinguish only "rewritten" vs "not rewritten" via bool,
    but the three not-rewritten reasons have different semantics:
      - ALREADY_AT_MAX is normal expected behaviour ("can't promote opus further").
      - NO_PROMOTABLE_FIELD or UNREADABLE indicate the frontmatter is malformed or
        the file is missing — caller may want to surface this more loudly than a
        routine "already at max" log line.
    All three currently lead to the same caller action (skip recovery, mark task
    exhausted) but the distinction is preserved for future-proofing and clearer logs.
    """
    PROMOTED = "promoted"             # opus_recommended flipped from false → true
    ALREADY_AT_MAX = "already_at_max" # task is already opus_recommended=true
    NO_PROMOTABLE_FIELD = "no_promotable_field"  # frontmatter missing opus_recommended line
    UNREADABLE = "unreadable"         # goal.md not located, or read/write error

    @property
    def is_success(self) -> bool:
        """True only when the promotion actually rewrote goal.md."""
        return self == PromoteResult.PROMOTED


def _promote_task_to_opus_for_context_limit(
    task_id: str, deps: "OrchestratorDeps"
) -> "PromoteResult":
    """Set opus_recommended=true and reset for fresh launch after a context-overflow failure.

    Why: two distinct error signatures both mean "this conversation is too big for the current
    model's context window":
      - "Extra usage is required for 1M context": Claude Code tried to upgrade Sonnet to the
        1M-context variant; the account lacks the entitlement.
      - "Prompt is too long": the resumed JSONL exceeds the model's effective window on the
        first turn of --resume.
    Opus has a 1M-context baseline that requires no entitlement, so promoting the task gives
    it ~5x the headroom of Sonnet. We also clear session_id and reset status to pending —
    the resume path reuses the original session's model, so a fresh launch is required to
    actually pick up the new model from goal.md frontmatter, and the lost JSONL is acceptable
    because it was the cause of the overflow in the prompt_too_long case anyway.

    Returns a PromoteResult; only PROMOTED means the recovery can proceed. Callers
    should treat any other value as "skip recovery, mark task exhausted" — see
    PromoteResult docstring for why the non-success values are kept distinct.
    """
    goal_path, current_model = _resolve_task_goal_and_model(task_id, deps)
    if not goal_path or goal_path == task_id:
        _proto(f"WARNING: cannot locate goal.md for {task_id} — context-limit recovery skipped")
        return PromoteResult.UNREADABLE

    if current_model == "opus":
        _proto(
            f"{task_id} is already opus_recommended — cannot promote further; "
            f"context overflow appears genuine. Skipping recovery for this run"
        )
        return PromoteResult.ALREADY_AT_MAX

    try:
        raw = deps.read_file(goal_path)
    except OSError as e:
        _proto(f"WARNING: could not read {goal_path} ({e}) — context-limit recovery skipped")
        return PromoteResult.UNREADABLE

    # Why: migrated to the central helper (TASK-PROC-051-04 / REQ-PROC-051 AC-08).
    # We rewrite the YAML region line-by-line (rather than via a full ruamel
    # round-trip) to preserve goal.md's existing formatting and inline comments
    # — only the three target fields (opus_recommended, session_id, status)
    # are touched.
    raw_yaml, body = _split_frontmatter(raw)
    if not raw_yaml:
        _proto(f"WARNING: no opus_recommended line found in {goal_path} — context-limit recovery skipped")
        return PromoteResult.NO_PROMOTABLE_FIELD

    yaml_lines = raw_yaml.split("\n")
    new_yaml_lines: list[str] = []
    rewrote_opus = False
    for line in yaml_lines:
        if line.startswith("opus_recommended:"):
            new_yaml_lines.append("opus_recommended: true  # promoted after context_limit_no_entitlement")
            rewrote_opus = True
            continue
        if line.startswith("session_id:"):
            new_yaml_lines.append('session_id: ""')
            continue
        if line.startswith("status:"):
            new_yaml_lines.append("status: pending")
            continue
        new_yaml_lines.append(line)

    if not rewrote_opus:
        _proto(f"WARNING: no opus_recommended line found in {goal_path} — context-limit recovery skipped")
        return PromoteResult.NO_PROMOTABLE_FIELD

    new_content = "---\n" + "\n".join(new_yaml_lines) + f"\n---\n{body}"

    try:
        deps.write_file(goal_path, new_content)
    except OSError as e:
        _proto(f"WARNING: could not write {goal_path} ({e})")
        return PromoteResult.UNREADABLE

    _proto(f"Promoted {task_id} to opus_recommended=true and reset to pending after context_limit_no_entitlement error")
    return PromoteResult.PROMOTED


JSONL_BASE = (
    "/home/vscode/.ccs/shared/context-groups/default/projects"
    "/-workspaces-private-mood-tracker-flutter-app"
)


def run_session_with_hung_detection(
    cmd: list[Any],
    env: dict[Any, Any],
    session_uuid: str,
    hung_check_interval: int,
    hung_timeout_secs: int,
    session_timeout_secs: int,
    stop_flag: dict[Any, Any],
    deps: "OrchestratorDeps",
) -> subprocess.CompletedProcess[Any]:
    """Launch cmd via Popen and poll for hung-session conditions.

    Why: subprocess.run() blocks indefinitely — a hung claude session (no output,
    no child processes, JSONL stale) would block the orchestrator forever.
    This wrapper polls every hung_check_interval seconds and kills the process when:
    - stop_flag is set (graceful shutdown)
    - elapsed >= session_timeout_secs (hard ceiling, default 4 h)
    - JSONL mtime frozen AND no child processes for >= hung_timeout_secs (hung)
    Child process presence is the key signal: the 13-hour incident showed a session
    with stale JSONL but active dart/bash children — it was genuinely working.
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_session_orchestrator/tasks/2026-04-24_impl_hung-session-detection/
            plans_and_protocols/2026-04-24_01_plan_hung-session-detection.md
    """
    proc = deps.popen_subprocess(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    start_mono = time.monotonic()
    last_mtime: float | None = None
    stale_since_mono: float | None = None
    jsonl_path = os.path.join(JSONL_BASE, f"{session_uuid}.jsonl")
    next_heartbeat_mono = start_mono + _RATE_LIMIT_HEARTBEAT_SECS

    reason = "unknown"
    while True:
        deps.sleep(hung_check_interval)

        # (a) Graceful stop requested
        if stop_flag["requested"]:
            reason = "stop_requested"
            break

        # (b) Process already exited — collect output and return normally
        rc = proc.poll()
        if rc is not None:
            output, _ = proc.communicate(timeout=5)
            return subprocess.CompletedProcess(cmd, rc, stdout=output or "")

        # (c) Hard session ceiling
        elapsed = time.monotonic() - start_mono
        if elapsed >= session_timeout_secs:
            reason = "session_timeout"
            break

        # (c2) Heartbeat — keeps orchestrate.log fresh so sleep_when_autorun_done.ps1
        # does not mistake a long-running session for a crashed orchestrator.
        now_mono = time.monotonic()
        if now_mono >= next_heartbeat_mono:
            _proto(
                f"Session {session_uuid[:8]} still running — "
                f"{elapsed / 60:.0f} min elapsed",
                flush=True,
            )
            next_heartbeat_mono = now_mono + _RATE_LIMIT_HEARTBEAT_SECS

        # (d) JSONL mtime stale-check
        try:
            current_mtime: float | None = deps.get_mtime(jsonl_path)
        except FileNotFoundError:
            current_mtime = None

        if current_mtime is None:
            # JSONL doesn't exist yet — session may just be starting; don't count as stale
            stale_since_mono = None
        elif last_mtime is None or current_mtime != last_mtime:
            # Mtime changed → session is making progress
            last_mtime = current_mtime
            stale_since_mono = None
        else:
            # Mtime frozen and file exists — check for child processes
            child_result = deps.run_subprocess(
                ["ps", "--ppid", str(proc.pid), "--no-headers"],
                capture_output=True,
                text=True,
            )
            if child_result.stdout.strip():
                # Children present — session is actively working (e.g. running dart/bash)
                stale_since_mono = None
            else:
                # No children and JSONL frozen — start or continue stale timer
                if stale_since_mono is None:
                    stale_since_mono = time.monotonic()
                elif (time.monotonic() - stale_since_mono) >= hung_timeout_secs:
                    reason = "hung"
                    break

    # Kill sequence: SIGTERM first, then SIGKILL if still alive after 10 s
    elapsed = time.monotonic() - start_mono
    _proto(
        f"WARNING: session {session_uuid[:8]} appears hung "
        f"(reason: {reason}) after {elapsed:.0f}s — killing"
    )
    proc.send_signal(signal.SIGTERM)
    deps.sleep(10)
    if proc.poll() is None:
        proc.kill()
        rc = -9
    else:
        rc = -15
    output, _ = proc.communicate(timeout=5)
    result = subprocess.CompletedProcess(cmd, rc, stdout=output or "")
    result.kill_reason = reason  # type: ignore[attr-defined]  # custom attribute for caller inspection
    result.elapsed_secs = elapsed  # type: ignore[attr-defined]  # custom attribute extended dynamically here to record elapsed wall time so callers (run_session, ScratchpadResult assembly) can report kill latency without re-measuring
    return result


def find_resumable_session(
    project_root: str,
    feedback_dir: str,
    skip_session_ids: "set[Any] | None",
    deps: "OrchestratorDeps",
) -> "dict[Any, Any] | None":
    """Find an in_progress task whose previous session can be resumed.

    Returns dict with keys: goal_path, task_id, session_id, account
    Returns None if no resumable session exists.

    Only returns tasks that:
    - have status: in_progress in goal.md frontmatter
    - have a session_id set in goal.md frontmatter
    - do NOT have an unanswered question.md in pending_feedback/
      (those are handled by the existing answered/unanswered feedback paths)
    - are NOT in skip_session_ids (sessions that already failed this run)
    - do NOT have any still-open awaiting dependencies (awaiting items whose
      referenced tasks are not yet in a terminal status)

    Why: when a session exits 0 but the task is still in_progress (e.g. stopped at
    a confirmation point without writing question.md), the next orchestrator run should
    resume that exact session rather than launching "Do next task" which would
    re-encounter the in_progress task and ask the user to skip it.
    Source: automation/plans/2026-04-08_01_opus_plan_automation_improvements.md
    """
    _TERMINAL = {"completed", "cancelled", "superseded", "deprecated"}

    req_dir = os.path.join(project_root, "requirements_tasks")
    result = deps.run_subprocess(
        ["grep", "-rl", "^status: in_progress", req_dir],
        capture_output=True,
        text=True,
    )
    goal_paths = [p for p in result.stdout.strip().splitlines() if p.endswith("goal.md")]
    if not goal_paths:
        return None

    # Index: task_id → goal_path for all goal.md files — built lazily on first awaiting check.
    # Why: we need to look up the live status of awaiting dependencies; awaiting entries
    # are never deleted, so bool(awaiting) alone is not a reliable block signal.
    _task_index: dict[Any, Any] | None = None

    def _awaiting_still_open(awaiting_ids: list[Any]) -> bool:
        """Return True if any item in awaiting_ids is not yet in a terminal status."""
        nonlocal _task_index
        if not awaiting_ids:
            return False
        if _task_index is None:
            idx_result = deps.run_subprocess(
                ["grep", "-rl", "^task_id:", req_dir],
                capture_output=True,
                text=True,
            )
            _task_index = {}
            for gp in idx_result.stdout.strip().splitlines():
                if gp.endswith("goal.md"):
                    gfm = read_yaml_frontmatter(gp)
                    tid = gfm.get("task_id", "").strip()
                    if tid:
                        _task_index[tid] = gfm.get("status", "")
        for dep in awaiting_ids:
            if dep and _task_index.get(dep, "") not in _TERMINAL:
                return True
        return False

    for goal_path in goal_paths:
        fm = read_yaml_frontmatter(goal_path)
        if fm.get("status") != "in_progress":
            continue
        session_id = fm.get("session_id", "").strip()
        task_id = fm.get("task_id", "")
        account = fm.get("session_account", "").strip()

        if not session_id:
            continue

        # Skip sessions that already failed this run to prevent retry loops
        if skip_session_ids and session_id in skip_session_ids:
            continue

        # Skip if any awaiting dependency is not yet in a terminal status.
        # Why: awaiting items stay in the list after completion; we check live status.
        awaiting = fm.get("awaiting", [])
        if not isinstance(awaiting, list):
            awaiting = [awaiting] if awaiting else []
        if _awaiting_still_open(awaiting):
            continue

        # Skip if there's already an unanswered question — handled by existing paths
        task_feedback_dir = os.path.join(feedback_dir, task_id)
        question_path = os.path.join(task_feedback_dir, "question.md")
        answer_path = os.path.join(task_feedback_dir, "answer.md")
        if os.path.exists(question_path) and answer_is_empty(answer_path):
            continue

        return {
            "goal_path": goal_path,
            "task_id": task_id,
            "session_id": session_id,
            "account": account,
        }

    return None


def snapshot_in_progress_tasks(project_root: str, deps: "OrchestratorDeps") -> dict[Any, Any]:
    """Return {task_id: goal_path} for all tasks currently in_progress.

    Why: captured at run start so the health summary can compare initial vs
    final task states without re-reading historical data.
    """
    req_dir = os.path.join(project_root, "requirements_tasks")
    result = deps.run_subprocess(
        ["grep", "-rl", "^status: in_progress", req_dir],
        capture_output=True,
        text=True,
    )
    snapshot = {}
    for path in result.stdout.strip().splitlines():
        if not path.endswith("goal.md"):
            continue
        fm = read_yaml_frontmatter(path)
        if fm.get("status") != "in_progress":
            continue
        task_id = fm.get("task_id", "")
        if task_id:
            snapshot[task_id] = path
    return snapshot


# --- Section 5: Domain logic / dataclasses ---


@dataclass
class SessionRecord:
    """Typed record for a single launched session."""
    start: datetime
    end: "datetime | None" = None
    account: str = ""
    task_id: str = "unknown"
    session_uuid: str = ""
    is_resume: bool = False
    exit_code: "int | None" = None
    output_excerpt: str = ""
    rate_limited: bool = False
    reset_at: "str | None" = None


@dataclass
class RunData:
    """In-memory accumulator for the current run. Never written to state.json.

    Why: splitting in-memory run state (RunData) from disk-persisted state
    (PersistentState) prevents accidentally persisting transient data like
    disabled_accounts (which should reset each run) and makes the boundary
    between persistence and computation explicit.
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_session_orchestrator/tasks/2026-04-10_impl_implement-orchestrator-monitoring-improvements/
            plans_and_protocols/2026-04-10_02_plan_rewrite-architecture.md#3-state-management
    """
    start_time: datetime
    sessions: "list[dict[Any, Any]]" = field(default_factory=list)
    accounts_used: "set[str]" = field(default_factory=set)
    disabled_accounts: "set[str]" = field(default_factory=set)
    exhausted_resume_ids: "set[str]" = field(default_factory=set)
    resume_attempt_counts: "dict[str, int]" = field(default_factory=dict)   # session_id -> count (AC-21)
    exhausted_resume_tasks: "list[dict[Any, Any]]" = field(default_factory=list)       # AC-21 report [{task_id, session_id}]
    skipped_no_session_id: "list[str]" = field(default_factory=list)         # AC-22 report
    repeated_questions: "list[dict[Any, Any]]" = field(default_factory=list)           # AC-26 report [{task_id, similarity}]
    initial_in_progress: dict[Any, Any] = field(default_factory=dict)                  # task_id -> goal_path
    stop_time: "datetime | None" = None
    stop_reason: str = "manual"

    def mark_exhausted(
        self,
        *,
        session_id: str,
        task_id: "str | None" = None,
    ) -> None:
        """Mark a session (and optionally its task) as exhausted for this run.

        Why: two filters live in find_answered_feedback — by session_id and by
        task_id. Tasks whose stored session_id is the "NEW_SESSION_REQUIRED"
        sentinel can only be filtered by task_id (the sentinel isn't unique).
        Centralizing the dual-tracking prevents the bug where a caller adds to
        one set but forgets the other; see TASK-PROC-046-03 incident 2026-05-16.

        Pass task_id when the item should be skipped on future iterations of
        THIS run even if its session_id is the sentinel; omit it when only the
        specific session uuid is exhausted (e.g. a generic resume failure that
        could be retried next orchestrator run with the same session).
        """
        self.exhausted_resume_ids.add(session_id)
        if task_id is not None:
            self.exhausted_resume_tasks.append(
                {"task_id": task_id, "session_id": session_id}
            )


@dataclass
class OrchestratorDeps:
    """Injectable I/O and subprocess boundaries. Tests substitute fake implementations.

    Why: a dataclass of callables gives 100% mockability without the ceremony of
    abstract base classes. Each callable corresponds to exactly one I/O boundary,
    so tests can inject fakes for only the boundaries they care about while leaving
    others as the real implementation. Global patching (e.g. @patch("subprocess.run"))
    leaks into unrelated code and is fragile; this pattern is scoped to the orchestrator.
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_session_orchestrator/tasks/2026-04-10_impl_implement-orchestrator-monitoring-improvements/
            plans_and_protocols/2026-04-10_02_plan_rewrite-architecture.md#2-dependency-injection
    """
    # Subprocess
    run_subprocess: Callable[..., Any]     # default: subprocess.run
    popen_subprocess: Callable[..., Any]   # default: subprocess.Popen (used for hung-session polling)

    # Filesystem
    read_file: Callable[..., Any]          # default: open(path).read()
    write_file: Callable[..., Any]         # default: open(path, 'w').write(content)
    file_exists: Callable[..., Any]        # default: os.path.exists
    list_dir: Callable[..., Any]           # default: list(os.scandir(path))
    makedirs: Callable[..., Any]           # default: os.makedirs(path, exist_ok=True)
    glob_files: Callable[..., Any]         # default: glob.glob(pattern)
    get_mtime: Callable[..., Any]          # default: os.path.getmtime (injectable for hung-detection tests)

    # System
    get_now_utc: Callable[..., Any]        # default: lambda: datetime.now(timezone.utc)
    get_now_local: Callable[..., Any]      # default: datetime.now
    sleep: Callable[..., Any]             # default: time.sleep
    getpid: Callable[..., Any]             # default: os.getpid

    # Paths (injectable so tests can redirect writes away from production directories)
    # Why: finalize_session_record writes session output files; hardcoding OUTPUTS_DIR
    # caused pytest runs with real write_file lambdas to pollute automation/session_outputs/
    # with test artifacts. Making the path injectable lets test make_deps redirect to /tmp.
    outputs_dir: str = field(default_factory=lambda: OUTPUTS_DIR)


def check_and_update_question_fingerprint(
    task_id: str,
    question_body: str,
    state: PersistentState,
    run_data: RunData,
    deps: "OrchestratorDeps",
    is_awaiting_answer: bool = False,
) -> None:
    """Compare new question fingerprint with stored one; log WARNING if Jaccard >= 0.60.

    Updates state.question_fingerprints[task_id] in-place so the comparison
    is available on the next orchestrator run (via save_state / load_state).

    The 0.60 threshold (see _jaccard) catches near-identical re-phrasings while
    tolerating normal variation in phrasing.

    is_awaiting_answer: when True the task is correctly skipped (unanswered question),
    so a repeated fingerprint is expected — log as INFO instead of WARNING.
    """
    new_fp = compute_question_fingerprint(question_body)
    new_words = set(new_fp["words"])

    existing = state.question_fingerprints.get(task_id)

    if existing:
        old_words = set(existing.get("words", []))
        similarity = _jaccard(old_words, new_words)
        if similarity >= 0.60:
            if is_awaiting_answer:
                _proto_once(
                    f"unchanged:{task_id}",
                    f"INFO: {task_id} question unchanged (similarity {similarity:.2f})"
                    f" — still awaiting human answer, not a loop",
                )
            else:
                _proto(
                    f"WARNING: {task_id} appears to be asking the same question again "
                    f"(similarity {similarity:.2f}) — possible loop"
                )
                run_data.repeated_questions.append({
                    "task_id": task_id,
                    "similarity": round(similarity, 2),
                })

    # Update fingerprint (words stored as list for JSON serialisability)
    state.question_fingerprints[task_id] = {"words": list(new_words), "preview": new_fp["preview"]}


def write_report(reports_dir: str, run_data: RunData, accounts: list[Any], feedback_dir: str, deps: "OrchestratorDeps") -> str:
    """Generate automation/reports/YYYY-MM-DD_HH-MM_report.md.

    Why: returns the path it wrote to (rather than reconstructing it in the caller)
    to fix the pre-rewrite filename-collision bug where datetime.now() was called
    twice — once inside write_report and once in main() to derive report_path — and
    the minute could tick over between the two calls, causing write_health_summary()
    to append to a non-existent file.
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_session_orchestrator/tasks/2026-04-10_impl_implement-orchestrator-monitoring-improvements/
            plans_and_protocols/2026-04-10_02_plan_rewrite-architecture.md#8-risk-assessment (Risk 5)
    """
    now = deps.get_now_local()
    filename = now.strftime("%Y-%m-%d_%H-%M_report.md")
    path = os.path.join(reports_dir, filename)

    sessions = run_data.sessions
    completed = sum(1 for s in sessions if s.get("exit_code") == 0)
    paused = sum(1 for s in sessions if s.get("rate_limited"))
    failed = len(sessions) - completed - paused

    start_dt = run_data.start_time
    stop_dt = run_data.stop_time
    start_str = start_dt.strftime("%Y-%m-%d %H:%M") if isinstance(start_dt, datetime) else str(start_dt)
    stop_str = stop_dt.strftime("%Y-%m-%d %H:%M") if isinstance(stop_dt, datetime) else str(stop_dt)

    accounts_used = sorted(run_data.accounts_used)

    lines = [
        f"# Automation Run Report — {start_str}",
        "",
        f"**Started**: {start_str}",
        f"**Stopped**: {stop_str}",
        f"**Stop reason**: {run_data.stop_reason}",
        f"**Accounts used**: {', '.join(accounts_used)}",
        f"**Total sessions**: {len(sessions)} ({completed} completed, {paused} paused, {failed} failed)",
        "",
        "---",
    ]

    for i, s in enumerate(sessions, 1):
        task_label = s.get("task_id", "unknown")
        account = s.get("account", "?")
        start_s = s["start"].strftime("%H:%M") if isinstance(s.get("start"), datetime) else "?"
        end_s = s["end"].strftime("%H:%M") if isinstance(s.get("end"), datetime) else "?"
        exit_code = s.get("exit_code", "?")
        excerpt = s.get("output_excerpt", "")
        if len(excerpt) > 1500:
            excerpt = excerpt[:1500] + "\n[... truncated]"

        lines += [
            "",
            f"## Session {i} — {task_label} ({account})",
            f"**Started**: {start_s} | **Ended**: {end_s} | **Exit**: {exit_code}",
            excerpt,
            "",
            "---",
        ]

    # Pending feedback section
    pending = []
    if os.path.isdir(feedback_dir):
        for task_dir in deps.list_dir(feedback_dir):
            if not task_dir.is_dir():
                continue
            question_path = os.path.join(task_dir.path, "question.md")
            answer_path = os.path.join(task_dir.path, "answer.md")
            if os.path.exists(question_path) and answer_is_empty(answer_path):
                try:
                    content = deps.read_file(question_path)
                    parts = content.split("---", 2)
                    body = parts[2].strip() if len(parts) >= 3 else content.strip()
                    first_line = body.splitlines()[0] if body.splitlines() else "(no text)"
                    fm = read_yaml_frontmatter(question_path)
                    pending.append((fm.get("task_id", task_dir.name), first_line))
                except OSError:
                    pass

    if pending:
        lines += ["", "## Pending Feedback", ""]
        for task_id, question in pending:
            lines.append(f'- {task_id}: "{question}"')

    # Hung / timed-out sessions section
    hung_sessions = [s for s in sessions if s.get("hung_killed")]
    if hung_sessions:
        lines += ["", "### Hung / Timed-Out Sessions", ""]
        for s in hung_sessions:
            uuid_short = s.get("session_uuid", s.get("task_id", "?"))[:8]
            reason = s.get("kill_reason", "?")
            elapsed = s.get("elapsed_secs", 0)
            lines.append(f"- {s.get('task_id', '?')} (session {uuid_short}): reason={reason}, elapsed={elapsed:.0f}s")

    deps.makedirs(reports_dir)
    try:
        deps.write_file(path, "\n".join(lines) + "\n")
        _proto(f"Report written to {path}")
    except OSError as e:
        _proto(f"WARNING: could not write report ({e})")

    return path


def write_health_summary(
    report_path: str,
    run_data: RunData,
    initial_summary: dict[Any, Any],
    deps: "OrchestratorDeps",
) -> None:
    """Append a ## Health Summary section to the existing run report.

    Why: pure-Python quality check after every run — no LLM call, no tokens.
    Compares task states before/after the run, flags stuck sessions, lists
    pending questions, and gives an overall health verdict.
    Source: TASK-PROC-041-01-03 goal.md
    """
    lines = ["", "## Health Summary", ""]

    warnings = 0

    # --- Task progress ---
    lines.append("### Task Progress")
    lines.append("")

    # Re-snapshot current in_progress tasks
    current_in_progress = snapshot_in_progress_tasks(PROJECT_ROOT, deps)

    if not initial_summary:
        lines.append("No tasks were in_progress at run start.")
    else:
        for task_id, _goal_path in initial_summary.items():
            if task_id not in current_in_progress:
                lines.append(f"- {task_id}: completed \u2705")
            else:
                lines.append(f"- {task_id}: still in_progress \u26a0\ufe0f")
                warnings += 1

    lines.append("")

    # --- Stuck sessions ---
    # Sessions that exited 0 but whose task is still in_progress
    stuck = []
    for session in run_data.sessions:
        if session.get("exit_code") == 0 and not session.get("is_resume", False):
            task_id = session.get("task_id", "")
            if task_id and task_id != "unknown" and task_id in current_in_progress:
                stuck.append(task_id)
        elif session.get("exit_code") == 0 and session.get("is_resume", False):
            task_id = session.get("task_id", "")
            if task_id and task_id in current_in_progress:
                stuck.append(task_id)

    if stuck:
        lines.append("### Stuck Sessions (exited 0, task still in_progress)")
        lines.append("")
        for task_id in stuck:
            lines.append(f"- {task_id}: session exited 0 but task not completed \u26a0\ufe0f")
            warnings += 1
        lines.append("")

    # --- Pending questions ---
    pending_questions = get_unanswered_questions(FEEDBACK_DIR, deps)
    if pending_questions:
        lines.append("### Pending Questions")
        lines.append("")
        for q in pending_questions:
            lines.append(f"- {q['task_id']}: awaiting answer in pending_feedback/")
        lines.append("")

    # --- Skipped tasks (no session_id) --- AC-22
    skipped_no_sid = run_data.skipped_no_session_id
    if skipped_no_sid:
        lines.append("### Skipped Tasks (no session_id)")
        lines.append("")
        for tid in skipped_no_sid:
            lines.append(f"- {tid}: in_progress but no session_id \u2014 skipped")
        lines.append("")

    # --- Exhausted resumes --- AC-21
    exhausted = run_data.exhausted_resume_tasks
    if exhausted:
        lines.append("### Exhausted Resumes")
        lines.append("")
        for entry in exhausted:
            lines.append(f"- {entry['task_id']}: resume exhausted 3 attempts (session {entry['session_id']})")
        lines.append("")

    # --- Repeated questions --- AC-26
    repeated = run_data.repeated_questions
    if repeated:
        lines.append("### Repeated Questions")
        lines.append("")
        for entry in repeated:
            lines.append(f"- {entry['task_id']}: similarity {entry['similarity']} \u2014 possible loop")
        lines.append("")

    # --- Modified skills (review reminder) ---
    # Why: sessions may autonomously improve skills; surface uncommitted changes
    # so the user can review them after the run without having to run git status manually.
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", ".claude/skills/"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        modified_skills = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if modified_skills:
            lines.append("### Modified Skills (Review Recommended)")
            lines.append("")
            lines.append("The following skill files were changed by sessions this run and are uncommitted:")
            lines.append("")
            for path in modified_skills:
                lines.append(f"- `{path}`")
            lines.append("")
    except Exception:
        pass  # non-fatal

    # --- Verdict ---
    lines.append("### Overall Health")
    lines.append("")
    if pending_questions:
        verdict = f"\U0001f534 Blocked \u2014 {len(pending_questions)} unanswered question(s)"
    elif warnings > 0:
        verdict = f"\U0001f7e1 {warnings} warning(s) \u2014 review stuck tasks above"
    else:
        verdict = "\U0001f7e2 Healthy"
    lines.append(verdict)
    lines.append("")

    try:
        with open(report_path, "a") as f:
            f.write("\n".join(lines))
        _proto(f"Health summary appended to {report_path}")
    except OSError as e:
        _proto(f"WARNING: could not append health summary ({e})")


def find_answered_feedback(feedback_dir: str, deps: "OrchestratorDeps") -> list[Any]:
    """Scan pending_feedback/ for dirs with both question.md and answer.md.

    Returns list of dicts: {task_id, session_id, account, answer_path,
    folder_path, requires_fresh_session}.
    Skips entries with empty answer or malformed question.md frontmatter.
    "NEW_SESSION_REQUIRED" is accepted as a valid session_id (not malformed) —
    it signals that the original session bypassed task-start so no resume UUID
    exists; the orchestrator must launch a fresh session instead.
    """
    results: list[Any] = []
    if not os.path.isdir(feedback_dir):
        return results

    for task_dir in deps.list_dir(feedback_dir):
        if not task_dir.is_dir():
            continue
        question_path = os.path.join(task_dir.path, "question.md")
        answer_path = os.path.join(task_dir.path, "answer.md")

        if not (os.path.exists(question_path) and os.path.exists(answer_path)):
            continue

        frontmatter = read_yaml_frontmatter(question_path)
        # Why: "NEW_SESSION_REQUIRED" is a valid sentinel written by terminate_session.sh
        # when $CLAUDE_SESSION_ID was unavailable — it is NOT malformed; it triggers the
        # fresh-session resume path below rather than --resume <uuid>.
        sid = frontmatter.get("session_id", "")
        if not sid or not frontmatter.get("account"):
            _proto(f"WARNING: malformed question.md in {task_dir.path}, skipping")
            continue

        # Why: use answer_is_empty() (not a raw strip-check) so that the TEMPLATE_answer.md
        # placeholder is correctly treated as unanswered. A raw .strip() check passes the
        # template text through as a "real" answer, causing the orchestrator to resume the
        # session with the prohibition boilerplate as the answer content.
        if answer_is_empty(answer_path):
            _proto_once(
                f"template:{task_dir.name}",
                f"DEBUG: answer.md for {task_dir.name} is empty or template-only — skipping",
            )
            continue

        results.append(
            {
                "task_id": frontmatter.get("task_id", task_dir.name),
                "session_id": sid,
                "account": frontmatter["account"],
                "answer_path": answer_path,
                "folder_path": task_dir.path,
                "requires_fresh_session": sid == "NEW_SESSION_REQUIRED",
            }
        )

    return results


def get_unanswered_questions(feedback_dir: str, deps: "OrchestratorDeps") -> list[Any]:
    """Return list of dicts {task_id, session_id} for questions without a non-empty answer.md."""
    result: list[Any] = []
    if not os.path.isdir(feedback_dir):
        return result
    for task_dir in deps.list_dir(feedback_dir):
        if not task_dir.is_dir():
            continue
        question_path = os.path.join(task_dir.path, "question.md")
        answer_path = os.path.join(task_dir.path, "answer.md")
        if os.path.exists(question_path) and answer_is_empty(answer_path):
            # AC-20: log WARNING when answer.md exists but is whitespace-only
            if os.path.exists(answer_path) and os.path.getsize(answer_path) > 0:
                fm_name = read_yaml_frontmatter(question_path).get("task_id", task_dir.name)
                _proto_once(
                    f"whitespace:{fm_name}",
                    f"WARNING: answer.md for {fm_name} contains only whitespace "
                    f"— treating as unanswered",
                )
            fm = read_yaml_frontmatter(question_path)
            result.append({
                "task_id": fm.get("task_id", task_dir.name),
                "session_id": fm.get("session_id", ""),
            })
    return result


def new_question_written_for(task_id: str, feedback_dir: str, deps: "OrchestratorDeps") -> bool:
    """Return True if a new question.md exists without a non-empty answer.md.

    Used after resume to detect whether the session paused again with a new question.
    """
    task_dir = os.path.join(feedback_dir, task_id)
    question_path = os.path.join(task_dir, "question.md")
    answer_path = os.path.join(task_dir, "answer.md")
    return os.path.exists(question_path) and answer_is_empty(answer_path)


def cleanup_old_artifacts(
    reports_dir: str,
    outputs_dir: str,
    answered_dir: str,
    feedback_dir: str,
    deps: "OrchestratorDeps",
) -> None:
    """Keep only the most recent run's artifacts; delete everything older.

    Why: reports and session outputs accumulate indefinitely. One run of history
    is enough for post-mortem debugging; CCS session logs retain the full history.
    Runs at orchestrator start, before new sessions are launched.
    Session outputs for unanswered questions are protected from deletion so the
    developer retains context when they come back to answer.
    """
    # Collect session IDs that have unanswered questions — protect their outputs
    protected_ids = {q["session_id"] for q in get_unanswered_questions(feedback_dir, deps) if q["session_id"]}

    # Sort reports chronologically by filename (YYYY-MM-DD_HH-MM_report.md)
    report_files: list[Any] = []
    if os.path.isdir(reports_dir):
        report_files = sorted(
            [f for f in deps.list_dir(reports_dir) if f.name.endswith(".md")],
            key=lambda f: f.name,
        )

    # Delete all but the most recent report
    for entry in report_files[:-1]:
        try:
            os.unlink(entry.path)
            _proto(f"Cleanup: deleted old report {entry.name}")
        except OSError as e:
            _proto(f"WARNING: could not delete {entry.path} ({e})")

    # Session outputs older than the kept report belong to earlier runs — delete them,
    # but spare any whose UUID matches an unanswered question (developer still needs context).
    kept = report_files[-1] if report_files else None
    cutoff_mtime = kept.stat().st_mtime if kept else None
    if cutoff_mtime is not None and os.path.isdir(outputs_dir):
        for entry in deps.list_dir(outputs_dir):
            uid = entry.name.removesuffix(".txt")
            if uid in protected_ids:
                _proto(f"Cleanup: keeping {entry.name} (unanswered question)")
                continue
            if entry.stat().st_mtime < cutoff_mtime:
                try:
                    os.unlink(entry.path)
                    _proto(f"Cleanup: deleted old session output {entry.name}")
                except OSError as e:
                    _proto(f"WARNING: could not delete {entry.path} ({e})")

    # Answered feedback has been processed — no value in keeping it
    if os.path.isdir(answered_dir):
        for entry in deps.list_dir(answered_dir):
            if entry.is_dir():
                try:
                    shutil.rmtree(entry.path)
                    _proto(f"Cleanup: deleted answered feedback {entry.name}")
                except OSError as e:
                    _proto(f"WARNING: could not delete {entry.path} ({e})")


def next_available_account(
    accounts: list[Any],
    state: PersistentState,
    disabled_accounts: "set[Any] | None" = None,
    now_utc: "datetime | None" = None,
) -> tuple[Any, ...]:
    """Return (account_name, wait_until) for the next non-rate-limited account.

    wait_until is None if an account is available now.
    wait_until is a datetime if ALL accounts are rate-limited — sleep until then.
    Returns (None, None) if all accounts are permanently disabled (AC-19 fix).

    Why: the pre-rewrite code called min() on an empty sequence when all accounts
    were in disabled_accounts (not just rate-limited), raising ValueError. This fix
    returns the sentinel (None, None) which the caller interprets as
    stop_reason = "all_accounts_disabled" and breaks the main loop cleanly.
    Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
            feat_session_orchestrator/tasks/2026-04-10_impl_implement-orchestrator-monitoring-improvements/
            plans_and_protocols/2026-04-10_02_plan_rewrite-architecture.md#5-new-functions (AC-19)

    now_utc: optional override for the current UTC time. Why: the same call from
    process_answered_feedback / process_in_progress_resume also reads `deps.get_now_utc()`
    for account_blocked(); passing the same value keeps both checks on the same clock and
    fixes a test-stability bug where frozen-clock tests diverged from real wall-clock.
    """
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    rate_limited = state.rate_limited_until

    # Try each account starting from current index
    for i in range(len(accounts)):
        idx = (state.account_index + i) % len(accounts)
        acct = accounts[idx]
        if disabled_accounts and acct in disabled_accounts:
            continue
        if acct not in rate_limited:
            state.account_index = idx
            return acct, None
        reset_str = rate_limited[acct]
        try:
            reset_dt = datetime.fromisoformat(reset_str)
        except ValueError:
            # Corrupt reset time — treat as cleared
            del state.rate_limited_until[acct]
            state.account_index = idx
            return acct, None
        if now_utc >= reset_dt:
            # Reset window has passed — remove from exhausted map
            del state.rate_limited_until[acct]
            state.account_index = idx
            return acct, None

    # All accounts exhausted — find earliest reset time among accounts in use only.
    # Why: state.rate_limited_until may contain entries for accounts not in the current
    # --accounts list (e.g. "web" from a prior run with an already-expired reset time).
    # Including them causes `earliest` to be in the past → wait_secs ≤ 0 → no sleep →
    # the loop spins at full speed instead of waiting for the actual reset.
    remaining_rate_limited = {
        k: v for k, v in rate_limited.items()
        if k in accounts
        and not (disabled_accounts and k in disabled_accounts)
    }
    if not remaining_rate_limited:
        # All accounts are permanently disabled — nothing to wait for
        return None, None
    earliest = min(
        datetime.fromisoformat(t) for t in remaining_rate_limited.values()
    )
    return accounts[state.account_index % len(accounts)], earliest


def build_env(account: str, session_uuid: str = "") -> dict[Any, Any]:
    """Build subprocess environment with per-account CLAUDE_CONFIG_DIR.

    Why: CLAUDE_SESSION_ID and CLAUDE_SESSION_ACCOUNT are set so the AI session
    can read them via Bash and write them into question.md frontmatter — enabling
    the orchestrator to resume the correct session when feedback is provided.
    """
    env = {
        **os.environ,
        "CLAUDE_AUTOMATED_MODE": "1",
        "CLAUDE_CONFIG_DIR": f"{CCS_ROOT}/{account}",
        "CLAUDE_SESSION_ACCOUNT": account,
    }
    if session_uuid:
        env["CLAUDE_SESSION_ID"] = session_uuid
    else:
        env.pop("CLAUDE_SESSION_ID", None)
    return env


def unlink_if_exists(path: str) -> None:
    """Delete a file if it exists; silently ignore if already gone."""
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass
    except OSError as e:
        _proto(f"WARNING: could not remove {path} ({e})")


def _clear_inbox() -> None:
    """Clear any pending operator message from automation/inbox.md.

    Called when a task completes or just before a fresh session launches so
    messages meant for the current task do not leak into the next one.
    """
    inbox = _Path(os.path.join(PROJECT_ROOT, "automation", "inbox.md"))
    try:
        if inbox.exists() and inbox.stat().st_size > 0:
            inbox.write_text("")
    except OSError as e:
        _proto(f"WARNING: could not clear inbox ({e})")


# --- Section 6: Orchestrator class ---


class Orchestrator:
    """Encapsulates the main loop logic with injectable dependencies.

    Each method is a named loop step with a clear contract, making the
    ~25-line run_loop() body readable and the individual steps independently testable.
    """

    def __init__(self, deps: OrchestratorDeps) -> None:
        self.deps = deps

    def _read_external_stop_request(self) -> bool:
        """Re-read state.json[stop_requested] from disk without disturbing in-memory state.

        Why: an external process (claude-autorun stop, the user's editor) may set
        stop_requested=true in state.json. We must observe that write — but we
        cannot just trust self.state because self.state is our own write cache.
        Cheap (small file, polled once per loop iteration ~30-60s).
        Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
                feat_session_orchestrator/tasks/2026-04-30_impl_orchestrator-state-json-consolidation/
                plans_and_protocols/2026-04-30_01_plan_state-json-consolidation.md#step-6
        """
        try:
            if not self.deps.file_exists(STATE_PATH):
                return False
            raw = self.deps.read_file(STATE_PATH)
            data = json.loads(raw)
            return bool(data.get("stop_requested", False))
        except (json.JSONDecodeError, OSError):
            return False

    def check_stop_conditions(
        self,
        state: PersistentState,
        run_data: RunData,
        args: argparse.Namespace,
        stop_flag: dict[Any, Any],
        stop_at: "datetime | None",
        sessions_launched: int,
    ) -> "tuple[bool, str]":
        """Check all stop conditions. Returns (should_stop, reason). No I/O except state.json re-read."""
        if stop_flag["requested"]:
            state.stop_requested = True   # mirror to persistent state so save_state reflects it
            return True, "manual"
        # AC-38: replace sentinel file check with state.json re-read for external stop requests
        if self._read_external_stop_request():
            # Mirror to in-memory so subsequent checks short-circuit on stop_flag
            state.stop_requested = True
            return True, "manual"
        if stop_at and self.deps.get_now_local() >= stop_at:
            return True, "scheduled"
        if args.max_tasks is not None and sessions_launched >= args.max_tasks:
            _proto(f"Reached --max-tasks {args.max_tasks}, stopping")
            return True, "max_tasks"
        return False, ""

    def process_answered_feedback(
        self,
        state: PersistentState,
        run_data: RunData,
        args: argparse.Namespace,
        stop_flag: dict[Any, Any],
        sessions_launched: int,
    ) -> "tuple[str, int]":
        """Process one answered feedback item if available.

        Returns (decision, new_sessions_launched) where decision is:
        - "continue": an answer was processed, restart the loop
        - "next": no answered feedback, proceed to next step
        """
        # Why: filter out sessions already given up on this run — find_answered_feedback
        # does not know about exhausted_resume_ids, so without this filter the same
        # exhausted item is returned every loop iteration, causing an infinite print loop.
        # For requires_fresh_session items, session_id is "NEW_SESSION_REQUIRED" (not a
        # unique UUID), so we also exclude task_ids that are in exhausted_resume_tasks.
        exhausted_task_ids = {t["task_id"] for t in run_data.exhausted_resume_tasks}
        all_answered = find_answered_feedback(FEEDBACK_DIR, self.deps)
        answered = [
            a for a in all_answered
            if a["session_id"] not in run_data.exhausted_resume_ids
            and a["task_id"] not in exhausted_task_ids
        ]
        if all_answered:
            _proto(f"DEBUG: find_answered_feedback found {len(all_answered)} item(s): "
                  f"{[a['task_id'] for a in all_answered]}; after exhaustion filter: {len(answered)}")
        if not answered:
            _proto("DEBUG: no answered feedback to process")
            return "next", sessions_launched

        item = answered[0]  # process one at a time
        stored_account = item["account"]
        session_id = item["session_id"]

        # AC-21: track and limit resume attempts per session_id (or task_id for fresh sessions)
        # Why: "NEW_SESSION_REQUIRED" is not a unique session UUID — use task_id as the
        # attempt-count key so multiple answered fresh-session items don't share a counter.
        attempt_key = item["task_id"] if item.get("requires_fresh_session") else session_id
        attempt = run_data.resume_attempt_counts.get(attempt_key, 0) + 1
        run_data.resume_attempt_counts[attempt_key] = attempt
        if attempt > 3:
            _proto(
                f"WARNING: resume of {item['task_id']} exhausted 3 attempts "
                f"— giving up this run"
            )
            run_data.mark_exhausted(task_id=item["task_id"], session_id=session_id)
            return "continue", sessions_launched

        # CCS account dirs are symlinks to shared session storage, so any available
        # account can resume any session JSONL or launch the fresh-recovery path.
        # If the account stored in question.md is currently rate-limited or disabled,
        # switch to an alternative rather than blindly launching and immediately
        # hitting the same limit (which previously burned every --max-tasks slot on
        # the same task — see TASK-PROC-046-03 incident 2026-05-16).
        disabled = run_data.disabled_accounts
        now_utc = self.deps.get_now_utc()
        rate_limited_map = state.rate_limited_until

        def account_blocked(acct: str) -> bool:
            if acct in disabled:
                return True
            if acct in rate_limited_map:
                try:
                    return cast("bool", now_utc < datetime.fromisoformat(rate_limited_map[acct]))
                except ValueError:
                    return False
            return False

        account = stored_account
        if stored_account not in self._accounts or account_blocked(stored_account):
            alt_account, wait_until = next_available_account(
                self._accounts, state, disabled, now_utc=now_utc,
            )
            if alt_account is None and wait_until is None:
                # All accounts permanently disabled — orchestrator can't make progress
                _proto("All accounts are permanently disabled — stopping")
                run_data.stop_reason = "all_accounts_disabled"
                # Roll back the attempt counter — we never actually tried
                run_data.resume_attempt_counts[attempt_key] = attempt - 1
                return "stop", sessions_launched
            if wait_until is not None:
                # All accounts exhausted — wait for earliest reset then re-enter loop
                wait_secs = (wait_until - now_utc).total_seconds()
                if wait_secs > 0:
                    _proto(
                        f"All accounts exhausted for resume of "
                        f"{item['task_id']} — waiting {wait_secs:.0f}s"
                    )
                    state.rate_limit_reached = True
                    state.next_wake_time = wait_until.astimezone().isoformat()
                    save_state(STATE_PATH, state, self.deps)
                    rate_limit_sleep(wait_secs, stop_flag, reset_dt=wait_until, poll_stop=self._read_external_stop_request)
                    state.rate_limit_reached = False
                    state.next_wake_time = None
                    save_state(STATE_PATH, state, self.deps)
                # Roll back the attempt counter — we never actually tried
                run_data.resume_attempt_counts[attempt_key] = attempt - 1
                return "continue", sessions_launched  # Re-enter loop after wait
            account = alt_account
            if stored_account != account:
                _proto(
                    f"Switching resume account {stored_account} → "
                    f"{account} (shared session storage)"
                )

        if item.get("requires_fresh_session"):
            # Why: session_id is "NEW_SESSION_REQUIRED" — no JSONL file to --resume.
            # Find the task's goal.md and launch a fresh session with the answer as context.
            session_uuid = str(uuid.uuid4())
            env = build_env(account, session_uuid)

            goal_path, fresh_model = _resolve_task_goal_and_model(item["task_id"], self.deps)

            # Why: archive before launching so the preamble path (AC-09) is valid when
            # the session reads it, and the record persists even if the session crashes.
            archive_path = _archive_feedback_checkpoint(
                item["task_id"], item["folder_path"], goal_path, self.deps
            )

            model_note = f" model={fresh_model}" if fresh_model else ""
            _proto(
                f"Launching fresh session for {item['task_id']} "
                f"(answered pending question) with account {account}{model_note}"
            )
            session_record: dict[Any, Any] = make_session_record(
                account=account,
                task_id=item["task_id"],
                is_resume=False,
                deps=self.deps,
                fresh_for_answered_question=True,
            )

            register_session_in_goal(goal_path, session_uuid, account, self.deps)
            with active_session(state, session_uuid, self.deps):
                result = run_fresh_session_with_answer(
                    env, session_uuid, goal_path, archive_path,
                    args.hung_check_interval, args.hung_timeout * 60, args.session_timeout,
                    stop_flag, self.deps, model=fresh_model,
                )
            output_key = session_uuid
        else:
            env = build_env(account)

            # Resolve model from the task's goal.md so resume launches with the
            # same model the original session used. Without this, --resume falls
            # back to the global CLI default and an opus-sized JSONL can blow
            # past sonnet's effective context window.
            resume_goal_path, resume_model = _resolve_task_goal_and_model(item["task_id"], self.deps)
            model_note = f" model={resume_model}" if resume_model else ""
            _proto(
                f"Resuming {item['task_id']} with account "
                f"{account}{model_note}"
            )
            session_record = make_session_record(
                account=account,
                task_id=item["task_id"],
                is_resume=True,
                deps=self.deps,
            )

            # Why: archive before resuming so the preamble path (AC-09) is valid when
            # the session reads it, and the record persists even if the session crashes.
            archive_path = _archive_feedback_checkpoint(
                item["task_id"], item["folder_path"], resume_goal_path, self.deps
            )

            with active_session(state, session_id, self.deps):
                result = run_resume_session(
                    env, session_id, archive_path,
                    args.hung_check_interval, args.hung_timeout * 60, args.session_timeout,
                    stop_flag, self.deps, model=resume_model,
                )
            output_key = session_id

        finalize_session_record(
            session_record, result, output_key, account, run_data, self.deps,
            label=item["task_id"],
        )

        # Classify infrastructure failures before deciding whether to move the
        # task to answered_feedback. Previously the answered-feedback path
        # treated *every* non-zero exit identically, so rate limits, perm
        # errors, and "Prompt is too long" silently fell into "new question or
        # failure" and got blindly retried up to the AC-21 cap.
        failure = classify_session_failure(result)

        if failure == "perm_error":
            _proto(
                f"Disabling for {item['task_id']}; "
                f"will retry with a different account next iteration"
            )
            apply_perm_error_to_account(account, state, run_data, len(self._accounts), self.deps)
            # Roll back the attempt counter — this was an infra failure, not a real try
            run_data.resume_attempt_counts[attempt_key] = attempt - 1
            return "continue", sessions_launched

        if failure == "rate_limited":
            apply_rate_limit_to_account(
                account, result.stdout, session_record, state, len(self._accounts), self.deps,
            )
            # Roll back the attempt counter — rate-limit didn't consume a real try
            # under AC-21, and doesn't consume a --max-tasks slot either (policy: only
            # successful sessions count; infra failures rotate accounts and try again).
            run_data.resume_attempt_counts[attempt_key] = attempt - 1
            return "continue", sessions_launched

        # Why: a Sonnet session whose conversation crosses ~200K tokens triggers
        # Claude Code to request the 1M-context Sonnet variant. Without the
        # account's "Extra usage" entitlement, Anthropic rejects the upgrade.
        # Promoting the task to Opus (1M baseline, no entitlement) and resetting
        # for a fresh launch lets the next iteration retry on a model that can
        # actually hold the conversation. Question.md session_id is rewritten to
        # NEW_SESSION_REQUIRED so the answered-feedback path stops trying to
        # --resume the doomed sonnet JSONL.
        if failure == "context_limit_no_entitlement":
            _proto(
                f"Resume of {item['task_id']} hit 1M-context entitlement "
                f"limit on sonnet — promoting to opus and resetting to fresh-launch path"
            )
            promoted = _promote_task_to_opus_for_context_limit(item["task_id"], self.deps)
            if not promoted.is_success:
                # Already on opus — promoting further is impossible. Don't rewrite
                # question.md to NEW_SESSION_REQUIRED (which would queue a doomed
                # fresh recovery next iteration); mark the task exhausted for this
                # run instead. The session itself doesn't count toward --max-tasks
                # (error, not a real session).
                run_data.mark_exhausted(task_id=item["task_id"], session_id=session_id)
                save_state(STATE_PATH, state, self.deps)
                return "continue", sessions_launched
            run_data.mark_exhausted(session_id=session_id)
            _rewrite_question_session_id(
                os.path.join(item["folder_path"], "question.md"),
                "NEW_SESSION_REQUIRED",
                self.deps,
            )
            save_state(STATE_PATH, state, self.deps)
            return "continue", sessions_launched

        # Why: "Prompt is too long" means the JSONL is past the model's context
        # window. Re-running --resume <uuid> against the same JSONL will fail
        # identically every time, so retrying within AC-21's 3-attempt budget
        # just wastes sessions. Rewrite the question.md session_id to the
        # NEW_SESSION_REQUIRED sentinel so this run (and any future orchestrator
        # restart) routes to the fresh-session path, and immediately launch one
        # fresh recovery attempt in this iteration so the user's answer doesn't
        # sit idle.
        if failure == "prompt_too_long" and not item.get("requires_fresh_session"):
            _proto(
                f"Resume of {item['task_id']} hit 'Prompt is too long' "
                f"(JSONL exceeds model context) — promoting to opus and switching to fresh-session recovery"
            )
            # Promote BEFORE resolving the model: the helper rewrites goal.md so the
            # subsequent _resolve_task_goal_and_model picks up opus_recommended=true
            # and the recovery session launches on Opus (1M baseline) instead of
            # repeating the failure on Sonnet.
            promoted = _promote_task_to_opus_for_context_limit(item["task_id"], self.deps)
            if not promoted.is_success:
                # Task is already on opus and STILL exceeded the model context — the
                # conversation has outgrown 1M tokens. Launching a fresh recovery on
                # opus would fail identically; skip it and mark the task exhausted
                # for this run. (Session does not count toward --max-tasks.)
                _proto(
                    f"{item['task_id']} is already on opus — "
                    f"context overflow is permanent. Skipping recovery for this run."
                )
                run_data.mark_exhausted(task_id=item["task_id"], session_id=session_id)
                save_state(STATE_PATH, state, self.deps)
                return "continue", sessions_launched
            run_data.mark_exhausted(session_id=session_id)
            _rewrite_question_session_id(
                os.path.join(item["folder_path"], "question.md"),
                "NEW_SESSION_REQUIRED",
                self.deps,
            )

            recovery_uuid = str(uuid.uuid4())
            recovery_env = build_env(account, recovery_uuid)
            goal_path, fresh_model = _resolve_task_goal_and_model(item["task_id"], self.deps)
            # Why: archive before launching recovery so the preamble path (AC-09) is
            # valid when the session reads it. Uses the same idempotent helper — if
            # the archive was already written by the original resume attempt above,
            # the helper returns the existing path without re-writing.
            recovery_archive_path = _archive_feedback_checkpoint(
                item["task_id"], item["folder_path"], goal_path, self.deps
            )
            recovery_model_note = f" model={fresh_model}" if fresh_model else ""
            _proto(
                f"Launching fresh recovery session for {item['task_id']} "
                f"with account {account}{recovery_model_note}"
            )
            recovery_record: dict[Any, Any] = make_session_record(
                account=account,
                task_id=item["task_id"],
                is_resume=False,
                deps=self.deps,
                fresh_for_answered_question=True,
                recovery_from="prompt_too_long",
            )
            register_session_in_goal(goal_path, recovery_uuid, account, self.deps)
            with active_session(state, recovery_uuid, self.deps):
                result = run_fresh_session_with_answer(
                    recovery_env, recovery_uuid, goal_path, recovery_archive_path,
                    args.hung_check_interval, args.hung_timeout * 60, args.session_timeout,
                    stop_flag, self.deps, model=fresh_model,
                )
            finalize_session_record(
                recovery_record, result, recovery_uuid, account, run_data, self.deps,
                label=item["task_id"],
            )
            # Classify the recovery's own failure (if any). Without this, a
            # recovery session that itself hit a rate limit or a permanent
            # access error would never update state, so the orchestrator would
            # keep trying the same blocked account on the next iteration.
            recovery_failure = classify_session_failure(result)
            if recovery_failure == "perm_error":
                apply_perm_error_to_account(
                    account, state, run_data, len(self._accounts), self.deps,
                )
            elif recovery_failure == "rate_limited":
                apply_rate_limit_to_account(
                    account, result.stdout, recovery_record, state,
                    len(self._accounts), self.deps,
                )
            elif recovery_failure in ("context_limit_no_entitlement", "prompt_too_long"):
                # The recovery was launched on Opus (1M baseline) precisely to escape
                # context-window failures. If it still hits one, the task has genuinely
                # outgrown even Opus's window — keep retrying is futile. Mark this
                # recovery_uuid as exhausted so the rest of this run skips the task,
                # rather than re-entering the same recovery path on each iteration
                # (which would burn an account-attempt every time under AC-21's cap).
                _proto(
                    f"WARNING: recovery for {item['task_id']} hit "
                    f"{recovery_failure} on Opus — task may have outgrown 1M context. "
                    f"Skipping for this run."
                )
                run_data.mark_exhausted(task_id=item["task_id"], session_id=recovery_uuid)
            # The recovery counts as one of the attempts under AC-21 cap.

        # Safety-net: if the resumed session wrote a follow-up question but skipped
        # Step 3 (copying TEMPLATE_answer.md over answer.md), the stale answer causes
        # find_answered_feedback to pick up the task every iteration and resume it with
        # the old answer — the session reads it, sees it is stale, and exits in a loop.
        # Detect by mtime: if question.md is newer than answer.md, the session may have
        # written a fresh question after the human had answered → reset answer.md to the
        # template. But mtime alone is ambiguous: a session that merely edits question.md
        # to mark the existing question status: resolved (a normal, correct action) also
        # bumps its mtime, which previously tripped a false positive that wiped a valid
        # human answer. Gate on the frontmatter status: only an awaiting_answer question
        # represents an unanswered follow-up; a resolved/other status must not reset.
        _q_path = os.path.join(FEEDBACK_DIR, item["task_id"], "question.md")
        _a_path = os.path.join(FEEDBACK_DIR, item["task_id"], "answer.md")
        if (
            os.path.exists(_q_path)
            and os.path.exists(_a_path)
            and not answer_is_empty(_a_path)
            and self.deps.get_mtime(_q_path) > self.deps.get_mtime(_a_path)
            and read_yaml_frontmatter(_q_path).get("status") == QUESTION_STATUS_AWAITING
            and os.path.exists(ANSWER_TEMPLATE_PATH)
        ):
            shutil.copy2(ANSWER_TEMPLATE_PATH, _a_path)
            _proto(
                f"[safety-net] {item['task_id']}: follow-up question detected "
                f"(question.md newer than answer.md) — reset answer.md to template"
            )

        # Archive already written before session run; delete pending_feedback folder on clean exit.
        # Why: AC-06 — the feedback-checkpoint is now in the task's plans_and_protocols/;
        # pending_feedback/ is only an inbox and should be empty after a successful resume.
        # The answered_feedback/ folder is no longer used for new entries (deprecated).
        if result.returncode == 0 and not new_question_written_for(item["task_id"], FEEDBACK_DIR, self.deps):
            _clear_inbox()
            if not os.path.exists(item["folder_path"]):
                _proto(f"{item['task_id']} pending_feedback folder already removed (task-complete cleaned up)")
            else:
                try:
                    shutil.rmtree(item["folder_path"])
                    _proto(f"Deleted {item['task_id']} from pending_feedback/ (archived to plans_and_protocols/)")
                except OSError as e:
                    _proto(f"WARNING: could not delete pending_feedback/{item['task_id']} ({e})")
        else:
            _proto(f"{item['task_id']} left in pending_feedback (new question or failure)")

        # Policy: only successful sessions count toward --max-tasks. Errors
        # (rate-limit, perm-error, context-overflow, generic non-zero exit) rotate
        # accounts / retry next iteration without consuming a slot — otherwise a
        # few unlucky early failures could exhaust the budget before any real work.
        if result.returncode == 0:
            state.run_count += 1
            sessions_launched += 1
        save_state(STATE_PATH, state, self.deps)

        if args.min_wait_seconds > 0:
            self.deps.sleep(args.min_wait_seconds)
        return "continue", sessions_launched

    def scan_unanswered_questions(self, state: PersistentState, run_data: RunData) -> list[Any]:
        """Return list of tasks with question.md but no answer.md. Logs them.

        Also calls check_and_update_question_fingerprint for each (AC-26).
        """
        unanswered = get_unanswered_questions(FEEDBACK_DIR, self.deps)
        if unanswered:
            task_ids = [q["task_id"] for q in unanswered]
            _proto(
                f"Note: unanswered questions for {', '.join(task_ids)} — "
                f"these tasks are skipped; other tasks will continue."
            )
            # AC-26: check for repeated questions
            for q in unanswered:
                q_path = os.path.join(FEEDBACK_DIR, q["task_id"], "question.md")
                try:
                    raw = self.deps.read_file(q_path)
                    parts = raw.split("---", 2)
                    body = parts[2].strip() if len(parts) >= 3 else raw.strip()
                    check_and_update_question_fingerprint(
                        q["task_id"], body, state, run_data, self.deps,
                        is_awaiting_answer=True,
                    )
                except OSError:
                    pass
        return unanswered

    def scan_in_progress_without_session_id(self, run_data: RunData) -> "list[str]":
        """Scan for in_progress tasks with no session_id. Log and collect for report. (AC-22)"""
        found = _find_in_progress_without_session_id(PROJECT_ROOT, self.deps)
        for tid in found:
            if tid not in run_data.skipped_no_session_id:
                _proto(
                    f"WARNING: {tid} is in_progress with no session_id in goal.md "
                    f"— skipping (manual session, or goal.md update failed on a prior launch)"
                )
                run_data.skipped_no_session_id.append(tid)
        return found

    def process_in_progress_resume(
        self,
        state: PersistentState,
        run_data: RunData,
        args: argparse.Namespace,
        stop_flag: dict[Any, Any],
        unanswered_task_ids: "list[str]",
        sessions_launched: int,
    ) -> "tuple[str, int]":
        """Attempt to resume an in_progress task session.

        Returns (decision, new_sessions_launched):
        - "continue": a resume was processed (or skipped), restart the loop
        - "next": no resumable session, proceed to normal session
        """
        resumable = find_resumable_session(
            PROJECT_ROOT, FEEDBACK_DIR, run_data.exhausted_resume_ids, self.deps
        )
        if not resumable:
            _proto("DEBUG: no in-progress task to resume")
            return "next", sessions_launched
        _proto(f"DEBUG: found resumable in-progress task {resumable['task_id']} "
              f"(session {resumable['session_id'][:8]}..., account {resumable['account']})")

        # AC-21: track and limit resume attempts per session_id
        session_id = resumable["session_id"]
        attempt = run_data.resume_attempt_counts.get(session_id, 0) + 1
        run_data.resume_attempt_counts[session_id] = attempt
        if attempt > 3:
            _proto(
                f"WARNING: resume of {resumable['task_id']} exhausted 3 attempts "
                f"— giving up this run"
            )
            run_data.mark_exhausted(task_id=resumable["task_id"], session_id=session_id)
            return "continue", sessions_launched

        stored_account = resumable["account"] or accounts_from_state(state, self._accounts)

        # CCS account dirs are symlinks to shared session storage, so any available
        # account can access any session file via --resume. If the stored account is
        # disabled or rate-limited, find an alternative rather than waiting or clearing
        # session data — switching accounts is free and preserves full session context.
        disabled = run_data.disabled_accounts
        now_utc = self.deps.get_now_utc()
        rate_limited_map = state.rate_limited_until

        def account_blocked(acct: str) -> bool:
            if acct in disabled:
                return True
            if acct in rate_limited_map:
                try:
                    return cast("bool", now_utc < datetime.fromisoformat(rate_limited_map[acct]))
                except ValueError:
                    return False
            return False

        resume_account = stored_account
        if stored_account not in self._accounts or account_blocked(stored_account):
            alt_account, wait_until = next_available_account(
                self._accounts, state, disabled, now_utc=now_utc,
            )
            if alt_account is None and wait_until is None:
                # AC-19: all accounts permanently disabled
                _proto("All accounts are permanently disabled — stopping")
                run_data.stop_reason = "all_accounts_disabled"
                return "stop", sessions_launched
            if wait_until is not None:
                # All accounts exhausted — wait for earliest reset then re-enter loop
                wait_secs = (wait_until - now_utc).total_seconds()
                if wait_secs > 0:
                    _proto(
                        f"All accounts exhausted for resume of "
                        f"{resumable['task_id']} — waiting {wait_secs:.0f}s"
                    )
                    state.rate_limit_reached = True
                    state.next_wake_time = wait_until.astimezone().isoformat()
                    save_state(STATE_PATH, state, self.deps)
                    rate_limit_sleep(wait_secs, stop_flag, reset_dt=wait_until, poll_stop=self._read_external_stop_request)
                    state.rate_limit_reached = False
                    state.next_wake_time = None
                    save_state(STATE_PATH, state, self.deps)
                return "continue", sessions_launched  # Re-enter loop after wait
            resume_account = alt_account
            if stored_account != resume_account:
                _proto(
                    f"Switching resume account {stored_account} → "
                    f"{resume_account} (shared session storage)"
                )

        resume_env = build_env(resume_account)

        # Resolve model from the task's goal.md (see resume call in
        # handle_pending_feedback for rationale — same reason here).
        _, resume_model = _resolve_task_goal_and_model(resumable["task_id"], self.deps)
        resume_model_note = f" model={resume_model}" if resume_model else ""
        _proto(
            f"Resuming in-progress {resumable['task_id']} "
            f"(session {resumable['session_id']}) with account {resume_account}"
            f"{resume_model_note}"
        )

        resume_record: dict[Any, Any] = make_session_record(
            account=resume_account,
            task_id=resumable["task_id"],
            is_resume=True,
            deps=self.deps,
        )

        with active_session(state, resumable["session_id"], self.deps):
            resume_result = run_resume_session(
                resume_env,
                resumable["session_id"],
                (
                    f"Continue from where you left off on task {resumable['task_id']}. "
                    f"The task is still in_progress. "
                    f"If all work is complete, call task-complete now. "
                    f"If you need user input before completing, write question.md to "
                    f"automation/pending_feedback/{resumable['task_id']}/ "
                    f"following the automated-mode rules, then terminate. "
                    f"If you cannot make progress now (e.g. a rate/session limit you "
                    f"depend on is still active), state in one line why and terminate. "
                    f"Do not schedule, wait, or reason about reset times — scheduling is "
                    f"the orchestrator's responsibility and it will resume you again."
                ),
                args.hung_check_interval, args.hung_timeout * 60, args.session_timeout,
                stop_flag, self.deps, model=resume_model,
            )

        finalize_session_record(
            resume_record, resume_result, resumable["session_id"], resume_account,
            run_data, self.deps, label=resumable["task_id"],
        )

        failure = classify_session_failure(resume_result)

        # Permanent access error on resume — disable the account; the next
        # iteration will switch to a working one (shared session storage means
        # any account can resume any session). No sessions_launched++ — this is
        # an infrastructure failure, not a task attempt.
        if failure == "perm_error":
            _proto(
                f"Disabling for {resumable['task_id']}; "
                f"will retry with a different account next iteration"
            )
            apply_perm_error_to_account(resume_account, state, run_data, len(self._accounts), self.deps)
            # Roll back the attempt counter — perm-error is infra, not a task failure
            run_data.resume_attempt_counts[session_id] = attempt - 1
            return "continue", sessions_launched

        # Rate limit on resume — recorded in state so account_blocked() picks an
        # available account on the next iteration. Policy: errors don't count
        # toward --max-tasks, so no sessions_launched bump.
        if failure == "rate_limited":
            apply_rate_limit_to_account(
                resume_account, resume_result.stdout, resume_record, state,
                len(self._accounts), self.deps,
            )
            # Roll back the attempt counter — rate-limit is infra, not a task failure;
            # the 3-attempt budget should only count genuine task-level failures
            run_data.resume_attempt_counts[session_id] = attempt - 1
            return "continue", sessions_launched

        # Context-overflow on sonnet resume — same recovery path for both signatures:
        # promote the task to opus (1M baseline) and reset for a fresh launch on the
        # next iteration. The original session_id is added to exhausted_resume_ids so
        # this run won't try it again; the helper clears session_id in goal.md and
        # flips status back to pending so the next iteration's find_next_task picks
        # it up cleanly on the opus model. Without this branch, prompt_too_long on an
        # in-progress task resume would fall through to "exhausted, retry next run"
        # and the same --resume would fail identically on every orchestrator start.
        if failure in ("context_limit_no_entitlement", "prompt_too_long"):
            signal = (
                "1M-context entitlement limit"
                if failure == "context_limit_no_entitlement"
                else "'Prompt is too long' (JSONL exceeds model context)"
            )
            _proto(
                f"Resume of {resumable['task_id']} hit {signal} "
                f"on sonnet — promoting to opus and resetting to fresh-launch path"
            )
            promoted = _promote_task_to_opus_for_context_limit(resumable["task_id"], self.deps)
            if not promoted.is_success:
                # Already on opus — context overflow is permanent. Mark task
                # exhausted for this run so we don't keep re-attempting the same
                # doomed --resume on every iteration.
                run_data.mark_exhausted(
                    task_id=resumable["task_id"], session_id=resumable["session_id"]
                )
            else:
                run_data.mark_exhausted(session_id=resumable["session_id"])
            save_state(STATE_PATH, state, self.deps)
            return "continue", sessions_launched

        # Generic resume failure — not a perm error, not a rate limit, not a
        # context overflow. Mark the session as exhausted for this run so we
        # don't loop on it again. session_id is intentionally kept in goal.md
        # so the next orchestrator run can attempt the resume again (e.g. after
        # a transient error clears). Errors don't count toward --max-tasks.
        if resume_result.returncode != 0:
            _proto(
                f"WARNING: resume of {resumable['task_id']} "
                f"(session {resumable['session_id']}) failed with exit "
                f"{resume_result.returncode} — skipping for this run; "
                f"will retry on next orchestrator start"
            )
            run_data.mark_exhausted(session_id=resumable["session_id"])
            save_state(STATE_PATH, state, self.deps)
            return "continue", sessions_launched

        state.run_count += 1
        sessions_launched += 1
        save_state(STATE_PATH, state, self.deps)

        if args.min_wait_seconds > 0:
            self.deps.sleep(args.min_wait_seconds)
        return "continue", sessions_launched

    def run_preflight_queue_check(
        self,
        state: PersistentState,
        run_data: RunData,
        args: argparse.Namespace,
    ) -> "tuple[bool, str | None]":
        """Check whether there are runnable tasks in the queue.

        Returns:
        - (True, None): runnable tasks exist
        - (False, "all_tasks_awaiting_answer"): tasks exist but all blocked
        - (False, "queue_empty"): next_tasks.py returned no tasks at all (AC-18)
        """
        next_result = self.deps.run_subprocess(
            ["python3", "scripts/tasks/next_tasks.py"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        task_ids_in_output = re.findall(
            r"^\s*\d+\.\s+\[(TASK-[A-Z0-9\-]+)\]",
            next_result.stdout,
            re.MULTILINE,
        )

        # AC-18: detect empty output (no tasks at all) before checking runnable subset
        if not task_ids_in_output:
            _proto("No tasks in queue — stopping")
            return False, "queue_empty"

        runnable = [
            tid for tid in task_ids_in_output
            if self.deps.run_subprocess(
                ["python3", "scripts/tasks/is_awaiting_answer.py", "--task-id", tid],
                capture_output=True,
                cwd=PROJECT_ROOT,
            ).returncode == 0
        ]
        if not runnable:
            waiting = ", ".join(task_ids_in_output)
            _proto(
                f"No runnable tasks — all candidates are awaiting answers. "
                f"Waiting: {waiting}. Answer pending questions to continue."
            )
            return False, "all_tasks_awaiting_answer"

        return True, None

    def wait_for_account_if_needed(
        self,
        state: PersistentState,
        run_data: RunData,
        args: argparse.Namespace,
        stop_flag: dict[Any, Any],
    ) -> "tuple[str | None, bool]":
        """Get next available account, sleeping if all are rate-limited.

        Returns (account, waited):
        - (account_str, False): account is available now
        - (None, True): slept and should re-enter loop
        - (None, False): all accounts permanently disabled (AC-19) — caller sets stop_reason
        """
        account, wait_until = next_available_account(
            self._accounts, state, run_data.disabled_accounts,
            now_utc=self.deps.get_now_utc(),
        )

        # AC-19: sentinel (None, None) means all permanently disabled
        if account is None and wait_until is None:
            _proto("All accounts are permanently disabled — stopping")
            return None, False

        if wait_until is not None:
            wait_secs = (wait_until - self.deps.get_now_utc()).total_seconds()
            if wait_secs > 0:
                _proto(
                    f"All accounts rate-limited. "
                    f"Waiting {wait_secs:.0f}s until {wait_until}"
                )
                state.rate_limit_reached = True
                state.next_wake_time = wait_until.astimezone().isoformat()
                save_state(STATE_PATH, state, self.deps)
                rate_limit_sleep(wait_secs, stop_flag, reset_dt=wait_until, poll_stop=self._read_external_stop_request)
                state.rate_limit_reached = False
                state.next_wake_time = None
                save_state(STATE_PATH, state, self.deps)
            # After sleeping, re-enter loop to re-check stop conditions and pick account
            return None, True

        return account, False

    def run_normal_session_step(
        self,
        state: PersistentState,
        run_data: RunData,
        account: str,
        args: argparse.Namespace,
        stop_flag: dict[Any, Any],
        sessions_launched: int,
    ) -> "tuple[str, int]":
        """Launch one normal (non-resume) session.

        Returns (decision, new_sessions_launched):
        - always "continue" (loop continues after a normal session step)
        """
        session_uuid = str(uuid.uuid4())

        # Decide task and model BEFORE session launch. find_active_task_goal returns
        # an existing in_progress task (interrupted prior session); otherwise we
        # pre-pick via next_tasks.py so --model opus can be set on the claude CLI
        # for opus_recommended tasks.
        goal_path = find_active_task_goal(PROJECT_ROOT, self.deps)
        task_id: str | None = None
        model: str | None = None
        if goal_path:
            fm = read_yaml_frontmatter(goal_path)
            task_id = fm.get("task_id") or None
            session_id = fm.get("session_id", "").strip()
            exhausted_task_ids = {t["task_id"] for t in run_data.exhausted_resume_tasks}
            if (session_id and session_id in run_data.exhausted_resume_ids) or (
                task_id and task_id in exhausted_task_ids
            ):
                _proto(
                    f"Skipping {task_id} from find_active_task_goal — "
                    f"already exhausted this run"
                )
                goal_path = None
            elif _is_opus_recommended(fm):
                model = "opus"
        if not goal_path:
            picked = pick_next_task_for_session(self.deps)
            if picked:
                goal_path, task_id, is_opus = picked
                if is_opus:
                    model = "opus"

        if goal_path:
            register_session_in_goal(goal_path, session_uuid, account, self.deps)
        else:
            _proto("No task pre-picked — session will pick via routing skill")

        # Clear any pending operator message before launching a new task session
        # so messages meant for the previous task do not leak into this one.
        _clear_inbox()

        env = build_env(account, session_uuid)

        model_note = " model=opus" if model else ""
        task_note = f" task={task_id}" if task_id else ""
        _proto(f"Launching session {session_uuid} with account {account}{model_note}{task_note}")
        session_record = make_session_record(
            account=account,
            task_id=task_id,
            is_resume=False,
            deps=self.deps,
            session_uuid=session_uuid,
        )

        with active_session(state, session_uuid, self.deps):
            result = run_normal_session(
                env, session_uuid,
                args.hung_check_interval, args.hung_timeout * 60, args.session_timeout,
                stop_flag, self.deps,
                model=model, task_id=task_id,
            )

        finalize_session_record(
            session_record, result, session_uuid, account, run_data, self.deps,
            label=session_uuid,
        )
        # Hung-kill on a fresh launch: goal.md is left untouched so AC-15
        # resume logic handles recovery on the next orchestrator pass.

        failure = classify_session_failure(result)

        # Policy: errors don't count toward --max-tasks. perm_error / rate_limited /
        # context_limit_no_entitlement rotate accounts or promote the task without
        # consuming a slot — otherwise a few unlucky early failures could exhaust
        # the budget before any real work.
        if failure == "perm_error":
            apply_perm_error_to_account(account, state, run_data, len(self._accounts), self.deps)
            return "continue", sessions_launched

        if failure == "rate_limited":
            apply_rate_limit_to_account(
                account, result.stdout, session_record, state, len(self._accounts), self.deps,
            )
            # No min_wait_seconds sleep — rate limit handling takes precedence
            return "continue", sessions_launched

        # 1M-context entitlement refused on fresh sonnet launch — promote the
        # task to opus so the next iteration relaunches it on a model whose 1M
        # baseline doesn't require Extra usage. If promote returns False the task
        # is already on opus → context overflow is permanent; skip retry by leaving
        # the failure on record (the next iteration's task picker will pick a
        # different task since this one still has opus_recommended=true and the
        # session would just hit the same wall).
        if failure == "context_limit_no_entitlement":
            target_task_id = task_id if task_id else "unknown"
            _proto(
                f"Fresh launch for {target_task_id} hit 1M-context "
                f"entitlement limit on sonnet — promoting to opus for next iteration"
            )
            if task_id:
                promoted = _promote_task_to_opus_for_context_limit(task_id, self.deps)
                if not promoted.is_success:
                    _proto(
                        f"{target_task_id} is already on opus and "
                        f"still exceeded 1M context — task may need to be split."
                    )
                    # Why: promote-to-opus is the only recovery for the entitlement
                    # error; when the task is already on opus the recovery is
                    # exhausted. Without clearing the doomed session_id and marking
                    # the session as exhausted, the next iteration's
                    # find_resumable_session picks the task up and burns another
                    # rate-limit budget on a --resume that cannot succeed.
                    run_data.mark_exhausted(task_id=task_id, session_id=session_uuid)
                    if goal_path:
                        update_goal_session_fields(goal_path, "", "", self.deps)
                        _proto(
                            f"Cleared session_id from {target_task_id} goal.md to "
                            f"prevent doomed resume attempts this run"
                        )
            return "continue", sessions_launched

        # Success — advance account index round-robin
        state.account_index = (state.account_index + 1) % len(self._accounts)
        state.run_count += 1
        sessions_launched += 1
        save_state(STATE_PATH, state, self.deps)

        if args.min_wait_seconds > 0:
            self.deps.sleep(args.min_wait_seconds)

        return "continue", sessions_launched

    def run_loop(
        self,
        state: PersistentState,
        run_data: RunData,
        accounts: list[Any],
        args: argparse.Namespace,
        stop_flag: dict[Any, Any],
        stop_at: "datetime | None",
    ) -> None:
        """Main orchestration loop (~25 lines). Delegates to named step methods."""
        # Store accounts on self so step methods can access them
        # without threading through every parameter signature.
        self._accounts = accounts

        sessions_launched = 0
        loop_iteration = 0

        while True:
            loop_iteration += 1
            _proto(f"--- Loop iteration {loop_iteration} (sessions launched: {sessions_launched}) ---")

            # Step 1: stop conditions
            should_stop, reason = self.check_stop_conditions(
                state, run_data, args, stop_flag, stop_at, sessions_launched
            )
            if should_stop:
                run_data.stop_reason = reason
                break

            # Step 2: answered feedback (highest priority)
            decision, sessions_launched = self.process_answered_feedback(
                state, run_data, args, stop_flag, sessions_launched
            )
            if decision == "continue":
                continue

            # Step 3: unanswered question guard (log + AC-26 fingerprint)
            unanswered = self.scan_unanswered_questions(state, run_data)
            unanswered_task_ids = [q["task_id"] for q in unanswered]

            # Step 4: AC-22 — scan for in_progress without session_id
            self.scan_in_progress_without_session_id(run_data)

            # Step 5: in-progress resume
            decision, sessions_launched = self.process_in_progress_resume(
                state, run_data, args, stop_flag, unanswered_task_ids, sessions_launched
            )
            if decision == "continue":
                continue
            if decision == "stop":
                break

            # Step 6: pre-flight queue check (AC-18)
            ok, stop_reason = self.run_preflight_queue_check(state, run_data, args)
            if not ok:
                run_data.stop_reason = stop_reason or "preflight_failed"
                break

            # Step 7: account selection (AC-19)
            account, waited = self.wait_for_account_if_needed(state, run_data, args, stop_flag)
            if waited:
                continue
            if account is None:
                run_data.stop_reason = "all_accounts_disabled"
                break

            # Step 8: normal session
            _decision, sessions_launched = self.run_normal_session_step(
                state, run_data, account, args, stop_flag, sessions_launched
            )


# --- Section 7: Entry point ---


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Orchestrate sequential claude sessions with account rotation"
    )
    parser.add_argument(
        "--accounts",
        default="gmail,web,gmail2",
        help="Comma-separated list of CCS account names (default: gmail,web,gmail2)",
    )
    parser.add_argument(
        "--stop-at",
        metavar="YYYY-MM-DD HH:MM",
        default=None,
        help="Stop after current session once this datetime is reached (local time)",
    )
    parser.add_argument(
        "--min-wait-seconds",
        type=int,
        default=0,
        metavar="N",
        help="Minimum seconds to wait between sessions (default: 0)",
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=None,
        metavar="N",
        help="Stop after N sessions have been launched (default: run indefinitely)",
    )
    parser.add_argument(
        "--hung-check-interval",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Seconds between hung-session polls (default: 60)",
    )
    parser.add_argument(
        "--hung-timeout",
        type=int,
        default=30,
        metavar="MINUTES",
        help="Minutes of stale JSONL + no child processes before declaring hung (default: 30)",
    )
    parser.add_argument(
        "--session-timeout",
        type=int,
        default=14400,
        metavar="SECONDS",
        help="Hard ceiling in seconds before a session is killed regardless (default: 14400 = 4 h)",
    )
    return parser.parse_args()


def setup_signals(stop_flag: dict[Any, Any]) -> None:
    """Register SIGTERM and SIGINT handlers to set stop_flag["requested"].

    Why: dict-based stop_flag (not a global bool) allows mutation from a lambda
    without needing 'global' keyword — compatible with signal handler constraints.
    Source: plan section 10.
    """
    def handler(signum: Any, frame: Any) -> None:
        stop_flag["requested"] = True
        print()
        _proto(f"Signal {signum} received — stopping after current session")

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)


def main(_skip_lock: bool = False) -> None:
    """Wiring only: parse args, acquire lock, create deps, load state, run loop, finalise.

    _skip_lock: set True in tests to bypass fcntl.flock (Unix-only, untestable in unit tests).
    """
    args = parse_args()
    accounts = [a.strip() for a in args.accounts.split(",") if a.strip()]
    if not accounts:
        raise ValueError("--accounts must contain at least one account name")

    stop_at = None
    if args.stop_at:
        stop_at = datetime.strptime(args.stop_at, "%Y-%m-%d %H:%M")

    # AC-25: lock file prevents concurrent orchestrator instances.
    # Why: fcntl.flock(LOCK_EX | LOCK_NB) is used (non-blocking exclusive lock) rather
    # than a PID file with manual staleness checks — the OS releases the lock automatically
    # if the process dies, so no stale lock cleanup is needed. The lockfile library is not
    # used to keep the script stdlib-only.
    # Source: requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
    #         feat_session_orchestrator/tasks/2026-04-10_impl_implement-orchestrator-monitoring-improvements/
    #         plans_and_protocols/2026-04-10_02_plan_rewrite-architecture.md#8-risk-assessment (Risk 3)
    lock_path = os.path.join(AUTOMATION_DIR, ".orchestrator.lock")
    os.makedirs(AUTOMATION_DIR, exist_ok=True)
    lock_fd = open(lock_path, "w")  # noqa: SIM115, RUF100 -- kept open for lifetime of process (advisory file lock); RUF100 false-positive companion

    if not _skip_lock:
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
            _proto(f"ERROR: orchestrator already running (PID {running_pid}) — aborting")
            lock_fd.close()
            import sys
            sys.exit(1)

    # Why: dict container allows lambda signal handler to mutate the flag
    stop_flag = {"requested": False}
    setup_signals(stop_flag)

    # Production deps wiring — all I/O boundaries injected here
    deps = OrchestratorDeps(
        run_subprocess=subprocess.run,
        popen_subprocess=subprocess.Popen,
        read_file=lambda p: open(p).read(),  # noqa: SIM115, RUF100 -- dep-injection lambda; orchestrator owns the I/O contract and reads small files synchronously
        write_file=lambda p, c: open(p, "w").write(c),  # noqa: SIM115, RUF100 -- dep-injection lambda; orchestrator owns the I/O contract and writes small files synchronously
        file_exists=os.path.exists,
        list_dir=lambda p: list(os.scandir(p)),
        makedirs=lambda p: os.makedirs(p, exist_ok=True),
        glob_files=glob.glob,
        get_now_utc=lambda: datetime.now(timezone.utc),
        get_now_local=lambda: datetime.now().astimezone(),
        sleep=time.sleep,
        getpid=os.getpid,
        get_mtime=os.path.getmtime,
        outputs_dir=OUTPUTS_DIR,
    )

    state = load_state(STATE_PATH, deps)

    # Create runtime directories
    deps.makedirs(OUTPUTS_DIR)
    deps.makedirs(REPORTS_DIR)
    deps.makedirs(ANSWERED_DIR)

    # Clean up artifacts from runs older than the most recent one
    cleanup_old_artifacts(REPORTS_DIR, OUTPUTS_DIR, ANSWERED_DIR, FEEDBACK_DIR, deps)

    # Commit cleanup deletions (old reports, processed pending_feedback) — non-fatal
    cleanup_str = deps.get_now_local().strftime("%Y-%m-%d %H:%M")
    git_commit_best_effort(
        [],
        f"chore(automation): commit cleanup deletions {cleanup_str}",
        deps,
        update_dirs=["automation/reports/", "automation/pending_feedback/"],
    )

    # Create sentinel: marks this process as running in automated mode
    deps.makedirs(AUTOMATION_DIR)
    try:
        deps.write_file(SENTINEL_AUTOMATED, str(deps.getpid()))
    except OSError as e:
        _proto(f"WARNING: could not create .automated_mode sentinel ({e})")

    # Always reset start_time on each new launch so state.json reflects the current run
    start_time = deps.get_now_local()
    state.start_time = start_time.isoformat()
    # Initialise observability fields (AC-34, AC-38): reset any stale state from a prior run
    _reset_startup_state(state)
    # Clear the per-run log dedupe set so warnings emitted on a previous run
    # (e.g. tests in the same process) don't suppress this run's first occurrence.
    _run_log_dedupe.clear()
    save_state(STATE_PATH, state, deps, startup=True)    # startup=True skips disk-merge so stale stop_requested is cleared

    run_data = RunData(start_time=start_time)

    # Snapshot in_progress tasks at run start for health summary comparison
    run_data.initial_in_progress = snapshot_in_progress_tasks(PROJECT_ROOT, deps)

    # AC-23: git commit answer.md files at start (non-fatal)
    now_str = deps.get_now_local().strftime("%Y-%m-%d %H:%M")
    git_commit_best_effort(
        ["automation/pending_feedback/*/answer.md"],
        f"chore(automation): record user answers {now_str}",
        deps,
    )

    orchestrator = Orchestrator(deps)
    report_path = None

    try:
        orchestrator.run_loop(state, run_data, accounts, args, stop_flag, stop_at)

    except KeyboardInterrupt:
        run_data.stop_reason = "manual"
        print()
        _proto("KeyboardInterrupt — stopping after current session")

    finally:
        stop_time = deps.get_now_local()
        run_data.stop_time = stop_time
        report_path = write_report(REPORTS_DIR, run_data, accounts, FEEDBACK_DIR, deps)
        # write_health_summary receives the exact path returned by write_report,
        # fixing the pre-rewrite minute-rollover bug.
        write_health_summary(
            report_path,
            run_data,
            run_data.initial_in_progress,
            deps,
        )
        # AC-24: git commit report + question.md files on stop (non-fatal)
        stop_str = stop_time.strftime("%Y-%m-%d %H:%M")
        stop_reason = run_data.stop_reason
        git_commit_best_effort(
            [report_path, "automation/pending_feedback/*/question.md"],
            f"chore(automation): session report {stop_str} [{stop_reason}]",
            deps,
        )
        # Clean up sentinels (best-effort)
        unlink_if_exists(SENTINEL_AUTOMATED)
        # .stop-requested sentinel no longer used (AC-38) — replaced by state.stop_requested

        # Mark not-running and clear active_session for external observers (AC-34, AC-35)
        state.is_running = False
        state.active_session = None
        state.rate_limit_reached = False
        state.next_wake_time = None
        state.stop_reason = run_data.stop_reason
        save_state(STATE_PATH, state, deps)
        _proto(f"Stopped. Reason: {stop_reason}")
        # Release lock
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()
        except OSError:
            pass


def accounts_from_state(state: PersistentState, accounts: list[Any]) -> str:
    """Resolve the current account from state.account_index, with bounds guard."""
    if not accounts:
        return ""
    return cast("str", accounts[state.account_index % len(accounts)])


if __name__ == "__main__":
    main()
