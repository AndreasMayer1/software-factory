#!/usr/bin/env python3
"""Monitor: a skill file edited then substantially undone within 48h (REQ-PROC-006 IMPL-C).

Signal: a change to a `.claude/skills` file that was rolled back shortly after is
a high-confidence sign the change was wrong or contested — worth a closer look.
Detection: among skill files touched by >=2 commits in the last 48 hours, fire a
`skill_change_reverted` event (confidence High) for any whose net diff against its
pre-window state is empty (i.e. the edits cancelled out). Idempotent within a
48-hour cooldown window.

Consumes git history only — committed, project-local. No session JSONL (G-INV-2).
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

EVENT_TYPE = "skill_change_reverted"
WINDOW = timedelta(hours=48)
COOLDOWN = timedelta(hours=48)
# At least an edit and an undo must appear in the window for a revert to exist.
MIN_COMMITS_FOR_REVERT = 2


def find_reverted_skills(now: datetime, git: mc.GitRunner = mc.real_git) -> list[str]:
    """Return skill-file paths whose recent edits net back to their pre-window content."""
    since_iso = (now - WINDOW).isoformat()
    commits = mc.skill_commits_in_window(since_iso, git)
    reverted: list[str] = []
    for path, shas in commits.items():
        if len(shas) < MIN_COMMITS_FOR_REVERT:
            continue
        earliest = shas[-1]  # oldest commit in the window (git log is newest-first)
        net_diff = git(["diff", f"{earliest}~1", "HEAD", "--", path])
        if net_diff.strip() == "":
            reverted.append(path)
    return reverted


def _build_events(now: datetime, reverted_files: list[str]) -> list[mc.Event]:
    return [
        mc.Event(
            event_type=EVENT_TYPE,
            confidence=mc.CONFIDENCE_HIGH,
            fingerprint=path,
            created=now,
            payload={"skill_path": path},
        )
        for path in sorted(reverted_files)
    ]


def detect(now: datetime, git: mc.GitRunner = mc.real_git) -> list[mc.Event]:
    return _build_events(now, find_reverted_skills(now, git))


def run(
    now: datetime | None = None,
    git: mc.GitRunner = mc.real_git,
    events_dir: Path = mc.EVENTS_DIR,
) -> list[Path]:
    """Detect reverted skill changes and emit at most one event per path/cooldown."""
    now = now or mc.utc_now()
    written: list[Path] = []
    for event in detect(now, git):
        path = mc.emit_once(event, COOLDOWN, now, events_dir)
        if path is not None:
            written.append(path)
    return written
