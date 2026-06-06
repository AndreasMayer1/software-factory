#!/usr/bin/env python3
"""
Unit tests for scripts/util/yaml_frontmatter.py (REQ-PROC-051 AC-08).

Tests cover all 10 required cases from the plan:
1.  read_frontmatter on file with frontmatter -> metadata + body extracted
2.  read_frontmatter on file without frontmatter -> metadata empty, body=full
3.  read_frontmatter on file with malformed frontmatter -> raises FrontmatterError
4.  update_frontmatter preserves trailing comments
5.  update_frontmatter preserves key order; appended keys go at end
6.  update_frontmatter is atomic (tmp file deleted if crash simulated)
7.  frontmatter_session writes on clean exit
8.  frontmatter_session does NOT write on exception
9.  frontmatter_session releases lock on exception
10. update_frontmatter removes keys from remove_keys
"""

import threading
from pathlib import Path

import pytest

from scripts.util.yaml_frontmatter import (
    FrontmatterError,
    frontmatter_session,
    read_frontmatter,
    update_frontmatter,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SIMPLE_FRONTMATTER = """\
---
task_id: TASK-001
status: pending
---

Body text here.
"""

NO_FRONTMATTER = """\
# Just a markdown file

No YAML header at all.
"""

FRONTMATTER_WITH_COMMENT = """\
---
task_id: TASK-002
# This comment must survive round-trip
status: done
---

Body.
"""

MALFORMED_FRONTMATTER = """\
---
- this
- is
- a list not a mapping
---

Body.
"""


# ---------------------------------------------------------------------------
# Test 1: read_frontmatter on file with frontmatter -> metadata + body extracted
# ---------------------------------------------------------------------------


def test_read_frontmatter_extracts_metadata_and_body(tmp_path: Path) -> None:
    target = tmp_path / "goal.md"
    target.write_text(SIMPLE_FRONTMATTER, encoding="utf-8")

    doc = read_frontmatter(target)

    assert doc.has_frontmatter is True
    assert doc.metadata["task_id"] == "TASK-001"
    assert doc.metadata["status"] == "pending"
    assert "Body text here." in doc.body


# ---------------------------------------------------------------------------
# Test 2: read_frontmatter on file without frontmatter -> metadata empty, body=full
# ---------------------------------------------------------------------------


def test_read_frontmatter_no_frontmatter_gives_empty_metadata(tmp_path: Path) -> None:
    target = tmp_path / "readme.md"
    target.write_text(NO_FRONTMATTER, encoding="utf-8")

    doc = read_frontmatter(target)

    assert doc.has_frontmatter is False
    assert len(doc.metadata) == 0
    assert "Just a markdown file" in doc.body


# ---------------------------------------------------------------------------
# Test 3: read_frontmatter on file with malformed frontmatter -> raises FrontmatterError
# ---------------------------------------------------------------------------


def test_read_frontmatter_raises_on_malformed(tmp_path: Path) -> None:
    target = tmp_path / "bad.md"
    target.write_text(MALFORMED_FRONTMATTER, encoding="utf-8")

    with pytest.raises(FrontmatterError):
        read_frontmatter(target)


# ---------------------------------------------------------------------------
# Test 4: update_frontmatter preserves trailing comments
# ---------------------------------------------------------------------------


def test_update_frontmatter_preserves_comments(tmp_path: Path) -> None:
    target = tmp_path / "task.md"
    target.write_text(FRONTMATTER_WITH_COMMENT, encoding="utf-8")

    update_frontmatter(target, {"status": "in_progress"})

    result = target.read_text(encoding="utf-8")
    # The comment on its own line should survive the round-trip
    assert "# This comment must survive round-trip" in result
    assert "status: in_progress" in result


# ---------------------------------------------------------------------------
# Test 5: update_frontmatter preserves key order; appended keys go at end
# ---------------------------------------------------------------------------


def test_update_frontmatter_preserves_key_order_and_appends_new(
    tmp_path: Path,
) -> None:
    target = tmp_path / "task.md"
    target.write_text(SIMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter(target, {"new_key": "new_value"})

    result = target.read_text(encoding="utf-8")
    # task_id should appear before status, which appears before new_key
    task_id_pos = result.index("task_id")
    status_pos = result.index("status")
    new_key_pos = result.index("new_key")
    assert task_id_pos < status_pos < new_key_pos


# ---------------------------------------------------------------------------
# Test 6: update_frontmatter is atomic (original intact if write interrupted)
# ---------------------------------------------------------------------------


def test_update_is_atomic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulate a crash mid-write: the tmp file is cleaned up and original is intact."""
    target = tmp_path / "task.md"
    target.write_text(SIMPLE_FRONTMATTER, encoding="utf-8")
    original = target.read_text(encoding="utf-8")

    # Monkeypatch os.rename to raise mid-way (simulating crash after write but
    # before rename completes)
    import os

    _real_rename = os.rename  # captured for documentation; test only patches with failing_rename

    def failing_rename(src: str, dst: str) -> None:
        raise OSError("Simulated mid-rename crash")

    monkeypatch.setattr("os.rename", failing_rename)

    with pytest.raises(OSError, match="Simulated"):
        update_frontmatter(target, {"status": "crashed"})

    # Original file must be unchanged
    assert target.read_text(encoding="utf-8") == original

    # The tmp file must have been cleaned up (no orphaned .tmp files)
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0


# ---------------------------------------------------------------------------
# Test 7: frontmatter_session writes on clean exit
# ---------------------------------------------------------------------------


def test_session_writes_on_clean_exit(tmp_path: Path) -> None:
    target = tmp_path / "goal.md"
    target.write_text(SIMPLE_FRONTMATTER, encoding="utf-8")

    with frontmatter_session(target) as doc:
        doc.metadata["status"] = "in_progress"

    result = target.read_text(encoding="utf-8")
    assert "status: in_progress" in result


# ---------------------------------------------------------------------------
# Test 8: frontmatter_session does NOT write on exception
# ---------------------------------------------------------------------------


def test_session_does_not_write_on_exception(tmp_path: Path) -> None:
    target = tmp_path / "goal.md"
    target.write_text(SIMPLE_FRONTMATTER, encoding="utf-8")

    with pytest.raises(RuntimeError, match="deliberate"), frontmatter_session(target) as doc:
        doc.metadata["status"] = "in_progress"
        raise RuntimeError("deliberate error")

    result = target.read_text(encoding="utf-8")
    # The original value must still be there
    assert "status: pending" in result
    assert "status: in_progress" not in result


# ---------------------------------------------------------------------------
# Test 9: frontmatter_session releases lock on exception
# ---------------------------------------------------------------------------


def test_session_releases_lock_on_exception(tmp_path: Path) -> None:
    """After an exception in a session, a second session can acquire the lock."""
    target = tmp_path / "goal.md"
    target.write_text(SIMPLE_FRONTMATTER, encoding="utf-8")

    with pytest.raises(RuntimeError), frontmatter_session(target) as _doc:
        raise RuntimeError("force exception")

    # Why: if the lock were not released, this second session would deadlock.
    # We run it in a thread with a timeout to detect the deadlock case.
    acquired: list[bool] = []

    def try_second_session() -> None:
        with frontmatter_session(target) as doc:
            doc.metadata["status"] = "second_write"
        acquired.append(True)

    thread = threading.Thread(target=try_second_session)
    thread.start()
    thread.join(timeout=5.0)

    assert thread.is_alive() is False, "Lock was not released — second session deadlocked"
    assert acquired == [True]


# ---------------------------------------------------------------------------
# Test 10: update_frontmatter removes keys from remove_keys
# ---------------------------------------------------------------------------


def test_update_frontmatter_removes_keys(tmp_path: Path) -> None:
    target = tmp_path / "task.md"
    target.write_text(SIMPLE_FRONTMATTER, encoding="utf-8")

    update_frontmatter(target, {}, remove_keys=["status"])

    result = target.read_text(encoding="utf-8")
    assert "status" not in result
    assert "task_id: TASK-001" in result


# ---------------------------------------------------------------------------
# Test 11: read_frontmatter on long text string does not raise ENAMETOOLONG
# ---------------------------------------------------------------------------


def test_read_frontmatter_long_text_no_enametoolong() -> None:
    """Regression: text longer than NAME_MAX must not raise OSError.

    Why: read_frontmatter dispatches via Path(source).exists() to decide
    whether source is a path or raw text. That call raises OSError (errno
    36, ENAMETOOLONG) when source exceeds NAME_MAX (~255 bytes). Typical
    goal.md / requirements.md contents trip this. The dispatch must
    treat OSError as "not a path" and fall back to text parsing.
    """
    body_padding = "x" * 1000
    long_text = (
        "---\n"
        "task_id: TASK-LONG-001\n"
        "status: pending\n"
        "---\n"
        f"\n{body_padding}\n"
    )
    assert len(long_text) > 255  # would trip NAME_MAX on Path.exists()

    doc = read_frontmatter(long_text)

    assert doc.has_frontmatter is True
    assert doc.metadata["task_id"] == "TASK-LONG-001"
    assert doc.metadata["status"] == "pending"
    assert body_padding in doc.body
