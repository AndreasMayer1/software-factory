---
task_id: TASK-PROC-044-01-03
type: verify
parent_requirement: REQ-PROC-044-01
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-31
started: 2026-06-01
completed: 2026-06-01
session_completed_at: 2026-06-01T15:03:47Z
after: [TASK-PROC-044-01-01, TASK-PROC-044-01-02, TASK-PROC-044-01-05]
awaiting: []
awaiting_note: ""
verification_task: true
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05]
  sections: []
scope_description: "Audit the shipped capability-authoring skills and the six modified agents against AC-01..AC-05; file fix-tasks for any gap."
release_description: ""
opus_recommended: true  # reason: judges shipped artifacts (vocabulary quality, gate enforcement) against ACs — judgment-dependent
writes_requirements: false
requirements_version:
  commit: 6ece1dc7
  file: ../../requirements.md
session_id: fb24c177-5b47-4806-a73c-9b0bec3c329c
session_account: gmail2
---
# Goal: Verify the capability-authoring skills against REQ-PROC-044-01

## Objective

Audit the **shipped artifacts** (not the implementation tasks' claims) of
TASK-PROC-044-01-01 and TASK-PROC-044-01-02 against every acceptance criterion of
REQ-PROC-044-01. File a fix-task for any gap rather than ticking optimistically.

## Requirements Summary

REQ-PROC-044-01 (Capability-Authoring Skills): governed agent authoring (AC-01),
required structural sections (AC-02), the Domain-Vocabulary aid (AC-03),
contract-mechanism integration (AC-04), and single meta-skill ownership (AC-05).

For complete requirements at task creation time:
```
git show 6ece1dc7:requirements_tasks/process/AI_rules/epic_factory_quality/feat_capability_authoring_skills/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope — audit each AC against the shipped artifact

- **AC-01 (governed authoring):** author a throwaway test agent through
  `claude-create-agent` and confirm: a colliding name (vs a built-in / Han import /
  existing agent) is rejected before write; `allowed_tools` is constrained to the
  intent class with no bare `*` lacking justification; the when-to-create gate
  fires; the agent-vs-session suitability check runs. Delete the throwaway after.
- **AC-02 (required sections):** confirm every agent authored/modified through the
  pair carries a ≤50-token role identity and the five sections (`## Domain
  Vocabulary`, `## Anti-Patterns`, `## Protocols`, `## Output`, `## Rules`).
- **AC-03 (Domain-Vocabulary aid):** confirm the aid produces 10–25 terms and that
  the six existing agents (post-TASK-PROC-044-01-02) carry **expert-tier**
  vocabulary passing the practitioner test — reject if generic/padded. A shallow
  result is an N1-aid defect routed back, not a pass.
- **AC-04 (contract integration):** confirm `contract.yaml` is emitted/maintained
  for the two new skills (and for the modified agents) and that the
  sub-skill-vs-agent split rubric (REQ-PROC-044 AC-03) is referenced, not
  re-derived.
- **AC-05 (single ownership):** confirm `.claude/skills/INDEX.md` lists the six
  meta-skills as the governed set with cross-links to their governing ACs, with no
  duplicated or stale ownership.

### Out of Scope

- Fixing the gaps directly — file fix-tasks instead (this is an audit).

## Acceptance Criteria

- [x] AC-01..AC-05 each audited against the shipped artifact, with evidence recorded in `plans_and_protocols/` (protocol + coverage report)
- [x] A throwaway agent authored via `claude-create-agent` demonstrably triggers the collision check, tool-class heuristic, when-to-create gate, and session check (then removed — `plan-reviewer`, deleted)
- [x] The six modified agents' Domain Vocabulary verified expert-tier (not shallow) — PASS; format/aid-spec gap (AC-03) routed to TASK-PROC-044-01-07
- [x] `contract.yaml` presence/sync confirmed (AC-04 PASS); INDEX.md ownership cross-links confirmed with one consistency defect (AC-05) routed to TASK-PROC-044-01-07
- [x] A fix-task is filed for every gap found (TASK-PROC-044-01-07 covers AC-02, AC-03, AC-05; none ticked optimistically)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-01-01 | pending | Delivers the skills under audit |
| TASK-PROC-044-01-02 | pending | Delivers the six modified agents under audit |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-044-01-01](../2026-05-31_impl_create-claude-agent-authoring-skills/goal.md) | Predecessor — the skill pair this task audits |
| [TASK-PROC-044-01-02](../2026-05-31_impl_port-domain-vocabulary-to-existing-agents/goal.md) | Predecessor — the six modified agents this task audits |

## Notes

This is the REQ-PROC-044-01 analogue of REQ-PROC-032's widened verify task 032-20.
