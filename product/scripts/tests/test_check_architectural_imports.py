# tier: B
"""Tests for scripts/quality/check_architectural_imports.sh (REQ-PROC-046 AC-05).

Isolation strategy: same as test_check_type_naming.py — creates a temp
scripts/quality/ mirror with a stub _lib.sh that overrides PROJECT_ROOT,
copies the real script and the policy YAML beside it.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REAL_SCRIPT = Path(__file__).parent.parent / "quality" / "check_architectural_imports.sh"
REAL_POLICY = Path(__file__).parent.parent / "quality" / "architectural_imports_policy.yaml"
PROJECT_ROOT = Path(__file__).parent.parent.parent


def _make_env(tmp: Path) -> tuple[Path, Path]:
    """Build an isolated scripts/quality/ mirror. Returns (script_path, fake_project_root)."""
    quality_dir = tmp / "scripts" / "quality"
    quality_dir.mkdir(parents=True)

    fake_root = tmp / "project"
    (fake_root / "lib").mkdir(parents=True)

    stub_lib = quality_dir / "_lib.sh"
    stub_lib.write_text(
        f"""#!/usr/bin/env bash
_QUALITY_DIR="{quality_dir}"
PROJECT_ROOT="{fake_root}"
EXCLUDE_FILE="{quality_dir}/exclusions.txt"
EXCLUDE_PATTERNS=()

parse_exclude_arg() {{
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --exclude-paths) EXCLUDE_FILE="$2"; shift 2 ;;
            --exclude-paths=*) EXCLUDE_FILE="${{1#*=}}"; shift ;;
            *) shift ;;
        esac
    done
}}

load_exclude_patterns() {{
    EXCLUDE_PATTERNS=()
    [[ ! -f "$EXCLUDE_FILE" ]] && return 0
    while IFS= read -r line || [[ -n "$line" ]]; do
        local trimmed="${{line%%#*}}"
        trimmed="$(echo "$trimmed" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        [[ -z "$trimmed" ]] && continue
        EXCLUDE_PATTERNS+=("$trimmed")
    done < "$EXCLUDE_FILE"
}}

is_excluded() {{
    local path="$1"
    local pat
    for pat in "${{EXCLUDE_PATTERNS[@]}}"; do
        [[ "$path" == *"$pat"* ]] && return 0
    done
    return 1
}}
"""
    )
    (quality_dir / "exclusions.txt").write_text("")
    shutil.copy2(REAL_POLICY, quality_dir / "architectural_imports_policy.yaml")
    shutil.copy2(REAL_SCRIPT, quality_dir / "check_architectural_imports.sh")
    return quality_dir / "check_architectural_imports.sh", fake_root


def _run(script: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(script)], capture_output=True, text=True)


def _write_dart(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# ---------------------------------------------------------------------------
# True-negatives
# ---------------------------------------------------------------------------

def test_clean_domain_file_passes() -> None:
    """Domain file with no Flutter imports passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/core/domain/entities/my_entity.dart",
                    "class MyEntity {}\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
        assert "PASS" in result.stdout


def test_flutter_import_in_presentation_passes() -> None:
    """Flutter imports outside domain are allowed."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/core/presentation/my_widget.dart",
                    "import 'package:flutter/material.dart';\nclass MyWidget {}\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_empty_lib_passes() -> None:
    """An empty lib/ dir exits 0."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, _root = _make_env(Path(tmp_str))
        result = _run(script)
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# True-positives
# ---------------------------------------------------------------------------

def test_flutter_import_in_core_domain_flagged() -> None:
    """Flutter import in lib/core/domain/ violates the policy."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/core/domain/entities/bad.dart",
                    "import 'package:flutter/material.dart';\nclass Bad {}\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}\nstderr: {result.stderr}"
        assert "FAIL" in result.stdout


def test_flutter_bloc_import_in_domain_flagged() -> None:
    """flutter_bloc import in domain violates the policy."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/core/domain/services/bad_service.dart",
                    "import 'package:flutter_bloc/flutter_bloc.dart';\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_flutter_import_in_feature_domain_flagged() -> None:
    """Flutter import in lib/features/*/domain/ violates the policy."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _write_dart(root, "lib/features/mood/domain/entities/mood.dart",
                    "import 'package:flutter/widgets.dart';\nclass Mood {}\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}\nstderr: {result.stderr}"
