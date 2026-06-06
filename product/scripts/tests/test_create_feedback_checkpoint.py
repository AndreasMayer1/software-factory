#!/usr/bin/env python3
"""CLI tests for scripts/tasks/create_feedback_checkpoint.py (REQ-PROC-044-03).

Exercises the interactive writer end-to-end: AC-03 filename (contains 'feedback-checkpoint', NO
TASK-ID, under plans_and_protocols/, matches the registry glob), verbatim preservation, and the
AC-01 negative case (empty answer produces no file). The envelope/body format and the filename
resolver are unit-tested at the shared layer in test_feedback_checkpoint.py.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

MODULE_PATH = Path(__file__).resolve().parent.parent / "tasks" / "create_feedback_checkpoint.py"


def _run(*args: str) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(
        [sys.executable, str(MODULE_PATH), *args],
        capture_output=True,
        text=True,
    )


def test_cli_writes_file_matching_registry_glob(tmp_path: Path) -> None:
    protocols = tmp_path / "plans_and_protocols"
    protocols.mkdir()
    answer = tmp_path / "answer.txt"
    answer.write_text("Drop the TASK-ID; we're already in the tasks folder.")

    result = _run(
        "--skill", "task-complete",
        "--decision", "redirected",
        "--task-id", "TASK-PROC-044-03-01",
        "--protocols-dir", str(protocols),
        "--answer-file", str(answer),
        "--question-text", "Name the file with the TASK-ID.",
    )

    assert result.returncode == 0, result.stderr
    written = list(protocols.glob("*feedback-checkpoint*.md"))  # AC-03 registry glob
    assert len(written) == 1
    assert "TASK-" not in written[0].name  # developer steering: no TASK-ID in filename
    text = written[0].read_text()
    assert "mode: interactive" in text
    assert "Drop the TASK-ID" in text  # verbatim preserved


def test_cli_refuses_empty_answer(tmp_path: Path) -> None:
    protocols = tmp_path / "plans_and_protocols"
    protocols.mkdir()
    answer = tmp_path / "answer.txt"
    answer.write_text("   \n")

    result = _run(
        "--skill", "task-complete",
        "--decision", "revised",
        "--task-id", "TASK-X",
        "--protocols-dir", str(protocols),
        "--answer-file", str(answer),
    )

    assert result.returncode == 2  # AC-01 negative case: no file for an empty / non-steering input
    assert list(protocols.glob("*.md")) == []
