#!/usr/bin/env python3
"""Lint external-interface boundary contracts (REQ-PROC-044 AC-08).

Checks, across every `.claude/contracts/external/*.yaml`:
  1. kind: external-interface and interface: E<n> present.
  2. contract_version: 1 declared.
  3. input_modality: (when present) is a valid enum value; absent defaults to 'file'.
  4. every quality_criteria[*].check resolves to scripts/factory/external_state/check_<term>.py.
  5. every schema: reference points to an existing file under .claude/schemas/.

Output: human-readable lines on stdout. `PASS — ...` (exit 0) or `FAIL — N violation(s)`
        (exit 1). Consumed by verify-quality per-change gate (§3.3c).
"""

# tier: B

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

CONTRACT_VERSION_REQUIRED = 1
KIND_REQUIRED = "external-interface"
INTERFACE_PATTERN = re.compile(r"^E[0-9]+$")

VALID_INPUT_MODALITIES = frozenset(
    {"file", "frontmatter", "conversation", "invocation_arg", "command_output", "url_response"}
)

EXTERNAL_STATE_DIR = Path("scripts/factory/external_state")


def _label(contract_path: Path) -> str:
    """Return a short label for violation messages (e.g. 'E1_developer_question_response.yaml')."""
    return contract_path.name


def _items(block: dict[str, Any], *sections: str) -> list[dict[str, Any]]:
    """Flatten the dict items of the named sub-sections of a derived_from/produces block."""
    out: list[dict[str, Any]] = []
    for section in sections:
        for item in (block or {}).get(section, []) or []:
            if isinstance(item, dict):
                out.append(item)
    return out


def load_contracts(contracts_dir: Path) -> list[tuple[Path, dict[str, Any]]]:
    """Load every *.yaml from contracts_dir; return list of (path, data) pairs."""
    result: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(contracts_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        result.append((path, data))
    return result


def check_kind_and_interface(
    path: Path, data: dict[str, Any], violations: list[str]
) -> None:
    """Rule 1: kind must be 'external-interface'; interface must match E[0-9]+."""
    label = _label(path)
    kind = data.get("kind")
    if kind != KIND_REQUIRED:
        violations.append(
            f"{label}: 'kind' is {kind!r}; expected 'external-interface'."
        )
    interface = data.get("interface")
    if not interface:
        violations.append(
            f"{label}: 'interface' field is missing. Must match pattern E[0-9]+ (e.g. E1)."
        )
    elif not INTERFACE_PATTERN.match(str(interface)):
        violations.append(
            f"{label}: 'interface' value {interface!r} does not match pattern E[0-9]+."
        )


def check_contract_version(
    path: Path, data: dict[str, Any], violations: list[str]
) -> None:
    """Rule 2: contract_version must equal CONTRACT_VERSION_REQUIRED."""
    label = _label(path)
    version = data.get("contract_version")
    if version != CONTRACT_VERSION_REQUIRED:
        violations.append(
            f"{label}: 'contract_version' is {version!r}; only"
            f" contract_version: {CONTRACT_VERSION_REQUIRED} is valid."
        )


def check_input_modalities(
    path: Path, data: dict[str, Any], violations: list[str]
) -> None:
    """Rule 3: input_modality, when present, must be a valid enum value.

    Absent input_modality defaults to 'file' — not a violation.
    """
    label = _label(path)
    for block_name in ("derived_from", "produces"):
        block = data.get(block_name) or {}
        for item in _items(block, "required", "optional", "conditional"):
            modality = item.get("input_modality")
            if modality is not None and modality not in VALID_INPUT_MODALITIES:
                violations.append(
                    f"{label}: {block_name} item path={item.get('path', '?')!r}"
                    f" has invalid input_modality {modality!r}."
                    f" Valid values: {', '.join(sorted(VALID_INPUT_MODALITIES))}."
                )


def check_quality_criteria(
    path: Path, data: dict[str, Any], external_state_dir: Path, violations: list[str]
) -> None:
    """Rule 4: each quality_criteria item's check: term must resolve to a script."""
    label = _label(path)
    for item in data.get("quality_criteria") or []:
        if not isinstance(item, dict):
            continue
        check_term = item.get("check")
        if check_term is None:
            continue
        script = external_state_dir / f"check_{check_term}.py"
        if not script.exists():
            violations.append(
                f"{label}: quality_criteria check={check_term!r} resolves to"
                f" '{script}' which does not exist."
            )


def check_schema_refs(
    path: Path, data: dict[str, Any], repo_root: Path, violations: list[str]
) -> None:
    """Rule 5: every non-null schema: reference must point to an existing file."""
    label = _label(path)
    items: list[dict[str, Any]] = []
    for block_name in ("derived_from", "produces"):
        block = data.get(block_name) or {}
        items.extend(_items(block, "required", "optional", "conditional"))
    for item in items:
        schema = item.get("schema")
        if schema and not (repo_root / schema).exists():
            violations.append(
                f"{label}: references schema '{schema}' which does not exist."
            )


def run_checks(
    contracts_dir: Path, repo_root: Path
) -> tuple[list[str], int]:
    """Run all checks; return (violations, contracts-checked count)."""
    contracts = load_contracts(contracts_dir)
    violations: list[str] = []
    external_state_dir = repo_root / EXTERNAL_STATE_DIR

    for path, data in contracts:
        check_kind_and_interface(path, data, violations)
        check_contract_version(path, data, violations)
        check_input_modalities(path, data, violations)
        check_quality_criteria(path, data, external_state_dir, violations)
        check_schema_refs(path, data, repo_root, violations)

    return violations, len(contracts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        default=Path(".claude/contracts/external"),
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    if not args.contracts_dir.exists():
        print(f"No contracts directory found at {args.contracts_dir}")
        return 0

    violations, checked = run_checks(args.contracts_dir, args.repo_root)

    if checked == 0:
        print(f"No contract YAML files found under {args.contracts_dir}")
        return 0

    if violations:
        print(f"FAIL — {len(violations)} violation(s):")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    print(f"PASS — {checked} contract(s) checked, 0 violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
