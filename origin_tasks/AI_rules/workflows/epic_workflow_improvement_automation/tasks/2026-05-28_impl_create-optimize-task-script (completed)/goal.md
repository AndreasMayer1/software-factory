---
task_id: TASK-PROC-006-09
type: impl
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-28
started: 2026-05-28
completed: 2026-05-28
session_completed_at: 2026-05-28T08:47:59Z
after: [TASK-PROC-006-07]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-04, AC-10]
  sections: [SEC-04]
scope_description: "Implement scripts/optimize/create_optimize_task.py that emits the produced improvement task with awaiting:['user-unblock'] (G-INV-1, non-configurable) and enforces the write-surface deny-list at task-creation time."
release_description: ""
opus_recommended: true   # reason: programmatic safety invariants (G-INV-1, deny-list)
writes_requirements: false
worktree_path: ""
target_package: "claude-optimize"
backlog_id: IMPL-D
requirements_version:
  commit: eabdeaf0
  file: ../requirements.md
session_id: 10a5ce79-6317-4648-8750-7386732755ae
session_account: gmail
---
# Goal: `create_optimize_task.py` with Auto-Block + Deny-List (IMPL-D)

## Objective

Build the single chokepoint through which claude-optimize creates improvement
tasks. Two non-removable invariants live here: G-INV-1 (every produced task is
auto-blocked) and the write-surface deny-list (SEC-04) that prevents proposals
targeting the factory's evaluation surface.

## Requirements Summary

Reference: REQ-PROC-006 §"Hard Constraints" G-INV-1, §"Write-Surface Deny-List"
(SEC-04), and §"Producer Paradigm" (commit eabdeaf0). The deny-list minimum is
listed in SEC-04 and includes claude-optimize itself, verify-quality,
task-complete, claude-modify-skill, scripts/quality/**, analysis_options.yaml,
.claude/factory_flows.md, .claude/skills/INDEX.md.

For complete requirements at task creation time:
```
git show eabdeaf0:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- `scripts/optimize/create_optimize_task.py` — accepts an improvement-candidate event (or candidate descriptor) and emits a `goal.md` for the improvement task.
- The produced goal.md MUST contain `awaiting: ["user-unblock"]` in YAML frontmatter. No flag, env var, or branch may produce a task without this field set to exactly that value. (G-INV-1)
- Deny-list enforcement: reject (exit non-zero) any produced task whose `target_path` matches one of the SEC-04 entries (glob patterns supported, e.g. `scripts/quality/**`). Deny-list lives as a module-level constant in the script.
- The produced task carries the two-field taxonomy fields (`optimization_target`, `optimization_dimension`) and the `optimization_approach` block per SEC-02/SEC-03 — emitted from the input event descriptor.
- Unit tests asserting: (a) every output goal.md has `awaiting: ["user-unblock"]`; (b) the deny-list rejects each SEC-04 path; (c) a normal, non-deny-listed target produces a valid goal.md.

### Out of Scope

- The producing skill (IMPL-E / TASK-PROC-006-10) that calls this script.
- A pre-commit hook variant — round-4 IMPL-D notes this as optional; reject during code review if introduces complexity not justified by a concrete bypass scenario.
- Monitor scripts that emit candidate events (IMPL-C / TASK-PROC-006-08).

## Acceptance Criteria

- [x] Script exists at `scripts/optimize/create_optimize_task.py` with a documented CLI.
- [x] Every produced goal.md has `awaiting: ["user-unblock"]` exactly (G-INV-1).
- [x] No code path produces an unblocked task (verified by unit test exhaustive on flag combinations).
- [x] Deny-list rejects every SEC-04 path (one unit test per path), with a clear error message naming the matched pattern.
- [x] Deny-list supports glob patterns (`scripts/quality/**` rejects nested files).
- [x] Produced goal.md carries the `optimization_target`, `optimization_dimension`, and `optimization_approach` block.
- [x] G-INV-1 invariant is named in a code comment at the auto-block line and references this AC (`AC-04`).

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TASK-PROC-006-07 (IMPL-B) | pending | Needs `.factory/optimize/` scaffolding for events |

## Notes

Concept docs: round-4 §6 IMPL-D (pre-commit hook variant noted as a "consider";
G-INV-1 auto-block is the primary control per round-4 Part 3). Deny-list is
defense-in-depth per the requirement §"Write-Surface Deny-List": "G-INV-1 makes
a stale deny-list tolerable."
