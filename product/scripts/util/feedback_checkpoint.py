#!/usr/bin/env python3
"""Shared renderer + filename resolver for feedback-checkpoint files (REQ-PROC-041-04 AC-06).

Single source of truth for the checkpoint envelope/body and filename, used by BOTH session modes:
  - automated: scripts/automation/orchestrate.py::_archive_feedback_checkpoint (mode: automated)
  - interactive: scripts/tasks/create_feedback_checkpoint.py (mode: interactive, REQ-PROC-044-03)

Keeping one renderer prevents the two modes' formats from drifting — the exact failure mode
doc/python/anti_patterns.md opens with (duplicated format/parse surfaces that share a bug but not
a fix). The envelope and body are identical across modes; only the `mode` value and the supplied
field contents differ.
"""

# tier: B  # reusable library; imported by orchestrate.py (A) and create_feedback_checkpoint.py (C)

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass

# Why: the filename stem is the load-bearing token — the registry glob
# (requirements_tasks/**/plans_and_protocols/*feedback-checkpoint*.md) matches on it, so both
# modes must spell it identically. One constant guarantees that.
FILENAME_STEM = "feedback-checkpoint"


@dataclass(frozen=True)
class CheckpointFields:
    """The values that populate one feedback-checkpoint file (envelope + body)."""

    skill: str
    mode: str  # "automated" | "interactive"
    decision: str
    task_id: str
    captured_at: str
    question: str
    answer: str
    rationale: str


def render_checkpoint(fields: CheckpointFields) -> str:
    """Return the full file content (YAML envelope + body) for one checkpoint.

    Pure function (no I/O, no clock read) so the AC-06 format is pinned by a direct unit test.
    `decision` is always emitted quoted so the automated path's empty `decision: ""` is preserved
    byte-for-byte when this renderer replaces its former inline string.
    """
    envelope = (
        "---\n"
        f"skill: {fields.skill}\n"
        f"mode: {fields.mode}\n"
        f'decision: "{fields.decision}"\n'
        f"task_id: {fields.task_id}\n"
        f"captured_at: {fields.captured_at}\n"
        "---\n\n"
    )
    body = (
        f"# Question\n\n{fields.question.strip()}\n\n"
        f"# Developer Answer\n\n{fields.answer.strip()}\n\n"
        f"# Rationale Captured\n\n{fields.rationale.strip()}\n"
    )
    return envelope + body


def resolve_checkpoint_path(
    protocols_dir: str,
    captured_at: str,
    exists: Callable[[str], bool],
) -> str:
    """Pick a non-colliding path: <date>_feedback-checkpoint.md, then _01, _02, ...

    `exists` is injected (orchestrator passes deps.file_exists; the CLI passes os.path.exists) so
    the resolver is testable without touching the real filesystem. Multiple checkpoints in one
    task each get their own file.
    """
    base = os.path.join(protocols_dir, f"{captured_at}_{FILENAME_STEM}.md")
    if not exists(base):
        return base
    suffix = 1
    while True:
        candidate = os.path.join(protocols_dir, f"{captured_at}_{FILENAME_STEM}_{suffix:02d}.md")
        if not exists(candidate):
            return candidate
        suffix += 1
