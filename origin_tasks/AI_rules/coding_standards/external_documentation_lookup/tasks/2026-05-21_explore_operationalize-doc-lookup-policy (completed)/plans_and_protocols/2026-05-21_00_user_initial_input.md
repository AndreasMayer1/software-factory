# User Initial Input — 2026-05-21

The user's unedited words across the REQ-PROC-053 authoring session that
informed this follow-up exploration. Read as a seed bed, not a spec.

---

## On "we will do the implementation later"

> We will do the implementation later for that. First we write the
> requirement and after that we create a task that has the goal to do
> actually to actually implement some rules for the LLM to enable it to
> actually look up documentation at the right time And using the right
> method.

(This task IS that follow-up. But: "implement" here is loosely used —
exploration synthesis comes first; concrete skill amendments + context7
wiring are *further* follow-up impl tasks derived from this exploration's
synthesis.)

---

## On heuristics and workflow integration

> So of course when we are going to implement a mechanism to enforce
> that. We need also to uh find good rules or horistics for the LLM um
> that are placed and the existing skills we have so they are executed
> at the right time in the workflow. The implementation workflow. So
> that um this documentation lookup is actually done. And that can
> happen during implementing a new feature, but maybe also when
> implementing tests, because for tests you might also need um
> documentation depending on what you are testing and how you are
> testing, and so on.

---

## On agent-scope (explicitly named as exploration territory)

**Question:** Which agents/skills must comply?

**User answer:**
> I need an exploration and brainstorming to answer that.

---

## On LLM self-uncertainty and prior-art research

> "every time an agent is about to call an API surface it cannot
> demonstrably name the *current* shape of, the agent looks it up":
> since llms hallucinate and are usually quite confident and do not
> know what they don't know, it is unlikely that the llm will notice
> that it is not able to name the current shape...
>
> maybe we can do a web search in an agent. it's possible that other
> people already have a solution...

(Note: the AC-02 framing was already updated to lean on *external
evidence* not self-confidence — but the user's suggestion to *web-search
prior art* explicitly belongs to this exploration. Do it before
designing.)

---

## On checkpoint duplication across skill / agent boundary

> "Every code-producing skill in the project includes a
> documentation-lookup checkpoint at the workflow step where the
> authoring decision is made." => we need to make sure that the lookup
> is not done twice, for example once in the skill, then again in the
> agent.

(AC-07 was updated to "exactly one checkpoint per authoring chain" and
references a *task-scope lookup log*. The log's design — file format,
location, cache invalidation, dedup semantics across skill / spawned
agent — is part of THIS exploration.)

---

## On the dependency-update mechanism (out of scope)

> we currently do not have a mechanism in place that updates
> dependencies... that's a problem when defining this mechanism. in
> general I think that the pinned version is authorative, but i also
> think that we can already switch to the a new interface if the old
> one gets deprecated and the new one is alrerady available must not
> be a todo comment, but must be acted on directly. I'll create a new
> task in a new session that defines how we're going to do dependency
> updates.

(AC-05 was updated accordingly. The dependency-update mechanism is the
user's *separate* task in a *separate* session — this exploration must
NOT design it, but MUST identify the interaction seam.)

---

## Distillation (orientation only)

This exploration has THREE substantive blocks:

1. **Prior art** (web-search, delegated to general-purpose agent) — how
   do existing LLM coding tools handle this? Inform the design before
   inventing.

2. **Agent scope + checkpoint placement** — enumerate every
   code-producing skill / agent, decide where the AC-07 single
   checkpoint lives in each chain.

3. **Mechanics** — context7 integration mechanism; task-scope lookup
   log format; per-technology trigger thresholds; AC-02 (a)
   toolchain-clean verification; interaction with REQ-PROC-046 (gate
   failure → lookup) and REQ-PROC-001 (per-task lookup budget).

Output is design synthesis. Follow-up *impl* tasks (skill amendments,
context7 wiring) are derived from the synthesis, NOT pre-created here.
