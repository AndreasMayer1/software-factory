"""Tests for parse_task_creation_plan.py — --next-uncreated-package mode.

Covers tests T-A1 through T-A8 from:
  requirements_tasks/.../plans_and_protocols/2026-04-27_01_opus_impl_plan.md#agent-a
"""

import json
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Helpers for building synthetic plan files and goal.md files
# ---------------------------------------------------------------------------

PLAN_HEADER = textwrap.dedent("""\
    ---
    status: active
    ---

    """)


def _make_plan(packages: list[dict[Any, Any]]) -> str:
    """Build a minimal task_creation_plan.md body with the given packages.

    Each package dict has:
        name: str         — used as heading text (e.g. "Transfer Data Model")
        tasks: list[dict] — each dict has keys: task_name, req_id,
                            target_package, covers_acs, task_type, effort, layer
    """
    lines = [PLAN_HEADER]
    for pkg in packages:
        lines.append(f"### PKG: {pkg['name']}\n")
        for i, task in enumerate(pkg["tasks"], start=1):
            acs = ", ".join(task.get("covers_acs", []))
            lines.append(f"#### Task {i}: {task['task_name']}\n")
            lines.append("```yaml")
            lines.append(f"task_name: \"{task['task_name']}\"")
            lines.append(f"target_package: \"{task.get('target_package', pkg['name'])}\"")
            lines.append(f"req_id: \"{task.get('req_id', 'REQ-TEST-001')}\"")
            lines.append(f"covers_acs: [{acs}]")
            lines.append(f"task_type: \"{task.get('task_type', 'impl')}\"")
            lines.append(f"effort: \"{task.get('effort', 'M')}\"")
            lines.append(f"layer: \"{task.get('layer', 'data')}\"")
            lines.append("```\n")
    return "\n".join(lines)


def _make_goal_md(
    target_package: str,
    parent_requirement: str,
    covers_acs: list[str],
    task_type: str = "impl",
) -> str:
    """Build a minimal goal.md frontmatter that matches task-create-code output."""
    acs_yaml = "\n".join(f"    - {ac}" for ac in covers_acs)
    return textwrap.dedent(f"""\
        ---
        target_package: "{target_package}"
        parent_requirement: "{parent_requirement}"
        task_type: "{task_type}"
        covers:
          acceptance_criteria:
{acs_yaml}
          sections: []
        ---
        # Goal
        """)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def plan_dir(tmp_path: Path) -> Path:
    """Return a temp directory usable as a synthetic requirements_tasks root."""
    return tmp_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestNextUncreatedPackage:
    """T-A1 through T-A8 from the Opus plan."""

    # -------------------------------------------------------------------
    # T-A1: returns all tasks for first uncreated package as JSON array
    # -------------------------------------------------------------------
    def test_t_a1_returns_first_package_tasks(self, tmp_path: Path, plan_dir: Path) -> None:
        plan_content = _make_plan([
            {
                "name": "Package Alpha",
                "tasks": [
                    {"task_name": "Task 1", "req_id": "REQ-001", "target_package": "Package Alpha",
                     "covers_acs": ["AC-01", "AC-02"]},
                    {"task_name": "Task 2", "req_id": "REQ-001", "target_package": "Package Alpha",
                     "covers_acs": ["AC-03"]},
                ],
            }
        ])
        plan_file = tmp_path / "task_creation_plan.md"
        plan_file.write_text(plan_content)

        from scripts.tasks.parse_task_creation_plan import (
            _find_next_uncreated_package,
            parse_plan,
        )
        result = parse_plan(str(plan_file))
        batch = _find_next_uncreated_package(result, plan_dir)

        assert batch is not None
        assert len(batch) == 2
        assert batch[0]["task_name"] == "Task 1"
        assert batch[1]["task_name"] == "Task 2"

    # -------------------------------------------------------------------
    # T-A2: caps at 6 tasks even when package has 8 plan entries
    # -------------------------------------------------------------------
    def test_t_a2_capped_at_six(self, tmp_path: Path, plan_dir: Path) -> None:
        tasks = [
            {"task_name": f"Task {i}", "req_id": "REQ-002", "target_package": "Big Package",
             "covers_acs": [f"AC-{i:02d}"]}
            for i in range(1, 9)  # 8 tasks
        ]
        plan_content = _make_plan([{"name": "Big Package", "tasks": tasks}])
        plan_file = tmp_path / "task_creation_plan.md"
        plan_file.write_text(plan_content)

        from scripts.tasks.parse_task_creation_plan import (
            _find_next_uncreated_package,
            parse_plan,
        )
        result = parse_plan(str(plan_file))
        batch = _find_next_uncreated_package(result, plan_dir)

        assert batch is not None
        assert len(batch) == 6

    # -------------------------------------------------------------------
    # T-A3: exits 3 when every plan entry has a matching goal.md
    # -------------------------------------------------------------------
    def test_t_a3_exits_3_all_created(self, tmp_path: Path, plan_dir: Path) -> None:
        plan_content = _make_plan([
            {
                "name": "Done Package",
                "tasks": [
                    {"task_name": "Task A", "req_id": "REQ-003", "target_package": "Done Package",
                     "covers_acs": ["AC-01"]},
                ],
            }
        ])
        plan_file = tmp_path / "task_creation_plan.md"
        plan_file.write_text(plan_content)

        # Create matching goal.md
        goal_dir = plan_dir / "feat_done" / "tasks" / "2026-01-01_impl_done-task"
        goal_dir.mkdir(parents=True)
        (goal_dir / "goal.md").write_text(
            _make_goal_md("Done Package", "REQ-003", ["AC-01"])
        )

        from scripts.tasks.parse_task_creation_plan import (
            _find_next_uncreated_package,
            parse_plan,
        )
        result = parse_plan(str(plan_file))
        batch = _find_next_uncreated_package(result, plan_dir)

        assert batch is None

    # -------------------------------------------------------------------
    # T-A4: skips a fully-created package and returns the next package's tasks
    # -------------------------------------------------------------------
    def test_t_a4_skips_created_returns_next(self, tmp_path: Path, plan_dir: Path) -> None:
        plan_content = _make_plan([
            {
                "name": "First Package",
                "tasks": [
                    {"task_name": "Task F1", "req_id": "REQ-010", "target_package": "First Package",
                     "covers_acs": ["AC-01"]},
                ],
            },
            {
                "name": "Second Package",
                "tasks": [
                    {"task_name": "Task S1", "req_id": "REQ-020", "target_package": "Second Package",
                     "covers_acs": ["AC-01"]},
                ],
            },
        ])
        plan_file = tmp_path / "task_creation_plan.md"
        plan_file.write_text(plan_content)

        # Create goal.md only for First Package
        goal_dir = plan_dir / "tasks" / "2026-01-01_impl_first"
        goal_dir.mkdir(parents=True)
        (goal_dir / "goal.md").write_text(
            _make_goal_md("First Package", "REQ-010", ["AC-01"])
        )

        from scripts.tasks.parse_task_creation_plan import (
            _find_next_uncreated_package,
            parse_plan,
        )
        result = parse_plan(str(plan_file))
        batch = _find_next_uncreated_package(result, plan_dir)

        assert batch is not None
        assert len(batch) == 1
        assert batch[0]["task_name"] == "Task S1"
        assert batch[0]["target_package"] == "Second Package"

    # -------------------------------------------------------------------
    # T-A5: regression — heading "PKG: Transfer Data Model" with task
    #        target_package "Transfer Data Model" matches goal.md that has
    #        target_package "Transfer Data Model" (prefix irrelevant)
    # -------------------------------------------------------------------
    def test_t_a5_pkg_prefix_regression(self, tmp_path: Path, plan_dir: Path) -> None:
        """Heading 'PKG: Transfer Data Model' must match goal.md 'Transfer Data Model'."""
        plan_content = _make_plan([
            {
                "name": "Transfer Data Model",  # heading becomes "### PKG: Transfer Data Model"
                "tasks": [
                    {"task_name": "Implement model", "req_id": "REQ-FUNC-007-03",
                     "target_package": "Transfer Data Model",
                     "covers_acs": ["AC-06", "AC-07"]},
                ],
            }
        ])
        plan_file = tmp_path / "task_creation_plan.md"
        plan_file.write_text(plan_content)

        # Goal.md uses the plain package name (no "PKG: " prefix)
        goal_dir = plan_dir / "tasks" / "2026-01-01_impl_tdm"
        goal_dir.mkdir(parents=True)
        (goal_dir / "goal.md").write_text(
            _make_goal_md("Transfer Data Model", "REQ-FUNC-007-03", ["AC-06", "AC-07"])
        )

        from scripts.tasks.parse_task_creation_plan import (
            _find_next_uncreated_package,
            parse_plan,
        )
        result = parse_plan(str(plan_file))
        batch = _find_next_uncreated_package(result, plan_dir)

        # Should be None — task already created; match must succeed
        assert batch is None

    # -------------------------------------------------------------------
    # T-A6: --next-uncreated returns a single dict (not a list) for the
    #        first uncreated task when no goal.md files exist at all
    # -------------------------------------------------------------------
    def test_t_a6_next_uncreated_backward_compat(self, tmp_path: Path, plan_dir: Path) -> None:
        plan_content = _make_plan([
            {
                "name": "Compat Package",
                "tasks": [
                    {"task_name": "Task 1", "req_id": "REQ-099", "target_package": "Compat Package",
                     "covers_acs": ["AC-01"]},
                    {"task_name": "Task 2", "req_id": "REQ-099", "target_package": "Compat Package",
                     "covers_acs": ["AC-02"]},
                ],
            }
        ])
        plan_file = tmp_path / "task_creation_plan.md"
        plan_file.write_text(plan_content)

        from scripts.tasks.parse_task_creation_plan import (
            _find_next_uncreated,
            parse_plan,
        )
        result = parse_plan(str(plan_file))
        # plan_dir has no goal.md files — tuple match finds nothing created,
        # so the first task in document order is returned as a single dict.
        task = _find_next_uncreated(result, plan_dir)

        assert task is not None
        # Must return a single dict (not a list)
        assert isinstance(task, dict)
        assert task["task_name"] == "Task 1"

    # -------------------------------------------------------------------
    # Regression: when an exact (target_package, req_id, covers_acs) tuple
    # match exists in goal.md, _find_next_uncreated must return None.
    # -------------------------------------------------------------------
    def test_find_next_uncreated_exact_tuple_suppresses_task(
        self, tmp_path: Path, plan_dir: Path
    ) -> None:
        plan_content = _make_plan([
            {
                "name": "Transfer Data Model",
                "tasks": [
                    {"task_name": "T1", "req_id": "REQ-FUNC-007-03",
                     "target_package": "Transfer Data Model",
                     "covers_acs": ["AC-06"]},
                ],
            }
        ])
        plan_file = tmp_path / "task_creation_plan.md"
        plan_file.write_text(plan_content)

        goal_dir = plan_dir / "tasks" / "2026-01-01_impl_tdm"
        goal_dir.mkdir(parents=True)
        (goal_dir / "goal.md").write_text(
            _make_goal_md("Transfer Data Model", "REQ-FUNC-007-03", ["AC-06"])
        )

        from scripts.tasks.parse_task_creation_plan import (
            _find_next_uncreated,
            parse_plan,
        )
        result = parse_plan(str(plan_file))
        task = _find_next_uncreated(result, plan_dir)

        # Exact tuple match → task is covered → nothing uncreated.
        assert task is None

    # -------------------------------------------------------------------
    # Regression (TASK-PROC-035-17): a legacy goal.md with the same
    # target_package but a different (req_id, covers_acs) must NOT suppress
    # a plan task.  The old package-name heuristic returned exit-3 here;
    # the tuple-match implementation must return the plan task instead.
    # -------------------------------------------------------------------
    def test_find_next_uncreated_legacy_task_does_not_suppress(
        self, tmp_path: Path, plan_dir: Path
    ) -> None:
        plan_content = _make_plan([
            {
                "name": "Adaptive Scanner Settings",
                "tasks": [
                    {"task_name": "Impl Windows Screen Capture Session Path",
                     "req_id": "REQ-FUNC-NEW",
                     "target_package": "Adaptive Scanner Settings",
                     "covers_acs": ["AC-15", "AC-16"]},
                ],
            }
        ])
        plan_file = tmp_path / "task_creation_plan.md"
        plan_file.write_text(plan_content)

        # Legacy goal.md: same package, but different req and ACs.
        goal_dir = plan_dir / "tasks" / "2026-03-13_impl_legacy-scanner"
        goal_dir.mkdir(parents=True)
        (goal_dir / "goal.md").write_text(
            _make_goal_md("Adaptive Scanner Settings", "REQ-FUNC-OLD", ["AC-01", "AC-02"])
        )

        from scripts.tasks.parse_task_creation_plan import (
            _find_next_uncreated,
            parse_plan,
        )
        result = parse_plan(str(plan_file))
        task = _find_next_uncreated(result, plan_dir)

        # The plan task does NOT match the legacy goal.md tuple → must be returned.
        assert task is not None
        assert task["task_name"] == "Impl Windows Screen Capture Session Path"

    # -------------------------------------------------------------------
    # T-A7: same target_package but different parent_requirement → no match
    # -------------------------------------------------------------------
    def test_t_a7_different_parent_requirement_no_match(self, tmp_path: Path, plan_dir: Path) -> None:
        plan_content = _make_plan([
            {
                "name": "Shared Package",
                "tasks": [
                    {"task_name": "Task X", "req_id": "REQ-111", "target_package": "Shared Package",
                     "covers_acs": ["AC-01"]},
                ],
            }
        ])
        plan_file = tmp_path / "task_creation_plan.md"
        plan_file.write_text(plan_content)

        # goal.md has same target_package but different parent_requirement
        goal_dir = plan_dir / "tasks" / "2026-01-01_impl_other"
        goal_dir.mkdir(parents=True)
        (goal_dir / "goal.md").write_text(
            _make_goal_md("Shared Package", "REQ-999", ["AC-01"])  # different req
        )

        from scripts.tasks.parse_task_creation_plan import (
            _find_next_uncreated_package,
            parse_plan,
        )
        result = parse_plan(str(plan_file))
        batch = _find_next_uncreated_package(result, plan_dir)

        # REQ-111 task not matched by REQ-999 goal.md → package still uncreated
        assert batch is not None
        assert len(batch) == 1
        assert batch[0]["task_name"] == "Task X"

    # -------------------------------------------------------------------
    # T-A8: never returns empty list — either ≥1 task or None (exit 3)
    # -------------------------------------------------------------------
    def test_t_a8_never_returns_empty_list(self, tmp_path: Path, plan_dir: Path) -> None:
        """The function must return None (not []) when all packages are created."""
        plan_content = _make_plan([
            {
                "name": "Full Package",
                "tasks": [
                    {"task_name": "Task Z", "req_id": "REQ-888", "target_package": "Full Package",
                     "covers_acs": ["AC-01", "AC-02"]},
                ],
            }
        ])
        plan_file = tmp_path / "task_creation_plan.md"
        plan_file.write_text(plan_content)

        # Create matching goal.md for every plan entry
        goal_dir = plan_dir / "tasks" / "2026-01-01_impl_full"
        goal_dir.mkdir(parents=True)
        (goal_dir / "goal.md").write_text(
            _make_goal_md("Full Package", "REQ-888", ["AC-01", "AC-02"])
        )

        from scripts.tasks.parse_task_creation_plan import (
            _find_next_uncreated_package,
            _is_task_created,
            _load_all_created_tasks,
            parse_plan,
        )
        result = parse_plan(str(plan_file))
        _ = _load_all_created_tasks(plan_dir)
        _ = result["packages"][0]["tasks"][0]
        _ = _is_task_created
        batch = _find_next_uncreated_package(result, plan_dir)

        # Must be None, not []
        assert batch is None
        assert batch != []


class TestCLINextUncreatedPackage:
    """CLI integration tests for --next-uncreated-package flag."""

    def _run_cli(self, plan_file: Path, *extra_args: str) -> subprocess.CompletedProcess[Any]:
        script = (
            Path(__file__).parent.parent / "tasks" / "parse_task_creation_plan.py"
        )
        return subprocess.run(
            [sys.executable, str(script), "--plan", str(plan_file), *extra_args],
            capture_output=True,
            text=True,
        )

    def test_cli_exits_0_with_json_array(self, tmp_path: Path) -> None:
        plan_content = _make_plan([
            {
                "name": "CLI Package",
                "tasks": [
                    {"task_name": "CLI Task 1", "req_id": "REQ-CLI-001",
                     "target_package": "CLI Package", "covers_acs": ["AC-01"]},
                ],
            }
        ])
        plan_file = tmp_path / "task_creation_plan.md"
        plan_file.write_text(plan_content)

        proc = self._run_cli(plan_file, "--next-uncreated-package")
        assert proc.returncode == 0
        parsed = json.loads(proc.stdout)
        assert isinstance(parsed, list)
        assert len(parsed) >= 1

    def test_help_shows_flag(self) -> None:
        script = Path(__file__).parent.parent / "tasks" / "parse_task_creation_plan.py"
        proc = subprocess.run(
            [sys.executable, str(script), "--help"],
            capture_output=True,
            text=True,
        )
        assert "--next-uncreated-package" in proc.stdout
