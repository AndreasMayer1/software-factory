# Protocol: target_package Propagation Gap for Impl Tasks
**Task**: TASK-PROC-030-06
**Date**: 2026-04-02
**Status**: Investigation complete — fix proposal ready

---

## 1. Prior Session Context

Commit `347ede85` already addressed a related but distinct issue:

> `requ-explore` was back-propagating `target_package` onto `source_gap` goal.md files
> after AC package assignment.

Fix applied in `requ-explore` Phase 2.4:

```
4. **Do NOT back-propagate to the originating task**: If the goal.md that triggered
   this exploration has `source_gap:` in its frontmatter, never write or update
   `target_package` on that goal.md file — even if packages were just assigned to the
   requirement's ACs.
```

This was **over-propagation** (unwanted propagation to flow-derived explore tasks). The current task addresses **under-propagation** (needed propagation to impl tasks that was never implemented).

---

## 2. Gap Confirmation

### AC-01: Gap confirmed with concrete trace

**Full trace: `requ-explore` → deferred packages → `task-create-impl` → batch assignment → `next_tasks.py`**

**Step 1**: `requ-explore` runs on a new requirement (Phase 2.4, Package Assignment).
User defers: "skip / let's wait" for some ACs.
Result: requirement YAML written with ACs that have no `target_package`.

```yaml
# requirement's trackable_items — after deferred assignment
trackable_items:
  acceptance_criteria:
    - id: AC-01
      target_package: "Transfer Data Model"   # assigned
    - id: AC-02
                                            # no target_package — deferred
    - id: AC-03
                                            # no target_package — deferred
```

**Step 2**: `task-create-impl` is called for this requirement.
In Section 3.4 (Package Inheritance), Rule 3 fires:
> "Some items unassigned or `covers` is empty: Prompt user — 'Covered items have mixed/no
> package assignments. Which package should this task target?'"

User skips (same reason as before).
Result: impl task created with no `target_package` in its goal.md YAML.

**Step 3**: Later, batch package assignment runs — user re-runs `requ-explore` or manually
assigns packages to the requirement's ACs.
`requ-explore` Phase 2.4 updates the requirement's YAML — AC-02 and AC-03 now have
`target_package: "Transfer Data Model"`.

**Step 4**: The already-created impl task's goal.md is NOT touched.
It still has no `target_package`.

**Step 5**: `next_tasks.py` calls `rank_tasks_by_package()`.
The task has `t.get("target_package") == None`, so it is never included in
`packages_with_open` for the "Data Transfer Core" package context.
The task is deprioritized to the bottom of the unassigned bucket — effectively invisible.

**Verdict: Gap confirmed.**

### AC-02: All staleness scenarios identified

| # | Scenario | How it manifests | Frequency |
|---|----------|-----------------|-----------|
| S1 | `task-create-impl` before AC package assignment, user skips | Task has no `target_package` permanently | Primary confirmed gap |
| S2 | Task covers ACs from 2 packages; one AC later reassigned to different package | Task `target_package` points to old earliest package | Low — requires manual re-assignment of ACs |
| S3 | Task created with `covers: {acceptance_criteria: [], sections: []}` (no explicit coverage), user skips | No `target_package` since Rule 3 fires for empty covers | Medium — common during early task creation |
| S4 | AC package changed via `requ-explore` update, existing task not synced | Task `target_package` stale | Low — only when requirements are updated post-task |

S1 and S3 are by far the most common. S2 and S4 are edge cases.

---

## 3. Fix Proposals

### Option A: Block `task-create-impl` until all covered ACs have `target_package`

**Location**: `.claude/skills/task-create-impl/skill.md`, Section 3.4 Rule 3

**Change**: Replace the "Prompt user" behavior with a hard stop:
> "If any covered AC has no `target_package`, STOP. Require user to assign packages
> to the parent requirement first (via `requ-explore`), then retry."

**Assessment**: **Too disruptive.**
- The current workflow intentionally supports creating tasks before packaging is finalized.
- Package assignment belongs to `release-plan`, which may not have run yet when tasks are created.
- A hard block would prevent legitimate early task creation for requirements under active development.

### Option B (recommended): Sync covering impl tasks in `requ-explore` Phase 2.4

**Location**: `.claude/skills/requ-explore/skill.md`, Phase 2.4 Step 2

**Change**: After all trackable items in a requirement are assigned packages (at the end of
Phase 2.4 Step 2), add a new sub-step:

```
3. **Sync covering impl tasks**: After package assignment is complete for this requirement:
   a. Grep for goal.md files under [requirement_folder]/tasks/*/goal.md whose
      covers.acceptance_criteria or covers.sections reference any updated AC/section IDs
   b. Skip tasks with source_gap: or verification_task: true frontmatter fields
      (these are managed separately — see existing guard in Phase 2.4 Step 2.4)
   c. For each impl/bugfix task found:
      - Read its covers.acceptance_criteria and covers.sections
      - For each covered item, look up its target_package from the parent requirement's
        current YAML (just updated)
      - Recompute task target_package as earliest-versioned package (same semver rule as Step 2)
      - If computed value differs from task's current target_package (or is now set where
        it was previously absent): update the target_package field in the task's goal.md
      - Log: "Synced target_package in [task_path]: [old or absent] → [new]"
```

**Why this is the best fit**:
- Runs automatically at the natural point where AC packages change
- Limited scope: only affects tasks covering the modified requirement
- Idempotent: re-running produces the same result
- Consistent with existing skill design (no new commands, no new scripts required)
- Heals S1, S3, S4 automatically

**Does NOT heal**: S2 after the fact (requires a separate repair pass). But S2 would be caught the next time `requ-explore` is run for that requirement.

### Option C: Standalone script `scripts/sync_task_packages.py`

**New file**: `scripts/sync_task_packages.py`

**Args**: `[requirement-path]` (optional; scans all requirements if omitted), `[--dry-run | --apply]`

**Logic**:
1. For each `requirements.md` found (under given path or all of `requirements_tasks/`):
   - Read `trackable_items.acceptance_criteria` and `trackable_items.sections`
   - For each such item, extract its `target_package` (if any)
2. For each `tasks/*/goal.md` under the same requirement folder:
   - Read `covers.acceptance_criteria` and `covers.sections`
   - Skip if `source_gap:` or `verification_task: true` present
   - Compute `target_package` from earliest-versioned covered item
   - If different from current: update (or report in dry-run)

**Assessment**: Useful as repair tool for already-orphaned tasks. Not sufficient alone — requires user to remember to run it. Good complement to Fix B.

---

## 4. Recommendation

**Two deliverables** (Option B and C combined):

**Deliverable 1: `scripts/sync_task_packages.py`**
The script does all the work — finds covering impl tasks for a requirement and writes their
`target_package` based on the requirement's current AC assignments. Reusable for both
automated and manual repair use cases.

**Deliverable 2: One-line addition in `requ-explore` Phase 2.4**
After package assignment runs, call the script:
```
python3 scripts/sync_task_packages.py --requirement [requirement_folder_path] --apply
```
No logic duplication. The skill delegates entirely to the script.

**Warning improvement in `task-create-impl`**: Dropped. No meaningful benefit, wastes tokens.

---

## 5. Specific Edit Locations

### Deliverable 1 — New script

**File**: `scripts/sync_task_packages.py`

**Interface**:
```
python3 scripts/sync_task_packages.py [--requirement PATH] [--dry-run | --apply]
```
- Without `--requirement`: scan all `requirements_tasks/`
- `--dry-run` (default): report what would change without writing
- `--apply`: write changes

**Logic**:
1. For each `requirements.md` under the given path (or all of `requirements_tasks/`):
   - Read `trackable_items.acceptance_criteria` and `trackable_items.sections`
   - Build a map: `item_id → target_package`
2. For each `tasks/*/goal.md` under the same requirement folder:
   - Read `covers.acceptance_criteria` and `covers.sections`
   - **Skip if both are empty** — the task has no concrete AC/section coverage
     (this naturally skips flow-derived explore tasks with `source_gap:`, explore tasks
     whose goal is to write/extend the requirement itself, and verification tasks —
     all of which have no `covers` entries. No explicit type or frontmatter checks needed.)
   - For each covered item, look up its `target_package` from the map
   - Compute `target_package` as earliest-versioned package (semver, using RELEASE_BACKLOG.md for version lookup)
   - If computed value differs from current `target_package` (or absent → now set): update in goal.md
   - Report: "[path]: [old or absent] → [new]" (or "[path]: unchanged")

**Code reuse** from `scripts/migrate_target_release_to_package.py`:
- `split_frontmatter()`, `FRONTMATTER_RE`
- `earliest_package()`, `semver_tuple()`, `_parse_semver()`

### Deliverable 2 — `requ-explore` Phase 2.4

**File**: `.claude/skills/requ-explore/skill.md`

**Section**: `### 2.4 Release Chunk + Package Assignment → Step 2 — Package Assignment`

**Insert after**: The existing note 4 ("Do NOT back-propagate to the originating task",
added in commit 347ede85), before the YAML structure example block.

**New content** (note 5):
```
5. **Sync covering impl tasks**: After assigning packages to all items in this requirement,
   run:
   ```bash
   python3 scripts/sync_task_packages.py --requirement [path-to-requirement-folder] --apply
   ```
   This updates `target_package` in any task (impl, bugfix, or explore) whose `covers`
   references the requirement's ACs. Tasks with empty `covers` are automatically skipped
   (covers flow-derived explore tasks, requirement-writing explore tasks, and verification
   tasks — all have no concrete AC coverage). Log the script output to the user.
```

---

## 6. Acceptance Criteria Status

- [x] **AC-01**: Gap confirmed with concrete trace (see Section 2)
- [x] **AC-02**: Fix proposal written to plans_and_protocols/ (this file, Section 3–5)
- [x] **AC-03**: Specific edit locations identified (Section 5)
- [x] **AC-04**: Script scope defined (Section 5, Deliverable 1)

---

## 7. Next Steps

Two implementation tasks to create:

1. **impl**: Create `scripts/sync_task_packages.py`
   *Effort*: S (~150 lines, reusing patterns from migrate_target_release_to_package.py)

2. **impl**: Add script call to `requ-explore` Phase 2.4 Step 2, note 5
   *Target file*: `.claude/skills/requ-explore/skill.md`
   *Effort*: XS (~5 lines)
