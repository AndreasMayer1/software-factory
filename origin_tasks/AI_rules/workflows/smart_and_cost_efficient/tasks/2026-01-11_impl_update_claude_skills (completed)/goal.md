---
task_id: TASK-PROC-031-01
type: impl
parent_requirement: REQ-PROC-031
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-DEV-EFFICIENCY
status: completed
effort: L
created: 2026-01-11
completed: 2026-01-11
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Integrate smart model-switching (Sonnet gather → Opus think) into 6 skills and 2 agents"
requirements_version:
  commit: f68c878
  file: ../../requirement.md
---

# Goal: Update Claude Skills with Smart Model-Switching Strategy

## Objective

Integrate the cost-efficient model-switching pattern (Sonnet for gathering → Opus for thinking) into multiple skills and agents. This pattern is already working in `opus-workflow` skill and needs to be applied to:

**Skills to update:**
- complex-implementation
- create-impl-task
- explore-requirements
- test-implementation
- update-guidelines
- verify-quality

**Agents to update:**
- architecture-advisor
- test-engineer

## Requirements Summary (at task creation)

I created a general workflow to use opus to analyze a problem in a cost efficient way by using sonnet first to read all relevant files and then switching to opus only for the thinking part. That workflow is defined in the skill opus-workflow.
It works well and I also want to use something similar for the other workflows. 

The task is to add the same principle to:
- complex-implementation 
- create-impl-task
- explore-requirements
- test-implementation
- update-guidelines
- verify-quality

The principle is simple, but to explain it some facts about claude code:

- Agents can be called with a model defined. Agents can define which model to use if no model is given when the agent is called.
- Agents start with an empty context window. That means, that an agent has to read all necessary information from files again.
- Agents can not give back everything they know (context window) to the main conversation, instead they have to write files and/or write a completion message.
- Agents can't start other agents. No nesting possible.
- Skills can be started by agents and by the main conversation.
- Skills do not start a new context window. If the main conversation (or an agent) invoke a skill, the skill instructions are loaded in the existing context. That means that no information is lost when a skill is called and when a skill is done, the information stays in the context. 
- Skills can define which model they want to use. That means that if the skill is started, the model is automatically changed if needed.
- While a skill is "executed" another skill can be started, that's no problem.

That means following is possible:
1. Main conversation/agent reads a lot of files or gathers information from other sources. 
2. Once that information gathering is completed, a skill is started with model opus. All the information that was gathered in step 1 is still avaiable to opus. Opus can now to heavy reasoning with all that information and write the details and conclusions to a report.
3. Opus is not needed anymore, we can switch back to sonnet. How can we do that? Yes, we could start another skill. BUT the problem is: the context window is quite full now, because we gathered so much information in step 1 and opus wrote a long report.WE CAN'T USE A SKILL. Instead we need to wrap everything in an agent: An agent is used that gets the task to perform step 1 and step 2. After the agent is done with step 2 it will terminate and return to the main conversation. The main conversation runs with sonnet, so there we have the model switch back.

Easy, right?

How can this be done in the existing skills mentioned above? We need to make sure that the rules are not violated. I will tell you how to modify the skills one by one. 

For all skills: Add a note in the beginning that it can be called with the optional instruction to use opus. This must not use opus from the start for the skill, but instead follow the additional instructions we add now to the skills. This opus usage is optional, the default is that the skills (and agents) run like they are currently defined, that means we add a switch. THat must be clear in the skill and agent descriptions/instructions.

## complex-implementation

Here it is a bit tricky because the most complex part is the creation of the high level plan. But that is done by the architecture-advisor agent. We have to modify the architecture-advisor agent as well. 

## architecture-advisor agent

The architecture-advisor agent starts with model sonnet. After phase 1 the model is switched to opus using the switch-to-opus skill. That means phase 2 is actually: Switch to opus if the agent has the instruction to use opus, otherwise stay with the current model. The currently existing phase 2 and following phases are pushed back.

## create-impl-task

Before step 3.3 the switch-to-opus skill is executed, so that the goal.md file can be written by opus. Also add an instruction that opus must think about the knowledge before writing the goal.md file. Or in other words: the switch-to-opus skill is used to execute step 3.3. 
After the goal.md file is written, the switch-to-opus skill must complete and the rest of create-impl-task steps are performed normally (which means that the model is switched back to the previous model automatically). 

## explore-requirements

The complete Phase 3 is done with opus. That means that switch-to-opus must for phase 3. Only for phase 3, switch-to-opus must complete once phase 3 is done so that the model is switched back automatically for the rest of the phases. 

## test-implementation

Most work is done by the test-engineer agent. In the test-implementation skill there is no need to switch to opus, but we have to modify test-engineer agent as well and pass the instruction to use opus to it.

## test-engineer agent

The switch-to-opus skill must be used for Phase 1 steps 3 and 4:
3. Analyze code to test
4. Create `plans_and_protocols/[date]_test_plan.md`
Everything else shall be done by sonnet.

## update-guidelines

(Instructions TBD - needs clarification on where Opus should be used)

## verify-quality

(Instructions TBD - needs clarification on where Opus should be used)

## Scope

### In Scope
- Modify 6 skills to support optional Opus-based thinking mode
- Modify 2 agents to integrate with switch-to-opus skill
- Add clear documentation about the optional Opus usage
- Ensure backward compatibility (default behavior unchanged)
- All changes maintain existing workflow structure

### Out of Scope
- Modifying other skills/agents not listed above
- Changing the default behavior (Sonnet remains default)
- Automatic detection of when to use Opus (user explicitly invokes)
- Modifying the switch-to-opus skill itself

## Acceptance Criteria

- [ ] All 6 skills updated with Opus-switching capability
- [ ] All 2 agents updated to support switch-to-opus skill
- [ ] Documentation added to each skill/agent about optional Opus usage
- [ ] Default behavior (Sonnet-only) preserved for all workflows
- [ ] switch-to-opus skill properly integrated at specified phases
- [ ] User instructions added for how to invoke Opus mode
- [ ] Backward compatibility verified (existing workflows work unchanged)

## Dependencies

None - this is a self-contained enhancement to existing skills/agents.

## Notes

**Key Design Principle**: The Opus mode is OPTIONAL. All skills and agents must work exactly as before when Opus is not requested. The switch happens only when explicitly instructed by the user.

**Implementation Pattern**:
1. Agent/skill gathers information (Sonnet)
2. switch-to-opus skill invoked for heavy reasoning
3. Opus writes detailed plan/analysis
4. switch-to-opus completes, returning to Sonnet
5. Sonnet continues with implementation

For complete requirements at task creation time:
```
git show f68c878:requirements_tasks/process/AI_rules/workflows/smart_and_cost_efficient/requirement.md
```

Current requirements: ../../requirement.md
