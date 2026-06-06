#!/usr/bin/env python3
"""Regression tests for scripts/util/should_use_agents.py.

Pins observable behaviour of _parse_frontmatter, find_packages_for_release,
and compute_verdict before swapping the hand-rolled parser to
scripts.util.yaml_frontmatter (TASK-PROC-051-04 / G4).
"""

from pathlib import Path

import pytest

from scripts.util import should_use_agents as sua

# ---------------------------------------------------------------------------
# _parse_frontmatter contract — returns dict on success, None on absence
# ---------------------------------------------------------------------------


def test_parse_frontmatter_returns_dict_for_valid_input() -> None:
    text = (
        "---\n"
        "task_id: TASK-001\n"
        "status: pending\n"
        "---\n"
        "\n"
        "Body\n"
    )
    result = sua._parse_frontmatter(text)
    assert isinstance(result, dict)
    assert result["task_id"] == "TASK-001"
    assert result["status"] == "pending"


def test_parse_frontmatter_returns_none_for_no_frontmatter() -> None:
    text = "# Just a markdown file\n\nNo YAML header.\n"
    assert sua._parse_frontmatter(text) is None


def test_parse_frontmatter_handles_packages_list() -> None:
    text = (
        "---\n"
        "packages:\n"
        "  - id: PKG-001\n"
        "    assigned_release: 1.0.0\n"
        "  - id: PKG-002\n"
        "    assigned_release: 1.1.0\n"
        "---\n"
    )
    result = sua._parse_frontmatter(text)
    assert result is not None
    pkgs = result["packages"]
    assert isinstance(pkgs, list)
    assert len(pkgs) == 2
    # Each item is a dict with id + assigned_release
    assert pkgs[0]["id"] == "PKG-001"
    assert pkgs[0]["assigned_release"] == "1.0.0"
    assert pkgs[1]["id"] == "PKG-002"


def test_parse_frontmatter_strips_bom() -> None:
    text = "﻿---\ntask_id: TASK-001\n---\n\nBody\n"
    result = sua._parse_frontmatter(text)
    assert result is not None
    assert result["task_id"] == "TASK-001"


# ---------------------------------------------------------------------------
# find_packages_for_release end-to-end against a fake RELEASE_BACKLOG file
# ---------------------------------------------------------------------------


def test_find_packages_for_release_filters_by_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backlog = tmp_path / "RELEASE_BACKLOG.md"
    backlog.write_text(
        "---\n"
        "packages:\n"
        "  - id: PKG-A\n"
        "    assigned_release: 1.0.0\n"
        "  - id: PKG-B\n"
        "    assigned_release: 1.1.0\n"
        "  - id: PKG-C\n"
        "    assigned_release: 1.0.0\n"
        "---\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(sua, "RELEASE_BACKLOG_FILE", backlog)

    result = sua.find_packages_for_release("1.0.0")
    assert sorted(result) == ["PKG-A", "PKG-C"]

    result = sua.find_packages_for_release("1.1.0")
    assert result == ["PKG-B"]

    result = sua.find_packages_for_release("9.9.9")
    assert result == []


def test_find_packages_for_release_missing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sua, "RELEASE_BACKLOG_FILE", tmp_path / "missing.md")
    assert sua.find_packages_for_release("1.0.0") == []


# ---------------------------------------------------------------------------
# compute_verdict — pure function
# ---------------------------------------------------------------------------


def test_compute_verdict_thresholds() -> None:
    assert sua.compute_verdict(0, 0) == "orchestrator_direct"
    assert sua.compute_verdict(30 * 1024, 5) == "orchestrator_direct"
    assert sua.compute_verdict(30 * 1024 + 1, 5) == "agents_required"
    assert sua.compute_verdict(0, 6) == "agents_required"
