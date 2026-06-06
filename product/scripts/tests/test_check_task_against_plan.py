#!/usr/bin/env python3
"""Regression tests for scripts/tasks/check_task_against_plan.py.

Pins _parse_frontmatter behavior + effort_conformant + check_conformance
contract before swapping the hand-rolled parser to the central helper.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "tasks" / "check_task_against_plan.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("ctap_under_test", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return _load_module()


def test_parse_fm_basic(mod: Any) -> None:
    out = mod._parse_frontmatter("---\ntask_id: TASK-A\n---\nbody\n")
    assert out is not None
    assert out.get("task_id") == "TASK-A"


def test_parse_fm_bom(mod: Any) -> None:
    out = mod._parse_frontmatter("﻿---\ntask_id: TASK-B\n---\n")
    assert out is not None
    assert out.get("task_id") == "TASK-B"


def test_parse_fm_none_when_absent(mod: Any) -> None:
    assert mod._parse_frontmatter("plain text\n") is None


def test_effort_conformant_levels(mod: Any) -> None:
    assert mod.effort_conformant("M", "M") == (True, False)
    assert mod.effort_conformant("M", "S") == (True, True)  # +/-1 warn
    assert mod.effort_conformant("M", "L") == (True, True)
    assert mod.effort_conformant("XS", "L") == (False, False)
    assert mod.effort_conformant("M", "huh") == (False, False)


def test_check_conformance_target_package_pass(mod: Any) -> None:
    goal = {
        "target_package": "Pkg A",
        "covers": {"acceptance_criteria": ["AC-01"]},
        "effort": "M",
    }
    plan = {
        "target_package": "Pkg A",
        "covers_acs": ["AC-01"],
        "effort": "M",
    }
    results = mod.check_conformance(goal, plan)
    by_field = {r["field"]: r["status"] for r in results}
    assert by_field["target_package"] == "PASS"
    assert by_field["covers_acs"] == "PASS"
    assert by_field["effort"] == "PASS"
