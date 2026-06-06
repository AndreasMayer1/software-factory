"""
test_update_doc_references.py — Tests for scripts/update_doc_references.py
"""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "artifacts"))

from update_doc_references import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    Deps,
    find_references,
    replace_references,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SEARCH_PATH = "doc/testing/presentation_testing.md"
_SEARCH_PATH_ABS = "/workspaces/private_mood_tracker/flutter_app/doc/testing/presentation_testing.md"


def make_deps(**overrides: Any) -> Deps:
    defaults = {
        "glob_files": lambda p: [],
        "read_file": lambda p: "",
        "write_file": lambda p, c: None,
        "file_exists": lambda p: True,
    }
    defaults.update(overrides)
    return Deps(**defaults)


# ---------------------------------------------------------------------------
# find_references tests
# ---------------------------------------------------------------------------

class TestFindReturnMatchesInClaudeMd:
    def test_find_returns_matches_in_claude_md(self) -> None:
        content = (
            "Some text before\n"
            f"See `{_SEARCH_PATH}` for details\n"
            "Some text after\n"
        )

        # CLAUDE.md is found via file_exists + a fixed path; we simulate it
        # by injecting a file_exists that confirms CLAUDE.md and a read_file
        # that returns our content for it.

        deps = make_deps(
            glob_files=lambda p: [],
            read_file=lambda p: content if "CLAUDE.md" in p else "",
            file_exists=lambda p: "CLAUDE.md" in p,
        )

        results = find_references(deps, _SEARCH_PATH)
        assert len(results) == 1
        file_path, line_no, ctx = results[0]
        assert "CLAUDE.md" in file_path
        assert line_no == 2
        assert _SEARCH_PATH in ctx


class TestFindReturnMatchesInSkills:
    def test_find_returns_matches_in_skills(self) -> None:
        skill_path = "/fake/.claude/skills/some-skill/skill.md"
        content = f"Run `{_SEARCH_PATH}` for testing\n"

        deps = make_deps(
            glob_files=lambda p: [skill_path] if "skills" in p else [],
            read_file=lambda p: content if p == skill_path else "",
            file_exists=lambda p: False,
        )

        results = find_references(deps, _SEARCH_PATH)
        assert len(results) == 1
        file_path, line_no, ctx = results[0]
        assert file_path == skill_path
        assert line_no == 1
        assert _SEARCH_PATH in ctx


class TestFindExcludesCompletedFolders:
    def test_find_excludes_completed_folders(self) -> None:
        completed_path = (
            "/workspaces/private_mood_tracker/flutter_app/requirements_tasks/"
            "functional/some/tasks/2025-01-01_task (completed)/goal.md"
        )
        content = f"See {_SEARCH_PATH} here\n"

        deps = make_deps(
            glob_files=lambda p: [completed_path] if "requirements_tasks" in p else [],
            read_file=lambda p: content,
            file_exists=lambda p: False,
        )

        results = find_references(deps, _SEARCH_PATH)
        assert results == []


class TestFindExcludesSupersededFolders:
    def test_find_excludes_superseded_folders(self) -> None:
        superseded_path = (
            "/workspaces/private_mood_tracker/flutter_app/requirements_tasks/"
            "process/some/tasks/2025-01-01_task (superseded)/protocol.md"
        )
        content = f"Reference to {_SEARCH_PATH} here\n"

        deps = make_deps(
            glob_files=lambda p: [superseded_path] if "requirements_tasks" in p else [],
            read_file=lambda p: content,
            file_exists=lambda p: False,
        )

        results = find_references(deps, _SEARCH_PATH)
        assert results == []


class TestFindExits0WhenNoReferences:
    def test_find_exits_0_when_no_references(self) -> None:
        deps = make_deps(
            glob_files=lambda p: [],
            read_file=lambda p: "no references here\n",
            file_exists=lambda p: False,
        )

        results = find_references(deps, _SEARCH_PATH)
        assert results == []
        # exit code driven by caller: len(results) == 0 → exit 0


class TestFindExits1WhenReferencesFound:
    def test_find_exits_1_when_references_found(self) -> None:
        skill_path = "/fake/.claude/skills/doc-split/skill.md"
        content = f"Read {_SEARCH_PATH} first\n"

        deps = make_deps(
            glob_files=lambda p: [skill_path] if "skills" in p else [],
            read_file=lambda p: content,
            file_exists=lambda p: False,
        )

        results = find_references(deps, _SEARCH_PATH)
        # exit code driven by caller: len(results) > 0 → exit 1
        assert len(results) > 0


# ---------------------------------------------------------------------------
# replace_references tests
# ---------------------------------------------------------------------------

class TestReplaceRewritesFile:
    def test_replace_rewrites_file(self) -> None:
        skill_path = "/fake/.claude/skills/code-test/skill.md"
        original = f"See {_SEARCH_PATH} for details\n"
        new_path = "doc/testing/widget_testing.md"

        written: dict[Any, Any] = {}

        deps = make_deps(
            glob_files=lambda p: [skill_path] if "skills" in p else [],
            read_file=lambda p: original if p == skill_path else "",
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: False,
        )

        modified = replace_references(deps, [(_SEARCH_PATH, new_path)])
        assert skill_path in modified
        assert written[skill_path] == f"See {new_path} for details\n"


class TestReplaceMultiplePairs:
    def test_replace_multiple_pairs(self) -> None:
        skill_path = "/fake/.claude/skills/code-test/skill.md"
        original = (
            "doc/old/file_a.md and doc/old/file_b.md\n"
        )

        written: dict[Any, Any] = {}

        deps = make_deps(
            glob_files=lambda p: [skill_path] if "skills" in p else [],
            read_file=lambda p: original if p == skill_path else "",
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: False,
        )

        modified = replace_references(
            deps,
            [("doc/old/file_a.md", "doc/new/file_a.md"),
             ("doc/old/file_b.md", "doc/new/file_b.md")],
        )
        assert skill_path in modified
        assert written[skill_path] == "doc/new/file_a.md and doc/new/file_b.md\n"


class TestReplaceDoesNotModifyUnrelatedFiles:
    def test_replace_does_not_modify_unrelated_files(self) -> None:
        skill_path = "/fake/.claude/skills/code-test/skill.md"
        unrelated_content = "Nothing relevant here\n"

        written: dict[Any, Any] = {}

        deps = make_deps(
            glob_files=lambda p: [skill_path] if "skills" in p else [],
            read_file=lambda p: unrelated_content,
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: False,
        )

        modified = replace_references(deps, [(_SEARCH_PATH, "doc/new/path.md")])
        assert modified == []
        assert written == {}


class TestReplaceExcludesCompletedFolders:
    def test_replace_excludes_completed_folders(self) -> None:
        completed_path = (
            "/workspaces/private_mood_tracker/flutter_app/requirements_tasks/"
            "functional/some/tasks/2025-01-01_task (completed)/goal.md"
        )
        content = f"See {_SEARCH_PATH} for details\n"

        written: dict[Any, Any] = {}

        deps = make_deps(
            glob_files=lambda p: [completed_path] if "requirements_tasks" in p else [],
            read_file=lambda p: content,
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: False,
        )

        modified = replace_references(deps, [(_SEARCH_PATH, "doc/new/path.md")])
        assert modified == []
        assert written == {}


class TestFindDoesNotMatchFileItself:
    def test_find_does_not_match_file_itself(self) -> Any:
        # The searched-for file itself appears in doc/ but must be excluded.
        # We simulate the file being included in doc/** glob results.
        # We use a relative search_path; both the target file and another doc
        # file contain that string — only the other doc should be returned.
        target_file = _SEARCH_PATH_ABS
        other_doc = "/workspaces/private_mood_tracker/flutter_app/doc/testing/README.md"
        # The target file references itself (e.g. in a title line)
        content_with_self_ref = f"# {_SEARCH_PATH}\nThis is the file itself.\n"
        # The README also references the path
        readme_content = f"See `{_SEARCH_PATH}` for widget tests.\n"

        def fake_glob(pattern):
            if "doc" in pattern and "**" in pattern:
                return [target_file, other_doc]
            return []

        def fake_read(path):
            if path == target_file:
                return content_with_self_ref
            if path == other_doc:
                return readme_content
            return ""

        deps = make_deps(
            glob_files=fake_glob,
            read_file=fake_read,
            file_exists=lambda p: False,
        )

        # Search with the relative path — the target_file resolves to the same
        # absolute path, so it must be excluded from results.
        results = find_references(deps, _SEARCH_PATH)

        # The target file itself must not appear in results
        result_files = [r[0] for r in results]
        assert target_file not in result_files

        # But the README that references it should appear
        assert other_doc in result_files


# ---------------------------------------------------------------------------
# Relative-path reference tests
# ---------------------------------------------------------------------------

# Target: doc/testing/presentation_testing.md
# A file in doc/testing/coding/ referencing ../presentation_testing.md
# resolves to the same file.

_TARGET_PATH = "doc/testing/presentation_testing.md"
_TARGET_ABS = "/workspaces/private_mood_tracker/flutter_app/doc/testing/presentation_testing.md"


class TestFindDetectsRelativeParentPathReference:
    """--find detects a ../tokens/old.md reference from a sibling folder."""

    def test_find_detects_dotdot_relative_reference(self) -> None:
        # File lives at doc/testing/coding/design_system.md
        referring_file = (
            "/workspaces/private_mood_tracker/flutter_app/"
            "doc/testing/coding/design_system.md"
        )
        # Line contains a relative reference that resolves to the target
        content = "See [presentation testing](../presentation_testing.md) for details\n"

        deps = make_deps(
            glob_files=lambda p: [referring_file] if "doc" in p else [],
            read_file=lambda p: content if p == referring_file else "",
            file_exists=lambda p: False,
        )

        results = find_references(deps, _TARGET_PATH)
        assert len(results) == 1
        file_path, line_no, ctx = results[0]
        assert file_path == referring_file
        assert line_no == 1
        assert "../presentation_testing.md" in ctx


class TestFindDetectsDotSlashRelativeReference:
    """--find detects a ./old.md reference from a file in the same folder."""

    def test_find_detects_dot_slash_relative_reference(self) -> None:
        # File lives in the same folder as the target
        referring_file = (
            "/workspaces/private_mood_tracker/flutter_app/"
            "doc/testing/overview.md"
        )
        # Line contains ./presentation_testing.md
        content = "Also read [./presentation_testing.md] for full coverage.\n"

        deps = make_deps(
            glob_files=lambda p: [referring_file] if "doc" in p else [],
            read_file=lambda p: content if p == referring_file else "",
            file_exists=lambda p: False,
        )

        results = find_references(deps, _TARGET_PATH)
        assert len(results) == 1
        file_path, line_no, ctx = results[0]
        assert file_path == referring_file
        assert line_no == 1
        assert "./presentation_testing.md" in ctx


class TestReplaceRewritesRelativeReference:
    """--replace rewrites a relative reference to the correct new relative path."""

    def test_replace_rewrites_dotdot_relative_reference(self) -> None:
        # File lives at doc/testing/coding/design_system.md
        referring_file = (
            "/workspaces/private_mood_tracker/flutter_app/"
            "doc/testing/coding/design_system.md"
        )
        original = (
            "See [presentation testing](../presentation_testing.md) for details\n"
        )

        old_path = "doc/testing/presentation_testing.md"
        # Move the file to doc/presentation/presentation_testing.md
        new_path = "doc/presentation/presentation_testing.md"

        written: dict[Any, Any] = {}

        deps = make_deps(
            glob_files=lambda p: [referring_file] if "doc" in p else [],
            read_file=lambda p: original if p == referring_file else "",
            write_file=lambda p, c: written.update({p: c}),
            file_exists=lambda p: False,
        )

        modified = replace_references(deps, [(old_path, new_path)])
        assert referring_file in modified

        rewritten = written[referring_file]
        # The relative path from doc/testing/coding/ to doc/presentation/ is
        # ../../presentation/presentation_testing.md
        assert "../../presentation/presentation_testing.md" in rewritten
        # The old relative reference must be gone
        assert "../presentation_testing.md" not in rewritten
