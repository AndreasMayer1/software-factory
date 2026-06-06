#!/usr/bin/env python3
"""Regression tests for scripts/artifacts/generate_technical_release_notes.py.

Pins observable behaviour of parse_frontmatter before swapping the hand-rolled
parser to scripts.util.yaml_frontmatter (TASK-PROC-051-04 / G4).

NOTE: PyYAML is NOT installed; pre-migration the script silently used the
buggy _parse_simple_yaml fallback for some shapes. Tests pin the CORRECT
(post-migration) behaviour.
"""

from scripts.artifacts import generate_technical_release_notes as m


def test_parse_frontmatter_returns_none_for_no_delimiter() -> None:
    assert m.parse_frontmatter("# heading\n\nbody\n") is None


def test_parse_frontmatter_strips_bom() -> None:
    text = "﻿---\ntask_id: T1\n---\n"
    meta = m.parse_frontmatter(text)
    assert meta is not None
    assert meta["task_id"] == "T1"


def test_parse_frontmatter_extracts_scalars() -> None:
    text = (
        "---\n"
        "task_id: TASK-PROC-051-04\n"
        "type: impl\n"
        "status: in_progress\n"
        'target_release: "1.0.0"\n'
        'release_description: "Bring scripts/ to passing gates"\n'
        "---\n"
        "body\n"
    )
    meta = m.parse_frontmatter(text)
    assert meta is not None
    assert meta["task_id"] == "TASK-PROC-051-04"
    assert meta["type"] == "impl"
    assert meta["status"] == "in_progress"
    assert meta["target_release"] == "1.0.0"
    assert meta["release_description"] == "Bring scripts/ to passing gates"


def test_parse_frontmatter_extracts_inline_lists() -> None:
    text = (
        "---\n"
        "task_id: T2\n"
        "after: [TASK-001, TASK-002]\n"
        "---\n"
    )
    meta = m.parse_frontmatter(text)
    assert meta is not None
    assert list(meta["after"]) == ["TASK-001", "TASK-002"]
