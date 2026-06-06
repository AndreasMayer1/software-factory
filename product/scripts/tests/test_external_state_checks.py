#!/usr/bin/env python3
"""Tests for the external-state postcondition validators (REQ-PROC-044 FU-8).

Covers the importable predicate functions of scripts/factory/external_state/*.
Network-only and OS-only paths (live URL fetch, real package install) are not
exercised here — see the README's "could not validate" note.
"""

from pathlib import Path

from scripts.factory.external_state import (
    check_command_exited_zero as cmd_exit,
)
from scripts.factory.external_state import (
    check_command_output_nonempty as cmd_out,
)
from scripts.factory.external_state import (
    check_developer_responded as dev,
)
from scripts.factory.external_state import (
    check_file_exists_at_path as fexists,
)
from scripts.factory.external_state import (
    check_json_event_wellformed as jevent,
)
from scripts.factory.external_state import (
    check_network_host_allowlisted as net,
)
from scripts.factory.external_state import (
    check_package_installed_at_version as pkg,
)
from scripts.factory.external_state import (
    check_url_returned_2xx as url,
)


def test_command_exited_zero() -> None:
    assert cmd_exit.exit_code(["true"]) == 0
    assert cmd_exit.exit_code(["false"]) == 1


def test_command_output_nonempty() -> None:
    assert cmd_out.stdout_nonempty(["echo", "hi"]) is True
    assert cmd_out.stdout_nonempty(["true"]) is False


def test_is_2xx() -> None:
    assert url.is_2xx(200) is True
    assert url.is_2xx(299) is True
    assert url.is_2xx(404) is False


def test_file_ok(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("xyz")
    assert fexists.file_ok(f, 0) is True
    assert fexists.file_ok(f, 3) is True
    assert fexists.file_ok(f, 4) is False
    assert fexists.file_ok(tmp_path / "missing", 0) is False


def test_developer_responded(tmp_path: Path) -> None:
    template = tmp_path / "TEMPLATE_answer.md"
    template.write_text("DO NOT let automation write here.")
    answer = tmp_path / "answer.md"
    assert dev.answered(answer, template) is False  # missing
    answer.write_text("DO NOT let automation write here.")
    assert dev.answered(answer, template) is False  # still template
    answer.write_text("Yes, raise the budget.")
    assert dev.answered(answer, template) is True


def test_version_matches() -> None:
    assert pkg.version_matches("uv 0.5.1", "0.5.1") is True
    assert pkg.version_matches("uv 0.5.1", "0.6.0") is False


def test_host_allowed() -> None:
    allow = ["flutter.dev", "pub.dev"]
    assert net.host_allowed("https://docs.flutter.dev/api", allow) is True
    assert net.host_allowed("https://flutter.dev/", allow) is True
    assert net.host_allowed("https://evil.com/flutter.dev", allow) is False


def test_event_ok(tmp_path: Path) -> None:
    good = tmp_path / "e.json"
    good.write_text('{"event": "x", "ts": 1}')
    assert jevent.event_ok(good, ["event", "ts"]) == (True, "well-formed")
    assert jevent.event_ok(good, ["event", "missing"])[0] is False
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert jevent.event_ok(bad, [])[0] is False
