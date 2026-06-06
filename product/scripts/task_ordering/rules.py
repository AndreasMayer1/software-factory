"""Rule file loader — loads .claude/task_ordering_rules.yaml with fallback to hardcoded defaults.

TASK-PROC-042-04: Phase B — load/validate/fallback only.
The loaded Rules object is not yet used for ranking (TASK-PROC-042-05/06).
"""

# tier: B  # reusable library; imported by classifier, ranker, simulate

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# Why: route warnings through stdlib logging (G5 print discipline) so callers
# control sink/handler configuration; default WARNING level keeps current
# stderr-on-warning behavior when the application configures basicConfig.
logger = logging.getLogger(__name__)

SUPPORTED_SCHEMA_VERSION = "1.0"
DEFAULT_RULES_PATH = Path(__file__).parent.parent.parent / ".claude" / "task_ordering_rules.yaml"


@dataclass
class Rules:
    schema_version: str = "1.0"
    layers: list[dict[str, Any]] = field(default_factory=list)
    special_flags: list[dict[str, Any]] = field(default_factory=list)
    ranking_signals: list[dict[str, Any]] = field(default_factory=list)
    dependency_heuristics: list[dict[str, Any]] = field(default_factory=list)
    fallback: dict[str, Any] = field(default_factory=lambda: {
        "unclassified_layer_order": 999,
        "unclassified_task_behavior": "warn_and_rank_last",
        "malformed_rules_behavior": "use_hardcoded_defaults_and_warn",
    })


def hardcoded_rules() -> Rules:
    """Return minimal hardcoded Rules mirroring current next_tasks.py behavior."""
    return Rules()


def _normalize(data: dict[str, Any]) -> Rules:
    return Rules(
        schema_version=str(data.get("schema_version", "1.0")),
        layers=data.get("layers") or [],
        special_flags=data.get("special_flags") or [],
        ranking_signals=data.get("ranking_signals") or [],
        dependency_heuristics=data.get("dependency_heuristics") or [],
        fallback=data.get("fallback") or hardcoded_rules().fallback,
    )


def load_rules(path: Optional[Path] = None) -> Rules:
    """Load ordering rules from a YAML file; fall back to hardcoded defaults on any error."""
    target = Path(path) if path is not None else DEFAULT_RULES_PATH

    if not target.exists():
        logger.warning(
            "[task_ordering] rule file not found at %s; using hardcoded defaults.",
            target,
        )
        return hardcoded_rules()

    try:
        import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope. Deferred so callers that never load rules pay no import cost.

        with open(target, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            logger.warning(
                "[task_ordering] rule file %s is not a YAML mapping; using hardcoded defaults.",
                target,
            )
            return hardcoded_rules()

        schema_version = str(data.get("schema_version", ""))
        if schema_version != SUPPORTED_SCHEMA_VERSION:
            logger.warning(
                "[task_ordering] rule file schema_version '%s' != supported '%s'; "
                "using hardcoded defaults.",
                schema_version,
                SUPPORTED_SCHEMA_VERSION,
            )
            return hardcoded_rules()

        return _normalize(data)

    except Exception as exc:
        logger.warning(
            "[task_ordering] failed to load rule file %s (%s); using hardcoded defaults.",
            target,
            exc,
        )
        return hardcoded_rules()
