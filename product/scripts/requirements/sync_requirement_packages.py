#!/usr/bin/env python3
"""
Read-only gap scanner: list requirements with unassigned trackable_items.

Outputs requirements whose acceptance_criteria or sections entries have no
target_package set. Used by the requ-assign-packages skill and standalone for
CI/audit purposes.

Usage:
    python3 scripts/sync_requirement_packages.py [--requirement PATH]

    --requirement PATH   Scan only this requirements.md file; omit to scan all
                         requirements_tasks/

Run from the flutter_app directory.

Output:
    Prints one '<REQ-ID> <AC-ID> <status>' row per unassigned trackable_item to stdout, ending with a count summary.
"""

# tier: C  # one-shot CLI requirements tool; no in-tree Python imports

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Helpers (shared interface with sync_task_packages.py — copied to keep
# sync_requirement_packages.py self-contained and read-only)
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^(---\n)(.*?)(\n---)", re.DOTALL)


def split_frontmatter(content: str) -> tuple[str, str, str]:
    """
    Split file content into (opening, frontmatter_body, closing+rest).

    Returns (opening, frontmatter_body, closing+rest) or raises ValueError.
    Handles BOM prefix and CRLF line endings.
    """
    m = re.match(
        r"^(---\n)(.*?)(\n---(?:\n|$))(.*)",
        content,
        re.DOTALL,
    )
    if not m:
        raise ValueError("No valid YAML frontmatter found")
    return m.group(1), m.group(2), m.group(3) + m.group(4)


# ---------------------------------------------------------------------------
# Unassigned items parser
# ---------------------------------------------------------------------------

def parse_unassigned_items(req_path: Path) -> list[tuple[str, Optional[str]]]:
    """
    Parse a requirements.md and return items that have NO target_package.

    Reads from trackable_items.acceptance_criteria and trackable_items.sections
    in the YAML frontmatter.

    Returns a list of (item_id, text_or_none) for each unassigned item.
    text_or_none is None when no `text:` field is present on the item.

    Returns an empty list if frontmatter cannot be parsed or no items found.
    """
    raw = req_path.read_text(encoding="utf-8-sig")
    content = raw.replace("\r\n", "\n")

    try:
        _, fm_body, _ = split_frontmatter(content)
    except ValueError:
        return []

    unassigned: list[tuple[str, Optional[str]]] = []
    current_item_id: Optional[str] = None
    current_item_text: Optional[str] = None
    current_has_package: bool = False

    in_trackable_items = False
    in_ac_or_sections = False

    def flush_item() -> None:
        nonlocal current_item_id, current_item_text, current_has_package
        if current_item_id is not None and not current_has_package:
            unassigned.append((current_item_id, current_item_text))
        current_item_id = None
        current_item_text = None
        current_has_package = False

    for line in fm_body.splitlines():
        # Detect entry into trackable_items block
        if re.match(r'^trackable_items:\s*$', line):
            in_trackable_items = True
            continue

        if in_trackable_items:
            # Detect entry into acceptance_criteria or sections sub-block
            if re.match(r'^\s+acceptance_criteria:\s*$', line) or re.match(r'^\s+sections:\s*$', line):
                flush_item()
                in_ac_or_sections = True
                continue

            # Exit trackable_items if we hit a top-level key (no indent)
            if re.match(r'^\S', line) and not re.match(r'^---', line):
                flush_item()
                in_trackable_items = False
                in_ac_or_sections = False
                continue

        if in_trackable_items and in_ac_or_sections:
            # Match item id line: "    - id: AC-01" or "    - id: SEC-01"
            id_match = re.match(r'^\s+- id:\s+(\S+)', line)
            if id_match:
                flush_item()
                current_item_id = id_match.group(1).strip('"')
                continue

            # Match text line under current item: "      text: ..."
            text_match = re.match(r'^\s+text:\s+"?(.+?)"?\s*$', line)
            if text_match and current_item_id is not None:
                current_item_text = text_match.group(1).strip('"').strip()
                continue

            # Match target_package line under current item
            pkg_match = re.match(r'^\s+target_package:\s+"([^"]+)"', line)
            if pkg_match and current_item_id is not None:
                current_has_package = True
                continue

    # Flush last item
    flush_item()

    return unassigned


# ---------------------------------------------------------------------------
# Requirement ID extractor
# ---------------------------------------------------------------------------

def parse_req_id(req_path: Path) -> Optional[str]:
    """Extract the req_id field from requirements.md frontmatter."""
    raw = req_path.read_text(encoding="utf-8-sig")
    content = raw.replace("\r\n", "\n")

    try:
        _, fm_body, _ = split_frontmatter(content)
    except ValueError:
        return None

    m = re.search(r'^req_id:\s+"?([A-Z0-9\-]+)"?', fm_body, re.MULTILINE)
    if m:
        return m.group(1)

    # Fallback: try id: field
    m = re.search(r'^id:\s+"?([A-Z0-9\-]+)"?', fm_body, re.MULTILINE)
    if m:
        return m.group(1)

    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only gap scanner: list requirements with unassigned trackable_items. "
            "Never writes files."
        )
    )
    parser.add_argument(
        "--requirement",
        metavar="PATH",
        help="Scan only this requirements.md file; omit to scan all requirements_tasks/",
    )
    args = parser.parse_args()

    # Resolve paths relative to script location (scripts/ inside flutter_app/)
    script_dir = Path(__file__).parent
    flutter_app_dir = script_dir.parent.parent
    tasks_root = flutter_app_dir / "requirements_tasks"

    # Determine scan targets
    if args.requirement:
        req_path = Path(args.requirement)
        if not req_path.is_absolute():
            req_path = flutter_app_dir / req_path
        if not req_path.exists():
            print(f"ERROR: --requirement path does not exist: {req_path}", file=sys.stderr)
            return 1
        req_files = [req_path]
    else:
        req_files = sorted(tasks_root.rglob("requirements.md"))

    results: list[tuple[str, Path, list[tuple[str, Optional[str]]]]] = []

    for req_file in req_files:
        unassigned = parse_unassigned_items(req_file)
        if not unassigned:
            continue

        req_id = parse_req_id(req_file)
        label = req_id if req_id else req_file.parent.name

        try:
            display_path = req_file.relative_to(flutter_app_dir)
        except ValueError:
            display_path = req_file

        results.append((label, display_path, unassigned))

    if not results:
        print("No requirements with unassigned trackable items found.")
        return 0

    print("Requirements with unassigned trackable items:\n")

    total_items = 0
    for label, display_path, items in results:
        print(f"{label}  {display_path}")
        for item_id, text in items:
            if text:
                print(f'  {item_id}: "{text}"')
            else:
                print(f'  {item_id}: (no description)')
            total_items += 1
        print()

    req_count = len(results)
    print(f"{req_count} requirement{'s' if req_count != 1 else ''}, {total_items} unassigned item{'s' if total_items != 1 else ''}.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
