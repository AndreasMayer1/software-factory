---
task_id: TASK-PROC-046-07
type: analyze
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-PROC
status: completed
effort: S
created: 2026-05-10
started: 2026-05-15
completed: 2026-05-15
session_completed_at: 2026-05-15T06:43:30Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-07]
  sections: []
scope_description: "Walk the GoRouter route configuration to enumerate every navigation target in lib/, cross-reference against existing widget tests, and produce a list of screens that lack a widget test invoking tester.ensureSemantics() with the four AccessibilityGuideline checks."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: 323deef8-feb5-4c8d-9e32-ad6161f804e7
session_account: gmail2
---

# Goal: Inventory screens needing widget tests with accessibility checks

## Objective

REQ-PROC-046 AC-07 says every screen has a widget test that runs `tester.ensureSemantics()` against the four `AccessibilityGuideline` checks. The size of the backfill required is currently unknown. This task produces the inventory: the list of screens, which already have tests, which lack tests, and the rough effort to close each gap.

## Requirements Summary

REQ-PROC-046 AC-07. The accessibility gate (G6) cannot be enforced until every screen has a test exercising it; this task is the first step toward that state.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Walk the project's `GoRouter` configuration (likely in `lib/core/routing/` or feature-specific route files).
- Produce an inventory: every navigation target → backing widget file → existing widget test (if any) → uses `tester.ensureSemantics()` (yes / no).
- Categorize each screen as: (a) covered fully (test exists with ensureSemantics), (b) test exists but no semantics check, (c) no widget test.
- For each (b) and (c) screen, estimate effort to close the gap (S / M / L).
- Output the inventory as `plans_and_protocols/screens_inventory.md` with a clear table.
- Surface any structural blockers (e.g. screens that are hard to test in isolation due to dependency injection issues).

### Out of Scope

- Writing the missing widget tests. That's the backfill work, scoped by this inventory.
- Adding `ensureSemantics()` to existing tests that lack it. Same — backfill task created from this output.
- Inventory of tests for non-screen widgets (composite organisms, components in `core/design_system/`). Optional; only if straightforward.

## Acceptance Criteria

- [x] `plans_and_protocols/screens_inventory.md` lists every navigation target from the route configuration.
- [x] Each screen is categorized (a) / (b) / (c) per scope above.
- [x] Effort estimate (S / M / L) is given for each (b) and (c) entry.
- [x] Total effort is summarized at the top so the user can decide whether to backfill in one task or break it up.
- [x] Any testability blockers are flagged separately (so they can be addressed before backfill begins).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

This is a pure analysis task. No code changes, no requirement updates. Output is a single inventory document.

Use `codegraph` if available for the routing-config walk; fall back to grep for `GoRoute(` and `routes:`.
