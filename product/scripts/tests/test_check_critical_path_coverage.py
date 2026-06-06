# tier: B
"""Tests for scripts/quality/check_critical_path_coverage.py (REQ-PROC-046 AC-04).

Tests pure logic functions directly without running flutter test.
main() is exercised via --lcov pointing at a synthetic lcov file.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Guard: check_critical_path_coverage.py calls sys.exit(2) at import time
# when PyYAML is missing. Skip the whole module cleanly instead.
pytest.importorskip("yaml", reason="PyYAML not installed in test environment")

sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
import check_critical_path_coverage as cpc  # type: ignore[import-not-found]

# ---------------------------------------------------------------------------
# Synthetic doc and lcov helpers
# ---------------------------------------------------------------------------

_DOC_TEMPLATE = """\
# Critical Paths

<!-- critical-paths:begin -->
```yaml
categories:
{categories_yaml}
```
<!-- critical-paths:end -->
"""


def _make_doc(tmp: Path, categories_yaml: str) -> Path:
    doc = tmp / "critical_paths.md"
    doc.write_text(_DOC_TEMPLATE.format(categories_yaml=categories_yaml))
    return doc


def _make_lcov(tmp: Path, entries: list[tuple[str, int, int]]) -> Path:
    """entries: [(sf_path, hit_lines, total_lines)]"""
    lines = []
    for sf, hit, total in entries:
        lines.append(f"SF:{sf}")
        for i in range(total):
            lines.append(f"DA:{i + 1},{1 if i < hit else 0}")
        lines.append("end_of_record")
    lcov = tmp / "lcov.info"
    lcov.write_text("\n".join(lines) + "\n")
    return lcov


# ---------------------------------------------------------------------------
# parse_lcov
# ---------------------------------------------------------------------------

def test_parse_lcov_counts_hits(tmp_path: Path) -> None:
    lcov = _make_lcov(tmp_path, [("/project/lib/auth.dart", 8, 10)])
    result = cpc.parse_lcov(lcov, {"lib/auth.dart"})
    assert "lib/auth.dart" in result
    assert result["lib/auth.dart"].hit == 8
    assert result["lib/auth.dart"].total == 10


def test_parse_lcov_matches_by_suffix(tmp_path: Path) -> None:
    """parse_lcov matches wanted paths by suffix regardless of absolute prefix."""
    lcov = _make_lcov(tmp_path, [("/some/deep/project/lib/foo/bar.dart", 5, 5)])
    result = cpc.parse_lcov(lcov, {"lib/foo/bar.dart"})
    assert "lib/foo/bar.dart" in result
    assert result["lib/foo/bar.dart"].pct == 100.0


def test_parse_lcov_empty_file(tmp_path: Path) -> None:
    lcov = tmp_path / "empty.info"
    lcov.write_text("")
    result = cpc.parse_lcov(lcov, {"lib/foo.dart"})
    assert result == {}


# ---------------------------------------------------------------------------
# load_categories / _extract_yaml_block
# ---------------------------------------------------------------------------

def test_load_categories_parses_paths(tmp_path: Path) -> None:
    doc = _make_doc(tmp_path, (
        "  - id: CP-001\n"
        "    label: Auth\n"
        "    paths:\n"
        "      - lib/features/auth/auth.dart\n"
    ))
    cats = cpc.load_categories(doc)
    assert len(cats) == 1
    assert cats[0]["id"] == "CP-001"
    assert "lib/features/auth/auth.dart" in cats[0]["paths"]


def test_load_categories_dormant_has_empty_paths(tmp_path: Path) -> None:
    doc = _make_doc(tmp_path, (
        "  - id: CP-002\n"
        "    label: Dormant\n"
        "    paths: []\n"
    ))
    cats = cpc.load_categories(doc)
    assert cats[0]["paths"] == []


# ---------------------------------------------------------------------------
# evaluate — gate logic
# ---------------------------------------------------------------------------

def test_evaluate_dormant_category(tmp_path: Path) -> None:
    cats = [{"id": "CP-001", "label": "Dormant", "paths": []}]
    lcov = _make_lcov(tmp_path, [])
    results = cpc.evaluate(cats, lcov)
    assert results[0].dormant is True
    assert results[0].total == 0


def test_evaluate_full_coverage_passes(tmp_path: Path) -> None:
    cats = [{"id": "CP-001", "label": "Auth", "paths": ["lib/auth.dart"]}]
    lcov = _make_lcov(tmp_path, [("/project/lib/auth.dart", 10, 10)])
    results = cpc.evaluate(cats, lcov)
    assert results[0].pct == 100.0


def test_evaluate_low_coverage_fails(tmp_path: Path) -> None:
    cats = [{"id": "CP-001", "label": "Auth", "paths": ["lib/auth.dart"]}]
    lcov = _make_lcov(tmp_path, [("/project/lib/auth.dart", 5, 100)])
    results = cpc.evaluate(cats, lcov)
    assert results[0].pct < cpc.COVERAGE_THRESHOLD


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------

def test_main_passes_when_all_dormant(tmp_path: Path) -> None:
    doc = _make_doc(tmp_path, "  - id: CP-001\n    label: Dormant\n    paths: []\n")
    lcov = _make_lcov(tmp_path, [])
    argv = ["check_critical_path_coverage.py", "--doc", str(doc), "--lcov", str(lcov)]
    with patch("sys.argv", argv):
        rc = cpc.main()
    assert rc == 0


def test_main_passes_on_full_coverage(tmp_path: Path) -> None:
    doc = _make_doc(tmp_path,
                    "  - id: CP-001\n    label: Auth\n    paths:\n"
                    "      - lib/auth.dart\n")
    lcov = _make_lcov(tmp_path, [("/project/lib/auth.dart", 100, 100)])
    fake_default_lcov = tmp_path / "coverage" / "lcov.info"
    argv = ["check_critical_path_coverage.py", "--doc", str(doc), "--lcov", str(lcov)]
    with (patch("sys.argv", argv),
          patch.object(cpc, "PROJECT_ROOT", tmp_path),
          patch.object(cpc, "DEFAULT_LCOV", fake_default_lcov)):
        rc = cpc.main()
    assert rc == 0


def test_main_fails_on_low_coverage(tmp_path: Path) -> None:
    doc = _make_doc(tmp_path,
                    "  - id: CP-001\n    label: Auth\n    paths:\n"
                    "      - lib/auth.dart\n")
    lcov = _make_lcov(tmp_path, [("/project/lib/auth.dart", 1, 100)])
    fake_default_lcov = tmp_path / "coverage" / "lcov.info"
    argv = ["check_critical_path_coverage.py", "--doc", str(doc), "--lcov", str(lcov)]
    with (patch("sys.argv", argv),
          patch.object(cpc, "PROJECT_ROOT", tmp_path),
          patch.object(cpc, "DEFAULT_LCOV", fake_default_lcov)):
        rc = cpc.main()
    assert rc == 1


def test_main_returns_2_on_missing_doc(tmp_path: Path) -> None:
    lcov = _make_lcov(tmp_path, [])
    argv = ["check_critical_path_coverage.py",
            "--doc", str(tmp_path / "missing.md"), "--lcov", str(lcov)]
    with patch("sys.argv", argv):
        rc = cpc.main()
    assert rc == 2
