---
task_id: TASK-PROC-052-03
type: impl
parent_requirement: REQ-PROC-052
urgency: 3
urgency_reason: U3-PRIVACY
impact: 5
impact_reason: I5-TRUST
status: completed
effort: M
created: 2026-05-10
started: 2026-05-18
completed: 2026-05-18
session_completed_at: 2026-05-18T12:32:07Z
after: [TASK-PROC-049-08]  # canon-bootstrap T7 must complete first; see .claude/task_ordering_priority_override.txt
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-05, AC-06]
  sections: []
scope_description: "Inventory domain types holding user-entered mental-health content (entries, notes, mood values, plans, free-text value objects), add redacted toString() overrides, write unit tests asserting that toString() of an instance with sentinel content does not contain that content."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: 33e6aab1-a0ee-40c0-b12b-ea3a59e5f6d7
session_account: web
---
# Goal: Add toString() redaction to PII-bearing types

## Recommended Skill

**Use `code-complex` skill for this task.** The work writes Dart `toString()` overrides on multiple domain types and adds redaction unit tests for each. The skill's plan-and-approve gate confirms the inventory of PII-bearing types is correct before the writing begins (a missed type means logging exposure when the type is later used in a logger call).

## Objective

REQ-PROC-052 AC-05 requires every domain type holding user-entered mental-health content to override `toString()` to a redacted form, with unit tests asserting redaction. AC-06 then makes safe logging structurally enforceable. This task implements both: identifies PII-bearing types, adds redacted `toString()`, writes the redaction unit tests.

## Requirements Summary

REQ-PROC-052 AC-05 (PII redaction in `toString()`), AC-06 (safe logging building on AC-05).

Current requirements: ../../requirements.md

## Scope

### In Scope

- Inventory PII-bearing types: walk `lib/core/domain/` and `lib/features/*/domain/` for types whose fields hold user-entered content. Likely candidates:
  - `JournalEntry` / `Entry` / equivalent
  - `Note`
  - `MoodValue` (if it carries user free-text rationale alongside the score)
  - `Plan` (if it embeds user notes)
  - Any value object containing user free text
- For each type, add `@override String toString()` returning a redacted form: structural fields (id, createdAt, contentLength) only; user content excluded.
- Write a unit test per type: construct an instance with sentinel content (`__SENTINEL_CONTENT_DO_NOT_LEAK__`), assert `toString()` does not contain the sentinel, and asserts it does contain expected metadata (id, length, etc.).
- Update any existing call sites that log instances directly: confirm the new `toString()` is sufficient; no change should be needed because `toString()` is overridden, but verify.
- Add a brief note to `doc/testing/` (or `doc/architecture/logging.md` if it exists) describing the redaction convention.

### Out of Scope

- Changing the logger facade or call sites except to verify safety (logger discipline is AC-06's broader topic; this task is the structural defense layer).
- Property-based tests for the redaction (could be added later — bounded by `toString()` doesn't contain *any* random content, expressed as a `glados` property).
- Audit of test-fixture PII — that's TASK-PROC-052-02 (SP6 in the audit).

## Acceptance Criteria

- [x] Every type identified as PII-bearing has an overridden `toString()` returning a redacted form.
- [x] Each type has a unit test asserting the sentinel-content rule.
- [x] All redaction tests pass.
- [x] `doc/testing/` (or `doc/architecture/logging.md`) documents the redaction convention so future types added to the domain layer know to follow it.
- [x] No existing code that calls `toString()` on these types is broken by the change.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

The sentinel string `__SENTINEL_CONTENT_DO_NOT_LEAK__` is a pattern that does not naturally occur in any redacted output, so the test is robust against incidental contains-substring matches.

For types with multiple PII fields, the test asserts the sentinel is absent for each field individually (multi-call test) — not just one field tested while others leak.
