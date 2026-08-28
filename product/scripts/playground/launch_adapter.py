"""Standalone child-session launcher for the Skill-Test Playground (SG-01).

Extracted from scripts/automation/orchestrate.py's run_session_with_hung_detection
and _launch_claude_session, but freed from orchestrator-global dependencies:
  - No OrchestratorDeps, state.json, inbox.md, or stop_flag required.
  - JSONL hung-detection path is PARAMETERIZED on the child's cwd, not
    hardcoded to the host project's JSONL_BASE (the SG-01 blocker).

Why a new module rather than reusing orchestrate.py directly:
  orchestrate.py's launch core requires OrchestratorDeps (popen/sleep/
  get_mtime/run_subprocess), stop_flag dict, state.json path, and inbox.md.
  Those are orchestrator-global singletons — importing them for playground
  use would pull in ~3800 lines of stateful orchestrator machinery and
  couple the playground to the orchestrator's internal contracts.
  A standalone adapter with injectable boundaries gives the playground an
  independently testable, orchestrator-free launch primitive.
  Source: TASK-PROC-068-04 plans_and_protocols/2026-06-27_01_plan_walking-skeleton.md#SG-01

JSONL path parameterization:
  orchestrate.py hardcodes JSONL_BASE to the host project path. For playground
  child sessions running with harness_dir as cwd, the JSONL file is written
  under a path derived from harness_dir, not the host project. The adapter
  accepts jsonl_dir as a parameter so hung-detection watches the right file.

Dependency injection:
  LaunchDeps is a dataclass of callables matching OrchestratorDeps' shape
  for the subset of boundaries used here (popen, sleep, get_mtime,
  run_subprocess). Tests inject fakes without global monkey-patching.
"""

# tier: B  # reusable library imported by run_skeleton; injectable boundaries

import logging
import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

_LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_HUNG_CHECK_INTERVAL_SECS = 30
DEFAULT_HUNG_TIMEOUT_SECS = 300       # 5 minutes of frozen JSONL + no children
DEFAULT_SESSION_TIMEOUT_SECS = 3600   # 1 hour hard ceiling for playground runs
_KILL_GRACE_SECS = 10
_HEARTBEAT_INTERVAL_SECS = 270        # 4m30s — keeps caller aware of long runs


# ---------------------------------------------------------------------------
# Session configuration (groups timeout params to stay within PLR0913 ≤ 5)
# ---------------------------------------------------------------------------


@dataclass
class SessionConfig:
    """Timeout and polling configuration for a child session launch.

    Why a dataclass rather than individual params:
      run_with_hung_detection had 8 parameters (PLR0913 violation: >5).
      The three timeout/interval values are related configuration, not
      independent concerns — grouping them into SessionConfig reduces the
      public signature to 5 params while keeping the configuration explicit.
    """

    hung_check_interval: int = DEFAULT_HUNG_CHECK_INTERVAL_SECS
    hung_timeout_secs: int = DEFAULT_HUNG_TIMEOUT_SECS
    session_timeout_secs: int = DEFAULT_SESSION_TIMEOUT_SECS


# ---------------------------------------------------------------------------
# Launch request (groups positional params to stay within PLR0913 ≤ 5)
# ---------------------------------------------------------------------------


@dataclass
class LaunchRequest:
    """Positional launch parameters for run_with_hung_detection.

    Why a dataclass rather than individual params:
      run_with_hung_detection originally took cmd, env, session_uuid, jsonl_dir
      as four positional args — combined with config and deps that was 6 params
      (PLR0913 violation: >5).  LaunchRequest bundles the four launch-identity
      fields (the command to run, its environment, the UUID, and the JSONL dir)
      into one cohesive value so the public signature stays at ≤ 5 params.
    """

    cmd: list[str]
    env: dict[str, str]
    session_uuid: str
    jsonl_dir: str


# ---------------------------------------------------------------------------
# Dependency injection boundary
# ---------------------------------------------------------------------------


@dataclass
class LaunchDeps:
    """Injectable I/O boundaries for LaunchAdapter.

    Mirrors the shape of OrchestratorDeps for the subset of calls needed
    here, so tests can inject fakes for only the boundaries they care about.

    Why dataclass of callables: matches the pattern established in
    orchestrate.py (see OrchestratorDeps docstring) — gives 100%
    mockability without abstract base class ceremony.
    """

    popen_subprocess: Callable[..., Any] = field(
        default_factory=lambda: subprocess.Popen
    )
    run_subprocess: Callable[..., Any] = field(
        default_factory=lambda: subprocess.run
    )
    get_mtime: Callable[[str], float] = field(
        default_factory=lambda: os.path.getmtime
    )
    sleep: Callable[[float], None] = field(default_factory=lambda: time.sleep)


def make_real_deps() -> LaunchDeps:
    """Return a LaunchDeps wired to real subprocess/filesystem calls."""
    return LaunchDeps()


# ---------------------------------------------------------------------------
# Session outcome
# ---------------------------------------------------------------------------


class LaunchResult:
    """Outcome of a child session launch."""

    def __init__(
        self,
        returncode: int,
        stdout: str,
        reason: str,
    ) -> None:
        self.returncode = returncode
        self.stdout = stdout
        # Why the session ended: "exited", "session_timeout", "hung", "stop_requested"
        self.reason = reason

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0


# ---------------------------------------------------------------------------
# Core hung-detection loop (extracted from orchestrate.py, parameterized)
# ---------------------------------------------------------------------------


def run_with_hung_detection(
    request: LaunchRequest,
    *,
    config: Optional[SessionConfig] = None,
    deps: Optional[LaunchDeps] = None,
) -> LaunchResult:
    """Launch request.cmd via Popen and poll for hung-session conditions.

    Key difference from orchestrate.py's run_session_with_hung_detection:
      The JSONL path is derived from request.jsonl_dir + request.session_uuid,
      NOT from the hardcoded JSONL_BASE.  This allows the playground to watch
      the child session's JSONL in the harness-specific CCS directory.

    Hung detection fires when:
      (a) elapsed >= session_timeout_secs (hard ceiling)
      (b) JSONL mtime frozen AND no child processes for >= hung_timeout_secs

    Args:
        request: Launch identity — cmd, env, session_uuid, jsonl_dir bundled
            into a LaunchRequest so the signature stays within PLR0913 ≤ 5.
        config: Session timeout/polling configuration.  Defaults to
            SessionConfig() which uses the DEFAULT_* constants.
        deps: Injectable boundaries; defaults to real subprocess/fs calls.

    Returns:
        LaunchResult with returncode, stdout, and termination reason.
    """
    if config is None:
        config = SessionConfig()
    if deps is None:
        deps = make_real_deps()

    # stderr must stay SEPARATE from stdout: the child (claude --output-format
    # json) prints its result envelope to stdout, but writes warnings (e.g.
    # "no stdin data received in 3s...") to stderr.  Merging them (stderr=STDOUT)
    # prepends that warning to the JSON, so record_run's json.loads fails at
    # char 0.  stdin=DEVNULL stops the child from waiting ~3s for stdin (and
    # emitting that warning) in the first place — the prompt is passed via -p.
    proc = deps.popen_subprocess(
        request.cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=request.env,
    )

    jsonl_path = os.path.join(request.jsonl_dir, f"{request.session_uuid}.jsonl")
    start_mono = time.monotonic()
    last_mtime: Optional[float] = None
    stale_since_mono: Optional[float] = None
    next_heartbeat_mono = start_mono + _HEARTBEAT_INTERVAL_SECS
    reason = "unknown"

    while True:
        deps.sleep(config.hung_check_interval)

        # (a) Process already exited
        rc = proc.poll()
        if rc is not None:
            output, _ = proc.communicate(timeout=5)
            return LaunchResult(rc, output or "", reason="exited")

        elapsed = time.monotonic() - start_mono

        # (b) Hard session ceiling
        if elapsed >= config.session_timeout_secs:
            reason = "session_timeout"
            break

        # Heartbeat log so long-running sessions are visible
        now_mono = time.monotonic()
        if now_mono >= next_heartbeat_mono:
            _LOG.info(
                "Playground session %s still running — %.0f min elapsed",
                request.session_uuid[:8],
                elapsed / 60,
            )
            next_heartbeat_mono = now_mono + _HEARTBEAT_INTERVAL_SECS

        # (c) JSONL mtime stale-check
        current_mtime = _safe_get_mtime(jsonl_path, deps)
        stale_since_mono = _update_stale_timer(
            current_mtime, last_mtime, stale_since_mono, proc, deps
        )
        if current_mtime is not None:
            last_mtime = current_mtime

        if _is_hung(stale_since_mono, config.hung_timeout_secs):
            reason = "hung"
            break

    return _kill_and_return(proc, reason, deps)


def _safe_get_mtime(path: str, deps: LaunchDeps) -> Optional[float]:
    """Return mtime or None if the file does not exist yet."""
    try:
        return deps.get_mtime(path)
    except (FileNotFoundError, OSError):
        return None


def _update_stale_timer(
    current_mtime: Optional[float],
    last_mtime: Optional[float],
    stale_since_mono: Optional[float],
    proc: Any,
    deps: LaunchDeps,
) -> Optional[float]:
    """Return updated stale_since_mono based on JSONL mtime and child processes."""
    if current_mtime is None:
        return None  # JSONL not yet created — not stale

    if last_mtime is None or current_mtime != last_mtime:
        return None  # mtime changed — session making progress

    # Mtime frozen: check for active child processes
    child_result = deps.run_subprocess(
        ["ps", "--ppid", str(proc.pid), "--no-headers"],
        capture_output=True,
        text=True,
    )
    if child_result.stdout.strip():
        return None  # children present — session is working

    # No children and mtime frozen — start or continue stale timer
    if stale_since_mono is None:
        return time.monotonic()
    return stale_since_mono


def _is_hung(stale_since_mono: Optional[float], hung_timeout_secs: int) -> bool:
    """Return True if the stale timer has exceeded hung_timeout_secs."""
    if stale_since_mono is None:
        return False
    return (time.monotonic() - stale_since_mono) >= hung_timeout_secs


def _kill_and_return(
    proc: Any,
    reason: str,
    deps: LaunchDeps,
) -> LaunchResult:
    """SIGTERM the process, wait grace period, SIGKILL if still alive."""
    elapsed = time.monotonic()
    _LOG.warning(
        "Playground session appears hung (reason: %s) after %.0f s — killing",
        reason,
        elapsed,
    )
    proc.send_signal(signal.SIGTERM)
    deps.sleep(_KILL_GRACE_SECS)
    if proc.poll() is None:
        proc.kill()
        rc = -9
    else:
        rc = -15
    output, _ = proc.communicate(timeout=5)
    return LaunchResult(rc, output or "", reason=reason)
