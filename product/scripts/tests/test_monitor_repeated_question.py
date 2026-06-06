#!/usr/bin/env python3
"""Tests for scripts/optimize/monitor_repeated_question.py (REQ-PROC-006 IMPL-C).

Covers the >=3-repeat fire condition, the per-body normalization, and the
cooldown idempotency (run twice -> one event).
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "optimize"))
import monitor_repeated_question as m  # type: ignore[import-not-found]  # sys.path mutated above

NOW = datetime(2026, 5, 28, 12, 0, 0, tzinfo=timezone.utc)


def _write_question(feedback_dir, task_id, body):
    qdir = feedback_dir / task_id
    qdir.mkdir(parents=True)
    (qdir / "question.md").write_text(
        f"---\ntask_id: {task_id}\nstatus: awaiting_answer\n---\n\n{body}\n",
        encoding="utf-8",
    )


def test_fires_when_body_repeats_three_times(tmp_path):
    body = "Should the export screen use a QR code or a deep link?"
    for i in range(3):
        _write_question(tmp_path, f"TASK-{i}", body)
    events = m.detect(NOW, feedback_dir=tmp_path)
    assert len(events) == 1
    assert events[0].event_type == "repeated_question"
    assert events[0].confidence == "high"
    assert events[0].payload["count"] == 3


def test_no_fire_below_threshold(tmp_path):
    body = "A one-off question."
    for i in range(2):
        _write_question(tmp_path, f"TASK-{i}", body)
    assert m.detect(NOW, feedback_dir=tmp_path) == []


def test_normalization_ignores_whitespace_and_case(tmp_path):
    _write_question(tmp_path, "TASK-0", "Same   Question?")
    _write_question(tmp_path, "TASK-1", "same question?")
    _write_question(tmp_path, "TASK-2", "SAME\nQUESTION?")
    events = m.detect(NOW, feedback_dir=tmp_path)
    assert len(events) == 1


def test_run_is_idempotent_within_cooldown(tmp_path):
    feedback = tmp_path / "feedback"
    events = tmp_path / "events"
    body = "Repeated decision question?"
    for i in range(3):
        _write_question(feedback, f"TASK-{i}", body)
    first = m.run(now=NOW, feedback_dir=feedback, events_dir=events)
    second = m.run(now=NOW, feedback_dir=feedback, events_dir=events)
    assert len(first) == 1
    assert second == []
    assert len(list(events.glob("*.json"))) == 1
