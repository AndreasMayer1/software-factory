#!/usr/bin/env python3
"""Validate a YAML artifact against a .claude/schemas/<artifact>.yaml schema (REQ-PROC-044 Wave 2).

The schema dialect is the flat YAML form adopted in REQ-PROC-044 D-2 (NOT JSON Schema):
a top-level ``required:`` / ``optional:`` / ``conditional:`` block, each a mapping of
field-name -> field-spec (``type`` / ``enum`` / ``pattern`` / ...). This validator is the
runtime leg of the contract mechanism — the 5-line consumer pre-checks call it so a malformed
or incomplete input fails loudly at skill entry instead of producing a silent bad artifact.

Three checks (the contract scope — kept deliberately narrow to avoid false positives):
  1. every key declared under ``required:`` is present in the artifact;
  2. every key in the artifact is declared somewhere in the schema (unknown keys rejected —
     "optional keys allowed" means only the declared optional/conditional keys);
  3. every present field whose spec carries an ``enum:`` holds a value from that enum.

Output (Output: contract for AC-09): a ``PASS — ...`` line (exit 0) or a ``FAIL — N error(s)``
header followed by one ``  - `` line per error naming the artifact, the field, and what is
wrong (exit 1). The per-error specificity satisfies the file-02 §Q5 anti-punting rule.
Usage: ``validate_against_schema.py <artifact-path> <schema-path>``.
"""

# tier: B  # validator; imported by tests, run as the runtime leg of the contract mechanism

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

# Sub-blocks of a schema that declare artifact fields. Other top-level keys
# (schema_version, artifact, description) are schema metadata, not field declarations.
FIELD_SECTIONS: tuple[str, ...] = ("required", "optional", "conditional")
# Suffix whose presence means the input carries YAML frontmatter rather than being pure YAML.
FRONTMATTER_SUFFIX = ".md"


class ArtifactLoadError(ValueError):
    """Raised when the artifact file cannot be read as the expected YAML shape."""


def load_artifact(path: Path) -> dict[str, Any]:
    """Load the artifact as a mapping — frontmatter for .md, whole-file YAML otherwise."""
    if path.suffix == FRONTMATTER_SUFFIX:
        # Why: .md inputs (e.g. goal.md) carry the data in YAML frontmatter; the sanctioned
        # helper is the only G4-allowlisted frontmatter reader (no hand-rolled parsing here).
        # Local import: keeps the util helper optional for pure-YAML callers.
        from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # sibling import via sys.path; mypy cannot follow runtime path manipulation
            read_frontmatter,
        )

        return dict(read_frontmatter(path).metadata)
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ArtifactLoadError(
            f"{path}: expected a YAML mapping at the top level, got {type(data).__name__}."
        )
    return data


def load_schema(path: Path) -> dict[str, Any]:
    """Load a schema file; raise if it is not a mapping."""
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ArtifactLoadError(f"{path}: schema is not a YAML mapping.")
    return data


def _field_specs(schema: dict[str, Any]) -> dict[str, Any]:
    """Flatten required/optional/conditional sub-blocks into one field-name -> spec map."""
    specs: dict[str, Any] = {}
    for section in FIELD_SECTIONS:
        block = schema.get(section) or {}
        if isinstance(block, dict):
            specs.update(block)
    return specs


def _required_keys(schema: dict[str, Any]) -> list[str]:
    block = schema.get("required") or {}
    return list(block) if isinstance(block, dict) else []


def check_artifact(artifact: dict[str, Any], schema: dict[str, Any], label: str) -> list[str]:
    """Return a list of human-readable error messages (empty list == valid)."""
    errors: list[str] = []
    specs = _field_specs(schema)

    for key in _required_keys(schema):
        if key not in artifact:
            errors.append(f"{label}: missing required key '{key}'.")

    for key in artifact:
        if key not in specs:
            errors.append(f"{label}: unknown key '{key}' not declared in the schema.")

    for key, value in artifact.items():
        spec = specs.get(key)
        if not isinstance(spec, dict):
            continue
        enum = spec.get("enum")
        if isinstance(enum, list) and isinstance(value, (str, int, bool)) and value not in enum:
            errors.append(f"{label}: key '{key}' value '{value}' is not one of {enum}.")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path, help="Path to the YAML / .md-frontmatter artifact to validate.")
    parser.add_argument("schema", type=Path, help="Path to the .claude/schemas/<artifact>.yaml schema.")
    args = parser.parse_args(argv)

    if not args.artifact.exists():
        print(f"FAIL — artifact not found: {args.artifact}")
        return 1
    if not args.schema.exists():
        print(f"FAIL — schema not found: {args.schema}")
        return 1

    try:
        artifact = load_artifact(args.artifact)
        schema = load_schema(args.schema)
    except (ArtifactLoadError, yaml.YAMLError) as exc:
        print(f"FAIL — {exc}")
        return 1

    errors = check_artifact(artifact, schema, str(args.artifact))
    if errors:
        print(f"FAIL — {len(errors)} error(s) against {args.schema}:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS — {args.artifact} conforms to {args.schema}.")
    return 0


if __name__ == "__main__":
    # Why: scripts/ is not a package root; the util import in load_artifact resolves once
    # scripts/ is on sys.path. Add it here so the .md branch works under direct execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    sys.exit(main())
