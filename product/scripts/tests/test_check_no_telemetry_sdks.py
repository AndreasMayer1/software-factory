# tier: B
"""Tests for scripts/quality/check_no_telemetry_sdks.py (REQ-PROC-052 SP2).

Tests the pure logic functions directly (parse_dependency_keys, find_violations)
without touching the real pubspec.yaml.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Module import — sys.path extended so the quality script can be imported
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
import check_no_telemetry_sdks as ct  # type: ignore[import-not-found]  # runtime path

# ---------------------------------------------------------------------------
# parse_dependency_keys
# ---------------------------------------------------------------------------

def test_parses_dependencies_section() -> None:
    yaml = "dependencies:\n  flutter:\n    sdk: flutter\n  provider: ^6.0.0\n"
    result = ct.parse_dependency_keys(yaml)
    assert "provider" in result["dependencies"]
    assert "flutter" in result["dependencies"]


def test_parses_dev_dependencies() -> None:
    yaml = "dev_dependencies:\n  mocktail: ^1.0.0\n  build_runner: ^2.4.0\n"
    result = ct.parse_dependency_keys(yaml)
    assert "mocktail" in result["dev_dependencies"]


def test_ignores_comments() -> None:
    yaml = "dependencies:\n  # firebase_analytics: ^10.0.0  # disabled\n  provider: ^6.0.0\n"
    result = ct.parse_dependency_keys(yaml)
    assert "firebase_analytics" not in result["dependencies"]
    assert "provider" in result["dependencies"]


# ---------------------------------------------------------------------------
# find_violations
# ---------------------------------------------------------------------------

def test_no_forbidden_sdks_passes() -> None:
    deps = {"dependencies": ["provider", "go_router"], "dev_dependencies": ["mocktail"],
            "dependency_overrides": []}
    violations = ct.find_violations(deps)
    assert violations == []


def test_firebase_analytics_flagged() -> None:
    deps = {"dependencies": ["firebase_analytics"], "dev_dependencies": [],
            "dependency_overrides": []}
    violations = ct.find_violations(deps)
    assert len(violations) == 1
    assert violations[0][1] == "firebase_analytics"
    assert "Firebase Analytics" in violations[0][2]


def test_sentry_flutter_flagged() -> None:
    deps = {"dependencies": ["sentry_flutter"], "dev_dependencies": [],
            "dependency_overrides": []}
    violations = ct.find_violations(deps)
    assert len(violations) == 1
    assert "Sentry" in violations[0][2]


def test_companion_package_flagged() -> None:
    """firebase_analytics_web starts with firebase_analytics_ → flagged."""
    deps = {"dependencies": ["firebase_analytics_web"], "dev_dependencies": [],
            "dependency_overrides": []}
    violations = ct.find_violations(deps)
    assert len(violations) == 1


def test_multiple_forbidden_sdks_all_flagged() -> None:
    deps = {"dependencies": ["firebase_analytics", "sentry_flutter"],
            "dev_dependencies": ["bugsnag_flutter"], "dependency_overrides": []}
    violations = ct.find_violations(deps)
    assert len(violations) == 3


# ---------------------------------------------------------------------------
# main() integration — patch PUBSPEC and sys.argv (main uses parse_args())
# ---------------------------------------------------------------------------

def test_main_passes_on_clean_pubspec(tmp_path: Path) -> None:
    pubspec = tmp_path / "pubspec.yaml"
    pubspec.write_text("dependencies:\n  flutter:\n    sdk: flutter\n  provider: ^6.0.0\n")
    with (patch.object(ct, "PUBSPEC", pubspec),
          patch.object(ct, "PROJECT_ROOT", tmp_path),
          patch("sys.argv", ["check_no_telemetry_sdks.py"])):
        rc = ct.main()
    assert rc == 0


def test_main_fails_on_forbidden_sdk(tmp_path: Path) -> None:
    pubspec = tmp_path / "pubspec.yaml"
    pubspec.write_text("dependencies:\n  firebase_analytics: ^10.0.0\n")
    with (patch.object(ct, "PUBSPEC", pubspec),
          patch.object(ct, "PROJECT_ROOT", tmp_path),
          patch("sys.argv", ["check_no_telemetry_sdks.py"])):
        rc = ct.main()
    assert rc == 1


def test_main_returns_2_when_pubspec_missing(tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent.yaml"
    with (patch.object(ct, "PUBSPEC", missing),
          patch.object(ct, "PROJECT_ROOT", tmp_path),
          patch("sys.argv", ["check_no_telemetry_sdks.py"])):
        rc = ct.main()
    assert rc == 2
