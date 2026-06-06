# Plan: Group 2 — create_orchestration_task.py + release-begin-impl Rewrite

**Task**: TASK-PROC-035-08 | **Date**: 2026-04-25 | **Author**: Opus (via claude-switch-opus)

**Depends on**: Group 1 scripts must exist (should_use_agents.py, summarize_plan.py).
**Self-contained**: The implementation agent must NOT re-read the protocol. Everything needed is in this file.

---

## Part A: `scripts/create_orchestration_task.py` — 6 Changes

### Overview of Changes

The current script (276 lines) needs these additions:
1. `--dry-run` flag: skip steps 4–6, same exit codes
2. `--after-task TASK-ID` argument: append to `after:` list in goal.md template
3. `--plan-path PATH` argument: add `plan_path: "..."` to template frontmatter
4. `--task-type TYPE` argument: write type-specific Step 1 text in ACs
5. Exit 3 replacement: create validation orchestration task instead of returning 3
6. Concurrency lock: `fcntl.flock` on `.create_orchestration_task.lock`

### Change A1 — Add imports and argparse

**Add to imports block** (after `from typing import Callable, List, Optional`):

```python
import argparse
import fcntl
```

### Change A2 — New `parse_args()` function

**Insert before `make_real_deps()`** (after the module docstring and imports):

```python
def parse_args() -> argparse.Namespace:
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
        choices=["implement", "verify", "scribble", "scribble_to_flutter"],
        help="Task type from plan entry; controls which skill is named in Step 1 AC text.",
    )
    return parser.parse_args()
```

### Change A3 — Update `_GOAL_TEMPLATE`

**Replace the entire `_GOAL_TEMPLATE` string** (lines 117–172) with:

```python
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
after: [{after_entries}]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Orchestration: run task-create-code (zero-parameter mode) for the next missing impl task in release {version}. One package per execution; chain self-perpetuates."
target_release: "{version}"
release_description: ""
task_type: "{task_type}"
plan_path: "{plan_path}"
opus_recommended: false
requirements_version:
  commit: {req_commit}
  file: ../requirements.md
---

# Goal: Create Next Impl Task for Release {version}

## Objective

Run the `{step1_skill}` skill in **zero-parameter (auto-pick) mode** to create the next
missing implementation task for release {version}.

After `{step1_skill}` completes and the impl task is committed, run
`python3 scripts/create_orchestration_task.py --after-task {task_id}{plan_path_arg}` to
create the next orchestration task (or a validation task when all packages are covered).
Then call `task-complete` on **this** orchestration task.

## Scope

- **In Scope**: Run `{step1_skill}` once (zero-parameter), commit the result, create next orch task, call `task-complete`.
- **Out of Scope**: Multiple packages, validation, implementation of the created task.

## Acceptance Criteria

- [ ] {step1_ac}
- [ ] Run `python3 scripts/create_orchestration_task.py --after-task {task_id}{plan_path_arg}` — creates next orch task OR validation task
- [ ] Run `task-complete` on this orchestration task ({task_id})

## Notes

This task is created by `release-begin-impl` Phase 6 or by the self-perpetuating chain.
Intended for automated (unattended) execution. In interactive mode, run via `Do {task_id}`.
"""
```

**Helper: compute `step1_skill` and `step1_ac` from task_type**:

```python
_STEP1_BY_TYPE = {
    "implement":          ("task-create-code",   "`task-create-code` called in zero-parameter mode (reads plan entry if plan_path set)"),
    "verify":             ("task-create-code",   "`task-create-code` called in zero-parameter mode with task_type: verify (reads plan entry if plan_path set)"),
    "scribble_to_flutter":("task-create-code",   "`task-create-code` called in zero-parameter mode with task_type: scribble_to_flutter"),
    "scribble":           ("ui-create-scribble", "`ui-create-scribble` skill invoked for the next UI scribble task"),
}
```

### Change A4 — Validation task goal template

**Add a second template constant** (insert after `_GOAL_TEMPLATE`):

```python
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

- [ ] Run `python3 scripts/check_task_against_plan.py` for each impl task in release {version}; write results to `validation_report.md`
- [ ] Run `python3 scripts/reconcile_after_chains.py --release {version}` (detect only, no --apply); append findings to `validation_report.md`
- [ ] Verify all impl tasks have `target_package` set; list any missing in `validation_report.md`
- [ ] Write `validation_report.md` to the explore task folder for release {version} (path from RELEASES.md)
- [ ] Call `task-complete` on this validation orchestration task ({task_id})

## Notes

`validation_report.md` is the handoff document for `/release-begin-impl-finalize`.
Every failure entry must include: task ID, expected vs. actual value, and remediation command.
Semantic correctness is NOT in scope — that belongs to `release-begin-impl-finalize` Phase 3.
"""
```

### Change A5 — Update `create_orchestration_task` function signature and body

**Replace the entire `create_orchestration_task` function** (lines 179–267) with:

```python
def create_orchestration_task(deps: Deps, args: argparse.Namespace) -> int:
    """Execute all steps. Returns exit code."""

    lock_path = str(Path(__file__).parent / ".create_orchestration_task.lock")
    lock_file = open(lock_path, "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        return _create_orchestration_task_locked(deps, args)
    finally:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()


def _create_orchestration_task_locked(deps: Deps, args: argparse.Namespace) -> int:
    """Inner implementation, called while holding the flock."""

    # Step 1 — find active release
    next_tasks_result = deps.run_subprocess(
        [sys.executable, "scripts/next_tasks.py"],
        cwd=str(PROJECT_ROOT),
    )
    next_tasks_output = next_tasks_result.stdout

    version = parse_release_from_next_tasks(next_tasks_output)

    if not version:
        releases_path = str(PROJECT_ROOT / "requirements_tasks" / "RELEASES.md")
        if deps.file_exists(releases_path):
            version = parse_release_from_releases_md(deps.read_file(releases_path))

    if not version:
        print("ERROR: No active release found. Set up a release first.", file=sys.stderr)
        return 1

    # Step 2 — guard against duplicate
    existing = find_existing_orchestration_task(deps)
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

    # Step 3 — check whether there is anything to do
    all_covered = not has_uncovered_packages(next_tasks_output)

    if args.dry_run:
        # Dry-run: validate steps 1-3 only, return same exit code without mutations
        if all_covered:
            print(f"DRY-RUN: All packages covered — would create validation task for release {version}.")
        else:
            print(f"DRY-RUN: Uncovered packages found — would create impl orchestration task for release {version}.")
        return 0

    # Step 4 — allocate task ID
    alloc_result = deps.run_subprocess(
        [sys.executable, "scripts/allocate_task_id.py",
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
    plan_path_arg = f' --plan-path "{args.plan_path}"' if args.plan_path else ""

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
        task_type = args.task_type
        step1_skill, step1_ac = _STEP1_BY_TYPE.get(
            task_type, _STEP1_BY_TYPE["implement"]
        )
        task_dir = str(
            PROJECT_ROOT / REQ_PATH / "tasks"
            / f"{today}_explore_create-impl-tasks-release-{version}"
        )
        deps.makedirs(str(Path(task_dir) / "plans_and_protocols"))

        goal_content = _GOAL_TEMPLATE.format(
            task_id=task_id,
            req_id=REQ_ID,
            today=today,
            version=version,
            req_commit=req_commit,
            after_entries=after_entries,
            plan_path=args.plan_path,
            task_type=task_type,
            step1_skill=step1_skill,
            step1_ac=step1_ac,
            plan_path_arg=plan_path_arg,
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
```

### Change A6 — Update `main()`

**Replace the `main()` function** (lines 270–275):

```python
def main() -> None:
    args = parse_args()
    sys.exit(create_orchestration_task(make_real_deps(), args))
```

### Docstring update

**Replace the module docstring** (lines 1–13) with:

```python
"""Create an orchestration task to drive iterative impl-task creation for the active release.

Usage:
    python3 scripts/create_orchestration_task.py [--dry-run] [--after-task TASK-ID]
                                                  [--plan-path PATH] [--task-type TYPE]

Exit codes:
    0  task created (or dry-run validated) — prints TASK_ID=, TASK_PATH=, VERSION= to stdout
    1  no active release found
    2  orchestration task already exists (prints path to stderr)
    4  error during task creation

Note: Exit code 3 is retired. When all packages are covered, a validation orchestration
task is created (VALIDATION_TASK=true printed to stdout) rather than returning 3.
"""
```

### Dry-run note — Exit 3 retirement

Exit code 3 is intentionally retired (replaced by creating a validation task). The docstring update above documents this. Any callers that checked for exit 3 (e.g., old `claude-automated-mode` Case B) are removed in Group 4.

---

## Part B: `.claude/skills/release-begin-impl/skill.md` — Full Rewrite

The implementation agent must write the following content **verbatim** to
`.claude/skills/release-begin-impl/skill.md`, replacing all 182 lines of the current file.

```markdown
---
name: release-begin-impl
description: Begin implementation of a release: verify scope, create holistic task plan, activate release, create first orchestration task
tools: "*"
model: inherit
---

> This skill covers scope verification and planning only. Task creation runs in autorun.
> `/release-begin-impl-finalize` handles post-creation review.
> This skill never reads a feature's requirements.md in the orchestrator's main context —
> only Phase 2 epic agents and Phase 2c planner do.

## Inputs

- `release_version`: e.g. "0.0.1" (required)
- `task_path`: path to the release prep explore task folder (for writing questions/ and task_creation_plan.md)

## Decision Domains (Read This Before Anything Else)

Three kinds of questions surface during release prep. Each has a designated
phase. Mixing them up wastes user time and burns context.

| Domain | Examples | Where it belongs |
|--------|----------|------------------|
| Scope — does X belong in this release? | "Transfer Notifications in 0.0.1?", "Move AC-28–36 to 0.2.0?" | Phase 2 ONLY. Once Phase 2 ends, scope is frozen for this iteration. |
| Coverage — does in-scope work have requirements + impl tasks? | "Does feat_pairing have an impl task?" | Phase 2c Planner. Agents create tasks or flag blockers, never scope questions. |
| Investigation — answer obtainable by reading more files? | "Are these 2 open analyze tasks still relevant?", "Does this task cover AC-28?" | Inside the agent. NEVER escalate to user. Read the files first. |

Phase 2b and Phase 2c must NOT contain Scope-domain questions. If a Phase 2c
agent identifies scope ambiguity, it flags it as a Phase 2 reopener — the
orchestrator re-runs Phase 2 for that epic before the plan can be finalized.

## Phase 0 — Bootstrap (you, main context)

1. Ask user: "Are you preparing by package ID or by release version?"
   - By package: ask for package ID (e.g. `PKG-0.0.1-core`)
   - By release: ask for release version (e.g. `0.0.1`)

2. **If by package**:
   Run `python3 scripts/generate_status_overview.py --package [pkg_id]`
   Read `requirements_tasks/RELEASE_BACKLOG.md` — extract package `name`, `description`, version scope.

   **If by release**:
   Run `python3 scripts/generate_status_overview.py --release [release_version]`
   Read `requirements_tasks/RELEASES.md` — extract `scope_boundaries.includes` and `packages:` list.

3. Read `requirements_tasks/STATUS_NEXT_RELEASE.md` — extract all requirements targeting this package/release.
4. Build work list: `(req_id, path, status, has_impl_tasks)` — split into epics vs. features.
5. Record `explore_task_id` (the TASK-ID from this task's goal.md frontmatter — needed in Phase 6).
6. **Check for in-progress prior session**: scan the release_preparation tasks folder for an explore task
   with `target_release` matching the current release AND `status: in_progress`.
   If found, offer: "A prior release-begin-impl session is in progress ([TASK-ID]).
   Resume it, or abandon and start fresh?"
   - Resume: read existing `questions/` folder, count `iteration_NN/` folders, set `current_iteration` accordingly, proceed.
   - Abandon: set prior task `status: cancelled`, start fresh as below.
7. Determine current iteration: count `[task_path]/questions/iteration_NN/` folders; set `current_iteration = count + 1` (zero-padded, e.g. `01`).
8. Create `[task_path]/questions/iteration_[NN]/` folder.

## Phase 1 — Scope Coverage Check (inline or 1 agent)

**First**: call `python3 scripts/should_use_agents.py --release [version]` (or `--package [pkg_id]`).
- Result `orchestrator_direct` (≤30KB and ≤5 files): run the checks below inline.
- Result `agents_required`: spawn 1 agent with the same instructions.

**Checks** (3 checks total):

1. **Package coverage**: every package in the release's `packages:` array has ≥1 requirement assigned via `target_package`.
2. **Includes coverage**: only if `scope_boundaries.includes` is non-empty. Each item maps to ≥1 requirement. If `includes` is empty: valid — `packages:` IS the scope. Note this explicitly in output (do NOT say "nothing to check").
3. **Contradiction check**: any package whose theme appears in `scope_boundaries.excludes` → surface as explicit contradiction.

Files to read (max 3):
- `requirements_tasks/RELEASES.md`
- `requirements_tasks/STATUS_NEXT_RELEASE.md`
- `requirements_tasks/_meta/id_registry.md`

Output: `[task_path]/questions/iteration_[NN]/phase_1/scope_gaps.md`

Output quality standard: file must begin with `## Summary for User` (≤3 bullets + numbered open questions).

## Phase 2 — Epic Agents (spawn 1 per epic, in parallel)

Each agent reads ONLY (max 5 files):
- The epic's `requirements.md`
- Its direct child feature `requirements.md` files
- `requirements_tasks/RELEASES.md`

Each agent checks: do release-scoped trackable items have feature-level requirements?
- If missing feature: write draft requirement content + flag gap.

Output per agent: `[task_path]/questions/iteration_[NN]/phase_2/epic_[REQ_ID]_findings.md`

Each findings file MUST start with a `## Summary for User` section containing:
- 2-3 bullet points max summarizing what was found
- A `### Open Questions` subsection listing decisions the user must make, numbered

**USER APPROVAL GATE**: After Phase 2 completes, tell the user the findings files are ready
and list their full paths under `[task_path]/questions/iteration_[NN]/phase_2/`.
Instruct the user to read the files directly and answer the open questions. Do NOT read the files yourself.
Wait for the user's answers before proceeding to Phase 2b.

## Phase 2b — Remediation (you, main context + spawned agents)

Once the user signals they have answered the Phase 2 questions, read and act on those answers.

### Step 1 — Read user answers (orchestrator reads phase_2/ files only)

Read all files under `[task_path]/questions/iteration_[NN]/phase_2/`. Extract user answers
and dispatch remediation work. Do NOT read underlying requirement files.

### Step 2 — Classify each gap and dispatch agents

For each gap or user-approved action, spawn one agent per work item (parallel where independent).
Pass each agent a self-contained prompt with the exact target file path and draft content.

Work item types:
- **Missing requirement (user approved)**: agent writes new `requirements.md` to given path with draft content.
- **Scope boundary update**: agent updates only the relevant section of `requirements_tasks/RELEASES.md`.
- **Requirement metadata fix**: agent fixes frontmatter of the specific file(s).
- **No action (user said skip)**: log it, no agent spawned.

Each remediation agent reads max 5 files and writes to a pre-assigned output path:
`[task_path]/questions/iteration_[NN]/phase_2b/gap_N/output.md`

If an agent hits a blocker it cannot resolve, it writes questions to
`[task_path]/questions/iteration_[NN]/phase_2b/[topic]_questions.md` and terminates.

### Step 3 — Wait for all agents to complete

Scan for output files at `[task_path]/questions/iteration_[NN]/phase_2b/gap_N/output.md`.
An agent is done when its output file exists. (No agent-ID tracking needed — output-file polling only.)

### Step 4 — Handle blockers and open questions

Check for unanswered question files under `[task_path]/questions/iteration_[NN]/phase_2b/`
(exclude `gap_N/output.md` files).

If unanswered files exist: list their paths to the user, wait for answers.
Once answered: spawn a fresh agent with the answered question + original context. Do NOT resume by agent ID.

Repeat until no open question files remain.

### Step 5 — Proceed to Phase 2c

Only when all phase_2b question files are answered (or none exist): proceed.

## Phase 2c — Task Creation Planner (spawn 1 agent)

Spawn one agent. Agent reads ALL in-scope feature requirements.md files (one Read per file),
plus `requirements_tasks/RELEASE_BACKLOG.md` and `requirements_tasks/RELEASES.md`.

**Large-release mitigation** (if `should_use_agents.py` total bytes >100KB for all feature files):
1. Split into N/2 sub-agents in parallel, each reading half the feature files. Each produces a partial plan.
2. One aggregation agent reads all partial plans and produces the final `task_creation_plan.md`.
For most releases (≤10 features, ≤100KB): single agent suffices.

**Agent task**:
- Optionally call `python3 scripts/check_requirement_implementation.py --requirement [R]` per feature
  to detect already-implemented ACs. ACs with verdict `likely_implemented` → set `task_type: verify`.
- Produce `[task_path]/task_creation_plan.md` (schema: see protocol.md §5).

**Plan must contain**:
- YAML frontmatter: `plan_id`, `release`, `created`, `status: draft`, `explore_task`, `total_tasks`, etc.
- `## Layer Dependency Rules` section
- `## Execution Order` section (ordered package list)
- `## Architecture Notes` section
- `## Planned Tasks` section with per-package `### PKG-...` and per-task `#### Task N:` subsections
- Per task: YAML block with `task_name`, `task_type`, `target_package`, `covers_acs`, `effort`, `layer`, `after`, `opus_recommended`, `req_path`, `req_commit`, `implementation_notes`
- Per task: `**Rationale**:` prose below the YAML block

**Phase 2c must NOT contain Scope-domain questions.** If scope ambiguity is found,
write a "Phase 2 reopener" note to `[task_path]/questions/iteration_[NN]/phase_2c_reopeners.md`
and notify the orchestrator. Orchestrator re-runs Phase 2 for the flagged epic before finalizing.

Output: `[task_path]/task_creation_plan.md`

## Phase 5 — User Gate (you)

1. Run: `python3 scripts/summarize_plan.py --plan [task_path]/task_creation_plan.md`
2. Show the 1-page summary output directly to the user.
3. Also provide paths to:
   - Full plan: `[task_path]/task_creation_plan.md`
   - All findings files: `[task_path]/questions/iteration_[NN]/`
4. Ask the user to read and approve.
5. Wait. Do NOT proceed until the user explicitly says "approved" (or equivalent confirmation).

If user requests revisions: implement or re-run relevant phases as needed, then return to Phase 5.

## Phase 6 — Activate + Hand Off (you)

Only proceed after the user has said "approved" in Phase 5.

### 6.0 — Pre-checks (no mutations)

- Confirm `explore_task_id` is set (recorded in Phase 0 step 5).
- Confirm `[task_path]/task_creation_plan.md` exists.

### 6.1 — Pre-check: dry-run

Run:
```
python3 scripts/create_orchestration_task.py --dry-run --after-task [explore_task_id]
```
- Exit 0: proceed.
- Non-zero: show stderr to user, stop. Do not proceed to mutations.

### 6.2 — Mutation: activate release

**If by release**:
- Read `requirements_tasks/RELEASES.md`
- Update `status: planned` → `status: active` for the target release.
- Do NOT commit yet.

**If by package**:
- Read `requirements_tasks/RELEASE_BACKLOG.md`
- Update `status: planned` → `status: active` for the target package.
- Do NOT commit yet.

### 6.3 — Mutation: create orchestration task

Run:
```
python3 scripts/create_orchestration_task.py \
  --after-task [explore_task_id] \
  --plan-path [task_path]/task_creation_plan.md
```
- Exit 0: note the TASK_ID and TASK_PATH printed to stdout.
- Non-zero: show stderr, stop. Inform user that RELEASES.md was already mutated (step 6.2); they may re-run step 6.3 manually.

Script does NOT commit.

### 6.4 — Mutation: close explore task

Edit `[task_path]/goal.md` inline:
- `status: in_progress` → `status: completed`
- Check all completed ACs (mark `- [x]`)

Do NOT commit yet.

### 6.5 — Atomic commit via task-complete

Call the `task-complete` skill on the explore task (`[task_path]`).
`task-complete` handles: STATUS.md regeneration + ONE atomic commit covering:
- `requirements_tasks/RELEASES.md` (or RELEASE_BACKLOG.md) with active status
- New orchestration task goal.md
- Explore task goal.md with completed status

### 6.6 — Post-success message

Print:
```
Release [version] is now active. Orchestration task [TASK_ID] is ready.
Next: run /autorun to begin distributed task creation, or run `Do [TASK_ID]` manually.
Each autorun session creates exactly one impl task.
```

### Failure Recovery

| Step | Failure | Safe? | Recovery |
|------|---------|-------|----------|
| 6.1 | dry-run fails | Yes | Fix issue, re-run Phase 6 |
| 6.2 | RELEASES write fails | Yes | Re-run Phase 6 |
| 6.3 | script fails | Partial (RELEASES activated, no orch task) | Re-run script manually |
| 6.4 | status edit fails | Yes | Orch task exists but blocked by after-chain; user runs task-complete manually |
| 6.5 | task-complete fails | Yes | Files mutated, uncommitted; `git status` shows all; commit manually |

At no point can the orchestration task execute prematurely (after-chain blocks until explore task is terminal).

## Key Constraints

| Context | Rule |
|---------|------|
| Orchestrator Phase 0 | Max 3 files |
| Phase 1 | Call should_use_agents.py first; inline if ≤30KB/5 files, else 1 agent |
| Each epic agent Phase 2 | Max 5 files; always agents (fan-out) |
| Orchestrator Phase 2b Step 1 | phase_2/ files only |
| Each remediation agent Phase 2b | Max 5 files; output-file polling (no agent-ID tracking) |
| Phase 2c Planner | Always 1 agent (needs full feature context); split if >100KB total |
| Phase 5 | summarize_plan.py output shown directly; no requirement files read |
| Phase 6 | Dry-run before any mutation; all mutations committed atomically by task-complete |

- Never read individual requirements files in the main orchestrator context
- `generate_status_overview.py` replaces bulk requirement reading
- Phase 2c must NOT escalate scope questions to user; write Phase 2 reopeners instead
```

---

## Implementation Instructions for the Agent

### File 1: `scripts/create_orchestration_task.py`

**Read the current file first** (mandatory before Write).

Apply all 6 changes from Part A in sequence. The result is a complete rewrite of the file.
The full file structure after changes:

1. Module docstring (updated — see A, docstring section)
2. Imports block: add `import argparse` and `import fcntl`
3. `PROJECT_ROOT`, `REQ_ID`, `REQ_PATH`, `REQUIREMENTS_FILE` constants (unchanged)
4. `Deps` dataclass (unchanged)
5. `make_real_deps()` (unchanged)
6. `parse_args()` — NEW function (Change A2)
7. Pure parsing helpers (unchanged): `parse_release_from_next_tasks`, `parse_release_from_releases_md`, `has_uncovered_packages`
8. I/O helpers (unchanged): `find_existing_orchestration_task`, `get_requirements_commit`
9. `_GOAL_TEMPLATE` — updated (Change A3)
10. `_STEP1_BY_TYPE` dict — NEW (Change A3, helper)
11. `_VALIDATION_GOAL_TEMPLATE` — NEW (Change A4)
12. `create_orchestration_task(deps, args)` — updated signature + flock wrapper (Change A5)
13. `_create_orchestration_task_locked(deps, args)` — inner logic (Change A5)
14. `main()` — updated (Change A6)
15. `if __name__ == "__main__": main()` (unchanged)

### File 2: `.claude/skills/release-begin-impl/skill.md`

**Read the current file first** (mandatory before Write).

Write the complete new content from Part B verbatim. The new file:
- Has YAML frontmatter (name, description, tools, model)
- Has introductory note paragraph
- Has `## Inputs` section
- Has `## Decision Domains` section with the 3-row table
- Has Phases 0, 1, 2, 2b, 2c, 5, 6 (NO Phases 3 or 4)
- Has `## Key Constraints` table at end
- Does NOT contain `///` Dart-style comments
- Uses inline `(reason)` parentheticals only where context is needed

---

## Verification Checklist (agent runs after writing both files)

- [ ] `python3 scripts/create_orchestration_task.py --help` exits 0 and shows all 4 new arguments
- [ ] `python3 scripts/create_orchestration_task.py --dry-run` exits 0 (or 1 if no active release — that is correct) without creating any files
- [ ] `grep "fcntl.flock" scripts/create_orchestration_task.py` finds the lock call
- [ ] `grep "after_entries" scripts/create_orchestration_task.py` confirms after field interpolation
- [ ] `grep "plan_path" scripts/create_orchestration_task.py` confirms plan_path field interpolation
- [ ] `grep "VALIDATION_TASK" scripts/create_orchestration_task.py` confirms validation task path
- [ ] `grep "task_type" scripts/create_orchestration_task.py` confirms task_type field in template
- [ ] `grep "Exit code 3 is retired" scripts/create_orchestration_task.py` confirms docstring update
- [ ] `grep "Decision Domains" .claude/skills/release-begin-impl/skill.md` finds the section
- [ ] `grep "Phase 2c" .claude/skills/release-begin-impl/skill.md` finds Phase 2c heading
- [ ] `grep "Phase 3\|Phase 4" .claude/skills/release-begin-impl/skill.md` returns nothing (old phases absent)
- [ ] `grep "summarize_plan.py" .claude/skills/release-begin-impl/skill.md` finds Phase 5 reference
- [ ] `grep "6.1\|dry-run" .claude/skills/release-begin-impl/skill.md` finds Phase 6 dry-run step
- [ ] `grep "_agent_state.md" .claude/skills/release-begin-impl/skill.md` returns nothing (pattern removed)
- [ ] `grep "task-complete" .claude/skills/release-begin-impl/skill.md` finds Phase 6.5 reference

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| `_GOAL_TEMPLATE` format fields collide with Python `str.format()` braces in Markdown | Use `{{` / `}}` escaping for any literal braces in the template that are not format fields |
| `fcntl` not available on Windows | Add `try/except ImportError` around `import fcntl`; skip lock on Windows (autorun is Linux-only) |
| `--dry-run` with `--after-task` must not allocate an ID | Confirmed: dry-run returns at Step 3 before Step 4 (allocate_task_id call) |
| Old skill callers checking exit code 3 | `claude-automated-mode` Case B is removed in Group 4; no other callers exist |
| Phase 2b output-file polling: agent writes to wrong path | Pre-assign paths in the spawn prompt; agent must write to exactly `phase_2b/gap_N/output.md` |
| Phase 2c scope-question leakage | Skill explicitly forbids it; reopener file path defined; orchestrator checks for reopeners before Phase 5 |
