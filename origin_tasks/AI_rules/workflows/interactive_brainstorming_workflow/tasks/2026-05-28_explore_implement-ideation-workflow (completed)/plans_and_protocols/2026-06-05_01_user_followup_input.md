# User Follow-up Input — 2026-06-05

Verbatim message that extended this task's goals (typos and formatting preserved):

---

There is a task with the goal to explore how the new iteration/brainstorming skill/agent should work. I want you to extend the tasks goals: the new ideation process shall also take into account that the process we currently have has the problem that the llm produces a "synthesis" documet that still has open questions. I think sometimes the research question is just too large and the llm can't answer it in one run, because it has a maximum thinking budget and a maximum output budget. In such a case the llm needs to run multiple times producing followup iterations until everything is covered (in breath and in depth). The terminal condition is something like "until no gaps exist anymore".

---

Read this as a seed bed, not a spec. This input motivates the additions made to `goal.md` on 2026-06-05 (Objective, Background, Seed 7, Output, Acceptance Criteria).

## Clarification (2026-06-05, verbatim)

> "how a follow-up iteration reacquires just enough context without a full reload" => That's not actually the problem. The problem is not the limit of the session or the context window of the session itself, but the amount of output the LLM can produce for one single request.

Interpretation applied to `goal.md`: the binding constraint is the **per-request output budget** (and per-request thinking budget) — a single response cannot emit the full answer, even though the model still holds all the context. This is distinct from the input-context / context-window / token-reload concerns of Seeds 1/2 and REQ-PROC-059. Context re-acquisition only becomes relevant if a follow-up iteration is implemented as a cold restart (new agent), which is a vehicle choice downstream of this root cause, not the root cause itself.
