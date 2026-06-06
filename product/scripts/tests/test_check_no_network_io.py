# tier: B
"""Tests for scripts/quality/check_no_network_io.sh (REQ-PROC-052 SP1)."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REAL_SCRIPT = Path(__file__).parent.parent / "quality" / "check_no_network_io.sh"


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
    shutil.copy2(REAL_SCRIPT, quality_dir / "check_no_network_io.sh")
    return quality_dir / "check_no_network_io.sh", fake_root


def _run(script: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(script)], capture_output=True, text=True)


def _dart(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


# ---------------------------------------------------------------------------
# True-negatives
# ---------------------------------------------------------------------------

def test_clean_file_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/data/repo.dart", "class Repo { void save() {} }\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}"
        assert "PASS" in result.stdout


def test_dart_io_import_without_network_passes() -> None:
    """Plain dart:io import is allowed (covers File, Platform, etc.)."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/util/file_util.dart", "import 'dart:io';\nclass F {}\n")
        result = _run(script)
        assert result.returncode == 0


def test_generated_file_skipped() -> None:
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/gen.g.dart", "import 'package:http/http.dart';\n")
        result = _run(script)
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# True-positives
# ---------------------------------------------------------------------------

def test_http_package_import_flagged() -> None:
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/data/client.dart", "import 'package:http/http.dart';\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"
        assert "FAIL" in result.stdout


def test_dio_package_flagged() -> None:
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/data/client.dart", "import 'package:dio/dio.dart';\n")
        result = _run(script)
        assert result.returncode == 1


def test_http_client_constructor_flagged() -> None:
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/data/client.dart",
              "import 'dart:io';\nfinal c = HttpClient();\n")
        result = _run(script)
        assert result.returncode == 1


def test_websocket_package_flagged() -> None:
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/data/ws.dart",
              "import 'package:web_socket_channel/web_socket_channel.dart';\n")
        result = _run(script)
        assert result.returncode == 1
