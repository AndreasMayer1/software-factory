# Analysis: Task Creation Model — Upfront vs Sequential

**Date**: 2026-04-27
**Author**: Opus (analysis), prompted by user (Andreas)
**Status**: draft / discussion document — no code changes yet

---

## Context

Two systems disagree about *when* implementation tasks should exist:

- **REQ-PROC-035** (Release Preparation) defines a **self-perpetuating orchestration chain** — one impl task created per autorun session, materialized just-in-time from `task_creation_plan.md`.
- **`next_tasks.py` + `check_ac_coverage.py`** raise an "UNCOVERED ACs — DEPENDENCY GRAPH INCOMPLETE" warning, implying all impl tasks should exist *before* any implementation runs.

Today's run surfaced exactly that warning even though `TASK-PROC-035-12` (the orchestration task that *will* create the next impl task) is sitting at rank #2 — i.e. the system is healthy by design, but the diagnostic is calling foul.

---

## What I read

- `requirements_tasks/process/AI_rules/requirements_management/release_preparation/requirements.md` (REQ-PROC-035)
- `requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md` (REQ-PROC-042)
- `requirements_tasks/.../tasks/2026-04-26_explore_create-impl-tasks-release-0.0.1/goal.md` (live orch task)
- `requirements_tasks/.../tasks/2026-04-25_explore_release-begin-impl-0.0.1 (completed)/task_creation_plan.md` (the actual upfront plan)
- `scripts/check_ac_coverage.py`
- `scripts/create_orchestration_task.py`
- `scripts/next_tasks.py` (full AC-coverage section, lines 614–645)
- `scripts/parse_task_creation_plan.py` (header + CLI)

---

## Key discovery — there's a real bug, not just a design clash

`next_tasks.py` lines 617–624 *already* guards the warning:

```python
open_explore_for_package = any(
    t for t in tasks
    if t.get("target_package") == next_package
    and t["type"] == "explore"
    ...
)
if not open_explore_for_package:
    # show warning
```

The intent is: *"If an open explore task exists for this package, suppress the warning — that explore is the mechanism that will produce the missing impl tasks."* That intent matches Model B.

But orchestration tasks have **no `target_package`** field — they carry `target_release` only (because they create tasks across all packages of the release). So the guard returns `False` for the active package, and the warning fires.

The two systems aren't *philosophically* in conflict — the guard already encodes Model B's assumption. The conflict is a **scope mismatch in one boolean check**.

---

## Pro/Con: Model A vs Model B

### Model A — Upfront task creation
*All impl task files (goal.md) are written in one bulk operation at the end of `release-begin-impl` Phase 6.*

**Pros**
- Coverage check is meaningful and trustworthy at any moment — no false positives.
- STATUS.md and `next_tasks.py` show the complete release picture from day one.
- Easy to parallelise impl across multiple sessions/agents — independent tasks can be picked up concurrently.
- After-chains and `target_package` are committed atomically — no `reconcile_after_chains.py` round at the end.
- Simpler mental model — no orchestration task layer; the task list contains real work only.
- Easier release effort estimation (count the tasks, sum the efforts).
- Recovery from a broken pipeline is trivial — there's no "chain" to repair.

**Cons**
- One Phase 6 session must write ~12 task folders + goal.md files + atomic commit. Token-heavy and risks hitting output/context limits.
- ID allocation must succeed for all tasks atomically — more surface area in one session.
- Just-in-time learnings are lost: if impl task #1 reveals the plan was wrong for impl task #5, you must edit/cancel/recreate task files.
- If the user revises the plan mid-release, many task files must be reconciled in bulk.

### Model B — Sequential orchestration chain (status quo)
*Each autorun session creates exactly one impl task, then closes itself; the next session creates the next one.*

**Pros**
- Each session is focused, small, autorun-friendly — no risk of bulk-write context blowups.
- Just-in-time materialisation: each new task can absorb anything learned by previous impl tasks.
- Plan revisions are cheap — only un-materialised entries need re-touching.
- Self-perpetuating; no external scheduler needed.
- Works gracefully under interruption — the chain resumes from the next un-completed orch task.

**Cons**
- Coverage check (`check_ac_coverage.py`) returns false positives by design — the dependency graph is *intentionally* incomplete mid-flight (this is the live bug).
- Cannot parallelise impl across sessions — sequential materialisation forces one-at-a-time execution.
- ~5 min orchestration overhead per impl task (orch session = read goal, run script, commit, close) — for a 12-task release that's ≈1 hour pure orchestration overhead.
- Pollutes task list / git history with orchestration tasks (12 orch + 12 impl = 24 entries instead of 12).
- After-chain reconciliation has to happen at the end (`release-begin-impl-finalize` Phase 2).
- Recovery from a broken chain (e.g. `create_orchestration_task.py` crash) requires manual intervention — `release-begin-impl` resume path documented but rarely exercised.

### Hybrid candidates worth naming

- **B-fixed**: Keep B's sequential chain but make the coverage check chain-aware (read `task_creation_plan.md` and treat un-materialised plan entries as covered-by-plan). Also widen the guard to recognise orch tasks with `target_release == active_release` for the active package. **Smallest possible fix; preserves all existing infrastructure.**
- **A-bulk-from-plan**: Phase 6 of `release-begin-impl` materialises all plan entries in one go using `parse_task_creation_plan.py` + a new `bulk_create_tasks_from_plan.py`. Drop the orchestration chain entirely. Plan is the single source of truth; tasks are derived artefacts.
- **A-batched**: Materialise in batches sized by package or layer (e.g. all "domain" layer tasks at once, then all "data" tasks once domain is partially complete). Compromise between A's atomicity and B's just-in-time.

---

## Recommendation

**Pick B-fixed for now. Track A-bulk-from-plan as a follow-up if pain accumulates.**

Reasons:

1. **The plan file already provides the upfront contract.** `task_creation_plan.md` is the real "upfront task list" — concrete enough to be authoritative for ordering, dependency, and coverage decisions. The materialised goal.md files are a derived artefact. So Model B isn't *philosophically* sequential — only its *materialisation* is. Bringing the coverage check up to that abstraction layer dissolves most of the pain.

2. **The fix is small and low-risk** — two surgical changes (below) — vs. A which requires rewriting `release-begin-impl` Phase 6 and removing `create_orchestration_task.py`.

3. **B's just-in-time advantage is real for this project.** Releases are small (12-ish tasks), but learnings from impl task #1 *do* often shift the rest of the plan — the plan revision history of release 0.0.1 confirms that. A would require those revisions to touch many committed task files.

4. **The orchestration-overhead cost (~1 h per release)** is annoying but tolerable, and at least partially recoverable later by collapsing several plan entries per orch session (a small B-variant).

5. **Parallelisation isn't actually used today**, so A's parallelism advantage is unrealised. If the user starts running multiple autoruns in parallel, that calculus changes — revisit then.

### Concrete fix (B-fixed)

**Change 1**: `scripts/next_tasks.py` (around line 617)

Widen the guard so an orchestration task for the *active release* counts as "explore covering this package":

```python
def _is_orch_for_active_release(t, active_release):
    return (
        t["type"] == "explore"
        and t.get("target_release") == active_release
        and str(t.get("scope_description", "")).startswith("Orchestration:")
        and t["status"] not in EXCLUDED_STATUSES
    )

open_coverage_mechanism = any(
    t for t in tasks
    if (
        (t.get("target_package") == next_package and t["type"] == "explore"
         and t["status"] not in EXCLUDED_STATUSES and not is_blocked(t, completed_ids, known_ids))
        or _is_orch_for_active_release(t, active_release)
    )
)
if not open_coverage_mechanism:
    # … existing warning …
```

**Change 2** (optional, defensive): `scripts/check_ac_coverage.py`

Add a `--plan PATH` option that treats plan entries (whether materialised or not) as covering ACs. Caller passes the active release's `task_creation_plan.md` path. Without `--plan`, behaviour is unchanged.

**Change 3** (documentation): REQ-PROC-035 — add a sentence to "Task Creation Process" stating that an open orchestration task is the authoritative coverage mechanism while the chain is mid-flight. Cross-reference REQ-PROC-042's ranking signals.

---

## Open questions for the user

1. **Pain threshold**: Is the ~1 h/release orchestration overhead bothering you, or is it fine?
2. **Parallel impl**: Do you want to run more than one impl session at a time? If yes, A becomes much more attractive.
3. **Plan churn**: How often does the plan revise mid-release? If rarely, A's downside shrinks.
4. **STATUS.md visibility**: Do you currently look at STATUS.md mid-release and feel misled by the missing tasks? If yes, A's full-picture argument is stronger.

Your answers to (1)–(4) determine whether B-fixed is enough or whether we should plan A-bulk-from-plan as a follow-up.
