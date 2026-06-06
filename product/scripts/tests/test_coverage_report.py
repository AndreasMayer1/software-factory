#!/usr/bin/env python3
"""Regression tests for scripts/requirements/coverage_report.py.

Pins parse_yaml_frontmatter behavior and end-to-end scan_requirements +
scan_tasks against synthetic fixtures before swapping the hand-rolled parser
to scripts.util.yaml_frontmatter (TASK-PROC-051-04 / G4).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "requirements" / "coverage_report.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("coverage_report_under_test", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return _load_module()


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_parse_returns_none_without_fm(mod: Any) -> None:
    rep = mod.CoverageReporter(Path("/tmp"))
    assert rep.parse_yaml_frontmatter("# no fm\n") is None


def test_parse_extracts_id_status(mod: Any) -> None:
    rep = mod.CoverageReporter(Path("/tmp"))
    content = "---\nid: REQ-FUNC-100\nstatus: defined\n---\nbody\n"
    meta = rep.parse_yaml_frontmatter(content)
    assert meta is not None
    assert meta.get("id") == "REQ-FUNC-100"
    assert meta.get("status") == "defined"


def test_scan_requirements_and_tasks_links(mod: Any, tmp_path: Path) -> None:
    base = tmp_path
    req_dir = base / "requirements_tasks" / "functional" / "feat_x"
    req_file = req_dir / "requirements.md"
    _write(
        req_file,
        "---\n"
        "id: REQ-FUNC-200\n"
        "status: active\n"
        "trackable_items:\n"
        "  acceptance_criteria:\n"
        "    - id: AC-01\n"
        "      text: First criterion\n"
        "    - id: AC-02\n"
        "      text: Second criterion\n"
        "  sections: []\n"
        "---\n"
        "body\n",
    )

    task_dir = req_dir / "tasks" / "2026-01-01_impl_x"
    _write(
        task_dir / "goal.md",
        "---\n"
        "task_id: TASK-FUNC-200-01\n"
        "parent_requirement: REQ-FUNC-200\n"
        "status: in_progress\n"
        "covers:\n"
        "  acceptance_criteria: [AC-01]\n"
        "  sections: []\n"
        "---\n"
        "body\n",
    )

    rep = mod.CoverageReporter(base)
    rep.scan_requirements()
    rep.scan_tasks()
    assert "REQ-FUNC-200" in rep.requirements
    req = rep.requirements["REQ-FUNC-200"]
    assert "AC-01" in req.acceptance_criteria
    assert "AC-02" in req.acceptance_criteria
    # AC-01 should be covered by the task
    assert req.acceptance_criteria["AC-01"].covered_by == ["TASK-FUNC-200-01"]
    assert req.acceptance_criteria["AC-02"].covered_by == []


def test_value_helpers_unchanged(mod: Any) -> None:
    rep = mod.CoverageReporter(Path("/tmp"))
    assert rep._parse_value("42") == 42
    assert rep._parse_value("true") is True
    assert rep._parse_value("\"quoted\"") == "quoted"
