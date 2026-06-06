"""Tests for scripts/factory/render_user_input_gates.py."""

# tier: B  # tests for a Tier B generator

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("yaml", reason="PyYAML not installed in test environment")
import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs

sys.path.insert(0, str(Path(__file__).parent.parent / "factory"))
import render_user_input_gates as rug  # type: ignore[import-not-found]  # runtime path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _valid_gate(**overrides: str) -> dict[str, Any]:
    base: dict[str, Any] = {
        "phase": "Step 1 — Review",
        "description": "Developer approves the output.",
        "decision_kind": "approval",
        "required": "always",
    }
    base.update(overrides)
    return base


def _contract_with_gates(gates: list[dict[str, Any]]) -> dict[str, Any]:
    return {"contract_version": 1, "user_input_gates": gates}


def _make_skill_contract(tmp_path: Path, name: str, data: dict[str, Any]) -> tuple[str, Path, dict[str, Any]]:
    contract_path = tmp_path / name / "contract.yaml"
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(yaml.safe_dump(data))
    return (name, contract_path, data)


# ---------------------------------------------------------------------------
# validate_gate_entry
# ---------------------------------------------------------------------------


class TestValidateGateEntry:
    def test_valid_entry_returns_true(self) -> None:
        violations: list[str] = []
        result = rug.validate_gate_entry("skill/test[0]", _valid_gate(), violations)
        assert result is True
        assert violations == []

    def test_missing_phase_produces_violation(self) -> None:
        gate = _valid_gate()
        del gate["phase"]
        violations: list[str] = []
        result = rug.validate_gate_entry("skill/test[0]", gate, violations)
        assert result is False
        assert any("phase" in v for v in violations)

    def test_missing_description_produces_violation(self) -> None:
        gate = _valid_gate()
        del gate["description"]
        violations: list[str] = []
        rug.validate_gate_entry("skill/test[0]", gate, violations)
        assert any("description" in v for v in violations)

    def test_missing_decision_kind_produces_violation(self) -> None:
        gate = _valid_gate()
        del gate["decision_kind"]
        violations: list[str] = []
        rug.validate_gate_entry("skill/test[0]", gate, violations)
        assert any("decision_kind" in v for v in violations)

    def test_missing_required_field_produces_violation(self) -> None:
        gate = _valid_gate()
        del gate["required"]
        violations: list[str] = []
        rug.validate_gate_entry("skill/test[0]", gate, violations)
        assert any("'required'" in v for v in violations)

    def test_invalid_decision_kind_produces_violation(self) -> None:
        violations: list[str] = []
        rug.validate_gate_entry("skill/test[0]", _valid_gate(decision_kind="bogus"), violations)
        assert any("decision_kind" in v and "bogus" in v for v in violations)

    def test_invalid_required_value_produces_violation(self) -> None:
        violations: list[str] = []
        rug.validate_gate_entry("skill/test[0]", _valid_gate(required="sometimes"), violations)
        assert any("required value" in v and "sometimes" in v for v in violations)

    @pytest.mark.parametrize("kind", ["approval", "revision", "selection", "path-selection", "free-text"])
    def test_all_valid_decision_kinds_accepted(self, kind: str) -> None:
        violations: list[str] = []
        rug.validate_gate_entry("skill/test[0]", _valid_gate(decision_kind=kind), violations)
        assert violations == []

    @pytest.mark.parametrize("req", ["always", "conditional"])
    def test_all_valid_required_values_accepted(self, req: str) -> None:
        violations: list[str] = []
        rug.validate_gate_entry("skill/test[0]", _valid_gate(required=req), violations)
        assert violations == []


# ---------------------------------------------------------------------------
# collect_gates
# ---------------------------------------------------------------------------


class TestCollectGates:
    def test_no_user_input_gates_field_skipped(self, tmp_path: Path) -> None:
        contracts = [_make_skill_contract(tmp_path, "my-skill", {"contract_version": 1})]
        violations: list[str] = []
        rows = rug.collect_gates(contracts, ".claude/skills", violations)
        assert rows == []
        assert violations == []

    def test_valid_gate_produces_row(self, tmp_path: Path) -> None:
        data = _contract_with_gates([_valid_gate()])
        contracts = [_make_skill_contract(tmp_path, "my-skill", data)]
        violations: list[str] = []
        rows = rug.collect_gates(contracts, ".claude/skills", violations)
        assert len(rows) == 1
        assert rows[0]["source"] == "my-skill"
        assert rows[0]["decision_kind"] == "approval"
        assert violations == []

    def test_non_list_gates_produces_violation(self, tmp_path: Path) -> None:
        data = {"contract_version": 1, "user_input_gates": "not-a-list"}
        contracts = [_make_skill_contract(tmp_path, "bad-skill", data)]
        violations: list[str] = []
        rug.collect_gates(contracts, ".claude/skills", violations)
        assert any("must be a list" in v for v in violations)

    def test_non_dict_entry_produces_violation(self, tmp_path: Path) -> None:
        data = {"contract_version": 1, "user_input_gates": ["not-a-dict"]}
        contracts = [_make_skill_contract(tmp_path, "bad-skill", data)]
        violations: list[str] = []
        rug.collect_gates(contracts, ".claude/skills", violations)
        assert any("must be a dict" in v for v in violations)

    def test_malformed_entry_produces_violation_and_still_adds_row(self, tmp_path: Path) -> None:
        gate = _valid_gate()
        del gate["phase"]
        data = _contract_with_gates([gate])
        contracts = [_make_skill_contract(tmp_path, "my-skill", data)]
        violations: list[str] = []
        rows = rug.collect_gates(contracts, ".claude/skills", violations)
        assert len(rows) == 1
        assert any("phase" in v for v in violations)

    def test_multiple_skills_aggregated(self, tmp_path: Path) -> None:
        c1 = _make_skill_contract(tmp_path, "skill-a", _contract_with_gates([_valid_gate()]))
        c2 = _make_skill_contract(tmp_path, "skill-b", _contract_with_gates([_valid_gate(), _valid_gate()]))
        violations: list[str] = []
        rows = rug.collect_gates([c1, c2], ".claude/skills", violations)
        assert len(rows) == 3
        assert violations == []


# ---------------------------------------------------------------------------
# render_markdown
# ---------------------------------------------------------------------------


class TestRenderMarkdown:
    def test_empty_rows_produces_no_table_message(self) -> None:
        md = rug.render_markdown([], n_skills=5, n_agents=2)
        assert "No `user_input_gates:`" in md
        assert "|" not in md

    def test_rows_produce_table(self) -> None:
        rows = [
            {
                "source": "my-skill",
                "phase": "Step 1",
                "description": "Developer decides.",
                "decision_kind": "approval",
                "required": "always",
            }
        ]
        md = rug.render_markdown(rows, n_skills=1, n_agents=0)
        assert "| my-skill |" in md
        assert "| Step 1 |" in md
        assert "| approval |" in md
        assert "Total: 1 gate(s)" in md

    def test_pipe_characters_escaped(self) -> None:
        rows = [
            {
                "source": "skill|name",
                "phase": "Step 1",
                "description": "Desc.",
                "decision_kind": "approval",
                "required": "always",
            }
        ]
        md = rug.render_markdown(rows, n_skills=1, n_agents=0)
        assert "skill\\|name" in md

    def test_coverage_counts_in_header(self) -> None:
        md = rug.render_markdown([], n_skills=7, n_agents=3)
        assert "7 skill contract(s)" in md
        assert "3 agent contract(s)" in md


# ---------------------------------------------------------------------------
# collect_skill_contracts / collect_agent_contracts
# ---------------------------------------------------------------------------


class TestCollectContracts:
    def test_missing_skills_dir_returns_empty(self, tmp_path: Path) -> None:
        result = rug.collect_skill_contracts(tmp_path / "nonexistent")
        assert result == []

    def test_missing_agents_dir_returns_empty(self, tmp_path: Path) -> None:
        result = rug.collect_agent_contracts(tmp_path / "nonexistent")
        assert result == []

    def test_skill_contract_loaded(self, tmp_path: Path) -> None:
        skills_root = tmp_path / ".claude" / "skills"
        skill_dir = skills_root / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "contract.yaml").write_text("contract_version: 1\n")
        results = rug.collect_skill_contracts(tmp_path)
        assert len(results) == 1
        name, _path, data = results[0]
        assert name == "my-skill"
        assert data["contract_version"] == 1

    def test_agent_contract_loaded(self, tmp_path: Path) -> None:
        agents_root = tmp_path / ".claude" / "agents"
        agents_root.mkdir(parents=True)
        (agents_root / "my-agent.contract.yaml").write_text("contract_version: 1\n")
        results = rug.collect_agent_contracts(tmp_path)
        assert len(results) == 1
        name, _path, data = results[0]
        assert name == "my-agent"
        assert data["contract_version"] == 1
