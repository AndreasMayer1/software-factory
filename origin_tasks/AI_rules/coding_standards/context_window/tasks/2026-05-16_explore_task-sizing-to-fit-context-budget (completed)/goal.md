---
task_id: TASK-PROC-001-02
type: explore
parent_requirement: REQ-PROC-001
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-16
started: 2026-05-19
completed: 2026-05-23
session_completed_at: 2026-05-23T21:23:59Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Discover criteria that keep every task executable within a 200K-token sonnet budget without forcing blind splits or wasteful agent fan-out. Update REQ-PROC-001 via requ-explore and propose follow-up tasks for the skills that need updating."
release_description: ""
opus_recommended: true   # reason: cross-cutting explore — multi-skill audit + requirement edits + explicit trade-off analysis
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: fadfd042
  file: ../requirements.md
session_id: 14f805ee-3a21-4f6c-a86b-c7696850c2b7
session_account: gmail
---
# Goal: Task sizing and agent fan-out criteria that keep tasks executable

## Objective

What does it actually take for *every* task in this repo to be executable in
a single ~200 K-token Claude Code session on Sonnet, without (a) blindly
splitting tasks that benefit from a shared mental model, or (b) reflexively
fanning out to subagents that re-read the same files and waste tokens?

The two mechanisms intended to prevent this — auto-split at task creation
and the `should_use_agents.py` runtime check — are partially wired today,
yet two tasks in the 2026-05-16 autorun still exceeded Sonnet's 200 K
ceiling and failed with the 1M-context entitlement error. What we do *not*
yet know:

- When is a task *genuinely* too large to execute as one session? Is the
  signal "scope lists N deliverables", "scope mentions N files", "estimated
  context to read > X KB", "estimated tool-call breadth", or something not
  captured by any structural metric?
- When is splitting *worse than* leaving the task monolithic — because the
  parts share an unwritten mental model that would be lost across folder
  boundaries, or because the split produces N tasks that each have to
  re-establish baseline context?
- When does delegating to a sub-agent *reduce* total token cost (the agent
  reads the heavy material and returns a distilled summary) versus *increase*
  it (the agent re-reads files the main session would have read anyway,
  doubling input cost)?
- Where on this spectrum do the two recent failures (TASK-PROC-049-08 and
  TASK-PROC-052-04) sit — oversized, mis-skilled, or simply mis-chunked at
  the skill level?

## Background

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-16_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show fadfd042:requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md
```

Current requirements: ../requirements.md

REQ-PROC-001 today defines the general principle ("the context window should
stay as small as possible while having exactly the information needed") and
one mechanism (manual condensation with a written report). It does not
define **how task creators decide whether a task is sized to fit**. That
gap is what this task fills.

CLAUDE.md §7 already contains a Context-Window Rule mandating
`should_use_agents.py` at 30 KB / 5 files. Its threshold is structural, not
semantic — and only `release-begin-impl/skill.md` actually calls it. The
exploration must decide whether the existing threshold is right, whether
the structural-only framing is enough, and whether the runtime check
belongs in more skills or should be replaced by a stronger creation-time
check.

The orchestrator now auto-promotes context-limit failures to Opus on the
next iteration (see `scripts/automation/orchestrate.py`
`_promote_task_to_opus_for_context_limit`). That is a safety net, not a
substitute for getting task sizing right — Opus runs cost real tokens, and
the goal is for Sonnet to handle the bulk of tasks cleanly.

## How to Approach This

Use design thinking as the guiding process — empathize before defining,
diverge before converging, let questions lead, iterate. A single pass
through the material will not be enough. Surface surprises — the most
valuable discoveries are the ones that were not anticipated.

The user's explicit nuance must be respected throughout: *we cannot
blindly use agents everywhere or split up any task. Sometimes deep
context produces better results; sometimes agents re-reading files is
just a waste of tokens.* A framework that ignores this nuance is wrong
even if every individual rule looks defensible.

## Seeds

(Open-ended entry points — questions and tensions, not deliverables.
Expect some to dead-end and others to open new threads.)

- **Anatomy of the failures.** Why did TASK-PROC-049-08 hit the ceiling
  during a fresh launch at 7 min while TASK-PROC-052-04 hit it at 4 min
  with a much smaller JSONL? Is the trigger really "tokens accumulated"
  or is it something else (a single oversized tool result, an upfront
  baseline cost, an internal Claude Code heuristic)?
- **Anatomy of comparable successes.** Several tasks in the same autorun
  ran cleanly on Sonnet. What do their skill chain, scope shape, and
  per-launch token profile look like? Where is the line the failures
  crossed?
- **The shared-mental-model counterweight.** Find an example in this repo
  of a task that benefits from monolithic execution because the parts
  inform each other. What would happen if we forced it through agents?
  Quantify, even roughly.
- **The agent-rereads-everything failure mode.** Find a case where
  delegating would be worse than inline because the main session must
  see the material anyway. Does this happen with `requ-explore`?
  `task-resolve`?
- **The structural-vs-semantic threshold question.** Is 30 KB / 5 files
  the right boundary, or does it miss the actual signal? Are there cases
  where 4 small files exceed the cap (because of tool churn) and cases
  where 8 medium files don't (because the model only needs to skim)?
- **Override mechanisms.** If we commit to defaults, what does the
  "this task should ignore the defaults" affordance look like at task-
  creation time? At runtime?
- **Where does the rule live?** Creation-time check, runtime check,
  CLAUDE.md, per-skill, central script — each placement has different
  failure modes when the rule itself is wrong.

## Execution Model

Gather raw material — read the failing goal.mds, the JSONL byte sizes
captured in the diagnosis conversation, the current skill source files,
the CLAUDE.md §7 rule, and the `should_use_agents.py` script. Sample
several successful Sonnet sessions for contrast. Synthesise iteratively
— multiple gathering rounds may be needed before the problem space is
well understood.

The session's model is fixed at launch (Opus, because
`opus_recommended: true`). No mid-session model switching.

Delegate breadth-first surveys (current skill behaviour across many
files, profile sampling of past sessions) to `general-purpose` agents
with focused prompts so they return distilled summaries rather than raw
transcripts. Keep the synthesis and trade-off reasoning in the main
session — that is exactly the kind of work where shared mental context
across pieces matters and a sub-agent would lose continuity.

**Web research**: Optional. Use only if there is established prior art
on task-decomposition heuristics for LLM agents that is worth citing.
Always delegate to a spawned `general-purpose` agent with a focused
question; never run WebSearch inline. Frame queries as questions, not
keyword bags.

## Output

A future implementer should be able to read the synthesis and decide,
for any given task, whether to leave it monolithic, split it, or fan
out parts of it to agents — *and* understand the reasoning well enough
to recognise an edge case the rule does not cover. The synthesis must
name signals (not just thresholds), boundaries, defaults, and the
override path. It must be honest about which signals are easy to
measure structurally and which require semantic judgement.

The exploration also ends with concrete next steps:

- An invocation of `requ-explore` to update REQ-PROC-001 with new
  acceptance criteria (per memory `feedback_requ_explore_for_modifications`,
  never edit requirements.md directly).
- Follow-up tasks created via `task-create` for each skill the audit
  identifies as needing changes (likely some subset of `task-create`,
  `task-create-code`, `requ-explore`, `task-resolve`).

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not
      fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly
      enough for the user to decide
- [x] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies. The orchestrator-side recovery (`_promote_task_to_opus_for_context_limit`) has already shipped; this task fixes the upstream cause. |
