# tier: B
"""Tests for scripts/quality/check_scribble_parity.py (REQ-PROC-032 AC-37).

Tests pure logic functions directly using tmp_path fixtures with fake trees.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("yaml", reason="PyYAML not installed in test environment")

sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
import check_scribble_parity as csp  # type: ignore[import-not-found]  # runtime path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_scribble_meta(scribbles_root: Path, feature_path: str, version: str = "v1") -> None:
    """Create a minimal metadata.yaml for the given feature_path and version."""
    meta_dir = scribbles_root / feature_path / version
    meta_dir.mkdir(parents=True, exist_ok=True)
    (meta_dir / "metadata.yaml").write_text(f"feature_path: {feature_path}\nstatus: draft\n")


def make_lib_leaf(features_root: Path, feature_path: str) -> None:
    """Create a minimal lib/features/ leaf with a presentation/ subdir."""
    (features_root / feature_path / "presentation").mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# collect_scribble_feature_paths
# ---------------------------------------------------------------------------


def test_collects_feature_path_from_metadata(tmp_path: Path) -> None:
    scribbles_root = tmp_path / "requirements_tasks" / "scribbles"
    make_scribble_meta(scribbles_root, "therapist/data_transfer")

    result = csp.collect_scribble_feature_paths(scribbles_root)

    assert result == {"therapist/data_transfer"}


def test_deduplication_across_versions(tmp_path: Path) -> None:
    """Same feature_path in v1 and v2 is counted once."""
    scribbles_root = tmp_path / "requirements_tasks" / "scribbles"
    make_scribble_meta(scribbles_root, "therapist/data_transfer", "v1")
    make_scribble_meta(scribbles_root, "therapist/data_transfer", "v2")

    result = csp.collect_scribble_feature_paths(scribbles_root)

    assert result == {"therapist/data_transfer"}


def test_missing_scribbles_root_returns_empty_set(tmp_path: Path) -> None:
    scribbles_root = tmp_path / "requirements_tasks" / "scribbles"

    result = csp.collect_scribble_feature_paths(scribbles_root)

    assert result == set()


# ---------------------------------------------------------------------------
# collect_lib_features_leaves
# ---------------------------------------------------------------------------


def test_leaf_detected_by_presentation_subdir(tmp_path: Path) -> None:
    features_root = tmp_path / "lib" / "features"
    make_lib_leaf(features_root, "therapist/data_transfer")

    result = csp.collect_lib_features_leaves(features_root)

    assert "therapist/data_transfer" in result


def test_intermediate_dir_without_presentation_not_a_leaf(tmp_path: Path) -> None:
    """lib/features/therapist/ alone (no presentation/) is not reported as a leaf."""
    features_root = tmp_path / "lib" / "features"
    (features_root / "therapist").mkdir(parents=True)
    make_lib_leaf(features_root, "therapist/data_transfer")

    result = csp.collect_lib_features_leaves(features_root)

    assert "therapist" not in result
    assert "therapist/data_transfer" in result


def test_missing_features_root_returns_empty_set(tmp_path: Path) -> None:
    features_root = tmp_path / "lib" / "features"

    result = csp.collect_lib_features_leaves(features_root)

    assert result == set()


# ---------------------------------------------------------------------------
# check_parity
# ---------------------------------------------------------------------------


def test_valid_scribble_path_passes(tmp_path: Path) -> None:
    features_root = tmp_path / "lib" / "features"
    scribbles_root = tmp_path / "requirements_tasks" / "scribbles"
    make_lib_leaf(features_root, "therapist/data_transfer")
    make_scribble_meta(scribbles_root, "therapist/data_transfer")

    errors, _warnings = csp.check_parity(
        {"therapist/data_transfer"},
        {"therapist/data_transfer"},
        features_root,
        scribbles_root,
    )

    assert errors == []


def test_stale_scribble_path_is_error(tmp_path: Path) -> None:
    """Scribble feature_path with no matching lib/features/ node → ERROR."""
    features_root = tmp_path / "lib" / "features"
    scribbles_root = tmp_path / "requirements_tasks" / "scribbles"
    features_root.mkdir(parents=True)
    make_scribble_meta(scribbles_root, "deleted/feature")

    errors, _warnings = csp.check_parity(
        {"deleted/feature"},
        set(),
        features_root,
        scribbles_root,
    )

    assert len(errors) == 1
    assert "stale scribble path" in errors[0]
    assert "deleted/feature" in errors[0]


def test_coverage_gap_is_warning_not_error(tmp_path: Path) -> None:
    """lib/features/ leaf with no scribble → WARNING, not ERROR."""
    features_root = tmp_path / "lib" / "features"
    scribbles_root = tmp_path / "requirements_tasks" / "scribbles"
    make_lib_leaf(features_root, "therapist/clients")
    scribbles_root.mkdir(parents=True)

    errors, warnings = csp.check_parity(
        set(),
        {"therapist/clients"},
        features_root,
        scribbles_root,
    )

    assert errors == []
    assert len(warnings) == 1
    assert "coverage gap" in warnings[0]
    assert "therapist/clients" in warnings[0]


# ---------------------------------------------------------------------------
# run_check — exit codes and flags
# ---------------------------------------------------------------------------


def test_exit_0_when_only_warnings(tmp_path: Path) -> None:
    """Exit code is 0 when only coverage-gap warnings exist (no --strict)."""
    features_root = tmp_path / "lib" / "features"
    scribbles_root = tmp_path / "requirements_tasks" / "scribbles"
    make_lib_leaf(features_root, "home")
    scribbles_root.mkdir(parents=True)

    exit_code = csp.run_check(tmp_path)

    assert exit_code == 0


def test_strict_promotes_warnings_to_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--strict: coverage-gap warnings become errors; exit code 1."""
    features_root = tmp_path / "lib" / "features"
    scribbles_root = tmp_path / "requirements_tasks" / "scribbles"
    make_lib_leaf(features_root, "home")
    scribbles_root.mkdir(parents=True)

    exit_code = csp.run_check(tmp_path, strict=True)

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "ERROR" in captured.out


def test_quiet_suppresses_warnings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--quiet: warning lines suppressed; exit code still 0."""
    features_root = tmp_path / "lib" / "features"
    scribbles_root = tmp_path / "requirements_tasks" / "scribbles"
    make_lib_leaf(features_root, "home")
    scribbles_root.mkdir(parents=True)

    exit_code = csp.run_check(tmp_path, quiet=True)

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "WARNING" not in captured.out
