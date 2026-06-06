#!/usr/bin/env python3
"""Regression tests for scripts/tasks/next_tasks.py.

Pins parse_frontmatter behavior and the end-to-end load_tasks/load_backlog_packages
contract before swapping the hand-rolled parser to scripts.util.yaml_frontmatter
(TASK-PROC-051-04 / G4). This module is used by task-start (via claude-route) so any behavior
divergence must be detected.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "tasks" / "next_tasks.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("next_tasks_under_test", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return _load_module()


def test_parse_basic_scalars(mod: Any) -> None:
    out = mod.parse_frontmatter(
        "---\n"
        "task_id: TASK-FUNC-001-01\n"
        "type: impl\n"
        "status: pending\n"
        "urgency: 3\n"
        "impact: 4\n"
        "---\n"
    )
    assert out is not None
    assert out.get("task_id") == "TASK-FUNC-001-01"
    assert out.get("type") == "impl"
    assert int(out.get("urgency")) == 3


def test_parse_inline_list(mod: Any) -> None:
    out = mod.parse_frontmatter(
        "---\n"
        "task_id: TASK-A\n"
        "after: [TASK-B, TASK-C]\n"
        "---\n"
    )
    assert out is not None
    after = out.get("after")
    assert isinstance(after, list)
    assert list(after) == ["TASK-B", "TASK-C"]


def test_parse_empty_list_with_block_form(mod: Any) -> None:
    out = mod.parse_frontmatter(
        "---\n"
        "task_id: TASK-A\n"
        "awaiting: []\n"
        "after:\n"
        "  - TASK-B\n"
        "  - TASK-C\n"
        "---\n"
    )
    assert out is not None
    assert list(out.get("awaiting")) == []
    after = out.get("after")
    assert list(after) == ["TASK-B", "TASK-C"]


def test_task_name_strips_impl_prefix(mod: Any) -> None:
    # explore/impl prefixes are stripped; analyze is no longer stripped (folded into explore)
    fake = Path("/tasks/2026-01-01_impl_do_something/goal.md")
    assert mod._task_name(fake) == "do something"


def test_task_name_strips_explore_prefix(mod: Any) -> None:
    fake = Path("/tasks/2026-01-01_explore_research_topic/goal.md")
    assert mod._task_name(fake) == "research topic"


def test_task_name_preserves_analyze_prefix(mod: Any) -> None:
    # analyze_ is no longer in the strip list — historical folders keep the prefix
    fake = Path("/tasks/2026-01-01_analyze_flow_003/goal.md")
    assert mod._task_name(fake) == "analyze flow 003"


def test_parse_bom(mod: Any) -> None:
    out = mod.parse_frontmatter("﻿---\ntask_id: TASK-X\n---\n")
    assert out is not None
    assert out.get("task_id") == "TASK-X"


def test_parse_returns_none_when_absent(mod: Any) -> None:
    assert mod.parse_frontmatter("no frontmatter here\n") is None


def test_parse_quoted_value_strips_quotes(mod: Any) -> None:
    out = mod.parse_frontmatter(
        "---\n"
        "task_id: TASK-Q\n"
        "target_release: \"0.1.0\"\n"
        "---\n"
    )
    assert out is not None
    # PyYAML / ruamel both unwrap quoted strings to plain str
    assert out.get("target_release") == "0.1.0"


def test_load_backlog_packages_skips_when_file_missing(mod: Any, monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(mod, "RELEASE_BACKLOG_FILE", tmp_path / "missing.md")
    assert mod.load_backlog_packages() == []


def test_load_backlog_packages_reads_packages(mod: Any, monkeypatch: Any, tmp_path: Path) -> None:
    backlog = tmp_path / "RELEASE_BACKLOG.md"
    backlog.write_text(
        "---\n"
        "packages:\n"
        "  - id: PKG-A\n"
        "    name: Alpha\n"
        "    assigned_release: \"0.1.0\"\n"
        "    status: planned\n"
        "  - id: PKG-B\n"
        "    name: Beta\n"
        "    assigned_release: \"0.2.0\"\n"
        "    status: planned\n"
        "---\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "RELEASE_BACKLOG_FILE", backlog)
    pkgs = mod.load_backlog_packages()
    ids = [p["id"] for p in pkgs]
    assert ids == ["PKG-A", "PKG-B"]
    assert pkgs[0]["version"] == "0.1.0"


def test_load_active_release_returns_active_version(mod: Any, monkeypatch: Any, tmp_path: Path) -> None:
    releases = tmp_path / "RELEASES.md"
    releases.write_text(
        "---\n"
        "releases:\n"
        "  - version: \"0.0.1\"\n"
        "    status: released\n"
        "  - version: \"0.1.0\"\n"
        "    status: active\n"
        "---\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "RELEASES_FILE", releases)
    assert mod.load_active_release() == "0.1.0"


# ---------------------------------------------------------------------------
# Override-first logic (TASK-PROC-042-12)
# ---------------------------------------------------------------------------

def _make_task(
    task_id: str,
    status: str,
    target_package: str | None = "pkg1",
    after: list[str] | None = None,
) -> dict[str, Any]:
    """Build a minimal task dict for override tests."""
    return {
        "task_id": task_id,
        "path": f"/fake/{task_id}/goal.md",
        "name": task_id.lower().replace("-", " "),
        "parent_requirement": "REQ-FAKE",
        "type": "impl",
        "status": status,
        "urgency": 5,
        "impact": 5,
        "awaiting": [],
        "after": after or [],
        "target_release": None,
        "target_package": target_package,
        "completed": None,
        "writes_requirements": False,
        "cascade_active": False,
        "factory_urgent": False,
        "orchestration_task": False,
        "scope_description": "",
    }


def test_override_blocks_normal_tasks(mod: Any, monkeypatch: Any, tmp_path: Path) -> None:
    """When a non-terminal override task exists, only that task is surfaced (not normal tasks)."""
    override_file = tmp_path / "task_ordering_priority_override.txt"
    override_file.write_text("OVERRIDE-01\n")
    monkeypatch.setattr(mod, "PRIORITY_OVERRIDE_FILE", override_file)

    override_task = _make_task("OVERRIDE-01", "pending", target_package=None)
    normal_task = _make_task("NORMAL-01", "pending", target_package="pkg1")
    all_tasks = [override_task, normal_task]

    completed_ids: set[str] = set()
    known_ids = {t["task_id"] for t in all_tasks}

    # Access via mod to avoid direct task_ordering import (sibling path; mypy can't follow)
    TERMINAL_STATUSES = mod.TERMINAL_STATUSES
    EXCLUDED_STATUSES = mod.EXCLUDED_STATUSES
    is_blocked = mod.is_blocked

    override_ids = mod.load_priority_override()
    task_by_id = {t["task_id"]: t for t in all_tasks}
    override_nonterminal = [
        task_by_id[tid] for tid in override_ids
        if tid in task_by_id and task_by_id[tid]["status"] not in TERMINAL_STATUSES
    ]
    assert len(override_nonterminal) == 1

    override_runnable = [
        t for t in override_nonterminal
        if t["status"] not in EXCLUDED_STATUSES
        and not is_blocked(t, completed_ids, known_ids)
    ]
    assert len(override_runnable) == 1
    assert override_runnable[0]["task_id"] == "OVERRIDE-01"
    # Normal task must NOT appear in the runnable override set
    assert all(t["task_id"] != "NORMAL-01" for t in override_runnable)


def test_override_all_blocked_no_runnable(mod: Any, monkeypatch: Any, tmp_path: Path) -> None:
    """When all pending override tasks are blocked, override_runnable is empty."""
    override_file = tmp_path / "task_ordering_priority_override.txt"
    override_file.write_text("OVERRIDE-02\n")
    monkeypatch.setattr(mod, "PRIORITY_OVERRIDE_FILE", override_file)

    # OVERRIDE-02 depends on PREREQ-01 which is still pending → blocked
    override_task = _make_task("OVERRIDE-02", "pending", target_package=None, after=["PREREQ-01"])
    prereq_task = _make_task("PREREQ-01", "pending", target_package=None)
    all_tasks = [override_task, prereq_task]

    completed_ids: set[str] = set()
    known_ids = {t["task_id"] for t in all_tasks}

    TERMINAL_STATUSES = mod.TERMINAL_STATUSES
    EXCLUDED_STATUSES = mod.EXCLUDED_STATUSES
    is_blocked = mod.is_blocked

    override_ids = mod.load_priority_override()
    task_by_id = {t["task_id"]: t for t in all_tasks}
    override_nonterminal = [
        task_by_id[tid] for tid in override_ids
        if tid in task_by_id and task_by_id[tid]["status"] not in TERMINAL_STATUSES
    ]
    assert len(override_nonterminal) == 1
    assert is_blocked(override_task, completed_ids, known_ids)

    override_runnable = [
        t for t in override_nonterminal
        if t["status"] not in EXCLUDED_STATUSES
        and not is_blocked(t, completed_ids, known_ids)
    ]
    # No runnable override task — caller must exit with blocked message
    assert override_runnable == []


def test_override_terminal_resumes_normal(mod: Any, monkeypatch: Any, tmp_path: Path) -> None:
    """When all override tasks are terminal, override_nonterminal is empty (normal ranking resumes)."""
    override_file = tmp_path / "task_ordering_priority_override.txt"
    override_file.write_text("OVERRIDE-03\n")
    monkeypatch.setattr(mod, "PRIORITY_OVERRIDE_FILE", override_file)

    completed_override = _make_task("OVERRIDE-03", "completed", target_package=None)
    normal_task = _make_task("NORMAL-02", "pending", target_package="pkg1")
    all_tasks = [completed_override, normal_task]

    TERMINAL_STATUSES = mod.TERMINAL_STATUSES

    override_ids = mod.load_priority_override()
    task_by_id = {t["task_id"]: t for t in all_tasks}
    override_nonterminal = [
        task_by_id[tid] for tid in override_ids
        if tid in task_by_id and task_by_id[tid]["status"] not in TERMINAL_STATUSES
    ]
    # All override tasks are terminal → empty → normal ranking proceeds
    assert override_nonterminal == []


# ---------------------------------------------------------------------------
# Pending orchestration task block (REQ-PROC-035 SEC-05 / Option D)
# ---------------------------------------------------------------------------

def _make_orch_task(
    task_id: str,
    status: str,
    target_release: str | None = "0.0.1",
) -> dict[str, Any]:
    """Build a minimal orchestration task dict."""
    t = _make_task(task_id, status, target_package=None)
    t["orchestration_task"] = True
    t["target_release"] = target_release
    return t


def test_pending_orch_active_release_blocks(mod: Any) -> None:
    """Pending orch task for the active release is returned as a blocker."""
    orch = _make_orch_task("TASK-PROC-035-17", "in_progress", target_release="0.0.1")
    result = mod._find_pending_orch_tasks([orch], {"TASK-PROC-035-17"}, "0.0.1")
    assert len(result) == 1
    assert result[0]["task_id"] == "TASK-PROC-035-17"


def test_pending_orch_does_not_block_override_path(mod: Any) -> None:
    """override_surfaced=True suppresses the orch block (override tasks are orthogonal)."""
    orch = _make_orch_task("TASK-PROC-035-17", "in_progress", target_release="0.0.1")
    pending_orch = mod._find_pending_orch_tasks([orch], {"TASK-PROC-035-17"}, "0.0.1")
    assert len(pending_orch) == 1
    # Simulate: override path surfaced its own tasks → orch block must not fire
    override_surfaced = True
    should_block = not override_surfaced and bool(pending_orch)
    assert not should_block


def test_pending_orch_blocks_when_override_not_surfaced(mod: Any) -> None:
    """override_surfaced=False with a pending orch task → block fires."""
    orch = _make_orch_task("TASK-PROC-035-17", "in_progress", target_release="0.0.1")
    pending_orch = mod._find_pending_orch_tasks([orch], {"TASK-PROC-035-17"}, "0.0.1")
    override_surfaced = False
    should_block = not override_surfaced and bool(pending_orch)
    assert should_block


def test_pending_orch_different_release_not_blocked(mod: Any) -> None:
    """Pending orch task for a different release does NOT block."""
    orch = _make_orch_task("TASK-PROC-035-17", "in_progress", target_release="0.1.0")
    result = mod._find_pending_orch_tasks([orch], {"TASK-PROC-035-17"}, "0.0.1")
    assert result == []


def test_pending_orch_terminal_not_blocked(mod: Any) -> None:
    """A completed orch task in pending_feedback does NOT block."""
    orch = _make_orch_task("TASK-PROC-035-17", "completed", target_release="0.0.1")
    result = mod._find_pending_orch_tasks([orch], {"TASK-PROC-035-17"}, "0.0.1")
    assert result == []


def test_pending_non_orch_task_not_blocked(mod: Any) -> None:
    """A non-orchestration task in pending_feedback does NOT trigger the orch block."""
    impl = _make_task("TASK-FUNC-007-01", "in_progress")
    impl["target_release"] = "0.0.1"
    result = mod._find_pending_orch_tasks([impl], {"TASK-FUNC-007-01"}, "0.0.1")
    assert result == []


def test_pending_orch_no_active_release_not_blocked(mod: Any) -> None:
    """When there is no active release the check is skipped entirely."""
    orch = _make_orch_task("TASK-PROC-035-17", "in_progress", target_release="0.0.1")
    result = mod._find_pending_orch_tasks([orch], {"TASK-PROC-035-17"}, None)
    assert result == []


def test_pending_orch_empty_pending_ids_not_blocked(mod: Any) -> None:
    """Empty pending_ids set short-circuits without inspecting tasks."""
    orch = _make_orch_task("TASK-PROC-035-17", "in_progress", target_release="0.0.1")
    result = mod._find_pending_orch_tasks([orch], set(), "0.0.1")
    assert result == []


# ---------------------------------------------------------------------------
# Autonomous optimize cycle task surfacing (REQ-PROC-006 F-1 / TASK-PROC-006-18)
# ---------------------------------------------------------------------------

def _make_optimize_task(task_id: str, status: str = "pending") -> dict[str, Any]:
    """Build a type:optimize cycle task (no package/release, awaiting:[]).

    Path lives under PROJECT_ROOT so _format_task's relative_to(PROJECT_ROOT)
    succeeds (the optimize block formats and prints the task).
    """
    t = _make_task(task_id, status, target_package=None)
    t["type"] = "optimize"
    t["path"] = str(REPO_ROOT / "requirements_tasks" / f"{task_id}" / "goal.md")
    return t


def test_optimize_task_surfaces_under_active_override(
    mod: Any, monkeypatch: Any, tmp_path: Path, capsys: Any
) -> None:
    """A type:optimize task is returned even while a priority override is active.

    This is the surfacing fix: the override gate returns ONLY override-listed
    tasks, and an optimize task (no package) would never rank normally — so it
    must be surfaced ahead of the override gate. Fails against pre-change code,
    which would print the override task instead.
    """
    import sys as _sys

    override_file = tmp_path / "task_ordering_priority_override.txt"
    override_file.write_text("OVERRIDE-OPT\n")
    monkeypatch.setattr(mod, "PRIORITY_OVERRIDE_FILE", override_file)

    optimize_task = _make_optimize_task("TASK-OPT-0-1")
    override_task = _make_task("OVERRIDE-OPT", "pending", target_package="pkg1")
    override_task["path"] = str(REPO_ROOT / "requirements_tasks" / "OVERRIDE-OPT" / "goal.md")
    monkeypatch.setattr(mod, "load_tasks", lambda: [optimize_task, override_task])
    monkeypatch.setattr(mod, "load_pending_feedback_ids", lambda: set())
    monkeypatch.setattr(mod, "load_active_release", lambda: None)
    monkeypatch.setattr(mod, "load_backlog_packages", lambda: [])
    monkeypatch.setattr(_sys, "argv", ["next_tasks.py"])

    mod.main()

    out = capsys.readouterr().out
    assert "TASK-OPT-0-1" in out
    assert "OVERRIDE-OPT" not in out


def test_optimize_task_not_surfaced_when_terminal(
    mod: Any, monkeypatch: Any, tmp_path: Path, capsys: Any
) -> None:
    """A completed optimize task does not preempt; normal/override ranking resumes."""
    import sys as _sys

    override_file = tmp_path / "task_ordering_priority_override.txt"
    override_file.write_text("OVERRIDE-OPT2\n")
    monkeypatch.setattr(mod, "PRIORITY_OVERRIDE_FILE", override_file)

    optimize_task = _make_optimize_task("TASK-OPT-0-2", status="completed")
    override_task = _make_task("OVERRIDE-OPT2", "pending", target_package="pkg1")
    override_task["path"] = str(REPO_ROOT / "requirements_tasks" / "OVERRIDE-OPT2" / "goal.md")
    monkeypatch.setattr(mod, "load_tasks", lambda: [optimize_task, override_task])
    monkeypatch.setattr(mod, "load_pending_feedback_ids", lambda: set())
    monkeypatch.setattr(mod, "load_active_release", lambda: None)
    monkeypatch.setattr(mod, "load_backlog_packages", lambda: [])
    monkeypatch.setattr(_sys, "argv", ["next_tasks.py"])

    mod.main()

    out = capsys.readouterr().out
    # Terminal optimize task is filtered out; the override task surfaces instead.
    assert "TASK-OPT-0-2" not in out
    assert "OVERRIDE-OPT2" in out
