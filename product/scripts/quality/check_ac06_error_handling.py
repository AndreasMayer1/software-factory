"""AC-06 error-handling gate for Dart sources (REQ-PROC-046 AC-06).

Belt-and-suspenders companion to G1 (flutter analyze). The very_good_analysis
baseline already enforces these patterns via unawaited_futures, only_throw_errors,
and avoid_catches_without_on_clauses (info-level). This script provides a named
gate entry in the runner summary so violations are visibly labelled AC-06.

Two checks:
  1. Bare catch — catch ( without an `on Type` guard on the same or immediately
     preceding non-blank line. Mental-health data must never be silently swallowed.
  2. Literal throw — throw of a string, number, null, true, or false. These lose
     stack-trace context and are always wrong in production code.

Scope: lib/ .dart files, excluding generated (*.g.dart, *.freezed.dart,
/generated/ directories) and any paths in the exclusions file.

Baseline suppression (--baseline FILE):
  Pre-existing violations are recorded in the baseline file (one "path:lineno"
  per line). The gate suppresses violations whose "path:lineno" is listed there
  and only fails on NEW violations not in the baseline. Run with --dump-baseline
  to emit the current violation list to stdout (redirect to update the file).

Output:
    Pass  — single "PASS: ..." line on stdout, exit 0.
    Fail  — one "path:lineno: <description>" line per NEW violation, then a
             summary "FAIL: ..." line, exit 1.
    Error — message on stderr, exit 2.
"""

# tier: B

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Bare catch: `catch (` not preceded by `on <Identifier>` on the same line.
_RE_CATCH = re.compile(r"\bcatch\s*\(")
_RE_ON_GUARD = re.compile(r"\bon\s+[A-Z_$]")

# Literal throws that bypass the Error/Exception hierarchy.
_RE_THROW_STRING = re.compile(r"\bthrow\s+r?[\"']")
_RE_THROW_NULL = re.compile(r"\bthrow\s+null\b")
_RE_THROW_BOOL = re.compile(r"\bthrow\s+(true|false)\b")
_RE_THROW_INT = re.compile(r"\bthrow\s+-?\d+\b")

# ---------------------------------------------------------------------------
# Exclusions (mirrors _lib.sh `is_excluded` logic: substring match)
# ---------------------------------------------------------------------------

_DEFAULT_EXCLUSIONS = Path(__file__).parent / "exclusions.txt"


def _load_exclusions(path: Path) -> list[str]:
    if not path.exists():
        return []
    patterns: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.split("#")[0].strip()
        if stripped:
            patterns.append(stripped)
    return patterns


def _is_excluded(rel: str, patterns: list[str]) -> bool:
    return any(pat in rel for pat in patterns)


# ---------------------------------------------------------------------------
# Baseline suppression
# ---------------------------------------------------------------------------

def _load_baseline(path: Path) -> set[str]:
    """Return set of 'filepath:lineno' keys that are pre-approved violations."""
    if not path.exists():
        return set()
    result: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.split("#")[0].strip()
        if stripped:
            result.add(stripped)
    return result


# ---------------------------------------------------------------------------
# Per-file analysis
# ---------------------------------------------------------------------------

def _is_generated(path: Path) -> bool:
    name = path.name
    if name.endswith(".g.dart") or name.endswith(".freezed.dart"):
        return True
    return "/generated/" in path.as_posix()


def check_file(path: Path, rel: str) -> list[tuple[int, str]]:
    """Return list of (lineno, description) violations for a single file."""
    violations: list[tuple[int, str]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return violations

    prev_nonblank = ""
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        # --- Check 1: bare catch ----------------------------------------
        # Accept if same line has `on <UppercaseType>`, or if the immediately
        # preceding non-blank line has the guard (multi-line `on Type\n  catch`).
        if (
            _RE_CATCH.search(stripped)
            and not _RE_ON_GUARD.search(stripped)
            and not _RE_ON_GUARD.search(prev_nonblank)
        ):
            violations.append((i, "bare catch without 'on Type' guard (AC-06)"))

        # --- Check 2: literal throws ------------------------------------
        if (
            (
                _RE_THROW_STRING.search(stripped)
                or _RE_THROW_NULL.search(stripped)
                or _RE_THROW_BOOL.search(stripped)
                or _RE_THROW_INT.search(stripped)
            )
            and not stripped.startswith("//")
        ):
            violations.append((i, "throw of non-Error/non-Exception value (AC-06)"))

        if stripped:
            prev_nonblank = stripped

    return violations


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="REQ-PROC-046 AC-06 error-handling gate for Dart sources."
    )
    parser.add_argument(
        "--exclude-paths",
        metavar="FILE",
        default=str(_DEFAULT_EXCLUSIONS),
        help="Path to exclusions file (default: scripts/quality/exclusions.txt)",
    )
    parser.add_argument(
        "--baseline",
        metavar="FILE",
        default="",
        help="Path to baseline file of pre-existing violations (path:lineno per line). "
             "Suppresses listed violations; fails only on new ones.",
    )
    parser.add_argument(
        "--dump-baseline",
        action="store_true",
        help="Print current violations as baseline format (path:lineno) and exit 0.",
    )
    args = parser.parse_args(argv)

    project_root = Path(__file__).parent.parent.parent
    lib_dir = project_root / "lib"

    if not lib_dir.is_dir():
        print(f"ERROR: lib/ not found at {lib_dir}", file=sys.stderr)
        return 2

    exclusions = _load_exclusions(Path(args.exclude_paths))
    baseline = _load_baseline(Path(args.baseline)) if args.baseline else set()

    all_violations: list[tuple[str, int, str]] = []

    for dart_file in sorted(lib_dir.rglob("*.dart")):
        if _is_generated(dart_file):
            continue
        rel = str(dart_file.relative_to(project_root))
        if _is_excluded(rel, exclusions):
            continue
        for lineno, desc in check_file(dart_file, rel):
            all_violations.append((rel, lineno, desc))

    if args.dump_baseline:
        for rel, lineno, _ in all_violations:
            print(f"{rel}:{lineno}")
        return 0

    # Filter out baseline-suppressed violations.
    new_violations = [
        (rel, lineno, desc)
        for rel, lineno, desc in all_violations
        if f"{rel}:{lineno}" not in baseline
    ]
    suppressed = len(all_violations) - len(new_violations)

    if new_violations:
        for rel, lineno, desc in new_violations:
            print(f"{rel}:{lineno}: {desc}")
        print()
        if suppressed:
            print(f"  ({suppressed} pre-existing baseline violation(s) suppressed)")
        print(
            f"FAIL: REQ-PROC-046 AC-06 (error-handling discipline) — "
            f"{len(new_violations)} new finding(s)"
        )
        return 1

    if suppressed:
        print(
            f"PASS: REQ-PROC-046 AC-06 (error-handling discipline) — "
            f"0 new findings ({suppressed} pre-existing suppressed; fix to shrink baseline)"
        )
    else:
        print(
            "PASS: REQ-PROC-046 AC-06 (error-handling discipline) — "
            "0 findings in lib/"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
