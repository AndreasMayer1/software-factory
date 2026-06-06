---
task_id: TASK-PROC-058-03
type: impl
parent_requirement: REQ-PROC-058
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-24
started: 2026-05-25
completed: 2026-05-25
session_completed_at: 2026-05-25T13:51:13Z
after: [TASK-PROC-058-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-17]
  sections: []
scope_description: "Implement task-derive-from-requ Phase 1.5: cross-reference completeness gate. Detects gaps via keyword-grep (REQ-PROC-045 mechanism), classifies via user/answer.md, applies fixes via spawned requ-explore agent, blocks until resolved."
release_description: ""
opus_recommended: true   # reason: novel agent-spawning-requ-explore pattern, never done before — needs architectural judgment
writes_requirements: false
requirements_version:
  commit: e680b5e9
  file: ../../requirements.md
session_id: 9065936d-d58b-4e30-99f1-f7bec37f34cd
session_account: web
---
# Goal: Implement cross-reference completeness gate (AC-17)

## Objective

Add Phase 1.5 to the `task-derive-from-requ` skill: the cross-reference completeness gate that detects, classifies, and fixes cross-reference gaps in the target requirement before task planning proceeds.

## Requirements Summary

REQ-PROC-058 AC-17 mandates that task-derive-from-requ verify cross-reference completeness before producing the task plan. The detection uses keyword-grep (mechanism owned by REQ-PROC-045). Classification is done by the user (or developer via answer.md in automated mode). Fixes are applied by spawning an agent that invokes `requ-explore` against the target requirement.

For complete requirements at task creation time:
```
git show e680b5e9:requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

1. **Phase 1.5 in task-derive-from-requ skill** (the skill itself is created by TASK-PROC-058-02):
   - Detect step: invoke REQ-PROC-045's keyword-grep mechanism; compare against target requirement's `after:`, `blocks:`, `## Related Requirements`
   - Classify step:
     - Interactive: present each gap to user; user picks hard dependency / semantic relationship / ignore-with-reason
     - Automated: write `cross_ref_gaps.md` to `plans_and_protocols/`, write `question.md` to `automation/pending_feedback/<TASK_ID>/`, terminate session, developer fills `answer.md`, orchestrator resumes
   - Apply step (both modes): spawn a single agent that invokes `requ-explore` against the target requirement, passing the classified fixes as input; agent commits the updates
   - Resume step: re-run Phase 1 to verify gaps resolved, proceed to Phase 2

2. **Integration with REQ-PROC-045 mechanism**: if REQ-PROC-045's keyword-grep script doesn't exist yet, fall back to inline keyword-grep using requ-explore Phase 1.4 pattern (with TODO note). Once the script lands (separate impl task under REQ-PROC-045), update integration.

3. **Agent prompt template** for the spawned requ-explore agent: structured input describing which fields to update, which classifications to apply

4. **Block-and-resume semantics**: task-derive-from-requ must NOT proceed to Phase 2 until gaps are resolved (or explicitly waived with logged justification)

### Out of Scope

- The keyword-grep mechanism itself — owned by REQ-PROC-045 (separate impl task there)
- The `requ-explore` skill itself — already exists; just being invoked
- All other phases of task-derive-from-requ — covered by TASK-PROC-058-02

## Acceptance Criteria

- [x] Phase 1.5 implemented in `.claude/skills/task-derive-from-requ/SKILL.md`
- [x] Detect step calls REQ-PROC-045's keyword-grep mechanism (or inline fallback if not yet implemented)
- [x] Interactive classification works: user can pick hard / semantic / ignore per gap
- [x] Automated mode writes `cross_ref_gaps.md` + `question.md` and terminates correctly
- [x] Apply step spawns a requ-explore agent with structured input; agent successfully updates and commits
- [x] Block semantics work: Phase 2 does not start until gaps are resolved or explicitly waived
- [x] Resume step re-runs Phase 1 and verifies gaps are gone
- [x] Documented in skill body with rationale (cross-reference completeness is the last check before implementation work)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-058-02 | pending | task-derive-from-requ skill must exist first |
| REQ-PROC-045 impl tasks | not yet created | Keyword-grep script — integrate fully when available; use inline fallback meanwhile |

## Notes

This is the most novel piece of REQ-PROC-058: a skill spawning an agent that invokes another skill. Test carefully — the previous attempt to test requ-explore-in-agent (via the background agent that updated REQ-PROC-035) revealed that requ-explore in agent context may stop early. The agent prompt must be very explicit about completing all steps.

The Apply step's design is documented in REQ-PROC-058 Behavior section ("Cross-reference completeness gate (Phase 1.5)").
