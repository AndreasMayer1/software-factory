#!/usr/bin/env python3
"""Run all claude-optimize monitors after task-complete (REQ-PROC-006 IMPL-C).

Invoked as a plain Python process by the post-task-complete hook (wired later by
IMPL-F / TASK-PROC-006-11). It is NOT a tool any agent can call, shape, or
suppress — that is the G-INV-2 invariant. Runs the four structural-signal
monitors sequentially, then invokes the read-frequency aggregator when the
completion threshold is met; the whole run targets well under 2 seconds.

Monitor scripts read only committed, project-local sources (state.json, git
history, protocol/question files) — never session JSONL. The aggregator
(invoked rate-limited from this module) may read project-local session logs.

Event file schema — one JSON object per file, named
`<ISO8601-ts>-<event-type>-<fingerprint>.json`:

    {
      "event_type":  "repeated_question" | "skill_change_reverted"
                     | "skill_changed_and_used" | "periodic",
      "confidence":  "high" | "medium" | "low",
      "fingerprint": "<stable id used for idempotency / dedup>",
      "created":     "<UTC ISO-8601; machine-exchange value per the timezone rule>",
      "payload":     { monitor-specific fields }
    }

Output:
    stdout — one `event: <filename>` line per event written, then a
    `summary: <n> event(s), <m> error(s), <t>s` line.
    stderr — one `monitor-error: <name>: <exc>` line per monitor that raised.

Exit codes:
    0  all monitors ran (events may or may not have fired)
    1  one or more monitors raised
"""

# tier: C  # one-shot CLI orchestrator; no production importers

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path

_OPTIMIZE_DIR = str(Path(__file__).resolve().parent)
if _OPTIMIZE_DIR not in sys.path:
    sys.path.insert(0, _OPTIMIZE_DIR)

import create_optimize_cycle_task as cycle  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above
import monitor_common as mc  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
import monitor_periodic_counter as periodic  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above
import monitor_repeated_question as repeated  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above
import monitor_skill_change_first_use as first_use  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above
import monitor_skill_change_reverted as reverted  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above

# Each entry: (name, run). Every run() accepts now= and events_dir= keywords;
# monitor-specific sources fall back to their committed defaults.
MonitorRun = Callable[..., "list[Path]"]
MONITORS: list[tuple[str, MonitorRun]] = [
    ("repeated_question", repeated.run),
    ("skill_change_reverted", reverted.run),
    ("skill_change_first_use", first_use.run),
    ("periodic", periodic.run),
]

# Minimum completions_since_last_run before the read-frequency aggregator is invoked.
_AGGREGATOR_THRESHOLD = 5


def _invoke_aggregator() -> None:
    """Call aggregate_read_metrics --emit-events (subprocess; not a monitor, not a tool)."""
    script = mc.PROJECT_ROOT / "scripts" / "factory" / "aggregate_read_metrics.py"
    subprocess.run(
        [sys.executable, str(script), "--emit-events"],
        check=False,
        capture_output=True,
    )


def run_all(
    now: datetime | None = None,
    events_dir: Path = mc.EVENTS_DIR,
) -> tuple[list[Path], list[str]]:
    """Run every monitor, returning (written event paths, per-monitor error strings).

    A monitor raising must not crash the post-task-complete path, so each is
    guarded at this process boundary: the failure is recorded and the remaining
    monitors still run (see doc/python/anti_patterns.md — broad except is allowed
    at a process boundary that records and surfaces the error).
    """
    now = now or mc.utc_now()
    written: list[Path] = []
    errors: list[str] = []
    for name, run in MONITORS:
        try:
            written.extend(run(now=now, events_dir=events_dir))
        except Exception as exc:  # boundary guard (documented above): record and continue
            errors.append(f"{name}: {exc}")
    state = mc.load_state()
    if mc.as_int(state.get("completions_since_last_run")) >= _AGGREGATOR_THRESHOLD:
        try:
            _invoke_aggregator()
        except Exception as exc:  # boundary guard (documented above): record and continue
            errors.append(f"aggregator: {exc}")
    # REQ-PROC-006 §Monitor-Based Detection: when events sit in the queue and no
    # optimize task is pending, scaffold the autonomous (awaiting:[]) cycle task
    # the orchestrator picks up to run the producer skill (F-1, TASK-PROC-006-18).
    # Distinct from create_optimize_task.py's downstream auto-blocked proposal.
    # Guarded at this process boundary — a failure must not crash task-complete.
    # DISABLED untill TASK-PROC-006-06-01 creates a better approach - this just fires
    # and fires and blocks all other work
#    try:
#        cycle.create_cycle_task(now=now, events_dir=events_dir)
#    except Exception as exc:  # boundary guard (documented above): record and continue
#        errors.append(f"cycle-task: {exc}")
    return written, errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run all claude-optimize monitors (post task-complete)."
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Print elapsed wall-clock time (target: <2s on an empty event queue).",
    )
    args = parser.parse_args(argv)

    start = time.perf_counter()
    written, errors = run_all()
    elapsed = time.perf_counter() - start

    for path in written:
        print(f"event: {path.name}")
    for err in errors:
        print(f"monitor-error: {err}", file=sys.stderr)
    if args.benchmark:
        print(f"elapsed: {elapsed:.3f}s")
    print(f"summary: {len(written)} event(s), {len(errors)} error(s), {elapsed:.3f}s")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
