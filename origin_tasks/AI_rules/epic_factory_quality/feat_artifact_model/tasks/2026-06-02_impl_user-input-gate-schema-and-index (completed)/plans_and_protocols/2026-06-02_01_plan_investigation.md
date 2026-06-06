# Investigation Plan: User Input Gate Schema and Index

**Task**: TASK-PROC-044-02-06  
**Date**: 2026-06-02  
**Status**: Investigation complete — ready for implementation

---

## Section 1: File Inventory

### 1.1 `scripts/factory/render_factory_map.py`

- **Tier annotation**: `# tier: B  # generator; imported by tests and CI — non-trivial graph-building logic`
- **Module docstring** pattern: multi-line, describes what it reads/writes, stdout format, and usage CLI
- **`from __future__ import annotations`** at top (all tier-B scripts use this)
- **Imports**: `argparse`, `json`, `sys`, `pathlib.Path`, `typing.Any`, `yaml`
- **Constants block**: `_PROJECT_ROOT = Path(__file__).parent.parent.parent`, named string constants, tuple of tuples
- **`_parse_args(argv)`** function with `argparse.ArgumentParser`, `--output` and optional flags
- **`main(argv=None) -> int`** returns exit code, called via `if __name__ == "__main__": sys.exit(main())`
- **Error handling**: `sys.stderr.write(f"WARNING: ...")` for non-fatal parse errors; exit code 1 for failures
- **Output**: writes file, prints to stdout `"<Label> written to <path> (...)"`, returns 0
- **Project root resolution**: `Path(__file__).parent.parent.parent` (script is in `scripts/factory/`, so this resolves to repo root)
- **Default output path**: relative string constant, made absolute in `main()` via `project_root / output_path`

### 1.2 `scripts/quality/check_skill_contracts.py`

- **Tier annotation**: `# tier: B  # validator; non-trivial cross-reference logic, run as a quality gate`
- **Docstring**: describes all 6 checks, output format (`PASS —` / `FAIL — N violation(s)`), and consumer
- **Key constants**: `EXTERNAL_PREFIXES`, `SKILL_SOURCE_PREFIX`, `SKILL_DOC_NAMES`
- **Top-level YAML keys in contracts**: `contract_version`, `purpose`, `derived_from`, `produces`, `quality_criteria`, `may_invoke`, `side_effects`, `preconditions`, `postconditions`
- **`load_contracts(skills_root)`**: maps skill-name → `{file: Path, data: dict}` by globbing `*/contract.yaml`
- **`run_checks(skills_root, repo_root)`**: calls individual check functions; returns `(violations, warnings, count)`
- **Check pattern**: each check function takes `contracts`, optional extras, and mutates `violations: list[str]`
- **`main()`**: `argparse` with `--skills-root` and `--repo-root`; calls `run_checks`; prints violations with `"  - "` prefix; exits 1 on violations
- **Violation severity model**: `violations` = FAIL (exit 1); `warnings` = advisory only (exit 0)
- **`_items(block, *sections)`** helper: flattens `required`/`optional`/`conditional` sub-lists of a contract block into a flat list of dicts
- **Schema ref check** (`check_schema_refs`): iterates `derived_from` and `produces` items, finds `schema:` key, checks `(repo_root / schema).exists()`
- **The `user_input_gates` block** does not currently exist in contracts; this task adds it

### 1.3 `.factory/registry/artifacts.yaml`

- **Top-level structure**: `_categories` dict (category → description), then flat token entries
- **Each token entry format**:
  ```yaml
  token-name:
    category: <category-key>
    path: "<glob-pattern>"
    definition: "One-line definition"
  ```
- **`factory-skills` category** entries already present (lines 280–320):
  - `skill`, `skill-contract`, `skill-index`, `agent`, `agent-contract`, `factory-flows`, `task-ordering`, `claude-md`
- **`feedback-checkpoint`** token is already present (lines 81–84) — confirmed by grep. This is the predecessor token added by TASK-PROC-041-04-03.
- **Append pattern**: new tokens go at the bottom of the relevant category section. The `factory-skills` section is section 7 (lines 277–320).
- **The `user-input-gate` token is NOT yet present** — confirmed by artifact list scan.

### 1.4 `.claude/skills/ux-write-persona/contract.yaml`

- **Top-level keys**: `contract_version`, `skill`, `purpose`, `derived_from`, `produces`, `quality_criteria`, `may_invoke`, `side_effects`, `preconditions`, `postconditions`
- **`quality_criteria`** (line 49): `"User approval gate must be passed before cascade scan runs."` — this is the prose description of the gate that should be supplemented by a structured `user_input_gates:` section
- **Skill phases** (from SKILL.md): gate occurs at **Step 6.5 — "User Approval Gate"** between generation (Step 5/6) and cascade scan (Step 7)
- **Decision kind**: `approval` — user either approves or provides revision feedback; no selection between options
- **Required**: `always` — the gate is unconditional; it runs for both CREATE and UPDATE modes

### 1.5 `.claude/skills/ux-write-scenario/contract.yaml`

- **Top-level keys**: identical structure to ux-write-persona contract
- **`quality_criteria`** (line 49): `"User approval gate must be passed before SCENARIO_INDEX update and cascade run."` — same pattern
- **Skill phases** (from SKILL.md): gate occurs at **Step 8.5 — "User Approval Gate"** between scenario generation (Step 8/8.1) and index update (Step 9)
- **Decision kind**: `approval` — same pattern; user approves or revises
- **Required**: `always` — unconditional

### 1.6 `.claude/skills/claude-create-skill/SKILL.md`

- **Artifact-Establishment Gate section** (lines 99–108): covers `produces:` and `derived_from:` token registration
- **Gate logic**: read registry → for each unknown token → interactive: propose+ratify; automated: write pending_feedback → proceed only when all tokens exist
- **`user_input_gates:` is NOT mentioned** — this is the gap to fill
- **Target edit**: Step 4b and the "Artifact-Establishment Gate" section at the bottom need updating to mention `user_input_gates:` entries

### 1.7 `.claude/skills/claude-modify-skill/SKILL.md`

- **Artifact-Establishment Gate section** (lines 49–57): identical logic to claude-create-skill; covers only `produces:` and `derived_from:`
- **Target edit**: Step 4b and "Artifact-Establishment Gate" section need the same `user_input_gates:` addition

### 1.8 `.claude/schemas/` directory

**Exists**. Contents:
- `concept_canon_entry.yaml`
- `external_contract.yaml`
- `flow_navigation.yaml`
- `flutter_handoff.yaml`
- `goal_metadata.yaml`
- `pending_question.yaml`
- `requirements_frontmatter.yaml`
- `revision_target.yaml`
- `scribble_metadata.yaml`

**Schema dialect**: The schemas in this directory use the project's own "flat YAML with required:/optional: blocks" dialect (REQ-PROC-044 D-2), NOT the full JSON Schema Draft-7 dialect. They use `schema_version: 1`, `artifact:`, `description:`, then `required:` and `optional:` blocks where each field is described with `type:`, `enum:`, `description:`, etc.

**`user_input_gate.yaml` does NOT exist yet** — this is deliverable 1.

### 1.9 `.claude/agents/*.contract.yaml`

**Files found**:
- `architecture-advisor.contract.yaml`
- `implementation-engineer.contract.yaml`
- `opus-advisor.contract.yaml`
- `quality-checker.contract.yaml`
- `setup-optimizer.contract.yaml`
- `test-engineer.contract.yaml`
- `ui-scribble-generator.contract.yaml`
- `ui-scribble-handoff-emitter.contract.yaml`
- `ui-scribble-persona-walker.contract.yaml`

Agent contracts have a simpler structure (see `quality-checker.contract.yaml`): top-level keys include `contract_version`, `purpose`, `derived_from`, `consumes`, `produces` — slightly different from skill contracts (no `quality_criteria`, `may_invoke`, `side_effects`, etc.). The render script must handle both structures gracefully.

---

## Section 2: Proposed Content for Each Deliverable

### 2.1 `.claude/schemas/user_input_gate.yaml`

Full file content:

```yaml
# Schema: user_input_gate.yaml
#
# Canonical shape of a single entry in the `user_input_gates:` list field
# of any skill or agent contract (.claude/skills/*/contract.yaml,
# .claude/agents/*.contract.yaml).
#
# Produced by: (human-authored when adding user_input_gates: to a contract)
# Consumed by: check_skill_contracts.py (contract lint gate),
#              scripts/factory/render_user_input_gates.py (index generator)
#
# Governance: REQ-PROC-044-02 AC-07
#
# Dialect: flat YAML with required:/optional: blocks (REQ-PROC-044 D-2).
# NOT full JSON Schema — human-readable documentation + lint-augmented
# declaration consumed by check_skill_contracts.py.

schema_version: 1
artifact: user_input_gates entry in a skill or agent contract
description: >
  One developer-decision checkpoint declared inside a skill or agent contract.
  Each entry names the skill execution phase where the gate occurs, describes
  what the developer decides, classifies the decision kind, and states whether
  the gate is unconditional or conditional.

required:
  phase:
    type: string
    description: >
      The named skill step or phase where the gate occurs (e.g.
      "Step 6.5 — User Approval Gate"). Must be a non-empty string that
      identifies a specific step in the skill's execution sequence.

  description:
    type: string
    description: >
      One sentence describing what the developer decides at this gate
      (e.g. "Developer approves the generated persona or provides revision
      feedback before cascade scan runs.").

  decision_kind:
    type: string
    enum: [approval, revision, selection, path-selection, free-text]
    description: >
      Classification of the decision type:
        approval      — binary yes/proceed or no/revise; developer either
                        approves the artifact or sends it back for changes
        revision      — developer supplies specific corrective content;
                        the gate is not a yes/no but a directive rewrite
        selection     — developer picks one item from an enumerated list
                        of options the skill presents
        path-selection — developer chooses between two or more execution
                        branches that lead to meaningfully different outputs
        free-text     — developer enters open-ended input that the skill
                        cannot anticipate (e.g. naming a new persona)

  required:
    type: string
    enum: [always, conditional]
    description: >
      'always'      — the gate runs on every invocation of this skill,
                      regardless of input or mode.
      'conditional' — the gate only runs under conditions described in the
                      skill's SKILL.md (e.g. only in CREATE mode, or only
                      when a conflict is detected). When 'conditional',
                      authors SHOULD add a `condition:` field (optional below).

optional:
  condition:
    type: string
    description: >
      Present only when required: conditional. A brief statement of when
      the gate fires (e.g. "Only in UPDATE mode when existing artifact is
      already approved.").
```

### 2.2 `scripts/factory/render_user_input_gates.py`

Full file content:

```python
#!/usr/bin/env python3
"""Render a Markdown index of all user_input_gates declared in skill and agent contracts.

Reads .claude/skills/*/contract.yaml and .claude/agents/*.contract.yaml, collects
every `user_input_gates:` entry, validates each entry against the
.claude/schemas/user_input_gate.yaml schema, and writes a Markdown table.

Output:
    requirements_tasks/STATUS.user_input_gates.md (or --output PATH)
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

DEFAULT_OUTPUT = "requirements_tasks/STATUS.user_input_gates.md"
SKILLS_DIR = ".claude/skills"
AGENTS_DIR = ".claude/agents"
SCHEMA_PATH = ".claude/schemas/user_input_gate.yaml"

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
    for name, contract_path, data in contracts:
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
        # Escape pipe characters in field values
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
```

### 2.3 `.factory/registry/artifacts.yaml` append

Append the following block at the end of **Section 7 (factory-skills)**, after the `claude-md:` entry (currently the last entry in that section, around line 320). Insert it before the section 8 comment `# ---------------------------------------------------------------------------`:

```yaml
user-input-gate:
  category: factory-skills
  path: ".claude/schemas/user_input_gate.yaml"
  definition: "Schema for a single user_input_gates entry in a skill or agent contract"
```

**Exact insertion context** — the text immediately before the insertion point (the separator line starting section 8):

Old (the last lines of section 7 and the separator):
```yaml
claude-md:
  category: factory-skills
  path: "CLAUDE.md"
  definition: "Project constitution: orchestration rules, coding standards, workflow enforcement"

# ---------------------------------------------------------------------------
# 8. Automation
# ---------------------------------------------------------------------------
```

New:
```yaml
claude-md:
  category: factory-skills
  path: "CLAUDE.md"
  definition: "Project constitution: orchestration rules, coding standards, workflow enforcement"

user-input-gate:
  category: factory-skills
  path: ".claude/schemas/user_input_gate.yaml"
  definition: "Schema for a single user_input_gates entry in a skill or agent contract"

# ---------------------------------------------------------------------------
# 8. Automation
# ---------------------------------------------------------------------------
```

### 2.4 `scripts/quality/check_skill_contracts.py` extension

Two changes are needed:

**Change A**: Add a new check function after `check_contract_versions` (around line 208).

Insert this new function **between `check_contract_versions` and `run_checks`**:

```python
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
```

**Change B**: Add the call to `check_user_input_gates` inside `run_checks`, after the existing `check_contract_versions` call.

Old `run_checks` function:
```python
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
    return violations, warnings, len(contracts)
```

New `run_checks` function:
```python
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
```

Also update the module docstring to include the new check. The old docstring list ends at rule 6; append rule 7:

Old docstring (last two lines of the numbered list):
```
  5. every skill folder with a SKILL.md has a contract.yaml (post-sunset: missing → FAIL).
  6. every contract.yaml declares `contract_version: 1` (post-sunset: version 0 → FAIL).
```

New (add line after rule 6):
```
  5. every skill folder with a SKILL.md has a contract.yaml (post-sunset: missing → FAIL).
  6. every contract.yaml declares `contract_version: 1` (post-sunset: version 0 → FAIL).
  7. every `user_input_gates:` entry conforms to .claude/schemas/user_input_gate.yaml —
     malformed entry (missing field or out-of-vocabulary value) is a FAIL at the same
     severity as an unresolved produces: token.
```

### 2.5 `.claude/skills/ux-write-persona/contract.yaml` patch

**Where**: Add a new top-level `user_input_gates:` section after `quality_criteria:` and before `may_invoke:`.

Old (lines 45–52 of the contract):
```yaml
quality_criteria:
  - All 8 README guideline files read simultaneously before authoring.
  - Preanalysis (Phase 2.5) must be complete before persona.md is written in CREATE mode.
  - Unique PERSONA-ID verified by re-running generate_id_registry.py before writing.
  - User approval gate must be passed before cascade scan runs.
  - Cascade scan uses keyword matching for constraint personas — keywords listed per impairment type.

may_invoke: []
```

New:
```yaml
quality_criteria:
  - All 8 README guideline files read simultaneously before authoring.
  - Preanalysis (Phase 2.5) must be complete before persona.md is written in CREATE mode.
  - Unique PERSONA-ID verified by re-running generate_id_registry.py before writing.
  - User approval gate must be passed before cascade scan runs.
  - Cascade scan uses keyword matching for constraint personas — keywords listed per impairment type.

user_input_gates:
  - phase: "Step 6.5 — User Approval Gate"
    description: "Developer approves the generated or updated persona before cascade scan runs, or provides revision feedback to loop back."
    decision_kind: approval
    required: always

may_invoke: []
```

### 2.6 `.claude/skills/ux-write-scenario/contract.yaml` patch

**Where**: Add a new top-level `user_input_gates:` section after `quality_criteria:` and before `may_invoke:`.

Old (lines 45–53 of the contract):
```yaml
quality_criteria:
  - All 9 README guideline files read simultaneously before authoring.
  - Parent persona must be approved (or user explicitly accepts the warning).
  - Unique SCEN-ID verified by re-running generate_id_registry.py before writing.
  - User approval gate must be passed before SCENARIO_INDEX update and cascade run.
  - Scope exclusion overlap checked before scenario creation proceeds.
  - Canon check (ux-write-canon-concept) invoked only for FUTURE-state scenarios.

may_invoke:
  - ux-write-canon-concept
```

New:
```yaml
quality_criteria:
  - All 9 README guideline files read simultaneously before authoring.
  - Parent persona must be approved (or user explicitly accepts the warning).
  - Unique SCEN-ID verified by re-running generate_id_registry.py before writing.
  - User approval gate must be passed before SCENARIO_INDEX update and cascade run.
  - Scope exclusion overlap checked before scenario creation proceeds.
  - Canon check (ux-write-canon-concept) invoked only for FUTURE-state scenarios.

user_input_gates:
  - phase: "Step 8.5 — User Approval Gate"
    description: "Developer approves the generated or updated scenario before SCENARIO_INDEX update and cascade scan run, or provides revision feedback to loop back."
    decision_kind: approval
    required: always

may_invoke:
  - ux-write-canon-concept
```

### 2.7 `.claude/skills/claude-create-skill/SKILL.md` update

Two locations need editing.

**Edit A — Step 4b** (line 89 in current file):

Old:
```
4b. **Contract** (§ Artifact-Establishment Gate): identify the token names this skill will emit in `produces:` and `derived_from:` (short names that identify artifact types — these become the `path:` values in the contract, not raw file paths). Run the gate on each token not yet in `.factory/registry/artifacts.yaml`. Write `.claude/skills/{name}/contract.yaml` only after all tokens are registered.
```

New:
```
4b. **Contract** (§ Artifact-Establishment Gate): identify the token names this skill will emit in `produces:` and `derived_from:` (short names that identify artifact types — these become the `path:` values in the contract, not raw file paths). Run the gate on each token not yet in `.factory/registry/artifacts.yaml`. Write `.claude/skills/{name}/contract.yaml` only after all tokens are registered. If the skill has developer-decision checkpoints, draft each `user_input_gates:` entry and validate it against `.claude/schemas/user_input_gate.yaml` (required fields: `phase`, `description`, `decision_kind`, `required`) before writing.
```

**Edit B — Artifact-Establishment Gate section** (lines 99–108):

Old:
```markdown
## Artifact-Establishment Gate

Before writing any token into a `contract.yaml` (a `produces:`/`derived_from:` `path:` value is a registry token name such as `skill` or `goal`, not a raw file path):

1. Read `.factory/registry/artifacts.yaml` — collect known token names (top-level YAML keys).
2. For each proposed token not in the known set:
   - **Interactive**: propose an entry (token name, path glob, one-line definition); developer ratifies / renames to existing / rejects; append to `artifacts.yaml` only on ratification; refuse duplicate or alias.
   - **Automated** (`$CLAUDE_AUTOMATED_MODE=1`): write `automation/pending_feedback/<TASK_ID>/question.md` (include token name, suggested path glob, definition); copy `automation/pending_feedback/TEMPLATE_answer.md`; stop — never auto-append.
3. Proceed only when every proposed token exists in the registry.
```

New:
```markdown
## Artifact-Establishment Gate

Before writing any token into a `contract.yaml` (a `produces:`/`derived_from:` `path:` value is a registry token name such as `skill` or `goal`, not a raw file path):

1. Read `.factory/registry/artifacts.yaml` — collect known token names (top-level YAML keys).
2. For each proposed token not in the known set:
   - **Interactive**: propose an entry (token name, path glob, one-line definition); developer ratifies / renames to existing / rejects; append to `artifacts.yaml` only on ratification; refuse duplicate or alias.
   - **Automated** (`$CLAUDE_AUTOMATED_MODE=1`): write `automation/pending_feedback/<TASK_ID>/question.md` (include token name, suggested path glob, definition); copy `automation/pending_feedback/TEMPLATE_answer.md`; stop — never auto-append.
3. Proceed only when every proposed token exists in the registry.

**`user_input_gates:` entries** (if the skill has developer-decision checkpoints): validate each entry against `.claude/schemas/user_input_gate.yaml` before writing to the contract. Required fields: `phase` (string), `description` (string), `decision_kind` (one of: `approval`, `revision`, `selection`, `path-selection`, `free-text`), `required` (one of: `always`, `conditional`). A malformed entry will be rejected by `check_skill_contracts.py`.
```

### 2.8 `.claude/skills/claude-modify-skill/SKILL.md` update

Two locations need editing, symmetric to 2.7.

**Edit A — Step 4b** (line 24 in current file):

Old:
```
4b. **Contract** (§ Artifact-Establishment Gate): if the change introduces new `produces:` or `derived_from:` tokens, run the gate before updating `.claude/skills/{name}/contract.yaml`. Token names in contract `path:` values must be registry keys (e.g. `skill`), not raw file paths.
```

New:
```
4b. **Contract** (§ Artifact-Establishment Gate): if the change introduces new `produces:` or `derived_from:` tokens, run the gate before updating `.claude/skills/{name}/contract.yaml`. Token names in contract `path:` values must be registry keys (e.g. `skill`), not raw file paths. If the change adds or modifies `user_input_gates:` entries, validate each against `.claude/schemas/user_input_gate.yaml` (required fields: `phase`, `description`, `decision_kind`, `required`) before writing.
```

**Edit B — Artifact-Establishment Gate section** (lines 49–57):

Old:
```markdown
## Artifact-Establishment Gate

Before writing any new token into a `contract.yaml` (a `produces:`/`derived_from:` `path:` value is a registry token name such as `skill` or `goal`, not a raw file path):

1. Read `.factory/registry/artifacts.yaml` — collect known token names (top-level YAML keys).
2. For each proposed token not in the known set:
   - **Interactive**: propose an entry (token name, path glob, one-line definition); developer ratifies / renames to existing / rejects; append to `artifacts.yaml` only on ratification; refuse duplicate or alias.
   - **Automated** (`$CLAUDE_AUTOMATED_MODE=1`): write `automation/pending_feedback/<TASK_ID>/question.md` (include token name, suggested path glob, definition); copy `automation/pending_feedback/TEMPLATE_answer.md`; stop — never auto-append.
3. Proceed only when every proposed token exists in the registry.
```

New:
```markdown
## Artifact-Establishment Gate

Before writing any new token into a `contract.yaml` (a `produces:`/`derived_from:` `path:` value is a registry token name such as `skill` or `goal`, not a raw file path):

1. Read `.factory/registry/artifacts.yaml` — collect known token names (top-level YAML keys).
2. For each proposed token not in the known set:
   - **Interactive**: propose an entry (token name, path glob, one-line definition); developer ratifies / renames to existing / rejects; append to `artifacts.yaml` only on ratification; refuse duplicate or alias.
   - **Automated** (`$CLAUDE_AUTOMATED_MODE=1`): write `automation/pending_feedback/<TASK_ID>/question.md` (include token name, suggested path glob, definition); copy `automation/pending_feedback/TEMPLATE_answer.md`; stop — never auto-append.
3. Proceed only when every proposed token exists in the registry.

**`user_input_gates:` entries** (if the change adds or modifies checkpoints): validate each entry against `.claude/schemas/user_input_gate.yaml` before writing to the contract. Required fields: `phase` (string), `description` (string), `decision_kind` (one of: `approval`, `revision`, `selection`, `path-selection`, `free-text`), `required` (one of: `always`, `conditional`). A malformed entry will be rejected by `check_skill_contracts.py`.
```

---

## Section 3: Gaps, Risks, and Decisions for the Implementer

### 3.1 Schema dialect

The project uses its own "flat YAML with required:/optional: blocks" dialect (REQ-PROC-044 D-2), not full JSON Schema Draft-7. The proposed `user_input_gate.yaml` follows this dialect exactly (see `goal_metadata.yaml`, `scribble_metadata.yaml`, `pending_question.yaml` for confirmation). Do NOT use `$schema:`, `$id:`, or `additionalProperties` — those are JSON Schema keywords.

### 3.2 Agent contracts have different structure

Agent `.contract.yaml` files (e.g., `quality-checker.contract.yaml`) do NOT use the same top-level structure as skill contracts. They use `consumes:` instead of `derived_from:` and may lack `quality_criteria`, `may_invoke`, `side_effects`, etc. The render script handles this correctly (it only reads `user_input_gates:` which is a new additive field). However, `check_skill_contracts.py` only loads `skills_root.glob("*/contract.yaml")` — it does NOT currently check agent contracts. The `check_user_input_gates` extension follows the same scope (skills only). The render script reads BOTH skill and agent contracts — this asymmetry is intentional per the task spec.

### 3.3 No `user_input_gates:` entries exist yet in any contract

As of investigation date, no contract has a `user_input_gates:` key. The two reference implementations (ux-write-persona, ux-write-scenario) are the first instances. Running `render_user_input_gates.py` before adding them will produce a table with zero rows but exit 0 (valid, not a failure).

### 3.4 Agent contract glob pattern

The `collect_agent_contracts` function uses `agents_root.glob("*.contract.yaml")`. This correctly matches the file naming pattern `<agent-name>.contract.yaml`. The stem extraction uses `.replace(".contract", "")` on the stem (which is already `<name>.contract`), yielding just `<name>`. This has been verified against the actual file list.

### 3.5 `check_skill_contracts.py` docstring update

The task spec says "same severity as unresolved `produces:` token". The violation message format must match the existing `"  - {violation}"` pattern — which the proposed implementation does. The docstring update to add rule 7 is important for the reader but does not affect runtime behavior.

### 3.6 Ordering of registry append

The predecessor task (TASK-PROC-041-04-03) has already completed and added `feedback-checkpoint` to the registry. There are no registry conflicts. The `user-input-gate` token append is clean.

### 3.7 `render_user_input_gates.py` output file

The script writes to `requirements_tasks/STATUS.user_input_gates.md`. This path follows the `STATUS.*` naming convention used by `STATUS.md` and `STATUS.factory_map.html`. The path is NOT added to the `artifacts.yaml` registry (it is a generated file, not a contract-level artifact type). If the project wants to register the output file as a token later, that is a separate concern.

### 3.8 Python quality gates

The new script must pass all five Python gates (G1: ruff, G2: mypy, G3: pytest, G4: no hand-rolled YAML, G5: print() discipline). The proposed code:
- Uses `yaml.safe_load` (not hand-rolled YAML parsing — passes G4)
- Uses `print()` only for the final status line and violations (acceptable — passes G5; diagnostic-only output with no production conditionals)
- All type annotations are explicit — should pass mypy
- No external dependencies beyond `yaml` (already present in the dev environment)

The implementer should run `scripts/quality/check_python_gates.sh` after writing the file.

### 3.9 `SKILL.md` edit token-efficiency constraint

`claude-create-skill` and `claude-modify-skill` are token-sensitive skill files. The proposed additions to step 4b and the Artifact-Establishment Gate section are concise (one sentence for 4b, one paragraph for the gate section). The additions follow the existing terse imperative style. The total body length remains under 60 lines for `claude-modify-skill` (57 lines currently + 5 net new lines = within budget). `claude-create-skill` is already over 60 lines (108 lines); the guideline says "cut prose — never cut decisions," so the addition is justified.

### 3.10 `check_skill_contracts.py` docstring line count

The current docstring for `check_skill_contracts.py` references 6 numbered checks. The implementer must update both the numbered list in the docstring AND the `run_checks` call site. Both are specified above. Do not forget the docstring update or the linter may flag it as inconsistent documentation.
