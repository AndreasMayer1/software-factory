"""Tests for scripts/release/check_dependency_usage.py."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

pytest.importorskip("yaml", reason="PyYAML not installed in test environment")

_MODULE_PATH = (
    Path(__file__).resolve().parent.parent / "release" / "check_dependency_usage.py"
)
_spec = importlib.util.spec_from_file_location("check_dependency_usage", _MODULE_PATH)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_parse_pubspec_deps = _mod._parse_pubspec_deps
_scan_import_counts = _mod._scan_import_counts
_classify = _mod._classify
classify_dependencies = _mod.classify_dependencies
INDIRECT_REQUIREMENTS = _mod.INDIRECT_REQUIREMENTS
main = _mod.main


# ---------------------------------------------------------------------------
# _classify — pure function
# ---------------------------------------------------------------------------


def test_classify_directly_imported() -> None:
    r = _classify("flutter_bloc", 3)
    assert r.classification == "directly_imported"
    assert r.import_count == 3
    assert r.name == "flutter_bloc"


def test_classify_indirectly_required_known() -> None:
    r = _classify("sqlite3_flutter_libs", 0)
    assert r.classification == "indirectly_required"
    assert "drift" in r.indirect_reason.lower()


def test_classify_no_evidence() -> None:
    r = _classify("totally_unused_pkg", 0)
    assert r.classification == "no_evidence_of_use"
    assert r.import_count == 0
    assert r.indirect_reason == ""


def test_classify_indirect_overrides_zero_imports() -> None:
    """Packages in INDIRECT_REQUIREMENTS with 0 imports → indirectly_required, not no_evidence."""
    for pkg in INDIRECT_REQUIREMENTS:
        r = _classify(pkg, 0)
        assert r.classification == "indirectly_required", f"failed for {pkg}"


def test_classify_direct_import_overrides_indirect_list() -> None:
    """A package in INDIRECT_REQUIREMENTS that also has imports → directly_imported wins."""
    r = _classify("build_runner", 2)
    assert r.classification == "directly_imported"


# ---------------------------------------------------------------------------
# _parse_pubspec_deps — uses tmp_path
# ---------------------------------------------------------------------------

_PUBSPEC_CONTENT = """\
name: test_app
dependencies:
  flutter:
    sdk: flutter
  flutter_localizations:
    sdk: flutter
  go_router: ^16.0.0
  drift: ^2.22.0
  path: any
dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: any
  drift_dev: any
"""


def test_parse_excludes_sdk_packages(tmp_path: Path) -> None:
    (tmp_path / "pubspec.yaml").write_text(_PUBSPEC_CONTENT)
    deps = _parse_pubspec_deps(tmp_path)
    assert "flutter" not in deps["direct"]
    assert "flutter_localizations" not in deps["direct"]
    assert "flutter_test" not in deps["dev"]


def test_parse_includes_pub_packages(tmp_path: Path) -> None:
    (tmp_path / "pubspec.yaml").write_text(_PUBSPEC_CONTENT)
    deps = _parse_pubspec_deps(tmp_path)
    assert "go_router" in deps["direct"]
    assert "drift" in deps["direct"]
    assert "path" in deps["direct"]
    assert "build_runner" in deps["dev"]
    assert "drift_dev" in deps["dev"]


def test_parse_missing_pubspec_exits_1(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        _parse_pubspec_deps(tmp_path)
    assert exc.value.code == 1


# ---------------------------------------------------------------------------
# _scan_import_counts — uses tmp_path with Dart files
# ---------------------------------------------------------------------------


def test_scan_counts_direct_import(tmp_path: Path) -> None:
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "main.dart").write_text("import 'package:go_router/go_router.dart';\n")
    counts = _scan_import_counts(tmp_path, ["go_router", "drift"])
    assert counts["go_router"] == 1
    assert counts["drift"] == 0


def test_scan_counts_multiple_files(tmp_path: Path) -> None:
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "a.dart").write_text("import 'package:drift/drift.dart';\n")
    (lib / "b.dart").write_text("import 'package:drift/drift.dart';\n")
    counts = _scan_import_counts(tmp_path, ["drift"])
    assert counts["drift"] == 2


def test_scan_counts_by_file_not_by_import_line(tmp_path: Path) -> None:
    """Two import lines for the same package in one file → count 1, not 2."""
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "a.dart").write_text(
        "import 'package:drift/drift.dart';\nimport 'package:drift/isolate.dart';\n"
    )
    counts = _scan_import_counts(tmp_path, ["drift"])
    assert counts["drift"] == 1


def test_scan_skips_missing_dirs(tmp_path: Path) -> None:
    # No lib/, test/, integration_test/ dirs — should not error.
    counts = _scan_import_counts(tmp_path, ["go_router"])
    assert counts["go_router"] == 0


def test_scan_handles_double_quotes(tmp_path: Path) -> None:
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "a.dart").write_text('import "package:equatable/equatable.dart";\n')
    counts = _scan_import_counts(tmp_path, ["equatable"])
    assert counts["equatable"] == 1


# ---------------------------------------------------------------------------
# classify_dependencies — integration
# ---------------------------------------------------------------------------


def test_classify_dependencies_full(tmp_path: Path) -> None:
    (tmp_path / "pubspec.yaml").write_text(_PUBSPEC_CONTENT)
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "router.dart").write_text("import 'package:go_router/go_router.dart';\n")
    (lib / "db.dart").write_text("import 'package:drift/drift.dart';\n")

    direct, dev = classify_dependencies(tmp_path)
    direct_by_name = {r.name: r for r in direct}
    dev_by_name = {r.name: r for r in dev}

    assert direct_by_name["go_router"].classification == "directly_imported"
    assert direct_by_name["drift"].classification == "directly_imported"
    assert direct_by_name["path"].classification == "indirectly_required"
    assert dev_by_name["build_runner"].classification == "indirectly_required"
    assert dev_by_name["drift_dev"].classification == "indirectly_required"


# ---------------------------------------------------------------------------
# main() — JSON and human-readable output
# ---------------------------------------------------------------------------


def test_main_json_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "pubspec.yaml").write_text(_PUBSPEC_CONTENT)
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "a.dart").write_text("import 'package:go_router/go_router.dart';\n")

    with patch.object(_mod, "PROJECT_ROOT", tmp_path):
        main_args = ["--json", "--project-root", str(tmp_path)]
        with patch("sys.argv", ["check_dependency_usage.py", *main_args]):
            main()

    captured = capsys.readouterr()
    data: dict[str, Any] = json.loads(captured.out)
    assert "direct" in data
    assert "dev" in data
    assert "removal_candidates" in data
    names = [r["name"] for r in data["direct"]]
    assert "go_router" in names


def test_main_human_readable_shows_removal(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "pubspec.yaml").write_text(_PUBSPEC_CONTENT)
    # Don't create any dart files — go_router and drift have no imports.

    with patch("sys.argv", ["check_dependency_usage.py", "--project-root", str(tmp_path)]):
        main()

    captured = capsys.readouterr()
    assert "REMOVAL CANDIDATE" in captured.out or "removal candidates" in captured.out.lower()
