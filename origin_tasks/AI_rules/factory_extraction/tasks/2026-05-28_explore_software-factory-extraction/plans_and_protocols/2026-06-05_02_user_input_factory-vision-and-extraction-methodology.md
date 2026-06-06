# User Input — Factory Vision (Citizen Developers / Ethics / Personas) & the Extraction Methodology

*Verbatim, lightly punctuated and paragraphed for readability only. Read as a seed bed, not a spec.*
*Captured 2026-06-05. Continues `2026-05-28_00_user_initial_input.md` and `2026-06-02_01_user_input_deployment_and_testing.md`.*

---

## Goal of the Factory

The end goal is a product that can be used by anyone to create software — enabling citizen
developers.

Some things that would be required for that:

**GUI.** First step: show user-needs artifacts in a browser.

**Ethical considerations.** The designer and product manager is responsible for all harm
that is caused by the produced software. There needs to be a harm checker in the
user-needs artifact-creation skills. Harmful outcomes must be presented to the user in an
objective, not patronizing way. There needs to be a line that, if crossed, causes the LLM
to try to refuse to continue. Also the LLM shall suggest alternatives that cause no harm
and still serve the personas. Effects on other people, animals, and resources — now and in
the future — must be considered. That includes all types/categories of harm, from
increasing inequality to genocide.

**Support for more personas.** Currently we only support a single developer who develops a
Flutter app. Characteristics of the current single supported context:

- The Flutter app is offline-only — there is no server involved.
- The developer works on a Windows machine with WSL installed and a dev container running
  on WSL.
- The developer uses Claude Code only, with multiple accounts on the Pro plan. (Someone who
  has to pay the normal API prices might not want to use it, because no token-cost-savings
  optimization has been done yet.)
- Currently all requirements, all user research — everything — is in one repository. There
  is no ticket system like Jira or any other external data storage for any of the
  artifacts. Everything is created inside this repository. There is no external UI screen
  creation in Figma, for example, or other tools that feed information in. This is
  intentional: other software that uses AI of course uses the same models — the effort to
  extract the information from the repository, hand it as a prompt to external software, and
  then bring the result back into the repository was not considered worth the effort.
- Additionally, the developer has all roles: project management, PO, market research,
  UX/UI design, software engineering, …

If someone wants to use the Software Factory who is, for example, not using Claude Code, it
will not work out of the box. There are many things that would have to be adapted if
someone with other needs wants to use it. But given that the Software Factory uses itself
to improve itself, that shouldn't be too difficult.

---

## The Extraction Process

The extraction must happen with as little developer interaction as possible, while still
producing very good quality. We have to develop a plan for how to achieve that. We have to
think about which decisions have to be made in advance by the developer, so that during
execution there are as few questions left as possible.

Things I already anticipate need deciding up front:

- which personas should exist,
- which scenarios should exist,
- how to structure the requirements,
- how to write the requirements that are currently missing — because not every skill, not
  every aspect of the Software Factory actually has a requirement; some were just created,
  skipping the requirements. But I think from reading the skills, the scripts, and the
  agents we can actually derive requirements.

### The two-sided problem

We now have the problem that we start from two sides at the same time. On one side we have
the persona(s), which should guide what has to be implemented. But in this case we already
have something implemented. So we have to reverse-engineer the user needs from the existing
implementation. "Implementation" here means skills, and the artifacts used by the skills:
agents, scripts, and so on.

I don't know how well that works, but I think it makes sense to read the implementation and
reason about what the user needs behind the implementation are. For that we need a process —
certain steps. For example, the LLM has to think about which persona would be interested in
a given piece of implementation.

### Proposed step order

1. **First create the personas.** Then start the implementation analysis.
2. **Implementation analysis.** The LLM checks the implementation and compares it to the
   personas, reasoning about what benefit those personas have from this particular
   implementation.
3. The first result would be a collection of **"tasks the user wants to perform"** (the
   term "user needs" is difficult here, so "tasks the user wants to perform" may be better).
4. From those tasks we **analyze and combine them to form scenarios.**

### Scenarios — difference from the Flutter app project

Unlike the Flutter app project, for the Software Factory project I do **not** want to write
scenarios that describe how users behaved *before* the solution existed. (In the Flutter app
we have scenarios describing what users did before the app existed.) For the Software
Factory I want scenarios that describe how the users **actually work with** the Software
Factory.

And we can ground some of these — maybe not everything — in data, because we already have
the Software Factory in use. It's new; not everything is completed and not everything works
perfectly round; not everything has been used that often. But at least some of those
scenarios can be grounded in empirical observations of how the developer used the Software
Factory so far.

So once we have personas defined and the implementation analyzed, it is possible to derive
scenarios. We have to be careful **not to create too many.** There is a real risk of being
too fine-grained and writing one hundred scenarios — that would not benefit us. So there is
a task to define **how many scenarios are needed.** To do that we have to think about what
level they should be at — how detailed — and how large the gaps between them can be. We have
to decide **how much coverage** we actually want.

### User flows — same logic

The next step is to derive user flows. It's the same as for scenarios: since we already have
the implementation, we can write the user flows based on the implementation (and on the
scenarios). We also have to make sure to find user flows that are **large enough** so that
one user flow can cover as much implementation as possible. We have to define how that is
possible — we don't want very small user flows and an immense number of flows. We want **as
few user flows as possible**, but it has to still make sense and be understandable. We
cannot just squeeze everything into one user flow.

### Requirements — derive, double-check, restructure, map, fill gaps

Once we have the user flows, we keep following the process: we derive the requirements from
the user flows. Those requirements should describe what is actually implemented. At this
stage we probably also have to **double-check that the requirements actually still describe
what is implemented.**

Here we have to be careful: we already have a lot of requirements. So we have to do
something the Software Factory currently does not support — we have to **restructure the
existing requirements.** I think we already have a proposal for how the new structure should
look, but we have to be more specific about it. Then we **map the user flows onto the
existing requirements** (after they have been restructured), and **fill the gaps** — because
not everything that is implemented has requirements yet. Deriving requirements from the user
flows and mapping them onto existing requirements is exactly how we surface those gaps. Once
the requirements are updated, we continue to follow the process and define tasks where
needed.

### Tasks — already-completed-at-creation, and brownfield reuse

This part is tricky because the implementation already exists. We would write tasks that are
**already completed** at creation time. So we also have to invent a **new skill** that lets
us write tasks that are already completed at the moment they are created.

Thinking about it: maybe we should provide this functionality in the Software Factory
generally, in case someone wants to use the Software Factory for a **brownfield project** —
because that is exactly this use case. The Software Factory itself is a brownfield project:
some things already exist in the requirements (so in some regards it already uses the
Software Factory), but in many things we still have to add. So the process we define now —
how to extract a Software Factory and fill the gaps — is actually something anyone needs who
wants to use it on a brownfield / already-existing project. It would be a waste to find a
solution now and then throw it away. We should build a solution that works and can be reused
by other people later. (That was an idea in between.)

### Why we need tasks at all even though it's implemented

You could ask: why do we need tasks if it's already implemented? Because requirements are at
a higher abstraction level — they describe **what**, not **how**. We have a definition
somewhere of the difference: what a requirement is on a feature level, what a requirement is
on an epic level, and what a task is. Tasks are important because they describe **how** to
implement, and they are the **single source of truth** — not the implementation.

The implementation is, if you think about it, more like the result of a compiler: the input
of the compiler is the requirement (including the task), and the output is the
implementation — which is disposable. That's how we define it in our Software Factory.

This is why we need tasks. It will be a lot of duplication, yes — the implementation is
already in place and we now have to write it again in a different format. But we need it.
Without the functionality documented in requirements and tasks, the implementation will
drift, because LLMs tend to delete things they think are unnecessary — and that can happen
fast. The best way to prevent the implementation from drifting away from the intended
functionality is to have a specification holding it in place — where the LLM can look and
see "that's needed, I cannot just remove it."

### Driving the work — the Ralph loop and automation

I already created the Ralph-loop mechanism because I thought it could be helpful to keep the
LLM working during this extraction — there are a lot of steps and a lot of work, and we need
a way for the LLM to work through it. The task that first explores whether the Ralph loop
actually helps for the extraction was scheduled **before** the extraction-exploration task,
because I first wanted a small exploration to see if it makes sense at all.

There are many details that have to be clarified to make that work: the LLM needs strong
guidelines and strong rules about what it has to build, when to stop, when to ask the user,
and when **not** to ask the user. Otherwise this autonomous Ralph-loop approach will not
work.

But no matter whether we use the Ralph loop or any other approach, the problem stays the
same: the developer does not have the time to sit next to the laptop and watch the LLM do
the extraction. **It has to be automated as much as possible.**
