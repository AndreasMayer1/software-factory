"""Git-reset the Skill-Test Playground harness to a clean state between runs.

After each child session completes, the harness directory may have been
modified by the candidate factory skills (files created, edited, deleted).
This module restores the harness to its committed HEAD state so the next
run starts from a known-good baseline.

Why git-reset rather than a fresh clone:
  A fresh clone is slower and requires network access.  The harness is a
  git repository, so `git reset --hard HEAD` + `git clean -fdx` is fast,
  offline, and reproducible.
  Source: TASK-PROC-068-04 plans_and_protocols/2026-06-27_01_plan_walking-skeleton.md#reset

Why verify after reset:
  AC-07 requires that the harness is verifiably unmodified after reset.
  We check `git status --porcelain` and raise HarnessNotClean if any
  tracked or untracked files remain, so callers get an explicit error
  rather than silently running the next iteration on a dirty harness.

Why the own-repo guard (TASK-PROC-068-11 Change 2):
  `git reset --hard` / `git clean -fdx` resolve to the enclosing repo when
  run inside a directory that is merely a SUBDIRECTORY of a git repo (not
  its root) — e.g. the in-tree `test_harness_app/`, which lives inside the
  outer flutter_app repo and is not itself a repo root. Running reset there
  would wipe the outer repo's working tree, not just the harness. The guard
  verifies harness_dir IS the toplevel of its own repo before ever calling
  `git reset`/`git clean`; if not, it raises instead of resetting. This is
  defense-in-depth kept regardless of the ephemeral-workspace fix (Change 3)
  — reset_harness must never be safe to call only "as long as the caller
  passes the right path".
"""

# tier: B  # reusable library imported by run_skeleton; no long-lived state

import logging
import os
import subprocess
from pathlib import Path

_LOG = logging.getLogger(__name__)

_GIT_RESET_CMD = ["git", "reset", "--hard", "HEAD"]
_GIT_CLEAN_CMD = ["git", "clean", "-fdx"]
_GIT_STATUS_CMD = ["git", "status", "--porcelain"]
_GIT_TOPLEVEL_CMD = ["git", "rev-parse", "--show-toplevel"]

_SUBPROCESS_TIMEOUT_SECS = 60


class HarnessNotClean(RuntimeError):
    """Raised when the harness is not clean after a git-reset attempt.

    Carries the porcelain status output so callers can log or report the
    specific files that prevented a clean reset.
    """

    def __init__(self, harness_dir: str, status_output: str) -> None:
        self.harness_dir = harness_dir
        self.status_output = status_output
        super().__init__(
            f"Harness at {harness_dir!r} is not clean after git-reset.\n"
            f"Remaining changes:\n{status_output}"
        )


class HarnessNotOwnRepo(RuntimeError):
    """Raised when harness_dir is not the ROOT of its own git repository.

    Guards against `git reset --hard` / `git clean -fdx` resolving to an
    ENCLOSING repo (e.g. harness_dir is a subdirectory of a larger repo) —
    see the module docstring "Why the own-repo guard" for the failure mode.
    """

    def __init__(self, harness_dir: str, toplevel: str) -> None:
        self.harness_dir = harness_dir
        self.toplevel = toplevel
        super().__init__(
            f"Refusing to reset {harness_dir!r}: it is not the root of its own "
            f"git repository (repo toplevel is {toplevel!r}). Resetting here "
            "would run git reset/clean against the ENCLOSING repo."
        )


def reset_harness(harness_dir: str) -> None:
    """Git-reset the harness to HEAD and verify it is clean.

    Runs:
      0. verify harness_dir is the toplevel of its own git repo (guard)
      1. git reset --hard HEAD  (restore tracked files to committed state)
      2. git clean -fdx         (remove untracked files and ignored files)
      3. git status --porcelain (verify nothing remains)

    Args:
        harness_dir: Absolute path to the harness git repository root.

    Raises:
        HarnessNotOwnRepo: If harness_dir is not the root of its own repo.
        HarnessNotClean: If the harness is not clean after reset.
        subprocess.CalledProcessError: If a git command fails (non-zero exit).
        FileNotFoundError: If harness_dir does not exist.
    """
    harness_path = Path(harness_dir)
    if not harness_path.exists():
        raise FileNotFoundError(f"Harness directory not found: {harness_dir}")

    _verify_own_repo(harness_dir)

    _LOG.info("Resetting harness: %s", harness_dir)
    _run_git(harness_dir, _GIT_RESET_CMD)
    _run_git(harness_dir, _GIT_CLEAN_CMD)
    _verify_clean(harness_dir)
    _LOG.info("Harness reset complete and verified clean: %s", harness_dir)


def is_harness_clean(harness_dir: str) -> bool:
    """Return True if the harness has no uncommitted changes.

    Uses `git status --porcelain`; empty output means clean.
    Does not raise — returns False on any error (git not found, not a repo, etc.).
    """
    try:
        result = _run_git(harness_dir, _GIT_STATUS_CMD, check=False)
        return result.stdout.strip() == ""
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return False


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _run_git(
    cwd: str,
    cmd: list[str],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a git command in cwd and return the CompletedProcess."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=_SUBPROCESS_TIMEOUT_SECS,
        check=check,
    )


def _verify_clean(harness_dir: str) -> None:
    """Raise HarnessNotClean if porcelain status is non-empty."""
    result = _run_git(harness_dir, _GIT_STATUS_CMD)
    status = result.stdout.strip()
    if status:
        raise HarnessNotClean(harness_dir, status)


def _verify_own_repo(harness_dir: str) -> None:
    """Raise HarnessNotOwnRepo unless harness_dir IS its repo's toplevel.

    Why realpath on both sides: harness_dir may be passed via a symlinked
    path (e.g. through a tmp dir on macOS, or a devcontainer bind mount);
    `git rev-parse --show-toplevel` always resolves symlinks, so comparing
    the raw strings could reject a legitimate own-repo case.
    """
    result = _run_git(harness_dir, _GIT_TOPLEVEL_CMD, check=False)
    toplevel = result.stdout.strip()
    if result.returncode != 0 or not toplevel:
        raise HarnessNotOwnRepo(harness_dir, toplevel or "<not a git repository>")
    if os.path.realpath(toplevel) != os.path.realpath(harness_dir):
        raise HarnessNotOwnRepo(harness_dir, toplevel)
