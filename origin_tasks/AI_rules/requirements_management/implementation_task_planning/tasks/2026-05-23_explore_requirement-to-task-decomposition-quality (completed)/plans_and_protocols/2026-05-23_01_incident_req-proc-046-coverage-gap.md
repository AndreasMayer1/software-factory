# Incident Report: REQ-PROC-046 Task Coverage Gap

Date: 2026-05-23
Discovered by: Developer (manual audit session)

## What Happened

REQ-PROC-046 (Code Quality Standard / LLM Back-Pressure Gates) defines 13 acceptance
criteria (AC-01 through AC-13) and was explored by TASK-PROC-046-01 (Opus, 3 feedback
rounds, converged 2026-05-15). The exploration produced 14+ implementation tasks.
The requirement was treated as substantially complete — most tasks marked done, the
gate enforcement mechanism running, CLAUDE.md fully updated.

On 2026-05-23 the developer asked: "are we done implementing the back pressure
requirement?" A manual audit revealed three categories of gaps.

## Gap 1: Uncovered Acceptance Criteria

Two ACs had **zero tasks** covering them:

| AC | Text | Why missed |
|---|---|---|
| AC-03 | "All tests pass with zero failures" | Noted in exploration as "already covered" by the analyzer, but no task was created to enforce it in the gate runner. The gate runner (`check_quality_gates.sh`) does not run `flutter test` at all. |
| AC-06 | "No unawaited futures, bare catch, non-Error throws" | Also noted as "already covered" by analyzer rules. Partially true (the analyzer catches some cases), but no dedicated check and no task to verify completeness. |

**Root cause**: The exploration task (TASK-PROC-046-01) triaged these ACs as "already
covered" without creating a verification task to confirm that claim. The triage
decision was correct at the time (the analyzer does catch some of these), but "partially
covered by existing tooling" ≠ "has a task ensuring full coverage."

## Gap 2: Gate Scripts Created Without Baseline Cleanup

TASK-PROC-046-14 created 12 custom gate scripts (replacing DCM) that detect complexity,
type-naming, architectural imports, direct styling, test smells, folder taxonomy,
suppression justification, and debug artifact violations. These scripts were wired
into `check_quality_gates.sh` and the pre-commit hook.

However, **no task was created to fix the ~160 pre-existing violations** these scripts
detect on the existing codebase. The scripts were built, tested to work (they detect
violations), and declared complete — but the codebase they run against was never
brought to green.

Additionally, **no tests exist for the gate scripts themselves**. Some of the ~160
"violations" may be false positives (e.g., Flutter's standard `_FooState` pattern
flagged by the type-naming gate — 22 hits). Without tests, true violations and false
positives are indistinguishable.

**Root cause**: TASK-PROC-046-03 was scoped as "Baseline-Switch + Violation Cleanup"
and fixed all `flutter analyze` violations (G1) to zero. TASK-PROC-046-14 then created
*new* gate scripts that find *new* violations — but the plan never included a follow-up
task to bring the codebase green against these new scripts. The gap existed between
two tasks: -03 cleaned up G1, -14 created G2/G4/G5/etc., but nobody owned "clean up
G2/G4/G5/etc. violations."

## Gap 3: No Verification Task

No task exists to verify that REQ-PROC-046 as a whole is actually met. Specifically:
- No task checks that `check_quality_gates.sh` exits 0 on the existing codebase
- No task verifies that the pre-commit hook actually blocks on all defined gates (it
  doesn't — it misses G1/G3/G6)
- No integration test or audit confirms the gate table in CLAUDE.md matches what
  scripts actually run

**Root cause**: The exploration (TASK-PROC-046-01) was synthesis-oriented — it defined
the requirement, designed the gates, and created implementation tasks. But it did not
include a final verification step in the task chain. The closest thing was the
`verify-quality` skill (TASK-PROC-046-11), which enforces gates on *new changes* but
does not audit whether the gate *infrastructure* itself is complete and correct.

## Gap 4: Status Inconsistency

TASK-PROC-046-10 had `status: completed` in its goal.md but the folder was never
renamed to include `(completed)`. This made it appear as an open task in directory
listings while being invisible to status scripts that check the YAML field.

TASK-PROC-052-03 (PII toString redaction) was marked `completed` but its code changes
were never committed — they sat in the working tree until bundled into an unrelated
WSL migration commit, where they caused 8 test failures in `choice_service_test.dart`
(stale `Unit` vs `void` type assertions). The task's verify step either didn't run the
full test suite or ran in a worktree that didn't include the pre-existing tests.

## What Would Have Prevented This

1. **AC coverage matrix at decomposition time**: A mandatory check that every AC in
   the parent requirement maps to at least one task. AC-03 and AC-06 would have been
   flagged as uncovered.

2. **Verification task as a mandatory output**: Every task decomposition should include
   at least one task that verifies the requirement is actually met end-to-end — not
   just that individual tasks completed, but that the whole is greater than the sum
   of its parts.

3. **Baseline-impact analysis for new gates**: When a task creates enforcement scripts
   that detect violations, a follow-up task to remediate those violations should be
   automatically proposed (or at least flagged as needed).

4. **Gate script testing as a prerequisite for gate enforcement**: Before enforcing a
   gate (wiring it into the pre-commit hook), its script should have tests proving it
   detects what it claims to detect and doesn't false-positive on standard patterns.

## Remediation (Completed 2026-05-23)

Five new tasks created to close the gaps:
- TASK-PROC-046-18: Validate gate scripts with test cases
- TASK-PROC-046-19: Fix pre-existing baseline violations
- TASK-PROC-046-20: Wire G1/G3/AC-06 into gate runner
- TASK-PROC-002-25: Document test-quality gates (AC-08)
- TASK-PROC-052-05: Document privacy/security gates (AC-10)

TASK-PROC-046-10 folder renamed to `(completed)`.
8 test failures from TASK-PROC-052-03 fixed (choice_service_test.dart Unit→void).

## Systemic Fix (This Task: TASK-PROC-055-01)

The remediation fixes REQ-PROC-046 specifically. The systemic problem — that task
decomposition from requirements has no coverage or verification quality gate — is
the subject of TASK-PROC-055-01 (this task's parent exploration).
