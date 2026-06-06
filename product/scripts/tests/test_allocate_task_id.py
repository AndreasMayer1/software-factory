"""
test_allocate_task_id.py — Tests for scripts/allocate_task_id.py

Covers:
  A — Input validation (bad req_id, missing req_path)
  B — Empty tasks folder (first task gets -01)
  C — Sequential allocation (always max+1)
  D — Gap handling: used IDs from goal.md are not reused
  E — Reserve files: active reserves are skipped; reserve is created on success
  F — Cross-prefix isolation: only IDs matching the current prefix count
  G — Concurrent safety: second call skips reserve left by first call
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tasks"))

from allocate_task_id import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    allocate_id,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lock(tmp: str) -> str:
    """Return a per-test lock file path inside tmp so tests don't share state."""
    meta = os.path.join(tmp, "_meta")
    os.makedirs(meta, exist_ok=True)
    return os.path.join(meta, ".task_id_lock")


def _req_dir(tmp: str) -> str:
    path = os.path.join(tmp, "req")
    os.makedirs(path, exist_ok=True)
    return path


def _write_goal(tasks_dir: str, folder_name: str, task_id: str) -> None:
    folder = os.path.join(tasks_dir, folder_name)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "goal.md"), "w") as f:
        f.write(f"---\ntask_id: {task_id}\nstatus: completed\n---\n")


def _write_reserve(tasks_dir: str, task_id: str) -> None:
    with open(os.path.join(tasks_dir, f".reserve-{task_id}"), "w") as f:
        f.write(f"Reserved for {task_id}\n")


# ---------------------------------------------------------------------------
# A — Input validation
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_invalid_req_id_exits(self, tmp_path):
        with pytest.raises(SystemExit):
            allocate_id("INVALID-ID", str(tmp_path), _lock(str(tmp_path)))

    def test_req_id_missing_number_exits(self, tmp_path):
        with pytest.raises(SystemExit):
            allocate_id("REQ-PROC", str(tmp_path), _lock(str(tmp_path)))

    def test_nonexistent_req_path_exits(self, tmp_path):
        with pytest.raises(SystemExit):
            allocate_id("REQ-PROC-048", str(tmp_path / "does_not_exist"), _lock(str(tmp_path)))


# ---------------------------------------------------------------------------
# B — Empty tasks folder
# ---------------------------------------------------------------------------

class TestEmptyFolder:
    def test_first_task_gets_01(self, tmp_path):
        req = _req_dir(str(tmp_path))
        result = allocate_id("REQ-PROC-048", req, _lock(str(tmp_path)))
        assert result == "TASK-PROC-048-01"

    def test_tasks_dir_created_if_absent(self, tmp_path):
        req = _req_dir(str(tmp_path))
        allocate_id("REQ-PROC-048", req, _lock(str(tmp_path)))
        assert os.path.isdir(os.path.join(req, "tasks"))


# ---------------------------------------------------------------------------
# C — Sequential allocation
# ---------------------------------------------------------------------------

class TestSequential:
    def test_two_existing_tasks_allocates_03(self, tmp_path):
        req = _req_dir(str(tmp_path))
        tasks = os.path.join(req, "tasks")
        os.makedirs(tasks)
        _write_goal(tasks, "2026-01-01_impl_first", "TASK-PROC-048-01")
        _write_goal(tasks, "2026-01-02_impl_second", "TASK-PROC-048-02")
        result = allocate_id("REQ-PROC-048", req, _lock(str(tmp_path)))
        assert result == "TASK-PROC-048-03"

    def test_zero_padded_to_two_digits(self, tmp_path):
        req = _req_dir(str(tmp_path))
        result = allocate_id("REQ-FUNC-001", req, _lock(str(tmp_path)))
        assert result == "TASK-FUNC-001-01"


# ---------------------------------------------------------------------------
# D — Gap handling: used IDs from goal.md are never reused
# ---------------------------------------------------------------------------

class TestGapHandling:
    def test_gap_01_02_09_allocates_10(self, tmp_path):
        req = _req_dir(str(tmp_path))
        tasks = os.path.join(req, "tasks")
        os.makedirs(tasks)
        _write_goal(tasks, "explore (completed)", "TASK-PROC-048-01")
        _write_goal(tasks, "impl-enforce (completed)", "TASK-PROC-048-02")
        _write_goal(tasks, "impl-split (completed)", "TASK-PROC-048-09")
        result = allocate_id("REQ-PROC-048", req, _lock(str(tmp_path)))
        assert result == "TASK-PROC-048-10"

    def test_goal_without_task_id_is_ignored(self, tmp_path):
        req = _req_dir(str(tmp_path))
        tasks = os.path.join(req, "tasks")
        os.makedirs(tasks)
        folder = os.path.join(tasks, "2026-01-01_impl_broken")
        os.makedirs(folder)
        with open(os.path.join(folder, "goal.md"), "w") as f:
            f.write("---\nstatus: pending\n---\n")
        result = allocate_id("REQ-PROC-048", req, _lock(str(tmp_path)))
        assert result == "TASK-PROC-048-01"

    def test_completed_folder_name_suffix_does_not_affect_id(self, tmp_path):
        req = _req_dir(str(tmp_path))
        tasks = os.path.join(req, "tasks")
        os.makedirs(tasks)
        _write_goal(tasks, "2026-01-01_impl_first (completed)", "TASK-PROC-048-01")
        result = allocate_id("REQ-PROC-048", req, _lock(str(tmp_path)))
        assert result == "TASK-PROC-048-02"


# ---------------------------------------------------------------------------
# E — Reserve files
# ---------------------------------------------------------------------------

class TestReserveFiles:
    def test_active_reserve_is_skipped(self, tmp_path):
        req = _req_dir(str(tmp_path))
        tasks = os.path.join(req, "tasks")
        os.makedirs(tasks)
        _write_goal(tasks, "2026-01-01_impl_first", "TASK-PROC-048-01")
        _write_reserve(tasks, "TASK-PROC-048-02")
        result = allocate_id("REQ-PROC-048", req, _lock(str(tmp_path)))
        assert result == "TASK-PROC-048-03"

    def test_reserve_file_created_after_allocation(self, tmp_path):
        req = _req_dir(str(tmp_path))
        result = allocate_id("REQ-PROC-048", req, _lock(str(tmp_path)))
        reserve = os.path.join(req, "tasks", f".reserve-{result}")
        assert os.path.isfile(reserve)

    def test_reserve_for_gap_id_is_skipped(self, tmp_path):
        req = _req_dir(str(tmp_path))
        tasks = os.path.join(req, "tasks")
        os.makedirs(tasks)
        _write_goal(tasks, "2026-01-01_impl_first", "TASK-PROC-048-01")
        _write_goal(tasks, "2026-01-03_impl_third", "TASK-PROC-048-09")
        _write_reserve(tasks, "TASK-PROC-048-10")
        result = allocate_id("REQ-PROC-048", req, _lock(str(tmp_path)))
        assert result == "TASK-PROC-048-11"


# ---------------------------------------------------------------------------
# F — Cross-prefix isolation
# ---------------------------------------------------------------------------

class TestCrossPrefixIsolation:
    def test_other_req_goal_not_counted(self, tmp_path):
        req = _req_dir(str(tmp_path))
        tasks = os.path.join(req, "tasks")
        os.makedirs(tasks)
        _write_goal(tasks, "2026-01-01_impl_other", "TASK-PROC-007-01")
        result = allocate_id("REQ-PROC-048", req, _lock(str(tmp_path)))
        assert result == "TASK-PROC-048-01"

    def test_other_req_reserve_not_counted(self, tmp_path):
        req = _req_dir(str(tmp_path))
        tasks = os.path.join(req, "tasks")
        os.makedirs(tasks)
        _write_reserve(tasks, "TASK-PROC-007-01")
        result = allocate_id("REQ-PROC-048", req, _lock(str(tmp_path)))
        assert result == "TASK-PROC-048-01"


# ---------------------------------------------------------------------------
# G — Concurrent safety
# ---------------------------------------------------------------------------

class TestConcurrentSafety:
    def test_second_call_skips_reserve_from_first(self, tmp_path):
        req = _req_dir(str(tmp_path))
        lock = _lock(str(tmp_path))
        first = allocate_id("REQ-PROC-048", req, lock)
        second = allocate_id("REQ-PROC-048", req, lock)
        assert first == "TASK-PROC-048-01"
        assert second == "TASK-PROC-048-02"

    def test_three_sequential_calls_get_unique_ids(self, tmp_path):
        req = _req_dir(str(tmp_path))
        lock = _lock(str(tmp_path))
        ids = [allocate_id("REQ-PROC-048", req, lock) for _ in range(3)]
        assert ids == ["TASK-PROC-048-01", "TASK-PROC-048-02", "TASK-PROC-048-03"]
        assert len(set(ids)) == 3
