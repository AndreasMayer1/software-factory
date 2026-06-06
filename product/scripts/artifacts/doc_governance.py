#!/usr/bin/env python3
"""doc_governance.py — Post-write enforcement for doc/ file size limits.

Scans in-scope doc/ folders for files ≥ 600 lines and creates a generic
split task if needed (unless a pending split task already exists).

Usage:
    python3 scripts/doc_governance.py                 # default: scan + create task
    python3 scripts/doc_governance.py --list-violations
    python3 scripts/doc_governance.py --check
    python3 scripts/doc_governance.py --check-depth
    python3 scripts/doc_governance.py --dry-run

Output:
    Default / --dry-run: prints scan status, any created/skipped tasks,
    and a one-line summary on stdout.
    --list-violations / --check / --check-depth: prints one
    "<path>: <message>" line per violation on stdout; nothing on pass.

Exit codes (default / --dry-run):
    0  always

Exit codes (--list-violations):
    0  no violations
    1  violations found

Exit codes (--check / --check-depth):
    0  no violations
    1  violations found
"""

# tier: C  # one-shot CLI artifact generator; no in-tree Python imports

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent

# In-scope root folders relative to PROJECT_ROOT
_IN_SCOPE_ROOTS = [
    "doc/architecture",
    "doc/domain",
    "doc/testing",
    "doc/presentation",
    "doc/cross_cutting_standards",
    "doc/linter",
]

# Excluded roots (never scan)
_EXCLUDED_ROOTS = [
    "doc/from_figma",
    "doc/general",
]

_SIZE_LIMIT = 600

_REQ_PATH = "requirements_tasks/process/documentation_rules/guideline_file_organization"
_REQ_ID = "REQ-PROC-048"
_TASK_FOLDER_PATTERN = "*_impl_split-oversized-doc-files*"


@dataclass
class Deps:
    list_files: Callable[[str], list[str]]
    """Return all file paths (recursively) under a given directory path string."""
    count_lines: Callable[[str], int]
    """Return the number of lines in a file given its path string."""
    glob_dirs: Callable[[str], list[str]]
    """Glob for directory names matching a pattern (for dedup check)."""
    read_file: Callable[[str], str]
    """Read a file by path string and return its contents."""
    makedirs: Callable[[str], None]
    """Create directories recursively (like os.makedirs exist_ok=True)."""
    write_file: Callable[[str, str], None]
    """Write content to a file path."""
    run_subprocess: Callable[..., "subprocess.CompletedProcess[str]"]
    """Run a subprocess and return its CompletedProcess."""
    get_today: Callable[[], str]
    """Return today's date as ISO string (YYYY-MM-DD)."""


def make_real_deps() -> Deps:
    def _list_files(root: str) -> list[str]:
        result = []
        for dirpath, _dirnames, filenames in os.walk(root):
            for fname in filenames:
                result.append(os.path.join(dirpath, fname))
        return result

    def _count_lines(path: str) -> int:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                return sum(1 for _ in f)
        except OSError:
            return 0

    return Deps(
        list_files=_list_files,
        count_lines=_count_lines,
        glob_dirs=lambda p: [
            str(d)
            for d in Path(p).parent.glob(Path(p).name)
            if d.is_dir()
        ],
        read_file=lambda p: Path(p).read_text(encoding="utf-8"),
        makedirs=lambda p: os.makedirs(p, exist_ok=True),
        write_file=lambda p, c: (Path(p).write_text(c, encoding="utf-8"), None)[1],
        run_subprocess=lambda cmd, **kw: subprocess.run(
            cmd, capture_output=True, text=True, **kw
        ),
        get_today=lambda: date.today().isoformat(),
    )


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def _is_excluded(path: str) -> bool:
    """Return True if the path falls under an excluded root or is a README.md."""
    p = Path(path)
    if p.name == "README.md":
        return True
    # Normalise to relative path from project root if possible
    try:
        rel = str(p.relative_to(PROJECT_ROOT))
    except ValueError:
        rel = str(p)
    for excl in _EXCLUDED_ROOTS:
        if rel.startswith(excl + os.sep) or rel.startswith(excl + "/"):
            return True
    return False


def _depth_violation(path: str) -> bool:
    """Return True if the path is deeper than doc/[X]/[Y]/file.md.

    A path is "too deep" if the number of components between doc/ and the
    filename is >= 3 (i.e. doc/a/b/c/file.md has depth 3 → violation).

    Why: REQ-PROC-048 AC-06 mandates no path deeper than doc/[level1]/[level2]/file.md.
    """
    try:
        rel = Path(path).relative_to(PROJECT_ROOT / "doc")
    except ValueError:
        try:
            rel = Path(path).relative_to(Path("doc"))
        except ValueError:
            return False
    # parts: e.g. ('testing', 'file.md') → depth 1 → OK
    #        ('testing', 'sub', 'file.md') → depth 2 → OK
    #        ('testing', 'sub', 'deep', 'file.md') → depth 3 → VIOLATION
    return len(rel.parts) - 1 >= 3


def scan_violations(deps: Deps) -> list[tuple[str, int]]:
    """Return list of (path, linecount) for in-scope files with >= 600 lines."""
    violations: list[tuple[str, int]] = []
    for root in _IN_SCOPE_ROOTS:
        root_path = str(PROJECT_ROOT / root)
        try:
            files = deps.list_files(root_path)
        except OSError:
            continue
        for fpath in files:
            if _is_excluded(fpath):
                continue
            lines = deps.count_lines(fpath)
            if lines >= _SIZE_LIMIT:
                violations.append((fpath, lines))
    return violations


def scan_depth_violations(deps: Deps) -> list[str]:
    """Return list of paths that violate the depth constraint."""
    violations: list[str] = []
    for root in _IN_SCOPE_ROOTS:
        root_path = str(PROJECT_ROOT / root)
        try:
            files = deps.list_files(root_path)
        except OSError:
            continue
        for fpath in files:
            if _is_excluded(fpath):
                continue
            if _depth_violation(fpath):
                violations.append(fpath)
    return violations


# ---------------------------------------------------------------------------
# Dedup: find pending split task
# ---------------------------------------------------------------------------

def find_pending_split_task(deps: Deps) -> Optional[str]:
    """Return the path of a pending split task, or None."""
    tasks_dir = str(PROJECT_ROOT / _REQ_PATH / "tasks")
    pattern = os.path.join(tasks_dir, _TASK_FOLDER_PATTERN)
    for folder in deps.glob_dirs(pattern):
        goal_path = os.path.join(folder, "goal.md")
        try:
            content = deps.read_file(goal_path)
        except OSError:
            continue
        import re
        m = re.search(r"^status:\s*(\S+)", content, re.MULTILINE)
        # Why: only a pending task blocks creation — a task already in_progress is
        # handling its batch of ≤3 files. When the governance script is called again
        # during that run, it should queue the remaining violations as a NEW task so
        # work can continue in a fresh session without context-window pressure.
        if m and m.group(1).strip() == "pending":
            return goal_path
    return None


# ---------------------------------------------------------------------------
# Task creation
# ---------------------------------------------------------------------------

_GOAL_TEMPLATE = """\
---
task_id: {task_id}
type: impl
parent_requirement: REQ-PROC-048
urgency: 3
urgency_reason: U3-QUAL
impact: 4
impact_reason: I4-MAINT
status: pending
effort: M
created: {date}
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria:
    - AC-01
    - AC-02
    - AC-03
    - AC-05
    - AC-06
  sections: []
scope_description: "Split oversized doc/ guideline files to restore AC-01 compliance"
release_description: ""
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
---

# Goal: Split Oversized doc/ Guideline Files

## Steps

1. List violations:
   ```bash
   python3 scripts/doc_governance.py --list-violations
   ```
2. Use the `doc-split` skill individually on the first 3 files with violations — **max 3 files**.
3. After all splits are done, run:
   ```bash
   python3 scripts/doc_governance.py
   ```
   This queues a follow-up task for any remaining violations. **Run this before `task-complete` every time, regardless of how many files were processed.**
4. Invoke `task-complete`.

## Acceptance Criteria

- [ ] AC-01: No file in the in-scope `doc/` folders exceeds 600 lines
- [ ] AC-02: After each split, parent README mentions output files/subfolder by name
- [ ] AC-03: New subfolders from splits have a README per REQ-PROC-026 §4.5
- [ ] AC-05: No reference to any deleted source file path remains in CLAUDE.md, .claude/skills/, .claude/agents/, doc/, or active requirements_tasks/
- [ ] AC-06: No path deeper than doc/[level1]/[level2]/file.md produced by a split
- [ ] `python3 scripts/doc_governance.py` was called after all splits and before `task-complete`
"""


def create_split_task(deps: Deps, dry_run: bool = False) -> str:
    """Allocate a task ID, create folder + goal.md. Returns task folder path."""
    # Allocate task ID via allocate_task_id.py
    result = deps.run_subprocess(
        [
            sys.executable,
            "scripts/allocate_task_id.py",
            "--req-id", _REQ_ID,
            "--req-path", _REQ_PATH,
        ],
        cwd=str(PROJECT_ROOT),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"allocate_task_id.py failed (exit {result.returncode}): {result.stderr}"
        )

    task_id = result.stdout.strip()
    today = deps.get_today()
    tasks_root = PROJECT_ROOT / _REQ_PATH / "tasks"

    # Find a unique folder name: the base name may already exist if this is the
    # second (or later) split task created on the same calendar day.
    base_name = f"{today}_impl_split-oversized-doc-files"
    task_folder = str(tasks_root / base_name)
    counter = 2
    while os.path.exists(task_folder):
        task_folder = str(tasks_root / f"{base_name}-{counter}")
        counter += 1

    protocols_folder = os.path.join(task_folder, "plans_and_protocols")
    goal_path = os.path.join(task_folder, "goal.md")
    reserve_path = str(tasks_root / f".reserve-{task_id}")

    if not dry_run:
        deps.makedirs(protocols_folder)
        deps.write_file(goal_path, _GOAL_TEMPLATE.format(task_id=task_id, date=today))
        # Remove the reserve marker now that goal.md is written, consistent with
        # how task-create skill handles it (reserve file is only needed inside the
        # allocate_task_id lock to prevent concurrent ID collisions).
        if os.path.exists(reserve_path):
            os.remove(reserve_path)

    return task_folder


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enforce doc/ file size limits and create split tasks."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--list-violations",
        action="store_true",
        help="Print in-scope files >= 600 lines (path:linecount). Exit 1 if any.",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Exit 0 if no violations, exit 1 if any. Print nothing.",
    )
    mode.add_argument(
        "--check-depth",
        action="store_true",
        help="Like --check but also enforces depth constraint. Exit 1 if any violation.",
    )
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Run default mode but do not create files; print what would happen.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run(deps: Deps, args: argparse.Namespace) -> int:
    """Execute the requested mode. Returns exit code."""

    if args.check:
        violations = scan_violations(deps)
        return 1 if violations else 0

    if args.check_depth:
        violations = scan_violations(deps)
        depth_violations = scan_depth_violations(deps)
        return 1 if (violations or depth_violations) else 0

    if args.list_violations:
        violations = scan_violations(deps)
        for path, count in violations:
            # Print relative to project root when possible, else absolute
            try:
                rel = Path(path).relative_to(PROJECT_ROOT)
                print(f"{rel}:{count}")
            except ValueError:
                print(f"{path}:{count}")
        return 1 if violations else 0

    # Default mode (with or without --dry-run)
    dry_run = args.dry_run
    violations = scan_violations(deps)

    if violations:
        print("Violations found (path:linecount):")
        for path, count in violations:
            try:
                rel = Path(path).relative_to(PROJECT_ROOT)
                print(f"  {rel}:{count}")
            except ValueError:
                print(f"  {path}:{count}")

        # Dedup check
        pending = find_pending_split_task(deps)
        if pending:
            try:
                rel = Path(pending).relative_to(PROJECT_ROOT)
            except ValueError:
                rel = Path(pending)
            print(f"no new task — pending task exists at {rel}")
        else:
            task_folder = create_split_task(deps, dry_run=dry_run)
            try:
                rel_folder = Path(task_folder).relative_to(PROJECT_ROOT)
            except ValueError:
                rel_folder = Path(task_folder)
            if dry_run:
                print(f"Would create split task: {rel_folder}")
            else:
                print(f"Created split task: {rel_folder}")
    else:
        print("No violations found.")

    return 0


def main() -> None:
    args = parse_args()
    sys.exit(run(make_real_deps(), args))


if __name__ == "__main__":
    main()
