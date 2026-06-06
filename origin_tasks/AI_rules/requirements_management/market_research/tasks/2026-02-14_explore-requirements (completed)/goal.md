---
task_id: TASK-PROC-029-01
type: explore
parent_requirement: REQ-PROC-029
urgency: 2
urgency_reason: U2-PLANNED
impact: 4
impact_reason: I4-PRODUCT_DIRECTION
status: completed
completed: 2026-02-14
effort: M
created: 2026-02-14
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Write market research requirement, create impl task for incorporating research into the project, create impl task for evaluating research quality"
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Market Research Requirements & Implementation Tasks

## Context

Initial market research was conducted via Gemini (see `Copy of App Marktanalyse.json` in this folder). The conversation covers:
- CBT/KVT-focused mental health apps in the German market (DiGA apps: HelloBetter, Selfapy, deprexis, Velibra, Invirto, somnio)
- Free/international apps (Woebot, MindDoc, CBT Thought Diary, Wysa)
- Blended care platforms (Minddistrict)
- Data protection analysis (DiGA vs. free apps, GDPR)
- Market trends: prescription-first, specialization, AI integration

Additionally there is `requirements_tasks\process\AI_rules\requirements_management\market_research\tasks\2026-02-14_explore-requirements\initial research november 2023.md` that contains a old research with not as much information.  

The user's vision is to incorporate market research as a **3rd requirements flow** (alongside the existing persona/scenario/user-flow flow and the UX/design flow). Market research should inform feature priorities and decisions, with traceable references so decisions can be reevaluated when new data arrives.

## Objective

Perform three steps:

### Step 1 — Write Market Research Requirement (use `explore-requirements` skill)
Write a proper `requirements.md` for `requirements_tasks/process/AI_rules/requirements_management/market_research/`. The requirement should:
- Be generic: "incorporate market research to ensure users are willing to use the app"
- Be approximately 30 lines including metadata
- Support extensibility (research is never finished; more data can always be added)
- Define the 3rd requirements flow concept clearly

### Step 2 — Create Impl Task: Incorporate Market Research (use `create-impl-task` with opus)
Create an implementation task whose goal is:
- Incorporate the market research into the project in an extensible way
- Define a workflow (Claude Code skill adaptations) that "pushes" information from market research into features in `requirements_tasks/functional/` and `requirements_tasks/non-functional/` (possibly via `requirements_user_needs/user_flows/`)
- Document the 3rd requirements flow alongside the existing 2 flows
- Ensure decisions referencing market research are traceable (references to source data)
- Support reevaluation when new research data arrives

### Step 3 — Create Impl Task: Evaluate Research Quality (use `create-impl-task`, NO opus)
Create an implementation task whose goal is:
- Evaluate the quality of the market research created by Step 2's process
- Identify gaps in the market research
- Double-check that the process for making market research usable in app development makes sense
- Identify improvements to the process and data organisation inside the market research folder

## Scope

### In Scope
- Writing `requirements.md` for the market_research requirement
- Creating 2 implementation tasks (impl tasks, not actual code)
- Defining the concept of a 3rd requirements flow (market research → features)

### Out of Scope
- Actual implementation of the workflow (that's Step 2's impl task)
- Actual evaluation of research quality (that's Step 3's impl task)

## Acceptance Criteria

- [ ] `requirements.md` written with proper YAML, ~30 lines, extensible framing
- [ ] Impl task created for incorporating market research (opus quality)
- [ ] Impl task created for evaluating market research quality

## Notes

- Research data lives in this task folder (Gemini JSON conversation)
- The `initial-research.md` file in this folder is a placeholder (currently empty)
- REQ-PROC-029 assigned to the market_research requirement
