#!/usr/bin/env python3
"""Smoke test: task-complete skill wires run_monitors.py post-commit (IMPL-F / TASK-PROC-006-11).

Verifies that .claude/skills/task-complete/SKILL.md:
  1. Invokes run_monitors.py after the Commit step
  2. Documents the SKIP_QUALITY_GATES=1 skip condition
  3. Documents failure-continuation behaviour (monitor crash must not abort)
"""

from pathlib import Path

SKILL_MD = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "task-complete" / "SKILL.md"


def _text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def test_skill_references_run_monitors() -> None:
    assert "run_monitors.py" in _text(), "SKILL.md must invoke run_monitors.py"


def test_monitor_wiring_is_post_commit() -> None:
    text = _text()
    commit_pos = text.find("**Commit**")
    monitor_pos = text.find("run_monitors.py")
    assert commit_pos != -1, "SKILL.md must have a Commit step"
    assert monitor_pos != -1, "SKILL.md must reference run_monitors.py"
    assert monitor_pos > commit_pos, "Monitor sweep must appear AFTER the Commit step"


def test_skill_has_skip_quality_gates_condition() -> None:
    assert "SKIP_QUALITY_GATES" in _text(), (
        "Monitor wiring must document skipping when SKIP_QUALITY_GATES=1"
    )


def test_skill_documents_failure_continuation() -> None:
    text = _text()
    assert "continue" in text.lower(), (
        "SKILL.md must document that a monitor failure does not abort task-complete"
    )
