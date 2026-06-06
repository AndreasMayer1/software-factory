---
task_id: TASK-PROC-061-02
type: impl
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: S
created: 2026-05-26
started: 2026-05-27
completed: 2026-05-27
session_completed_at: 2026-05-27T07:42:38Z
after: [TASK-PROC-061-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01]
  sections: []
scope_description: "Set up the monthly dependency review as a calendar mechanism"
release_description: "Monthly dependency health check runs automatically — no human memory required."
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 3cbd51ab
  file: ../requirements.md
session_id: d719c86b-5f4f-4566-89cc-3307cc0052a2
session_account: gmail2

---
# Goal: Monthly Review Schedule

## Objective

Establish the calendar mechanism for the monthly dependency review (AC-01). The review must fire once per calendar month without depending on an agent remembering to check. The mechanism runs `flutter pub outdated` (Dart) and the equivalent for Python manifests under `scripts/`, evaluates each available upgrade against REQ-PROC-056's intake gates (DG1–DG4), and produces a grouped update proposal.

## Requirements Summary

AC-01 requires a monthly dependency review triggered by a calendar mechanism — "it does not depend on the agent remembering to check." The review produces a grouped update proposal; it does not auto-apply upgrades.

For complete requirements at task creation time:
```
git show 3cbd51ab:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- Evaluate and choose the calendar mechanism: the project's `schedule` skill (Claude Code routines via cron) is the primary candidate
- Set up a monthly scheduled routine that:
  1. Runs `flutter pub outdated` and records output
  2. Runs the Python equivalent (`pip list --outdated` or `uv pip list --outdated`) for manifests under `scripts/`
  3. Evaluates each candidate upgrade against REQ-PROC-056 DG1–DG4 (version age ≥ 7 days, no advisories, etc.)
  4. Produces a grouped update proposal for developer review
- The proposal is human-reviewed before any upgrade is applied (autonomous patch/minor bumps per AC-06 may proceed after human review confirms)
- Document the chosen mechanism in `plans_and_protocols/` so future agents know what runs and when

### Out of Scope

- Actually applying the upgrades (that happens after developer review)
- The per-release sweep (TASK-PROC-061-03)
- Any changes to `lib/`, `test/`, or `integration_test/`

## Acceptance Criteria

- [x] A calendar mechanism exists that fires the monthly dependency review without human memory
- [x] The mechanism runs `flutter pub outdated` and the Python equivalent
- [x] The mechanism evaluates candidates against REQ-PROC-056 gates (or flags them for manual evaluation)
- [x] The output is a grouped proposal, not an auto-applied upgrade
- [x] The mechanism and its schedule are documented in `plans_and_protocols/`

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-061-01 | pending | Authoritative doc must exist so the scheduled routine can reference it |

## Notes

The `schedule` skill creates Claude Code routines (cron-scheduled remote agents). A monthly cron (`0 9 1 * *` or similar) fits AC-01's cadence requirement. If the schedule skill is not suitable for this use case, consider a recurring task entry in the task backlog as the fallback — but document the limitation explicitly.
