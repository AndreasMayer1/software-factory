---
task_id: TASK-PROC-044-01-02
type: impl
parent_requirement: REQ-PROC-044-01
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-06-01
completed: 2026-06-01
session_completed_at: 2026-06-01T10:08:20Z
effort: M
created: 2026-05-31
after: [TASK-PROC-044-01-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03]
  sections: []
scope_description: "Apply ## Domain Vocabulary + ## Anti-Patterns to the six existing agents using the new claude-modify-agent skill, exercising the AC-03 authoring aid."
release_description: ""
opus_recommended: true  # reason: expert-tier vocabulary (15-year-practitioner bar) across six distinct agent domains — synthesis/judgment heavy
writes_requirements: false
requirements_version:
  commit: 6ece1dc7
  file: ../../requirements.md
session_id: 6409479f-48d4-4c57-8ad5-68025aa4f9e1
session_account: gmail
---
# Goal: Port Domain Vocabulary + Anti-Patterns to the six existing agents

## Objective

Using the new `claude-modify-agent` skill (delivered by TASK-PROC-044-01-01), add
a `## Domain Vocabulary` section (10–25 expert-tier terms passing the "15-year
practitioner test") and a `## Anti-Patterns` section to the six existing general
agents:

- `architecture-advisor`
- `implementation-engineer`
- `opus-advisor`
- `quality-checker`
- `setup-optimizer`
- `test-engineer`

This is capability **D9**, executed *through* the new skill — it is the real-world
exercise of REQ-PROC-044-01 AC-03's Domain-Vocabulary authoring aid against live
agents.

## Requirements Summary

REQ-PROC-044-01 AC-03 requires the capability-authoring skills to produce 10–25
expert-tier terms per agent domain, each passing the practitioner test, rejecting
shallow/common-web vocabulary. The six general agents currently carry no
`## Domain Vocabulary`; this task fills that gap via the governed path.

For complete requirements at task creation time:
```
git show 6ece1dc7:requirements_tasks/process/AI_rules/epic_factory_quality/feat_capability_authoring_skills/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

- Run `claude-modify-agent` on each of the six agents to add:
  - `## Domain Vocabulary` — 10–25 terms that are **domain-distinct per agent**
    (architecture vs implementation vs Opus-routing vs quality review vs
    environment setup vs testing); each must pass the practitioner test; shallow
    or generic terms are rejected, not padded in to hit the count;
  - `## Anti-Patterns` — the failure modes / mistakes characteristic of that
    agent's domain.
- Keep each agent's `contract.yaml` in sync (REQ-PROC-044 AC-04 mechanism) as part
  of the modify-agent run.

### Out of Scope

- The other required sections (`## Protocols`, `## Output`, `## Rules`) where they
  already exist — only add them if `claude-modify-agent`'s structural check finds
  them missing.
- The `ui-scribble-*` agents (owned by the REQ-PROC-032 strand).
- Creating new agents (that is `claude-create-agent`, not in this task's scope).

## Acceptance Criteria

- [x] All six agents have a `## Domain Vocabulary` section authored via `claude-modify-agent`
- [x] Each vocabulary set is 10–25 expert-tier, domain-distinct terms passing the 15-year-practitioner test (no shallow/generic padding)
- [x] All six agents have a `## Anti-Patterns` section
- [x] Each modified agent's `contract.yaml` is kept in sync
- [x] Modifications were made THROUGH `claude-modify-agent` (not hand-edited), exercising AC-03's aid

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-01-01 | pending | Provides `claude-modify-agent` and the Domain-Vocabulary aid this task exercises |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-044-01-01](../2026-05-31_impl_create-claude-agent-authoring-skills/goal.md) | Predecessor — delivers the `claude-modify-agent` skill and the AC-03 Domain-Vocabulary aid that this task uses |

## Notes

This task validates that the AC-03 authoring aid actually produces expert-tier
vocabulary on real, varied agent domains — if any agent's vocabulary comes out
shallow, that is a defect in the N1 aid to be routed back, not papered over here.
