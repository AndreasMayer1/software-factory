---
task_id: TASK-PROC-058-08
type: impl
parent_requirement: REQ-PROC-058
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-05-27
session_completed_at: 2026-05-27T12:36:55Z
started: 2026-05-26
session_id: f87d553b-afb4-4e7f-bd52-822be0a4968d
session_account: web
effort: S
created: 2026-05-26
after: [TASK-PROC-058-07]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []   # follow-up fixes, no specific AC mapping; surfaced during validation
  sections: []
scope_description: "Fix the script/skill integration mismatches surfaced by TASK-PROC-058-07 (validation run of task-derive-from-requ on REQ-PROC-001): align skill SKILL.md with the actual implemented scripts and tighten the auto-derived search terms in the cross-ref detector."
release_description: ""
opus_recommended: false
writes_requirements: false
expected_tool_calls: 18
synthesis_dependent: false
requirements_version:
  commit: e680b5e9
  file: ../../requirements.md
source: "TASK-PROC-058-07 validation findings D, E, F, G, H"

---
# Goal: Align task-derive-from-requ skill with implemented scripts

## Objective

The validation run TASK-PROC-058-07 (real-world test of `task-derive-from-requ`
against REQ-PROC-001) surfaced five concrete integration mismatches between the
skill's documented behavior and the implemented scripts. None are blocking, but
each forces the skill to fall back to a less precise path. This task fixes all
five together.

## Requirements Summary

REQ-PROC-058 introduces `task-derive-from-requ` (Phase 1.5 includes the
cross-ref completeness gate from REQ-PROC-045 AC-11; Phase 5 includes the
orchestration-task pattern). The skill text was written against planned
script interfaces that the implementations diverged from.

For complete requirements at task creation time:
```
git show e680b5e9:requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope — five concrete fixes

**Finding D — Cross-ref detector script name mismatch.**
- Skill (`.claude/skills/task-derive-from-requ/SKILL.md` Phase 1.5.1) references
  `scripts/requirements/detect_cross_ref_gaps.py`. The actual implemented script
  is `scripts/requirements/check_cross_refs.py` (TASK-PROC-045-07).
- Fix: update SKILL.md to reference the implemented name. Optionally add a
  legacy alias.

**Finding E — Cross-ref detector interface mismatch.**
- Skill documents the invocation as `--target <path> --json`. The implemented
  script uses a positional `requirement` argument; JSON is the default output.
- Fix: update SKILL.md to show the actual invocation
  (`check_cross_refs.py <path>` and optionally `--terms <t1> <t2> ...`).

**Finding F — Auto-derived search terms too generic.**
- `check_cross_refs.py` without `--terms` produced 128 candidates against
  REQ-PROC-001 because the auto-derived terms were generic words from the
  User Story ("User", "want", "Story", "developer"). With explicit domain
  terms it produced 9. Stop-word filtering is missing.
- Fix: in `scripts/requirements/check_cross_refs.py`, exclude a stop-word set
  (common English words + User Story boilerplate) from the auto-derived terms.
  Re-run against a sample of requirements to confirm candidate counts drop to
  workable sizes without losing genuine matches. Skill text should also
  recommend passing `--terms` explicitly when auto-derivation is poor.

**Finding G — Orchestration script --task-type values.**
- Skill (Phase 5) documents `--task-type [impl|mixed]`. The implemented script
  (`scripts/tasks/create_orchestration_task.py`) accepts
  `implement|verify|scribble|scribble_to_flutter`. There is no `mixed` option.
- Fix: update SKILL.md to use the actual values. If `mixed` is needed, either
  add it to the script or document the workaround (split into two orchestration
  tasks by task_type).

**Finding H — Orchestration script does not route to `task-create`.**
- Line 183 of `create_orchestration_task.py` only branches between
  `ui-create-scribble` and `task-create-code`. Non-code task types (skill
  edits, audits) cannot be planned through this orchestration pattern as-is.
- Fix: extend `create_orchestration_task.py` to route to `task-create` for
  task entries whose `task_type` is `impl` AND whose plan entry does NOT touch
  `lib/`, `test/`, `integration_test/`. Add `verify` routing for verification
  tasks (currently they would default to `task-create-code` which is wrong).
- Until this lands, TASK-PROC-058-07 used the fallback path (invoke
  `task-create` inline per plan entry).

### Out of Scope

- Re-running the cross-ref gate on every existing requirement (separate effort).
- Restructuring the orchestration-task pattern itself.
- Anything beyond the five findings listed above.

## Acceptance Criteria

- [x] SKILL.md Phase 1.5.1 references `check_cross_refs.py` with its actual
      positional interface (Findings D + E).
- [x] `check_cross_refs.py` applies stop-word filtering to auto-derived terms;
      a sample run on REQ-PROC-001 with no `--terms` produces a workable
      candidate count (e.g. ≤ 30) without dropping the two genuine matches
      (REQ-PROC-008, REQ-PROC-058) (Finding F).
- [x] SKILL.md Phase 5 documents the correct `--task-type` values
      (`implement|verify|scribble|scribble_to_flutter`) (Finding G).
- [x] `create_orchestration_task.py` routes to `task-create` for non-code
      task types and to `task-create-code` for `lib/`/`test/`/`integration_test/`
      task types (Finding H); SKILL.md Phase 5 reflects this.
- [x] All five fixes verified by re-running the equivalent of TASK-PROC-058-07
      against another requirement (or by manual probe).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-058-07 | in_progress | The validation run that surfaced these findings. |

## Notes

Source findings: `requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/tasks/2026-05-24_impl_test-case-req-proc-001-decomposition/plans_and_protocols/2026-05-26_test_case_findings.md`
(written by TASK-PROC-058-07 alongside this task creation).
