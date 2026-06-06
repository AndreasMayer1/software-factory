# tier: B
"""Tests for scripts/quality/check_test_smells.py (REQ-PROC-046 TQ1).

Imports check_test_smells directly and calls check_file() with synthetic
Dart test files written to tmp paths.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
import check_test_smells as cs  # type: ignore[import-not-found]

PROJECT_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# True-negatives — check_file() returns 0
# ---------------------------------------------------------------------------

def test_test_with_expect_passes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """test() body containing expect() passes."""
    f = tmp_path / "good_test.dart"
    f.write_text(
        "void main() {\n"
        "  test('adds', () {\n"
        "    expect(1 + 1, 2);\n"
        "  });\n"
        "}\n"
    )
    count = cs.check_file(f, str(f))
    assert count == 0


def test_test_with_verify_passes(tmp_path: Path) -> None:
    """test() body containing verify() passes."""
    f = tmp_path / "good_test.dart"
    f.write_text(
        "void main() {\n"
        "  test('calls method', () {\n"
        "    verify(mockObj.method());\n"
        "  });\n"
        "}\n"
    )
    count = cs.check_file(f, str(f))
    assert count == 0


def test_group_with_tests_passes(tmp_path: Path) -> None:
    """group() containing test() passes empty-group check."""
    f = tmp_path / "good_test.dart"
    f.write_text(
        "void main() {\n"
        "  group('feature', () {\n"
        "    test('works', () { expect(true, isTrue); });\n"
        "  });\n"
        "}\n"
    )
    count = cs.check_file(f, str(f))
    assert count == 0


# ---------------------------------------------------------------------------
# True-positives — check_file() returns > 0
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason=(
        "KNOWN LIMITATION: check_test_smells.py scan_blocks() cannot extract "
        "closure bodies in the standard Dart pattern test('name', () { body }). "
        "The paren-depth scanner finds the matching close-paren of test(...) and "
        "then looks for '{' AFTER it — but in closure-style tests the body brace "
        "is INSIDE the argument list, not after the call. Sub-checks 1 and 2 "
        "therefore never fire on idiomatic Dart tests. Proposal filed: "
        "scripts/quality/proposals/grep_gates/"
        "2026-05-25_test-smells-closure-scanner-limitation_TASK-PROC-046-18.md"
    ),
)
def test_test_without_assertion_flagged(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """test() body with no assertion SHOULD be flagged but scanner can't see it (xfail)."""
    f = tmp_path / "bad_test.dart"
    f.write_text(
        "void main() {\n"
        "  test('does nothing', () {\n"
        "    final x = 1 + 1;\n"
        "  });\n"
        "}\n"
    )
    count = cs.check_file(f, str(f))
    assert count >= 1
    captured = capsys.readouterr()
    assert "no assertion" in captured.out


@pytest.mark.xfail(
    strict=True,
    reason=(
        "KNOWN LIMITATION: same scan_blocks closure-pattern limitation — "
        "group() body is never extracted because the closing '}' is inside "
        "the argument list of group(...), not after the call. See xfail on "
        "test_test_without_assertion_flagged for full details."
    ),
)
def test_empty_group_flagged(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """group() with no nested tests SHOULD be flagged but scanner can't see it (xfail)."""
    f = tmp_path / "bad_test.dart"
    f.write_text(
        "void main() {\n"
        "  group('empty', () {\n"
        "    final setup = true;\n"
        "  });\n"
        "}\n"
    )
    count = cs.check_file(f, str(f))
    assert count >= 1
    captured = capsys.readouterr()
    assert "empty group" in captured.out


def test_literal_length_expect_flagged(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """expect(list.length, N) is flagged in favour of hasLength(N)."""
    f = tmp_path / "bad_test.dart"
    f.write_text(
        "void main() {\n"
        "  test('length check', () {\n"
        "    expect(items.length, 3);\n"
        "  });\n"
        "}\n"
    )
    count = cs.check_file(f, str(f))
    assert count >= 1
    captured = capsys.readouterr()
    assert "hasLength" in captured.out


# ---------------------------------------------------------------------------
# main() integration — with patched roots
# ---------------------------------------------------------------------------

def test_main_returns_0_on_empty_roots(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits 0 when no test roots exist (NOTICE path)."""
    with tempfile.TemporaryDirectory() as tmp_str:
        monkeypatch.setattr(cs, "PROJECT_ROOT", Path(tmp_str))
        rc = cs.main([])
    assert rc == 0


@pytest.mark.xfail(
    strict=True,
    reason="Same closure-scanner limitation: test() body inside argument list "
           "is not reachable by scan_blocks; main() returns 0 instead of 1.",
)
def test_main_returns_1_on_smelly_tests(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """main() SHOULD return 1 for a closure-style assertion-free test (xfail)."""
    unit_dir = tmp_path / "test" / "unit"
    unit_dir.mkdir(parents=True)
    (unit_dir / "bad_test.dart").write_text(
        "void main() { test('empty', () { final x = 1; }); }\n"
    )
    monkeypatch.setattr(cs, "PROJECT_ROOT", tmp_path)
    rc = cs.main([])
    assert rc == 1
