#!/usr/bin/env python3
"""Compute total size of requirement files for a release and output a JSON verdict.

Verdict is 'orchestrator_direct' if total_bytes <= 30KB AND file_count <= 5;
otherwise 'agents_required'.

Usage:
    python3 scripts/should_use_agents.py --release VERSION [--verbose]
    python3 scripts/should_use_agents.py --single-file FILE_PATH [--verbose]

Exit codes:
    0  always (JSON output; read the 'verdict' key)
    1  release not found or file not readable

Output:
    Prints a single JSON object to stdout with keys 'verdict', 'size_bytes', 'file_count', and 'reason'. Exit 0 unless inputs are missing.
"""

# tier: B  # reusable threshold helper; used by skills via subprocess invocation; tests import it directly

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, cast

# Why: this script runs both as `python3 scripts/util/should_use_agents.py`
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
RELEASE_BACKLOG_FILE = PROJECT_ROOT / "requirements_tasks" / "RELEASE_BACKLOG.md"

THRESHOLD_BYTES = 30 * 1024  # 30 KB
THRESHOLD_FILES = 5


# ---------------------------------------------------------------------------
# YAML parsing helper — central yaml_frontmatter wrapper.
# Preserves prior contract: returns dict on success, None when no frontmatter.
# ---------------------------------------------------------------------------


def _parse_frontmatter(content: str) -> Optional[dict[str, Any]]:
    """Extract and parse YAML frontmatter from markdown content.

    Returns a plain dict on success, or None if the content has no frontmatter
    block, an empty frontmatter block, or malformed YAML (prior behaviour
    silently swallowed parse errors via the fallback path).
    """
    if content.startswith("﻿"):
        content = content[1:]

    try:
        doc = read_frontmatter(content)
    except FrontmatterError:
        return None

    if not doc.has_frontmatter:
        return None
    if len(doc.metadata) == 0:
        # Prior behaviour: empty `yaml_lines` returned None
        return None
    # Convert CommentedMap → plain dict for downstream callers that use isinstance
    return dict(doc.metadata)


# ---------------------------------------------------------------------------
# Package/requirement discovery
# ---------------------------------------------------------------------------

def _find_files(root: Path, name: str) -> list[Path]:
    """Locate files by name using native find (faster than rglob on WSL2)."""
    try:
        result = subprocess.run(
            ["find", str(root), "-name", name],
            capture_output=True, text=True,
        )
        return [Path(p) for p in result.stdout.splitlines() if p.strip()]
    except FileNotFoundError:
        return list(root.rglob(name))


def find_packages_for_release(version: str) -> list[str]:
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


def find_req_files_for_packages(package_ids: list[str]) -> list[dict[str, Any]]:
    """Find requirements.md files for the given package IDs.

    Uses two strategies:
    1. Find requirements.md with target_package matching the package ID
    2. Also checks for source.ref requirement ID references (for feature-level reqs)
    Returns list of {path, package, bytes} dicts, deduplicated by path.
    """
    req_root = PROJECT_ROOT / "requirements_tasks"
    all_req_files = _find_files(req_root, "requirements.md")

    found: dict[str, dict[str, Any]] = {}  # path -> info

    for req_file in all_req_files:
        try:
            content = req_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"WARNING: cannot read {req_file}: {e}", file=sys.stderr)
            continue

        meta = _parse_frontmatter(content)
        if not meta:
            continue

        # Strategy 1: target_package exact match
        target_pkg = str(meta.get("target_package", "") or "").strip().strip("\"'")
        if target_pkg in package_ids:
            path_str = str(req_file)
            if path_str not in found:
                try:
                    size = os.path.getsize(str(req_file))
                except OSError:
                    size = 0
                found[path_str] = {"path": path_str, "package": target_pkg, "bytes": size}

    return list(found.values())


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------

def compute_verdict(total_bytes: int, file_count: int) -> str:
    """Return 'orchestrator_direct' or 'agents_required' based on thresholds."""
    if total_bytes <= THRESHOLD_BYTES and file_count <= THRESHOLD_FILES:
        return "orchestrator_direct"
    return "agents_required"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute requirement file sizes and output agent-use verdict as JSON"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--release", metavar="VERSION",
                       help="Find all requirement files for this release")
    group.add_argument("--single-file", metavar="FILE_PATH",
                       help="Check just one file")
    parser.add_argument("--verbose", action="store_true",
                        help="Include per-file sizes in output")
    args = parser.parse_args()

    if args.single_file:
        path = Path(args.single_file)
        if not path.exists():
            print(f"ERROR: File not found: {args.single_file}", file=sys.stderr)
            sys.exit(1)
        try:
            size = os.path.getsize(str(path))
        except OSError as e:
            print(f"ERROR: Cannot stat file: {e}", file=sys.stderr)
            sys.exit(1)

        files = [{"path": str(path), "bytes": size}]
        total_bytes = size
        file_count = 1
        verdict = compute_verdict(total_bytes, file_count)

        output: dict[str, Any] = {
            "verdict": verdict,
            "total_bytes": total_bytes,
            "file_count": file_count,
            "threshold_bytes": THRESHOLD_BYTES,
            "threshold_files": THRESHOLD_FILES,
            "files": files,
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    # --release mode
    version = args.release
    package_ids = find_packages_for_release(version)

    if not package_ids:
        # Release not found — still output valid JSON with empty files
        output = {
            "release": version,
            "verdict": "orchestrator_direct",
            "total_bytes": 0,
            "file_count": 0,
            "threshold_bytes": THRESHOLD_BYTES,
            "threshold_files": THRESHOLD_FILES,
            "files": [],
            "warning": f"No packages found for release {version} in RELEASE_BACKLOG.md",
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    files = find_req_files_for_packages(package_ids)
    total_bytes = sum(int(cast(int, f["bytes"])) for f in files)
    file_count = len(files)
    verdict = compute_verdict(total_bytes, file_count)

    output = {
        "release": version,
        "verdict": verdict,
        "total_bytes": total_bytes,
        "file_count": file_count,
        "threshold_bytes": THRESHOLD_BYTES,
        "threshold_files": THRESHOLD_FILES,
    }

    if True:  # always include files per spec
        output["files"] = files

    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
