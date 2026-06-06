#!/usr/bin/env python3
"""
Returns the next N tasks to work on (default 3).

Ranking rules (applied in order):
  1. Critical-path explores (writes_requirements: true) always first — these write
     requirements that impl tasks depend on, so they must run before any impl work
  2. Tasks assigned to the next release/package first
     (next release = lowest semver with at least one open, non-blocked task)
  3. Exploration tasks (type: explore) before implementation tasks (within scope)
  4. Requirements already in-progress (has a completed task for the next release)
     come before fresh requirements
  5. Highest priority score (urgency x 10 + impact) as tiebreaker

Blocked tasks (awaiting non-empty, status == 'blocked', or after references
a non-terminal task) are excluded.
Terminal tasks (completed / cancelled / superseded) are excluded.
Legacy goal.md files without YAML frontmatter (no task_id) are skipped.

Usage:
    python scripts/next_tasks.py
    python scripts/next_tasks.py --release 0.0.1
    python scripts/next_tasks.py --count 5

Output:
    Prints one task per line ('<RANK> <TASK-ID> <PATH> <NAME>') to stdout, ranked by release / explore-before-impl / priority.
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, cast

# Allow running as a script without installing the package.
# task_ordering/ lives one level up in scripts/, not in scripts/tasks/
sys.path.insert(0, str(Path(__file__).parent.parent))

from task_ordering import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    EXCLUDED_STATUSES,
    TERMINAL_STATUSES,
    find_next_package,
    find_next_release,
    is_blocked,
    parse_semver,
    rank_tasks,
    rank_tasks_by_package,
)
from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    _split_frontmatter,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent
RELEASES_FILE = PROJECT_ROOT / "requirements_tasks" / "RELEASES.md"
RELEASE_BACKLOG_FILE = PROJECT_ROOT / "requirements_tasks" / "RELEASE_BACKLOG.md"
PENDING_FEEDBACK_DIR = PROJECT_ROOT / "automation" / "pending_feedback"

# The last fixed line of the answer.md template written by the orchestrator.
# Anything after this line (once stripped) is the human's actual answer.
_ANSWER_TEMPLATE_SENTINEL = (
    "The developer will open this file and type their answer below"
    " — replacing or appending to this text."
)

# Why: Temporary override for bootstrapping the task-ordering engine itself.
# The 10 new ordering tasks rank below other work under the old scoring logic,
# but must run first so the new engine exists before anything else is ranked.
# Delete .claude/task_ordering_priority_override.txt when TASK-PROC-042-11 completes.
PRIORITY_OVERRIDE_FILE = PROJECT_ROOT / ".claude" / "task_ordering_priority_override.txt"


def load_pending_feedback_ids() -> set[Any]:
    """Return task IDs that have an unanswered question in automation/pending_feedback/.

    A question is considered unanswered when answer.md:
      - does not exist, OR
      - is empty / whitespace-only, OR
      - contains only the template placeholder with no real answer appended.

    Why: The orchestrator writes a question.md and exits when it needs human input.
    next_tasks.py must not surface those tasks again — doing so wastes 2-7 min per
    session as the new session re-asks the same question instead of doing real work.
    """
    pending: set[Any] = set()
    if not PENDING_FEEDBACK_DIR.is_dir():
        return pending

    for entry in PENDING_FEEDBACK_DIR.iterdir():
        if not entry.is_dir():
            continue
        task_id = entry.name
        answer_file = entry / "answer.md"

        if not answer_file.exists():
            pending.add(task_id)
            continue

        try:
            text = answer_file.read_text(encoding="utf-8")
        except Exception:
            # If unreadable, treat as unanswered to be safe
            pending.add(task_id)
            continue

        stripped = text.strip()
        if not stripped:
            pending.add(task_id)
            continue

        # A real answer is anything written *after* the template's last fixed
        # line. Split on the sentinel: if nothing follows it (after stripping),
        # no human answer has been appended yet.
        if _ANSWER_TEMPLATE_SENTINEL in text:
            after_sentinel = text.split(_ANSWER_TEMPLATE_SENTINEL, 1)[1].strip()
            if not after_sentinel:
                pending.add(task_id)
        # If the sentinel is absent the file was replaced entirely by the human,
        # which also counts as answered — leave it out of the pending set.

    return pending


def load_priority_override() -> list[str]:
    """Return ordered task IDs from the override file, or [] if file absent."""
    if not PRIORITY_OVERRIDE_FILE.exists():
        return []
    lines = PRIORITY_OVERRIDE_FILE.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


# ---------------------------------------------------------------------------
# YAML parsing — delegates to scripts/util/yaml_frontmatter (REQ-PROC-051 AC-08)
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> Optional[dict[str, Any]]:
    """Extract and parse YAML frontmatter from markdown content.

    Routes through the central helper's internal split helper
    (`_split_frontmatter`) instead of `read_frontmatter`, because the latter
    calls `Path(text).exists()` to auto-detect path-vs-text sources and raises
    ENAMETOOLONG for any text > NAME_MAX (~255 bytes).

    Uses a tolerant ruamel loader: the prior hand-rolled parser silently kept
    the last value for duplicate keys (encountered in some real user-flow
    docs); we preserve that lax-read behaviour here.
    """
    # Strip UTF-8 BOM added by some Windows editors
    if content.startswith("﻿"):
        content = content[1:]
    raw_yaml, _body = _split_frontmatter(content)
    if not raw_yaml.strip():
        return None
    from io import StringIO

    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True  # tolerate legacy docs with duplicate keys
    try:
        result = yaml.load(StringIO(raw_yaml))
    except Exception:
        return None
    if result is None:
        return None
    if not isinstance(result, dict):
        return None
    if len(result) == 0:
        return None
    return dict(result)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _task_name(goal_file: Path) -> str:
    folder = goal_file.parent.name
    name = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", folder)
    name = re.sub(r"^(impl|explore|fix|create|update)_", "", name, flags=re.IGNORECASE)
    for suffix in ("_(completed)", "_(superseded)", "_(cancelled)", "_(paused)"):
        name = name.replace(suffix, "")
    return name.replace("_", " ").strip()


def _find_files(root: Path, name: str) -> list[Path]:
    """Locate files by name using native find (faster than rglob on WSL2/Windows mounts)."""
    try:
        result = subprocess.run(
            ["find", str(root), "-name", name],
            capture_output=True, text=True
        )
        return [Path(p) for p in result.stdout.splitlines() if p.strip()]
    except FileNotFoundError:
        return list(root.rglob(name))


def load_tasks() -> list[dict[str, Any]]:
    """Scan all goal.md files and return parsed task dicts."""
    tasks: list[dict[str, Any]] = []
    root = PROJECT_ROOT / "requirements_tasks"

    for goal_file in _find_files(root, "goal.md"):
        try:
            content = goal_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = goal_file.read_text(encoding="latin-1")
            except Exception:
                continue
        except Exception:
            continue

        meta = parse_frontmatter(content)
        if not meta or "task_id" not in meta:
            continue  # skip legacy tasks without frontmatter

        awaiting = meta.get("awaiting", [])
        if not isinstance(awaiting, list):
            awaiting = [awaiting] if awaiting else []
        awaiting = [b for b in awaiting if b]

        after = meta.get("after", [])
        if not isinstance(after, list):
            after = [after] if after else []
        after = [d for d in after if d]

        target_release = meta.get("target_release")
        if target_release is not None:
            target_release = str(target_release).strip().strip("\"'") or None

        target_package = meta.get("target_package")
        if target_package is not None:
            target_package = str(target_package).strip().strip("\"'") or None

        tasks.append(
            {
                "task_id": str(meta.get("task_id", "")),
                "path": str(goal_file),
                "name": _task_name(goal_file),
                "parent_requirement": str(meta.get("parent_requirement", "")),
                "type": str(meta.get("type", "impl")).lower(),
                "status": str(meta.get("status", "unknown")).lower(),
                "urgency": int(meta.get("urgency", 0) or 0),
                "impact": int(meta.get("impact", 0) or 0),
                "awaiting": awaiting,
                "after": after,
                "target_release": target_release,
                "target_package": target_package,
                "completed": meta.get("completed"),
                "writes_requirements": bool(meta.get("writes_requirements", False)),
                "cascade_active": bool(meta.get("cascade_active", False)),
                "factory_urgent": bool(meta.get("factory_urgent", False)),
                "orchestration_task": bool(meta.get("orchestration_task", False)),
                "scope_description": str(meta.get("scope_description", "")),
            }
        )

    return tasks


# ---------------------------------------------------------------------------
# Release boundary detection
# ---------------------------------------------------------------------------

def load_backlog_packages() -> list[dict[Any, Any]]:
    """Parse RELEASE_BACKLOG.md and return flat list of packages with version info."""
    if not RELEASE_BACKLOG_FILE.exists():
        return []
    try:
        content = RELEASE_BACKLOG_FILE.read_text(encoding="utf-8")
    except Exception:
        return []
    meta = parse_frontmatter(content)
    if not meta or "packages" not in meta:
        return []
    result = []
    for pkg in meta.get("packages", []):
        if isinstance(pkg, dict) and "id" in pkg:
            version = str(pkg.get("assigned_release", "") or "")
            result.append({
                "id": pkg["id"],
                "name": pkg.get("name", ""),
                "version": version,
                "status": pkg.get("status", "planned"),
            })
    return result


def load_active_release() -> Optional[str]:
    """Parse RELEASES.md frontmatter and return the version with status: active."""
    try:
        content = RELEASES_FILE.read_text(encoding="utf-8")
    except Exception:
        return None

    meta = parse_frontmatter(content)
    if meta:
        releases_list = meta.get("releases")
        if isinstance(releases_list, list):
            for r in releases_list:
                if isinstance(r, dict) and r.get("status") == "active":
                    return str(r.get("version", "")).strip().strip("\"'")

    # Fallback regex: works when simple parser can't handle nested dicts
    fm_match = re.search(r"^---\n(.*?)^---", content, re.DOTALL | re.MULTILINE)
    if fm_match:
        yaml_text = fm_match.group(1)
        blocks = re.split(r"\n\s*-\s+", yaml_text)
        for block in blocks:
            if "status: active" in block:
                m = re.search(r'version:\s*["\']?([0-9][0-9.]*)["\']?', block)
                if m:
                    return m.group(1)

    return None


def find_completed_previous_release(
    tasks: list[dict[Any, Any]], next_release: str
) -> Optional[str]:
    """Return the release immediately before next_release if all its tasks are terminal."""
    all_releases = {t["target_release"] for t in tasks if t["target_release"]}
    sorted_releases = sorted(all_releases, key=lambda v: parse_semver(v))

    try:
        idx = sorted_releases.index(next_release)
    except ValueError:
        return None

    if idx == 0:
        return None

    prev_release = sorted_releases[idx - 1]
    prev_tasks = [t for t in tasks if t["target_release"] == prev_release]
    if prev_tasks and all(t["status"] in TERMINAL_STATUSES for t in prev_tasks):
        return cast("str | None", prev_release)

    return None


def _find_pending_orch_tasks(
    tasks: list[dict[str, Any]],
    pending_ids: set[Any],
    active_release: Optional[str],
) -> list[dict[str, Any]]:
    """Return non-terminal orchestration tasks that are stuck in pending_feedback.

    Used to enforce REQ-PROC-035 SEC-05: no impl task surfaces while any orch
    task for the active release is awaiting human input.
    """
    if not pending_ids or not active_release:
        return []
    return [
        t for t in tasks
        if t["task_id"] in pending_ids
        and t["orchestration_task"]
        and t["status"] not in TERMINAL_STATUSES
        and t["target_release"] == active_release
    ]


def _print_release_warning(title: str, lines: list[str]) -> None:
    width = 62
    print("!" * width)
    print(f"  {title}")
    print("!" * width)
    for line in lines:
        print(f"  {line}")
    print("!" * width)
    print()


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def _format_task(task: dict[Any, Any], rank: int) -> str:
    release = task["target_release"] or "unassigned"
    from task_ordering import priority_score
    score = priority_score(task)
    rel_path = Path(task["path"]).relative_to(PROJECT_ROOT)
    lines = [
        f"{rank}. [{task['task_id']}] {task['name']}",
        f"   Release: {release} | Type: {task['type']} | Status: {task['status']} | Priority: {score} | Req: {task['parent_requirement']}",
        f"   Path: {rel_path}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> Any:
    parser = argparse.ArgumentParser(
        description="Show the next N tasks to work on."
    )
    parser.add_argument(
        "--release", help="Override the auto-detected next release version"
    )
    parser.add_argument(
        "--package", help="Override the auto-detected next package ID"
    )
    parser.add_argument(
        "--count", type=int, default=4, help="Number of tasks to show (default: 4)"
    )
    parser.add_argument(
        "--type", choices=["impl", "explore"], default=None,
        help="Filter to only impl or explore tasks"
    )
    args = parser.parse_args()

    tasks = load_tasks()

    # Exclude tasks that have an unanswered question in automation/pending_feedback/.
    # Re-surfacing them only causes new sessions to waste time re-asking the same
    # question instead of picking up other work.
    pending_ids = load_pending_feedback_ids()

    # Identify pending orchestration tasks BEFORE filtering them out of the list.
    # We cannot exit here yet — the priority override path must surface its own
    # tasks first (override tasks have no target_release/target_package and are
    # independent of the release impl chain). The orch block fires after the
    # override check, only on the normal package/release ranking path.
    # See REQ-PROC-035 SEC-05 for the orchestration-first ordering requirement.
    pending_orch: list[dict[str, Any]] = []
    if pending_ids:
        pending_orch = _find_pending_orch_tasks(tasks, pending_ids, load_active_release())
        tasks = [t for t in tasks if t["task_id"] not in pending_ids]

    # Apply type filter before ranking if requested
    if args.type:
        tasks = [t for t in tasks if t["type"] == args.type]

    completed_ids = {t["task_id"] for t in tasks if t["status"] in TERMINAL_STATUSES}
    known_ids = {t["task_id"] for t in tasks}

    backlog_packages = load_backlog_packages()
    next_package = args.package if args.package else find_next_package(tasks, completed_ids, known_ids, backlog_packages)

    # Fall back to release-based ranking if no target_package data exists
    next_release = args.release if args.release else find_next_release(tasks, completed_ids, known_ids)

    # Primary: use package if available, else fall back to release
    if next_package:
        display_next = f"Next package: {next_package}"
        if args.type:
            display_next += f" (filter: {args.type} only)"
        ranked = rank_tasks_by_package(tasks, next_package, completed_ids, known_ids)
        completed_count = sum(
            1 for t in tasks
            if t.get("target_package") == next_package and t["status"] == "completed"
        )
        open_count = sum(
            1 for t in tasks
            if t.get("target_package") == next_package
            and t["status"] not in EXCLUDED_STATUSES
            and not is_blocked(t, completed_ids, known_ids)
        )
    elif next_release:
        display_next = f"Next release: {next_release} (no package data — falling back to release)"
        ranked = rank_tasks(tasks, next_release, completed_ids, known_ids)
        completed_count = sum(
            1 for t in tasks
            if t["target_release"] == next_release and t["status"] == "completed"
        )
        open_count = sum(
            1 for t in tasks
            if t["target_release"] == next_release
            and t["status"] not in EXCLUDED_STATUSES
            and not is_blocked(t, completed_ids, known_ids)
        )
    else:
        print("No open tasks with a target_package or target_release found.")
        sys.exit(0)

    # --- Release boundary check for package mode ---
    if next_package and backlog_packages:
        active_release = load_active_release()
        next_pkg_version = next(
            (p["version"] for p in backlog_packages if p["id"] == next_package), None
        )
        if next_pkg_version:
            last_completed_version = None
            for pkg in backlog_packages:
                pkg_tasks = [t for t in tasks if t.get("target_package") == pkg["id"]]
                if pkg_tasks and all(t["status"] in TERMINAL_STATUSES for t in pkg_tasks):
                    last_completed_version = pkg["version"]
                else:
                    break  # packages are ordered; stop at first non-complete

            if active_release and parse_semver(active_release) < parse_semver(next_pkg_version):
                _print_release_warning(
                    "WARNING: RELEASE NOT EXECUTED",
                    [
                        f"RELEASES.md marks release {active_release!r} as active,",
                        f"but the next package ({next_package!r}) belongs to",
                        f"release {next_pkg_version!r}.",
                        "",
                        "Suggested next step: run the /release skill for",
                        f"release {active_release!r} before continuing.",
                    ],
                )
            elif (
                not active_release
                and last_completed_version is not None
                and parse_semver(last_completed_version) < parse_semver(next_pkg_version)
                and completed_count == 0
            ):
                _print_release_warning(
                    "RELEASE BOUNDARY DETECTED",
                    [
                        f"All tasks for release {last_completed_version!r} are complete.",
                        f"The next package ({next_package!r}) belongs to",
                        f"release {next_pkg_version!r} and no work on it has started.",
                        "",
                        "Suggested next step: run the /release skill for",
                        f"release {last_completed_version!r} before starting new work.",
                    ],
                )

    # --- Release boundary / forgotten-release checks (only in release-fallback mode) ---
    if not next_package and next_release:
        active_release = load_active_release()

        if active_release and parse_semver(active_release) < parse_semver(next_release):
            # RELEASES.md still shows an older release as active → release step was skipped
            _print_release_warning(
                "WARNING: RELEASE NOT EXECUTED",
                [
                    f"RELEASES.md marks release {active_release!r} as active,",
                    f"but the next open tasks already belong to release {next_release!r}.",
                    "",
                    "This means the /release skill was never run for",
                    f"release {active_release!r}.",
                    "",
                    "Suggested next step: run the /release skill for",
                    f"release {active_release!r} before continuing.",
                ],
            )
        elif not active_release:
            # No active release set → check for a clean release boundary via task data
            prev_completed = find_completed_previous_release(tasks, next_release)
            if prev_completed and completed_count == 0:
                _print_release_warning(
                    "RELEASE BOUNDARY DETECTED",
                    [
                        f"All tasks for release {prev_completed!r} are complete.",
                        f"The tasks shown below belong to the next release ({next_release!r}),",
                        "and no work on it has started yet.",
                        "",
                        "Suggested next step: run the /release skill for",
                        f"release {prev_completed!r} before starting new work.",
                    ],
                )
    # ---

    # Autonomous optimize cycle task (REQ-PROC-006 §Monitor-Based Detection):
    # a `type: optimize` task is the unattended cycle (awaiting: []) created by
    # run_monitors.py when the optimizer event queue is non-empty. It carries no
    # target_package/target_release, so it would never rank on the normal path,
    # and the priority-override gate below returns ONLY override-listed tasks.
    # Surface it here — ahead of both — so it is always-eligible and preempts
    # other work until it completes. Bounded: at most one exists at a time (it is
    # only created when none is pending) and the cycle is short, so the preemption
    # window self-clears. Blocked optimize tasks fall through (none expected —
    # awaiting is []) so they cannot deadlock the queue.
    optimize_tasks = [
        t for t in tasks
        if t["type"] == "optimize"
        and t["status"] not in EXCLUDED_STATUSES
        and not is_blocked(t, completed_ids, known_ids)
    ]
    if optimize_tasks:
        print(display_next)
        print(f"Completed tasks: {completed_count} | Open tasks: {open_count}")
        print()
        print(f"Next {len(optimize_tasks[: args.count])} tasks:")
        print()
        for i, task in enumerate(optimize_tasks[: args.count], 1):
            print(_format_task(task, i))
            print()
        return

    # Priority override: while non-terminal override tasks exist, block all other
    # work — return ONLY the override tasks until they are all completed/terminal.
    override_surfaced = False
    override_ids = load_priority_override()
    if override_ids:
        task_by_id = {t["task_id"]: t for t in tasks}
        override_nonterminal = [
            task_by_id[tid] for tid in override_ids
            if tid in task_by_id
            and task_by_id[tid]["status"] not in TERMINAL_STATUSES
        ]
        if override_nonterminal:
            override_runnable = [
                t for t in override_nonterminal
                if t["status"] not in EXCLUDED_STATUSES
                and not is_blocked(t, completed_ids, known_ids)
            ]
            if override_runnable:
                ranked = override_runnable
                override_surfaced = True
            else:
                # All pending override tasks are blocked — print informational message
                # and exit. The message intentionally does NOT use the "N. [TASK-ID]"
                # format so the orchestrator's pick_next_task_for_session regex finds
                # zero entries and returns None (no spurious fresh launch).
                override_blocked = [
                    t for t in override_nonterminal
                    if t["status"] not in EXCLUDED_STATUSES
                    and is_blocked(t, completed_ids, known_ids)
                ]
                override_in_progress = [
                    t for t in override_nonterminal
                    if t["status"] == "in_progress"
                ]
                print(display_next)
                print(f"Completed tasks: {completed_count} | Open tasks: {open_count}")
                print()
                print("Priority override active: task_ordering_priority_override.txt tasks must complete first.")
                print("No runnable override tasks found — all pending override tasks are blocked:")
                for t in override_blocked:
                    print(f"  Blocked: [{t['task_id']}] {t['name']}")
                if override_in_progress:
                    print("Tasks currently in progress (handled by resume path):")
                    for t in override_in_progress:
                        print(f"  In progress: [{t['task_id']}] {t['name']}")
                sys.exit(0)
        # else: all override tasks are terminal → fall through to normal ranking

    # Orch block (REQ-PROC-035 SEC-05): fires only when the override path did
    # not surface its own tasks. Override tasks are orthogonal to the release
    # impl chain and must not be suppressed by a stuck orchestration task.
    if not override_surfaced and pending_orch:
        print("Orchestration task awaiting human input — no impl tasks surfaced.")
        print("Resolve the following before implementation can proceed:")
        for t in pending_orch:
            print(f"  Pending: [{t['task_id']}] {t['name']}")
            print(f"    Answer: automation/pending_feedback/{t['task_id']}/answer.md")
        sys.exit(0)

    top = ranked[: args.count]

    print(display_next)
    print(f"Completed tasks: {completed_count} | Open tasks: {open_count}")
    print()
    print(f"Next {len(top)} tasks:")
    print()
    for i, task in enumerate(top, 1):
        print(_format_task(task, i))
        print()

    # --- AC coverage check for the active package ---
    # Only warn if there are no open exploration tasks for the package —
    # existing explore tasks are the mechanism that produces missing impl tasks.
    # Also suppress when an open orchestration task for the active release exists:
    # orch tasks carry target_release (not target_package) so the original guard
    # missed them, causing false-positive warnings during the orch-chain
    # materialization phase before all impl tasks are created.
    if next_package:
        active_release_for_guard = load_active_release()

        def _is_orch_task_for_active_release(t: dict[Any, Any]) -> bool:
            return (
                t["type"] == "explore"
                and t.get("target_release") == active_release_for_guard
                and str(t.get("scope_description", "")).startswith("Orchestration:")
                and t["status"] not in EXCLUDED_STATUSES
                and not is_blocked(t, completed_ids, known_ids)
            )

        open_coverage_mechanism = any(
            t for t in tasks
            if t["status"] not in EXCLUDED_STATUSES
            and not is_blocked(t, completed_ids, known_ids)
            and (
                (t.get("target_package") == next_package and t["type"] == "explore")
                or _is_orch_task_for_active_release(t)
            )
        )
        if not open_coverage_mechanism:
            coverage_script = Path(__file__).parent.parent.parent / "requirements" / "check_ac_coverage.py"
            if coverage_script.exists():
                result = subprocess.run(
                    [sys.executable, str(coverage_script), "--package", next_package],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 1 and result.stdout.strip():
                    width = 62
                    print("!" * width)
                    print("  WARNING: UNCOVERED ACs — DEPENDENCY GRAPH INCOMPLETE")
                    print("!" * width)
                    for line in result.stdout.strip().splitlines():
                        print(f"  {line}")
                    print("!")
                    print("  No exploration tasks exist for this package.")
                    print("  Create missing impl tasks before starting implementation")
                    print("  or the dependency graph will be incomplete.")
                    print("!" * width)
                    print()


if __name__ == "__main__":
    main()
