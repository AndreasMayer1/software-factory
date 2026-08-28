---
task_id: TASK-PROC-068-23
type: bugfix
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
effort: S
created: 2026-07-10
started: 2026-07-10
completed: 2026-07-10
session_completed_at: 2026-07-10T12:04:01Z
expected_tool_calls: 20
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-15]
  sections: []
egp:
  - { ac: AC-15, archetype: F, referent: "a later cold session re-attaches to a preserved in-progress build/maintain run and resumes the derivation from its preserved state without re-running deploy/seed/snapshot" }
consequence: MEDIUM
scope_description: "Fix build_resume.py reusing the run's session_uuid on relaunch (Claude CLI rejects an already-used session id), which makes every build-mode resume fail; mint a fresh child session-uuid per relaunch."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 7b56c6ef
  file: ../../requirements.md
session_id: 4f08fc87-7ff3-4b59-a845-4d0dda1f28ea
session_account: gmail2
---
# Goal: Ensure that AC-15 of REQ-PROC-068 works correctly

## Objective

Make `scripts/playground/build_resume.py resume` able to actually relaunch a preserved build-mode run.
Today it reuses the run-registry record's original `session_uuid` as the relaunched child's
`--session-id`; the Claude CLI rejects an already-used id, so every resume of a run whose first child
already ran fails immediately. AC-15 (cold session re-attaches and resumes) is therefore unmet in
practice.

## Bug Report

**Steps to reproduce:**
1. Start a build-mode run (`scripts/playground/build.py`) whose contained child runs at least one turn, then interrupt it (session termination / usage-limit) so the copy is preserved and the registry record stays `running`/`preserved`.
2. Run `python3 -m scripts.playground.build_resume resume`.

**Expected behavior:**
The preserved copy is re-attached and a fresh child session continues the derivation from its committed progress; on verified-complete it harvests + discards.

**Actual behavior:**
The relaunched child exits `rc=1` with **empty stdout** and `build.py` raises
`Invalid JSON envelope from claude: Expecting value: line 1 column 1 (char 0)`; the run is preserved
again but never advances. Root cause: the child is launched with the SAME `--session-id` as the first
(consumed) child, and the CLI errors `Session ID <uuid> is already in use.`

**Environment:** devcontainer, Claude CLI, build-mode playground.

**Logs / repro proof:** A second `claude -p --session-id <any-used-uuid>` fails identically with
`Session ID ... is already in use`; a fresh-uuid `claude -p` succeeds — ruling out rate-limit/auth.

## Requirements Summary

REQ-PROC-068 AC-15: a later cold session discovers the in-progress run and re-attaches to resume the
derivation from its preserved state, without re-running deploy/seed/snapshot and without a human
supplying paths. The session-id reuse defeats the "re-attaches and resumes" clause.

For complete requirements at task creation time:
```
git show 7b56c6ef:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope
- In `build_resume.resume_run` (and any shared launch helper), mint a **fresh** child `session_uuid`
  for each relaunch instead of reusing the record's original. Keep the record's original run id as the
  durable run identity (registry key, workspace name); only the child CLI `--session-id` must be new.
- A regression test asserting a second launch/resume for the same run uses a different `--session-id`
  than the first (and does not fail with "already in use").

### Out of Scope
- Any change to build.py's deploy/seed/harvest/gate logic or the driver.
- The layer-derivation mechanism.

## Acceptance Criteria

- [x] AC-15 — EGP: F (a later cold session re-attaches to a preserved in-progress build/maintain run and resumes the derivation from its preserved state without re-running deploy/seed/snapshot); consequence: MEDIUM

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-071-06-09](../../../epic_layer_derivation/feat_backfill_orchestration/tasks/2026-07-10_impl_execute-deployed-derivation-resumability-run/goal.md) | Discovered this bug during the first real build-mode resume; full root-cause + recommended fix in its plans_and_protocols/2026-07-10_04_finding_build-resume-session-id-bug.md |
| [TASK-PROC-068-12](../2026-07-01_impl_harness-middle-rederive/goal.md) | BLOCKED by this bug — it resumes build-mode runs for the full harness middle-layer derivation |

## Notes

- Operational workaround used by TASK-PROC-071-06-09 to complete its run: clear the stale CCS session
  state for the run's uuid before each resume (`find /home/vscode/.ccs -iname "*<uuid>*" -exec rm -rf {} +`).
  This is a stopgap, not the fix — the proper fix is a fresh child session-uuid per relaunch.
