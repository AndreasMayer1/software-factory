# Opus Analysis: Release "active" Status — Workflow & Bug Investigation

Date: 2026-04-24  
Session: interactive

---

## Objective

Clarify when a release should be set to `status: active` in RELEASES.md, whether setting
it before impl tasks exist is correct, and identify any bugs in the interaction between
the release lifecycle, `next_tasks.py`, and the orchestration task creation mechanism.

---

## Current State (verified by running the scripts)

```
python3 scripts/next_tasks.py          → "No open tasks with a target_package or target_release found."
python3 scripts/check_requirements_ready.py  → "READY: 1 authoring task completed, none pending"
check_ac_coverage.py --package "QR Transfer Send"   → exit 0  (all covered — DONE)
check_ac_coverage.py --package "QR Transfer Receive" → exit 1  (UNCOVERED ACs)
```

**Conclusion**: "QR Transfer Send" is complete (TASK-FUNC-007-04-11 was the last task).
All remaining 0.0.1 packages ("QR Transfer Receive" and onwards) have NO impl tasks yet.
The queue is genuinely empty. The autorun stopping was correct behaviour.

---

## Root Cause Analysis

### Issue 1 — Bootstrap Gap (most important)

The `claude-automated-mode` bootstrap checks for "UNCOVERED ACs" in `next_tasks.py` output.
But `next_tasks.py` only runs `check_ac_coverage.py` for the **current next package** — the
lowest-versioned package that has at least one open task. When **no tasks exist at all**,
`find_next_package()` returns None → no AC coverage check runs → "UNCOVERED ACs" never
appears in output → **Case A never fires**.

Result: The bootstrap cannot detect that 6 packages still need impl tasks.
The autorun stops with `queue_empty` even though a huge amount of implementation work remains.

### Issue 2 — `create_orchestration_task.py` Detection Broken in Package Mode

The script detects the target release in two steps:

```python
# Step 1 (primary): regex on next_tasks.py stdout
version = parse_release_from_next_tasks(output)  # looks for "Next release: X.Y.Z"

# Step 2 (fallback): read RELEASES.md directly
version = parse_release_from_releases_md(...)  # looks for status: active
```

In the new package-based system, `next_tasks.py` outputs `Next package: PKG-xxx`, NEVER
`Next release: X.Y.Z`. So the Step 1 regex **never matches**. The fallback (Step 2) always
fires. The primary detection mechanism is permanently ineffective.

### Issue 3 — Lifecycle Definition Is Misleading

`RELEASES.md` documents:
> `active` — At least one task for this release is `in_progress`

But `requ-prep-release` Phase 6 sets a release to `active` **before any impl tasks exist**,
as the final step that signals "requirements verified, implementation may begin."

The definition describes a *consequence* of impl starting, but in practice the status is
set as a *precondition* for impl. These are different semantics.

### Issue 4 — What the User Did Was Correct (but bypassed the intended gateway)

Setting 0.0.1 to `active` manually was necessary for `create_orchestration_task.py` to work
(Issue 2 means the fallback to RELEASES.md is the only mechanism). The instinct was right.

However, the intended path is: run `requ-prep-release` → it verifies requirements in all
phases → Phase 6 sets `active`. The user skipped this gateway, which is fine when
requirements are already verified — but the gateway also catches gaps.

---

## Recommended Fixes

### Fix 1 — Bootstrap Gap (HIGH PRIORITY)

Add a new Case A-prime to `claude-automated-mode` bootstrap: when `next_tasks.py` returns
"No open tasks" AND `check_requirements_ready.py` exits 0 AND RELEASES.md has an active
release → check ALL packages for the active release for uncovered ACs, and if any found,
call `create_orchestration_task.py`.

Alternatively (simpler): run `create_orchestration_task.py` directly as a fallback whenever
Case A doesn't fire but the queue is empty and an active release exists.

### Fix 2 — `create_orchestration_task.py` Package Mode Support (MEDIUM)

Update `parse_release_from_next_tasks` to also handle:
```
Next package: PKG-ID
```
When this pattern is found: look up PKG-ID in RELEASE_BACKLOG.md, return its
`assigned_release`. This restores Step 1 as the primary mechanism in package mode.

### Fix 3 — Update RELEASES.md Lifecycle Documentation (LOW — cosmetic)

Replace:
> `active` — At least one task for this release is `in_progress`

With:
> `active` — Release requirements are verified and implementation has been approved to begin.
>   Set by `requ-prep-release` Phase 6 (or manually when skipping preparation). Implementation
>   tasks are being created or executed. Do NOT set this before requirements are verified.

---

## Immediate Action Required

The user needs impl tasks for the remaining 6 packages of release 0.0.1. Two options:

**Option A (automated)**: Fix Issue 1 first, then restart autorun → bootstrap creates
orchestration tasks automatically.

**Option B (manual, no code change)**: Run `task-create-code-orchestrator` skill now →
creates one orchestration task → autorun picks it up → creates one impl task per session →
bootstrap iterates until all packages are covered.

Option B is available immediately. Option A requires a code fix first.

---

## Answers to the User's Questions

**Q: Should the release be set to active before impl tasks exist?**
Yes — this is correct and necessary. The lifecycle documentation is wrong, not the practice.
"Active" = "approved for implementation, task creation begins." It is set by `requ-prep-release`
Phase 6 precisely at this moment.

**Q: Do we still need the "active" mechanism with the new next_tasks.py?**
Yes — `create_orchestration_task.py` cannot determine the target release without it (Issue 2
shows the primary detection is broken). Fix 2 would make this more robust, but the RELEASES.md
active status remains the necessary anchor.

**Q: Was the fix needed, or is the system working as designed?**
Issue 1 is a real bug — the autorun cannot self-restart impl task creation when the queue
empties between packages. Issue 2 is a latent bug (harmless as long as RELEASES.md stays
updated). Issue 3 is documentation debt.

---

## Execution Plan (if user approves fixes)

All fixes are small, independent, and low-risk.

### Agent 1: Fix Bootstrap Gap (Issue 1)
File: `.claude/skills/claude-automated-mode/skill.md`
Change: Add handling for the "queue empty + active release + requirements ready" case,
calling `create_orchestration_task.py` directly.

### Agent 2: Fix `create_orchestration_task.py` (Issue 2)
File: `scripts/create_orchestration_task.py`
Change: Update `parse_release_from_next_tasks` to handle "Next package: PKG-ID" by
looking up the package's assigned_release in RELEASE_BACKLOG.md.

### Agent 3: Update Lifecycle Documentation (Issue 3)
File: `requirements_tasks/RELEASES.md`
Change: Update the lifecycle definition text (2-line edit).

All three agents can run in parallel. No tests to write (scripts have their own test files).
Each change should be committed separately for traceability.

---

## Quality Criteria
- [ ] Bootstrap correctly detects uncovered ACs even when task queue is empty
- [ ] `create_orchestration_task.py` correctly identifies target release in package mode
- [ ] RELEASES.md lifecycle definition matches actual workflow semantics
- [ ] `python3 scripts/check_ac_coverage.py --package "QR Transfer Receive"` still exits 1
      (confirming uncovered ACs remain and will trigger orchestration)
- [ ] After fix, running autorun creates orchestration task on first session
