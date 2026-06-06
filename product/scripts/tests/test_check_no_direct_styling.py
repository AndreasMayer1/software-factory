# tier: B
"""Tests for scripts/quality/check_no_direct_styling.sh (REQ-PROC-046 AC-02).

Isolation: stub _lib.sh mirrors pointing PROJECT_ROOT at a temp directory.
The script scans ${PROJECT_ROOT}/lib/features/ only.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REAL_SCRIPT = Path(__file__).parent.parent / "quality" / "check_no_direct_styling.sh"
PROJECT_ROOT = Path(__file__).parent.parent.parent


def _make_env(tmp: Path) -> tuple[Path, Path]:
    quality_dir = tmp / "scripts" / "quality"
    quality_dir.mkdir(parents=True)
    fake_root = tmp / "project"
    (fake_root / "lib" / "features").mkdir(parents=True)

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
    shutil.copy2(REAL_SCRIPT, quality_dir / "check_no_direct_styling.sh")
    return quality_dir / "check_no_direct_styling.sh", fake_root


def _run(script: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(script)], capture_output=True, text=True)


def _write_dart(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# ---------------------------------------------------------------------------
# True-negatives
# ---------------------------------------------------------------------------

def test_no_features_dir_exits_0() -> None:
    """Missing lib/features/ dir exits 0 with NOTICE."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        (root / "lib" / "features").rmdir()
        result = _run(script)
        assert result.returncode == 0


def test_empty_features_passes() -> None:
    """Empty lib/features/ (no dart files) passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, _root = _make_env(Path(tmp_str))
        result = _run(script)
        assert result.returncode == 0
        assert "PASS" in result.stdout


def test_clean_widget_passes() -> None:
    """Widget using design-system component (no raw primitives) passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/features/mood/my_widget.dart",
                    "import 'package:flutter/material.dart';\n"
                    "class MoodWidget extends StatelessWidget {\n"
                    "  Widget build(context) => AppText('hello');\n"
                    "}\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_style_in_comment_passes() -> None:
    """TextStyle inside a comment line is not flagged."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/features/mood/w.dart",
                    "// Use AppTextStyles instead of TextStyle(\n"
                    "class W {}\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}"


# ---------------------------------------------------------------------------
# True-positives
# ---------------------------------------------------------------------------

def test_textstyle_in_features_flagged() -> None:
    """TextStyle( constructor in lib/features/ is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/features/mood/w.dart",
                    "final s = TextStyle(fontSize: 14);\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"
        assert "FAIL" in result.stdout


def test_colors_dot_in_features_flagged() -> None:
    """Colors.xxx usage in lib/features/ is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/features/mood/w.dart",
                    "final c = Colors.white;\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"


def test_button_style_in_features_flagged() -> None:
    """ButtonStyle( in lib/features/ is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/features/mood/w.dart",
                    "final btn = ButtonStyle();\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"
