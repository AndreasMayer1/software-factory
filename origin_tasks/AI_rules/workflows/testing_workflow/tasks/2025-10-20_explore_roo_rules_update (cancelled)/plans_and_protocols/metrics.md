# Metrics Template

Author: Roo, AI Architect
Date: 2025-10-20

Purpose

- Provide a standard schema and storage location for metrics produced by the Testing Orchestrator and Test Part Orchestrator.

Location

- plans_and_protocols/metrics.md

Schema (per test file / per part)

- test_file_id: string # example: plan_templates/plan_list_test
- part_id: string # example: p1
- total_attempts_for_part: integer
- number_of_explores_created: integer
- time_to_first_success_seconds: number|null
- first_attempt_timestamp: ISO8601
- last_attempt_timestamp: ISO8601
- time_to_resolution_seconds: number|null
- flakiness_detected: boolean
- flakiness_probe_runs: integer|null
- attempts: # array of attempt objects
  - attempt_number: integer
    subtask_id: string
    commit_hash: string
    verification_result: PASS|FAIL|ERROR|NONE
    duration_seconds: number
    logs_path: string
    timestamp: ISO8601
- notes: string

Guidelines for use

- The Test Part Orchestrator MUST append a single entry per part to `plans_and_protocols/metrics.md` when a part completes (success or escalation).
- The Testing Orchestrator MUST aggregate per-file metrics into its `testing_orchestrator_protocol.md` after Phase 3 verification.
- Use ISO8601 timestamps and seconds for durations.
- For flakiness probes, record `flakiness_probe_runs` and include a short summary in `notes`.

Example entry (YAML)

---
test_file_id: plan_templates/plan_list_test
part_id: p1
total_attempts_for_part: 2
number_of_explores_created: 0
time_to_first_success_seconds: 420.5
first_attempt_timestamp: 2025-10-20T09:12:00Z
last_attempt_timestamp: 2025-10-20T09:19:00Z
time_to_resolution_seconds: 420.5
flakiness_detected: false
flakiness_probe_runs: null
attempts:
  - attempt_number: 1
    subtask_id: impl_test_part_2025-10-20_..._a1
    commit_hash: abcdef123
    verification_result: FAIL
    duration_seconds: 180.2
    logs_path: plans_and_protocols/logs/attempt1.log
    timestamp: 2025-10-20T09:12:00Z
  - attempt_number: 2
    subtask_id: impl_test_part_2025-10-20_..._a2
    commit_hash: fedcba321
    verification_result: PASS
    duration_seconds: 240.3
    logs_path: plans_and_protocols/logs/attempt2.log
    timestamp: 2025-10-20T09:16:00Z
notes: "Fixed mocking of repository and added safe pump patterns."
---

Implementation notes

- Append entries; do not overwrite existing metrics.
- Keep logs referenced by `logs_path` in `plans_and_protocols/logs/` using attempt-identifying filenames.
- The Test Part Orchestrator should compute `time_to_first_success_seconds` as difference between first attempt timestamp and the first successful attempt's timestamp.

Interpretation notes

- The task might get interrupted by the user, therfore a gap of multiple hours or even days between attempts do not mean that that the task really took that amount of time to run.