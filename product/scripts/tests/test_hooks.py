# tier: B  # test suite — imported by pytest, exercises .claude/hooks/ shell scripts
"""Tests for the Claude Code hook scripts in .claude/hooks/.

Each hook receives a JSON payload on stdin and produces stdout + an exit code.
Tests invoke the scripts via subprocess, supplying the JSON input directly,
so the full shell pipeline is exercised without Claude Code running.
"""

from __future__ import annotations

import json
import os
import subprocess
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
HOOKS_DIR = PROJECT_ROOT / ".claude" / "hooks"


def run_hook(
    script: Path,
    stdin_data: dict[str, object],
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a hook script with a JSON payload on stdin."""
    merged = {**os.environ, **(env or {})}
    return subprocess.run(
        ["bash", str(script)],
        input=json.dumps(stdin_data),
        capture_output=True,
        text=True,
        env=merged,
        cwd=str(PROJECT_ROOT),
    )


# ---------------------------------------------------------------------------
# pre_edit_scripts_reminder.sh
# ---------------------------------------------------------------------------


class TestPreEditScriptsReminder:
    """Injects reminder JSON only for scripts/*.py|.ps1 edits; silent otherwise."""

    _script = HOOKS_DIR / "pre_edit_scripts_reminder.sh"

    def test_python_in_scripts_triggers_reminder(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": "scripts/tasks/foo.py"}})
        assert result.returncode == 0
        data = json.loads(result.stdout.strip())
        assert "hookSpecificOutput" in data
        assert "REMINDER" in data["hookSpecificOutput"]["additionalContext"]

    def test_ps1_in_scripts_triggers_reminder(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": "scripts/windows/foo.ps1"}})
        assert result.returncode == 0
        data = json.loads(result.stdout.strip())
        assert "hookSpecificOutput" in data

    def test_nested_python_triggers_reminder(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": "scripts/quality/check_gates.py"}})
        assert result.returncode == 0
        assert "hookSpecificOutput" in json.loads(result.stdout.strip())

    def test_dart_file_no_output(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": "lib/foo.dart"}})
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_markdown_no_output(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": "requirements_tasks/foo.md"}})
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_python_outside_scripts_no_output(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": "lib/foo.py"}})
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_empty_path_no_output(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": ""}})
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_missing_file_path_key_no_output(self) -> None:
        result = run_hook(self._script, {"tool_input": {}})
        assert result.returncode == 0
        assert result.stdout.strip() == ""


# ---------------------------------------------------------------------------
# pre_bash_commit_gate.sh
# ---------------------------------------------------------------------------


class TestPreBashCommitGate:
    """Intercepts git commit; bypasses all other Bash commands immediately."""

    _script = HOOKS_DIR / "pre_bash_commit_gate.sh"

    def test_non_git_command_silent_pass(self) -> None:
        result = run_hook(self._script, {"tool_input": {"command": "ls -la"}})
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_git_status_silent_pass(self) -> None:
        result = run_hook(self._script, {"tool_input": {"command": "git status"}})
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_empty_command_silent_pass(self) -> None:
        result = run_hook(self._script, {"tool_input": {"command": ""}})
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_skip_quality_gates_env_bypasses(self) -> None:
        result = run_hook(
            self._script,
            {"tool_input": {"command": "git commit -m 'test'"}},
            env={"SKIP_QUALITY_GATES": "1"},
        )
        assert result.returncode == 0
        assert "SKIPPED" in result.stderr

    def test_git_commit_no_staged_dart_files_bypasses(self) -> None:
        # Current repo has no staged files under lib/test/integration_test —
        # the gate auto-bypasses with a message to stderr.
        result = run_hook(self._script, {"tool_input": {"command": "git commit -m 'test'"}})
        assert result.returncode == 0

    def test_leading_whitespace_in_git_commit_detected(self) -> None:
        result = run_hook(
            self._script,
            {"tool_input": {"command": "  git  commit -m 'test'"}},
            env={"SKIP_QUALITY_GATES": "1"},
        )
        assert result.returncode == 0
        assert "SKIPPED" in result.stderr


# ---------------------------------------------------------------------------
# pre_read_log_event.sh
# ---------------------------------------------------------------------------


class TestPreReadLogEvent:
    """Logs a Read event to the session JSONL when CLAUDE_SESSION_ID is set."""

    _script = HOOKS_DIR / "pre_read_log_event.sh"

    def test_no_session_id_exits_cleanly(self) -> None:
        env: dict[str, str] = {k: v for k, v in os.environ.items() if k != "CLAUDE_SESSION_ID"}
        env["CLAUDE_SESSION_ID"] = ""
        result = run_hook(self._script, {"tool_input": {"file_path": "lib/foo.dart"}}, env=env)
        assert result.returncode == 0

    def test_logs_entry_with_session_id(self) -> None:
        session_id = f"test-hook-pre-read-{uuid.uuid4().hex[:8]}"
        log_dir = PROJECT_ROOT / ".factory" / "session_logs" / session_id
        log_file = log_dir / "read_events.jsonl"
        try:
            result = run_hook(
                self._script,
                {"tool_input": {"file_path": "lib/foo.dart"}},
                env={"CLAUDE_SESSION_ID": session_id},
            )
            assert result.returncode == 0
            assert log_file.exists()
            entry = json.loads(log_file.read_text().strip().splitlines()[-1])
            assert entry["tool"] == "Read"
            assert entry["file_path"] == "lib/foo.dart"
            assert entry["session_id"] == session_id
            assert "timestamp" in entry
        finally:
            if log_file.exists():
                log_file.unlink()
            if log_dir.exists():
                log_dir.rmdir()

    def test_empty_file_path_no_log_written(self) -> None:
        session_id = f"test-hook-pre-read-empty-{uuid.uuid4().hex[:8]}"
        log_dir = PROJECT_ROOT / ".factory" / "session_logs" / session_id
        try:
            run_hook(
                self._script,
                {"tool_input": {"file_path": ""}},
                env={"CLAUDE_SESSION_ID": session_id},
            )
            assert not log_dir.exists()
        finally:
            if log_dir.exists():
                for f in log_dir.iterdir():
                    f.unlink()
                log_dir.rmdir()

    def test_kill_switch_disables_logging(self) -> None:
        # FACTORY_DISABLE_READ_LOG=1 lets operators cut per-Read hook overhead in
        # long sessions; the hook drains stdin then exits before creating the log.
        session_id = f"test-hook-pre-read-kill-{uuid.uuid4().hex[:8]}"
        log_dir = PROJECT_ROOT / ".factory" / "session_logs" / session_id
        try:
            result = run_hook(
                self._script,
                {"tool_input": {"file_path": "lib/foo.dart"}},
                env={"CLAUDE_SESSION_ID": session_id, "FACTORY_DISABLE_READ_LOG": "1"},
            )
            assert result.returncode == 0
            assert not log_dir.exists()
        finally:
            if log_dir.exists():
                for f in log_dir.iterdir():
                    f.unlink()
                log_dir.rmdir()


# ---------------------------------------------------------------------------
# post_edit_dart_fix.sh
# ---------------------------------------------------------------------------


class TestPostEditDartFix:
    """Runs dart fix only for .dart files; no-ops for all other paths."""

    _script = HOOKS_DIR / "post_edit_dart_fix.sh"

    def test_markdown_file_exits_cleanly(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": "requirements_tasks/foo.md"}})
        assert result.returncode == 0

    def test_empty_path_exits_cleanly(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": ""}})
        assert result.returncode == 0

    def test_python_file_exits_cleanly(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": "scripts/tasks/foo.py"}})
        assert result.returncode == 0

    def test_missing_key_exits_cleanly(self) -> None:
        result = run_hook(self._script, {"tool_input": {}})
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# post_edit_dart_analyze.sh
# ---------------------------------------------------------------------------


class TestPostEditDartAnalyze:
    """Runs dart analyze only for .dart files; no-ops for all other paths."""

    _script = HOOKS_DIR / "post_edit_dart_analyze.sh"

    def test_markdown_file_exits_cleanly(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": "requirements_tasks/foo.md"}})
        assert result.returncode == 0

    def test_empty_path_exits_cleanly(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": ""}})
        assert result.returncode == 0

    def test_python_file_exits_cleanly(self) -> None:
        result = run_hook(self._script, {"tool_input": {"file_path": "scripts/tasks/foo.py"}})
        assert result.returncode == 0

    def test_missing_key_exits_cleanly(self) -> None:
        result = run_hook(self._script, {"tool_input": {}})
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# post_read_log_bytes.sh
# ---------------------------------------------------------------------------


class TestPostReadLogBytes:
    """Appends a read_bytes entry to an existing session log; no-ops otherwise."""

    _script = HOOKS_DIR / "post_read_log_bytes.sh"

    def test_no_session_id_exits_cleanly(self) -> None:
        env: dict[str, str] = {k: v for k, v in os.environ.items() if k != "CLAUDE_SESSION_ID"}
        env["CLAUDE_SESSION_ID"] = ""
        result = run_hook(self._script, {"tool_input": {"file_path": "lib/foo.dart"}}, env=env)
        assert result.returncode == 0

    def test_session_without_log_file_exits_cleanly(self) -> None:
        session_id = f"test-hook-post-bytes-nofile-{uuid.uuid4().hex[:8]}"
        result = run_hook(
            self._script,
            {"tool_input": {"file_path": "lib/foo.dart"}},
            env={"CLAUDE_SESSION_ID": session_id},
        )
        assert result.returncode == 0

    def test_appends_entry_when_log_exists(self) -> None:
        session_id = f"test-hook-post-bytes-{uuid.uuid4().hex[:8]}"
        log_dir = PROJECT_ROOT / ".factory" / "session_logs" / session_id
        log_file = log_dir / "read_events.jsonl"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file.write_text("")
        try:
            result = run_hook(
                self._script,
                {"tool_input": {"file_path": "pubspec.yaml"}},
                env={"CLAUDE_SESSION_ID": session_id},
            )
            assert result.returncode == 0
            lines = [ln for ln in log_file.read_text().splitlines() if ln.strip()]
            assert len(lines) == 1
            entry = json.loads(lines[0])
            assert entry["type"] == "read_bytes"
            assert entry["file_path"] == "pubspec.yaml"
            assert entry["session_id"] == session_id
            assert isinstance(entry["bytes"], int)
            assert "timestamp" in entry
        finally:
            if log_file.exists():
                log_file.unlink()
            if log_dir.exists():
                log_dir.rmdir()

    def test_missing_file_path_key_exits_cleanly(self) -> None:
        session_id = f"test-hook-post-bytes-missing-{uuid.uuid4().hex[:8]}"
        result = run_hook(self._script, {"tool_input": {}}, env={"CLAUDE_SESSION_ID": session_id})
        assert result.returncode == 0

    def test_kill_switch_skips_append(self) -> None:
        # With FACTORY_DISABLE_READ_LOG=1 the hook drains stdin then exits without
        # appending, even when a session log already exists (REQ-PROC-067).
        session_id = f"test-hook-post-bytes-kill-{uuid.uuid4().hex[:8]}"
        log_dir = PROJECT_ROOT / ".factory" / "session_logs" / session_id
        log_file = log_dir / "read_events.jsonl"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file.write_text("")
        try:
            result = run_hook(
                self._script,
                {"tool_input": {"file_path": "pubspec.yaml"}},
                env={"CLAUDE_SESSION_ID": session_id, "FACTORY_DISABLE_READ_LOG": "1"},
            )
            assert result.returncode == 0
            assert log_file.read_text() == ""
        finally:
            if log_file.exists():
                log_file.unlink()
            if log_dir.exists():
                log_dir.rmdir()


# ---------------------------------------------------------------------------
# post_tool_use_inbox.sh
# ---------------------------------------------------------------------------


class TestPostToolUseInbox:
    """Catch-all PostToolUse hook: drains stdin (pipe-safe) and delivers operator messages."""

    _script = HOOKS_DIR / "post_tool_use_inbox.sh"
    _inbox = PROJECT_ROOT / "automation" / "inbox.md"

    def test_large_payload_drained_exits_cleanly(self) -> None:
        # A 200 KB tool_result must not break the pipe: the hook drains stdin via
        # `cat >/dev/null` before doing anything else (REQ-PROC-067 AC-02, #63966).
        result = run_hook(self._script, {"tool_result": "x" * 200_000})
        assert result.returncode == 0

    def test_operator_message_delivered_and_cleared(self) -> None:
        original = self._inbox.read_text() if self._inbox.exists() else None
        try:
            self._inbox.parent.mkdir(parents=True, exist_ok=True)
            self._inbox.write_text("PING from operator test\n")
            result = run_hook(self._script, {"tool_result": "ok"})
            assert result.returncode == 0
            assert "OPERATOR MESSAGE" in result.stdout
            assert "PING from operator test" in result.stdout
            assert self._inbox.read_text() == ""  # atomically cleared
        finally:
            if original is not None:
                self._inbox.write_text(original)
            elif self._inbox.exists():
                self._inbox.unlink()

    def test_empty_inbox_no_output(self) -> None:
        original = self._inbox.read_text() if self._inbox.exists() else None
        try:
            self._inbox.parent.mkdir(parents=True, exist_ok=True)
            self._inbox.write_text("")
            result = run_hook(self._script, {"tool_result": "ok"})
            assert result.returncode == 0
            assert result.stdout.strip() == ""
        finally:
            if original is not None:
                self._inbox.write_text(original)
            elif self._inbox.exists():
                self._inbox.unlink()
