---
task_id: TASK-PROC-045-10
type: impl
parent_requirement: REQ-PROC-045
urgency: 3
urgency_reason: U3-FIX
impact: 4
impact_reason: I4-ENAB
status: pending
effort: M
created: 2026-05-28
after: [TASK-PROC-045-08]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-06, AC-07, AC-08, AC-12, AC-13, AC-14, AC-15, AC-16, AC-17]
  sections: []
scope_description: "Extend the structural validation script and skill integration points (requ-explore Phase 1.4 / release-begin-impl Phase 0) to enforce REQ-PROC-045's new ACs covering anchor files, sub-axis declarations, single-axis-per-level, and the placement algorithm halt-on-no-match behavior"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Enforce REQ-PROC-045's New ACs in Validation Script and Skill Integration Points

## Objective

REQ-PROC-045 was rewritten in TASK-PROC-045-08 to add structural ACs that no current code path enforces:

- AC-12: anchor files (`README.md` for groupings, `requirements.md` for epic/atomic) on every folder with semantic children.
- AC-13: anchor files contain `## Inclusion Criteria`, `## Anti-Scope`, and (for groupings) `## Sub-Axis` sections.
- AC-14: single-axis-per-level rule with axis declared in the parent's anchor.
- AC-15: placement algorithm walks anchors; halts on no match; ad-hoc placement is rejected.
- AC-16: governance gate — Path A/B/C resolution for halted placements; Path C requires user authorisation.
- AC-17: top-level axes match the enumerated set in REQ-PROC-045 §3.

Plus the existing AC-06 / AC-07 / AC-08 integration points (validation script invocation from `requ-explore` and `release-begin-impl`) which now need to call the new checks too.

This task extends the enforcement code so the new ACs are checked at the same workflow boundaries the old ones are.

## Scope

### In Scope

- Extend `scripts/validate_epic_requirements.py` (or split into modules if size warrants) to check:
  - Every folder with semantic children carries the correct anchor file type (AC-12).
  - Every anchor file contains the required sections (AC-13).
  - Each grouping anchor declares a single sub-axis matching the parent's sanctioned set (AC-14, AC-17).
  - Top-level category folders carry anchors whose declared axis matches the enumerated set in REQ-PROC-045 SEC-03 (AC-17).
- Update `requ-explore` skill (specifically Phase 1.4 and Phase 2.5) to invoke the new checks and halt on violation (AC-08).
- Update `release-begin-impl` skill Phase 0 pre-flight to invoke the new checks and abort on violation (AC-07).
- Add explicit error messages naming the failing AC ID, the offending folder, and the resolution path (Path A / B / C per AC-16).
- Update or extend the script's tests under `scripts/tests/` to cover the new checks.

### Out of Scope

- Physically restructuring `process/` or `non-functional/` to comply with the new ACs — that is TASK-PROC-045-09's roadmap and its spawned conversion tasks.
- Implementing the placement algorithm as an interactive tool (AC-15 describes the algorithm as a behavior; this task enforces its halt-on-no-match outcome but does not build a placement assistant).
- Changes to REQ-PROC-049 (language coherence) integration — separate concern.

## Behavior Expected After This Task

- Running `python3 scripts/validate_epic_requirements.py` against the current repository surfaces all new-AC violations as findings with AC IDs and resolution paths.
- A `requ-explore` session that writes a new or modified requirement halts at Phase 2.5 if any new-AC violation is introduced or remains.
- A `release-begin-impl` session aborts at Phase 0 if any new-AC violation exists in the repository.
- Existing AC-01 through AC-05 / AC-10 / AC-11 checks continue to work as before; the new checks are additive.

## Acceptance Criteria

- [ ] `scripts/validate_epic_requirements.py` (or an equivalent module set) enforces AC-12, AC-13, AC-14, AC-15 (the halt behavior), AC-16 (the path identification on violation), and AC-17.
- [ ] Script test suite under `scripts/tests/` covers each new check with at least one passing and one failing fixture.
- [ ] `requ-explore` skill invokes the updated validation in Phase 1.4 and Phase 2.5 and halts on failure.
- [ ] `release-begin-impl` Phase 0 pre-flight invokes the updated validation and aborts on failure.
- [ ] Error messages name the failing AC ID, the offending folder path, and the suggested resolution path.
- [ ] Existing structural checks (AC-01 through AC-05, AC-10, AC-11) continue to pass against the unchanged repository state.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-045-08 | in_progress | Defined the new ACs this task enforces. |
| TASK-PROC-045-09 | pending | Migration roadmap. Independent — this task can land first; once enforcement is in place, validation will surface violations until TASK-PROC-045-09's spawned conversion tasks remediate them. |

## Notes

- This task touches Python scripts. `claude-write-script` skill is mandatory for any edit to `scripts/**/*.py` per CLAUDE.md.
- Test fixtures must NOT create real folders under `requirements_tasks/`; they live under `scripts/tests/fixtures/` or use tmpdir.
- The script's existing CLI surface is preserved; new checks are additive flags or always-on, decided in the impl plan.
