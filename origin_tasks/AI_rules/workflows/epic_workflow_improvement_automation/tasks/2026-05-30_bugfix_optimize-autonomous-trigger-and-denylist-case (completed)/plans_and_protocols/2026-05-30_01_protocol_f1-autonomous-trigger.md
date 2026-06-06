---
skills_used:
  - claude-route
  - code-bugfix
  - claude-write-script
  - claude-modify-skill
  - task-complete-bugfix
  - task-complete
  - claude-commit
---

# Protocol — F-1 autonomous optimize-task creation (TASK-PROC-006-18)

- **Agent ID**: adecd24d4ae9cf867
- **Date**: 2026-05-30
- **Scope**: F-1 ONLY. F-2 (deny-list SKILL.md case) was already implemented and
  committed (verified: `create_optimize_task.py::match_deny_list` is case-insensitive
  and `DENY_LIST` carries `SKILL.md`). Not touched.

## Design decisions (resolved before coding)

### Decision 1 — task_id scheme: `TASK-OPT-0-<n>`

- Must satisfy schema pattern `TASK-[A-Z]+-[0-9]+-[0-9]+(-[0-9]+)?` → `TASK-OPT-0-7`
  validates (OPT = `[A-Z]+`, `0` = req-number placeholder, `7` = monotone counter).
- `<n>` is a monotone counter persisted in `.factory/optimize/state.json` under a new
  `optimize_task_seq` key, incremented per created cycle task. Avoids the heavyweight
  `allocate_task_id.py` (which mints reserve markers and needs a requirement path) and
  guarantees folder/id uniqueness without scanning.
- **Why not `TASK-PROC-006-<n>`**: PROC-006 IDs are hand-allocated; reusing that
  namespace would collide with the registry's max-ID logic and future manual
  allocation. The cycle task is ephemeral (created → run → completed each cycle), so a
  separate `OPT` namespace is correct.
- **id_registry / validate_meta impact**: `generate_id_registry.py` filters task IDs
  with `^TASK-(FUNC|NFUNC|PROC)-\d{3}-\d{2}` (lines 458/221) — an `OPT` ID is silently
  skipped (the `if task_id and re.match(...)` guard means no crash, no registry entry).
  Acceptable: the autonomous cycle task is ephemeral and not a tracked requirement task.
  No category enum anywhere rejects `OPT`; schema `type` enum is extended to include
  `optimize` (see (b)).

### Decision 2 — "no optimize task currently pending" detection

- Scan the single known optimize-tasks parent folder
  (`requirements_tasks/.../workflow_improvement_automation/tasks/`) for any `goal.md`
  whose frontmatter has `type: optimize` and `status` in {pending, in_progress}.
- **Why folder scan over a state.json pointer**: robust against a stale pointer (a
  crashed session that created a task but never updated state would otherwise mint
  duplicates forever). The scan is cheap — one shallow `glob` of immediate subdirs'
  `goal.md` (tens of dirs), well under the <2s budget, and only runs when `events/` is
  non-empty (the common case is an empty queue → early return, zero scan cost).
- Idempotency: if such a task exists, the helper no-ops and returns None.

### Decision 3 — cycle-task goal.md location

- `requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/<YYYY-MM-DD>_optimize_cycle-<n>/goal.md`
  — matches the concept (round-3 §2.2 placed it under …/workflow_improvement_automation/tasks/).
  Folder prefix `<date>_optimize_` is consistent with the `_(impl|explore|…)_` naming and
  parses cleanly in `_task_name`.

### Decision 4 — SURFACING (the hard part)

- **Chosen**: make `type: optimize` tasks an early always-eligible class in
  `next_tasks.py`, surfaced *ahead of* the priority-override gate. A non-terminal,
  non-blocked `type: optimize` task is returned immediately (highest precedence),
  before the override-only short-circuit (lines 561–607) can suppress all non-override
  work.
- **Why**: the active `task_ordering_priority_override.txt` makes `next_tasks.py` return
  ONLY override-listed tasks while any are non-terminal. A process-category task with no
  target_package would also never rank on the normal package/release path. Surfacing
  `type: optimize` before the override gate is the minimal, self-contained mechanism —
  it does NOT touch the `task_ordering` ranking engine or the rule YAML, so blast radius
  is confined to one early block in `next_tasks.py`.
- **Precedent**: the concept treats the optimize cycle task as a regular task routed via
  claude-route, "no special handling needed in the orchestrator" — surfacing it like a
  critical-path always-first item is consistent with that (the orchestrator just picks
  what `next_tasks.py` returns).
- **Blast radius**: while an `awaiting:[]`, non-blocked `type: optimize` task exists, it
  preempts everything (including override tasks). This is intended — the optimize cycle
  is short (one event → one downstream task or no-op → completed) and self-clearing.
  Because the cycle task is only created when `events/` is non-empty AND no optimize task
  is pending, at most one exists at a time and it completes quickly, so the preemption
  window is bounded. Once it reaches a terminal status the override/normal ranking
  resumes unchanged. Blocked optimize tasks (none expected, awaiting is []) fall through
  so they cannot deadlock the queue.

## Mechanism (a) — autonomous creation in run_monitors.py

New tier-C helper `scripts/optimize/create_optimize_cycle_task.py`:
- `optimize_task_pending(tasks_dir)` → bool (Decision 2 scan).
- `next_seq(state)` / state bump (Decision 1 counter).
- `create_cycle_task(events_dir, tasks_dir, state_path, now)` → Path|None: if events_dir
  non-empty and not pending, scaffold `goal.md` with `type: optimize`, `awaiting: []`,
  bump+persist counter; else None.
- `run_monitors.run_all` calls it after monitors, inside the same process-boundary
  try/except (a failure is recorded in `errors`, never crashes task-complete). It runs
  only when `written`/queue indicate events exist, so the empty-queue fast path is
  unaffected (<2s preserved).

Distinct from `create_optimize_task.py`: that mints the DOWNSTREAM proposal
(`awaiting:["user-unblock"]`); this mints the AUTONOMOUS CYCLE task (`awaiting: []`)
that, when run, invokes the claude-optimize producer skill which then calls
`create_optimize_task.py`. Comments in both files state the distinction.

## File-by-file changes

1. **NEW `scripts/optimize/create_optimize_cycle_task.py`** (tier B) — the autonomous
   cycle-task scaffolder. `optimize_task_pending()` (folder scan), `_next_seq`/`_persist_seq`
   (state.json counter), `create_cycle_task()` (events-present + not-pending → write
   `type: optimize`, `awaiting: []` goal.md, bump counter). Reads frontmatter via the
   central AC-08 helper (`util.yaml_frontmatter.read_frontmatter`, Path form). sys.path
   gains `scripts/` so `util.*` imports.
2. **`scripts/optimize/run_monitors.py`** — import `create_optimize_cycle_task as cycle`;
   in `run_all`, after the aggregator block and inside the same process-boundary guard,
   call `cycle.create_cycle_task(now=now, events_dir=events_dir)`. Failure recorded in
   `errors`, never crashes task-complete. Empty-queue fast path preserved (helper returns
   early when no events).
3. **`scripts/tasks/next_tasks.py`** — new always-eligible block in `main()` BEFORE the
   priority-override gate: a non-terminal, non-blocked `type: optimize` task is printed and
   returned immediately, preempting override/normal ranking (Decision 4).
4. **`.claude/schemas/goal_metadata.yaml`** — added `optimize` to the `type` enum + extended
   the description.
5. **`.claude/skills/claude-route/SKILL.md`** (via claude-modify-skill) — new step 3c
   shortcut (`type: optimize` → `claude-optimize` immediately) + a match-table row in step 4.
   INDEX.md / factory_flows.md unchanged (claude-route description unchanged; the optimizer
   loop edge already exists; routing is minor-logic per the modify-skill table).
6. **NEW `scripts/tests/test_create_optimize_cycle_task.py`** — creation chain, idempotency,
   empty-queue no-op, resume-after-complete, run_all wiring.
7. **`scripts/tests/test_next_tasks.py`** — `test_optimize_task_surfaces_under_active_override`
   (FAILS pre-change — proves the live surfacing path) + `test_optimize_task_not_surfaced_when_terminal`.
8. **`scripts/tests/test_run_monitors.py`** — three pre-existing tests neutralize
   `cycle.create_cycle_task` (they assert monitor/aggregator behavior, not cycle creation,
   and `main([])` / live-repo monitors would otherwise touch real tasks).

## F-2 status
Already implemented + committed before this task (verified): `match_deny_list` is
case-insensitive and `DENY_LIST` carries `SKILL.md`. Not touched.

## Gate results (`scripts/quality/check_python_gates.sh`)
- G1 lint — PASS
- G2 type — PASS
- G3 tests — PASS (1032 passed, 6 skipped, 5 xfailed)
- G4 no-handrolled — PASS
- G5 print-discipline — PASS

## Tests added
- `test_create_optimize_cycle_task.py::test_creates_one_autonomous_optimize_task`
- `::test_idempotent_while_pending`
- `::test_no_task_when_events_empty`
- `::test_resumes_after_pending_task_completes`
- `::test_run_all_creates_cycle_task_when_events_exist`
- `test_next_tasks.py::test_optimize_task_surfaces_under_active_override` (fails pre-change)
- `test_next_tasks.py::test_optimize_task_not_surfaced_when_terminal`

## Caveats
- **Surfacing preemption**: while a non-blocked `type: optimize` task exists it preempts
  ALL other work (including override tasks). Bounded because at most one exists at a time
  (created only when none pending) and the cycle is short/self-clearing. If a cycle task
  ever got stuck `in_progress`, it would block the queue — same failure mode as a stuck
  override task; the orchestrator's resume path handles in_progress tasks.
- **id_registry**: `TASK-OPT-*` IDs are silently skipped by `generate_id_registry.py`
  (only FUNC/NFUNC/PROC registered). Intentional — ephemeral cycle tasks are not tracked
  requirement tasks.
- **`--type impl` filter**: optimize tasks are excluded under `next_tasks.py --type impl`
  (the filter runs before the optimize block). The default `Do next task` route (no filter)
  surfaces them. Acceptable.
