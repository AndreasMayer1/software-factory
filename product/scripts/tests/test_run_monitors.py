#!/usr/bin/env python3
"""Tests for scripts/optimize/run_monitors.py (REQ-PROC-006 IMPL-C).

Covers exit-code/event aggregation, the per-monitor boundary guard (a raising
monitor is recorded, the rest still run), and the <2s runtime target on an
effectively empty event queue.
"""

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "optimize"))
import monitor_common as mc  # type: ignore[import-not-found]  # sys.path mutated above
import run_monitors as rm  # type: ignore[import-not-found]  # sys.path mutated above

NOW = datetime(2026, 5, 28, 12, 0, 0, tzinfo=timezone.utc)
_LOW_COMPLETIONS = {"completions_since_last_run": 0}


def test_run_all_aggregates_events_and_errors(tmp_path, monkeypatch):
    def good(now=None, events_dir=None):
        return [Path("a.json"), Path("b.json")]

    def bad(now=None, events_dir=None):
        raise ValueError("boom")

    monkeypatch.setattr(rm, "MONITORS", [("good", good), ("bad", bad)])
    monkeypatch.setattr(mc, "load_state", lambda: _LOW_COMPLETIONS)
    written, errors = rm.run_all(now=NOW, events_dir=tmp_path)
    assert len(written) == 2
    assert len(errors) == 1
    assert "bad: boom" in errors[0]


def test_main_exit_code_reflects_errors(tmp_path, monkeypatch, capsys):
    def bad(now=None, events_dir=None):
        raise RuntimeError("nope")

    monkeypatch.setattr(rm, "MONITORS", [("bad", bad)])
    monkeypatch.setattr(mc, "load_state", lambda: _LOW_COMPLETIONS)
    # Neutralize cycle-task creation (main([]) uses the real events dir).
    monkeypatch.setattr(rm.cycle, "create_cycle_task", lambda *a, **k: None)
    assert rm.main([]) == 1
    err = capsys.readouterr().err
    assert "monitor-error: bad: nope" in err


def test_main_exit_zero_when_clean(monkeypatch):
    monkeypatch.setattr(rm, "MONITORS", [("noop", lambda now=None, events_dir=None: [])])
    monkeypatch.setattr(mc, "load_state", lambda: _LOW_COMPLETIONS)
    # Autonomous cycle-task creation is exercised in test_create_optimize_cycle_task;
    # neutralize it here so this monitor/aggregator test does not touch real tasks.
    monkeypatch.setattr(rm.cycle, "create_cycle_task", lambda *a, **k: None)
    assert rm.main([]) == 0


def test_runs_under_two_seconds(tmp_path, monkeypatch):
    # Real monitors against the live repo, but events written to a temp dir.
    # Prevent aggregator invocation so its subprocess latency doesn't skew the timing.
    monkeypatch.setattr(mc, "load_state", lambda: _LOW_COMPLETIONS)
    # Cycle-task creation covered elsewhere; neutralize to keep this a pure timing test.
    monkeypatch.setattr(rm.cycle, "create_cycle_task", lambda *a, **k: None)
    start = time.perf_counter()
    _written, errors = rm.run_all(now=NOW, events_dir=tmp_path)
    elapsed = time.perf_counter() - start
    assert errors == []
    assert elapsed < 2.0, f"monitors took {elapsed:.3f}s (target <2s)"


def test_aggregator_invoked_when_threshold_met(monkeypatch):
    monkeypatch.setattr(rm, "MONITORS", [])
    monkeypatch.setattr(mc, "load_state", lambda: {"completions_since_last_run": 5})
    called: list[int] = []
    monkeypatch.setattr(rm, "_invoke_aggregator", lambda: called.append(1))
    rm.run_all(events_dir=Path("/tmp/no-events"))
    assert called == [1]


def test_aggregator_not_invoked_below_threshold(monkeypatch):
    monkeypatch.setattr(rm, "MONITORS", [])
    monkeypatch.setattr(mc, "load_state", lambda: {"completions_since_last_run": 4})
    called: list[int] = []
    monkeypatch.setattr(rm, "_invoke_aggregator", lambda: called.append(1))
    rm.run_all(events_dir=Path("/tmp/no-events"))
    assert called == []
