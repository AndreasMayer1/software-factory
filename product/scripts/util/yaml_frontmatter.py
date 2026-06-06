#!/usr/bin/env python3
"""
scripts/util/yaml_frontmatter.py

Central YAML-frontmatter helper (REQ-PROC-051 AC-08).

THIS MODULE IS ALLOW-LISTED FOR G4 (check_no_handrolled_yaml.py) — it is
the *only* place hand-rolled boundary detection is permitted. Every other
call site must import from here instead of parsing frontmatter directly.

Three use cases, three entry points:

1. read_frontmatter(text_or_path) -> FrontmatterDoc
   Read-only parsing. Returns FrontmatterDoc(metadata, body, raw_yaml).
   Uses ruamel round-trip loader so subsequent updates preserve comments
   and key order.

2. update_frontmatter(path, updates, *, remove_keys=())
   One-shot read-modify-write. Atomic (write to .tmp, fsync, rename).
   Comment-preserving. Existing key order preserved; new keys appended.

3. with frontmatter_session(path) as doc:
       doc.metadata['status'] = 'done'
   Context manager for non-trivial read-modify-write. On __exit__ without
   exception: atomic write. On exception: nothing written. Acquires an
   advisory fcntl lock on the file for the duration of the block.

Tier: B
"""

# tier: B  # reusable library; imported by every requirements/task script in TASK-PROC-051-04

# Why: ruamel.yaml is required (not PyYAML) because CommentedMap is the only
# mainstream Python data structure that preserves comments and key order through
# a round-trip parse → modify → serialize cycle. PyYAML silently drops comments,
# which would corrupt goal.md / protocol.md files that have inline comments.
# Source: requirements_tasks/process/AI_rules/coding_standards/python_code_quality/
#         tasks/2026-05-17_impl_python-tooling-config-and-gates/
#         plans_and_protocols/2026-05-17_01_plan_tooling-mechanism.md#D
# Tests: scripts/tests/test_yaml_frontmatter.py

from __future__ import annotations

import fcntl
import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class FrontmatterError(ValueError):
    """Raised when frontmatter cannot be parsed from a document."""


@dataclass
class FrontmatterDoc:
    """Parsed YAML-frontmatter document.

    metadata: mutable CommentedMap — comment-preserving, supports round-trip.
    body: the markdown content after the closing '---' delimiter.
    raw_yaml: the original YAML text between the delimiters, for diagnostics.
    """

    metadata: CommentedMap
    body: str
    raw_yaml: str
    _path: Path | None = field(default=None, repr=False)

    @property
    def has_frontmatter(self) -> bool:
        """True if the document contained a YAML frontmatter block."""
        return bool(self.raw_yaml)


def _make_yaml() -> YAML:
    """Return a ruamel YAML instance configured for round-trip with comments."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    return yaml


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split *text* into (raw_yaml, body).

    Why: hand-rolled boundary detection is the only pattern G4 allows here
    because this helper IS the central abstraction. All other modules must
    call read_frontmatter() instead of doing this themselves.
    Source: plans_and_protocols/2026-05-17_01_plan_tooling-mechanism.md#E
    (allow-list justification)

    Returns (raw_yaml, body) where raw_yaml is the text between the opening
    and closing '---' delimiters (exclusive), and body is everything after
    the closing delimiter. If the document has no frontmatter block,
    returns ('', text).
    """
    if not text.startswith("---"):
        return "", text

    # Skip the opening '---' line and scan for the closing delimiter
    lines = text.split("\n")
    in_frontmatter = True
    end_index: int | None = None
    for i, line in enumerate(lines):
        if i == 0:
            continue  # skip opening '---'
        if line.strip() == "---":
            end_index = i
            break

    if end_index is None:
        # Unclosed frontmatter — treat entire file as body (no frontmatter)
        return "", text

    raw_yaml = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :])
    # Canonical: body starts without a leading newline from the delimiter line
    if body.startswith("\n"):
        body = body[1:]
    _ = in_frontmatter  # consumed: flag is implicit in the loop above
    return raw_yaml, body


def _parse_yaml_block(raw_yaml: str) -> CommentedMap:
    """Parse a YAML string into a CommentedMap using round-trip loader."""
    if not raw_yaml.strip():
        return CommentedMap()
    yaml = _make_yaml()
    result = yaml.load(StringIO(raw_yaml))
    if result is None:
        return CommentedMap()
    if not isinstance(result, CommentedMap):
        raise FrontmatterError(
            f"Frontmatter must be a YAML mapping, got {type(result).__name__}"
        )
    return result


def read_frontmatter(source: str | Path) -> FrontmatterDoc:
    """Parse a file (or text string) and return a FrontmatterDoc.

    Parameters
    ----------
    source:
        Either a filesystem path or a raw text string. If a Path (or a str
        that is an existing file), the file is read as UTF-8. Otherwise the
        string is treated as document text.

    Raises
    ------
    FrontmatterError
        If the frontmatter block is present but malformed (e.g. not a mapping).
    """
    path: Path | None = None
    if isinstance(source, Path):
        path = source
        text = source.read_text(encoding="utf-8")
    else:
        # Check whether the string looks like a path to an existing file.
        # Why: Path(source).exists() raises OSError (ENAMETOOLONG, errno 36)
        # when source is a text string longer than NAME_MAX (~255 bytes on
        # most filesystems) — typical goal.md/requirements.md bodies trip
        # this. Any OSError from the path probe means "this isn't a usable
        # path", so we fall back to treating source as raw document text.
        # Source: requirements_tasks/process/AI_rules/coding_standards/
        #         python_code_quality/yaml_frontmatter_helper_followup_2026-05-18.md
        candidate = Path(source)
        try:
            is_existing_file = candidate.exists() and candidate.is_file()
        except OSError:
            is_existing_file = False
        if is_existing_file:
            path = candidate
            text = candidate.read_text(encoding="utf-8")
        else:
            text = source

    raw_yaml, body = _split_frontmatter(text)
    try:
        metadata = _parse_yaml_block(raw_yaml)
    except Exception as exc:
        raise FrontmatterError(f"Malformed frontmatter: {exc}") from exc

    return FrontmatterDoc(
        metadata=metadata,
        body=body,
        raw_yaml=raw_yaml,
        _path=path,
    )


def _serialize_frontmatter(doc: FrontmatterDoc) -> str:
    """Serialize *doc* back to a full file text (frontmatter + body)."""
    yaml = _make_yaml()
    buf = StringIO()
    yaml.dump(doc.metadata, buf)
    yaml_text = buf.getvalue()

    if not yaml_text.strip() and not doc.raw_yaml:
        # Document had no frontmatter originally; just return the body
        return doc.body

    return f"---\n{yaml_text}---\n{doc.body}"


def _atomic_write(path: Path, content: str) -> None:
    """Write *content* to *path* atomically via tmp-file + fsync + rename.

    Why: write-to-tmp → fsync → rename is the POSIX-guaranteed atomic
    update pattern. A plain open(path, 'w') write can leave a partially
    written file if the process is interrupted mid-write. With rename(),
    the file either has the old content or the new content — never a partial.
    The fsync() before rename ensures the data is on disk before the
    directory entry changes, guarding against power-loss between the
    two kernel calls.
    Source: plans_and_protocols/2026-05-17_01_plan_tooling-mechanism.md#D
    Tests: scripts/tests/test_yaml_frontmatter.py::test_update_is_atomic
    """
    dir_ = path.parent
    # NamedTemporaryFile in the same directory ensures rename stays on the
    # same filesystem (cross-device rename would fail with EXDEV).
    fd, tmp_path_str = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    tmp_path = Path(tmp_path_str)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        tmp_path.rename(path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def update_frontmatter(
    path: Path,
    updates: dict[str, Any],
    *,
    remove_keys: list[str] | None = None,
) -> None:
    """One-shot read-modify-write with comment preservation.

    Reads *path*, applies *updates* (upsert semantics — existing keys updated,
    new keys appended at the end), removes any keys in *remove_keys*, then
    writes atomically back to *path*.

    Parameters
    ----------
    path:
        Target file. Must exist.
    updates:
        Key-value pairs to set. Existing keys retain their position and
        comments; new keys are appended.
    remove_keys:
        Keys to delete from the frontmatter (silently ignored if absent).
    """
    if remove_keys is None:
        remove_keys = []

    doc = read_frontmatter(path)
    for key, value in updates.items():
        doc.metadata[key] = value
    for key in remove_keys:
        doc.metadata.pop(key, None)

    content = _serialize_frontmatter(doc)
    _atomic_write(path, content)


@contextmanager
def frontmatter_session(path: Path) -> Iterator[FrontmatterDoc]:
    """Context manager for multi-step read-modify-write of *path*'s frontmatter.

    Acquires an advisory exclusive lock (fcntl.LOCK_EX) on *path* on enter
    and releases it on exit, even if an exception occurs. The file is written
    atomically on clean exit; nothing is written if an exception propagates.

    Why: advisory fcntl locks coordinate concurrent writers (e.g. two agent
    sessions running simultaneously). The lock is 'advisory' — uncooperative
    processes can ignore it — but all paths that write frontmatter go through
    this module, so cooperative locking is sufficient.
    Source: plans_and_protocols/2026-05-17_01_plan_tooling-mechanism.md#D
    Tests: scripts/tests/test_yaml_frontmatter.py::test_session_releases_lock_on_exception

    Usage
    -----
    with frontmatter_session(path) as doc:
        doc.metadata['status'] = 'done'
        doc.metadata.setdefault('audit', []).append('2026-05-17')
    # File written atomically here; lock released.
    """
    lock_fd = path.open("r", encoding="utf-8")
    try:
        # Why: LOCK_EX blocks until the lock is acquired; LOCK_NB would raise
        # immediately. Blocking is the safer default for sequential scripts
        # where contention means "wait your turn", not "give up".
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        doc = read_frontmatter(path)
        try:
            yield doc
        except Exception:
            # On exception: release lock, do NOT write
            raise
        else:
            # Clean exit: write atomically, then release lock
            content = _serialize_frontmatter(doc)
            _atomic_write(path, content)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()
