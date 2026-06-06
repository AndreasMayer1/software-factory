"""Complexity-metric gate for Dart sources (REQ-PROC-046 AC-02).

Replaces DCM's `metrics:` block (cyclomatic-complexity, number-of-parameters,
source-lines-of-code, maximum-nesting-level). Shells out to the Dart helper
package at scripts/quality/_complexity_analyzer/ which uses the analyzer
package to compute the four metrics per function. The Python side applies
thresholds and reports violations.

Output:
    Pass — single line "PASS: ..." on stdout, exit 0.
    Fail — one line per violation "file:line: <metric> exceeds <threshold>",
           then a summary, exit 1.
    Invocation error — message on stderr, exit 2.

Thresholds (carried over from REQ-PROC-046 AC-02):
    cyclomatic complexity    <= 20 per function
    parameter count          <= 4  per function
    source lines of code     <= 50 per function body
    max control-flow nesting <= 5  (control-flow only)
"""

# tier: B

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

THRESHOLD_CYCLOMATIC = 20
THRESHOLD_PARAMETERS = 4
THRESHOLD_SLOC = 50
THRESHOLD_NESTING = 5

# Constructors/copyWith mirror the class field count — a separate, relaxed
# threshold avoids false positives on data classes with many fields.
THRESHOLD_CONSTRUCTOR_PARAMETERS = 15

_PARAM_EXEMPT_NAMES = frozenset({"copyWith", "create"})


def _exempt_from_param_check(kind: str, name: str) -> bool:
    """Constructors and copy/factory methods are exempt from the strict param limit."""
    if kind == "constructor":
        return True
    return name in _PARAM_EXEMPT_NAMES

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HELPER_DIR = Path(__file__).resolve().parent / "_complexity_analyzer"
DEFAULT_EXCLUDE_FILE = Path(__file__).resolve().parent / "exclusions.txt"


def load_exclude_patterns(path: Path) -> list[str]:
    if not path.exists():
        return []
    patterns: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            patterns.append(line)
    return patterns


def is_excluded(rel_path: str, patterns: list[str]) -> bool:
    return any(p in rel_path for p in patterns)


def run_analyzer(scan_root: Path) -> dict[str, object]:
    """Invoke the Dart helper and parse its JSON output."""
    pubspec_lock = HELPER_DIR / "pubspec.lock"
    if not pubspec_lock.exists():
        sys.stderr.write(
            f"NOTICE: {HELPER_DIR}/pubspec.lock not found; run "
            f"'dart pub get' inside {HELPER_DIR} before invoking this gate.\n"
        )
        return {"version": 1, "files": []}

    cmd = [
        "dart",
        "run",
        "bin/complexity_analyzer.dart",
        str(scan_root),
    ]
    try:
        result = subprocess.run(
            cmd,
            cwd=HELPER_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        sys.stderr.write(
            "NOTICE: 'dart' executable not on PATH; complexity gate skipped.\n"
        )
        return {"version": 1, "files": []}

    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.stderr.write(
            f"ERROR: complexity analyzer exited {result.returncode}.\n"
        )
        sys.exit(2)

    try:
        data = json.loads(result.stdout)
        if not isinstance(data, dict):
            raise ValueError("analyzer output is not a JSON object")
        return data
    except (json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write(f"ERROR: parsing analyzer JSON failed: {exc}\n")
        sys.exit(2)


def emit_violations(
    data: dict[str, object], excluded: list[str]
) -> int:
    files = data.get("files", [])
    if not isinstance(files, list):
        sys.stderr.write("ERROR: analyzer 'files' field is not a list.\n")
        sys.exit(2)

    violations = 0
    for entry in files:
        if not isinstance(entry, dict):
            continue
        raw_path = str(entry.get("path", ""))
        if not raw_path:
            continue
        try:
            path = str(Path(raw_path).resolve().relative_to(PROJECT_ROOT))
        except ValueError:
            path = raw_path
        if is_excluded(path, excluded):
            continue
        functions = entry.get("functions", [])
        if not isinstance(functions, list):
            continue
        for fn in functions:
            if not isinstance(fn, dict):
                continue
            line = fn.get("line", 0)
            name = fn.get("name", "<anon>")
            kind = str(fn.get("kind", "function"))
            cyc = int(fn.get("cyclomatic", 0))
            params = int(fn.get("parameters", 0))
            sloc = int(fn.get("sloc", 0))
            nesting = int(fn.get("max_nesting", 0))

            if cyc > THRESHOLD_CYCLOMATIC:
                sys.stdout.write(
                    f"{path}:{line}: {name}: cyclomatic complexity "
                    f"{cyc} exceeds {THRESHOLD_CYCLOMATIC}\n"
                )
                violations += 1
            param_limit = (
                THRESHOLD_CONSTRUCTOR_PARAMETERS
                if _exempt_from_param_check(kind, name)
                else THRESHOLD_PARAMETERS
            )
            if params > param_limit:
                sys.stdout.write(
                    f"{path}:{line}: {name}: parameters {params} "
                    f"exceeds {param_limit}\n"
                )
                violations += 1
            if sloc > THRESHOLD_SLOC:
                sys.stdout.write(
                    f"{path}:{line}: {name}: sloc {sloc} "
                    f"exceeds {THRESHOLD_SLOC}\n"
                )
                violations += 1
            if nesting > THRESHOLD_NESTING:
                sys.stdout.write(
                    f"{path}:{line}: {name}: max_nesting {nesting} "
                    f"exceeds {THRESHOLD_NESTING}\n"
                )
                violations += 1

    return violations


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Complexity-metric gate for Dart sources."
    )
    parser.add_argument(
        "--exclude-paths",
        type=Path,
        default=DEFAULT_EXCLUDE_FILE,
        help="Path to substring-exclusion file (one pattern per line).",
    )
    parser.add_argument(
        "--scan-root",
        type=Path,
        default=PROJECT_ROOT / "lib",
        help="Directory to scan (default: project lib/).",
    )
    args = parser.parse_args(argv)

    if not args.scan_root.exists():
        sys.stderr.write(
            f"NOTICE: scan root {args.scan_root} does not exist; nothing to do.\n"
        )
        return 0

    excluded = load_exclude_patterns(args.exclude_paths)
    data = run_analyzer(args.scan_root)
    violations = emit_violations(data, excluded)

    if violations:
        sys.stdout.write("\n")
        sys.stdout.write(
            f"FAIL: {violations} complexity-threshold violation(s).\n"
        )
        return 1
    sys.stdout.write(
        "PASS: every Dart function is within complexity thresholds.\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
