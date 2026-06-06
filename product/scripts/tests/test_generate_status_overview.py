#!/usr/bin/env python3
"""Regression tests for scripts/artifacts/generate_status_overview.py.

Pins observable behaviour of YAMLParser.parse_frontmatter, load_releases,
and load_backlog_packages before the migration to scripts.util.yaml_frontmatter
(TASK-PROC-051-04 / G4).

NOTE: pre-migration the script could not even import (top-level `import yaml`
with PyYAML absent). Tests pin post-migration semantics.
"""

from pathlib import Path
from unittest.mock import patch

from scripts.artifacts import generate_status_overview as m

# ---------------------------------------------------------------------------
# YAMLParser.parse_frontmatter
# ---------------------------------------------------------------------------


def test_parse_frontmatter_returns_none_for_no_delimiter() -> None:
    p = m.YAMLParser()
    assert p.parse_frontmatter("# heading\n\nbody\n") is None


def test_parse_frontmatter_extracts_scalars() -> None:
    p = m.YAMLParser()
    text = (
        "---\n"
        "id: REQ-FUNC-001\n"
        "status: completed\n"
        "urgency: 3\n"
        "---\n"
        "body\n"
    )
    meta = p.parse_frontmatter(text)
    assert meta is not None
    assert meta["id"] == "REQ-FUNC-001"
    assert meta["status"] == "completed"
    assert meta["urgency"] == 3


def test_parse_frontmatter_extracts_inline_lists() -> None:
    p = m.YAMLParser()
    text = (
        "---\n"
        "id: REQ-FUNC-002\n"
        "after: [TASK-001, TASK-002]\n"
        "---\n"
    )
    meta = p.parse_frontmatter(text)
    assert meta is not None
    assert list(meta["after"]) == ["TASK-001", "TASK-002"]


def test_parse_frontmatter_extracts_nested_lists() -> None:
    p = m.YAMLParser()
    text = (
        "---\n"
        "id: REQ-FUNC-003\n"
        "covers:\n"
        "  acceptance_criteria:\n"
        "    - AC-01\n"
        "    - AC-02\n"
        "---\n"
    )
    meta = p.parse_frontmatter(text)
    assert meta is not None
    assert list(meta["covers"]["acceptance_criteria"]) == ["AC-01", "AC-02"]


def test_parse_frontmatter_strips_bom() -> None:
    p = m.YAMLParser()
    text = "﻿---\nid: X\n---\n"
    meta = p.parse_frontmatter(text)
    assert meta is not None
    assert meta["id"] == "X"


# ---------------------------------------------------------------------------
# load_releases / load_backlog_packages
# ---------------------------------------------------------------------------


def test_load_releases_returns_empty_for_missing_file(tmp_path: Path) -> None:
    # tmp_path has no requirements_tasks/RELEASES.md → empty list
    assert m.load_releases(tmp_path) == []


def test_load_releases_returns_sorted_releases(tmp_path: Path) -> None:
    rel = tmp_path / "requirements_tasks"
    rel.mkdir(parents=True)
    (rel / "RELEASES.md").write_text(
        "---\n"
        "releases:\n"
        '  - version: "1.1.0"\n'
        '    name: "Second"\n'
        '  - version: "1.0.0"\n'
        '    name: "First"\n'
        "---\n",
        encoding="utf-8",
    )
    out = m.load_releases(tmp_path)
    assert [r["version"] for r in out] == ["1.0.0", "1.1.0"]
    assert out[0]["name"] == "First"


def test_load_backlog_packages_returns_empty_for_missing(tmp_path: Path) -> None:
    assert m.load_backlog_packages(tmp_path) == []


def test_load_backlog_packages_extracts_flat_list(tmp_path: Path) -> None:
    rel = tmp_path / "requirements_tasks"
    rel.mkdir(parents=True)
    (rel / "RELEASE_BACKLOG.md").write_text(
        "---\n"
        "packages:\n"
        "  - id: PKG-A\n"
        "    name: Package A\n"
        '    assigned_release: "1.0.0"\n'
        "    status: active\n"
        "  - id: PKG-B\n"
        "    name: Package B\n"
        "---\n",
        encoding="utf-8",
    )
    out = m.load_backlog_packages(tmp_path)
    assert len(out) == 2
    assert out[0]["id"] == "PKG-A"
    assert out[0]["version"] == "1.0.0"
    assert out[0]["status"] == "active"
    assert out[1]["id"] == "PKG-B"
    assert out[1]["version"] == ""


# ---------------------------------------------------------------------------
# git_commit
# ---------------------------------------------------------------------------


def test_git_commit_commits_when_file_changed(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    output_file = tmp_path / "requirements_tasks" / "STATUS.md"
    output_file.parent.mkdir(parents=True)
    output_file.write_text("content", encoding="utf-8")

    run_results = [
        None,  # git add
        type("R", (), {"stdout": "M requirements_tasks/STATUS.md\n"})(),  # git status
        None,  # git commit
    ]

    with patch("scripts.artifacts.generate_status_overview.subprocess.run", side_effect=run_results) as mock_run:
        m.git_commit(output_file)

    assert mock_run.call_count == 3
    commit_call = mock_run.call_args_list[2]
    assert commit_call[0][0][0:2] == ["git", "commit"]


def test_git_commit_skips_when_no_changes(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    output_file = tmp_path / "requirements_tasks" / "STATUS.md"
    output_file.parent.mkdir(parents=True)
    output_file.write_text("content", encoding="utf-8")

    run_results = [
        None,  # git add
        type("R", (), {"stdout": ""})(),  # git status — nothing staged
    ]

    with patch("scripts.artifacts.generate_status_overview.subprocess.run", side_effect=run_results) as mock_run:
        m.git_commit(output_file)

    # git commit must NOT be called
    assert mock_run.call_count == 2
    assert all(c[0][0][1] != "commit" for c in mock_run.call_args_list)
