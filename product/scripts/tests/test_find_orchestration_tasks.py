#!/usr/bin/env python3
"""Regression tests for scripts/tasks/find_orchestration_tasks.py.

Pins _parse_frontmatter + is_orchestration_task + find_orchestration_tasks
contract before swapping the parser to the central helper.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "tasks" / "find_orchestration_tasks.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("fot_under_test", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return _load_module()


def test_parse_basic(mod: Any) -> None:
    out = mod._parse_frontmatter("---\ntask_id: TASK-X\n---\n")
    assert out is not None
    assert out.get("task_id") == "TASK-X"


def test_parse_bom(mod: Any) -> None:
    out = mod._parse_frontmatter("﻿---\ntask_id: TASK-Y\n---\n")
    assert out is not None
    assert out.get("task_id") == "TASK-Y"


def test_is_orchestration_task_both_conditions(mod: Any) -> None:
    assert mod.is_orchestration_task(
        {"target_release": "0.1.0", "scope_description": "Orchestration: blah"}
    )


def test_is_orchestration_task_missing_release(mod: Any) -> None:
    assert not mod.is_orchestration_task(
        {"target_release": "", "scope_description": "Orchestration: blah"}
    )


def test_is_orchestration_task_wrong_prefix(mod: Any) -> None:
    assert not mod.is_orchestration_task(
        {"target_release": "0.1.0", "scope_description": "Something else"}
    )


def test_find_filters_by_status_and_release(mod: Any, tmp_path: Path) -> None:
    # Build a tiny synthetic tree
    t1 = tmp_path / "t1" / "goal.md"
    t1.parent.mkdir(parents=True)
    t1.write_text(
        "---\n"
        "task_id: TASK-A\n"
        "status: pending\n"
        "target_release: \"0.1.0\"\n"
        "scope_description: \"Orchestration: alpha\"\n"
        "---\n",
        encoding="utf-8",
    )
    t2 = tmp_path / "t2" / "goal.md"
    t2.parent.mkdir(parents=True)
    t2.write_text(
        "---\n"
        "task_id: TASK-B\n"
        "status: completed\n"
        "target_release: \"0.1.0\"\n"
        "scope_description: \"Orchestration: beta\"\n"
        "---\n",
        encoding="utf-8",
    )

    all_tasks = mod.find_orchestration_tasks(root=tmp_path)
    ids = sorted(t["task_id"] for t in all_tasks)
    assert ids == ["TASK-A", "TASK-B"]

    only_pending = mod.find_orchestration_tasks(status="pending", root=tmp_path)
    assert [t["task_id"] for t in only_pending] == ["TASK-A"]
