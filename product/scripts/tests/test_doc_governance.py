"""
test_doc_governance.py — Tests for scripts/doc_governance.py
"""

import argparse
import os
import subprocess
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "artifacts"))

from doc_governance import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    PROJECT_ROOT,
    Deps,
    _depth_violation,
    _is_excluded,
    find_pending_split_task,
    run,
    scan_violations,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _completed(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[Any]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def _make_args(
    list_violations: bool = False,
    check: bool = False,
    check_depth: bool = False,
    dry_run: bool = False,
) -> argparse.Namespace:
    return argparse.Namespace(
        list_violations=list_violations,
        check=check,
        check_depth=check_depth,
        dry_run=dry_run,
    )


def make_deps(**overrides: Any) -> Deps:
    defaults = {
        "list_files": lambda root: [],
        "count_lines": lambda path: 0,
        "glob_dirs": lambda pattern: [],
        "read_file": lambda path: "",
        "makedirs": lambda path: None,
        "write_file": lambda path, content: None,
        "run_subprocess": lambda *a, **kw: _completed(),
        "get_today": lambda: "2026-04-30",
    }
    defaults.update(overrides)
    return Deps(**defaults)


# ---------------------------------------------------------------------------
# A — _is_excluded helper
# ---------------------------------------------------------------------------

class TestIsExcluded:
    def test_readme_is_excluded(self):
        assert _is_excluded(str(PROJECT_ROOT / "doc/testing/README.md"))

    def test_readme_in_subfolder_is_excluded(self):
        assert _is_excluded(str(PROJECT_ROOT / "doc/architecture/sub/README.md"))

    def test_from_figma_is_excluded(self):
        assert _is_excluded(str(PROJECT_ROOT / "doc/from_figma/some_file.md"))

    def test_general_is_excluded(self):
        assert _is_excluded(str(PROJECT_ROOT / "doc/general/guide.md"))

    def test_in_scope_not_excluded(self):
        assert not _is_excluded(str(PROJECT_ROOT / "doc/testing/widget_testing.md"))

    def test_presentation_not_excluded(self):
        assert not _is_excluded(str(PROJECT_ROOT / "doc/presentation/design.md"))


# ---------------------------------------------------------------------------
# B — _depth_violation helper
# ---------------------------------------------------------------------------

class TestDepthViolation:
    def test_depth_1_is_ok(self):
        # doc/testing/file.md → depth 1
        assert not _depth_violation(str(PROJECT_ROOT / "doc/testing/file.md"))

    def test_depth_2_is_ok(self):
        # doc/testing/presentation/widget_testing.md → depth 2
        assert not _depth_violation(str(PROJECT_ROOT / "doc/testing/presentation/widget_testing.md"))

    def test_depth_3_is_violation(self):
        # doc/testing/presentation/bloc/events.md → depth 3
        assert _depth_violation(str(PROJECT_ROOT / "doc/testing/presentation/bloc/events.md"))

    def test_depth_4_is_violation(self):
        assert _depth_violation(str(PROJECT_ROOT / "doc/a/b/c/d/file.md"))


# ---------------------------------------------------------------------------
# C — scan_violations
# ---------------------------------------------------------------------------

class TestScanFindsInScopeViolations:
    def test_scan_finds_in_scope_violations(self):
        """A 601-line file in doc/testing/ is detected as a violation."""
        testing_path = str(PROJECT_ROOT / "doc/testing/some_guide.md")

        def fake_list_files(root):
            if "testing" in root:
                return [testing_path]
            return []

        deps = make_deps(
            list_files=fake_list_files,
            count_lines=lambda path: 601,
        )
        violations = scan_violations(deps)
        assert len(violations) == 1
        assert violations[0][0] == testing_path
        assert violations[0][1] == 601

    def test_scan_excludes_readme(self):
        """README.md is not counted as a violation even if large."""
        readme_path = str(PROJECT_ROOT / "doc/testing/README.md")

        def fake_list_files(root):
            if "testing" in root:
                return [readme_path]
            return []

        deps = make_deps(
            list_files=fake_list_files,
            count_lines=lambda path: 9999,
        )
        violations = scan_violations(deps)
        assert len(violations) == 0

    def test_scan_excludes_from_figma(self):
        """doc/from_figma/ is not scanned at all (not in in-scope roots)."""
        figma_path = str(PROJECT_ROOT / "doc/from_figma/big_file.md")

        def fake_list_files(root):
            # from_figma is not in _IN_SCOPE_ROOTS, so it is never passed to list_files
            # but if somehow it appears under a different root, it should be excluded
            return [figma_path]

        deps = make_deps(
            list_files=fake_list_files,
            count_lines=lambda path: 9999,
        )
        # Since from_figma is not in _IN_SCOPE_ROOTS, list_files will never be called
        # for it. But even if a figma path slips through, _is_excluded catches it.
        violations = scan_violations(deps)
        # All returned paths are excluded (from_figma or README)
        assert all(
            "from_figma" not in path for path, _ in violations
        )

    def test_under_limit_not_reported(self):
        """Files under 600 lines are not violations."""
        path = str(PROJECT_ROOT / "doc/testing/small.md")

        deps = make_deps(
            list_files=lambda root: [path] if "testing" in root else [],
            count_lines=lambda path: 599,
        )
        assert scan_violations(deps) == []

    def test_exactly_600_is_violation(self):
        """600 lines exactly meets the threshold (>= 600)."""
        path = str(PROJECT_ROOT / "doc/architecture/guide.md")

        deps = make_deps(
            list_files=lambda root: [path] if "architecture" in root else [],
            count_lines=lambda path: 600,
        )
        violations = scan_violations(deps)
        assert len(violations) == 1


# ---------------------------------------------------------------------------
# D — --check mode exit codes
# ---------------------------------------------------------------------------

class TestCheckMode:
    def test_check_mode_exits_0_when_clean(self):
        deps = make_deps(
            list_files=lambda root: [],
        )
        assert run(deps, _make_args(check=True)) == 0

    def test_check_mode_exits_1_when_violation(self):
        path = str(PROJECT_ROOT / "doc/testing/big.md")
        deps = make_deps(
            list_files=lambda root: [path] if "testing" in root else [],
            count_lines=lambda p: 700,
        )
        assert run(deps, _make_args(check=True)) == 1


# ---------------------------------------------------------------------------
# E — dedup logic
# ---------------------------------------------------------------------------

class TestDedup:
    def _make_task_folder(self, task_name: str) -> str:
        return str(
            PROJECT_ROOT
            / "requirements_tasks/process/documentation_rules/guideline_file_organization/tasks"
            / task_name
        )

    def test_dedup_skips_when_pending_exists(self):
        """No task created when a pending split task exists."""
        folder = self._make_task_folder("2026-04-30_impl_split-oversized-doc-files")
        written = []

        deps = make_deps(
            list_files=lambda root: [str(PROJECT_ROOT / "doc/testing/big.md")] if "testing" in root else [],
            count_lines=lambda p: 700,
            glob_dirs=lambda pattern: [folder],
            read_file=lambda p: "status: pending\n",
            write_file=lambda p, c: written.append(p),
        )
        result = run(deps, _make_args())
        assert result == 0
        assert written == []

    def test_dedup_creates_when_only_inprogress(self):
        """Task created when only in_progress task exists."""
        folder = self._make_task_folder("2026-04-30_impl_split-oversized-doc-files")
        written = []

        def fake_glob(pattern):
            if "split-oversized" in pattern:
                return [folder]
            return []

        deps = make_deps(
            list_files=lambda root: [str(PROJECT_ROOT / "doc/testing/big.md")] if "testing" in root else [],
            count_lines=lambda p: 700,
            glob_dirs=fake_glob,
            read_file=lambda p: "status: in_progress\n",
            makedirs=lambda p: None,
            write_file=lambda p, c: written.append(p),
            run_subprocess=lambda *a, **kw: _completed(stdout="TASK-PROC-048-05"),
        )
        result = run(deps, _make_args())
        assert result == 0
        assert any("goal.md" in p for p in written)

    def test_dedup_creates_when_no_task_exists(self):
        """Task created when no matching task exists."""
        written = []

        deps = make_deps(
            list_files=lambda root: [str(PROJECT_ROOT / "doc/testing/big.md")] if "testing" in root else [],
            count_lines=lambda p: 700,
            glob_dirs=lambda pattern: [],
            makedirs=lambda p: None,
            write_file=lambda p, c: written.append(p),
            run_subprocess=lambda *a, **kw: _completed(stdout="TASK-PROC-048-06"),
        )
        result = run(deps, _make_args())
        assert result == 0
        assert any("goal.md" in p for p in written)


# ---------------------------------------------------------------------------
# F — task creation writes correct goal.md
# ---------------------------------------------------------------------------

class TestTaskCreationWritesGoalMd:
    def test_task_creation_writes_goal_md(self):
        """Correct goal.md content written when a violation is detected."""
        written = {}

        deps = make_deps(
            list_files=lambda root: [str(PROJECT_ROOT / "doc/testing/big.md")] if "testing" in root else [],
            count_lines=lambda p: 700,
            glob_dirs=lambda pattern: [],
            makedirs=lambda p: None,
            write_file=lambda p, c: written.update({p: c}),
            run_subprocess=lambda *a, **kw: _completed(stdout="TASK-PROC-048-07"),
            get_today=lambda: "2026-04-30",
        )
        result = run(deps, _make_args())
        assert result == 0
        assert any("goal.md" in p for p in written)
        content = next(v for k, v in written.items() if "goal.md" in k)
        assert "TASK-PROC-048-07" in content
        assert "task_id:" in content
        assert "status: pending" in content
        assert "Split Oversized doc/ Guideline Files" in content
        assert "AC-01" in content


# ---------------------------------------------------------------------------
# G — --dry-run does not write files
# ---------------------------------------------------------------------------

class TestDryRun:
    def test_dry_run_does_not_write(self):
        """No files written with --dry-run."""
        written = []
        made = []

        deps = make_deps(
            list_files=lambda root: [str(PROJECT_ROOT / "doc/testing/big.md")] if "testing" in root else [],
            count_lines=lambda p: 700,
            glob_dirs=lambda pattern: [],
            makedirs=lambda p: made.append(p),
            write_file=lambda p, c: written.append(p),
            run_subprocess=lambda *a, **kw: _completed(stdout="TASK-PROC-048-08"),
        )
        result = run(deps, _make_args(dry_run=True))
        assert result == 0
        assert written == []
        assert made == []


# ---------------------------------------------------------------------------
# H — --list-violations exit code
# ---------------------------------------------------------------------------

class TestListViolations:
    def test_list_violations_exits_1_when_violations(self):
        """--list-violations exits 1 when violations are present."""
        path = str(PROJECT_ROOT / "doc/testing/big.md")
        deps = make_deps(
            list_files=lambda root: [path] if "testing" in root else [],
            count_lines=lambda p: 700,
        )
        assert run(deps, _make_args(list_violations=True)) == 1

    def test_list_violations_exits_0_when_clean(self):
        deps = make_deps(list_files=lambda root: [])
        assert run(deps, _make_args(list_violations=True)) == 0


# ---------------------------------------------------------------------------
# I — --check-depth
# ---------------------------------------------------------------------------

class TestCheckDepth:
    def test_check_depth_detects_level3_path(self):
        """doc/testing/presentation/bloc/events.md (depth 3) is a violation."""
        deep_path = str(PROJECT_ROOT / "doc/testing/presentation/bloc/events.md")

        deps = make_deps(
            list_files=lambda root: [deep_path] if "testing" in root else [],
            count_lines=lambda p: 10,  # No size violation — only depth
        )
        assert run(deps, _make_args(check_depth=True)) == 1

    def test_check_depth_exits_0_for_depth2(self):
        path = str(PROJECT_ROOT / "doc/testing/presentation/widget_testing.md")
        deps = make_deps(
            list_files=lambda root: [path] if "testing" in root else [],
            count_lines=lambda p: 10,
        )
        assert run(deps, _make_args(check_depth=True)) == 0

    def test_check_depth_also_catches_size_violations(self):
        """--check-depth exits 1 if there are size violations too."""
        path = str(PROJECT_ROOT / "doc/testing/big.md")
        deps = make_deps(
            list_files=lambda root: [path] if "testing" in root else [],
            count_lines=lambda p: 700,
        )
        assert run(deps, _make_args(check_depth=True)) == 1


# ---------------------------------------------------------------------------
# J — find_pending_split_task
# ---------------------------------------------------------------------------

class TestFindPendingSplitTask:
    def test_returns_none_when_no_tasks(self):
        deps = make_deps(glob_dirs=lambda p: [])
        assert find_pending_split_task(deps) is None

    def test_returns_none_when_completed_only(self):
        folder = str(
            PROJECT_ROOT
            / "requirements_tasks/process/documentation_rules/guideline_file_organization/tasks"
            / "2026-04-30_impl_split-oversized-doc-files (completed)"
        )
        deps = make_deps(
            glob_dirs=lambda p: [folder],
            read_file=lambda p: "status: completed\n",
        )
        assert find_pending_split_task(deps) is None

    def test_returns_path_when_pending(self):
        folder = str(
            PROJECT_ROOT
            / "requirements_tasks/process/documentation_rules/guideline_file_organization/tasks"
            / "2026-04-30_impl_split-oversized-doc-files"
        )
        goal_path = os.path.join(folder, "goal.md")
        deps = make_deps(
            glob_dirs=lambda p: [folder],
            read_file=lambda p: "status: pending\n",
        )
        result = find_pending_split_task(deps)
        assert result == goal_path
