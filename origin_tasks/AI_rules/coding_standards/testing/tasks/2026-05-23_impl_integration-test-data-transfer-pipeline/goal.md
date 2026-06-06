---
task_id: TASK-PROC-002-27
type: impl
parent_requirement: REQ-PROC-002
urgency: 1
urgency_reason: U1-LATER-PHASE
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-05-23
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-09]
  sections: []
scope_description: "Integration test for the data-transfer pipeline (AC-09 b): single-process simulation of QR send + receive — encode payload in test, decode in same test, verify round-trip and per-chunk correctness. Deferred until release 0.0.1 data-transfer flow is complete."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 2c52ed48
  file: ../../requirements.md
---
# Goal: Data-transfer pipeline integration test (AC-09 b)

## Recommended Skill

**Use `code-test` skill for this task.**

## Objective

Write the integration test for the data-transfer pipeline named in REQ-PROC-002 AC-09 (b):
test the QR send + receive flow as a **single-process simulation** (the user-confirmed approach
from 2026-05-14): encode payload in test, decode in the same test, verify round-trip and
per-chunk correctness. Two-process screen-to-camera optical testing is out of scope.

## Deferral Reason

Release 0.0.1 (alpha) only partially implements the data-transfer flow. The pipeline's
serialization, chunking, framing, and error-correction layers are still in progress.
This test must wait until the 0.0.1 data-transfer implementation is complete.

**When to un-defer**: when the 0.0.1 data-transfer tasks reach terminal status, add the
final TASK-ID to `after:` and lower `urgency` to 2.

## Scope

- File: `integration_test/flows/data_transfer_pipeline_flow_test.dart`
- Follow the `test_di.dart` pattern from TASK-PROC-002-08 (`integration_test/helpers/test_di.dart`).
- Single-process approach:
  1. Encode a synthetic payload through the sender pipeline (serialization → chunking → framing → error correction).
  2. Decode through the receiver pipeline in the same test process.
  3. Assert payload round-trip: decoded output equals original input exactly.
  4. Assert per-chunk correctness: chunk count, sizes, frame structure, error-correction metadata.
- No `flutter drive` multi-device setup — optical QR capture tested manually by the developer.
- Synthetic test data only (REQ-PROC-052 AC-07): Latin pseudonyms, placeholder dates, "this is a test" content.

## Requirements Reference

- **Requirement**: `../../requirements.md` (REQ-PROC-002)
- **AC-09 (b)**: integration test for the data-transfer pipeline — sender + receiver.
- **Related**: TASK-PROC-002-08 (parent scaffolding task; sets up `test_di.dart`).

## Acceptance Criteria

- `integration_test/flows/data_transfer_pipeline_flow_test.dart` exists and passes under `xvfb-run`.
- Round-trip assertion: decoded output equals original synthetic payload exactly.
- Per-chunk assertions: chunk count, sizes, frame structure, error-correction metadata all verified.
- Stable selectors only (no `find.text(...)` patterns needed for this pipeline test).
- Test passes 5× consecutively without state leakage.

---

**Note**: This task describes WHAT to implement, not HOW. The implementation plan is created
fresh at execution time.
