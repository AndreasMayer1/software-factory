#!/usr/bin/env python3
"""REQ-PROC-046 AC-09 / G8 — bundle-size budget gate.

Builds an Android arm64 APK and an AAB with `--analyze-size`, then asserts that
the per-ABI APK is <= 30 MB and the AAB is <= 50 MB. Archives the size-analysis
JSON files to `releases/<version>/size_analysis/<timestamp>/` so size regressions
are visible across releases.

Usage:
    scripts/release/check_bundle_size.py [--skip-build] [--release-version V]
                                          [--apk-budget-mb N] [--aab-budget-mb N]
                                          [--archive-dir DIR]

Flags:
    --skip-build         Use pre-existing artifacts under build/ instead of running flutter build.
    --release-version V  Override release version (default: active release from RELEASES.md).
    --apk-budget-mb N    APK per-ABI budget in MB (default 30).
    --aab-budget-mb N    AAB budget in MB (default 50).
    --archive-dir DIR    Override archive base directory (default releases/<version>/size_analysis/).

Exit codes:
    0   all budgets satisfied
    1   one or both budgets exceeded, or a flutter build failed
    2   invocation error (missing tools, missing artifacts, unknown release)

Output:
    Per-artifact pass/fail lines with measured size vs. budget, followed by a
    PASS/FAIL summary. On budget violation: prints top contributors parsed from
    the size-analysis JSON to aid investigation.
"""

# tier: C  # one-shot CLI release-pipeline script; no in-tree Python imports beyond util.yaml_frontmatter

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Why: this script runs as `python3 scripts/release/check_bundle_size.py` without
# PYTHONPATH and also under pytest. Insert scripts/ onto sys.path so
# `from util.yaml_frontmatter import ...` resolves either way — same pattern as
# scripts/release/check_release_preconditions.py.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above
    FrontmatterError,
    read_frontmatter,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = PROJECT_ROOT / "build"

DEFAULT_APK_BUDGET_MB = 30
DEFAULT_AAB_BUDGET_MB = 50
MB = 1024 * 1024

_JSON_PATH_RE = re.compile(r"(\S*code-size-analysis_\S+\.json)")


def get_active_release_version() -> str | None:
    """Return the version string of the active release in RELEASES.md, or None."""
    releases_path = PROJECT_ROOT / "requirements_tasks" / "RELEASES.md"
    if not releases_path.exists():
        return None
    try:
        doc = read_frontmatter(releases_path)
    except (FrontmatterError, OSError):
        return None
    if not doc.has_frontmatter:
        return None
    releases = doc.metadata.get("releases")
    if not isinstance(releases, list):
        return None
    for entry in releases:
        if isinstance(entry, dict) and str(entry.get("status", "")).strip() == "active":
            version = entry.get("version")
            if version is not None:
                return str(version).strip().strip("\"'")
    return None


def run_flutter_build(flutter_args: list[str], label: str) -> tuple[int, str]:
    """Run `flutter <args>` in the project root and return (rc, combined_output)."""
    print(f"[INFO] flutter {' '.join(flutter_args)} (this may take several minutes)", flush=True)
    result = subprocess.run(
        ["flutter", *flutter_args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        check=False,
    )
    combined = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        print(f"[FAIL] flutter {label} exited with code {result.returncode}")
        print(combined)
    return result.returncode, combined


def parse_analysis_json_path(output: str) -> Path | None:
    """Extract the size-analysis JSON path from flutter build output.

    Flutter prints e.g. 'A summary of your APK analysis can be found at:
    /abs/path/to/apk-code-size-analysis_01.json'. We pick the first token
    matching *code-size-analysis_*.json.
    """
    match = _JSON_PATH_RE.search(output)
    if not match:
        return None
    candidate = Path(match.group(1))
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / candidate).resolve()
    return candidate if candidate.exists() else None


def file_size_mb(path: Path) -> float:
    return path.stat().st_size / MB


def top_contributors(json_path: Path, n: int = 10) -> list[tuple[str, int]]:
    """Walk the size-analysis JSON depth-first; return top-N leaves by byte size.

    The JSON encodes a tree of nodes with 'n' (name) and 'value' (size in bytes),
    optionally with 'children'. Leaves are nodes without children that have a
    numeric value. We build the path during the walk so the leaf name carries
    enough context to identify the contributor (asset path, Dart class, etc.).
    """
    try:
        data = json.loads(json_path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    leaves: list[tuple[str, int]] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            name = str(node.get("n") or node.get("name") or "")
            value = node.get("value")
            children = node.get("children")
            full = f"{path}/{name}" if name else path
            if isinstance(value, (int, float)) and not children:
                leaves.append((full or "(unnamed)", int(value)))
            if isinstance(children, list):
                for child in children:
                    walk(child, full)
        elif isinstance(node, list):
            for item in node:
                walk(item, path)

    walk(data, "")
    leaves.sort(key=lambda x: x[1], reverse=True)
    return leaves[:n]


def archive_json(json_path: Path, archive_dir: Path, label: str) -> Path:
    archive_dir.mkdir(parents=True, exist_ok=True)
    dest = archive_dir / f"{label}_{json_path.name}"
    shutil.copy2(json_path, dest)
    return dest


def check_artifact(
    label: str,
    artifact_path: Path,
    budget_mb: int,
    json_path: Path | None,
) -> tuple[bool, str]:
    """Return (passed, summary block). On fail, block includes top contributors."""
    if not artifact_path.exists():
        return False, f"[FAIL] {label}: artifact not found at {artifact_path.relative_to(PROJECT_ROOT)}"
    size_mb = file_size_mb(artifact_path)
    passed = size_mb <= budget_mb
    marker = "[PASS]" if passed else "[FAIL]"
    head = (
        f"{marker} {label}: {size_mb:.2f} MB (budget {budget_mb} MB) — "
        f"{artifact_path.relative_to(PROJECT_ROOT)}"
    )
    if passed or json_path is None:
        return passed, head
    contributors = top_contributors(json_path)
    if not contributors:
        return passed, head
    lines = [head, "  Top contributors (from size-analysis JSON):"]
    for name, size in contributors:
        lines.append(f"    {size / MB:7.2f} MB  {name}")
    return passed, "\n".join(lines)


def resolve_archive_dir(archive_dir_arg: str | None, version: str | None) -> Path:
    if archive_dir_arg:
        return Path(archive_dir_arg).resolve()
    if version:
        return PROJECT_ROOT / "releases" / version / "size_analysis"
    return PROJECT_ROOT / "releases" / "unversioned" / "size_analysis"


def find_fallback_json(exclude: Path | None) -> Path | None:
    """Find the newest *code-size-analysis_*.json in build/ excluding `exclude`.

    Used when --skip-build is set (no build output to parse), or to locate the
    AAB JSON when only the APK path was captured from output.
    """
    if not BUILD_DIR.exists():
        return None
    candidates = sorted(
        (p for p in BUILD_DIR.rglob("*code-size-analysis_*.json") if p != exclude),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="REQ-PROC-046 AC-09 / G8 bundle-size budget gate")
    p.add_argument("--skip-build", action="store_true",
                   help="Use already-built artifacts under build/ instead of running flutter build")
    p.add_argument("--release-version", default=None,
                   help="Override release version (default: active release from RELEASES.md)")
    p.add_argument("--apk-budget-mb", type=int, default=DEFAULT_APK_BUDGET_MB,
                   help=f"APK per-ABI budget in MB (default {DEFAULT_APK_BUDGET_MB})")
    p.add_argument("--aab-budget-mb", type=int, default=DEFAULT_AAB_BUDGET_MB,
                   help=f"AAB budget in MB (default {DEFAULT_AAB_BUDGET_MB})")
    p.add_argument("--archive-dir", default=None,
                   help="Override archive base directory (default releases/<version>/size_analysis/)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    version = args.release_version or get_active_release_version()
    archive_base = resolve_archive_dir(args.archive_dir, version)
    stamp = datetime.now().astimezone().strftime("%Y-%m-%dT%H%M%S")
    archive_dir = archive_base / stamp

    apk_json: Path | None = None
    aab_json: Path | None = None

    if not args.skip_build:
        apk_rc, apk_out = run_flutter_build(
            ["build", "apk", "--analyze-size", "--target-platform=android-arm64"],
            label="build apk",
        )
        if apk_rc != 0:
            return 1
        apk_json = parse_analysis_json_path(apk_out)
        aab_rc, aab_out = run_flutter_build(
            ["build", "appbundle", "--analyze-size", "--target-platform=android-arm64"],
            label="build appbundle",
        )
        if aab_rc != 0:
            return 1
        aab_json = parse_analysis_json_path(aab_out)

    if apk_json is None:
        apk_json = find_fallback_json(exclude=None)
    if aab_json is None:
        aab_json = find_fallback_json(exclude=apk_json)

    apk_path = PROJECT_ROOT / "build" / "app" / "outputs" / "flutter-apk" / "app-release.apk"
    aab_path = PROJECT_ROOT / "build" / "app" / "outputs" / "bundle" / "release" / "app-release.aab"

    apk_ok, apk_line = check_artifact("APK arm64", apk_path, args.apk_budget_mb, apk_json)
    aab_ok, aab_line = check_artifact("AAB", aab_path, args.aab_budget_mb, aab_json)

    archived: list[Path] = []
    if apk_json is not None and apk_json.exists():
        archived.append(archive_json(apk_json, archive_dir, "apk"))
    if aab_json is not None and aab_json.exists() and aab_json != apk_json:
        archived.append(archive_json(aab_json, archive_dir, "aab"))

    print()
    print(apk_line)
    print(aab_line)
    print()
    if version:
        print(f"Release version: {version}")
    if archived:
        rel = archive_dir.relative_to(PROJECT_ROOT)
        print(f"Archived size-analysis JSON ({len(archived)} file(s)): {rel}")
    else:
        print("No size-analysis JSON found to archive.")
    print()

    all_ok = apk_ok and aab_ok
    print("[PASS] Bundle-size gate (G8)" if all_ok else "[FAIL] Bundle-size gate (G8)")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
