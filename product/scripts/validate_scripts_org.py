#!/usr/bin/env python3
"""Lint script for scripts/ folder organization (REQ-PROC-043).

Default mode: validates scripts found inside domain subfolders only.
Passes on the pre-refactor flat state because domain folders are empty/absent.

--strict mode: additionally enforces that no flat top-level scripts exist
and that all required domain folders are present. Use after TASK-PROC-043-03.

Output:
    Prints one '<path>: <violation>' line per misplaced script to stdout, ending with a PASS/FAIL summary.
"""

# tier: C  # one-shot CLI structural-lint script; only test imports check_domain_folders helper

import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CLAUDE_MD = os.path.join(PROJECT_ROOT, "CLAUDE.md")

DOMAIN_FOLDERS = [
    "tasks",
    "requirements",
    "artifacts",
    "user_needs",
    "release",
    "util",
    "windows",
]

PRESERVED_SUBSYSTEMS = [
    "automation",
    "task_ordering",
    "integration_test_runner",
    "tests",
]

# verb prefixes → lifecycle bucket (order matters: longer matches first)
_READ_ONLY_VERBS = [
    "check_", "find_", "is_", "list_", "next_", "top_", "propose_", "validate_",
    "goal_preview", "should_", "release_readiness", "summarize_", "parse_",
    "coverage_",
]
_FILE_GEN_VERBS = [
    "generate_", "aggregate_", "merge_", "process_",
]
_STATE_MOD_VERBS = [
    "allocate_", "sync_", "complete_", "execute_", "reconcile_",
    "create_", "migrate_", "update_", "sleep_", "smoke_", "doc_",
    "win_",
]

_KNOWN_VERBS = _READ_ONLY_VERBS + _FILE_GEN_VERBS + _STATE_MOD_VERBS

_SCRIPT_PATTERN = re.compile(r"^[a-z][a-z0-9_]*\.(py|ps1|dart|sh)$")
_SCRIPT_EXTS = {".py", ".ps1", ".dart", ".sh"}

# Matches script paths referenced in CLAUDE.md (e.g. `scripts/foo.py` or scripts/tasks/bar.py)
_CLAUDE_MD_PATH_RE = re.compile(r"\bscripts/[a-zA-Z0-9_/\-]+\.[a-zA-Z0-9]+")


def _script_files_in(folder: str) -> list[str]:
    """Return all script files (by extension) directly inside folder (non-recursive)."""
    if not os.path.isdir(folder):
        return []
    return [
        f for f in os.listdir(folder)
        if os.path.splitext(f)[1] in _SCRIPT_EXTS and not f.startswith(".")
    ]


def _classify_verb(name: str) -> str | None:
    """Return lifecycle bucket for script name, or None if unknown."""
    stem = os.path.splitext(name)[0]
    for verb in _KNOWN_VERBS:
        if stem.startswith(verb) or stem == verb.rstrip("_"):
            if verb in _READ_ONLY_VERBS:
                return "read-only"
            if verb in _FILE_GEN_VERBS:
                return "file-generating"
            return "state-modifying"
    return None


_PESTER_PATTERN = re.compile(r"^[a-z][a-z0-9_]*\.Tests\.ps1$")


def _check_naming(name: str) -> bool:
    # Allow Pester test files (*.Tests.ps1) — Windows test framework naming convention
    if _PESTER_PATTERN.match(name):
        return True
    return bool(_SCRIPT_PATTERN.match(name))


def _check_windows_isolation(folder_name: str, filename: str) -> bool:
    """Returns True (ok) when .ps1 is only in windows/ or integration_test_runner/."""
    if filename.endswith(".ps1"):
        return folder_name in ("windows", "integration_test_runner")
    return True


def _check_claude_md_paths(errors: list[str]) -> None:
    if not os.path.isfile(CLAUDE_MD):
        errors.append(f"CLAUDE.md not found at {CLAUDE_MD}")
        return
    with open(CLAUDE_MD, encoding="utf-8") as fh:
        content = fh.read()
    for match in _CLAUDE_MD_PATH_RE.finditer(content):
        rel = match.group(0)
        abs_path = os.path.join(PROJECT_ROOT, rel)
        if not os.path.exists(abs_path):
            errors.append(f"CLAUDE.md references missing path: {rel}")


def validate(strict: bool = False) -> tuple[list[str], list[str]]:
    """Run all checks. Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if strict:
        # Check no flat top-level scripts (except validate_scripts_org.py itself)
        for entry in os.listdir(SCRIPT_DIR):
            if os.path.splitext(entry)[1] in _SCRIPT_EXTS and entry != "validate_scripts_org.py":
                errors.append(f"Flat top-level script not allowed: scripts/{entry}")

        # Check all domain folders present
        for folder in DOMAIN_FOLDERS:
            path = os.path.join(SCRIPT_DIR, folder)
            if not os.path.isdir(path):
                errors.append(f"Required domain folder missing: scripts/{folder}/")

    # Check scripts inside domain folders
    for folder in DOMAIN_FOLDERS:
        folder_path = os.path.join(SCRIPT_DIR, folder)
        for filename in _script_files_in(folder_path):
            # __init__.py is a Python package marker, not a script — exempt globally.
            if filename == "__init__.py":
                continue

            # Pester test files (*.Tests.ps1) are Windows test framework artifacts;
            # exempt from naming/verb rules since their names follow Pester convention.
            if _PESTER_PATTERN.match(filename):
                continue

            # Naming format
            if not _check_naming(filename):
                errors.append(
                    f"Naming violation in scripts/{folder}/{filename}: "
                    f"must match ^[a-z][a-z0-9_]*\\.(py|ps1|dart|sh)$"
                )

            # Verb-lifecycle consistency.
            # util/ holds shared library modules that are imported, not invoked,
            # so noun-form module names are valid there (yaml_frontmatter.py etc.).
            if folder != "util":
                lifecycle = _classify_verb(filename)
                if lifecycle is None:
                    errors.append(
                        f"Unknown verb prefix in scripts/{folder}/{filename}: "
                        f"cannot classify lifecycle"
                    )

            # Windows isolation
            if not _check_windows_isolation(folder, filename):
                errors.append(
                    f"Windows isolation violation: scripts/{folder}/{filename} "
                    f"(.ps1 only allowed in windows/ or integration_test_runner/)"
                )

    # util/ size gate (warning only)
    util_path = os.path.join(SCRIPT_DIR, "util")
    if os.path.isdir(util_path):
        util_count = len(_script_files_in(util_path))
        if util_count > 5:
            warnings.append(
                f"util/ contains {util_count} scripts (>5). "
                f"Re-evaluate domain placement for the excess."
            )

    # CLAUDE.md path accuracy
    _check_claude_md_paths(errors)

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate scripts/ folder organization (REQ-PROC-043)."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Also enforce: no flat top-level scripts and all domain folders present. "
            "Use after TASK-PROC-043-03 (the refactor) is complete."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Alias for running the check (default behavior, provided for explicit invocation).",
    )
    args = parser.parse_args()

    errors, warnings = validate(strict=args.strict)

    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"\n{len(errors)} violation(s) found.")
        return 1

    if warnings:
        print(f"\nOK (with {len(warnings)} warning(s)).")
    else:
        print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
