---
task_id: TASK-PROC-006-13
type: impl
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-28
completed: 2026-05-28
session_completed_at: 2026-05-28T09:37:31Z
effort: S
created: 2026-05-28
after: [TASK-PROC-006-08]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02]
  sections: []
scope_description: "Instrument protocol.md logging (via claude-log or task-complete) to record a skills_used: list per session. Enables Stage 2 of monitor_skill_change_first_use (fires only after evidence that an edited skill was actually exercised)."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
target_package: "claude-optimize"
backlog_id: IMPL-H
requirements_version:
  commit: eabdeaf0
  file: ../requirements.md
session_id: fb1bcecf-8d01-4e3b-b586-dea989883da7
session_account: gmail2
---
# Goal: `skills_used:` Protocol Instrumentation (IMPL-H)

## Objective

Capture which skills a session actually exercised so the first-use monitor
(IMPL-C, Stage 2) can confirm that an edited skill was put to work — not just
edited. Stage 1 fires on the edit alone (higher false-positive rate); Stage 2
upgrades the signal once this instrumentation is in place.

## Requirements Summary

Reference: REQ-PROC-006 §"Monitor Taxonomy" — `monitor_skill_change_first_use`
description (commit eabdeaf0): "Stage 2 fires only after protocol-level
`skills_used:` evidence confirms the changed skill was exercised."

For complete requirements at task creation time:
```
git show eabdeaf0:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- Add a `skills_used:` field (list of skill names) to the protocol logging surface — either claude-log emission or the task-complete protocol writer, whichever owns the canonical protocol frontmatter.
- The list is populated from the actual skill invocations during the session (best-effort enumeration via the skill-invocation log).
- Once the field is written, enable IMPL-C's first-use monitor Stage 2 logic (small follow-up edit inside IMPL-C's script): when an edited skill appears in any subsequent session's `skills_used:`, the Stage 2 event fires.
- Document the field in the protocol template / claude-log skill body.

### Out of Scope

- The monitor scripts themselves (IMPL-C / TASK-PROC-006-08) — only the small enablement edit referenced above.
- Backfilling `skills_used:` into historical protocols.

## Acceptance Criteria

- [x] Protocol frontmatter (or its canonical location) carries a `skills_used:` list on every new protocol written after this task lands.
- [x] The list reflects the actual skills invoked during the session (verified on at least one fixture session).
- [x] IMPL-C's monitor_skill_change_first_use Stage 2 code path is enabled (was a no-op in IMPL-C) and fires when an edited skill appears in a later session's skills_used.
- [x] Documentation for the field exists in claude-log SKILL.md or the protocol template.

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TASK-PROC-006-08 (IMPL-C) | pending | The Stage 2 enablement edit lives inside IMPL-C's monitor; ship the field here, edit the monitor after both have landed |

## Notes

Concept docs: round-4 §6 IMPL-H ("note complementarity with DuckDB" from Part
1.4 — `skills_used:` is account-local; DuckDB-over-JSONL is account-local
too — runs.tsv stays canonical for cross-account history).
