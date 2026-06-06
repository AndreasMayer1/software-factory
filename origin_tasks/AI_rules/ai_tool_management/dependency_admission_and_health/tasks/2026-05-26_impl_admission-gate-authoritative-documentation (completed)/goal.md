---
task_id: TASK-PROC-060-01
type: impl
parent_requirement: REQ-PROC-060
urgency: 3
urgency_reason: U3-PRIVACY
impact: 5
impact_reason: I5-TRUST
status: completed
effort: S
created: 2026-05-26
started: 2026-05-27
completed: 2026-05-27
session_completed_at: 2026-05-26T22:09:57Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-03, AC-04, AC-05, AC-06, AC-07]
  sections: []
scope_description: "Author the single authoritative documentation file for the dependency admission gate"
release_description: "Documents admission criteria agents must evaluate before any new dependency is added."
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 593ff1cc
  file: ../requirements.md
session_id: 43478b18-6cb0-4790-b273-4a3c5c0faee2
session_account: gmail
---
# Goal: Admission Gate Authoritative Documentation

## Objective

Author a single, concise authoritative reference document for the dependency admission gate. This document is the canonical source agents consult when proposing a new dependency — it must fully cover the admission checklist, the verified-publisher threshold reduction, the capability-surface advisory flag, the ongoing health re-evaluation trigger, the override path, and the LLM autonomy boundary table.

The document satisfies AC-07: any agent or developer can determine, without asking, what is required to add a new dependency and what health properties an existing dependency must maintain.

## Requirements Summary

REQ-PROC-060 establishes the admission gate for all new top-level dependencies (pub.dev, PyPI, npm). The gate consists of five binary criteria (package age, license compatibility, maintenance activity, transitive footprint ≤5, pub points ≥100), a verified-publisher threshold reduction (6 months → 30 days), a capability-surface advisory flag (network I/O, telemetry, platform channels), and an override path requiring recorded developer authorization.

The sibling requirement REQ-PROC-061 triggers health re-evaluation of existing dependencies on a cadence; this task's document must also describe that ongoing health check (AC-05).

For complete requirements at task creation time:
```
git show 593ff1cc:requirements_tasks/process/AI_rules/ai_tool_management/dependency_admission_and_health/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- Create `doc/process/dependency_admission_gate.md` (or equivalent location that makes the document reachable from CLAUDE.md)
- The document must cover:
  - The five binary admission criteria (AC-02a through AC-02e) as a checklist table
  - Verified-publisher threshold reduction (AC-03)
  - Capability-surface advisory flag with the three flagged capability classes (AC-04)
  - Ongoing health re-evaluation: when it is triggered and what happens on failure (AC-05)
  - Override path: what must be recorded, who authorizes, what is forbidden (AC-06)
  - LLM autonomy boundary table (which operations are autonomous, which require human pre-authorization)
- The document must be concise — agents load it into context; brevity matters

### Out of Scope

- Updating CLAUDE.md or skills to enforce the gate (covered by TASK-PROC-060-02)
- Setting up the monthly review cadence or scheduled jobs (REQ-PROC-061)
- Any changes to `lib/`, `test/`, or `integration_test/`

## Acceptance Criteria

- [x] A single authoritative document exists and is not split across multiple files
- [x] The five admission criteria checklist is present and accurate per AC-02a–e
- [x] Verified-publisher threshold reduction (AC-03) is documented
- [x] Capability-surface advisory flag and the three flagged classes (AC-04) are documented
- [x] Ongoing health re-evaluation trigger and failure path (AC-05) are documented
- [x] Override path (AC-06) is documented: required fields, who authorizes, "silent override is forbidden"
- [x] LLM autonomy boundary table is present
- [x] Document is concise enough for agent context loading (target: ≤ 150 lines)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Consider `doc/process/` as the target directory — it keeps process docs separate from coding guidelines in `doc/architecture/`, `doc/testing/`, etc. If `doc/process/` does not exist, create it. The document path must be recorded in TASK-PROC-060-02's implementation notes so that task can reference it correctly from CLAUDE.md.
