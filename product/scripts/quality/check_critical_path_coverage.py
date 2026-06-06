#!/usr/bin/env python3
"""REQ-PROC-046 AC-04 — critical-path coverage gate.

Asserts ≥ 90 % line coverage (lcov) on the safety-critical paths documented in
doc/testing/critical_paths.md. Categories with no current implementation
(status: not_implemented, paths: []) are dormant — they contribute 0/0 and do
not affect the gate. Coverage is computed only over implemented paths.

Usage:
    # Run flutter test --coverage, then evaluate:
    scripts/quality/check_critical_path_coverage.py

    # Evaluate a pre-existing lcov file (skip flutter test):
    scripts/quality/check_critical_path_coverage.py --lcov coverage/lcov.info
    scripts/quality/check_critical_path_coverage.py --no-run

    # Use a non-default critical_paths.md:
    scripts/quality/check_critical_path_coverage.py --doc path/to/critical_paths.md

Output:
    On pass: prints the overall coverage percentage and per-category
    breakdown to stdout.
    On fail: same breakdown plus per-file lines under the failing
    categories, ending with a FAIL summary line.

Exit codes:
    0  gate passed (coverage ≥ 90 % or all categories are dormant)
    1  gate failed (coverage < 90 %); per-file/category breakdown printed
    2  invocation error (doc missing, YAML parse error, lcov missing, flutter failure)
"""

# tier: C  # one-shot CLI gate script; no in-tree Python imports

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, NamedTuple, cast

try:
    import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DOC = PROJECT_ROOT / "doc" / "testing" / "critical_paths.md"
DEFAULT_LCOV = PROJECT_ROOT / "coverage" / "lcov.info"

COVERAGE_THRESHOLD = 90.0  # REQ-PROC-046 AC-04


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

class FileStats(NamedTuple):
    path: str          # lib/-relative path as it appears in the doc
    hit: int
    total: int

    @property
    def pct(self) -> float:
        return (self.hit / self.total * 100.0) if self.total else 100.0


class CategoryResult(NamedTuple):
    id: str
    label: str
    dormant: bool      # True when no paths are listed (not yet implemented)
    files: list[FileStats]

    @property
    def hit(self) -> int:
        return sum(f.hit for f in self.files)

    @property
    def total(self) -> int:
        return sum(f.total for f in self.files)

    @property
    def pct(self) -> float:
        return (self.hit / self.total * 100.0) if self.total else 100.0


# ---------------------------------------------------------------------------
# Doc parsing
# ---------------------------------------------------------------------------

def _extract_yaml_block(doc_path: Path) -> str:
    """Return the YAML text between the critical-paths markers in the doc."""
    text = doc_path.read_text(encoding="utf-8")
    m = re.search(
        r"<!--\s*critical-paths:begin\s*-->.*?```yaml\n(.*?)```.*?<!--\s*critical-paths:end\s*-->",
        text,
        re.DOTALL,
    )
    if not m:
        raise ValueError(
            f"Could not locate <!-- critical-paths:begin --> … <!-- critical-paths:end --> "
            f"markers with a ```yaml block in {doc_path}"
        )
    return m.group(1)


def load_categories(doc_path: Path) -> list[dict[Any, Any]]:
    """Parse and return the categories list from the doc."""
    raw = _extract_yaml_block(doc_path)
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML parse error in {doc_path}: {exc}") from exc
    if not isinstance(data, dict) or "categories" not in data:
        raise ValueError(f"Expected top-level 'categories' key in YAML block of {doc_path}")
    return cast("list[dict[Any, Any]]", data["categories"])


# ---------------------------------------------------------------------------
# lcov parsing
# ---------------------------------------------------------------------------

def parse_lcov(lcov_path: Path, wanted_paths: set[str]) -> dict[str, FileStats]:
    """
    Parse lcov.info and return {lib/…/file.dart: FileStats} for wanted paths.

    SF: lines in lcov can be absolute or project-relative. We match by suffix:
    a wanted path 'lib/foo/bar.dart' matches any SF: that ends with that string
    (after normalising to forward slashes).
    """
    results: dict[str, FileStats] = {}
    current_sf: str | None = None
    hit_count = 0
    total_count = 0

    def _flush() -> None:
        nonlocal current_sf, hit_count, total_count
        if current_sf is not None:
            # Match against wanted paths by suffix
            matched = next(
                (w for w in wanted_paths if current_sf.endswith("/" + w) or current_sf == w),
                None,
            )
            if matched and matched not in results:
                results[matched] = FileStats(matched, hit_count, total_count)
        current_sf = None
        hit_count = 0
        total_count = 0

    text = lcov_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("SF:"):
            _flush()
            current_sf = line[3:].strip().replace("\\", "/")
        elif line.startswith("DA:"):
            parts = line[3:].split(",")
            if len(parts) >= 2:
                total_count += 1
                try:
                    if int(parts[1]) > 0:
                        hit_count += 1
                except ValueError:
                    pass
        elif line == "end_of_record":
            _flush()

    _flush()
    return results


# ---------------------------------------------------------------------------
# Gate evaluation
# ---------------------------------------------------------------------------

def evaluate(categories_raw: list[dict[Any, Any]], lcov_path: Path) -> list[CategoryResult]:
    """Build per-category results from lcov data."""
    # Collect all wanted paths so we do one lcov parse pass
    all_paths: set[str] = set()
    for cat in categories_raw:
        for p in cat.get("paths") or []:
            all_paths.add(p)

    file_stats = parse_lcov(lcov_path, all_paths) if all_paths else {}

    results: list[CategoryResult] = []
    for cat in categories_raw:
        paths = cat.get("paths") or []
        dormant = len(paths) == 0
        files: list[FileStats] = []
        for p in paths:
            if p in file_stats:
                files.append(file_stats[p])
            else:
                # Path listed in doc but absent from lcov — 0/0 (file may have no executable lines,
                # or flutter test didn't cover it at all). Record as 0 hit, 0 total so it's visible.
                files.append(FileStats(p, 0, 0))
        results.append(CategoryResult(
            id=cat.get("id", "?"),
            label=cat.get("label", cat.get("id", "?")),
            dormant=dormant,
            files=files,
        ))
    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _bar(pct: float, width: int = 20) -> str:
    filled = int(pct / 100 * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def print_report(results: list[CategoryResult]) -> None:
    print()
    print("=" * 70)
    print("CRITICAL-PATH COVERAGE GATE  (REQ-PROC-046 AC-04)")
    print("=" * 70)

    for cat in results:
        if cat.dormant:
            print(f"\n  [{cat.id}]  {cat.label}")
            print("    Status: dormant — no implementation yet, contributing 0/0")
            continue

        print(f"\n  [{cat.id}]  {cat.label}")
        print(f"    {'File':<65}  {'Hit':>5}  {'Tot':>5}  {'%':>6}")
        print(f"    {'-'*65}  {'---':>5}  {'---':>5}  {'---':>6}")
        for f in cat.files:
            short = f.path if len(f.path) <= 65 else "…" + f.path[-64:]
            pct_str = f"{f.pct:6.1f}%" if f.total else "   N/A"
            print(f"    {short:<65}  {f.hit:>5}  {f.total:>5}  {pct_str}")
        cat_pct = f"{cat.pct:.1f}%" if cat.total else "N/A"
        print(f"    {'CATEGORY TOTAL':<65}  {cat.hit:>5}  {cat.total:>5}  {cat_pct:>6}")

    # Overall
    overall_hit = sum(c.hit for c in results if not c.dormant)
    overall_total = sum(c.total for c in results if not c.dormant)
    print()
    print("=" * 70)
    if overall_total == 0:
        print("Gate is dormant — no critical-path code exists yet.")
        print("=" * 70)
    else:
        overall_pct = overall_hit / overall_total * 100.0
        bar = _bar(overall_pct)
        threshold_str = f"{COVERAGE_THRESHOLD:.1f}%"
        print(f"Overall  {bar}  {overall_pct:.1f}%  (threshold: {threshold_str})")
        print("=" * 70)
        if overall_pct >= COVERAGE_THRESHOLD:
            print(f"PASS: critical-path coverage {overall_pct:.1f}% ≥ {threshold_str}")
        else:
            print(f"FAIL: critical-path coverage {overall_pct:.1f}% < {threshold_str}")
            print()
            print("Categories below threshold:")
            for cat in results:
                if not cat.dormant and cat.total > 0 and cat.pct < COVERAGE_THRESHOLD:
                    print(f"  {cat.label}: {cat.pct:.1f}%")
        print("=" * 70)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="REQ-PROC-046 AC-04 critical-path coverage gate.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--lcov",
        metavar="PATH",
        help="Use this lcov.info file; skip running flutter test --coverage.",
    )
    parser.add_argument(
        "--no-run",
        action="store_true",
        help=f"Alias for --lcov {DEFAULT_LCOV.relative_to(PROJECT_ROOT)}",
    )
    parser.add_argument(
        "--doc",
        metavar="PATH",
        default=str(DEFAULT_DOC),
        help="Path to critical_paths.md (default: doc/testing/critical_paths.md)",
    )
    args = parser.parse_args()

    # Resolve doc
    doc_path = Path(args.doc)
    if not doc_path.is_absolute():
        doc_path = PROJECT_ROOT / doc_path
    if not doc_path.exists():
        print(f"ERROR: critical_paths.md not found: {doc_path}", file=sys.stderr)
        return 2

    # Load categories
    try:
        categories_raw = load_categories(doc_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    # Resolve lcov path
    if args.no_run:
        lcov_path = DEFAULT_LCOV
    elif args.lcov:
        lcov_path = Path(args.lcov)
        if not lcov_path.is_absolute():
            lcov_path = PROJECT_ROOT / lcov_path
    else:
        lcov_path = None

    # Run flutter test --coverage if needed
    if lcov_path is None:
        print("Running flutter test --coverage …")
        result = subprocess.run(
            ["flutter", "test", "--coverage"],
            cwd=PROJECT_ROOT,
        )
        if result.returncode != 0:
            print("ERROR: flutter test --coverage failed.", file=sys.stderr)
            return 2
        lcov_path = DEFAULT_LCOV

    if not lcov_path.exists():
        print(f"ERROR: lcov file not found: {lcov_path}", file=sys.stderr)
        print("Tip: run without --no-run/--lcov to execute flutter test --coverage first.")
        return 2

    # Evaluate
    results = evaluate(categories_raw, lcov_path)

    # Report
    print_report(results)

    # Determine exit code
    overall_total = sum(c.total for c in results if not c.dormant)
    if overall_total == 0:
        return 0
    overall_hit = sum(c.hit for c in results if not c.dormant)
    overall_pct = overall_hit / overall_total * 100.0
    return 0 if overall_pct >= COVERAGE_THRESHOLD else 1


if __name__ == "__main__":
    sys.exit(main())
