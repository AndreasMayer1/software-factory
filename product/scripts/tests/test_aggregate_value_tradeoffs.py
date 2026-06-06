#!/usr/bin/env python3
"""Regression tests for scripts/artifacts/aggregate_value_tradeoffs.py.

Pins observable behaviour of parse_vcd_block and scan_persona_vcd_blocks
before swapping the hand-rolled parsers to scripts.util.yaml_frontmatter
(TASK-PROC-051-04 / G4).

NOTE: PyYAML is NOT installed in this environment. The pre-migration script
therefore used the buggy _parse_simple_yaml fallback. For nested mappings
inside list items (the VTR vcd-record shape) the fallback happened to be
correct, so tests pinning the documented behaviour pass before AND after the
migration.
"""

from pathlib import Path

from scripts.artifacts import aggregate_value_tradeoffs as m

# ---------------------------------------------------------------------------
# parse_vcd_block — embedded YAML inside vcd-record HTML comments
# ---------------------------------------------------------------------------


def test_parse_vcd_block_flat_scalars() -> None:
    text = (
        "id: VTR-001\n"
        "date: 2026-01-01\n"
        "artifact: foo.md\n"
        "decision_status: open\n"
    )
    rec = m.parse_vcd_block(text)
    assert rec is not None
    assert rec["id"] == "VTR-001"
    # date may be a datetime.date (ruamel) or "2026-01-01" string (legacy).
    # Either renders identically when interpolated into markdown tables.
    assert str(rec["date"]) == "2026-01-01"
    assert rec["artifact"] == "foo.md"
    assert rec["decision_status"] == "open"


def test_parse_vcd_block_nested_personas_list() -> None:
    text = (
        "id: VTR-002\n"
        "personas:\n"
        "  - id: PERSONA-001\n"
        "    value: privacy\n"
        "    impact: degraded\n"
        "  - id: PERSONA-002\n"
        "    value: speed\n"
        "    impact: supported\n"
    )
    rec = m.parse_vcd_block(text)
    assert rec is not None
    assert rec["id"] == "VTR-002"
    personas = rec["personas"]
    # dict-like behaviour preserved (CommentedSeq is a list subclass)
    assert len(personas) == 2
    p1 = dict(personas[0])
    p2 = dict(personas[1])
    assert p1 == {"id": "PERSONA-001", "value": "privacy", "impact": "degraded"}
    assert p2 == {"id": "PERSONA-002", "value": "speed", "impact": "supported"}


# ---------------------------------------------------------------------------
# scan_persona_vcd_blocks — reads persona.md frontmatter
# ---------------------------------------------------------------------------


def _write_persona(root: Path, folder: str, frontmatter: str) -> None:
    """Helper to create a persona.md file under root/personas/<folder>/."""
    p = root / "requirements_user_needs" / "personas" / folder
    p.mkdir(parents=True, exist_ok=True)
    (p / "persona.md").write_text(f"---\n{frontmatter}---\n\nbody\n", encoding="utf-8")


def test_scan_persona_vcd_blocks_extracts_vcd_data(tmp_path: Path) -> None:
    _write_persona(
        tmp_path,
        "alice",
        (
            "persona_id: PERSONA-001\n"
            "name: Alice\n"
            "vcd:\n"
            "  primary_value:\n"
            "    name: privacy\n"
            "  secondary_values:\n"
            "    - name: clarity\n"
            "    - name: speed\n"
        ),
    )
    entries = m.scan_persona_vcd_blocks(tmp_path)
    assert len(entries) == 1
    e = entries[0]
    assert e["id"] == "PERSONA-001"
    assert e["name"] == "Alice"
    assert e["primary_value"] == "privacy"
    assert e["secondary_values"] == "clarity, speed"


def test_scan_persona_vcd_blocks_returns_empty_when_dir_missing(tmp_path: Path) -> None:
    assert m.scan_persona_vcd_blocks(tmp_path) == []


def test_scan_persona_vcd_blocks_skips_persona_without_id(tmp_path: Path) -> None:
    _write_persona(tmp_path, "nameless", "name: NoId\n")
    assert m.scan_persona_vcd_blocks(tmp_path) == []


def test_scan_persona_vcd_blocks_handles_string_secondary(tmp_path: Path) -> None:
    _write_persona(
        tmp_path,
        "bob",
        (
            "persona_id: PERSONA-002\n"
            "name: Bob\n"
            "vcd:\n"
            "  primary_value: focus\n"
            "  secondary_values: clarity\n"
        ),
    )
    entries = m.scan_persona_vcd_blocks(tmp_path)
    assert len(entries) == 1
    e = entries[0]
    assert e["id"] == "PERSONA-002"
    assert e["primary_value"] == "focus"
    assert e["secondary_values"] == "clarity"
