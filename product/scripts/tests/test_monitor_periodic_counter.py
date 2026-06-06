#!/usr/bin/env python3
"""Tests for scripts/optimize/monitor_periodic_counter.py (REQ-PROC-006 IMPL-C).

Covers the threshold fire condition, the below-threshold/no-fire case, the
configurable threshold, and the single-pending-event idempotency.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "optimize"))
import monitor_periodic_counter as m  # type: ignore[import-not-found]  # sys.path mutated above

NOW = datetime(2026, 5, 28, 12, 0, 0, tzinfo=timezone.utc)


def test_fires_at_default_threshold():
    events = m.detect(NOW, state={"completions_since_last_run": 10})
    assert len(events) == 1
    assert events[0].event_type == "periodic"
    assert events[0].confidence == "low"
    assert events[0].payload["threshold"] == m.DEFAULT_THRESHOLD


def test_no_fire_below_threshold():
    assert m.detect(NOW, state={"completions_since_last_run": 9}) == []


def test_respects_configured_threshold():
    state = {"completions_since_last_run": 4, "periodic_counter_threshold": 4}
    assert len(m.detect(NOW, state=state)) == 1


def test_run_keeps_single_pending_event(tmp_path, monkeypatch):
    # run() reads real state via load_state; force the threshold-met state.
    monkeypatch.setattr(m.mc, "load_state", lambda: {"completions_since_last_run": 50})
    first = m.run(now=NOW, events_dir=tmp_path)
    second = m.run(now=NOW, events_dir=tmp_path)
    assert len(first) == 1
    assert second == []
    assert len(list(tmp_path.glob("*.json"))) == 1
