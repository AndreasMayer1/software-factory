#!/usr/bin/env python3
"""Check parity between requirements_tasks/scribbles/ and lib/features/.

Output:
  stdout — ERROR/WARNING lines plus a summary line.
  Exit 0 — no errors (warnings are OK unless --strict).
  Exit 1 — one or more errors present.

Consumer: CI / pre-commit hook (reads exit code); developer (reads stdout).
"""

# tier: B  # validator; parity enforcement for scribble-storage mirror (REQ-PROC-032 AC-37)

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIBBLES_ROOT_REL = "requirements_tasks/scribbles"
FEATURES_ROOT_REL = "lib/features"
METADATA_FILENAME = "metadata.yaml"
PRESENTATION_DIR_NAME = "presentation"


# ---------------------------------------------------------------------------
# Collection helpers
# ---------------------------------------------------------------------------


def collect_scribble_feature_paths(scribbles_root: Path) -> set[str]:
    """Return unique feature_path values from all metadata.yaml files under scribbles_root."""
    paths: set[str] = set()
    if not scribbles_root.is_dir():
        return paths
    for meta_file in scribbles_root.rglob(METADATA_FILENAME):
        try:
            with meta_file.open() as f:
                data = yaml.safe_load(f)
        except (OSError, yaml.YAMLError):
            continue
        if isinstance(data, dict):
            fp = data.get("feature_path")
            if isinstance(fp, str) and fp:
                paths.add(fp)
    return paths


def collect_lib_features_leaves(features_root: Path) -> set[str]:
    """Return relative paths of leaf features — dirs that contain a presentation/ sub-dir."""
    leaves: set[str] = set()
    if not features_root.is_dir():
        return leaves
    for candidate in features_root.rglob(PRESENTATION_DIR_NAME):
        if candidate.is_dir():
            leaf_abs = candidate.parent
            leaves.add(str(leaf_abs.relative_to(features_root)))
    return leaves


# ---------------------------------------------------------------------------
# Parity check
# ---------------------------------------------------------------------------


def check_parity(
    scribble_paths: set[str],
    lib_leaves: set[str],
    features_root: Path,
    scribbles_root: Path,
) -> tuple[list[str], list[str]]:
    """Return (errors, warnings).

    Errors: scribble feature_path with no matching lib/features/ node (stale).
    Warnings: lib/features/ leaf with no covering scribble (coverage gap).
    """
    errors: list[str] = []
    warnings: list[str] = []

    for fp in sorted(scribble_paths):
        if not (features_root / fp).is_dir():
            errors.append(
                f"ERROR: stale scribble path: {fp} has no matching lib/features/ node"
            )

    for leaf in sorted(lib_leaves):
        scribble_dir = scribbles_root / leaf
        if not any(scribble_dir.rglob(METADATA_FILENAME)):
            warnings.append(
                f"WARNING: coverage gap: lib/features/{leaf} has no scribble"
            )

    return errors, warnings


# ---------------------------------------------------------------------------
# Project root detection
# ---------------------------------------------------------------------------


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from start (default: cwd) to find the project root via pubspec.yaml."""
    current = (start or Path.cwd()).resolve()
    for ancestor in [current, *current.parents]:
        if (ancestor / "pubspec.yaml").exists():
            return ancestor
    return current


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------


def run_check(
    root: Path,
    *,
    quiet: bool = False,
    strict: bool = False,
) -> int:
    """Run the parity check and print results. Returns exit code (0 or 1)."""
    scribbles_root = root / SCRIBBLES_ROOT_REL
    features_root = root / FEATURES_ROOT_REL

    scribble_paths = collect_scribble_feature_paths(scribbles_root)
    lib_leaves = collect_lib_features_leaves(features_root)

    errors, warnings = check_parity(scribble_paths, lib_leaves, features_root, scribbles_root)

    if strict:
        promoted = [w.replace("WARNING:", "ERROR:") for w in warnings]
        errors = errors + promoted
        warnings = []

    if not quiet:
        for line in warnings:
            print(line)
    for line in errors:
        print(line)

    error_count = len(errors)
    warning_count = len(warnings)

    summary_parts: list[str] = []
    if error_count:
        summary_parts.append(f"{error_count} error(s)")
    if not quiet and warning_count:
        summary_parts.append(f"{warning_count} warning(s)")
    if not summary_parts:
        summary_parts.append("OK")

    print(f"scribble-parity: {', '.join(summary_parts)}")

    return 1 if errors else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check parity between scribble storage and lib/features/."
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress warnings; only show errors.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat coverage-gap warnings as errors.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Project root (default: auto-detected via pubspec.yaml).",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    root = args.root if args.root is not None else find_project_root()
    sys.exit(run_check(root, quiet=args.quiet, strict=args.strict))


if __name__ == "__main__":
    main()
