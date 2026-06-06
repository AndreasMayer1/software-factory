#!/usr/bin/env python3
"""Monitor: N completed tasks since the last optimize run (REQ-PROC-006 IMPL-C).

Signal: a low-confidence safety net so claude-optimize runs at least periodically
even when no high-signal event fired. Fires a `periodic` event (confidence Low)
when `completions_since_last_run` in state.json reaches `periodic_counter_threshold`
(default 10, configurable in state.json).

Idempotent: only one pending `periodic` event exists at a time — emit_once with a
constant fingerprint and a long window acts as a "one pending event" guard until
claude-optimize consumes it and resets the counter.

Reads only state.json — committed, project-local. No session JSONL (G-INV-2).
"""

# tier: B  # imported by run_monitors.py and its tests

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

_OPTIMIZE_DIR = str(Path(__file__).resolve().parent)
if _OPTIMIZE_DIR not in sys.path:
    sys.path.insert(0, _OPTIMIZE_DIR)

import monitor_common as mc  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation

EVENT_TYPE = "periodic"
FINGERPRINT = "periodic"
DEFAULT_THRESHOLD = 10
# A long window so emit_once only suppresses while an un-consumed periodic event
# is still pending; the counter reset by claude-optimize is the real re-arm.
COOLDOWN = timedelta(days=3650)


def detect(now: datetime, state: dict[str, object] | None = None) -> list[mc.Event]:
    """Return a periodic event when the completion counter has reached the threshold."""
    state = mc.load_state() if state is None else state
    completions = mc.as_int(state.get("completions_since_last_run"), 0)
    threshold = mc.as_int(state.get("periodic_counter_threshold"), DEFAULT_THRESHOLD)
    if completions < threshold:
        return []
    return [
        mc.Event(
            event_type=EVENT_TYPE,
            confidence=mc.CONFIDENCE_LOW,
            fingerprint=FINGERPRINT,
            created=now,
            payload={"completions": completions, "threshold": threshold},
        )
    ]


def run(
    now: datetime | None = None,
    events_dir: Path = mc.EVENTS_DIR,
) -> list[Path]:
    """Detect the periodic trigger and emit at most one pending periodic event."""
    now = now or mc.utc_now()
    written: list[Path] = []
    for event in detect(now):
        path = mc.emit_once(event, COOLDOWN, now, events_dir)
        if path is not None:
            written.append(path)
    return written
