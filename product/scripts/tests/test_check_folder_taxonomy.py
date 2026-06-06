# tier: B
"""Tests for scripts/quality/check_folder_taxonomy.sh.

Key validation: usecases/ is in the allowlist (REQ-PROC-046 K.2).
Isolation: stub _lib.sh + copy of script + copy of allowlist.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REAL_SCRIPT = Path(__file__).parent.parent / "quality" / "check_folder_taxonomy.sh"
REAL_ALLOWLIST = Path(__file__).parent.parent / "quality" / "folder_taxonomy_allowlist.txt"


def _make_env(tmp: Path) -> tuple[Path, Path]:
    quality_dir = tmp / "scripts" / "quality"
    quality_dir.mkdir(parents=True)
    fake_root = tmp / "project"
    fake_root.mkdir()

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
    shutil.copy2(REAL_ALLOWLIST, quality_dir / "folder_taxonomy_allowlist.txt")
    shutil.copy2(REAL_SCRIPT, quality_dir / "check_folder_taxonomy.sh")
    return quality_dir / "check_folder_taxonomy.sh", fake_root


def _run(script: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(script)], capture_output=True, text=True)


def _dart(root: Path, rel: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("class C {}\n")


# ---------------------------------------------------------------------------
# True-negatives
# ---------------------------------------------------------------------------

def test_no_domain_dirs_exits_0() -> None:
    """No */domain/ directories at all → NOTICE + exit 0."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, _root = _make_env(Path(tmp_str))
        result = _run(script)
        assert result.returncode == 0


def test_entities_subfolder_passes() -> None:
    """lib/core/domain/entities/ is in the allowlist → passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/core/domain/entities/my_entity.dart")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
        assert "PASS" in result.stdout


def test_usecases_subfolder_passes() -> None:
    """usecases/ is explicitly in the allowlist — must NOT be flagged."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/features/role_selection/domain/usecases/select_role.dart")
        result = _run(script)
        assert result.returncode == 0, (
            f"usecases/ should be in allowlist but was flagged.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


def test_services_subfolder_passes() -> None:
    """services/ is in the allowlist → passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/core/domain/services/my_service.dart")
        result = _run(script)
        assert result.returncode == 0


def test_repositories_subfolder_passes() -> None:
    """repositories/ is in the allowlist → passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/core/domain/repositories/i_user_repo.dart")
        result = _run(script)
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# True-positives
# ---------------------------------------------------------------------------

def test_file_directly_in_domain_flagged() -> None:
    """Dart file placed directly in domain/ (no subfolder) is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/core/domain/stray_file.dart")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"
        assert "FAIL" in result.stdout


def test_unlisted_subfolder_flagged() -> None:
    """A subfolder not in the allowlist (e.g. widgets/) is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/core/domain/widgets/my_widget.dart")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"
        assert "widgets" in result.stdout
