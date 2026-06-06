---
task_id: TASK-PROC-046-06
type: impl
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-10
started: 2026-05-19
completed: 2026-05-19
session_completed_at: 2026-05-19T07:04:03Z
after: [TASK-PROC-046-03, TASK-PROC-002-02, TASK-PROC-046-11]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-10, AC-13]
  sections: []
scope_description: "Update CLAUDE.md to document the back-pressure protocol, list the active gates from REQ-PROC-046, REQ-PROC-002, and REQ-PROC-052, and reference the supporting scripts and analyzer config so an LLM agent has a single authoritative source for what 'complete' means."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: a8c96a91-c639-48e0-be67-6f15d40cfaf2
session_account: web
---
# Goal: Update CLAUDE.md with back-pressure protocol and gate set

## Objective

The back-pressure protocol and the gate set defined in REQ-PROC-046, REQ-PROC-002, and REQ-PROC-052 are currently invisible to an LLM agent reading CLAUDE.md. This task makes them explicit: a section that names every gate, says how to run it, and states the five-cycle revision rule with escalation behaviour. Without this, the gates are documented in requirements but not in the operational checklist that drives task execution.

## Requirements Summary

- REQ-PROC-046 AC-10 (back-pressure protocol exists in operational form), AC-13 (single authoritative source documents the gates and protocol)
- REQ-PROC-002 AC-07 (inheritance of REQ-PROC-046 protocol), AC-08 (single authoritative source documents test-quality gates)
- REQ-PROC-052 AC-09 (inheritance of REQ-PROC-046 protocol), AC-10 (single authoritative source documents privacy/security gates)

Current requirements: ../../requirements.md

## Scope

### In Scope

- Add or update a CLAUDE.md section (e.g. "Quality Gates and Back-Pressure Protocol") that:
  - Lists every active gate from the three requirements (G1–G8 from REQ-PROC-046; TQ1–TQ4 from REQ-PROC-002; SP1–SP6 from REQ-PROC-052)
  - For each gate, names the tool/script and the pass condition
  - States the five-cycle revision protocol (run → fail → read errors → revise → re-run all → escalate after 5 cycles)
  - References the calibrated A40 cold-start threshold (post-TASK-PROC-046-02 if available, else "see TASK-PROC-046-02 for calibration")
  - References the safety-critical paths doc (post-TASK-PROC-046-04)
- Update the "Doing tasks" / "Verify" sections of CLAUDE.md to invoke the gate set rather than ad-hoc checks.
- Reference the `verify-quality` skill (created by TASK-PROC-046-11) and the hook configuration as the canonical enforcement mechanism. Ensure CLAUDE.md's quality-checklist points readers at the skill rather than restating its checks.
- Cross-reference the three requirements explicitly so a reader can trace from CLAUDE.md → requirement → analyzer config / script.

### Out of Scope

- Implementing missing gates (separate tasks).
- Changing the protocol's substance — this task documents the protocol, it does not negotiate it.
- Updating skill files unrelated to verify-quality.

## Acceptance Criteria

- [x] CLAUDE.md has a section listing all active gates from REQ-PROC-046, REQ-PROC-002, REQ-PROC-052 with tool / pass-condition for each.
- [x] The five-cycle back-pressure protocol is documented in CLAUDE.md with the escalation behaviour.
- [x] The `verify-quality` skill (or equivalent) is aligned with the gate set.
- [x] Cross-references from CLAUDE.md to each requirement and to the supporting scripts (coverage check, bundle-size check, grep gates) are present.
- [x] An LLM agent reading CLAUDE.md can determine, without reading the requirement files, which gates apply and how to run each.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-03 | pending | Analyzer config must be live so CLAUDE.md describes reality |
| TASK-PROC-002-02 | pending | Mutation/property tooling must be installed so CLAUDE.md can reference it |

## Notes

The protocol is described once in CLAUDE.md and inherited by the other requirements via cross-reference. Avoid duplicating the protocol text — pointer-only, so divergence is impossible.

If TASK-PROC-046-04 (critical paths) and TASK-PROC-046-02 (A40 calibration) complete before this task, fold their outputs in. If they don't, this task documents pointers ("see [doc] once available") and a follow-up minor edit closes the gap once those are done.
