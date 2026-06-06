#!/usr/bin/env python3
"""Classify direct pubspec.yaml dependencies by usage evidence (REQ-PROC-061 AC-11).

Scans lib/, test/, integration_test/ for Dart import statements. Classifies
each direct dependency as: directly_imported / indirectly_required / no_evidence_of_use.
Packages with no_evidence_of_use are removal candidates — not upgrade candidates.

Usage:
    python3 scripts/release/check_dependency_usage.py [--json] [--project-root PATH]

Output:
    Human-readable table (default): per-package classification printed to stdout,
    sorted by classification then name. Removal candidates listed at the bottom.
    JSON (--json): {"direct": [...], "dev": [...], "removal_candidates": [...]}
    each entry has name, classification, import_count, indirect_reason fields.
    Exit 0 on success; exit 1 if pubspec.yaml not found.
"""

# tier: C  # one-shot CLI review tool; no in-tree Python imports

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Packages with no direct import but required as platform binaries, code-gen tools,
# or runtime support libraries for another admitted direct dependency. Each value
# names the consuming dependency so the chain is auditable in the proposal.
INDIRECT_REQUIREMENTS: dict[str, str] = {
    "sqlite3_flutter_libs": (
        "platform binaries (SQLite native library) required by drift NativeDatabase "
        "on desktop and Android"
    ),
    "path": "runtime path utilities required by drift for database file-path resolution",
    "build_runner": (
        "code-generation runner required to invoke drift_dev, freezed, "
        "injectable_generator, and json_serializable"
    ),
    "drift_dev": (
        "code-generation companion for drift — generates .g.dart database schema files"
    ),
    "freezed": (
        "code-generation companion for freezed_annotation — generates .freezed.dart files"
    ),
    "injectable_generator": (
        "code-generation companion for injectable — generates get_it registration code"
    ),
    "json_serializable": (
        "code-generation companion for json_annotation — "
        "generates .g.dart JSON serialization files"
    ),
}

Classification = Literal["directly_imported", "indirectly_required", "no_evidence_of_use"]

_CLASSIFICATION_ORDER: dict[str, int] = {
    "directly_imported": 0,
    "indirectly_required": 1,
    "no_evidence_of_use": 2,
}

_SOURCE_DIRS: tuple[str, ...] = ("lib", "test", "integration_test")

# Matches `import 'package:<name>/` or `import "package:<name>/` in Dart source.
_IMPORT_RE = re.compile(r"""import\s+['"]{1}package:(\w+)/""")

_COL_PKG = 35
_COL_CLS = 22


@dataclass
class DependencyResult:
    name: str
    classification: Classification
    indirect_reason: str = ""
    import_count: int = 0


def _parse_pubspec_deps(project_root: Path) -> dict[str, list[str]]:
    """Return {'direct': [...], 'dev': [...]} package names, excluding SDK packages."""
    pubspec = project_root / "pubspec.yaml"
    if not pubspec.exists():
        print(f"[ERROR] pubspec.yaml not found: {pubspec}", file=sys.stderr)
        sys.exit(1)
    with pubspec.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, dict):
        return {"direct": [], "dev": []}
    result: dict[str, list[str]] = {"direct": [], "dev": []}
    for section_key, result_key in (
        ("dependencies", "direct"),
        ("dev_dependencies", "dev"),
    ):
        section = raw.get(section_key) or {}
        if not isinstance(section, dict):
            continue
        for name, spec in section.items():
            # Skip SDK packages (flutter, flutter_localizations, integration_test…)
            if isinstance(spec, dict) and "sdk" in spec:
                continue
            result[result_key].append(str(name))
    return result


def _scan_import_counts(project_root: Path, packages: list[str]) -> dict[str, int]:
    """Count how many source files import each package.

    Scans .dart files in lib/, test/, integration_test/ for import statements.
    Counts by file (not by import line), so a file with two imports of the same
    package counts as one.
    """
    packages_set = set(packages)
    counts: dict[str, int] = dict.fromkeys(packages, 0)
    for dir_name in _SOURCE_DIRS:
        src_dir = project_root / dir_name
        if not src_dir.exists():
            continue
        for dart_file in src_dir.rglob("*.dart"):
            try:
                content = dart_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            seen: set[str] = set()
            for match in _IMPORT_RE.finditer(content):
                pkg = match.group(1)
                if pkg in packages_set:
                    seen.add(pkg)
            for pkg in seen:
                counts[pkg] += 1
    return counts


def _classify(name: str, import_count: int) -> DependencyResult:
    """Classify a single package into one of three buckets."""
    if import_count > 0:
        return DependencyResult(name, "directly_imported", import_count=import_count)
    if name in INDIRECT_REQUIREMENTS:
        return DependencyResult(
            name, "indirectly_required", indirect_reason=INDIRECT_REQUIREMENTS[name]
        )
    return DependencyResult(name, "no_evidence_of_use")


def classify_dependencies(
    project_root: Path,
) -> tuple[list[DependencyResult], list[DependencyResult]]:
    """Return (direct_results, dev_results) for all pubspec.yaml packages."""
    deps = _parse_pubspec_deps(project_root)
    counts = _scan_import_counts(project_root, deps["direct"] + deps["dev"])
    direct = [_classify(p, counts.get(p, 0)) for p in deps["direct"]]
    dev = [_classify(p, counts.get(p, 0)) for p in deps["dev"]]
    return direct, dev


def _sort_key(r: DependencyResult) -> tuple[int, str]:
    return (_CLASSIFICATION_ORDER.get(r.classification, 99), r.name)


def _print_section(results: list[DependencyResult], heading: str) -> None:
    if not results:
        return
    print(f"\n## {heading}")
    print(f"  {'Package':<{_COL_PKG}} {'Classification':<{_COL_CLS}} Notes")
    print("  " + "-" * 85)
    for r in sorted(results, key=_sort_key):
        if r.classification == "directly_imported":
            notes = f"{r.import_count} file(s)"
        elif r.classification == "indirectly_required":
            notes = r.indirect_reason[:55] + ("…" if len(r.indirect_reason) > 55 else "")
        else:
            notes = "** REMOVAL CANDIDATE **"
        print(f"  {r.name:<{_COL_PKG}} {r.classification:<{_COL_CLS}} {notes}")


def _to_dict(r: DependencyResult) -> dict[str, object]:
    return {
        "name": r.name,
        "classification": r.classification,
        "import_count": r.import_count,
        "indirect_reason": r.indirect_reason,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify pubspec.yaml dependencies by usage.")
    parser.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Output JSON instead of human-readable table",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        metavar="PATH",
        help="Project root (default: inferred from script location)",
    )
    args = parser.parse_args()
    root: Path = args.project_root.resolve()

    direct_results, dev_results = classify_dependencies(root)
    all_results = direct_results + dev_results
    removal_candidates = [r.name for r in all_results if r.classification == "no_evidence_of_use"]

    if args.output_json:
        print(
            json.dumps(
                {
                    "direct": [_to_dict(r) for r in direct_results],
                    "dev": [_to_dict(r) for r in dev_results],
                    "removal_candidates": removal_candidates,
                },
                indent=2,
            )
        )
        return

    print("Dependency Usage Classification (REQ-PROC-061 AC-11)")
    print("=" * 90)
    print(f"Project root : {root}")
    print(f"Scanned dirs : {', '.join(_SOURCE_DIRS)}")
    print("SDK packages excluded (flutter_sdk family)")
    _print_section(direct_results, "Direct Dependencies (dependencies:)")
    _print_section(dev_results, "Dev Dependencies (dev_dependencies:)")
    print(f"\n{'=' * 90}")
    if removal_candidates:
        print(
            f"\nREMOVAL CANDIDATES — {len(removal_candidates)} package(s) with no evidence of use:"
        )
        for name in removal_candidates:
            print(f"  - {name}")
        print()
        print("  List these in the 'Removal Candidates' section of proposal.md,")
        print("  not in the upgrade section.")
    else:
        print("\nNo removal candidates — all packages have usage evidence.")
    print()


if __name__ == "__main__":
    main()
