---
task_id: TASK-PROC-002-07
type: analyze
parent_requirement: REQ-PROC-002
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-PROC
status: completed
effort: S
created: 2026-05-10
started: 2026-05-16
completed: 2026-05-16
session_completed_at: 2026-05-16T15:57:32Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-05, AC-06]
  sections: []
scope_description: "Audit existing tests under test/unit/ and test/widget/ for AC-05 (test names describe behaviour, not method) and AC-06 (no real network / unmocked filesystem / unmocked platform channels / wall-clock dependence). Record findings and either fix inline or create a backfill-creator follow-on if volume is high."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: b943e06f-e475-4bf0-acc0-36f6b594c87e
session_account: gmail2
---

# Goal: Audit test suite for naming and isolation hygiene

## Recommended Skill

**If the audit takes the inline-fix path** (≤ 10 problematic findings): use `code-complex` for the fix portion. Fixes touch real Dart in `test/unit/` and `test/widget/` (renaming tests, injecting clock fakes, replacing real I/O with mocks) and benefit from the plan-and-approve gate. **If the backfill-creator path is taken** (> 10 findings): no `code-complex` needed — the audit task itself is just analysis and task creation.

## Objective

REQ-PROC-002 AC-05 (behaviour-describing test names) and AC-06 (no real I/O / clock dependence in unit / widget tests) are forward-looking properties: new tests must conform, but existing tests have not been audited. This task surfaces the existing-test debt so it can be addressed deliberately rather than discovered piecemeal.

## Requirements Summary

REQ-PROC-002 AC-05 (test names describe behaviour: e.g. `parses_entry_with_unicode_content_preserves_grapheme_clusters` — not `testParseEntry`).
REQ-PROC-002 AC-06 (no real network, no real filesystem outside `path_provider` test mock or per-test temp directory, no real platform channels other than the standard mock, no wall-clock time without a controllable clock fake).

Current requirements: ../../requirements.md

## Scope

### In Scope

**AC-05 audit (naming):**
- Scan every `test('...')` and `testWidgets('...')` under `test/unit/` and `test/widget/`.
- Classify each test name as: (a) describes behaviour ("returns null when entry is empty"), (b) describes method only ("testParseEntry", "encryptTest"), (c) ambiguous ("works correctly", "happy path").
- Report counts and provide a representative sample of (b) and (c).

**AC-06 audit (isolation):**
- grep test files for: `dart:io HttpClient`, `package:http`, `package:dio` (network); `File(`, `Directory(`, `Platform.environment` outside test temp/`path_provider` mocks (real filesystem); `DateTime.now()`, `Clock.now()` without a fake-clock injection (wall-clock); platform-channel calls without `TestDefaultBinaryMessenger` mock setup.
- Classify each match as: (a) genuinely problematic (test would behave differently in a different environment), (b) acceptable (uses an established mock/temp pattern), (c) ambiguous.
- Report counts and provide a representative sample of (a).

**Output:**
- `plans_and_protocols/test_hygiene_audit.md` with sections per AC, counts, and samples.
- Volume decision rule:
  - If total problematic findings (across both ACs) ≤ 10 → fix inline as part of this task; record fixes in the protocol.
  - If > 10 → create a single backfill-creator follow-on task (`task-create` skill, type impl) whose goal is "convert findings in `test_hygiene_audit.md` into scheduled fix tasks." This keeps cadence consistent with the other backfill-creator tasks in this requirement family.
- If zero findings: record explicitly and complete.

### Out of Scope

- Reviewing tests under `integration_test/`. Those are explicitly allowed real I/O (it's their purpose).
- Reviewing test fixture data — that's TASK-PROC-052-02's SP6 audit.
- Adding the analyzer / DCM rules that *would* catch these going forward — TASK-PROC-046-03 covers what's catchable; AC-05 (naming) and AC-06 (isolation) are partly about discipline that lints can't fully verify.
- Renaming tests for stylistic reasons unrelated to behaviour-vs-method-name (e.g. case style, length).

## Acceptance Criteria

- [x] `plans_and_protocols/test_hygiene_audit.md` exists with AC-05 and AC-06 sections, counts, and representative samples.
- [x] Volume decision is recorded (inline fix vs. backfill-creator follow-on).
- [x] If inline-fix path was chosen: the fixes are committed and the protocol records what changed. (N/A — zero findings)
- [x] If backfill-creator path was chosen: the follow-on task exists and is referenced from the protocol. (N/A — zero findings)
- [x] If zero findings: that fact is recorded explicitly.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

For AC-05, naming is judgment — `testEncryptionRoundtrip` is method-style but arguably also describes behaviour. The audit should flag clear (b) cases (`testFoo`, `Foo test`, `it works`) and leave borderline cases for the user to decide.

For AC-06, the most common real-world finding is `DateTime.now()` used without a clock fake. Fixing this typically means injecting a `Clock` (or a `DateTime Function()` factory) into the unit under test. It is a targeted refactor, not a rewrite — but if many call sites use `DateTime.now()` directly, the fix per call site is small but the volume is large. That's exactly the case the volume rule is designed to catch.

This task is intentionally pragmatic: small findings get fixed in place; large findings get a creator task. Avoid the trap of treating a 2-finding audit with the same ceremony as a 50-finding one.
