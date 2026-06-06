---
task_id: TASK-PROC-060-02
type: impl
parent_requirement: REQ-PROC-060
urgency: 3
urgency_reason: U3-PRIVACY
impact: 5
impact_reason: I5-TRUST
status: completed
started: 2026-05-27
completed: 2026-05-27
session_completed_at: 2026-05-27T07:35:50Z
effort: S
created: 2026-05-26
after: [TASK-PROC-060-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01]
  sections: []
scope_description: "Enforce the admission gate in agent workflows — CLAUDE.md and/or relevant skills"
release_description: "Agents now escalate for any new dependency instead of self-authorizing."
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 593ff1cc
  file: ../requirements.md
session_id: 7f3e5868-42b7-4e79-a445-380aa40360ad
session_account: web
---
# Goal: Admission Gate Workflow Enforcement

## Objective

Make the dependency admission gate active in AI agent workflows. After this task, any agent that encounters a task requiring a new top-level dependency will know it must escalate (via the back-pressure protocol of REQ-PROC-046) rather than self-authorize. The authoritative documentation authored in TASK-PROC-060-01 must be reachable without asking.

This satisfies AC-01: no new top-level dependency is introduced without recorded developer pre-authorization.

## Requirements Summary

AC-01 requires that LLM agents escalate rather than self-authorize when a new dependency is needed. The escalation uses REQ-PROC-046's back-pressure protocol. The gate covers pubspec.yaml (runtime and dev), Python manifests under scripts/, and npm manifests.

For complete requirements at task creation time:
```
git show 593ff1cc:requirements_tasks/process/AI_rules/ai_tool_management/dependency_admission_and_health/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- Add a "Dependency Admission Gate" entry to CLAUDE.md's operational rules section, pointing to the authoritative doc created in TASK-PROC-060-01 and stating the autonomy boundary in one sentence
- Evaluate whether any of the following skills need an inline reminder (not full duplication — just a pointer to the doc):
  - `claude-write-script` (Python dependencies)
  - `code-complex` / `code-simple` (Dart/Flutter dependencies)
  - Any skill that explicitly adds packages
- If a skill reminder is warranted, add one short inline note; if CLAUDE.md alone is sufficient, document why
- The enforcement must be lightweight — CLAUDE.md and skills are token-sensitive

### Out of Scope

- Rewriting the full admission criteria into CLAUDE.md (the authoritative doc handles that)
- Any changes to `lib/`, `test/`, or `integration_test/`
- Setting up the monthly review cadence (REQ-PROC-061)

## Acceptance Criteria

- [x] CLAUDE.md contains a reference to the dependency admission gate document (created in TASK-PROC-060-01) in a location agents will encounter during pre-work reading
- [x] The reference states the core autonomy boundary: "agent must escalate — not self-authorize — when a new dependency is needed"
- [x] Decision recorded: which skills (if any) received inline reminders and why
- [x] No full duplication of admission criteria in CLAUDE.md (pointer pattern only)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-060-01 | pending | Must know the document path before adding the CLAUDE.md reference |

## Notes

Keep CLAUDE.md additions minimal — it is loaded into every agent context. A single bullet with the document path and the autonomy boundary sentence is the target. If in doubt, err toward less.
