#!/usr/bin/env python3
"""Regression tests for scripts/requirements/check_ac_coverage.py.

Pins parse_frontmatter, load_required_acs, and load_covered_acs behavior
before swapping the hand-rolled parser to scripts.util.yaml_frontmatter
(TASK-PROC-051-04 / G4).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "requirements" / "check_ac_coverage.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "check_ac_coverage_under_test", MODULE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return _load_module()


def _write(p: Path, text: str) -> None:
    p.write_text(text, encoding="utf-8")


def test_parse_frontmatter_returns_dict(mod: Any) -> None:
    content = (
        "---\n"
        "id: REQ-FUNC-001\n"
        "status: active\n"
        "---\n"
        "Body.\n"
    )
    out = mod.parse_frontmatter(content)
    assert isinstance(out, dict)
    assert out.get("id") == "REQ-FUNC-001"
    assert out.get("status") == "active"


def test_parse_frontmatter_no_frontmatter_returns_none(mod: Any) -> None:
    assert mod.parse_frontmatter("# Plain doc\nno fm\n") is None


def test_parse_frontmatter_strips_bom(mod: Any) -> None:
    content = "﻿---\nid: REQ-X\n---\nbody\n"
    out = mod.parse_frontmatter(content)
    assert out is not None
    assert out.get("id") == "REQ-X"


def test_load_required_acs_filters_by_package(mod: Any, tmp_path: Path) -> None:
    req_dir = tmp_path / "feat_x"
    req_dir.mkdir()
    f = req_dir / "requirements.md"
    _write(
        f,
        "---\n"
        "id: REQ-FUNC-100\n"
        "trackable_items:\n"
        "  acceptance_criteria:\n"
        "    - id: AC-01\n"
        "      target_package: \"Pkg A\"\n"
        "    - id: AC-02\n"
        "      target_package: \"Pkg B\"\n"
        "    - id: AC-03\n"
        "      target_package: \"Pkg A\"\n"
        "---\nbody\n",
    )
    out = mod.load_required_acs("Pkg A", [f])
    assert out == {"REQ-FUNC-100": ["AC-01", "AC-03"]}


def test_load_covered_acs_skips_terminal(mod: Any, tmp_path: Path) -> None:
    g1 = tmp_path / "g1.md"
    g2 = tmp_path / "g2.md"
    _write(
        g1,
        "---\n"
        "task_id: TASK-FUNC-100-01\n"
        "parent_requirement: REQ-FUNC-100\n"
        "status: in_progress\n"
        "covers:\n"
        "  acceptance_criteria: [AC-01, AC-02]\n"
        "---\n",
    )
    _write(
        g2,
        "---\n"
        "task_id: TASK-FUNC-100-02\n"
        "parent_requirement: REQ-FUNC-100\n"
        "status: completed\n"
        "covers:\n"
        "  acceptance_criteria: [AC-03]\n"
        "---\n",
    )
    out = mod.load_covered_acs([g1, g2])
    # AC-03 from terminal task should be filtered out
    assert ("REQ-FUNC-100", "AC-01") in out
    assert ("REQ-FUNC-100", "AC-02") in out
    assert ("REQ-FUNC-100", "AC-03") not in out
