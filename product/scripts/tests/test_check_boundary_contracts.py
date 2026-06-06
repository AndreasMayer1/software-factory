#!/usr/bin/env python3
"""Tests for scripts/quality/check_boundary_contracts.py (REQ-PROC-044 AC-08).

Strategy: build synthetic .claude/contracts/external/*.yaml trees under tmp_path and
call run_checks directly. This exercises the kind/interface, contract_version,
input_modality, quality_criteria check→script resolution, and schema-ref logic
without depending on the real repository contracts.
"""

# tier: B

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("yaml", reason="PyYAML not installed in test environment")
import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
import check_boundary_contracts as cbc  # type: ignore[import-not-found]  # runtime path; mypy cannot follow sys.path manipulation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_contract(contracts_dir: Path, name: str, contract: dict[str, object]) -> Path:
    """Write a contract YAML file into contracts_dir and return its path."""
    contracts_dir.mkdir(parents=True, exist_ok=True)
    path = contracts_dir / name
    path.write_text(yaml.safe_dump(contract))
    return path


def _make_external_state_dir(repo_root: Path, terms: list[str]) -> Path:
    """Create a mock external_state dir with stub check_<term>.py files."""
    es_dir = repo_root / "scripts" / "factory" / "external_state"
    es_dir.mkdir(parents=True, exist_ok=True)
    for term in terms:
        (es_dir / f"check_{term}.py").write_text(f"# stub for {term}\n")
    return es_dir


def _minimal_valid(check_term: str | None = None) -> dict[str, object]:
    """Return the smallest valid external-interface contract."""
    criteria: list[object] = []
    if check_term is not None:
        criteria = [{"check": check_term, "target": "some/path"}]
    return {
        "contract_version": 1,
        "kind": "external-interface",
        "interface": "E1",
        "title": "Test interface",
        "direction": "dev -> factory",
        "purpose": "Test purpose.",
        "quality_criteria": criteria,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_valid_contract_passes(tmp_path: Path) -> None:
    """A minimal valid contract with a known check term must produce zero violations."""
    contracts_dir = tmp_path / ".claude" / "contracts" / "external"
    _make_external_state_dir(tmp_path, ["developer_responded"])
    _write_contract(contracts_dir, "E1_test.yaml", _minimal_valid("developer_responded"))

    violations, checked = cbc.run_checks(contracts_dir, tmp_path)

    assert checked == 1
    assert violations == []


def test_unknown_check_term_fails(tmp_path: Path) -> None:
    """A quality_criteria item with an unknown check term must produce a violation."""
    contracts_dir = tmp_path / ".claude" / "contracts" / "external"
    # Create the external_state dir but NOT a script for the unknown term.
    _make_external_state_dir(tmp_path, ["developer_responded"])
    _write_contract(contracts_dir, "E1_test.yaml", _minimal_valid("nonexistent_term"))

    violations, _ = cbc.run_checks(contracts_dir, tmp_path)

    assert any("nonexistent_term" in v for v in violations)


def test_missing_input_modality_defaults_to_file(tmp_path: Path) -> None:
    """An item without input_modality must not produce a violation (defaults to 'file')."""
    contracts_dir = tmp_path / ".claude" / "contracts" / "external"
    _make_external_state_dir(tmp_path, [])
    contract = _minimal_valid()
    contract["derived_from"] = {
        "required": [{"path": "some/path.md", "source": "external"}]
        # Note: no input_modality field — must be accepted as default 'file'
    }
    _write_contract(contracts_dir, "E1_test.yaml", contract)

    violations, _ = cbc.run_checks(contracts_dir, tmp_path)

    assert violations == []


def test_invalid_input_modality_fails(tmp_path: Path) -> None:
    """An item with an unrecognised input_modality value must produce a violation."""
    contracts_dir = tmp_path / ".claude" / "contracts" / "external"
    _make_external_state_dir(tmp_path, [])
    contract = _minimal_valid()
    contract["derived_from"] = {
        "required": [{"path": "some/path.md", "source": "external", "input_modality": "fax"}]
    }
    _write_contract(contracts_dir, "E1_test.yaml", contract)

    violations, _ = cbc.run_checks(contracts_dir, tmp_path)

    assert any("fax" in v and "input_modality" in v for v in violations)


def test_missing_schema_reference_fails(tmp_path: Path) -> None:
    """A schema: reference pointing to a non-existent file must produce a violation."""
    contracts_dir = tmp_path / ".claude" / "contracts" / "external"
    _make_external_state_dir(tmp_path, [])
    contract = _minimal_valid()
    contract["produces"] = {
        "required": [
            {
                "path": "some/output.md",
                "input_modality": "file",
                "schema": ".claude/schemas/nonexistent.yaml",
            }
        ]
    }
    _write_contract(contracts_dir, "E1_test.yaml", contract)

    violations, _ = cbc.run_checks(contracts_dir, tmp_path)

    assert any("nonexistent.yaml" in v and "does not exist" in v for v in violations)


def test_missing_kind_fails(tmp_path: Path) -> None:
    """A contract without a 'kind' field must produce a violation."""
    contracts_dir = tmp_path / ".claude" / "contracts" / "external"
    _make_external_state_dir(tmp_path, [])
    contract = _minimal_valid()
    del contract["kind"]
    _write_contract(contracts_dir, "E1_test.yaml", contract)

    violations, _ = cbc.run_checks(contracts_dir, tmp_path)

    assert any("kind" in v for v in violations)


def test_wrong_contract_version_fails(tmp_path: Path) -> None:
    """A contract with contract_version != 1 must produce a violation."""
    contracts_dir = tmp_path / ".claude" / "contracts" / "external"
    _make_external_state_dir(tmp_path, [])
    contract = _minimal_valid()
    contract["contract_version"] = 0
    _write_contract(contracts_dir, "E1_test.yaml", contract)

    violations, _ = cbc.run_checks(contracts_dir, tmp_path)

    assert any("contract_version" in v for v in violations)


def test_wrong_kind_fails(tmp_path: Path) -> None:
    """A contract with kind != 'external-interface' must produce a violation."""
    contracts_dir = tmp_path / ".claude" / "contracts" / "external"
    _make_external_state_dir(tmp_path, [])
    contract = _minimal_valid()
    contract["kind"] = "skill"
    _write_contract(contracts_dir, "E1_test.yaml", contract)

    violations, _ = cbc.run_checks(contracts_dir, tmp_path)

    assert any("kind" in v and "skill" in v for v in violations)


def test_empty_quality_criteria_passes(tmp_path: Path) -> None:
    """Empty quality_criteria list (governance-only, e.g. E2) must pass without violations."""
    contracts_dir = tmp_path / ".claude" / "contracts" / "external"
    _make_external_state_dir(tmp_path, [])
    contract = _minimal_valid()
    contract["quality_criteria"] = []
    _write_contract(contracts_dir, "E2_product_intake.yaml", contract)

    violations, checked = cbc.run_checks(contracts_dir, tmp_path)

    assert checked == 1
    assert violations == []


def test_check_skill_contracts_ignores_boundary_dir(tmp_path: Path) -> None:
    """check_skill_contracts.py must not ingest boundary contracts from .claude/contracts/external/.

    This test verifies the glob isolation: run_checks from check_skill_contracts targets
    .claude/skills/*/contract.yaml — it must not reach .claude/contracts/external/*.yaml.
    """
    sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
    import check_skill_contracts as csc  # type: ignore[import-not-found]  # runtime path

    # A skills root with a single valid managed skill — no boundary contract files here.
    skills_root = tmp_path / ".claude" / "skills"
    skill_dir = skills_root / "my-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: my-skill\n---\n")
    (skill_dir / "contract.yaml").write_text(
        yaml.safe_dump({"contract_version": 1, "skill": "my-skill"})
    )

    # Also create a boundary contract under .claude/contracts/external/ — must be ignored.
    boundary_dir = tmp_path / ".claude" / "contracts" / "external"
    boundary_dir.mkdir(parents=True)
    (boundary_dir / "E1_test.yaml").write_text(
        yaml.safe_dump(
            {
                "contract_version": 1,
                "kind": "external-interface",
                "interface": "E1",
            }
        )
    )

    violations, _warnings, checked = csc.run_checks(skills_root, tmp_path)

    # Only the one managed skill contract should be counted — not the boundary contract.
    assert checked == 1
    assert violations == []
