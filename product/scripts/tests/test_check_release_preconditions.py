#!/usr/bin/env python3
"""Regression tests for scripts/release/check_release_preconditions.py.

Pins observable behaviour of get_active_release_version and parse_frontmatter
before swapping the hand-rolled parsers to scripts.util.yaml_frontmatter
(TASK-PROC-051-04 / G4).
"""

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from scripts.release import check_release_preconditions as m

# ---------------------------------------------------------------------------
# get_active_release_version — reads RELEASES.md frontmatter
# ---------------------------------------------------------------------------


def test_get_active_release_version_returns_active(tmp_path: Path) -> None:
    rel = tmp_path / "requirements_tasks"
    rel.mkdir(parents=True)
    (rel / "RELEASES.md").write_text(
        "---\n"
        "releases:\n"
        '  - version: "1.0.0"\n'
        "    status: planned\n"
        '  - version: "1.1.0"\n'
        "    status: active\n"
        '  - version: "2.0.0"\n'
        "    status: planned\n"
        "---\n"
        "\nbody\n",
        encoding="utf-8",
    )
    with patch.object(m, "PROJECT_ROOT", tmp_path):
        assert m.get_active_release_version() == "1.1.0"


def test_get_active_release_version_returns_none_when_no_active(tmp_path: Path) -> None:
    rel = tmp_path / "requirements_tasks"
    rel.mkdir(parents=True)
    (rel / "RELEASES.md").write_text(
        "---\n"
        "releases:\n"
        '  - version: "1.0.0"\n'
        "    status: planned\n"
        "---\n",
        encoding="utf-8",
    )
    with patch.object(m, "PROJECT_ROOT", tmp_path):
        assert m.get_active_release_version() is None


def test_get_active_release_version_returns_none_for_missing_file(tmp_path: Path) -> None:
    with patch.object(m, "PROJECT_ROOT", tmp_path):
        assert m.get_active_release_version() is None


# ---------------------------------------------------------------------------
# parse_frontmatter — used to scan goal.md files for release_description
# ---------------------------------------------------------------------------


def test_parse_frontmatter_returns_none_for_no_delimiter() -> None:
    assert m.parse_frontmatter("# heading\n\nbody\n") is None


def test_parse_frontmatter_extracts_scalars() -> None:
    text = (
        "---\n"
        "task_id: T1\n"
        "type: impl\n"
        'target_release: "1.0.0"\n'
        'release_description: "Feature X"\n'
        "status: in_progress\n"
        "---\n"
        "body\n"
    )
    meta = m.parse_frontmatter(text)
    assert meta is not None
    assert meta["task_id"] == "T1"
    assert meta["type"] == "impl"
    assert meta["target_release"] == "1.0.0"
    assert meta["release_description"] == "Feature X"
    assert meta["status"] == "in_progress"


def test_parse_frontmatter_strips_bom() -> None:
    text = "﻿---\ntask_id: T2\n---\n"
    meta = m.parse_frontmatter(text)
    assert meta is not None
    assert meta["task_id"] == "T2"


def test_parse_frontmatter_handles_inline_list() -> None:
    text = (
        "---\n"
        "task_id: T3\n"
        "after: [TASK-001, TASK-002]\n"
        "---\n"
    )
    meta = m.parse_frontmatter(text)
    assert meta is not None
    assert list(meta["after"]) == ["TASK-001", "TASK-002"]


# ---------------------------------------------------------------------------
# Dependency sweep gate (Check 4e) — tests added for REQ-PROC-061 AC-03
# ---------------------------------------------------------------------------


def _setup_minimal_root(tmp_path: Path, *, sweep_script_exists: bool = True) -> None:
    """Write the minimal file tree so main() can reach Check 4e."""
    rt = tmp_path / "requirements_tasks"
    rt.mkdir(parents=True)
    (rt / "RELEASES.md").write_text(
        '---\nreleases:\n  - version: "1.0.0"\n    status: active\n---\n',
        encoding="utf-8",
    )
    (tmp_path / "pubspec.yaml").write_text("version: 0.0.0\n", encoding="utf-8")
    canon_dir = tmp_path / "scripts" / "user_needs"
    canon_dir.mkdir(parents=True)
    (canon_dir / "check_canon.py").touch()
    sweep_dir = tmp_path / "scripts" / "release"
    sweep_dir.mkdir(parents=True)
    if sweep_script_exists:
        (sweep_dir / "check_dependency_sweep.py").touch()


def _run_side_effect(*, sweep_exit: int = 0) -> Any:
    """Return a side_effect for m.run that passes every check except sweep per sweep_exit."""

    def side_effect(cmd: list[str], cwd: Any = None) -> tuple[int, str]:
        joined = " ".join(str(c) for c in cmd)
        if "rev-parse" in joined:
            return 0, "develop"
        if "status --porcelain" in joined:
            return 0, ""
        # check script-specific paths before "flutter" — the uv venv python lives
        # inside flutter_app/.venv so sys.executable contains "flutter"
        if "next_tasks" in joined:
            return 0, "Open tasks: 0"
        if "check_dependency_sweep" in joined:
            msg = "[PASS] clean" if sweep_exit == 0 else "[FAIL] advisory found"
            return sweep_exit, msg
        if "check_canon" in joined:
            return 0, ""
        if "flutter" in joined:
            return 0, ""
        return 0, ""

    return side_effect


def test_sweep_gate_missing_script_fails_preconditions(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _setup_minimal_root(tmp_path, sweep_script_exists=False)
    with (
        patch.object(m, "PROJECT_ROOT", tmp_path),
        patch.object(m, "run", side_effect=_run_side_effect()),
        patch.object(m, "check_line_coverage", return_value=(True, 80.0)),
        patch.object(m, "find_goal_files", return_value=[]),
        pytest.raises(SystemExit) as exc,
    ):
        m.main()
    assert exc.value.code == 1
    assert "dependency sweep: FAIL" in capsys.readouterr().out


def test_sweep_gate_nonzero_exit_fails_preconditions(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _setup_minimal_root(tmp_path)
    with (
        patch.object(m, "PROJECT_ROOT", tmp_path),
        patch.object(m, "run", side_effect=_run_side_effect(sweep_exit=1)),
        patch.object(m, "check_line_coverage", return_value=(True, 80.0)),
        patch.object(m, "find_goal_files", return_value=[]),
        pytest.raises(SystemExit) as exc,
    ):
        m.main()
    assert exc.value.code == 1
    assert "dependency sweep: FAIL" in capsys.readouterr().out


def test_sweep_gate_zero_exit_passes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _setup_minimal_root(tmp_path)
    with (
        patch.object(m, "PROJECT_ROOT", tmp_path),
        patch.object(m, "run", side_effect=_run_side_effect(sweep_exit=0)),
        patch.object(m, "check_line_coverage", return_value=(True, 80.0)),
        patch.object(m, "find_goal_files", return_value=[]),
        pytest.raises(SystemExit) as exc,
    ):
        m.main()
    assert exc.value.code == 0
    assert "dependency sweep: PASS" in capsys.readouterr().out
