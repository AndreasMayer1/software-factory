---
task_id: TASK-PROC-044-15
type: impl
parent_requirement: REQ-PROC-044
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-05-31
completed: 2026-05-31
effort: M
created: 2026-05-31
after: [TASK-PROC-044-13]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-04, AC-05]
  sections: []
scope_description: "Reconcile goal_metadata.yaml + requirements_frontmatter.yaml schemas with the real corpus; repair the skipped real-corpus smoke test"
release_description: ""
opus_recommended: false  # mechanical schema reconciliation, fully specified by the defects log
writes_requirements: false
requirements_version:
  commit: a7fe5b32
  file: ../requirements.md
---

# Goal: Reconcile REQ-PROC-044 schemas with the production corpus

## Objective

Fix the AC-05 schema↔corpus drift found by the TASK-PROC-044-13 audit. The two flagged
canonical schemas reject the overwhelming majority of real artifacts, so they are
non-functional as validators:

- `goal_metadata.yaml` — **123/540** real goal.md files FAIL `validate_against_schema.py`
- `requirements_frontmatter.yaml` — **155/156** real requirements.md files FAIL

Bring both schemas into correspondence with the real corpus, fix the misleading
`target_package` pattern, and repair the one real-corpus test that should have caught
this but silently skips.

## Requirements Summary

REQ-PROC-044 AC-05 requires schema patterns, enum values, and required fields in
`goal_metadata.yaml` and `requirements_frontmatter.yaml` to MATCH the actual values in
the production corpus. AC-01/AC-04 require schemas to produce useful warnings on real
input rather than spurious failures.

For complete requirements at task creation time:
```
git show a7fe5b32:requirements_tasks/process/AI_rules/factory_quality/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

Full defect detail + exact repro commands + field/enum counts are in the audit's defects log:
`../2026-05-30_verify_req-proc-044-implementation-quality/plans_and_protocols/2026-05-31_02_defects.md`

- **DEFECT-1** — add the ~25 actively-used optional fields to `goal_metadata.yaml`
  (`source_flows`, `cross_flow_impact`, `depends_on_foundations`, `related_flows`,
  `target_release`, `foundation_for`, `backlog_id`, `verification_gaps`,
  `verification_foundations`, `source_matrix`, `orchestration_task`, `updated`, `blocks`,
  `expected_tool_calls`, `task_type`, `plan_path`, `status_gap`, … full list in defects log).
  Reconcile the `type` enum (decide: declare or treat analyze/review/define/explore+impl
  as legacy corpus to be cleaned — record the decision).
- **DEFECT-2** — add the near-universal missing fields to `requirements_frontmatter.yaml`
  (`created`, `updated`, `after`, `blocks`, `stakeholder`, `parent`, `parent_epic`,
  top-level `personas_served`, `parent_requirement`, …). Reconcile `effort` (`ongoing`)
  and `status` (`draft`/`deprecated`/`completed`) enums against the lifecycle policy in
  `requirements_management/requirements_and_tasks/requirements.md`.
- **DEFECT-3** — fix or remove the bogus `target_package` pattern
  `PKG-[0-9]+\.[0-9]+\.[0-9]+-[a-z]+` in `goal_metadata.yaml` (real values are free-form
  RELEASE_BACKLOG.md names; align with the `requirements_frontmatter.yaml` target_package field).
- **DEFECT-4** — repair `scripts/tests/test_validate_against_schema.py::test_real_goal_md_against_real_schema`,
  which silently `pytest.skip`s on a stale hardcoded path. Replace with iteration over a
  real-corpus sample (or all goal.md / requirements.md) asserting zero validation errors.
  **MUST use the `claude-write-script` skill** (edit under `scripts/`).

### Out of Scope

- Adding `pattern` enforcement to `validate_against_schema.py` — its 3-check scope is an
  intentional D-2 decision. Any change there is a gate-script change requiring a proposal
  under `scripts/quality/proposals/` (CLAUDE.md §7); do NOT edit the validator directly here.
- Cleaning up legacy corpus values (e.g. rewriting old `type: analyze` goal.md files).
  If the chosen approach is "reject legacy values", file a separate corpus-cleanup task.

## Acceptance Criteria

- [x] goal_metadata.yaml declares every legitimate field present in the corpus; the
      type-enum decision is made and documented in the schema comments.
- [x] requirements_frontmatter.yaml declares created/updated/after/blocks/stakeholder/
      parent/parent_epic/personas_served and reconciles effort/status enums.
- [x] target_package pattern in goal_metadata.yaml no longer claims PKG-x.y.z (fixed or removed).
- [x] The real-corpus smoke test no longer skips; it runs and asserts zero validation
      errors across a real-corpus sample (repaired via claude-write-script).
- [x] `validate_against_schema.py` runs green — or near-green with each remaining failure
      explicitly classified as a documented legacy exception — across all real goal.md and
      requirements.md files (re-run the repro commands from the defects log).
- [x] verify-quality / Python gates pass for the touched scripts/tests file.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-13 | in_progress | The audit that found these defects; defects log is the spec |

## Notes

Created by the TASK-PROC-044-13 audit as the follow-up impl task for the confirmed AC-05
defects. Relationship: extends the REQ-PROC-044 schema work (waves 1–3) — does not
duplicate it; it corrects the schemas those tasks produced so they match reality.
