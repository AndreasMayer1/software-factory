#!/usr/bin/env python3
"""
Generates releases/[version]/release_notes_technical.md from completed task metadata.

Reads the active release from RELEASES.md (or --release arg), scans functional/,
non-functional/, and process/ tasks, and writes Keep-a-Changelog format release notes.

Sections (Keep-a-Changelog convention):
  Added       — type=impl in functional/
  Fixed       — type=bugfix anywhere
  Improvements — type=impl in non-functional/ or process/

Usage:
    python scripts/generate_technical_release_notes.py
    python scripts/generate_technical_release_notes.py --release 0.0.1

Output:
    Writes releases/[version]/release_notes_technical.md. Prints a
    one-line summary ("Wrote …" or error text) to stdout/stderr.
"""

# tier: C  # one-shot CLI artifact generator; no in-tree Python imports

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Optional

# Why: this script runs both as `python3 scripts/artifacts/generate_technical_release_notes.py`
# (standalone, no PYTHONPATH) and via pytest (which adds project root to sys.path).
# Add scripts/ to sys.path so `from util.yaml_frontmatter import ...` resolves
# regardless of invocation path.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    _parse_yaml_block,
    _split_frontmatter,
)

PROJECT_ROOT = Path(__file__).parent.parent
RELEASES_MD = PROJECT_ROOT / "requirements_tasks" / "RELEASES.md"
RELEASE_BACKLOG_MD = PROJECT_ROOT / "RELEASE_BACKLOG.md"
TODAY = date.today().isoformat()


# ---------------------------------------------------------------------------
# YAML parsing \u2014 delegates to the central helper (REQ-PROC-051 AC-08).
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> Optional[dict[str, Any]]:
    """Parse YAML frontmatter from a content string.

    Returns dict on success, None when frontmatter is absent/empty/malformed.
    """
    # Strip UTF-8 BOM (some Windows editors add it; central helper does not).
    if content.startswith("\ufeff"):
        content = content[1:]
    raw_yaml, _body = _split_frontmatter(content)
    if not raw_yaml:
        return None
    try:
        metadata = _parse_yaml_block(raw_yaml)
    except Exception:
        # Legacy fallback silently returned partial dict on malformed YAML;
        # callers downstream rely on None-or-dict so we map both to None.
        return None
    if not metadata:
        return None
    return dict(metadata)


# ---------------------------------------------------------------------------
# RELEASES.md parsing
# ---------------------------------------------------------------------------

def find_active_release() -> Optional[str]:
    """Read RELEASES.md and return the version with status: active."""
    if not RELEASES_MD.exists():
        print(f"ERROR: {RELEASES_MD} not found.", file=sys.stderr)
        return None

    try:
        content = RELEASES_MD.read_text(encoding="utf-8")
    except Exception as e:
        print(f"ERROR: Could not read {RELEASES_MD}: {e}", file=sys.stderr)
        return None

    # Structured parse via central helper (ruamel.yaml).
    fm = parse_frontmatter(content)
    if fm and isinstance(fm.get("releases"), list):
        for entry in fm["releases"]:
            if isinstance(entry, dict) and str(entry.get("status", "")).strip() == "active":
                version = entry.get("version")
                if version:
                    return str(version).strip().strip("\"'")

    # Fallback: regex scan — find a releases list entry where status is active
    # and read the version from the nearby line
    version_pattern = re.compile(r'version:\s*["\']?([^"\'\s]+)["\']?')
    status_pattern = re.compile(r'status:\s*active')

    # Strip frontmatter delimiters and scan block by block
    # Simple approach: split on "- version:" to get per-release blocks
    # Strip leading "---" if present
    text = content
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[3:end]

    blocks = re.split(r'\n\s*-\s+version:', text)
    for block in blocks[1:]:  # first block is before any "- version:"
        version_match = version_pattern.match(block.strip())
        if version_match and status_pattern.search(block):
            return version_match.group(1).strip().strip("\"'")

    return None


def find_active_package() -> Optional[str]:
    """Read RELEASE_BACKLOG.md and return the package id with status: active."""
    if not RELEASE_BACKLOG_MD.exists():
        return None
    try:
        content = RELEASE_BACKLOG_MD.read_text(encoding="utf-8")
    except Exception:
        return None

    fm = parse_frontmatter(content)
    if fm and isinstance(fm.get("packages"), list):
        for version_block in fm["packages"]:
            if isinstance(version_block, dict):
                for pkg in version_block.get("packages", []):
                    if isinstance(pkg, dict) and str(pkg.get("status", "")).strip() == "active":
                        return str(pkg.get("id", "")).strip()
    return None


def find_version_for_package(package_id: str) -> Optional[str]:
    """Look up the version string for a given package ID in RELEASE_BACKLOG.md."""
    if not RELEASE_BACKLOG_MD.exists():
        return None
    try:
        content = RELEASE_BACKLOG_MD.read_text(encoding="utf-8")
    except Exception:
        return None

    fm = parse_frontmatter(content)
    if fm and isinstance(fm.get("packages"), list):
        for version_block in fm["packages"]:
            if isinstance(version_block, dict):
                version = str(version_block.get("version", "")).strip()
                for pkg in version_block.get("packages", []):
                    if isinstance(pkg, dict) and pkg.get("id") == package_id:
                        return version
    return None


# ---------------------------------------------------------------------------
# Task scanning
# ---------------------------------------------------------------------------

def _read_file(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return None
    except Exception:
        return None


def load_release_tasks(version_or_package: str, by_package: bool = False) -> dict[str, list[dict[Any, Any]]]:
    """Scan functional/ and non-functional/ for completed tasks matching version or package.

    Returns a dict with keys 'features', 'fixed', and 'improvements'.
    - features: type=impl in functional/
    - fixed: type=bugfix anywhere
    - improvements: type=impl in non-functional/

    # Why: by_package=True matches target_package field (new model); by_package=False matches
    # target_release (legacy/transition-period fallback). Tasks with target_package take
    # precedence — callers that detect an active package should pass by_package=True.
    # Source: requirements_tasks/process/AI_rules/requirements_management/release_version_management/tasks/2026-03-26_impl_update-skills-and-scripts/plans_and_protocols/2026-03-26_01_plan_package-model-migration.md#D4
    """
    results: dict[str, list[dict[Any, Any]]] = {"features": [], "fixed": [], "improvements": []}

    scan_roots = [
        PROJECT_ROOT / "requirements_tasks" / "functional",
        PROJECT_ROOT / "requirements_tasks" / "non-functional",
    ]

    for scan_root in scan_roots:
        if not scan_root.exists():
            continue

        for goal_file in scan_root.rglob("goal.md"):
            content = _read_file(goal_file)
            if content is None:
                continue

            meta = parse_frontmatter(content)
            if not meta:
                continue

            task_type = str(meta.get("type", "")).lower()
            if task_type not in ("impl", "bugfix"):
                continue

            status = str(meta.get("status", "")).lower()
            if status != "completed":
                continue

            if by_package:
                # Match by target_package (new model)
                task_target_pkg = meta.get("target_package")
                if task_target_pkg:
                    task_target_pkg = str(task_target_pkg).strip().strip("\"'")
                if task_target_pkg != version_or_package:
                    continue
            else:
                # Match by target_release (transition period fallback)
                target_release = meta.get("target_release")
                if not target_release and meta.get("target_package"):
                    # Has package but no release — skip in release mode
                    continue
                if target_release is not None:
                    target_release = str(target_release).strip().strip("\"'")
                if target_release != version_or_package:
                    continue

            release_description = meta.get("release_description")
            if release_description:
                release_description = str(release_description).strip().strip("\"'")

            task_id = str(meta.get("task_id", meta.get("id", "")))

            if not release_description:
                print(
                    f"WARNING: Task {task_id} at {goal_file} "
                    f"has no release_description — skipped.",
                    file=sys.stderr,
                )
                continue

            entry = {
                "task_id": task_id,
                "release_description": release_description,
            }

            # bugfix tasks go into 'fixed' regardless of folder
            if task_type == "bugfix":
                results["fixed"].append(entry)
            elif scan_root.name == "functional":
                results["features"].append(entry)
            else:
                results["improvements"].append(entry)

    # Sort each group alphabetically by release_description
    for key in results:
        results[key].sort(key=lambda t: t["release_description"].lower())

    return results


# ---------------------------------------------------------------------------
# Output generation
# ---------------------------------------------------------------------------

def generate_notes(version: str, tasks: dict[str, list[dict[Any, Any]]]) -> str:
    lines = [
        f"# Release Notes \u2013 {version}",
        "",
        "_Generated from task metadata. Source: requirements_tasks/_",
        "",
        f"## [{version}] \u2013 {TODAY}",
    ]

    features = tasks.get("features", [])
    fixed = tasks.get("fixed", [])
    improvements = tasks.get("improvements", [])

    if features:
        lines.append("")
        lines.append("### Added")
        for t in features:
            lines.append(f"- {t['release_description']}")

    if fixed:
        lines.append("")
        lines.append("### Fixed")
        for t in fixed:
            lines.append(f"- {t['release_description']}")

    if improvements:
        lines.append("")
        lines.append("### Improvements")
        for t in improvements:
            lines.append(f"- {t['release_description']}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate technical release notes from completed impl task metadata."
    )
    parser.add_argument(
        "--release",
        help="Target release version (default: read active release from RELEASES.md)",
    )
    parser.add_argument(
        "--package",
        help="Target package ID (default: read active package from RELEASE_BACKLOG.md)",
    )
    args = parser.parse_args()

    by_package = False

    if args.package:
        version_label = args.package.strip()
        tasks = load_release_tasks(version_label, by_package=True)
        by_package = True
    elif args.release:
        version_label = args.release.strip()
        tasks = load_release_tasks(version_label, by_package=False)
        by_package = False
    else:
        # Try package first, fall back to release
        package_id = find_active_package()
        if package_id:
            version_label = package_id
            tasks = load_release_tasks(package_id, by_package=True)
            by_package = True
        else:
            if not RELEASE_BACKLOG_MD.exists():
                print(
                    "WARNING: RELEASE_BACKLOG.md not found — falling back to RELEASES.md.",
                    file=sys.stderr,
                )
            version_label = find_active_release()
            if not version_label:
                print(
                    "ERROR: No active package or release found. "
                    "Use --package PKG_ID or --release VERSION to specify explicitly.",
                    file=sys.stderr,
                )
                sys.exit(1)
            tasks = load_release_tasks(version_label, by_package=False)
            by_package = False

    # Determine output directory:
    # When using a package ID, look up its associated version in RELEASE_BACKLOG.md
    # so notes go to releases/[version]/ — fall back to package ID as directory name.
    if by_package:
        version_for_path = find_version_for_package(version_label) or version_label
    else:
        version_for_path = version_label

    total = len(tasks.get("features", [])) + len(tasks.get("fixed", [])) + len(tasks.get("improvements", []))

    out_dir = PROJECT_ROOT / "releases" / version_for_path
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "release_notes_technical.md"

    if total == 0:
        out_file.write_text(
            f"_No completed impl tasks found for {'package' if by_package else 'release'} {version_label}._\n",
            encoding="utf-8",
        )
        print(f"Created: releases/{version_for_path}/release_notes_technical.md")
        sys.exit(0)

    content = generate_notes(version_label, tasks)
    out_file.write_text(content, encoding="utf-8")
    print(f"Created: releases/{version_for_path}/release_notes_technical.md")


if __name__ == "__main__":
    main()
