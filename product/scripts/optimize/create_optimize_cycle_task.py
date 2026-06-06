#!/usr/bin/env python3
"""Scaffold the autonomous claude-optimize *cycle* task (REQ-PROC-006 §Monitor-Based Detection).

This is the F-1 fix for TASK-PROC-006-18: monitors were emitting events into
``.factory/optimize/events/`` but nothing created the autonomous task the
orchestrator picks up to run the producer skill. This helper closes that gap.

Distinct from ``create_optimize_task.py``:

* ``create_optimize_task.py`` mints the *downstream proposal* task — the output
  of the claude-optimize producer skill — hard-coded ``awaiting: ["user-unblock"]``
  (G-INV-1, the non-removable auto-block).
* THIS module mints the *autonomous cycle* task — ``type: optimize`` with
  ``awaiting: []`` — which, when the orchestrator runs it via task-start → claude-route →
  claude-optimize, invokes the producer skill which in turn calls
  ``create_optimize_task.py``. The two are deliberately separate: the cycle task
  runs unattended, the proposal it produces does not.

Invoked from ``run_monitors.py`` after the monitor sweep, inside that module's
process-boundary guard (a failure here must never crash task-complete).

Idempotency: a new cycle task is created only when (a) the event queue is
non-empty AND (b) no ``type: optimize`` task is currently pending/in_progress.
Running twice while one is pending is a no-op (returns None).

Task ID scheme: ``TASK-OPT-0-<n>`` where ``<n>`` is a monotone counter persisted
in ``state.json`` under ``optimize_task_seq``. Validates against the goal_metadata
schema pattern ``TASK-[A-Z]+-[0-9]+-[0-9]+(-[0-9]+)?``; the ``OPT`` namespace avoids
collision with hand-allocated ``TASK-PROC-006-*`` IDs and the heavyweight
``allocate_task_id.py`` (reserve markers, requirement path) is unnecessary for an
ephemeral per-cycle task.
"""

# tier: B  # reusable helper imported by run_monitors.py

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

_OPTIMIZE_DIR = str(Path(__file__).resolve().parent)
if _OPTIMIZE_DIR not in sys.path:
    sys.path.insert(0, _OPTIMIZE_DIR)
# scripts/ on path so ``util.yaml_frontmatter`` (the central AC-08 parser) imports.
_SCRIPTS_DIR = str(Path(__file__).resolve().parents[1])
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import monitor_common as mc  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation

# The single known parent folder for autonomous optimize cycle tasks — same
# location the concept (round-3 §2.2) placed it and where the rest of the
# claude-optimize workstream lives.
OPTIMIZE_TASKS_DIR = (
    mc.PROJECT_ROOT
    / "requirements_tasks"
    / "process"
    / "AI_rules"
    / "workflows"
    / "workflow_improvement_automation"
    / "tasks"
)

# state.json key holding the monotone cycle-task counter.
_SEQ_KEY = "optimize_task_seq"

# Statuses that mean an existing optimize task still occupies the queue slot.
_PENDING_STATUSES = frozenset({"pending", "in_progress"})


def _read_type_and_status(goal_file: Path) -> tuple[str, str]:
    """Return (type, status) from a goal.md frontmatter, lowercased; ("", "") on failure."""
    # Read-only frontmatter access via the central helper (AC-08; no hand-rolled
    # YAML). Pass the Path (not the text) so the helper's path/text auto-detect
    # reads the file directly rather than calling Path(text).exists() on content.
    from util.yaml_frontmatter import (  # type: ignore[import-not-found]
        FrontmatterError,
        read_frontmatter,
    )

    try:
        meta = read_frontmatter(goal_file).metadata
    except (OSError, FrontmatterError):
        # Unreadable or malformed/legacy goal.md must not block the scan — treat
        # as non-matching (it is not a pending optimize task).
        return "", ""
    if not isinstance(meta, dict):
        return "", ""
    return (
        str(meta.get("type", "")).strip().lower(),
        str(meta.get("status", "")).strip().lower(),
    )


def optimize_task_pending(tasks_dir: Path = OPTIMIZE_TASKS_DIR) -> bool:
    """True if a ``type: optimize`` task with a pending/in_progress status exists.

    Shallow scan of immediate task subfolders' ``goal.md`` (tens of dirs). Chosen
    over a state.json pointer so a crashed session that created a task but never
    updated state cannot cause duplicate cycle tasks forever (the on-disk task is
    the source of truth).
    """
    if not tasks_dir.is_dir():
        return False
    for goal_file in tasks_dir.glob("*/goal.md"):
        task_type, status = _read_type_and_status(goal_file)
        if task_type == "optimize" and status in _PENDING_STATUSES:
            return True
    return False


def _next_seq(state_path: Path) -> int:
    """Return the next cycle-task sequence number (current + 1) without persisting."""
    state = mc.load_state(state_path)
    # int() pins the type: mc is imported under type: ignore[import-not-found],
    # so mc.as_int(...) is seen as Any by mypy (G2 no-any-return otherwise).
    return int(mc.as_int(state.get(_SEQ_KEY))) + 1


def _persist_seq(state_path: Path, seq: int) -> None:
    """Write the bumped counter back into state.json, preserving other keys."""
    state = mc.load_state(state_path)
    state[_SEQ_KEY] = seq
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _events_present(events_dir: Path) -> bool:
    """True if at least one event JSON file sits in the queue."""
    return events_dir.is_dir() and any(events_dir.glob("*.json"))


def _render_goal_md(task_id: str, created_date: str) -> str:
    """Render the autonomous cycle task's goal.md.

    ``type: optimize`` routes via task-start → claude-route → claude-optimize. ``awaiting: []``
    is the load-bearing distinction from downstream proposals (which carry
    ``awaiting: ["user-unblock"]`` via create_optimize_task.py): the cycle task
    runs unattended; only its produced proposal is auto-blocked (G-INV-1 / AC-04).
    """
    return (
        "---\n"
        f"task_id: {task_id}\n"
        "type: optimize\n"
        "parent_requirement: REQ-PROC-006\n"
        "status: pending\n"
        f"created: {created_date}\n"
        # awaiting: [] — autonomous. NOT the downstream proposal's auto-block.
        "awaiting: []\n"
        'scope_description: "Autonomous claude-optimize cycle: consume one optimize '
        'event, produce one auto-blocked improvement task or a documented no-op."\n'
        "---\n"
        "\n"
        "# Goal: run one claude-optimize producer cycle\n"
        "\n"
        "## Objective\n"
        "\n"
        "Monitors emitted at least one event into `.factory/optimize/events/`.\n"
        "Run the claude-optimize producer skill once: select the highest-priority\n"
        "candidate, produce exactly one auto-blocked improvement task (via\n"
        "`create_optimize_task.py`) or a documented no-op, and commit `runs.tsv`\n"
        "and `state.json` (REQ-PROC-006 §Producer Paradigm, §Commit Behavior).\n"
        "\n"
        "## Source\n"
        "\n"
        "Created autonomously by `scripts/optimize/run_monitors.py` "
        "(REQ-PROC-006 §Monitor-Based Detection). This cycle task runs\n"
        "unattended (`awaiting: []`); only the improvement task it produces is\n"
        'auto-blocked (`awaiting: ["user-unblock"]`, G-INV-1 / AC-04).\n'
    )


def create_cycle_task(
    now: datetime,
    events_dir: Path = mc.EVENTS_DIR,
    tasks_dir: Path = OPTIMIZE_TASKS_DIR,
    state_path: Path = mc.STATE_PATH,
) -> Path | None:
    """Scaffold one autonomous optimize cycle task, or no-op.

    Returns the written goal.md path, or None when no task was created (empty
    event queue, or an optimize task is already pending). Idempotent: a second
    call while a task is pending returns None.
    """
    if not _events_present(events_dir):
        return None
    if optimize_task_pending(tasks_dir):
        return None

    seq = _next_seq(state_path)
    task_id = f"TASK-OPT-0-{seq}"
    # Folder/date use OS-local time (timezone rule — file/stdout values are local).
    created_date = now.astimezone().strftime("%Y-%m-%d")
    folder = tasks_dir / f"{created_date}_optimize_cycle-{seq}"
    folder.mkdir(parents=True, exist_ok=True)
    goal_path = folder / "goal.md"
    goal_path.write_text(_render_goal_md(task_id, created_date), encoding="utf-8")
    # Persist only after the task is on disk, so a crash mid-write cannot advance
    # the counter past a task that was never created.
    _persist_seq(state_path, seq)
    return goal_path
