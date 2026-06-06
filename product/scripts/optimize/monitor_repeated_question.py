#!/usr/bin/env python3
"""Monitor: the same pending-question fingerprint repeated >=3 times (REQ-PROC-006 IMPL-C).

Signal: the developer keeps being asked structurally the same question across
tasks — a high-confidence sign that a skill, rule, or doc is unclear. Fires a
`repeated_question` event (confidence High) for any normalized question body that
appears at least REPEAT_THRESHOLD times across `automation/pending_feedback`.
Idempotent within a 14-day cooldown window.

Reads only committed project-local files (question.md). No session JSONL, no
per-account memory — G-INV-2 / REQ-PROC-006 AC-02.
"""

# tier: B  # imported by run_monitors.py and its tests

from __future__ import annotations

import sys
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path

# Resolve sibling (scripts/optimize) and scripts/ imports regardless of how the
# module is invoked (via run_monitors.py, directly, or under pytest).
_OPTIMIZE_DIR = str(Path(__file__).resolve().parent)
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
for _p in (_OPTIMIZE_DIR, _SCRIPTS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import monitor_common as mc  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    _split_frontmatter,
)

EVENT_TYPE = "repeated_question"
REPEAT_THRESHOLD = 3
COOLDOWN = timedelta(days=14)
PENDING_FEEDBACK_DIR = mc.PROJECT_ROOT / "automation" / "pending_feedback"


def _iter_question_bodies(feedback_dir: Path) -> Iterator[tuple[str, str]]:
    """Yield (task_dir_name, question_body) for every question.md under feedback_dir."""
    if not feedback_dir.is_dir():
        return
    for qpath in sorted(feedback_dir.glob("*/question.md")):
        try:
            text = qpath.read_text(encoding="utf-8")
        except OSError:
            continue
        _, body = _split_frontmatter(text)
        yield qpath.parent.name, body


def detect(now: datetime, feedback_dir: Path = PENDING_FEEDBACK_DIR) -> list[mc.Event]:
    """Return one event per question fingerprint seen at least REPEAT_THRESHOLD times."""
    seen: dict[str, list[str]] = {}
    for task_id, body in _iter_question_bodies(feedback_dir):
        if not body.strip():
            continue
        seen.setdefault(mc.fingerprint_text(body), []).append(task_id)
    events: list[mc.Event] = []
    for fingerprint, task_ids in seen.items():
        if len(task_ids) >= REPEAT_THRESHOLD:
            events.append(
                mc.Event(
                    event_type=EVENT_TYPE,
                    confidence=mc.CONFIDENCE_HIGH,
                    fingerprint=fingerprint,
                    created=now,
                    payload={"count": len(task_ids), "task_ids": sorted(task_ids)},
                )
            )
    return events


def run(
    now: datetime | None = None,
    feedback_dir: Path = PENDING_FEEDBACK_DIR,
    events_dir: Path = mc.EVENTS_DIR,
) -> list[Path]:
    """Detect repeated questions and emit at most one event per fingerprint/cooldown."""
    now = now or mc.utc_now()
    written: list[Path] = []
    for event in detect(now, feedback_dir):
        path = mc.emit_once(event, COOLDOWN, now, events_dir)
        if path is not None:
            written.append(path)
    return written
