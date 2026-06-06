"""Task ranking — project-agnostic sorting and next-item detection."""

# tier: B  # reusable library; imported by task_ordering package __init__

from pathlib import Path
from typing import Any, Optional, cast

from .classifier import classify_layer
from .defaults import EXCLUDED_STATUSES, make_sort_key, parse_semver
from .dependencies import is_blocked
from .rules import Rules, load_rules

_PROJECT_ROOT = Path(__file__).parent.parent.parent


def _compute_special_flags_weight(task: dict[str, Any], rules: Rules) -> int:
    """Sum weights of all matching special_flags entries from the rule file."""
    total = 0
    for flag_def in rules.special_flags:
        weight = flag_def.get("weight")
        if weight is None:
            continue
        flag_name = flag_def.get("flag")
        flag_value = flag_def.get("value")
        if flag_name is None:
            continue
        task_value = task.get(flag_name)
        if flag_value is True:
            if bool(task_value):
                total += weight
        else:
            if str(task_value) == str(flag_value):
                total += weight
    return total


def _layer_intra_type_rank(task: dict[str, Any], layer_name: str) -> int:
    """0 for explore, 1 for impl/bugfix — only within layers that mix both task types."""
    applicable_layers = {"factory_process", "requirement_exploration"}
    if layer_name not in applicable_layers:
        return 0
    return 0 if task.get("type") == "explore" else 1


def _enrich_tasks(tasks: list[dict[str, Any]], rules: Rules) -> None:
    """Annotate each task dict with layer classification and ranking signal values."""
    layer_order_map = {layer["name"]: layer.get("order", 999) for layer in rules.layers}
    for task in tasks:
        # Why: glob patterns in the rule file are relative to project root, but task
        # paths loaded from next_tasks.py are absolute. Convert before classifying.
        abs_path = Path(task.get("path", ""))
        try:
            rel_path = str(abs_path.relative_to(_PROJECT_ROOT)).replace("\\", "/")
        except ValueError:
            rel_path = str(abs_path).replace("\\", "/")
        classify_task = {**task, "path": rel_path}
        layer_name = classify_layer(classify_task, rules)
        order = layer_order_map.get(layer_name, 999)
        task["_layer"] = {"name": layer_name, "order": order}
        task["_special_flags_weight"] = _compute_special_flags_weight(task, rules)
        task["_layer_intra_type_rank"] = _layer_intra_type_rank(task, layer_name)


def _requirements_in_progress(tasks: list[dict[Any, Any]], release: Optional[str]) -> set[str]:
    if not release:
        return set()
    return {
        t["parent_requirement"]
        for t in tasks
        if t["target_release"] == release and t["status"] == "completed" and t["parent_requirement"]
    }


def _requirements_in_progress_by_package(tasks: list[dict[Any, Any]], package: Optional[str]) -> set[str]:
    if not package:
        return set()
    return {
        t["parent_requirement"]
        for t in tasks
        if t.get("target_package") == package and t["status"] == "completed" and t["parent_requirement"]
    }


def find_next_release(
    tasks: list[dict[Any, Any]], completed_ids: set[str], known_ids: set[str]
) -> Optional[str]:
    """Lowest semver release that still has at least one open, non-blocked task."""
    releases_with_open = {
        t["target_release"]
        for t in tasks
        if t["status"] not in EXCLUDED_STATUSES
        and not is_blocked(t, completed_ids, known_ids)
        and t["target_release"]
    }
    if not releases_with_open:
        return None
    return cast("str | None", min(releases_with_open, key=lambda v: parse_semver(v)))


def find_next_package(
    tasks: list[dict[Any, Any]],
    completed_ids: set[str],
    known_ids: set[str],
    backlog_packages: list[dict[Any, Any]],
) -> Optional[str]:
    """Lowest-versioned package that still has at least one open, non-blocked task.

    # Why: Falls back to release-based ranking when no target_package data exists.
    # Transition period — tasks migrated at different times, mixed-field state is normal.
    # Source: requirements_tasks/process/AI_rules/requirements_management/release_version_management/tasks/2026-03-26_impl_update-skills-and-scripts/plans_and_protocols/2026-03-26_01_plan_package-model-migration.md
    """
    packages_with_open = {
        t["target_package"]
        for t in tasks
        if t["status"] not in EXCLUDED_STATUSES
        and not is_blocked(t, completed_ids, known_ids)
        and t.get("target_package")
    }
    if not packages_with_open:
        return None

    def pkg_sort_key(pkg_id: str) -> tuple[Any, ...]:
        for pkg in backlog_packages:
            if pkg["id"] == pkg_id:
                return (
                    parse_semver(str(pkg.get("version", "999.999.999"))),
                    backlog_packages.index(pkg),
                )
        return ((999, 999, 999), 9999)

    return cast("str | None", min(packages_with_open, key=pkg_sort_key))


def rank_tasks(
    tasks: list[dict[Any, Any]],
    next_release: Optional[str],
    completed_ids: set[str],
    known_ids: set[str],
    rules: Optional[Rules] = None,
) -> list[dict[Any, Any]]:
    """Return eligible tasks sorted by priority rules (release-based)."""
    if rules is None:
        rules = load_rules()
    _enrich_tasks(tasks, rules)
    reqs_active = _requirements_in_progress(tasks, next_release)
    eligible = [
        t for t in tasks
        if t["status"] not in EXCLUDED_STATUSES and not is_blocked(t, completed_ids, known_ids)
    ]
    return sorted(eligible, key=make_sort_key(next_release, "target_release", reqs_active))


def rank_tasks_by_package(
    tasks: list[dict[Any, Any]],
    next_package: Optional[str],
    completed_ids: set[str],
    known_ids: set[str],
    rules: Optional[Rules] = None,
) -> list[dict[Any, Any]]:
    """Return eligible tasks sorted by priority rules (package-based)."""
    if rules is None:
        rules = load_rules()
    _enrich_tasks(tasks, rules)
    reqs_active = _requirements_in_progress_by_package(tasks, next_package)
    eligible = [
        t for t in tasks
        if t["status"] not in EXCLUDED_STATUSES and not is_blocked(t, completed_ids, known_ids)
    ]
    return sorted(eligible, key=make_sort_key(next_package, "target_package", reqs_active))
