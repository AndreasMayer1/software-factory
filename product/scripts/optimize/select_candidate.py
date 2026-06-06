#!/usr/bin/env python3
"""Select one candidate event for claude-optimize (REQ-PROC-006 IMPL-E, AC-07).

The claude-optimize skill body calls this helper to pick exactly one event from
`.factory/optimize/events/`. The selection rule is fixed by SEC-01 and AC-07:

* Bugfix candidates strictly first; only fall back to optimization when no
  bugfix candidate exists. No fairness, no rotation, no quota.
* Within each class, priority order: ``repeated_question`` >
  ``skill_change_reverted`` > ``skill_changed_and_used`` > ``periodic``.

The classification table (bugfix vs optimization, and the inferred
``optimization_dimension``) lives in this module so the skill body and the
tests share one source of truth — the SKILL.md table mirrors what this code
returns. This is what AC-07's "fixture-driven test" exercises.

CLI:
    python3 scripts/optimize/select_candidate.py [--events-dir <path>]

Output (stdout, single JSON object):
    {
      "selected":     true | false,
      "outcome":      "candidate" | "no-op",
      "reason":       "<short reason if no-op, else empty string>",
      "event_path":   "<absolute path to selected event JSON, or empty>",
      "event_type":   "<value from selected event, or empty>",
      "fingerprint":  "<value from selected event, or empty>",
      "confidence":   "<value from selected event, or empty>",
      "klass":        "bugfix" | "optimization" | "",
      "dimension":    "<inferred optimization_dimension or empty>",
      "payload":      <object copy of selected event's payload, or {}>
    }

Exit codes:
    0  always (CLI is read-only; the caller inspects ``selected``)
"""

# tier: B  # imported by tests and the SKILL.md CLI shim — shared library

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVENTS_DIR = PROJECT_ROOT / ".factory" / "optimize" / "events"

# SEC-01 monitor taxonomy → SEC-02 priority order (highest first).
# A position that doesn't appear here sorts last (defensive — future event
# types may exist before this table is updated).
PRIORITY_ORDER: tuple[str, ...] = (
    "repeated_question",
    "skill_change_reverted",
    "skill_changed_and_used",
    "periodic",
)

# Klass label for the two-class split used by the bugfix-first rule (AC-07).
Klass = Literal["bugfix", "optimization"]

# Dimensions inferred by the classification table; the full SEC-02 set is
# enforced at the create_optimize_task.py boundary, not here.
DIMENSION_BUGFIX = "bugfix"
DIMENSION_CLARITY = "clarity"
DIMENSION_TRIGGER_ACCURACY = "trigger_accuracy"
DIMENSION_ALIGNMENT = "alignment"
DIMENSION_TOKEN_COST = "token_cost"

# Confidence values from monitor events; used only to disambiguate the
# medium/low branch of skill_changed_and_used in the classification table.
CONFIDENCE_MEDIUM = "medium"

# Reason strings — short, machine-readable, mirrored by SKILL.md Step 6.
REASON_EMPTY_QUEUE = "empty_queue_after_prune"


@dataclass(frozen=True)
class LoadedEvent:
    """One event JSON file loaded from disk.

    ``raw`` keeps the full parsed object so the CLI can echo ``payload``
    back to the caller without re-reading the file. Skipping pre-validation
    of fields beyond what the selector needs keeps this layer thin —
    create_optimize_task.py validates the rest at task-creation time.
    """

    path: Path
    event_type: str
    fingerprint: str
    confidence: str
    raw: dict[str, Any]

    @property
    def payload(self) -> dict[str, Any]:
        p = self.raw.get("payload", {})
        return p if isinstance(p, dict) else {}


def load_events(events_dir: Path = DEFAULT_EVENTS_DIR) -> list[LoadedEvent]:
    """Return every parseable event in ``events_dir`` (corrupt files are skipped).

    Idempotency-pruning (30-day filename cutoff) happens in SKILL.md before this
    helper is invoked; this function only reads what it finds. Unreadable or
    schema-incomplete files are silently dropped — the alternative (crashing
    the post-task-complete path) is worse than skipping a malformed event.
    """
    if not events_dir.is_dir():
        return []
    out: list[LoadedEvent] = []
    for path in sorted(events_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        try:
            out.append(
                LoadedEvent(
                    path=path,
                    event_type=str(data["event_type"]),
                    fingerprint=str(data["fingerprint"]),
                    confidence=str(data["confidence"]),
                    raw=data,
                )
            )
        except KeyError:
            continue
    return out


def classify(event: LoadedEvent) -> tuple[Klass, str]:
    """Map an event to its (klass, optimization_dimension).

    Table mirrors the one in claude-optimize SKILL.md Step 2. Keep both in
    sync — a divergence here is exactly the kind of silent drift the skill's
    "heuristics live in one place" rule (requirements §Developer Guidelines)
    is meant to prevent. If the rules grow, this function grows with them.
    """
    et = event.event_type
    if et == "repeated_question":
        return ("bugfix", DIMENSION_BUGFIX)
    if et == "skill_change_reverted":
        return ("bugfix", DIMENSION_BUGFIX)
    if et == "skill_changed_and_used":
        if bool(event.payload.get("broken", False)):
            return ("bugfix", DIMENSION_BUGFIX)
        if event.confidence == CONFIDENCE_MEDIUM:
            return ("optimization", DIMENSION_CLARITY)
        return ("optimization", DIMENSION_TRIGGER_ACCURACY)
    if et == "high_read_file":
        candidates = event.payload.get("optimization_candidates", [])
        if "cache" in candidates:
            return ("optimization", DIMENSION_TOKEN_COST)
        return ("optimization", DIMENSION_CLARITY)
    # ``periodic`` and any future event type default to optimization/alignment.
    return ("optimization", DIMENSION_ALIGNMENT)


def _priority_rank(event_type: str) -> int:
    """Stable rank for sorting — unknown types sort after the known set."""
    try:
        return PRIORITY_ORDER.index(event_type)
    except ValueError:
        return len(PRIORITY_ORDER)


def select_candidate(events: list[LoadedEvent]) -> LoadedEvent | None:
    """Apply AC-07: bugfix candidates strictly first; then priority order.

    Returns the chosen event or ``None`` when ``events`` is empty.
    """
    if not events:
        return None
    decorated = [(classify(e), _priority_rank(e.event_type), e) for e in events]
    # bugfix < optimization in our ordering — sort by (klass-not-bugfix, rank)
    decorated.sort(key=lambda t: (0 if t[0][0] == "bugfix" else 1, t[1]))
    return decorated[0][2]


def _emit(selected: LoadedEvent | None) -> dict[str, Any]:
    """Build the stdout JSON payload for the CLI."""
    if selected is None:
        return {
            "selected": False,
            "outcome": "no-op",
            "reason": REASON_EMPTY_QUEUE,
            "event_path": "",
            "event_type": "",
            "fingerprint": "",
            "confidence": "",
            "klass": "",
            "dimension": "",
            "payload": {},
        }
    klass, dimension = classify(selected)
    return {
        "selected": True,
        "outcome": "candidate",
        "reason": "",
        "event_path": str(selected.path),
        "event_type": selected.event_type,
        "fingerprint": selected.fingerprint,
        "confidence": selected.confidence,
        "klass": klass,
        "dimension": dimension,
        "payload": selected.payload,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Select one candidate event for claude-optimize."
    )
    parser.add_argument(
        "--events-dir",
        type=Path,
        default=DEFAULT_EVENTS_DIR,
        help="Directory of event JSON files (default: .factory/optimize/events).",
    )
    args = parser.parse_args(argv)
    events = load_events(args.events_dir)
    selected = select_candidate(events)
    json.dump(_emit(selected), sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
