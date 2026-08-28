---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - code-bugfix
  - claude-write-script
  - task-complete-bugfix
  - task-complete
  - claude-commit
---

# Protocol — build-resume fresh child session-id per relaunch (TASK-PROC-068-23)

Session: 4f08fc87 (automated, gmail2). Mode: code-bugfix slim (Python script, no worktree).

## Root cause (confirmed by upstream finding)

`build_resume.resume_run` reconstructed the child `BuildModeConfig` with
`session_uuid=record["session_uuid"]` — the run's ORIGINAL id, already consumed by the
interrupted first child. `build.launch_and_gate` passes that id to `_build_claude_cmd` as
`--session-id`; the Claude CLI rejects a reused id (`Session ID <uuid> is already in use.`)
and returns rc=1 with EMPTY stdout, which `record_run` then surfaces as
`Invalid JSON envelope … Expecting value: line 1 column 1 (char 0)`. Every resume of an
already-launched run died here → AC-15 ("cold session re-attaches and resumes") unmet.

Full upstream diagnosis: `…/2026-07-10_impl_execute-deployed-derivation-resumability-run
(completed)/plans_and_protocols/2026-07-10_04_finding_build-resume-session-id-bug.md`.

## Fix

`scripts/playground/build_resume.py`:
- Added `import uuid`.
- `resume_run` now mints a **fresh** child session-id per relaunch via a new injectable
  `session_id_factory: Callable[[], str] = lambda: str(uuid.uuid4())` parameter, and passes
  that (`child_session_uuid`) into `BuildModeConfig.session_uuid` instead of
  `record["session_uuid"]`.
- The run's durable identity is untouched: registry key / workspace name / baseline sidecar
  still key off the record's original `session_uuid`. Only the ephemeral child CLI
  `--session-id` is new. No registry mutation, no re-deploy/seed/snapshot (AC-15 preserved).

Verified the id flows only to (a) `_build_claude_cmd` `--session-id`, (b)
`LaunchRequest.session_uuid` (child jsonl name + hung-detection), (c) `record_run` cost label
— all correct with a fresh id. `_gate_harvest` does not use it; gate status is written to
`record[_source_path]` (original file). So a fresh child id is safe.

## Regression tests (`scripts/tests/test_playground_build_resume.py`)

- `test_resume_run_uses_fresh_session_id_not_the_records_original`: resumes the same preserved
  run twice, captures each launch's `--session-id` via a capturing `LaunchDeps.popen`, asserts
  neither equals the record's original id and the two differ. FAILS against pre-change code
  (which reused the record id for both).
- `test_resume_run_session_id_factory_is_honored`: asserts the injected factory value reaches
  the child `--session-id`.

## Gate result

`scripts/quality/check_python_gates.sh`: G1 lint, G2 type, G4, G5, G6, G7 PASS.
G3 shows 2 failures — both in `test_aggregate_read_metrics.py` (read-metrics aggregation,
unrelated to this change); confirmed pre-existing on the develop baseline via stash (2 failed,
22 passed with my change stashed). No new findings introduced by this task.
All 10 tests in `test_playground_build_resume.py` pass (8 existing + 2 new).
