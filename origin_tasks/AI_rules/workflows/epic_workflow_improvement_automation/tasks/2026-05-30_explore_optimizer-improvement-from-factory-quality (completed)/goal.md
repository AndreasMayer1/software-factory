---
task_id: TASK-PROC-006-17
type: explore
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-30
started: 2026-05-30
completed: 2026-05-30
session_completed_at: 2026-05-30T12:11:56Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore how claude-optimize can be improved using the read-frequency instrumentation from REQ-PROC-044; determine whether REQ-PROC-006 and/or the optimizer skill need updating to properly integrate high_read_file signals"
release_description: ""
opus_recommended: false
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: 95f9eaa7
  file: ../requirements.md
session_id: 503d573f-8993-4be1-b861-478671205182
session_account: gmail
---
# Goal: Optimizer Improvement from Factory-Quality Instrumentation

## Objective

REQ-PROC-044 (TASK-PROC-044-09) has shipped read-frequency instrumentation: PreToolUse/PostToolUse hooks log every file read to `.factory/session_logs/`, and `aggregate_read_metrics.py` aggregates these into `high_read_file` events that land in `.factory/optimize/events/`. This exploration investigates what that means for claude-optimize — what improvements are now possible, and what needs to change in REQ-PROC-006 or the optimizer skill to properly integrate these signals.

## Background

TASK-PROC-006-14 (impl, awaiting) was created as a placeholder: "once REQ-PROC-044 ships observability data, extend monitors to consume it." That blocking condition is now met. But before implementing, several open questions need resolution:

1. `aggregate_read_metrics.py` reads session JSONL — REQ-PROC-006 AC-02 explicitly forbids monitors from doing this. Is the aggregator a "monitor"? If not, the taxonomy needs updating to describe this new producer class.
2. The `high_read_file` event type is absent from REQ-PROC-006's Monitor Taxonomy table. The optimizer currently has no handling for it.
3. The "Common Pitfalls" section of REQ-PROC-006 says reading session JSONL is a pitfall — yet the aggregator does exactly that by design. This is confusing and needs clarification.
4. REQ-PROC-044 AC-07 (just added) specifies a 30-day retention/prune policy for session logs — the aggregator needs to implement this before it can be called reliably from the optimizer pipeline.

The user's initial thinking is in:
`plans_and_protocols/2026-05-30_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 95f9eaa7:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **What class of producer is `aggregate_read_metrics.py`?** REQ-PROC-006 defines "monitors" as scripts invoked by task-complete. The aggregator is different: it reads session JSONL (account-local, not project-local), runs on demand, and emits to the same events/ queue. Does this need a new producer class in the taxonomy, or can the existing monitor framework accommodate it?

2. **What does the optimizer actually do with a `high_read_file` event today?** The event type is undocumented — does the optimizer skill silently ignore unknown event types, or does it produce broken tasks? What would a well-formed `high_read_file`-triggered improvement task look like?

3. **Is AC-02's "no monitor reads session JSONL" a safety rule or an incidental constraint?** The original rationale was "expensive, fragile, account-local." Does `aggregate_read_metrics.py` satisfy the spirit of that rule (it's a separate, on-demand script, not a real-time hook), or does it violate it? What update to AC-02's text correctly captures the intent?

4. **What improvements does read-frequency data actually enable?** The aggregator emits "cache", "section", "reference" candidates. Which of these are actionable by the optimizer today? Which require new executor skills or deny-list entries? Is `high_read_file` more useful as a periodic signal or as an event-driven trigger?

5. **What is the right relationship between this explore task and TASK-PROC-006-14?** TASK-PROC-006-14 is scoped to "extend monitors to consume observability data." Should it be re-scoped, split, or replaced based on what this exploration finds?

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

**Key files to read**: `requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md`, `scripts/factory/aggregate_read_metrics.py`, `.claude/skills/claude-optimize/skill.md`, `.factory/optimize/README.md`, `TASK-PROC-006-14/goal.md`.

**Web research**: For seeds requiring external knowledge — how similar self-improving systems handle tiered signal sources, how ML observability pipelines separate collection from consumption — delegate to a spawned `general-purpose` agent with a focused question; never run WebSearch inline.

## Output

A future implementer (likely working on TASK-PROC-006-14 or a replacement) should understand from the output:
- Whether REQ-PROC-006 needs patching, and what the patch should say
- Whether `aggregate_read_metrics.py` needs to be called differently (e.g. via a new monitor wrapper, or only on explicit request)
- What the optimizer skill needs to handle `high_read_file` events correctly
- A concrete recommendation on TASK-PROC-006-14: re-scope, split, or proceed as-is

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-09 | completed | Shipped aggregate_read_metrics.py and session log hooks |
| REQ-PROC-044 AC-07 | defined | Retention/prune policy just added — aggregator not yet updated |
