"""Ephemeral-workspace lifecycle for the Skill-Test Playground (TASK-PROC-068-11).

Three entry points, composed by run_skeleton.py:
  - create_workspace(host_project_dir, harness_app_dir, session_uuid) -> workspace path
  - init_workspace_git(workspace)  -- makes the workspace its own git repo
  - destroy_workspace(workspace)   -- tears it down

Why a workspace outside test_harness_app, under the host project's .worktree/:
  The persistent `test_harness_app/` product tree lives IN-TREE, inside the host
  factory project (flutter_app), and is therefore NOT its own git repository --
  it is just a subdirectory of the outer repo. `reset_harness()` runs `git reset
  --hard` + `git clean -fdx`, and Change 2's own-repo guard (reset.py) makes that
  a hard failure when pointed at a non-repo-root. Deploying/running/resetting
  directly against test_harness_app would either fail the guard (safe but
  unusable) or -- absent the guard -- run `git reset --hard` against the OUTER
  flutter_app repo (catastrophic). The fix moves the run's deploy target/reset
  target to a throwaway directory under `<host_project_dir>/.worktree/`,
  seeded by copying the persistent test_harness_app tree, then `git init`-ed
  there so it genuinely is its own repo root. test_harness_app itself becomes
  a read-only seed, never touched.

  Nesting the workspace inside the host project tree (rather than beside it)
  is safe specifically because the workspace is git-inited as its own repo:
  `git rev-parse --show-toplevel` (what reset.py's own-repo guard reads) walks
  up to the NEAREST ancestor `.git`, which is the workspace's own -- it never
  sees the outer flutter_app repo. `.worktree/` is also gitignored, so the
  outer repo's `status`/`add` never observes the nested repo either. The
  earlier sibling-of-host placement avoided nesting only because this wasn't
  understood at the time, not because of an actual footgun.
  Source: TASK-PROC-068-11 plan
  plans_and_protocols/2026-07-04_07_plan_ephemeral-workspace-and-deploy-fix.md#Change 3
"""

# tier: B  # reusable library imported by run_skeleton; no long-lived state

import logging
import os
import shutil
import subprocess

_LOG = logging.getLogger(__name__)

# Prefix every ephemeral workspace directory name carries. destroy_workspace's
# safety guard trusts this prefix as proof "this path is a workspace we made,
# not the host project / harness seed / anything enclosing them" -- see
# destroy_workspace's docstring for why that is sufficient.
_WORKSPACE_PREFIX = "playground_ws_"

_SUBPROCESS_TIMEOUT_SECS = 60
_GIT_USER_EMAIL = "playground@localhost"
_GIT_USER_NAME = "Skill-Test Playground"

# Persistent-harness-git conventions (REQ-PROC-068 AC-20, TASK-PROC-068-31).
# The bundle lives WITH the harness inside the container project (never an OS
# temp dir): <harness_app_dir>/.playground_harness_git/harness.bundle.
# create_workspace EXCLUDES this directory from the seed copy — if the bundle
# file were copied into the workspace it would be committed into the workspace's
# own history and re-exported into every later bundle (self-referential,
# unbounded growth), and a test-mode copy must carry no persisted history at all.
HARNESS_GIT_DIRNAME = ".playground_harness_git"
HARNESS_BUNDLE_FILENAME = "harness.bundle"

# Single-branch convention for maintenance-mode history: every persisted bundle
# carries exactly refs/heads/<MAINTENANCE_BRANCH>, so restore never has to
# discover which branch a bundle's HEAD pointed at.
MAINTENANCE_BRANCH = "main"

# Temporary unborn branch restore_workspace_git inits on. Deliberately NOT
# MAINTENANCE_BRANCH: `git fetch` refuses to update the currently checked-out
# branch ref, so the fetch below must land on a branch that is never current.
# The unborn temp branch has no ref and simply vanishes once HEAD moves.
_RESTORE_TMP_BRANCH = "playground_restore_tmp"


class WorkspaceError(RuntimeError):
    """Raised when workspace create/init/destroy fails for an I/O or git reason.

    Kept distinct from the ValueError raised by destroy_workspace's safety
    guard: a guard trip is a refusal-to-act (a bug in the CALLER passing a
    wrong path), while WorkspaceError is a failure of the action itself
    (copy failed, git command failed). Conflating them would let a caller
    catch-all past the guard and silently ignore what should be a loud stop.
    """


def create_workspace(
    host_project_dir: str,
    harness_app_dir: str,
    session_uuid: str,
    workspace_root: str | None = None,
) -> str:
    """Create a throwaway run workspace, seeded from harness_app_dir.

    The workspace lives at ``<parent>/playground_ws_<uuid8>`` -- never a
    descendant of harness_app_dir itself (test_harness_app stays a read-only
    seed). ``parent`` defaults to ``<host_project_dir>/.worktree``; when
    ``workspace_root`` is given it is used as ``parent`` instead (build mode
    passes the config-resolved worktree root here -- worktree_root.py +
    worktree.config.json -- so the copy lands at the same configured
    location, REQ-PROC-068 AC-13). The default and the worktree-root default
    coincide, so run_skeleton's existing callers are unaffected. Idempotent: a
    leftover workspace from a crashed prior run (same first 8 chars of
    session_uuid) is removed first via destroy_workspace, so its own-prefix
    safety guard applies even to this internal cleanup.

    Does NOT deploy the candidate factory or git-init the workspace -- callers
    compose those separately (deploy_candidate, init_workspace_git) to keep
    this function single-purpose.

    Args:
        host_project_dir: Root of the host factory project. Its ``.worktree``
            subdirectory is where the workspace is created (unless
            workspace_root overrides it).
        harness_app_dir: Root of the persistent test_harness_app seed tree,
            copied wholesale into the new workspace.
        session_uuid: The run's session UUID; first 8 chars name the workspace.
        workspace_root: Optional explicit parent directory for the workspace.
            When None, ``<host_project_dir>/.worktree`` is used.

    Returns:
        Absolute path to the newly created workspace directory.

    Raises:
        FileNotFoundError: If harness_app_dir does not exist.
        WorkspaceError: If the copy fails for any other OS reason.
    """
    if workspace_root is not None:
        parent = os.path.realpath(workspace_root)
    else:
        parent = os.path.join(os.path.realpath(host_project_dir), ".worktree")
    os.makedirs(parent, exist_ok=True)
    workspace = os.path.join(parent, f"{_WORKSPACE_PREFIX}{session_uuid[:8]}")

    if os.path.exists(workspace):
        _LOG.info("Removing leftover workspace from a prior run: %s", workspace)
        destroy_workspace(workspace)

    if not os.path.exists(harness_app_dir):
        raise FileNotFoundError(f"Harness seed directory not found: {harness_app_dir}")

    _LOG.info("Creating ephemeral workspace: %s -> %s", harness_app_dir, workspace)
    try:
        # ignore= excludes the persisted-bundle dir from the seed copy — see
        # HARNESS_GIT_DIRNAME's comment for why copying it in would make every
        # later bundle grow without bound (and leak persisted history into
        # test-mode copies, which must stay history-free per AC-20).
        shutil.copytree(
            harness_app_dir,
            workspace,
            ignore=shutil.ignore_patterns(HARNESS_GIT_DIRNAME),
        )
    except OSError as exc:
        raise WorkspaceError(f"Failed to create workspace at {workspace!r}: {exc}") from exc

    return workspace


def init_workspace_git(workspace: str, initial_branch: str | None = None) -> None:
    """Make workspace its own git repository with one baseline commit.

    Runs ``git init``, ``git add -A``, ``git commit`` inside workspace, with a
    local user.email/user.name supplied via -c flags (the workspace has no
    global git config of its own in a bare/CI environment, so a plain
    ``git commit`` would fail with "please tell me who you are").

    This baseline commit is what reset_harness() restores workspace to between
    fixture runs within the same session.

    Args:
        workspace: Absolute path to the ephemeral workspace (from create_workspace).
        initial_branch: Optional branch name for ``git init -b``. Maintenance
            mode passes MAINTENANCE_BRANCH so its first-ever run (no persisted
            bundle yet) already sits on the single-branch convention
            export_workspace_git_bundle persists (AC-20). Default None keeps
            the exact pre-existing behavior — test mode (run_skeleton.py) is
            deliberately unchanged (AC-07 clean-reset contract).

    Raises:
        WorkspaceError: If any git command fails.
    """
    init_cmd = ["git", "init", "-q"]
    if initial_branch is not None:
        init_cmd += ["-b", initial_branch]
    _run_git(workspace, init_cmd)
    _commit_baseline(workspace)


def harness_git_bundle_path(harness_app_dir: str) -> str:
    """Return the persisted-bundle path for a harness tree (AC-20 storage convention).

    ``<harness_app_dir>/.playground_harness_git/harness.bundle`` — with the
    harness inside the container project, never an OS temp dir. Absolute, so it
    stays valid as a git remote/refspec argument regardless of the cwd the git
    subprocess runs in (restore/export run with cwd=workspace).
    """
    return os.path.join(
        os.path.realpath(harness_app_dir), HARNESS_GIT_DIRNAME, HARNESS_BUNDLE_FILENAME
    )


def restore_workspace_git(workspace: str, bundle_path: str) -> None:
    """Init workspace git by restoring the persisted harness history (AC-20).

    Replaces the fresh-``git init`` baseline for a maintenance-mode deploy when
    a persisted bundle exists: the workspace's MAINTENANCE_BRANCH is fetched
    from the bundle, HEAD is pointed at it WITHOUT touching the worktree/index
    (``git symbolic-ref``), and the freshly deployed+seeded content is committed
    on top as a new baseline. The baseline commit is therefore a CHILD of the
    persisted tip — every commit an earlier run's artifact references stays
    reachable with a stable hash (the backward-reference constraint; see the
    fixed design in TASK-PROC-068-28's protocol).

    The init uses a temporary unborn branch (_RESTORE_TMP_BRANCH), never
    MAINTENANCE_BRANCH itself: git refuses to fetch into the currently
    checked-out branch ref, and controlling the temp name also shields against
    an ``init.defaultBranch`` config that happens to equal MAINTENANCE_BRANCH.

    Args:
        workspace: Absolute path to the ephemeral workspace (deployed + seeded).
        bundle_path: Absolute path to the persisted harness bundle (must exist).

    Raises:
        WorkspaceError: If any git command fails (including a corrupt bundle —
            fail loud, never fall back to a fresh init that would silently
            orphan every previously persisted commit reference).
    """
    branch_ref = f"refs/heads/{MAINTENANCE_BRANCH}"
    _run_git(workspace, ["git", "init", "-q", "-b", _RESTORE_TMP_BRANCH])
    _run_git(
        workspace,
        ["git", "fetch", "-q", os.path.realpath(bundle_path), f"+{branch_ref}:{branch_ref}"],
    )
    _run_git(workspace, ["git", "symbolic-ref", "HEAD", branch_ref])
    _commit_baseline(workspace)


def export_workspace_git_bundle(workspace: str, bundle_path: str) -> None:
    """Persist the workspace's advanced history back to the harness bundle (AC-20).

    Normalizes the current branch to MAINTENANCE_BRANCH first (``git branch -M``
    — a no-op when already on it) so a legacy preserved workspace resumed from
    before the single-branch convention still exports the ref restore expects.
    The bundle is written to a sibling ``.tmp`` path and moved into place with
    ``os.replace`` — atomic on POSIX — so a failed export can never truncate or
    corrupt the existing persisted bundle (the only copy of prior runs'
    history once their workspaces are discarded).

    Args:
        workspace: Absolute path to the ephemeral workspace (has >= 1 commit).
        bundle_path: Destination bundle path (harness_git_bundle_path). Parent
            directory is created if absent.

    Raises:
        WorkspaceError: If any git command fails.
        OSError: If the atomic replace itself fails.
    """
    dest = os.path.realpath(bundle_path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = f"{dest}.tmp"
    _run_git(workspace, ["git", "branch", "-M", MAINTENANCE_BRANCH])
    _run_git(
        workspace,
        ["git", "bundle", "create", tmp, f"refs/heads/{MAINTENANCE_BRANCH}"],
    )
    os.replace(tmp, dest)


# A squashable tail must contain at least this many commits: replacing a single
# unreferenced tip with a single squash commit rewrites a hash without shrinking
# history — churn with zero compaction gain.
_MIN_SQUASHABLE_TAIL = 2


def compact_workspace_git(
    workspace: str, bundle_path: str, referenced_commits: set[str]
) -> int:
    """Squash the history's unreferenced tail before persist-on-harvest (AC-20).

    Implements the fixed compaction policy (TASK-PROC-068-28 design protocol):
    preserve every referenced commit with a stable hash, omit unreferenced
    intermediates, never rewrite commits persisted by a prior run. Because a
    commit hash covers its full ancestry, preserving a referenced commit's hash
    freezes ALL its ancestors too — so on the linear maintenance history the
    only legally squashable region is the TRAILING segment above the newest
    preserved point (the prior persisted tip recovered from the pre-run
    ``bundle_path``, or a resolved member of ``referenced_commits``, whichever
    is newest). That segment — this run's own unreferenced tail, which nothing
    references and no prior run has persisted — is replaced by ONE commit
    carrying the tip's tree, so worktree content (and the already-completed
    harvest) stays byte-identical. Unreferenced commits BELOW a preserved point
    are that point's ancestors: their hashes are frozen by the
    backward-reference constraint itself and correctly stay untouched.

    Compaction is an optimization; reachability is the correctness property.
    Semantic surprises therefore degrade to a safe no-op (return 0 — the full
    history is persisted as-is): merge commits in the history, a persisted tip
    off the first-parent line, an ambiguous reference abbreviation, or a tail
    shorter than _MIN_SQUASHABLE_TAIL. Mechanical git failures still raise
    (fail loud, matching restore/export).

    Args:
        workspace: Absolute path to the ephemeral workspace (>= 1 commit).
        bundle_path: The PRE-RUN persisted bundle path (must not have been
            re-exported yet — its head IS the prior persisted tip / the
            immutability boundary). May not exist (first maintenance run).
        referenced_commits: Raw candidate commit ids (full or abbreviated)
            found in the harvested artifacts. Candidates that do not resolve
            in the workspace repo (deployed factory-repo refs, hash-like
            noise) are dropped — resolution against THIS repo is the filter
            separating harness-git references from foreign strings.

    Returns:
        Number of commits squashed away (0 when no compaction happened).

    Raises:
        WorkspaceError: If a git command fails mechanically, or the pre-run
            bundle exists but carries no MAINTENANCE_BRANCH head.
    """
    # Same normalization as export: a legacy preserved workspace resumed from
    # before the single-branch convention may still sit on another branch name.
    _run_git(workspace, ["git", "branch", "-M", MAINTENANCE_BRANCH])
    history = _run_git(
        workspace, ["git", "rev-list", "--first-parent", MAINTENANCE_BRANCH]
    ).splitlines()
    if _run_git(workspace, ["git", "rev-list", "--merges", MAINTENANCE_BRANCH]):
        _LOG.warning("Compaction skipped: merge commits present in %s", workspace)
        return 0
    preserved = _resolve_workspace_commits(workspace, referenced_commits)
    if preserved is None:
        return 0
    persisted_tip = _persisted_bundle_tip(workspace, bundle_path)
    if persisted_tip is not None:
        if persisted_tip not in history:
            _LOG.warning(
                "Compaction skipped: persisted tip %s not on %s's first-parent line",
                persisted_tip,
                MAINTENANCE_BRANCH,
            )
            return 0
        preserved.add(persisted_tip)
    tail = _unreferenced_tail(history, preserved)
    if len(tail) < _MIN_SQUASHABLE_TAIL:
        return 0
    boundary = history[len(tail)] if len(tail) < len(history) else None
    _squash_tail_into_one(workspace, boundary, len(tail))
    return len(tail)


def _persisted_bundle_tip(workspace: str, bundle_path: str) -> str | None:
    """Prior persisted tip: sha of MAINTENANCE_BRANCH's head in the pre-run bundle.

    None when the bundle file does not exist (first maintenance run — nothing
    persisted yet, nothing immutable). Raises when the bundle exists but has no
    MAINTENANCE_BRANCH head: restore-on-deploy fetches exactly that ref, so a
    run restored from this bundle cannot legitimately observe it missing — fail
    loud rather than treat already-persisted history as squashable.
    """
    bundle = os.path.realpath(bundle_path)
    if not os.path.exists(bundle):
        return None
    heads = _run_git(workspace, ["git", "bundle", "list-heads", bundle])
    for line in heads.splitlines():
        sha, _, ref = line.strip().partition(" ")
        if ref == f"refs/heads/{MAINTENANCE_BRANCH}":
            return sha
    raise WorkspaceError(
        f"Persisted bundle {bundle!r} has no refs/heads/{MAINTENANCE_BRANCH} head"
    )


def _resolve_workspace_commits(workspace: str, candidates: set[str]) -> set[str] | None:
    """Resolve candidate ids to full shas in the workspace repo; drop the rest.

    A candidate that fails to resolve names no commit of THIS history, so
    dropping it loses nothing reachable. The single exception is an AMBIGUOUS
    abbreviation — there a real referenced commit might hide behind the failed
    resolution, so the function returns None and the caller skips compaction
    for this run entirely (preserving everything is always correct).
    """
    resolved: set[str] = set()
    for candidate in sorted(candidates):
        try:
            sha = _run_git(
                workspace,
                ["git", "rev-parse", "--verify", f"{candidate}^{{commit}}"],
            )
        except WorkspaceError as exc:
            if "ambiguous" in str(exc).lower():
                _LOG.warning(
                    "Compaction skipped: ambiguous commit reference %r", candidate
                )
                return None
            continue
        if sha:
            resolved.add(sha)
    return resolved


def _unreferenced_tail(history: list[str], preserved: set[str]) -> list[str]:
    """Longest newest-first prefix of history containing no preserved commit."""
    tail: list[str] = []
    for sha in history:
        if sha in preserved:
            break
        tail.append(sha)
    return tail


def _squash_tail_into_one(workspace: str, boundary: str | None, tail_len: int) -> None:
    """Replace the tail above ``boundary`` with one commit carrying the tip's tree.

    ``boundary`` None means the whole history is the tail (first run, nothing
    referenced): the squash commit becomes the new root. The update-ref carries
    the old tip as its expected old value, so a branch moved since rev-list
    (impossible in the single-process harvest, but cheap insurance) is refused.
    """
    tip = _run_git(workspace, ["git", "rev-parse", MAINTENANCE_BRANCH])
    tree = _run_git(workspace, ["git", "rev-parse", f"{MAINTENANCE_BRANCH}^{{tree}}"])
    cmd = [
        "git",
        "-c", f"user.email={_GIT_USER_EMAIL}",
        "-c", f"user.name={_GIT_USER_NAME}",
        "commit-tree", tree,
    ]
    if boundary is not None:
        cmd += ["-p", boundary]
    cmd += ["-m", f"playground compaction: squash of {tail_len} unreferenced commits"]
    squash = _run_git(workspace, cmd)
    _run_git(
        workspace,
        ["git", "update-ref", f"refs/heads/{MAINTENANCE_BRANCH}", squash, tip],
    )


def _commit_baseline(workspace: str) -> None:
    """Stage everything and record the "playground baseline" commit."""
    _run_git(workspace, ["git", "add", "-A"])
    _run_git(
        workspace,
        [
            "git",
            "-c", f"user.email={_GIT_USER_EMAIL}",
            "-c", f"user.name={_GIT_USER_NAME}",
            # --allow-empty: harness_app_dir may legitimately have nothing to
            # add yet (e.g. an empty seed in a test); without it, `git commit`
            # exits 1 with "nothing to commit" and the workspace never gets
            # its baseline commit, which reset_harness() requires to exist.
            # (On a bundle restore the same flag covers a workspace whose
            # content is byte-identical to the restored tip.)
            "commit", "-q", "--allow-empty", "-m", "playground baseline",
        ],
    )


def destroy_workspace(workspace: str) -> None:
    """Remove the ephemeral workspace directory tree.

    SAFETY (the reason this function exists rather than a bare shutil.rmtree
    call at the call site): refuses to act unless workspace's basename starts
    with _WORKSPACE_PREFIX. Every real workspace create_workspace() ever
    returns carries that prefix; the host project, the harness seed, and any
    path enclosing either of them never do (barring deliberate, out-of-scope
    sabotage of the naming scheme). The prefix check is therefore sufficient
    to make it IMPOSSIBLE for this function to rmtree the host project dir,
    the harness seed dir, or any ancestor of either -- exactly the failure
    mode this whole change exists to close off.

    Args:
        workspace: Absolute path to the ephemeral workspace.

    Raises:
        ValueError: If workspace does not look like a workspace this module
            created (basename does not start with _WORKSPACE_PREFIX, or the
            path resolves to the filesystem root).
        WorkspaceError: If shutil.rmtree fails for an OS reason.
    """
    resolved = os.path.realpath(workspace)
    basename = os.path.basename(resolved.rstrip(os.sep))

    if not basename.startswith(_WORKSPACE_PREFIX):
        raise ValueError(
            f"Refusing to rmtree {workspace!r} (resolved: {resolved!r}): basename "
            f"does not start with {_WORKSPACE_PREFIX!r}. destroy_workspace only "
            "removes ephemeral playground workspaces created by create_workspace() "
            "-- never the host project, the harness seed, or anything enclosing them."
        )
    if resolved == os.path.sep:
        raise ValueError(f"Refusing to rmtree the filesystem root: {resolved!r}")

    _LOG.info("Destroying ephemeral workspace: %s", resolved)
    try:
        shutil.rmtree(resolved, ignore_errors=False)
    except OSError as exc:
        raise WorkspaceError(f"Failed to destroy workspace at {resolved!r}: {exc}") from exc


def _run_git(cwd: str, cmd: list[str]) -> str:
    """Run a git command in cwd, return stripped stdout; wrap failure as WorkspaceError."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=_SUBPROCESS_TIMEOUT_SECS,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise WorkspaceError(f"git command {cmd!r} failed in {cwd!r}: {exc.stderr}") from exc
    except subprocess.TimeoutExpired as exc:
        raise WorkspaceError(f"git command {cmd!r} timed out in {cwd!r}") from exc
    except OSError as exc:
        # e.g. FileNotFoundError when cwd does not exist, or git itself is missing.
        raise WorkspaceError(f"git command {cmd!r} could not run in {cwd!r}: {exc}") from exc
