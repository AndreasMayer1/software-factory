# User Input — Self-Deployment & Artifact Validation

*Verbatim, lightly punctuated for readability only. Read as a seed bed, not a spec.*
*Captured 2026-06-02. Continues `2026-05-28_00_user_initial_input.md`.*

---

## Thought 1 — Output folder + deployed copy + a deploy mechanism

We already added that the software factory project must (or should) also contain the
same user needs and requirements that the normal project does. So in principle the
software factory project uses itself to define itself. I think that's a good idea and it
will work.

One quick note about that: the software factory probably needs to have the things that it
produces — which are skills and agents, for example — in a dedicated output folder. (I
don't know how to call it; in a software project it would be the `lib` folder.) And it
would also have to have a copy of its own output again inside the `.claude` folder,
because when the LLM is working on the project it has to have those skills and agents
loaded in the folder that is defined by the coding tool — in our case Claude Code.
Otherwise those skills and agents cannot be used by the LLM.

That means, of course, that whenever the software factory project runs and changes its
products, there must be a mechanism that deploys those results to the software factory
itself. That could just be a script that copies the changed files from the output folder
to the `.claude` folder.

## Thought 2 — Validation / tests for scripts, skills, and agents (the larger one)

Since the output of the software factory is actually skills and agents and other
artifacts that are used by an LLM to create something, we cannot just run unit tests and
integration tests like we do when we create code.

If the software factory is used to create code, it's easy: you have the user needs, the
requirements, the tasks; the tasks implement code; and then there's validation of the
code. Unit tests are written, integration tests, and there's a loop of iteration until
the code works and matches the requirements. The developer does not have to do much — he
defines the requirements and the LLM iterates using the automated tests until the result
is good enough. Then the user does a review again, because maybe the requirements were not
precise enough, for example. But thanks to those automated tests the quality is already at
a very high level, and the user does not have to be in the loop the whole time. And there
are other automated quality gates like the back-pressure protocol we implemented, which
uses `flutter analyze`, lint, and other scripts that check the code for quality.

That's also something that does not exist for the artifacts that are created by the
software factory for itself. There is no automated way currently to check if the skills
and the agents and other artifacts that are produced actually work like they are intended.
One exception is the scripts — there are also scripts used in the software factory.
Everything that can be performed by a script is performed by a script; the LLMs are only
used for things that cannot be automated with a script.

My point is that for the software factory as a standalone project that uses itself to
improve itself — the software factory is used to develop the software factory — for that
to really work, we actually need validation, integration tests and unit tests for scripts,
skills, and agents.

How can that be achieved?

**(a) Real data from a real project.** For example the project we are currently working
on, which is documented — we also have this optimizer that is logging which skills are
used in which task. So we can retrospectively go through the git history and find where
skills have been used in the past. We can check out the old commit (well, one commit
before), make a branch, and re-run the skill. Before we re-run the old skill, we of course
have to deploy the new skill / the new software factory, and then run it and see how the
outcome compares to the original outcome in the git history.

It's not that easy to compare if the AI model changed. If this old commit is one year old
and the current generation of LLM model is so much more advanced, it will just produce a
better output — so we don't measure the improvement of the skill, but the improvement of
the model. In that case we might need to use the old model, if it's still available.

**(b) A small project of its own as a testing ground.** The software factory project
could contain a small project on its own that is used to test. It could be a very simple
project — I don't know, a calculator app, for example, in JavaScript. Maybe that's too
simple, but something that is just there and can be used as a testing ground for automatic
tests. We can think about doing unit tests where single skills or single agents are
tested, and also integration tests where the whole sequence of skill uses is tested to see
if they still work together after changes.

**(c) Expected-output / minimum-quality definitions.** For that to work we would also have
to have test files — like you write test files in programming languages — a file that
defines what the output must contain, like the expected minimum quality. That's already
defined by the requirements and by the tasks that created the skill. Maybe that's enough.
But we have to think about that.
