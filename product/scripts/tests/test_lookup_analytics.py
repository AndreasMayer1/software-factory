#!/usr/bin/env python3
"""Tests for scripts/lookup_analytics/lookup_analytics.py."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "scripts" / "lookup_analytics" / "lookup_analytics.py"


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("lookup_analytics_under_test", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(name="la")
def _la() -> Any:
    return _load()


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8"
    )


def _looked_up(
    chain: str = "code-simple",
    technology: str = "package:flutter",
    api_surface: str = "Widget.build",
    cycle: int = 1,
) -> dict[str, Any]:
    return {
        "ts": "2026-05-26T10:00:00Z",
        "agent": "implementation-engineer",
        "agent_id": "abc123",
        "chain": chain,
        "step": "batch-1/1",
        "technology": technology,
        "pinned_version": "3.24.0",
        "api_surface": api_surface,
        "decision": "looked_up",
        "channel": "context7",
        "source_ref": "context7:flutter/Widget@3.24.0",
        "result_summary": "build returns Widget",
        "trigger": "default",
        "cycle": cycle,
    }


def _fallback(
    technology: str = "package:some_lib",
    api_surface: str = "SomeClass.method",
) -> dict[str, Any]:
    return {
        "ts": "2026-05-26T10:01:00Z",
        "agent": "implementation-engineer",
        "agent_id": "abc123",
        "chain": "code-simple",
        "step": "batch-1/1",
        "technology": technology,
        "pinned_version": "1.0.0",
        "api_surface": api_surface,
        "decision": "fallback_websearch",
        "channel": "websearch",
        "source_ref": "https://pub.dev/packages/some_lib",
        "result_summary": "found via web",
        "trigger": "default",
        "cycle": 1,
        "note": "not indexed by context7",
    }


# ---------------------------------------------------------------------------
# find_log_files
# ---------------------------------------------------------------------------


def test_find_log_files_empty_dir(la: Any, tmp_path: Path) -> None:
    assert la.find_log_files(tmp_path) == []


def test_find_log_files_finds_nested(la: Any, tmp_path: Path) -> None:
    nested = tmp_path / "task1" / "plans_and_protocols"
    nested.mkdir(parents=True)
    log = nested / "lookup_log.jsonl"
    log.write_text("")
    result = la.find_log_files(tmp_path)
    assert result == [log]


def test_find_log_files_multiple(la: Any, tmp_path: Path) -> None:
    for i in range(3):
        p = tmp_path / f"task{i}" / "plans_and_protocols"
        p.mkdir(parents=True)
        (p / "lookup_log.jsonl").write_text("")
    result = la.find_log_files(tmp_path)
    assert len(result) == 3


# ---------------------------------------------------------------------------
# parse_log_file
# ---------------------------------------------------------------------------


def test_parse_log_file_valid(la: Any, tmp_path: Path) -> None:
    records = [_looked_up(), _fallback()]
    log = tmp_path / "lookup_log.jsonl"
    _write_jsonl(log, records)
    parsed, skipped = la.parse_log_file(log)
    assert len(parsed) == 2
    assert skipped == 0


def test_parse_log_file_skips_malformed(la: Any, tmp_path: Path, capsys: Any) -> None:
    log = tmp_path / "lookup_log.jsonl"
    log.write_text('{"ok": true}\nNOT JSON\n{"also": "ok"}\n', encoding="utf-8")
    parsed, skipped = la.parse_log_file(log)
    assert len(parsed) == 2
    assert skipped == 1
    captured = capsys.readouterr()
    assert "malformed" in captured.err


def test_parse_log_file_empty(la: Any, tmp_path: Path) -> None:
    log = tmp_path / "lookup_log.jsonl"
    log.write_text("", encoding="utf-8")
    parsed, skipped = la.parse_log_file(log)
    assert parsed == []
    assert skipped == 0


def test_parse_log_file_missing(la: Any, tmp_path: Path, capsys: Any) -> None:
    missing = tmp_path / "no_such_file.jsonl"
    parsed, skipped = la.parse_log_file(missing)
    assert parsed == []
    assert skipped == 0
    captured = capsys.readouterr()
    assert "Warning" in captured.err


# ---------------------------------------------------------------------------
# collect_all_records
# ---------------------------------------------------------------------------


def test_collect_all_records_no_files(la: Any, tmp_path: Path) -> None:
    pairs, log_files, skipped = la.collect_all_records(tmp_path)
    assert pairs == []
    assert log_files == []
    assert skipped == 0


def test_collect_all_records_aggregates(la: Any, tmp_path: Path) -> None:
    for i in range(2):
        p = tmp_path / f"task{i}" / "plans_and_protocols"
        p.mkdir(parents=True)
        _write_jsonl(p / "lookup_log.jsonl", [_looked_up(), _fallback()])
    pairs, log_files, skipped = la.collect_all_records(tmp_path)
    assert len(log_files) == 2
    assert len(pairs) == 4
    assert skipped == 0


# ---------------------------------------------------------------------------
# analytics_report
# ---------------------------------------------------------------------------


def test_analytics_report_empty(la: Any) -> None:
    data = la.analytics_report([])
    assert data["looked_up_total"] == 0
    assert data["fallback_total"] == 0
    assert data["fallback_rate_pct"] is None
    assert data["by_chain"] == {}
    assert data["cycle_correlation"] == {}


def test_analytics_report_counts_by_chain(la: Any, tmp_path: Path) -> None:
    log = tmp_path / "lookup_log.jsonl"
    _write_jsonl(log, [
        _looked_up(chain="code-simple"),
        _looked_up(chain="code-simple"),
        _looked_up(chain="code-complex"),
    ])
    pairs_parsed, _, _ = la.collect_all_records(tmp_path)
    data = la.analytics_report(pairs_parsed)
    assert data["by_chain"]["code-simple"] == 2
    assert data["by_chain"]["code-complex"] == 1
    assert data["looked_up_total"] == 3


def test_analytics_report_fallback_rate(la: Any, tmp_path: Path) -> None:
    p = tmp_path / "plans_and_protocols"
    p.mkdir(parents=True)
    _write_jsonl(p / "lookup_log.jsonl", [
        _looked_up(),
        _looked_up(),
        _looked_up(),
        _fallback(),
    ])
    pairs, _, _ = la.collect_all_records(tmp_path)
    data = la.analytics_report(pairs)
    assert data["looked_up_total"] == 3
    assert data["fallback_total"] == 1
    # 1/3 * 100 = 33.3%
    assert data["fallback_rate_pct"] == pytest.approx(33.3, abs=0.1)


def test_analytics_report_no_fallbacks(la: Any, tmp_path: Path) -> None:
    p = tmp_path / "plans_and_protocols"
    p.mkdir(parents=True)
    _write_jsonl(p / "lookup_log.jsonl", [_looked_up(), _looked_up()])
    pairs, _, _ = la.collect_all_records(tmp_path)
    data = la.analytics_report(pairs)
    assert data["fallback_rate_pct"] == 0.0


def test_analytics_report_cycle_correlation(la: Any, tmp_path: Path) -> None:
    # task1: 2 lookups at cycle 1
    p1 = tmp_path / "task1" / "plans_and_protocols"
    p1.mkdir(parents=True)
    _write_jsonl(p1 / "lookup_log.jsonl", [
        _looked_up(cycle=1),
        _looked_up(cycle=1),
    ])
    # task2: 4 lookups at cycle 1
    p2 = tmp_path / "task2" / "plans_and_protocols"
    p2.mkdir(parents=True)
    _write_jsonl(p2 / "lookup_log.jsonl", [
        _looked_up(cycle=1),
        _looked_up(cycle=1),
        _looked_up(cycle=1),
        _looked_up(cycle=1),
    ])
    pairs, _, _ = la.collect_all_records(tmp_path)
    data = la.analytics_report(pairs)
    corr = data["cycle_correlation"]
    assert 1 in corr
    # avg = (2 + 4) / 2 = 3.0
    assert corr[1]["avg_lookups_per_task"] == pytest.approx(3.0)
    assert corr[1]["task_count"] == 2
    assert corr[1]["total_lookups"] == 6


# ---------------------------------------------------------------------------
# gaps_report
# ---------------------------------------------------------------------------


def test_gaps_report_empty(la: Any) -> None:
    data = la.gaps_report([])
    assert data["fallback_total"] == 0
    assert data["technologies"] == []


def test_gaps_report_groups_by_technology(la: Any, tmp_path: Path) -> None:
    p = tmp_path / "plans_and_protocols"
    p.mkdir(parents=True)
    _write_jsonl(p / "lookup_log.jsonl", [
        _fallback(technology="package:foo", api_surface="Foo.bar"),
        _fallback(technology="package:foo", api_surface="Foo.baz"),
        _fallback(technology="package:foo", api_surface="Foo.qux"),
        _fallback(technology="package:zoo", api_surface="Zoo.run"),
        _looked_up(),  # should be ignored
    ])
    pairs, _, _ = la.collect_all_records(tmp_path)
    data = la.gaps_report(pairs)
    assert data["fallback_total"] == 4
    techs = data["technologies"]
    assert techs[0]["technology"] == "package:foo"
    assert techs[0]["fallback_count"] == 3
    assert techs[1]["technology"] == "package:zoo"
    assert techs[1]["fallback_count"] == 1


def test_gaps_report_limits_examples_to_three(la: Any, tmp_path: Path) -> None:
    p = tmp_path / "plans_and_protocols"
    p.mkdir(parents=True)
    records = [
        _fallback(technology="package:foo", api_surface=f"Foo.method{i}")
        for i in range(5)
    ]
    _write_jsonl(p / "lookup_log.jsonl", records)
    pairs, _, _ = la.collect_all_records(tmp_path)
    data = la.gaps_report(pairs)
    assert len(data["technologies"][0]["example_surfaces"]) == 3


def test_gaps_report_sorted_descending(la: Any, tmp_path: Path) -> None:
    p = tmp_path / "plans_and_protocols"
    p.mkdir(parents=True)
    records = (
        [_fallback(technology="package:rare")] +
        [_fallback(technology="package:common")] * 5
    )
    _write_jsonl(p / "lookup_log.jsonl", records)
    pairs, _, _ = la.collect_all_records(tmp_path)
    data = la.gaps_report(pairs)
    assert data["technologies"][0]["technology"] == "package:common"
    assert data["technologies"][1]["technology"] == "package:rare"


# ---------------------------------------------------------------------------
# main() CLI integration
# ---------------------------------------------------------------------------


def test_main_no_log_files(la: Any, tmp_path: Path, capsys: Any) -> None:
    rc = la.main(["--path", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "No lookup_log.jsonl" in captured.out


def test_main_nonexistent_path(la: Any, tmp_path: Path, capsys: Any) -> None:
    rc = la.main(["--path", str(tmp_path / "does_not_exist")])
    assert rc == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_main_analytics_mode(la: Any, tmp_path: Path, capsys: Any) -> None:
    p = tmp_path / "plans_and_protocols"
    p.mkdir(parents=True)
    _write_jsonl(p / "lookup_log.jsonl", [_looked_up(), _fallback()])
    rc = la.main(["--path", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Lookup Analytics Report" in captured.out
    assert "code-simple" in captured.out


def test_main_gaps_mode(la: Any, tmp_path: Path, capsys: Any) -> None:
    p = tmp_path / "plans_and_protocols"
    p.mkdir(parents=True)
    _write_jsonl(p / "lookup_log.jsonl", [_fallback(technology="package:mystery")])
    rc = la.main(["--path", str(tmp_path), "--gaps"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Fallback Gap Report" in captured.out
    assert "package:mystery" in captured.out


def test_main_json_analytics(la: Any, tmp_path: Path, capsys: Any) -> None:
    p = tmp_path / "plans_and_protocols"
    p.mkdir(parents=True)
    _write_jsonl(p / "lookup_log.jsonl", [_looked_up()])
    rc = la.main(["--path", str(tmp_path), "--json"])
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert "looked_up_total" in payload
    assert payload["looked_up_total"] == 1


def test_main_json_gaps(la: Any, tmp_path: Path, capsys: Any) -> None:
    p = tmp_path / "plans_and_protocols"
    p.mkdir(parents=True)
    _write_jsonl(p / "lookup_log.jsonl", [_fallback(technology="package:x")])
    rc = la.main(["--path", str(tmp_path), "--gaps", "--json"])
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["fallback_total"] == 1
    assert payload["technologies"][0]["technology"] == "package:x"


def test_main_json_no_files(la: Any, tmp_path: Path, capsys: Any) -> None:
    rc = la.main(["--path", str(tmp_path), "--json"])
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["log_files_found"] == 0
