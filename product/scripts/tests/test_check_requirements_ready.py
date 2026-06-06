#!/usr/bin/env python3
"""Regression tests for scripts/requirements/check_requirements_ready.py.

Pins the observable contract of parse_frontmatter_fields and the main()
exit-code semantics before swapping the hand-rolled parser to
scripts.util.yaml_frontmatter (TASK-PROC-051-04 / G4).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "requirements" / "check_requirements_ready.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "check_requirements_ready_under_test", MODULE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def cr():
    return _load_module()


def _write(p: Path, text: str) -> None:
    p.write_text(text, encoding="utf-8")


def test_parse_extracts_writes_requirements_and_status(tmp_path: Path, cr: Any) -> None:
    f = tmp_path / "goal.md"
    _write(
        f,
        "---\n"
        "task_id: TASK-001\n"
        "writes_requirements: true\n"
        "status: completed\n"
        "type: explore\n"
        "---\n"
        "\n"
        "Body.\n",
    )
    out = cr.parse_frontmatter_fields(str(f), ["writes_requirements", "status"])
    assert out.get("writes_requirements") == "true"
    assert out.get("status") == "completed"


def test_parse_missing_field_absent_in_result(tmp_path: Path, cr: Any) -> None:
    f = tmp_path / "goal.md"
    _write(f, "---\nstatus: pending\n---\nbody\n")
    out = cr.parse_frontmatter_fields(str(f), ["writes_requirements", "status"])
    assert "writes_requirements" not in out
    assert out.get("status") == "pending"


def test_parse_no_frontmatter_returns_empty(tmp_path: Path, cr: Any) -> None:
    f = tmp_path / "goal.md"
    _write(f, "# Plain markdown\n\nNo frontmatter here.\n")
    out = cr.parse_frontmatter_fields(str(f), ["writes_requirements", "status"])
    assert out == {}


def test_parse_unreadable_file_returns_empty(tmp_path: Path, cr: Any) -> None:
    out = cr.parse_frontmatter_fields(
        str(tmp_path / "does-not-exist.md"), ["status"]
    )
    assert out == {}


def test_main_ready_when_one_completed_no_pending( tmp_path: Path, cr: Any, monkeypatch: Any, capsys: Any) -> None:
    base = tmp_path / "requirements_tasks"
    base.mkdir()
    task_dir = base / "task1"
    task_dir.mkdir()
    _write(
        task_dir / "goal.md",
        "---\n"
        "task_id: TASK-A\n"
        "writes_requirements: true\n"
        "status: completed\n"
        "---\n",
    )
    # Patch __file__ via the base path computation
    monkeypatch.setattr(
        cr,
        "find_goal_files",
        lambda b: [str(task_dir / "goal.md")],
    )
    rc = cr.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert "READY" in captured.out


def test_main_not_ready_when_blocking_pending( tmp_path: Path, cr: Any, monkeypatch: Any, capsys: Any) -> None:
    task_dir = tmp_path / "task1"
    task_dir.mkdir()
    _write(
        task_dir / "goal.md",
        "---\n"
        "task_id: TASK-B\n"
        "writes_requirements: true\n"
        "status: in_progress\n"
        "---\n",
    )
    monkeypatch.setattr(
        cr, "find_goal_files", lambda b: [str(task_dir / "goal.md")]
    )
    rc = cr.main()
    captured = capsys.readouterr()
    assert rc == 1
    assert "NOT READY" in captured.out


def test_main_not_ready_when_no_writes_requirements( tmp_path: Path, cr: Any, monkeypatch: Any, capsys: Any) -> None:
    task_dir = tmp_path / "task1"
    task_dir.mkdir()
    _write(
        task_dir / "goal.md",
        "---\n"
        "task_id: TASK-C\n"
        "writes_requirements: false\n"
        "status: completed\n"
        "---\n",
    )
    monkeypatch.setattr(
        cr, "find_goal_files", lambda b: [str(task_dir / "goal.md")]
    )
    rc = cr.main()
    captured = capsys.readouterr()
    assert rc == 1
    assert "NOT READY" in captured.out
