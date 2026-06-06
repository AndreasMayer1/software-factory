# ruff: noqa: SIM115, RUF100
# SIM115: test fakes use one-line lambdas like `lambda p, c: open(p, "w").write(c)` to wire
# dependency-injected file I/O into the orchestrator under test; a context manager would
# change the lambda shape and the dep contract.
# RUF100: false-positive on file-level noqa for codes ruff cannot introspect into the file body.
"""
test_orchestrate_yaml_migration.py -- additional regression tests pinning the
observable behaviour of the four hand-rolled YAML-frontmatter parser sites in
scripts/automation/orchestrate.py that TASK-PROC-051-04 migrates to the central
scripts/util/yaml_frontmatter helper.

These tests are layered on top of the pre-existing pins in test_orchestrate.py
(TestReadYamlFrontmatter, TestUpdateGoalSessionFields, TestRewriteQuestionSessionId,
TestPromoteTaskToOpusForContextLimit). Together both files cover:

  - read_yaml_frontmatter  (parser, site at line ~350)
  - update_goal_session_fields  (read-modify-write, site at line ~694)
  - _rewrite_question_session_id  (read-modify-write, site at line ~1133)
  - _promote_task_to_opus_for_context_limit  (read-modify-write, site at line ~1225)

Every test in this file is required to pass BOTH against the pre-migration
code AND against the post-migration code (helper-based). Where the legacy
parser was provably buggy in a way that the helper repairs, the divergence is
documented in 2026-05-17_03_protocol_phase1_yaml_migration.md.
"""

import os
import sys
from typing import Any

# Add scripts/automation to sys.path so we can import orchestrate without installation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Reuse the make_deps fixture from the main test module so we get the same
# OrchestratorDeps shape with no-op subprocess defaults.
sys.path.insert(0, os.path.dirname(__file__))
from orchestrate import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    PromoteResult,
    _is_opus_recommended,
    _promote_task_to_opus_for_context_limit,
    _rewrite_question_session_id,
    read_yaml_frontmatter,
    update_goal_session_fields,
)
from test_orchestrate import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    _fake_completed,
    make_deps,
)

# ---------------------------------------------------------------------------
# Site 1 — read_yaml_frontmatter (line ~350)
# ---------------------------------------------------------------------------


class TestReadYamlFrontmatterMigration:
    """Pin shape contracts read_yaml_frontmatter must preserve through migration."""

    def test_parses_inline_list(self, tmp_path: Any) -> None:
        """Inline list `[a, b, c]` must parse to a real list."""
        path = tmp_path / "g.md"
        path.write_text("---\nafter: [TASK-A, TASK-B]\n---\nBody")
        result = read_yaml_frontmatter(str(path))
        assert isinstance(result.get("after"), list)
        assert list(result["after"]) == ["TASK-A", "TASK-B"]

    def test_parses_block_list(self, tmp_path: Any) -> None:
        """Block list `- item` lines must parse to a real list under the parent key."""
        path = tmp_path / "g.md"
        path.write_text(
            "---\n"
            "after:\n"
            "  - TASK-A\n"
            "  - TASK-B\n"
            "---\n"
            "Body"
        )
        result = read_yaml_frontmatter(str(path))
        assert isinstance(result.get("after"), list)
        assert list(result["after"]) == ["TASK-A", "TASK-B"]

    def test_empty_list_yields_empty_list(self, tmp_path: Any) -> None:
        """`after: []` must yield an empty list, not None."""
        path = tmp_path / "g.md"
        path.write_text("---\nafter: []\n---\nBody")
        result = read_yaml_frontmatter(str(path))
        assert result.get("after") == []

    def test_opus_recommended_boolean_round_trips_via_is_opus_recommended(self, tmp_path: Any) -> None:
        """opus_recommended values with an inline comment must still be readable
        by _is_opus_recommended (the helper that downstream callers rely on)."""
        path = tmp_path / "g.md"
        path.write_text(
            "---\n"
            "task_id: TASK-X\n"
            "opus_recommended: true   # reason: cross-cutting\n"
            "---\n"
            "Body"
        )
        fm = read_yaml_frontmatter(str(path))
        # The exact in-memory type (bool vs str) is intentionally NOT pinned —
        # the contract is that _is_opus_recommended interprets it as True.
        assert _is_opus_recommended(fm) is True

    def test_opus_recommended_false_is_false(self, tmp_path: Any) -> None:
        path = tmp_path / "g.md"
        path.write_text(
            "---\n"
            "opus_recommended: false\n"
            "---\n"
            "Body"
        )
        fm = read_yaml_frontmatter(str(path))
        assert _is_opus_recommended(fm) is False

    def test_quoted_scalar_strips_quotes(self, tmp_path: Any) -> None:
        """Double-quoted scalar should arrive as the bare string, not with quotes."""
        path = tmp_path / "g.md"
        path.write_text('---\ntask_id: "TASK-Q"\n---\nBody')
        result = read_yaml_frontmatter(str(path))
        assert result.get("task_id") == "TASK-Q"


# ---------------------------------------------------------------------------
# Site 2 — update_goal_session_fields (line ~694)
# ---------------------------------------------------------------------------


class TestUpdateGoalSessionFieldsMigration:
    """Pin additional contracts beyond TestUpdateGoalSessionFields in test_orchestrate."""

    def test_preserves_body_after_frontmatter(self, tmp_path: Any) -> None:
        """The body after the closing --- must be preserved verbatim."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\n"
            "status: in_progress\n"
            "task_id: TASK-X\n"
            "---\n"
            "# Header\n\nSome multi-line body content.\nLine two.\n"
        )

        written: dict[Any, Any] = {}

        def fake_write(p, c):
            written[p] = c

        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=fake_write,
        )
        update_goal_session_fields(str(goal_path), "uuid-1", "web", deps)
        content = next(iter(written.values()))
        assert "# Header" in content
        assert "Some multi-line body content." in content
        assert "Line two." in content

    def test_preserves_other_frontmatter_fields(self, tmp_path: Any) -> None:
        """Fields that are not session_id/session_account must survive untouched."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\n"
            "task_id: TASK-X\n"
            "status: in_progress\n"
            "after: [TASK-A, TASK-B]\n"
            "opus_recommended: true   # reason: cross-cutting\n"
            "---\n"
            "Body"
        )

        written: dict[Any, Any] = {}

        def fake_write(p, c):
            written[p] = c

        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=fake_write,
        )
        update_goal_session_fields(str(goal_path), "uuid-1", "web", deps)
        content = next(iter(written.values()))
        assert "task_id: TASK-X" in content
        assert "status: in_progress" in content
        # The after: list and the opus_recommended line must still be readable
        # afterwards (exact formatting is not pinned, just round-trip-ability).
        # Round-trip back through read_yaml_frontmatter to verify.
        roundtrip_path = tmp_path / "after.md"
        roundtrip_path.write_text(content)
        fm = read_yaml_frontmatter(str(roundtrip_path))
        assert fm.get("task_id") == "TASK-X"
        assert fm.get("status") == "in_progress"
        assert list(fm.get("after") or []) == ["TASK-A", "TASK-B"]
        assert _is_opus_recommended(fm) is True

    def test_no_frontmatter_does_not_crash(self, tmp_path: Any, capsys: Any) -> None:
        """A goal.md without frontmatter must not raise; behaviour is best-effort.

        The legacy parser would silently skip the inject (no closing ---
        found, in_frontmatter stays False) and write the file verbatim.
        We pin "does not raise" only — the exact emitted text is not pinned.
        """
        goal_path = tmp_path / "goal.md"
        goal_path.write_text("Plain markdown, no frontmatter.\n")

        written: dict[Any, Any] = {}

        def fake_write(p, c):
            written[p] = c

        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=fake_write,
        )
        # Should not raise.
        update_goal_session_fields(str(goal_path), "uuid-1", "web", deps)


# ---------------------------------------------------------------------------
# Site 3 — _rewrite_question_session_id (line ~1133)
# ---------------------------------------------------------------------------


class TestRewriteQuestionSessionIdMigration:
    """Pin additional contracts beyond TestRewriteQuestionSessionId in test_orchestrate."""

    def test_preserves_body(self, tmp_path: Any) -> None:
        """The body after the closing --- must be preserved verbatim."""
        qpath = tmp_path / "question.md"
        qpath.write_text(
            "---\n"
            "task_id: TASK-X\n"
            "session_id: old-uuid\n"
            "---\n"
            "Question body line 1.\n\nQuestion body line 2.\n"
        )
        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
        )

        _rewrite_question_session_id(str(qpath), "NEW_SESSION_REQUIRED", deps)

        text = qpath.read_text()
        assert "Question body line 1." in text
        assert "Question body line 2." in text

    def test_preserves_unrelated_frontmatter_keys(self, tmp_path: Any) -> None:
        """Fields other than session_id must survive untouched."""
        qpath = tmp_path / "question.md"
        qpath.write_text(
            "---\n"
            "task_id: TASK-X\n"
            "session_id: old-uuid\n"
            "account: web\n"
            "ts: 2026-05-17T12:34:56\n"
            "---\n"
            "body\n"
        )
        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
        )

        _rewrite_question_session_id(str(qpath), "NEW", deps)

        text = qpath.read_text()
        assert "session_id: NEW" in text
        assert "old-uuid" not in text
        assert "task_id: TASK-X" in text
        assert "account: web" in text
        # ts may be a `datetime`-formatted string post-migration; the legacy
        # parser kept it as plain text. We pin only that the key survives.
        assert "ts:" in text

    def test_no_frontmatter_is_non_fatal(self, tmp_path: Any, capsys: Any) -> None:
        """A file with no frontmatter prints a warning and does not crash."""
        qpath = tmp_path / "question.md"
        qpath.write_text("Plain body, no frontmatter.\n")
        original = qpath.read_text()
        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
        )

        _rewrite_question_session_id(str(qpath), "NEW", deps)

        # File should be unchanged because session_id was not found.
        assert qpath.read_text() == original

    def test_read_error_is_non_fatal(self, tmp_path: Any, capsys: Any) -> None:
        """A read failure prints a WARNING and does not raise."""
        def raise_os(p):
            raise OSError("disk error")

        deps = make_deps(read_file=raise_os)
        _rewrite_question_session_id("/nonexistent/question.md", "NEW", deps)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out


# ---------------------------------------------------------------------------
# Site 4 — _promote_task_to_opus_for_context_limit (line ~1225)
# ---------------------------------------------------------------------------


class TestPromoteTaskToOpusMigration:
    """Pin additional contracts beyond TestPromoteTaskToOpusForContextLimit."""

    def _setup_goal(self, tmp_path: Any, frontmatter: str) -> str:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(frontmatter)
        return str(goal_path)

    def _make_deps(self, goal_path: str, writes: dict[Any, Any]) -> Any:
        def fake_subprocess(cmd, *args, **kwargs):
            if "grep" in cmd[0]:
                return _fake_completed(stdout=goal_path + "\n")
            return _fake_completed()

        def fake_write(p, c):
            writes[p] = c
            open(p, "w").write(c)

        return make_deps(
            run_subprocess=fake_subprocess,
            read_file=lambda p: open(p).read(),
            write_file=fake_write,
        )

    def test_preserves_body_after_promotion(self, tmp_path: Any) -> None:
        """The markdown body after the frontmatter must survive verbatim."""
        goal_path = self._setup_goal(
            tmp_path,
            "---\n"
            "task_id: TASK-CTX\n"
            "status: in_progress\n"
            "opus_recommended: false\n"
            "session_id: doomed-uuid\n"
            "---\n"
            "# Goal\n\nBody line one.\nBody line two.\n",
        )
        writes: dict[Any, Any] = {}
        deps = self._make_deps(goal_path, writes)

        result = _promote_task_to_opus_for_context_limit("TASK-CTX", deps)
        assert result == PromoteResult.PROMOTED

        text = open(goal_path).read()
        assert "# Goal" in text
        assert "Body line one." in text
        assert "Body line two." in text

    def test_preserves_unrelated_frontmatter_fields(self, tmp_path: Any) -> None:
        """Fields other than opus_recommended / session_id / status survive."""
        goal_path = self._setup_goal(
            tmp_path,
            "---\n"
            "task_id: TASK-CTX\n"
            "status: in_progress\n"
            "opus_recommended: false\n"
            "session_id: doomed-uuid\n"
            "after: [TASK-A]\n"
            "urgency: 2\n"
            "impact: 4\n"
            "---\n"
            "body\n",
        )
        writes: dict[Any, Any] = {}
        deps = self._make_deps(goal_path, writes)

        result = _promote_task_to_opus_for_context_limit("TASK-CTX", deps)
        assert result == PromoteResult.PROMOTED

        text = open(goal_path).read()
        # Pin observable outcomes: status flipped, session_id cleared, opus flipped.
        assert "opus_recommended: true" in text
        assert "promoted after context_limit_no_entitlement" in text
        assert "status: pending" in text
        assert 'session_id: ""' in text
        # Unrelated keys survive.
        assert "task_id: TASK-CTX" in text
        assert "urgency: 2" in text
        assert "impact: 4" in text

        # And the after: list must round-trip through read_yaml_frontmatter.
        fm = read_yaml_frontmatter(goal_path)
        assert list(fm.get("after") or []) == ["TASK-A"]

    def test_write_failure_returns_unreadable(self, tmp_path: Any, capsys: Any) -> Any:
        """If the post-promotion write raises OSError, result is UNREADABLE."""
        goal_path = self._setup_goal(
            tmp_path,
            "---\n"
            "task_id: TASK-CTX\n"
            "status: in_progress\n"
            "opus_recommended: false\n"
            "session_id: doomed\n"
            "---\n",
        )

        def fake_subprocess(cmd, *args, **kwargs):
            if "grep" in cmd[0]:
                return _fake_completed(stdout=goal_path + "\n")
            return _fake_completed()

        def fake_write(p, c):
            raise OSError("disk full")

        deps = make_deps(
            run_subprocess=fake_subprocess,
            read_file=lambda p: open(p).read(),
            write_file=fake_write,
        )

        result = _promote_task_to_opus_for_context_limit("TASK-CTX", deps)
        assert result == PromoteResult.UNREADABLE
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
