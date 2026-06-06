---
task_id: TASK-PROC-001-05
type: impl
parent_requirement: REQ-PROC-001
urgency: 4
urgency_reason: U4-PROC
impact: 4
impact_reason: I4-ENAB
status: pending
effort: S
created: 2026-05-19
after: [TASK-PROC-001-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-06]
  sections: []
scope_description: "Add a re-entry guard to the requ-explore skill: at Phase 1 entry, refuse a second in-session invocation and instruct the caller to spawn a fresh agent per invocation."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ba1e025f
  file: ../../requirements.md
---
# Goal: requ-explore re-entry guard

## Objective

`requ-explore` is one of the heaviest read skills in the repo: it walks personas, scenarios, flows, and requirements docs end-to-end. Invoking it twice in one session doubles the read pass against the same baseline context — the second pass cannot benefit from the first because the underlying file set is identical. This task implements REQ-PROC-001 AC-06: detect a second in-session invocation and refuse, pointing the caller to spawn a fresh agent per invocation.

## Scope

- Edit `.claude/skills/requ-explore/skill.md` to add a re-entry guard at Phase 1 entry.
- The guard checks whether the current session already invoked `requ-explore` (e.g. via a session-scoped sentinel or by inspecting protocol files). If so, abort with a clear message telling the caller to spawn a fresh agent.
- Document the guard's rationale inline in the skill body so a future modifier does not delete it as redundant.
- No skill body bloat — the guard text must respect skill token-sensitivity rules (see CLAUDE.md §7 "Skills").

## Acceptance Criteria

- [ ] **AC-06** — `requ-explore` refuses a second invocation in the same session and instructs the caller to spawn a fresh agent per invocation. A task that legitimately requires multiple `requ-explore` runs achieves this via fan-out, not in-session re-entry.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-001-02 | completed-after-this-runs | Synthesis from explore task |
