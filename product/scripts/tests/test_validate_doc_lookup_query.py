#!/usr/bin/env python3
"""Tests for scripts/util/validate_doc_lookup_query.py."""

import pytest

from scripts.util import validate_doc_lookup_query as vdq

# ---------------------------------------------------------------------------
# sanitize() — core stripping logic
# ---------------------------------------------------------------------------


def test_keeps_package_identifier() -> None:
    assert vdq.sanitize("package:flutter") == "package:flutter"


def test_keeps_dart_identifier() -> None:
    assert vdq.sanitize("dart:async") == "dart:async"


def test_keeps_dotted_api_path() -> None:
    assert vdq.sanitize("ListView.builder.itemBuilder") == "ListView.builder.itemBuilder"


def test_keeps_version_number() -> None:
    assert vdq.sanitize("3.24.0") == "3.24.0"


def test_keeps_plain_word() -> None:
    assert vdq.sanitize("flutter") == "flutter"


def test_strips_absolute_path_token() -> None:
    result = vdq.sanitize("/workspaces/private_mood_tracker/lib/foo.dart")
    assert result == ""


def test_strips_relative_path_token() -> None:
    result = vdq.sanitize("lib/features/mood/bloc.dart")
    assert result == ""


def test_strips_backslash_path() -> None:
    result = vdq.sanitize("lib\\features\\bloc.dart")
    assert result == ""


def test_strips_tilde_home_path() -> None:
    result = vdq.sanitize("~/project/lib/foo.dart")
    assert result == ""


def test_strips_dot_relative_path() -> None:
    result = vdq.sanitize("./lib/foo.dart")
    assert result == ""


def test_mixed_query_removes_paths_keeps_api() -> None:
    raw = "flutter ListView.builder.itemBuilder /workspaces/project/lib/foo.dart 3.24.0"
    result = vdq.sanitize(raw)
    assert "ListView.builder.itemBuilder" in result
    assert "flutter" in result
    assert "3.24.0" in result
    assert "/workspaces" not in result
    assert "lib/foo.dart" not in result


def test_query_with_only_paths_returns_empty() -> None:
    result = vdq.sanitize("lib/foo.dart scripts/bar.py")
    assert result == ""


def test_multiple_packages_preserved() -> None:
    result = vdq.sanitize("package:flutter package:flutter_bloc dart:async")
    assert result == "package:flutter package:flutter_bloc dart:async"


# ---------------------------------------------------------------------------
# main() — CLI behaviour
# ---------------------------------------------------------------------------


def test_main_prints_sanitized_query(capsys: pytest.CaptureFixture[str]) -> None:
    rc = vdq.main(["flutter", "ListView.builder"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "flutter" in captured.out
    assert "ListView.builder" in captured.out


def test_main_exits_1_when_no_args(capsys: pytest.CaptureFixture[str]) -> None:
    rc = vdq.main([])
    assert rc == 1
    assert "Usage" in capsys.readouterr().err


def test_main_exits_1_when_query_all_paths(capsys: pytest.CaptureFixture[str]) -> None:
    rc = vdq.main(["lib/foo.dart", "/workspaces/bar.dart"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "empty after sanitization" in captured.err


def test_main_joins_multiple_argv_words(capsys: pytest.CaptureFixture[str]) -> None:
    rc = vdq.main(["package:flutter", "itemBuilder", "signature"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "package:flutter itemBuilder signature" in captured.out
