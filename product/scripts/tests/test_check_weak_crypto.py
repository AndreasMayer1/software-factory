# tier: B
"""Tests for scripts/quality/check_weak_crypto.sh (REQ-PROC-052 SP4).

Each weak-crypto usage (sha1/md5) must have an adjacent non-security comment.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REAL_SCRIPT = Path(__file__).parent.parent / "quality" / "check_weak_crypto.sh"


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
    shutil.copy2(REAL_SCRIPT, quality_dir / "check_weak_crypto.sh")
    return quality_dir / "check_weak_crypto.sh", fake_root


def _run(script: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(script)], capture_output=True, text=True)


def _dart(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


# ---------------------------------------------------------------------------
# True-negatives
# ---------------------------------------------------------------------------

def test_no_crypto_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/clean.dart", "class Hasher { String id(String s) => s; }\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}"
        assert "PASS" in result.stdout


def test_sha1_with_nonsecurity_trailing_comment_passes() -> None:
    """sha1 with inline non-security justification passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/cache.dart",
              "final key = sha1.convert(utf8.encode(q)).toString();"
              " // non-security: cache key only\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}"


def test_sha1_with_preceding_justification_passes() -> None:
    """sha1 preceded by a checksum comment passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/cache.dart",
              "// non-security: cache key for query deduplication\n"
              "final key = sha1.convert(bytes).toString();\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}"


def test_md5_with_checksum_comment_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/util.dart",
              "// non-security: file checksum for cache invalidation\n"
              "final digest = md5.convert(fileBytes);\n")
        result = _run(script)
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# True-positives
# ---------------------------------------------------------------------------

def test_sha1_without_justification_flagged() -> None:
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/bad.dart",
              "final hash = sha1.convert(utf8.encode(password));\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"
        assert "FAIL" in result.stdout


def test_md5_without_justification_flagged() -> None:
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/bad.dart",
              "final h = md5.convert(data);\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"
