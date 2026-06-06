# User Initial Input — 2026-05-23

Raw user request (lightly reformatted for readability, content unedited):

---

Create a new skill that is similar to task-create-code (which probably also needs an update) and somehow also to requ-derive-from-flow. It must prevent what we saw here: tasks have been created to implement a requirement, but not everything was covered and importantly: there was no verification! I want this task to ensure that certain quality criterias are met when tasks are created for a requirement.

In contrast to the generic task-create skill, which does not focus on creating tasks from requirements, but can also be used to for example create exploration tasks that have the goal to write/modify requirements.

The new task shall of course evaluate if it would make more sense to integrate into task-create or if a new dedicated task makes sense. It must explore different things, at least:

1. Which workflows exist? E.g. there is an exploration task that writes a new requirement. requ-explore is used. The new skill is then used in the same session right after writing the new requirement to create the implementation tasks. Or the requirement is old and a gap was discovered, now a new task is created to implement something to fix the gap. Also it must respect that it is possible that a dedicated exploration task exists that has the goal to create implementation tasks for an existing requirement. And many other workflows. Imagine what the user might request and when. Also consider product-intake and other skills.

2. Does not target coding of files in lib/ or test/ or anything that is handled by task-create-code.

3. Makes sure that tasks are created based on good information: maybe other requirements are important because the thing that needs to be created needs to interact or integrate. The existing stuff/files that touch the new thing need to be understood, etc.

4. Make sure that a good plan is created about the best way to actually implement the requirement. A multi step process is required: information gathering, analysis, ideation, weighing the options against each other, divide and conquer. Actually maybe even doing that in multiple iterations because we might have to go from the big picture into the details. But note: the actual details of how exactly to do something are to be defined by the tasks that are to be created when they are finally executed. So we need a good way to deal with that uncertainty. The process that creates the plan must make sure that it is implementable and the best solution but without doing all the work already - that's the job of the tasks. So: there's also the possibility to create just a task that has the goal to do a spike and then create other tasks. We have many options here.

5. There are minimum requirements what is actually part of the tasks: everything of the requirement must be covered and importantly: the implementation of the requirement must be verified and when possible also tested. We need a quality gate that checks if the requirement is actually implemented. We already have such verification steps in multiple processes, but obviously not here (which caused a problem now).

6. Other things I'm too lazy to write down. Think about it, you're smart!
