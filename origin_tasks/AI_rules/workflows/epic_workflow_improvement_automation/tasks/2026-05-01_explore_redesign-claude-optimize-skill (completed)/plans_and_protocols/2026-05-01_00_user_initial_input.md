# User Initial Input — 2026-05-01

Raw, unedited starting point provided by the user when creating this task. Not a specification — a collection of questions, hunches, and directions worth investigating. Some will lead somewhere; others won't.

---

things we need to explore:
1. what is "optimize"? what is improvement? what is better?
- starting point for exploration/ideation: user need documents (personas, because they define the apps goal and purpose, it's abstract but a good baseline for deduction), requirements (describe what the app and the software factory shall do, so here we see if something does not meet expectations), logic (reasoning about what could mean better, only works if user needs and requirements are used as basis), websearch (there are many people that share skills and best practices online, that helps to see what is possible with llm, the tech stack and also in the business goal domain).
2. how does the skill work?
- starting point: a script can be used that creates a task file automatically after each skill run (inspiration is scripts\tasks\create_orchestration_task.py).the script uses awais to block it such that it is surfaces after the next 10? tasks. caution: next tasks.py does not show tasks that are blocked by other taks, so the script can't just use the top 5 tasks returned by next task.py. instead it has to check the awaits graph for the first result (that might get complicated). 
- also: the skill must check the last 10? tasks that ran and decide what could be improved. how? also it should not improve mechanisms again and again unless there is a chance that improvement is still possible. how to know that? it probably needs a log of past improvements to know what it did and see where it already could make improvements and see if the imrpovmenets get smaller and smaller, so that it is not worth it anymore. 
- how to measure improvement? is there a way to rate it? the skills makes improvements, but how does it know that it actually works? maybe the improvements make things worse. inspiration could be the skill optimizer we have loaded as plugin.
- how to avoid context window overflow if we improve 10 tasks?
- it will consum,e a lot of tokens, cause it needs to do a lot of research and thinking. how to avoid that? run it not that often? good heursitic to chekc if improvemnts make sense and skipp early? but how to make sure that we don't skip to early?
- what phases are needed? pick something to optimize (incl check history) > define what optimization means in that context (that might alredy need research in the web) > do research for ideas how to improve it > create a plan > define how to measure success/improvement > create a new workbench to perform benchmarking > iterate?
- also include a "bugfix" improvement path were all the research in the web is skipped, because the observed behaviour clearly does not match the expectations according to project documentation? there it might just be a broken script that needs a fix are a line in a skill file.
3. premissions
- claude code alsoways asks the user for permission when the llm tries to change skill files or claude.md. there must be a way to disable that for this skill.

and many things more! that's just a starting point I expect a deep iterative exploration, ideation, research  and reasoning. the task shall use sonnet for information gathering and opus for ideation, reasoning, ideation.
