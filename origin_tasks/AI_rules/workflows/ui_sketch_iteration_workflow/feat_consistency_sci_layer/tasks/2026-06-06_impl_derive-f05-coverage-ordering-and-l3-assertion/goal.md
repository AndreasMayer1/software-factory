---
task_id: TASK-PROC-032-05-02
type: impl
parent_requirement: REQ-PROC-032-05
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: pending
effort: L
created: 2026-06-06
skill_chain_depth: 4
synthesis_dependent: true
synthesis_justification: "Must hold coverage ordering model, L3 assertion logic, and ordering-rule edits across multiple skills/scripts in one coherent design."
after: [TASK-PROC-032-06-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-07, AC-09]
  sections: []
scope_description: "Implement flow→scribble coverage report, auto task_type:scribble for presentation/both ACs, task-ordering soft-pref for primary forward entry path, L3 coverage assertion + chain-length alert, graph-stats dump (E3 probe)."
release_description: "Adds scribble coverage ordering and L3 assertion to enforce presentation-layer task sequencing."
opus_recommended: true  # reason: cross-cutting invariant — coverage ordering spans new report script + skill edits + ordering rules; cross-slice after T-C1 (REQ-PROC-035) not yet derived
requirements_version:
  commit: 85ed6d20
  file: ../requirements.md
---

# Goal: Implement Coverage/Ordering and L3 Assertion (T-C13)

## Objective

Implement the flow→scribble coverage/ordering machinery (PROP-9/11) and L3 assertion. Specifically:

1. **Coverage report** (`scripts/quality/check_scribble_coverage.py`, new): resolves for each AC whether a scribble covers it (functional + chrome-owning non-functional), advisory output, graph-stats dump (E3 probe).
2. **Auto task_type:scribble**: `task-derive-from-requ` auto-sets `task_type: scribble` for presentation/both-layer ACs.
3. **Task-ordering soft-pref**: ordering rules emit a soft preference placing the primary forward entry-path scribble task before downstream coding tasks; depth-1, basis resolution.
4. **L3 coverage assertion**: detects missing L3 entries and emits a chain-length alert when the L3 chain exceeds the configurable threshold.

Skills/scripts: `claude-modify-skill` (task-derive-from-requ) + `claude-modify-ordering-rules` + `claude-write-script` (new coverage script).

**CROSS-SLICE dependency**: this task logically depends on the REQ-PROC-035 spine task implementing T-C1 (--scope mode). That task is not yet derived; this dependency is unresolved. Reconcile via `task-repair-meta` once REQ-PROC-035 is decomposed. Do NOT add the spine task to `after:` now — it does not exist yet.

## Requirements Summary

Covers AC-07 (flow→scribble coverage ordering) and AC-09 (L3 coverage assertion + chain-length alert) of REQ-PROC-032-05.

For complete requirements at task creation time:
```
git show 85ed6d20:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- New `check_scribble_coverage.py` script (advisory coverage report + graph-stats E3 probe)
- Auto `task_type: scribble` injection in `task-derive-from-requ` for presentation/both-layer ACs
- Soft-preference ordering rule for primary forward entry-path scribble task (depth-1, basis resolution)
- L3 coverage assertion + chain-length alert emission
- E3 probe (graph-stats dump) output format

### Out of Scope
- Blocking (hard) enforcement of coverage ordering (advisory only at this stage)
- Cross-slice spine (T-C1, REQ-PROC-035) — reconcile via task-repair-meta
- Domain→design edge and facet tagging (T-C14)

## Acceptance Criteria

- [ ] `check_scribble_coverage.py` runs against a fixture and produces advisory coverage report + E3 graph-stats dump
- [ ] `task-derive-from-requ` auto-sets `task_type: scribble` for presentation/both-layer ACs
- [ ] Ordering rules emit soft-preference for primary forward entry-path scribble task (depth-1, basis resolution)
- [ ] L3 coverage assertion detects missing L3 entries and emits chain-length alert above threshold
- [ ] All existing tests pass; new script passes Python quality gates (ruff, mypy, pytest)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No within-slice blocking dependencies; CROSS-SLICE after: T-C1 (REQ-PROC-035, not yet derived) — reconcile via task-repair-meta |

## Notes

Location auto-accepted (plan-driven mode): requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/tasks/2026-06-06_impl_derive-f05-coverage-ordering-and-l3-assertion/

Coverage auto-set from plan: [AC-07, AC-09]

target_package omitted: process task, no release package.

CROSS-SLICE note: The REQ-PROC-035 spine task T-C1 (--scope mode) is a logical predecessor but is not yet derived. Record in implementation_notes and reconcile via task-repair-meta once REQ-PROC-035 is decomposed.
