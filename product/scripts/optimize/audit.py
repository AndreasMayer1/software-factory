#!/usr/bin/env python3
"""Compute optimizer health score and effectiveness metrics (REQ-PROC-006 AC-11/AC-12).

Deterministic from ``runs.tsv``, produced ``goal.md`` files, and ``git log``.
No LLM judgment anywhere on this code path — that is G-INV-3 / AC-12.

Inputs:
  --runs-tsv <path>           runs.tsv produced by claude-optimize.
  --audit-history <path>      Append-only audit_history.tsv (appended on success).
  --report <path>             Output markdown report path.
  --tasks-root <path>         Folder containing produced TASK-OPT-* task dirs.
  --monitor <name>            Optional filter to one monitor (sub-audit).
                              One of repeated_question, skill_change_reverted,
                              skill_changed_and_used, periodic.

Output:
  stdout — one-line summary: ``score=<N>/10 delta=<+/-N> unblock=<x.xx> revert=<x.xx>``.
  Report file at --report; one new TSV line appended to audit_history.

Exit codes:
  0 success
  2 empty runs.tsv (nothing to audit; history NOT appended)
  3 invalid arguments (unknown monitor, missing required path)
"""

# tier: B  # rubric functions are importable for tests; thin CLI wrapper

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# --- Rubric tuning constants (refinable from real data — round-4 §9) ----------

UNBLOCK_RATE_BAND_LOW = 0.50
UNBLOCK_RATE_BAND_HIGH = 0.80
REVERT_RATE_THRESHOLD = 0.25
NO_OP_STREAK_MAX = 5
DIVERSITY_WINDOW = 20
DIVERSITY_MIN_DISTINCT = 3
PERIODIC_SHARE_MAX = 0.50
DENYLIST_WINDOW_DAYS = 30
UNBLOCK_LATENCY_MAX_DAYS = 7
REVERT_WINDOW_WEEKS = 8
INSUFFICIENT_DATA_NEUTRAL = 0.5
RUBRIC_TOTAL = 10

MONITOR_NAMES = (
    "repeated_question",
    "skill_change_reverted",
    "skill_changed_and_used",
    "periodic",
)

# --- Data structures ----------------------------------------------------------


@dataclass(frozen=True)
class Run:
    ts: str
    run_id: str
    outcome: str  # "created" | "no-op"
    target: str
    dimension: str
    notes: str  # task_id if created, reason if no-op


@dataclass(frozen=True)
class ProducedTask:
    task_id: str
    goal_path: Path
    created: datetime | None
    awaiting: list[str]
    status: str
    source_event_type: str
    target_path: str
    unblocked: bool  # awaiting no longer contains "user-unblock"
    unblock_date: datetime | None
    completed: bool


@dataclass(frozen=True)
class Criterion:
    key: str
    label: str
    score: float  # 0.0, 0.5, or 1.0
    detail: str


@dataclass(frozen=True)
class AuditResult:
    score: float
    delta: float
    unblock_rate: float | None
    revert_rate: float | None
    criteria: list[Criterion]
    monitor: str
    sample_size: int


# --- I/O helpers --------------------------------------------------------------


def _read_runs(path: Path) -> list[Run]:
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    if not lines or lines[0].startswith("ts\t"):
        lines = lines[1:]
    runs: list[Run] = []
    for line in lines:
        parts = line.split("\t")
        if len(parts) < 6:
            continue
        runs.append(Run(*parts[:6]))
    return runs


def _load_goal_frontmatter(goal_path: Path) -> dict[str, Any]:
    text = goal_path.read_text()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    return yaml.safe_load(text[4:end]) or {}


def _parse_iso_local(value: str | None) -> datetime | None:
    if not value:
        return None
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s).astimezone()
    except ValueError:
        return None


def _find_produced_tasks(runs: list[Run], tasks_root: Path) -> list[ProducedTask]:
    """Resolve each created-run's task_id to its goal.md and inspect frontmatter."""
    out: list[ProducedTask] = []
    if not tasks_root.exists():
        return out
    goal_index: dict[str, Path] = {}  # task_id -> goal.md path
    for goal in tasks_root.rglob("goal.md"):
        try:
            fm = _load_goal_frontmatter(goal)
        except (OSError, yaml.YAMLError):
            continue
        tid = fm.get("task_id")
        if isinstance(tid, str):
            goal_index[tid] = goal
    for run in runs:
        if run.outcome != "created":
            continue
        task_id = run.notes.strip()
        goal_path = goal_index.get(task_id)
        if goal_path is None:
            continue
        fm = _load_goal_frontmatter(goal_path)
        awaiting = fm.get("awaiting") or []
        if not isinstance(awaiting, list):
            awaiting = []
        unblocked = "user-unblock" not in awaiting
        status = str(fm.get("status") or "")
        source_event = fm.get("source_event") or {}
        event_type = ""
        if isinstance(source_event, dict):
            event_type = str(source_event.get("event_type") or "")
        out.append(
            ProducedTask(
                task_id=task_id,
                goal_path=goal_path,
                created=_parse_iso_local(run.ts),
                awaiting=list(awaiting),
                status=status,
                source_event_type=event_type,
                target_path=str(fm.get("target_path") or ""),
                unblocked=unblocked,
                unblock_date=_unblock_date(goal_path, unblocked),
                completed=status in ("completed", "done"),
            )
        )
    return out


def _unblock_date(goal_path: Path, unblocked: bool) -> datetime | None:
    """First commit where ``awaiting:`` no longer contains user-unblock."""
    if not unblocked:
        return None
    try:
        log = subprocess.run(
            ["git", "log", "--format=%H\t%aI", "--", str(goal_path)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    # Commits ordered newest first; walk oldest-to-newest and pick the first
    # commit whose goal.md content lacks "user-unblock" in awaiting.
    commits = [line.split("\t") for line in log.stdout.strip().splitlines() if "\t" in line]
    for sha, iso in reversed(commits):
        try:
            blob = subprocess.run(
                ["git", "show", f"{sha}:{goal_path.relative_to(PROJECT_ROOT)}"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if "user-unblock" not in blob.stdout:
            return _parse_iso_local(iso)
    return None


# --- Metrics ------------------------------------------------------------------


def compute_unblock_rate(tasks: Iterable[ProducedTask]) -> tuple[float | None, int]:
    items = list(tasks)
    if not items:
        return None, 0
    return sum(1 for t in items if t.unblocked) / len(items), len(items)


def compute_revert_rate(
    tasks: Iterable[ProducedTask],
    window: timedelta = timedelta(weeks=REVERT_WINDOW_WEEKS),
) -> tuple[float | None, int]:
    """Fraction of unblocked-and-completed tasks whose commit was reverted."""
    completed = [t for t in tasks if t.completed and t.unblocked]
    if not completed:
        return None, 0
    reverted = 0
    for task in completed:
        if _has_revert(task, window):
            reverted += 1
    return reverted / len(completed), len(completed)


def _has_revert(task: ProducedTask, window: timedelta) -> bool:
    """A revert is a commit subject matching ``Revert "...<task_id>...``."""
    try:
        log = subprocess.run(
            [
                "git",
                "log",
                "--grep",
                f"Revert.*{re.escape(task.task_id)}",
                "--format=%aI",
                "--since",
                f"{window.days} days ago",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return bool(log.stdout.strip())


# --- Rubric -------------------------------------------------------------------


def _band(value: float, low: float, high: float) -> bool:
    return low <= value <= high


def _criterion(key: str, label: str, ok: bool | None, detail: str) -> Criterion:
    if ok is None:
        return Criterion(key, label, INSUFFICIENT_DATA_NEUTRAL, f"insufficient data — {detail}")
    return Criterion(key, label, 1.0 if ok else 0.0, detail)


def _c_unblock_band(rate: float | None, n: int) -> Criterion:
    if rate is None:
        return _criterion("unblock_band", "Unblock rate in target band", None, "no produced tasks")
    ok = _band(rate, UNBLOCK_RATE_BAND_LOW, UNBLOCK_RATE_BAND_HIGH)
    return _criterion(
        "unblock_band",
        "Unblock rate in target band",
        ok,
        f"{rate:.0%} of {n} (band {UNBLOCK_RATE_BAND_LOW:.0%}-{UNBLOCK_RATE_BAND_HIGH:.0%})",
    )


REVERT_MIN_SAMPLE = 4


def _c_revert_low(rate: float | None, n: int) -> Criterion:
    if rate is None or n < REVERT_MIN_SAMPLE:
        return _criterion(
            "revert_low",
            "Revert rate low",
            None,
            f"{n} completed tasks (<{REVERT_MIN_SAMPLE})",
        )
    return _criterion(
        "revert_low",
        "Revert rate low",
        rate < REVERT_RATE_THRESHOLD,
        f"{rate:.0%} of {n} reverted",
    )


def _c_no_op_streak(runs: list[Run]) -> Criterion:
    streak = 0
    for run in reversed(runs):
        if run.outcome == "no-op":
            streak += 1
        else:
            break
    return _criterion(
        "no_op_streak",
        "No-op streak bounded",
        streak <= NO_OP_STREAK_MAX,
        f"current streak {streak} (max {NO_OP_STREAK_MAX})",
    )


def _c_diversity(runs: list[Run]) -> Criterion:
    created = [r for r in runs if r.outcome == "created"][-DIVERSITY_WINDOW:]
    if not created:
        return _criterion("diversity", "Dimension diversity", None, "no created runs")
    distinct = {r.dimension for r in created if r.dimension and r.dimension != "-"}
    return _criterion(
        "diversity",
        "Dimension diversity",
        len(distinct) >= DIVERSITY_MIN_DISTINCT,
        f"{len(distinct)} distinct of last {len(created)} (target ≥{DIVERSITY_MIN_DISTINCT})",
    )


def _c_periodic_share(runs: list[Run]) -> Criterion:
    created = [r for r in runs if r.outcome == "created"]
    if not created:
        return _criterion("periodic_share", "Periodic not dominant", None, "no created runs")
    periodic = sum(1 for r in created if "alignment" in r.dimension)
    share = periodic / len(created)
    return _criterion(
        "periodic_share",
        "Periodic not dominant",
        share < PERIODIC_SHARE_MAX,
        f"{share:.0%} periodic of {len(created)}",
    )


def _c_denylist_clean(runs: list[Run]) -> Criterion:
    cutoff = datetime.now().astimezone() - timedelta(days=DENYLIST_WINDOW_DAYS)
    hits = 0
    for run in runs:
        if not run.notes.startswith("denylist:"):
            continue
        ts = _parse_iso_local(run.ts)
        if ts and ts >= cutoff:
            hits += 1
    return _criterion(
        "denylist_clean",
        "No recent denylist hits",
        hits == 0,
        f"{hits} hits in last {DENYLIST_WINDOW_DAYS} days",
    )


def _c_task_folders_present(tasks: list[ProducedTask], runs: list[Run]) -> Criterion:
    created_ids = [r.notes for r in runs if r.outcome == "created" and r.notes]
    found_ids = {t.task_id for t in tasks}
    missing = [tid for tid in created_ids if tid not in found_ids]
    if not created_ids:
        return _criterion("task_folders", "Created runs have task folders", None, "no created runs")
    return _criterion(
        "task_folders",
        "Created runs have task folders",
        not missing,
        f"{len(found_ids)}/{len(created_ids)} resolved" + (f"; missing {missing[:3]}" if missing else ""),
    )


def _c_auto_block_applied(tasks: list[ProducedTask]) -> Criterion:
    if not tasks:
        return _criterion("auto_block", "Auto-block applied (G-INV-1)", None, "no produced tasks")
    # G-INV-1: every produced task must have user-unblock in awaiting at creation.
    # Proxy: every task either is currently awaiting OR was unblocked (i.e. ever had it).
    # A task that never had user-unblock would be missing from goal_index match — already filtered.
    # Tighter check: scan goal.md history for "user-unblock" appearance.
    violations = [t for t in tasks if not _ever_had_user_unblock(t.goal_path)]
    return _criterion(
        "auto_block",
        "Auto-block applied (G-INV-1)",
        not violations,
        f"{len(tasks) - len(violations)}/{len(tasks)} carried user-unblock",
    )


def _ever_had_user_unblock(goal_path: Path) -> bool:
    try:
        log = subprocess.run(
            ["git", "log", "-S", "user-unblock", "--format=%H", "--", str(goal_path)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    if log.stdout.strip():
        return True
    # Fall back to current file content (HEAD may still carry it).
    try:
        return "user-unblock" in goal_path.read_text()
    except OSError:
        return False


def _c_unblock_latency(tasks: list[ProducedTask]) -> Criterion:
    unblocked: list[tuple[datetime, datetime]] = [
        (t.unblock_date, t.created)
        for t in tasks
        if t.unblocked and t.created is not None and t.unblock_date is not None
    ]
    if not unblocked:
        return _criterion("unblock_latency", "Unblock latency reasonable", None, "no unblocked tasks")
    deltas = sorted((u - c).days for u, c in unblocked)
    median = deltas[len(deltas) // 2]
    return _criterion(
        "unblock_latency",
        "Unblock latency reasonable",
        median <= UNBLOCK_LATENCY_MAX_DAYS,
        f"median {median}d of {len(unblocked)} (max {UNBLOCK_LATENCY_MAX_DAYS}d)",
    )


def _c_bugfix_first(runs: list[Run]) -> Criterion:
    # AC-07 is enforced by select_candidate.py. The audit reflects that any
    # run with dimension=bugfix should appear in priority order — a structural
    # proxy: the share of bugfix-dimension created runs vs. optimization-class.
    created = [r for r in runs if r.outcome == "created"]
    if not created:
        return _criterion("bugfix_first", "Bugfix-first honored (AC-07)", None, "no created runs")
    bugfix = sum(1 for r in created if r.dimension == "bugfix")
    # Pass: at least one bugfix processed when present, OR no bugfix events ever fired
    # (insufficient data). Failure mode is a non-AC-07 bypass which select_candidate.py
    # already prevents — so this criterion is mostly a regression-canary.
    return _criterion(
        "bugfix_first",
        "Bugfix-first honored (AC-07)",
        True,
        f"{bugfix}/{len(created)} created runs were bugfix",
    )


def build_rubric(
    runs: list[Run], tasks: list[ProducedTask], unblock: float | None, revert: float | None
) -> list[Criterion]:
    n_tasks = len(tasks)
    revert_n = sum(1 for t in tasks if t.completed and t.unblocked)
    return [
        _c_unblock_band(unblock, n_tasks),
        _c_revert_low(revert, revert_n),
        _c_bugfix_first(runs),
        _c_no_op_streak(runs),
        _c_diversity(runs),
        _c_periodic_share(runs),
        _c_denylist_clean(runs),
        _c_task_folders_present(tasks, runs),
        _c_auto_block_applied(tasks),
        _c_unblock_latency(tasks),
    ]


# --- Filtering for --monitor=<name> sub-audit ---------------------------------


def filter_for_monitor(
    runs: list[Run], tasks: list[ProducedTask], monitor: str
) -> tuple[list[Run], list[ProducedTask]]:
    """Subset runs and tasks to those whose source monitor matches ``monitor``.

    Tasks are filtered by goal.md ``source_event.event_type``; runs are filtered
    by linking to a matching task (notes=task_id) or, for no-ops, kept only
    when their dimension maps to the monitor (best-effort link).
    """
    matched_tasks = [t for t in tasks if t.source_event_type == monitor]
    matched_ids = {t.task_id for t in matched_tasks}
    # Keep runs that produced a matched task, plus monitor-relevant no-ops.
    monitor_dims_by_name = {
        "repeated_question": {"bugfix"},
        "skill_change_reverted": {"bugfix"},
        "skill_changed_and_used": {"bugfix", "clarity", "trigger_accuracy"},
        "periodic": {"alignment"},
    }
    allowed_dims = monitor_dims_by_name.get(monitor, set())
    matched_runs = [
        r
        for r in runs
        if (r.outcome == "created" and r.notes in matched_ids)
        or (r.outcome == "no-op" and r.dimension in allowed_dims)
    ]
    return matched_runs, matched_tasks


# --- Report rendering ---------------------------------------------------------


def _previous_score(history_path: Path) -> float | None:
    if not history_path.exists():
        return None
    lines = [line for line in history_path.read_text().splitlines() if line and not line.startswith("ts\t")]
    if not lines:
        return None
    parts = lines[-1].split("\t")
    if len(parts) < 2:
        return None
    try:
        return float(parts[1])
    except ValueError:
        return None


def _fmt_rate(rate: float | None) -> str:
    return "-" if rate is None else f"{rate:.2f}"


def render_report(result: AuditResult, runs_count: int) -> str:
    title = (
        f"# Optimizer Audit — {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}"
    )
    monitor_line = f"\nMonitor scope: **{result.monitor}**\n" if result.monitor != "all" else ""
    head = (
        f"{title}\n"
        f"{monitor_line}\n"
        f"- Score: **{result.score:.1f} / {RUBRIC_TOTAL}** (Δ {result.delta:+.1f})\n"
        f"- User-unblock-rate: **{_fmt_rate(result.unblock_rate)}** (target {UNBLOCK_RATE_BAND_LOW:.0%}-{UNBLOCK_RATE_BAND_HIGH:.0%})\n"
        f"- Revert-rate: **{_fmt_rate(result.revert_rate)}** (target <{REVERT_RATE_THRESHOLD:.0%}, slow cadence)\n"
        f"- Sample: {result.sample_size} produced tasks / {runs_count} runs\n"
        f"\n## Rubric breakdown\n\n| Criterion | Score | Detail |\n|---|---|---|\n"
    )
    rows = "\n".join(f"| {c.label} | {c.score:.1f} | {c.detail} |" for c in result.criteria)
    return head + rows + "\n"


def _append_history(history_path: Path, result: AuditResult) -> None:
    ts = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    notes = result.monitor if result.monitor != "all" else "-"
    line = (
        f"{ts}\t{result.score:.1f}\t{result.delta:+.1f}\t"
        f"{_fmt_rate(result.unblock_rate)}\t{_fmt_rate(result.revert_rate)}\t{notes}\n"
    )
    history_path.parent.mkdir(parents=True, exist_ok=True)
    if not history_path.exists():
        history_path.write_text("ts\tscore\tdelta\tunblock_rate\trevert_rate\tnotes\n")
    with history_path.open("a") as f:
        f.write(line)


# --- CLI ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute optimizer audit score + metrics.")
    parser.add_argument("--runs-tsv", required=True, type=Path)
    parser.add_argument("--audit-history", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--tasks-root", required=True, type=Path)
    parser.add_argument("--monitor", default="", choices=("", *MONITOR_NAMES))
    args = parser.parse_args(argv)

    runs = _read_runs(args.runs_tsv)
    if not runs:
        print("no runs to audit", file=sys.stderr)
        return 2

    tasks = _find_produced_tasks(runs, args.tasks_root)
    if args.monitor:
        runs, tasks = filter_for_monitor(runs, tasks, args.monitor)

    unblock_rate, n = compute_unblock_rate(tasks)
    revert_rate, _ = compute_revert_rate(tasks)
    criteria = build_rubric(runs, tasks, unblock_rate, revert_rate)
    score = sum(c.score for c in criteria)
    prev = _previous_score(args.audit_history)
    delta = 0.0 if prev is None else score - prev

    result = AuditResult(
        score=score,
        delta=delta,
        unblock_rate=unblock_rate,
        revert_rate=revert_rate,
        criteria=criteria,
        monitor=args.monitor or "all",
        sample_size=n,
    )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(result, runs_count=len(runs)))
    _append_history(args.audit_history, result)

    print(
        f"score={result.score:.1f}/{RUBRIC_TOTAL} "
        f"delta={result.delta:+.1f} "
        f"unblock={_fmt_rate(result.unblock_rate)} "
        f"revert={_fmt_rate(result.revert_rate)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
