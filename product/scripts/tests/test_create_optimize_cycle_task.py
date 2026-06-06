#!/usr/bin/env python3
"""Tests for scripts/optimize/create_optimize_cycle_task.py (REQ-PROC-006 F-1).

Pins the autonomous-cycle-task creation chain (TASK-PROC-006-18): events present
+ no pending optimize task -> exactly one type:optimize, awaiting:[] task; a second
call while one is pending -> no second task. Also exercises run_monitors.run_all
end-to-end so the wired creation path is covered (not just the helper).
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "optimize"))
import create_optimize_cycle_task as cct  # type: ignore[import-not-found]  # sys.path mutated above
import run_monitors as rm  # type: ignore[import-not-found]  # sys.path mutated above

NOW = datetime(2026, 5, 30, 9, 0, 0, tzinfo=timezone.utc)


def _write_event(events_dir: Path, name: str = "evt") -> None:
    events_dir.mkdir(parents=True, exist_ok=True)
    (events_dir / f"20260530T090000Z-periodic-{name}.json").write_text(
        json.dumps({"event_type": "periodic", "confidence": "low", "fingerprint": name}),
        encoding="utf-8",
    )


def _read_frontmatter_lines(goal_path: Path) -> list[str]:
    text = goal_path.read_text(encoding="utf-8")
    return text.splitlines()


def test_creates_one_autonomous_optimize_task(tmp_path):
    events = tmp_path / "events"
    tasks = tmp_path / "tasks"
    state = tmp_path / "state.json"
    _write_event(events)

    path = cct.create_cycle_task(
        now=NOW, events_dir=events, tasks_dir=tasks, state_path=state
    )

    assert path is not None
    assert path.name == "goal.md"
    lines = _read_frontmatter_lines(path)
    assert "type: optimize" in lines
    assert "awaiting: []" in lines
    assert "parent_requirement: REQ-PROC-006" in lines
    # task_id must validate against the goal_metadata schema pattern.
    task_id_line = next(line for line in lines if line.startswith("task_id:"))
    task_id = task_id_line.split(":", 1)[1].strip()
    import re

    assert re.fullmatch(r"TASK-[A-Z]+-[0-9]+-[0-9]+(-[0-9]+)?", task_id), task_id
    assert task_id == "TASK-OPT-0-1"
    # Counter persisted.
    assert json.loads(state.read_text())["optimize_task_seq"] == 1


def test_idempotent_while_pending(tmp_path):
    events = tmp_path / "events"
    tasks = tmp_path / "tasks"
    state = tmp_path / "state.json"
    _write_event(events)

    first = cct.create_cycle_task(
        now=NOW, events_dir=events, tasks_dir=tasks, state_path=state
    )
    assert first is not None

    # Second call while the first (status: pending) task is on disk -> no-op.
    second = cct.create_cycle_task(
        now=NOW, events_dir=events, tasks_dir=tasks, state_path=state
    )
    assert second is None
    created = list(tasks.glob("*/goal.md"))
    assert len(created) == 1


def test_no_task_when_events_empty(tmp_path):
    events = tmp_path / "events"
    events.mkdir()
    tasks = tmp_path / "tasks"
    state = tmp_path / "state.json"

    path = cct.create_cycle_task(
        now=NOW, events_dir=events, tasks_dir=tasks, state_path=state
    )
    assert path is None
    assert not list(tasks.glob("*/goal.md"))


def test_resumes_after_pending_task_completes(tmp_path):
    events = tmp_path / "events"
    tasks = tmp_path / "tasks"
    state = tmp_path / "state.json"
    _write_event(events)

    first = cct.create_cycle_task(
        now=NOW, events_dir=events, tasks_dir=tasks, state_path=state
    )
    assert first is not None
    # Mark the first task completed -> no longer pending.
    completed = first.read_text().replace("status: pending", "status: completed")
    first.write_text(completed, encoding="utf-8")

    second = cct.create_cycle_task(
        now=NOW, events_dir=events, tasks_dir=tasks, state_path=state
    )
    assert second is not None
    assert second != first
    # Counter advanced monotonically.
    assert json.loads(state.read_text())["optimize_task_seq"] == 2


def test_run_all_creates_cycle_task_when_events_exist(tmp_path, monkeypatch):
    """End-to-end: run_monitors.run_all invokes the cycle helper via the wired call.

    The default tasks_dir/state_path point at the real repo, so the helper itself
    is faked to redirect them at temp dirs — this asserts the *wiring* (run_all
    calls create_cycle_task with the live now/events_dir), which is the F-1 gap.
    """
    events = tmp_path / "events"
    tasks = tmp_path / "tasks"
    state = tmp_path / "state.json"
    _write_event(events)

    # No real monitors; aggregator below threshold so it is not invoked.
    monkeypatch.setattr(rm, "MONITORS", [])
    import monitor_common as mc  # type: ignore[import-not-found]

    # run_all calls mc.load_state() (no arg) for the aggregator-threshold check;
    # the cycle helper calls mc.load_state(path). Accept both with *args.
    monkeypatch.setattr(
        mc, "load_state", lambda *a, **k: {"completions_since_last_run": 0}
    )

    captured: dict[str, object] = {}
    real_create = cct.create_cycle_task  # capture before patching to avoid recursion

    def fake_create(now, events_dir=None):
        captured["now"] = now
        captured["events_dir"] = events_dir
        return real_create(
            now=now, events_dir=events_dir, tasks_dir=tasks, state_path=state
        )

    monkeypatch.setattr(rm.cycle, "create_cycle_task", fake_create)

    _written, errors = rm.run_all(now=NOW, events_dir=events)

    assert errors == []
    # run_all passed the live now + events_dir into the cycle helper (the wiring).
    assert captured["now"] == NOW
    assert captured["events_dir"] == events
    created = list(tasks.glob("*/goal.md"))
    assert len(created) == 1
    assert "type: optimize" in created[0].read_text()
