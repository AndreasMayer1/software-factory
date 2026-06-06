#!/usr/bin/env python3
# ruff: noqa: RUF002, RUF100
# RUF002: docstring uses the en dash intentionally for numeric ranges like stage 0 to 5.
# RUF100: false-positive on file-level noqa for codes ruff cannot introspect into the file body.
"""
Print a human-readable summary of where the project stands for the next
(lowest planned or active) release.

Stages:
  0 — No requirements-authoring tasks exist for the next release
  1 — Requirements-authoring tasks exist but not all completed
  2 — Requirements complete, but packages not all assigned to a release
  3 — Packages assigned, release not yet active
  4 — Release active, impl tasks being created / executed
  5 — All impl tasks done — ready to cut the release

Usage:
  python3 scripts/release_readiness.py

Output:
    Prints a human-readable readiness section per stage (releases, pending tasks, last commit, gates) and a final stage number 1-5 to stdout.
"""

# tier: C  # one-shot CLI release-pipeline script; no in-tree Python imports

import os
import sys
from pathlib import Path
from typing import Any, cast

# Why: this script runs both as `python3 scripts/release/release_readiness.py`
# (standalone, no PYTHONPATH) and via pytest (which adds project root to sys.path).
# Add scripts/ to sys.path so `from util.yaml_frontmatter import ...` resolves
# regardless of invocation path.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    FrontmatterError,
    read_frontmatter,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent
RELEASES_FILE = PROJECT_ROOT / "requirements_tasks" / "RELEASES.md"
RELEASE_BACKLOG_FILE = PROJECT_ROOT / "requirements_tasks" / "RELEASE_BACKLOG.md"
AUTOMATED_MODE_FILE = PROJECT_ROOT / "automation" / ".automated_mode"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_yaml_frontmatter(path: Path) -> dict[Any, Any]:
    """Extract YAML frontmatter from a file via the central helper.

    Returns an empty dict on missing file, no frontmatter, or malformed YAML.
    """
    if not path.exists():
        return {}
    try:
        doc = read_frontmatter(path)
    except (FrontmatterError, OSError):
        return {}
    if not doc.has_frontmatter:
        return {}
    return dict(doc.metadata) if doc.metadata else {}


def _parse_frontmatter_fields(path: Path, fields: list[Any]) -> dict[Any, Any]:
    """Extract specific fields from YAML frontmatter as strings.

    Delegates to the central helper, then projects/coerces the requested
    fields to strings (with quote-stripping for backward compatibility with
    callers that used to receive raw line text).
    """
    meta = _parse_yaml_frontmatter(path)
    if not meta:
        return {}
    result: dict[Any, Any] = {}
    for field in fields:
        if field in meta:
            value = meta[field]
            if value is None:
                continue
            # Coerce bool to lowercase string for legacy compatibility:
            # callers compare to literal "true"/"false" strings.
            if isinstance(value, bool):
                result[field] = "true" if value else "false"
            else:
                result[field] = str(value).strip().strip('"').strip("'")
    return result


def _parse_semver(version: str) -> tuple[Any, ...]:
    parts = str(version).split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (999, 999, 999)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_next_release() -> dict[Any, Any] | None:
    """Return the lowest active or planned release, or None if none found."""
    data = _parse_yaml_frontmatter(RELEASES_FILE)
    releases = data.get("releases", [])
    if not releases:
        return None
    candidates = [r for r in releases if r.get("status") in ("active", "planned")]
    if not candidates:
        return None
    return cast("dict[Any, Any] | None", min(candidates, key=lambda r: _parse_semver(r.get("version", "999"))))


def load_release_packages(release: dict[Any, Any]) -> list[Any]:
    """Return list of package IDs for the given release."""
    return cast("list[Any]", release.get("packages", []))


def load_backlog_packages() -> list[Any]:
    """Return all packages from RELEASE_BACKLOG.md."""
    data = _parse_yaml_frontmatter(RELEASE_BACKLOG_FILE)
    return cast("list[Any]", data.get("packages", []))


def find_goal_files() -> list[Any]:
    """Find all goal.md files in requirements_tasks/."""
    base = PROJECT_ROOT / "requirements_tasks"
    return list(base.rglob("goal.md"))


# ---------------------------------------------------------------------------
# Stage checks
# ---------------------------------------------------------------------------

def check_requirements_ready() -> tuple[bool, list[Any], int, int]:
    """
    Returns (is_ready, blocking_paths, completed_count, total_count).
    Mirrors logic from scripts/check_requirements_ready.py.
    """
    goal_files = find_goal_files()
    completed = []
    blocking = []

    for path in goal_files:
        fields = _parse_frontmatter_fields(path, ["writes_requirements", "status"])
        if fields.get("writes_requirements") != "true":
            continue
        status = fields.get("status", "")
        if status == "completed":
            completed.append(path)
        elif status in ("pending", "in_progress"):
            blocking.append(path)

    total = len(completed) + len(blocking)
    if not completed and not blocking:
        return False, [], 0, 0  # Stage 0: no authoring tasks
    if blocking:
        return False, blocking, len(completed), total
    return True, [], len(completed), total


def check_packages_assigned(release_packages: list[Any], backlog_packages: list[Any]) -> tuple[bool, list[Any], int]:
    """
    Check whether all packages for the release have assigned_release set in backlog.
    Returns (all_assigned, unassigned_package_ids, total_count).
    """
    backlog_by_id = {p.get("id"): p for p in backlog_packages if isinstance(p, dict)}
    unassigned = []
    for pkg_id in release_packages:
        entry = backlog_by_id.get(pkg_id)
        if entry is None:
            unassigned.append(f"{pkg_id} (not in backlog)")
        elif not entry.get("assigned_release"):
            unassigned.append(pkg_id)
    return (len(unassigned) == 0), unassigned, len(release_packages)


def count_impl_tasks(version: str) -> tuple[int, int, list[Any]]:
    """
    Count impl tasks for a release by scanning goal.md files.
    Returns (completed_count, total_count, in_progress_paths).
    """
    goal_files = find_goal_files()
    total = 0
    completed = 0
    in_progress = []

    non_impl_types = {"explore"}

    for path in goal_files:
        fields = _parse_frontmatter_fields(
            path,
            ["target_release", "target_package", "status", "type", "writes_requirements"]
        )
        task_release = fields.get("target_release", "")
        task_status = fields.get("status", "")
        task_type = fields.get("type", "")
        writes_requ = fields.get("writes_requirements", "")

        # Only count tasks tied to this release (by target_release or target_package match)
        if task_release != version and task_release != f'"{version}"':
            continue
        # Exclude pure authoring/analysis tasks
        if writes_requ == "true":
            continue
        if task_type in non_impl_types:
            continue

        total += 1
        if task_status == "completed":
            completed += 1
        elif task_status == "in_progress":
            in_progress.append(path)

    return completed, total, in_progress


def is_autorun_active() -> bool:
    """Check if the automated mode file exists (autorun is running)."""
    return AUTOMATED_MODE_FILE.exists()


# ---------------------------------------------------------------------------
# Stage detection and output
# ---------------------------------------------------------------------------

def detect_stage(release: dict[Any, Any], backlog_packages: list[Any]) -> dict[Any, Any]:
    """
    Detect which stage the release is at (0–5).
    Returns a dict with stage info.

    Stage 1 (requirements authoring) only blocks if Stage 2 (package assignments)
    is not yet satisfied. Once packages are assigned, any remaining authoring tasks
    are non-blocking process tasks unrelated to this release.
    """
    version = release.get("version", "?")
    status = release.get("status", "planned")
    release_packages = load_release_packages(release)

    # --- Gather data for all stages up-front ---
    _is_requ_ready, requ_blocking, requ_completed, requ_total = check_requirements_ready()
    all_assigned, unassigned, pkg_total = check_packages_assigned(release_packages, backlog_packages)
    pkg_assigned_count = pkg_total - len(unassigned)
    impl_completed, impl_total, impl_in_progress = count_impl_tasks(version)
    autorun = is_autorun_active()

    # --- Stage 0: no authoring tasks at all ---
    if requ_total == 0:
        return {
            "stage": 0,
            "version": version,
            "status": status,
            "description": "No requirements-authoring tasks exist for this release",
            "recommendation": (
                "Run /requ-derive-from-flow or /requ-explore to create requirements"
            ),
            "details": {},
        }

    # --- Stage 2 check: if packages are already assigned, Stage 1 is non-blocking ---
    if not all_assigned:
        # Stage 1 can only block if Stage 2 is not yet done
        if requ_blocking:
            return {
                "stage": 1,
                "version": version,
                "status": status,
                "description": "Requirements authoring in progress",
                "recommendation": (
                    f"Complete the {len(requ_blocking)} pending authoring task(s) below, "
                    "then run /requ-assign-packages to assign packages"
                ),
                "details": {
                    "blocking": [str(p) for p in requ_blocking],
                    "requ_completed": requ_completed,
                    "requ_total": requ_total,
                    "pkg_assigned": pkg_assigned_count,
                    "pkg_total": pkg_total,
                },
            }

        # Requirements done, but packages not assigned
        return {
            "stage": 2,
            "version": version,
            "status": status,
            "description": "Requirements complete, but not all packages are assigned to a release",
            "recommendation": "Run /requ-assign-packages to assign remaining packages",
            "details": {
                "requ_completed": requ_completed,
                "requ_total": requ_total,
                "unassigned": unassigned,
                "pkg_assigned": pkg_assigned_count,
                "pkg_total": pkg_total,
            },
        }

    # --- Stage 3: packages assigned, release not yet active ---
    if status != "active":
        # Detect out-of-order: impl tasks already exist despite release not being active
        out_of_order_note = ""
        if impl_total > 0:
            out_of_order_note = (
                f" ({impl_completed}/{impl_total} impl tasks already exist — "
                "looks like implementation was started before the release was activated)"
            )
        return {
            "stage": 3,
            "version": version,
            "status": status,
            "description": (
                "Requirements ready and packages assigned — ready to begin implementation"
                + out_of_order_note
            ),
            "recommendation": (
                f"Run /release-begin-impl to activate release {version} and formally begin implementation. "
                + (
                    f"Note: {impl_completed}/{impl_total} impl tasks already completed outside the process — "
                    "these will be counted once the release is activated."
                    if impl_total > 0
                    else "This creates the first orchestration task and activates the release."
                )
            ),
            "details": {
                "requ_completed": requ_completed,
                "requ_total": requ_total,
                "requ_pending": len(requ_blocking),
                "pkg_assigned": pkg_assigned_count,
                "pkg_total": pkg_total,
                "impl_completed": impl_completed,
                "impl_total": impl_total,
                "out_of_order": impl_total > 0,
            },
        }

    # --- Stage 4 / 5: release active ---
    if impl_total > 0 and impl_completed >= impl_total:
        return {
            "stage": 5,
            "version": version,
            "status": status,
            "description": f"All impl tasks completed ({impl_completed}/{impl_total})",
            "recommendation": f"Run /release to cut release {version}",
            "details": {
                "completed": impl_completed,
                "total": impl_total,
                "autorun": autorun,
            },
        }

    return {
        "stage": 4,
        "version": version,
        "status": status,
        "description": "Release active — implementation tasks being created/executed",
        "recommendation": (
            "Autorun is running — monitor progress with /autorun"
            if autorun
            else "Run /autorun to continue creating and executing impl tasks"
        ),
        "details": {
            "completed": impl_completed,
            "total": impl_total,
            "in_progress": [str(p) for p in impl_in_progress],
            "autorun": autorun,
        },
    }


def print_report(release: dict[Any, Any], info: dict[Any, Any]) -> Any:
    """Print the human-readable readiness report."""
    version = info["version"]
    release_name = release.get("name", version)
    status = info["status"]
    stage = info["stage"]
    details = info.get("details", {})

    print(f"Release Readiness: {version} ({release_name})")
    print(f"Status: {status}")
    print()

    stage_label = {
        0: "No requirements-authoring tasks found",
        1: "Requirements authoring in progress",
        2: "Requirements complete, packages not fully assigned",
        3: "Requirements ready, packages assigned — ready to begin implementation",
        4: "Implementation in progress",
        5: "All impl tasks completed — ready to release",
    }.get(stage, f"Stage {stage}")

    print(f"Stage {stage} of 5 — {stage_label}")
    print()

    # Stage checklist
    # ✓ = milestone fully cleared  ✗ = current blocking stage  ○ = not yet reached  ⚠ = passed but with caveats
    requ_completed = details.get("requ_completed", 0)
    requ_total = details.get("requ_total", 0)
    requ_pending = details.get("requ_pending", 0)
    pkg_assigned = details.get("pkg_assigned", 0)
    pkg_total = details.get("pkg_total", 0)
    impl_completed_d = details.get("completed", details.get("impl_completed", 0))
    impl_total_d = details.get("total", details.get("impl_total", 0))
    autorun = details.get("autorun", False)
    out_of_order = details.get("out_of_order", False)

    def _stage_prefix(s_num: int) -> str:
        if stage > s_num:
            return "✓"
        if stage == s_num and not details:
            return "✓"
        if stage == s_num:
            return "✗"
        # Stage 1 gets a special ⚠ when there are pending authoring tasks but Stage 2+ is done
        if s_num == 1 and stage > 1 and requ_pending > 0:
            return "⚠"
        return "○"

    lines = []

    # Stage 1
    p1 = _stage_prefix(1)
    if requ_total > 0:
        s1_suffix = f" ({requ_completed}/{requ_total} authoring tasks completed"
        if requ_pending > 0 and stage > 1:
            s1_suffix += f", {requ_pending} pending but not blocking"
        s1_suffix += ")"
    else:
        s1_suffix = ""
    lines.append(f"  {p1} Stage 1: Requirements authoring{s1_suffix}")

    # Stage 2
    p2 = _stage_prefix(2)
    if pkg_total > 0:
        s2_suffix = f" ({pkg_assigned}/{pkg_total} packages assigned)"
    else:
        s2_suffix = ""
    lines.append(f"  {p2} Stage 2: Package assignments{s2_suffix}")

    # Stage 3
    p3 = _stage_prefix(3)
    s3_suffix = ""
    if out_of_order and stage == 3:
        s3_suffix = f" ⚠ {impl_completed_d}/{impl_total_d} impl tasks already exist"
    lines.append(f"  {p3} Stage 3: Requirements ready — release can begin implementation{s3_suffix}")

    # Stage 4
    p4 = _stage_prefix(4)
    if stage >= 4 and impl_total_d > 0:
        autorun_str = " [autorun running]" if autorun else ""
        s4_suffix = f" ({impl_completed_d}/{impl_total_d} impl tasks done{autorun_str})"
    elif out_of_order and stage == 3:
        autorun_str = " [autorun running]" if autorun else ""
        s4_suffix = f" ({impl_completed_d}/{impl_total_d} done ahead of schedule{autorun_str})"
    else:
        s4_suffix = ""
    lines.append(f"  {p4} Stage 4: Implementation in progress (release is active){s4_suffix}")

    # Stage 5
    p5 = _stage_prefix(5)
    if stage >= 4 and impl_total_d > 0:
        if stage >= 5:
            s5_suffix = f" ({impl_completed_d}/{impl_total_d})"
        else:
            s5_suffix = f" ({impl_completed_d}/{impl_total_d} done so far)"
    else:
        s5_suffix = ""
    lines.append(f"  {p5} Stage 5: All impl tasks completed{s5_suffix}")

    for line in lines:
        print(line)
    print()

    # Extra detail sections
    if stage == 1 and details.get("blocking"):
        print("  Blocking authoring tasks:")
        for p in details["blocking"]:
            try:
                rel = os.path.relpath(p, str(PROJECT_ROOT))
            except ValueError:
                rel = p
            print(f"    - {rel}")
        print()

    if stage == 2 and details.get("unassigned"):
        print("  Unassigned packages:")
        for pkg in details["unassigned"]:
            print(f"    - {pkg}")
        print()

    if stage >= 4 and details.get("in_progress"):
        print("  In-progress tasks:")
        for p in details["in_progress"][:5]:
            try:
                rel = os.path.relpath(p, str(PROJECT_ROOT))
            except ValueError:
                rel = p
            print(f"    - {rel}")
        if len(details["in_progress"]) > 5:
            print(f"    ... and {len(details['in_progress']) - 5} more")
        print()

    print(f"Recommended next step: {info['recommendation']}")


def main() -> int:
    release = load_next_release()
    if release is None:
        print("No active or planned releases found in requirements_tasks/RELEASES.md.")
        return 1

    backlog_packages = load_backlog_packages()
    info = detect_stage(release, backlog_packages)
    print_report(release, info)
    return 0


if __name__ == "__main__":
    sys.exit(main())
