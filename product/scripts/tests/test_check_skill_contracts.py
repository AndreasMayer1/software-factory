# tier: B
"""Tests for scripts/quality/check_skill_contracts.py (REQ-PROC-044 Wave 3 sunset).

Strategy: build synthetic .claude/skills/<name>/contract.yaml trees under tmp_path and
call run_checks directly. This exercises the cross-reference, named-producer, may_invoke,
schema-ref, missing-contract, and contract-version logic without depending on the real
repository contracts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("yaml", reason="PyYAML not installed in test environment")
import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
import check_skill_contracts as csc  # type: ignore[import-not-found]  # runtime path; mypy cannot follow sys.path manipulation


def _write_skill(skills_root: Path, name: str, contract: dict[str, object] | None) -> None:
    """Create a skill folder with a SKILL.md and (optionally) a contract.yaml."""
    folder = skills_root / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(f"---\nname: {name}\n---\n")
    if contract is not None:
        (folder / "contract.yaml").write_text(yaml.safe_dump(contract))


def _producer(produces_basename: str) -> dict[str, object]:
    return {
        "contract_version": 1,
        "skill": "producer",
        "produces": {"required": [{"path": f"requirements_tasks/<x>/{produces_basename}"}]},
    }


def _consumer(source: str, path: str, **extra: object) -> dict[str, object]:
    item: dict[str, object] = {"path": path, "source": source}
    item.update(extra)
    return {
        "contract_version": 1,
        "skill": "consumer",
        "derived_from": {"required": [item]},
    }


def test_clean_named_producer_passes(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "producer", _producer("goal.md"))
    _write_skill(skills, "consumer", _consumer("skill:producer", "requirements_tasks/<y>/tasks/<t>/goal.md"))
    violations, _warnings, checked = csc.run_checks(skills, tmp_path)
    assert checked == 2
    assert violations == []


def test_named_producer_mismatch_violation(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "producer", _producer("goal.md"))
    # consumer claims producer makes requirements.md, but producer only makes goal.md
    _write_skill(skills, "consumer", _consumer("skill:producer", "requirements_tasks/<y>/requirements.md"))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("produces no artifact named 'requirements.md'" in v for v in violations)


def test_unmanaged_producer_warns_and_missing_contract_violates(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "ghost", None)  # exists but no contract.yaml
    _write_skill(skills, "consumer", _consumer("skill:ghost", "requirements_tasks/<y>/thing.md"))
    violations, warnings, _checked = csc.run_checks(skills, tmp_path)
    # post-sunset: ghost has no contract → violation; cross-ref still warns
    assert any("ghost" in v and "no contract.yaml" in v for v in violations)
    assert any("unmanaged" in w for w in warnings)


def test_missing_source_unmatched_violation(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "consumer", _consumer("", "requirements_tasks/<y>/mystery.md"))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("no `source:` annotation" in v for v in violations)


def test_external_source_skipped(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "consumer", _consumer("external", "requirements_tasks/<y>/whatever.md"))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert violations == []


def test_may_invoke_missing_skill_violation(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    contract = {"contract_version": 1, "skill": "consumer", "may_invoke": ["does-not-exist"]}
    _write_skill(skills, "consumer", contract)
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("does-not-exist" in v and "may_invoke" in v for v in violations)


def test_missing_schema_ref_violation(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    contract = _consumer("external", "doc/x.md", schema=".claude/schemas/nope.yaml")
    _write_skill(skills, "consumer", contract)
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("nope.yaml" in v and "does not exist" in v for v in violations)


def test_existing_schema_ref_passes(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    (tmp_path / ".claude" / "schemas").mkdir(parents=True)
    (tmp_path / ".claude" / "schemas" / "real.yaml").write_text("schema_version: 1\n")
    contract = _consumer("external", "doc/x.md", schema=".claude/schemas/real.yaml")
    _write_skill(skills, "consumer", contract)
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert violations == []


def test_violation_message_includes_skill_name(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "consumer", _consumer("", "requirements_tasks/<y>/mystery.md"))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    # message must be skill-qualified, not the bare "contract.yaml"
    assert any(v.startswith("consumer/contract.yaml ") for v in violations)


def test_no_contracts_returns_zero(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    skills.mkdir(parents=True)
    violations, _warnings, checked = csc.run_checks(skills, tmp_path)
    assert checked == 0
    assert violations == []


def test_skill_without_contract_is_violation(tmp_path: Path) -> None:
    """Post-sunset: a skill folder with SKILL.md but no contract.yaml is a FAIL."""
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "naked", None)  # SKILL.md present, no contract.yaml
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("naked" in v and "no contract.yaml" in v for v in violations)


def test_contract_version_zero_is_violation(tmp_path: Path) -> None:
    """Post-sunset: contract_version: 0 is an error, not an opt-out."""
    skills = tmp_path / ".claude" / "skills"
    contract = {"contract_version": 0, "skill": "legacy"}
    _write_skill(skills, "legacy", contract)
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("legacy/contract.yaml" in v and "contract_version" in v for v in violations)


def test_contract_version_one_passes(tmp_path: Path) -> None:
    """contract_version: 1 is the only valid post-sunset value."""
    skills = tmp_path / ".claude" / "skills"
    contract = {"contract_version": 1, "skill": "modern"}
    _write_skill(skills, "modern", contract)
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert not any("modern/contract.yaml" in v and "contract_version" in v for v in violations)


# ---------------------------------------------------------------------------
# check_user_input_gates (rule 7)
# ---------------------------------------------------------------------------


def _skill_with_gates(gates: object) -> dict[str, object]:
    return {"contract_version": 1, "skill": "gated", "user_input_gates": gates}


def _valid_gate() -> dict[str, object]:
    return {
        "phase": "Step 6.5 — Approval",
        "description": "Developer approves the output.",
        "decision_kind": "approval",
        "required": "always",
    }


def test_valid_user_input_gate_passes(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "gated", _skill_with_gates([_valid_gate()]))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert not any("user_input_gates" in v for v in violations)


def test_no_user_input_gates_key_is_ignored(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "plain", {"contract_version": 1, "skill": "plain"})
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert not any("user_input_gates" in v for v in violations)


def test_user_input_gates_not_a_list_violation(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "gated", _skill_with_gates("not-a-list"))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("user_input_gates must be a list" in v for v in violations)


def test_user_input_gate_missing_phase_violation(tmp_path: Path) -> None:
    gate = dict(_valid_gate())
    del gate["phase"]
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "gated", _skill_with_gates([gate]))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("missing required field 'phase'" in v for v in violations)


def test_user_input_gate_missing_description_violation(tmp_path: Path) -> None:
    gate = dict(_valid_gate())
    del gate["description"]
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "gated", _skill_with_gates([gate]))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("missing required field 'description'" in v for v in violations)


def test_user_input_gate_invalid_decision_kind_violation(tmp_path: Path) -> None:
    gate = {**_valid_gate(), "decision_kind": "bogus"}
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "gated", _skill_with_gates([gate]))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("invalid decision_kind 'bogus'" in v for v in violations)


def test_user_input_gate_invalid_required_value_violation(tmp_path: Path) -> None:
    gate = {**_valid_gate(), "required": "sometimes"}
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "gated", _skill_with_gates([gate]))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("invalid required value 'sometimes'" in v for v in violations)


def test_user_input_gate_all_decision_kinds_accepted(tmp_path: Path) -> None:
    for kind in ("approval", "revision", "selection", "path-selection", "free-text"):
        gate = {**_valid_gate(), "decision_kind": kind}
        skills = tmp_path / ".claude" / "skills"
        _write_skill(skills, f"gated-{kind}", _skill_with_gates([gate]))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert not any("invalid decision_kind" in v for v in violations)


def test_user_input_gate_entry_not_dict_violation(tmp_path: Path) -> None:
    skills = tmp_path / ".claude" / "skills"
    _write_skill(skills, "gated", _skill_with_gates(["not-a-dict"]))
    violations, _warnings, _checked = csc.run_checks(skills, tmp_path)
    assert any("must be a dict" in v for v in violations)
