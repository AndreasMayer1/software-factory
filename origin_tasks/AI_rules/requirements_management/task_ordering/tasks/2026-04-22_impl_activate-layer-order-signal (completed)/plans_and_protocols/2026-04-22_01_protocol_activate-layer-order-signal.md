# Protocol: Activate layer_order Ranking Signal

**Task**: TASK-PROC-042-06  
**Agent**: session df8d71b8-5982-4797-a573-9ba7f7398798  
**Date**: 2026-04-22

## Baseline (pre-change)

```
Next package: Adaptive Scanner Settings
Completed tasks: 6 | Open tasks: 1

1. [TASK-PROC-042-06] activate-layer-order-signal   unassigned | impl | in_progress | 34 | REQ-PROC-042
2. [TASK-PROC-042-07] add-simulate-cli              unassigned | impl | open       | 34 | REQ-PROC-042
3. [TASK-PROC-042-08] create-propose-after-script   unassigned | impl | open       | 34 | REQ-PROC-042
4. [TASK-FUNC-007-04-08] spike-cleanup              unassigned | impl | pending    | 22 | REQ-FUNC-007-04
5. [TASK-FUNC-006-03] security technical open questions  unassigned | explore | pending | 24 | REQ-FUNC-006
6. [TASK-PROC-029-05] primary-source-research-round unassigned | explore | pending | 24 | REQ-PROC-029
7. [TASK-PROC-027-34] therapy end flow              unassigned | explore | pending | 23 | REQ-PROC-027
8. [TASK-PROC-027-08] backup external storage       unassigned | explore | pending | 23 | REQ-PROC-027
9. [TASK-PROC-027-09] backup incremental            unassigned | explore | pending | 23 | REQ-PROC-027
10.[TASK-PROC-027-10] backup verification mode      unassigned | explore | pending | 23 | REQ-PROC-027
```

Note: Tasks are dominated by priority_override.txt (TASK-PROC-042-06,07,08) and then package scope.

## Changes

### `scripts/next_tasks.py`
- Add `cascade_active`, `factory_urgent` to task dict in `load_tasks()`

### `scripts/task_ordering/ranker.py`
- Import `load_rules`, `classify_layer`, `UNCLASSIFIED`
- Add `_compute_special_flags_weight(task, rules)` helper
- Add `_layer_intra_type_rank(task, layer_name, rules)` helper  
- Add `_enrich_tasks(tasks, rules)` helper
- Call `_enrich_tasks` in `rank_tasks()` and `rank_tasks_by_package()`

### `scripts/task_ordering/defaults.py`
- Update `make_sort_key()` new tuple:
  `(special_flags_weight, is_next, layer_order, layer_intra_type_rank, req_not_active, -priority_score)`

## Bug Fix During Implementation

`classifier.py` had an absolute import (`from scripts.task_ordering.rules import Rules`) that broke
when called via `next_tasks.py` (which adds `scripts/` to sys.path, not the project root).
Fixed to use relative import (`from .rules import Rules`).

## Path Normalization Fix

`_enrich_tasks()` needed to convert absolute task paths to project-relative paths before passing
to `classify_layer()`, because glob patterns in the rule file are relative to the project root.
Fix: use `Path.relative_to(_PROJECT_ROOT)` in `_enrich_tasks`.

## Regression Comparison

**Post-change output (top 10):**
```
1. TASK-PROC-042-06 activate-layer-order-signal  (override) ← unchanged
2. TASK-PROC-042-07 add-simulate-cli             (override) ← unchanged
3. TASK-PROC-042-08 create-propose-after-script  (override) ← unchanged
4. TASK-FUNC-007-04-08 spike-cleanup     impl | prio 22     ← unchanged
5. TASK-PROC-029-05 primary-source-research      explore | prio 24 | factory_process(0)
6. TASK-PROC-027-34 therapy end flow             explore | prio 23 | factory_process(0)
7. TASK-PROC-027-08 backup external storage      explore | prio 23 | factory_process(0)
8. TASK-PROC-027-09 backup incremental           explore | prio 23 | factory_process(0)
9. TASK-PROC-027-10 backup verification mode     explore | prio 23 | factory_process(0)
10.TASK-PROC-027-01 continue scenario generation impl  | prio 44 | factory_process(0)
```

**Shifts from baseline (positions 5-10):**

| Task | Before | After | Verdict |
|---|---|---|---|
| TASK-FUNC-006-03 (explore, REQ-FUNC-006) | #5 | <#10 | ✅ INTENTIONAL |
| TASK-PROC-027-01 (impl, REQ-PROC-027) | <#10 | #10 | ✅ INTENTIONAL |

**Shift explanations:**

1. **TASK-FUNC-006-03 dropped below #10**: This task is in `requirement_exploration` layer (order 50).
   All other explore tasks in positions 5-9 are in `factory_process` layer (order 0). Under the new
   layer_order signal, factory_process (upstream) correctly outranks requirement_exploration (downstream).
   Previously, all explores were treated identically by the `type_rank` signal.

2. **TASK-PROC-027-01 appeared at #10**: This factory_process impl task (priority 44) now correctly
   ranks after factory_process explores (intra_type_rank = 1 vs 0), but before requirement_exploration
   tasks (layer order 0 < 50). Previously it was below explores from any layer due to `type_rank`.

**Assessment**: No unintentional regressions. All shifts reflect correct layer-based ordering
as specified in the design (factory_process upstream of requirement_exploration).

## 2026-04-22T (session log entry)
**Agent**: Main conversation (session df8d71b8-5982-4797-a573-9ba7f7398798)
**Agent ID**: df8d71b8-5982-4797-a573-9ba7f7398798
**Action**: Implemented all ranking signals (layer_order, layer_intra_type_rank, special_flags_weight, cascade_active, factory_urgent). Fixed classifier.py absolute import bug. Added path normalization for absolute→relative path conversion. Ran regression comparison.
**Outcome**: Pass — all AC criteria met, validate_rules.py passes, no unintentional regressions.
**Next Step**: task-complete

