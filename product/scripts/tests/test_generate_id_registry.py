#!/usr/bin/env python3
"""Regression tests for scripts/artifacts/generate_id_registry.py.

Pins observable behaviour of parse_yaml_frontmatter before the migration to
scripts.util.yaml_frontmatter (TASK-PROC-051-04 / G4).

Pre-migration: PyYAML absent → buggy _parse_simple_yaml fallback returned
empty strings for list/nested keys. Tests pin the CORRECT post-migration
behaviour where lists and nested dicts parse correctly via ruamel.yaml.
"""

import pathlib
from pathlib import Path

from scripts.artifacts import generate_id_registry as m


def test_parse_yaml_frontmatter_returns_none_for_no_delimiter() -> None:
    assert m.parse_yaml_frontmatter("# heading\n\nbody") is None


def test_parse_yaml_frontmatter_returns_none_for_empty_content() -> None:
    assert m.parse_yaml_frontmatter("") is None


def test_parse_yaml_frontmatter_strips_bom() -> None:
    text = "﻿---\nid: REQ-PROC-001\n---\nbody\n"
    meta = m.parse_yaml_frontmatter(text)
    assert meta is not None
    assert meta["id"] == "REQ-PROC-001"


def test_parse_yaml_frontmatter_parses_scalars() -> None:
    text = (
        "---\n"
        "id: REQ-FUNC-005\n"
        'name: "Feature X"\n'
        "status: completed\n"
        "---\n"
        "body\n"
    )
    meta = m.parse_yaml_frontmatter(text)
    assert meta is not None
    assert meta["id"] == "REQ-FUNC-005"
    assert meta["name"] == "Feature X"
    assert meta["status"] == "completed"


def test_parse_yaml_frontmatter_parses_task_goal() -> None:
    text = (
        "---\n"
        "task_id: TASK-PROC-051-04\n"
        "parent_requirement: REQ-PROC-051\n"
        "status: in_progress\n"
        "---\n"
        "body\n"
    )
    meta = m.parse_yaml_frontmatter(text)
    assert meta is not None
    assert meta["task_id"] == "TASK-PROC-051-04"
    assert meta["parent_requirement"] == "REQ-PROC-051"
    assert meta["status"] == "in_progress"


def test_parse_yaml_frontmatter_handles_nested_lists() -> None:
    """Post-migration: lists parse correctly (pre-migration fallback dropped them)."""
    text = (
        "---\n"
        "id: REQ-PROC-001\n"
        "covers:\n"
        "  acceptance_criteria: [AC-01, AC-02]\n"
        "---\n"
    )
    meta = m.parse_yaml_frontmatter(text)
    assert meta is not None
    assert meta["id"] == "REQ-PROC-001"
    # The 'covers' nested mapping is preserved by ruamel.
    assert list(meta["covers"]["acceptance_criteria"]) == ["AC-01", "AC-02"]


# ---------------------------------------------------------------------------
# AC-01/02/03 (REQ-PROC-009 SEC-08): hierarchical ID handling
# ---------------------------------------------------------------------------

def _make_req_file(tmp_path: Path, req_id: str, name: str = "Test Req") -> Path:
    """Create a minimal requirements.md file under tmp_path with the given ID."""
    folder = tmp_path / req_id
    folder.mkdir(parents=True, exist_ok=True)
    content = f"---\nid: {req_id}\nname: {name}\nstatus: active\n---\n# Requirement: {name}\n"
    (folder / "requirements.md").write_text(content, encoding="utf-8")
    return folder


def test_hierarchical_id_included_in_req_entries(tmp_path: Path) -> None:
    """AC-01/02: _process_req_files includes REQ-FUNC-006-07 in req_entries."""
    # Create a top-level and a hierarchical requirements.md under tmp_path
    _make_req_file(tmp_path, "REQ-FUNC-006", "Parent Epic")
    _make_req_file(tmp_path, "REQ-FUNC-006-07", "Sub Requirement")

    files = [
        str(tmp_path / "REQ-FUNC-006" / "requirements.md"),
        str(tmp_path / "REQ-FUNC-006-07" / "requirements.md"),
    ]
    req_entries, _ = m._process_req_files(pathlib.Path(tmp_path), files)

    ids = [e["id"] for e in req_entries]
    assert "REQ-FUNC-006" in ids, "Top-level ID must be included"
    assert "REQ-FUNC-006-07" in ids, "Hierarchical ID must be included (AC-01/02)"


def test_hierarchical_id_rendered_with_tree_marker() -> None:
    """AC-01: hierarchical IDs render with the └─ tree marker prefix in the catalog."""
    # _req_id_cell is the rendering helper — test it directly (pure function, no I/O)
    assert m._req_id_cell("REQ-FUNC-006") == "REQ-FUNC-006", \
        "Top-level ID must render unchanged"
    assert m._req_id_cell("REQ-FUNC-006-07") == "└─ REQ-FUNC-006-07", \
        "Hierarchical ID must carry the tree marker"
    assert m._req_id_cell("REQ-PROC-009-15") == "└─ REQ-PROC-009-15", \
        "PROC hierarchical ID must also carry the tree marker"
    assert m._req_id_cell("REQ-NFUNC-003-01") == "└─ REQ-NFUNC-003-01", \
        "NFUNC hierarchical ID must also carry the tree marker"


def test_per_category_count_includes_hierarchical_ids(tmp_path: Path) -> None:
    """AC-02: per-category count includes hierarchical IDs (count=2 for one top + one sub)."""
    _make_req_file(tmp_path, "REQ-FUNC-006", "Parent Epic")
    _make_req_file(tmp_path, "REQ-FUNC-006-07", "Sub Requirement")

    files = [
        str(tmp_path / "REQ-FUNC-006" / "requirements.md"),
        str(tmp_path / "REQ-FUNC-006-07" / "requirements.md"),
    ]
    req_entries, _ = m._process_req_files(pathlib.Path(tmp_path), files)

    func_entries = [e for e in req_entries if e["id"].startswith("REQ-FUNC-")]
    assert len(func_entries) == 2, (
        f"Expected 2 FUNC entries (1 top-level + 1 hierarchical), got {len(func_entries)}"
    )


def test_compute_next_ids_ignores_hierarchical_ids() -> None:
    """AC-03: compute_next_ids uses top-level IDs only; a hierarchical ID does not advance it."""
    entries = [
        {"id": "REQ-FUNC-023", "path": "p", "name": "n", "status": "active"},
        {"id": "REQ-FUNC-023-04", "path": "p2", "name": "n2", "status": "active"},
        {"id": "REQ-PROC-069", "path": "p3", "name": "n3", "status": "active"},
        {"id": "REQ-NFUNC-023", "path": "p4", "name": "n4", "status": "active"},
    ]
    next_ids = m.compute_next_ids(entries)
    assert next_ids["FUNC"] == "REQ-FUNC-024", (
        "Hierarchical REQ-FUNC-023-04 must not advance next FUNC beyond REQ-FUNC-024"
    )
    assert next_ids["PROC"] == "REQ-PROC-070", "PROC next must be 070"
    assert next_ids["NFUNC"] == "REQ-NFUNC-024", "NFUNC next must be 024"
