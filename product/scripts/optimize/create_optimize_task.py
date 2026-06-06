#!/usr/bin/env python3
"""Create an auto-blocked claude-optimize improvement task (REQ-PROC-006 IMPL-D).

Single chokepoint through which the claude-optimize skill produces improvement
tasks. Two non-removable invariants live here:

* G-INV-1 (REQ-PROC-006 AC-04) — every produced ``goal.md`` carries
  ``awaiting: ["user-unblock"]``. The value is a hard-coded literal at one
  call site (see ``_render_frontmatter``); no flag, env var, or branch can
  produce an unblocked task.
* Write-Surface Deny-List (REQ-PROC-006 AC-10 / SEC-04) — a produced task
  whose ``target_path`` matches a deny-list entry is rejected with a clear
  message before any file is written. Glob entries are supported via
  ``fnmatch`` so nested files under ``scripts/quality/**`` are caught.

Inputs:
  --event <path>             Optional JSON event file emitted by a monitor
                             (see scripts/optimize/run_monitors.py). Its
                             ``event_type``, ``confidence`` and ``fingerprint``
                             populate ``source_event:`` in the produced goal.md.
  --task-dir <dir>           Destination folder (created if missing). The
                             produced file is ``<task-dir>/goal.md``.
  --task-id <id>             Task ID for the YAML frontmatter (required).
  --target-path <path>       File the produced task proposes to modify
                             (subject to deny-list).
  --optimization-target ...  One of skill_body | skill_description |
                             doc_guideline | ordering_rule | hook | script
                             (REQ-PROC-006 SEC-02).
  --optimization-dimension . One of bugfix | alignment | latency |
                             token_cost | safety | clarity |
                             trigger_accuracy | trigger_precision |
                             layer_order | priority_signal | dependency.
  --web-research / --no-web-research
                             Whether the produced task should perform web
                             research (REQ-PROC-006 SEC-03 heuristics).
  --web-research-query <q>   Focused question — required iff --web-research.
  --web-research-reason <r>  One-line justification for the recommendation.
  --objective <text>         One-line objective shown in the goal body.
  --scope <text>             Optional in-scope description.

Output:
  stdout — the absolute path of the written goal.md on success.
  stderr — deny-list rejection messages naming the matched pattern.

Exit codes:
  0  goal.md written
  2  deny-list rejected the target_path (no file written)
  3  invalid arguments (missing required field, event file unreadable, etc.)
"""

# tier: C  # one-shot CLI, no imported callers, minimal enforcement required

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# REQ-PROC-006 SEC-04 minimum write-surface deny-list. Patterns are matched
# with fnmatch — literal entries match exactly, glob entries (containing
# ``*``, ``?`` or ``[``) match nested files. Defense-in-depth on top of
# G-INV-1; periodic human review is expected.
DENY_LIST: tuple[str, ...] = (
    ".claude/skills/claude-optimize/SKILL.md",
    ".claude/skills/verify-quality/SKILL.md",
    ".claude/skills/task-complete/SKILL.md",
    ".claude/skills/claude-modify-skill/SKILL.md",
    "scripts/quality/**",
    "analysis_options.yaml",
    ".claude/factory_flows.md",
    ".claude/skills/INDEX.md",
)

# Closed sets per REQ-PROC-006 SEC-02 ("Two-Field Taxonomy"). Invalid values
# are rejected at the CLI boundary so produced goal.md files always carry a
# value the downstream router (claude-optimize / claude-modify-skill) understands.
OPTIMIZATION_TARGETS: tuple[str, ...] = (
    "skill_body",
    "skill_description",
    "doc_guideline",
    "ordering_rule",
    "hook",
    "script",
)
OPTIMIZATION_DIMENSIONS: tuple[str, ...] = (
    "bugfix",
    "alignment",
    "latency",
    "token_cost",
    "safety",
    "clarity",
    "trigger_accuracy",
    "trigger_precision",
    "layer_order",
    "priority_signal",
    "dependency",
)

PARENT_REQUIREMENT = "REQ-PROC-006"
EXIT_DENYLIST = 2
EXIT_INVALID = 3


@dataclass(frozen=True)
class SourceEvent:
    """Subset of a monitor event carried into the produced goal.md.

    Only the three structural fields needed to trace a produced task back to
    its triggering signal — payload is intentionally omitted to keep the
    produced goal.md focused on what the developer must review.
    """

    event_type: str
    fingerprint: str
    confidence: str


@dataclass(frozen=True)
class OptimizationApproach:
    """Web-research recommendation block (REQ-PROC-006 SEC-03)."""

    web_research_recommended: bool
    reason: str
    web_research_query: str = ""


@dataclass(frozen=True)
class TaskSpec:
    """Everything needed to produce one goal.md."""

    task_id: str
    target_path: str
    optimization_target: str
    optimization_dimension: str
    approach: OptimizationApproach
    objective: str
    scope: str
    source_event: SourceEvent | None
    created_date: str


def match_deny_list(target_path: str, deny_list: tuple[str, ...] = DENY_LIST) -> str | None:
    """Return the deny-list pattern matched by ``target_path``, or None.

    Matching is case-insensitive: both the target and each pattern are lowered
    before comparison (literal via ``==``, glob via ``fnmatch.fnmatchcase``), and
    the original-cased pattern is returned for messages.

    Why case-insensitive: the protected skill files are ``SKILL.md`` on disk, but
    monitor event payloads have carried both ``SKILL.md`` and ``skill.md``. A
    case-sensitive compare let a case variant slip past the deny-list and defeat
    the AC-10 / SEC-04 defense-in-depth control (TASK-PROC-006-18 / F-1 validation
    finding F-2). No legitimate deny-listed path in this repo differs only by case,
    so normalizing case cannot over-match.
    """
    norm_target = target_path.lower()
    for pattern in deny_list:
        norm_pattern = pattern.lower()
        if any(ch in pattern for ch in "*?["):
            if fnmatch.fnmatchcase(norm_target, norm_pattern):
                return pattern
        elif norm_target == norm_pattern:
            return pattern
    return None


def load_event(path: Path) -> SourceEvent:
    """Read a monitor event JSON file and return its SourceEvent projection.

    Raises ValueError if the file is missing required fields. JSONDecodeError
    and OSError propagate to ``main`` which converts them to exit code 3.
    """
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"event file {path} is not a JSON object")
    missing = [k for k in ("event_type", "fingerprint", "confidence") if k not in data]
    if missing:
        raise ValueError(f"event file {path} missing fields: {missing}")
    return SourceEvent(
        event_type=str(data["event_type"]),
        fingerprint=str(data["fingerprint"]),
        confidence=str(data["confidence"]),
    )


def _render_frontmatter(spec: TaskSpec) -> str:
    """Render the YAML frontmatter for the produced goal.md.

    G-INV-1 (REQ-PROC-006 AC-04): the literal ``awaiting: ["user-unblock"]``
    below is the single point of truth for the auto-block invariant. There is
    no conditional, no flag, no env var feeding into this line; every code
    path through this script lands on the same literal.
    """
    lines: list[str] = [
        "---",
        f"task_id: {spec.task_id}",
        "type: impl",
        f"parent_requirement: {PARENT_REQUIREMENT}",
        "status: pending",
        f"created: {spec.created_date}",
        # G-INV-1 (REQ-PROC-006 AC-04): hard-coded literal — never derived
        # from input. See module docstring "Two non-removable invariants".
        'awaiting: ["user-unblock"]',
        f"target_path: {spec.target_path}",
        f"optimization_target: {spec.optimization_target}",
        f"optimization_dimension: {spec.optimization_dimension}",
    ]
    if spec.source_event is not None:
        lines.extend(
            [
                "source_event:",
                f"  event_type: {spec.source_event.event_type}",
                f"  fingerprint: {spec.source_event.fingerprint}",
                f"  confidence: {spec.source_event.confidence}",
            ]
        )
    lines.append("optimization_approach:")
    lines.append(
        f"  web_research_recommended: {'true' if spec.approach.web_research_recommended else 'false'}"
    )
    if spec.approach.web_research_recommended:
        lines.append(f'  web_research_query: "{spec.approach.web_research_query}"')
    lines.append(f'  reason: "{spec.approach.reason}"')
    lines.append("---")
    return "\n".join(lines)


def _render_body(spec: TaskSpec) -> str:
    """Render the markdown body of the produced goal.md."""
    parts: list[str] = [
        f"# Goal: optimize `{spec.target_path}` ({spec.optimization_dimension})",
        "",
        "## Objective",
        "",
        spec.objective,
        "",
        "## Source",
        "",
        f"Produced by claude-optimize ({PARENT_REQUIREMENT}). This task is",
        "auto-blocked (`awaiting: [\"user-unblock\"]`) — the developer must",
        "review and unblock before any executor picks it up (G-INV-1).",
    ]
    if spec.scope:
        parts.extend(["", "## Scope", "", spec.scope])
    return "\n".join(parts) + "\n"


def render_goal_md(spec: TaskSpec) -> str:
    return _render_frontmatter(spec) + "\n" + _render_body(spec)


def write_goal_md(spec: TaskSpec, task_dir: Path) -> Path:
    """Write goal.md into task_dir (creating it if missing) and return the path."""
    task_dir.mkdir(parents=True, exist_ok=True)
    path = task_dir / "goal.md"
    path.write_text(render_goal_md(spec), encoding="utf-8")
    return path


def _today_local() -> str:
    """Local-date string for the ``created:`` field (timezone rule)."""
    return datetime.now().astimezone().strftime("%Y-%m-%d")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create an auto-blocked claude-optimize improvement task."
    )
    parser.add_argument("--event", type=Path, default=None)
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--target-path", required=True)
    parser.add_argument(
        "--optimization-target", required=True, choices=OPTIMIZATION_TARGETS
    )
    parser.add_argument(
        "--optimization-dimension", required=True, choices=OPTIMIZATION_DIMENSIONS
    )
    parser.add_argument(
        "--web-research", dest="web_research", action="store_true", default=False
    )
    parser.add_argument(
        "--no-web-research", dest="web_research", action="store_false"
    )
    parser.add_argument("--web-research-query", default="")
    parser.add_argument("--web-research-reason", default="")
    parser.add_argument(
        "--objective", default="(no objective provided — fill in before unblocking)"
    )
    parser.add_argument("--scope", default="")
    return parser


def _spec_from_args(args: argparse.Namespace) -> TaskSpec:
    source = load_event(args.event) if args.event is not None else None
    approach = OptimizationApproach(
        web_research_recommended=args.web_research,
        web_research_query=args.web_research_query if args.web_research else "",
        reason=args.web_research_reason
        or ("see SEC-03 heuristics" if args.web_research else "internal change"),
    )
    if args.web_research and not args.web_research_query.strip():
        raise ValueError(
            "--web-research-query is required when --web-research is set"
        )
    return TaskSpec(
        task_id=args.task_id,
        target_path=args.target_path,
        optimization_target=args.optimization_target,
        optimization_dimension=args.optimization_dimension,
        approach=approach,
        objective=args.objective,
        scope=args.scope,
        source_event=source,
        created_date=_today_local(),
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    matched = match_deny_list(args.target_path)
    if matched is not None:
        print(
            f"deny-list: target_path '{args.target_path}' matches pattern '{matched}'",
            file=sys.stderr,
        )
        return EXIT_DENYLIST

    try:
        spec = _spec_from_args(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"invalid input: {exc}", file=sys.stderr)
        return EXIT_INVALID

    path = write_goal_md(spec, args.task_dir)
    print(str(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
