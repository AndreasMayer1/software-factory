#!/usr/bin/env python3
"""Heuristic dependency detector — proposes after: entries for a new task.

CLI: python3 scripts/propose_after.py --path <task-folder-path> --metadata <json-string>
Output: one line per proposal — TASK-ID   reason
Exit 0 in all cases (empty output is not an error).

Runtime: O(N), no LLM calls, no file writes.
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import json
import sys
from pathlib import Path
from typing import Any, cast

# task_ordering/ lives one level up in scripts/, not in scripts/tasks/
sys.path.insert(0, str(Path(__file__).parent.parent))
# next_tasks.py is a sibling in scripts/tasks/
sys.path.insert(0, str(Path(__file__).parent))

from task_ordering import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    TERMINAL_STATUSES,
)
from task_ordering.classifier import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    UNCLASSIFIED,
    classify_layer,
)
from task_ordering.rules import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    Rules,
    load_rules,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# Scope key extraction
# ---------------------------------------------------------------------------

def extract_scope_key(path: str, metadata: dict[str, Any], layer: dict[str, Any]) -> str:
    """Extract scope key value based on layer's scope_key spec.

    Supports two spec forms:
      path_segment[N]   — Nth segment of the forward-slash path
      <field_name>      — frontmatter field lookup
    """
    spec = layer.get("scope_key", "")
    if not spec:
        return ""
    if spec.startswith("path_segment["):
        idx = int(spec[len("path_segment["):-1])
        parts = path.replace("\\", "/").split("/")
        return parts[idx] if idx < len(parts) else ""
    return str(metadata.get(spec, ""))


# ---------------------------------------------------------------------------
# Heuristic applicability + matching
# ---------------------------------------------------------------------------

def _applies_when(heuristic: dict[str, Any], new_layer_name: str) -> bool:
    when = heuristic.get("when") or {}
    layer_cond = when.get("new_task_layer", "any")
    return layer_cond == "any" or str(layer_cond) == new_layer_name


def _reason_for(heuristic: dict[str, Any]) -> str:
    for entry in (heuristic.get("propose") or []):
        if isinstance(entry, dict) and "reason" in entry:
            return str(entry["reason"])
    return cast("str", heuristic.get("name", "dependency"))


def _match_heuristic(
    heuristic: dict[str, Any],
    candidate: dict[str, Any],
    new_task_metadata: dict[str, Any],
    new_layer_name: str,
    new_layer_order: int,
    new_scope: str,
    layers: dict[str, dict[str, Any]],
) -> bool:
    name = heuristic.get("name", "")
    cand_layer_name = candidate.get("_layer_name", UNCLASSIFIED)
    cand_layer_order = candidate.get("_layer_order", 999)

    if name == "same_scope_upstream_layer":
        if cand_layer_order >= new_layer_order:
            return False
        cand_layer_def = layers.get(cand_layer_name, {})
        cand_scope = extract_scope_key(
            candidate.get("_rel_path", candidate.get("path", "")),
            candidate,
            cand_layer_def,
        )
        return bool(cand_scope) and cand_scope == new_scope

    if name == "requirement_then_implementation":
        if cand_layer_name not in ("requirement_exploration", "requirement_derivation"):
            return False
        new_req = str(new_task_metadata.get("parent_requirement", ""))
        return bool(new_req) and candidate.get("parent_requirement") == new_req

    if name == "scribble_then_implementation":
        if cand_layer_name != "ui_design":
            return False
        new_req = str(new_task_metadata.get("parent_requirement", ""))
        return bool(new_req) and candidate.get("parent_requirement") == new_req

    if name == "flow_approval_then_derivation":
        if cand_layer_name != "user_flow":
            return False
        source_gap = str(new_task_metadata.get("source_gap", ""))
        if not source_gap:
            return False
        cand_path = candidate.get("_rel_path", candidate.get("path", ""))
        parts = cand_path.replace("\\", "/").split("/")
        try:
            uf_idx = parts.index("user_flows")
            flow_name = parts[uf_idx + 1] if uf_idx + 1 < len(parts) else ""
        except ValueError:
            flow_name = ""
        return bool(flow_name) and flow_name in source_gap

    if name == "bundle_explores_then_verification":
        if cand_layer_name != "requirement_derivation":
            return False
        bundle = str(new_task_metadata.get("verification_bundle", ""))
        return bool(bundle) and str(candidate.get("verification_bundle", "")) == bundle

    return False


# ---------------------------------------------------------------------------
# Candidate classification
# ---------------------------------------------------------------------------

def _classify_tasks(tasks: list[dict[str, Any]], rules: Rules) -> None:
    """Annotate each task with _layer_name, _layer_order, _rel_path in-place."""
    layer_ord = {layer["name"]: layer.get("order", 999) for layer in rules.layers}
    for task in tasks:
        abs_path = Path(task.get("path", ""))
        try:
            rel_path = str(abs_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        except ValueError:
            rel_path = str(abs_path).replace("\\", "/")
        classify_input = {**task, "path": rel_path}
        layer_name = classify_layer(classify_input, rules)
        task["_layer_name"] = layer_name
        task["_layer_order"] = layer_ord.get(layer_name, 999)
        task["_rel_path"] = rel_path


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def propose_after(
    new_task_path: str,
    new_task_metadata: dict[str, Any],
    rules: Rules,
) -> list[tuple[str, str]]:
    """Return (task_id, reason) pairs to propose as after: entries.

    Does not write any files. O(N) runtime, no LLM calls.
    """
    from next_tasks import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
        load_tasks,
    )

    rel_new_path = _make_rel(new_task_path)
    classify_input = {**new_task_metadata, "path": rel_new_path}
    new_layer_name = classify_layer(classify_input, rules)

    if new_layer_name == UNCLASSIFIED:
        print(
            f"[propose_after] WARNING: path '{new_task_path}' matches no layer; no proposals.",
            file=sys.stderr,
        )
        return []

    layers: dict[str, dict[str, Any]] = {layer["name"]: layer for layer in rules.layers}
    layer_ord: dict[str, int] = {layer["name"]: layer.get("order", 999) for layer in rules.layers}
    new_layer_def = layers.get(new_layer_name, {})
    new_layer_order = layer_ord.get(new_layer_name, 999)
    new_scope = extract_scope_key(rel_new_path, new_task_metadata, new_layer_def)

    all_tasks = load_tasks()
    _classify_tasks(all_tasks, rules)

    proposals: list[tuple[str, str]] = []
    seen_ids: set[str] = set()

    for heuristic in rules.dependency_heuristics:
        if not _applies_when(heuristic, new_layer_name):
            continue
        reason = _reason_for(heuristic)
        for task in all_tasks:
            task_id = str(task.get("task_id", ""))
            if not task_id or task_id in seen_ids:
                continue
            if task.get("status", "") in TERMINAL_STATUSES:
                continue
            try:
                matched = _match_heuristic(
                    heuristic, task, new_task_metadata,
                    new_layer_name, new_layer_order, new_scope,
                    layers,
                )
            except Exception as exc:
                print(
                    f"[propose_after] WARNING: error matching '{heuristic.get('name')}' "
                    f"against '{task_id}': {exc}",
                    file=sys.stderr,
                )
                continue
            if matched:
                proposals.append((task_id, reason))
                seen_ids.add(task_id)

    return proposals


def _make_rel(path: str) -> str:
    """Convert to relative path from project root, or return as-is."""
    abs_path = Path(path)
    try:
        return str(abs_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(abs_path).replace("\\", "/")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Propose after: entries for a new task based on heuristic dependency detection."
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Path to the new task's folder",
    )
    parser.add_argument(
        "--metadata",
        default="{}",
        help="JSON string of the new task's frontmatter fields",
    )
    parser.add_argument(
        "--rules",
        default=None,
        help="Path to custom rules file (defaults to .claude/task_ordering_rules.yaml)",
    )
    args = parser.parse_args()

    try:
        metadata = json.loads(args.metadata)
    except json.JSONDecodeError as exc:
        print(f"[propose_after] ERROR: invalid --metadata JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    rules = load_rules(Path(args.rules) if args.rules else None)
    proposals = propose_after(args.path, metadata, rules)

    for task_id, reason in proposals:
        print(f"{task_id}   {reason}")


if __name__ == "__main__":
    main()
