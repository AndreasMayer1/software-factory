#!/usr/bin/env python3
"""Regression tests for scripts/release/execute_release.py.

Pins observable behaviour of get_active_release_version before swapping the
hand-rolled parser to scripts.util.yaml_frontmatter (TASK-PROC-051-04 / G4).
"""

from pathlib import Path
from unittest.mock import patch

from scripts.release import execute_release as m


def test_get_active_release_version_returns_active(tmp_path: Path) -> None:
    rel = tmp_path / "requirements_tasks"
    rel.mkdir(parents=True)
    (rel / "RELEASES.md").write_text(
        "---\n"
        "releases:\n"
        '  - version: "1.0.0"\n'
        "    status: planned\n"
        '  - version: "1.1.0"\n'
        "    status: active\n"
        "---\n",
        encoding="utf-8",
    )
    with patch.object(m, "PROJECT_ROOT", tmp_path):
        assert m.get_active_release_version() == "1.1.0"


def test_get_active_release_version_returns_none_when_no_active(tmp_path: Path) -> None:
    rel = tmp_path / "requirements_tasks"
    rel.mkdir(parents=True)
    (rel / "RELEASES.md").write_text(
        "---\n"
        "releases:\n"
        '  - version: "1.0.0"\n'
        "    status: planned\n"
        "---\n",
        encoding="utf-8",
    )
    with patch.object(m, "PROJECT_ROOT", tmp_path):
        assert m.get_active_release_version() is None


def test_get_active_release_version_returns_none_for_missing_file(tmp_path: Path) -> None:
    with patch.object(m, "PROJECT_ROOT", tmp_path):
        assert m.get_active_release_version() is None
