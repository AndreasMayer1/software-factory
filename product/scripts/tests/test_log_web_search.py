#!/usr/bin/env python3
"""Tests for scripts/optimize/log_web_search.py (REQ-PROC-006 IMPL-J).

Covers: normal append, goal-path with recommended=true, goal-path with missing
file (defaults false), missing TSV file creates header+row.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "optimize"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import log_web_search as m  # type: ignore[import-not-found]  # sys.path mutated above

FIXED_TS = "2026-05-28T12:00:00Z"
TASK_ID = "TASK-TEST-001"
QUERY = "how does ruamel.yaml preserve comments?"


def _goal_with_recommended(tmp_path: Path, recommended: bool) -> Path:
    goal = tmp_path / "goal.md"
    flag = "true" if recommended else "false"
    goal.write_text(
        f"---\ntask_id: {TASK_ID}\noptimization_approach:\n  web_research_recommended: {flag}\n---\n# Body\n",
        encoding="utf-8",
    )
    return goal


# ---------------------------------------------------------------------------
# read_recommended_flag
# ---------------------------------------------------------------------------


def test_read_recommended_flag_true(tmp_path):
    goal = _goal_with_recommended(tmp_path, recommended=True)
    assert m.read_recommended_flag(goal) is True


def test_read_recommended_flag_false(tmp_path):
    goal = _goal_with_recommended(tmp_path, recommended=False)
    assert m.read_recommended_flag(goal) is False


def test_read_recommended_flag_missing_file(tmp_path):
    assert m.read_recommended_flag(tmp_path / "nonexistent.md") is False


def test_read_recommended_flag_no_optimization_approach(tmp_path):
    goal = tmp_path / "goal.md"
    goal.write_text("---\ntask_id: T-001\n---\n# Body\n", encoding="utf-8")
    assert m.read_recommended_flag(goal) is False


# ---------------------------------------------------------------------------
# append_row
# ---------------------------------------------------------------------------


def test_append_row_creates_header_when_file_missing(tmp_path):
    tsv = tmp_path / "web_searches.tsv"
    m.append_row(tsv, FIXED_TS, TASK_ID, QUERY, recommended=False)
    lines = tsv.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "timestamp\ttask_id\tquery\trecommended_by_optimization_approach"
    assert lines[1] == f"{FIXED_TS}\t{TASK_ID}\t{QUERY}\tfalse"


def test_append_row_no_duplicate_header_when_file_exists(tmp_path):
    tsv = tmp_path / "web_searches.tsv"
    tsv.write_text(
        "timestamp\ttask_id\tquery\trecommended_by_optimization_approach\n",
        encoding="utf-8",
    )
    m.append_row(tsv, FIXED_TS, TASK_ID, QUERY, recommended=True)
    lines = tsv.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "timestamp\ttask_id\tquery\trecommended_by_optimization_approach"
    assert lines[1] == f"{FIXED_TS}\t{TASK_ID}\t{QUERY}\ttrue"
    assert len(lines) == 2


def test_append_row_accumulates_multiple_rows(tmp_path):
    tsv = tmp_path / "web_searches.tsv"
    m.append_row(tsv, FIXED_TS, TASK_ID, "query one", recommended=False)
    m.append_row(tsv, FIXED_TS, TASK_ID, "query two", recommended=True)
    lines = tsv.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3  # header + 2 data rows
    assert "query one" in lines[1]
    assert "query two" in lines[2]


# ---------------------------------------------------------------------------
# main (CLI integration)
# ---------------------------------------------------------------------------


def test_main_normal_append(tmp_path, monkeypatch):
    tsv = tmp_path / "web_searches.tsv"
    monkeypatch.setattr(m, "TSV_PATH", tsv)
    rc = m.main(["--task-id", TASK_ID, "--query", QUERY, "--timestamp", FIXED_TS])
    assert rc == 0
    lines = tsv.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("timestamp")
    assert QUERY in lines[1]
    assert "\tfalse" in lines[1]


def test_main_with_goal_path_recommended_true(tmp_path, monkeypatch):
    tsv = tmp_path / "web_searches.tsv"
    monkeypatch.setattr(m, "TSV_PATH", tsv)
    goal = _goal_with_recommended(tmp_path, recommended=True)
    rc = m.main(
        [
            "--task-id",
            TASK_ID,
            "--query",
            QUERY,
            "--timestamp",
            FIXED_TS,
            "--goal-path",
            str(goal),
        ]
    )
    assert rc == 0
    assert "\ttrue" in tsv.read_text(encoding="utf-8")


def test_main_with_missing_goal_path_defaults_false(tmp_path, monkeypatch):
    tsv = tmp_path / "web_searches.tsv"
    monkeypatch.setattr(m, "TSV_PATH", tsv)
    rc = m.main(
        [
            "--task-id",
            TASK_ID,
            "--query",
            QUERY,
            "--timestamp",
            FIXED_TS,
            "--goal-path",
            str(tmp_path / "nonexistent.md"),
        ]
    )
    assert rc == 0
    assert "\tfalse" in tsv.read_text(encoding="utf-8")
