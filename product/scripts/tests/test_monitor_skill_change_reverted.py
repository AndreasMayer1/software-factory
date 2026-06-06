#!/usr/bin/env python3
"""Tests for scripts/optimize/monitor_skill_change_reverted.py (REQ-PROC-006 IMPL-C).

Covers the "edited then net-zero diff" revert detection via a fake GitRunner and
the cooldown idempotency (run twice -> one event).
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "optimize"))
import monitor_common as mc  # type: ignore[import-not-found]  # sys.path mutated above
import monitor_skill_change_reverted as m  # type: ignore[import-not-found]  # sys.path mutated above

NOW = datetime(2026, 5, 28, 12, 0, 0, tzinfo=timezone.utc)
SKILL = ".claude/skills/foo/SKILL.md"
OTHER = ".claude/skills/bar/SKILL.md"


def _log_two_commits_for(skill):
    return (
        f"{mc._COMMIT_MARKER}sha2\nM\t{skill}\n"
        f"{mc._COMMIT_MARKER}sha1\nM\t{skill}\n"
    )


def _fake_git(log, diffs):
    def run(args):
        if args[0] == "log":
            return log
        if args[0] == "diff":
            return diffs.get(args[-1], "some leftover change\n")
        return ""

    return run


def test_fires_when_net_diff_empty(tmp_path):
    git = _fake_git(_log_two_commits_for(SKILL), {SKILL: ""})
    events = m.detect(NOW, git=git)
    assert len(events) == 1
    assert events[0].fingerprint == SKILL
    assert events[0].confidence == "high"


def test_no_fire_when_net_diff_nonempty(tmp_path):
    git = _fake_git(_log_two_commits_for(SKILL), {SKILL: "real change\n"})
    assert m.detect(NOW, git=git) == []


def test_no_fire_with_single_commit(tmp_path):
    # Only one commit in the window -> not an edit-then-undo.
    log = f"{mc._COMMIT_MARKER}sha1\nM\t{OTHER}\n"
    git = _fake_git(log, {OTHER: ""})
    assert m.detect(NOW, git=git) == []


def test_run_is_idempotent_within_cooldown(tmp_path):
    git = _fake_git(_log_two_commits_for(SKILL), {SKILL: ""})
    first = m.run(now=NOW, git=git, events_dir=tmp_path)
    second = m.run(now=NOW, git=git, events_dir=tmp_path)
    assert len(first) == 1
    assert second == []
    assert len(list(tmp_path.glob("*.json"))) == 1
