#!/usr/bin/env python3
"""Tests for scripts/optimize/create_optimize_task.py (REQ-PROC-006 IMPL-D).

Covers the two non-removable invariants:

* G-INV-1 (AC-04) — every produced goal.md carries
  ``awaiting: ["user-unblock"]`` across every flag combination.
* Write-Surface Deny-List (AC-10 / SEC-04) — every SEC-04 path is rejected;
  glob patterns reject nested files.

Plus shape / round-trip checks on the optimization_approach block and the
``source_event`` projection from a monitor event file.
"""

import itertools
import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Import from sibling scripts/optimize/ and scripts/util/ via path injection,
# mirroring the existing monitor tests (test_monitor_common.py etc.).
_TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_TESTS_DIR.parent / "optimize"))
sys.path.insert(0, str(_TESTS_DIR.parent))

import create_optimize_task as cot  # type: ignore[import-not-found]  # noqa: E402, I001 -- sys.path mutated above; isort cannot follow runtime path inserts
from util.yaml_frontmatter import read_frontmatter  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above

# A target that is NOT on the deny-list — used in every positive-path test.
SAFE_TARGET = ".claude/skills/requ-explore/skill.md"


def _parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse a produced goal.md text and return its frontmatter as a dict.

    Routes through the canonical scripts/util/yaml_frontmatter.read_frontmatter
    so future format-preserving changes there flow into these tests.
    """
    doc = read_frontmatter(text)
    return dict(doc.metadata)


def _base_argv(task_dir: Path, **overrides: str) -> list[str]:
    """Build a minimal valid argv; overrides win."""
    args = {
        "--task-dir": str(task_dir),
        "--task-id": "TASK-PROC-006-XX",
        "--target-path": SAFE_TARGET,
        "--optimization-target": "skill_body",
        "--optimization-dimension": "bugfix",
    }
    args.update(overrides)
    argv: list[str] = []
    for k, v in args.items():
        argv.extend([k, v])
    return argv


# --- G-INV-1: awaiting: ["user-unblock"] for every flag combination ---


@pytest.mark.parametrize(
    ("target", "dimension", "research"),
    list(
        itertools.product(
            cot.OPTIMIZATION_TARGETS,
            ("bugfix", "trigger_accuracy", "clarity"),
            (True, False),
        )
    ),
)
def test_g_inv_1_awaiting_user_unblock_for_every_combo(
    tmp_path: Path, target: str, dimension: str, research: bool
) -> None:
    argv = _base_argv(
        tmp_path,
        **{"--optimization-target": target, "--optimization-dimension": dimension},
    )
    if research:
        argv = [*argv, "--web-research", "--web-research-query", "is there prior art?"]
    rc = cot.main(argv)
    assert rc == 0
    fm = _parse_frontmatter((tmp_path / "goal.md").read_text())
    assert list(fm["awaiting"]) == ["user-unblock"]


def test_no_code_path_can_omit_awaiting(tmp_path: Path) -> None:
    """Even with --no-web-research and minimal args the line is present."""
    rc = cot.main([*_base_argv(tmp_path), "--no-web-research"])
    assert rc == 0
    text = (tmp_path / "goal.md").read_text()
    assert 'awaiting: ["user-unblock"]' in text


# --- Deny-list: every SEC-04 entry rejects; glob covers nested files ---


@pytest.mark.parametrize(
    "denied_path",
    [
        ".claude/skills/claude-optimize/SKILL.md",
        ".claude/skills/verify-quality/SKILL.md",
        ".claude/skills/task-complete/SKILL.md",
        ".claude/skills/claude-modify-skill/SKILL.md",
        "scripts/quality/check_python_gates.sh",
        "analysis_options.yaml",
        ".claude/factory_flows.md",
        ".claude/skills/INDEX.md",
    ],
)
def test_deny_list_rejects_sec04_path(
    tmp_path: Path, denied_path: str, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = cot.main(_base_argv(tmp_path, **{"--target-path": denied_path}))
    assert rc == cot.EXIT_DENYLIST
    err = capsys.readouterr().err
    assert "deny-list" in err
    assert denied_path in err
    assert not (tmp_path / "goal.md").exists()


def test_deny_list_glob_matches_nested_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = cot.main(
        _base_argv(tmp_path, **{"--target-path": "scripts/quality/sub/dir/check.py"})
    )
    assert rc == cot.EXIT_DENYLIST
    assert "scripts/quality/**" in capsys.readouterr().err


def test_match_deny_list_returns_pattern() -> None:
    assert cot.match_deny_list("scripts/quality/check_x.py") == "scripts/quality/**"
    assert cot.match_deny_list(".claude/factory_flows.md") == ".claude/factory_flows.md"
    assert cot.match_deny_list(SAFE_TARGET) is None


def test_match_deny_list_is_case_insensitive() -> None:
    # F-2 regression: the real on-disk path is SKILL.md; a case variant in an
    # event payload must not bypass the deny-list. Both casings match the same
    # original-cased pattern.
    expected = ".claude/skills/claude-optimize/SKILL.md"
    assert cot.match_deny_list(".claude/skills/claude-optimize/SKILL.md") == expected
    assert cot.match_deny_list(".claude/skills/claude-optimize/skill.md") == expected
    assert cot.match_deny_list("SCRIPTS/QUALITY/check_x.py") == "scripts/quality/**"


# --- Normal target produces a valid goal.md ---


def test_normal_target_produces_valid_goal_md(tmp_path: Path) -> None:
    rc = cot.main(_base_argv(tmp_path))
    assert rc == 0
    fm = _parse_frontmatter((tmp_path / "goal.md").read_text())
    assert fm["task_id"] == "TASK-PROC-006-XX"
    assert fm["type"] == "impl"
    assert fm["parent_requirement"] == "REQ-PROC-006"
    assert fm["status"] == "pending"
    assert fm["target_path"] == SAFE_TARGET
    assert fm["optimization_target"] == "skill_body"
    assert fm["optimization_dimension"] == "bugfix"
    assert "optimization_approach" in fm


def test_optimization_approach_with_web_research(tmp_path: Path) -> None:
    argv = [
        *_base_argv(tmp_path),
        "--web-research",
        "--web-research-query",
        "what is the standard skill-description pattern?",
        "--web-research-reason",
        "Anthropic publishes guidance on skill descriptions",
    ]
    rc = cot.main(argv)
    assert rc == 0
    fm = _parse_frontmatter((tmp_path / "goal.md").read_text())
    approach = fm["optimization_approach"]
    assert approach["web_research_recommended"] is True
    assert approach["web_research_query"].startswith("what is")
    assert "Anthropic" in approach["reason"]


def test_optimization_approach_without_web_research_omits_query(tmp_path: Path) -> None:
    argv = [
        *_base_argv(tmp_path),
        "--no-web-research",
        "--web-research-reason",
        "answer is in the repo",
    ]
    rc = cot.main(argv)
    assert rc == 0
    fm = _parse_frontmatter((tmp_path / "goal.md").read_text())
    approach = fm["optimization_approach"]
    assert approach["web_research_recommended"] is False
    assert "web_research_query" not in approach
    assert approach["reason"] == "answer is in the repo"


def test_web_research_requires_query(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = cot.main([*_base_argv(tmp_path), "--web-research"])
    assert rc == cot.EXIT_INVALID
    assert "web-research-query" in capsys.readouterr().err
    assert not (tmp_path / "goal.md").exists()


# --- Source event projection from a monitor event file ---


def test_source_event_fields_populated_from_event_file(tmp_path: Path) -> None:
    event_path = tmp_path / "event.json"
    event_path.write_text(
        json.dumps(
            {
                "event_type": "skill_change_reverted",
                "confidence": "high",
                "fingerprint": "abc123def456",
                "created": "2026-05-28T12:00:00Z",
                "payload": {"skill": "requ-explore"},
            }
        )
    )
    out_dir = tmp_path / "out"
    argv = [
        *_base_argv(out_dir, **{"--task-id": "TASK-PROC-006-YY"}),
        "--event",
        str(event_path),
    ]
    rc = cot.main(argv)
    assert rc == 0
    fm = _parse_frontmatter((out_dir / "goal.md").read_text())
    assert fm["source_event"]["event_type"] == "skill_change_reverted"
    assert fm["source_event"]["fingerprint"] == "abc123def456"
    assert fm["source_event"]["confidence"] == "high"


def test_missing_event_file_returns_invalid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    argv = [*_base_argv(tmp_path), "--event", str(tmp_path / "missing.json")]
    rc = cot.main(argv)
    assert rc == cot.EXIT_INVALID
    assert "invalid input" in capsys.readouterr().err


def test_malformed_event_file_returns_invalid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("not valid json {")
    rc = cot.main([*_base_argv(tmp_path), "--event", str(bad)])
    assert rc == cot.EXIT_INVALID
    assert "invalid input" in capsys.readouterr().err


def test_event_file_missing_fields_returns_invalid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "partial.json"
    bad.write_text(json.dumps({"event_type": "periodic"}))
    rc = cot.main([*_base_argv(tmp_path), "--event", str(bad)])
    assert rc == cot.EXIT_INVALID
    assert "missing fields" in capsys.readouterr().err


# --- Argparse-level validation ---


def test_invalid_optimization_target_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        cot.main(_base_argv(tmp_path, **{"--optimization-target": "nonsense"}))


def test_invalid_optimization_dimension_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        cot.main(_base_argv(tmp_path, **{"--optimization-dimension": "nonsense"}))
