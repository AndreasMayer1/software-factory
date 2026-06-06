#!/usr/bin/env python3
"""Compare a created task's goal.md against its plan entry.

Called by task-create-code Phase 6 and release-begin-impl-finalize Phase 1
to verify conformance between what was created and what was planned.

Usage:
    python3 scripts/check_task_against_plan.py --task TASK-ID --plan PLAN_PATH [--verbose]

Exit codes:
    0  task matches plan entry (all required fields conform)
    1  mismatch found (at least one conformance rule violated, excluding effort +/-1)
    2  no plan entry found for this task (task has no target_package in plan)
    3  argument error or file not found

Output:
    Prints one '<field>: <mismatch>' line per conformance violation to stdout, ending with a PASS/FAIL summary.
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

# Allow importing parse_task_creation_plan from the same scripts/ directory
sys.path.insert(0, str(Path(__file__).parent))
# Make scripts/util importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from io import StringIO

from parse_task_creation_plan import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    PlanArchivedError,
    PlanParseError,
    get_package_tasks,
    parse_plan,
)
from ruamel.yaml import YAML
from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    _split_frontmatter,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent

EFFORT_ORDER = ["XS", "S", "M", "L", "XL"]


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
# Task finding
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


def find_goal_by_task_id(task_id: str) -> Optional[tuple[Path, dict[str, Any]]]:
    """Find goal.md with matching task_id in frontmatter.

    Returns (path, frontmatter_dict) or None.
    """
    root = PROJECT_ROOT / "requirements_tasks"
    for goal_file in _find_files(root, "goal.md"):
        try:
            content = goal_file.read_text(encoding="utf-8")
        except Exception:
            continue
        meta = _parse_frontmatter(content)
        if meta and str(meta.get("task_id", "")).strip() == task_id:
            return goal_file, meta
    return None


def _find_best_plan_entry(
    plan_tasks: list[dict[str, Any]],
    goal_meta: dict[str, Any],
) -> Optional[dict[str, Any]]:
    """Find the best matching plan task entry for this goal.

    Matches by task_name similarity. Falls back to first entry if single task.
    """
    if not plan_tasks:
        return None
    if len(plan_tasks) == 1:
        return plan_tasks[0]

    # Try to match by task_name similarity
    goal_name = str(goal_meta.get("name", "") or "").lower()
    task_folder = str(goal_meta.get("_folder_name", "") or "").lower()

    best_score = -1
    best_task = None

    for pt in plan_tasks:
        plan_name = str(pt.get("task_name", "") or "").lower()
        # Simple word overlap score
        goal_words = set(re.findall(r"\w+", goal_name + " " + task_folder))
        plan_words = set(re.findall(r"\w+", plan_name))
        overlap = len(goal_words & plan_words)
        if overlap > best_score:
            best_score = overlap
            best_task = pt

    return best_task


# ---------------------------------------------------------------------------
# Conformance checking
# ---------------------------------------------------------------------------

def effort_conformant(goal_effort: str, plan_effort: str) -> tuple[bool, bool]:
    """Check effort conformance. Returns (passes, is_warning).

    Exact match = PASS, +/-1 = WARN (still passes), >+/-1 = FAIL.
    Unknown effort values = FAIL.
    """
    try:
        gi = EFFORT_ORDER.index(goal_effort)
        pi = EFFORT_ORDER.index(plan_effort)
        diff = abs(gi - pi)
        if diff == 0:
            return True, False
        if diff == 1:
            return True, True
        return False, False
    except ValueError:
        return False, False


def check_conformance(
    goal_meta: dict[str, Any],
    plan_entry: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return list of check results: {field, status, goal_val, plan_val, message}."""
    results: list[dict[str, Any]] = []

    # target_package: exact match
    goal_pkg = str(goal_meta.get("target_package", "") or "").strip().strip("\"'")
    plan_pkg = str(plan_entry.get("target_package", "") or "").strip()
    results.append({
        "field": "target_package",
        "status": "PASS" if goal_pkg == plan_pkg else "FAIL",
        "goal_val": goal_pkg,
        "plan_val": plan_pkg,
    })

    # covers_acs: set equality
    goal_covers = goal_meta.get("covers", {})
    if isinstance(goal_covers, dict):
        goal_acs_raw = goal_covers.get("acceptance_criteria", [])
    else:
        goal_acs_raw = []
    if not isinstance(goal_acs_raw, list):
        goal_acs_raw = [goal_acs_raw] if goal_acs_raw else []
    goal_acs = {str(ac).strip() for ac in goal_acs_raw if ac}

    plan_acs_raw = plan_entry.get("covers_acs", [])
    if not isinstance(plan_acs_raw, list):
        plan_acs_raw = [plan_acs_raw] if plan_acs_raw else []
    plan_acs = {str(ac).strip() for ac in plan_acs_raw if ac}

    results.append({
        "field": "covers_acs",
        "status": "PASS" if goal_acs == plan_acs else "FAIL",
        "goal_val": sorted(goal_acs),
        "plan_val": sorted(plan_acs),
    })

    # effort: +/-1 allowed
    goal_effort = str(goal_meta.get("effort", "") or "").strip()
    plan_effort = str(plan_entry.get("effort", "") or "").strip()
    if not goal_effort or not plan_effort:
        # Missing effort in either — skip (SKIP status)
        status = "SKIP"
        passes = True
        is_warn = False
    else:
        passes, is_warn = effort_conformant(goal_effort, plan_effort)
        if is_warn:
            status = "WARN"
        elif passes:
            status = "PASS"
        else:
            status = "FAIL"

    results.append({
        "field": "effort",
        "status": status,
        "goal_val": goal_effort,
        "plan_val": plan_effort,
    })

    # layer: optional check (SKIP if not in goal.md)
    goal_layer = str(goal_meta.get("layer", "") or "").strip()
    plan_layer = str(plan_entry.get("layer", "") or "").strip()

    if not goal_layer:
        # Try scope_description for hints
        scope_desc = str(goal_meta.get("scope_description", "") or "").lower()
        for layer in ("data", "domain", "presentation", "test"):
            if layer in scope_desc:
                goal_layer = layer
                break

    if not goal_layer or not plan_layer:
        layer_status = "SKIP"
    else:
        layer_status = "PASS" if goal_layer == plan_layer else "FAIL"

    results.append({
        "field": "layer",
        "status": layer_status,
        "goal_val": goal_layer,
        "plan_val": plan_layer,
    })

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare goal.md against plan entry for conformance"
    )
    parser.add_argument("--task", required=True, metavar="TASK-ID",
                        help="Task ID to look up (e.g. TASK-FUNC-007-12)")
    parser.add_argument("--plan", required=True, metavar="PLAN_PATH",
                        help="Path to task_creation_plan.md")
    parser.add_argument("--verbose", action="store_true",
                        help="Print full diff of all fields")
    args = parser.parse_args()

    task_id = args.task.strip()

    # Find the goal.md
    found = find_goal_by_task_id(task_id)
    if found is None:
        print(f"ERROR: goal.md not found for task_id: {task_id}", file=sys.stderr)
        sys.exit(3)

    _goal_path, goal_meta = found

    # Load the plan
    try:
        plan = parse_plan(args.plan)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(3)
    except (PlanParseError, PlanArchivedError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(3)

    # Find target_package for this task
    target_package = str(goal_meta.get("target_package", "") or "").strip().strip("\"'")
    if not target_package:
        # No target_package — cannot match to plan
        sys.exit(2)

    plan_tasks = get_package_tasks(plan, target_package)
    if not plan_tasks:
        # Package not in plan
        sys.exit(2)

    # Find best matching plan entry
    plan_entry = _find_best_plan_entry(plan_tasks, goal_meta)
    if plan_entry is None:
        sys.exit(2)

    plan_task_name = str(plan_entry.get("task_name", "") or "").strip()

    # Run conformance checks
    check_results = check_conformance(goal_meta, plan_entry)

    # Print report
    print(f"{task_id} vs plan entry \"{plan_task_name}\"")

    warn_count = 0
    has_fail = False

    for r in check_results:
        field = r["field"].ljust(16)
        status = r["status"]
        goal_val = r["goal_val"]
        plan_val = r["plan_val"]

        if status == "WARN":
            warn_count += 1
            detail = f"goal={goal_val} plan={plan_val} (±1 allowed)"
        elif status == "SKIP":
            detail = "(not present in goal.md — skipped)"
        elif status == "PASS":
            detail = f"({goal_val})"
        else:
            has_fail = True
            detail = f"goal={goal_val!r} != plan={plan_val!r}"

        if args.verbose or status in ("FAIL", "WARN") or status == "PASS":
            print(f"  {field}: {status}  {detail}")

    overall = "FAIL" if has_fail else "PASS"
    warn_note = f" ({warn_count} warning{'s' if warn_count != 1 else ''})" if warn_count else ""
    print(f"  Overall        : {overall}{warn_note}")

    sys.exit(1 if has_fail else 0)


if __name__ == "__main__":
    main()
