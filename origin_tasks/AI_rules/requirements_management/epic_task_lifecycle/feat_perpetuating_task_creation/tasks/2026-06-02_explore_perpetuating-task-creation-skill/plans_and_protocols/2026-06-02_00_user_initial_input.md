# User Initial Input — 2026-06-02

Read this as a seed bed, not a spec.

---

I want to have a special task create a skill that creates a task that has as last step before closing a step that creates another task for things that still have to be done. So essentially when executed it completes work in the end starts an agent with the opus model that looks for more work to do. And then creates a new task. And then the original task is completed.

Together with the automation, this is essentially a Ralph loop.

I suggest to use an agent to find more work and to find more work because that might require reading a lot of files. And I suggest to use opus as model because defining what to do next needs as much brain power as possible.

I don't want to duplicate the task create skill, but instead create a new skill that internally uses the normal task create skill. It's more of a wrapper around it.

I think it's not required that this new Ralph Loop tasks get a own type. I think the type implementation or exploration, for example, um stays as it as it is because this Ralph Loop Task can actually create implementation tasks and it can also create exploration tasks. Whatever it finds should be the next task, right?
