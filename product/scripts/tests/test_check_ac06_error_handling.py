# tier: B
"""Tests for scripts/quality/check_ac06_error_handling.py (REQ-PROC-046 AC-06).

Tests pure logic functions directly without touching the real lib/ tree.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
import check_ac06_error_handling as ac06  # type: ignore[import-not-found]

# ---------------------------------------------------------------------------
# _is_generated
# ---------------------------------------------------------------------------


def test_generated_g_dart_excluded() -> None:
    assert ac06._is_generated(Path("lib/foo/bar.g.dart")) is True


def test_generated_freezed_excluded() -> None:
    assert ac06._is_generated(Path("lib/foo/bar.freezed.dart")) is True


def test_generated_dir_excluded() -> None:
    assert ac06._is_generated(Path("lib/generated/models.dart")) is True


def test_regular_dart_not_excluded() -> None:
    assert ac06._is_generated(Path("lib/foo/bar.dart")) is False


# ---------------------------------------------------------------------------
# check_file — bare catch detection
# ---------------------------------------------------------------------------


def _check(source: str) -> list[tuple[int, str]]:
    with tempfile.NamedTemporaryFile(suffix=".dart", mode="w", delete=False, encoding="utf-8") as f:
        f.write(source)
        tmp = Path(f.name)
    try:
        return cast(list[tuple[int, str]], ac06.check_file(tmp, "lib/fake.dart"))
    finally:
        tmp.unlink(missing_ok=True)


def test_bare_catch_detected() -> None:
    src = "void f() {\n  try {\n    x();\n  } catch (e) {\n    log(e);\n  }\n}\n"
    violations = _check(src)
    assert any("bare catch" in d for _, d in violations)


def test_typed_catch_passes() -> None:
    src = "void f() {\n  try {\n    x();\n  } on Exception catch (e) {\n    log(e);\n  }\n}\n"
    violations = _check(src)
    assert not any("bare catch" in d for _, d in violations)


def test_multiline_on_guard_passes() -> None:
    # `on` guard on the line immediately before `catch (`
    src = "void f() {\n  try {\n    x();\n  } on SomeVeryLongExceptionType\n      catch (e, s) {\n    log(e);\n  }\n}\n"
    violations = _check(src)
    assert not any("bare catch" in d for _, d in violations)


def test_bare_catch_lineno_correct() -> None:
    src = "void f() {\n  try {\n    x();\n  } catch (e) {\n    log(e);\n  }\n}\n"
    violations = _check(src)
    assert violations[0][0] == 4


# ---------------------------------------------------------------------------
# check_file — literal throw detection
# ---------------------------------------------------------------------------


def test_throw_string_single_quote_detected() -> None:
    src = "void f() { throw 'message'; }\n"
    violations = _check(src)
    assert any("non-Error" in d for _, d in violations)


def test_throw_string_double_quote_detected() -> None:
    src = 'void f() { throw "message"; }\n'
    violations = _check(src)
    assert any("non-Error" in d for _, d in violations)


def test_throw_raw_string_detected() -> None:
    src = "void f() { throw r'raw'; }\n"
    violations = _check(src)
    assert any("non-Error" in d for _, d in violations)


def test_throw_null_detected() -> None:
    src = "void f() { throw null; }\n"
    violations = _check(src)
    assert any("non-Error" in d for _, d in violations)


def test_throw_bool_detected() -> None:
    src = "void f() { throw true; }\n"
    violations = _check(src)
    assert any("non-Error" in d for _, d in violations)


def test_throw_integer_detected() -> None:
    src = "void f() { throw 42; }\n"
    violations = _check(src)
    assert any("non-Error" in d for _, d in violations)


def test_throw_exception_passes() -> None:
    src = "void f() { throw StateError('bad'); }\n"
    violations = _check(src)
    assert not any("non-Error" in d for _, d in violations)


def test_throw_in_comment_ignored() -> None:
    src = "// throw 'nope';\nvoid f() {}\n"
    violations = _check(src)
    assert not any("non-Error" in d for _, d in violations)


# ---------------------------------------------------------------------------
# _load_exclusions / _is_excluded
# ---------------------------------------------------------------------------


def test_exclusions_substring_match() -> None:
    patterns = ["generated/", "foo_bar"]
    assert ac06._is_excluded("lib/generated/models.dart", patterns) is True
    assert ac06._is_excluded("lib/src/foo_bar_widget.dart", patterns) is True
    assert ac06._is_excluded("lib/src/other.dart", patterns) is False


def test_exclusions_file_missing_returns_empty() -> None:
    result = ac06._load_exclusions(Path("/nonexistent/exclusions.txt"))
    assert result == []


def test_exclusions_strips_comments() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("# comment\nsome/path  # inline comment\n\n")
        tmp = Path(f.name)
    try:
        result = ac06._load_exclusions(tmp)
        assert result == ["some/path"]
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# _load_baseline
# ---------------------------------------------------------------------------


def test_baseline_file_missing_returns_empty_set() -> None:
    result = ac06._load_baseline(Path("/nonexistent/baseline.txt"))
    assert result == set()


def test_baseline_loads_path_lineno_pairs() -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("lib/foo.dart:10\nlib/bar.dart:42\n# comment\n\n")
        tmp = Path(f.name)
    try:
        result = ac06._load_baseline(tmp)
        assert "lib/foo.dart:10" in result
        assert "lib/bar.dart:42" in result
        assert len(result) == 2
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# main — baseline suppression
# ---------------------------------------------------------------------------


def _make_baseline(entries: list[str]) -> Path:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("\n".join(entries) + "\n")
        return Path(f.name)


def test_baseline_suppresses_listed_violation(tmp_path: Path) -> None:
    dart = tmp_path / "lib"
    dart.mkdir()
    (dart / "foo.dart").write_text("void f() { throw null; }\n", encoding="utf-8")
    # Build a baseline that references the violation at line 1
    baseline = _make_baseline([f"{dart / 'foo.dart'}:1".replace(str(tmp_path) + "/", "")])
    # The main function uses project_root derived from __file__; we test _load_baseline
    # indirectly by verifying the key format matches what check_file produces.
    violations = cast(list[tuple[int, str]], ac06.check_file(dart / "foo.dart", "lib/foo.dart"))
    key = f"lib/foo.dart:{violations[0][0]}"
    loaded = ac06._load_baseline(baseline)
    baseline.unlink(missing_ok=True)
    # key must be suppressed when present in the baseline
    assert key in loaded


def test_baseline_does_not_suppress_new_violation() -> None:
    baseline = _make_baseline(["lib/other.dart:99"])
    try:
        loaded = ac06._load_baseline(baseline)
        # A violation in a file not listed in the baseline is not suppressed
        assert "lib/foo.dart:1" not in loaded
    finally:
        baseline.unlink(missing_ok=True)
