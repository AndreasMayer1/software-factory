"""Layer classifier — maps a task (path + frontmatter) to its declared layer.

Uses the Rules object from rules.py. Evaluation is first-match-wins in
declaration order (YAML layer list order, not the numeric `order` field).
"""

# tier: B  # reusable library; imported by ranker, simulate, propose_after

from fnmatch import fnmatch
from typing import Any, cast

from .rules import Rules

UNCLASSIFIED = "__unclassified__"


def classify_layer(task: dict[str, Any], rules: Rules) -> str:
    """Return the layer name for *task*, or UNCLASSIFIED if no rule matches.

    *task* must have a ``path`` key (str or Path) pointing to the goal.md.
    Additional keys are treated as frontmatter fields (type, scope_description, …).
    """
    path = _normalize_path(str(task.get("path", "")))

    for layer in rules.layers:
        for match_rule in layer.get("match") or []:
            if _matches(path, task, match_rule):
                return cast("str", layer["name"])

    return UNCLASSIFIED


def _normalize_path(path: str) -> str:
    """Convert backslashes to forward slashes for Windows compatibility."""
    return path.replace("\\", "/")


def _matches(path: str, task: dict[str, Any], rule: dict[str, Any]) -> bool:
    """Return True if *task* satisfies all predicates in *rule*."""
    if "path_glob" in rule:
        glob = _normalize_path(rule["path_glob"])
        if not fnmatch(path, glob):
            return False

    if "frontmatter" in rule:
        for key, expected in rule["frontmatter"].items():
            if str(task.get(key, "")) != str(expected):
                return False

    if "scope_description_contains" in rule:
        scope_desc = str(task.get("scope_description", ""))
        needles = rule["scope_description_contains"]
        if not any(needle in scope_desc for needle in needles):
            return False

    return True
