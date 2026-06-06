#!/usr/bin/env python3
"""Validate epic-level requirements files against size and content-type rules.

Rules enforced:
  - Epic body (non-YAML) must not exceed 90 lines
  - All features listed in ## Features must have a corresponding feat_*/ folder

Usage:
  python3 scripts/validate_epic_requirements.py [--path PATH] [--quiet]

Exits 0 if all epics pass, non-zero if violations found.

Output:
    Prints one '<path>: <violation>' line per failing epic to stdout (or stays silent with --quiet on pass), ending with a summary line.
"""

# tier: C  # one-shot CLI requirements tool; no in-tree Python imports

import argparse
import sys
from pathlib import Path

# Why: this script runs both as `python3 scripts/requirements/validate_epic_requirements.py`
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

EPIC_BODY_LINE_LIMIT = 90


def count_body_lines(content: str) -> int:
    """Count non-YAML body lines (strips frontmatter block).

    When the document has no frontmatter (or it is unclosed), the helper
    returns the whole input as `body`; we then return the full line count
    matching the prior behaviour for that case.

    For documents WITH frontmatter, the prior implementation counted lines
    using `content.splitlines()[body_start:]`. The central helper strips one
    leading newline from the body, which would under-count by 1 when the
    body consists exclusively of empty lines. We restore the prior count by
    locating the closing '---' in the raw text and counting from there.
    """
    try:
        doc = read_frontmatter(content)
    except FrontmatterError:
        # Malformed frontmatter — fall back to full line count, matching the
        # prior tolerance of unclosed/unparseable headers.
        return len(content.splitlines())

    if not doc.has_frontmatter:
        return len(content.splitlines())

    # Reproduce prior exact semantics: count lines after the closing '---'.
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if i == 0:
            continue
        if line.strip() == "---":
            return len(lines[i + 1 :])
    return len(lines)


def find_feature_folders(epic_dir: Path) -> set[str]:
    """Return names of feat_*/ subfolders in an epic directory."""
    return {
        d.name for d in epic_dir.iterdir()
        if d.is_dir() and d.name.startswith("feat_")
    }


def extract_listed_features(content: str) -> list[str]:
    """Extract feat_*/ links mentioned in the ## Features section body."""
    features = []
    in_features = False
    for line in content.splitlines():
        if line.strip().startswith("## Features"):
            in_features = True
            continue
        if in_features and line.startswith("## "):
            break
        if in_features:
            # Match patterns like `feat_foo/` or (feat_foo/) in the line
            import re
            matches = re.findall(r"\bfeat_[\w]+(?:/)?", line)
            for m in matches:
                name = m.rstrip("/")
                if name not in features:
                    features.append(name)
    return features


def validate_epic(path: Path, quiet: bool) -> tuple[list[str], int]:
    """Validate a single epic requirements.md. Returns (violations, body_line_count)."""
    violations = []
    content = path.read_text(encoding="utf-8")
    epic_dir = path.parent

    # Rule 1: body line count
    body_lines = count_body_lines(content)
    if body_lines > EPIC_BODY_LINE_LIMIT:
        violations.append(
            f"body too long: {body_lines} lines (limit: {EPIC_BODY_LINE_LIMIT})"
        )

    # Rule 2: features listed without corresponding folder
    listed = extract_listed_features(content)
    existing_folders = find_feature_folders(epic_dir)
    for feat in listed:
        if feat not in existing_folders:
            violations.append(
                f"listed feature '{feat}' has no folder in {epic_dir.name}/"
            )

    return violations, body_lines


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate epic requirements size and structure"
    )
    parser.add_argument(
        "--path", default="requirements_tasks",
        help="Root directory to search (default: requirements_tasks)"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Only show failures, not passing epics"
    )
    args = parser.parse_args()

    root = Path(args.path)
    if not root.exists():
        print(f"Error: path '{root}' not found", file=sys.stderr)
        sys.exit(1)

    epics = sorted(root.glob("**/epic_*/requirements.md"))

    if not epics:
        print("No epic requirements files found.")
        sys.exit(0)

    print(f"Checking {len(epics)} epic requirements file(s)...\n")
    total_violations = 0

    for epic_path in epics:
        violations, body_lines = validate_epic(epic_path, args.quiet)
        rel = epic_path.relative_to(Path("."))

        if violations:
            total_violations += len(violations)
            print(f"FAIL  {rel}  ({body_lines} lines)")
            for v in violations:
                print(f"      → {v}")
        elif not args.quiet:
            print(f"OK    {rel}  ({body_lines} lines)")

    print(f"\n{'='*60}")
    if total_violations:
        print(f"FAILED: {total_violations} violation(s)")
        sys.exit(1)
    else:
        print(f"PASSED: all {len(epics)} epic(s) within limits")
        sys.exit(0)


if __name__ == "__main__":
    main()
