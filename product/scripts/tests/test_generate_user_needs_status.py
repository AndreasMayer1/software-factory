#!/usr/bin/env python3
"""Tests for scripts/artifacts/generate_user_needs_status.py — git_commit behaviour."""

from pathlib import Path
from unittest.mock import patch

import pytest

# generate_user_needs_status imports `yaml` (PyYAML) at module level.
# The uv venv only has ruamel-yaml, so skip this whole module when PyYAML is
# absent rather than stubbing sys.modules (which would pollute other tests).
pytest.importorskip("yaml")

from scripts.artifacts import generate_user_needs_status as m

# ---------------------------------------------------------------------------
# git_commit
# ---------------------------------------------------------------------------


def test_git_commit_commits_when_file_changed(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    output_file = tmp_path / "requirements_user_needs" / "STATUS.md"
    output_file.parent.mkdir(parents=True)
    output_file.write_text("content", encoding="utf-8")

    run_results = [
        None,  # git add
        type("R", (), {"stdout": "M requirements_user_needs/STATUS.md\n"})(),  # git status
        None,  # git commit
    ]

    with patch("scripts.artifacts.generate_user_needs_status.subprocess.run", side_effect=run_results) as mock_run:
        m.git_commit(output_file)

    assert mock_run.call_count == 3
    commit_call = mock_run.call_args_list[2]
    assert commit_call[0][0][0:2] == ["git", "commit"]


def test_git_commit_skips_when_no_changes(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    output_file = tmp_path / "requirements_user_needs" / "STATUS.md"
    output_file.parent.mkdir(parents=True)
    output_file.write_text("content", encoding="utf-8")

    run_results = [
        None,  # git add
        type("R", (), {"stdout": ""})(),  # git status — nothing staged
    ]

    with patch("scripts.artifacts.generate_user_needs_status.subprocess.run", side_effect=run_results) as mock_run:
        m.git_commit(output_file)

    # git commit must NOT be called
    assert mock_run.call_count == 2
    assert all(c[0][0][1] != "commit" for c in mock_run.call_args_list)
