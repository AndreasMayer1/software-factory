#!/usr/bin/env python3
"""Aggregate per-file read-frequency metrics from session read-event logs.

Reads .factory/session_logs/*/read_events.jsonl (written by the PreToolUse/
PostToolUse Read hooks in .claude/settings.json), aggregates per-file read counts,
and optionally emits .factory/optimize/events/*.json for high-read files so that
claude-optimize can surface caching and restructuring opportunities.

Output:
    stdout (or --output PATH): JSON aggregate
    {"generated_at": ..., "total_sessions": N, "total_reads": N,
     "by_file": {"path": {"reads": N, "bytes_total": N,
                          "sessions": N, "task_ids": [...]}}}

Events:
    .factory/optimize/events/<timestamp>-high-read-file-<sha256[:12]>.json
    (only with --emit-events, for files above --threshold)

Usage:
    scripts/factory/aggregate_read_metrics.py [--threshold N] [--emit-events]
                                              [--output PATH] [--logs-root PATH]
"""

# tier: B  # generator; results consumed by render_factory_map.py heat overlay; direct tests required

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_THRESHOLD = 5
AGGREGATOR_PRUNE_DAYS = 30
SKILL_PREFIX = ".claude/skills/"
LARGE_DOC_BYTES_THRESHOLD = 5_000
MULTI_SESSION_REFERENCE_THRESHOLD = 2  # files read in >2 sessions are widely shared
SESSION_LOGS_DIR = ".factory/session_logs"
EVENTS_DIR = ".factory/optimize/events"
EVENT_TYPE = "high_read_file"
EVENT_CONFIDENCE = "medium"
RECORD_TOOL_READ = "Read"
RECORD_TYPE_BYTES = "read_bytes"

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class FileStats:
    reads: int = 0
    bytes_total: int = 0
    sessions: set[str] = field(default_factory=set)
    task_ids: set[str] = field(default_factory=set)


@dataclass
class AggregateResult:
    total_sessions: int
    total_reads: int
    by_file: dict[str, FileStats]


# ---------------------------------------------------------------------------
# Log parsing
# ---------------------------------------------------------------------------


def _iter_log_files(logs_root: Path) -> Iterator[Path]:
    """Yield all read_events.jsonl files under logs_root, sorted by session dir name."""
    if not logs_root.exists():
        return
    for session_dir in sorted(logs_root.iterdir()):
        if session_dir.is_dir():
            log_file = session_dir / "read_events.jsonl"
            if log_file.exists():
                yield log_file


def _parse_jsonl_file(path: Path) -> list[dict[str, object]]:
    """Parse a JSONL file, skipping blank and malformed lines."""
    records: list[dict[str, object]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(f"warning: could not read {path}: {exc}\n")
        return records
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            sys.stderr.write(f"warning: skipping malformed JSONL line in {path}\n")
    return records


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def _apply_read_record(
    record: dict[str, object],
    session_id: str,
    by_file: dict[str, FileStats],
    sessions: set[str],
) -> None:
    """Update by_file and sessions for a Read-tool record."""
    file_path = str(record.get("file_path", ""))
    if not file_path:
        return
    sessions.add(session_id)
    if file_path not in by_file:
        by_file[file_path] = FileStats()
    stats = by_file[file_path]
    stats.reads += 1
    stats.sessions.add(session_id)
    task_id = str(record.get("task_id", ""))
    if task_id:
        stats.task_ids.add(task_id)


def _apply_bytes_record(
    record: dict[str, object],
    bytes_by_file: dict[str, int],
) -> None:
    """Accumulate bytes from a read_bytes record."""
    file_path = str(record.get("file_path", ""))
    if not file_path:
        return
    raw = record.get("bytes", 0)
    try:
        b = int(raw) if isinstance(raw, (int, float, str)) else 0
    except ValueError:
        b = 0
    bytes_by_file[file_path] = bytes_by_file.get(file_path, 0) + b


def _aggregate_all_records(
    all_records: list[tuple[str, dict[str, object]]],
) -> AggregateResult:
    """Aggregate (session_id, record) pairs into per-file FileStats."""
    sessions: set[str] = set()
    by_file: dict[str, FileStats] = {}
    bytes_by_file: dict[str, int] = {}

    for session_id, record in all_records:
        record_type = str(record.get("tool", record.get("type", "")))
        if record_type == RECORD_TOOL_READ:
            _apply_read_record(record, session_id, by_file, sessions)
        elif record_type == RECORD_TYPE_BYTES:
            _apply_bytes_record(record, bytes_by_file)

    for file_path, stats in by_file.items():
        stats.bytes_total = bytes_by_file.get(file_path, 0)

    return AggregateResult(
        total_sessions=len(sessions),
        total_reads=sum(s.reads for s in by_file.values()),
        by_file=by_file,
    )


def prune_old_sessions(logs_root: Path, prune_days: int = AGGREGATOR_PRUNE_DAYS) -> None:
    """Remove session directories whose most recent timestamp is older than prune_days.

    Iterates all subdirectories of logs_root, parses every *.jsonl file to find
    the most recent ``timestamp`` field, and removes the directory via shutil.rmtree
    when the most recent timestamp is older than (now - prune_days).

    Sessions with no parseable timestamps are retained (fail-safe).
    Silent no-op when logs_root does not exist or nothing qualifies for removal.
    """
    if not logs_root.exists():
        return
    cutoff = datetime.now(timezone.utc) - timedelta(days=prune_days)
    for session_dir in sorted(logs_root.iterdir()):
        if not session_dir.is_dir():
            continue
        most_recent: datetime | None = None
        for jsonl_file in session_dir.glob("*.jsonl"):
            for record in _parse_jsonl_file(jsonl_file):
                raw_ts = record.get("timestamp")
                if not isinstance(raw_ts, str):
                    continue
                try:
                    ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                    if most_recent is None or ts > most_recent:
                        most_recent = ts
                except ValueError:
                    continue
        if most_recent is not None and most_recent < cutoff:
            shutil.rmtree(session_dir, ignore_errors=True)


def aggregate_logs(logs_root: Path, prune_days: int = AGGREGATOR_PRUNE_DAYS) -> AggregateResult:
    """Load all session log files under logs_root and aggregate read events.

    Prunes old session directories before reading (AC-07, REQ-PROC-044 §6).
    """
    prune_old_sessions(logs_root, prune_days)
    all_records: list[tuple[str, dict[str, object]]] = []
    for log_file in _iter_log_files(logs_root):
        session_id = log_file.parent.name
        for record in _parse_jsonl_file(log_file):
            all_records.append((session_id, record))
    return _aggregate_records(all_records)


def _aggregate_records(
    all_records: list[tuple[str, dict[str, object]]],
) -> AggregateResult:
    """Public-facing alias for _aggregate_all_records (testable without I/O)."""
    return _aggregate_all_records(all_records)


# ---------------------------------------------------------------------------
# Optimization candidates
# ---------------------------------------------------------------------------


def optimization_candidates(file_path: str, stats: FileStats) -> list[str]:
    """Return suggested optimization actions for a frequently-read file.

    Heuristics:
    - skill files → cache (loaded every session, benefit from caching)
    - large average read (>5 KB) → section (split into smaller addressable parts)
    - read across multiple sessions → reference (use schema/reference instead of inline)
    """
    candidates: list[str] = []
    if file_path.startswith(SKILL_PREFIX):
        candidates.append("cache")
    avg_bytes = stats.bytes_total / max(stats.reads, 1)
    if avg_bytes > LARGE_DOC_BYTES_THRESHOLD:
        candidates.append("section")
    if len(stats.sessions) > MULTI_SESSION_REFERENCE_THRESHOLD:
        candidates.append("reference")
    return candidates


# ---------------------------------------------------------------------------
# Event emission
# ---------------------------------------------------------------------------


def _event_filename(file_path: str) -> str:
    """Return the filename (no directory) for a high-read-file event."""
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    h = hashlib.sha256(file_path.encode()).hexdigest()[:12]
    return f"{ts}-high-read-file-{h}.json"


def _build_event_payload(file_path: str, stats: FileStats) -> dict[str, object]:
    """Build the optimize event dict for a single high-read file."""
    return {
        "event_type": EVENT_TYPE,
        "confidence": EVENT_CONFIDENCE,
        "fingerprint": f"{file_path}@{stats.reads}",
        "created": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": {
            "file_path": file_path,
            "read_count": stats.reads,
            "total_bytes": stats.bytes_total,
            "session_count": len(stats.sessions),
            "optimization_candidates": optimization_candidates(file_path, stats),
        },
    }


def _load_existing_fingerprints(events_dir: Path) -> set[str]:
    """Return the set of fingerprint values already written to events_dir."""
    existing: set[str] = set()
    if not events_dir.exists():
        return existing
    for efp in events_dir.glob("*.json"):
        try:
            edata = json.loads(efp.read_text(encoding="utf-8"))
            if isinstance(edata, dict) and edata.get("fingerprint"):
                existing.add(str(edata["fingerprint"]))
        except (OSError, json.JSONDecodeError):
            continue
    return existing


def emit_events(
    result: AggregateResult,
    events_dir: Path,
    threshold: int,
) -> int:
    """Write .factory/optimize/events/*.json for files above the threshold.

    Skips events whose fingerprint already exists in events_dir (idempotency).
    Returns the number of events written.
    """
    events_dir.mkdir(parents=True, exist_ok=True)
    existing_fps = _load_existing_fingerprints(events_dir)
    count = 0
    for file_path, stats in sorted(result.by_file.items()):
        if stats.reads < threshold:
            continue
        event = _build_event_payload(file_path, stats)
        if event["fingerprint"] in existing_fps:
            continue
        out_path = events_dir / _event_filename(file_path)
        try:
            out_path.write_text(json.dumps(event, indent=2), encoding="utf-8")
            count += 1
        except OSError as exc:
            sys.stderr.write(f"warning: could not write event {out_path}: {exc}\n")
    return count


# ---------------------------------------------------------------------------
# Output serialization
# ---------------------------------------------------------------------------


def serialize_result(result: AggregateResult) -> dict[str, object]:
    """Convert AggregateResult to a JSON-serializable dict for CLI output."""
    by_file: dict[str, object] = {
        fp: {
            "reads": s.reads,
            "bytes_total": s.bytes_total,
            "sessions": len(s.sessions),
            "task_ids": sorted(s.task_ids),
        }
        for fp, s in sorted(result.by_file.items())
    }
    return {
        "generated_at": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "total_sessions": result.total_sessions,
        "total_reads": result.total_reads,
        "by_file": by_file,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for this CLI."""
    parser = argparse.ArgumentParser(
        description="Aggregate read-frequency metrics from .factory/session_logs/.",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        metavar="N",
        help=f"Minimum read count to emit an optimize event (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--emit-events",
        action="store_true",
        help="Write .factory/optimize/events/*.json for files above threshold",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Write JSON aggregate to PATH instead of stdout",
    )
    parser.add_argument(
        "--logs-root",
        metavar="PATH",
        default=SESSION_LOGS_DIR,
        help=f"Root directory for session logs (default: {SESSION_LOGS_DIR})",
    )
    parser.add_argument(
        "--prune-days",
        type=int,
        default=AGGREGATOR_PRUNE_DAYS,
        metavar="N",
        help=f"Remove session dirs older than N days before aggregating (default: {AGGREGATOR_PRUNE_DAYS})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point; returns exit code."""
    args = _build_parser().parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    logs_root = project_root / args.logs_root
    events_dir = project_root / EVENTS_DIR

    result = aggregate_logs(logs_root, prune_days=args.prune_days)
    serialized = serialize_result(result)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
    else:
        print(json.dumps(serialized, indent=2))

    if args.emit_events:
        count = emit_events(result, events_dir, args.threshold)
        sys.stderr.write(f"Emitted {count} optimize event(s) to {events_dir}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
