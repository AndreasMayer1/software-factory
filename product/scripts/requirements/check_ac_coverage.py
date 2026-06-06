#!/usr/bin/env python3
"""
Check AC coverage for a given package.

Scans all requirements.md files for ACs assigned to the target package,
then checks which ACs are not covered by any non-terminal task.

Usage:
    python scripts/check_ac_coverage.py --package "QR Transfer Core"

Exit codes:
    0 — no gaps found
    1 — uncovered ACs detected

Output:
    Prints one line per AC ('<AC-ID> <STATUS>') and a summary table to stdout. Uncovered ACs are reported with their requirement paths.
"""

# tier: C  # one-shot CLI requirements tool; no in-tree Python imports

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

# Make scripts/util importable when invoked directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from io import StringIO

from ruamel.yaml import YAML
from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    _split_frontmatter,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent
TERMINAL_STATUSES = {"completed", "cancelled", "superseded"}


# ---------------------------------------------------------------------------
# YAML parsing \u2014 delegates to scripts/util/yaml_frontmatter (REQ-PROC-051 AC-08)
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> Optional[dict[Any, Any]]:
    """Parse YAML frontmatter; returns dict or None when absent/malformed.

    Uses _split_frontmatter directly (not read_frontmatter) because the latter
    calls Path(text).exists(), which raises ENAMETOOLONG for any text bigger
    than NAME_MAX. Tolerates duplicate keys for legacy doc compatibility.
    """
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


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Filesystem helper
# ---------------------------------------------------------------------------

def _find_files_proc(root: str, name: str) -> "subprocess.Popen[str]":
    """Launch `find` for a named file as a background process."""
    return subprocess.Popen(
        ["find", root, "-name", name],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )


def _collect_paths(proc: "subprocess.Popen[str]") -> list[Path]:
    stdout, _ = proc.communicate()
    return [Path(p) for p in stdout.splitlines() if p.strip()]


# ---------------------------------------------------------------------------
# Load ACs for a package from all requirements.md files
# ---------------------------------------------------------------------------

def load_required_acs(package: str, req_files: list[Path]) -> dict[str, list[str]]:
    """Return {req_id: [AC_id, ...]} for all ACs assigned to package."""
    result: dict[str, list[str]] = {}

    for req_file in req_files:
        content = _read_file(req_file)
        if not content:
            continue
        meta = parse_frontmatter(content)
        if not meta:
            continue

        req_id = str(meta.get("id", "")).strip()
        if not req_id:
            continue

        trackable = meta.get("trackable_items")
        if not isinstance(trackable, dict):
            continue

        acs = trackable.get("acceptance_criteria", [])
        if not isinstance(acs, list):
            continue

        for ac in acs:
            if not isinstance(ac, dict):
                continue
            ac_pkg = str(ac.get("target_package", "") or "").strip().strip("\"'")
            if ac_pkg != package:
                continue
            ac_id = str(ac.get("id", "") or "").strip()
            if ac_id:
                result.setdefault(req_id, []).append(ac_id)

    return result


# ---------------------------------------------------------------------------
# Load covered ACs from all non-terminal task goal.md files
# ---------------------------------------------------------------------------

def load_covered_acs(goal_files: list[Path]) -> set[tuple[str, str]]:
    """Return set of (req_id, AC_id) covered by any non-terminal task."""
    covered: set[tuple[str, str]] = set()

    for goal_file in goal_files:
        content = _read_file(goal_file)
        if not content:
            continue
        meta = parse_frontmatter(content)
        if not meta or "task_id" not in meta:
            continue

        status = str(meta.get("status", "")).lower()
        if status in TERMINAL_STATUSES:
            continue

        req_id = str(meta.get("parent_requirement", "") or "").strip()
        if not req_id:
            continue

        covers = meta.get("covers")
        if not isinstance(covers, dict):
            continue

        ac_list = covers.get("acceptance_criteria", [])
        if not isinstance(ac_list, list):
            continue

        for ac_id in ac_list:
            if ac_id:
                covered.add((req_id, str(ac_id).strip()))

    return covered


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check AC coverage for a given release package."
    )
    parser.add_argument("--package", required=True, help="Package ID to check")
    args = parser.parse_args()

    req_root = str(PROJECT_ROOT / "requirements_tasks")
    # Launch both find processes in parallel before waiting on either
    req_proc = _find_files_proc(req_root, "requirements.md")
    goal_proc = _find_files_proc(req_root, "goal.md")
    req_files = _collect_paths(req_proc)
    goal_files = _collect_paths(goal_proc)

    required = load_required_acs(args.package, req_files)
    if not required:
        sys.exit(0)

    covered = load_covered_acs(goal_files)

    gaps: dict[str, list[str]] = {}
    for req_id, ac_ids in sorted(required.items()):
        missing = [ac for ac in ac_ids if (req_id, ac) not in covered]
        if missing:
            gaps[req_id] = missing

    if not gaps:
        sys.exit(0)

    print(f'Uncovered ACs in "{args.package}":')
    for req_id, ac_ids in gaps.items():
        print(f"  {req_id} \u2192 {', '.join(ac_ids)}")

    sys.exit(1)


if __name__ == "__main__":
    main()
