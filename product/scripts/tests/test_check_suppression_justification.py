# tier: B
"""Tests for scripts/quality/check_suppression_justification.sh (REQ-PROC-046 AC-11).

The script cd's to PROJECT_ROOT and scans lib/, test/, integration_test/.
Isolation: stub _lib.sh + copy of script, fake project root with lib/ subdir.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REAL_SCRIPT = Path(__file__).parent.parent / "quality" / "check_suppression_justification.sh"


def _make_env(tmp: Path) -> tuple[Path, Path]:
    quality_dir = tmp / "scripts" / "quality"
    quality_dir.mkdir(parents=True)
    fake_root = tmp / "project"
    (fake_root / "lib").mkdir(parents=True)

    (quality_dir / "_lib.sh").write_text(
        f"""#!/usr/bin/env bash
_QUALITY_DIR="{quality_dir}"
PROJECT_ROOT="{fake_root}"
EXCLUDE_FILE="{quality_dir}/exclusions.txt"
EXCLUDE_PATTERNS=()
parse_exclude_arg() {{ while [[ $# -gt 0 ]]; do shift; done; }}
load_exclude_patterns() {{
    EXCLUDE_PATTERNS=()
    [[ ! -f "$EXCLUDE_FILE" ]] && return 0
    while IFS= read -r line || [[ -n "$line" ]]; do
        local t="${{line%%#*}}"
        t="$(echo "$t" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        [[ -z "$t" ]] && continue
        EXCLUDE_PATTERNS+=("$t")
    done < "$EXCLUDE_FILE"
}}
is_excluded() {{
    local path="$1"
    for pat in "${{EXCLUDE_PATTERNS[@]}}"; do [[ "$path" == *"$pat"* ]] && return 0; done
    return 1
}}
"""
    )
    (quality_dir / "exclusions.txt").write_text("")
    shutil.copy2(REAL_SCRIPT, quality_dir / "check_suppression_justification.sh")
    return quality_dir / "check_suppression_justification.sh", fake_root


def _run(script: Path, root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(script)], capture_output=True, text=True,
                          cwd=str(root))


def _write_dart(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# ---------------------------------------------------------------------------
# True-negatives
# ---------------------------------------------------------------------------

def test_no_suppressions_passes() -> None:
    """File with no ignore directives passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/clean.dart", "class MyClass {}\n")
        result = _run(script, root)
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_ignore_with_trailing_justification_passes() -> None:
    """ignore: with inline trailing justification (after the rules) passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/ok.dart",
                    "// ignore: prefer_const_constructors // justified because generated code requires this\n"
                    "final x = MyClass();\n")
        result = _run(script, root)
        assert result.returncode == 0, f"stdout: {result.stdout}"


def test_ignore_with_preceding_comment_passes() -> None:
    """ignore: preceded (within 2 lines) by a long-enough comment passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/ok2.dart",
                    "// Generated code cannot use const here due to build_runner\n"
                    "// ignore: prefer_const_constructors\n"
                    "final x = MyClass();\n")
        result = _run(script, root)
        assert result.returncode == 0, f"stdout: {result.stdout}"


def test_generated_files_skipped() -> None:
    """*.g.dart and *.freezed.dart files are skipped."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/foo.g.dart", "// ignore: avoid_print\nprint('');\n")
        _write_dart(root, "lib/bar.freezed.dart", "// ignore: prefer_const\nvar x;\n")
        result = _run(script, root)
        assert result.returncode == 0, f"stdout: {result.stdout}"


# ---------------------------------------------------------------------------
# True-positives
# ---------------------------------------------------------------------------

def test_bare_ignore_without_justification_flagged() -> None:
    """ignore: with no adjacent justification comment is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/bad.dart",
                    "// ignore: avoid_print\n"
                    "print('hi');\n")
        result = _run(script, root)
        assert result.returncode == 1, f"stdout: {result.stdout}"
        assert "FAIL" in result.stdout


def test_ignore_for_file_without_justification_flagged() -> None:
    """ignore_for_file: without justification is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/bad2.dart",
                    "// ignore_for_file: prefer_const_constructors\n"
                    "class X {}\n")
        result = _run(script, root)
        assert result.returncode == 1, f"stdout: {result.stdout}"


def test_short_trailing_justification_flagged() -> None:
    """A trailing justification shorter than 12 chars is not sufficient."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/short.dart",
                    "// ignore: avoid_print // ok\n"
                    "print('hi');\n")
        result = _run(script, root)
        assert result.returncode == 1, f"stdout: {result.stdout}"
