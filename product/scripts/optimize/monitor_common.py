#!/usr/bin/env python3
"""Shared helpers for the claude-optimize monitor scripts (REQ-PROC-006 IMPL-C).

Provides project-local path resolution, an injectable clock boundary, the
candidate-event dataclass with its JSON form, and the idempotency check that
lets every monitor refuse to write a duplicate event within its cooldown window.
Imported by the four ``monitor_*.py`` scripts and ``run_monitors.py``.

Monitors consume only committed, project-local sources (state.json, runs.tsv,
git history, protocol/question files). Nothing here reads session JSONL or any
per-account memory tree — that is the G-INV-2 / REQ-PROC-006 AC-02 invariant:
detection runs outside any agent's tool surface and on local data only.
"""

# tier: B  # reusable library imported by every monitor and the runner

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Project root: scripts/optimize/monitor_common.py -> parents[2] is the repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OPTIMIZE_DIR = PROJECT_ROOT / ".factory" / "optimize"
EVENTS_DIR = OPTIMIZE_DIR / "events"
STATE_PATH = OPTIMIZE_DIR / "state.json"

# Confidence labels mirror the Monitor Taxonomy (requirements.md SEC-01).
CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"

# Length of the hex fingerprint kept for filenames / dedup (collision-safe at this scale).
FINGERPRINT_LEN = 16

# Event content uses UTC: event files are machine-to-machine artifacts consumed by
# the claude-optimize skill — the timezone-rule exception for stored exchange values.
_TS_CONTENT_FMT = "%Y-%m-%dT%H:%M:%SZ"
_TS_FILENAME_FMT = "%Y%m%dT%H%M%SZ"

# A substitutable clock boundary so cooldown logic is testable on a frozen clock.
Clock = Callable[[], datetime]

_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_WHITESPACE = re.compile(r"\s+")


def utc_now() -> datetime:
    """Production default for the clock boundary (timezone-aware UTC)."""
    return datetime.now(timezone.utc)


def fingerprint_text(text: str) -> str:
    """Stable short fingerprint of normalized text (lowercased, whitespace-collapsed)."""
    normalized = _WHITESPACE.sub(" ", text).strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:FINGERPRINT_LEN]


def _safe_token(token: str) -> str:
    """Filesystem-safe form of an event-type or fingerprint token."""
    return _NON_ALNUM.sub("-", token.lower()).strip("-")


@dataclass(frozen=True)
class Event:
    """A candidate improvement event produced by a monitor."""

    event_type: str
    confidence: str
    fingerprint: str
    created: datetime
    payload: dict[str, object] = field(default_factory=dict)

    def to_json(self) -> dict[str, object]:
        return {
            "event_type": self.event_type,
            "confidence": self.confidence,
            "fingerprint": self.fingerprint,
            "created": self.created.astimezone(timezone.utc).strftime(_TS_CONTENT_FMT),
            "payload": self.payload,
        }

    def filename(self) -> str:
        ts = self.created.astimezone(timezone.utc).strftime(_TS_FILENAME_FMT)
        return f"{ts}-{_safe_token(self.event_type)}-{_safe_token(self.fingerprint)}.json"


def load_state(state_path: Path = STATE_PATH) -> dict[str, object]:
    """Read .factory/optimize/state.json; empty dict if missing or unreadable."""
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def pending_events_of_type(
    event_type: str, events_dir: Path = EVENTS_DIR
) -> list[dict[str, object]]:
    """Return parsed JSON of every un-consumed event of the given type in events_dir."""
    if not events_dir.is_dir():
        return []
    out: list[dict[str, object]] = []
    for path in sorted(events_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and data.get("event_type") == event_type:
            out.append(data)
    return out


def recent_event_exists(
    event_type: str,
    fingerprint: str,
    now: datetime,
    cooldown: timedelta,
    events_dir: Path = EVENTS_DIR,
) -> bool:
    """True if an un-consumed event of this type+fingerprint sits within the cooldown window.

    This is the idempotency guard: events are consumed-then-deleted by
    claude-optimize, so an event lingering in events_dir means the trigger has
    not yet been acted on and must not be duplicated.
    """
    for data in pending_events_of_type(event_type, events_dir):
        if data.get("fingerprint") != fingerprint:
            continue
        created_raw = data.get("created")
        if not isinstance(created_raw, str):
            continue
        try:
            created = datetime.strptime(created_raw, _TS_CONTENT_FMT).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue
        if now.astimezone(timezone.utc) - created < cooldown:
            return True
    return False


def write_event(event: Event, events_dir: Path = EVENTS_DIR) -> Path:
    """Write one event JSON file to events_dir and return its path."""
    events_dir.mkdir(parents=True, exist_ok=True)
    path = events_dir / event.filename()
    path.write_text(json.dumps(event.to_json(), indent=2) + "\n", encoding="utf-8")
    return path


def emit_once(
    event: Event,
    cooldown: timedelta,
    now: datetime,
    events_dir: Path = EVENTS_DIR,
) -> Path | None:
    """Write the event unless an equivalent one already exists within the cooldown window."""
    if recent_event_exists(
        event.event_type, event.fingerprint, now, cooldown, events_dir
    ):
        return None
    return write_event(event, events_dir)


def as_int(value: object, default: int = 0) -> int:
    """Coerce a JSON-loaded value to int, ignoring bool (a subclass of int)."""
    if isinstance(value, bool):
        return default
    return value if isinstance(value, int) else default


# --- Git boundary (substitutable so the skill-change monitors are testable) ---

# A GitRunner takes the argument list after `git` and returns captured stdout.
GitRunner = Callable[[list[str]], str]

SKILLS_DIR_REL = ".claude/skills"
# Per-commit record separator embedded via --pretty so name-status output can be
# attributed to the right commit in a single `git log` call.
_COMMIT_MARKER = "\x01"


def real_git(args: list[str]) -> str:
    """Production GitRunner: run `git <args>` at the repo root, returning stdout.

    check=False so a non-zero git exit (e.g. unknown revision) yields empty
    output rather than raising — monitors must never crash the post-task-complete
    path.
    """
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout


def skill_commits_in_window(
    since_iso: str, git: GitRunner = real_git
) -> dict[str, list[str]]:
    """Map each `.claude/skills` file changed since *since_iso* to its commit shas.

    Shas are ordered newest-first (git log order). One git invocation total.
    """
    out = git(
        [
            "log",
            f"--since={since_iso}",
            "--name-status",
            f"--pretty=format:{_COMMIT_MARKER}%H",
            "--",
            SKILLS_DIR_REL,
        ]
    )
    files: dict[str, list[str]] = {}
    current_sha: str | None = None
    for line in out.splitlines():
        if line.startswith(_COMMIT_MARKER):
            current_sha = line[len(_COMMIT_MARKER) :].strip()
            continue
        if current_sha is None or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        path = parts[-1].strip()
        files.setdefault(path, []).append(current_sha)
    return files
