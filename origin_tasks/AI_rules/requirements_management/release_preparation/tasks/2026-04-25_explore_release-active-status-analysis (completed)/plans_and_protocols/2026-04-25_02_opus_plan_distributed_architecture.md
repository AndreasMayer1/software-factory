# Opus Plan: Distributed Release Implementation Architecture

## Objective

Redesign the release-begin-impl workflow so that no single session ever needs
to create more than one implementation task. Instead, the session creates the
scope verification + activation scaffolding, then hands off to the autorun
system. This prevents Claude usage-limit failures on releases with 10+ features
and 100+ tasks.

## Key Finding: Most of the Infrastructure Already Exists

`claude-automated-mode` already has a three-case bootstrap that handles the
full lifecycle:

| Case | Trigger | Action |
|------|---------|--------|
| **A** | Uncovered ACs exist for active release | Create one orchestration task → autorun executes it → creates one impl task |
| **B** | All packages covered, validation not yet run | Create validation orchestration task |
| **C** | Validated, all done | Write completion summary |

The problem is not that the infrastructure is missing — it's that
`release-begin-impl` doesn't hand off to it early enough. It tries to do
Phases 3–5 (feature-level task creation for ALL features) in one session,
bypassing the distributed orchestration entirely.

## Target Architecture

```
User types /release-begin-impl
          │
          ▼
  Session 1: release-begin-impl (scope verification only)
  ┌─────────────────────────────────────────┐
  │ Phase 0: Bootstrap                       │
  │ Phase 1: Package coverage check (agent) │
  │ Phase 2: Epic requirements check (agents)│
  │ Phase 2b: Remediation                    │
  │ Phase 6: Activate RELEASES.md            │
  │          → call create_orchestration_task│
  └─────────────────────────────────────────┘
          │
          ▼ (user runs /autorun or autorun is already running)
          │
  Sessions 2–N: autorun, Case A bootstrap, one per session
  ┌─────────────────────────────────────────┐
  │ Execute orchestration task:              │
  │   task-create-code (zero-parameter)     │
  │   → creates one impl task for next      │
  │     uncovered package                   │
  │   → task-complete on orchestration task │
  │ Bootstrap creates next orchestration    │
  │ task if more packages remain            │
  └─────────────────────────────────────────┘
          │
          ▼ (all packages covered)
  Session N+1: autorun, Case B bootstrap
  ┌─────────────────────────────────────────┐
  │ Create validation orchestration task:   │
  │   Checks AC coverage, after-chains,     │
  │   task graph correctness                │
  │   → task-complete                       │
  └─────────────────────────────────────────┘
          │
          ▼ (validation passes)
  Session N+2: autorun, Case C bootstrap
  ┌─────────────────────────────────────────┐
  │ Write release completion summary        │
  │ → human reviews and runs /release       │
  └─────────────────────────────────────────┘
          │
          ▼ (human, interactive)
  /release-finalize (new skill) — review + handoff
```

---

## What Changes Where

### 1. `release-begin-impl` — Strip to Scope Phase Only

**Remove**: Phases 3, 4, 5 entirely.
**Keep**: Phases 0, 1, 2, 2b, 6.
**Rename Phase 6** to "Activate + Hand Off".

The new Phase 6 end message should be:

> "Release [version] is now active. Orchestration task created.
> **Next**: Run `/autorun` to distribute task creation across sessions.
> Each autorun session creates exactly one impl task per package.
> When all packages are covered, autorun creates a validation task.
> You can do other work — autorun will handle the rest."

Phase 6 still calls `python3 scripts/create_orchestration_task.py`.
If Exit 3 (already covered): confirm coverage and skip to validation.
If Exit 2 (task already exists): just tell user to run `/autorun`.

No Phase 3/4/5 ever runs in `release-begin-impl` again.

**Why remove Phase 3?** Phase 3 was trying to check each feature's
requirements.md (a 200-line file per feature) to see if impl tasks exist,
then create goal.md for missing ones — for all features in parallel, in one
session. With 10 features that's 2000+ lines of requirements read in a
single context. The autorun system already does this one-at-a-time across
sessions via `task-create-code` zero-parameter mode.

**Important note on scope verification**: Phase 2 (epic agents) already
checks that every in-scope AC has a feature-level requirement. That's enough
— it doesn't need to check whether impl tasks exist for every AC. That's the
autorun system's job.

### 2. `create_orchestration_task.py` — Minor Change: No More Exit 3

Currently Exit 3 means "all packages covered — no orchestration task needed".
This is wrong: when all packages are covered, a *validation* orchestration task
should be created instead. The script should handle this.

**Change**:
```python
# Current:
if not has_uncovered_packages(next_tasks_output):
    print("All packages for release X already have impl tasks. No orchestration task needed.")
    return 3  # EXIT 3

# New:
if not has_uncovered_packages(next_tasks_output):
    return create_finalization_task(deps, version)  # creates validation/finalize task, exits 0
```

The finalization task goal.md should say:
```yaml
scope_description: "Finalization: validate impl task graph for release {version}, then run /release-finalize for user review."
```

Its goal.md body:
```markdown
# Goal: Finalize Release {version}

All impl tasks for release {version} have been created by the orchestration loop.

Run `/release-finalize` to:
1. Verify AC coverage across all packages
2. Check task graph correctness (after-chains, layer order, missing dependencies)
3. Present any gaps to the user
4. Update release status

## Acceptance Criteria
- [ ] /release-finalize completed
- [ ] No unresolved AC coverage gaps
- [ ] task-complete called on this task
```

Exit codes become:
- `0`: orchestration task created (impl or finalization)
- `1`: no active release
- `2`: task already exists (unchanged)
- `4`: error (unchanged)
- (Exit 3 retired)

### 3. `claude-automated-mode` — Rationalize Cases A and B

**Case A** already works but uses inline `task-create` logic instead of
`create_orchestration_task.py`. This creates two code paths for the same thing.

**Rationalize**: Change Case A to call `python3 scripts/create_orchestration_task.py`
directly. This keeps the task template in one place (the script) and makes
both interactive and automated modes identical in what they create.

```bash
# Case A (new):
python3 scripts/create_orchestration_task.py
# Exit 0 → orchestration task created, proceed
# Exit 2 → task already exists, go to Case D
# Exit 1/4 → error, surface it
```

**Case B** (validation after all packages covered) currently creates a
heavyweight validation task that checks `check_ac_coverage.py`, after-chains,
opus_recommended flags, etc. This overlaps with what `release-finalize` should
do. **Keep Case B as-is** — it does implementation validation (are tasks wired
correctly?). `release-finalize` does release-level verification (are all ACs
covered by tasks?). They're complementary.

**Case C** currently writes a summary file and lets the orchestrator stop.
**Add**: a signal or message that the user should run `/release-finalize`
for the interactive review and final activation. The case-C summary should
include this instruction.

### 4. New Skill: `release-finalize`

This skill is the user-facing end of the pipeline. It runs interactively,
after autorun has finished creating all tasks and validation has passed.

**Trigger**: User runs `/release-finalize`, OR the finalization orchestration
task (created by the updated script) is picked up by autorun.

**Phases**:

#### Phase 1 — Coverage Verification (spawn 1 agent)
Agent reads STATUS_NEXT_RELEASE.md (re-generated) and checks:
- Every in-scope package has ≥1 impl task
- Report any remaining gaps (unexpected given autorun ran, but check anyway)

Output: `release_finalize_report.md`

#### Phase 2 — Present to User (orchestrator)
Show the user:
- Coverage report summary
- Any gaps requiring decisions (Phase 2 reopeners from the earlier skill run)
- Auto-created task list (from STATUS_NEXT_RELEASE.md)
- **This is the ONLY user gate in the entire distributed flow**

#### Phase 3 — Update Release Status (orchestrator, inline)
If user approves:
- Update RELEASES.md: optionally add a `tasks_created_date` field
- The `status: active` is already set (done by `release-begin-impl`)
- Generate or update `requirements_tasks/STATUS.md`
- Commit (via `claude-commit`)

#### Phase 4 — Hand Off to Release
Print:
> "Release [version] implementation tasks are complete and verified.
> Next step: run `/release` when ready to ship."

---

## Decision: Where Does Phase 3 (feature-level impl task creation) Belong?

**Answer: Nowhere in a skill. Only in the autorun pipeline.**

The old Phase 3 was the skill trying to short-circuit the autorun system.
With the distributed architecture:

- `task-create-code` (zero-parameter mode) already knows how to pick the next
  uncovered package for the active release
- It reads the feature's requirements.md in its own session (not the main context)
- It creates exactly one goal.md per session
- The bootstrap iterates

We don't need to replicate this logic in `release-begin-impl`.

---

## Handling the "I want to see all tasks before committing" Use Case

The user may want to review all created tasks before the release moves forward.
This is the role of `release-finalize` Phase 2. By the time the user runs
`/release-finalize`, all tasks are created and they can review the full list.

If the user wants to review tasks as they're created during autorun, they can
simply pause autorun and read the task folder — no skill change needed.

---

## Two Inconsistencies to Resolve in Passing

1. **`create_orchestration_task.py` vs. Case A's inline `task-create`**: Both
   create orchestration tasks, but with different content templates. After
   this change, Case A calls the script and the duplication is eliminated.

2. **Phase 1 in `release-begin-impl` checks `scope_boundaries.includes`**
   (often empty) instead of checking the `packages:` list. Fix this as part of
   the skill rewrite (covered in the companion plan
   `2026-04-25_01_opus_plan_skill_improvements.md`).

---

## Execution Plan

**Agent count: 3 (can run in parallel)**

### Agent 1 — Rewrite `release-begin-impl`
File: `.claude/skills/release-begin-impl/SKILL.md`

Apply all changes from `2026-04-25_01_opus_plan_skill_improvements.md` PLUS:
- Remove Phase 3 section entirely
- Remove Phase 4 section entirely
- Remove Phase 5 section entirely
- Rewrite Phase 6 with new hand-off language
- Update Key Constraints table (remove Phase 3/4/5 rows)
- Add introductory note: "This skill covers scope only. Task creation
  is handled by autorun. /release-finalize handles post-creation review."

### Agent 2 — Update `create_orchestration_task.py`
File: `scripts/create_orchestration_task.py`

- Add `create_finalization_task(deps, version) -> int` function with new
  goal.md template (see above)
- Replace the Exit 3 branch with a call to `create_finalization_task`
- Update docstring exit codes (retire Exit 3, document new Exit 0 variants)
- Add unit test for the new branch (the file already has test patterns)

### Agent 3 — Create `release-finalize` skill
File: `.claude/skills/release-finalize/SKILL.md`

Write the new skill with the four phases defined above. Ensure:
- Phase 1 agent reads max 3 files
- Phase 2 user gate is clear and non-redundant
- Phase 3 inline edits are minimal
- The skill explicitly says it expects autorun to have completed before it runs

### After all 3 agents complete (orchestrator, inline):
- Update `claude-automated-mode` Case A to call the script instead of
  inline `task-create` (small edit, ~10 lines, orchestrator does it inline)
- Update `claude-automated-mode` Case C summary to mention `/release-finalize`
- Run `python3 scripts/release_readiness.py` to verify the script still works
- Commit everything via `claude-commit`

---

## Quality Criteria

- [ ] `release-begin-impl` has no Phase 3, 4, or 5
- [ ] `release-begin-impl` Phase 6 ends with a clear autorun handoff message
- [ ] `create_orchestration_task.py` creates a finalization task instead of
      returning Exit 3
- [ ] `release-finalize` skill exists with 4 phases
- [ ] `claude-automated-mode` Case A calls the script (no inline task-create)
- [ ] `claude-automated-mode` Case C mentions `/release-finalize`
- [ ] `release_readiness.py` still runs without error after script changes
- [ ] A 100-task release can complete via autorun without hitting usage limits
      (by design: each session creates at most 1 task)

## Risks

- **Risk: `task-create-code` zero-parameter mode may not know which package
  to pick next.** Mitigation: verify `next_tasks.py` correctly identifies
  uncovered packages by `target_package`; the script fix for package→release
  mapping (already applied to `generate_status_overview.py`) may need to be
  applied to `next_tasks.py` as well. Agent 2 should check this.

- **Risk: finalization task created by script is picked up before all impl
  tasks are complete.** Mitigation: the finalization task should have `after:`
  entries pointing to the last orchestration task — but since we don't know
  the last task ID at creation time, use a different guard: the `release-finalize`
  skill itself re-runs `next_tasks.py` in Phase 1 and aborts if uncovered
  packages still exist.

- **Risk: Removing Phase 3 means the skill no longer verifies ACs at the
  feature level before activating.** Mitigation: Phase 2 (epic agents) already
  verifies that feature-level requirements exist for all in-scope ACs. The
  question of whether *impl tasks* exist is deferred to autorun + `release-finalize`.
  This is acceptable: activation means "requirements are ready"; task creation
  proceeds after.
