#!/usr/bin/env python3
"""Find and rewrite cross-references to doc/ files after a split.

Called by the doc-split skill during a split operation.

Usage:
    python3 scripts/update_doc_references.py --find <path>
    python3 scripts/update_doc_references.py --replace <old=new> [--replace <old2=new2> ...]

Output:
    --find:    prints one "<file>:<line>: <match>" per reference to stdout.
    --replace: prints a summary of files rewritten to stdout.

Exit codes:
    --find: 0 if no references found, 1 if any found
    --replace: 0 always
"""

# tier: C  # one-shot CLI artifact generator; no in-tree Python imports

import argparse
import glob as _glob
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class Deps:
    glob_files: Callable[[str], list[str]]   # glob.glob(pattern, recursive=True)
    read_file: Callable[[str], str]           # Path(p).read_text(encoding="utf-8")
    write_file: Callable[[str, str], None]    # Path(p).write_text(c, encoding="utf-8")
    file_exists: Callable[[str], bool]        # os.path.isfile


def make_real_deps() -> Deps:
    return Deps(
        glob_files=lambda p: _glob.glob(p, recursive=True),
        read_file=lambda p: Path(p).read_text(encoding="utf-8"),
        write_file=lambda p, c: (Path(p).write_text(c, encoding="utf-8"), None)[1],
        file_exists=os.path.isfile,
    )


def _is_excluded_requirements_path(path: str) -> bool:
    """Return True if any path component ends with '(completed)' or '(superseded)'."""
    parts = Path(path).parts
    for part in parts:
        if part.endswith("(completed)") or part.endswith("(superseded)"):
            return True
    return False


def _collect_in_scope_files(deps: Deps, exclude_path: str = "") -> list[str]:
    """Return all in-scope files for search/replace.

    In-scope locations:
    1. CLAUDE.md (project root)
    2. .claude/skills/**/*.md
    3. .claude/agents/**/*.md (if folder exists)
    4. doc/**/*.md (excluding the file being searched for itself)
    5. requirements_tasks/**/*.md (excluding (completed)/(superseded) folders)
    """
    files: list[str] = []

    # 1. CLAUDE.md
    claude_md = str(PROJECT_ROOT / "CLAUDE.md")
    if deps.file_exists(claude_md):
        files.append(claude_md)

    # 2. .claude/skills/**/*.md
    skills_pattern = str(PROJECT_ROOT / ".claude" / "skills" / "**" / "*.md")
    files.extend(deps.glob_files(skills_pattern))

    # 3. .claude/agents/**/*.md (if folder exists)
    agents_dir = str(PROJECT_ROOT / ".claude" / "agents")
    if deps.file_exists(agents_dir) or Path(agents_dir).is_dir():
        agents_pattern = str(PROJECT_ROOT / ".claude" / "agents" / "**" / "*.md")
        files.extend(deps.glob_files(agents_pattern))

    # 4. doc/**/*.md — exclude the file being searched for itself
    doc_pattern = str(PROJECT_ROOT / "doc" / "**" / "*.md")
    for f in deps.glob_files(doc_pattern):
        # Normalise paths for comparison so both absolute and relative forms match
        if exclude_path and Path(f).resolve() == Path(exclude_path).resolve():
            continue
        files.append(f)

    # 5. requirements_tasks/**/*.md — exclude (completed)/(superseded) folders
    req_pattern = str(PROJECT_ROOT / "requirements_tasks" / "**" / "*.md")
    for f in deps.glob_files(req_pattern):
        if _is_excluded_requirements_path(f):
            continue
        files.append(f)

    return files


def _extract_relative_path_candidates(line: str) -> list[str]:
    """Extract substrings from a line that look like relative file paths.

    Looks for tokens containing '../', './', or ending in '.md' adjacent to '/'.
    Returns a list of candidate path strings (may be empty).
    """
    import re
    # Match tokens that start with ./ or ../ or contain a bare word.md component
    # We look for sequences of non-whitespace non-quote chars that contain
    # '../' or './' or end with '.md' and contain a '/'
    pattern = re.compile(r'(?<!["\'\w])([./][\w./\-]+\.md|[\w\-]+/[\w./\-]+\.md)(?!["\'\w])')
    candidates = []
    for m in pattern.finditer(line):
        token = m.group(1)
        if "../" in token or token.startswith("./") or ("/" in token and token.endswith(".md")):
            candidates.append(token)
    return candidates


def find_references(deps: Deps, search_path: str) -> list[tuple[str, int, str]]:
    """Search all in-scope files for occurrences of search_path.

    Detects both exact string matches (e.g. 'doc/foo/bar.md') and relative-path
    references that resolve to the same file (e.g. '../foo/bar.md' from a sibling
    directory).

    Returns list of (file_path, line_number, line_content_stripped).
    The file at search_path itself is excluded from doc/ results.
    """
    # Resolve exclude_path to an absolute path so self-match works even when
    # search_path is given as a relative path (e.g. "doc/testing/foo.md")
    if Path(search_path).is_absolute():
        exclude_path = search_path
        target_abs = Path(search_path)
    else:
        exclude_path = str(PROJECT_ROOT / search_path)
        target_abs = PROJECT_ROOT / search_path

    # Normalise to string for comparison
    target_abs_str = str(target_abs)

    results: list[tuple[str, int, str]] = []
    in_scope = _collect_in_scope_files(deps, exclude_path=exclude_path)

    for file_path in in_scope:
        try:
            content = deps.read_file(file_path)
        except OSError:
            continue
        file_dir = Path(file_path).parent
        for line_no, line in enumerate(content.splitlines(), start=1):
            # Exact match (existing behaviour)
            if search_path in line:
                results.append((file_path, line_no, line.strip()))
                continue

            # Relative-path resolution check
            matched = False
            for candidate in _extract_relative_path_candidates(line):
                try:
                    resolved = str((file_dir / candidate).resolve())
                except Exception:
                    continue
                if resolved == target_abs_str:
                    matched = True
                    break
            if matched:
                results.append((file_path, line_no, line.strip()))

    return results


def _rewrite_line_relative_refs(
    line: str, file_path: str, replacements: list[tuple[str, str]]
) -> str:
    """Rewrite relative-path references in a single line.

    For each (old, new) replacement pair, resolve any relative-path candidate
    in the line relative to file_path's directory. If it resolves to the
    absolute path of 'old', replace the candidate token with the correct
    relative path from file_path's directory to 'new'.
    """
    file_dir = Path(file_path).parent
    result = line

    for old, new in replacements:
        # Resolve the 'old' target to absolute
        old_path = Path(old)
        old_abs = old_path if old_path.is_absolute() else PROJECT_ROOT / old_path

        old_abs_str = str(old_abs)

        # Resolve the 'new' target to absolute
        new_path = Path(new)
        new_abs = new_path if new_path.is_absolute() else PROJECT_ROOT / new_path

        # Find all relative-path candidates in the current (possibly already
        # partially rewritten) result line and replace matching ones.
        for candidate in _extract_relative_path_candidates(result):
            try:
                resolved = str((file_dir / candidate).resolve())
            except Exception:
                continue
            if resolved == old_abs_str:
                # Compute the correct relative path from the referring file's
                # directory to the new target.
                try:
                    rel_new = os.path.relpath(str(new_abs), str(file_dir))
                    # Ensure it uses forward slashes (portable in Markdown)
                    rel_new = rel_new.replace(os.sep, "/")
                    if not rel_new.startswith("."):
                        rel_new = "./" + rel_new
                except ValueError:
                    # On Windows, relpath can fail across drives; fall back to absolute form
                    rel_new = new
                result = result.replace(candidate, rel_new, 1)

    return result


def replace_references(
    deps: Deps, replacements: list[tuple[str, str]]
) -> list[str]:
    """Apply string replacements across all in-scope files.

    Each element of replacements is an (old, new) pair.
    Handles both exact string matches and relative-path references that resolve
    to the old target — rewriting them to the correct relative path to the new
    target.
    Returns list of file paths that were modified.
    """
    in_scope = _collect_in_scope_files(deps)
    modified: list[str] = []

    for file_path in in_scope:
        try:
            content = deps.read_file(file_path)
        except OSError:
            continue

        new_content = content

        # Pass 1: exact string replacements (existing behaviour)
        for old, new in replacements:
            new_content = new_content.replace(old, new)

        # Pass 2: relative-path replacements for any lines that still contain
        # a relative reference to one of the old targets (i.e. the exact match
        # didn't fire because the line used a relative path form).
        lines = new_content.splitlines(keepends=True)
        rewritten_lines = []
        for line in lines:
            rewritten_lines.append(_rewrite_line_relative_refs(line, file_path, replacements))
        new_content = "".join(rewritten_lines)

        if new_content != content:
            deps.write_file(file_path, new_content)
            modified.append(file_path)

    return modified


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find and rewrite cross-references to doc/ files after a split."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--find",
        metavar="PATH",
        help="Search for all references to PATH in in-scope locations.",
    )
    group.add_argument(
        "--replace",
        metavar="OLD=NEW",
        action="append",
        dest="replacements",
        help="Replace OLD with NEW in all in-scope files. Repeatable.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    deps = make_real_deps()

    if args.find:
        matches = find_references(deps, args.find)
        for file_path, line_no, context in matches:
            print(f"{file_path}:{line_no}: {context}")
        sys.exit(1 if matches else 0)

    else:
        # --replace mode
        pairs: list[tuple[str, str]] = []
        for raw in args.replacements:
            if "=" not in raw:
                print(f"ERROR: --replace value must be in OLD=NEW format, got: {raw}", file=sys.stderr)
                sys.exit(2)
            old, new = raw.split("=", 1)
            pairs.append((old, new))

        modified = replace_references(deps, pairs)
        for file_path in modified:
            print(f"Updated: {file_path}")
        sys.exit(0)


if __name__ == "__main__":
    main()
