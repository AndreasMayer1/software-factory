#!/usr/bin/env python3
"""Render a Markdown index of all user_input_gates declared in skill and agent contracts.

Reads .claude/skills/*/contract.yaml and .claude/agents/*.contract.yaml, collects
every `user_input_gates:` entry, validates each entry against the
.claude/schemas/user_input_gate.yaml schema, and writes a Markdown table.

Output:
    .factory/overview/user_input_gates.md (or --output PATH)
    Stdout: "User input gates written to <path> (N gates across M skills)"

Usage:
    scripts/factory/render_user_input_gates.py [--output PATH]

Exit codes:
    0 — success (file written, no schema violations)
    1 — one or more schema violations found
"""

# tier: B  # generator; reads contracts and validates against schema — non-trivial logic

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).parent.parent.parent

DEFAULT_OUTPUT = ".factory/overview/user_input_gates.md"
SKILLS_DIR = ".claude/skills"
AGENTS_DIR = ".claude/agents"

REQUIRED_FIELDS: tuple[str, ...] = ("phase", "description", "decision_kind", "required")
DECISION_KIND_VALUES: frozenset[str] = frozenset(
    {"approval", "revision", "selection", "path-selection", "free-text"}
)
REQUIRED_VALUES: frozenset[str] = frozenset({"always", "conditional"})


# ---------------------------------------------------------------------------
# Contract collection
# ---------------------------------------------------------------------------


def collect_skill_contracts(project_root: Path) -> list[tuple[str, Path, dict[str, Any]]]:
    """Return (skill_name, contract_path, data) for every skill contract."""
    skills_root = project_root / SKILLS_DIR
    results: list[tuple[str, Path, dict[str, Any]]] = []
    if not skills_root.exists():
        return results
    for contract_path in sorted(skills_root.glob("*/contract.yaml")):
        skill_name = contract_path.parent.name
        try:
            data = yaml.safe_load(contract_path.read_text()) or {}
        except yaml.YAMLError as exc:
            sys.stderr.write(f"WARNING: failed to parse {contract_path}: {exc}\n")
            data = {}
        results.append((skill_name, contract_path, data))
    return results


def collect_agent_contracts(project_root: Path) -> list[tuple[str, Path, dict[str, Any]]]:
    """Return (agent_name, contract_path, data) for every agent contract."""
    agents_root = project_root / AGENTS_DIR
    results: list[tuple[str, Path, dict[str, Any]]] = []
    if not agents_root.exists():
        return results
    for contract_path in sorted(agents_root.glob("*.contract.yaml")):
        agent_name = contract_path.stem.replace(".contract", "")
        try:
            data = yaml.safe_load(contract_path.read_text()) or {}
        except yaml.YAMLError as exc:
            sys.stderr.write(f"WARNING: failed to parse {contract_path}: {exc}\n")
            data = {}
        results.append((agent_name, contract_path, data))
    return results


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def validate_gate_entry(
    source_label: str,
    entry: dict[str, Any],
    violations: list[str],
) -> bool:
    """Validate one user_input_gates entry against the schema. Returns True if valid."""
    valid = True

    for field in REQUIRED_FIELDS:
        if field not in entry:
            violations.append(
                f"{source_label}: user_input_gates entry missing required field '{field}'. "
                f"Required fields: {', '.join(REQUIRED_FIELDS)}."
            )
            valid = False

    kind = entry.get("decision_kind", "")
    if kind and kind not in DECISION_KIND_VALUES:
        violations.append(
            f"{source_label}: user_input_gates entry has invalid decision_kind '{kind}'. "
            f"Must be one of: {', '.join(sorted(DECISION_KIND_VALUES))}."
        )
        valid = False

    req = entry.get("required", "")
    if req and req not in REQUIRED_VALUES:
        violations.append(
            f"{source_label}: user_input_gates entry has invalid required value '{req}'. "
            f"Must be one of: {', '.join(sorted(REQUIRED_VALUES))}."
        )
        valid = False

    return valid


# ---------------------------------------------------------------------------
# Gate collection
# ---------------------------------------------------------------------------


def collect_gates(
    contracts: list[tuple[str, Path, dict[str, Any]]],
    source_type: str,
    violations: list[str],
) -> list[dict[str, Any]]:
    """Extract and validate all user_input_gates entries from a list of contracts.

    Returns a list of row dicts with keys: source, phase, description, decision_kind, required.
    """
    rows: list[dict[str, Any]] = []
    for name, _contract_path, data in contracts:
        gates = data.get("user_input_gates", None)
        if gates is None:
            continue
        if not isinstance(gates, list):
            violations.append(
                f"{source_type}/{name}/contract.yaml: user_input_gates must be a list, "
                f"got {type(gates).__name__}."
            )
            continue
        for i, entry in enumerate(gates):
            if not isinstance(entry, dict):
                violations.append(
                    f"{source_type}/{name}/contract.yaml: user_input_gates[{i}] must be "
                    f"a dict, got {type(entry).__name__}."
                )
                continue
            source_label = f"{source_type}/{name}/contract.yaml[{i}]"
            validate_gate_entry(source_label, entry, violations)
            rows.append({
                "source": name,
                "phase": entry.get("phase", ""),
                "description": entry.get("description", ""),
                "decision_kind": entry.get("decision_kind", ""),
                "required": entry.get("required", ""),
            })
    return rows


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_markdown(rows: list[dict[str, Any]], n_skills: int, n_agents: int) -> str:
    """Render the gate rows as a Markdown table."""
    lines: list[str] = [
        "# User Input Gates Index",
        "",
        "Generated from `.claude/skills/*/contract.yaml` and `.claude/agents/*.contract.yaml`.",
        f"Covers {n_skills} skill contract(s) and {n_agents} agent contract(s).",
        "",
    ]

    if not rows:
        lines.append("_No `user_input_gates:` sections declared in any contract yet._")
        return "\n".join(lines)

    lines += [
        "| Skill / Agent | Phase | Description | Decision Kind | Required |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        def _esc(s: str) -> str:
            return s.replace("|", "\\|")

        lines.append(
            f"| {_esc(row['source'])} "
            f"| {_esc(row['phase'])} "
            f"| {_esc(row['description'])} "
            f"| {_esc(row['decision_kind'])} "
            f"| {_esc(row['required'])} |"
        )

    lines += ["", f"_Total: {len(rows)} gate(s)._"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a Markdown index of user_input_gates from skill and agent contracts."
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output Markdown path (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    args = _parse_args(argv)
    project_root = Path(__file__).parent.parent.parent

    violations: list[str] = []

    skill_contracts = collect_skill_contracts(project_root)
    agent_contracts = collect_agent_contracts(project_root)

    skill_rows = collect_gates(skill_contracts, ".claude/skills", violations)
    agent_rows = collect_gates(agent_contracts, ".claude/agents", violations)
    all_rows = skill_rows + agent_rows

    if violations:
        print(f"FAIL — {len(violations)} user_input_gates schema violation(s):")
        for v in violations:
            print(f"  - {v}")
        return 1

    md = render_markdown(all_rows, len(skill_contracts), len(agent_contracts))

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = project_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8")

    print(
        f"User input gates written to {output_path} "
        f"({len(all_rows)} gates across {len(skill_contracts)} skills, "
        f"{len(agent_contracts)} agents)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
