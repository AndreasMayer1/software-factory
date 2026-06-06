#!/usr/bin/env python3
"""Regression tests for scripts/requirements/check_requirement_implementation.py.

Pins _parse_frontmatter behavior before/after swapping the hand-rolled parser
to scripts.util.yaml_frontmatter (TASK-PROC-051-04 / G4).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "requirements" / "check_requirement_implementation.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "cri_under_test", MODULE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return _load_module()


def test_parse_frontmatter_basic(mod: Any) -> None:
    content = "---\nid: REQ-FUNC-007\nstatus: active\n---\nBody\n"
    out = mod._parse_frontmatter(content)
    assert out is not None
    assert out.get("id") == "REQ-FUNC-007"


def test_parse_frontmatter_strips_bom(mod: Any) -> None:
    content = "﻿---\nid: REQ-X\n---\nbody\n"
    out = mod._parse_frontmatter(content)
    assert out is not None
    assert out.get("id") == "REQ-X"


def test_parse_frontmatter_none_when_absent(mod: Any) -> None:
    assert mod._parse_frontmatter("body only\n") is None


def test_extract_acs_handles_multiple_patterns(mod: Any) -> None:
    body = (
        "---\nid: REQ-FUNC-001\n---\n\n"
        "- [ ] AC-01: First criterion text\n"
        "**AC-02**: Bold criterion text\n"
        "### AC-03\nSome description\n"
        "AC-04: Bare criterion\n"
    )
    acs = mod.extract_acs(body)
    ids = [a["id"] for a in acs]
    assert ids == ["AC-01", "AC-02", "AC-03", "AC-04"]


def test_compute_verdict_levels(mod: Any) -> None:
    assert mod.compute_verdict([]) == "likely_missing"
    assert mod.compute_verdict(["a.dart"]) == "uncertain"
    assert mod.compute_verdict(["a.dart", "b.dart"]) == "likely_implemented"
