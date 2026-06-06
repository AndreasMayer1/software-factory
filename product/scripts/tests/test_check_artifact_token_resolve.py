#!/usr/bin/env python3
"""Tests for scripts/quality/check_artifact_token_resolve.py (REQ-PROC-044-02 AC-02, AC-03).

Strategy: build synthetic registry / skill / agent file trees under tmp_path and call
run_checks / load_baseline / _expertise_segment directly. All I/O goes through tmp_path —
no dependency on the live repository files.
"""

# tier: B

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("yaml", reason="PyYAML not installed in test environment")
import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs

sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
import check_artifact_token_resolve as catr  # type: ignore[import-not-found]  # runtime path; mypy cannot follow sys.path manipulation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_registry(registry_dir: Path, tokens: dict[str, Any]) -> Path:
    """Write artifacts.yaml with the given tokens and return its path."""
    registry_dir.mkdir(parents=True, exist_ok=True)
    path = registry_dir / "artifacts.yaml"
    lines = []
    for token, meta in tokens.items():
        lines.append(f"{token}:")
        lines.append(f"  path: {meta['path']}")
        lines.append(f"  definition: {meta['definition']}")
    path.write_text("\n".join(lines) + "\n")
    return path


def _make_skill_contract(skills_root: Path, skill_name: str, data: dict[str, Any]) -> Path:
    skill_dir = skills_root / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    path = skill_dir / "contract.yaml"
    path.write_text(yaml.safe_dump(data))
    return path


def _make_agent_contract(agents_root: Path, agent_name: str, data: dict[str, Any]) -> Path:
    agents_root.mkdir(parents=True, exist_ok=True)
    path = agents_root / f"{agent_name}.contract.yaml"
    path.write_text(yaml.safe_dump(data))
    return path


def _make_agent_md(agents_root: Path, agent_name: str) -> Path:
    agents_root.mkdir(parents=True, exist_ok=True)
    path = agents_root / f"{agent_name}.md"
    path.write_text(f"# {agent_name}\n")
    return path


_SIMPLE_TOKENS = {
    "goal": {"path": "requirements_tasks/**/tasks/*/goal.md", "definition": "Task goal file"},
    "plan": {"path": "requirements_tasks/**/plans_and_protocols/*plan*.md", "definition": "Plan file"},
    "scribble": {"path": "**/scribbles/v*/", "definition": "HTML wireframe set"},
}


# ---------------------------------------------------------------------------
# _expertise_segment unit tests
# ---------------------------------------------------------------------------


def test_expertise_segment_writer() -> None:
    assert catr._expertise_segment("scribble-writer") == "scribble"


def test_expertise_segment_transformer() -> None:
    assert catr._expertise_segment("goal-transformer") == "goal"


def test_expertise_segment_reviewer() -> None:
    assert catr._expertise_segment("plan-reviewer") == "plan"


def test_expertise_segment_classifier() -> None:
    assert catr._expertise_segment("scribble-classifier") == "scribble"


def test_expertise_segment_unknown_role_returns_none() -> None:
    assert catr._expertise_segment("architecture-advisor") is None


def test_expertise_segment_no_hyphen_returns_none() -> None:
    assert catr._expertise_segment("writer") is None


def test_expertise_segment_multi_part_expertise() -> None:
    assert catr._expertise_segment("ui-scribble-reviewer") == "ui-scribble"


# ---------------------------------------------------------------------------
# load_baseline unit tests
# ---------------------------------------------------------------------------


def test_load_baseline_missing_file_returns_empty(tmp_path: Path) -> None:
    result = catr.load_baseline(tmp_path / "nonexistent.txt")
    assert result == set()


def test_load_baseline_none_returns_empty() -> None:
    assert catr.load_baseline(None) == set()


def test_load_baseline_reads_lines(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.txt"
    baseline.write_text("violation one\n# comment\nviolation two\n  \nviolation three\n")
    result = catr.load_baseline(baseline)
    assert result == {"violation one", "violation two", "violation three"}


def test_load_baseline_ignores_comments(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.txt"
    baseline.write_text("# this is a comment\nreal violation\n")
    result = catr.load_baseline(baseline)
    assert "# this is a comment" not in result
    assert "real violation" in result


# ---------------------------------------------------------------------------
# run_checks — PASS scenarios
# ---------------------------------------------------------------------------


def test_pass_all_token_values(tmp_path: Path) -> None:
    """All contract path values are valid tokens → no violations."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"

    _make_skill_contract(
        skills_root,
        "my-skill",
        {
            "produces": {"required": [{"path": "goal", "reason": "produces goal"}]},
            "derived_from": {"optional": [{"path": "plan", "reason": "reads plan"}]},
        },
    )
    _make_agent_contract(agents_root, "my-agent", {"produces": ["scribble"], "consumes": ["goal"]})
    _make_agent_md(agents_root, "scribble-writer")

    violations, sc, acc, ac = catr.run_checks(registry_path, skills_root, agents_root)

    assert violations == []
    assert sc == 1
    assert acc == 1
    assert ac == 1


def test_pass_empty_contract_fields(tmp_path: Path) -> None:
    """Contracts with empty/missing produces and derived_from pass cleanly."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"

    _make_skill_contract(skills_root, "my-skill", {"contract_version": 1, "produces": {}})
    _make_agent_contract(agents_root, "my-agent", {})
    _make_agent_md(agents_root, "goal-writer")

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)
    assert violations == []


def test_pass_no_contracts_or_agents(tmp_path: Path) -> None:
    """Empty directories produce zero violations and zero counts."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"
    skills_root.mkdir(parents=True, exist_ok=True)
    agents_root.mkdir(parents=True, exist_ok=True)

    violations, sc, acc, ac = catr.run_checks(registry_path, skills_root, agents_root)
    assert violations == []
    assert sc == 0
    assert acc == 0
    assert ac == 0


# ---------------------------------------------------------------------------
# run_checks — FAIL scenarios: skill contract
# ---------------------------------------------------------------------------


def test_fail_skill_contract_unresolved_produces_path(tmp_path: Path) -> None:
    """A skill contract produces path that is not a token → violation."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"
    agents_root.mkdir(parents=True, exist_ok=True)

    _make_skill_contract(
        skills_root,
        "my-skill",
        {"produces": {"required": [{"path": "requirements_tasks/task/plans/plan.md", "reason": "x"}]}},
    )

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)
    assert any("requirements_tasks/task/plans/plan.md" in v for v in violations)


def test_fail_skill_contract_unresolved_derived_from_path(tmp_path: Path) -> None:
    """A skill contract derived_from path that is not a token → violation."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"
    agents_root.mkdir(parents=True, exist_ok=True)

    _make_skill_contract(
        skills_root,
        "my-skill",
        {"derived_from": {"required": [{"path": "doc/some/guideline.md", "source": "external"}]}},
    )

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)
    assert any("doc/some/guideline.md" in v for v in violations)


def test_fail_skill_contract_conditional_path(tmp_path: Path) -> None:
    """A skill contract produces.conditional path that is not a token → violation."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"
    agents_root.mkdir(parents=True, exist_ok=True)

    _make_skill_contract(
        skills_root,
        "my-skill",
        {"produces": {"conditional": [{"path": "some/free-text/path.md", "condition": "when X"}]}},
    )

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)
    assert any("some/free-text/path.md" in v for v in violations)


# ---------------------------------------------------------------------------
# run_checks — FAIL scenarios: agent contract
# ---------------------------------------------------------------------------


def test_fail_agent_contract_unresolved_produces(tmp_path: Path) -> None:
    """An agent contract produces list item that is not a token → violation."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"
    skills_root.mkdir(parents=True, exist_ok=True)

    _make_agent_contract(agents_root, "my-agent", {"produces": ["test/**", "integration_test/**"]})

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)
    assert any("test/**" in v for v in violations)
    assert any("integration_test/**" in v for v in violations)


def test_fail_agent_contract_unresolved_consumes(tmp_path: Path) -> None:
    """An agent contract consumes value that is not a token → violation."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"
    skills_root.mkdir(parents=True, exist_ok=True)

    _make_agent_contract(agents_root, "my-agent", {"consumes": ["lib/**", "doc/**"]})

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)
    assert any("lib/**" in v for v in violations)


# ---------------------------------------------------------------------------
# run_checks — FAIL scenarios: agent name
# ---------------------------------------------------------------------------


def test_fail_agent_name_non_conforming(tmp_path: Path) -> None:
    """An agent whose name does not end with a governed role → non-conforming violation."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"
    skills_root.mkdir(parents=True, exist_ok=True)

    _make_agent_md(agents_root, "architecture-advisor")

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)
    assert any("architecture-advisor" in v and "does not follow" in v for v in violations)


def test_fail_agent_name_expertise_not_a_token(tmp_path: Path) -> None:
    """An agent whose role is governed but expertise is not a token → token violation."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"
    skills_root.mkdir(parents=True, exist_ok=True)

    _make_agent_md(agents_root, "unknown-artifact-writer")

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)
    assert any("unknown-artifact" in v and "does not resolve" in v for v in violations)


def test_pass_agent_name_expertise_is_token(tmp_path: Path) -> None:
    """An agent whose expertise segment is a valid token → no violation."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"
    skills_root.mkdir(parents=True, exist_ok=True)

    _make_agent_md(agents_root, "scribble-reviewer")

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)
    assert violations == []


# ---------------------------------------------------------------------------
# run_checks — registry duplicate detection
# ---------------------------------------------------------------------------


def test_fail_duplicate_registry_token(tmp_path: Path) -> None:
    """A registry with a duplicate token → violation recorded."""
    registry_dir = tmp_path / ".factory/registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry_path = registry_dir / "artifacts.yaml"
    # Write raw YAML with duplicate key (yaml.safe_dump would silently merge them)
    registry_path.write_text(
        "goal:\n  path: a.md\n  definition: First\n"
        "goal:\n  path: b.md\n  definition: Second\n"
    )

    skills_root = tmp_path / ".claude/skills"
    agents_root = tmp_path / ".claude/agents"
    skills_root.mkdir(parents=True, exist_ok=True)
    agents_root.mkdir(parents=True, exist_ok=True)

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)
    assert any("goal" in v and ("duplicate" in v.lower() or "Duplicate" in v) for v in violations)


# ---------------------------------------------------------------------------
# Baseline suppression integration
# ---------------------------------------------------------------------------


def test_baseline_suppresses_known_violations(tmp_path: Path) -> None:
    """Violations listed in the baseline do not appear in unbaselined output."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    agents_root = tmp_path / ".claude/agents"
    skills_root = tmp_path / ".claude/skills"
    skills_root.mkdir(parents=True, exist_ok=True)

    _make_agent_md(agents_root, "architecture-advisor")

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)
    assert len(violations) >= 1

    # Put the violation in the baseline
    baseline_path = tmp_path / "baseline.txt"
    baseline_path.write_text("\n".join(violations))
    baseline = catr.load_baseline(baseline_path)

    unbaselined = [v for v in violations if v not in baseline]
    assert unbaselined == []


def test_baseline_does_not_suppress_new_violations(tmp_path: Path) -> None:
    """A violation not in the baseline is still reported."""
    registry_path = _make_registry(tmp_path / ".factory/registry", _SIMPLE_TOKENS)
    agents_root = tmp_path / ".claude/agents"
    skills_root = tmp_path / ".claude/skills"
    skills_root.mkdir(parents=True, exist_ok=True)

    _make_agent_md(agents_root, "architecture-advisor")
    _make_agent_md(agents_root, "quality-checker")

    violations, _, _, _ = catr.run_checks(registry_path, skills_root, agents_root)

    baseline_path = tmp_path / "baseline.txt"
    # Only baseline the first violation
    baseline_path.write_text(violations[0])
    baseline = catr.load_baseline(baseline_path)

    unbaselined = [v for v in violations if v not in baseline]
    assert len(unbaselined) >= 1
