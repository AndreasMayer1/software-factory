#!/usr/bin/env python3
"""Unit tests for scripts/util/feedback_checkpoint.py — the shared checkpoint renderer.

Pins the REQ-PROC-041-04 AC-06 envelope/body for BOTH modes, the byte-identical automated
`decision: ""`, and the filename resolver's _NN suffixing. This is the single source of truth for
the format used by orchestrate.py (automated) and create_feedback_checkpoint.py (interactive).
"""

from __future__ import annotations

from scripts.util.feedback_checkpoint import (
    FILENAME_STEM,
    CheckpointFields,
    render_checkpoint,
    resolve_checkpoint_path,
)


def _fields(**overrides: str) -> CheckpointFields:
    base = {
        "skill": "requ-explore",
        "mode": "interactive",
        "decision": "revised",
        "task_id": "TASK-PROC-044-03-01",
        "captured_at": "2026-06-02",
        "question": "Put the requirement under folder X.",
        "answer": "No, use folder Y because it groups with the sibling feature.",
        "rationale": "Y keeps the cascade scan in one place.",
    }
    base.update(overrides)
    return CheckpointFields(**base)


def test_render_pins_ac06_envelope_interactive() -> None:
    out = render_checkpoint(_fields())

    assert out.startswith("---\n")
    assert "skill: requ-explore\n" in out
    assert "mode: interactive\n" in out
    assert 'decision: "revised"\n' in out  # decision is quoted
    assert "task_id: TASK-PROC-044-03-01\n" in out
    assert "captured_at: 2026-06-02\n" in out
    assert "# Question\n" in out
    assert "# Developer Answer\n" in out
    assert "# Rationale Captured\n" in out
    assert "No, use folder Y because it groups with the sibling feature." in out  # verbatim


def test_render_automated_empty_decision_is_byte_preserved() -> None:
    """The former inline orchestrate.py output emitted `decision: ""` — must be preserved."""
    out = render_checkpoint(
        _fields(
            mode="automated",
            decision="",
            question="Q",
            answer="A",
            rationale="(Automated archival — no rationale extracted.)",
        )
    )

    expected = (
        "---\n"
        "skill: requ-explore\n"
        "mode: automated\n"
        'decision: ""\n'
        "task_id: TASK-PROC-044-03-01\n"
        "captured_at: 2026-06-02\n"
        "---\n\n"
        "# Question\n\nQ\n\n"
        "# Developer Answer\n\nA\n\n"
        "# Rationale Captured\n\n(Automated archival — no rationale extracted.)\n"
    )
    assert out == expected


def test_resolve_path_no_task_id_and_suffixes_on_collision() -> None:
    taken: set[str] = set()

    first = resolve_checkpoint_path("/p", "2026-06-02", lambda p: p in taken)
    assert first == f"/p/2026-06-02_{FILENAME_STEM}.md"
    assert "TASK-" not in first  # no TASK-ID in filename

    taken.add(first)
    second = resolve_checkpoint_path("/p", "2026-06-02", lambda p: p in taken)
    assert second == f"/p/2026-06-02_{FILENAME_STEM}_01.md"
