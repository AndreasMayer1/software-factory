#!/usr/bin/env python3
"""
Tests for scripts/user_needs/update_scribble_requirements.py (AC-41).

Covers:
1.  discover_primary — exact match returns primary, no match returns ambiguous
2.  discover_primary — multiple matches returns ambiguous with first candidate
3.  discover_cross_cutting — returns reqs sharing ≥1 flow with UI scope
4.  discover_cross_cutting — excludes reqs without feature_path (not UI-scoped)
5.  discover_cross_cutting — excludes the primary requirement itself
6.  check_consistency — passes when feature_paths match
7.  check_consistency — fails and prints error when feature_paths differ
8.  check_consistency — fails when primary is None
9.  apply_updates — normalises legacy `requirement` scalar to array
10. apply_updates — writes contributing_requirements and participating_flows
11. apply_updates — dry_run=True does not write file
12. resolve_metadata_path — dir arg → dir/metadata.yaml
13. resolve_metadata_path — file arg returned unchanged
14. read_plain_yaml / write_plain_yaml — round-trip preserves existing fields
15. _extract_flow_ids — handles missing user_needs, empty implements_flows
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------
from scripts.user_needs.update_scribble_requirements import (
    RequirementFields,
    _extract_flow_ids,
    apply_updates,
    check_consistency,
    discover_cross_cutting,
    discover_primary,
    read_plain_yaml,
    resolve_metadata_path,
    write_plain_yaml,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REQ_A = RequirementFields(
    req_id="REQ-FUNC-007-01",
    feature_path="therapist/data_transfer",
    flow_ids=("FLOW-002", "FLOW-003"),
)
REQ_B = RequirementFields(
    req_id="REQ-FUNC-007-12",
    feature_path="client/qr_transfer",
    flow_ids=("FLOW-003", "FLOW-004"),
)
REQ_C = RequirementFields(
    req_id="REQ-FUNC-006",  # security requirement — no feature_path (not UI-scoped)
    feature_path="",
    flow_ids=("FLOW-002", "FLOW-003"),
)
REQ_D = RequirementFields(
    req_id="REQ-FUNC-007-04",
    feature_path="shared/transfer_settings",
    flow_ids=("FLOW-002",),
)


def _make_metadata_file(tmp_path: Path, content: str) -> Path:
    meta = tmp_path / "metadata.yaml"
    meta.write_text(content, encoding="utf-8")
    return meta


# ---------------------------------------------------------------------------
# 1. discover_primary — exact match
# ---------------------------------------------------------------------------


def test_discover_primary_exact_match() -> None:
    result = discover_primary("therapist/data_transfer", [REQ_A, REQ_B, REQ_C])
    assert result.primary == REQ_A
    assert not result.is_ambiguous


# ---------------------------------------------------------------------------
# 2. discover_primary — no match → ambiguous
# ---------------------------------------------------------------------------


def test_discover_primary_no_match() -> None:
    result = discover_primary("nonexistent/path", [REQ_A, REQ_B])
    assert result.primary is None
    assert result.is_ambiguous
    assert "nonexistent/path" in result.ambiguity_reason


# ---------------------------------------------------------------------------
# 3. discover_primary — multiple matches → ambiguous, first used
# ---------------------------------------------------------------------------


def test_discover_primary_multiple_matches() -> None:
    dup = RequirementFields(
        req_id="REQ-FUNC-007-99",
        feature_path="therapist/data_transfer",
        flow_ids=(),
    )
    result = discover_primary("therapist/data_transfer", [REQ_A, dup])
    assert result.primary == REQ_A
    assert result.is_ambiguous
    assert "REQ-FUNC-007-99" in result.ambiguity_reason


# ---------------------------------------------------------------------------
# 4. discover_cross_cutting — returns UI-scoped reqs sharing a flow
# ---------------------------------------------------------------------------


def test_discover_cross_cutting_finds_shared_flow() -> None:
    # REQ_B shares FLOW-003 with REQ_A and has feature_path set → cross-cutting
    cross = discover_cross_cutting(REQ_A, [REQ_A, REQ_B, REQ_C])
    assert "REQ-FUNC-007-12" in cross


# ---------------------------------------------------------------------------
# 5. discover_cross_cutting — excludes reqs without feature_path
# ---------------------------------------------------------------------------


def test_discover_cross_cutting_excludes_non_ui() -> None:
    # REQ_C has no feature_path → excluded even though it shares flows
    cross = discover_cross_cutting(REQ_A, [REQ_A, REQ_C])
    assert "REQ-FUNC-006" not in cross


# ---------------------------------------------------------------------------
# 6. discover_cross_cutting — excludes primary itself
# ---------------------------------------------------------------------------


def test_discover_cross_cutting_excludes_primary() -> None:
    cross = discover_cross_cutting(REQ_A, [REQ_A, REQ_B])
    assert "REQ-FUNC-007-01" not in cross


# ---------------------------------------------------------------------------
# 7. check_consistency — feature_paths match → True
# ---------------------------------------------------------------------------


def test_check_consistency_match() -> None:
    assert check_consistency("therapist/data_transfer", REQ_A) is True


# ---------------------------------------------------------------------------
# 8. check_consistency — feature_paths differ → False, error printed
# ---------------------------------------------------------------------------


def test_check_consistency_mismatch(capsys: pytest.CaptureFixture[str]) -> None:
    result = check_consistency("wrong/path", REQ_A)
    assert result is False
    err = capsys.readouterr().err
    assert "LINT ERROR" in err
    assert "REQ-FUNC-007-01" in err


# ---------------------------------------------------------------------------
# 9. check_consistency — primary is None → False
# ---------------------------------------------------------------------------


def test_check_consistency_none_primary() -> None:
    assert check_consistency("therapist/data_transfer", None) is False


# ---------------------------------------------------------------------------
# 10. apply_updates — normalises legacy `requirement` scalar to array
# ---------------------------------------------------------------------------


def test_apply_updates_normalises_legacy(tmp_path: Path) -> None:
    content = "version: v1\nfeature_path: therapist/data_transfer\nrequirement: REQ-FUNC-007-01\n"
    meta = _make_metadata_file(tmp_path, content)

    apply_updates(
        meta,
        ["REQ-FUNC-007-01"],
        ["FLOW-002", "FLOW-003"],
        is_ambiguous=False,
        ambiguity_reason="",
        dry_run=False,
    )

    data = read_plain_yaml(meta)
    assert "requirement" not in data
    assert list(data["contributing_requirements"]) == ["REQ-FUNC-007-01"]
    assert list(data["participating_flows"]) == ["FLOW-002", "FLOW-003"]


# ---------------------------------------------------------------------------
# 11. apply_updates — dry_run does NOT write
# ---------------------------------------------------------------------------


def test_apply_updates_dry_run_no_write(tmp_path: Path) -> None:
    content = "version: v1\nfeature_path: x\n"
    meta = _make_metadata_file(tmp_path, content)
    mtime_before = meta.stat().st_mtime

    apply_updates(
        meta,
        ["REQ-X"],
        ["FLOW-001"],
        is_ambiguous=False,
        ambiguity_reason="",
        dry_run=True,
    )

    # File must not have been modified
    assert meta.stat().st_mtime == mtime_before


# ---------------------------------------------------------------------------
# 12. resolve_metadata_path — directory arg → dir/metadata.yaml
# ---------------------------------------------------------------------------


def test_resolve_metadata_path_dir(tmp_path: Path) -> None:
    result = resolve_metadata_path(str(tmp_path))
    assert result == tmp_path / "metadata.yaml"


# ---------------------------------------------------------------------------
# 13. resolve_metadata_path — file arg returned unchanged
# ---------------------------------------------------------------------------


def test_resolve_metadata_path_file(tmp_path: Path) -> None:
    p = tmp_path / "metadata.yaml"
    result = resolve_metadata_path(str(p))
    assert result == p


# ---------------------------------------------------------------------------
# 14. read_plain_yaml / write_plain_yaml — round-trip
# ---------------------------------------------------------------------------


def test_round_trip_plain_yaml(tmp_path: Path) -> None:
    content = "version: v2\nfeature_path: a/b\nstatus: draft\n"
    meta = _make_metadata_file(tmp_path, content)

    data = read_plain_yaml(meta)
    assert data["version"] == "v2"
    assert data["feature_path"] == "a/b"

    data["status"] = "reviewed"
    write_plain_yaml(meta, data)

    data2 = read_plain_yaml(meta)
    assert data2["status"] == "reviewed"
    assert data2["version"] == "v2"


# ---------------------------------------------------------------------------
# 15. _extract_flow_ids — handles edge cases
# ---------------------------------------------------------------------------


def test_extract_flow_ids_empty() -> None:
    from ruamel.yaml.comments import CommentedMap

    meta: CommentedMap = CommentedMap()
    assert _extract_flow_ids(meta) == []


def test_extract_flow_ids_no_user_needs() -> None:
    from ruamel.yaml.comments import CommentedMap

    meta: CommentedMap = CommentedMap({"id": "REQ-X"})
    assert _extract_flow_ids(meta) == []


def test_extract_flow_ids_present() -> None:
    from ruamel.yaml.comments import CommentedMap

    meta: CommentedMap = CommentedMap(
        {
            "user_needs": {
                "implements_flows": [
                    {"id": "FLOW-002", "steps": [1, 2]},
                    {"id": "FLOW-003"},
                ]
            }
        }
    )
    assert _extract_flow_ids(meta) == ["FLOW-002", "FLOW-003"]
