"""Tests for scripts/release/check_dependency_sweep.py."""

import importlib.util
import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Load module under test directly (avoids import-path issues).
_MODULE_PATH = Path(__file__).resolve().parent.parent / "release" / "check_dependency_sweep.py"
_spec = importlib.util.spec_from_file_location("check_dependency_sweep", _MODULE_PATH)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_count_advisories = _mod._count_advisories
_scan_lockfile = _mod._scan_lockfile
main = _mod.main


# ---------------------------------------------------------------------------
# _count_advisories
# ---------------------------------------------------------------------------


def test_count_advisories_empty_results() -> None:
    assert _count_advisories({}) == []
    assert _count_advisories({"results": []}) == []


def test_count_advisories_no_vulns() -> None:
    data: dict[str, Any] = {
        "results": [
            {
                "packages": [
                    {
                        "package": {"name": "foo", "version": "1.0.0"},
                        "vulnerabilities": [],
                    }
                ]
            }
        ]
    }
    assert _count_advisories(data) == []


def test_count_advisories_one_vuln() -> None:
    data: dict[str, Any] = {
        "results": [
            {
                "packages": [
                    {
                        "package": {"name": "bar", "version": "2.3.1"},
                        "vulnerabilities": [
                            {
                                "id": "GHSA-xxxx-yyyy-zzzz",
                                "summary": "Critical RCE",
                                "aliases": ["CVE-2024-1234"],
                            }
                        ],
                    }
                ]
            }
        ]
    }
    result = _count_advisories(data)
    assert len(result) == 1
    assert "bar@2.3.1" in result[0]
    assert "GHSA-xxxx-yyyy-zzzz" in result[0]
    assert "CVE-2024-1234" in result[0]
    assert "Critical RCE" in result[0]


def test_count_advisories_multiple_vulns_one_package() -> None:
    data: dict[str, Any] = {
        "results": [
            {
                "packages": [
                    {
                        "package": {"name": "baz", "version": "0.9.0"},
                        "vulnerabilities": [
                            {"id": "GHSA-aaa", "summary": "First", "aliases": []},
                            {"id": "GHSA-bbb", "summary": "Second", "aliases": []},
                        ],
                    }
                ]
            }
        ]
    }
    result = _count_advisories(data)
    assert len(result) == 2


def test_count_advisories_no_aliases() -> None:
    data: dict[str, Any] = {
        "results": [
            {
                "packages": [
                    {
                        "package": {"name": "pkg", "version": "1.0.0"},
                        "vulnerabilities": [
                            {"id": "GHSA-nnn", "summary": "Desc", "aliases": []},
                        ],
                    }
                ]
            }
        ]
    }
    result = _count_advisories(data)
    assert len(result) == 1
    # No parenthesised aliases in the output
    assert "(" not in result[0].split("\n")[0]


# ---------------------------------------------------------------------------
# _scan_lockfile — patches subprocess.run
# ---------------------------------------------------------------------------


def test_scan_lockfile_returns_parsed_json(tmp_path: Path) -> None:
    fake_json: dict[str, Any] = {"results": [], "experimental_config": {}}
    fake_lockfile = tmp_path / "pubspec.lock"
    fake_lockfile.write_text("fake")

    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(fake_json)
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        rc, data = _scan_lockfile(fake_lockfile)

    assert rc == 0
    assert data == fake_json


def test_scan_lockfile_invalid_json_returns_empty(tmp_path: Path) -> None:
    fake_lockfile = tmp_path / "pubspec.lock"
    fake_lockfile.write_text("fake")

    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "not valid json"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        rc, data = _scan_lockfile(fake_lockfile)

    assert rc == 1
    assert data == {}


def test_scan_lockfile_empty_stdout_returns_empty(tmp_path: Path) -> None:
    fake_lockfile = tmp_path / "pubspec.lock"
    fake_lockfile.write_text("fake")

    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        rc, data = _scan_lockfile(fake_lockfile)

    assert rc == 0
    assert data == {}


# ---------------------------------------------------------------------------
# main() integration — patches shutil.which and subprocess.run
# ---------------------------------------------------------------------------


def _make_run_side_effect(
    *,
    osv_version: str = "osv-scanner version: 2.3.8\n",
    osv_scan_json: dict[str, Any] | None = None,
    flutter_out: str = "No dependencies",
) -> Any:
    """Build a side_effect callable for subprocess.run used in main() tests."""
    if osv_scan_json is None:
        osv_scan_json = {"results": [], "experimental_config": {}}

    resolved_json = osv_scan_json

    def side_effect(cmd: list[str], **kwargs: Any) -> MagicMock:
        result = MagicMock()
        result.stderr = ""
        if cmd[0] == "osv-scanner" and "--version" in cmd:
            result.returncode = 0
            result.stdout = osv_version
        elif cmd[0] == "osv-scanner" and "scan" in cmd:
            result.returncode = 0
            result.stdout = json.dumps(resolved_json)
        elif cmd[0] == "flutter":
            result.returncode = 0
            result.stdout = flutter_out
        else:
            result.returncode = 0
            result.stdout = ""
        return result

    return side_effect


def test_main_clean_sweep_exits_0(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pubspec = tmp_path / "pubspec.lock"
    pubspec.write_text("fake")

    with (
        patch.object(_mod, "PROJECT_ROOT", tmp_path),
        patch("shutil.which", return_value="/usr/local/bin/osv-scanner"),
        patch("subprocess.run", side_effect=_make_run_side_effect()),
        pytest.raises(SystemExit) as exc,
    ):
        main()

    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "[PASS]" in captured.out


def test_main_advisory_found_exits_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pubspec = tmp_path / "pubspec.lock"
    pubspec.write_text("fake")

    advisory_json: dict[str, Any] = {
        "results": [
            {
                "packages": [
                    {
                        "package": {"name": "evil_pkg", "version": "1.0.0"},
                        "vulnerabilities": [
                            {"id": "GHSA-evil", "summary": "Bad vuln", "aliases": ["CVE-9999"]}
                        ],
                    }
                ]
            }
        ]
    }

    with (
        patch.object(_mod, "PROJECT_ROOT", tmp_path),
        patch("shutil.which", return_value="/usr/local/bin/osv-scanner"),
        patch("subprocess.run", side_effect=_make_run_side_effect(osv_scan_json=advisory_json)),
        pytest.raises(SystemExit) as exc,
    ):
        main()

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "[FAIL]" in captured.out
    assert "evil_pkg" in captured.out


def test_main_osv_not_installed_exits_1(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("shutil.which", return_value=None), pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "not installed" in captured.out
