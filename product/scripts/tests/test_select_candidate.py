#!/usr/bin/env python3
"""Fixture-driven tests for scripts/optimize/select_candidate.py (REQ-PROC-006 AC-07).

Covers the bugfix-first selection rule, the intra-class priority order, the
classification table (event_type/payload → klass/dimension), and the CLI shape
the SKILL.md body consumes.

The tests synthesize events on a tmp_path so the real .factory/optimize/events/
state is never read or written.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

_TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_TESTS_DIR.parent / "optimize"))

import select_candidate as sc  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation

_TS_FILENAME_FMT = "%Y%m%dT%H%M%SZ"


def _write_event(
    events_dir: Path,
    event_type: str,
    fingerprint: str,
    confidence: str = "high",
    payload: dict[str, Any] | None = None,
    ts: datetime | None = None,
) -> Path:
    """Synthesize one event JSON file with the on-disk schema from run_monitors.py."""
    events_dir.mkdir(parents=True, exist_ok=True)
    ts = ts or datetime.now(timezone.utc)
    name = f"{ts.strftime(_TS_FILENAME_FMT)}-{event_type}-{fingerprint}.json"
    path = events_dir / name
    body: dict[str, Any] = {
        "event_type": event_type,
        "fingerprint": fingerprint,
        "confidence": confidence,
        "created": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": payload or {},
    }
    path.write_text(json.dumps(body), encoding="utf-8")
    return path


# ─── AC-07: bugfix-first selection ───────────────────────────────────────


def test_bugfix_strictly_beats_optimization_when_both_present(tmp_path: Path) -> None:
    """AC-07: a low-priority bugfix wins over a high-priority optimization.

    skill_changed_and_used with broken=true is a bugfix candidate; periodic is
    optimization. The bugfix MUST be chosen even though periodic sits at a
    "lower" position in the priority list — class beats intra-class rank.
    """
    events_dir = tmp_path / "events"
    _write_event(
        events_dir,
        "skill_changed_and_used",
        "f-bug",
        confidence="medium",
        payload={"broken": True, "path": ".claude/skills/foo/skill.md"},
    )
    _write_event(events_dir, "periodic", "f-periodic", confidence="low")

    selected = sc.select_candidate(sc.load_events(events_dir))
    assert selected is not None
    assert selected.event_type == "skill_changed_and_used"
    assert selected.fingerprint == "f-bug"


def test_bugfix_repeated_question_beats_skill_change_reverted(tmp_path: Path) -> None:
    """Within the bugfix class: repeated_question > skill_change_reverted."""
    events_dir = tmp_path / "events"
    _write_event(events_dir, "skill_change_reverted", "f-rev")
    _write_event(events_dir, "repeated_question", "f-rq")

    selected = sc.select_candidate(sc.load_events(events_dir))
    assert selected is not None and selected.event_type == "repeated_question"


def test_no_bugfix_falls_back_to_optimization_priority(tmp_path: Path) -> None:
    """No bugfix candidate ⇒ pick the highest-priority optimization candidate."""
    events_dir = tmp_path / "events"
    _write_event(events_dir, "periodic", "f-periodic", confidence="low")
    _write_event(
        events_dir,
        "skill_changed_and_used",
        "f-clarity",
        confidence="medium",
        payload={"broken": False, "path": ".claude/skills/foo/skill.md"},
    )

    selected = sc.select_candidate(sc.load_events(events_dir))
    assert selected is not None and selected.event_type == "skill_changed_and_used"


def test_empty_queue_returns_none(tmp_path: Path) -> None:
    """No events ⇒ None (caller renders a no-op)."""
    events_dir = tmp_path / "events"
    events_dir.mkdir()
    assert sc.select_candidate(sc.load_events(events_dir)) is None


# ─── Classification table (klass + dimension per event_type) ──────────────


@pytest.mark.parametrize(
    ("event_type", "confidence", "payload", "expected_klass", "expected_dimension"),
    [
        ("repeated_question", "high", {}, "bugfix", "bugfix"),
        ("skill_change_reverted", "high", {}, "bugfix", "bugfix"),
        (
            "skill_changed_and_used",
            "medium",
            {"broken": True},
            "bugfix",
            "bugfix",
        ),
        (
            "skill_changed_and_used",
            "medium",
            {"broken": False},
            "optimization",
            "clarity",
        ),
        (
            "skill_changed_and_used",
            "low",
            {"broken": False},
            "optimization",
            "trigger_accuracy",
        ),
        ("periodic", "low", {}, "optimization", "alignment"),
        (
            "high_read_file",
            "medium",
            {"optimization_candidates": ["cache", "section"]},
            "optimization",
            "token_cost",
        ),
        (
            "high_read_file",
            "medium",
            {"optimization_candidates": ["section", "reference"]},
            "optimization",
            "clarity",
        ),
        (
            "high_read_file",
            "medium",
            {"optimization_candidates": []},
            "optimization",
            "clarity",
        ),
    ],
)
def test_classification_table_matches_skill_body(
    tmp_path: Path,
    event_type: str,
    confidence: str,
    payload: dict[str, Any],
    expected_klass: str,
    expected_dimension: str,
) -> None:
    """The (event_type, payload) → (klass, dimension) table is the SKILL.md source of truth."""
    events_dir = tmp_path / "events"
    _write_event(
        events_dir,
        event_type,
        f"fp-{event_type}",
        confidence=confidence,
        payload=payload,
    )
    [loaded] = sc.load_events(events_dir)
    klass, dimension = sc.classify(loaded)
    assert klass == expected_klass
    assert dimension == expected_dimension


# ─── load_events: robustness against malformed files ──────────────────────


def test_load_events_skips_corrupt_files(tmp_path: Path) -> None:
    """A malformed event must NOT crash the post-task-complete path."""
    events_dir = tmp_path / "events"
    _write_event(events_dir, "repeated_question", "f-ok")
    (events_dir / "20260528T000000Z-broken-xx.json").write_text(
        "{not json", encoding="utf-8"
    )
    (events_dir / "20260528T000000Z-incomplete-yy.json").write_text(
        json.dumps({"event_type": "periodic"}), encoding="utf-8"
    )

    loaded = sc.load_events(events_dir)
    assert len(loaded) == 1
    assert loaded[0].fingerprint == "f-ok"


def test_load_events_missing_directory_returns_empty(tmp_path: Path) -> None:
    """A missing events_dir is treated as an empty queue, not an error."""
    assert sc.load_events(tmp_path / "does-not-exist") == []


# ─── CLI shape — the contract the SKILL.md bash step consumes ──────────────


def test_cli_emits_candidate_payload(tmp_path: Path) -> None:
    """SKILL.md Step 2 reads stdout as JSON; the schema must match what it parses."""
    events_dir = tmp_path / "events"
    _write_event(
        events_dir,
        "repeated_question",
        "fpabc123",
        payload={"path": ".claude/skills/foo/skill.md", "question": "Why?"},
    )

    script = Path(__file__).resolve().parent.parent / "optimize" / "select_candidate.py"
    result = subprocess.run(
        [sys.executable, str(script), "--events-dir", str(events_dir)],
        capture_output=True,
        text=True,
        check=True,
    )
    out = json.loads(result.stdout)
    assert out["selected"] is True
    assert out["outcome"] == "candidate"
    assert out["event_type"] == "repeated_question"
    assert out["fingerprint"] == "fpabc123"
    assert out["klass"] == "bugfix"
    assert out["dimension"] == "bugfix"
    assert out["payload"]["path"] == ".claude/skills/foo/skill.md"
    assert out["event_path"].endswith(".json")


def test_cli_emits_no_op_when_queue_empty(tmp_path: Path) -> None:
    """No events ⇒ outcome=no-op with reason=empty_queue_after_prune."""
    events_dir = tmp_path / "events"
    events_dir.mkdir()
    script = Path(__file__).resolve().parent.parent / "optimize" / "select_candidate.py"
    result = subprocess.run(
        [sys.executable, str(script), "--events-dir", str(events_dir)],
        capture_output=True,
        text=True,
        check=True,
    )
    out = json.loads(result.stdout)
    assert out["selected"] is False
    assert out["outcome"] == "no-op"
    assert out["reason"] == "empty_queue_after_prune"
    assert out["event_path"] == ""
