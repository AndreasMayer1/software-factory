"""Tests for scripts/factory/aggregate_read_metrics.py."""

# tier: B  # tests for a Tier B generator

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "factory"))
import aggregate_read_metrics as arm  # type: ignore[import-not-found]  # runtime path; mypy cannot follow sys.path manipulation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_read_record(
    file_path: str, session_id: str = "sess-a", task_id: str = ""
) -> dict[str, object]:
    return {
        "tool": "Read",
        "file_path": file_path,
        "session_id": session_id,
        "task_id": task_id,
        "timestamp": "2026-05-30T10:00:00Z",
    }


def _make_bytes_record(
    file_path: str, bytes_val: int, session_id: str = "sess-a"
) -> dict[str, object]:
    return {
        "type": "read_bytes",
        "file_path": file_path,
        "session_id": session_id,
        "bytes": bytes_val,
        "timestamp": "2026-05-30T10:00:00Z",
    }


# ---------------------------------------------------------------------------
# _aggregate_records
# ---------------------------------------------------------------------------


def test_aggregate_single_read() -> None:
    records = [("sess-a", _make_read_record("foo.md"))]
    result = arm._aggregate_records(records)
    assert result.total_reads == 1
    assert result.total_sessions == 1
    assert "foo.md" in result.by_file
    assert result.by_file["foo.md"].reads == 1


def test_aggregate_multiple_reads_same_file() -> None:
    records = [
        ("sess-a", _make_read_record("foo.md")),
        ("sess-a", _make_read_record("foo.md")),
        ("sess-b", _make_read_record("foo.md")),
    ]
    result = arm._aggregate_records(records)
    stats = result.by_file["foo.md"]
    assert stats.reads == 3
    assert len(stats.sessions) == 2
    assert result.total_sessions == 2


def test_aggregate_bytes_merged() -> None:
    records = [
        ("sess-a", _make_read_record("foo.md")),
        ("sess-a", _make_bytes_record("foo.md", 1234)),
    ]
    result = arm._aggregate_records(records)
    assert result.by_file["foo.md"].bytes_total == 1234


def test_aggregate_task_ids_collected() -> None:
    records = [
        ("sess-a", _make_read_record("foo.md", task_id="TASK-001")),
        ("sess-b", _make_read_record("foo.md", task_id="TASK-002")),
    ]
    result = arm._aggregate_records(records)
    assert result.by_file["foo.md"].task_ids == {"TASK-001", "TASK-002"}


def test_aggregate_skips_empty_file_path() -> None:
    records = [("sess-a", {"tool": "Read", "file_path": "", "session_id": "sess-a"})]
    result = arm._aggregate_records(records)
    assert result.total_reads == 0
    assert result.by_file == {}


def test_aggregate_bytes_malformed_value() -> None:
    records = [
        ("sess-a", _make_read_record("foo.md")),
        ("sess-a", {"type": "read_bytes", "file_path": "foo.md", "bytes": "bad"}),
    ]
    result = arm._aggregate_records(records)
    assert result.by_file["foo.md"].bytes_total == 0


def test_aggregate_unknown_record_type_ignored() -> None:
    records = [
        ("sess-a", {"tool": "Edit", "file_path": "foo.md", "session_id": "sess-a"}),
    ]
    result = arm._aggregate_records(records)
    assert result.total_reads == 0


# ---------------------------------------------------------------------------
# aggregate_logs (filesystem-based)
# ---------------------------------------------------------------------------


def test_aggregate_logs_empty_dir(tmp_path: Path) -> None:
    result = arm.aggregate_logs(tmp_path)
    assert result.total_reads == 0
    assert result.total_sessions == 0
    assert result.by_file == {}


def test_aggregate_logs_missing_dir(tmp_path: Path) -> None:
    result = arm.aggregate_logs(tmp_path / "nonexistent")
    assert result.total_reads == 0


def test_aggregate_logs_reads_jsonl(tmp_path: Path) -> None:
    session_dir = tmp_path / "sess-1"
    session_dir.mkdir()
    log_file = session_dir / "read_events.jsonl"
    lines = [
        json.dumps(_make_read_record("doc.md", "sess-1")),
        json.dumps(_make_bytes_record("doc.md", 500, "sess-1")),
    ]
    log_file.write_text("\n".join(lines), encoding="utf-8")
    result = arm.aggregate_logs(tmp_path)
    assert result.by_file["doc.md"].reads == 1
    assert result.by_file["doc.md"].bytes_total == 500


def test_aggregate_logs_skips_malformed_lines(tmp_path: Path) -> None:
    session_dir = tmp_path / "sess-1"
    session_dir.mkdir()
    log_file = session_dir / "read_events.jsonl"
    log_file.write_text("not json\n" + json.dumps(_make_read_record("ok.md")), encoding="utf-8")
    result = arm.aggregate_logs(tmp_path)
    assert "ok.md" in result.by_file


def test_aggregate_logs_pruned_session_excluded(tmp_path: Path) -> None:
    old_dir = tmp_path / "old-sess"
    old_dir.mkdir()
    old_ts = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
    (old_dir / "read_events.jsonl").write_text(
        json.dumps({"tool": "Read", "file_path": "old.md", "timestamp": old_ts}),
        encoding="utf-8",
    )

    new_dir = tmp_path / "new-sess"
    new_dir.mkdir()
    recent_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (new_dir / "read_events.jsonl").write_text(
        json.dumps({"tool": "Read", "file_path": "new.md", "timestamp": recent_ts}),
        encoding="utf-8",
    )

    result = arm.aggregate_logs(tmp_path, prune_days=30)
    assert "new.md" in result.by_file
    assert "old.md" not in result.by_file


# ---------------------------------------------------------------------------
# optimization_candidates
# ---------------------------------------------------------------------------


def test_candidates_skill_file_gets_cache() -> None:
    stats = arm.FileStats(reads=10, bytes_total=0, sessions={"s1"})
    cands = arm.optimization_candidates(".claude/skills/task-create/SKILL.md", stats)
    assert "cache" in cands


def test_candidates_large_doc_gets_section() -> None:
    stats = arm.FileStats(reads=2, bytes_total=20_000, sessions={"s1"})
    cands = arm.optimization_candidates("doc/big_guide.md", stats)
    assert "section" in cands


def test_candidates_multi_session_gets_reference() -> None:
    stats = arm.FileStats(reads=5, bytes_total=0, sessions={"s1", "s2", "s3"})
    cands = arm.optimization_candidates("some/file.md", stats)
    assert "reference" in cands


def test_candidates_few_sessions_no_reference() -> None:
    stats = arm.FileStats(reads=5, bytes_total=0, sessions={"s1", "s2"})
    cands = arm.optimization_candidates("some/file.md", stats)
    assert "reference" not in cands


def test_candidates_small_non_skill_file_is_empty() -> None:
    stats = arm.FileStats(reads=3, bytes_total=100, sessions={"s1"})
    cands = arm.optimization_candidates("lib/main.dart", stats)
    assert cands == []


# ---------------------------------------------------------------------------
# emit_events
# ---------------------------------------------------------------------------


def test_emit_events_writes_files_above_threshold(tmp_path: Path) -> None:
    by_file: dict[str, arm.FileStats] = {
        "high.md": arm.FileStats(reads=10, bytes_total=1000, sessions={"s1"}),
        "low.md": arm.FileStats(reads=2, bytes_total=100, sessions={"s1"}),
    }
    result = arm.AggregateResult(total_sessions=1, total_reads=12, by_file=by_file)
    count = arm.emit_events(result, tmp_path, threshold=5)
    assert count == 1
    events = list(tmp_path.glob("*-high-read-file-*.json"))
    assert len(events) == 1
    payload = json.loads(events[0].read_text())
    assert payload["event_type"] == "high_read_file"
    assert payload["payload"]["file_path"] == "high.md"
    assert payload["payload"]["read_count"] == 10


def test_emit_events_no_collision_for_different_paths(tmp_path: Path) -> None:
    by_file: dict[str, arm.FileStats] = {
        "a.md": arm.FileStats(reads=10, bytes_total=0, sessions={"s1"}),
        "b.md": arm.FileStats(reads=10, bytes_total=0, sessions={"s1"}),
    }
    result = arm.AggregateResult(total_sessions=1, total_reads=20, by_file=by_file)
    arm.emit_events(result, tmp_path, threshold=5)
    events = list(tmp_path.glob("*.json"))
    filenames = [e.name for e in events]
    assert len(set(filenames)) == len(filenames), "Event filenames should be unique"


# ---------------------------------------------------------------------------
# serialize_result
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# prune_old_sessions
# ---------------------------------------------------------------------------


def test_prune_removes_old_session(tmp_path: Path) -> None:
    session_dir = tmp_path / "old-sess"
    session_dir.mkdir()
    old_ts = (datetime.now(timezone.utc) - timedelta(days=60)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    record = {"tool": "Read", "file_path": "x.md", "timestamp": old_ts}
    (session_dir / "read_events.jsonl").write_text(
        json.dumps(record), encoding="utf-8"
    )
    arm.prune_old_sessions(tmp_path, prune_days=30)
    assert not session_dir.exists()


def test_prune_retains_recent_session(tmp_path: Path) -> None:
    session_dir = tmp_path / "new-sess"
    session_dir.mkdir()
    recent_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record = {"tool": "Read", "file_path": "x.md", "timestamp": recent_ts}
    (session_dir / "read_events.jsonl").write_text(
        json.dumps(record), encoding="utf-8"
    )
    arm.prune_old_sessions(tmp_path, prune_days=30)
    assert session_dir.exists()


def test_prune_retains_session_with_no_timestamps(tmp_path: Path) -> None:
    session_dir = tmp_path / "no-ts-sess"
    session_dir.mkdir()
    record = {"tool": "Read", "file_path": "x.md"}
    (session_dir / "read_events.jsonl").write_text(
        json.dumps(record), encoding="utf-8"
    )
    arm.prune_old_sessions(tmp_path, prune_days=30)
    assert session_dir.exists()


def test_emit_events_skips_duplicate_fingerprint(tmp_path: Path) -> None:
    by_file: dict[str, arm.FileStats] = {
        "dup.md": arm.FileStats(reads=10, bytes_total=500, sessions={"s1"}),
    }
    result = arm.AggregateResult(total_sessions=1, total_reads=10, by_file=by_file)
    # First call writes the event.
    count1 = arm.emit_events(result, tmp_path, threshold=5)
    assert count1 == 1
    # Second call with same file stats must be skipped (fingerprint already exists).
    count2 = arm.emit_events(result, tmp_path, threshold=5)
    assert count2 == 0


# ---------------------------------------------------------------------------
# serialize_result
# ---------------------------------------------------------------------------


def test_serialize_result_structure() -> None:
    by_file: dict[str, arm.FileStats] = {
        "x.md": arm.FileStats(reads=3, bytes_total=600, sessions={"s1"}, task_ids={"T1"}),
    }
    result = arm.AggregateResult(total_sessions=1, total_reads=3, by_file=by_file)
    s = arm.serialize_result(result)
    assert s["total_sessions"] == 1
    assert s["total_reads"] == 3
    assert "generated_at" in s
    file_entry = s["by_file"]["x.md"]
    assert file_entry["reads"] == 3
    assert file_entry["sessions"] == 1
    assert "T1" in file_entry["task_ids"]
