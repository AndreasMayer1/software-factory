# User initial input (seed bed) — verbatim, 2026-05-30

> Read this as a seed bed, not a spec. Lightly transcribed from the developer's
> spoken/typed messages that prompted this task.

---

**Reframe.**
"I changed my mind. Let's take a step back and think about the whole optimizer again.
We have a first implementation now. And we have some bugs, but we also have probably some
things that are not bugs, but essentially bad design. We have to tackle both. Also I think
we really need the optimizer to optimise itself as well — now that it is new, probably more
frequently than later. I also want to question how well the optimization actually works and
towards which targets we are optimizing. So I think the targets are the most important.
Well, maybe not the most, but very important. Because as we can see here with the example of
the optimizer, it creates a lot of events. And one could say that's fine — the optimizer now
runs two hundred times, no problem. But it IS a problem because it completely blocks other
work. So one target would of course be that we are still efficient — we are delivering the
product, the app, efficiently and in good quality. And for that we also have to keep token
usage as low as possible, because we run on a limited plan that only has a certain amount of
tokens per week. The more tokens we use, the more weeks we need for the same amount of work.
There are other targets as well, and I'm not sure we made them explicit enough. But the
targets are only one thing — the optimizer must actually be able to increase toward the
target, and I'm not sure we will be able to do it. That's also why I really want to let the
optimizer run on itself.

So my proposal: create a plan for a complete analysis of the optimizer — not only the
implementation and the bugs, but also the design and the alignment with the overarching
goals. Based on that plan, create tasks and, if needed, modify the tasks already created."

**North star (clarification).**
"The North Star is of course also the quality of the app. The app is the end result we are
producing, but to produce it we have a lot of steps. Every skill produces its own artifacts
that are then consumed somewhere else. So every part of the whole software factory has to
work toward this end goal, but in its own scope. Just writing that 'the end result must be
good' is the north star, but I'm not sure that's so easy to actually use as a metric."

**Reference pointer.**
"If you need, you can also read the exploration of the design we did before writing the
requirements." → the original redesign exploration (rounds 1–4) in
`../2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`.

**Surfacing / override context.**
The priority-override will be disabled once the scribble-skill redesign is done — maybe in
about a week. (So the surfacing design should target normal ranking, not a permanent
override bypass.)

**Decision already taken on the backlog (251 → 247 events example).**
Keep the autonomous trigger preempting, but prune the event backlog AND investigate why
there are so many events; address the one-event-per-cycle domination in this work.
