"""Deploy a candidate factory snapshot into the Skill-Test Playground harness.

A "candidate factory" is a snapshot of the **whole** host factory project —
not just `.claude/skills/` — copied into the harness directory so that a
child `claude` session launched with `cwd=harness_dir` sees the candidate as
its own self-contained factory, including any skill that shells out to
`scripts/` (REQ-PROC-068 AC-10; see TASK-PROC-068-16).

Why snapshot rather than symlink:
  Symlinks would let the child session modify the host factory tree through
  the link.  A real copy gives the child an isolated working set.
  Source: TASK-PROC-068-04 plans_and_protocols/2026-06-27_01_plan_walking-skeleton.md#deploy
"""

# tier: B  # reusable library imported by run_skeleton; no long-lived state

import logging
import os
import shutil
from pathlib import Path

_LOG = logging.getLogger(__name__)

# Relative path within a factory project to the skills directory
_SKILLS_SUBPATH = os.path.join(".claude", "skills")

# TEMPORARY: coarse, exclude-based whole-factory copy boundary. Pre-extraction,
# factory and app content share one repo with no clean folder cut (entangled
# trees: requirements_tasks/, requirements_user_needs/, scripts/, doc/).
# Exclude-based so factory growth is copied by default; over-inclusion is
# safe (harness is isolated + git-reset between runs; AC-09 covers reaching
# *out* of the jail, not extra content copied *in*). Replace with "copy
# whatever the extracted factory project provides" once REQ-PROC-066 extracts
# the factory into its own project (not yet scheduled).
# Source: TASK-PROC-068-16 goal.md + seed plan "Pre-extraction exclude set".
_TOP_LEVEL_EXCLUDES = frozenset(
    {
        # Tooling/dotdirs
        ".codegraph",
        ".dart_tool",
        ".idea",
        ".roo_archive",
        ".vscode",
        ".VSCodeCounter",
        ".git",
        ".github",
        ".githooks",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        # Git-worktree / ephemeral-playground-workspace scratch area
        # (scripts/dev_env/worktree_root.py, scripts/playground/workspace.py).
        # MUST be excluded, not just "safe to skip": deploy_candidate snapshots
        # the whole host_project_dir tree INTO a workspace that itself lives
        # under host_project_dir/.worktree/. Without this exclusion the copy
        # is self-referential — it walks into its own not-yet-finished
        # destination and recurses until the OS path-length limit aborts it.
        ".worktree",
        # Platform/build/app assets
        "android",
        "assets",
        "build",
        "coverage",
        "doc-temp",
        "web",
        "windows",
        "Temp",
        "figma",
        "ios",
        "linux",
        "macos",
        "packages",
        # App code/tests
        "lib",
        "integration_test",
        "test",
        "test_driver",
        "test_hive",
        # Other non-factory
        "dev-analytics",
        "releases",
        "requirements_market_research",
        "requirements_general_overview",
        # automation/ is host-operational state (orchestrator logs, reports,
        # pending_feedback/) — authoring-time/orchestrator input, never a
        # harness-runtime input a deployed skill reads for its own sake. Its
        # absence here fixed a real defect (TASK-PROC-068-34): build.py's
        # has_recorded_blocker globs the deployed copy for
        # automation/pending_feedback/*/question.md with no baseline diff, so
        # deploying the host's own pre-existing, unrelated standing questions
        # made EVERY maintenance run misclassify BLOCKED regardless of what the
        # child did. Residual AC-10-class risk (same class as the
        # _scribble_components/id_registry precedent, TASK-PROC-068-19): the
        # claude-automated-mode skill's genuine-escalation procedure `cp`s
        # automation/pending_feedback/TEMPLATE_answer.md — a child that hits a
        # REAL blocker mid-run will find that template absent. Not
        # pre-emptively worked around; escalate if a real run actually hits it.
        "automation",
        # Deploy target itself, not factory content — a naive "test*" glob
        # would otherwise sweep it in (risk 1, TASK-PROC-068-16 goal.md).
        "test_harness_app",
    }
)

# Sub-folder excludes inside otherwise-copied entangled trees (risk 2,
# TASK-PROC-068-16 goal.md): requirements_tasks/ mixes the factory's own
# process/AI_rules/** corpus with app requirements under functional/ and
# non-functional/.
#
# requirements_tasks/process/ is excluded because it is an AUTHORING-TIME
# input, not a HARNESS-RUNTIME input (TASK-PROC-068-19). Those ~130
# process/AI_rules/**/requirements.md files are the specs that DEFINE the
# factory's own skills/scripts — read only when *authoring* those skills,
# which never happens inside the harness (the harness runs candidate skills
# against a product; it does not develop the factory). Deploying them served
# no runtime need and was the root of the build-mode harvest over-inclusion:
# the full-registry harvest's `requirements_tasks/**/requirements.md` glob
# swept them into test_harness_app/. Build mode harvests before discarding
# and never git-resets, so (unlike test-mode's reset) the over-inclusion
# persisted. Excluding process/ at deploy removes it at the root — nothing to
# sweep in. (AC-10 still holds: skills run end-to-end without process/, proven
# in TASK-PROC-068-19; if a skill is ever found to read a process spec at
# runtime, that is an AC-10 tension to escalate, not silently re-include.)
#
# requirements_user_needs/ is the same entangled-tree case, one level up:
# the factory MACHINERY that lives there (README_*.md authoring guides,
# SCENARIO_INDEX.md, _meta/, CHANGE_PROPAGATION.md) is needed by the
# candidate factory's own authoring skills (e.g. ux-write-persona,
# ux-write-scenario) when they run inside the harness, so it must be
# present under the run cwd. The mood-tracker's own product CONTENT
# (personas/, user_flows/) must NOT be — only the sub-folders are excluded,
# not the whole top-level directory (TASK-PROC-068-11 plan, Change 1).
#
# requirements_user_needs/_meta/project/ is the E' contract-first per-project
# concern DATA (role_tags.yaml, domain.yaml — REQ-PROC-066 T1/T2): it is Layer-P
# leaf content specific to THIS project (flutter), same leak-containment case as
# personas/ and user_flows/ above — must not ship into the harness's isolated
# deployed copy (leak-containment C3, _009 D4#5 / _010 T1).
#
# requirements_tasks/_scribble_components/ holds THIS flutter app's wireframe
# component definitions (c_app_bar, c_mood_entry_card, …) — app-specific product
# content, not factory machinery, so it is excluded as leak-containment (same
# class as personas/ and user_flows/; developer decision, TASK-PROC-068-19). The
# net-new harvest (build.py, Option B) already stops it from leaking on harvest;
# excluding it from deploy keeps the harness's isolated copy free of foreign app
# content entirely. (Deferred: an exhaustive deploy-exclude enumeration of every
# app-specific / script-generated path waits for the REQ-PROC-066 factory
# extraction — Option B makes it non-urgent for harvest correctness.)
#
# requirements_user_needs/product_materialization/ is the harness's OWN
# factory-runtime provenance — the materialization decision-record plus the
# ideation index/ledger backing it (REQ-PROC-068 AC-11 reword tail). The harness
# derives and retains this itself as project data of the standalone harness, so
# deploying the transient factory's copy would clobber that own provenance.
# Excluding it keeps the harness's materialization provenance intact
# (leak-containment, same class as personas/user_flows above; TASK-PROC-068-33).
_SUBFOLDER_EXCLUDES = frozenset(
    {
        os.path.join("requirements_tasks", "functional"),
        os.path.join("requirements_tasks", "non-functional"),
        os.path.join("requirements_tasks", "process"),
        os.path.join("requirements_tasks", "_scribble_components"),
        os.path.join("requirements_user_needs", "personas"),
        os.path.join("requirements_user_needs", "user_flows"),
        os.path.join("requirements_user_needs", "_meta", "project"),
        os.path.join("requirements_user_needs", "product_materialization"),
    }
)


def _make_ignore(src_root: Path):  # type: ignore[no-untyped-def]  # shutil.copytree's ignore callback type is untyped in typeshed
    """Build a shutil.copytree ignore callback bound to src_root.

    Applies _TOP_LEVEL_EXCLUDES only at the copy root, and _SUBFOLDER_EXCLUDES
    at their exact relative path, anywhere in the tree.
    """

    def _ignore(current_dir: str, names: list[str]) -> set[str]:
        rel_dir = os.path.relpath(current_dir, src_root)
        ignored: set[str] = set()
        for name in names:
            if rel_dir == os.curdir:
                if name in _TOP_LEVEL_EXCLUDES:
                    ignored.add(name)
                continue
            if os.path.join(rel_dir, name) in _SUBFOLDER_EXCLUDES:
                ignored.add(name)
        return ignored

    return _ignore


def deploy_candidate(host_project_dir: str, harness_dir: str) -> None:
    """Copy the whole host factory project into harness_dir.

    Merges into any existing harness_dir content (does not remove the
    harness's own `.git` or other pre-existing files) — cleanup of a prior
    run's leftovers is `reset_harness()`'s job, not deploy's.

    Args:
        host_project_dir: Root of the host factory project (source).
        harness_dir: Root of the test harness (deployment target).

    Raises:
        FileNotFoundError: If host_project_dir does not exist.
        OSError: If the copy fails (permissions, disk space, etc.).
    """
    src = Path(host_project_dir)
    dst = Path(harness_dir)

    if not src.exists():
        raise FileNotFoundError(
            f"Host project directory not found: {src}. "
            "Cannot deploy candidate factory."
        )

    _LOG.info("Deploying whole factory: %s → %s", src, dst)

    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=_make_ignore(src), dirs_exist_ok=True)

    _LOG.info(
        "Deployment complete: %d skill entries copied",
        _count_entries(dst / _SKILLS_SUBPATH),
    )


def _count_entries(directory: Path) -> int:
    """Return the number of immediate children of directory."""
    try:
        return sum(1 for _ in directory.iterdir())
    except OSError:
        return 0


def list_deployed_skills(harness_dir: str) -> list[str]:
    """Return sorted list of skill names deployed in harness_dir.

    Returns an empty list if no skills are deployed yet.
    """
    dst = Path(harness_dir) / _SKILLS_SUBPATH
    if not dst.exists():
        return []
    return sorted(entry.name for entry in dst.iterdir() if entry.is_dir())
