---
task_id: TASK-PROC-058-02
type: impl
parent_requirement: REQ-PROC-058
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-25
completed: 2026-05-25
session_completed_at: 2026-05-25T13:44:18Z
effort: XL
created: 2026-05-24
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-12, AC-15, AC-16]
  sections: [SEC-01, SEC-04]
scope_description: "Create the task-derive-from-requ skill implementing the 6-phase decomposition workflow, mode selection, agent strategy, unified plan format, and no-duplication enforcement per REQ-PROC-058. Excludes AC-17 cross-reference gate (separate task)."
release_description: ""
opus_recommended: true   # reason: novel skill creation with architectural decisions (mode selection, agent strategy, plan format, coverage matrix logic, cross-package handling)
writes_requirements: false
requirements_version:
  commit: e680b5e9
  file: ../../requirements.md
session_id: b2120720-0746-49d1-a940-4c2e2f95f890
session_account: gmail
---
# Goal: Create task-derive-from-requ skill (core)

## Objective

Implement the new `task-derive-from-requ` skill at `.claude/skills/task-derive-from-requ/SKILL.md` per REQ-PROC-058. This is the foundational task for the requirement; other impl tasks depend on this.

## Requirements Summary

REQ-PROC-058 defines the implementation task planning quality contract. This task delivers the core skill — the 6-phase workflow that produces a quality-assured task plan from a requirement, with mandatory coverage matrix and verification task.

For complete requirements at task creation time:
```
git show e680b5e9:requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

1. **Skill file**: `.claude/skills/task-derive-from-requ/SKILL.md` with:
   - Phase 1 (Gather): read target requirement, scan existing tasks via frontmatter only, read related requirements (after/blocks/Related Requirements), optionally spawn gather agent if > 3 related requirements
   - Phase 2 (Analyze): group ACs by logical implementation unit, classify task types (code/process/doc/explore/verification), detect enforcement-creates-violations pattern, identify cross-cutting and cross-package concerns
   - Phase 3 (Plan): per-task scope + S1-S4 sizing (from REQ-PROC-001) + after-chains + opus_recommended; produce coverage matrix grouped by package (AC-16); generate mandatory verification task (AC-02)
   - Phase 4 (Review): present plan + coverage matrix; user approves; in automated mode auto-accept (coverage matrix is the gate)
   - Phase 5 (Create): delegate to task-create (non-code) / task-create-code (Dart code); plan-driven mode; orchestration task pattern for > 6 tasks via create_orchestration_task.py
   - Phase 6 (Validate): run coverage_report.py; confirm 100% coverage; print final matrix

2. **Mode selection logic**: quick mode (1-2 tasks, ≤ 1 code task, user-named ACs); full mode (default for ≥ 3 uncovered ACs or new requirements with zero tasks)

3. **Plan format definition**: YAML/JSON schema with task_name, req_path, requirements_version, covers_acs, effort, layer, after, task_type, implementation_notes, opus_recommended, target_package; coverage matrix section

4. **Agent strategy**: gather agent (Phase 1) for many related requirements; orchestration task (Phase 5) for > 6 tasks

5. **No-duplication enforcement (AC-15)**:
   - Compute-once-trust-downstream: coverage matrix, verification, user review
   - Estimate-upstream-refine-downstream: sizing, effort, dependencies

6. **Coverage matrix repair (AC-09)**: when existing tasks have empty `covers:` fields, read their goal.md bodies, infer coverage from scope description and task name, propose `covers:` updates for user confirmation, write the updates before planning new tasks

7. **Cross-package AC handling (AC-16)**: group tasks by AC package; matrix grouped by package; tasks in multiple packages allowed

8. **claude-route integration**: add detection pattern to claude-route's match table for "decompose REQ-X" / "plan tasks for" goal shapes

9. **Automated mode**: auto-accept Phase 4 (coverage matrix is the gate); always use orchestration task in Phase 5; question.md on blocking errors

10. **Supporting scripts** (per "prefer scripts" principle in REQ-PROC-058 Developer Guidelines, deferred to implementation judgment):
    - Candidates: `plan_validate.py` (coverage matrix completeness, no circular deps, verification task present), `coverage_matrix.py` (matrix from requirement + planned tasks)
    - Decide per-step whether script or inline; create scripts via `claude-write-script` skill if chosen

### Out of Scope

- **AC-17 cross-reference completeness gate** — covered by TASK-PROC-058-03 (separate task to keep this one focused)
- **task-create updates (AC-10, AC-11 redirect + plan-driven mode)** — covered by TASK-PROC-058-04
- **task-create-code updates (AC-10, AC-11, AC-13 preservation, stale-plan check)** — covered by TASK-PROC-058-05
- **release-begin-impl Phase 2c rewrite (AC-14)** — covered by REQ-PROC-035 impl tasks (separate requirement)
- **REQ-PROC-001 test case** — covered by TASK-PROC-058-07

## Acceptance Criteria

- [x] Skill file `.claude/skills/task-derive-from-requ/SKILL.md` exists with all 6 phases documented
- [x] Mode selection logic (quick vs full) implemented per REQ-PROC-058 Skill Boundary section
- [x] Unified plan format defined matching REQ-PROC-058 SEC-04 (including requirements_version field)
- [x] Coverage matrix logic: blocking gate at 100% AC coverage, grouped by package, handles incremental decomposition
- [x] Verification task generation logic: mandatory, type matches requirement type
- [x] Enforcement-creates-violations detection: proposes companion remediation tasks
- [x] No-duplication enforcement per AC-15: documented in skill; downstream skills (task-create, task-create-code) accept upstream values
- [x] Phase 5 delegates to task-create / task-create-code via plan-driven mode (depends on TASK-PROC-058-04 and TASK-PROC-058-05)
- [x] Phase 6 invokes coverage_report.py and confirms 100%
- [x] Existing-task covers: repair (AC-09) works when fields are empty
- [x] Cross-package handling (AC-16) implemented
- [x] Automated mode behavior documented and consistent with REQ-PROC-058 Behavior section
- [x] Orchestration task pattern integrated (reuses create_orchestration_task.py)
- [x] claude-route detection pattern added for "decompose requirement" goal shapes
- [x] INDEX.md updated to list the new skill

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | None — this is the foundation |

## Notes

This is the FIRST use of REQ-PROC-058 design. No prior `task-derive-from-requ` exists. The skill creation itself uses the existing `task-create` (the primitive). This is the bootstrap.

The implementation will use the `claude-create-skill` skill (per CLAUDE.md). When questions arise about specific phases or detection logic, refer to REQ-PROC-058 ACs and the synthesis artifacts in `requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/tasks/2026-05-23_explore_requirement-to-task-decomposition-quality (completed)/plans_and_protocols/` for design intent.

Per REQ-PROC-058's "Prefer scripts over skill instructions" principle (Developer Guidelines), evaluate each phase step for script extraction. Use `claude-write-script` for any new Python script.
