#!/usr/bin/env python3
"""Produce a 1-page statistics summary of a task_creation_plan.md.

Used by release-begin-impl Phase 5 for the user gate before implementation begins.

Usage:
    python3 scripts/summarize_plan.py --plan PLAN_PATH [--format md|text]

Exit codes:
    0  success — summary written to stdout
    1  file not found or parse error

Output:
    Prints a one-page summary (counts, ranges, package list) in the requested format (md/text) to stdout.
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# Allow importing parse_task_creation_plan from the same scripts/ directory
sys.path.insert(0, str(Path(__file__).parent))
from parse_task_creation_plan import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    PlanArchivedError,
    PlanParseError,
    get_execution_order,
    parse_plan,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent

EFFORT_ORDER = ["XS", "S", "M", "L", "XL"]
EFFORT_DAYS = {"XS": 0.5, "S": 1, "M": 2, "L": 4, "XL": 8}
MAX_TASK_NAME_LEN = 40


# ---------------------------------------------------------------------------
# DAG depth computation for after-chain density
# ---------------------------------------------------------------------------

def _build_dag(packages: list[dict[str, Any]]) -> tuple[dict[str, list[str]], list[str]]:
    """Build a DAG from intra-plan after: references.

    Returns (adjacency: {node -> [deps]}, all_nodes).
    Nodes are task entry identifiers like "PackageName:N".
    """
    # Map tasks to stable node IDs: "{pkg_id}:{_entry_index}"
    all_nodes: list[str] = []
    node_by_ref: dict[str, str] = {}  # pkg_name -> [node_ids]

    for pkg in packages:
        pkg_id = pkg["id"]
        for task in pkg["tasks"]:
            idx = task.get("_entry_index", 1)
            node_id = f"{pkg_id}:{idx}"
            all_nodes.append(node_id)
            # Also register by position for #pkg:Task N refs
            ref_key = f"#{pkg_id}:Task {idx}"
            node_by_ref[ref_key] = node_id

    adjacency: dict[str, list[str]] = {n: [] for n in all_nodes}

    for pkg in packages:
        pkg_id = pkg["id"]
        for task in pkg["tasks"]:
            idx = task.get("_entry_index", 1)
            node_id = f"{pkg_id}:{idx}"
            for after_ref in task.get("after", []):
                ref_str = str(after_ref).strip()
                if ref_str in node_by_ref:
                    dep_node = node_by_ref[ref_str]
                    adjacency[node_id].append(dep_node)
                # else: real TASK-ID reference or unresolvable — skip for depth calc

    return adjacency, all_nodes


def _compute_max_depth(adjacency: dict[str, list[str]], nodes: list[str]) -> int:
    """Compute longest path in the DAG (max chain depth).

    Uses memoized DFS. Returns 1 for a single node with no deps.
    Handles cycles by tracking visited nodes.
    """
    memo: dict[str, int] = {}

    def dfs(node: str, visiting: set[str]) -> int:
        if node in memo:
            return memo[node]
        if node in visiting:
            # Cycle detected — return 0 to avoid infinite recursion
            return 0
        visiting = visiting | {node}
        deps = adjacency.get(node, [])
        result = 1 if not deps else 1 + max(dfs(dep, visiting) for dep in deps)
        memo[node] = result
        return result

    if not nodes:
        return 0
    return max(dfs(n, set()) for n in nodes)


# ---------------------------------------------------------------------------
# Summary computation
# ---------------------------------------------------------------------------

def compute_summary(plan: dict[str, Any]) -> dict[str, Any]:
    """Compute all statistics from a parsed plan."""
    packages = plan.get("packages", [])
    fm = plan.get("frontmatter", {})
    execution_order = get_execution_order(plan)

    all_tasks: list[dict[str, Any]] = []
    for pkg in packages:
        for task in pkg["tasks"]:
            all_tasks.append({**task, "_pkg_id": pkg["id"]})

    # Task type counts
    type_counts = Counter(str(t.get("task_type", "implement")).lower() for t in all_tasks)

    # Effort distribution
    effort_counts: dict[str, list[str]] = {e: [] for e in EFFORT_ORDER}
    unknown_effort: list[str] = []
    for t in all_tasks:
        effort = str(t.get("effort", "") or "").strip()
        name = str(t.get("task_name", "") or "")[:MAX_TASK_NAME_LEN]
        if effort in EFFORT_ORDER:
            effort_counts[effort].append(name)
        else:
            unknown_effort.append(name)

    total_days = sum(
        EFFORT_DAYS.get(str(t.get("effort", "") or "").strip(), 0)
        for t in all_tasks
    )

    # Layer distribution
    layer_counts = Counter(str(t.get("layer", "unspecified") or "unspecified").lower() for t in all_tasks)

    # Opus recommendations
    opus_tasks = [t for t in all_tasks if t.get("opus_recommended")]

    # Verify tasks
    verify_tasks = [t for t in all_tasks if str(t.get("task_type", "")).lower() == "verify"]

    # After-chain statistics
    tasks_with_after = sum(1 for t in all_tasks if t.get("after"))
    adjacency, nodes = _build_dag(packages)
    max_depth = _compute_max_depth(adjacency, nodes)

    # Per-package summary (respecting execution order if available)
    pkg_map = {pkg["id"]: pkg for pkg in packages}
    if execution_order:
        ordered_pkg_ids = execution_order
        # Add any packages not in the execution order at the end
        remaining = [pid for pid in pkg_map if pid not in set(execution_order)]
        ordered_pkg_ids = ordered_pkg_ids + remaining
    else:
        ordered_pkg_ids = [pkg["id"] for pkg in packages]

    pkg_summaries: list[dict[str, Any]] = []
    for pkg_id in ordered_pkg_ids:
        pkg = pkg_map.get(pkg_id)
        if not pkg:
            continue
        efforts = [
            str(t.get("effort", "?") or "?").strip()
            for t in pkg["tasks"]
        ]
        pkg_summaries.append({
            "id": pkg_id,
            "task_count": len(pkg["tasks"]),
            "efforts": efforts,
        })

    return {
        "frontmatter": fm,
        "package_count": len(packages),
        "total_tasks": len(all_tasks),
        "type_counts": dict(type_counts),
        "effort_counts": effort_counts,
        "unknown_effort": unknown_effort,
        "total_days": total_days,
        "layer_counts": dict(layer_counts),
        "opus_tasks": [str(t.get("task_name", ""))[:MAX_TASK_NAME_LEN] for t in opus_tasks],
        "verify_tasks": verify_tasks,
        "tasks_with_after": tasks_with_after,
        "max_depth": max_depth,
        "pkg_summaries": pkg_summaries,
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_md(s: dict[str, Any]) -> str:
    """Render summary as markdown."""
    fm = s["frontmatter"]
    plan_id = str(fm.get("plan_id", "unknown") or "unknown")
    status = str(fm.get("status", "unknown") or "unknown")
    created = str(fm.get("created", "") or fm.get("date", "") or "")
    release = str(fm.get("release", "") or "")

    lines: list[str] = []
    lines.append(f"# Task Creation Plan Summary: Release {release}")
    meta_parts = [f"Plan ID: {plan_id}", f"Status: {status}"]
    if created:
        meta_parts.append(f"Created: {created}")
    lines.append(" | ".join(meta_parts))
    lines.append("")

    # Coverage
    type_str = ", ".join(
        f"{t}={c}" for t, c in sorted(s["type_counts"].items()) if c > 0
    )
    lines.append("## Coverage")
    lines.append(f"- Packages covered: {s['package_count']}")
    lines.append(f"- Total tasks: {s['total_tasks']}")
    lines.append(f"- Task types: {type_str or 'n/a'}")
    lines.append("")

    # Effort distribution
    lines.append("## Effort Distribution")
    lines.append("| Effort | Count | Tasks |")
    lines.append("|--------|-------|-------|")
    for e in EFFORT_ORDER:
        task_list = s["effort_counts"].get(e, [])
        count = len(task_list)
        names = ", ".join(task_list[:3])
        if len(task_list) > 3:
            names += f" (+{len(task_list)-3} more)"
        lines.append(f"| {e:<6} | {count:<5} | {names} |")
    if s["unknown_effort"]:
        lines.append(f"| ?      | {len(s['unknown_effort']):<5} | {', '.join(s['unknown_effort'][:3])} |")
    lines.append(f"\nEstimated total: {s['total_days']:.1f} days")
    lines.append("")

    # By layer
    lines.append("## By Layer")
    for layer, count in sorted(s["layer_counts"].items()):
        lines.append(f"- {layer}: {count} task{'s' if count != 1 else ''}")
    lines.append("")

    # Packages in execution order
    lines.append("## Packages (Execution Order)")
    for i, pkg in enumerate(s["pkg_summaries"], 1):
        efforts_str = ", ".join(pkg["efforts"])
        lines.append(f"{i}. {pkg['id']} — {pkg['task_count']} task{'s' if pkg['task_count'] != 1 else ''} ({efforts_str})")
    lines.append("")

    # Flags
    lines.append("## Flags")
    opus_count = len(s["opus_tasks"])
    if opus_count:
        names = ", ".join(s["opus_tasks"][:3])
        if opus_count > 3:
            names += f" (+{opus_count-3} more)"
        lines.append(f"- opus_recommended: {opus_count} task{'s' if opus_count != 1 else ''} ({names})")
    else:
        lines.append("- opus_recommended: 0 tasks")
    verify_count = len(s["verify_tasks"])
    lines.append(f"- verify tasks: {verify_count} (already-implemented ACs)")
    lines.append("")

    # After-chain density
    total = s["total_tasks"]
    with_after = s["tasks_with_after"]
    pct = round(100 * with_after / total) if total else 0
    lines.append("## After-Chain Density")
    lines.append(f"- Tasks with after dependencies: {with_after} / {total} ({pct}%)")
    lines.append(f"- Max chain depth: {s['max_depth']}")

    return "\n".join(lines)


def render_text(s: dict[str, Any]) -> str:
    """Render summary as plain text."""
    fm = s["frontmatter"]
    release = str(fm.get("release", "") or "")
    plan_id = str(fm.get("plan_id", "unknown") or "unknown")

    lines: list[str] = []
    lines.append(f"Plan Summary: Release {release}  [{plan_id}]")
    lines.append("=" * 50)
    lines.append(f"Packages: {s['package_count']}  Tasks: {s['total_tasks']}  "
                 f"Est. {s['total_days']:.1f} days")
    lines.append("")
    lines.append("Effort: " + "  ".join(
        f"{e}:{len(s['effort_counts'].get(e, []))}" for e in EFFORT_ORDER
    ))
    lines.append("")
    lines.append("Layers: " + "  ".join(f"{k}:{v}" for k, v in sorted(s["layer_counts"].items())))
    lines.append("")
    lines.append("Packages:")
    for i, pkg in enumerate(s["pkg_summaries"], 1):
        efforts_str = ", ".join(pkg["efforts"])
        lines.append(f"  {i}. {pkg['id']} ({pkg['task_count']} tasks: {efforts_str})")
    lines.append("")
    total = s["total_tasks"]
    with_after = s["tasks_with_after"]
    pct = round(100 * with_after / total) if total else 0
    lines.append(f"After-chains: {with_after}/{total} ({pct}%)  Max depth: {s['max_depth']}")
    lines.append(f"Opus tasks: {len(s['opus_tasks'])}  Verify tasks: {len(s['verify_tasks'])}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Produce a 1-page statistics summary of task_creation_plan.md"
    )
    parser.add_argument("--plan", required=True, metavar="PLAN_PATH",
                        help="Path to task_creation_plan.md")
    parser.add_argument("--format", choices=["md", "text"], default="md",
                        help="Output format (default: md)")
    args = parser.parse_args()

    try:
        plan = parse_plan(args.plan)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except (PlanParseError, PlanArchivedError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    summary = compute_summary(plan)

    if args.format == "text":
        print(render_text(summary))
    else:
        print(render_md(summary))

    sys.exit(0)


if __name__ == "__main__":
    main()
