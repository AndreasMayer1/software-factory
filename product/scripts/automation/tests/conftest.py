# ruff: noqa: RUF100
# RUF100: false-positive on file-level noqa for codes ruff cannot introspect into the file body.
"""
conftest.py -- pytest session-level fixture that redirects every module-level
filesystem path constant in orchestrate.py to a temporary directory.

Why: orchestrate.py resolves AUTOMATION_DIR (and all derived paths) against the
real PROJECT_ROOT at import time.  Any test that exercises production code paths —
even indirectly — would otherwise write to automation/state.json and fool the
sleep watchdog into thinking the orchestrator has stopped.  A session-scoped
autouse fixture ensures isolation without requiring individual tests to opt in.
"""

# tier: A  # session fixture; owns test isolation invariant for the whole run

import os
import sys
from collections.abc import Generator

import pytest
from pytest import MonkeyPatch

# Ensure orchestrate is importable (mirrors the sys.path setup in the test files)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import orchestrate  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation


@pytest.fixture(scope="session")
def monkeypatch_session() -> Generator[MonkeyPatch, None, None]:
    """Session-scoped MonkeyPatch context.

    Why: pytest's built-in monkeypatch fixture is function-scoped and cannot be
    used directly in session-scoped fixtures.  MonkeyPatch.context() provides the
    same undo semantics at session granularity — all patches are reverted when the
    session ends, even if it exits abnormally.
    """
    with MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope="session", autouse=True)
def _isolate_automation_paths(
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch_session: MonkeyPatch,
) -> None:
    """Redirect every orchestrate module-level path constant to a temp directory.

    Why: prevents the test suite from ever touching the real automation/ folder.
    The fixture is autouse so every test in the session benefits automatically
    without an opt-in import or fixture request.

    Sub-directories created mirror the expected production layout so that
    production code that calls os.makedirs(..., exist_ok=True) does not fail when
    the directory already exists, and code that expects sub-dirs to be present
    finds them ready.
    """
    tmp = tmp_path_factory.mktemp("automation_test_artifacts")

    # Mirror the production sub-directory layout
    for subdir in ("pending_feedback", "answered_feedback", "session_outputs", "reports"):
        (tmp / subdir).mkdir(parents=True, exist_ok=True)

    automation_dir = str(tmp)
    state_path = os.path.join(automation_dir, "state.json")
    feedback_dir = os.path.join(automation_dir, "pending_feedback")
    answered_dir = os.path.join(automation_dir, "answered_feedback")
    answer_template_path = os.path.join(feedback_dir, "TEMPLATE_answer.md")
    outputs_dir = os.path.join(automation_dir, "session_outputs")
    reports_dir = os.path.join(automation_dir, "reports")
    sentinel_automated = os.path.join(automation_dir, ".automated_mode")

    monkeypatch_session.setattr(orchestrate, "AUTOMATION_DIR", automation_dir)
    monkeypatch_session.setattr(orchestrate, "STATE_PATH", state_path)
    monkeypatch_session.setattr(orchestrate, "FEEDBACK_DIR", feedback_dir)
    monkeypatch_session.setattr(orchestrate, "ANSWERED_DIR", answered_dir)
    monkeypatch_session.setattr(orchestrate, "ANSWER_TEMPLATE_PATH", answer_template_path)
    monkeypatch_session.setattr(orchestrate, "OUTPUTS_DIR", outputs_dir)
    monkeypatch_session.setattr(orchestrate, "REPORTS_DIR", reports_dir)
    monkeypatch_session.setattr(orchestrate, "SENTINEL_AUTOMATED", sentinel_automated)
