#!/usr/bin/env python3
"""Regression tests for scripts/requirements/validate_meta.py.

Pins parse_yaml_frontmatter behavior before/after swapping to the central
helper (TASK-PROC-051-04 / G4). Only the YAML parser behavior is locked here;
the larger validation pipeline relies on the same helper transitively.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "requirements" / "validate_meta.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("validate_meta_under_test", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return _load_module()


def test_parse_returns_none_without_fm(mod: Any, tmp_path: Path) -> None:
    v = mod.MetaValidator(tmp_path)
    assert v.parse_yaml_frontmatter("# plain\n") is None


def test_parse_strips_bom(mod: Any, tmp_path: Path) -> None:
    v = mod.MetaValidator(tmp_path)
    out = v.parse_yaml_frontmatter("﻿---\nid: REQ-X\n---\nbody\n")
    assert out is not None
    assert out.get("id") == "REQ-X"


def test_parse_basic_scalars(mod: Any, tmp_path: Path) -> None:
    v = mod.MetaValidator(tmp_path)
    content = (
        "---\n"
        "id: REQ-FUNC-001\n"
        "status: active\n"
        "urgency: 2\n"
        "---\nbody\n"
    )
    out = v.parse_yaml_frontmatter(content)
    assert out is not None
    assert out.get("id") == "REQ-FUNC-001"
    assert out.get("status") == "active"
    assert int(out.get("urgency")) == 2


def test_parse_nested_trackable_items(mod: Any, tmp_path: Path) -> None:
    v = mod.MetaValidator(tmp_path)
    content = (
        "---\n"
        "id: REQ-FUNC-002\n"
        "trackable_items:\n"
        "  acceptance_criteria:\n"
        "    - id: AC-01\n"
        "    - id: AC-02\n"
        "  sections: []\n"
        "---\nbody\n"
    )
    out = v.parse_yaml_frontmatter(content)
    assert out is not None
    trackable = out.get("trackable_items")
    assert isinstance(trackable, dict)
    acs = trackable.get("acceptance_criteria")
    assert isinstance(acs, list)
    assert len(acs) == 2
    # Items may be dict or CommentedMap; check id field
    assert acs[0].get("id") == "AC-01"
    assert acs[1].get("id") == "AC-02"
