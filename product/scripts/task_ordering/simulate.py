#!/usr/bin/env python3
"""
Dry-run CLI: shows how a proposed rule-file change affects backlog ranking.

Usage:
    python3 scripts/task_ordering/simulate.py --proposed-rules <path>
    python3 scripts/task_ordering/simulate.py --proposed-rules <path> --verbose

Exit 0 always (informational, not a gate).

Output:
    Prints a side-by-side comparison of current-rules vs proposed-rules rankings for the backlog to stdout. --verbose adds the score breakdown per task.
"""

# tier: C  # one-shot CLI simulation/validation tool; no in-tree Python imports

import argparse
import copy
import sys
from pathlib import Path
from typing import Any, cast

# Add scripts/ to path for importing next_tasks helpers
_SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from task_ordering import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    find_next_release,
    rank_tasks,
)
from task_ordering.classifier import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    UNCLASSIFIED,
    classify_layer,
)
from task_ordering.rules import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    DEFAULT_RULES_PATH,
    load_rules,
)

TOP_N = 20
SHIFT_THRESHOLD = 5


def _layer_name(task: dict[Any, Any], rules: Any) -> str:
    """Classify *task* under *rules*, converting abs path to repo-relative first."""
    project_root = _SCRIPTS_DIR.parent
    abs_path = Path(task.get("path", ""))
    try:
        rel_path = str(abs_path.relative_to(project_root)).replace("\\", "/")
    except ValueError:
        rel_path = str(abs_path).replace("\\", "/")
    return cast("str", classify_layer({**task, "path": rel_path}, rules))


def _rank(tasks_snapshot: list[Any], rules: Any) -> list[Any]:
    """Return ranked list using *rules*; deep-copies to avoid mutating the snapshot."""
    tasks = copy.deepcopy(tasks_snapshot)
    all_ids = {t["task_id"] for t in tasks}
    completed_ids = {t["task_id"] for t in tasks if t["status"] == "completed"}
    next_release = find_next_release(tasks, completed_ids, all_ids)
    return cast("list[Any]", rank_tasks(tasks, next_release, completed_ids, all_ids, rules=rules))


def _print_row(new_pos_str: str, old_pos_str: str, delta_str: str, flags: str, label: str) -> None:
    print(f"  {new_pos_str:>4}  {old_pos_str:>4}  {delta_str:>5}  {flags:<10}  {label}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulate how a proposed rule-file change affects backlog ranking."
    )
    parser.add_argument(
        "--proposed-rules",
        required=True,
        type=Path,
        metavar="PATH",
        help="Path to the proposed rule file.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Also flag tasks that shift by 1-4 places.",
    )
    parser.add_argument(
        "--current-rules",
        type=Path,
        default=DEFAULT_RULES_PATH,
        help=f"Current rule file (default: {DEFAULT_RULES_PATH})",
    )
    args = parser.parse_args()

    # Import load_tasks from next_tasks (not part of the task_ordering package)
    try:
        import next_tasks as _nt  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    except ImportError:
        print("[simulate] ERROR: cannot import next_tasks — run from project root or scripts/.", file=sys.stderr)
        sys.exit(1)

    current_rules = load_rules(args.current_rules)
    proposed_rules = load_rules(args.proposed_rules)

    tasks = _nt.load_tasks()

    old_ranked = _rank(tasks, current_rules)
    new_ranked = _rank(tasks, proposed_rules)

    old_top = old_ranked[:TOP_N]
    new_top = new_ranked[:TOP_N]

    old_pos = {t["task_id"]: i + 1 for i, t in enumerate(old_ranked)}
    new_pos = {t["task_id"]: i + 1 for i, t in enumerate(new_ranked)}

    # --- header ---
    print(f"\n{'='*72}")
    print(f"  Proposed rules: {args.proposed_rules}")
    print(f"  Top {TOP_N} tasks — old position vs new position")
    print(f"{'='*72}")
    _print_row("NEW", "OLD", "Δ", "FLAGS", "TASK")
    _print_row("---", "---", "-----", "----------", "-" * 50)

    shown_ids: set[Any] = set()
    shifted_total = 0
    unclassified_total = 0

    # --- new top-20 in order ---
    for n_pos, task in enumerate(new_top, 1):
        tid = task["task_id"]
        shown_ids.add(tid)
        o_pos = old_pos.get(tid)

        if o_pos is None:
            delta_str = "  new"
            delta_int = None
        else:
            delta_int = n_pos - o_pos
            delta_str = f"{delta_int:+d}" if delta_int != 0 else "  ─"

        flags = []
        if delta_int is not None and abs(delta_int) >= SHIFT_THRESHOLD:
            flags.append("⚑SHIFT")
            shifted_total += 1
        elif delta_int is not None and abs(delta_int) >= 1 and args.verbose:
            flags.append(f"~{abs(delta_int)}")

        layer = _layer_name(task, proposed_rules)
        if layer == UNCLASSIFIED:
            flags.append("UNCLASS")
            unclassified_total += 1

        old_str = str(o_pos) if o_pos is not None else "-"
        label = f"{tid}: {task['name'][:45]}"
        _print_row(str(n_pos), old_str, delta_str, ",".join(flags), label)

    # --- tasks that fell out of new top-20 ---
    dropped = [t for t in old_top if t["task_id"] not in shown_ids]
    if dropped:
        print(f"  {'─'*68}")
        print(f"  {'':>4}  {'':>4}  {'':>5}  {'':>10}  Dropped out of top {TOP_N}:")
        for task in dropped:
            tid = task["task_id"]
            shown_ids.add(tid)
            o_pos = old_pos[tid]
            n_pos_val = new_pos.get(tid)
            delta_str = f">{TOP_N}" if n_pos_val is not None else "gone"

            flags = []
            if n_pos_val is not None and (n_pos_val - o_pos) >= SHIFT_THRESHOLD:
                flags.append("⚑SHIFT")
                shifted_total += 1

            layer = _layer_name(task, proposed_rules)
            if layer == UNCLASSIFIED:
                flags.append("UNCLASS")
                unclassified_total += 1

            n_str = f">{TOP_N}" if n_pos_val is not None else "-"
            label = f"{tid}: {task['name'][:45]}"
            _print_row(n_str, str(o_pos), delta_str, ",".join(flags), label)

    print(f"{'='*72}")
    print("\n  Summary:")
    print(f"    Tasks shifting ≥{SHIFT_THRESHOLD} places:  {shifted_total}")
    print(f"    Tasks becoming unclassified: {unclassified_total}")
    print()

    sys.exit(0)


if __name__ == "__main__":
    main()
