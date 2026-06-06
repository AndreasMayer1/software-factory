#!/usr/bin/env python3
"""Find and fix missing after: entries across all impl tasks for a release.

Compares the after: chains in goal.md files against what the task_creation_plan.md
specifies, and optionally edits goal.md files in-place to add missing entries.

Usage:
    python3 scripts/reconcile_after_chains.py --release VERSION [--plan PLAN_PATH] [--apply] [--verbose]

Exit codes:
    0  all after-chains valid (or --apply completed successfully)
    1  missing after-entries found (without --apply); or apply failed for >=1 task
    3  no active release found or argument error

Output:
    Prints one '<TASK-ID> missing after: <PRED-ID>' line per gap to stdout. --apply additionally writes the fixes into goal.md files and prints 'fixed <TASK-ID>' per write.
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import os
import re
import subprocess
import sys
import tempfile
from io import StringIO
from pathlib import Path
from typing import Any, Optional, cast

from ruamel.yaml import YAML

# Allow importing parse_task_creation_plan from the same scripts/ directory
sys.path.insert(0, str(Path(__file__).parent))
# Make scripts/util importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parse_task_creation_plan import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    PlanArchivedError,
    PlanParseError,
    parse_plan,
)
from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    _split_frontmatter,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent
RELEASE_BACKLOG_FILE = PROJECT_ROOT / "requirements_tasks" / "RELEASE_BACKLOG.md"


# ---------------------------------------------------------------------------
# YAML parsing — delegates to scripts/util/yaml_frontmatter (REQ-PROC-051 AC-08)
# ---------------------------------------------------------------------------

def _parse_frontmatter(content: str) -> Optional[dict[str, Any]]:
    """Extract and parse YAML frontmatter from markdown content."""
    if content.startswith("﻿"):
        content = content[1:]
    raw_yaml, _body = _split_frontmatter(content)
    if not raw_yaml.strip():
        return None
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True
    try:
        result = yaml.load(StringIO(raw_yaml))
    except Exception:
        return None
    if result is None or not isinstance(result, dict) or len(result) == 0:
        return None
    return dict(result)


# ---------------------------------------------------------------------------
# File finding
# ---------------------------------------------------------------------------

def _find_files(root: Path, name: str) -> list[Path]:
    """Locate files by name using native find."""
    try:
        result = subprocess.run(
            ["find", str(root), "-name", name],
            capture_output=True, text=True,
        )
        return [Path(p) for p in result.stdout.splitlines() if p.strip()]
    except FileNotFoundError:
        return list(root.rglob(name))


# ---------------------------------------------------------------------------
# Release package discovery
# ---------------------------------------------------------------------------

def _find_packages_for_release(version: str) -> list[str]:
    """Find package IDs assigned to the given release from RELEASE_BACKLOG.md."""
    if not RELEASE_BACKLOG_FILE.exists():
        return []

    content = RELEASE_BACKLOG_FILE.read_text(encoding="utf-8")
    meta = _parse_frontmatter(content)
    if not meta or "packages" not in meta:
        return []

    packages = meta.get("packages", [])
    if not isinstance(packages, list):
        return []

    result: list[str] = []
    for pkg in packages:
        if not isinstance(pkg, dict):
            continue
        assigned = str(pkg.get("assigned_release", "") or "").strip().strip("\"'")
        if assigned == version:
            pkg_id = str(pkg.get("id", "") or "").strip().strip("\"'")
            if pkg_id:
                result.append(pkg_id)
    return result


# ---------------------------------------------------------------------------
# Task loading
# ---------------------------------------------------------------------------

def _load_release_tasks(version: str) -> list[dict[str, Any]]:
    """Load all goal.md files for tasks in the given release.

    Filters by target_release == version OR target_package in release packages.
    """
    release_packages = set(_find_packages_for_release(version))
    root = PROJECT_ROOT / "requirements_tasks"
    tasks: list[dict[str, Any]] = []

    for goal_file in _find_files(root, "goal.md"):
        try:
            content = goal_file.read_text(encoding="utf-8")
        except Exception:
            continue
        meta = _parse_frontmatter(content)
        if not meta or not meta.get("task_id"):
            continue

        target_release = str(meta.get("target_release", "") or "").strip().strip("\"'")
        target_package = str(meta.get("target_package", "") or "").strip().strip("\"'")

        if target_release == version or (release_packages and target_package in release_packages):
            after = meta.get("after", [])
            if not isinstance(after, list):
                after = [after] if after else []
            after = [str(a).strip() for a in after if a]

            tasks.append({
                "task_id": str(meta["task_id"]).strip(),
                "target_package": target_package,
                "target_release": target_release,
                "after": after,
                "path": str(goal_file),
                "meta": meta,
            })

    return tasks


# ---------------------------------------------------------------------------
# Plan-based after reference resolution
# ---------------------------------------------------------------------------

def _resolve_intra_plan_ref(
    ref: str,
    plan: dict[str, Any],
    all_tasks: list[dict[str, Any]],
) -> Optional[str]:
    """Resolve a #PKG-X:Task N intra-plan reference to a real TASK-ID.

    Strategy:
    1. Parse package name from #PKG:... prefix
    2. Find the Nth task entry in that package in the plan
    3. Look up which goal.md has matching target_package and similar task name
    Returns None if not resolved.
    """
    # Pattern: #PkgName:Task N or #PackageName:TaskName
    m = re.match(r"#([^:]+):Task\s+(\d+)", ref)
    if not m:
        return None

    pkg_name = m.group(1).strip()
    task_num = int(m.group(2))

    # Find plan package
    for pkg in plan.get("packages", []):
        if pkg["id"] == pkg_name or pkg_name.lower() in pkg["id"].lower():
            tasks_in_pkg = pkg["tasks"]
            if 0 < task_num <= len(tasks_in_pkg):
                plan_task = tasks_in_pkg[task_num - 1]
                plan_task_name = str(plan_task.get("task_name", "") or "").lower()
                plan_pkg_id = pkg["id"]

                # Find matching goal.md task
                for t in all_tasks:
                    if t["target_package"] == plan_pkg_id:
                        return cast("str | None", t["task_id"])

                # Fallback: find by task name similarity
                for t in all_tasks:
                    t_name = str(t["meta"].get("name", "") or "").lower()
                    if plan_task_name and plan_task_name[:10] in t_name:
                        return cast("str | None", t["task_id"])

    return None


def _get_plan_after_entries(
    plan: Optional[dict[str, Any]],
    target_package: str,
    all_tasks: list[dict[str, Any]],
) -> list[str]:
    """Get the after: entries the plan specifies for a package's tasks.

    Returns resolved TASK-IDs only (unresolvable references are skipped with warning).
    """
    if plan is None:
        return []

    plan_after: list[str] = []

    for pkg in plan.get("packages", []):
        if pkg["id"] != target_package:
            continue
        for plan_task in pkg["tasks"]:
            after_raw = plan_task.get("after", [])
            if not isinstance(after_raw, list):
                after_raw = [after_raw] if after_raw else []

            for ref in after_raw:
                ref_str = str(ref).strip()
                if not ref_str:
                    continue
                if ref_str.startswith("#"):
                    # Intra-plan reference — resolve
                    resolved = _resolve_intra_plan_ref(ref_str, plan, all_tasks)
                    if resolved:
                        plan_after.append(resolved)
                    else:
                        print(
                            f"WARNING: Cannot resolve plan reference '{ref_str}' — skipping",
                            file=sys.stderr,
                        )
                else:
                    plan_after.append(ref_str)

    return list(dict.fromkeys(plan_after))  # deduplicate, preserve order


# ---------------------------------------------------------------------------
# In-place edit helpers
# ---------------------------------------------------------------------------

def _parse_after_from_yaml(yaml_text: str) -> list[str]:
    """Extract existing after: entries from YAML frontmatter text."""
    # Try inline form: after: [A, B, C]
    inline_m = re.search(r"^after:\s*\[(.*?)\]", yaml_text, re.MULTILINE)
    if inline_m:
        inner = inline_m.group(1).strip()
        if not inner:
            return []
        return [i.strip().strip("\"'") for i in inner.split(",") if i.strip()]

    # Try block form:
    # after:
    #   - A
    #   - B
    block_m = re.search(r"^after:\s*$", yaml_text, re.MULTILINE)
    if block_m:
        after_start = block_m.end()
        entries: list[str] = []
        for line in yaml_text[after_start:].split("\n"):
            item_m = re.match(r"^\s+-\s+(.+)$", line)
            if item_m:
                item = item_m.group(1).strip().strip("\"'")
                entries.append(item)
            elif line.strip() and not line.startswith(" ") and ":" in line:
                break
        return entries

    return []


def _update_after_field(yaml_text: str, new_entries: list[str]) -> str:
    """Merge existing + new entries in the after: field, preserving YAML structure.

    Returns updated YAML text. Uses inline format for compactness.
    """
    existing = _parse_after_from_yaml(yaml_text)
    merged = list(dict.fromkeys(existing + new_entries))  # preserve order, deduplicate

    inline_str = "[" + ", ".join(merged) + "]"
    replacement = f"after: {inline_str}"

    # Try replacing inline form: after: [...]
    inline_pattern = r"^after:\s*\[.*?\]"
    if re.search(inline_pattern, yaml_text, re.MULTILINE):
        return re.sub(inline_pattern, replacement, yaml_text, flags=re.MULTILINE)

    # Try replacing block form: after:\n  - ...\n  - ...
    block_pattern = r"^after:\s*\n(?:[ \t]+-[^\n]*\n?)+"
    if re.search(block_pattern, yaml_text, re.MULTILINE):
        return re.sub(block_pattern, replacement + "\n", yaml_text, flags=re.MULTILINE)

    # Try replacing bare after: (no value)
    bare_pattern = r"^after:\s*$"
    if re.search(bare_pattern, yaml_text, re.MULTILINE):
        return re.sub(bare_pattern, replacement, yaml_text, flags=re.MULTILINE)

    # after: field not found — append it before the closing ---
    print("WARNING: 'after:' field not found in frontmatter — appending", file=sys.stderr)
    return yaml_text.rstrip() + f"\nafter: {inline_str}\n"


def add_after_entries(goal_path: str, new_entries: list[str]) -> None:
    """Add new after: entries to a goal.md frontmatter, using atomic write.

    Uses os.replace() for atomic swap to avoid partial writes on crash.
    """
    content = Path(goal_path).read_text(encoding="utf-8")

    fm_match = re.search(r"^(---\n)(.*?)(^---)", content, re.DOTALL | re.MULTILINE)
    if not fm_match:
        raise ValueError(f"No frontmatter in {goal_path}")

    yaml_text = fm_match.group(2)
    updated_yaml = _update_after_field(yaml_text, new_entries)
    new_content = "---\n" + updated_yaml + "---" + content[fm_match.end():]

    # Atomic write: write to temp file, then replace
    goal_dir = Path(goal_path).parent
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=str(goal_dir),
        suffix=".tmp", delete=False
    ) as tmp:
        tmp.write(new_content)
        tmp_path = tmp.name

    os.replace(tmp_path, goal_path)


# ---------------------------------------------------------------------------
# Plan auto-detection
# ---------------------------------------------------------------------------

def _auto_detect_plan_path(version: str) -> Optional[Path]:
    """Try to auto-detect task_creation_plan.md for the given release.

    Scans for completed explore tasks with matching target_release that may
    contain a task_creation_plan.md.
    """
    root = PROJECT_ROOT / "requirements_tasks"
    for goal_file in _find_files(root, "task_creation_plan.md"):
        return goal_file  # return first found

    # Also check explore task folders
    for goal_file in _find_files(root, "goal.md"):
        try:
            content = goal_file.read_text(encoding="utf-8")
        except Exception:
            continue
        meta = _parse_frontmatter(content)
        if not meta:
            continue
        if (str(meta.get("type", "")).lower() == "explore" and
                str(meta.get("target_release", "")).strip() == version):
            plan_candidate = goal_file.parent / "task_creation_plan.md"
            if plan_candidate.exists():
                return plan_candidate

    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find and fix missing after: entries for a release"
    )
    parser.add_argument("--release", required=True, metavar="VERSION",
                        help="Release version (e.g. 0.0.1)")
    parser.add_argument("--plan", metavar="PLAN_PATH",
                        help="Path to task_creation_plan.md (auto-detected if omitted)")
    parser.add_argument("--apply", action="store_true",
                        help="Edit goal.md files in-place to add missing after entries")
    parser.add_argument("--verbose", action="store_true",
                        help="Print full detail per task")
    args = parser.parse_args()

    version = args.release.strip()

    # Load tasks for this release
    all_tasks = _load_release_tasks(version)
    if not all_tasks:
        print(f"No tasks found for release {version}", file=sys.stderr)
        sys.exit(3)

    # Load plan if provided or auto-detected
    plan: Optional[dict[str, Any]] = None
    plan_path = args.plan
    if not plan_path:
        detected = _auto_detect_plan_path(version)
        if detected:
            plan_path = str(detected)
            if args.verbose:
                print(f"Auto-detected plan: {plan_path}")

    if plan_path:
        try:
            plan = parse_plan(plan_path)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(3)
        except (PlanParseError, PlanArchivedError) as e:
            print(f"WARNING: Cannot load plan: {e}", file=sys.stderr)
            plan = None

    if not plan:
        # Without a plan, nothing to reconcile
        print(f"After-chain reconciliation for release {version}")
        print("No task_creation_plan.md found — nothing to reconcile.")
        sys.exit(0)

    print(f"After-chain reconciliation for release {version}")

    missing_count = 0
    apply_errors = 0
    updated_count = 0

    for task in all_tasks:
        task_id = task["task_id"]
        target_package = task["target_package"]
        current_after: set[str] = set(task["after"])

        # Get what the plan says should be in after:
        plan_after = _get_plan_after_entries(plan, target_package, all_tasks)
        missing = [e for e in plan_after if e not in current_after]

        if not missing:
            if args.verbose:
                print(f"  {task_id}: OK (after: {sorted(current_after)})")
            continue

        missing_count += 1

        if not args.apply:
            print(f"\n{task_id} ({target_package}): missing after: {missing}")
            print(f"  Plan says: after: {plan_after}")
            print(f"  Goal has:  after: {sorted(current_after)}")
        else:
            try:
                add_after_entries(task["path"], missing)
                print(f"  {task_id}: added after: {missing} — DONE")
                updated_count += 1
            except Exception as e:
                print(f"  ERROR updating {task_id}: {e}", file=sys.stderr)
                apply_errors += 1

    if not args.apply:
        if missing_count == 0:
            print("All after-chains are valid.")
            sys.exit(0)
        print(f"\nTotal: {missing_count} task{'s' if missing_count != 1 else ''} with missing after-entries.")
        print("Run with --apply to fix.")
        sys.exit(1)
    else:
        print(f"Total: {updated_count} task{'s' if updated_count != 1 else ''} updated.")
        sys.exit(1 if apply_errors else 0)


if __name__ == "__main__":
    main()
