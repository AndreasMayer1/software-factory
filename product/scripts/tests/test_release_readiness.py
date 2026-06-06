#!/usr/bin/env python3
"""Regression tests for scripts/release/release_readiness.py.

Pins observable behaviour of _parse_yaml_frontmatter and
_parse_frontmatter_fields before swapping the hand-rolled parsers to
scripts.util.yaml_frontmatter (TASK-PROC-051-04 / G4).
"""

from pathlib import Path

from scripts.release import release_readiness as rr

# ---------------------------------------------------------------------------
# _parse_yaml_frontmatter — full-YAML parse used for RELEASES.md
# ---------------------------------------------------------------------------


def test_parse_yaml_frontmatter_returns_dict_for_valid(tmp_path: Path) -> None:
    """Round-trip parse of a structured releases list.

    Note: the prior fallback parser (when PyYAML was absent) was buggy and
    returned `releases: ''` for nested lists. The migration restores correct
    behaviour by routing through ruamel.yaml. This test pins the *correct*
    semantics — they happen to match what the script always intended.
    """
    f = tmp_path / "RELEASES.md"
    f.write_text(
        "---\n"
        "releases:\n"
        "  - version: 1.0.0\n"
        "    status: active\n"
        "  - version: 1.1.0\n"
        "    status: planned\n"
        "---\n"
        "\nBody\n",
        encoding="utf-8",
    )
    result = rr._parse_yaml_frontmatter(f)
    assert isinstance(result, dict)
    assert isinstance(result["releases"], list)
    assert result["releases"][0]["version"] == "1.0.0"
    assert result["releases"][0]["status"] == "active"


def test_parse_yaml_frontmatter_returns_empty_for_no_frontmatter(tmp_path: Path) -> None:
    f = tmp_path / "no_fm.md"
    f.write_text("# Just markdown\n\nNo YAML.\n", encoding="utf-8")
    assert rr._parse_yaml_frontmatter(f) == {}


def test_parse_yaml_frontmatter_returns_empty_for_missing_file(tmp_path: Path) -> None:
    assert rr._parse_yaml_frontmatter(tmp_path / "missing.md") == {}


# ---------------------------------------------------------------------------
# _parse_frontmatter_fields — selective scalar extraction from goal.md
# ---------------------------------------------------------------------------


def test_parse_frontmatter_fields_extracts_requested(tmp_path: Path) -> None:
    f = tmp_path / "goal.md"
    f.write_text(
        "---\n"
        "task_id: TASK-001\n"
        "status: completed\n"
        "writes_requirements: true\n"
        "target_release: 1.0.0\n"
        "---\n"
        "\nbody\n",
        encoding="utf-8",
    )
    out = rr._parse_frontmatter_fields(f, ["status", "writes_requirements"])
    assert out == {"status": "completed", "writes_requirements": "true"}


def test_parse_frontmatter_fields_strips_quotes(tmp_path: Path) -> None:
    f = tmp_path / "goal.md"
    f.write_text(
        '---\n'
        'target_release: "1.0.0"\n'
        "---\n",
        encoding="utf-8",
    )
    out = rr._parse_frontmatter_fields(f, ["target_release"])
    assert out["target_release"] == "1.0.0"


def test_parse_frontmatter_fields_missing_file_returns_empty(tmp_path: Path) -> None:
    assert rr._parse_frontmatter_fields(tmp_path / "missing.md", ["status"]) == {}


def test_parse_frontmatter_fields_no_frontmatter_returns_empty(tmp_path: Path) -> None:
    f = tmp_path / "no_fm.md"
    f.write_text("# Plain\n\ntext\n", encoding="utf-8")
    assert rr._parse_frontmatter_fields(f, ["status"]) == {}
