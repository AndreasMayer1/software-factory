# tier: B
"""Tests for scripts/quality/check_complexity.py (REQ-PROC-046 G2).

Strategy: the script shells out to a Dart helper that is not available in the
test environment. Tests therefore either:

  (a) exercise code paths that never reach the Dart helper (e.g. missing
      scan-root exits 0 immediately), or
  (b) patch `run_analyzer` at the module level to return a synthetic JSON
      payload, then call `emit_violations` directly to verify threshold logic.

The subprocess-level integration is kept as a single smoke test that passes
`--scan-root /nonexistent` (the script exits 0 before touching Dart).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Module import — mirror the sys.path pattern used in the rest of the suite
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
import check_complexity as cc  # type: ignore[import-not-found]  # runtime path; mypy cannot follow sys.path manipulation

SCRIPT = Path(__file__).parent.parent / "quality" / "check_complexity.py"
PROJECT_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_payload(
    *,
    path: str = "lib/fake.dart",
    name: str = "fakeFunc",
    kind: str = "function",
    line: int = 1,
    cyclomatic: int = 1,
    parameters: int = 0,
    sloc: int = 1,
    max_nesting: int = 0,
) -> dict[str, Any]:
    """Build a minimal JSON payload as the Dart helper would produce."""
    return {
        "version": 1,
        "files": [
            {
                "path": str(PROJECT_ROOT / path),
                "functions": [
                    {
                        "name": name,
                        "kind": kind,
                        "line": line,
                        "cyclomatic": cyclomatic,
                        "parameters": parameters,
                        "sloc": sloc,
                        "max_nesting": max_nesting,
                    }
                ],
            }
        ],
    }


# ---------------------------------------------------------------------------
# Threshold constants — verify they match REQ-PROC-046 AC-02
# ---------------------------------------------------------------------------

def test_threshold_cyclomatic_matches_ac02() -> None:
    """Cyclomatic complexity threshold must be ≤ 20 per AC-02."""
    assert cc.THRESHOLD_CYCLOMATIC == 20


def test_threshold_parameters_matches_ac02() -> None:
    """Parameter count threshold must be ≤ 4 per AC-02."""
    assert cc.THRESHOLD_PARAMETERS == 4


def test_threshold_sloc_matches_ac02() -> None:
    """Source-lines-of-code threshold must be ≤ 50 per AC-02."""
    assert cc.THRESHOLD_SLOC == 50


def test_threshold_nesting_matches_ac02() -> None:
    """Control-flow nesting threshold must be ≤ 5 per AC-02."""
    assert cc.THRESHOLD_NESTING == 5


# ---------------------------------------------------------------------------
# emit_violations — unit tests with mocked payloads
# ---------------------------------------------------------------------------

def test_emit_violations_clean_passes(capsys: Any) -> None:
    """A function at exactly the thresholds is NOT a violation."""
    payload = _make_payload(
        cyclomatic=cc.THRESHOLD_CYCLOMATIC,
        parameters=cc.THRESHOLD_PARAMETERS,
        sloc=cc.THRESHOLD_SLOC,
        max_nesting=cc.THRESHOLD_NESTING,
    )
    count = cc.emit_violations(payload, excluded=[])
    assert count == 0


def test_emit_violations_cyclomatic_too_high(capsys: Any) -> None:
    """Cyclomatic complexity above threshold is flagged."""
    payload = _make_payload(cyclomatic=cc.THRESHOLD_CYCLOMATIC + 1)
    count = cc.emit_violations(payload, excluded=[])
    assert count >= 1
    captured = capsys.readouterr()
    assert "cyclomatic complexity" in captured.out


def test_emit_violations_parameters_too_many(capsys: Any) -> None:
    """More parameters than threshold is flagged."""
    payload = _make_payload(parameters=cc.THRESHOLD_PARAMETERS + 1)
    count = cc.emit_violations(payload, excluded=[])
    assert count >= 1
    captured = capsys.readouterr()
    assert "parameters" in captured.out


def test_emit_violations_sloc_too_high(capsys: Any) -> None:
    """SLOC above threshold is flagged."""
    payload = _make_payload(sloc=cc.THRESHOLD_SLOC + 1)
    count = cc.emit_violations(payload, excluded=[])
    assert count >= 1
    captured = capsys.readouterr()
    assert "sloc" in captured.out


def test_emit_violations_nesting_too_deep(capsys: Any) -> None:
    """Control-flow nesting above threshold is flagged."""
    payload = _make_payload(max_nesting=cc.THRESHOLD_NESTING + 1)
    count = cc.emit_violations(payload, excluded=[])
    assert count >= 1
    captured = capsys.readouterr()
    assert "max_nesting" in captured.out


def test_emit_violations_multiple_metrics_each_counted(capsys: Any) -> None:
    """Every exceeded metric produces its own violation line."""
    payload = _make_payload(
        cyclomatic=cc.THRESHOLD_CYCLOMATIC + 5,
        parameters=cc.THRESHOLD_PARAMETERS + 5,
        sloc=cc.THRESHOLD_SLOC + 5,
        max_nesting=cc.THRESHOLD_NESTING + 5,
    )
    count = cc.emit_violations(payload, excluded=[])
    assert count == 4  # one per metric


def test_constructor_exempt_from_strict_param_limit(capsys: Any) -> None:
    """A constructor with >4 but <=15 params is NOT a violation."""
    payload = _make_payload(
        name="MyEntity",
        kind="constructor",
        parameters=8,
    )
    count = cc.emit_violations(payload, excluded=[])
    assert count == 0


def test_constructor_above_relaxed_limit_is_violation(capsys: Any) -> None:
    """A constructor exceeding the relaxed threshold IS flagged."""
    payload = _make_payload(
        name="HugeClass",
        kind="constructor",
        parameters=cc.THRESHOLD_CONSTRUCTOR_PARAMETERS + 1,
    )
    count = cc.emit_violations(payload, excluded=[])
    assert count >= 1
    captured = capsys.readouterr()
    assert "parameters" in captured.out


def test_copyWith_exempt_from_strict_param_limit(capsys: Any) -> None:
    """copyWith methods mirror constructor params — exempt from strict limit."""
    payload = _make_payload(
        name="copyWith",
        kind="method",
        parameters=8,
    )
    count = cc.emit_violations(payload, excluded=[])
    assert count == 0


def test_create_factory_exempt_from_strict_param_limit(capsys: Any) -> None:
    """Factory create methods are exempt from strict param limit."""
    payload = _make_payload(
        name="create",
        kind="method",
        parameters=7,
    )
    count = cc.emit_violations(payload, excluded=[])
    assert count == 0


def test_regular_method_still_gated_at_4_params(capsys: Any) -> None:
    """A regular method with >4 params IS a violation."""
    payload = _make_payload(
        name="doSomething",
        kind="method",
        parameters=5,
    )
    count = cc.emit_violations(payload, excluded=[])
    assert count >= 1
    captured = capsys.readouterr()
    assert "parameters" in captured.out


def test_emit_violations_excluded_path_skipped(capsys: Any) -> None:
    """A path that matches an exclusion pattern is not flagged."""
    payload = _make_payload(
        path="lib/generated/foo.dart",
        cyclomatic=cc.THRESHOLD_CYCLOMATIC + 99,
    )
    count = cc.emit_violations(payload, excluded=["lib/generated/"])
    assert count == 0


# ---------------------------------------------------------------------------
# main() — integration via patched run_analyzer
# ---------------------------------------------------------------------------

def test_main_returns_0_when_no_violations() -> None:
    """main() returns 0 when run_analyzer reports no violations."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        scan_root = Path(tmp) / "lib"
        scan_root.mkdir()
        clean_payload: dict[str, Any] = {"version": 1, "files": []}
        with patch.object(cc, "run_analyzer", return_value=clean_payload):
            rc = cc.main(["--scan-root", str(scan_root)])
    assert rc == 0


def test_main_returns_1_when_violations_present() -> None:
    """main() returns 1 when run_analyzer reports a violation."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        scan_root = Path(tmp) / "lib"
        scan_root.mkdir()
        bad_payload = _make_payload(
            path=str(scan_root / "bad.dart"),
            cyclomatic=cc.THRESHOLD_CYCLOMATIC + 1,
        )
        # Override the path so it matches the (tmp) scan root, not PROJECT_ROOT
        bad_payload["files"][0]["path"] = str(scan_root / "bad.dart")
        with patch.object(cc, "run_analyzer", return_value=bad_payload):
            rc = cc.main(["--scan-root", str(scan_root)])
    assert rc == 1


# ---------------------------------------------------------------------------
# Subprocess smoke test — missing scan root exits 0
# ---------------------------------------------------------------------------

def test_subprocess_missing_scan_root_exits_0() -> None:
    """Passing a non-existent --scan-root exits 0 (nothing to scan notice)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--scan-root", "/nonexistent_dir_12345"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "NOTICE" in result.stderr or result.returncode == 0
