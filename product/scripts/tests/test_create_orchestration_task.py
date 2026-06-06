# ruff: noqa: RUF001, RUF100
# RUF001: fixture strings include the en dash inside release names like Alpha-Data Transfer
# to match real release_backlog.md content.
# RUF100: false-positive on file-level noqa for codes ruff cannot introspect into the file body.
"""
test_create_orchestration_task.py -- Tests for scripts/create_orchestration_task.py
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tasks"))

from create_orchestration_task import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    Deps,
    _build_ac_block,
    create_orchestration_task,
    find_existing_orchestration_task,
    find_predecessor_slot_dir,
    get_requirements_commit,
    parse_args,
    parse_release_from_releases_md,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _completed(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[Any]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def _make_args(**kwargs: Any) -> argparse.Namespace:
    defaults = {"dry_run": False, "after_task": "", "plan_path": "", "task_type": "implement"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def make_deps(**overrides: Any) -> Deps:
    defaults = {
        "run_subprocess": lambda *a, **kw: _completed(),
        "makedirs": lambda p: None,
        "write_file": lambda p, c: None,
        "file_exists": lambda p: False,
        "remove_file": lambda p: None,
        "remove_dir": lambda p: None,
        "glob_files": lambda p: [],
        "read_file": lambda p: "",
        "get_today": lambda: "2026-04-24",
    }
    defaults.update(overrides)
    return Deps(**defaults)


# ---------------------------------------------------------------------------
# A — parse_release_from_releases_md
# ---------------------------------------------------------------------------

class TestParseReleaseFromReleasesMd:
    def test_extracts_active_version_from_yaml_frontmatter(self):
        content = (
            "releases:\n"
            '  - version: "0.0.1"\n'
            "    status: active\n"
        )
        assert parse_release_from_releases_md(content) == "0.0.1"

    def test_extracts_active_version_without_quotes(self):
        content = (
            "releases:\n"
            "  - version: 0.1.0\n"
            "    name: Beta\n"
            "    status: active\n"
        )
        assert parse_release_from_releases_md(content) == "0.1.0"

    def test_returns_none_when_no_active_status(self):
        content = (
            "releases:\n"
            '  - version: "1.0.0"\n'
            "    status: planned\n"
        )
        assert parse_release_from_releases_md(content) is None

    def test_returns_none_on_empty(self):
        assert parse_release_from_releases_md("") is None

    def test_ignores_planned_versions_picks_active(self):
        content = (
            "releases:\n"
            '  - version: "0.0.1"\n'
            "    status: released\n"
            '  - version: "0.0.2"\n'
            "    status: active\n"
            '  - version: "0.0.3"\n'
            "    status: planned\n"
        )
        assert parse_release_from_releases_md(content) == "0.0.2"

    def test_handles_multi_field_entry(self):
        content = (
            "releases:\n"
            '  - version: "0.0.1"\n'
            '    name: "Alpha – Data Transfer"\n'
            "    status: active\n"
            "    planned_date: null\n"
            "    packages:\n"
            "      - QR Transfer Send\n"
        )
        assert parse_release_from_releases_md(content) == "0.0.1"

    def test_handles_many_fields_between_version_and_status(self):
        content = (
            "releases:\n"
            '  - version: "0.0.5"\n'
            '    name: "Alpha – UI/UX Foundation"\n'
            '    description: "Establish non-functional UI/UX standards."\n'
            "    planned_date: null\n"
            "    status: active\n"
        )
        assert parse_release_from_releases_md(content) == "0.0.5"

    def test_does_not_match_version_in_different_entry(self):
        content = (
            "releases:\n"
            '  - version: "0.0.1"\n'
            "    status: planned\n"
            '  - version: "0.0.2"\n'
            "    status: planned\n"
        )
        assert parse_release_from_releases_md(content) is None

    def test_handles_only_yaml_frontmatter_markers(self):
        content = "---\nreleases: []\n---\n"
        assert parse_release_from_releases_md(content) is None


# ---------------------------------------------------------------------------
# B — find_existing_orchestration_task
# ---------------------------------------------------------------------------

class TestFindExistingOrchestrationTask:
    def test_returns_none_when_no_files(self):
        deps = make_deps(glob_files=lambda p: [])
        assert find_existing_orchestration_task(deps) is None

    def test_returns_none_when_no_orchestration_scope(self):
        deps = make_deps(
            glob_files=lambda p: ["/fake/goal.md"],
            read_file=lambda p: (
                'target_release: "0.0.1"\n'
                'scope_description: "Regular task, not orchestration"\n'
                "status: pending\n"
            ),
        )
        assert find_existing_orchestration_task(deps) is None

    def test_returns_none_when_status_completed(self):
        deps = make_deps(
            glob_files=lambda p: ["/fake/goal.md"],
            read_file=lambda p: (
                'target_release: "0.0.1"\n'
                'scope_description: "Orchestration: create impl tasks"\n'
                "status: completed\n"
            ),
        )
        assert find_existing_orchestration_task(deps) is None

    def test_returns_none_when_status_pending_only_in_description_text(self):
        # Regression: goal.md body mentions "status: pending" in prose but
        # the frontmatter field is "status: completed" — must not be a false positive.
        content = (
            "task_id: TASK-PROC-035-05\n"
            'target_release: "0.0.1"\n'
            'scope_description: "Orchestration: create impl tasks"\n'
            "status: completed\n"
            "Description: tasks with `status: pending` or `in_progress` block release.\n"
        )
        deps = make_deps(
            glob_files=lambda p: ["/fake/goal.md"],
            read_file=lambda p: content,
        )
        assert find_existing_orchestration_task(deps) is None

    def test_returns_path_for_pending_task(self):
        from create_orchestration_task import PROJECT_ROOT
        goal_path = str(PROJECT_ROOT / "requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-04-24_explore_x/goal.md")
        deps = make_deps(
            glob_files=lambda p: [goal_path],
            read_file=lambda p: (
                'target_release: "0.0.1"\n'
                'scope_description: "Orchestration: create impl tasks"\n'
                "status: pending\n"
                "task_id: TASK-PROC-035-06\n"
            ),
        )
        result = find_existing_orchestration_task(deps)
        assert result == goal_path

    def test_returns_path_for_in_progress_task(self):
        from create_orchestration_task import PROJECT_ROOT
        goal_path = str(PROJECT_ROOT / "requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-04-24_explore_x/goal.md")
        deps = make_deps(
            glob_files=lambda p: [goal_path],
            read_file=lambda p: (
                'target_release: "0.0.1"\n'
                'scope_description: "Orchestration: create impl tasks"\n'
                "status: in_progress\n"
                "task_id: TASK-PROC-035-06\n"
            ),
        )
        result = find_existing_orchestration_task(deps)
        assert result == goal_path

    def test_skips_unreadable_file(self):
        deps = make_deps(
            glob_files=lambda p: ["/fake/goal.md"],
            read_file=lambda p: (_ for _ in ()).throw(OSError("not found")),
        )
        assert find_existing_orchestration_task(deps) is None


# ---------------------------------------------------------------------------
# C — get_requirements_commit
# ---------------------------------------------------------------------------

class TestGetRequirementsCommit:
    def test_extracts_first_token(self):
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _completed(
                stdout="abc1234 feat: something\n"
            )
        )
        assert get_requirements_commit(deps) == "abc1234"

    def test_returns_unknown_on_failure(self):
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _completed(returncode=1, stdout="")
        )
        assert get_requirements_commit(deps) == "unknown"

    def test_returns_unknown_on_empty_stdout(self):
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _completed(stdout="")
        )
        assert get_requirements_commit(deps) == "unknown"


# ---------------------------------------------------------------------------
# D — create_orchestration_task (main flow)
# ---------------------------------------------------------------------------

class TestCreateOrchestrationTaskNoRelease:
    def test_exits_1_when_no_releases_md(self):
        deps = make_deps(file_exists=lambda p: False)
        assert create_orchestration_task(deps, _make_args()) == 1

    def test_exits_1_when_releases_md_has_no_active_status(self):
        deps = make_deps(
            file_exists=lambda p: p.endswith("RELEASES.md"),
            read_file=lambda p: 'releases:\n  - version: "1.0.0"\n    status: planned\n',
        )
        assert create_orchestration_task(deps, _make_args()) == 1


class TestCreateOrchestrationTaskDuplicate:
    def test_exits_2_when_orchestration_task_exists(self):
        from create_orchestration_task import PROJECT_ROOT
        goal_path = str(
            PROJECT_ROOT
            / "requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-04-20_explore_x/goal.md"
        )

        def fake_read(p):
            if p.endswith("RELEASES.md"):
                return 'releases:\n  - version: "0.0.1"\n    status: active\n'
            return (
                'target_release: "0.0.1"\n'
                'scope_description: "Orchestration: create impl tasks"\n'
                "status: pending\n"
                "task_id: TASK-PROC-035-06\n"
            )

        deps = make_deps(
            file_exists=lambda p: p.endswith("RELEASES.md"),
            glob_files=lambda p: [goal_path],
            read_file=fake_read,
        )
        assert create_orchestration_task(deps, _make_args()) == 2


# ---------------------------------------------------------------------------
# Two-slot alternation guard (REQ-PROC-035 SEC-05)
# ---------------------------------------------------------------------------

def _orch_goal(task_id, status, version="0.0.1", scope="create impl tasks", after=None):
    after_line = f'after: [{", ".join(chr(34) + a + chr(34) for a in (after or []))}]\n'
    return (
        f"task_id: {task_id}\n"
        f'target_release: "{version}"\n'
        f"{after_line}"
        f'scope_description: "Orchestration: {scope}"\n'
        f"status: {status}\n"
    )


class TestFindExistingExcludesCaller:
    """find_existing_orchestration_task excludes the --after-task caller."""

    def test_caller_excluded_returns_none_when_caller_is_sole_nonterminal(self):
        from create_orchestration_task import PROJECT_ROOT
        caller = str(PROJECT_ROOT / "requirements_tasks/x/tasks/2026-05-14_explore_y/goal.md")
        deps = make_deps(
            glob_files=lambda p: [caller],
            read_file=lambda p: _orch_goal("TASK-PROC-035-17", "in_progress"),
        )
        assert find_existing_orchestration_task(deps, exclude_task_id="TASK-PROC-035-17") is None

    def test_different_nonterminal_still_returned(self):
        from create_orchestration_task import PROJECT_ROOT
        other = str(PROJECT_ROOT / "requirements_tasks/x/tasks/2026-05-14_explore_z/goal.md")
        deps = make_deps(
            glob_files=lambda p: [other],
            read_file=lambda p: _orch_goal("TASK-PROC-035-99", "pending"),
        )
        result = find_existing_orchestration_task(deps, exclude_task_id="TASK-PROC-035-17")
        assert result == other


class TestFindPredecessorSlotDir:
    """find_predecessor_slot_dir resolves the caller's after: target to a terminal slot dir.

    `--after-task` carries the CALLER's own id; the slot to reuse is the orch task named
    in the caller's `after:` list (its own predecessor), now terminal.
    """

    def _deps(self, files):
        return make_deps(
            glob_files=lambda p: list(files.keys()),
            read_file=lambda p: files.get(p, ""),
        )

    def test_returns_dir_of_caller_predecessor(self):
        from create_orchestration_task import PROJECT_ROOT
        caller = str(PROJECT_ROOT / "requirements_tasks/x/tasks/2026-05-14_explore_caller/goal.md")
        pred_dir = PROJECT_ROOT / "requirements_tasks/x/tasks/2026-04-29_explore_prev (completed)"
        pred = str(pred_dir / "goal.md")
        files = {
            caller: _orch_goal("TASK-PROC-035-17", "in_progress", after=["TASK-PROC-035-16"]),
            pred: _orch_goal("TASK-PROC-035-16", "completed"),
        }
        assert find_predecessor_slot_dir(self._deps(files), "TASK-PROC-035-17", "0.0.1") == str(pred_dir)

    def test_returns_none_when_predecessor_not_terminal(self):
        from create_orchestration_task import PROJECT_ROOT
        caller = str(PROJECT_ROOT / "requirements_tasks/x/tasks/2026-05-14_explore_caller/goal.md")
        pred = str(PROJECT_ROOT / "requirements_tasks/x/tasks/2026-04-29_explore_prev/goal.md")
        files = {
            caller: _orch_goal("TASK-PROC-035-17", "in_progress", after=["TASK-PROC-035-16"]),
            pred: _orch_goal("TASK-PROC-035-16", "in_progress"),
        }
        assert find_predecessor_slot_dir(self._deps(files), "TASK-PROC-035-17", "0.0.1") is None

    def test_returns_none_when_no_caller_id(self):
        deps = make_deps(glob_files=lambda p: [])
        assert find_predecessor_slot_dir(deps, "", "0.0.1") is None

    def test_returns_none_when_caller_has_no_after(self):
        from create_orchestration_task import PROJECT_ROOT
        caller = str(PROJECT_ROOT / "requirements_tasks/x/tasks/2026-05-14_explore_caller/goal.md")
        files = {caller: _orch_goal("TASK-PROC-035-17", "in_progress", after=[])}
        assert find_predecessor_slot_dir(self._deps(files), "TASK-PROC-035-17", "0.0.1") is None

    def test_returns_none_when_predecessor_wrong_release(self):
        from create_orchestration_task import PROJECT_ROOT
        caller = str(PROJECT_ROOT / "requirements_tasks/x/tasks/2026-05-14_explore_caller/goal.md")
        pred = str(PROJECT_ROOT / "requirements_tasks/x/tasks/2026-04-29_explore_prev (completed)/goal.md")
        files = {
            caller: _orch_goal("TASK-PROC-035-17", "in_progress", after=["TASK-PROC-035-16"]),
            pred: _orch_goal("TASK-PROC-035-16", "completed", version="0.0.2"),
        }
        assert find_predecessor_slot_dir(self._deps(files), "TASK-PROC-035-17", "0.0.1") is None


class TestTwoSlotAlternation:
    """End-to-end create_orchestration_task behaviour under the two-slot scheme."""

    def _make_chain_deps(self, goal_files, *, batch_exit3=False):
        """goal_files: dict mapping goal.md path -> content (the orch tasks on disk)."""
        from create_orchestration_task import PROJECT_ROOT
        written = {}
        removed_dirs = []
        made_dirs = []
        releases_path = str(PROJECT_ROOT / "requirements_tasks" / "RELEASES.md")

        batch_tasks = [
            {"task_name": "T1", "target_package": "Pkg", "task_type": "implement", "covers_acs": ["AC-01"]},
        ]

        def fake_subprocess(cmd, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "parse_task_creation_plan" in joined and "next-uncreated-package" in joined:
                if batch_exit3:
                    return _completed(returncode=3)
                return _completed(stdout=json.dumps(batch_tasks))
            if "allocate_task_id" in joined:
                return _completed(stdout="TASK-PROC-035-77")
            if "git" in joined:
                return _completed(stdout="abc1234 feat\n")
            return _completed()

        def fake_read(p):
            if p == releases_path:
                return 'releases:\n  - version: "0.0.1"\n    status: active\n'
            return goal_files.get(p, "")

        deps = make_deps(
            run_subprocess=fake_subprocess,
            makedirs=lambda p: made_dirs.append(p),
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: p == releases_path,
            remove_file=lambda p: None,
            remove_dir=lambda p: removed_dirs.append(p),
            glob_files=lambda p: list(goal_files.keys()),
            read_file=fake_read,
            get_today=lambda: "2026-05-28",
        )
        return deps, written, removed_dirs, made_dirs

    def test_self_perpetuation_succeeds_when_caller_sole_in_progress(self):
        from create_orchestration_task import PROJECT_ROOT
        caller = str(PROJECT_ROOT / "requirements_tasks/p/tasks/2026-05-14_explore_caller/goal.md")
        goal_files = {caller: _orch_goal("TASK-PROC-035-17", "in_progress")}
        deps, written, _removed, _made = self._make_chain_deps(goal_files)
        result = create_orchestration_task(
            deps, _make_args(after_task="TASK-PROC-035-17", plan_path="some/plan.md")
        )
        assert result == 0
        assert any("goal.md" in k for k in written)

    def test_overwrites_terminal_predecessor_slot(self):
        from create_orchestration_task import PROJECT_ROOT
        caller = str(PROJECT_ROOT / "requirements_tasks/p/tasks/2026-05-14_explore_caller/goal.md")
        pred_dir = PROJECT_ROOT / "requirements_tasks/p/tasks/2026-04-29_explore_prev (completed)"
        pred = str(pred_dir / "goal.md")
        # Caller (17, in_progress) passes its OWN id; its after: points to terminal pred (16).
        goal_files = {
            caller: _orch_goal("TASK-PROC-035-17", "in_progress", after=["TASK-PROC-035-16"]),
            pred: _orch_goal("TASK-PROC-035-16", "completed"),
        }
        deps, _written, removed, _made = self._make_chain_deps(goal_files)
        result = create_orchestration_task(
            deps, _make_args(after_task="TASK-PROC-035-17", plan_path="some/plan.md")
        )
        assert result == 0
        # The terminal predecessor folder is removed (slot reused, no third folder).
        assert str(pred_dir) in removed

    def test_fresh_create_when_no_prior_slot(self):
        from create_orchestration_task import PROJECT_ROOT
        caller = str(PROJECT_ROOT / "requirements_tasks/p/tasks/2026-05-14_explore_caller/goal.md")
        # Caller's after: points to a non-orch / absent task — no terminal slot to reuse.
        goal_files = {caller: _orch_goal("TASK-PROC-035-17", "in_progress", after=["TASK-EXPLORE-001"])}
        deps, written, removed, _made = self._make_chain_deps(goal_files)
        result = create_orchestration_task(
            deps, _make_args(after_task="TASK-PROC-035-17", plan_path="some/plan.md")
        )
        assert result == 0
        assert removed == []  # nothing overwritten — fresh folder created
        assert any("goal.md" in k for k in written)

    def test_validation_branch_overwrites_terminal_predecessor(self):
        from create_orchestration_task import PROJECT_ROOT
        caller = str(PROJECT_ROOT / "requirements_tasks/p/tasks/2026-05-14_explore_caller/goal.md")
        pred_dir = PROJECT_ROOT / "requirements_tasks/p/tasks/2026-04-29_explore_prev (completed)"
        pred = str(pred_dir / "goal.md")
        goal_files = {
            caller: _orch_goal("TASK-PROC-035-17", "in_progress", after=["TASK-PROC-035-16"]),
            pred: _orch_goal("TASK-PROC-035-16", "completed"),
        }
        deps, written, removed, _made = self._make_chain_deps(goal_files, batch_exit3=True)
        result = create_orchestration_task(
            deps, _make_args(after_task="TASK-PROC-035-17", plan_path="some/plan.md")
        )
        assert result == 0
        content = next(v for k, v in written.items() if "goal.md" in k)
        assert "Structural Validation" in content
        assert str(pred_dir) in removed

    def test_refuses_when_different_nonterminal_orch_exists(self):
        from create_orchestration_task import PROJECT_ROOT
        caller = str(PROJECT_ROOT / "requirements_tasks/p/tasks/2026-05-14_explore_caller/goal.md")
        other = str(PROJECT_ROOT / "requirements_tasks/p/tasks/2026-05-20_explore_other/goal.md")
        goal_files = {
            caller: _orch_goal("TASK-PROC-035-17", "in_progress"),
            other: _orch_goal("TASK-PROC-035-99", "pending"),
        }
        deps, _written, _removed, _made = self._make_chain_deps(goal_files)
        result = create_orchestration_task(
            deps, _make_args(after_task="TASK-PROC-035-17", plan_path="some/plan.md")
        )
        assert result == 2


class TestCreateOrchestrationTaskAllocError:
    def test_exits_4_when_allocate_task_id_fails(self):
        def fake_subprocess(cmd, **kw):
            if "allocate_task_id" in " ".join(str(c) for c in cmd):
                return _completed(returncode=1, stderr="lock error")
            return _completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            file_exists=lambda p: p.endswith("RELEASES.md"),
            read_file=lambda p: 'releases:\n  - version: "0.0.1"\n    status: active\n',
            glob_files=lambda p: [],
        )
        assert create_orchestration_task(deps, _make_args()) == 4


# ---------------------------------------------------------------------------
# T-B7: batch of 2 tasks → 4 ACs + orchestration_task: true
# ---------------------------------------------------------------------------

class TestCreateOrchestrationTaskBatchTwoTasks:
    """T-B7: Parse returns 2-task batch; goal.md has 4 AC lines and orchestration_task: true."""

    def _make_batch_deps(self, batch_json, extra=None):
        written = {}
        created_dirs = []

        batch_tasks = [
            {"task_name": "Task Alpha", "target_package": "Pkg A", "task_type": "implement", "covers_acs": ["AC-01", "AC-02"]},
            {"task_name": "Task Beta", "target_package": "Pkg A", "task_type": "implement", "covers_acs": ["AC-03"]},
        ]

        def fake_subprocess(cmd, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "parse_task_creation_plan" in joined and "next-uncreated-package" in joined:
                return _completed(stdout=json.dumps(batch_tasks))
            if "allocate_task_id" in joined:
                return _completed(stdout="TASK-PROC-035-88")
            if "git" in joined:
                return _completed(stdout="abc1234 feat: x\n")
            return _completed()

        deps_kwargs = {
            "run_subprocess": fake_subprocess,
            "makedirs": lambda p: created_dirs.append(p),
            "write_file": lambda p, c: written.update({p: c}),
            "file_exists": lambda p: p.endswith("RELEASES.md"),
            "remove_file": lambda p: None,
            "glob_files": lambda p: [],
            "read_file": lambda p: 'releases:\n  - version: "0.0.1"\n    status: active\n',
            "get_today": lambda: "2026-04-27",
        }
        if extra:
            deps_kwargs.update(extra)
        return make_deps(**deps_kwargs), written, created_dirs

    def _get_goal_content(self, written):
        return next(v for k, v in written.items() if "goal.md" in k)

    def test_exits_0(self):
        deps, _written, _ = self._make_batch_deps(None)
        result = create_orchestration_task(deps, _make_args(plan_path="some/plan.md"))
        assert result == 0

    def test_goal_contains_orchestration_task_true(self):
        deps, written, _ = self._make_batch_deps(None)
        create_orchestration_task(deps, _make_args(plan_path="some/plan.md"))
        content = self._get_goal_content(written)
        assert "orchestration_task: true" in content

    def test_goal_contains_exactly_4_ac_lines(self):
        deps, written, _ = self._make_batch_deps(None)
        create_orchestration_task(deps, _make_args(plan_path="some/plan.md"))
        content = self._get_goal_content(written)
        ac_lines = [line for line in content.splitlines() if line.strip().startswith("- [ ]")]
        assert len(ac_lines) == 4, f"Expected 4 AC lines, got {len(ac_lines)}: {ac_lines}"

    def test_goal_contains_task_names(self):
        deps, written, _ = self._make_batch_deps(None)
        create_orchestration_task(deps, _make_args(plan_path="some/plan.md"))
        content = self._get_goal_content(written)
        assert "Task Alpha" in content
        assert "Task Beta" in content


# ---------------------------------------------------------------------------
# T-B8: batch of 6 tasks → 8 ACs
# ---------------------------------------------------------------------------

class TestCreateOrchestrationTaskBatchSixTasks:
    """T-B8: Parse returns 6-task batch; goal.md has 8 AC lines."""

    def _make_6task_deps(self):
        written = {}
        batch_tasks = [
            {"task_name": f"Task {i}", "target_package": "BigPkg", "task_type": "implement", "covers_acs": [f"AC-0{i}"]}
            for i in range(1, 7)
        ]

        def fake_subprocess(cmd, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "parse_task_creation_plan" in joined and "next-uncreated-package" in joined:
                return _completed(stdout=json.dumps(batch_tasks))
            if "allocate_task_id" in joined:
                return _completed(stdout="TASK-PROC-035-89")
            if "git" in joined:
                return _completed(stdout="abc1234 feat\n")
            return _completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            makedirs=lambda p: None,
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: p.endswith("RELEASES.md"),
            remove_file=lambda p: None,
            glob_files=lambda p: [],
            read_file=lambda p: 'releases:\n  - version: "0.0.1"\n    status: active\n',
            get_today=lambda: "2026-04-27",
        )
        return deps, written

    def test_exactly_8_ac_lines(self):
        deps, written = self._make_6task_deps()
        create_orchestration_task(deps, _make_args(plan_path="some/plan.md"))
        content = next(v for k, v in written.items() if "goal.md" in k)
        ac_lines = [line for line in content.splitlines() if line.strip().startswith("- [ ]")]
        assert len(ac_lines) == 8, f"Expected 8 AC lines, got {len(ac_lines)}"


# ---------------------------------------------------------------------------
# T-B9: scribble task in batch → uses ui-scribble-iterate
# ---------------------------------------------------------------------------

class TestCreateOrchestrationTaskScribble:
    """T-B9: Scribble task in batch generates ui-scribble-iterate AC text."""

    def test_scribble_skill_in_ac(self):
        written = {}
        batch_tasks = [
            {"task_name": "Scribble Design", "target_package": "UI Pkg", "task_type": "scribble", "covers_acs": ["AC-01"]},
            {"task_name": "Regular Impl", "target_package": "UI Pkg", "task_type": "implement", "covers_acs": ["AC-02"]},
        ]

        def fake_subprocess(cmd, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "parse_task_creation_plan" in joined and "next-uncreated-package" in joined:
                return _completed(stdout=json.dumps(batch_tasks))
            if "allocate_task_id" in joined:
                return _completed(stdout="TASK-PROC-035-90")
            if "git" in joined:
                return _completed(stdout="abc1234 feat\n")
            return _completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            makedirs=lambda p: None,
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: p.endswith("RELEASES.md"),
            remove_file=lambda p: None,
            glob_files=lambda p: [],
            read_file=lambda p: 'releases:\n  - version: "0.0.1"\n    status: active\n',
            get_today=lambda: "2026-04-27",
        )
        create_orchestration_task(deps, _make_args(plan_path="some/plan.md"))
        content = next(v for k, v in written.items() if "goal.md" in k)
        assert "ui-scribble-iterate" in content
        assert "task-create-code" in content


# ---------------------------------------------------------------------------
# T-B10: scope_description includes package name and task count
# ---------------------------------------------------------------------------

class TestCreateOrchestrationTaskScopeDescription:
    """T-B10: scope_description matches REQ-PROC-035 SEC-05 wording."""

    def test_scope_description_wording(self):
        written = {}
        batch_tasks = [
            {"task_name": "Alpha Task", "target_package": "Transfer Data Model", "task_type": "implement", "covers_acs": ["AC-06"]},
            {"task_name": "Beta Task", "target_package": "Transfer Data Model", "task_type": "implement", "covers_acs": ["AC-07"]},
        ]

        def fake_subprocess(cmd, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "parse_task_creation_plan" in joined and "next-uncreated-package" in joined:
                return _completed(stdout=json.dumps(batch_tasks))
            if "allocate_task_id" in joined:
                return _completed(stdout="TASK-PROC-035-91")
            if "git" in joined:
                return _completed(stdout="abc1234 feat\n")
            return _completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            makedirs=lambda p: None,
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: p.endswith("RELEASES.md"),
            remove_file=lambda p: None,
            glob_files=lambda p: [],
            read_file=lambda p: 'releases:\n  - version: "0.0.1"\n    status: active\n',
            get_today=lambda: "2026-04-27",
        )
        create_orchestration_task(deps, _make_args(plan_path="some/plan.md"))
        content = next(v for k, v in written.items() if "goal.md" in k)
        assert "package Transfer Data Model" in content
        assert "(2 task(s))" in content


# ---------------------------------------------------------------------------
# T-B11: parse exits 3 → validation template with orchestration_task: true
# ---------------------------------------------------------------------------

class TestCreateOrchestrationTaskValidationTemplate:
    """T-B11: When parse exits 3, validation orch task is created with orchestration_task: true."""

    def test_validation_task_created_on_exit3(self):
        written = {}

        def fake_subprocess(cmd, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "parse_task_creation_plan" in joined and "next-uncreated-package" in joined:
                return _completed(returncode=3, stdout="")
            if "allocate_task_id" in joined:
                return _completed(stdout="TASK-PROC-035-92")
            if "git" in joined:
                return _completed(stdout="abc1234 feat\n")
            return _completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            makedirs=lambda p: None,
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: p.endswith("RELEASES.md"),
            remove_file=lambda p: None,
            glob_files=lambda p: [],
            read_file=lambda p: 'releases:\n  - version: "0.0.1"\n    status: active\n',
            get_today=lambda: "2026-04-27",
        )
        result = create_orchestration_task(deps, _make_args(plan_path="some/plan.md"))
        assert result == 0
        content = next(v for k, v in written.items() if "goal.md" in k)
        assert "Structural Validation" in content
        assert "orchestration_task: true" in content


# ---------------------------------------------------------------------------
# T-B12: dry_run → no write/makedirs calls
# ---------------------------------------------------------------------------

class TestCreateOrchestrationTaskDryRun:
    """T-B12: dry_run=True skips all file writes and makedirs regardless of coverage."""

    def _run_dry(self, plan_exits_3=False):
        wrote = []
        made = []

        def fake_subprocess(cmd, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "parse_task_creation_plan" in joined and "next-uncreated-package" in joined:
                if plan_exits_3:
                    return _completed(returncode=3)
                return _completed(stdout=json.dumps([
                    {"task_name": "T", "target_package": "P", "task_type": "implement", "covers_acs": []}
                ]))
            if "allocate_task_id" in joined:
                return _completed(stdout="TASK-PROC-035-93")
            return _completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            makedirs=lambda p: made.append(p),
            write_file=lambda p, c: wrote.append(p),
            file_exists=lambda p: p.endswith("RELEASES.md"),
            glob_files=lambda p: [],
            read_file=lambda p: 'releases:\n  - version: "0.0.1"\n    status: active\n',
        )
        result = create_orchestration_task(deps, _make_args(dry_run=True, plan_path="some/plan.md"))
        return result, wrote, made

    def test_dry_run_impl_no_writes(self):
        result, wrote, made = self._run_dry(plan_exits_3=False)
        assert result == 0
        assert wrote == []
        assert made == []

    def test_dry_run_all_covered_no_writes(self):
        result, wrote, made = self._run_dry(plan_exits_3=True)
        assert result == 0
        assert wrote == []
        assert made == []


# ---------------------------------------------------------------------------
# T-B13: empty stdout from parse (returncode 0) → placeholder AC created
# ---------------------------------------------------------------------------

class TestCreateOrchestrationTaskEmptyBatch:
    """T-B13: parse exits 0 but stdout is empty JSON → fallback placeholder impl task."""

    def test_empty_batch_creates_impl_task(self):
        written = {}

        def fake_subprocess(cmd, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "parse_task_creation_plan" in joined and "next-uncreated-package" in joined:
                return _completed(returncode=0, stdout="[]")
            if "allocate_task_id" in joined:
                return _completed(stdout="TASK-PROC-035-94")
            if "git" in joined:
                return _completed(stdout="abc1234 feat\n")
            return _completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            makedirs=lambda p: None,
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: p.endswith("RELEASES.md"),
            remove_file=lambda p: None,
            glob_files=lambda p: [],
            read_file=lambda p: 'releases:\n  - version: "0.0.1"\n    status: active\n',
            get_today=lambda: "2026-04-27",
        )
        result = create_orchestration_task(deps, _make_args(plan_path="some/plan.md"))
        assert result == 0
        # Should write a goal.md (impl orch task, not validation)
        assert any("goal.md" in k for k in written)
        content = next(v for k, v in written.items() if "goal.md" in k)
        assert "Structural Validation" not in content


# ---------------------------------------------------------------------------
# T-B14: reserve marker removed on success
# ---------------------------------------------------------------------------

class TestCreateOrchestrationTaskRemoveReserve:
    """T-B14: Reserve marker created by allocate_task_id.py is removed on success."""

    def test_removes_reserve_marker(self):
        removed = []
        batch_tasks = [
            {"task_name": "T1", "target_package": "Pkg", "task_type": "implement", "covers_acs": ["AC-01"]},
        ]

        def fake_subprocess(cmd, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "parse_task_creation_plan" in joined and "next-uncreated-package" in joined:
                return _completed(stdout=json.dumps(batch_tasks))
            if "allocate_task_id" in joined:
                return _completed(stdout="TASK-PROC-035-95")
            if "git" in joined:
                return _completed(stdout="abc1234 feat\n")
            return _completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
            file_exists=lambda p: "TASK-PROC-035-95" in p or p.endswith("RELEASES.md"),
            remove_file=lambda p: removed.append(p),
            glob_files=lambda p: [],
            read_file=lambda p: 'releases:\n  - version: "0.0.1"\n    status: active\n',
            get_today=lambda: "2026-04-27",
        )
        create_orchestration_task(deps, _make_args(plan_path="some/plan.md"))
        assert any("TASK-PROC-035-95" in r for r in removed)


# ---------------------------------------------------------------------------
# T-B15: task_id present in goal.md
# ---------------------------------------------------------------------------

class TestCreateOrchestrationTaskIdInGoal:
    """T-B15: The allocated task ID appears in the written goal.md content."""

    def test_task_id_in_goal_md(self):
        written = {}
        batch_tasks = [
            {"task_name": "T1", "target_package": "Pkg", "task_type": "implement", "covers_acs": []},
        ]

        def fake_subprocess(cmd, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "parse_task_creation_plan" in joined and "next-uncreated-package" in joined:
                return _completed(stdout=json.dumps(batch_tasks))
            if "allocate_task_id" in joined:
                return _completed(stdout="TASK-PROC-035-96")
            if "git" in joined:
                return _completed(stdout="abc1234 feat\n")
            return _completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            makedirs=lambda p: None,
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: p.endswith("RELEASES.md"),
            remove_file=lambda p: None,
            glob_files=lambda p: [],
            read_file=lambda p: 'releases:\n  - version: "0.0.1"\n    status: active\n',
            get_today=lambda: "2026-04-27",
        )
        create_orchestration_task(deps, _make_args(plan_path="some/plan.md"))
        content = next(v for k, v in written.items() if "goal.md" in k)
        assert "TASK-PROC-035-96" in content


# ---------------------------------------------------------------------------
# Unit tests for _build_ac_block helper
# ---------------------------------------------------------------------------

class TestBuildAcBlock:
    def test_two_tasks_produces_4_lines(self):
        tasks = [
            {"task_name": "Alpha", "task_type": "implement", "covers_acs": ["AC-01"]},
            {"task_name": "Beta", "task_type": "implement", "covers_acs": ["AC-02"]},
        ]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "some/plan.md")
        lines = result.splitlines()
        assert len(lines) == 4

    def test_scribble_uses_correct_skill(self):
        tasks = [{"task_name": "Sketch", "task_type": "scribble", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "plan.md")
        assert "ui-scribble-iterate" in result
        assert "task-create-code" not in result

    def test_impl_uses_task_create_code(self):
        tasks = [{"task_name": "Code", "task_type": "implement", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "plan.md")
        assert "task-create-code" in result

    def test_covers_acs_in_line(self):
        tasks = [{"task_name": "T", "task_type": "implement", "covers_acs": ["AC-01", "AC-02"]}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "plan.md")
        assert "AC-01, AC-02" in result

    def test_empty_batch_produces_2_lines(self):
        result = _build_ac_block([], "TASK-PROC-035-99", "plan.md")
        lines = result.splitlines()
        assert len(lines) == 2

    def test_chain_line_contains_task_id(self):
        tasks = [{"task_name": "T", "task_type": "implement", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "some/plan.md")
        assert "TASK-PROC-035-99" in result
        assert "create_orchestration_task.py" in result

    def test_complete_line_contains_task_id(self):
        tasks = [{"task_name": "T", "task_type": "implement", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-55", "plan.md")
        assert "task-complete" in result
        assert "TASK-PROC-035-55" in result

    # Regression: plan_path with spaces and (completed) parens used to produce
    # an unquoted bash command that errored with "syntax error near unexpected
    # token '('", silently breaking the orch chain (TASK-PROC-035-16 incident).
    def test_plan_path_with_parens_is_shell_safe(self):
        import re as _re

        tasks = [{"task_name": "T", "task_type": "implement", "covers_acs": []}]
        plan_path = "requirements_tasks/foo/2026-04-25_explore_x (completed)/plan.md"
        result = _build_ac_block(tasks, "TASK-PROC-035-99", plan_path)

        chain_line = next(
            line for line in result.splitlines() if "create_orchestration_task.py" in line
        )
        match = _re.search(r"`([^`]+)`", chain_line)
        assert match, "chain line must contain a backtick-wrapped command"
        command = match.group(1)

        proc = subprocess.run(
            ["bash", "-n", "-c", command], capture_output=True, text=True
        )
        assert proc.returncode == 0, f"bash rejected the command: {proc.stderr}"

    def test_plain_plan_path_is_unchanged_in_command(self):
        tasks = [{"task_name": "T", "task_type": "implement", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "some/plan.md")
        assert "--plan-path some/plan.md" in result

    def test_verify_uses_task_create(self):
        tasks = [{"task_name": "Verify Coverage", "task_type": "verify", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "plan.md")
        assert "task-create" in result
        assert "task-create-code" not in result

    def test_verification_alias_uses_task_create(self):
        tasks = [{"task_name": "Verify Step", "task_type": "verification", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "plan.md")
        assert "task-create" in result
        assert "task-create-code" not in result

    def test_explore_uses_task_create(self):
        tasks = [{"task_name": "Explore Design", "task_type": "explore", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "plan.md")
        assert "task-create" in result
        assert "task-create-code" not in result

    def test_scribble_to_flutter_uses_task_create_code(self):
        tasks = [{"task_name": "Flutter Impl", "task_type": "scribble_to_flutter", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "plan.md")
        assert "task-create-code" in result
        assert "ui-scribble-iterate" not in result

    def test_impl_with_lib_notes_uses_task_create_code(self):
        tasks = [{"task_name": "Code Task", "task_type": "implement",
                  "implementation_notes": "Modify lib/domain/foo.dart", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "plan.md")
        assert "task-create-code" in result

    def test_impl_with_non_code_notes_uses_task_create(self):
        tasks = [{"task_name": "Skill Edit", "task_type": "implement",
                  "implementation_notes": "Update .claude/skills/foo/SKILL.md", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "plan.md")
        assert "task-create" in result
        assert "task-create-code" not in result

    def test_impl_without_notes_defaults_to_task_create_code(self):
        """Backward compat: no implementation_notes → old behaviour (task-create-code)."""
        tasks = [{"task_name": "Legacy", "task_type": "implement", "covers_acs": []}]
        result = _build_ac_block(tasks, "TASK-PROC-035-99", "plan.md")
        assert "task-create-code" in result


# ---------------------------------------------------------------------------
# CLI choices: --task-type explore must be accepted by argparse
# ---------------------------------------------------------------------------

class TestParseArgsTaskTypeChoices:
    def test_explore_is_accepted_by_argparse(self):
        """Regression: 'explore' was missing from CLI choices despite being handled
        in _build_ac_block routing. Argparse must accept it without error."""
        args = parse_args(["--task-type", "explore"])
        assert args.task_type == "explore"

    def test_all_valid_task_types_accepted(self):
        """Verify all documented task types are accepted by argparse."""
        for t in ["implement", "verify", "explore", "scribble", "scribble_to_flutter"]:
            args = parse_args(["--task-type", t])
            assert args.task_type == t
