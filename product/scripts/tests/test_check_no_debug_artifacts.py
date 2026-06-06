# tier: B
"""Tests for scripts/quality/check_no_debug_artifacts.sh (REQ-PROC-046 AC-12).

Scans ${PROJECT_ROOT}/lib/ for bare print(), debugPrint() without [DIAG-*],
and // TEMPORARY: markers.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REAL_SCRIPT = Path(__file__).parent.parent / "quality" / "check_no_debug_artifacts.sh"


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
    shutil.copy2(REAL_SCRIPT, quality_dir / "check_no_debug_artifacts.sh")
    return quality_dir / "check_no_debug_artifacts.sh", fake_root


def _run(script: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(script)], capture_output=True, text=True)


def _write_dart(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# ---------------------------------------------------------------------------
# True-negatives
# ---------------------------------------------------------------------------

def test_clean_file_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/clean.dart", "class MyClass { void run() {} }\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
        assert "PASS" in result.stdout


def test_diag_debug_print_passes() -> None:
    """debugPrint with [DIAG-*] prefix is allowed."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/ok.dart",
                    "void f() { debugPrint('[DIAG-auth] token refreshed'); }\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}"


def test_print_in_comment_passes() -> None:
    """print( mentioned in a comment is not flagged."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/ok2.dart",
                    "// Do not use print() in production code\nclass X {}\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}"


def test_generated_files_skipped() -> None:
    """*.g.dart files are skipped."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/foo.g.dart", "print('generated');\n")
        result = _run(script)
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# True-positives
# ---------------------------------------------------------------------------

def test_bare_print_flagged() -> None:
    """Bare print() call in lib/ is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/bad.dart", "void f() { print('debug'); }\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"
        assert "FAIL" in result.stdout


def test_debug_print_without_diag_flagged() -> None:
    """debugPrint without [DIAG-*] prefix is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/bad.dart",
                    "void f() { debugPrint('some message'); }\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"


def test_temporary_marker_flagged() -> None:
    """// TEMPORARY: comment marker is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/bad.dart",
                    "// TEMPORARY: remove after TASK-XYZ lands\nvoid probe() {}\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"
