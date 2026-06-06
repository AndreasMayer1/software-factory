---
task_id: TASK-PROC-065-04-01
type: explore
parent_requirement: REQ-PROC-065-04
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-06-03
expected_tool_calls: 30
skill_chain_depth: 1
synthesis_dependent: true
synthesis_justification: "must hold the task-eligibility engine, the orchestrator picker, status rendering, and ≥3 downstream consumers simultaneously to design one coherent primitive"
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Design a not_before date-gate scheduling primitive for the task lifecycle; produce the requirement/AC text and the implementation surface"
release_description: ""
opus_recommended: true   # reason: cross-cutting engine design synthesizing the eligibility engine + orchestrator + status rendering + ≥3 consumers
writes_requirements: true
requirements_version:
  commit: b4e3add6
  file: ../requirements.md
---

# Goal: Design a `not_before:` Date-Gate Scheduling Primitive for the Task Lifecycle

## Objective

How should a task become eligible **only on or after a future calendar date**, so a
standing task can re-arm itself for a recurring date (e.g. the 1st of next month)
without a human or an external cron remembering to trigger it?

Today the task-eligibility engine has no concept of time. A task is runnable unless its
`status` is terminal/excluded, its `awaiting` is non-empty, or its `after:` references a
non-completed task/requirement ID. There is no way to say "not yet — not before
2026-07-01." This exploration should discover *whether* a date-gate belongs in the
lifecycle model, *where* it lives, *what its semantics are* against the existing
eligibility signals, and *what surface* must change to honour it consistently.

The exploration is not committed to the `not_before` name or to any particular field
shape — those are starting hypotheses to pressure-test, not the answer.

## Background

The concrete trigger is a failure in the dependency-lifecycle automation. The monthly
dependency review (REQ-PROC-061 AC-01) currently runs as a remote Claude Code cron
routine that fires in a cloud container **without the Flutter SDK**. Unable to run a real
`flutter pub outdated`, it queried the pub.dev API and proposed each package's `Latest`
version. Those targets were never validated against an actual `pub solve`, so 7 of 16
proposed bumps in TASK-PROC-061-05 turned out to be unreachable under the project's real
constraint graph — wasting an escalation cycle.

The devcontainer **does** have the SDK, and the local autorun orchestrator
(`automation/orchestrate.py`) already runs there. The developer's proposed fix: move the
check local and make it a **standing task that re-arms itself to the next month's date**.
That requires a date-gate the task model does not have. This exploration designs that
gate as a *general* lifecycle primitive — the monthly review is only its first consumer.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-06-03_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show b4e3add6:requirements_tasks/process/AI_rules/requirements_management/epic_task_lifecycle/feat_task_state_machine/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking — empathize with the engine and its consumers before defining a
field; diverge on mechanisms before converging; let the awkward edge cases lead. A single
read of `next_tasks.py` will not be enough — trace how eligibility, blocking, and status
rendering actually compose, then test each candidate design against the real consumers.

## Seeds

1. **Is a date-gate a new eligibility signal, a new `status`, or a sub-case of the state
   machine (REQ-PROC-065-04)?** A task with a future gate is "not blocked, not runnable,
   not terminal" — does that deserve a distinct rendered state ("scheduled") so it never
   looks like a stuck/blocked task in STATUS.md?
2. **Field semantics.** If `not_before: YYYY-MM-DD`: how does it compose with `after:`
   (both must clear?), with non-empty `awaiting` (external blocker — does a date even
   make sense there?), and with `status`? What is the comparison basis — date vs.
   datetime, which timezone, and "on or after" vs. "strictly after"?
3. **Where does the check live so it is honoured *consistently*?** At minimum:
   `scripts/tasks/next_tasks.py` (`is_blocked` / eligibility), `automation/orchestrate.py`
   (the picker), and `scripts/artifacts/generate_status_overview.py` (render scheduled
   vs. blocked). Note the governance boundary: `scripts/task_ordering/` is edit-locked
   behind `claude-modify-ordering-rules`, and any `scripts/tasks/` change routes through
   `claude-write-script`. Map which module each change belongs to.
4. **Re-arming / recurrence.** Who advances the date after a run — the task itself on
   completion, a skill, or the orchestrator? Is recurrence a property of the gate
   (`every: monthly`) or just a fresh `not_before` written by a re-arming step? Keep the
   primitive minimal; recurrence can be a thin layer on top.
5. **Downstream consumers.** Name them and check the design serves all: (a) the monthly
   dependency review (REQ-PROC-061 AC-01); (b) AC-04 quarterly deferred-dependency
   re-evaluation; (c) the per-release dependency sweep (AC-03); (d) any "remind me / do
   not start before X" task. Does one primitive cover all four?
6. **Relationship to `feat_perpetuating_task_creation` (REQ-PROC-065-06).** That feature
   re-arms via *work-discovery* (spawn an Opus agent, scan for remaining work). This is
   the *calendar / time-triggered* sibling. Are they two faces of one "perpetuating task"
   concept, or genuinely separate mechanisms that should not be conflated?
7. **Reliability tradeoff vs. cron.** A date-gated standing task only fires when the
   orchestrator next runs *after* the date; a cloud cron fires regardless (but cannot run
   the toolchain). For a monthly cadence, is "picked up within ~a day of the 1st"
   acceptable against AC-01's "does not depend on the agent remembering"? What is the
   failure mode under long orchestrator dormancy, and what backstops it (per-release
   sweep)?

## Execution Model

Gather raw material first — read `next_tasks.py` (eligibility/`is_blocked`),
`orchestrate.py` (picker), `generate_status_overview.py` (rendering), the state-machine
placeholder (REQ-PROC-065-04), the perpetuating-task spec (REQ-PROC-065-06), and the
dependency-lifecycle requirement (REQ-PROC-061, esp. AC-01/AC-03/AC-04). Synthesize
across rounds before converging on a single recommended design.

The session's model is fixed at launch (Opus — `opus_recommended: true`). No mid-session
model switching.

**Web research** (optional): if it helps to see how other task/CI systems express
"not before" / deferred-eligibility (e.g. cron-vs-queue scheduling, "snooze" semantics),
delegate to a spawned `general-purpose` agent with a focused question; never run
WebSearch inline.

## Output

A future implementer should be able to read the output and know: the recommended field
(name, type, semantics) and how it composes with `after`/`awaiting`/`status`; whether it
warrants a distinct rendered "scheduled" state; the exact requirement home (this feat vs.
a new `feat_task_scheduling`) with proposed AC text ready to feed `requ-explore`; the
ordered implementation surface mapped to the correct governed skill for each module; how
re-arming/recurrence sits on top; and confirmation that the four named consumers are all
served. The output must be explicit about the cron-vs-standing-task reliability tradeoff
and what remains uncertain.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Out of scope (follow-up impl tasks once the AC lands): implementing the primitive,
converting the monthly review to a local standing task, and retiring the remote
`monthly-dep-review` cron. This task only designs the primitive and produces its
requirement grounding.

Related: REQ-PROC-061 (dependency lifecycle — first consumer), REQ-PROC-065-06
(perpetuating-task creation — the work-discovery sibling of this calendar variant),
TASK-PROC-061-05 (the escalation that surfaced the gap).
