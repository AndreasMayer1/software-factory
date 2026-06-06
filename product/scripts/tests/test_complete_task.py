"""Tests for scripts/tasks/complete_task.py — unchecked-AC guard."""

import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve().parents[1] / "tasks" / "complete_task.py"


def _make_goal(folder: Path, ac_block: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "goal.md").write_text(
        "---\nstatus: in_progress\n---\n\n# Goal\n\n## Acceptance Criteria\n\n"
        + ac_block
        + "\n"
    )


def _run(task_path: Path, *extra: str) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(task_path), *extra],
        capture_output=True,
        text=True,
    )


def test_refuses_when_unchecked_ac_remains(tmp_path: Path) -> None:
    task = tmp_path / "2026-05-14_impl_x"
    _make_goal(task, "- [x] First done\n- [ ] Second unchecked\n")

    result = _run(task)

    assert result.returncode == 2
    assert "unchecked acceptance criteria" in result.stderr
    assert task.exists(), "folder must NOT be renamed when ACs are unchecked"


def test_renames_when_all_acs_checked(tmp_path: Path) -> None:
    task = tmp_path / "2026-05-14_impl_x"
    _make_goal(task, "- [x] One\n- [x] Two\n")

    result = _run(task)

    assert result.returncode == 0
    assert not task.exists()
    assert (tmp_path / "2026-05-14_impl_x (completed)").exists()


def test_force_overrides_unchecked_guard(tmp_path: Path) -> None:
    task = tmp_path / "2026-05-14_impl_x"
    _make_goal(task, "- [ ] Still unchecked\n")

    result = _run(task, "--force")

    assert result.returncode == 0
    assert (tmp_path / "2026-05-14_impl_x (completed)").exists()


def test_task_without_ac_section_passes(tmp_path: Path) -> None:
    task = tmp_path / "2026-05-14_impl_x"
    task.mkdir()
    (task / "goal.md").write_text("---\nstatus: in_progress\n---\n\n# Goal\n\nNo ACs here.\n")

    result = _run(task)

    assert result.returncode == 0
    assert (tmp_path / "2026-05-14_impl_x (completed)").exists()


def test_already_completed_is_idempotent(tmp_path: Path) -> None:
    task = tmp_path / "2026-05-14_impl_x (completed)"
    _make_goal(task, "- [ ] Even unchecked, already-completed exits cleanly\n")

    result = _run(task)

    assert result.returncode == 0
    assert "already marked as completed" in result.stdout
