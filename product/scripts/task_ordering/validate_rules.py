"""CLI: validate the task-ordering rule file for schema correctness.

Usage:
    python3 scripts/task_ordering/validate_rules.py [--rules PATH]

Exit 0 — all checks pass.
Exit 1 — one or more checks failed (errors printed to stderr).

Output:
    Prints one error line per schema violation to stderr (or 'OK' to stdout if the rule file passes all checks).
"""

# tier: C  # one-shot CLI simulation/validation tool; no in-tree Python imports

import argparse
import fnmatch
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
SUPPORTED_SCHEMA_VERSION = "1.0"
REQUIRED_LAYER_FIELDS = {"name", "order", "match"}


def _error(msg: str) -> None:
    print(f"[validate_rules] ERROR: {msg}", file=sys.stderr)


def _warn(msg: str) -> None:
    print(f"[validate_rules] WARNING: {msg}", file=sys.stderr)


def validate(rules_path: Path) -> int:
    """Run all schema checks. Returns number of errors found."""
    errors = 0

    # Load raw YAML so we check structure before normalisation
    try:
        import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope
    except ImportError:
        _error("PyYAML not installed — cannot validate rule file.")
        return 1

    if not rules_path.exists():
        _error(f"Rule file not found: {rules_path}")
        return 1

    with open(rules_path, encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            _error(f"YAML parse error: {exc}")
            return 1

    if not isinstance(data, dict):
        _error("Rule file is not a YAML mapping.")
        return 1

    # 1. Schema version
    schema_version = str(data.get("schema_version", ""))
    if not schema_version:
        _error("Missing required field: schema_version")
        errors += 1
    elif schema_version != SUPPORTED_SCHEMA_VERSION:
        _error(
            f"schema_version '{schema_version}' is not supported "
            f"(expected '{SUPPORTED_SCHEMA_VERSION}')."
        )
        errors += 1

    layers = data.get("layers") or []
    if not isinstance(layers, list):
        _error("`layers` must be a list.")
        return errors + 1

    # 2. Required fields per layer
    for i, layer in enumerate(layers):
        if not isinstance(layer, dict):
            _error(f"Layer #{i} is not a mapping.")
            errors += 1
            continue
        missing = REQUIRED_LAYER_FIELDS - set(layer.keys())
        if missing:
            name = layer.get("name", f"<layer #{i}>")
            _error(f"Layer '{name}' missing required fields: {sorted(missing)}")
            errors += 1

    # 3. Unique layer order values
    order_values: dict[int, str] = {}
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        name = layer.get("name", "<unnamed>")
        order = layer.get("order")
        if order is None:
            continue
        if order in order_values:
            _error(
                f"Duplicate layer order {order}: layers '{order_values[order]}' and '{name}'."
            )
            errors += 1
        else:
            order_values[order] = name

    # 4. Unique layer names
    seen_names: set[str] = set()
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        name = layer.get("name")
        if name is None:
            continue
        if name in seen_names:
            _error(f"Duplicate layer name: '{name}'.")
            errors += 1
        else:
            seen_names.add(name)

    # 5. path_glob sanity — each glob must match at least one goal.md in the repo
    # Search under both requirements_tasks/ and requirements_user_needs/ since
    # some layers (persona, scenario, user_flow) live outside requirements_tasks/.
    all_task_paths: list[str] = []
    for search_root in ("requirements_tasks", "requirements_user_needs"):
        root = REPO_ROOT / search_root
        if root.exists():
            all_task_paths.extend(
                str(p.relative_to(REPO_ROOT)).replace("\\", "/")
                for p in root.rglob("goal.md")
            )

    for layer in layers:
        if not isinstance(layer, dict):
            continue
        layer_name = layer.get("name", "<unnamed>")
        for match_rule in layer.get("match") or []:
            if not isinstance(match_rule, dict):
                continue
            glob = match_rule.get("path_glob")
            if not glob:
                continue
            if not any(fnmatch.fnmatch(p, glob) for p in all_task_paths):
                _warn(
                    f"Layer '{layer_name}': path_glob '{glob}' matches zero "
                    "goal.md files in the repo (sparsity warning — layer may be unused)."
                )
                # warn only — not an error (layer may be for future use)

    # 6. Dependency cycle check — consumes references must name existing layers
    layer_names = {layer["name"] for layer in layers if isinstance(layer, dict) and "name" in layer}
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        name = layer.get("name", "<unnamed>")
        for consumed in layer.get("consumes") or []:
            if consumed not in layer_names:
                _error(
                    f"Layer '{name}' consumes unknown layer '{consumed}'."
                )
                errors += 1

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the task-ordering rule file schema."
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=REPO_ROOT / ".claude" / "task_ordering_rules.yaml",
        help="Path to the rule file (default: .claude/task_ordering_rules.yaml)",
    )
    args = parser.parse_args()

    error_count = validate(args.rules)
    if error_count == 0:
        print(f"[validate_rules] OK — rule file passes all schema checks: {args.rules}")
        sys.exit(0)
    else:
        print(
            f"[validate_rules] FAILED — {error_count} error(s) found in: {args.rules}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
