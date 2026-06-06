# Group 3 Implementation Plan: Orchestration Template + task-create-code Plan Mode

**Task**: TASK-PROC-035-08, Group 3
**Date**: 2026-04-25
**Status**: Ready for implementation (blocked on Group 2 commit)
**Files changed**: 2
  1. `scripts/create_orchestration_task.py`
  2. `.claude/skills/task-create-code/skill.md`

---

## Dependency

Group 3 MUST NOT begin until Group 2 is committed. Group 2 adds:
- `--after-task TASK-ID` argument to `create_orchestration_task.py`
- `--plan-path PATH` argument to `create_orchestration_task.py`
- Those values threaded through `create_orchestration_task` function signature

Group 3 builds on top of those changes. The implementation agent must verify:
```bash
git log --oneline -5 scripts/create_orchestration_task.py
```
and confirm the Group 2 commit is present before editing.

---

## Change 3a: `scripts/create_orchestration_task.py`

### What changes

1. `_GOAL_TEMPLATE` — add three new frontmatter fields and replace the Acceptance Criteria section
2. `create_orchestration_task()` function — accept `task_type`, `plan_path`, `after_task` as parameters (Group 2 already adds `plan_path` and `after_task`; Group 3 adds `task_type`)
3. `_build_step1_ac()` helper — returns the correct Step 1 AC line based on `task_type`
4. `_build_after_field()` helper — returns either `after: []` or `after: ["{after_task}"]` (Group 2 may already provide this; Group 3 must verify and keep consistent)
5. `main()` — pass `task_type` through (read from plan if `--plan-path` is given; default to `implement`)

### New `_GOAL_TEMPLATE`

Replace the entire `_GOAL_TEMPLATE` string (currently lines 117–172) with the following.
**Note**: `{step1_ac}`, `{plan_path}`, `{after_field}`, `{task_type}` are new interpolation keys.
`{task_id}`, `{req_id}`, `{today}`, `{version}`, `{req_commit}` are unchanged from the current template.

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
{after_field}
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Orchestration: create next impl task for release {version} ({task_type} mode). One package per execution; chain self-perpetuates."
target_release: "{version}"
plan_path: "{plan_path}"
task_type: "{task_type}"
release_description: ""
opus_recommended: false
requirements_version:
  commit: {req_commit}
  file: ../requirements.md
---

# Goal: Create Next Impl Task for Release {version}

## Objective

Create the next missing implementation task for release {version} using the approved
task creation plan (if set).

## Scope

- **In Scope**: Run the appropriate skill once (zero-parameter), create the next orch task, call `task-complete`.
- **Out of Scope**: Multiple packages per session, validation, implementation of the created task.

## Acceptance Criteria

- [ ] {step1_ac}
- [ ] Run `python3 scripts/create_orchestration_task.py --after-task {task_id} --plan-path {plan_path}` — creates next orch task OR validation task
- [ ] Run `task-complete` on this orchestration task ({task_id})
"""
```

### Interpolation rules for new fields

#### `{after_field}` — the `after:` YAML line

This replaces the hardcoded `after: []` in the old template. Two cases:

```python
def _build_after_field(after_task: str) -> str:
    """Return the after: YAML line for the goal.md frontmatter."""
    if after_task:
        return f'after: ["{after_task}"]'
    return "after: []"
```

Pass `after_field=_build_after_field(after_task)` into `_GOAL_TEMPLATE.format(...)`.

#### `{plan_path}` — path to task_creation_plan.md

- When `--plan-path` was given: use that value verbatim (Group 2 already handles this)
- When not given: empty string `""`
- In the template the field appears as `plan_path: "{plan_path}"` so an empty value
  renders as `plan_path: ""` (valid YAML; task-create-code treats empty string as "no plan")

#### `{task_type}` — implement | verify | scribble | scribble_to_flutter

- Default: `"implement"`
- Source: read from plan entry when `--plan-path` is given (see Python changes below)
- Passed to both the frontmatter field and `_build_step1_ac()`

#### `{step1_ac}` — the first AC line, skill-dependent

```python
def _build_step1_ac(task_type: str) -> str:
    """Return the Step 1 AC text based on task_type."""
    if task_type == "scribble":
        return "Run `ui-create-scribble` skill in zero-parameter mode"
    # implement | verify | scribble_to_flutter all use task-create-code
    return "Run `task-create-code` skill in zero-parameter mode (reads plan_path if set)"
```

### Python function changes in `create_orchestration_task()`

Group 2 already adds `after_task: str = ""` and `plan_path: str = ""` parameters to
`create_orchestration_task()`. Group 3 adds `task_type: str = "implement"`.

**Read task_type from plan when plan_path is given** (insert after plan_path is validated,
before Step 5 folder creation):

```python
# Step 3b — read task_type from plan entry (if plan exists)
# Default task_type is "implement"; overridden by plan's first uncreated entry.
task_type = kwargs.get("task_type", "implement")  # or parameter directly
if plan_path:
    try:
        parse_result = deps.run_subprocess(
            [sys.executable, "scripts/parse_task_creation_plan.py",
             "--plan", plan_path, "--next-uncreated", "--field", "task_type"],
            cwd=str(PROJECT_ROOT),
        )
        if parse_result.returncode == 0 and parse_result.stdout.strip():
            task_type = parse_result.stdout.strip()
    except Exception:
        pass  # fall back to "implement"
```

**Note on `parse_task_creation_plan.py` CLI**: Group 1 defines this script. The CLI
interface needed here is:
```
python3 scripts/parse_task_creation_plan.py --plan PATH --next-uncreated --field task_type
```
which prints the `task_type` field of the next uncreated task entry, then exits 0.
If the plan has no uncreated entries (all created), exits 3 (same as create_orchestration_task
Exit 3 semantics — nothing to do). The implementation agent must verify this CLI exists
in the Group 1 implementation; if it doesn't, the fallback is `"implement"` (safe default).

**Updated `_GOAL_TEMPLATE.format()` call** (Step 5, currently around line 246):

```python
goal_content = _GOAL_TEMPLATE.format(
    task_id=task_id,
    req_id=REQ_ID,
    today=today,
    version=version,
    req_commit=req_commit,
    after_field=_build_after_field(after_task),   # new (Group 2 may partially add)
    plan_path=plan_path,                           # new (Group 2 adds)
    task_type=task_type,                           # new (Group 3)
    step1_ac=_build_step1_ac(task_type),           # new (Group 3)
)
```

**Updated `main()` — pass task_type** (the `--task-type` CLI flag is optional; default `implement`):

```python
# In argument parsing (after Group 2's --after-task and --plan-path):
parser.add_argument(
    "--task-type",
    default="implement",
    choices=["implement", "verify", "scribble", "scribble_to_flutter"],
    help="Task type for the orchestration task (default: implement). "
         "Overridden by plan entry when --plan-path is given.",
)
# ...
sys.exit(create_orchestration_task(
    make_real_deps(),
    after_task=args.after_task,
    plan_path=args.plan_path,
    task_type=args.task_type,
))
```

### Complete rendered examples

#### Example 1: No plan, no after-task (legacy/backward-compat)
```yaml
after: []
plan_path: ""
task_type: "implement"
```
AC Step 1: `Run `task-create-code` skill in zero-parameter mode (reads plan_path if set)`
AC Step 2: `Run `python3 scripts/create_orchestration_task.py --after-task TASK-PROC-035-42 --plan-path `` — creates next orch task OR validation task`

#### Example 2: With plan and after-task, task_type=implement
```yaml
after: ["TASK-PROC-035-07"]
plan_path: "requirements_tasks/.../task_creation_plan.md"
task_type: "implement"
```
AC Step 1: `Run `task-create-code` skill in zero-parameter mode (reads plan_path if set)`

#### Example 3: With plan, task_type=scribble
```yaml
after: ["TASK-PROC-035-07"]
plan_path: "requirements_tasks/.../task_creation_plan.md"
task_type: "scribble"
```
AC Step 1: `Run `ui-create-scribble` skill in zero-parameter mode`

#### Example 4: With plan, task_type=verify
```yaml
after: ["TASK-PROC-035-07"]
plan_path: "requirements_tasks/.../task_creation_plan.md"
task_type: "verify"
```
AC Step 1: `Run `task-create-code` skill in zero-parameter mode (reads plan_path if set)`

### What to remove from the old template

- The `## Notes` section at the bottom (replaced by self-perpetuating ACs — the notes are now redundant)
- The old `## Objective` paragraph that references "The bootstrap rule in `claude-automated-mode`" (bootstrap is being removed in Group 4; replace with the new Objective text shown above)

---

## Change 3b: `.claude/skills/task-create-code/skill.md`

### Two insertions required

#### Insertion 1: Phase 0 Plan-Mode Addition

**Location**: After the current Step 7 of Phase 0 (the line that reads "On confirmation, continue into Phase 1 with the resolved path."), before the `## Phase 1: Understand Requirement` header.

Insert the following as a new unnumbered subsection of Phase 0:

---

```markdown
### Phase 0 — Plan-Mode Override (when orchestration task has plan_path)

After step 7 (or after auto-accept in automated mode), check whether the orchestration
task's goal.md contains a non-empty `plan_path` field.

**How to find the orchestration task goal.md**: The session was routed via `Do [TASK-ID]`.
That task's goal.md path is the session entry point. Read it to extract `plan_path`:

```bash
# The orchestration task goal.md is the one that was routed to.
# Its path follows the pattern:
# requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/[date]_explore_[name]/goal.md
# Read it and extract the plan_path field from YAML frontmatter.
```

**If plan_path is empty or absent**: proceed normally (no change to existing flow).

**If plan_path is non-empty**:

1. Load the plan entry for the package selected in Phase 0 steps 1–5:
   ```bash
   python3 scripts/parse_task_creation_plan.py \
     --plan [plan_path] \
     --package [pkg-id] \
     --format json
   ```
   Output: JSON with fields `task_name`, `covers_acs`, `effort`, `layer`, `after`,
   `task_type`, `implementation_notes`, `opus_recommended`.

2. Use plan entry values as **authoritative defaults** for subsequent phases:
   - `covers_acs` → used as `covers.acceptance_criteria` in goal.md (Phase 3.3c)
   - `effort` → used directly (skip Phase 2.3 estimation)
   - `layer` → used in Scope Overview (Phase 3.3)
   - `after` → used as the dependency list (replaces propose_after.py dependency detection — see §propose_after interaction below)
   - `task_type` → determines routing; if `verify`, pass this context to code-complex at execution
   - `implementation_notes` → appended to goal.md `## Additional Details` section
   - `opus_recommended` → used directly (skip Phase 3.3f evaluation)

3. **Skip Phase 0 step 6** (user confirmation). Print instead:
   ```
   Using approved plan entry: [task_name] for [pkg-id]
     covers_acs: [AC-01, AC-02, ...]
     effort: [M]
     layer: [domain]
     after: [...]
   Proceeding without user confirmation (plan approved).
   ```

4. **In automated mode** (`CLAUDE_AUTOMATED_MODE=1`):
   - Never override plan entry values.
   - If `parse_task_creation_plan.py` exits non-zero or package not found in plan:
     write `question.md` with the error and stop (do not proceed to Phase 1).
   - Mismatch between Phase 0 discovery and plan (e.g. plan says pkg A but ranker says pkg B):
     write `question.md` describing the mismatch, stop.

5. **In interactive mode**: user may explicitly override with `--override-plan` signal.
   On override, revert to standard Phase 0 step 6 confirmation and discard plan defaults.

#### propose_after.py interaction when plan entry exists

- **Do NOT call `propose_after.py`** for full dependency detection. The plan's `after:`
  list is the authoritative cross-task dependency source; re-deriving risks false additions.
- **Do call `propose_after.py`** for the `requirement_then_implementation` heuristic only:
  ```bash
  python3 scripts/propose_after.py \
    --path "[new task folder path]" \
    --metadata '{"type":"impl","parent_requirement":"[REQ-ID]","target_package":"[pkg]"}' \
    --heuristic requirement_then_implementation
  ```
  (The `--heuristic` flag restricts output to one heuristic; if this flag is not yet
  implemented in Group 1's propose_after.py, run normally and filter results to lines
  whose `reason` contains "requirement" — discard the rest.)
- **Merge**: start with plan's `after:` list; append any propose_after results whose
  TASK-ID is not already in the plan's list.
- Write merged list to goal.md `after:` field.

When no plan entry exists (off-plan or plan-less task): call `propose_after.py` normally
with full heuristic set (existing Phase 3.2.5 behavior unchanged).
```

---

#### Insertion 2: Phase 6 — Plan Conformance Check

**Location**: After Phase 4.2 (`### 4.2 Commit` — the `claude-commit` step), before the
`## Output` section header.

Insert the following as a new top-level phase:

---

```markdown
## Phase 6: Plan Conformance Check (skip if no plan_path)

After the commit in Phase 4.2, if `plan_path` was set (from Phase 0 plan-mode override):

```bash
python3 scripts/check_task_against_plan.py \
  --task [task_id] \
  --plan [plan_path]
```

**Exit codes**:
- **Exit 0** — task conforms to plan entry. Proceed silently.
- **Exit 1** — mismatch detected (wrong ACs, wrong effort tier, wrong layer, wrong package).
  - Interactive mode: show the diff output to the user and ask whether to proceed or fix.
  - Automated mode: write `question.md` in the orchestration task's folder:
    ```
    Plan conformance check failed for [task_id].
    Plan: [plan_path]
    Diff:
    [paste check_task_against_plan.py stderr here]
    ```
    Stop (do not call task-complete on the orchestration task).
- **Exit 2** — no plan entry found for this task's package. Skip silently (off-plan task).

**Conformance rules** (what the script checks):
- `target_package`: exact match required
- `covers_acs`: set equality (order irrelevant)
- `effort`: ±1 size acceptable (XS↔S, S↔M, M↔L, L↔XL) — flagged but does NOT block
- `layer`: exact match required
```

---

### Updated Automated Mode checkpoint table

Add two new rows to the existing automated mode checkpoint table in the `## Automated Mode` section:

| Checkpoint | Interactive behavior | Automated behavior |
|---|---|---|
| Phase 0 plan-mode — package vs. plan mismatch | Show mismatch, ask user to confirm or override | Write `question.md` describing mismatch, stop |
| Phase 6 — plan conformance exit 1 | Show diff, ask user to proceed or fix | Write `question.md` with diff, stop |

Insert these rows after the existing `Phase 0.6 — confirm candidate` row (they are extensions of Phase 0 behavior).

### "When auto-accept is NOT safe" bullet addition

In the `## Automated Mode` section, under "When auto-accept is NOT safe", add:
- `parse_task_creation_plan.py` returns non-zero or package not found in plan
- Phase 6 `check_task_against_plan.py` exits 1 (conformance mismatch)

---

## File edit summary

### `scripts/create_orchestration_task.py`

| What | Where | Action |
|------|-------|--------|
| `_build_after_field()` helper | New function, insert before `_GOAL_TEMPLATE` | Add |
| `_build_step1_ac()` helper | New function, insert before `_GOAL_TEMPLATE` | Add |
| `_GOAL_TEMPLATE` | Lines 117–172 (current) | Replace entirely with new template |
| `create_orchestration_task()` signature | After Group 2 adds `plan_path`, `after_task` | Add `task_type: str = "implement"` parameter |
| Plan task_type read (Step 3b) | After Step 3 (uncovered packages check), before Step 4 (allocate ID) | Add |
| `_GOAL_TEMPLATE.format()` call | Step 5, currently ~line 246 | Add `after_field`, `task_type`, `step1_ac` kwargs |
| `main()` argument parser | After Group 2 adds `--plan-path` | Add `--task-type` argument |
| `main()` call to `create_orchestration_task()` | Last line of `main()` | Add `task_type=args.task_type` |

### `.claude/skills/task-create-code/skill.md`

| What | Where | Action |
|------|-------|--------|
| Phase 0 plan-mode override block | After current step 7, before `## Phase 1` header | Insert |
| Phase 6 conformance check | After `### 4.2 Commit`, before `## Output` | Insert |
| Automated mode table rows (2 new) | After `Phase 0.6` row | Insert |
| "Not safe" bullet additions (2) | Under "When auto-accept is NOT safe" | Insert |

---

## Verification criteria

After implementation, verify:

1. `python3 -c "import scripts.create_orchestration_task"` — no import errors
2. `python3 -m pytest scripts/tests/test_create_orchestration_task.py -q` — all pass (if test file exists)
3. Dry-run with `--plan-path` set to a real plan file — `task_type` field appears in generated goal.md
4. Dry-run with no `--plan-path` — `plan_path: ""` and `task_type: "implement"` in generated goal.md, `after: []` in frontmatter
5. `after: ["TASK-PROC-035-XX"]` appears correctly when `--after-task` is set
6. AC Step 1 text is skill-specific for `--task-type scribble` vs `--task-type implement`
7. `skill.md` Phase 0 section reads cleanly — no broken markdown headers
8. `skill.md` Phase 6 section is present between `### 4.2 Commit` and `## Output`
9. Automated mode table has the two new rows

---

## Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| Group 2 not yet committed when agent starts | Agent must check git log for Group 2 commit before editing; if absent, stop and report |
| `parse_task_creation_plan.py` `--package` flag not implemented in Group 1 | Fall back to `--next-uncreated --field task_type`; document the fallback in the code |
| `--heuristic requirement_then_implementation` flag absent from `propose_after.py` | Run full propose_after, filter results client-side to lines whose reason contains "requirement"; log the workaround |
| Template `{plan_path}` contains special characters (backslashes on Windows, curly braces) | `plan_path` is a filesystem path; use forward slashes always; `_GOAL_TEMPLATE.format()` is safe as long as no `{` appears in the path itself — acceptable constraint |
| Old orchestration tasks (pre-Group-3 template) still running during transition | They use old ACs; Case A in claude-automated-mode is still active during transition (Group 4 removes it); no conflict |
| skill.md is a non-code file — no WHY comment standard applies | Per CLAUDE.md §5: WHY comments only in `lib/`, `test/`, `integration_test/`. For skill.md, use inline parentheticals if context needed. The plan-mode override text is self-explanatory by design. |
