# User Initial Input (verbatim seed bed — read as seeds, not a spec)

Captured 2026-06-05. These are the developer's unedited messages that prompted this task,
from the session where TASK-PROC-069-03's planning surfaced the underlying problem.

---

> maybe we need an opus agent for the planning phase even when use opus is set to false for the task. maybe only if the task targets skill or claude.ms changes...

> yes, capture it as a process task. i also like idea c more than b. also works for sessions already running opus.
> could be a pattern that can apply to all planning work, not only for task-resolve work split planning, but also to for example architectural planning

> i don't like that requ [REQ-PROC-059] we should resolve it in the future. it can host almost anything. is the factory quality about the quality of the factory or about the quality of the output/outcomes of the factory?

> add a note to REQ-PROC-059 that it is still valid, but must not be used for new requ and tasks and that it will be merged in other/new features.
> yes REQ-PROC-044

---

## Originating evidence (the concrete trigger)

During TASK-PROC-069-03 planning, a Sonnet session mis-planned an agent-vs-inline work split:
it assumed `claude-modify-skill` (a Skill invocation) isolates context the way an agent does, so
it concluded "Agents: none" and would have run 6 `claude-modify-skill` calls inline — piling
~2,600 lines of repeated `INDEX.md`/`factory_flows.md` reads into the persistent main context.

The gap was a MISSING RULE, not a model deficiency: once the Skill-vs-Agent context distinction was
written into CLAUDE.md §2 (Agent Delegation Economics, commit 588325cf), a *restarted Sonnet session*
planned the same task correctly. Separately, a manual Opus review of the flawed plan had caught the
errors before execution.

Two lessons feed this exploration:
1. Rules generalize; a stronger model on a single run does not. Writing the rule down fixed it for every future run.
2. An independent review of the plan caught what the planner could not see in itself.
