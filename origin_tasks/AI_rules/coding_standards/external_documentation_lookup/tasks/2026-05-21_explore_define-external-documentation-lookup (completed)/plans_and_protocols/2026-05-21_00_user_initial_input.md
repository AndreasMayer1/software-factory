# User Initial Input — 2026-05-21

The user's unedited words that prompted this exploration. Read as a seed bed,
not a spec.

---

## Turn 1 — User asks if a rule already exists

> Check if we have a requirement that contains information or rules about how
> or when the AI looks for documentation about used technologies. I mean of
> course the coding agents / the LLM. With used technologies I mean for example
> the official flutter documentation or the official documentation of
> dependencies we are using in the project.

(Search result: no such requirement exists today. The only adjacent rule is
REQ-PROC-046 §6 — "capture non-obvious fixes into doc/" — which is reactive,
not preventive.)

---

## Turn 2 — User decides to add the requirement

> Okay, then I want you to add this requirement. I want the LLM to be able to
> look up the documentation of the used technologies. So that the LLM is aware
> of the current way of programming because the training data the LLM is
> trained on is by nature outdated. That ensures that we are not using
> deprecated functionality. And it also closes the gap when the LLM has not
> enough training data for a specific use case. So Ultimately it's about
> quality of the produced source code. And it prevents errors. and
> maintainability. And of course other things I'm currently too lazy to spell
> out.
>
> This requirement must be technology agnostic, but I already have a solution
> how we can ensure that the agent can actually access up to date documentation
> in an efficient way without doing a web search: context7
> (https://context7.com/docs/overview)
>
> We will do the implementation later for that. First we write the requirement
> and after that we create a task that has the goal to do actually to actually
> implement some rules for the LLM to enable it to actually look up
> documentation at the right time And using the right method.
>
> Maybe one additional thing for the requirement. I also want it to contain
> that the LLM shall only read the documentation if it is required. So not too
> often. But on the other hand, of course, it shall read the documentation
> often enough. Whatever that means, right? ;)
>
> So of course when we are going to implement a mechanism to enforce that. We
> need also to uh find good rules or horistics for the LLM um that are placed
> and the existing skills we have so they are executed at the right time in
> the workflow. The implementation workflow. So that um this documentation
> lookup is actually done. And that can happen during implementing a new
> feature, but maybe also when implementing tests, because for tests you might
> also need um documentation depending on what you are testing and how you
> are testing, and so on.

---

## Turn 3 — Scope-clarification answers (AskUserQuestion)

**Q: Which technologies does this requirement cover?**
> anything in the requirment, but not enforced for everything. the "when to
> look something up" must depend on the specific technology.

**Q: Which code languages does the rule apply to?**
> as stated: potentially all code, but there can be different rules for the
> technology / the code types

**Q: Which agents/skills must comply?**
> I need an exploratrion and brainstorming to answer that.

---

## Distillation (not the spec — for orientation only)

- Policy itself is technology-agnostic.
- Per-technology / per-code-type *trigger heuristics* are explicitly allowed to
  differ — and are out of scope for this requirement.
- `context7` is the user's preferred lookup mechanism (efficient, LLM-indexed,
  no full web search).
- The agent-scope question (which skills must comply, at which workflow step
  the lookup fires) is itself an open exploration that follows this
  requirement — it is NOT to be pre-decided here.
- Balance the user wants: "not too often, but often enough" — definition of
  "enough" is deferred to the follow-up exploration.
