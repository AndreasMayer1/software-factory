#!/usr/bin/env python3
"""
Sync target_package fields in task goal.md files from their covering requirement's ACs/sections.

When ACs in a requirement get packages assigned (via requ-explore Phase 2.4), covering
impl/explore tasks should be synced so their top-level target_package reflects the earliest
package among all items they cover.

Usage:
    python3 scripts/sync_task_packages.py [--requirement PATH] [--dry-run | --apply]

    --requirement PATH   Scan only this requirement folder; omit to scan all requirements_tasks/
    --dry-run            Report changes without writing (default)
    --apply              Write changes to files

Run from the flutter_app directory.

Output:
    Prints one '<TASK-ID> <OLD> -> <NEW>' line per change (or planned change in --dry-run) to stdout, ending with a summary count.
"""

# tier: C  # one-shot CLI requirements tool; no in-tree Python imports

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Optional, cast

# ---------------------------------------------------------------------------
# Helpers (originally shared with the now-deleted migrate_target_release_to_package.py)
# ---------------------------------------------------------------------------

def parse_release_backlog(backlog_path: Path) -> list[dict[Any, Any]]:
    """
    Parse the YAML frontmatter of RELEASE_BACKLOG.md and return the packages list.

    Returns a list of package dicts with keys:
        id, source (type, ref, scope), description,
        priority_within_source, status, assigned_release
    """
    content = backlog_path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")

    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        raise ValueError(f"No YAML frontmatter found in {backlog_path}")

    frontmatter = fm_match.group(1)

    packages = []
    current_pkg: dict[Any, Any] | None = None

    for line in frontmatter.splitlines():
        id_match = re.match(r'^  - id:\s*"(.+)"', line)
        if id_match:
            if current_pkg is not None:
                packages.append(current_pkg)
            current_pkg = {
                "id": id_match.group(1),
                "source": {"type": None, "ref": None, "scope": None},
                "description": None,
                "priority_within_source": None,
                "status": None,
                "assigned_release": None,
            }
            continue

        if current_pkg is None:
            continue

        src_type = re.match(r'^\s+type:\s+(.+)', line)
        if src_type:
            current_pkg["source"]["type"] = src_type.group(1).strip().strip('"')
            continue

        src_ref = re.match(r'^\s+ref:\s+(.+)', line)
        if src_ref:
            val = src_ref.group(1).strip().strip('"')
            current_pkg["source"]["ref"] = None if val == "null" else val
            continue

        src_scope = re.match(r'^\s+scope:\s+(.+)', line)
        if src_scope:
            val = src_scope.group(1).strip().strip('"')
            current_pkg["source"]["scope"] = val
            continue

        status_m = re.match(r'^\s+status:\s+(.+)', line)
        if status_m:
            current_pkg["status"] = status_m.group(1).strip().strip('"')
            continue

        ar_m = re.match(r'^\s+assigned_release:\s+(.+)', line)
        if ar_m:
            val = ar_m.group(1).strip().strip('"')
            current_pkg["assigned_release"] = None if val == "null" else val
            continue

    if current_pkg is not None:
        packages.append(current_pkg)

    return packages


def build_lookup(packages: list[dict[Any, Any]]) -> dict[Any, Any]:
    """
    Build a lookup structure (used for semver comparison via earliest_package).

    Returns:
        {
            "by_id": {package_id: pkg},
            "ordered": [pkg, ...],  # original order (position = priority)
        }
    """
    by_id: dict[str, dict[Any, Any]] = {}
    for pkg in packages:
        by_id[pkg["id"]] = pkg

    return {
        "by_id": by_id,
        "ordered": packages,
    }


def semver_tuple(version: str) -> tuple[Any, ...]:
    """Convert a semver string to a comparable tuple."""
    try:
        parts = [int(x) for x in version.split(".")]
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts)
    except ValueError:
        return (999, 999, 999)


def earliest_package(packages_found: list[dict[Any, Any]], lookup: dict[Any, Any]) -> Optional[str]:
    """
    Return the package id with the highest priority (earliest in backlog).

    Priority rules:
    1. Both versioned: lower semver = earlier
    2. One versioned: versioned is earlier
    3. Neither versioned: lower index in lookup["ordered"] = earlier
    """
    if not packages_found:
        return None
    if len(packages_found) == 1:
        return cast("str | None", packages_found[0]["id"])

    def sort_key(pkg: dict[Any, Any]) -> Any:
        ver = pkg["assigned_release"]
        if ver is not None:
            return (0, semver_tuple(ver), 0)
        try:
            idx = lookup["ordered"].index(pkg)
        except ValueError:
            idx = 999999
        return (1, (0, 0, 0), idx)

    sorted_pkgs = sorted(packages_found, key=sort_key)
    return cast("str | None", sorted_pkgs[0]["id"])


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
# Requirements.md parser — build item_id → target_package map
# ---------------------------------------------------------------------------

def parse_item_package_map(req_path: Path) -> dict[str, str]:
    """
    Parse a requirements.md and return a map of item_id → target_package.

    Reads from trackable_items.acceptance_criteria and trackable_items.sections
    in the YAML frontmatter.

    Returns an empty dict if frontmatter cannot be parsed or no items found.
    """
    raw = req_path.read_text(encoding="utf-8-sig")
    content = raw.replace("\r\n", "\n")

    try:
        _, fm_body, _ = split_frontmatter(content)
    except ValueError:
        return {}

    item_map: dict[str, str] = {}
    current_item_id: Optional[str] = None
    in_trackable_items = False
    in_ac_or_sections = False

    for line in fm_body.splitlines():
        # Detect entry into trackable_items block
        if re.match(r'^trackable_items:\s*$', line):
            in_trackable_items = True
            continue

        if in_trackable_items:
            # Detect entry into acceptance_criteria or sections sub-block
            if re.match(r'^\s+acceptance_criteria:\s*$', line) or re.match(r'^\s+sections:\s*$', line):
                in_ac_or_sections = True
                current_item_id = None
                continue

            # Exit trackable_items if we hit a top-level key (no indent)
            if re.match(r'^\S', line) and not re.match(r'^---', line):
                in_trackable_items = False
                in_ac_or_sections = False
                current_item_id = None
                continue

        if in_trackable_items and in_ac_or_sections:
            # Match item id line: "    - id: AC-01" or "    - id: SEC-01"
            id_match = re.match(r'^\s+- id:\s+(\S+)', line)
            if id_match:
                current_item_id = id_match.group(1).strip('"')
                continue

            # Match target_package line under current item
            pkg_match = re.match(r'^\s+target_package:\s+"([^"]+)"', line)
            if pkg_match and current_item_id is not None:
                item_map[current_item_id] = pkg_match.group(1)
                continue

    return item_map


# ---------------------------------------------------------------------------
# Goal.md parser and updater
# ---------------------------------------------------------------------------

def parse_covers(fm_body: str) -> tuple[list[str], list[str]]:
    """
    Parse covers.acceptance_criteria and covers.sections from frontmatter body.

    Returns (acceptance_criteria_list, sections_list).
    Handles both inline list format ([AC-01, AC-02]) and multi-line bullet format.
    Uses a line-by-line state machine to avoid greedy cross-field capturing.
    """
    ac_ids: list[str] = []
    sec_ids: list[str] = []

    # State machine states
    IN_NONE = 0
    IN_COVERS = 1
    IN_AC = 2
    IN_SEC = 3

    state = IN_NONE
    covers_indent = 0

    for line in fm_body.splitlines():
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if state == IN_NONE:
            if stripped.startswith("covers:"):
                state = IN_COVERS
                covers_indent = indent
            continue

        if state == IN_COVERS:
            # Exit covers block if we return to same or lower indent
            if stripped and indent <= covers_indent and not stripped.startswith("-"):
                break

            # Inline acceptance_criteria: [AC-01, AC-02]
            m = re.match(r'acceptance_criteria:\s*\[([^\]]*)\]', stripped)
            if m:
                raw = m.group(1)
                ac_ids = [i.strip().strip("\"'") for i in raw.split(',') if i.strip()]
                continue

            # Multi-line acceptance_criteria:
            if re.match(r'acceptance_criteria:\s*$', stripped):
                state = IN_AC
                continue

            # Inline sections: [SEC-01]
            m = re.match(r'sections:\s*\[([^\]]*)\]', stripped)
            if m:
                raw = m.group(1)
                sec_ids = [i.strip().strip("\"'") for i in raw.split(',') if i.strip()]
                continue

            # Multi-line sections:
            if re.match(r'sections:\s*$', stripped):
                state = IN_SEC
                continue

        elif state == IN_AC:
            # Back to covers-level key → exit ac list
            if stripped and indent <= covers_indent + 2 and not stripped.startswith("-"):
                state = IN_COVERS
                # Re-process this line as covers-level
                m = re.match(r'sections:\s*\[([^\]]*)\]', stripped)
                if m:
                    raw = m.group(1)
                    sec_ids = [i.strip().strip("\"'") for i in raw.split(',') if i.strip()]
                elif re.match(r'sections:\s*$', stripped):
                    state = IN_SEC
                continue

            m = re.match(r'-\s+(.+)', stripped)
            if m:
                ac_ids.append(m.group(1).strip().strip("\"'"))

        elif state == IN_SEC:
            # Back to covers-level key → done
            if stripped and indent <= covers_indent + 2 and not stripped.startswith("-"):
                break

            m = re.match(r'-\s+(.+)', stripped)
            if m:
                sec_ids.append(m.group(1).strip().strip("\"'"))

    return ac_ids, sec_ids


def compute_target_package(
    ac_ids: list[str],
    sec_ids: list[str],
    item_map: dict[str, str],
    lookup: dict[Any, Any],
) -> Optional[str]:
    """
    Compute the target_package for a task based on its covered items.

    Looks up each covered item_id in item_map, collects the distinct packages,
    and returns the earliest-versioned one.

    Returns None if no covered items have assigned packages.
    """
    packages_found: list[dict[Any, Any]] = []
    seen_pkg_ids: set[str] = set()

    all_covered = ac_ids + sec_ids
    for item_id in all_covered:
        pkg_name = item_map.get(item_id)
        if pkg_name and pkg_name not in seen_pkg_ids:
            pkg_obj = lookup["by_id"].get(pkg_name)
            if pkg_obj:
                packages_found.append(pkg_obj)
                seen_pkg_ids.add(pkg_name)
            else:
                # Package name exists in requirement but not in backlog — still use it
                # by creating a synthetic entry with no version (lowest priority)
                synthetic = {"id": pkg_name, "assigned_release": None}
                packages_found.append(synthetic)
                seen_pkg_ids.add(pkg_name)

    return earliest_package(packages_found, lookup)


def update_target_package_in_frontmatter(fm_body: str, new_pkg: str) -> str:
    """
    Set or update the target_package field in the frontmatter body.

    If target_package already exists as a top-level field, replace it.
    If absent, insert it after the first existing top-level field line
    that seems reasonable (after status or before covers).

    Uses targeted line-level replacement to avoid reformatting the YAML.
    """
    lines = fm_body.splitlines(keepends=True)
    new_lines = []
    replaced = False

    for line in lines:
        if not replaced and re.match(r'^target_package:\s*', line):
            new_lines.append(f'target_package: "{new_pkg}"\n')
            replaced = True
        else:
            new_lines.append(line)

    if not replaced:
        # Insert before 'covers:' line, or before 'scope_description:', or at end
        insert_before_patterns = [
            re.compile(r'^covers:\s*$'),
            re.compile(r'^scope_description:\s*'),
        ]
        insert_idx = len(new_lines)
        for i, line in enumerate(new_lines):
            for pat in insert_before_patterns:
                if pat.match(line):
                    insert_idx = i
                    break
            if insert_idx < len(new_lines):
                break

        new_lines.insert(insert_idx, f'target_package: "{new_pkg}"\n')

    return "".join(new_lines)


# ---------------------------------------------------------------------------
# Core sync logic
# ---------------------------------------------------------------------------

def sync_goal_md(
    goal_path: Path,
    item_map: dict[str, str],
    lookup: dict[Any, Any],
    dry_run: bool,
    base_dir: Path,
) -> Optional[str]:
    """
    Sync target_package in a goal.md based on its covers and item_map.

    Returns a report string if a change occurred (or would occur in dry-run),
    None if unchanged or skipped.
    """
    raw = goal_path.read_text(encoding="utf-8-sig")
    crlf = "\r\n" in raw
    content = raw.replace("\r\n", "\n")

    try:
        opening, fm_body, rest = split_frontmatter(content)
    except ValueError:
        return f"  ERROR: cannot parse frontmatter in {goal_path}"

    ac_ids, sec_ids = parse_covers(fm_body)

    # Skip tasks with empty covers — they have no concrete AC/section coverage.
    # This naturally handles flow-derived explore tasks, verification tasks, and
    # requirement-writing explore tasks — all of which have no covers entries.
    if not ac_ids and not sec_ids:
        return None

    computed_pkg = compute_target_package(ac_ids, sec_ids, item_map, lookup)
    if computed_pkg is None:
        # Covered items exist but none have packages assigned yet — skip silently
        return None

    # Read current target_package
    current_match = re.search(r'^target_package:\s*"([^"]*)"', fm_body, re.MULTILINE)
    current_pkg = current_match.group(1) if current_match else None

    if current_pkg == computed_pkg:
        try:
            rel = goal_path.relative_to(base_dir)
        except ValueError:
            rel = goal_path
        return f"  unchanged: {rel}"

    # Compute display path
    try:
        rel = goal_path.relative_to(base_dir)
    except ValueError:
        rel = goal_path

    old_label = f'"{current_pkg}"' if current_pkg else "absent"
    report = f"  synced:    {rel}: {old_label} → \"{computed_pkg}\""

    if not dry_run:
        new_fm_body = update_target_package_in_frontmatter(fm_body, computed_pkg)
        new_content = opening + new_fm_body + rest
        out = new_content.replace("\n", "\r\n") if crlf else new_content
        goal_path.write_text(out, encoding="utf-8")

    return report


def sync_requirement_folder(
    req_folder: Path,
    lookup: dict[Any, Any],
    dry_run: bool,
    base_dir: Path,
) -> list[str]:
    """
    Sync all task goal.md files under a requirement folder.

    Reads requirements.md from req_folder, builds the item_map, then processes
    each goal.md in req_folder/tasks/*/goal.md (one level deep).

    Returns a list of report lines.
    """
    reports: list[str] = []

    req_md = req_folder / "requirements.md"
    if not req_md.exists():
        return reports

    item_map = parse_item_package_map(req_md)
    if not item_map:
        # No packages assigned to any items yet — nothing to sync
        return reports

    tasks_dir = req_folder / "tasks"
    if not tasks_dir.is_dir():
        return reports

    # One level deep: tasks/[task_folder]/goal.md
    for task_folder in sorted(tasks_dir.iterdir()):
        if not task_folder.is_dir():
            continue
        goal_path = task_folder / "goal.md"
        if not goal_path.exists():
            continue

        result = sync_goal_md(goal_path, item_map, lookup, dry_run, base_dir)
        if result is not None:
            reports.append(result)

    return reports


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Sync target_package in task goal.md files from their covering requirement's "
            "AC/section packages. Defaults to --dry-run."
        )
    )
    parser.add_argument(
        "--requirement",
        metavar="PATH",
        help="Scan only this requirement folder; omit to scan all requirements_tasks/",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Report what would change without writing (default)",
    )
    mode_group.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Actually write changes to files",
    )
    args = parser.parse_args()

    dry_run = not args.apply

    # Resolve paths relative to script location (scripts/ inside flutter_app/)
    script_dir = Path(__file__).parent
    flutter_app_dir = script_dir.parent.parent
    backlog_path = flutter_app_dir / "requirements_tasks" / "RELEASE_BACKLOG.md"
    tasks_root = flutter_app_dir / "requirements_tasks"

    if not backlog_path.exists():
        print(f"ERROR: RELEASE_BACKLOG.md not found at {backlog_path}", file=sys.stderr)
        return 1

    # Parse backlog for version-based package ordering
    print(f"Parsing {backlog_path.relative_to(flutter_app_dir)} ...")
    packages = parse_release_backlog(backlog_path)
    lookup = build_lookup(packages)
    print(f"  Found {len(packages)} packages")

    # Determine scan root
    if args.requirement:
        scan_root = Path(args.requirement)
        if not scan_root.is_absolute():
            scan_root = flutter_app_dir / scan_root
        if not scan_root.is_dir():
            print(f"ERROR: --requirement path does not exist: {scan_root}", file=sys.stderr)
            return 1
        req_folders = [scan_root]
    else:
        # Collect all folders that contain a requirements.md
        req_folders = sorted(
            p.parent for p in tasks_root.rglob("requirements.md")
        )

    mode_label = "DRY RUN" if dry_run else "APPLYING"
    print(f"\n[{mode_label}] Scanning {len(req_folders)} requirement folder(s) ...\n")

    all_reports: list[str] = []
    synced_count = 0
    unchanged_count = 0

    for req_folder in req_folders:
        reports = sync_requirement_folder(req_folder, lookup, dry_run, flutter_app_dir)
        if reports:
            try:
                label = req_folder.relative_to(flutter_app_dir)
            except ValueError:
                label = req_folder
            print(f"{label}/")
            for line in reports:
                print(line)
                if "synced:" in line:
                    synced_count += 1
                elif "unchanged:" in line:
                    unchanged_count += 1
            all_reports.extend(reports)

    # Summary
    print("\n" + "=" * 60)
    print("SYNC REPORT")
    print("=" * 60)
    print(f"  Mode              : {'DRY RUN (no files written)' if dry_run else 'APPLIED (files written)'}")
    print(f"  Requirements scanned: {len(req_folders)}")
    print(f"  Tasks synced      : {synced_count}")
    print(f"  Tasks unchanged   : {unchanged_count}")

    if dry_run and synced_count > 0:
        print(
            "\nTo apply changes, re-run with --apply:\n"
            "  python3 scripts/sync_task_packages.py --apply"
        )

    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
