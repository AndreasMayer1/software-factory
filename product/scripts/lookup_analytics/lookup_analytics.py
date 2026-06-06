#!/usr/bin/env python3
"""Lookup analytics — reads lookup_log.jsonl files across tasks and reports:

  1. Default (analytics): lookup count per chain class, fallback-to-WebSearch
     rate, cycle x lookup correlation.
  2. --gaps: fallback gap report — technologies not covered by context7.

Usage:
    python3 scripts/lookup_analytics/lookup_analytics.py [--gaps] [--path PATH] [--json]

Output:
    Default mode: human-readable analytics report to stdout.
    --gaps mode: human-readable fallback gap report to stdout.
    --json flag: machine-readable JSON to stdout instead.
    Warnings for unreadable or malformed JSONL lines to stderr.

Exit codes:
    0  report printed successfully (including zero-state "no files found")
    1  fatal error (search path does not exist)

tier: B
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SEARCH_PATH = REPO_ROOT / "requirements_tasks"

DECISION_LOOKED_UP = "looked_up"
DECISION_FALLBACK = "fallback_websearch"


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def find_log_files(root: Path) -> list[Path]:
    """Return all lookup_log.jsonl files under root, sorted by path."""
    return sorted(root.rglob("lookup_log.jsonl"))


def parse_log_file(path: Path) -> tuple[list[dict[str, Any]], int]:
    """Parse a JSONL lookup log. Returns (valid_records, skipped_line_count)."""
    records: list[dict[str, Any]] = []
    skipped = 0
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Warning: cannot read {path}: {exc}", file=sys.stderr)
        return [], 0
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            records.append(json.loads(stripped))
        except json.JSONDecodeError as exc:
            print(
                f"Warning: {path}:{lineno} malformed JSON — {exc}", file=sys.stderr
            )
            skipped += 1
    return records, skipped


def collect_all_records(
    root: Path,
) -> tuple[list[tuple[Path, dict[str, Any]]], list[Path], int]:
    """Find and parse all lookup_log.jsonl under root.

    Returns ([(source_path, record), ...], log_files, total_skipped_lines).
    """
    log_files = find_log_files(root)
    all_pairs: list[tuple[Path, dict[str, Any]]] = []
    total_skipped = 0
    for path in log_files:
        records, skipped = parse_log_file(path)
        for rec in records:
            all_pairs.append((path, rec))
        total_skipped += skipped
    return all_pairs, log_files, total_skipped


# ---------------------------------------------------------------------------
# Analytics report
# ---------------------------------------------------------------------------


def analytics_report(
    pairs: list[tuple[Path, dict[str, Any]]],
) -> dict[str, Any]:
    """Compute analytics from all (source_path, record) pairs."""
    chain_counts: dict[str, int] = {}
    fallback_count = 0
    looked_up_count = 0
    # cycle_num → {task_folder_str → count_of_looked_up_records}
    cycle_task_counts: dict[int, dict[str, int]] = {}

    for source_path, rec in pairs:
        decision = rec.get("decision", "")
        if decision == DECISION_LOOKED_UP:
            chain = rec.get("chain", "unknown")
            chain_counts[chain] = chain_counts.get(chain, 0) + 1
            looked_up_count += 1
            cycle = rec.get("cycle")
            if isinstance(cycle, int):
                # Task identity = the task folder two levels above lookup_log.jsonl
                # (plans_and_protocols/ → task folder)
                task_key = str(source_path.parent.parent)
                if cycle not in cycle_task_counts:
                    cycle_task_counts[cycle] = {}
                cycle_task_counts[cycle][task_key] = (
                    cycle_task_counts[cycle].get(task_key, 0) + 1
                )
        elif decision == DECISION_FALLBACK:
            fallback_count += 1

    fallback_rate = (
        fallback_count / looked_up_count * 100 if looked_up_count else None
    )

    cycle_correlation: dict[int, dict[str, Any]] = {}
    for cycle_num in sorted(cycle_task_counts.keys()):
        counts = list(cycle_task_counts[cycle_num].values())
        total = sum(counts)
        avg = total / len(counts)
        cycle_correlation[cycle_num] = {
            "avg_lookups_per_task": round(avg, 2),
            "task_count": len(counts),
            "total_lookups": total,
        }

    return {
        "looked_up_total": looked_up_count,
        "fallback_total": fallback_count,
        "fallback_rate_pct": (
            round(fallback_rate, 1) if fallback_rate is not None else None
        ),
        "by_chain": dict(
            sorted(chain_counts.items(), key=lambda kv: kv[1], reverse=True)
        ),
        "cycle_correlation": cycle_correlation,
    }


# ---------------------------------------------------------------------------
# Gap report
# ---------------------------------------------------------------------------


def gaps_report(pairs: list[tuple[Path, dict[str, Any]]]) -> dict[str, Any]:
    """Compute fallback gap report: technologies needing WebSearch fallback."""
    tech_counts: dict[str, int] = {}
    tech_examples: dict[str, list[str]] = {}

    for _src, rec in pairs:
        if rec.get("decision") != DECISION_FALLBACK:
            continue
        tech = rec.get("technology", "unknown")
        tech_counts[tech] = tech_counts.get(tech, 0) + 1
        api_surface = rec.get("api_surface", "")
        if tech not in tech_examples:
            tech_examples[tech] = []
        examples = tech_examples[tech]
        if api_surface and api_surface not in examples and len(examples) < 3:
            examples.append(api_surface)

    sorted_techs = sorted(tech_counts.items(), key=lambda kv: kv[1], reverse=True)
    return {
        "fallback_total": sum(tech_counts.values()),
        "technologies": [
            {
                "technology": tech,
                "fallback_count": count,
                "example_surfaces": tech_examples.get(tech, []),
            }
            for tech, count in sorted_techs
        ],
    }


# ---------------------------------------------------------------------------
# Human-readable output
# ---------------------------------------------------------------------------


def print_analytics(
    data: dict[str, Any], log_files: list[Path], skipped: int
) -> None:
    """Print human-readable analytics report."""
    print("Lookup Analytics Report")
    print(f"  Log files found:             {len(log_files)}")
    if skipped:
        print(f"  Malformed lines skipped:     {skipped}")
    print()
    print(f"  Total lookups (looked_up):   {data['looked_up_total']}")
    print(f"  Total fallbacks (websearch):  {data['fallback_total']}")
    rate = data["fallback_rate_pct"]
    rate_str = f"{rate}%" if rate is not None else "n/a"
    print(f"  Fallback rate:               {rate_str}")
    print()

    if data["by_chain"]:
        print("  Lookups by chain class:")
        for chain, count in data["by_chain"].items():
            print(f"    {chain:<36}  {count}")
        print()
    else:
        print("  No lookup records found.\n")

    if data["cycle_correlation"]:
        print("  Cycle x lookup correlation:")
        print(f"    {'Cycle':<8}  {'Avg lookups/task':<20}  {'Tasks':<8}  Total")
        for cycle_num, stats in data["cycle_correlation"].items():
            print(
                f"    {cycle_num:<8}  "
                f"{stats['avg_lookups_per_task']:<20}  "
                f"{stats['task_count']:<8}  "
                f"{stats['total_lookups']}"
            )
    else:
        print("  No cycle data found.")


def print_gaps(
    data: dict[str, Any], log_files: list[Path], skipped: int
) -> None:
    """Print human-readable fallback gap report."""
    print("Fallback Gap Report (technologies not indexed by context7)")
    print(f"  Log files found: {len(log_files)}")
    if skipped:
        print(f"  Malformed lines skipped: {skipped}")
    print()
    print(f"  Total fallback records: {data['fallback_total']}")
    print()

    techs = data["technologies"]
    if not techs:
        print("  No fallback records found — context7 coverage looks complete!")
        return

    print(f"  {'Technology':<44}  {'Fallbacks':<12}  Example API surfaces")
    for entry in techs:
        examples_str = (
            ", ".join(entry["example_surfaces"]) if entry["example_surfaces"] else "(none recorded)"
        )
        print(
            f"  {entry['technology']:<44}  "
            f"{entry['fallback_count']:<12}  "
            f"{examples_str}"
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Lookup analytics — reads lookup_log.jsonl files across tasks."
    )
    parser.add_argument(
        "--gaps",
        action="store_true",
        help="Show fallback gap report (technologies not covered by context7)",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_SEARCH_PATH,
        help="Root path to search for lookup_log.jsonl (default: requirements_tasks/)",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Output as JSON (machine-readable)",
    )
    args = parser.parse_args(argv)

    root: Path = args.path
    if not root.exists():
        print(f"Error: search path does not exist: {root}", file=sys.stderr)
        return 1

    pairs, log_files, skipped = collect_all_records(root)

    if not log_files:
        msg = f"No lookup_log.jsonl files found under {root}."
        if args.as_json:
            print(json.dumps({"message": msg, "log_files_found": 0}))
        else:
            print(msg)
        return 0

    if args.gaps:
        data = gaps_report(pairs)
        if args.as_json:
            data["log_files_found"] = len(log_files)
            print(json.dumps(data, indent=2))
        else:
            print_gaps(data, log_files, skipped)
    else:
        data = analytics_report(pairs)
        if args.as_json:
            data["log_files_found"] = len(log_files)
            print(json.dumps(data, indent=2))
        else:
            print_analytics(data, log_files, skipped)

    return 0


if __name__ == "__main__":
    sys.exit(main())
