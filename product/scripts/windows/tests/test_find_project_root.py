"""Tests for find_project_root.py — the Python resolution helper."""

# tier: C  # Test for Windows-host resolution helper

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# The module under test lives at scripts/windows/find_project_root.py.
# We add its parent to sys.path so the import works from the test runner.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from find_project_root import find_project_root  # type: ignore[import-not-found]  # noqa: I001  # must follow sys.path injection above


class TestExplicitPath:
    """Precedence 1: explicit argument."""

    def test_returns_existing_directory(self, tmp_path: Path) -> None:
        result = find_project_root(explicit=str(tmp_path))
        assert result == tmp_path.resolve()

    def test_raises_on_nonexistent_directory(self) -> None:
        with pytest.raises(FileNotFoundError, match="explicit path does not exist"):
            find_project_root(explicit="/nonexistent/path/xyz_999")

    def test_explicit_takes_precedence_over_config(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "config_root"
        config_dir.mkdir()
        explicit_dir = tmp_path / "explicit_root"
        explicit_dir.mkdir()

        result = find_project_root(explicit=str(explicit_dir))
        assert result == explicit_dir.resolve()


class TestConfigFile:
    """Precedence 2: windows_scripts.config.json."""

    def test_reads_project_root_from_config(self, tmp_path: Path) -> None:
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        config = {"project_root": str(project_dir)}
        config_file = tmp_path / "windows_scripts.config.json"
        config_file.write_text(json.dumps(config), encoding="utf-8")

        import find_project_root as mod

        original_file = mod.__file__
        try:
            mod.__file__ = str(tmp_path / "find_project_root.py")
            result = find_project_root()
            assert result == project_dir.resolve()
        finally:
            mod.__file__ = original_file

    def test_raises_when_config_project_root_missing(self, tmp_path: Path) -> None:
        config_file = tmp_path / "windows_scripts.config.json"
        config_file.write_text(
            json.dumps({"project_root": "/nonexistent/zzz"}), encoding="utf-8"
        )

        import find_project_root as mod

        original_file = mod.__file__
        try:
            mod.__file__ = str(tmp_path / "find_project_root.py")
            with pytest.raises(
                FileNotFoundError, match="config project_root does not exist"
            ):
                find_project_root()
        finally:
            mod.__file__ = original_file


class TestAutoDerive:
    """Precedence 3: auto-derive from script location."""

    def test_derives_from_file_location(self, tmp_path: Path) -> None:
        # Simulate in-repo layout: project/scripts/windows/find_project_root.py
        scripts_windows = tmp_path / "scripts" / "windows"
        scripts_windows.mkdir(parents=True)
        fake_script = scripts_windows / "find_project_root.py"
        fake_script.touch()

        import find_project_root as mod

        original_file = mod.__file__
        try:
            mod.__file__ = str(fake_script)
            result = find_project_root()
            assert result == tmp_path.resolve()
        finally:
            mod.__file__ = original_file
