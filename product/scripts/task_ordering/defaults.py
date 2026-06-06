"""Hardcoded ordering defaults — encodes current next_tasks.py sort-key behavior.

TASK-PROC-042-04 will replace these with values loaded from
.claude/task_ordering_rules.yaml once the rules loader exists.
"""

# tier: B  # reusable library; imported by ranker and package __init__

from typing import Any, Callable, Optional, cast

TERMINAL_STATUSES: set[str] = {"completed", "cancelled", "superseded", "deprecated"}
EXCLUDED_STATUSES: set[str] = TERMINAL_STATUSES | {"active"}


def parse_semver(version: str) -> tuple[int, int, int]:
    if not version:
        return (999, 999, 999)
    parts = str(version).split(".")
    try:
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except ValueError:
        return (999, 999, 999)


def priority_score(task: dict[str, Any]) -> int:
    return cast("int", (task["urgency"] * 10) + task["impact"])


def make_sort_key(
    next_item_id: Optional[str],
    item_key: str,
    reqs_active: set[str],
) -> Callable[[dict[str, Any]], tuple[Any, ...]]:
    """Return a sort-key function for ranking tasks against a target package/release."""
    def sort_key(t: dict[str, Any]) -> tuple[Any, ...]:
        special_flags_weight = t.get("_special_flags_weight", 0)
        is_next = 0 if (next_item_id and t.get(item_key) == next_item_id) else 1
        layer_order = t.get("_layer", {}).get("order", 999)
        layer_intra_type_rank = t.get("_layer_intra_type_rank", 0)
        req_not_active = 0 if t["parent_requirement"] in reqs_active else 1
        return (special_flags_weight, is_next, layer_order, layer_intra_type_rank, req_not_active, -priority_score(t))
    return sort_key
