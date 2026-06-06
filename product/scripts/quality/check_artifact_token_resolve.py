#!/usr/bin/env python3
"""Resolve-to-token lint (REQ-PROC-044-02 AC-02, AC-03).

Checks:
  (a) Every produces:/derived_from: value in .claude/skills/*/contract.yaml and
      .claude/agents/*.contract.yaml is a token defined in the artifact registry.
  (b) The expertise segment of every .claude/agents/*.md name governed by the
      {expertise}-{role} scheme (REQ-PROC-044-01 AC-01) is a registry token.
  (c) The registry itself contains no duplicate tokens.

Output: PASS — ... (exit 0) or FAIL — N violation(s) (exit 1).
If the registry does not exist, exits 0 with a warning (graceful — registry may be
incomplete while TASK-PROC-044-02-01 is still in progress).
"""

# tier: B  # validator; cross-reference logic between contracts and registry, run as a quality gate

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

# Closed role set from REQ-PROC-044-01 AC-01: {expertise}-{role} naming scheme.
GOVERNED_ROLES: frozenset[str] = frozenset({"writer", "transformer", "reviewer", "classifier"})
REGISTRY_YAML_TAG = "tag:yaml.org,2002:map"


# ── Registry loading ────────────────────────────────────────────────────────


class _DupCheckLoader(yaml.SafeLoader):  # type: ignore[misc]  # yaml SafeLoader is untyped
    """SafeLoader subclass that raises yaml.YAMLError on duplicate mapping keys."""


def _construct_mapping_no_dups(
    loader: _DupCheckLoader,
    node: Any,
) -> dict[str, Any]:
    loader.flatten_mapping(node)
    pairs: list[tuple[str, Any]] = loader.construct_pairs(node)
    seen: set[str] = set()
    duplicates: list[str] = []
    for key, _ in pairs:
        key_s = str(key)
        if key_s in seen:
            duplicates.append(key_s)
        seen.add(key_s)
    if duplicates:
        raise yaml.YAMLError(
            f"Duplicate token(s) in registry: {', '.join(sorted(set(duplicates)))}"
        )
    return dict(pairs)


_DupCheckLoader.add_constructor(REGISTRY_YAML_TAG, _construct_mapping_no_dups)


def load_registry(registry_path: Path, violations: list[str]) -> set[str]:
    """Return the known token set; append duplicate-token violations to *violations*."""
    text = registry_path.read_text()
    try:
        data: dict[str, Any] = yaml.load(text, Loader=_DupCheckLoader) or {}
    except yaml.YAMLError as exc:
        violations.append(f"registry: {exc}")
        data = yaml.safe_load(text) or {}
    return set(data.keys())


# ── Value extraction helpers ────────────────────────────────────────────────


def _paths_from_block(block: Any, *sections: str) -> list[str]:
    """Extract path: strings from a structured contract block (skill-contract format)."""
    if not isinstance(block, dict):
        return []
    result: list[str] = []
    for section in sections:
        for item in block.get(section) or []:
            if isinstance(item, dict):
                path = item.get("path")
                if path:
                    result.append(str(path))
    return result


def _strings_from_field(field: Any) -> list[str]:
    """Extract plain string values from a contract field (list format used by agent contracts)."""
    if not isinstance(field, list):
        return []
    return [item for item in field if isinstance(item, str)]


# ── Check functions ────────────────────────────────────────────────────────


def check_skill_contracts(
    skills_root: Path, tokens: set[str], violations: list[str]
) -> int:
    """Check .claude/skills/*/contract.yaml; return number of files checked."""
    count = 0
    for path in sorted(skills_root.glob("*/contract.yaml")):
        data: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
        label = f"{path.parent.name}/contract.yaml"
        produces_paths = _paths_from_block(data.get("produces"), "required", "conditional")
        derived_paths = _paths_from_block(data.get("derived_from"), "required", "optional")
        for value in produces_paths + derived_paths:
            if value not in tokens:
                violations.append(
                    f"{label}: produces/derived_from path {value!r} does not resolve to a registry token."
                )
        count += 1
    return count


def check_agent_contracts(
    agents_root: Path, tokens: set[str], violations: list[str]
) -> int:
    """Check .claude/agents/*.contract.yaml; return number of files checked."""
    count = 0
    for path in sorted(agents_root.glob("*.contract.yaml")):
        data: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
        label = path.name
        for field_name in ("produces", "derived_from", "consumes"):
            for value in _strings_from_field(data.get(field_name)):
                if value not in tokens:
                    violations.append(
                        f"{label}: {field_name} value {value!r} does not resolve to a registry token."
                    )
        count += 1
    return count


def _expertise_segment(name: str) -> str | None:
    """Return the expertise prefix if *name* ends with a governed role; else None."""
    for role in GOVERNED_ROLES:
        suffix = f"-{role}"
        if name.endswith(suffix) and len(name) > len(suffix):
            return name[: -len(suffix)]
    return None


def check_agent_names(
    agents_root: Path, tokens: set[str], violations: list[str]
) -> int:
    """Check .claude/agents/*.md names for {expertise}-{role} compliance; return count."""
    count = 0
    for path in sorted(agents_root.glob("*.md")):
        if path.name.startswith("."):
            continue
        name = path.stem
        expertise = _expertise_segment(name)
        if expertise is None:
            violations.append(
                f"{path.name}: agent name {name!r} does not follow {{expertise}}-{{role}}"
                f" (role must be one of: {', '.join(sorted(GOVERNED_ROLES))})."
            )
        elif expertise not in tokens:
            violations.append(
                f"{path.name}: agent expertise {expertise!r} does not resolve to a registry token."
            )
        count += 1
    return count


# ── Baseline suppression ────────────────────────────────────────────────────


def load_baseline(baseline_path: Path | None) -> set[str]:
    """Return the set of violation strings suppressed by the baseline file."""
    if baseline_path is None or not baseline_path.exists():
        return set()
    return {
        line.strip()
        for line in baseline_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }


# ── Testable runner ────────────────────────────────────────────────────────


def run_checks(
    registry_path: Path,
    skills_root: Path,
    agents_root: Path,
) -> tuple[list[str], int, int, int]:
    """Run all checks; return (violations, skill_count, agent_contract_count, agent_count)."""
    violations: list[str] = []
    tokens = load_registry(registry_path, violations)
    skill_count = check_skill_contracts(skills_root, tokens, violations)
    agent_contract_count = check_agent_contracts(agents_root, tokens, violations)
    agent_count = check_agent_names(agents_root, tokens, violations)
    return violations, skill_count, agent_contract_count, agent_count


# ── Main ────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(".factory/registry/artifacts.yaml"),
        help="Path to the artifact registry YAML file.",
    )
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=Path(".claude/skills"),
        help="Root directory containing skill sub-folders.",
    )
    parser.add_argument(
        "--agents-root",
        type=Path,
        default=Path(".claude/agents"),
        help="Root directory containing agent files.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="Baseline file; violation strings matching a line are suppressed.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root (defaults to current working directory).",
    )
    args = parser.parse_args()

    registry_path = args.repo_root / args.registry
    if not registry_path.exists():
        print(
            f"WARNING: registry not found at {registry_path}"
            " — skipping resolve lint (TASK-PROC-044-02-01 may be incomplete). Exit 0."
        )
        return 0

    violations, skill_count, agent_contract_count, agent_count = run_checks(
        registry_path,
        args.repo_root / args.skills_root,
        args.repo_root / args.agents_root,
    )

    baseline = load_baseline(args.baseline)
    baselined = [v for v in violations if v in baseline]
    unbaselined = [v for v in violations if v not in baseline]
    baselined_note = f" [{len(baselined)} baselined]" if baselined else ""

    if unbaselined:
        print(f"FAIL — {len(unbaselined)} unbaselined violation(s){baselined_note}:")
        for v in unbaselined:
            print(f"  - {v}")
        return 1

    print(
        f"PASS — checked {skill_count} skill contract(s),"
        f" {agent_contract_count} agent contract(s),"
        f" {agent_count} agent(s);"
        f" 0 unbaselined violation(s).{baselined_note}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
