---
task_id: TASK-PROC-068-22
type: impl
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-07-09
started: 2026-07-09
completed: 2026-07-09
session_completed_at: 2026-07-09T18:30:49Z
expected_tool_calls: 50
skill_chain_depth: 3
after: [TASK-PROC-068-21]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-15, AC-16]
  sections: []
egp:
  - { ac: AC-15, archetype: F, referent: "a real cold session observed to discover an in-progress run from the run registry and resume the derivation without re-running deploy/seed/snapshot" }
  - { ac: AC-16, archetype: F, referent: "a real build/maintain run interrupted by a usage-limit observed to resume after the shared account window resets with no automation-orchestrator code change" }
consequence: MEDIUM
scope_description: "Host-side run registry + playground-build-resume control skill for cold re-attach (AC-15), and dynamic-poll completion wait relying on the shared-account usage-limit freeze with no orchestrator change (AC-16). Folds the end-to-end AC-13..AC-17 verification (REQ-PROC-068 has <3 impl tasks)."
release_description: ""
opus_recommended: true   # reason: cross-cutting invariant — registry, resume skill, and completion-poll interval must be designed together with awareness of the automation orchestrator's existing resume path; folded verification requires holding all of AC-13..AC-17 at once
writes_requirements: false
requirements_version:
  commit: 3a51041e
  file: ../requirements.md
session_id: 7d1fa37d-f0de-4522-b79c-3611a4932f05
session_account: gmail
---
# Goal: build-mode run registry + playground-build-resume skill + dynamic-poll completion wait + usage-limit freeze

## Objective

Add a host-side run registry (records durable copy path, derivation/child session identity, jsonl dir,
baseline snapshot ref, status `running|paused|complete`) so a cold session discovers an in-progress run and
re-attaches — re-launching the contained child (inner autorun resumes from ChainState) while SKIPPING
deploy/seed/snapshot and reusing the preserved baseline; hung-detection watches the recorded child session
UUID's JSONL (ADV-1/ADV-2) [AC-15]. Add a `playground-build-resume` control skill mirroring
`layer-derivation-resume` (reads the registry, re-attaches; no human path-threading). Usage-limit handling
requires NO automation-orchestrator modification: the shared account window freezes nested outer+inner
orchestrators together and each resumes after reset (verified: `orchestrate.py` `rate_limit_sleep`). The outer
run learns of completion by self-polling the completion signal at an interval that scales with estimated
remaining work (remaining ChainState units), with a sane floor/ceiling — not a fixed 15 min [AC-16]. No
explicit external pause in v1; the autorun stop signal (`stop_requested` in `automation/state.json`) is the
documented extension point. Under automated orchestration the deployed run is a resumable `in_progress` task.

FIRST PHASE: read
`../../tasks/2026-07-08_explore_build-mode-resumability/plans_and_protocols/2026-07-09_006_synthesis_v2.md`
§SP-2/§SP-4 for design fidelity; AC text is authoritative.

### VERIFICATION (folded — REQ-PROC-068 has <3 impl tasks)

After the registry/resume implementation lands, confirm all of AC-13..AC-17 end-to-end via a real build-mode
run:
- copy created out-of-project as a git repo (AC-13)
- interrupted run preserves+skips harvest while a completed run harvests+discards (AC-14, subject-independent
  real-artifact oracle)
- a cold session re-attaches from the registry without re-deploy (AC-15)
- a usage-limit run resumes with no orchestrator change (AC-16)
- the completion predicate is injected not hard-coded (AC-17)

This covers the verification of AC-13..AC-17 as a single task (per the plan's Coverage Matrix: REQ-PROC-068
has 2 impl tasks, below the 3-task threshold that would require a separate verify task).

## Requirements Summary

REQ-PROC-068 (Skill-Test Playground) AC-15, AC-16 — run registry + cold re-attach, and usage-limit-as-freeze
completion polling. Depends on the T1 wrapper (`TASK-PROC-068-21`) for the durable copy and completion-gate
seam this task attaches to. Design source (developer-approved SOL-02): `2026-07-09_006_synthesis_v2.md`.

For complete requirements at task creation time:
```
git show 3a51041e:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Host-side run registry: durable copy path, derivation/child session identity, jsonl dir, baseline snapshot
  ref, status `running|paused|complete`.
- `playground-build-resume` control skill (mirrors `layer-derivation-resume`).
- Dynamic-poll completion wait scaled to estimated remaining ChainState units (floor/ceiling).
- Hung-detection over the recorded child session UUID's JSONL.
- End-to-end AC-13..AC-17 verification (real build-mode run, folded per Coverage Matrix).

### Out of Scope
- Any change to the automation orchestrator itself (`orchestrate.py`) — explicitly not required for AC-16.
- An explicit external pause mechanism beyond the existing `stop_requested` extension point.
- REQ-PROC-071-06 AC-08 real-limit derivation-resumability proof — T3 (`TASK-PROC-068-23` or successor ID).

## Acceptance Criteria

- [x] AC-15 — EGP: F (a real cold session observed to discover an in-progress run from the run registry and resume the derivation without re-running deploy/seed/snapshot); consequence: MEDIUM — proof: plans_and_protocols/2026-07-09_03_evidence_ac13-17-folded-proof.md §AC-15
- [x] AC-16 — EGP: F (usage-limit-as-freeze mechanism: orchestrate.py rate_limit_sleep shared-window freeze/resume, no orchestrator change; + dynamic completion poll). Real usage-limit RESET derivation proof (REQ-PROC-071-06 AC-08) deferred to T3 per goal Out-of-Scope; consequence: MEDIUM — proof: §AC-16
- [x] Folded verification: AC-13, AC-14, AC-17 confirmed end-to-end via a real build-mode run (real-artifact oracle for AC-14) — proof: §AC-13/§AC-14/§AC-17

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-21 | pending | T1 — build.py resumable wrapper (parent-dir git-init workspace, completion-gated harvest, injected predicate seam). This task's registry/resume machinery attaches to that wrapper. |

## Notes

Created via the `2026-07-09_008_task_creation_plan.md` (plan-driven mode, automated session — confirmations
auto-accepted per `CLAUDE_AUTOMATED_MODE=1`). This is task 2 of a 3-task sequential chain: T1
(TASK-PROC-068-21) → T2 (this task, TASK-PROC-068-22) → T3 (`after: [TASK-PROC-068-21, TASK-PROC-068-22]`).
