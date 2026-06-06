#!/usr/bin/env python3
"""Create an orchestration task to drive iterative impl-task creation for the active release.

Usage:
    python3 scripts/tasks/create_orchestration_task.py [--dry-run] [--after-task TASK-ID]
                                                       [--plan-path PATH] [--task-type TYPE]

Exit codes:
    0  task created (or dry-run validated) — prints TASK_ID=, TASK_PATH=, VERSION= to stdout
    1  no active release found
    2  orchestration task already exists (prints path to stderr)
    4  error during task creation

Note: Exit code 3 is retired. When all packages are covered, a validation orchestration
task is created (VALIDATION_TASK=true printed to stdout) rather than returning 3.

Version detection uses RELEASES.md (status: active) as the sole authoritative source.
Coverage detection uses parse_task_creation_plan.py --next-uncreated when a plan is
provided (exit 0 = uncreated tasks remain; exit 3 = all created). Without a plan, the
fallback conservatively assumes not all packages are covered (always creates an impl task).

Output:
    Prints the created task folder path to stdout, or a 'skipped: <reason>' line if no orchestration task was needed.
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import glob as _glob
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable, Optional

# Terminal status values: an orchestration task in any of these states no longer
# occupies a "live" slot and its folder may be overwritten by the two-slot scheme.
TERMINAL_STATUSES = ("completed", "superseded", "cancelled")

try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

PROJECT_ROOT = Path(__file__).parent.parent.parent
REQ_ID = "REQ-PROC-035"
REQ_PATH = "requirements_tasks/process/AI_rules/requirements_management/release_preparation"
REQUIREMENTS_FILE = f"{REQ_PATH}/requirements.md"


@dataclass
class Deps:
    run_subprocess: Callable[..., "subprocess.CompletedProcess[str]"]
    makedirs: Callable[[str], None]
    write_file: Callable[[str, str], None]
    file_exists: Callable[[str], bool]
    remove_file: Callable[[str], None]
    remove_dir: Callable[[str], None]
    glob_files: Callable[[str], list[str]]
    read_file: Callable[[str], str]
    get_today: Callable[[], str]


def make_real_deps() -> Deps:
    return Deps(
        run_subprocess=lambda cmd, **kw: subprocess.run(
            cmd, capture_output=True, text=True, **kw
        ),
        makedirs=lambda p: os.makedirs(p, exist_ok=True),
        write_file=lambda p, c: (Path(p).write_text(c, encoding="utf-8"), None)[1],
        file_exists=os.path.isfile,
        remove_file=os.remove,
        remove_dir=lambda p: shutil.rmtree(p, ignore_errors=True),
        glob_files=lambda p: _glob.glob(p, recursive=True),
        read_file=lambda p: Path(p).read_text(encoding="utf-8"),
        get_today=lambda: date.today().isoformat(),
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an orchestration task for the active release."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and exit with the same code, but skip steps 4-6 (no file writes, no ID allocation).",
    )
    parser.add_argument(
        "--after-task",
        metavar="TASK-ID",
        default="",
        help="Append this task ID to the after: list in the goal.md frontmatter.",
    )
    parser.add_argument(
        "--plan-path",
        metavar="PATH",
        default="",
        help="Path to task_creation_plan.md; written as plan_path field in goal.md frontmatter.",
    )
    parser.add_argument(
        "--task-type",
        metavar="TYPE",
        default="implement",
        choices=["implement", "verify", "explore", "scribble", "scribble_to_flutter"],
        help="Task type from plan entry; controls which skill is named in Step 1 AC text.",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Pure parsing helpers (no I/O — easy to unit-test)
# ---------------------------------------------------------------------------

def parse_release_from_releases_md(content: str) -> Optional[str]:
    """Extract the version of the release with status: active from YAML frontmatter."""
    m = re.search(
        r'-\s+version:\s+"?(\d+\.\d+\.\d+)"?(?:(?!\n  -)[\s\S])*?status:\s+active',
        content,
        re.DOTALL,
    )
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# I/O-dependent helpers
# ---------------------------------------------------------------------------

def _read_orchestration_goal(deps: Deps, goal_path: str) -> Optional[tuple[str, str]]:
    """Return (task_id, status) if goal_path is an orchestration task, else None.

    An orchestration task has target_release set AND scope_description starting with
    'Orchestration:' (matches find_orchestration_tasks.py detection logic).
    """
    try:
        content = deps.read_file(goal_path)
    except OSError:
        return None
    target_release = re.search(r'^target_release:\s*"?(\S+?)"?\s*$', content, re.MULTILINE)
    if not target_release or not target_release.group(1).strip():
        return None
    if not re.search(r'^scope_description:\s*"?Orchestration:', content, re.MULTILINE):
        return None
    task_id_m = re.search(r"^task_id:\s*(\S+)", content, re.MULTILINE)
    status_m = re.search(r"^status:\s*(\S+)", content, re.MULTILINE)
    task_id = task_id_m.group(1).strip() if task_id_m else ""
    status = status_m.group(1).strip().lower() if status_m else ""
    return task_id, status


def find_existing_orchestration_task(deps: Deps, exclude_task_id: str = "") -> Optional[str]:
    """Return the goal.md path of a pending/in_progress orchestration task, or None.

    Two-slot alternation (REQ-PROC-035 SEC-05): the `--after-task` caller is itself
    a non-terminal orchestration task while it runs the create step. Excluding it via
    `exclude_task_id` is what lets the self-perpetuating chain advance — without the
    exclusion the caller would match its own duplicate guard and deadlock. The guard
    still fires for any OTHER non-terminal orch task, so two live tasks never coexist.
    """
    pattern = str(PROJECT_ROOT / "requirements_tasks" / "**" / "goal.md")
    for goal_path in deps.glob_files(pattern):
        parsed = _read_orchestration_goal(deps, goal_path)
        if parsed is None:
            continue
        task_id, status = parsed
        if exclude_task_id and task_id == exclude_task_id:
            continue
        if status in ("pending", "in_progress"):
            return goal_path
    return None


def _parse_after_ids(content: str) -> list[str]:
    """Extract task IDs from an `after: [...]` frontmatter line (inline-list form)."""
    m = re.search(r'^after:\s*\[(.*?)\]', content, re.MULTILINE)
    if not m:
        return []
    return re.findall(r"[A-Z]+-[A-Z]+-\d+(?:-\d+)*", m.group(1))


def find_predecessor_slot_dir(deps: Deps, caller_task_id: str, version: str) -> Optional[str]:
    """Return the folder path of the terminal predecessor orch task to overwrite, or None.

    Two-slot alternation: `--after-task <CALLER>` carries the caller's OWN id (the new
    task's `after:` will point back at it). The slot to reuse is the caller's OWN
    predecessor — the orch task named in the caller's `after:` list — which is now
    terminal. We (1) locate the caller's goal.md by id, (2) read its `after:` list,
    (3) for each referenced orch task that is terminal AND targets this release, return
    its folder. Returns None when no such terminal predecessor exists (first link in a
    chain / clean state) — the create step then makes a fresh folder, never a third one.
    """
    if not caller_task_id:
        return None

    pattern = str(PROJECT_ROOT / "requirements_tasks" / "**" / "goal.md")
    goal_paths = deps.glob_files(pattern)

    # Step 1 — find the caller's goal.md and read its after: list.
    predecessor_ids: list[str] = []
    for goal_path in goal_paths:
        try:
            content = deps.read_file(goal_path)
        except OSError:
            continue
        task_id_m = re.search(r"^task_id:\s*(\S+)", content, re.MULTILINE)
        if not task_id_m or task_id_m.group(1).strip() != caller_task_id:
            continue
        predecessor_ids = _parse_after_ids(content)
        break

    if not predecessor_ids:
        return None

    # Step 2 — among the caller's predecessors, find a terminal orch task for this release.
    for goal_path in goal_paths:
        parsed = _read_orchestration_goal(deps, goal_path)
        if parsed is None:
            continue
        task_id, status = parsed
        if task_id not in predecessor_ids:
            continue
        if status not in TERMINAL_STATUSES:
            continue
        try:
            content = deps.read_file(goal_path)
        except OSError:
            continue
        release_m = re.search(r'^target_release:\s*"?(\S+?)"?\s*$', content, re.MULTILINE)
        if not release_m or release_m.group(1).strip() != version:
            continue
        return str(Path(goal_path).parent)
    return None


def get_requirements_commit(deps: Deps) -> str:
    """Return the abbreviated commit hash for the requirements.md file."""
    result = deps.run_subprocess(
        ["git", "log", "--oneline", "-1", REQUIREMENTS_FILE],
        cwd=str(PROJECT_ROOT),
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().split()[0]
    return "unknown"


# ---------------------------------------------------------------------------
# goal.md templates
# ---------------------------------------------------------------------------


def _build_after_field(after_task: str) -> str:
    """Return the after: YAML line for the goal.md frontmatter."""
    if after_task:
        return f'after: ["{after_task}"]'
    return "after: []"


def _build_ac_block(batch_tasks: list[dict[Any, Any]], task_id: str, plan_path: str) -> str:
    """Build the dynamic AC checklist for an impl orchestration task goal.md.

    Each batch task gets one line; then a self-perpetuating chain line;
    then a task-complete line. Total lines = len(batch_tasks) + 2.
    """
    lines: list[str] = []
    for task in batch_tasks:
        task_type = task.get("task_type", "implement")
        notes = task.get("implementation_notes", "")
        if task_type == "scribble":
            skill = "ui-scribble-iterate"
        elif task_type in ("verify", "verification", "explore"):
            skill = "task-create"
        elif task_type == "scribble_to_flutter":
            skill = "task-create-code"
        elif notes and not any(d in notes for d in ("lib/", "test/", "integration_test/")):
            skill = "task-create"
        else:
            skill = "task-create-code"
        name = task.get("task_name", "<unknown>")
        acs = ", ".join(task.get("covers_acs", []))
        cov = f" (covers ACs: {acs})" if acs else ""
        lines.append(f"- [ ] Run `{skill}` skill in zero-parameter mode for `{name}`{cov}")
    # Why: plan_path can contain spaces and parentheses (e.g. "... (completed)/...")
    # because task-complete renames folders. Without shell-quoting the AC text
    # produces a bash syntax error when executed literally, silently breaking the chain.
    lines.append(
        f"- [ ] Run `python3 scripts/tasks/create_orchestration_task.py"
        f" --after-task {task_id} --plan-path {shlex.quote(plan_path)}`"
        f" — creates next orch task OR validation task"
    )
    lines.append(f"- [ ] Run `task-complete` on this orchestration task ({task_id}) — commit exactly once here, no earlier commits")
    return "\n".join(lines)


_GOAL_TEMPLATE = """\
---
task_id: {task_id}
type: explore
parent_requirement: {req_id}
urgency: 4
urgency_reason: U4-PLAN
impact: 4
impact_reason: I4-QUAL
status: pending
effort: XS
created: {today}
{after_field}
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Orchestration: create impl tasks for package {package_name} ({n_tasks} task(s)) on release {version}. Same-package per session; chain self-perpetuates."
target_release: "{version}"
plan_path: "{plan_path}"
task_type: "{task_type}"
orchestration_task: true
release_description: ""
opus_recommended: false
requirements_version:
  commit: {req_commit}
  file: ../requirements.md
---

# Goal: Create Impl Tasks for Package {package_name} (Release {version})

> **STOP — orchestration task.** This session ONLY creates task files. After every AC below is checked off, exit. Do NOT open the impl tasks you just created and do NOT touch `lib/` or `test/` in this session. If you start implementing, the chain breaks: the next orch task is never created and `release-begin-impl-finalize` never fires.

## Objective

Create all pending implementation tasks for package `{package_name}` in release {version}
using the approved task creation plan (if set). This session covers {n_tasks} task(s).

## Scope

- **In Scope**: Run the appropriate skill for each task listed in the ACs, create the next orch task, call `task-complete`.
- **Out of Scope**: Tasks from other packages per session, validation, implementation of the created tasks.
- **Commit rule**: Make exactly one commit for this entire session — at the `task-complete` step. Do not commit between individual skill runs.

## Ordering Rule

When a `plan_path` is set, the plan's execution order is **always authoritative** — even if RELEASE_BACKLOG `priority_within_source` suggests a different package. Implementation dependency order trumps business priority ranking. Do **not** ask for confirmation about this conflict; follow the plan silently.

## Acceptance Criteria

{ac_block}
"""

_VALIDATION_GOAL_TEMPLATE = """\
---
task_id: {task_id}
type: explore
parent_requirement: {req_id}
urgency: 4
urgency_reason: U4-PLAN
impact: 4
impact_reason: I4-QUAL
status: pending
effort: XS
created: {today}
after: [{after_entries}]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Orchestration: run structural validation for release {version} (all packages covered)."
target_release: "{version}"
release_description: ""
task_type: "validate"
orchestration_task: true
plan_path: "{plan_path}"
opus_recommended: false
requirements_version:
  commit: {req_commit}
  file: ../requirements.md
---

# Goal: Structural Validation for Release {version}

## Objective

Run structural validation for release {version}: AC coverage, after-chains,
target_package, opus_recommended flags. Write `validation_report.md`. Call `task-complete`.

All packages for release {version} are now covered by implementation tasks.
This task performs automated quality checks before the user runs `/release-begin-impl-finalize`.

## Acceptance Criteria

- [ ] Run `python3 scripts/artifacts/generate_status_overview.py --release {version}` and verify ≥1 non-terminal impl task exists per package. If ANY package has 0 impl tasks: write `validation_report.md` with a PREMATURE_TRIGGER section (list missing packages, count of tasks created vs expected from plan_path), then STOP — do NOT proceed to the remaining ACs. Call `task-complete`.
- [ ] Run `python3 scripts/tasks/check_task_against_plan.py` for each impl task in release {version}; write results to `validation_report.md`
- [ ] Run `python3 scripts/tasks/reconcile_after_chains.py --release {version}` (detect only, no --apply); append findings to `validation_report.md`
- [ ] Verify all impl tasks have `target_package` set; list any missing in `validation_report.md`
- [ ] Write `validation_report.md` to the explore task folder for release {version} (path from RELEASES.md)
- [ ] Call `task-complete` on this validation orchestration task ({task_id})

## Notes

`validation_report.md` is the handoff document for the next step.

**If all packages have impl tasks (normal case)**: the report is the handoff for `/release-begin-impl-finalize`. Every failure entry must include: task ID, expected vs. actual value, and remediation command. Semantic correctness is NOT in scope — that belongs to `release-begin-impl-finalize` Phase 3.

**If this task was triggered prematurely (PREMATURE_TRIGGER in report)**: the orchestration chain was broken. The impl tasks were never created. Do NOT run `/release-begin-impl-finalize`. Instead: check `plan_path` for the approved task creation plan, then either (a) re-run `python3 scripts/tasks/create_orchestration_task.py --plan-path <plan_path>` to restart the chain, or (b) run `/release-begin-impl` again for the same release (choose "Resume" when prompted).
"""


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def create_orchestration_task(deps: Deps, args: argparse.Namespace) -> int:
    """Execute all steps. Returns exit code."""

    if HAS_FCNTL:
        lock_path = str(Path(__file__).parent / ".create_orchestration_task.lock")
        lock_file = open(lock_path, "w")  # noqa: SIM115, RUF100 -- held open for the duration of the fcntl.flock critical section, closed in finally
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            return _create_orchestration_task_locked(deps, args)
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
            lock_file.close()
    else:
        return _create_orchestration_task_locked(deps, args)


def _create_orchestration_task_locked(deps: Deps, args: argparse.Namespace) -> int:
    """Inner implementation, called while holding the flock."""

    # Step 1 — find active release from RELEASES.md (sole authoritative source)
    version: Optional[str] = None
    releases_path = str(PROJECT_ROOT / "requirements_tasks" / "RELEASES.md")
    if deps.file_exists(releases_path):
        version = parse_release_from_releases_md(deps.read_file(releases_path))
    if not version:
        print("ERROR: No active release found. Set status: active in RELEASES.md first.", file=sys.stderr)
        return 1

    # Step 2 — guard against duplicate.
    # Exclude the --after-task caller: while it runs this create step it is itself a
    # non-terminal orch task. Excluding it lets the chain advance (two-slot alternation);
    # the guard still refuses if a DIFFERENT non-terminal orch task exists.
    existing = find_existing_orchestration_task(deps, exclude_task_id=args.after_task)
    if existing:
        rel_path = Path(existing).relative_to(PROJECT_ROOT)
        try:
            content = deps.read_file(existing)
            m = re.search(r"task_id:\s*(\S+)", content)
            task_id = m.group(1) if m else "unknown"
        except OSError:
            task_id = "unknown"
        print(
            f"ERROR: Orchestration task already exists at {rel_path}\n"
            f"Run `Do {task_id}` to execute it.",
            file=sys.stderr,
        )
        return 2

    # Step 3 — determine batch_tasks and coverage via parse_task_creation_plan.py
    # parse_task_creation_plan.py --next-uncreated-package is the authoritative coverage signal:
    #   exit 0 = returns JSON array of all uncreated tasks for the next package
    #   exit 3 = all plan entries already created (all covered)
    # Without a plan, conservatively default to not-all-covered so we always
    # create an impl task rather than skipping to validation prematurely.
    task_type = args.task_type
    plan_has_uncreated: Optional[bool] = None  # None = no plan or parse failed
    batch_tasks: list[dict[Any, Any]] = []

    if args.plan_path:
        parse_result = deps.run_subprocess(
            [sys.executable, "scripts/tasks/parse_task_creation_plan.py",
             "--plan", args.plan_path, "--next-uncreated-package"],
            cwd=str(PROJECT_ROOT),
        )
        if parse_result.returncode == 0:
            plan_has_uncreated = True
            try:
                batch_tasks = json.loads(parse_result.stdout) or []
            except (json.JSONDecodeError, ValueError):
                batch_tasks = []  # parse failure → fall through to fallback
        elif parse_result.returncode == 3:
            plan_has_uncreated = False
        # other exit codes (1=file not found, 2=parse error): leave plan_has_uncreated as None

    # No plan provided (or parse failed): safe fallback — always create an impl task
    all_covered = not plan_has_uncreated if plan_has_uncreated is not None else False

    if args.dry_run:
        # Dry-run: validate steps 1-3 only, return same exit code without mutations
        if all_covered:
            print(f"DRY-RUN: All packages covered — would create validation task for release {version}.")
        else:
            print(f"DRY-RUN: Uncovered packages found — would create impl orchestration task for release {version}.")
        return 0

    # Step 4 — allocate task ID
    alloc_result = deps.run_subprocess(
        [sys.executable, "scripts/tasks/allocate_task_id.py",
         "--req-id", REQ_ID, "--req-path", REQ_PATH],
        cwd=str(PROJECT_ROOT),
    )
    if alloc_result.returncode != 0:
        print(f"ERROR: Failed to allocate task ID:\n{alloc_result.stderr}", file=sys.stderr)
        return 4

    task_id = alloc_result.stdout.strip()

    # Step 5 — create folder and goal.md
    today = deps.get_today()
    req_commit = get_requirements_commit(deps)
    after_entries = f'"{args.after_task}"' if args.after_task else ""

    # Two-slot alternation: overwrite the terminal predecessor's folder rather than
    # accumulating a third orch-task folder. At most two folders (the live caller +
    # the one we are about to create) exist per release at any time. When no terminal
    # predecessor exists (first link / clean state), create_fresh proceeds untouched.
    predecessor_dir = find_predecessor_slot_dir(deps, args.after_task, version)
    if predecessor_dir:
        deps.remove_dir(predecessor_dir)

    if all_covered:
        # Exit-3 replacement: create validation orchestration task
        task_dir = str(
            PROJECT_ROOT / REQ_PATH / "tasks"
            / f"{today}_explore_validate-release-{version}"
        )
        deps.makedirs(str(Path(task_dir) / "plans_and_protocols"))

        goal_content = _VALIDATION_GOAL_TEMPLATE.format(
            task_id=task_id,
            req_id=REQ_ID,
            today=today,
            version=version,
            req_commit=req_commit,
            after_entries=after_entries,
            plan_path=args.plan_path,
        )
    else:
        # Normal case: create impl orchestration task
        task_dir = str(
            PROJECT_ROOT / REQ_PATH / "tasks"
            / f"{today}_explore_create-impl-tasks-release-{version}"
        )
        deps.makedirs(str(Path(task_dir) / "plans_and_protocols"))

        # Derive batch metadata; fall back gracefully when batch_tasks is empty
        # (defensive: parse succeeded but returned nothing — should not happen if
        # Agent A is correct, but we log a warning and create a placeholder task)
        package_name = batch_tasks[0].get("target_package", "unknown") if batch_tasks else "unknown"
        n_tasks = len(batch_tasks)
        if batch_tasks:
            task_type = batch_tasks[0].get("task_type", args.task_type)
        ac_block = _build_ac_block(batch_tasks, task_id, args.plan_path)

        if not batch_tasks:
            print(
                "WARNING: parse_task_creation_plan.py returned exit 0 but empty batch — "
                "creating placeholder impl orch task.",
                file=sys.stderr,
            )

        goal_content = _GOAL_TEMPLATE.format(
            task_id=task_id,
            req_id=REQ_ID,
            today=today,
            version=version,
            req_commit=req_commit,
            after_field=_build_after_field(args.after_task),
            plan_path=args.plan_path,
            task_type=task_type,
            package_name=package_name,
            n_tasks=n_tasks,
            ac_block=ac_block,
        )

    goal_path = str(Path(task_dir) / "goal.md")
    deps.write_file(goal_path, goal_content)

    # Step 6 — remove reserve marker created by allocate_task_id.py
    reserve_path = str(PROJECT_ROOT / REQ_PATH / "tasks" / f".reserve-{task_id}")
    if deps.file_exists(reserve_path):
        deps.remove_file(reserve_path)

    # Output structured result for the caller
    rel_task_dir = Path(task_dir).relative_to(PROJECT_ROOT)
    print(f"TASK_ID={task_id}")
    print(f"TASK_PATH={rel_task_dir}/goal.md")
    print(f"VERSION={version}")
    if all_covered:
        print("VALIDATION_TASK=true")

    return 0


def main() -> None:
    args = parse_args()
    sys.exit(create_orchestration_task(make_real_deps(), args))


if __name__ == "__main__":
    main()
