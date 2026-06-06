#!/usr/bin/env python3
"""Lint skill interface contracts (REQ-PROC-044 Wave 3 — sunset enforced 2026-07-29).

Checks, across every `.claude/skills/*/contract.yaml`:
  1. derived_from vs produces cross-reference (an unannotated input path must be a known
     external source or be declared by some skill's produces block).
  2. named-producer verification — an input marked `source: skill:<name>` must resolve to a
     managed producer that actually declares a matching artifact (by basename, robust to the
     freeform path placeholders documented as a v1 risk in REQ-PROC-044 D-2).
  3. may_invoke targets exist as a skill folder containing SKILL.md / skill.md.
  4. every `schema:` reference points to an existing file under .claude/schemas/.
  5. every skill folder with a SKILL.md has a contract.yaml (post-sunset: missing → FAIL).
  6. every contract.yaml declares `contract_version: 1` (post-sunset: version 0 → FAIL).
  7. every `user_input_gates:` entry conforms to .claude/schemas/user_input_gate.yaml —
     malformed entry (missing field or out-of-vocabulary value) is a FAIL at the same
     severity as an unresolved produces: token.

Output: human-readable lines on stdout. `PASS — ...` (exit 0) or `FAIL — N violation(s)`
        (exit 1), each violation on its own `  - ` line. WARNINGS are advisory and never
        change the exit code. Consumed by developers and the verify-quality gate.
"""

# tier: B  # validator; non-trivial cross-reference logic, run as a quality gate

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

CONTRACT_VERSION_REQUIRED = 1  # sunset 2026-07-29: contract_version: 0 opt-out removed (REQ-PROC-044 Wave 3)

# Path prefixes owned by the developer / filesystem / scripts — no producing skill expected.
# Used only as a fallback for derived_from items that omit an explicit `source:`.
EXTERNAL_PREFIXES: tuple[str, ...] = (
    "doc/",
    "requirements_user_needs/",
    "requirements_market_research/",
    "lib/",
    "test/",
    "integration_test/",
    ".claude/schemas/",
    "requirements_tasks/_meta/",
    "requirements_tasks/RELEASE_BACKLOG.md",
)

SKILL_SOURCE_PREFIX = "skill:"
SKILL_DOC_NAMES = ("SKILL.md", "skill.md")


def _norm(path: str) -> str:
    """Normalize a contract path for comparison (strip trailing slash, unify iteration tags)."""
    return path.rstrip("/").replace("iteration_{n}", "v{n}")


def _basename(path: str) -> str:
    """Last path segment — used for named-producer matching across placeholder divergence."""
    return _norm(path).rsplit("/", 1)[-1]


def _folder(path: str) -> str:
    """Folder form of a path: the directory when the tail looks like a file, else the path."""
    norm = _norm(path)
    tail = norm.rsplit("/", 1)[-1]
    return norm.rsplit("/", 1)[0] if "." in tail else norm


def _items(block: dict[str, Any], *sections: str) -> list[dict[str, Any]]:
    """Flatten the dict items of the named sub-sections of a derived_from/produces block."""
    out: list[dict[str, Any]] = []
    for section in sections:
        for item in (block or {}).get(section, []) or []:
            if isinstance(item, dict):
                out.append(item)
    return out


def _has_skill_doc(skills_root: Path, name: str) -> bool:
    return any((skills_root / name / doc).exists() for doc in SKILL_DOC_NAMES)


def _label(info: dict[str, Any]) -> str:
    """Skill-qualified contract label (e.g. 'requ-explore/contract.yaml') for messages."""
    file = info["file"]
    return f"{file.parent.name}/{file.name}"


def load_contracts(skills_root: Path) -> dict[str, dict[str, Any]]:
    """Map skill-folder-name -> {file, data} for every .claude/skills/*/contract.yaml."""
    contracts: dict[str, dict[str, Any]] = {}
    for path in sorted(skills_root.glob("*/contract.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        contracts[path.parent.name] = {"file": path, "data": data}
    return contracts


def build_producer_index(contracts: dict[str, dict[str, Any]]) -> tuple[set[str], dict[str, set[str]]]:
    """Return (global produced norm/folder forms, per-skill produced basenames)."""
    global_produced: set[str] = set()
    by_skill: dict[str, set[str]] = {}
    for name, info in contracts.items():
        paths = [i.get("path", "") for i in _items(info["data"].get("produces", {}), "required", "conditional")]
        by_skill[name] = {_basename(p) for p in paths if p}
        for path in (p for p in paths if p):
            global_produced.add(_norm(path))
            global_produced.add(_folder(path))
    return global_produced, by_skill


def check_derived_from(
    contracts: dict[str, dict[str, Any]],
    global_produced: set[str],
    by_skill: dict[str, set[str]],
    violations: list[str],
    warnings: list[str],
) -> None:
    """Cross-reference each derived_from input against producers (rules 1 + 2)."""
    for info in contracts.values():
        name = _label(info)
        for item in _items(info["data"].get("derived_from", {}), "required", "optional"):
            path = item.get("path", "")
            src = (item.get("source") or "").strip()
            if src == "external":
                continue
            if src.startswith(SKILL_SOURCE_PREFIX):
                _verify_named_producer(name, path, src, contracts, by_skill, violations, warnings)
                continue
            if any(path.startswith(prefix) for prefix in EXTERNAL_PREFIXES):
                continue
            if _norm(path) not in global_produced and _folder(path) not in global_produced:
                violations.append(
                    f"{name} derived_from '{path}' has no `source:` annotation and no skill "
                    f"declares it in produces. Add `source: external` or `source: skill:<name>`."
                )


def _verify_named_producer(
    name: str,
    path: str,
    src: str,
    contracts: dict[str, dict[str, Any]],
    by_skill: dict[str, set[str]],
    violations: list[str],
    warnings: list[str],
) -> None:
    """Verify a `source: skill:<producer>` input resolves to a managed producer (rule 2)."""
    producer = src[len(SKILL_SOURCE_PREFIX):].strip()
    if producer not in contracts:
        warnings.append(
            f"{name} derived_from '{path}' names producer skill:{producer}, which has no "
            f"contract.yaml yet (unmanaged — will be verifiable once it adopts a contract)."
        )
        return
    if _basename(path) not in by_skill.get(producer, set()):
        violations.append(
            f"{name} derived_from '{path}' declares source: skill:{producer}, but "
            f"{producer}/contract.yaml produces no artifact named '{_basename(path)}'."
        )


def check_may_invoke(contracts: dict[str, dict[str, Any]], skills_root: Path, violations: list[str]) -> None:
    """Every may_invoke target must resolve to an existing skill folder (rule 3)."""
    for info in contracts.values():
        for ref in info["data"].get("may_invoke", []) or []:
            if not _has_skill_doc(skills_root, str(ref)):
                violations.append(
                    f"{_label(info)} may_invoke '{ref}' — no .claude/skills/{ref}/SKILL.md. "
                    f"Misspelled skill name or skill not yet created."
                )


def check_schema_refs(contracts: dict[str, dict[str, Any]], repo_root: Path, violations: list[str]) -> None:
    """Every non-null `schema:` reference must point to an existing file (rule 4)."""
    for info in contracts.values():
        block = info["data"]
        items = _items(block.get("derived_from", {}), "required", "optional") + _items(
            block.get("produces", {}), "required", "conditional"
        )
        for item in items:
            schema = item.get("schema")
            if schema and not (repo_root / schema).exists():
                violations.append(
                    f"{_label(info)} references schema '{schema}' which does not exist."
                )


def check_unmanaged(
    skills_root: Path, contracts: dict[str, dict[str, Any]], violations: list[str]
) -> None:
    """Fail any skill folder that has a SKILL.md but no contract.yaml (sunset enforced 2026-07-29)."""
    managed = set(contracts)
    for folder in sorted(skills_root.iterdir()):
        if folder.is_dir() and folder.name not in managed and _has_skill_doc(skills_root, folder.name):
            violations.append(
                f"{folder.name}: no contract.yaml found. All skills must declare"
                f" contract_version: {CONTRACT_VERSION_REQUIRED} (sunset 2026-07-29)."
            )


def check_contract_versions(contracts: dict[str, dict[str, Any]], violations: list[str]) -> None:
    """Fail any contract that does not declare contract_version: 1 (sunset enforced 2026-07-29)."""
    for info in contracts.values():
        version = info["data"].get("contract_version")
        if version != CONTRACT_VERSION_REQUIRED:
            violations.append(
                f"{_label(info)} declares contract_version: {version!r}; only"
                f" contract_version: {CONTRACT_VERSION_REQUIRED} is valid after the 2026-07-29 sunset."
            )


def check_user_input_gates(contracts: dict[str, dict[str, Any]], violations: list[str]) -> None:
    """Validate every user_input_gates entry against the schema (rule 7).

    Required fields: phase (str), description (str), decision_kind (enum),
    required (enum). A malformed entry is a FAIL at the same severity as an
    unresolved produces: token.
    """
    _DECISION_KIND_VALUES: frozenset[str] = frozenset(
        {"approval", "revision", "selection", "path-selection", "free-text"}
    )
    _REQUIRED_VALUES: frozenset[str] = frozenset({"always", "conditional"})
    _REQUIRED_FIELDS: tuple[str, ...] = ("phase", "description", "decision_kind", "required")

    for info in contracts.values():
        gates = info["data"].get("user_input_gates", None)
        if gates is None:
            continue
        label = _label(info)
        if not isinstance(gates, list):
            violations.append(
                f"{label} user_input_gates must be a list, got {type(gates).__name__}."
            )
            continue
        for i, entry in enumerate(gates):
            if not isinstance(entry, dict):
                violations.append(
                    f"{label} user_input_gates[{i}] must be a dict, got {type(entry).__name__}."
                )
                continue
            for field in _REQUIRED_FIELDS:
                if field not in entry:
                    violations.append(
                        f"{label} user_input_gates[{i}] missing required field '{field}'. "
                        f"Schema: .claude/schemas/user_input_gate.yaml"
                    )
            kind = entry.get("decision_kind", "")
            if kind and kind not in _DECISION_KIND_VALUES:
                violations.append(
                    f"{label} user_input_gates[{i}] invalid decision_kind '{kind}'. "
                    f"Must be one of: {', '.join(sorted(_DECISION_KIND_VALUES))}."
                )
            req = entry.get("required", "")
            if req and req not in _REQUIRED_VALUES:
                violations.append(
                    f"{label} user_input_gates[{i}] invalid required value '{req}'. "
                    f"Must be one of: {', '.join(sorted(_REQUIRED_VALUES))}."
                )


def run_checks(skills_root: Path, repo_root: Path) -> tuple[list[str], list[str], int]:
    """Run every check; return (violations, warnings, contracts-checked count)."""
    contracts = load_contracts(skills_root)
    violations: list[str] = []
    warnings: list[str] = []
    check_unmanaged(skills_root, contracts, violations)  # runs even when contracts is empty
    if not contracts:
        return violations, warnings, 0
    global_produced, by_skill = build_producer_index(contracts)
    check_derived_from(contracts, global_produced, by_skill, violations, warnings)
    check_may_invoke(contracts, skills_root, violations)
    check_schema_refs(contracts, repo_root, violations)
    check_contract_versions(contracts, violations)
    check_user_input_gates(contracts, violations)
    return violations, warnings, len(contracts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", type=Path, default=Path(".claude/skills"))
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    violations, warnings, checked = run_checks(args.skills_root, args.repo_root)
    if checked == 0:
        print("No contract.yaml files found under", args.skills_root)
        return 0

    for warning in warnings:
        print(f"WARNING: {warning}")

    if violations:
        print(f"FAIL — {len(violations)} contract violation(s):")
        for violation in violations:
            print(f"  - {violation}")
        return 1
    print(f"PASS — {checked} contract(s) checked, 0 violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
