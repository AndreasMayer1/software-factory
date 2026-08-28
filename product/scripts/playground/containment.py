"""OS-level containment layer for the Skill-Test Playground child sessions.

Wraps a child command in a real mount-namespace jail to close CON-04
(absolute-path cwd-escape).  The host factory tree and the rest of the host
filesystem outside the harness directory are UNREACHABLE from inside the jail
via absolute paths or working-directory escape.

Preferred implementation: ``bwrap`` (bubblewrap) — declaratively binds only
the harness directory into the child's view of the filesystem; all other host
paths are absent from the child's mount namespace entirely.

Network: the jail intentionally RETAINS the host network namespace (bwrap
``--share-net``).  The child is a real ``claude -p`` session that must reach
``api.anthropic.com``.  CON-04 / AC-09 is a filesystem-isolation guarantee
(mount namespace), not a network-isolation one — no requirement asks the jail
to be offline, and re-sharing the network namespace leaves the host tree just
as absent.  Without ``--share-net``, ``--unshare-all`` would leave the jail
with no DNS and no ``claude`` session could run inside it.

Fallback: ``unshare --user --mount --map-root-user`` — creates a user+mount
namespace so the child cannot use absolute paths to reach host paths.  The
fallback does not bind-mount, so the host filesystem remains *visible* but the
child has no write capability on host paths outside the harness (user namespace
maps the child to an unprivileged UID on the host).

Preference order: bwrap > unshare > ContainmentUnavailable (fail-safe).

Fail-safe: if neither ``bwrap`` nor ``unshare`` is available (e.g. Docker
seccomp still blocking the syscall), ``ContainmentUnavailable`` is raised.
The launch is REFUSED rather than running uncontained.  The operator must
consciously opt out via ``PLAYGROUND_ALLOW_UNCONTAINED=1``.

Bypass: set PLAYGROUND_ALLOW_UNCONTAINED=1 for dev/test environments where
OS-level namespace isolation is unavailable.  This is an explicit opt-out that
logs a WARNING so consumers know they are running without containment.

Secondary defense: ``scrub_env()`` redirects HOME and XDG_* variables to the
harness directory so the child session writes data inside the harness, not
to the host user's home directory.  This does NOT close CON-04 by itself —
it is defense-in-depth only.

Why fail-safe instead of best-effort:
  Running an untrusted candidate factory uncontained means its skills can
  read and write the host factory tree via absolute paths.  A silent fallback
  to uncontained mode would give a false sense of security.  Refusing to
  launch makes the threat model explicit: the operator must consciously
  opt out via PLAYGROUND_ALLOW_UNCONTAINED=1.
  Source: TASK-PROC-068-04 plans_and_protocols/2026-06-27_04_protocol_decision-option-B.md

Why bwrap preferred over unshare:
  ``bwrap --unshare-all`` with only the harness bound makes the host tree
  *absent* (not just inaccessible by capability).  ``unshare`` without
  bind-mount leaves host paths visible; a child that runs as mapped-root
  inside the namespace can still attempt reads.  bwrap's absent-by-default
  model is strictly stronger for CON-04 closure.
  Source: TASK-PROC-068-04 plans_and_protocols/2026-06-27_04_protocol_decision-option-B.md
"""

# tier: B  # reusable library imported by launch_adapter; no long-lived state

import logging
import os
import subprocess
from typing import Callable, Optional

_LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOW_UNCONTAINED_ENV_VAR = "PLAYGROUND_ALLOW_UNCONTAINED"

# bwrap flags: unshare all namespaces EXCEPT network; bind harness dir RW;
# bind /tmp RW; bind /usr and /lib* read-only so standard tools (cat, ls, sh)
# work inside.
# Why /usr and /lib*: bwrap's absent-by-default model means no libc → child
# segfaults immediately.  Binding only the read-only OS runtime (not /home,
# not the project tree) keeps the host factory tree absent while the child
# has a working POSIX environment.
# Why --share-net (retain the host network namespace): the child is a real
# `claude -p` session that MUST reach api.anthropic.com; --unshare-all alone
# unshares the network namespace as an incidental side effect, leaving the jail
# with no DNS/network.  CON-04 / AC-09 is a *filesystem* guarantee (host tree
# absent via the mount namespace) — re-sharing only the network namespace does
# not weaken it: the host factory tree stays absent.  Empirically verified —
# --unshare-all fails getaddrinfo('api.anthropic.com'); +--share-net connects on
# :443 while /workspaces stays unreachable.  --share-net is only valid combined
# with --unshare-all (bwrap requires that pairing).
_BWRAP_BASE_FLAGS = [
    "--unshare-all",
    "--share-net",
    "--die-with-parent",
    "--proc", "/proc",
    "--dev", "/dev",
    "--ro-bind", "/usr", "/usr",
    "--ro-bind", "/etc", "/etc",
    "--symlink", "/usr/lib", "/lib",
    "--symlink", "/usr/lib64", "/lib64",
    "--symlink", "/usr/lib32", "/lib32",
    "--symlink", "/usr/bin", "/bin",
    "--symlink", "/usr/sbin", "/sbin",
    "--tmpfs", "/tmp",
    "--tmpfs", "/run",
]

# unshare fallback: user namespace + mount namespace
_UNSHARE_FLAGS = ["--user", "--mount", "--map-root-user"]

_PROBE_TIMEOUT_SECS = 5


# ---------------------------------------------------------------------------
# Public exception
# ---------------------------------------------------------------------------


class ContainmentUnavailable(RuntimeError):
    """Raised when OS-level containment cannot be established.

    This is a hard error by design: the caller must decide whether to abort
    or explicitly opt out via PLAYGROUND_ALLOW_UNCONTAINED=1.
    """


class AuthConfigUnavailable(RuntimeError):
    """Raised when the mandatory ~/.claude auth-config dir is absent (AC-12).

    ~/.ccs is optional (a non-CCS host is fully supported); ~/.claude is not
    — without it neither native `claude` nor `ccs` can authenticate inside
    the jail, so the launch is refused rather than starting a session that
    will only fail with "Not logged in".
    """


# ---------------------------------------------------------------------------
# Probe functions (called lazily, not at import time)
# ---------------------------------------------------------------------------


def probe_bwrap() -> bool:
    """Return True if ``bwrap --unshare-all ... echo`` succeeds.

    Why lazy probe (not module-level cache): the test suite may monkeypatch
    subprocess.run before calling wrap_with_containment; a module-level probe
    would run before the patch and give a stale result.
    """
    try:
        result = subprocess.run(
            [
                "bwrap",
                "--unshare-all",
                "--ro-bind", "/usr", "/usr",
                "--ro-bind", "/etc", "/etc",
                "--symlink", "/usr/lib", "/lib",
                "--symlink", "/usr/lib64", "/lib64",
                "--symlink", "/usr/lib32", "/lib32",
                "--symlink", "/usr/bin", "/bin",
                "--symlink", "/usr/sbin", "/sbin",
                "--dev", "/dev",
                "--proc", "/proc",
                "--tmpfs", "/tmp",
                "echo",
            ],
            capture_output=True,
            timeout=_PROBE_TIMEOUT_SECS,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def probe_unshare() -> bool:
    """Return True if ``unshare --user --mount --map-root-user true`` succeeds."""
    try:
        result = subprocess.run(
            ["unshare", "--user", "--mount", "--map-root-user", "true"],
            capture_output=True,
            timeout=_PROBE_TIMEOUT_SECS,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def _auth_config_binds(claude_dir: str, ccs_dir: str) -> list[str]:
    """Return bwrap ``--bind`` flags for the host auth-config dirs (AC-12).

    ~/.claude is MANDATORY: raises AuthConfigUnavailable if absent — neither
    native `claude` nor `ccs` can authenticate inside the jail without it.
    ~/.ccs is OPTIONAL: bound only if present, silently skipped otherwise (a
    non-CCS host is fully supported).

    Why both dirs are bound TOGETHER, read-WRITE, at their REAL absolute
    paths (not copied, not read-only):
      `~/.ccs/shared/{agents,commands,skills,plugins,settings.json}` are
      symlinks that resolve into `~/.claude/*`. Binding ~/.ccs without also
      binding ~/.claude leaves those symlink targets absent inside the jail;
      `ccs` then judges them "broken" and its auto-recovery DELETES the REAL
      symlinks on the host — this happened once and required manual repair
      (`~/.ccs doctor --fix`) — see
      plans_and_protocols/2026-07-04_09_protocol_ccs-auth-in-jail-findings.md
      §CRITICAL incident. Binding both together keeps the symlink web
      consistent so no destructive recovery can trigger. RW (not read-only)
      because a real session WRITES session state/credentials refresh into
      these dirs during normal use.
    """
    if not os.path.isdir(claude_dir):
        raise AuthConfigUnavailable(
            f"~/.claude ({claude_dir}) is required for the contained child "
            "session to authenticate — native `claude` reads its OAuth "
            "credentials from here, and `ccs` cannot work without it either "
            "(its shared/* entries are symlinks into ~/.claude). Launch refused."
        )
    binds = ["--bind", claude_dir, claude_dir]
    if os.path.isdir(ccs_dir):
        binds += ["--bind", ccs_dir, ccs_dir]
    return binds


def _build_bwrap_cmd(
    cmd: list[str],
    harness_dir: str,
    *,
    claude_dir: Optional[str] = None,
    ccs_dir: Optional[str] = None,
) -> list[str]:
    """Construct the bwrap command that confines ``cmd`` to ``harness_dir``.

    The harness is bound RW so the child can write inside it; everything
    else on the host filesystem is absent (not bound at all) EXCEPT the
    auth-config dirs (AC-12), bound so the child can authenticate.

    Args:
        claude_dir/ccs_dir: injectable overrides for tests (tmp dirs only —
            never point these at the real host dirs from a test). Default to
            the real ``~/.claude`` / ``~/.ccs`` via ``os.path.expanduser``,
            resolved at call time (not a module-level constant) so tests that
            monkeypatch HOME still see the correct path.
    """
    if claude_dir is None:
        claude_dir = os.path.expanduser("~/.claude")
    if ccs_dir is None:
        ccs_dir = os.path.expanduser("~/.ccs")
    return [
        "bwrap",
        *_BWRAP_BASE_FLAGS,
        "--bind", harness_dir, harness_dir,
        *_auth_config_binds(claude_dir, ccs_dir),
        "--chdir", harness_dir,
        *cmd,
    ]


def _build_unshare_cmd(cmd: list[str]) -> list[str]:
    """Wrap ``cmd`` in a user+mount namespace via ``unshare``."""
    return ["unshare", *_UNSHARE_FLAGS, *cmd]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def wrap_with_containment(
    cmd: list[str],
    harness_dir: str,
    *,
    probe_fn: Optional[Callable[[], bool]] = None,
) -> list[str]:
    """Wrap cmd in OS-level containment or raise ContainmentUnavailable.

    Tries bwrap first (preferred: host tree absent), falls back to unshare
    (host tree present but child unprivileged on host), then raises if
    neither is available.

    Args:
        cmd: The child command to wrap.
        harness_dir: Path to the harness directory.  bwrap binds only this
            path RW; everything else on the host is absent.
        probe_fn: Injectable probe for tests.  When supplied, it is used
            instead of the default bwrap-then-unshare detection sequence.
            If it returns True, bwrap is attempted; if False, falls through
            to unshare; if both fail, ContainmentUnavailable is raised.

    Returns:
        The wrapped command list.

    Raises:
        ContainmentUnavailable: If no containment method is available and
            PLAYGROUND_ALLOW_UNCONTAINED is not set.

    Why probe_fn is a single callable (not separate bwrap/unshare probes):
        Tests typically want to control the single gate (available/unavailable)
        without caring which backend is selected.  Keeping one injectable
        covers both structural tests and the behavioral AC-09 test, which
        exercises the real probes via the default path.
    """
    if probe_fn is not None:
        # Test-injectable path: probe_fn True → bwrap, False → unshare probe
        if probe_fn():
            return _build_bwrap_cmd(cmd, harness_dir)
        if probe_unshare():
            return _build_unshare_cmd(cmd)
    else:
        # Production path: try bwrap first, then unshare
        if probe_bwrap():
            return _build_bwrap_cmd(cmd, harness_dir)
        if probe_unshare():
            return _build_unshare_cmd(cmd)

    allow_uncontained = os.environ.get(ALLOW_UNCONTAINED_ENV_VAR, "").strip() == "1"
    if allow_uncontained:
        _LOG.warning(
            "PLAYGROUND_ALLOW_UNCONTAINED=1 is set — running WITHOUT OS-level "
            "containment. CON-04 (absolute-path cwd-escape) is NOT closed. "
            "Do not use in production skill regression runs."
        )
        return list(cmd)

    raise ContainmentUnavailable(
        "Neither bwrap nor unshare is available (Docker seccomp policy may be "
        "blocking the syscall). The child session cannot be launched without "
        "OS-level containment. "
        f"Set {ALLOW_UNCONTAINED_ENV_VAR}=1 to explicitly opt out of containment "
        "(dev/test environments only)."
    )


def scrub_env(env: dict[str, str], harness_dir: str) -> dict[str, str]:
    """Return a copy of env with HOME and XDG_* redirected to harness_dir.

    Why: defense-in-depth — even without OS-level namespace isolation, the
    child session should write config/cache/data inside the harness rather
    than into the host user's home directory.  This does NOT close CON-04
    (the child can still use absolute paths outside the harness) but limits
    accidental data leakage from well-behaved tools that honour XDG.
    """
    scrubbed = dict(env)
    scrubbed["HOME"] = harness_dir
    scrubbed["XDG_DATA_HOME"] = os.path.join(harness_dir, ".local", "share")
    scrubbed["XDG_CONFIG_HOME"] = os.path.join(harness_dir, ".config")
    scrubbed["XDG_CACHE_HOME"] = os.path.join(harness_dir, ".cache")
    return scrubbed
