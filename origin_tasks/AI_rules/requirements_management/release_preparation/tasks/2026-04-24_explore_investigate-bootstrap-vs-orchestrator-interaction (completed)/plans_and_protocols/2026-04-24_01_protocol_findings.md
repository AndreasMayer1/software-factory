# Protocol: Bootstrap Guard vs. Orchestrator Interaction — Findings

**Date**: 2026-04-24  
**Task**: TASK-PROC-035-04  
**Status**: Complete  

---

## 1. Root Cause

**The bootstrap in `claude-automated-mode` Case A can never fire in a mature project.**

Case A's condition: output of `next_tasks.py` contains "UNCOVERED ACs" **AND** the task list is empty (no numbered task lines).

Case D's condition: any runnable tasks exist → skip bootstrap entirely.

In a mature project, `next_tasks.py` always returns at least one runnable task (e.g. TASK-PROC-027-*, TASK-PROC-029-05 — process/maintenance explore tasks unrelated to the active release). These keep the task list non-empty. Case D fires first and the bootstrap is permanently skipped, so Case A never runs.

**Under what conditions would Case A ever fire?**  
Only if ALL pending tasks are simultaneously completed — impossible in ongoing development with a process backlog.

---

## 2. Original Design Intent vs. Real-World Behaviour

**Intent (as documented in REQ-PROC-035 SEC-05):**  
> "Pending explore tasks — including requirements-authoring or flow-writing tasks — prevent premature task creation."

The guard was designed for an early-stage project where all open explore tasks ARE requirement-authoring tasks for the same release. In that context, waiting for all explore tasks to complete before creating impl tasks makes sense: requirements might still change.

**Oversight:**  
The guard doesn't distinguish between:
- **Requirements-writing explore tasks** (may change the requirements that impl tasks depend on → should block)
- **Unrelated process/maintenance explore tasks** (TASK-PROC-027-*, TASK-PROC-029-05, etc. → should NOT block)

As the project matures, the second category permanently prevents the first category's guard from ever having any effect.

**Additional context from developer (2026-04-24):**  
Two important clarifications that sharpen the fix:

1. **Manual invocation implies user approval.** When `task-create-code-orchestrator` is called manually, the developer has already reviewed the requirements and decided it's safe to create impl tasks. The guard should not apply on the manual path — only on the fully-automated bootstrap path.

2. **`writes_requirements` flag exists.** Each task's `goal.md` frontmatter has a `writes_requirements:` boolean field. The bootstrap can check for pending tasks with `writes_requirements: true` rather than checking for any runnable task. This directly encodes the original guard intent without being overly broad.

---

## 3. Candidate Fix Evaluation

### Fix 1: Narrow Case D (impl-task filter)

**Change**: Case D fires only if there are runnable **impl tasks for the active release** (`next_tasks.py --type impl`).

**Effect**: Bootstrap always runs; Case A fires whenever there are uncovered ACs and no impl tasks queued, even if explore tasks are present.

**Pros**: Simple; minimal change to skill logic.

**Cons**: Completely bypasses the safety guard — even tasks that ARE writing requirements for the active release would no longer block bootstrap. Impl tasks could be created against incomplete requirements.

**Verdict**: Too broad. Discards the valid safety intent.

---

### Fix 2: Scope-filtered Case A (impl-type check)

**Change**: Case A's "task list empty" check is replaced with `next_tasks.py --type impl` returning empty.

**Effect**: Bootstrap fires when uncovered ACs exist and no impl tasks are queued, regardless of explore tasks.

**Pros**: Surgical — only changes the Case A condition.

**Cons**: Same problem as Fix 1 — explore tasks that ARE requirements-authoring for the active release would no longer block. Requirements may still be incomplete when impl task creation fires.

**Verdict**: Better precision but still bypasses the safety intent when requirements-writing tasks are pending.

---

### Fix 3: `writes_requirements` flag filter (RECOMMENDED)

**Change**: Case A's condition uses the `writes_requirements` flag to distinguish blocking from non-blocking explore tasks.

**New Case A condition**:
> Case A fires when:  
> (a) `next_tasks.py` output contains "UNCOVERED ACs"  
> AND  
> (b) no pending/in_progress tasks with `writes_requirements: true` exist for requirements assigned to the active release

**Detection command**:
```bash
# Check for pending tasks that write requirements for active release
grep -rl "writes_requirements: true" requirements_tasks/ --include="goal.md" \
  | xargs grep -l "status: pending\|status: in_progress" 2>/dev/null | head -1
```

If this returns nothing → safe to fire bootstrap (no requirements-writing tasks are pending).  
If it returns results → hold (requirements may still change).

**Pros**:
- Directly implements the original safety intent using existing metadata
- Unrelated process/maintenance tasks (all have `writes_requirements: false`) no longer block
- Requirements-writing tasks still block as intended
- The `writes_requirements` field already exists on all task frontmatter — no schema change needed

**Cons**:
- Requires tasks that write requirements to have `writes_requirements: true` set correctly
- If a task writes requirements but has `writes_requirements: false` (data quality issue), the guard silently fails — but this is already a metadata correctness problem

**Verdict**: Best fit. Implements the exact guard the design intended, using existing infrastructure.

---

### Fix 4: Manual path bypass (complements Fix 3)

**Change**: The `task-create-code-orchestrator` skill, when invoked manually, does not go through the bootstrap guard at all — it creates the orchestration task directly (which it already does). **No change needed here.**

The key insight from the developer: when the skill is invoked manually, the user has already approved. The guard only matters on the fully-automated bootstrap path. The skill already bypasses the guard — it creates the task directly in Steps 4–6 without checking `writes_requirements`. This is correct behaviour. The bootstrap (in `claude-automated-mode`) is the only path that needs the guard.

**Verdict**: No change needed to `task-create-code-orchestrator`. The manual path is already correct.

---

## 4. Recommended Fix: Fix 3

**Summary**: Replace Case A's "task list empty" check with a `writes_requirements: true` pending-task check.

### Exact change locations

#### 4.1 `claude-automated-mode/skill.md` — Case A

**Current wording**:
```
Case A — uncovered ACs, no runnable tasks: If output contains "UNCOVERED ACs" AND task list is 
empty (no numbered task lines found):
```

**Replace with**:
```
Case A — uncovered ACs, no requirements-writing tasks pending: If output contains "UNCOVERED ACs" 
AND no pending/in_progress tasks with `writes_requirements: true` exist:
```bash
WRITES_REQ=$(grep -rl "writes_requirements: true" requirements_tasks/ --include="goal.md" \
  | xargs grep -l "status: pending\|status: in_progress" 2>/dev/null | head -1)
```
If WRITES_REQ is empty → proceed to bootstrap steps 1–2 below.
If WRITES_REQ is non-empty → skip to Case D (a requirements-authoring task is still running).
```

The inner logic (check for existing orchestration task, create if none, then terminate) stays unchanged.

#### 4.2 `requirements_tasks/process/AI_rules/requirements_management/release_preparation/requirements.md` — SEC-05

**Current guard paragraph**:
> Guard: The bootstrap rule only fires when no runnable tasks exist. Pending explore tasks — including requirements-authoring or flow-writing tasks — prevent premature task creation (they appear in `next_tasks.py` output and keep the list non-empty).

**Replace with**:
> Guard: The bootstrap rule only fires when no pending or in-progress tasks with `writes_requirements: true` exist. Explore tasks that author or update requirements for the active release block task creation until they complete. Unrelated process or maintenance explore tasks do not block the bootstrap.

#### 4.3 `automation/MONITORING_CRITERIA.md` — S11 note

**Current note in S11**:
> If `queue_empty` fires during an active release build-out (packages remain uncovered) AND no `automation/release_status/` file exists AND session_outputs show no `[bootstrap-signal]` lines, this may indicate the bootstrap in `claude-automated-mode` failed silently. Treat as WARNING.

**Append** (after the existing note):
> After Fix 3: if `queue_empty` fires with uncovered ACs AND tasks with `writes_requirements: true` are still pending, this is expected behaviour — the bootstrap intentionally holds. No action needed.

#### 4.4 `automation/MONITORING_CRITERIA.md` — S21 (Bootstrap Created Orchestration Task)

**Append** to the S21 note:
> After Fix 3: bootstrap may fire even when explore tasks are in the queue, as long as none have `writes_requirements: true`. This is correct behaviour, not a regression.

---

## 5. Impact Assessment on SEC-05 Wording

Yes — SEC-05 wording needs updating (change specified in section 4.2 above). The current wording incorrectly states the guard is based on "any runnable tasks". After Fix 3, the guard is based on `writes_requirements: true` presence, which better reflects the actual intent.

The rest of SEC-05 (manual path description, completeness signal) needs no change.

---

## 6. Files Not Requiring Changes

- `task-create-code-orchestrator/skill.md` — already correct; manual path bypasses the guard
- `scripts/next_tasks.py` — no changes to ranking logic (out of scope per goal.md)

---

## 7. Note: Naming Discrepancy (Minor)

REQ-PROC-035 SEC-05 references `task-create-impl` but the actual skill is named `task-create-code`. The skills list contains `task-create-code` (confirmed in system context); `task-create-impl` does not exist. SEC-05 has stale naming. Fix 3's SEC-05 update should also correct this: replace `task-create-impl` with `task-create-code`.

---

## 8. Observed Failure Confirmed (Git Evidence)

TASK-PROC-035-03 completed 2026-04-22 at 11:17. Git history shows the next automated sessions
worked on TASK-PROC-042 (intelligent task ordering) — no new TASK-PROC-035-* orchestration task
was ever created. TASK-PROC-042-01 was pending, so Case D fired, the bootstrap was skipped,
and the impl task chain for release 0.0.1 stopped after one iteration.

---

## 9. Developer Refinements (2026-04-24 session)

Three additional insights from the developer that modify the Fix 3 recommendation:

### 9.1 Gap in Fix 3: `writes_requirements: true` check is necessary but not sufficient

Fix 3 checks whether any task with `writes_requirements: true` is currently pending.
**Problem**: A requirement may be incomplete even if no such task is currently pending — because
no `writes_requirements: true` task was EVER created for it. This happens when:
- A requirement was written manually (without a user flow / without `requ-derive-from-flow`)
- No `writes_requirements: true` task was ever allocated for it
- The check sees zero pending tasks and incorrectly concludes "requirements are ready"

**Correct check** (stronger condition):
> At least one task with `writes_requirements: true` must exist AND have status `completed`
> (i.e. requirements authoring was done at least once), AND no task with `writes_requirements: true`
> must be in `pending` or `in_progress` status.

If no `writes_requirements: true` task was ever completed for the active release's requirements,
the bootstrap should hold (requirements may not have been formally authored yet).

**Edge case**: Requirements authored before the `writes_requirements` flag was introduced would
fail this check. These must either be retroactively associated with a completed task, or the check
must include an explicit "grandfathered" bypass mechanism (e.g. a flag on the requirement itself).
This edge case requires further design — it is not resolved in this exploration.

### 9.2 The check must be a deterministic script, not LLM-evaluated

LLM evaluation of preconditions is non-deterministic, token-expensive, and untrustworthy for
gate logic. The bootstrap guard should call a Python script, e.g.:

```bash
python3 scripts/check_requirements_ready.py --release 0.0.1
```

Exit 0 → requirements are ready, proceed to Case A bootstrap.  
Exit 1 → hold, print reason.

The script encapsulates:
- Grep for `writes_requirements: true` tasks and their statuses
- "At least one completed, none pending/in_progress" check
- Any future refinements (grandfathering, release-scoping)

This keeps the LLM skill lean and deterministic for this gate.

### 9.3 Manual path chain also affected

The developer clarifies: when `task-create-code-orchestrator` is called manually, the intent is
that the full chain runs: skill creates ONE orchestration task → autorun executes it → bootstrap
creates the NEXT orchestration task → autorun executes → … until all packages are covered.

The manual invocation starts the chain correctly (one task created). But the chain BREAKS at the
second iteration because the bootstrap (Case D) is blocked by unrelated explore tasks in the queue.

**Implication**: The manual path is NOT "already correct" as stated in the initial finding (section 3,
Fix 4). The statement "manual path bypasses the guard" is true only for the first invocation.
All subsequent iterations in the same chain go through the automated bootstrap and hit the same bug.

**Correction to Fix 4 assessment**: Fix 4 is not "no change needed." The automated continuation
of a manually-started chain must also work. Fix 3 (or Fix 3 + script) must fix both the
fully-automated case and the continuation of manually-started chains.

---

## 10. Revised Recommended Fix

**Fix 3 revised**: Replace Case A's empty-list check with a call to a new script
`check_requirements_ready.py`, which checks:
1. At least one `writes_requirements: true` task for the active release has `status: completed`
2. No `writes_requirements: true` task for the active release has `status: pending` or `in_progress`

**New task needed**: Create an `impl` task to:
1. Write `scripts/check_requirements_ready.py`
2. Update `claude-automated-mode/skill.md` Case A to call the script
3. Update `REQ-PROC-035 SEC-05` wording
4. Update `MONITORING_CRITERIA.md` S11, S21 notes

The edge case of requirements authored before the flag existed must be addressed in the script
design (out of scope for this exploration — flag for the impl task).

---

## 11. Summary

| Item | Finding |
|------|---------|
| Root cause | Case D (any runnable tasks) permanently preempts Case A in mature projects |
| Git evidence | Chain broke after TASK-PROC-035-03 (2026-04-22); TASK-PROC-042 tasks blocked Case A |
| Design intent | Guard was correct in principle but too broad — any task blocked it, not just requirements-writing tasks |
| Fix 3 gap | Checking "no pending writes_requirements tasks" is not enough — must also confirm at least one was COMPLETED |
| Script requirement | Guard check must be a deterministic Python script (`check_requirements_ready.py`), not LLM-evaluated |
| Manual path chain | Also affected: second+ iterations of manually-started chains go through bootstrap and hit the same bug |
| Recommended fix | Fix 3 revised: Case A calls `check_requirements_ready.py` (exit 0 = proceed, exit 1 = hold) |
| New impl task needed | Write script, update skill, update requirement wording, update monitoring criteria |
| Files to update | `claude-automated-mode/skill.md`, `release_preparation/requirements.md` (SEC-05), `MONITORING_CRITERIA.md` (S11, S21), new `scripts/check_requirements_ready.py` |
