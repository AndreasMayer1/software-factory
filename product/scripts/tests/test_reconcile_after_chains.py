#!/usr/bin/env python3
"""Regression tests for scripts/tasks/reconcile_after_chains.py.

Pins _parse_frontmatter + _parse_after_from_yaml + _update_after_field
contract before swapping the parser to the central helper.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "tasks" / "reconcile_after_chains.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("rac_under_test", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return _load_module()


def test_parse_fm_basic(mod: Any) -> None:
    out = mod._parse_frontmatter("---\ntask_id: TASK-A\n---\n")
    assert out is not None
    assert out.get("task_id") == "TASK-A"


def test_parse_fm_bom(mod: Any) -> None:
    out = mod._parse_frontmatter("﻿---\ntask_id: TASK-B\n---\n")
    assert out is not None
    assert out.get("task_id") == "TASK-B"


def test_parse_after_inline(mod: Any) -> None:
    yaml_text = "task_id: TASK-A\nafter: [TASK-B, TASK-C]\n"
    assert mod._parse_after_from_yaml(yaml_text) == ["TASK-B", "TASK-C"]


def test_parse_after_block(mod: Any) -> None:
    yaml_text = "task_id: TASK-A\nafter:\n  - TASK-B\n  - TASK-C\nnext: foo\n"
    assert mod._parse_after_from_yaml(yaml_text) == ["TASK-B", "TASK-C"]


def test_parse_after_empty_inline(mod: Any) -> None:
    yaml_text = "after: []\n"
    assert mod._parse_after_from_yaml(yaml_text) == []


def test_update_after_field_inline_merge(mod: Any) -> None:
    yaml_text = "task_id: TASK-A\nafter: [TASK-B]\nstatus: pending\n"
    updated = mod._update_after_field(yaml_text, ["TASK-C", "TASK-B"])
    # Should preserve order: existing first, new items deduped
    assert "after: [TASK-B, TASK-C]" in updated
