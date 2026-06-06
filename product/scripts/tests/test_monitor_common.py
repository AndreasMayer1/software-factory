#!/usr/bin/env python3
"""Tests for scripts/optimize/monitor_common.py (REQ-PROC-006 IMPL-C).

Covers the event JSON/filename shape, the cooldown-window idempotency guard,
int coercion, and the single-call git-log parser (via a fake GitRunner).
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "optimize"))
import monitor_common as mc  # type: ignore[import-not-found]  # sys.path mutated above

NOW = datetime(2026, 5, 28, 12, 0, 0, tzinfo=timezone.utc)


def _event(fingerprint="abc", created=NOW, event_type="periodic"):
    return mc.Event(
        event_type=event_type,
        confidence=mc.CONFIDENCE_LOW,
        fingerprint=fingerprint,
        created=created,
        payload={"k": "v"},
    )


def test_write_event_roundtrip(tmp_path):
    path = mc.write_event(_event(), events_dir=tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["event_type"] == "periodic"
    assert data["fingerprint"] == "abc"
    assert data["created"] == "2026-05-28T12:00:00Z"
    assert data["payload"] == {"k": "v"}


def test_filename_is_filesystem_safe():
    name = _event(fingerprint=".claude/skills/foo@SHA").filename()
    assert name == "20260528T120000Z-periodic-claude-skills-foo-sha.json"
    assert "/" not in name
    assert "@" not in name


def test_recent_event_exists_within_window(tmp_path):
    mc.write_event(_event(), events_dir=tmp_path)
    assert mc.recent_event_exists("periodic", "abc", NOW, timedelta(days=1), tmp_path)


def test_recent_event_expired_outside_window(tmp_path):
    mc.write_event(_event(created=NOW - timedelta(days=2)), events_dir=tmp_path)
    assert not mc.recent_event_exists(
        "periodic", "abc", NOW, timedelta(days=1), tmp_path
    )


def test_recent_event_distinct_fingerprint(tmp_path):
    mc.write_event(_event(fingerprint="abc"), events_dir=tmp_path)
    assert not mc.recent_event_exists(
        "periodic", "other", NOW, timedelta(days=1), tmp_path
    )


def test_emit_once_suppresses_duplicate(tmp_path):
    first = mc.emit_once(_event(), timedelta(days=14), NOW, tmp_path)
    second = mc.emit_once(_event(), timedelta(days=14), NOW, tmp_path)
    assert first is not None
    assert second is None
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_as_int_ignores_bool_and_non_int():
    assert mc.as_int(5) == 5
    assert mc.as_int(True, 0) == 0  # bool is a subclass of int but not a count
    assert mc.as_int("7", 3) == 3
    assert mc.as_int(None, 9) == 9


def test_skill_commits_in_window_parses_single_log_call():
    log = (
        f"{mc._COMMIT_MARKER}sha2\n"
        "M\t.claude/skills/foo/SKILL.md\n"
        f"{mc._COMMIT_MARKER}sha1\n"
        "M\t.claude/skills/foo/SKILL.md\n"
        "A\t.claude/skills/bar/SKILL.md\n"
    )
    calls = []

    def fake_git(args):
        calls.append(args)
        return log

    result = mc.skill_commits_in_window("2026-05-26T12:00:00", fake_git)
    assert result[".claude/skills/foo/SKILL.md"] == ["sha2", "sha1"]
    assert result[".claude/skills/bar/SKILL.md"] == ["sha1"]
    assert len(calls) == 1  # one git invocation total
