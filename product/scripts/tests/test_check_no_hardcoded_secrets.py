# tier: B
"""Tests for scripts/quality/check_no_hardcoded_secrets.sh (REQ-PROC-052 SP3).

Uses synthetic credential-shaped strings that are obviously fake (not real keys).
The script falls back to regex scanning when gitleaks is absent.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REAL_SCRIPT = Path(__file__).parent.parent / "quality" / "check_no_hardcoded_secrets.sh"


def _make_env(tmp: Path) -> tuple[Path, Path]:
    quality_dir = tmp / "scripts" / "quality"
    quality_dir.mkdir(parents=True)
    fake_root = tmp / "project"
    (fake_root / "lib").mkdir(parents=True)
    # Minimal pubspec so the scan target exists
    (fake_root / "pubspec.yaml").write_text("name: test_project\n")

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
    shutil.copy2(REAL_SCRIPT, quality_dir / "check_no_hardcoded_secrets.sh")
    return quality_dir / "check_no_hardcoded_secrets.sh", fake_root


def _run(script: Path) -> subprocess.CompletedProcess[str]:
    # Unset GITLEAKS_PATH so the regex fallback is always exercised in CI.
    import os
    env = {k: v for k, v in os.environ.items() if k != "GITLEAKS_PATH"}
    # Also override PATH so gitleaks is not found even if installed globally.
    env["PATH"] = "/usr/bin:/bin"
    return subprocess.run(["bash", str(script)], capture_output=True, text=True, env=env)


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
        _dart(root, "lib/clean.dart", "const baseUrl = 'https://example.com';\n")
        result = _run(script)
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
        assert "PASS" in result.stdout


def test_short_token_passes() -> None:
    """A short token-like string below the threshold passes."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/cfg.dart", "const token = 'abc123';\n")
        result = _run(script)
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# True-positives (regex fallback only — gitleaks excluded from PATH)
# ---------------------------------------------------------------------------

def test_google_api_key_pattern_flagged() -> None:
    """A Google API key shaped string (AIza...) is flagged."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        # Synthetic key — obviously fake test fixture
        fake_key = "AIzaSyDEFGHIJKLMNOPQRSTUVWXYZ1234567890ab"
        _dart(root, "lib/cfg.dart", f"const apiKey = '{fake_key}';\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"
        assert "FAIL" in result.stdout


def test_generic_api_key_assignment_flagged() -> None:
    """api_key = 'long-secret-value...' pattern is flagged."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/cfg.dart",
              "const api_key = 'abcdefghijklmnopqrstuvwxyz123456';\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "KNOWN BUG: check_no_hardcoded_secrets.sh passes the PEM regex "
        "'-----BEGIN...' as the grep pattern, but it starts with '--' which "
        "grep interprets as end-of-options, causing the pattern to be treated "
        "as a file argument rather than a regex. PEM detection is silently "
        "broken. Proposal filed: scripts/quality/proposals/grep_gates/"
        "2026-05-25_hardcoded-secrets-pem-grep-option-bug_TASK-PROC-046-18.md"
    ),
)
def test_pem_private_key_header_flagged() -> None:
    """PEM private key header SHOULD be flagged but grep misparses the pattern (xfail)."""
    with tempfile.TemporaryDirectory() as tmp_str:
        script, root = _make_env(Path(tmp_str))
        _dart(root, "lib/crypto.dart",
              "const cert = '-----BEGIN RSA PRIVATE KEY-----';\n")
        result = _run(script)
        assert result.returncode == 1, f"stdout: {result.stdout}"
