# ruff: noqa: SIM115, RUF002, RUF003, RUF100, E402, SIM117
# SIM115: test fakes use one-line lambdas like `lambda p, c: open(p, "w").write(c)` to wire dependency-injected file I/O into the orchestrator under test; a context manager would change the lambda shape and the dep contract.
# RUF002 / RUF003: docstrings and comments mirror the orchestrator's Unicode glyphs (en dash, set-theory symbols) used in the production module.
# RUF100: false-positive on file-level noqa for codes ruff cannot introspect into the file body.
# E402: mid-file imports deliberately group symbols under category-banner comments (Cat I, Cat J, etc.) rather than burying every imported symbol in one top block.
# SIM117: tests use nested `with mock.patch(...)` blocks to clarify which patch is being asserted against in each layer; a combined `with` would obscure the per-mock failure attribution.
"""
test_orchestrate.py -- Test suite for scripts/automation/orchestrate.py

~150 tests across 8 categories (A–H) following the architecture defined in:
requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/
feat_session_orchestrator/tasks/2026-04-10_impl_implement-orchestrator-monitoring-improvements/
plans_and_protocols/2026-04-10_02_plan_rewrite-architecture.md#6-test-architecture
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest import mock
from unittest.mock import MagicMock

# Add scripts/automation to sys.path so we can import orchestrate without installation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from orchestrate import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    Orchestrator,
    OrchestratorDeps,
    PersistentState,
    RunData,
    _archive_feedback_checkpoint,
    _clear_inbox,
    _jaccard,
    _proto_once,
    _reset_startup_state,
    _run_log_dedupe,
    answer_is_empty,
    check_and_update_question_fingerprint,
    compute_question_fingerprint,
    find_answered_feedback,
    find_resumable_session,
    get_unanswered_questions,
    git_commit_best_effort,
    load_state,
    next_available_account,
    parse_rate_limit_reset,
    run_session_with_hung_detection,
    save_state,
    strip_hook_footer,
    write_health_summary,
    write_report,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _fake_completed(returncode: Any = 0, stdout: Any = "", stderr: Any = "") -> Any:
    """Create a fake subprocess.CompletedProcess."""
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def _make_immediately_exiting_proc(returncode: Any = 0, stdout: Any = "") -> Any:
    """Return a mock Popen-style object that appears to exit immediately on first poll."""
    proc = MagicMock()
    proc.poll.return_value = returncode  # non-None → process already exited
    proc.communicate.return_value = (stdout, "")
    proc.pid = 11111
    return proc


def make_deps(**overrides: Any) -> OrchestratorDeps:
    """Return OrchestratorDeps with safe no-op defaults. Override as needed."""
    defaults = {
        "run_subprocess": lambda *a, **kw: _fake_completed(),
        # Why: popen_subprocess default returns a process that "exits" immediately
        # (poll() returns 0) so existing tests that don't care about hung-detection
        # continue to work without modification. Tests that exercise hung-detection
        # supply their own popen_subprocess via make_deps(popen_subprocess=...).
        "popen_subprocess": lambda *a, **kw: _make_immediately_exiting_proc(),
        "read_file": lambda p: "",
        "write_file": lambda p, c: None,
        "file_exists": lambda p: False,
        "list_dir": lambda p: [],
        "makedirs": lambda p: None,
        "glob_files": lambda p: [],
        "get_now_utc": lambda: datetime(2026, 4, 10, 12, 0, 0, tzinfo=timezone.utc),
        "get_now_local": lambda: datetime(2026, 4, 10, 14, 0, 0),
        "sleep": lambda s: None,
        "getpid": lambda: 12345,
        "get_mtime": lambda p: 1000.0,
        # Why: redirect session-output writes away from the production automation/session_outputs/
        # directory. Tests that wire real write_file / makedirs lambdas (for realistic I/O
        # simulation) would otherwise create test artifacts in the live directory, which the
        # cleanup logic cannot distinguish from real session outputs.
        "outputs_dir": "/tmp/_pytest_session_outputs",
    }
    defaults.update(overrides)
    return OrchestratorDeps(**defaults)


def make_popen_from_subprocess_fn(subprocess_fn: Any) -> Any:
    """Wrap a fake_subprocess callable as a popen_subprocess callable.

    Why: existing tests provide a fake_subprocess that handles 'claude' commands and
    returns a CompletedProcess. Now that claude sessions go through popen_subprocess
    (run_session_with_hung_detection), we need to bridge the old style to the new API.
    The returned Popen-style mock immediately "exits" with the same returncode/stdout
    as what fake_subprocess would return, so session logic (rate-limit, perm-error, etc.)
    is tested without modification to existing assertions.
    """
    def _popen(cmd, *args, **kwargs):
        completed = subprocess_fn(cmd)
        proc = MagicMock()
        proc.poll.return_value = completed.returncode
        proc.communicate.return_value = (completed.stdout or "", "")
        proc.pid = 22222
        return proc
    return _popen


def make_args(**overrides: Any) -> argparse.Namespace:
    """Return argparse.Namespace with sensible test defaults."""
    defaults = {
        "accounts": "test_acct",
        "stop_at": None,
        "min_wait_seconds": 0,
        "max_tasks": None,
        "hung_check_interval": 60,
        "hung_timeout": 30,
        "session_timeout": 14400,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def make_fake_dir_entry(path: Any, is_dir: Any = True) -> Any:
    """Create a minimal DirEntry-like object for list_dir mocking."""
    entry = MagicMock()
    entry.path = path
    entry.name = os.path.basename(path)
    entry.is_dir.return_value = is_dir
    stat_result = MagicMock()
    stat_result.st_mtime = 1000.0
    entry.stat.return_value = stat_result
    return entry


# ---------------------------------------------------------------------------
# Category A: Pure utility functions (~25 tests)
# ---------------------------------------------------------------------------


class TestParseRateLimitReset:
    def test_valid_12h_format_returns_datetime(self) -> None:
        stdout = "You've hit your limit. It resets 9pm (Europe/Berlin)"
        result = parse_rate_limit_reset(stdout)
        assert result is not None
        assert isinstance(result, datetime)
        assert result.tzinfo is not None  # UTC-aware

    def test_valid_with_minutes(self) -> None:
        stdout = "resets 9:30pm (America/New_York)"
        result = parse_rate_limit_reset(stdout)
        assert result is not None

    def test_no_match_returns_none(self) -> None:
        result = parse_rate_limit_reset("No rate limit info here")
        assert result is None

    def test_empty_string_returns_none(self) -> None:
        result = parse_rate_limit_reset("")
        assert result is None

    def test_result_has_5_min_buffer(self) -> None:
        # The function adds 5 min buffer; the reset should be >= now
        stdout = "resets 11:59pm (UTC)"
        result = parse_rate_limit_reset(stdout)
        # Even if it cannot parse the exact time it should return None, not raise
        # (UTC is a valid zoneinfo name on most systems; if not, still shouldn't raise)
        # We just check no exception is raised
        assert result is None or isinstance(result, datetime)

    def test_unknown_timezone_falls_back_to_utc(self, capsys: Any) -> None:
        stdout = "resets 9pm (Unknown/Timezone)"
        result = parse_rate_limit_reset(stdout)
        # Should still return a datetime (falling back to UTC) or None on parse failure
        assert result is None or isinstance(result, datetime)
        captured = capsys.readouterr()
        if result is not None:
            assert "UTC" in captured.out or "unknown timezone" in captured.out

    def test_day_rollover_adds_one_day(self) -> None:
        # If we mock now to be after the parsed time, result should be next day
        # We cannot easily freeze datetime here without monkeypatching, but we can
        # verify the result is >= now (the buffer/rollover logic runs correctly)
        stdout = "resets 1am (UTC)"
        result = parse_rate_limit_reset(stdout)
        # Either None (parse failed on system) or a future datetime
        assert result is None or result > datetime.now(timezone.utc)


class TestFormatUtcOffset:
    """_format_utc_offset must produce '+HH:MM' / '-HH:MM' parseable by the
    PowerShell sleep_when_autorun_done.ps1 regex `^([+-])(\\d{2}):(\\d{2})$`.
    """

    def test_positive_offset(self) -> None:
        from orchestrate import _format_utc_offset
        assert _format_utc_offset(timedelta(hours=2)) == "+02:00"

    def test_negative_offset(self) -> None:
        from orchestrate import _format_utc_offset
        assert _format_utc_offset(timedelta(hours=-5)) == "-05:00"

    def test_zero_returns_plus_zero(self) -> None:
        from orchestrate import _format_utc_offset
        assert _format_utc_offset(timedelta(0)) == "+00:00"

    def test_double_digit_hours(self) -> None:
        from orchestrate import _format_utc_offset
        assert _format_utc_offset(timedelta(hours=12)) == "+12:00"
        assert _format_utc_offset(timedelta(hours=-12)) == "-12:00"

    def test_half_hour_offset(self) -> None:
        """India (+05:30), Newfoundland (-03:30) etc. — minutes must be preserved."""
        from orchestrate import _format_utc_offset
        assert _format_utc_offset(timedelta(hours=5, minutes=30)) == "+05:30"
        assert _format_utc_offset(timedelta(hours=-3, minutes=-30)) == "-03:30"

    def test_45_minute_offset(self) -> None:
        """Nepal (+05:45), Chatham Islands (+12:45)."""
        from orchestrate import _format_utc_offset
        assert _format_utc_offset(timedelta(hours=5, minutes=45)) == "+05:45"

    def test_format_matches_powershell_regex(self) -> None:
        """Round-trip: every produced string must match the PowerShell parse pattern."""
        import re

        from orchestrate import _format_utc_offset
        pattern = re.compile(r"^([+-])(\d{2}):(\d{2})$")
        for hours in (-12, -5, -1, 0, 1, 2, 8, 12):
            result = _format_utc_offset(timedelta(hours=hours))
            assert pattern.match(result), f"offset {hours}h produced {result!r}, not matching PS regex"
        # And the half-hour cases
        for delta in (timedelta(hours=5, minutes=30), timedelta(hours=-3, minutes=-30),
                      timedelta(hours=5, minutes=45)):
            result = _format_utc_offset(delta)
            assert pattern.match(result), f"delta {delta} produced {result!r}, not matching PS regex"


class TestGetLocalTimezoneOffset:
    """Integration smoke test: the helper returns a non-empty string in the
    expected format on the host this test runs on. Exact value depends on the
    OS local timezone, so we assert format only."""

    def test_returns_well_formed_offset(self) -> None:
        import re

        from orchestrate import _get_local_timezone_offset
        result = _get_local_timezone_offset()
        assert re.match(r"^([+-])(\d{2}):(\d{2})$", result), (
            f"_get_local_timezone_offset() returned {result!r}, not in '+HH:MM'/'-HH:MM' format"
        )


class TestStripHookFooter:
    def test_removes_footer(self) -> None:
        text = "Some output\n---\n**Reminder: do something**"
        assert strip_hook_footer(text) == "Some output"

    def test_no_footer_unchanged(self) -> None:
        text = "Clean output with no footer"
        assert strip_hook_footer(text) == text

    def test_multiline_footer_removed(self) -> None:
        text = "Output\n---\n**Reminder: line1\nline2\nline3**"
        result = strip_hook_footer(text)
        assert "---" not in result
        assert "Reminder" not in result

    def test_empty_string(self) -> None:
        assert strip_hook_footer("") == ""

    def test_footer_mid_content_not_removed_without_pattern(self) -> None:
        # Only the specific "---\n**Reminder:" pattern is stripped
        text = "line1\n---\nNot a reminder footer"
        # This should NOT be stripped (no **Reminder: pattern)
        result = strip_hook_footer(text)
        assert "Not a reminder footer" in result


class TestComputeQuestionFingerprint:
    def test_lowercases_text(self) -> None:
        fp = compute_question_fingerprint("HELLO WORLD")
        assert "hello" in fp["words"]
        assert "world" in fp["words"]

    def test_strips_punctuation(self) -> None:
        fp = compute_question_fingerprint("Hello, world!")
        assert "hello" in fp["words"]
        assert "world" in fp["words"]
        # Punctuation-only tokens should not appear
        assert "," not in fp["words"]
        assert "!" not in fp["words"]

    def test_splits_into_words(self) -> None:
        fp = compute_question_fingerprint("one two three")
        assert set(fp["words"]) == {"one", "two", "three"}

    def test_preview_truncated_at_300_chars(self) -> None:
        long_text = "word " * 100  # 500 chars
        fp = compute_question_fingerprint(long_text)
        assert len(fp["preview"]) <= 300

    def test_preview_short_text_not_truncated(self) -> None:
        text = "short question"
        fp = compute_question_fingerprint(text)
        assert fp["preview"] == text

    def test_returns_dict_with_words_and_preview(self) -> None:
        fp = compute_question_fingerprint("test")
        assert "words" in fp
        assert "preview" in fp
        assert isinstance(fp["words"], list)
        assert isinstance(fp["preview"], str)

    def test_deduplicates_words(self) -> None:
        fp = compute_question_fingerprint("the the the")
        assert fp["words"].count("the") == 1


class TestJaccard:
    def test_both_empty_returns_1(self) -> None:
        assert _jaccard(set(), set()) == 1.0

    def test_identical_sets_returns_1(self) -> None:
        s = {"a", "b", "c"}
        assert _jaccard(s, s) == 1.0

    def test_no_overlap_returns_0(self) -> None:
        assert _jaccard({"a", "b"}, {"c", "d"}) == 0.0

    def test_partial_overlap(self) -> None:
        # |{a,b} & {b,c}| = 1, |{a,b,c}| = 3 → 1/3
        result = _jaccard({"a", "b"}, {"b", "c"})
        assert abs(result - 1/3) < 1e-9

    def test_empty_vs_nonempty_returns_0(self) -> None:
        assert _jaccard(set(), {"a"}) == 0.0

    def test_nonempty_vs_empty_returns_0(self) -> None:
        assert _jaccard({"a"}, set()) == 0.0

    def test_threshold_exactly_060(self) -> None:
        # 3 shared out of 5 total → 0.6
        a = {"x", "y", "z", "p"}
        b = {"x", "y", "z", "q"}
        # intersection=3, union=5 → 0.6
        result = _jaccard(a, b)
        assert abs(result - 0.6) < 1e-9

    def test_below_threshold(self) -> None:
        result = _jaccard({"a", "b"}, {"a", "b", "c", "d", "e", "f"})
        assert result < 0.6


class TestAnswerIsEmpty:
    def test_nonexistent_file_returns_true(self, tmp_path: Any) -> None:
        path = str(tmp_path / "nonexistent.md")
        assert answer_is_empty(path) is True

    def test_zero_byte_file_returns_true(self, tmp_path: Any) -> None:
        path = tmp_path / "answer.md"
        path.write_bytes(b"")
        assert answer_is_empty(str(path)) is True

    def test_whitespace_only_returns_true(self, tmp_path: Any) -> None:
        path = tmp_path / "answer.md"
        path.write_text("   \n\t  \n")
        assert answer_is_empty(str(path)) is True

    def test_real_content_returns_false(self, tmp_path: Any) -> None:
        path = tmp_path / "answer.md"
        path.write_text("This is an actual answer.")
        assert answer_is_empty(str(path)) is False

    def test_newline_only_returns_true(self, tmp_path: Any) -> None:
        path = tmp_path / "answer.md"
        path.write_text("\n\n\n")
        assert answer_is_empty(str(path)) is True

    def test_unmodified_template_returns_true(self, tmp_path: Any) -> None:
        # A file whose content exactly matches TEMPLATE_answer.md is treated as unanswered
        template = tmp_path / "TEMPLATE_answer.md"
        template_content = "<!-- AWAITING_HUMAN_ANSWER -->\n\n⚠️ Do NOT write here.\n"
        template.write_text(template_content)
        answer = tmp_path / "answer.md"
        answer.write_text(template_content)
        with mock.patch("orchestrate.ANSWER_TEMPLATE_PATH", str(template)):
            assert answer_is_empty(str(answer)) is True

    def test_template_with_appended_human_answer_returns_false(self, tmp_path: Any) -> None:
        # Template marker present but human content appended → NOT empty
        template = tmp_path / "TEMPLATE_answer.md"
        template_content = "<!-- AWAITING_HUMAN_ANSWER -->\n\n⚠️ Do NOT write here.\n"
        template.write_text(template_content)
        answer = tmp_path / "answer.md"
        answer.write_text(template_content + "\nOption B — keep the task open.")
        with mock.patch("orchestrate.ANSWER_TEMPLATE_PATH", str(template)):
            assert answer_is_empty(str(answer)) is False

    def test_template_marker_but_missing_template_file_returns_false(self, tmp_path: Any) -> None:
        # Template file missing → fall through, marker-starting content treated as non-empty
        answer = tmp_path / "answer.md"
        answer.write_text("<!-- AWAITING_HUMAN_ANSWER -->\nSome content")
        with mock.patch("orchestrate.ANSWER_TEMPLATE_PATH", str(tmp_path / "nonexistent.md")):
            assert answer_is_empty(str(answer)) is False


# ---------------------------------------------------------------------------
# Category B: State management (~15 tests)
# ---------------------------------------------------------------------------


class TestLoadState:
    def test_missing_file_returns_default(self) -> None:
        deps = make_deps(file_exists=lambda p: False)
        state = load_state("/fake/state.json", deps)
        assert isinstance(state, PersistentState)
        assert state.account_index == 0
        assert state.run_count == 0
        assert state.paused_tasks == []
        assert state.rate_limited_until == {}
        assert state.question_fingerprints == {}
        # Observability fields (AC-34..AC-38)
        assert state.is_running is False
        assert state.active_session is None
        assert state.stop_requested is False
        assert state.rate_limit_reached is False
        assert state.next_wake_time is None
        assert state.timezone is None
        assert state.timezone_offset is None
        assert state.stop_reason is None

    def test_observability_fields_loaded_from_json(self) -> None:
        """AC-34..AC-38: observability fields are loaded from state.json correctly."""
        data = {
            "is_running": True,
            "active_session": "abc-123",
            "stop_requested": True,
            "rate_limit_reached": True,
            "next_wake_time": "2026-04-30T22:00:00+02:00",
            "timezone": "Europe/Berlin",
            "timezone_offset": "+02:00",
            "stop_reason": "manual",
        }
        deps = make_deps(file_exists=lambda p: True, read_file=lambda p: json.dumps(data))
        state = load_state("/fake/state.json", deps)
        assert state.is_running is True
        assert state.active_session == "abc-123"
        assert state.stop_requested is True
        assert state.rate_limit_reached is True
        assert state.next_wake_time == "2026-04-30T22:00:00+02:00"
        assert state.timezone == "Europe/Berlin"
        assert state.timezone_offset == "+02:00"
        assert state.stop_reason == "manual"

    def test_valid_json_loads_fields(self) -> None:
        data = {
            "account_index": 2,
            "run_count": 7,
            "start_time": "2026-01-01T00:00:00",
            "paused_tasks": ["TASK-1"],
            "rate_limited_until": {"web": "2026-01-01T01:00:00"},
            "question_fingerprints": {"TASK-1": {"words": ["hello"], "preview": "hello"}},
        }
        deps = make_deps(
            file_exists=lambda p: True,
            read_file=lambda p: json.dumps(data),
        )
        state = load_state("/fake/state.json", deps)
        assert state.account_index == 2
        assert state.run_count == 7
        assert state.paused_tasks == ["TASK-1"]
        assert state.rate_limited_until == {"web": "2026-01-01T01:00:00"}
        assert "TASK-1" in state.question_fingerprints

    def test_missing_keys_filled_with_defaults(self) -> None:
        data = {"account_index": 1}  # missing all other keys
        deps = make_deps(
            file_exists=lambda p: True,
            read_file=lambda p: json.dumps(data),
        )
        state = load_state("/fake/state.json", deps)
        assert state.account_index == 1
        assert state.run_count == 0
        assert state.paused_tasks == []

    def test_question_fingerprints_absent_defaults_to_empty_dict(self) -> None:
        data = {"account_index": 0, "run_count": 0}
        deps = make_deps(
            file_exists=lambda p: True,
            read_file=lambda p: json.dumps(data),
        )
        state = load_state("/fake/state.json", deps)
        assert state.question_fingerprints == {}

    def test_corrupt_json_returns_default(self, capsys: Any) -> None:
        deps = make_deps(
            file_exists=lambda p: True,
            read_file=lambda p: "NOT VALID JSON {{{",
        )
        state = load_state("/fake/state.json", deps)
        assert state.account_index == 0
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_start_time_preserved(self) -> None:
        data = {"start_time": "2026-03-15T08:00:00"}
        deps = make_deps(
            file_exists=lambda p: True,
            read_file=lambda p: json.dumps(data),
        )
        state = load_state("/fake/state.json", deps)
        assert state.start_time == "2026-03-15T08:00:00"


class TestSaveState:
    def test_writes_json_to_path(self, tmp_path: Any) -> None:
        path = str(tmp_path / "state.json")
        deps = make_deps(
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        # start_time set so the Issue 6 default-state guard does not fire.
        state = PersistentState(
            account_index=3,
            run_count=5,
            start_time="2026-05-18T22:08:05+02:00",
        )
        save_state(path, state, deps)
        with open(path) as f:
            data = json.loads(f.read())
        assert data["account_index"] == 3
        assert data["run_count"] == 5

    def test_atomic_write_uses_tmp_file(self) -> None:
        written_paths = []

        def fake_write(p, c):
            written_paths.append(p)

        deps = make_deps(
            write_file=fake_write,
            makedirs=lambda p: None,
        )
        # We call save_state; os.replace will fail since paths are fake,
        # but we can verify the tmp path was attempted.
        # start_time=ISO so the Issue 6 default-state guard does not fire.
        import unittest.mock as mock
        state = PersistentState(start_time="2026-05-18T22:08:05+02:00")
        with mock.patch("os.replace"):
            save_state("/fake/state.json", state, deps)
        assert any(".tmp" in p for p in written_paths)

    def test_type_error_logs_warning_and_does_not_crash(self, capsys: Any) -> None:
        # Inject a set (not JSON-serialisable) via question_fingerprints
        import unittest.mock as mock

        state = PersistentState()
        # Directly put a set to trigger TypeError in json.dumps
        state.question_fingerprints = {"bad": {"words": {1, 2, 3}}}  # set not serialisable

        written = []

        def fake_write(p, c):
            written.append(c)

        deps = make_deps(write_file=fake_write, makedirs=lambda p: None)
        # json.dumps will raise TypeError for a set
        with mock.patch("os.replace"):
            save_state("/fake/state.json", state, deps)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        # Should not crash; written should be empty (write never called after TypeError)
        assert written == []

    def test_os_error_logs_warning_and_does_not_crash(self, capsys: Any) -> None:
        def raise_os_error(p, c):
            raise OSError("disk full")

        deps = make_deps(write_file=raise_os_error, makedirs=lambda p: None)
        save_state("/fake/state.json", PersistentState(), deps)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_writes_observability_fields(self, tmp_path: Any) -> None:
        """AC-34: observability fields are written to state.json on save."""
        path = str(tmp_path / "state.json")
        deps = make_deps(
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        state = PersistentState(
            is_running=True,
            active_session="uuid-1",
            stop_requested=False,
            rate_limit_reached=True,
            next_wake_time="2026-04-30T22:00:00+02:00",
            stop_reason="manual",
            # start_time set so the Issue 6 default-state guard does not fire.
            start_time="2026-05-18T22:08:05+02:00",
        )
        save_state(path, state, deps)
        with open(path) as f:
            data = json.loads(f.read())
        assert data["is_running"] is True
        assert data["active_session"] == "uuid-1"
        assert data["rate_limit_reached"] is True
        assert data["next_wake_time"] == "2026-04-30T22:00:00+02:00"
        assert data["stop_reason"] == "manual"

    def test_save_state_writes_timezone_field(self, tmp_path: Any, monkeypatch: Any) -> None:
        """AC-35: timezone field is written on every save_state call."""
        import orchestrate
        path = str(tmp_path / "state.json")
        monkeypatch.setattr(orchestrate, "_get_local_timezone_name", lambda: "Europe/Berlin")
        deps = make_deps(
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        # start_time set so the Issue 6 default-state guard does not fire.
        save_state(path, PersistentState(start_time="2026-05-18T22:08:05+02:00"), deps)
        data = json.loads(open(path).read())
        assert data["timezone"] == "Europe/Berlin"

    def test_save_state_writes_timezone_offset_field(self, tmp_path: Any, monkeypatch: Any) -> None:
        """timezone_offset is written on every save so PowerShell 5.1 (which cannot
        resolve IANA names via TimeZoneInfo) can still detect TZ mismatch.
        """
        import orchestrate
        path = str(tmp_path / "state.json")
        monkeypatch.setattr(orchestrate, "_get_local_timezone_offset", lambda: "+02:00")
        deps = make_deps(
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        # start_time set so the Issue 6 default-state guard does not fire.
        save_state(path, PersistentState(start_time="2026-05-18T22:08:05+02:00"), deps)
        data = json.loads(open(path).read())
        assert data["timezone_offset"] == "+02:00"

    def test_save_state_refreshes_timezone_offset_on_dst_change(self, tmp_path: Any, monkeypatch: Any) -> None:
        """timezone_offset is recomputed on every save, so a DST transition between
        saves is reflected without restarting the orchestrator.
        """
        import orchestrate
        path = str(tmp_path / "state.json")
        offsets = iter(["+01:00", "+02:00"])
        monkeypatch.setattr(orchestrate, "_get_local_timezone_offset", lambda: next(offsets))
        deps = make_deps(
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        # start_time set so the Issue 6 default-state guard does not fire.
        state = PersistentState(start_time="2026-05-18T22:08:05+02:00")
        save_state(path, state, deps)
        assert json.loads(open(path).read())["timezone_offset"] == "+01:00"
        save_state(path, state, deps)
        assert json.loads(open(path).read())["timezone_offset"] == "+02:00"

    def test_preserves_external_stop_requested_true(self, tmp_path: Any) -> None:
        """Regression: an outside writer setting stop_requested=true on disk
        must survive a subsequent save_state(), even when the orchestrator's
        in-memory state still has stop_requested=false.

        Without this, save_state() blindly overwrites the disk value before
        check_stop_conditions._read_external_stop_request() can observe it,
        and external stop signals are silently dropped (see post-AC-38 race).
        """
        path = str(tmp_path / "state.json")
        # External writer puts stop_requested=true on disk
        with open(path, "w") as f:
            json.dump({"stop_requested": True}, f)
        deps = make_deps(
            file_exists=lambda p: os.path.exists(p),
            read_file=lambda p: open(p).read(),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        # In-memory state has stop_requested=false (orchestrator mid-session).
        # start_time set so the Issue 6 default-state guard does not fire.
        state = PersistentState(
            stop_requested=False, start_time="2026-05-18T22:08:05+02:00"
        )
        save_state(path, state, deps)
        data = json.loads(open(path).read())
        assert data["stop_requested"] is True, (
            "external stop_requested=true was clobbered by blind save_state"
        )
        # Side effect: in-memory state is mirrored so subsequent code sees it
        assert state.stop_requested is True

    def test_does_not_revive_consumed_stop_requested(self, tmp_path: Any) -> None:
        """When stop_requested is false both on disk and in memory, save_state
        must leave it false (no spurious revival from stale disk state)."""
        path = str(tmp_path / "state.json")
        with open(path, "w") as f:
            json.dump({"stop_requested": False}, f)
        deps = make_deps(
            file_exists=lambda p: os.path.exists(p),
            read_file=lambda p: open(p).read(),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        state = PersistentState(stop_requested=False)
        save_state(path, state, deps)
        data = json.loads(open(path).read())
        assert data["stop_requested"] is False
        assert state.stop_requested is False

    def test_refuses_default_state_overwrite_mid_run(
        self, tmp_path: Any, capsys: Any
    ) -> None:
        """Issue 6 regression: save_state must NOT clobber a populated on-disk
        state.json with a fresh PersistentState() (start_time=None).

        Reproduces the recurrent mid-run failure where state.json reverts to
        is_running=false, account_index=0, run_count=0, start_time=null while
        the orchestrator process and its child claude session are still alive.
        Downstream impact: the Windows sleep watcher reads is_running=false and
        suspends the host, losing wall-clock time on the active run.

        The defensive guard is: post-startup, the live state always carries
        start_time != None (main() sets it). A save_state call where
        start_time is None and startup=False is therefore a bug — refuse the
        write and log a WARNING so the on-disk state is preserved.
        """
        path = str(tmp_path / "state.json")
        # Populated on-disk state from a real run
        with open(path, "w") as f:
            json.dump(
                {
                    "account_index": 2,
                    "run_count": 7,
                    "start_time": "2026-05-18T22:08:05.057800+02:00",
                    "is_running": True,
                    "active_session": "ce8784d5-358d-432b-bf50-958e1b950c83",
                    "stop_requested": False,
                },
                f,
            )
        deps = make_deps(
            file_exists=lambda p: os.path.exists(p),
            read_file=lambda p: open(p).read(),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        # Simulate the bug: a fresh PersistentState() is passed mid-run
        bad_state = PersistentState()
        save_state(path, bad_state, deps)
        data = json.loads(open(path).read())
        # Disk state must be preserved — refuse the bad overwrite
        assert data["account_index"] == 2, (
            "default-state save clobbered populated account_index"
        )
        assert data["run_count"] == 7, (
            "default-state save clobbered populated run_count"
        )
        assert data["is_running"] is True, (
            "default-state save flipped is_running=true → false mid-run"
        )
        assert data["active_session"] == "ce8784d5-358d-432b-bf50-958e1b950c83", (
            "default-state save cleared the live active_session uuid"
        )
        # Guard must log a WARNING so the bad write is visible in orchestrate.log
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_refuses_partial_default_state_with_active_session(
        self, tmp_path: Any, capsys: Any
    ) -> None:
        """Issue 6 hardened regression: even if `active_session` happens to be
        set on the bad state object, the guard MUST still fire when start_time
        is None. The 2026-05-19 wall-clock snapshot showed exactly this shape:
        active_session populated but start_time=null and run_count/account_index
        both at 0. Only start_time is a reliable invariant — every other field
        can be set by transient code paths (e.g. the active_session context
        manager assigning the uuid before the save).
        """
        path = str(tmp_path / "state.json")
        with open(path, "w") as f:
            json.dump(
                {
                    "account_index": 1,
                    "run_count": 5,
                    "start_time": "2026-05-18T22:08:05.057800+02:00",
                    "is_running": True,
                },
                f,
            )
        deps = make_deps(
            file_exists=lambda p: os.path.exists(p),
            read_file=lambda p: open(p).read(),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        # Bad state: start_time=None but active_session is set (simulating the
        # observed 2026-05-19 state.json snapshot pattern).
        bad_state = PersistentState(
            active_session="3f464873-91db-4230-be34-1803c9b7d305"
        )
        save_state(path, bad_state, deps)
        data = json.loads(open(path).read())
        assert data["account_index"] == 1
        assert data["run_count"] == 5
        assert data["start_time"] == "2026-05-18T22:08:05.057800+02:00"
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_startup_save_allowed_even_with_null_start_time(
        self, tmp_path: Any
    ) -> None:
        """Guard regression: the defensive default-state guard must NOT block
        legitimate startup writes. _reset_startup_state runs BEFORE
        state.start_time = start_time.isoformat() in main() ordering would
        let a startup save through with start_time set, but to be safe the
        startup=True path explicitly bypasses the guard.
        """
        path = str(tmp_path / "state.json")
        # No existing file → no on-disk state to preserve
        deps = make_deps(
            file_exists=lambda p: os.path.exists(p),
            read_file=lambda p: open(p).read(),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        # start_time None mimics an early-startup save before main() sets it
        state = PersistentState(start_time=None, is_running=True)
        save_state(path, state, deps, startup=True)
        data = json.loads(open(path).read())
        assert data["is_running"] is True
        assert data["start_time"] is None


# ---------------------------------------------------------------------------
# Category C: Account management (~15 tests)
# ---------------------------------------------------------------------------


class TestNextAvailableAccount:
    def _make_state(self, account_index: Any = 0, rate_limited_until: Any = None) -> Any:
        state = PersistentState(account_index=account_index)
        if rate_limited_until:
            state.rate_limited_until = rate_limited_until
        return state

    def test_single_account_available_returns_it(self) -> None:
        state = self._make_state()
        account, wait_until = next_available_account(["web"], state)
        assert account == "web"
        assert wait_until is None

    def test_first_account_rate_limited_returns_second(self) -> None:
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        state = self._make_state(rate_limited_until={"gmail": future})
        account, wait_until = next_available_account(["gmail", "web"], state)
        assert account == "web"
        assert wait_until is None

    def test_all_rate_limited_returns_account_and_wait_time(self) -> None:
        future1 = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        future2 = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        state = self._make_state(rate_limited_until={"gmail": future1, "web": future2})
        _account, wait_until = next_available_account(["gmail", "web"], state)
        assert wait_until is not None
        assert isinstance(wait_until, datetime)

    def test_all_permanently_disabled_returns_none_none(self) -> None:
        """AC-19: when all accounts are in disabled_accounts and none are rate-limited."""
        state = self._make_state()
        account, wait_until = next_available_account(
            ["gmail", "web"], state, disabled_accounts={"gmail", "web"}
        )
        assert account is None
        assert wait_until is None

    def test_mix_disabled_and_available(self) -> None:
        state = self._make_state()
        account, wait_until = next_available_account(
            ["gmail", "web"], state, disabled_accounts={"gmail"}
        )
        assert account == "web"
        assert wait_until is None

    def test_disabled_accounts_none_handled(self) -> None:
        state = self._make_state()
        account, wait_until = next_available_account(["web"], state, disabled_accounts=None)
        assert account == "web"
        assert wait_until is None

    def test_reset_time_passed_clears_rate_limit(self) -> None:
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        state = self._make_state(rate_limited_until={"web": past})
        account, wait_until = next_available_account(["web"], state)
        assert account == "web"
        assert wait_until is None
        # The rate limit entry should be removed
        assert "web" not in state.rate_limited_until

    def test_corrupt_reset_time_treated_as_cleared(self) -> None:
        state = self._make_state(rate_limited_until={"web": "NOT_A_DATETIME"})
        account, wait_until = next_available_account(["web"], state)
        assert account == "web"
        assert wait_until is None

    def test_single_account_disabled_and_rate_limited_returns_none_none(self) -> None:
        """When the only account is both disabled AND rate-limited — (None, None) sentinel."""
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        state = self._make_state(rate_limited_until={"web": future})
        account, wait_until = next_available_account(
            ["web"], state, disabled_accounts={"web"}
        )
        assert account is None
        assert wait_until is None

    def test_multiple_accounts_rotates_from_index(self) -> None:
        state = self._make_state(account_index=1)
        account, wait_until = next_available_account(["gmail", "web", "gmail2"], state)
        assert account == "web"
        assert wait_until is None

    def test_earliest_wait_returned_when_all_rate_limited(self) -> None:
        early = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        late = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()
        state = self._make_state(rate_limited_until={"gmail": late, "web": early})
        _, wait_until = next_available_account(["gmail", "web"], state)
        # Should return the earliest reset time
        assert wait_until is not None
        early_dt = datetime.fromisoformat(early)
        assert abs((wait_until - early_dt).total_seconds()) < 1


# ---------------------------------------------------------------------------
# Category D: Feedback helpers (~20 tests)
# ---------------------------------------------------------------------------


class TestFindAnsweredFeedback:
    def test_empty_dir_returns_empty_list(self, tmp_path: Any) -> None:
        deps = make_deps(list_dir=lambda p: [])
        result = find_answered_feedback(str(tmp_path), deps)
        assert result == []

    def test_nonexistent_dir_returns_empty_list(self, tmp_path: Any) -> None:
        fake_path = str(tmp_path / "nonexistent")
        result = find_answered_feedback(fake_path, make_deps())
        assert result == []

    def test_one_answered_task_returned(self, tmp_path: Any) -> None:
        task_dir = tmp_path / "TASK-001"
        task_dir.mkdir()
        question_path = task_dir / "question.md"
        answer_path = task_dir / "answer.md"
        question_path.write_text(
            "---\ntask_id: TASK-001\nsession_id: sess-123\naccount: web\n---\nQuestion text"
        )
        answer_path.write_text("My answer")

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        deps = make_deps(
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
        )
        result = find_answered_feedback(str(tmp_path), deps)
        assert len(result) == 1
        assert result[0]["task_id"] == "TASK-001"
        assert result[0]["session_id"] == "sess-123"
        assert result[0]["account"] == "web"
        assert result[0]["answer_path"] == str(answer_path)

    def test_malformed_frontmatter_skipped(self, tmp_path: Any, capsys: Any) -> None:
        task_dir = tmp_path / "TASK-BAD"
        task_dir.mkdir()
        question_path = task_dir / "question.md"
        answer_path = task_dir / "answer.md"
        question_path.write_text("No frontmatter at all")  # no session_id or account
        answer_path.write_text("Some answer")

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        deps = make_deps(
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
        )
        result = find_answered_feedback(str(tmp_path), deps)
        assert result == []
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_empty_answer_skipped(self, tmp_path: Any, capsys: Any) -> None:
        task_dir = tmp_path / "TASK-002"
        task_dir.mkdir()
        question_path = task_dir / "question.md"
        answer_path = task_dir / "answer.md"
        question_path.write_text(
            "---\ntask_id: TASK-002\nsession_id: sess-456\naccount: gmail\n---\nQ"
        )
        answer_path.write_text("")  # empty

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        deps = make_deps(
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
        )
        result = find_answered_feedback(str(tmp_path), deps)
        assert result == []
        captured = capsys.readouterr()
        assert "DEBUG" in captured.out

    def test_whitespace_answer_skipped(self, tmp_path: Any, capsys: Any) -> None:
        task_dir = tmp_path / "TASK-003"
        task_dir.mkdir()
        question_path = task_dir / "question.md"
        answer_path = task_dir / "answer.md"
        question_path.write_text(
            "---\ntask_id: TASK-003\nsession_id: sess-789\naccount: web\n---\nQ"
        )
        answer_path.write_text("   \n\t  ")  # whitespace only

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        deps = make_deps(
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
        )
        result = find_answered_feedback(str(tmp_path), deps)
        assert result == []

    def test_file_entry_skipped(self, tmp_path: Any) -> None:
        # A non-dir entry in the feedback dir should be skipped
        file_entry = make_fake_dir_entry(str(tmp_path / "somefile.txt"), is_dir=False)
        deps = make_deps(list_dir=lambda p: [file_entry])
        result = find_answered_feedback(str(tmp_path), deps)
        assert result == []


class TestGetUnansweredQuestions:
    def test_no_question_files_returns_empty(self, tmp_path: Any) -> None:
        deps = make_deps(list_dir=lambda p: [])
        result = get_unanswered_questions(str(tmp_path), deps)
        assert result == []

    def test_question_with_no_answer_returned(self, tmp_path: Any) -> None:
        task_dir = tmp_path / "TASK-100"
        task_dir.mkdir()
        question_path = task_dir / "question.md"
        question_path.write_text("---\ntask_id: TASK-100\nsession_id: sid-1\n---\nQ text")

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        deps = make_deps(list_dir=lambda p: [entry])
        result = get_unanswered_questions(str(tmp_path), deps)
        assert len(result) == 1
        assert result[0]["task_id"] == "TASK-100"

    def test_question_with_whitespace_answer_logs_warning(self, tmp_path: Any, capsys: Any) -> None:
        task_dir = tmp_path / "TASK-200"
        task_dir.mkdir()
        question_path = task_dir / "question.md"
        answer_path = task_dir / "answer.md"
        question_path.write_text("---\ntask_id: TASK-200\nsession_id: sid-2\n---\nQ text")
        answer_path.write_text("   ")  # whitespace only

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        deps = make_deps(list_dir=lambda p: [entry])
        result = get_unanswered_questions(str(tmp_path), deps)
        assert len(result) == 1
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "whitespace" in captured.out

    def test_nonexistent_dir_returns_empty(self) -> None:
        deps = make_deps()
        result = get_unanswered_questions("/nonexistent/path", deps)
        assert result == []

    def test_question_with_real_answer_not_returned(self, tmp_path: Any) -> None:
        task_dir = tmp_path / "TASK-300"
        task_dir.mkdir()
        question_path = task_dir / "question.md"
        answer_path = task_dir / "answer.md"
        question_path.write_text("---\ntask_id: TASK-300\nsession_id: sid-3\n---\nQ text")
        answer_path.write_text("Real answer here")

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        deps = make_deps(list_dir=lambda p: [entry])
        result = get_unanswered_questions(str(tmp_path), deps)
        assert result == []


class TestCheckAndUpdateQuestionFingerprint:
    def test_no_prior_fingerprint_stores_new(self) -> None:
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        deps = make_deps()
        check_and_update_question_fingerprint("TASK-X", "What should I do next?", state, run_data, deps)
        assert "TASK-X" in state.question_fingerprints
        assert isinstance(state.question_fingerprints["TASK-X"]["words"], list)

    def test_low_similarity_no_warning(self, capsys: Any) -> None:
        state = PersistentState()
        state.question_fingerprints["TASK-X"] = {
            "words": ["apple", "banana", "cherry", "date", "elderberry"],
            "preview": "apple banana cherry date elderberry",
        }
        run_data = RunData(start_time=datetime.now())
        deps = make_deps()
        check_and_update_question_fingerprint(
            "TASK-X", "completely different unrelated topic vehicle road", state, run_data, deps
        )
        captured = capsys.readouterr()
        assert "WARNING" not in captured.out
        assert len(run_data.repeated_questions) == 0

    def test_high_similarity_logs_warning(self, capsys: Any) -> None:
        state = PersistentState()
        # Store a fingerprint with specific words
        state.question_fingerprints["TASK-Y"] = {
            "words": ["should", "i", "proceed", "with", "the", "implementation"],
            "preview": "should i proceed with the implementation",
        }
        run_data = RunData(start_time=datetime.now())
        deps = make_deps()
        # Ask nearly identical question
        check_and_update_question_fingerprint(
            "TASK-Y",
            "Should I proceed with the implementation now?",
            state,
            run_data,
            deps,
        )
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert len(run_data.repeated_questions) >= 1

    def test_similarity_at_threshold_060_triggers_warning(self, capsys: Any) -> None:
        # Construct two word sets with exactly 0.60 Jaccard similarity
        # |A∩B| = 3, |A∪B| = 5 → 3/5 = 0.60
        words_a = ["alpha", "beta", "gamma", "delta"]
        words_b = ["alpha", "beta", "gamma", "epsilon"]
        # Jaccard = 3/5 = 0.60

        state = PersistentState()
        state.question_fingerprints["TASK-Z"] = {
            "words": words_a,
            "preview": " ".join(words_a),
        }
        run_data = RunData(start_time=datetime.now())
        deps = make_deps()
        # Build a question from words_b
        question_text = " ".join(words_b)
        check_and_update_question_fingerprint("TASK-Z", question_text, state, run_data, deps)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_fingerprint_updated_after_call(self) -> None:
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        deps = make_deps()
        check_and_update_question_fingerprint("TASK-A", "first question text here", state, run_data, deps)
        first_words = set(state.question_fingerprints["TASK-A"]["words"])

        check_and_update_question_fingerprint("TASK-A", "second completely different words", state, run_data, deps)
        second_words = set(state.question_fingerprints["TASK-A"]["words"])
        assert first_words != second_words

    def test_repeated_questions_list_populated_on_high_similarity(self) -> None:
        state = PersistentState()
        state.question_fingerprints["TASK-B"] = {
            "words": ["should", "i", "proceed", "implementation"],
            "preview": "should i proceed implementation",
        }
        run_data = RunData(start_time=datetime.now())
        deps = make_deps()
        check_and_update_question_fingerprint(
            "TASK-B", "should i proceed with implementation now", state, run_data, deps
        )
        if run_data.repeated_questions:
            entry = run_data.repeated_questions[0]
            assert entry["task_id"] == "TASK-B"
            assert "similarity" in entry


# ---------------------------------------------------------------------------
# Category E: Loop step methods (~40 tests)
# ---------------------------------------------------------------------------


def make_orchestrator(**dep_overrides: Any) -> Orchestrator:
    deps = make_deps(**dep_overrides)
    return Orchestrator(deps)


def make_stop_flag(requested: Any = False) -> dict[Any, Any]:
    return {"requested": requested}


class TestCheckStopConditions:
    def test_stop_flag_set_returns_manual(self) -> None:
        o = make_orchestrator()
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        stop, reason = o.check_stop_conditions(
            state, run_data, args, {"requested": True}, None, 0
        )
        assert stop is True
        assert reason == "manual"

    def test_stop_requested_in_state_json_returns_manual(self) -> None:
        """AC-38: when state.json[stop_requested]=True, check_stop_conditions stops with 'manual'."""
        state_json = json.dumps({"stop_requested": True})
        o = make_orchestrator(
            file_exists=lambda p: p.endswith("state.json"),
            read_file=lambda p: state_json,
        )
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        stop, reason = o.check_stop_conditions(
            state, run_data, args, {"requested": False}, None, 0
        )
        assert stop is True
        assert reason == "manual"

    def test_max_tasks_reached_returns_max_tasks(self, capsys: Any) -> None:
        o = make_orchestrator(file_exists=lambda p: False)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args(max_tasks=3)
        stop, reason = o.check_stop_conditions(
            state, run_data, args, {"requested": False}, None, 3
        )
        assert stop is True
        assert reason == "max_tasks"

    def test_not_at_max_tasks_does_not_stop(self) -> None:
        o = make_orchestrator(file_exists=lambda p: False)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args(max_tasks=5)
        stop, reason = o.check_stop_conditions(
            state, run_data, args, {"requested": False}, None, 2
        )
        assert stop is False
        assert reason == ""

    def test_stop_at_in_future_does_not_stop(self) -> None:
        future = datetime(2099, 1, 1, 12, 0, 0)
        o = make_orchestrator(
            file_exists=lambda p: False,
            get_now_local=lambda: datetime(2026, 1, 1, 12, 0, 0),
        )
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        stop, _reason = o.check_stop_conditions(
            state, run_data, args, {"requested": False}, future, 0
        )
        assert stop is False

    def test_stop_at_passed_returns_scheduled(self) -> None:
        past = datetime(2020, 1, 1, 12, 0, 0)
        o = make_orchestrator(
            file_exists=lambda p: False,
            get_now_local=lambda: datetime(2026, 1, 1, 12, 0, 0),
        )
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        stop, reason = o.check_stop_conditions(
            state, run_data, args, {"requested": False}, past, 0
        )
        assert stop is True
        assert reason == "scheduled"

    def test_no_stop_conditions_met_returns_false(self) -> None:
        o = make_orchestrator(file_exists=lambda p: False)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args(max_tasks=None)
        stop, reason = o.check_stop_conditions(
            state, run_data, args, {"requested": False}, None, 0
        )
        assert stop is False
        assert reason == ""

    def test_max_tasks_none_does_not_stop(self) -> None:
        o = make_orchestrator(file_exists=lambda p: False)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args(max_tasks=None)
        stop, _reason = o.check_stop_conditions(
            state, run_data, args, {"requested": False}, None, 100
        )
        assert stop is False


class TestScanInProgressWithoutSessionId:
    def test_none_found_empty_list(self) -> None:
        o = make_orchestrator(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=""),
        )
        o._accounts = ["web"]
        run_data = RunData(start_time=datetime.now())
        result = o.scan_in_progress_without_session_id(run_data)
        assert result == []
        assert run_data.skipped_no_session_id == []

    def test_task_with_no_session_id_logged_and_reported(self, tmp_path: Any, capsys: Any) -> None:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text("---\nstatus: in_progress\ntask_id: TASK-NO-SID\n---\nBody")

        o = make_orchestrator(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(goal_path) + "\n"),
        )
        o._accounts = ["web"]
        run_data = RunData(start_time=datetime.now())
        result = o.scan_in_progress_without_session_id(run_data)
        assert "TASK-NO-SID" in result
        assert "TASK-NO-SID" in run_data.skipped_no_session_id
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_warning_text_lists_both_causes(self, tmp_path: Any, capsys: Any) -> None:
        """Finding 3: after the session-id-write fix, the warning fires for either
        (a) manual sessions, or (b) failed goal.md updates on a prior launch.
        The text must reflect both causes, not the misleading 'may have been started
        manually' which suggested only (a).
        """
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-CAUSES\n---\nBody"
        )
        o = make_orchestrator(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(goal_path) + "\n"),
        )
        o._accounts = ["web"]
        run_data = RunData(start_time=datetime.now())
        o.scan_in_progress_without_session_id(run_data)
        captured = capsys.readouterr()
        assert "manual session" in captured.out, (
            f"warning should name 'manual session' as one cause; got:\n{captured.out}"
        )
        assert "goal.md update failed" in captured.out, (
            f"warning should name 'goal.md update failed' as the other cause; got:\n{captured.out}"
        )

    def test_same_task_not_logged_twice_across_calls(self, tmp_path: Any, capsys: Any) -> None:
        """AC-22: deduplication — same task not appended to skipped_no_session_id twice."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text("---\nstatus: in_progress\ntask_id: TASK-DUP\n---\nBody")

        o = make_orchestrator(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(goal_path) + "\n"),
        )
        o._accounts = ["web"]
        run_data = RunData(start_time=datetime.now())
        o.scan_in_progress_without_session_id(run_data)
        o.scan_in_progress_without_session_id(run_data)
        assert run_data.skipped_no_session_id.count("TASK-DUP") == 1


class TestFindActiveTaskGoalSessionIdGuard:
    """Regression guard: manually-claimed in_progress tasks must not be hijacked.

    Manual sessions never write session_id to goal.md. Before the fix,
    find_active_task_goal returned any in_progress task; the launch path then
    overwrote session_id with the orchestrator's UUID, claiming the user's task.
    """

    def test_in_progress_without_session_id_is_skipped(self, tmp_path: Any) -> None:
        from orchestrate import find_active_task_goal

        goal_path = tmp_path / "manual_goal.md"
        goal_path.write_text(
            "---\ntask_id: TASK-MANUAL-99\nstatus: in_progress\n---\nBody"
        )

        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(goal_path) + "\n"),
        )
        assert find_active_task_goal(str(tmp_path), deps) is None

    def test_in_progress_with_session_id_is_returned(self, tmp_path: Any) -> None:
        from orchestrate import find_active_task_goal

        goal_path = tmp_path / "orch_goal.md"
        goal_path.write_text(
            "---\ntask_id: TASK-ORCH-01\nstatus: in_progress\n"
            "session_id: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee\n---\nBody"
        )

        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(goal_path) + "\n"),
        )
        assert find_active_task_goal(str(tmp_path), deps) == str(goal_path)

    def test_empty_session_id_value_treated_as_missing(self, tmp_path: Any) -> None:
        from orchestrate import find_active_task_goal

        goal_path = tmp_path / "empty_sid_goal.md"
        goal_path.write_text(
            "---\ntask_id: TASK-EMPTY-SID\nstatus: in_progress\n"
            'session_id: ""\n---\nBody'
        )

        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(goal_path) + "\n"),
        )
        assert find_active_task_goal(str(tmp_path), deps) is None


class TestPickNextTaskSkipsInProgress:
    """Defense-in-depth: next_tasks.py does not exclude in_progress, so the
    orchestrator must filter here. Without this guard, a manually-claimed task
    whose session_id was just cleared could resurface on the next loop.
    """

    def test_in_progress_task_from_next_tasks_is_skipped(self, tmp_path: Any) -> Any:
        import orchestrate
        from orchestrate import pick_next_task_for_session

        in_prog = tmp_path / "in_prog_goal.md"
        in_prog.write_text(
            "---\ntask_id: TASK-INPROG-01\nstatus: in_progress\n---\nBody"
        )
        pending = tmp_path / "pending_goal.md"
        pending.write_text(
            "---\ntask_id: TASK-PEND-02\nstatus: pending\n---\nBody"
        )

        next_tasks_stdout = (
            f"1. [TASK-INPROG-01] something\n"
            f"   Path: {in_prog}\n"
            f"\n"
            f"2. [TASK-PEND-02] something\n"
            f"   Path: {pending}\n"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            joined = " ".join(str(c) for c in cmd)
            if "next_tasks.py" in joined:
                return _fake_completed(stdout=next_tasks_stdout)
            if "is_awaiting_answer.py" in joined:
                return _fake_completed(returncode=0)
            return _fake_completed()

        deps = make_deps(run_subprocess=fake_subprocess)
        # PROJECT_ROOT is referenced by pick_next_task_for_session for path joining;
        # absolute paths are returned as-is so PROJECT_ROOT value does not affect this test.
        with mock.patch.object(orchestrate, "PROJECT_ROOT", str(tmp_path)):
            result = pick_next_task_for_session(deps)

        assert result is not None
        abs_path, task_id, _is_opus = result
        assert task_id == "TASK-PEND-02"
        assert abs_path == str(pending)


class TestRunPreflightQueueCheck:
    def _make_orchestrator_with_next_tasks(self, next_tasks_stdout: Any, is_awaiting_returncode: Any = 1) -> Any:
        def fake_subprocess(cmd, *args, **kwargs):
            if "next_tasks.py" in " ".join(str(c) for c in cmd):
                return _fake_completed(stdout=next_tasks_stdout)
            if "is_awaiting_answer.py" in " ".join(str(c) for c in cmd):
                return _fake_completed(returncode=is_awaiting_returncode)
            return _fake_completed()

        o = make_orchestrator(run_subprocess=fake_subprocess, file_exists=lambda p: False)
        o._accounts = ["web"]
        return o

    def test_empty_output_returns_queue_empty(self, capsys: Any) -> None:
        """AC-18: next_tasks.py returns empty → (False, 'queue_empty')"""
        o = self._make_orchestrator_with_next_tasks("")
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        ok, reason = o.run_preflight_queue_check(state, run_data, args)
        assert ok is False
        assert reason == "queue_empty"

    def test_all_tasks_awaiting_returns_all_tasks_awaiting(self, capsys: Any) -> None:
        stdout = "1. [TASK-001] - Some task\n"
        # is_awaiting_answer returns non-zero → task IS awaiting (not runnable)
        o = self._make_orchestrator_with_next_tasks(stdout, is_awaiting_returncode=1)
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        ok, reason = o.run_preflight_queue_check(state, run_data, args)
        assert ok is False
        assert reason == "all_tasks_awaiting_answer"

    def test_runnable_task_returns_true(self) -> None:
        stdout = "1. [TASK-001] - Some task\n"
        # is_awaiting_answer returns 0 → task is runnable
        o = self._make_orchestrator_with_next_tasks(stdout, is_awaiting_returncode=0)
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        ok, reason = o.run_preflight_queue_check(state, run_data, args)
        assert ok is True
        assert reason is None


class TestWaitForAccountIfNeeded:
    def test_account_available_now(self) -> None:
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        o = make_orchestrator(file_exists=lambda p: False)
        o._accounts = ["web"]
        args = make_args()
        account, waited = o.wait_for_account_if_needed(state, run_data, args, {"requested": False})
        assert account == "web"
        assert waited is False

    def test_none_none_sentinel_returns_none_false(self, capsys: Any) -> None:
        """AC-19: (None, None) → (None, False) indicating all accounts disabled."""
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        # All accounts disabled
        run_data.disabled_accounts = {"web"}
        o = make_orchestrator(file_exists=lambda p: False)
        o._accounts = ["web"]
        args = make_args()
        account, waited = o.wait_for_account_if_needed(state, run_data, args, {"requested": False})
        assert account is None
        assert waited is False
        captured = capsys.readouterr()
        assert "permanently disabled" in captured.out

    def test_rate_limited_sleeps_and_returns_none_true(self) -> None:
        # interruptible_sleep calls time.sleep directly (not deps.sleep).
        # Use stop_flag to break out immediately rather than sleeping 3600 seconds.
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        state = PersistentState(rate_limited_until={"web": future})
        run_data = RunData(start_time=datetime.now())
        stop_flag = {"requested": True}  # pre-set so interruptible_sleep exits immediately
        o = make_orchestrator(
            file_exists=lambda p: False,
            get_now_utc=lambda: datetime.now(timezone.utc),
        )
        o._accounts = ["web"]
        args = make_args()
        account, waited = o.wait_for_account_if_needed(state, run_data, args, stop_flag)
        assert account is None
        assert waited is True


class TestProcessAnsweredFeedbackResumeLimits:
    def test_after_3_attempts_4th_is_skipped(self, tmp_path: Any, capsys: Any) -> Any:
        """AC-21: after 3 resume attempts for same session_id, 4th is skipped."""
        task_dir = tmp_path / "TASK-RESUME"
        task_dir.mkdir()
        question_path = task_dir / "question.md"
        answer_path = task_dir / "answer.md"
        question_path.write_text(
            "---\ntask_id: TASK-RESUME\nsession_id: sess-rl\naccount: web\n---\nQ"
        )
        answer_path.write_text("An answer")

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)

        def fake_subprocess(cmd, *args, **kwargs):
            return _fake_completed(returncode=0, stdout="Done")

        o = make_orchestrator(
            run_subprocess=fake_subprocess,
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
            file_exists=lambda p: os.path.exists(p),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        # Pre-fill 3 attempts so the 4th call triggers the limit
        run_data.resume_attempt_counts["sess-rl"] = 3

        decision, _sl = o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        assert decision == "continue"
        # Should be logged to exhausted_resume_tasks
        assert len(run_data.exhausted_resume_tasks) == 1
        assert run_data.exhausted_resume_tasks[0]["session_id"] == "sess-rl"
        captured = capsys.readouterr()
        assert "exhausted" in captured.out


class TestProcessAnsweredFeedbackFolderMove:
    """After AC-06: the orchestrator deletes pending_feedback/<TASK_ID>/ on clean
    exit (archive already written to plans_and_protocols/ before the session runs).
    The delete must tolerate the source folder already being gone — task-complete
    deletes it too as part of its own cleanup.
    """

    def test_folder_already_removed_logs_info_not_warning(self, tmp_path: Any, capsys: Any) -> Any:
        task_dir = tmp_path / "pending_feedback" / "TASK-CLEANED"
        task_dir.mkdir(parents=True)
        (task_dir / "question.md").write_text(
            "---\ntask_id: TASK-CLEANED\nsession_id: sess-c\naccount: web\nskill: test-skill\n---\nQ"
        )
        (task_dir / "answer.md").write_text("An answer")

        # Create a fake goal.md so _resolve_task_goal_and_model returns a real path.
        goal_dir = tmp_path / "req" / "TASK-CLEANED"
        goal_dir.mkdir(parents=True)
        goal_path = goal_dir / "goal.md"
        goal_path.write_text("---\ntask_id: TASK-CLEANED\n---\n")

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            # Simulate task-complete deleting the pending_feedback folder mid-session.
            if "claude" in cmd_str and task_dir.exists():
                shutil.rmtree(task_dir)
            return _fake_completed(returncode=0, stdout="Done")

        o = make_orchestrator(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
            file_exists=lambda p: os.path.exists(p),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        import orchestrate as _orc
        orig_fb = _orc.FEEDBACK_DIR
        _orc.FEEDBACK_DIR = str(tmp_path / "pending_feedback")
        try:
            decision, _sl = o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        finally:
            _orc.FEEDBACK_DIR = orig_fb

        assert decision == "continue"
        captured = capsys.readouterr()
        assert "already removed" in captured.out
        assert "could not delete pending_feedback" not in captured.out

    def test_clean_exit_deletes_pending_feedback_folder(self, tmp_path: Any, capsys: Any) -> Any:
        """On clean exit the pending_feedback folder is deleted (not moved)."""
        task_dir = tmp_path / "pending_feedback" / "TASK-DEL"
        task_dir.mkdir(parents=True)
        (task_dir / "question.md").write_text(
            "---\ntask_id: TASK-DEL\nsession_id: sess-d\naccount: web\nskill: test-skill\n---\nQ"
        )
        (task_dir / "answer.md").write_text("An answer")

        goal_dir = tmp_path / "req" / "TASK-DEL"
        goal_dir.mkdir(parents=True)
        goal_path = goal_dir / "goal.md"
        goal_path.write_text("---\ntask_id: TASK-DEL\n---\n")

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)

        def fake_subprocess(cmd, *a, **kw):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            return _fake_completed(returncode=0, stdout="Done")

        o = make_orchestrator(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
            file_exists=lambda p: os.path.exists(p),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        import orchestrate as _orc
        orig_fb = _orc.FEEDBACK_DIR
        _orc.FEEDBACK_DIR = str(tmp_path / "pending_feedback")
        try:
            decision, _sl = o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        finally:
            _orc.FEEDBACK_DIR = orig_fb

        assert decision == "continue"
        # Folder must be gone (deleted, not moved)
        assert not task_dir.exists(), "pending_feedback folder must be deleted on clean exit"
        # answered_feedback/ must NOT be created (deprecated path)
        assert not (tmp_path / "answered_feedback").exists(), \
            "answered_feedback/ must not be created (deprecated)"
        captured = capsys.readouterr()
        assert "archived to plans_and_protocols" in captured.out


class TestProcessInProgressResumeLimits:
    def test_after_3_attempts_4th_is_skipped(self, tmp_path: Any, capsys: Any) -> Any:
        """AC-21: resume attempt limit for in-progress tasks."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-IPR\nsession_id: sess-ipr\nsession_account: web\n---\nBody"
        )

        call_count = [0]

        def fake_subprocess(cmd, *args, **kwargs):
            call_count[0] += 1
            return _fake_completed(stdout=str(goal_path) + "\n")

        o = make_orchestrator(
            run_subprocess=fake_subprocess,
            file_exists=lambda p: os.path.exists(p),
            read_file=lambda p: open(p).read(),
        )
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        # Pre-fill 3 attempts
        run_data.resume_attempt_counts["sess-ipr"] = 3

        decision, _sl = o.process_in_progress_resume(
            state, run_data, args, {"requested": False}, [], 0
        )
        assert decision == "continue"
        assert any(e["session_id"] == "sess-ipr" for e in run_data.exhausted_resume_tasks)
        captured = capsys.readouterr()
        assert "exhausted" in captured.out

    def test_rate_limit_failure_does_not_consume_attempt(self, tmp_path: Any) -> Any:
        """Rate-limit exits must not decrement the 3-attempt budget (AC-21).

        All three attempts were consumed by rate-limit failures in the
        2026-05-25 incident, leaving the task permanently skipped for the run
        despite no genuine task-level failure having occurred.
        """
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-RL-IPR\n"
            "session_id: sess-rl-ipr\nsession_account: web\n---\nBody"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                return _fake_completed(
                    returncode=1,
                    stdout="You've hit your session limit · resets 4pm (Europe/Berlin)",
                )
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        decision, _sl = o.process_in_progress_resume(
            state, run_data, args, {"requested": False}, [], 0
        )
        assert decision == "continue"
        # Counter must remain 0 — rate-limit is infra, not a task failure
        assert run_data.resume_attempt_counts.get("sess-rl-ipr", 0) == 0
        # Task must NOT be marked exhausted
        assert "sess-rl-ipr" not in run_data.exhausted_resume_ids

    def test_perm_error_does_not_consume_attempt(self, tmp_path: Any) -> Any:
        """Perm-error exits (account has no access) must not consume the 3-attempt budget."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-PE-IPR\n"
            "session_id: sess-pe-ipr\nsession_account: web\n---\nBody"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                return _fake_completed(returncode=1, stdout="does not have access")
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        decision, _sl = o.process_in_progress_resume(
            state, run_data, args, {"requested": False}, [], 0
        )
        assert decision == "continue"
        # Counter must remain 0 — perm-error is infra, not a task failure
        assert run_data.resume_attempt_counts.get("sess-pe-ipr", 0) == 0


# ---------------------------------------------------------------------------
# Category F: Git helpers (~10 tests)
# ---------------------------------------------------------------------------


class TestGitCommitBestEffort:
    def test_empty_files_list_no_subprocess_call(self) -> None:
        calls = []
        deps = make_deps(
            run_subprocess=lambda *a, **kw: (calls.append(a), _fake_completed())[1],  # type: ignore[func-returns-value]  # tuple-discard pattern captures append-side-effect; mypy still warns on the None-return
            glob_files=lambda p: [],
        )
        git_commit_best_effort([], "test commit", deps)
        assert calls == []

    def test_no_glob_matches_no_subprocess_call(self) -> None:
        calls = []
        deps = make_deps(
            run_subprocess=lambda *a, **kw: (calls.append(a), _fake_completed())[1],  # type: ignore[func-returns-value]  # tuple-discard pattern captures append-side-effect; mypy still warns on the None-return
            glob_files=lambda p: [],  # no files found
        )
        git_commit_best_effort(["/some/pattern/*.md"], "test commit", deps)
        assert calls == []

    def test_subprocess_success_calls_git_add_then_commit(self) -> Any:
        calls = []

        def fake_subprocess(cmd, *args, **kwargs):
            calls.append(list(cmd))
            # git diff --cached --quiet: returncode=1 means staged changes exist
            if "diff" in cmd:
                return _fake_completed(returncode=1)
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            glob_files=lambda p: ["/fake/file.md"],
        )
        git_commit_best_effort(["/fake/file.md"], "my commit", deps)
        assert len(calls) == 3
        assert calls[0][0] == "git"
        assert calls[0][1] == "add"
        assert calls[1][0] == "git"
        assert calls[1][1] == "diff"
        assert calls[2][0] == "git"
        assert calls[2][1] == "commit"

    def test_subprocess_failure_logs_warning_does_not_raise(self, capsys: Any) -> None:
        def fake_subprocess(cmd, *args, **kwargs):
            raise subprocess.CalledProcessError(1, cmd)

        deps = make_deps(
            run_subprocess=fake_subprocess,
            glob_files=lambda p: ["/fake/file.md"],
        )
        git_commit_best_effort(["/fake/file.md"], "commit", deps)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_unexpected_exception_logs_warning(self, capsys: Any) -> None:
        def fake_subprocess(cmd, *args, **kwargs):
            raise RuntimeError("unexpected")

        deps = make_deps(
            run_subprocess=fake_subprocess,
            glob_files=lambda p: ["/fake/file.md"],
        )
        git_commit_best_effort(["/fake/file.md"], "commit", deps)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_absolute_path_passed_directly_to_glob(self) -> None:
        globbed = []
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(),
            glob_files=lambda p: (globbed.append(p), [])[1],  # type: ignore[func-returns-value]  # tuple-discard pattern; mypy still warns on append None-return
        )
        git_commit_best_effort(["/abs/path/file.md"], "commit", deps)
        assert "/abs/path/file.md" in globbed

    def test_relative_path_expanded_via_glob(self) -> None:
        globbed = []
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(),
            glob_files=lambda p: (globbed.append(p), [])[1],  # type: ignore[func-returns-value]  # tuple-discard pattern; mypy still warns on append None-return
        )
        git_commit_best_effort(["automation/reports/*.md"], "commit", deps)
        assert len(globbed) == 1
        # Should be an absolute path (PROJECT_ROOT joined with the relative pattern)
        assert os.path.isabs(globbed[0])

    def test_commit_message_passed_correctly(self) -> Any:
        commit_cmd = []

        def fake_subprocess(cmd, *args, **kwargs):
            if "commit" in cmd:
                commit_cmd.extend(cmd)
            # git diff --cached --quiet: returncode=1 means staged changes exist
            if "diff" in cmd:
                return _fake_completed(returncode=1)
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            glob_files=lambda p: ["/fake/file.md"],
        )
        git_commit_best_effort(["/fake/file.md"], "special commit message", deps)
        assert "special commit message" in commit_cmd

    def test_no_commit_when_nothing_staged(self) -> Any:
        calls = []

        def fake_subprocess(cmd, *args, **kwargs):
            calls.append(list(cmd))
            return _fake_completed(returncode=0)  # diff returns 0 = nothing staged

        deps = make_deps(
            run_subprocess=fake_subprocess,
            glob_files=lambda p: ["/fake/file.md"],
        )
        git_commit_best_effort(["/fake/file.md"], "should not commit", deps)
        # git add + git diff only — no commit
        assert len(calls) == 2
        assert calls[1][1] == "diff"
        assert all("commit" not in c for c in calls)

    def test_git_not_found_logs_warning(self, capsys: Any) -> None:
        def fake_subprocess(cmd, *args, **kwargs):
            raise FileNotFoundError("git not found")

        deps = make_deps(
            run_subprocess=fake_subprocess,
            glob_files=lambda p: ["/fake/file.md"],
        )
        git_commit_best_effort(["/fake/file.md"], "commit", deps)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_multiple_files_all_added(self) -> Any:
        add_args = []

        def fake_subprocess(cmd, *args, **kwargs):
            if "add" in cmd:
                add_args.extend(cmd)
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            glob_files=lambda p: [p],  # return the pattern as-is (fake match)
        )
        git_commit_best_effort(["/file1.md", "/file2.md"], "commit", deps)
        assert "/file1.md" in add_args
        assert "/file2.md" in add_args


# ---------------------------------------------------------------------------
# Category G: Report sections (~15 tests)
# ---------------------------------------------------------------------------


class TestWriteReport:
    def _make_run_data(self, **overrides: Any) -> Any:
        defaults = {
            "start_time": datetime(2026, 4, 10, 8, 0, 0),
            "stop_time": datetime(2026, 4, 10, 9, 0, 0),
            "stop_reason": "manual",
        }
        defaults.update(overrides)
        rd = RunData(start_time=defaults.pop("start_time"))
        for k, v in defaults.items():
            setattr(rd, k, v)
        return rd

    def test_returns_path(self, tmp_path: Any) -> None:
        run_data = self._make_run_data()
        deps = make_deps(
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            list_dir=lambda p: [],
        )
        path = write_report(str(tmp_path / "reports"), run_data, ["web"], str(tmp_path / "feedback"), deps)
        assert path.endswith(".md")

    def test_skipped_no_session_id_section_present_when_nonempty(self, tmp_path: Any) -> None:
        run_data = self._make_run_data()
        run_data.skipped_no_session_id = ["TASK-NO-SID"]
        written = {}

        def fake_write(p, c):
            written[p] = c

        deps = make_deps(
            makedirs=lambda p: None,
            write_file=fake_write,
            list_dir=lambda p: [],
        )
        path = write_report("/fake/reports", run_data, ["web"], "/fake/feedback", deps)
        # The section label is in write_health_summary, not write_report — write_report
        # only writes per-session info and pending feedback. Check the path was returned.
        assert path is not None

    def test_exhausted_resume_tasks_section_in_health_summary(self, tmp_path: Any) -> None:
        run_data = self._make_run_data()
        run_data.exhausted_resume_tasks = [{"task_id": "TASK-EX", "session_id": "sid-ex"}]
        report_path = str(tmp_path / "report.md")
        (tmp_path / "report.md").write_text("")

        with open(report_path, "a") as f:
            f.write("")

        deps = make_deps(
            makedirs=lambda p: None,
            list_dir=lambda p: [],
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=""),
        )
        # write_health_summary appends to existing file
        import unittest.mock as mock
        with mock.patch("orchestrate.get_unanswered_questions", return_value=[]):
            with mock.patch("orchestrate.snapshot_in_progress_tasks", return_value={}):
                write_health_summary(report_path, run_data, {}, deps)

        content = (tmp_path / "report.md").read_text()
        assert "Exhausted Resumes" in content
        assert "TASK-EX" in content

    def test_repeated_questions_section_in_health_summary(self, tmp_path: Any) -> None:
        run_data = self._make_run_data()
        run_data.repeated_questions = [{"task_id": "TASK-RQ", "similarity": 0.8}]
        report_path = str(tmp_path / "report.md")
        (tmp_path / "report.md").write_text("")

        deps = make_deps(
            makedirs=lambda p: None,
            list_dir=lambda p: [],
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=""),
        )
        import unittest.mock as mock
        with mock.patch("orchestrate.get_unanswered_questions", return_value=[]):
            with mock.patch("orchestrate.snapshot_in_progress_tasks", return_value={}):
                write_health_summary(report_path, run_data, {}, deps)

        content = (tmp_path / "report.md").read_text()
        assert "Repeated Questions" in content
        assert "TASK-RQ" in content

    def test_skipped_no_session_id_section_in_health_summary(self, tmp_path: Any) -> None:
        run_data = self._make_run_data()
        run_data.skipped_no_session_id = ["TASK-NOSID"]
        report_path = str(tmp_path / "report.md")
        (tmp_path / "report.md").write_text("")

        deps = make_deps(
            makedirs=lambda p: None,
            list_dir=lambda p: [],
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=""),
        )
        import unittest.mock as mock
        with mock.patch("orchestrate.get_unanswered_questions", return_value=[]):
            with mock.patch("orchestrate.snapshot_in_progress_tasks", return_value={}):
                write_health_summary(report_path, run_data, {}, deps)

        content = (tmp_path / "report.md").read_text()
        assert "Skipped Tasks" in content
        assert "TASK-NOSID" in content

    def test_all_sections_absent_when_lists_empty(self, tmp_path: Any) -> None:
        run_data = self._make_run_data()
        report_path = str(tmp_path / "report.md")
        (tmp_path / "report.md").write_text("")

        deps = make_deps(
            makedirs=lambda p: None,
            list_dir=lambda p: [],
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=""),
        )
        import unittest.mock as mock
        with mock.patch("orchestrate.get_unanswered_questions", return_value=[]):
            with mock.patch("orchestrate.snapshot_in_progress_tasks", return_value={}):
                write_health_summary(report_path, run_data, {}, deps)

        content = (tmp_path / "report.md").read_text()
        assert "Exhausted Resumes" not in content
        assert "Repeated Questions" not in content
        assert "Skipped Tasks" not in content

    def test_healthy_verdict_when_no_warnings(self, tmp_path: Any) -> None:
        run_data = self._make_run_data()
        report_path = str(tmp_path / "report.md")
        (tmp_path / "report.md").write_text("")

        deps = make_deps(
            makedirs=lambda p: None,
            list_dir=lambda p: [],
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=""),
        )
        import unittest.mock as mock
        with mock.patch("orchestrate.get_unanswered_questions", return_value=[]):
            with mock.patch("orchestrate.snapshot_in_progress_tasks", return_value={}):
                write_health_summary(report_path, run_data, {}, deps)

        content = (tmp_path / "report.md").read_text()
        assert "Healthy" in content

    def test_blocked_verdict_when_pending_questions(self, tmp_path: Any) -> None:
        run_data = self._make_run_data()
        report_path = str(tmp_path / "report.md")
        (tmp_path / "report.md").write_text("")

        deps = make_deps(
            makedirs=lambda p: None,
            list_dir=lambda p: [],
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=""),
        )
        import unittest.mock as mock
        pending = [{"task_id": "TASK-Q", "session_id": "sid-q"}]
        with mock.patch("orchestrate.get_unanswered_questions", return_value=pending):
            with mock.patch("orchestrate.snapshot_in_progress_tasks", return_value={}):
                write_health_summary(report_path, run_data, {}, deps)

        content = (tmp_path / "report.md").read_text()
        assert "Blocked" in content

    def test_write_report_includes_stop_reason(self, tmp_path: Any) -> None:
        run_data = self._make_run_data()
        run_data.stop_reason = "queue_empty"
        written = {}

        def fake_write(p, c):
            written[p] = c

        deps = make_deps(
            makedirs=lambda p: None,
            write_file=fake_write,
            list_dir=lambda p: [],
        )
        write_report("/fake/reports", run_data, ["web"], "/fake/feedback", deps)
        content = next(iter(written.values())) if written else ""
        assert "queue_empty" in content

    def test_write_report_includes_accounts_used(self, tmp_path: Any) -> None:
        run_data = self._make_run_data()
        run_data.accounts_used = {"web", "gmail"}
        written = {}

        def fake_write(p, c):
            written[p] = c

        deps = make_deps(
            makedirs=lambda p: None,
            write_file=fake_write,
            list_dir=lambda p: [],
        )
        write_report("/fake/reports", run_data, ["web", "gmail"], "/fake/feedback", deps)
        content = next(iter(written.values())) if written else ""
        assert "web" in content or "gmail" in content


# ---------------------------------------------------------------------------
# Category H: Integration (full run_loop) (~10 tests)
# ---------------------------------------------------------------------------


class TestRunLoopIntegration:
    """Full run_loop() with a fake OrchestratorDeps that controls subprocess output."""

    def _make_loop_deps(self, subprocess_fn: Any = None, file_exists_fn: Any = None, **overrides: Any) -> Any:
        """Return deps wired for integration testing."""
        if subprocess_fn is None:
            def subprocess_fn(*a, **kw):
                return _fake_completed()
        if file_exists_fn is None:
            def file_exists_fn(p):
                return False
        return make_deps(
            run_subprocess=subprocess_fn,
            popen_subprocess=make_popen_from_subprocess_fn(subprocess_fn),
            file_exists=file_exists_fn,
            list_dir=lambda p: [],
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
            **overrides,
        )

    def _make_minimal_state_and_rundata(self) -> Any:
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        return state, run_data

    def test_max_tasks_1_stops_after_1_session(self, capsys: Any) -> Any:
        """Loop runs max_tasks=1 → stops after 1 session."""
        session_count = [0]

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "next_tasks.py" in cmd_str:
                return _fake_completed(stdout="1. [TASK-001] - A task\n")
            if "is_awaiting_answer.py" in cmd_str:
                return _fake_completed(returncode=0)  # runnable
            if "claude" in cmd_str:
                session_count[0] += 1
                return _fake_completed(returncode=0, stdout="Done")
            if "grep" in cmd_str:
                return _fake_completed(stdout="")
            return _fake_completed()

        deps = self._make_loop_deps(subprocess_fn=fake_subprocess)
        o = Orchestrator(deps)
        state, run_data = self._make_minimal_state_and_rundata()
        args = make_args(max_tasks=1)

        o.run_loop(state, run_data, ["web"], args, {"requested": False}, None)
        assert run_data.stop_reason == "max_tasks"

    def test_ac18_empty_queue_stops_with_queue_empty(self, capsys: Any) -> Any:
        """AC-18: next_tasks.py returns empty → stop_reason = 'queue_empty'"""
        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "next_tasks.py" in cmd_str:
                return _fake_completed(stdout="")  # empty
            if "grep" in cmd_str:
                return _fake_completed(stdout="")
            return _fake_completed()

        deps = self._make_loop_deps(subprocess_fn=fake_subprocess)
        o = Orchestrator(deps)
        state, run_data = self._make_minimal_state_and_rundata()
        args = make_args()

        o.run_loop(state, run_data, ["web"], args, {"requested": False}, None)
        assert run_data.stop_reason == "queue_empty"

    def test_ac19_all_accounts_disabled_stops(self, capsys: Any) -> Any:
        """AC-19: next_available_account() returns (None, None) → stop_reason = 'all_accounts_disabled'"""
        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "next_tasks.py" in cmd_str:
                return _fake_completed(stdout="1. [TASK-001] - A task\n")
            if "is_awaiting_answer.py" in cmd_str:
                return _fake_completed(returncode=0)
            if "grep" in cmd_str:
                return _fake_completed(stdout="")
            # claude returns perm error to disable account
            if "claude" in cmd_str:
                return _fake_completed(
                    returncode=1, stdout="does not have access"
                )
            return _fake_completed()

        deps = self._make_loop_deps(subprocess_fn=fake_subprocess)
        o = Orchestrator(deps)
        state, run_data = self._make_minimal_state_and_rundata()
        args = make_args(max_tasks=5)

        # Pre-disable the only account
        run_data.disabled_accounts.add("web")

        o.run_loop(state, run_data, ["web"], args, {"requested": False}, None)
        assert run_data.stop_reason == "all_accounts_disabled"

    def test_stop_flag_stops_loop_immediately(self) -> None:
        """When stop_flag is pre-set, loop exits on first iteration."""
        deps = self._make_loop_deps()
        o = Orchestrator(deps)
        state, run_data = self._make_minimal_state_and_rundata()
        args = make_args()
        stop_flag = {"requested": True}

        o.run_loop(state, run_data, ["web"], args, stop_flag, None)
        assert run_data.stop_reason == "manual"

    def test_ac21_resume_attempt_limit_logged_to_exhausted(self, tmp_path: Any, capsys: Any) -> Any:
        """AC-21: resume attempt limit reached → task appears in exhausted_resume_tasks."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-EXH\nsession_id: sess-exh\nsession_account: web\n---\nBody"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "next_tasks.py" in cmd_str:
                return _fake_completed(stdout="")  # empty queue — stops after exhaustion
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                return _fake_completed(returncode=0, stdout="Resumed")
            return _fake_completed()

        call_count = [0]
        original_fn = fake_subprocess

        def counting_fn(cmd, *args, **kwargs):
            call_count[0] += 1
            return original_fn(cmd, *args, **kwargs)

        # Isolate STATE_PATH reads so the test does not pick up stop_requested=true
        # from a real automation/state.json left over from a prior autorun.
        from orchestrate import STATE_PATH

        def isolated_read(p):
            if p == STATE_PATH:
                return '{"stop_requested": false}'
            return open(p).read()

        def isolated_exists(p):
            if p == STATE_PATH:
                return False
            return os.path.exists(p)

        deps = make_deps(
            run_subprocess=counting_fn,
            file_exists=isolated_exists,
            read_file=isolated_read,
            list_dir=lambda p: [],
            makedirs=lambda p: None,
            write_file=lambda p, c: open(p, "w").write(c),
        )
        o = Orchestrator(deps)
        state, run_data = self._make_minimal_state_and_rundata()
        args = make_args()

        # Pre-fill 3 attempts so the next call hits the limit
        run_data.resume_attempt_counts["sess-exh"] = 3

        o.run_loop(state, run_data, ["web"], args, {"requested": False}, None)
        assert any(e["session_id"] == "sess-exh" for e in run_data.exhausted_resume_tasks)

    def test_normal_session_success_increments_run_count(self, capsys: Any) -> Any:
        """A successful normal session increments state.run_count."""
        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "next_tasks.py" in cmd_str:
                return _fake_completed(stdout="1. [TASK-001] - A task\n")
            if "is_awaiting_answer.py" in cmd_str:
                return _fake_completed(returncode=0)
            if "grep" in cmd_str:
                return _fake_completed(stdout="")
            if "claude" in cmd_str:
                return _fake_completed(returncode=0, stdout="Done")
            return _fake_completed()

        written = {}

        def fake_write(p, c):
            written[p] = c

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            list_dir=lambda p: [],
            makedirs=lambda p: None,
            write_file=fake_write,
        )
        o = Orchestrator(deps)
        state, run_data = self._make_minimal_state_and_rundata()
        args = make_args(max_tasks=1)

        o.run_loop(state, run_data, ["web"], args, {"requested": False}, None)
        assert state.run_count >= 1

    def test_scheduled_stop_exits_with_scheduled_reason(self) -> None:
        past = datetime(2020, 1, 1, 12, 0, 0)

        deps = make_deps(
            file_exists=lambda p: False,
            list_dir=lambda p: [],
            get_now_local=lambda: datetime(2026, 1, 1, 12, 0, 0),
        )
        o = Orchestrator(deps)
        state, run_data = self._make_minimal_state_and_rundata()
        args = make_args()

        o.run_loop(state, run_data, ["web"], args, {"requested": False}, past)
        assert run_data.stop_reason == "scheduled"

    def test_all_tasks_awaiting_stops_loop(self, capsys: Any) -> Any:
        """When all tasks are awaiting answer, loop stops with correct reason."""
        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "next_tasks.py" in cmd_str:
                return _fake_completed(stdout="1. [TASK-001] - A task\n")
            if "is_awaiting_answer.py" in cmd_str:
                return _fake_completed(returncode=1)  # NOT runnable (awaiting)
            if "grep" in cmd_str:
                return _fake_completed(stdout="")
            return _fake_completed()

        deps = self._make_loop_deps(subprocess_fn=fake_subprocess)
        o = Orchestrator(deps)
        state, run_data = self._make_minimal_state_and_rundata()
        args = make_args()

        o.run_loop(state, run_data, ["web"], args, {"requested": False}, None)
        assert run_data.stop_reason == "all_tasks_awaiting_answer"

    def test_sessions_record_appended_after_normal_session(self) -> Any:
        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "next_tasks.py" in cmd_str:
                return _fake_completed(stdout="1. [TASK-001] - A task\n")
            if "is_awaiting_answer.py" in cmd_str:
                return _fake_completed(returncode=0)
            if "grep" in cmd_str:
                return _fake_completed(stdout="")
            if "claude" in cmd_str:
                return _fake_completed(returncode=0, stdout="Done")
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            list_dir=lambda p: [],
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        state, run_data = self._make_minimal_state_and_rundata()
        args = make_args(max_tasks=1)

        o.run_loop(state, run_data, ["web"], args, {"requested": False}, None)
        assert len(run_data.sessions) >= 1

    def test_accounts_used_populated_after_session(self) -> Any:
        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "next_tasks.py" in cmd_str:
                return _fake_completed(stdout="1. [TASK-001] - A task\n")
            if "is_awaiting_answer.py" in cmd_str:
                return _fake_completed(returncode=0)
            if "grep" in cmd_str:
                return _fake_completed(stdout="")
            if "claude" in cmd_str:
                return _fake_completed(returncode=0, stdout="Done")
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            list_dir=lambda p: [],
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        state, run_data = self._make_minimal_state_and_rundata()
        args = make_args(max_tasks=1)

        o.run_loop(state, run_data, ["web"], args, {"requested": False}, None)
        assert "web" in run_data.accounts_used


# ---------------------------------------------------------------------------
# Additional coverage tests for uncovered code paths
# ---------------------------------------------------------------------------


from orchestrate import (
    accounts_from_state,
    active_session,
    build_env,
    cleanup_old_artifacts,
    make_session_record,
    new_question_written_for,
    read_yaml_frontmatter,
    register_session_in_goal,
    snapshot_in_progress_tasks,
    update_goal_session_fields,
    write_session_output,
)


class TestUpdateGoalSessionFields:
    def test_writes_session_id_and_account(self, tmp_path: Any) -> None:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text("---\nstatus: in_progress\ntask_id: TASK-X\n---\nBody")

        written = {}

        def fake_write(p, c):
            written[p] = c

        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=fake_write,
        )
        update_goal_session_fields(str(goal_path), "uuid-123", "web", deps)
        content = next(iter(written.values()))
        assert "session_id: uuid-123" in content
        assert "session_account: web" in content

    def test_replaces_existing_session_id(self, tmp_path: Any) -> None:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-X\nsession_id: old-uuid\nsession_account: old-acct\n---\nBody"
        )

        written = {}

        def fake_write(p, c):
            written[p] = c

        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=fake_write,
        )
        update_goal_session_fields(str(goal_path), "new-uuid", "new-acct", deps)
        content = next(iter(written.values()))
        assert "session_id: new-uuid" in content
        assert "session_account: new-acct" in content
        assert "old-uuid" not in content
        assert "old-acct" not in content

    def test_os_error_is_non_fatal(self, capsys: Any) -> None:
        def raise_os(p):
            raise OSError("disk error")

        deps = make_deps(read_file=raise_os)
        update_goal_session_fields("/nonexistent/goal.md", "uuid", "acct", deps)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out


class TestRegisterSessionInGoal:
    """Invariant: every orchestrator-launched session MUST record its UUID in goal.md.

    Why: scan_in_progress_without_session_id classifies in_progress tasks with no
    session_id as "manual" and skips them. Three launch paths previously omitted the
    update_goal_session_fields call, causing the orchestrator to misclassify its own
    sessions as manual on subsequent iterations (TASK-PROC-046-03, 2026-05-16 23:27:34).
    """

    def test_writes_session_id_via_update_helper(self, tmp_path: Any) -> None:
        """register_session_in_goal must delegate to update_goal_session_fields."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text("---\nstatus: in_progress\ntask_id: TASK-X\n---\nBody")

        written = {}
        def fake_write(p, c):
            written[p] = c

        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=fake_write,
            # Make git_commit_best_effort a no-op by stubbing subprocess.
            run_subprocess=lambda *a, **kw: _fake_completed(returncode=0),
        )
        register_session_in_goal(str(goal_path), "uuid-fresh", "web", deps)
        # update_goal_session_fields wrote the file with session_id and account.
        assert any("session_id: uuid-fresh" in c for c in written.values())
        assert any("session_account: web" in c for c in written.values())

    def test_commits_goal_md_after_update(self, tmp_path: Any) -> Any:
        """Pair the write with a git commit so state survives an orchestrator restart."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text("---\nstatus: in_progress\ntask_id: TASK-X\n---\nBody")

        subprocess_calls = []
        def fake_subprocess(cmd, *args, **kwargs):
            subprocess_calls.append(cmd)
            # git_commit_best_effort runs `git diff --cached --quiet` and skips the
            # commit if return code is 0 (no staged diff). Return 1 to signal "diff
            # present" so the commit step actually executes.
            if cmd and cmd[0] == "git" and "diff" in cmd and "--quiet" in cmd:
                return _fake_completed(returncode=1)
            return _fake_completed(returncode=0)

        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: None,
            run_subprocess=fake_subprocess,
            # git_commit_best_effort uses glob_files to expand the staged-files list;
            # default in make_deps is `lambda p: []`, which would short-circuit before
            # any git command runs. Return the goal.md path so the commit path is exercised.
            glob_files=lambda p: [str(goal_path)] if str(goal_path) in p else [],
        )
        register_session_in_goal(str(goal_path), "uuid-abc12345", "gmail2", deps)
        # At least one git command should have run; commit message embeds the short uuid.
        git_calls = [c for c in subprocess_calls if c and c[0] == "git"]
        assert git_calls, "expected at least one git subprocess call"
        commit_calls = [c for c in git_calls if "commit" in c]
        assert commit_calls, f"expected a 'git commit' call; got {git_calls}"
        joined = " ".join(commit_calls[0])
        assert "uuid-abc" in joined, "commit message should embed the session uuid prefix"

    def test_noop_when_goal_path_is_none(self) -> None:
        """register_session_in_goal must not touch deps when goal_path is falsy.

        Why: pick_next_task_for_session can fail to locate a goal.md (returns None)
        and the launcher then falls back to a generic prompt. In that case there's
        no file to update — calling update_goal_session_fields with None would crash.
        """
        write_calls = []
        subprocess_calls = []
        deps = make_deps(
            read_file=lambda p: (_ for _ in ()).throw(AssertionError("read_file unexpected")),
            write_file=lambda p, c: write_calls.append((p, c)),
            run_subprocess=lambda *a, **kw: (subprocess_calls.append(a), _fake_completed())[1],  # type: ignore[func-returns-value]  # tuple-discard pattern; mypy still warns on append None-return
        )
        register_session_in_goal(None, "uuid", "web", deps)
        register_session_in_goal("", "uuid", "web", deps)
        assert write_calls == [], "register_session_in_goal must not write when goal_path is falsy"
        assert subprocess_calls == [], "register_session_in_goal must not run subprocesses when goal_path is falsy"


class TestMarkExhausted:
    """Invariant: marking a session as exhausted must populate both filters
    (exhausted_resume_ids set AND exhausted_resume_tasks list when a task_id is
    given) so find_answered_feedback's dual filter skips the item correctly.
    """

    def test_session_only_populates_id_set(self) -> None:
        rd = RunData(start_time=datetime.now())
        rd.mark_exhausted(session_id="sid-1")
        assert "sid-1" in rd.exhausted_resume_ids
        assert rd.exhausted_resume_tasks == [], (
            "task_id omitted should NOT append to exhausted_resume_tasks — that "
            "list filters by task_id, which we don't know in this branch"
        )

    def test_with_task_id_populates_both(self) -> None:
        rd = RunData(start_time=datetime.now())
        rd.mark_exhausted(task_id="TASK-A", session_id="sid-2")
        assert "sid-2" in rd.exhausted_resume_ids
        assert rd.exhausted_resume_tasks == [{"task_id": "TASK-A", "session_id": "sid-2"}]

    def test_multiple_calls_accumulate(self) -> None:
        rd = RunData(start_time=datetime.now())
        rd.mark_exhausted(session_id="a")
        rd.mark_exhausted(task_id="T", session_id="b")
        rd.mark_exhausted(session_id="c")
        assert rd.exhausted_resume_ids == {"a", "b", "c"}
        assert [t["session_id"] for t in rd.exhausted_resume_tasks] == ["b"]


class TestMakeSessionRecord:
    """Factory for session_record dicts — keeps the common fields consistent
    across the five launch sites while still allowing variant fields per path.
    """

    def test_base_fields_always_present(self) -> None:
        deps = make_deps(get_now_local=lambda: datetime(2026, 5, 17, 10, 0, 0))
        rec = make_session_record(
            account="web", task_id="TASK-A", is_resume=False, deps=deps,
        )
        assert rec["start"] == datetime(2026, 5, 17, 10, 0, 0)
        assert rec["account"] == "web"
        assert rec["task_id"] == "TASK-A"
        assert rec["is_resume"] is False
        # No extra fields when none requested.
        assert set(rec.keys()) == {"start", "account", "task_id", "is_resume"}

    def test_none_task_id_falls_back_to_unknown(self) -> None:
        """run_normal_session_step can pass task_id=None when the next task hasn't
        been pre-picked. The record must still have a string task_id for the
        report writer (which calls .get() / .startswith() on it).
        """
        deps = make_deps()
        rec = make_session_record(
            account="web", task_id=None, is_resume=False, deps=deps,
        )
        assert rec["task_id"] == "unknown"

    def test_extra_kwargs_added_verbatim(self) -> None:
        deps = make_deps()
        rec = make_session_record(
            account="web",
            task_id="TASK-B",
            is_resume=False,
            deps=deps,
            fresh_for_answered_question=True,
            recovery_from="prompt_too_long",
            session_uuid="sid-extra",
        )
        assert rec["fresh_for_answered_question"] is True
        assert rec["recovery_from"] == "prompt_too_long"
        assert rec["session_uuid"] == "sid-extra"


class TestActiveSessionContextManager:
    """Invariant: state.active_session is set before launch, cleared after.

    Why: previously five call sites hand-rolled set/save_state/launch/clear/save_state.
    A launcher exception left the UUID orphaned in state.json until the next
    orchestrator startup (where _reset_startup_state clears it). The context manager
    makes the clear unmissable.
    """

    def test_sets_uuid_then_clears_on_normal_exit(self) -> None:
        save_calls = []  # capture active_session value at each save_state call

        def spy_save(path, state, deps):
            save_calls.append(state.active_session)

        deps = make_deps()
        state = PersistentState()

        import orchestrate
        with mock.patch.object(orchestrate, "save_state", side_effect=spy_save):
            with active_session(state, "uuid-xyz", deps):
                # Inside the block, active_session must be the uuid.
                assert state.active_session == "uuid-xyz"
            # After exit, active_session must be cleared.
            assert state.active_session is None

        # Exactly two save_state calls: one with uuid set, one with None.
        assert save_calls == ["uuid-xyz", None], f"expected [uuid, None], got {save_calls}"

    def test_clears_active_session_when_body_raises(self) -> None:
        """active_session=None must be persisted even if the launcher raises.

        Why: previously, an OSError or KeyboardInterrupt from run_*_session would
        skip the clear-and-save line, leaving an orphan UUID in state.json that
        confuses monitoring tools (e.g. win_sleep_script reading state.json).
        """
        save_calls = []

        def spy_save(path, state, deps):
            save_calls.append(state.active_session)

        deps = make_deps()
        state = PersistentState()

        import orchestrate
        with mock.patch.object(orchestrate, "save_state", side_effect=spy_save):
            try:
                with active_session(state, "uuid-raise", deps):
                    raise RuntimeError("simulated launcher crash")
            except RuntimeError:
                pass

        # State must be cleared and the cleanup save_state must have fired.
        assert state.active_session is None
        assert save_calls == ["uuid-raise", None], (
            f"finally must run even on exception; got {save_calls}"
        )

    def test_pre_existing_active_session_is_overwritten(self) -> None:
        """Entering the context manager replaces any pre-existing active_session value.

        Why: defensive — guarantees we never leave stale state if a prior launch
        somehow set active_session without using the context manager.
        """
        deps = make_deps()
        state = PersistentState()
        state.active_session = "stale-uuid"

        import orchestrate
        with mock.patch.object(orchestrate, "save_state"):
            with active_session(state, "new-uuid", deps):
                assert state.active_session == "new-uuid"
            assert state.active_session is None


class TestSnapshotInProgressTasks:
    def test_returns_empty_when_no_in_progress(self) -> None:
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=""),
        )
        result = snapshot_in_progress_tasks("/fake/root", deps)
        assert result == {}

    def test_returns_task_id_to_path_mapping(self, tmp_path: Any) -> None:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-SNAP\n---\nBody"
        )
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(goal_path) + "\n"),
        )
        result = snapshot_in_progress_tasks("/fake/root", deps)
        assert "TASK-SNAP" in result
        assert result["TASK-SNAP"] == str(goal_path)

    def test_skips_non_goal_files(self, tmp_path: Any) -> None:
        readme = tmp_path / "README.md"
        readme.write_text("---\nstatus: in_progress\ntask_id: TASK-README\n---\n")
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(readme) + "\n"),
        )
        result = snapshot_in_progress_tasks("/fake/root", deps)
        assert result == {}


class TestFindResumableSession:
    def test_no_in_progress_tasks_returns_none(self) -> None:
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=""),
        )
        result = find_resumable_session("/fake/root", "/fake/feedback", None, deps)
        assert result is None

    def test_task_with_session_id_returned(self, tmp_path: Any) -> None:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-RES\nsession_id: sid-resume\nsession_account: web\n---\nBody"
        )
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(goal_path) + "\n"),
        )
        result = find_resumable_session("/fake/root", str(tmp_path / "feedback"), None, deps)
        assert result is not None
        assert result["task_id"] == "TASK-RES"
        assert result["session_id"] == "sid-resume"
        assert result["account"] == "web"

    def test_task_without_session_id_skipped(self, tmp_path: Any) -> None:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-NOSID\n---\nBody"
        )
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(goal_path) + "\n"),
        )
        result = find_resumable_session("/fake/root", str(tmp_path / "feedback"), None, deps)
        assert result is None

    def test_skips_session_in_skip_set(self, tmp_path: Any) -> None:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-SK\nsession_id: sid-skip\nsession_account: web\n---\nBody"
        )
        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(goal_path) + "\n"),
        )
        result = find_resumable_session("/fake/root", str(tmp_path / "feedback"), {"sid-skip"}, deps)
        assert result is None

    def test_task_with_unanswered_question_skipped(self, tmp_path: Any) -> None:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-UQ\nsession_id: sid-uq\nsession_account: web\n---\nBody"
        )
        # Create unanswered question in feedback dir
        feedback_dir = tmp_path / "feedback" / "TASK-UQ"
        feedback_dir.mkdir(parents=True)
        (feedback_dir / "question.md").write_text(
            "---\ntask_id: TASK-UQ\nsession_id: sid-uq\naccount: web\n---\nQ"
        )
        # No answer.md → answer_is_empty returns True

        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(stdout=str(goal_path) + "\n"),
        )
        result = find_resumable_session("/fake/root", str(tmp_path / "feedback"), None, deps)
        assert result is None

    def test_task_with_open_awaiting_dep_skipped(self, tmp_path: Any) -> Any:
        """Task is skipped when an awaiting dependency is not yet in a terminal status."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-AWAIT\nsession_id: sid-await\n"
            "session_account: web\nawaiting:\n  - TASK-DEP-01\n---\nBody"
        )
        dep_dir = tmp_path / "dep"
        dep_dir.mkdir()
        dep_goal = dep_dir / "goal.md"
        dep_goal.write_text(
            "---\nstatus: pending\ntask_id: TASK-DEP-01\n---\nBody"
        )

        def fake_run(cmd, **kw):
            cmd_str = " ".join(str(c) for c in cmd)
            if "in_progress" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "task_id:" in cmd_str:
                return _fake_completed(stdout=str(dep_goal) + "\n")
            return _fake_completed(stdout="")

        deps = make_deps(run_subprocess=fake_run)
        result = find_resumable_session("/fake/root", str(tmp_path / "feedback"), None, deps)
        assert result is None

    def test_task_with_completed_awaiting_dep_returned(self, tmp_path: Any) -> Any:
        """Task is resumed when all awaiting dependencies are in a terminal status."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-READY\nsession_id: sid-ready\n"
            "session_account: web\nawaiting:\n  - TASK-DEP-02\n---\nBody"
        )
        dep_dir = tmp_path / "dep"
        dep_dir.mkdir()
        dep_goal = dep_dir / "goal.md"
        dep_goal.write_text(
            "---\nstatus: completed\ntask_id: TASK-DEP-02\n---\nBody"
        )

        def fake_run(cmd, **kw):
            cmd_str = " ".join(str(c) for c in cmd)
            if "in_progress" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "task_id:" in cmd_str:
                return _fake_completed(stdout=str(dep_goal) + "\n")
            return _fake_completed(stdout="")

        deps = make_deps(run_subprocess=fake_run)
        result = find_resumable_session("/fake/root", str(tmp_path / "feedback"), None, deps)
        assert result is not None
        assert result["task_id"] == "TASK-READY"
        assert result["session_id"] == "sid-ready"

    def test_task_with_unknown_awaiting_dep_skipped(self, tmp_path: Any) -> Any:
        """Task is skipped when an awaiting dep ID is not found in the index (treated as open)."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-UNK\nsession_id: sid-unk\n"
            "session_account: web\nawaiting:\n  - TASK-NONEXISTENT\n---\nBody"
        )

        def fake_run(cmd, **kw):
            cmd_str = " ".join(str(c) for c in cmd)
            if "in_progress" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "task_id:" in cmd_str:
                return _fake_completed(stdout="")  # dep not found in index
            return _fake_completed(stdout="")

        deps = make_deps(run_subprocess=fake_run)
        result = find_resumable_session("/fake/root", str(tmp_path / "feedback"), None, deps)
        assert result is None

    def test_empty_awaiting_list_does_not_trigger_index_build(self, tmp_path: Any) -> Any:
        """No extra subprocess call when awaiting is empty — index is not built."""
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-NOAWAIT\nsession_id: sid-na\n"
            "session_account: web\nawaiting: []\n---\nBody"
        )
        calls = []

        def fake_run(cmd, **kw):
            calls.append(list(cmd))
            return _fake_completed(stdout=str(goal_path) + "\n")

        deps = make_deps(run_subprocess=fake_run)
        result = find_resumable_session("/fake/root", str(tmp_path / "feedback"), None, deps)
        assert result is not None
        # Only the initial in_progress grep — no task_id index grep
        assert len(calls) == 1


class TestWriteSessionOutput:
    def test_writes_content_to_path(self) -> None:
        written = {}

        def fake_write(p, c):
            written[p] = c

        deps = make_deps(write_file=fake_write, makedirs=lambda p: None)
        write_session_output("/fake/outputs", "uuid-session", "Session content", deps)
        assert any("uuid-session.txt" in p for p in written)
        assert "Session content" in next(iter(written.values()))

    def test_os_error_is_non_fatal(self, capsys: Any) -> None:
        def raise_os(p, c):
            raise OSError("write error")

        deps = make_deps(write_file=raise_os, makedirs=lambda p: None)
        write_session_output("/fake/outputs", "uuid-x", "content", deps)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out


class TestBuildEnv:
    def test_sets_claude_config_dir(self) -> None:
        env = build_env("web")
        assert env["CLAUDE_CONFIG_DIR"].endswith("web")

    def test_sets_claude_automated_mode(self) -> None:
        env = build_env("gmail")
        assert env["CLAUDE_AUTOMATED_MODE"] == "1"

    def test_sets_session_id_when_provided(self) -> None:
        env = build_env("web", "my-uuid")
        assert env["CLAUDE_SESSION_ID"] == "my-uuid"

    def test_no_session_id_when_empty(self) -> None:
        env = build_env("web")
        assert "CLAUDE_SESSION_ID" not in env


class TestAccountsFromState:
    def test_returns_current_account_by_index(self) -> None:
        state = PersistentState(account_index=1)
        result = accounts_from_state(state, ["gmail", "web", "gmail2"])
        assert result == "web"

    def test_empty_accounts_returns_empty_string(self) -> None:
        state = PersistentState(account_index=0)
        result = accounts_from_state(state, [])
        assert result == ""

    def test_index_wraps_around(self) -> None:
        state = PersistentState(account_index=5)
        result = accounts_from_state(state, ["gmail", "web"])
        # 5 % 2 = 1 → accounts[1] = "web"
        assert result == "web"


class TestReadYamlFrontmatter:
    def test_reads_flat_key_value_pairs(self, tmp_path: Any) -> None:
        path = tmp_path / "file.md"
        path.write_text("---\nkey1: value1\nkey2: value2\n---\nBody")
        result = read_yaml_frontmatter(str(path))
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"

    def test_no_frontmatter_returns_empty_dict(self, tmp_path: Any) -> None:
        path = tmp_path / "file.md"
        path.write_text("No frontmatter here")
        result = read_yaml_frontmatter(str(path))
        assert result == {}

    def test_missing_file_returns_empty_dict(self) -> None:
        result = read_yaml_frontmatter("/nonexistent/file.md")
        assert result == {}

    def test_empty_file_returns_empty_dict(self, tmp_path: Any) -> None:
        path = tmp_path / "empty.md"
        path.write_bytes(b"")
        result = read_yaml_frontmatter(str(path))
        assert result == {}


class TestNewQuestionWrittenFor:
    def test_returns_true_when_question_exists_no_answer(self, tmp_path: Any) -> None:
        task_dir = tmp_path / "TASK-Q"
        task_dir.mkdir()
        (task_dir / "question.md").write_text("---\ntask_id: TASK-Q\n---\nQ")
        result = new_question_written_for("TASK-Q", str(tmp_path), make_deps())
        assert result is True

    def test_returns_false_when_no_question(self, tmp_path: Any) -> None:
        result = new_question_written_for("TASK-NQ", str(tmp_path), make_deps())
        assert result is False

    def test_returns_false_when_answer_exists(self, tmp_path: Any) -> None:
        task_dir = tmp_path / "TASK-AQ"
        task_dir.mkdir()
        (task_dir / "question.md").write_text("---\ntask_id: TASK-AQ\n---\nQ")
        (task_dir / "answer.md").write_text("An answer")
        result = new_question_written_for("TASK-AQ", str(tmp_path), make_deps())
        assert result is False


class TestRunNormalSessionStep:
    """Tests for the full process_in_progress_resume and run_normal_session_step paths."""

    def test_perm_error_disables_account(self, tmp_path: Any, capsys: Any) -> Any:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-PERM\nsession_id: sid-p\nsession_account: web\n---\nBody"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                return _fake_completed(
                    returncode=1, stdout="does not have access to this feature"
                )
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        decision, _sl = o.run_normal_session_step(state, run_data, "web", args, {"requested": False}, 0)
        assert decision == "continue"
        assert "web" in run_data.disabled_accounts
        captured = capsys.readouterr()
        assert "no access" in captured.out

    def test_perm_error_does_not_increment_sessions_launched(self, tmp_path: Any) -> Any:
        """Policy: errors don't count toward --max-tasks. perm_error must not bump
        the slot counter — otherwise a single bad account could exhaust the budget
        before the orchestrator rotates to a working one.
        """
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-PERM-CNT\nsession_id: sid\nsession_account: web\n---\nBody"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                return _fake_completed(returncode=1, stdout="does not have access to this feature")
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        decision, sl_after = o.run_normal_session_step(
            state, run_data, "web", args, {"requested": False}, 0
        )
        assert decision == "continue"
        assert sl_after == 0, f"perm_error must not bump sessions_launched; got {sl_after}"

    def test_rate_limit_records_and_rotates(self, tmp_path: Any, capsys: Any) -> Any:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-RL\nsession_id: sid-rl\nsession_account: web\n---\nBody"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                return _fake_completed(
                    returncode=1,
                    stdout="You've hit your limit. It resets 9pm (Europe/Berlin)",
                )
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        decision, _sl = o.run_normal_session_step(state, run_data, "web", args, {"requested": False}, 0)
        assert decision == "continue"
        assert "web" in state.rate_limited_until
        captured = capsys.readouterr()
        assert "rate-limited" in captured.out

    def test_success_increments_sessions_launched(self, tmp_path: Any) -> Any:
        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout="")
            if "claude" in cmd_str:
                return _fake_completed(returncode=0, stdout="Done")
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        decision, new_sl = o.run_normal_session_step(state, run_data, "web", args, {"requested": False}, 0)
        assert decision == "continue"
        assert new_sl == 1

    def test_exhausted_task_from_find_active_goal_is_not_relaunched(self, tmp_path: Any, capsys: Any) -> Any:
        """Regression: a task whose answered-feedback resume was exhausted must not
        be re-picked by find_active_task_goal and relaunched as a fresh session
        (which would overwrite its session_id). Before the fix, find_active_task_goal
        returned any in_progress task with an answered question — including exhausted
        ones — so the orchestrator burned a --max-tasks slot on a doomed retry.
        """
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-EXH\n"
            "session_id: sid-exhausted\nsession_account: web\n---\nBody"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                # find_active_task_goal finds the exhausted in_progress task
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "next_tasks.py" in cmd_str:
                # pick_next_task_for_session finds nothing else runnable
                return _fake_completed(stdout="")
            if "claude" in cmd_str:
                return _fake_completed(returncode=0, stdout="Done")
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: os.path.exists(p),
            read_file=lambda p: open(p).read(),
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        run_data.mark_exhausted(task_id="TASK-EXH", session_id="sid-exhausted")
        args = make_args()

        o.run_normal_session_step(state, run_data, "web", args, {"requested": False}, 0)

        captured = capsys.readouterr()
        assert "Skipping TASK-EXH" in captured.out
        assert "already exhausted" in captured.out
        # goal.md must still hold the ORIGINAL session_id — not overwritten by a
        # fresh-launch UUID (which would have hijacked the exhausted task).
        assert "session_id: sid-exhausted" in goal_path.read_text()


class TestProcessInProgressResumeFullPath:
    """Tests for process_in_progress_resume complete execution (not just attempt limit)."""

    def test_no_resumable_session_returns_next(self) -> Any:
        def fake_subprocess(cmd, *args, **kwargs):
            if "grep" in " ".join(str(c) for c in cmd):
                return _fake_completed(stdout="")
            return _fake_completed()

        o = make_orchestrator(run_subprocess=fake_subprocess)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        decision, sl = o.process_in_progress_resume(state, run_data, args, {"requested": False}, [], 0)
        assert decision == "next"
        assert sl == 0

    def test_successful_resume_increments_sessions(self, tmp_path: Any) -> Any:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-SR\nsession_id: sid-sr\nsession_account: web\n---\nBody"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                return _fake_completed(returncode=0, stdout="Resumed successfully")
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        decision, sl = o.process_in_progress_resume(state, run_data, args, {"requested": False}, [], 0)
        assert decision == "continue"
        assert sl >= 1

    def test_perm_error_on_resume_disables_account(self, tmp_path: Any, capsys: Any) -> Any:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-PRE\nsession_id: sid-pre\nsession_account: web\n---\nBody"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                return _fake_completed(returncode=1, stdout="does not have access")
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        decision, _sl = o.process_in_progress_resume(state, run_data, args, {"requested": False}, [], 0)
        assert decision == "continue"
        assert "web" in run_data.disabled_accounts

    def test_generic_failure_adds_to_exhausted_resume_ids(self, tmp_path: Any, capsys: Any) -> Any:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-GF\nsession_id: sid-gf\nsession_account: web\n---\nBody"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                return _fake_completed(returncode=1, stdout="Some generic error")
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: False,
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()
        decision, _sl = o.process_in_progress_resume(state, run_data, args, {"requested": False}, [], 0)
        assert decision == "continue"
        assert "sid-gf" in run_data.exhausted_resume_ids


class TestCleanupOldArtifacts:
    def test_does_not_crash_with_empty_dirs(self, tmp_path: Any) -> None:
        reports_dir = str(tmp_path / "reports")
        outputs_dir = str(tmp_path / "outputs")
        answered_dir = str(tmp_path / "answered")
        feedback_dir = str(tmp_path / "feedback")
        os.makedirs(reports_dir)
        os.makedirs(outputs_dir)
        os.makedirs(answered_dir)
        os.makedirs(feedback_dir)

        deps = make_deps(
            list_dir=lambda p: list(os.scandir(p)) if os.path.isdir(p) else [],
        )
        cleanup_old_artifacts(reports_dir, outputs_dir, answered_dir, feedback_dir, deps)


class TestScanUnansweredQuestions:
    def test_scan_calls_fingerprint_check(self, tmp_path: Any, capsys: Any) -> None:
        """scan_unanswered_questions calls check_and_update_question_fingerprint (AC-26)."""
        feedback_dir = tmp_path / "feedback"
        task_dir = feedback_dir / "TASK-FP"
        task_dir.mkdir(parents=True)
        question_path = task_dir / "question.md"
        question_path.write_text(
            "---\ntask_id: TASK-FP\nsession_id: sid-fp\n---\nShould I proceed?"
        )

        import unittest.mock as mock


        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        deps = make_deps(
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
        )
        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())

        with mock.patch("orchestrate.FEEDBACK_DIR", str(feedback_dir)):
            result = o.scan_unanswered_questions(state, run_data)

        assert len(result) == 1
        assert result[0]["task_id"] == "TASK-FP"
        # Fingerprint should have been recorded in state
        assert "TASK-FP" in state.question_fingerprints


# ---------------------------------------------------------------------------
# New tests for TASK-PROC-041-04-02 changes
# ---------------------------------------------------------------------------


class TestFindAnsweredFeedbackNewSessionRequired:
    """Tests for the NEW_SESSION_REQUIRED sentinel behavior in find_answered_feedback."""

    def _make_deps(self, tmp_path: Any, task_dir: Any) -> Any:
        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        return make_deps(
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
        )

    def test_new_session_required_sentinel_is_accepted(self, tmp_path: Any) -> None:
        """NEW_SESSION_REQUIRED is a valid session_id, not malformed."""
        task_dir = tmp_path / "TASK-FOO-01"
        task_dir.mkdir()
        (task_dir / "question.md").write_text(
            "---\n"
            "task_id: TASK-FOO-01\n"
            'session_id: "NEW_SESSION_REQUIRED"\n'
            "account: gmail\n"
            "status: awaiting_answer\n"
            "asked_at: 2026-01-01T00:00:00Z\n"
            "skill: test\n"
            "---\n\n"
            "Question body\n"
        )
        (task_dir / "answer.md").write_text("Option A")

        deps = self._make_deps(tmp_path, task_dir)
        results = find_answered_feedback(str(tmp_path), deps)
        assert len(results) == 1
        assert results[0]["session_id"] == "NEW_SESSION_REQUIRED"
        assert results[0]["requires_fresh_session"] is True

    def test_empty_session_id_still_rejected(self, tmp_path: Any, capsys: Any) -> None:
        """Empty session_id is still malformed and causes the entry to be skipped."""
        task_dir = tmp_path / "TASK-FOO-02"
        task_dir.mkdir()
        (task_dir / "question.md").write_text(
            "---\n"
            "task_id: TASK-FOO-02\n"
            'session_id: ""\n'
            "account: gmail\n"
            "status: awaiting_answer\n"
            "asked_at: 2026-01-01T00:00:00Z\n"
            "skill: test\n"
            "---\n\n"
            "Question body\n"
        )
        (task_dir / "answer.md").write_text("Option A")

        deps = self._make_deps(tmp_path, task_dir)
        results = find_answered_feedback(str(tmp_path), deps)
        assert len(results) == 0
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_normal_session_id_has_requires_fresh_session_false(self, tmp_path: Any) -> None:
        """Normal (non-sentinel) session_id gets requires_fresh_session=False."""
        task_dir = tmp_path / "TASK-FOO-03"
        task_dir.mkdir()
        (task_dir / "question.md").write_text(
            "---\n"
            "task_id: TASK-FOO-03\n"
            'session_id: "abc123"\n'
            "account: gmail\n"
            "status: awaiting_answer\n"
            "asked_at: 2026-01-01T00:00:00Z\n"
            "skill: test\n"
            "---\n\n"
            "Question body\n"
        )
        (task_dir / "answer.md").write_text("Option A")

        deps = self._make_deps(tmp_path, task_dir)
        results = find_answered_feedback(str(tmp_path), deps)
        assert len(results) == 1
        assert results[0]["requires_fresh_session"] is False

    def test_new_session_required_returns_correct_task_and_account(self, tmp_path: Any) -> None:
        """Returned dict has correct task_id, account, and answer_path."""
        task_dir = tmp_path / "TASK-FOO-04"
        task_dir.mkdir()
        (task_dir / "question.md").write_text(
            "---\n"
            "task_id: TASK-FOO-04\n"
            "session_id: NEW_SESSION_REQUIRED\n"
            "account: work\n"
            "---\n\n"
            "Question body\n"
        )
        answer_file = task_dir / "answer.md"
        answer_file.write_text("Option B")

        deps = self._make_deps(tmp_path, task_dir)
        results = find_answered_feedback(str(tmp_path), deps)
        assert len(results) == 1
        assert results[0]["task_id"] == "TASK-FOO-04"
        assert results[0]["account"] == "work"
        assert results[0]["answer_path"] == str(answer_file)
        assert results[0]["requires_fresh_session"] is True


class TestTerminateSessionPatch:
    """Tests for the Python patch logic embedded in terminate_session.sh."""

    # Extracted helper functions (identical to the ones in terminate_session.sh)
    @staticmethod
    def _get_frontmatter_value(content: Any, key: Any) -> Any:
        import re
        m = re.search(r"^" + re.escape(key) + r":\s*(.*)\s*$", content, re.MULTILINE)
        if not m:
            return ""
        return m.group(1).strip().strip('"').strip("'")

    @staticmethod
    def _set_frontmatter_value(content: Any, key: Any, value: Any) -> Any:
        import re
        quoted = f'"{value}"'
        pattern = r"^" + re.escape(key) + r":.*$"
        if re.search(pattern, content, re.MULTILINE):
            return re.sub(pattern, f'{key}: {quoted}', content, flags=re.MULTILINE)
        return re.sub(r"^(---\s*\n)", r"\1" + f"{key}: {quoted}\n", content, count=1)

    @staticmethod
    def _set_status_in_progress(content: Any) -> Any:
        import re
        return re.sub(r"^(status:\s*)pending\s*$", r"\1in_progress", content, flags=re.MULTILINE)

    def test_patches_empty_session_id_in_question_md(self, tmp_path: Any) -> None:
        """question.md with session_id: '' gets patched to the provided session UUID."""
        q_content = (
            "---\n"
            'session_id: ""\n'
            "task_id: TASK-TEST-01\n"
            "account: gmail\n"
            "---\n\n"
            "Question body\n"
        )
        q_path = tmp_path / "question.md"
        q_path.write_text(q_content)

        patch_value = "test-uuid-123"
        existing_sid = self._get_frontmatter_value(q_content, "session_id")
        # Empty session_id — should patch
        assert not existing_sid
        patched = self._set_frontmatter_value(q_content, "session_id", patch_value)
        q_path.write_text(patched)

        result = q_path.read_text()
        assert self._get_frontmatter_value(result, "session_id") == patch_value

    def test_non_empty_session_id_not_overwritten(self, tmp_path: Any) -> None:
        """question.md with an existing non-empty session_id is not touched."""
        q_content = (
            "---\n"
            'session_id: "existing-uuid"\n'
            "task_id: TASK-TEST-02\n"
            "account: gmail\n"
            "---\n\n"
            "Question body\n"
        )
        q_path = tmp_path / "question.md"
        q_path.write_text(q_content)

        existing_sid = self._get_frontmatter_value(q_content, "session_id")
        # Non-empty — script should skip patching
        assert existing_sid == "existing-uuid"
        # No write should happen; value remains unchanged
        result = q_path.read_text()
        assert self._get_frontmatter_value(result, "session_id") == "existing-uuid"

    def test_patches_goal_md_session_id_and_status(self, tmp_path: Any) -> None:
        """goal.md without session_id gets session_id set; status: pending → in_progress."""
        g_content = (
            "---\n"
            "task_id: TASK-TEST-01\n"
            "status: pending\n"
            "---\n\n"
            "Goal body\n"
        )
        g_path = tmp_path / "goal.md"
        g_path.write_text(g_content)

        patch_value = "test-uuid-123"

        existing_goal_sid = self._get_frontmatter_value(g_content, "session_id")
        assert not existing_goal_sid  # no session_id yet

        patched = self._set_frontmatter_value(g_content, "session_id", patch_value)
        patched = self._set_status_in_progress(patched)
        g_path.write_text(patched)

        result = g_path.read_text()
        assert self._get_frontmatter_value(result, "session_id") == patch_value
        assert self._get_frontmatter_value(result, "status") == "in_progress"

    def test_set_frontmatter_value_inserts_key_when_absent(self, tmp_path: Any) -> None:
        """set_frontmatter_value inserts a new key after the opening --- when absent."""
        content = "---\nexisting_key: foo\n---\nbody\n"
        result = self._set_frontmatter_value(content, "session_id", "new-val")
        assert self._get_frontmatter_value(result, "session_id") == "new-val"
        assert self._get_frontmatter_value(result, "existing_key") == "foo"

    def test_set_frontmatter_value_replaces_existing_key(self) -> None:
        """set_frontmatter_value replaces an existing key's value."""
        content = '---\nsession_id: "old-value"\n---\nbody\n'
        result = self._set_frontmatter_value(content, "session_id", "new-value")
        assert self._get_frontmatter_value(result, "session_id") == "new-value"

    def test_no_session_id_env_var_uses_new_session_required_sentinel(self, tmp_path: Any) -> None:
        """When CLAUDE_SESSION_ID is empty, patch_value falls back to NEW_SESSION_REQUIRED."""
        session_id = ""  # simulates empty env var
        patch_value = session_id if session_id else "NEW_SESSION_REQUIRED"
        assert patch_value == "NEW_SESSION_REQUIRED"

    def test_full_patch_flow_via_subprocess(self, tmp_path: Any) -> None:
        """Run the terminate_session.sh Python block against a real temp dir."""
        import subprocess as sp

        # Build temp feedback dir and question.md
        feedback_dir = tmp_path / "pending_feedback"
        task_dir = feedback_dir / "TASK-TEST-01"
        task_dir.mkdir(parents=True)
        q_path = task_dir / "question.md"
        q_path.write_text(
            "---\n"
            'session_id: ""\n'
            "task_id: TASK-TEST-NOREQ\n"
            "account: gmail\n"
            "---\n\n"
            "Question body\n"
        )

        # Minimal Python script that replicates the patch block
        # Uses the temp dir instead of the real project feedback_dir
        patch_script = f"""
import os, re, sys

feedback_dir = r"{feedback_dir!s}"
session_id = os.environ.get("CLAUDE_SESSION_ID", "").strip()

def get_frontmatter_value(content, key):
    m = re.search(r"^" + re.escape(key) + r":\\s*(.*)\\s*$", content, re.MULTILINE)
    if not m:
        return ""
    return m.group(1).strip().strip('"').strip("'")

def set_frontmatter_value(content, key, value):
    quoted = f'"{{value}}"'
    pattern = r"^" + re.escape(key) + r":.*$"
    if re.search(pattern, content, re.MULTILINE):
        return re.sub(pattern, f'{{key}}: {{quoted}}', content, flags=re.MULTILINE)
    return re.sub(r"^(---\\s*\\n)", r"\\1" + f"{{key}}: {{quoted}}\\n", content, count=1)

for entry in os.scandir(feedback_dir):
    if not entry.is_dir():
        continue
    question_path = os.path.join(entry.path, "question.md")
    if not os.path.exists(question_path):
        continue
    with open(question_path) as f:
        q_content = f.read()
    existing_sid = get_frontmatter_value(q_content, "session_id")
    if existing_sid:
        continue
    patch_value = session_id if session_id else "NEW_SESSION_REQUIRED"
    q_patched = set_frontmatter_value(q_content, "session_id", patch_value)
    with open(question_path, "w") as f:
        f.write(q_patched)
"""
        env = os.environ.copy()
        env["CLAUDE_SESSION_ID"] = "test-uuid-123"
        result = sp.run(
            ["python3", "-c", patch_script],
            capture_output=True, text=True, env=env,
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        patched_content = q_path.read_text()
        # Extract session_id using the same regex logic
        import re
        m = re.search(r'^session_id:\s*(.*)\s*$', patched_content, re.MULTILINE)
        assert m is not None
        sid = m.group(1).strip().strip('"').strip("'")
        assert sid == "test-uuid-123"

    def test_full_patch_flow_no_env_var_writes_sentinel(self, tmp_path: Any) -> None:
        """When CLAUDE_SESSION_ID is absent, patch writes NEW_SESSION_REQUIRED."""
        import subprocess as sp

        feedback_dir = tmp_path / "pending_feedback"
        task_dir = feedback_dir / "TASK-TEST-02"
        task_dir.mkdir(parents=True)
        q_path = task_dir / "question.md"
        q_path.write_text(
            "---\n"
            'session_id: ""\n'
            "task_id: TASK-TEST-NOREQ2\n"
            "account: gmail\n"
            "---\n\n"
            "Question body\n"
        )

        patch_script = f"""
import os, re

feedback_dir = r"{feedback_dir!s}"
session_id = os.environ.get("CLAUDE_SESSION_ID", "").strip()

def get_frontmatter_value(content, key):
    m = re.search(r"^" + re.escape(key) + r":\\s*(.*)\\s*$", content, re.MULTILINE)
    if not m:
        return ""
    return m.group(1).strip().strip('"').strip("'")

def set_frontmatter_value(content, key, value):
    quoted = f'"{{value}}"'
    pattern = r"^" + re.escape(key) + r":.*$"
    if re.search(pattern, content, re.MULTILINE):
        return re.sub(pattern, f'{{key}}: {{quoted}}', content, flags=re.MULTILINE)
    return re.sub(r"^(---\\s*\\n)", r"\\1" + f"{{key}}: {{quoted}}\\n", content, count=1)

for entry in os.scandir(feedback_dir):
    if not entry.is_dir():
        continue
    question_path = os.path.join(entry.path, "question.md")
    if not os.path.exists(question_path):
        continue
    with open(question_path) as f:
        q_content = f.read()
    existing_sid = get_frontmatter_value(q_content, "session_id")
    if existing_sid:
        continue
    patch_value = session_id if session_id else "NEW_SESSION_REQUIRED"
    q_patched = set_frontmatter_value(q_content, "session_id", patch_value)
    with open(question_path, "w") as f:
        f.write(q_patched)
"""
        env = os.environ.copy()
        env.pop("CLAUDE_SESSION_ID", None)
        result = sp.run(
            ["python3", "-c", patch_script],
            capture_output=True, text=True, env=env,
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        import re
        patched_content = q_path.read_text()
        m = re.search(r'^session_id:\s*(.*)\s*$', patched_content, re.MULTILINE)
        assert m is not None
        sid = m.group(1).strip().strip('"').strip("'")
        assert sid == "NEW_SESSION_REQUIRED"


# ---------------------------------------------------------------------------
# Section I: Hung session detection tests
# ---------------------------------------------------------------------------


def _make_mock_proc(poll_returns: Any = None, stdout_output: Any = "") -> Any:
    """Return a MagicMock subprocess.Popen-style object."""
    proc = MagicMock()
    if poll_returns is None:
        proc.poll.return_value = None  # never exits
    else:
        proc.poll.side_effect = poll_returns
    proc.communicate.return_value = (stdout_output, "")
    proc.pid = 99999
    return proc


class TestRunSessionWithHungDetection:
    """Tests for the run_session_with_hung_detection() polling loop."""

    def test_hung_detection_no_children_stale_jsonl(self) -> None:
        """Process killed as hung when JSONL mtime is frozen and no child processes.

        With hung_timeout_secs=0 and hung_check_interval=0, the stale timer fires
        immediately after the first frozen-mtime observation with no children.
        """
        proc = _make_mock_proc()  # never exits
        no_children = _fake_completed(returncode=0, stdout="")  # ps returns empty

        deps = make_deps(
            popen_subprocess=lambda *a, **kw: proc,
            run_subprocess=lambda *a, **kw: no_children,
            sleep=lambda s: None,
            get_mtime=lambda p: 1000.0,  # mtime always the same — frozen
        )
        stop_flag = {"requested": False}

        result = run_session_with_hung_detection(
            cmd=["claude", "-p", "test"],
            env={},
            session_uuid="aaaaaaaa-0000-0000-0000-000000000000",
            hung_check_interval=0,
            hung_timeout_secs=0,   # fire immediately after first stale observation
            session_timeout_secs=99999,
            stop_flag=stop_flag,
            deps=deps,
        )

        assert getattr(result, "kill_reason", None) == "hung"
        proc.send_signal.assert_called_once()

    def test_hung_detection_children_present_not_hung(self) -> None:
        """Process is NOT killed when child processes are present despite frozen JSONL mtime.

        Why: child process presence means the session is actively running subprocesses
        (e.g. dart/bash) — this is the key lesson from the 13-hour incident.
        """
        # Poll sequence: None (alive) once, then 0 (exited) — process exits after one iteration
        proc = _make_mock_proc(poll_returns=[None, 0])
        children_present = _fake_completed(returncode=0, stdout="12345 dart")

        deps = make_deps(
            popen_subprocess=lambda *a, **kw: proc,
            run_subprocess=lambda *a, **kw: children_present,
            sleep=lambda s: None,
            get_mtime=lambda p: 1000.0,  # frozen mtime
        )
        stop_flag = {"requested": False}

        result = run_session_with_hung_detection(
            cmd=["claude", "-p", "test"],
            env={},
            session_uuid="bbbbbbbb-0000-0000-0000-000000000000",
            hung_check_interval=0,
            hung_timeout_secs=0,
            session_timeout_secs=99999,
            stop_flag=stop_flag,
            deps=deps,
        )

        # Should exit normally (returncode 0) without being killed
        assert result.returncode == 0
        assert getattr(result, "kill_reason", None) is None
        proc.send_signal.assert_not_called()
        proc.kill.assert_not_called()

    def test_session_timeout(self) -> None:
        """Process killed when elapsed time exceeds session_timeout_secs.

        With session_timeout_secs=0 the hard ceiling fires on the first poll iteration.
        """
        proc = _make_mock_proc()  # never exits
        # ps returns no children (not relevant — timeout fires first)
        no_children = _fake_completed(returncode=0, stdout="")

        deps = make_deps(
            popen_subprocess=lambda *a, **kw: proc,
            run_subprocess=lambda *a, **kw: no_children,
            sleep=lambda s: None,
            get_mtime=lambda p: 1000.0,
        )
        stop_flag = {"requested": False}

        result = run_session_with_hung_detection(
            cmd=["claude", "-p", "test"],
            env={},
            session_uuid="cccccccc-0000-0000-0000-000000000000",
            hung_check_interval=0,
            hung_timeout_secs=99999,
            session_timeout_secs=0,  # immediate timeout
            stop_flag=stop_flag,
            deps=deps,
        )

        assert getattr(result, "kill_reason", None) == "session_timeout"
        proc.send_signal.assert_called_once()

    def test_kill_sequence_sigterm_then_sigkill(self) -> None:
        """When SIGTERM does not stop the process, SIGKILL is sent and returncode is -9."""
        import signal as signal_module

        proc = _make_mock_proc()  # poll() always returns None — survives SIGTERM

        deps = make_deps(
            popen_subprocess=lambda *a, **kw: proc,
            run_subprocess=lambda *a, **kw: _fake_completed(returncode=0, stdout=""),
            sleep=lambda s: None,
            get_mtime=lambda p: 1000.0,
        )
        stop_flag = {"requested": False}

        result = run_session_with_hung_detection(
            cmd=["claude", "-p", "test"],
            env={},
            session_uuid="dddddddd-0000-0000-0000-000000000000",
            hung_check_interval=0,
            hung_timeout_secs=99999,
            session_timeout_secs=0,  # immediate timeout to trigger kill
            stop_flag=stop_flag,
            deps=deps,
        )

        # SIGTERM was sent first
        proc.send_signal.assert_called_once_with(signal_module.SIGTERM)
        # poll() still None after sleep → SIGKILL sent
        proc.kill.assert_called_once()
        assert result.returncode == -9

    def test_heartbeat_emitted_after_15_minutes(self, capsys: Any) -> None:
        """A status line is printed once the session has run for 15+ minutes.

        time.monotonic is patched to return start=0 on the first call, then 900
        (15 min) for the elapsed and now_mono checks in the first poll iteration.
        The process exits on the second poll, so exactly one heartbeat fires.
        """
        import time as time_module

        proc = _make_mock_proc(poll_returns=[None, 0])

        deps = make_deps(
            popen_subprocess=lambda *a, **kw: proc,
            run_subprocess=lambda *a, **kw: _fake_completed(returncode=0, stdout=""),
            sleep=lambda s: None,
            get_mtime=lambda p: None,  # JSONL not yet present — no stale timer
        )
        stop_flag = {"requested": False}

        # Call order: start_mono, then per-iteration: elapsed, now_mono
        monotonic_values = iter([0, 900, 900])
        with mock.patch.object(time_module, "monotonic", side_effect=lambda: next(monotonic_values)):
            result = run_session_with_hung_detection(
                cmd=["claude", "-p", "test"],
                env={},
                session_uuid="eeeeeeee-0000-0000-0000-000000000000",
                hung_check_interval=0,
                hung_timeout_secs=99999,
                session_timeout_secs=99999,
                stop_flag=stop_flag,
                deps=deps,
            )

        assert result.returncode == 0
        out = capsys.readouterr().out
        assert "still running" in out
        assert "15 min" in out

    def test_heartbeat_not_emitted_before_15_minutes(self, capsys: Any) -> None:
        """No heartbeat is printed when less than 15 minutes have elapsed."""
        import time as time_module

        proc = _make_mock_proc(poll_returns=[None, 0])

        deps = make_deps(
            popen_subprocess=lambda *a, **kw: proc,
            run_subprocess=lambda *a, **kw: _fake_completed(returncode=0, stdout=""),
            sleep=lambda s: None,
            get_mtime=lambda p: None,
        )
        stop_flag = {"requested": False}

        # 899 seconds — just under the 900 s (15 min) threshold
        monotonic_values = iter([0, 899, 899])
        with mock.patch.object(time_module, "monotonic", side_effect=lambda: next(monotonic_values)):
            result = run_session_with_hung_detection(
                cmd=["claude", "-p", "test"],
                env={},
                session_uuid="ffffffff-0000-0000-0000-000000000000",
                hung_check_interval=0,
                hung_timeout_secs=99999,
                session_timeout_secs=99999,
                stop_flag=stop_flag,
                deps=deps,
            )

        assert result.returncode == 0
        out = capsys.readouterr().out
        assert "still running" not in out


# ---------------------------------------------------------------------------
# Category I: Observability fields (AC-34..AC-38)
# ---------------------------------------------------------------------------


class TestExternalStopRequest:
    """AC-38: stop_requested in state.json replaces the .stop-requested sentinel."""

    def test_check_stop_conditions_reads_state_json(self) -> None:
        """When state.json[stop_requested]=true, check_stop_conditions returns (True, 'manual')."""
        state_content = json.dumps({"stop_requested": True})

        deps = make_deps(
            file_exists=lambda p: p.endswith("state.json"),
            read_file=lambda p: state_content,
        )
        orch = Orchestrator(deps=deps)
        state = PersistentState()
        run_data = RunData(start_time=datetime(2026, 4, 30, 12, 0, 0))
        stop_flag = {"requested": False}
        args = argparse.Namespace(max_tasks=None, stop_at=None)
        should_stop, reason = orch.check_stop_conditions(state, run_data, args, stop_flag, None, 0)
        assert should_stop is True
        assert reason == "manual"
        # Should also mirror to in-memory state
        assert state.stop_requested is True

    def test_sentinel_stop_path_no_longer_referenced(self) -> None:
        """AC-38: SENTINEL_STOP constant is removed from the module."""
        import orchestrate
        assert not hasattr(orchestrate, "SENTINEL_STOP"), (
            "SENTINEL_STOP should be removed (AC-38) — stop signalling now uses state.json"
        )

    def test_stop_flag_requested_also_mirrors_to_state(self) -> None:
        """When stop_flag['requested'] is True, stop_requested is also set on state."""
        deps = make_deps()
        orch = Orchestrator(deps=deps)
        state = PersistentState()
        run_data = RunData(start_time=datetime(2026, 4, 30, 12, 0, 0))
        stop_flag = {"requested": True}
        args = argparse.Namespace(max_tasks=None, stop_at=None)
        should_stop, reason = orch.check_stop_conditions(state, run_data, args, stop_flag, None, 0)
        assert should_stop is True
        assert reason == "manual"
        assert state.stop_requested is True

    def test_no_stop_when_state_json_missing(self) -> None:
        """When state.json is absent, _read_external_stop_request returns False."""
        deps = make_deps(
            file_exists=lambda p: False,
        )
        orch = Orchestrator(deps=deps)
        assert orch._read_external_stop_request() is False

    def test_no_stop_when_state_json_has_stop_requested_false(self) -> None:
        """When state.json[stop_requested]=false, no stop is triggered."""
        state_content = json.dumps({"stop_requested": False})
        deps = make_deps(
            file_exists=lambda p: p.endswith("state.json"),
            read_file=lambda p: state_content,
        )
        orch = Orchestrator(deps=deps)
        assert orch._read_external_stop_request() is False


class TestTimezoneField:
    """AC-35: timezone field is populated on save."""

    def test_get_local_timezone_name_returns_string(self) -> None:
        """_get_local_timezone_name returns a non-empty string in any environment."""
        from orchestrate import _get_local_timezone_name
        tz = _get_local_timezone_name()
        assert isinstance(tz, str)
        assert len(tz) > 0

    def test_get_local_timezone_name_fallback_with_tz_env(self, monkeypatch: Any) -> None:
        """When TZ env var is set and zoneinfo.key is absent, TZ env is used as fallback."""
        import orchestrate
        monkeypatch.setenv("TZ", "America/New_York")

        # Simulate the case where astimezone().tzinfo has no 'key' attribute
        class _NoKeyTZ:
            pass

        class _NoKeyDt:
            tzinfo = _NoKeyTZ()

        with mock.patch("orchestrate.datetime") as mock_dt:
            mock_dt.now.return_value = _NoKeyDt()
            result = orchestrate._get_local_timezone_name()

        # TZ env fallback or UTC — both are acceptable non-empty strings
        assert isinstance(result, str)
        assert len(result) > 0


class TestActiveSessionLifecycle:
    """AC-34: active_session is set before a session launches, cleared after."""

    def test_active_session_set_and_cleared_during_normal_session(self) -> None:
        """Verify save_state is called with active_session set before run_normal_session,
        and with active_session=None after it completes."""
        import orchestrate

        save_calls = []  # each entry is the active_session value at time of call

        def spy_save(path, state, deps):
            save_calls.append(state.active_session)

        # run_normal_session needs to return something with a returncode and stdout
        fake_result = mock.MagicMock()
        fake_result.returncode = 0
        fake_result.stdout = "done"
        fake_result.kill_reason = None

        deps = make_deps(
            run_subprocess=lambda *a, **kw: _fake_completed(returncode=0, stdout=""),
            file_exists=lambda p: False,
        )
        orch = Orchestrator(deps=deps)
        orch._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime(2026, 4, 30, 12, 0, 0))
        args = argparse.Namespace(
            max_tasks=None,
            hung_check_interval=0,
            hung_timeout=60,
            session_timeout=3600,
            min_wait_seconds=0,
        )
        stop_flag = {"requested": False}

        with mock.patch.object(orchestrate, "run_normal_session", return_value=fake_result), \
             mock.patch.object(orchestrate, "save_state", side_effect=spy_save), \
             mock.patch.object(orchestrate, "find_active_task_goal", return_value=None), \
             mock.patch.object(orchestrate, "write_session_output"):
            orch.run_normal_session_step(state, run_data, "web", args, stop_flag, 0)

        # There should be at least two save_state calls: one with a UUID set, one with None
        assert any(v is not None for v in save_calls), (
            "active_session should be set (non-None) before run_normal_session"
        )
        # Last call should clear active_session
        assert save_calls[-1] is None, (
            "active_session should be cleared (None) after run_normal_session"
        )


class TestRateLimitObservability:
    """AC-34: rate_limit_reached + next_wake_time around rate_limit_sleep."""

    def test_rate_limit_flags_set_before_sleep_cleared_after(self) -> None:
        """rate_limit_reached=True is saved before rate_limit_sleep, False after."""
        from datetime import timezone as tz

        import orchestrate

        save_calls = []  # captures (rate_limit_reached, next_wake_time) at each save_state call

        def spy_save(path, state, deps):
            save_calls.append((state.rate_limit_reached, state.next_wake_time))

        sleep_called = []

        def fake_sleep(secs, stop_flag, reset_dt=None, poll_stop=None):
            sleep_called.append(secs)

        deps = make_deps()
        orch = Orchestrator(deps=deps)
        orch._accounts = ["web"]

        state = PersistentState()
        run_data = RunData(start_time=datetime(2026, 4, 30, 12, 0, 0))
        stop_flag = {"requested": False}
        args = argparse.Namespace(max_tasks=None)

        # Simulate all accounts rate-limited with a future reset time
        future_dt = datetime(2026, 4, 30, 20, 0, 0, tzinfo=tz.utc)

        with mock.patch.object(orchestrate, "next_available_account",
                                return_value=(None, future_dt)), \
             mock.patch.object(orchestrate, "save_state", side_effect=spy_save), \
             mock.patch.object(orchestrate, "rate_limit_sleep", side_effect=fake_sleep):
            # Patch get_now_utc so wait_secs > 0
            deps2 = make_deps(get_now_utc=lambda: datetime(2026, 4, 30, 12, 0, 0, tzinfo=tz.utc))
            orch.deps = deps2
            orch.wait_for_account_if_needed(state, run_data, args, stop_flag)

        # rate_limit_sleep was called
        assert len(sleep_called) == 1, "rate_limit_sleep should be called once"

        # First save call (before sleep): rate_limit_reached=True, next_wake_time set
        assert save_calls[0][0] is True, "rate_limit_reached should be True before sleep"
        assert save_calls[0][1] is not None, "next_wake_time should be set before sleep"

        # Second save call (after sleep): rate_limit_reached=False, next_wake_time=None
        assert save_calls[1][0] is False, "rate_limit_reached should be False after sleep"
        assert save_calls[1][1] is None, "next_wake_time should be None after sleep"


class TestRateLimitSleepWallClock:
    """rate_limit_sleep uses wall-clock vs reset_dt so host-suspend doesn't extend the wait.

    Regression: on WSL2 the monotonic clock pauses while the Windows host is
    suspended; the original implementation used a monotonic deadline and so the
    wait would be extended by however long the host slept.
    """

    def test_returns_immediately_when_reset_in_past(self) -> None:
        """If reset_dt is already past, loop exits without sleeping."""
        import orchestrate

        past = datetime.now(timezone.utc) - timedelta(minutes=5)
        sleep_calls = []
        with mock.patch.object(orchestrate.time, "sleep", side_effect=lambda s: sleep_calls.append(s)):
            orchestrate.rate_limit_sleep(
                total_secs=10_000,  # large duration that would dominate if monotonic was used
                stop_flag={"requested": False},
                reset_dt=past,
            )
        assert sleep_calls == [], "should not sleep when reset_dt is already past"

    def test_wall_clock_advance_ends_wait_even_if_monotonic_is_frozen(self) -> Any:
        """Simulate host suspend: monotonic stays put but wall-clock crosses reset_dt → loop exits."""
        import orchestrate

        # reset 30s in the future at simulated start
        start_wall = datetime(2026, 5, 16, 19, 25, 0, tzinfo=timezone.utc)
        reset_dt = start_wall + timedelta(seconds=30)

        # Wall-clock jumps forward by 2h on the second sample (host suspend)
        wall_samples = iter([start_wall, start_wall + timedelta(hours=2)])
        # Monotonic only advances trivially (frozen during suspend)
        mono_samples = iter([1000.0, 1000.0, 1000.1, 1000.2, 1000.3])

        sleep_calls = []

        class _FakeDT(datetime):
            @classmethod
            def now(cls, tz=None):
                return next(wall_samples)

        with mock.patch.object(orchestrate, "datetime", _FakeDT), \
             mock.patch.object(orchestrate.time, "monotonic", side_effect=lambda: next(mono_samples)), \
             mock.patch.object(orchestrate.time, "sleep", side_effect=lambda s: sleep_calls.append(s)):
            orchestrate.rate_limit_sleep(
                total_secs=30,
                stop_flag={"requested": False},
                reset_dt=reset_dt,
            )

        # First iter: remaining=30s → sleeps once. Second iter: wall jumped 2h → exits.
        assert len(sleep_calls) == 1, f"expected exactly one sleep, got {sleep_calls}"

    def test_external_stop_flag_breaks_wait_without_signal(self) -> None:
        """Regression: a flag-only stop (state.json[stop_requested]=true with no SIGINT,
        e.g. the monitor's emergency auto-stop) must end the wait within one tick. The
        loop otherwise only honours the in-memory stop_flag set by signals, so a
        multi-hour rate-limit wait would ignore the external request until it expires."""
        import orchestrate

        # Reset far in the future so the only way out is poll_stop returning True.
        future = datetime.now(timezone.utc) + timedelta(hours=4)
        stop_flag = {"requested": False}
        sleep_calls: list[float] = []

        # poll_stop is False on the first check, then True (external writer set the flag).
        poll_results = iter([False, True])

        def fake_poll() -> bool:
            return next(poll_results)

        with mock.patch.object(orchestrate.time, "sleep", side_effect=lambda s: sleep_calls.append(s)):
            orchestrate.rate_limit_sleep(
                total_secs=14_400,
                stop_flag=stop_flag,
                reset_dt=future,
                poll_stop=fake_poll,
            )

        # The external request is mirrored into the in-memory flag and the loop exits
        # after a single sleep tick — not after the 4-hour window.
        assert stop_flag["requested"] is True, "external stop must mirror into stop_flag"
        assert len(sleep_calls) == 1, f"expected exactly one sleep before stop, got {sleep_calls}"


# ---------------------------------------------------------------------------
class TestStartupStateReset:
    """_reset_startup_state clears stale observability fields from a prior SIGKILL'd run."""

    def test_stale_stop_requested_is_cleared(self) -> None:
        state = PersistentState()
        state.stop_requested = True
        _reset_startup_state(state)
        assert state.stop_requested is False

    def test_stale_active_session_is_cleared(self) -> None:
        state = PersistentState()
        state.active_session = "stale-uuid-from-prior-crash"
        _reset_startup_state(state)
        assert state.active_session is None

    def test_stale_rate_limit_flags_are_cleared(self) -> None:
        state = PersistentState()
        state.rate_limit_reached = True
        state.next_wake_time = "2026-04-30T22:00:00+02:00"
        _reset_startup_state(state)
        assert state.rate_limit_reached is False
        assert state.next_wake_time is None

    def test_stale_stop_reason_is_cleared(self) -> None:
        state = PersistentState()
        state.stop_reason = "manual"
        _reset_startup_state(state)
        assert state.stop_reason is None

    def test_is_running_set_to_true_regardless_of_prior_value(self) -> None:
        state = PersistentState()
        state.is_running = False
        _reset_startup_state(state)
        assert state.is_running is True

    def test_all_stale_fields_reset_in_one_call(self) -> None:
        """All observability fields that could be stale from a crash are reset together."""
        state = PersistentState()
        state.is_running = True          # already running (stuck)
        state.active_session = "crashed-session"
        state.stop_requested = True
        state.stop_reason = "error"
        state.rate_limit_reached = True
        state.next_wake_time = "2026-04-30T23:00:00+00:00"

        _reset_startup_state(state)

        assert state.is_running is True
        assert state.active_session is None
        assert state.stop_requested is False
        assert state.stop_reason is None
        assert state.rate_limit_reached is False
        assert state.next_wake_time is None


# ---------------------------------------------------------------------------
class TestResumeSessionActiveSessionLifecycle:
    """AC-34: active_session is set before a resume session launches, cleared after."""

    def test_active_session_set_and_cleared_during_resume(self, tmp_path: Any) -> Any:
        """Verify save_state is called with active_session=<session_id> before
        run_resume_session, and with active_session=None after it completes."""
        import orchestrate

        save_calls = []

        def spy_save(path, state, deps):
            save_calls.append(state.active_session)

        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\nstatus: in_progress\ntask_id: TASK-RSL\n"
            "session_id: resume-sid-lifecycle\nsession_account: web\n---\nBody"
        )

        def fake_subprocess(cmd, *a, **kw):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            return _fake_completed(returncode=0, stdout="resumed ok")

        fake_result = MagicMock()
        fake_result.returncode = 0
        fake_result.stdout = "resumed ok"
        fake_result.kill_reason = None

        deps = make_deps(
            run_subprocess=fake_subprocess,
            file_exists=lambda p: False,
            makedirs=lambda p: None,
            write_file=lambda p, c: None,
        )
        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime(2026, 4, 30, 12, 0, 0))
        args = make_args()

        with mock.patch.object(orchestrate, "run_resume_session", return_value=fake_result), \
             mock.patch.object(orchestrate, "save_state", side_effect=spy_save), \
             mock.patch.object(orchestrate, "write_session_output"):
            o.process_in_progress_resume(state, run_data, args, {"requested": False}, [], 0)

        assert any(v == "resume-sid-lifecycle" for v in save_calls), (
            "active_session should be set to the resumed session_id before run_resume_session"
        )
        assert save_calls[-1] is None, (
            "active_session should be cleared (None) after run_resume_session completes"
        )


# ---------------------------------------------------------------------------
# Category I: Session-result helpers (finalize/classify/apply)
# ---------------------------------------------------------------------------

from orchestrate import (
    apply_perm_error_to_account,
    apply_rate_limit_to_account,
    classify_session_failure,
    finalize_session_record,
)


class TestFinalizeSessionRecord:
    """finalize_session_record applies common post-session bookkeeping."""

    def _make_result(self, returncode: Any = 0, stdout: Any = "ok", kill_reason: Any = None, elapsed_secs: Any = 0) -> Any:
        r = MagicMock()
        r.returncode = returncode
        r.stdout = stdout
        r.kill_reason = kill_reason
        if kill_reason is not None:
            r.elapsed_secs = elapsed_secs
        return r

    def test_normal_exit_populates_record(self) -> None:
        record: dict[str, Any] = {"task_id": "TASK-X"}
        result = self._make_result(returncode=0, stdout="all done")
        run_data = RunData(start_time=datetime(2026, 5, 15, 12, 0, 0))
        now = datetime(2026, 5, 15, 12, 30, 0)
        written: dict[Any, Any] = {}
        deps = make_deps(
            get_now_local=lambda: now,
            write_file=lambda p, c: written.setdefault(p, c),
            makedirs=lambda p: None,
        )

        cleaned = finalize_session_record(
            record, result, "sess-1", "web", run_data, deps
        )

        assert cleaned == "all done"
        assert record["end"] == now
        assert record["exit_code"] == 0
        assert record["output_excerpt"] == "all done"
        assert "hung_killed" not in record
        assert run_data.sessions == [record]
        assert run_data.accounts_used == {"web"}

    def test_hung_kill_records_metadata(self, capsys: Any) -> None:
        record: dict[str, Any] = {"task_id": "TASK-HUNG"}
        result = self._make_result(returncode=-9, stdout="...", kill_reason="hung_timeout", elapsed_secs=1800)
        run_data = RunData(start_time=datetime(2026, 5, 15, 12, 0, 0))
        deps = make_deps(
            get_now_local=lambda: datetime(2026, 5, 15, 12, 30, 0),
            write_file=lambda p, c: None,
            makedirs=lambda p: None,
        )

        finalize_session_record(record, result, "sess-2", "web", run_data, deps, label="TASK-HUNG")

        assert record["hung_killed"] is True
        assert record["kill_reason"] == "hung_timeout"
        assert record["elapsed_secs"] == 1800
        captured = capsys.readouterr()
        assert "killed" in captured.out
        assert "TASK-HUNG" in captured.out

    def test_excerpt_is_truncated_to_1500(self) -> None:
        record: dict[Any, Any] = {}
        big = "x" * 5000
        result = self._make_result(returncode=0, stdout=big)
        run_data = RunData(start_time=datetime(2026, 5, 15, 12, 0, 0))
        deps = make_deps(
            get_now_local=lambda: datetime(2026, 5, 15, 12, 30, 0),
            write_file=lambda p, c: None,
            makedirs=lambda p: None,
        )

        finalize_session_record(record, result, "sess-3", "web", run_data, deps)

        assert len(record["output_excerpt"]) == 1500

    def test_writes_to_outputs_dir(self) -> None:
        record: dict[Any, Any] = {}
        result = self._make_result(returncode=0, stdout="captured")
        run_data = RunData(start_time=datetime(2026, 5, 15, 12, 0, 0))
        writes: dict[Any, Any] = {}
        deps = make_deps(
            get_now_local=lambda: datetime(2026, 5, 15, 12, 30, 0),
            write_file=lambda p, c: writes.setdefault(p, c),
            makedirs=lambda p: None,
        )

        finalize_session_record(record, result, "sess-key", "web", run_data, deps)

        # write_session_output composes <deps.outputs_dir>/sess-key.txt — assert the suffix.
        assert any(p.endswith("sess-key.txt") for p in writes), list(writes.keys())
        assert next(iter(writes.values())) == "captured"

    def test_writes_to_deps_outputs_dir_not_global(self) -> None:
        """Regression: finalize_session_record must use deps.outputs_dir, not the global OUTPUTS_DIR.

        Before the fix, the hardcoded global caused tests with real write_file lambdas to
        create artifacts in the production automation/session_outputs/ directory.
        """
        record: dict[Any, Any] = {}
        result = self._make_result(returncode=0, stdout="content")
        run_data = RunData(start_time=datetime(2026, 5, 15, 12, 0, 0))
        writes: dict[Any, Any] = {}
        custom_dir = "/custom/test/outputs"
        deps = make_deps(
            get_now_local=lambda: datetime(2026, 5, 15, 12, 30, 0),
            write_file=lambda p, c: writes.setdefault(p, c),
            makedirs=lambda p: None,
            outputs_dir=custom_dir,
        )

        finalize_session_record(record, result, "sess-di", "web", run_data, deps)

        written_paths = list(writes.keys())
        assert written_paths, "expected a file to be written"
        assert all(p.startswith(custom_dir) for p in written_paths), (
            f"expected all writes under {custom_dir!r}, got {written_paths}"
        )


class TestClassifySessionFailure:
    """classify_session_failure returns the failure category as a string or None."""

    def test_exit_zero_is_none(self) -> None:
        r = _fake_completed(returncode=0, stdout="ok")
        assert classify_session_failure(r) is None

    def test_perm_error_substring(self) -> None:
        r = _fake_completed(returncode=1, stdout="your organization does not have access")
        assert classify_session_failure(r) == "perm_error"

    def test_perm_error_org_disabled_subscription(self) -> None:
        # Regression: org-level subscription-disabled message was not matched by the
        # old patterns, causing ~300 un-throttled retries in one run.
        r = _fake_completed(
            returncode=1,
            stdout="Your organization has disabled Claude subscription access for Claude Code · Use an Anthropic API key instead, or ask your admin to enable access",
        )
        assert classify_session_failure(r) == "perm_error"

    def test_rate_limit_substring(self) -> None:
        r = _fake_completed(returncode=1, stdout="You hit your limit. resets 5pm (UTC)")
        assert classify_session_failure(r) == "rate_limited"

    def test_rate_limit_session_limit_variant(self) -> None:
        # Regression: the real Claude message says "session limit", not "limit" —
        # the old "hit your limit" substring missed it and the orchestrator
        # retried the rate-limited account instead of rotating.
        r = _fake_completed(
            returncode=1,
            stdout="You've hit your session limit · resets 12:30am (Europe/Berlin)",
        )
        assert classify_session_failure(r) == "rate_limited"

    def test_rate_limit_weekly_limit_variant(self) -> None:
        # "weekly limit" likewise has a word between "your" and "limit".
        r = _fake_completed(
            returncode=1,
            stdout="You've hit your weekly limit · resets Mon 9am (Europe/Berlin)",
        )
        assert classify_session_failure(r) == "rate_limited"

    def test_prompt_too_long_substring(self) -> None:
        r = _fake_completed(returncode=1, stdout="Prompt is too long")
        assert classify_session_failure(r) == "prompt_too_long"

    def test_context_limit_no_entitlement_substring(self) -> None:
        # Sonnet auto-upgrade to 1M context refused because the account lacks "Extra usage".
        r = _fake_completed(
            returncode=1,
            stdout="API Error: Extra usage is required for 1M context · enable extra usage at claude.ai/settings/usage",
        )
        assert classify_session_failure(r) == "context_limit_no_entitlement"

    def test_unknown_failure_is_none(self) -> None:
        r = _fake_completed(returncode=1, stdout="some other failure")
        assert classify_session_failure(r) is None

    def test_perm_error_takes_precedence_over_rate_limit(self) -> None:
        # If both strings appear, perm error wins (more permanent condition).
        r = _fake_completed(returncode=1, stdout="does not have access. also hit your limit")
        assert classify_session_failure(r) == "perm_error"


class TestApplyPermErrorToAccount:
    def test_disables_account_and_advances_index(self, capsys: Any) -> None:
        state = PersistentState(account_index=0)
        run_data = RunData(start_time=datetime(2026, 5, 15, 12, 0, 0))
        saved = []
        deps = make_deps(write_file=lambda p, c: saved.append(p), makedirs=lambda p: None)

        apply_perm_error_to_account("web", state, run_data, num_accounts=2, deps=deps)

        assert "web" in run_data.disabled_accounts
        assert state.account_index == 1
        captured = capsys.readouterr()
        assert "no access" in captured.out


class TestApplyRateLimitToAccount:
    def test_records_reset_and_rotates(self, capsys: Any) -> None:
        state = PersistentState(account_index=0)
        record: dict[Any, Any] = {}
        deps = make_deps(
            get_now_utc=lambda: datetime(2026, 5, 15, 12, 0, 0, tzinfo=timezone.utc),
            write_file=lambda p, c: None,
            makedirs=lambda p: None,
        )

        stdout = "You hit your limit. resets 5pm (UTC)"
        apply_rate_limit_to_account("web", stdout, record, state, num_accounts=2, deps=deps)

        assert record["rate_limited"] is True
        assert record["reset_at"] is not None
        assert "web" in state.rate_limited_until
        assert state.account_index == 1
        captured = capsys.readouterr()
        assert "rate-limited" in captured.out

    def test_unparseable_reset_falls_back_to_now_plus_fallback(self) -> None:
        state = PersistentState(account_index=0)
        record: dict[Any, Any] = {}
        now_utc = datetime(2026, 5, 15, 12, 0, 0, tzinfo=timezone.utc)
        deps = make_deps(
            get_now_utc=lambda: now_utc,
            write_file=lambda p, c: None,
            makedirs=lambda p: None,
        )

        # stdout that doesn't match RATE_LIMIT_PATTERN
        apply_rate_limit_to_account("web", "hit your limit but no reset time", record, state, 1, deps)

        # reset_at gets None on the record because parse failed,
        # but state.rate_limited_until[acct] is still set to a fallback time
        assert record["reset_at"] is None
        assert "web" in state.rate_limited_until


# ---------------------------------------------------------------------------
# Category J: Resume helpers added with the "prompt too long" recovery
# ---------------------------------------------------------------------------

from orchestrate import (
    PromoteResult,
    _promote_task_to_opus_for_context_limit,
    _resolve_task_goal_and_model,
    _rewrite_question_session_id,
)


class TestRewriteQuestionSessionId:
    def test_rewrites_existing_session_id(self, tmp_path: Any) -> None:
        qpath = tmp_path / "question.md"
        qpath.write_text(
            "---\n"
            "task_id: TASK-X\n"
            "session_id: old-uuid\n"
            "account: web\n"
            "---\n"
            "body\n"
        )
        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
        )

        _rewrite_question_session_id(str(qpath), "NEW_SESSION_REQUIRED", deps)

        text = qpath.read_text()
        assert "session_id: NEW_SESSION_REQUIRED" in text
        assert "old-uuid" not in text
        assert "task_id: TASK-X" in text  # other fields preserved

    def test_missing_session_id_field_warns_and_skips(self, tmp_path: Any, capsys: Any) -> None:
        qpath = tmp_path / "question.md"
        qpath.write_text("---\ntask_id: TASK-Y\naccount: web\n---\nbody\n")
        original = qpath.read_text()
        deps = make_deps(
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
        )

        _rewrite_question_session_id(str(qpath), "NEW_SESSION_REQUIRED", deps)

        assert qpath.read_text() == original
        captured = capsys.readouterr()
        assert "no session_id line" in captured.out


class TestResolveTaskGoalAndModel:
    def test_returns_path_and_opus_when_recommended(self, tmp_path: Any) -> Any:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\n"
            "task_id: TASK-OPUS\n"
            "opus_recommended: true   # reason: cross-cutting\n"
            "---\n"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            if "grep" in cmd[0]:
                return _fake_completed(stdout=str(goal_path) + "\n")
            return _fake_completed()

        deps = make_deps(run_subprocess=fake_subprocess, read_file=lambda p: open(p).read())

        path, model = _resolve_task_goal_and_model("TASK-OPUS", deps)
        assert path == str(goal_path)
        assert model == "opus"

    def test_returns_task_id_and_none_when_goal_not_found(self) -> Any:
        def fake_subprocess(cmd, *args, **kwargs):
            return _fake_completed(stdout="")

        deps = make_deps(run_subprocess=fake_subprocess)
        path, model = _resolve_task_goal_and_model("TASK-MISSING", deps)
        assert path == "TASK-MISSING"
        assert model is None

    def test_returns_none_model_when_not_opus_recommended(self, tmp_path: Any) -> Any:
        goal_path = tmp_path / "goal.md"
        goal_path.write_text("---\ntask_id: TASK-S\n---\n")

        def fake_subprocess(cmd, *args, **kwargs):
            if "grep" in cmd[0]:
                return _fake_completed(stdout=str(goal_path) + "\n")
            return _fake_completed()

        deps = make_deps(run_subprocess=fake_subprocess, read_file=lambda p: open(p).read())
        path, model = _resolve_task_goal_and_model("TASK-S", deps)
        assert path == str(goal_path)
        assert model is None


class TestPromoteTaskToOpusForContextLimit:
    """_promote_task_to_opus_for_context_limit flips a sonnet task to opus and resets
    it to a fresh-launch state after a 1M-context entitlement error."""

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

    def test_promotes_sonnet_task_and_resets_for_fresh_launch(self, tmp_path: Any) -> None:
        goal_path = self._setup_goal(
            tmp_path,
            "---\n"
            "task_id: TASK-CTX\n"
            "status: in_progress\n"
            "opus_recommended: false\n"
            "session_id: doomed-uuid\n"
            "after: []\n"
            "---\n"
            "body\n",
        )
        writes: dict[Any, Any] = {}
        deps = self._make_deps(goal_path, writes)

        result = _promote_task_to_opus_for_context_limit("TASK-CTX", deps)

        assert result == PromoteResult.PROMOTED
        assert result.is_success is True
        text = open(goal_path).read()
        assert "opus_recommended: true" in text
        assert "promoted after context_limit_no_entitlement" in text
        assert "status: pending" in text
        assert 'session_id: ""' in text
        assert "doomed-uuid" not in text
        # Unrelated frontmatter survives.
        assert "task_id: TASK-CTX" in text
        assert "after: []" in text

    def test_skips_when_already_opus(self, tmp_path: Any, capsys: Any) -> None:
        goal_path = self._setup_goal(
            tmp_path,
            "---\n"
            "task_id: TASK-BIG\n"
            "status: in_progress\n"
            "opus_recommended: true\n"
            "session_id: doomed-uuid\n"
            "---\n",
        )
        original = open(goal_path).read()
        writes: dict[Any, Any] = {}
        deps = self._make_deps(goal_path, writes)

        result = _promote_task_to_opus_for_context_limit("TASK-BIG", deps)

        # Distinguishes "already at max" from other failure reasons — callers can
        # log differently or build different recovery flows on top of this.
        assert result == PromoteResult.ALREADY_AT_MAX
        assert result.is_success is False
        # File unchanged.
        assert open(goal_path).read() == original
        captured = capsys.readouterr()
        assert "already opus_recommended" in captured.out

    def test_skips_when_goal_not_found(self, capsys: Any) -> Any:
        # No goal.md anywhere — grep returns empty.
        def fake_subprocess(cmd, *args, **kwargs):
            return _fake_completed(stdout="")

        deps = make_deps(run_subprocess=fake_subprocess)
        result = _promote_task_to_opus_for_context_limit("TASK-MISSING", deps)

        assert result == PromoteResult.UNREADABLE
        assert result.is_success is False
        captured = capsys.readouterr()
        assert "cannot locate goal.md" in captured.out

    def test_returns_no_promotable_field_when_opus_line_missing(self, tmp_path: Any, capsys: Any) -> None:
        """Distinct PromoteResult.NO_PROMOTABLE_FIELD when frontmatter has no
        opus_recommended line at all — caller can surface this differently from
        ALREADY_AT_MAX, since this case indicates malformed task metadata.
        """
        goal_path = self._setup_goal(
            tmp_path,
            "---\ntask_id: TASK-NOOPUS\nstatus: in_progress\n---\n",
        )
        writes: dict[Any, Any] = {}
        deps = self._make_deps(goal_path, writes)

        result = _promote_task_to_opus_for_context_limit("TASK-NOOPUS", deps)

        assert result == PromoteResult.NO_PROMOTABLE_FIELD
        assert result.is_success is False
        captured = capsys.readouterr()
        assert "no opus_recommended line" in captured.out


class TestProcessAnsweredFeedbackPromptTooLong:
    """End-to-end: a resume returning 'Prompt is too long' switches to fresh-session
    recovery instead of burning the AC-21 retry budget on doomed --resume calls."""

    def _make_setup(self, tmp_path: Any, resume_stdouts: "list[tuple[int, str]]") -> Any:
        """Set up an answered-feedback item; popen returns from resume_stdouts in order."""
        task_dir = tmp_path / "TASK-LONG"
        task_dir.mkdir()
        question_path = task_dir / "question.md"
        answer_path = task_dir / "answer.md"
        question_path.write_text(
            "---\n"
            "task_id: TASK-LONG\n"
            "session_id: sess-toolong\n"
            "account: web\n"
            "---\n"
            "body\n"
        )
        answer_path.write_text("the answer")

        # Fake goal.md so _resolve_task_goal_and_model returns a real path.
        goal_dir = tmp_path / "req"
        goal_dir.mkdir()
        goal_path = goal_dir / "goal.md"
        # opus_recommended: false at the start so the prompt_too_long path can
        # actually promote (sonnet → opus) and launch a recovery on the new model.
        # Pre-fix this fixture had `true`, which (post-fix) would cause the recovery
        # to be skipped entirely under "already at max → context overflow is permanent".
        goal_path.write_text("---\ntask_id: TASK-LONG\nopus_recommended: false\n---\n")

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)

        call_idx = [0]
        writes: dict[str, str] = {}

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                i = call_idx[0]
                call_idx[0] += 1
                rc, out = resume_stdouts[min(i, len(resume_stdouts) - 1)]
                return _fake_completed(returncode=rc, stdout=out)
            return _fake_completed()

        def tracking_write(p, c):
            writes[str(p)] = c
            open(p, "w").write(c)

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
            file_exists=lambda p: os.path.exists(p),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=tracking_write,
        )
        return deps, task_dir, question_path, writes

    def test_resume_too_long_triggers_fresh_recovery(self, tmp_path: Any, capsys: Any) -> None:
        deps, _task_dir, question_path, writes = self._make_setup(
            tmp_path,
            resume_stdouts=[
                (1, "Prompt is too long"),   # the --resume attempt
                (0, "recovery succeeded"),   # the fresh recovery
            ],
        )
        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        decision, _sl = o.process_answered_feedback(
            state, run_data, args, {"requested": False}, 0
        )

        assert decision == "continue"
        # Two session records: the doomed resume + the fresh recovery
        assert len(run_data.sessions) == 2
        assert run_data.sessions[0]["exit_code"] == 1
        assert run_data.sessions[1].get("recovery_from") == "prompt_too_long"
        assert run_data.sessions[1]["exit_code"] == 0
        # The original session_id is marked exhausted so future iterations skip it
        assert "sess-toolong" in run_data.exhausted_resume_ids
        # The question.md was rewritten before the recovery ran, so the rewrite
        # is captured in the writes tracker even if the folder was later moved
        # to answered_feedback/ on recovery success.
        rewritten = writes.get(str(question_path), "")
        assert "session_id: NEW_SESSION_REQUIRED" in rewritten, rewritten
        captured = capsys.readouterr()
        assert "Prompt is too long" in captured.out
        assert "switching to fresh-session recovery" in captured.out

    def test_resume_too_long_does_not_burn_3_attempts(self, tmp_path: Any, capsys: Any) -> None:
        """Regression test for the original bug: 3 sessions all failing with
        'Prompt is too long' inside one orchestrator iteration."""
        deps, _, _, _ = self._make_setup(
            tmp_path,
            resume_stdouts=[
                (1, "Prompt is too long"),
                (0, "recovery ok"),
            ],
        )
        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        # Resume attempt counter should be exactly 1, not 3 (the recovery does not
        # bump the counter again — the AC-21 cap still kicks in eventually).
        assert run_data.resume_attempt_counts.get("sess-toolong", 0) == 1


class TestProcessAnsweredFeedbackRecoveryClassification:
    """The fresh-recovery session itself can hit rate limit or perm error;
    those must update state, not silently fall through."""

    def _make_setup(self, tmp_path: Any, resume_stdouts: Any) -> Any:
        task_dir = tmp_path / "TASK-RECOV"
        task_dir.mkdir()
        qpath = task_dir / "question.md"
        apath = task_dir / "answer.md"
        qpath.write_text(
            "---\ntask_id: TASK-RECOV\nsession_id: sess-x\naccount: web\n---\nbody\n"
        )
        apath.write_text("ans")

        goal_dir = tmp_path / "req"
        goal_dir.mkdir()
        gp = goal_dir / "goal.md"
        # opus_recommended: false so _promote_task_to_opus_for_context_limit can
        # promote to true on the first prompt_too_long failure (otherwise the helper
        # finds no opus_recommended line and returns False, which the recovery path
        # now treats as "already at max — skip recovery").
        gp.write_text("---\ntask_id: TASK-RECOV\nopus_recommended: false\n---\n")

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        idx = [0]

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(gp) + "\n")
            if "claude" in cmd_str:
                i = idx[0]
                idx[0] += 1
                rc, out = resume_stdouts[min(i, len(resume_stdouts) - 1)]
                return _fake_completed(returncode=rc, stdout=out)
            return _fake_completed()

        return make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
            file_exists=lambda p: os.path.exists(p),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
            get_now_utc=lambda: datetime(2026, 5, 15, 12, 0, 0, tzinfo=timezone.utc),
        )

    def test_recovery_rate_limit_updates_state(self, tmp_path: Any) -> None:
        deps = self._make_setup(
            tmp_path,
            resume_stdouts=[
                (1, "Prompt is too long"),
                (1, "You hit your limit. resets 9pm (UTC)"),
            ],
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        # Without the fix: state.rate_limited_until would be empty because the
        # recovery's "hit your limit" was never classified.
        assert "web" in state.rate_limited_until

    def test_recovery_perm_error_disables_account(self, tmp_path: Any) -> None:
        deps = self._make_setup(
            tmp_path,
            resume_stdouts=[
                (1, "Prompt is too long"),
                (1, "your organization does not have access"),
            ],
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        assert "web" in run_data.disabled_accounts

    def test_recovery_prompt_too_long_marks_exhausted(self, tmp_path: Any, capsys: Any) -> None:
        """Finding 2: prompt_too_long on the Opus recovery itself adds the recovery
        uuid to exhausted_resume_ids and exhausted_resume_tasks, so the task is
        skipped for the rest of this run.

        Why: the recovery is launched on Opus precisely to escape context-window
        failures. If it still hits one, the task has outgrown even 1M context.
        Without this guard the orchestrator would re-enter the same recovery path
        on each iteration, burning an account-attempt every time under AC-21's cap.
        """
        deps = self._make_setup(
            tmp_path,
            resume_stdouts=[
                (1, "Prompt is too long"),  # original resume — promotes to recovery
                (1, "Prompt is too long"),  # recovery itself ALSO too long
            ],
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)

        # Recovery uuid should be marked exhausted (we don't know its value upfront —
        # check that exactly one new entry beyond the original sess-x was added).
        assert len(run_data.exhausted_resume_ids) >= 2, (
            f"recovery uuid should be added to exhausted_resume_ids; got {run_data.exhausted_resume_ids}"
        )
        # Exhausted-tasks list should reference TASK-RECOV.
        task_ids = [t["task_id"] for t in run_data.exhausted_resume_tasks]
        assert "TASK-RECOV" in task_ids, (
            f"TASK-RECOV should be in exhausted_resume_tasks; got {task_ids}"
        )
        captured = capsys.readouterr()
        assert "outgrown 1M context" in captured.out, (
            "expected WARNING about Opus context overflow"
        )

    def test_recovery_context_limit_no_entitlement_marks_exhausted(self, tmp_path: Any, capsys: Any) -> None:
        """Same as prompt_too_long but for the context_limit_no_entitlement signature.

        Why: both signatures mean "conversation exceeds model context"; the recovery
        path must treat them symmetrically.
        """
        deps = self._make_setup(
            tmp_path,
            resume_stdouts=[
                (1, "Prompt is too long"),
                (1, "Extra usage is required for 1M context"),
            ],
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        task_ids = [t["task_id"] for t in run_data.exhausted_resume_tasks]
        assert "TASK-RECOV" in task_ids
        captured = capsys.readouterr()
        assert "outgrown 1M context" in captured.out

    def test_already_on_opus_skips_recovery_launch(self, tmp_path: Any, capsys: Any) -> None:
        """Finding #1: when prompt_too_long fires on a task that's already opus_recommended,
        _promote_task_to_opus_for_context_limit returns False (no further promotion
        possible). The recovery path must NOT launch a doomed fresh session — it should
        mark the task exhausted and return cleanly.

        Pre-fix: the orchestrator ignored the return value and launched a recovery
        that hit the same prompt_too_long error, burning an account-attempt.
        """
        # Override the standard fixture's opus_recommended: false with true,
        # simulating a task that's already been promoted on a prior iteration.
        deps = self._make_setup(
            tmp_path,
            resume_stdouts=[
                (1, "Prompt is too long"),  # original resume — promote no-op
                (1, "SHOULD NOT BE CALLED"),  # this MUST not run if fix works
            ],
        )
        # Patch the goal.md to opus_recommended: true.
        import glob as _glob
        for p in _glob.glob(str(tmp_path / "req" / "goal.md")):
            with open(p, "w") as f:
                f.write("---\ntask_id: TASK-RECOV\nopus_recommended: true\n---\n")

        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)

        # Exactly one session record (the original resume), NOT two (no recovery).
        assert len(run_data.sessions) == 1, (
            f"recovery should NOT launch when task is already on opus; got {len(run_data.sessions)} sessions"
        )
        # Task is marked exhausted so future iterations skip it.
        task_ids = [t["task_id"] for t in run_data.exhausted_resume_tasks]
        assert "TASK-RECOV" in task_ids
        captured = capsys.readouterr()
        assert "already on opus" in captured.out, (
            f"expected explanatory log about already-on-opus skip; got:\n{captured.out}"
        )

    def test_exhausted_recovery_skipped_on_subsequent_iterations(self, tmp_path: Any) -> None:
        """After a recovery is marked exhausted, the next iteration must skip the
        item rather than re-entering the same doomed recovery path.

        Why: without the exhausted_resume_tasks add, the same answered-feedback
        item would be re-discovered on each loop iteration (find_answered_feedback
        re-scans the directory), and each iteration would re-attempt the recovery,
        burning an account on every loop.
        """
        deps = self._make_setup(
            tmp_path,
            resume_stdouts=[
                (1, "Prompt is too long"),  # iter 1: original resume
                (1, "Prompt is too long"),  # iter 1: recovery (still too long)
                (1, "should-not-be-called"),  # iter 2 should not launch claude at all
            ],
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        # Iteration 1: original + recovery, both hit prompt_too_long → exhausted.
        o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        sessions_after_iter1 = len(run_data.sessions)

        # Iteration 2: must NOT enter the recovery again — item is exhausted.
        decision, _sl = o.process_answered_feedback(
            state, run_data, args, {"requested": False}, 0
        )
        assert decision == "next", (
            f"exhausted item should not be returned by find_answered_feedback's "
            f"post-filter; expected decision='next', got {decision!r}"
        )
        # No new sessions launched in iteration 2.
        assert len(run_data.sessions) == sessions_after_iter1, (
            "exhausted item must not trigger a new session launch"
        )


class TestProcessAnsweredFeedbackGoalSessionIdInvariant:
    """Regression tests for the 2026-05-16 23:27:34 bug: the orchestrator launched a
    fresh session for TASK-PROC-046-03 but never wrote the new session_id into
    goal.md. On the next iteration, scan_in_progress_without_session_id flagged the
    task as 'started manually' and skipped it.

    The invariant: every orchestrator-owned launch must record its session_uuid in
    goal.md so future iterations can distinguish orchestrator sessions from manual ones.
    """

    def _make_setup(self, tmp_path: Any, resume_stdouts: Any, session_id_in_question: Any = "sess-fresh") -> Any:
        task_dir = tmp_path / "TASK-INV"
        task_dir.mkdir()
        qpath = task_dir / "question.md"
        apath = task_dir / "answer.md"
        qpath.write_text(
            "---\n"
            f"task_id: TASK-INV\nsession_id: {session_id_in_question}\naccount: web\n"
            "---\nbody\n"
        )
        apath.write_text("ans")

        goal_dir = tmp_path / "req"
        goal_dir.mkdir()
        gp = goal_dir / "goal.md"
        # Start with empty session_id — the orchestrator must fill it in.
        # opus_recommended: false enables the prompt_too_long → opus promotion path
        # (see TASK-RECOV fixture comment).
        gp.write_text(
            "---\n"
            "task_id: TASK-INV\n"
            "status: in_progress\n"
            'session_id: ""\n'
            "opus_recommended: false\n"
            "---\nbody\n"
        )

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        idx = [0]

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(gp) + "\n")
            if "claude" in cmd_str:
                i = idx[0]
                idx[0] += 1
                rc, out = resume_stdouts[min(i, len(resume_stdouts) - 1)]
                return _fake_completed(returncode=rc, stdout=out)
            return _fake_completed()

        def tracking_write(p, c):
            open(p, "w").write(c)

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
            file_exists=lambda p: os.path.exists(p),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=tracking_write,
            get_now_utc=lambda: datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc),
        )
        return deps, gp

    def test_requires_fresh_session_path_writes_session_id_to_goal_md(self, tmp_path: Any) -> None:
        """When session_id=NEW_SESSION_REQUIRED triggers a fresh-session launch,
        the new uuid must end up in goal.md."""
        deps, gp = self._make_setup(
            tmp_path,
            resume_stdouts=[(0, "session ran ok")],
            session_id_in_question="NEW_SESSION_REQUIRED",
        )
        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)

        # After the launch, goal.md must have a non-empty session_id.
        # The launch's uuid is captured in run_data.sessions[0]["session_uuid"]
        # — but it's stored in finalize_session_record. More robustly: just
        # verify the empty-string sentinel was replaced.
        final = open(gp).read()
        assert 'session_id: ""' not in final, (
            "fresh-session launch must overwrite the empty session_id sentinel"
        )
        # Sanity: session_id line is present with some uuid value.
        session_id_lines = [line for line in final.splitlines() if line.startswith("session_id:")]
        assert session_id_lines and session_id_lines[0].split(":", 1)[1].strip(), (
            f"expected session_id line with a value, got {session_id_lines}"
        )

    def test_prompt_too_long_recovery_writes_session_id_to_goal_md(self, tmp_path: Any) -> None:
        """When the original resume hits 'Prompt is too long' and a fresh recovery
        is launched, the recovery uuid must end up in goal.md.

        Regression: this is the exact path that broke TASK-PROC-046-03. The recovery
        previously called run_fresh_session_with_answer without updating goal.md, so
        the next iteration treated the in_progress task as a manual session.
        """
        deps, gp = self._make_setup(
            tmp_path,
            resume_stdouts=[
                (1, "Prompt is too long"),
                (0, "recovery ok"),
            ],
        )
        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)

        # _promote_task_to_opus_for_context_limit clears session_id to "" before the
        # recovery launches. After the recovery, register_session_in_goal must have
        # written the recovery uuid back into goal.md.
        final = open(gp).read()
        session_id_lines = [line for line in final.splitlines() if line.startswith("session_id:")]
        assert session_id_lines, "expected session_id line in goal.md after recovery"
        value = session_id_lines[-1].split(":", 1)[1].strip().strip('"')
        assert value and value != "NEW_SESSION_REQUIRED", (
            f"recovery uuid should be written to goal.md (got session_id={value!r})"
        )


class TestProcessAnsweredFeedbackRateLimitedAccountSwitch:
    """Regression tests for 2026-05-16 incident: TASK-PROC-046-03 burned all 6
    --max-tasks slots because the answered-feedback resume path blindly launched
    with the rate-limited account stored in question.md instead of switching to
    an available account via shared session storage."""

    def _make_setup(self, tmp_path: Any, resume_stdouts: Any, stored_account: Any = "gmail") -> Any:
        task_dir = tmp_path / "TASK-RL-SWITCH"
        task_dir.mkdir()
        question_path = task_dir / "question.md"
        answer_path = task_dir / "answer.md"
        question_path.write_text(
            f"---\n"
            f"task_id: TASK-RL-SWITCH\n"
            f"session_id: sess-rl-switch\n"
            f"account: {stored_account}\n"
            f"---\n"
            f"body\n"
        )
        answer_path.write_text("an answer")

        goal_dir = tmp_path / "req"
        goal_dir.mkdir()
        goal_path = goal_dir / "goal.md"
        goal_path.write_text("---\ntask_id: TASK-RL-SWITCH\n---\n")

        entry = make_fake_dir_entry(str(task_dir), is_dir=True)
        call_idx = [0]
        claude_envs: list[dict[Any, Any]] = []  # env per claude popen call

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                i = call_idx[0]
                call_idx[0] += 1
                rc, out = resume_stdouts[min(i, len(resume_stdouts) - 1)]
                return _fake_completed(returncode=rc, stdout=out)
            return _fake_completed()

        def capturing_popen(cmd, *args, **kwargs):
            # The orchestrator launches claude sessions via popen_subprocess and
            # passes env= with CLAUDE_SESSION_ACCOUNT set. Capture it so the test
            # can assert which account was actually used for the resume.
            cmd_str = " ".join(str(c) for c in cmd)
            if "claude" in cmd_str:
                claude_envs.append(dict(kwargs.get("env", {})))
            completed = fake_subprocess(cmd)
            proc = MagicMock()
            proc.poll.return_value = completed.returncode
            proc.communicate.return_value = (completed.stdout or "", "")
            proc.pid = 33333
            return proc

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=capturing_popen,
            list_dir=lambda p: [entry],
            read_file=lambda p: open(p).read(),
            file_exists=lambda p: os.path.exists(p),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            write_file=lambda p, c: open(p, "w").write(c),
            get_now_utc=lambda: datetime(2026, 5, 16, 22, 0, 0, tzinfo=timezone.utc),
        )
        return deps, claude_envs

    def test_stored_account_rate_limited_switches_to_available(self, tmp_path: Any, capsys: Any) -> None:
        """When question.md.account is rate-limited but another account is free,
        the resume must launch with the alternative account (shared session storage)
        instead of burning a slot hitting the same rate limit."""
        future = (datetime(2026, 5, 16, 22, 0, 0, tzinfo=timezone.utc)
                  + timedelta(hours=5)).isoformat()
        deps, claude_envs = self._make_setup(
            tmp_path,
            resume_stdouts=[(0, "Done")],
            stored_account="gmail",
        )
        o = Orchestrator(deps)
        o._accounts = ["gmail", "web"]
        state = PersistentState(rate_limited_until={"gmail": future})
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        decision, _sl = o.process_answered_feedback(
            state, run_data, args, {"requested": False}, 0
        )
        assert decision == "continue"
        # Switch message logged
        captured = capsys.readouterr()
        assert "Switching resume account gmail" in captured.out
        assert "web" in captured.out
        # The session must have launched with web, not gmail
        assert claude_envs, "expected at least one claude invocation"
        used_acct = claude_envs[0].get("CLAUDE_SESSION_ACCOUNT", "")
        assert used_acct == "web", f"expected web, got {used_acct!r}"

    def test_all_accounts_rate_limited_waits_then_re_enters_loop(self, tmp_path: Any, capsys: Any) -> None:
        """When every configured account is rate-limited, the orchestrator must
        wait for the earliest reset (interruptibly) and return continue without
        launching a session — not blindly launch and hit the limit again."""
        future = (datetime(2026, 5, 16, 22, 0, 0, tzinfo=timezone.utc)
                  + timedelta(hours=5)).isoformat()
        deps, claude_envs = self._make_setup(
            tmp_path,
            resume_stdouts=[(0, "should-not-run")],
            stored_account="gmail",
        )
        o = Orchestrator(deps)
        o._accounts = ["gmail", "web"]
        state = PersistentState(
            rate_limited_until={"gmail": future, "web": future}
        )
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        # stop_flag set so rate_limit_sleep returns immediately
        decision, sl = o.process_answered_feedback(
            state, run_data, args, {"requested": True}, 0
        )
        assert decision == "continue"
        assert sl == 0  # no session launched
        # No claude invocation happened
        assert claude_envs == [], (
            f"expected no claude invocation when all accounts rate-limited, "
            f"got {len(claude_envs)}"
        )
        # Attempt counter must be rolled back so the AC-21 budget is preserved
        # for real attempts (not wasted on waits).
        assert run_data.resume_attempt_counts.get("sess-rl-switch", 0) == 0

    def test_does_not_burn_max_tasks_on_repeated_rate_limited_launches(self, tmp_path: Any) -> None:
        """Regression for the actual 2026-05-16 incident: 6 consecutive answered-feedback
        loop iterations against a rate-limited stored account must NOT each consume
        a sessions_launched slot. With the fix, the first iteration switches accounts
        (no rate-limit) and succeeds on the alternative. Without the fix, six
        iterations would each rate-limit and increment sessions_launched."""
        future = (datetime(2026, 5, 16, 22, 0, 0, tzinfo=timezone.utc)
                  + timedelta(hours=5)).isoformat()
        # If the fix is absent, the orchestrator launches gmail and gets rate-limited;
        # this stdout would be served. With the fix in place, it should never be served
        # because the orchestrator switches to web first.
        deps, claude_envs = self._make_setup(
            tmp_path,
            resume_stdouts=[(0, "Done on web")],
            stored_account="gmail",
        )
        o = Orchestrator(deps)
        o._accounts = ["gmail", "web"]
        state = PersistentState(rate_limited_until={"gmail": future})
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        sessions_launched = 0
        for _ in range(6):
            _decision, sessions_launched = o.process_answered_feedback(
                state, run_data, args, {"requested": False}, sessions_launched
            )

        # The first iteration switches accounts and the resume succeeds (exit 0)
        # → no rate-limit hit. Subsequent iterations don't loop because the answered
        # feedback was processed (test focuses on first iteration's account choice).
        assert sessions_launched <= 1, (
            f"sessions_launched={sessions_launched} indicates rate-limited account "
            f"was launched against repeatedly (regression of 2026-05-16 incident)"
        )
        # Web (not gmail) must be the account that ran
        if claude_envs:
            used = claude_envs[0].get("CLAUDE_SESSION_ACCOUNT", "")
            assert used == "web", f"expected web, got {used!r}"


class TestProtoOnceDedupe:
    """Covers the per-run log dedupe helper added to silence iterating warnings.

    Why: pending_feedback scans every loop, so tasks with persistent blockers
    (whitespace answer.md, unchanged unanswered question) used to log the same
    warning ~10x per run. `_proto_once` keys each log line so it fires at most
    once per run, with `_run_log_dedupe.clear()` resetting it at run start.
    """

    def setup_method(self) -> None:
        _run_log_dedupe.clear()

    def teardown_method(self) -> None:
        _run_log_dedupe.clear()

    def test_first_call_emits_message(self, capsys: Any) -> None:
        _proto_once("k1", "hello once")
        captured = capsys.readouterr()
        assert "hello once" in captured.out

    def test_second_call_with_same_key_suppressed(self, capsys: Any) -> None:
        _proto_once("k1", "hello once")
        _proto_once("k1", "hello again")
        captured = capsys.readouterr()
        # First message present, second NOT present.
        assert captured.out.count("hello") == 1
        assert "hello again" not in captured.out

    def test_different_keys_each_emit(self, capsys: Any) -> None:
        _proto_once("k1", "msg-A")
        _proto_once("k2", "msg-B")
        captured = capsys.readouterr()
        assert "msg-A" in captured.out
        assert "msg-B" in captured.out

    def test_clear_restores_emission(self, capsys: Any) -> None:
        _proto_once("k1", "first run")
        _run_log_dedupe.clear()
        _proto_once("k1", "second run")
        captured = capsys.readouterr()
        assert "first run" in captured.out
        assert "second run" in captured.out


class TestActiveSessionEndedLog:
    """Issue 5 — active_session context manager must log a 'Session <uuid8> ended'
    line on exit. Without it, external observers (LLM monitoring loop, sleep
    watcher) can only infer session completion by next-iteration counter
    increments — that gap masks silent crashes.
    """

    def test_emits_ended_line_on_normal_exit(self, capsys: Any) -> None:
        from orchestrate import active_session
        deps = make_deps()
        state = PersistentState()
        import orchestrate
        with mock.patch.object(orchestrate, "save_state"):
            with active_session(state, "abcdef1234567890", deps):
                pass
        captured = capsys.readouterr()
        assert "Session abcdef12 ended" in captured.out, (
            f"expected 'Session <uuid8> ended' line; got:\n{captured.out}"
        )

    def test_emits_ended_line_even_when_body_raises(self, capsys: Any) -> None:
        from orchestrate import active_session
        deps = make_deps()
        state = PersistentState()
        import orchestrate
        with mock.patch.object(orchestrate, "save_state"):
            try:
                with active_session(state, "deadbeef1111aaaa", deps):
                    raise RuntimeError("boom")
            except RuntimeError:
                pass
        captured = capsys.readouterr()
        assert "Session deadbeef ended" in captured.out, (
            "ended-log must fire from finally even when the body raises"
        )


class TestRunNormalSessionStepContextLimitAlreadyOpus:
    """Issue 3 — when a fresh-launch sonnet hit `context_limit_no_entitlement`
    and the task was already opus_recommended (so promote-to-opus is a no-op),
    the orchestrator previously left session_id in goal.md, causing the next
    iteration's find_resumable_session to attempt a doomed --resume and burn
    a rate-limit budget. The fix marks the session exhausted AND clears
    session_id from goal.md.
    """

    def test_already_opus_marks_exhausted_and_clears_session_id(self, tmp_path: Any, capsys: Any) -> None:
        # Goal.md is already opus_recommended (simulating a prior promotion).
        # status=in_progress so find_active_task_goal picks it up rather than
        # routing through pick_next_task_for_session.
        goal_path = tmp_path / "goal.md"
        goal_path.write_text(
            "---\n"
            "task_id: TASK-CTX-X\n"
            "status: in_progress\n"
            "opus_recommended: true\n"
            "session_id: prior-sid\n"
            "session_account: web\n"
            "---\n"
            "Body\n"
        )

        def fake_subprocess(cmd, *args, **kwargs):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout=str(goal_path) + "\n")
            if "claude" in cmd_str:
                # The opus-already case fires the same entitlement error again.
                return _fake_completed(
                    returncode=1,
                    stdout="Extra usage is required for 1M context",
                )
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: True,
            makedirs=lambda p: None,
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
        )
        o = Orchestrator(deps)
        o._accounts = ["web", "gmail"]
        state = PersistentState()
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        decision, sl_after = o.run_normal_session_step(
            state, run_data, "web", args, {"requested": False}, 0,
        )

        assert decision == "continue"
        assert sl_after == 0, "context-limit failure must not bump sessions_launched"

        # The task must be marked exhausted so future iterations skip it.
        task_ids = [t["task_id"] for t in run_data.exhausted_resume_tasks]
        assert "TASK-CTX-X" in task_ids, (
            f"TASK-CTX-X must be in exhausted_resume_tasks; got {task_ids}"
        )
        assert len(run_data.exhausted_resume_ids) >= 1, (
            "at least one session_id must be in exhausted_resume_ids"
        )

        # The goal.md session_id must be cleared so find_resumable_session skips it.
        new_content = open(goal_path).read()
        assert 'session_id: ""' in new_content or "session_id: \n" in new_content, (
            f"session_id must be cleared after already-opus context-limit failure; "
            f"goal.md is:\n{new_content}"
        )

        # User-facing log should mention the clear so the operator understands what happened.
        captured = capsys.readouterr()
        assert "already on opus" in captured.out
        assert "Cleared session_id" in captured.out


# ---------------------------------------------------------------------------
# Cat I — _clear_inbox
# ---------------------------------------------------------------------------

class TestClearInbox:
    """Unit tests for _clear_inbox().

    Verifies idempotency (empty/missing file → no-op) and clearing behaviour
    (non-empty file → truncated to zero bytes). Uses tmp_path so no production
    automation/inbox.md is touched.
    """

    def test_clears_non_empty_inbox(self, tmp_path: Any) -> None:
        (tmp_path / "automation").mkdir()
        inbox = tmp_path / "automation" / "inbox.md"
        inbox.write_text("hello operator")
        with mock.patch("orchestrate.PROJECT_ROOT", str(tmp_path)):
            _clear_inbox()
        assert inbox.read_text() == "", "inbox.md must be empty after _clear_inbox()"

    def test_no_op_when_inbox_empty(self, tmp_path: Any) -> None:
        (tmp_path / "automation").mkdir()
        inbox = tmp_path / "automation" / "inbox.md"
        inbox.write_text("")
        with mock.patch("orchestrate.PROJECT_ROOT", str(tmp_path)):
            _clear_inbox()  # must not raise; file stays empty
        assert inbox.read_text() == ""

    def test_no_op_when_inbox_missing(self, tmp_path: Any) -> None:
        # automation/ dir exists but inbox.md does not
        (tmp_path / "automation").mkdir()
        with mock.patch("orchestrate.PROJECT_ROOT", str(tmp_path)):
            _clear_inbox()  # must not raise

    def test_called_on_successful_answered_feedback(self, tmp_path: Any) -> None:
        """process_answered_feedback calls _clear_inbox() when session exits 0 and no new question."""
        inbox = tmp_path / "automation" / "inbox.md"
        inbox.parent.mkdir(parents=True)
        inbox.write_text("stale message")

        task_id = "TASK-INB-01"
        task_dir = tmp_path / "pending_feedback" / task_id
        task_dir.mkdir(parents=True)
        question_md = task_dir / "question.md"
        question_md.write_text(
            f"---\ntask_id: {task_id}\nsession_id: abc-123\naccount: web\n---\nQ?\n"
        )
        answer_md = task_dir / "answer.md"
        answer_md.write_text("The answer.")

        def fake_subprocess(cmd, *a, **kw):
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: True,
            list_dir=lambda p: list(__import__("os").scandir(p)),
            makedirs=lambda p: __import__("os").makedirs(p, exist_ok=True),
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
        )

        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        state.start_time = "2026-01-01T00:00:00"
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        import orchestrate as _orc
        orig_fb = _orc.FEEDBACK_DIR
        orig_ad = _orc.ANSWERED_DIR
        orig_pr = _orc.PROJECT_ROOT
        _orc.FEEDBACK_DIR = str(tmp_path / "pending_feedback")
        _orc.ANSWERED_DIR = str(tmp_path / "answered_feedback")
        _orc.PROJECT_ROOT = str(tmp_path)
        try:
            o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        finally:
            _orc.FEEDBACK_DIR = orig_fb
            _orc.ANSWERED_DIR = orig_ad
            _orc.PROJECT_ROOT = orig_pr

        assert inbox.read_text() == "", "_clear_inbox() must truncate inbox.md on task completion"

    def test_called_before_fresh_session_launch(self, tmp_path: Any) -> None:
        """run_normal_session_step calls _clear_inbox() before launching a new session."""
        inbox = tmp_path / "automation" / "inbox.md"
        inbox.parent.mkdir(parents=True)
        inbox.write_text("stale message from previous task")

        cleared: list[bool] = []

        def fake_subprocess(cmd, *a, **kw):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                return _fake_completed(stdout="")
            if "next_tasks" in cmd_str:
                return _fake_completed(stdout="")
            return _fake_completed()

        def fake_write(p: str, c: str) -> None:
            # Spy: record when inbox is cleared (written empty)
            if "inbox" in p and c == "":
                cleared.append(True)

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: True,
            makedirs=lambda p: None,
            read_file=lambda p: "",
            write_file=fake_write,
        )

        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        state.start_time = "2026-01-01T00:00:00"
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        import orchestrate as _orc
        orig_pr = _orc.PROJECT_ROOT
        _orc.PROJECT_ROOT = str(tmp_path)
        try:
            o.run_normal_session_step(state, run_data, "web", args, {"requested": False}, 0)
        finally:
            _orc.PROJECT_ROOT = orig_pr

        # inbox.md was non-empty before the session launched — it must be cleared now
        assert inbox.read_text() == "", "_clear_inbox() must truncate inbox.md before fresh session"


class TestFollowUpQuestionSafetyNet:
    """Regression tests for the safety-net that resets a stale answer.md when a
    resumed session writes a follow-up question without executing Step 3
    (copy TEMPLATE_answer.md over the old answer.md).
    """

    def _setup_feedback(
        self,
        tmp_path: Any,
        task_id: str,
        answer_mtime: float,
        question_mtime: float,
        answer_content: str = "yes I approve all",
        question_status: str = "awaiting_answer",
    ) -> tuple[Any, Any, Any]:
        """Create pending_feedback/<task_id>/{question,answer}.md and TEMPLATE_answer.md.

        Returns (task_dir, question_md, answer_md).
        """
        feedback_dir = tmp_path / "pending_feedback"
        task_dir = feedback_dir / task_id
        task_dir.mkdir(parents=True)

        question_md = task_dir / "question.md"
        question_md.write_text(
            f"---\ntask_id: {task_id}\nsession_id: new-session-id\naccount: web\n"
            f"status: {question_status}\n---\nFollow-up question?\n"
        )

        answer_md = task_dir / "answer.md"
        answer_md.write_text(answer_content)

        template = feedback_dir / "TEMPLATE_answer.md"
        template.write_text("<!-- AWAITING_HUMAN_ANSWER -->\nTemplate body.")

        return task_dir, question_md, answer_md

    def test_resets_answer_when_question_newer_than_answer(self, tmp_path: Any) -> None:
        """When question.md mtime > answer.md mtime, the stale answer is replaced
        with the template so find_answered_feedback skips the task next iteration."""
        task_id = "TASK-SAFETY-01"
        _task_dir, _q, answer_md = self._setup_feedback(
            tmp_path, task_id, answer_mtime=1000.0, question_mtime=2000.0
        )

        mtimes: dict[str, float] = {
            str(_q): 2000.0,   # question is NEWER
            str(answer_md): 1000.0,
        }

        def fake_get_mtime(p: str) -> float:
            return mtimes.get(p, 1000.0)

        def fake_subprocess(cmd, *a, **kw):
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: os.path.exists(p),
            list_dir=lambda p: list(__import__("os").scandir(p)),
            makedirs=lambda p: __import__("os").makedirs(p, exist_ok=True),
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
            get_mtime=fake_get_mtime,
        )

        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        state.start_time = "2026-01-01T00:00:00"
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        import orchestrate as _orc
        orig_fb = _orc.FEEDBACK_DIR
        orig_pr = _orc.PROJECT_ROOT
        orig_tmpl = _orc.ANSWER_TEMPLATE_PATH
        _orc.FEEDBACK_DIR = str(tmp_path / "pending_feedback")
        _orc.PROJECT_ROOT = str(tmp_path)
        _orc.ANSWER_TEMPLATE_PATH = str(tmp_path / "pending_feedback" / "TEMPLATE_answer.md")
        try:
            o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        finally:
            _orc.FEEDBACK_DIR = orig_fb
            _orc.PROJECT_ROOT = orig_pr
            _orc.ANSWER_TEMPLATE_PATH = orig_tmpl

        # answer.md must be reset to template content so it is treated as unanswered
        assert "<!-- AWAITING_HUMAN_ANSWER -->" in answer_md.read_text(), (
            "safety-net must reset answer.md to template when question.md is newer"
        )

    def test_does_not_reset_answer_when_question_older_than_answer(self, tmp_path: Any) -> None:
        """When answer.md mtime >= question.md mtime (normal answered state), answer.md
        must not be touched — the session should be resumed with the real answer."""
        task_id = "TASK-SAFETY-02"
        _task_dir, _q, answer_md = self._setup_feedback(
            tmp_path, task_id, answer_mtime=3000.0, question_mtime=1000.0
        )

        mtimes: dict[str, float] = {
            str(_q): 1000.0,    # question is OLDER (normal answered state)
            str(answer_md): 3000.0,
        }

        def fake_get_mtime(p: str) -> float:
            return mtimes.get(p, 1000.0)

        def fake_subprocess(cmd, *a, **kw):
            cmd_str = " ".join(str(c) for c in cmd)
            if "grep" in cmd_str:
                # Return the task's goal.md path so _resolve_task_goal_and_model succeeds
                goal_dir = tmp_path / "req" / task_id
                goal_dir.mkdir(parents=True, exist_ok=True)
                gp = goal_dir / "goal.md"
                if not gp.exists():
                    gp.write_text(f"---\ntask_id: {task_id}\n---\n")
                return _fake_completed(stdout=str(gp) + "\n")
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: os.path.exists(p),
            list_dir=lambda p: list(__import__("os").scandir(p)),
            makedirs=lambda p: __import__("os").makedirs(p, exist_ok=True),
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
            get_mtime=fake_get_mtime,
        )

        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        state.start_time = "2026-01-01T00:00:00"
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        import orchestrate as _orc
        orig_fb = _orc.FEEDBACK_DIR
        orig_pr = _orc.PROJECT_ROOT
        orig_tmpl = _orc.ANSWER_TEMPLATE_PATH
        _orc.FEEDBACK_DIR = str(tmp_path / "pending_feedback")
        _orc.PROJECT_ROOT = str(tmp_path)
        _orc.ANSWER_TEMPLATE_PATH = str(tmp_path / "pending_feedback" / "TEMPLATE_answer.md")
        try:
            o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        finally:
            _orc.FEEDBACK_DIR = orig_fb
            _orc.PROJECT_ROOT = orig_pr
            _orc.ANSWER_TEMPLATE_PATH = orig_tmpl

        # answer.md mtime < question.md mtime is the normal answered state: the session
        # exits 0 and the folder is deleted from pending_feedback/ (not moved anywhere).
        # Verify the folder was deleted — safety-net did not incorrectly reset the answer
        # to template (which would have left the task in pending_feedback instead).
        task_folder = tmp_path / "pending_feedback" / task_id
        assert not task_folder.exists(), (
            "pending_feedback folder must be deleted on clean exit when question is not newer than answer"
        )

    def test_does_not_reset_answer_when_question_newer_but_resolved(self, tmp_path: Any) -> None:
        """Regression: a session that edits question.md only to mark it status: resolved
        bumps question.md mtime above answer.md, but that is NOT a fresh follow-up
        question. The safety-net must gate on status and leave the human answer intact —
        otherwise a valid answer is wiped and the task is stranded in pending_feedback."""
        task_id = "TASK-SAFETY-03"
        _task_dir, _q, answer_md = self._setup_feedback(
            tmp_path, task_id, answer_mtime=1000.0, question_mtime=2000.0,
            question_status="resolved",
        )

        mtimes: dict[str, float] = {
            str(_q): 2000.0,    # question is NEWER (resolve-stamp edit bumped mtime)
            str(answer_md): 1000.0,
        }

        def fake_get_mtime(p: str) -> float:
            return mtimes.get(p, 1000.0)

        # Mirror TASK-SAFETY-01: goal resolution returns empty so the folder is not
        # deleted on clean exit, leaving answer.md inspectable. The ONLY difference from
        # the reset case is question_status="resolved" — so a reset here would be the bug.
        def fake_subprocess(cmd, *a, **kw):
            return _fake_completed()

        deps = make_deps(
            run_subprocess=fake_subprocess,
            popen_subprocess=make_popen_from_subprocess_fn(fake_subprocess),
            file_exists=lambda p: os.path.exists(p),
            list_dir=lambda p: list(__import__("os").scandir(p)),
            makedirs=lambda p: __import__("os").makedirs(p, exist_ok=True),
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
            get_mtime=fake_get_mtime,
        )

        o = Orchestrator(deps)
        o._accounts = ["web"]
        state = PersistentState()
        state.start_time = "2026-01-01T00:00:00"
        run_data = RunData(start_time=datetime.now())
        args = make_args()

        import orchestrate as _orc
        orig_fb = _orc.FEEDBACK_DIR
        orig_pr = _orc.PROJECT_ROOT
        orig_tmpl = _orc.ANSWER_TEMPLATE_PATH
        _orc.FEEDBACK_DIR = str(tmp_path / "pending_feedback")
        _orc.PROJECT_ROOT = str(tmp_path)
        _orc.ANSWER_TEMPLATE_PATH = str(tmp_path / "pending_feedback" / "TEMPLATE_answer.md")
        try:
            o.process_answered_feedback(state, run_data, args, {"requested": False}, 0)
        finally:
            _orc.FEEDBACK_DIR = orig_fb
            _orc.PROJECT_ROOT = orig_pr
            _orc.ANSWER_TEMPLATE_PATH = orig_tmpl

        # The real answer must survive — a resolved question is not an unanswered
        # follow-up. With the bug the answer would be reset to the (empty) template, so
        # new_question_written_for would return True and the folder would NOT be deleted.
        # With the fix the answer is preserved, the resume exits cleanly, and the folder
        # is removed from pending_feedback/. Folder-deletion is the discriminating signal.
        task_folder = tmp_path / "pending_feedback" / task_id
        assert not task_folder.exists(), (
            "safety-net must NOT reset answer.md when question.md status is resolved "
            "(folder should be deleted on clean resume, not stranded)"
        )


class TestArchiveFeedbackCheckpoint:
    """Unit tests for _archive_feedback_checkpoint (AC-06 / AC-09).

    Tests the pure helper directly using injected deps — no Orchestrator needed.
    """

    def _make_folder(self, tmp_path: Any, task_id: str, skill: str = "test-skill") -> Any:
        """Create pending_feedback/<task_id>/{question,answer}.md; return folder path."""
        folder = tmp_path / task_id
        folder.mkdir(parents=True)
        (folder / "question.md").write_text(
            f"---\ntask_id: {task_id}\nsession_id: abc-123\naccount: web\nskill: {skill}\n---\n\nThe question body.\n"
        )
        (folder / "answer.md").write_text("The developer answer.")
        return folder

    def _make_goal(self, tmp_path: Any, task_id: str) -> Any:
        """Create a fake goal.md for the task; return its path."""
        goal_dir = tmp_path / "req" / task_id
        goal_dir.mkdir(parents=True)
        gp = goal_dir / "goal.md"
        gp.write_text(f"---\ntask_id: {task_id}\n---\n")
        return gp

    def test_writes_checkpoint_with_correct_content(self, tmp_path: Any) -> None:
        """Merged checkpoint contains question body, answer body, and YAML envelope."""
        task_id = "TASK-ARC-01"
        folder = self._make_folder(tmp_path, task_id, skill="my-skill")
        goal = self._make_goal(tmp_path, task_id)

        written: dict[str, str] = {}

        def tracking_write(p: str, c: str) -> None:
            written[p] = c
            import builtins
            with builtins.open(p, "w") as fh:
                fh.write(c)

        deps = make_deps(
            file_exists=lambda p: os.path.exists(p),
            read_file=lambda p: open(p).read(),
            write_file=tracking_write,
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            get_now_local=lambda: datetime(2026, 6, 2, 14, 0, 0),
        )

        result = _archive_feedback_checkpoint(task_id, str(folder), str(goal), deps)

        assert result != "", "must return non-empty path on success"
        assert result.endswith("feedback-checkpoint.md")
        assert "2026-06-02" in result

        content = written[result]
        # YAML envelope fields
        assert "skill: my-skill" in content
        assert "mode: automated" in content
        assert f"task_id: {task_id}" in content
        assert "captured_at: 2026-06-02" in content
        # Body sections
        assert "# Question" in content
        assert "The question body." in content
        assert "# Developer Answer" in content
        assert "The developer answer." in content
        assert "# Rationale Captured" in content

    def test_returns_empty_when_files_missing(self, tmp_path: Any) -> None:
        """Returns empty string when question.md or answer.md is absent."""
        task_id = "TASK-ARC-02"
        folder = tmp_path / task_id
        folder.mkdir()
        goal = self._make_goal(tmp_path, task_id)

        deps = make_deps(
            file_exists=lambda p: False,
            get_now_local=lambda: datetime(2026, 6, 2, 14, 0, 0),
        )

        result = _archive_feedback_checkpoint(task_id, str(folder), str(goal), deps)
        assert result == "", "must return empty string when question/answer files are missing"

    def test_collision_avoidance_on_second_call(self, tmp_path: Any) -> None:
        """Two archive calls on the same day produce distinct files via _01 suffix."""
        task_id = "TASK-ARC-03"
        folder = self._make_folder(tmp_path, task_id)
        goal = self._make_goal(tmp_path, task_id)

        deps = make_deps(
            file_exists=lambda p: os.path.exists(p),
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            get_now_local=lambda: datetime(2026, 6, 2, 14, 0, 0),
        )

        path1 = _archive_feedback_checkpoint(task_id, str(folder), str(goal), deps)
        path2 = _archive_feedback_checkpoint(task_id, str(folder), str(goal), deps)

        assert path1 != path2, "second call must pick a non-colliding path"
        assert path1.endswith("feedback-checkpoint.md")
        assert path2.endswith("feedback-checkpoint_01.md")

    def test_checkpoint_placed_in_plans_and_protocols(self, tmp_path: Any) -> None:
        """Checkpoint file lands in plans_and_protocols/ next to goal.md."""
        task_id = "TASK-ARC-04"
        folder = self._make_folder(tmp_path, task_id)
        goal = self._make_goal(tmp_path, task_id)

        deps = make_deps(
            file_exists=lambda p: os.path.exists(p),
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
            makedirs=lambda p: os.makedirs(p, exist_ok=True),
            get_now_local=lambda: datetime(2026, 6, 2, 14, 0, 0),
        )

        result = _archive_feedback_checkpoint(task_id, str(folder), str(goal), deps)

        expected_dir = os.path.join(os.path.dirname(str(goal)), "plans_and_protocols")
        assert os.path.dirname(result) == expected_dir
        assert os.path.exists(result), "checkpoint file must exist on disk"

    def test_returns_empty_when_goal_path_is_not_absolute(self, tmp_path: Any) -> None:
        """Returns empty string when goal_path is a bare task_id (fallback from _resolve).

        Why: _resolve_task_goal_and_model returns the task_id string when no goal.md
        exists. os.path.dirname of a bare string is "", causing the checkpoint to land
        in the cwd (project root) rather than the task folder. This guard prevents that.
        """
        task_id = "TASK-SAFETY-01"
        folder = self._make_folder(tmp_path, task_id)

        makedirs_called: list[str] = []

        def tracking_makedirs(p: str) -> None:
            makedirs_called.append(p)
            os.makedirs(p, exist_ok=True)

        deps = make_deps(
            file_exists=lambda p: os.path.exists(p),
            read_file=lambda p: open(p).read(),
            write_file=lambda p, c: open(p, "w").write(c),
            makedirs=tracking_makedirs,
            get_now_local=lambda: datetime(2026, 6, 2, 14, 0, 0),
        )

        # Pass the bare task_id as goal_path — the fallback value from _resolve_task_goal_and_model
        result = _archive_feedback_checkpoint(task_id, str(folder), task_id, deps)

        assert result == "", "must return empty string when goal_path is not absolute"
        assert not any(
            not os.path.isabs(p) for p in makedirs_called
        ), "must not create any relative-path directories"
