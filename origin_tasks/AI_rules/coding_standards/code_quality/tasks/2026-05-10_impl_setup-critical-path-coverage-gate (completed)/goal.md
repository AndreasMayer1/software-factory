---
task_id: TASK-PROC-046-04
type: impl
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-10
started: 2026-05-16
completed: 2026-05-16
session_completed_at: 2026-05-16T20:10:58Z
after: [TASK-PROC-049-08]  # canon-bootstrap T7 must complete first; see .claude/task_ordering_priority_override.txt
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-04]
  sections: []
scope_description: "Document the safety-critical paths in doc/testing/, set up flutter test --coverage workflow with lcov filter, and add a script that asserts ≥ 90 % line coverage on those paths."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: caa8dd04-921f-418d-824d-4e3629776b9b
session_account: gmail2
---

# Goal: Set up critical-path coverage gate (AC-04)

## Objective

REQ-PROC-046 AC-04 asserts ≥ 90 % line coverage on a documented set of safety-critical paths. Neither the path list nor the coverage-check tooling currently exists. This task creates both: it pins down which paths are subject to the gate (in `doc/testing/`) and produces the script that computes lcov-scoped coverage and exits non-zero on regression.

## Requirements Summary

REQ-PROC-046 AC-04: encryption / decryption, Argon2id key derivation, atomic file rotation, version migration, and the data-transfer serialization pipeline must reach ≥ 90 % line coverage. The same path list will be reused by REQ-PROC-002 AC-02 (mutation testing scoped via lcov to these paths).

Current requirements: ../../requirements.md

## Scope

### In Scope

- Identify the actual file paths under `lib/` matching each category named in AC-04. Walk the codebase and produce the canonical list.
- Document the list in `doc/testing/` (a new section or new file, e.g. `doc/testing/critical_paths.md`) with the rationale for each entry.
- Add a script (e.g. `scripts/quality/check_critical_path_coverage.py` or `.sh`) that:
  1. Runs `flutter test --coverage`
  2. Filters `coverage/lcov.info` to the paths in the documented list
  3. Computes line coverage on the filtered set
  4. Exits 0 if ≥ 90 %, non-zero otherwise, with a clear failure message naming the offending path
- Make the script discoverable from `CLAUDE.md` quality checklist (the CLAUDE.md update itself is TASK-PROC-046-06; just ensure this script's path is stable).
- Run the script once against current code and record the baseline coverage in `plans_and_protocols/`.

### Out of Scope

- Writing missing tests to reach 90 %. If the baseline is below 90 %, that creates remediation tasks (one per path category, sized after the baseline is known).
- Mutation testing on these same paths — a different task (TASK-PROC-002-02 for tooling; mutation runs come later).

## Acceptance Criteria

- [x] `doc/testing/critical_paths.md` (or equivalent location) lists the file paths subject to AC-04 with rationale per category.
- [x] The coverage-check script exists and runs successfully.
- [x] Baseline coverage on each path category is recorded in `plans_and_protocols/`.
- [x] If baseline is < 90 % on any path, a remediation task is created (one per path category) with the gap quantified. (Baseline 91.6% — gate passes, no remediation needed.)
- [x] The script's path and invocation are noted in the protocol so TASK-PROC-046-06 (CLAUDE.md update) can reference them.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

The path list lives in `doc/testing/` (not in `analysis_options.yaml`) because lcov filtering is not an analyzer concern. Keeping it in a documented location means it stays human-maintained and visible alongside the testing guidance.

Picking a specific category like "atomic file rotation" requires reading code — REQ-FUNC-015 names the requirement; the actual implementation may be in `lib/core/data/storage/` or similar. List the *files*, not just the categories, in the doc.
