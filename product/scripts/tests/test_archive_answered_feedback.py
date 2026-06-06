#!/usr/bin/env python3
"""Tests for scripts/maintenance/archive_answered_feedback.py."""

from __future__ import annotations

import importlib.util
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "maintenance" / "archive_answered_feedback.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("archive_answered_feedback", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return _load_module()


def _set_mtime_days_ago(path: Path, days: int) -> None:
    mtime = (datetime.now(tz=timezone.utc) - timedelta(days=days)).timestamp()
    os.utime(path, (mtime, mtime))


def test_collect_stale_finds_old_entry(tmp_path: Path, mod: Any) -> None:
    old = tmp_path / "TASK-PROC-001-01"
    old.mkdir()
    _set_mtime_days_ago(old, 40)

    threshold = datetime.now().astimezone() - timedelta(days=30)
    stale = mod.collect_stale_entries(tmp_path, threshold)
    assert old in stale


def test_collect_stale_excludes_recent_entry(tmp_path: Path, mod: Any) -> None:
    new = tmp_path / "TASK-PROC-002-01"
    new.mkdir()
    # mtime defaults to now — well inside the 30-day window

    threshold = datetime.now().astimezone() - timedelta(days=30)
    stale = mod.collect_stale_entries(tmp_path, threshold)
    assert new not in stale


def test_collect_stale_raises_on_missing_dir(mod: Any) -> None:
    with pytest.raises(FileNotFoundError):
        mod.collect_stale_entries(Path("/nonexistent/path"), datetime.now().astimezone())


def test_prune_dry_run_does_not_delete(tmp_path: Path, mod: Any) -> None:
    entry = tmp_path / "TASK-PROC-003-01"
    entry.mkdir()
    mod.prune_entries([entry], dry_run=True, verbose=False)
    assert entry.exists()


def test_prune_real_deletes_entry(tmp_path: Path, mod: Any) -> None:
    entry = tmp_path / "TASK-PROC-004-01"
    entry.mkdir()
    mod.prune_entries([entry], dry_run=False, verbose=False)
    assert not entry.exists()


def test_prune_returns_count(tmp_path: Path, mod: Any) -> None:
    entries = [tmp_path / f"TASK-PROC-00{i}-01" for i in range(3)]
    for e in entries:
        e.mkdir()
    count = mod.prune_entries(entries, dry_run=True, verbose=False)
    assert count == 3


def test_archive_returns_examined_and_pruned(tmp_path: Path, mod: Any) -> None:
    old = tmp_path / "TASK-OLD-001-01"
    old.mkdir()
    _set_mtime_days_ago(old, 40)

    new = tmp_path / "TASK-NEW-002-01"
    new.mkdir()

    examined, pruned = mod.archive_answered_feedback(
        tmp_path, days=30, dry_run=True, verbose=False
    )
    assert examined == 2
    assert pruned == 1


def test_archive_dry_run_leaves_entries(tmp_path: Path, mod: Any) -> None:
    old = tmp_path / "TASK-OLD-003-01"
    old.mkdir()
    _set_mtime_days_ago(old, 40)

    mod.archive_answered_feedback(tmp_path, days=30, dry_run=True, verbose=False)
    assert old.exists()


def test_archive_real_deletes_old_only(tmp_path: Path, mod: Any) -> None:
    old = tmp_path / "TASK-OLD-004-01"
    old.mkdir()
    _set_mtime_days_ago(old, 40)

    new = tmp_path / "TASK-NEW-005-01"
    new.mkdir()

    mod.archive_answered_feedback(tmp_path, days=30, dry_run=False, verbose=False)
    assert not old.exists()
    assert new.exists()
