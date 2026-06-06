---
task_id: TASK-PROC-010-01
type: explore
parent_requirement: REQ-PROC-010
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-01-18
effort: XL
created: 2026-01-17
after: []
awaiting: []
covers:
  sections: [SEC-01, SEC-02, SEC-03, SEC-04, SEC-05, SEC-06, SEC-07, SEC-08, SEC-09, SEC-10]
scope_description: "Complete exploration and implementation of user needs structure (personas, scenarios, user flows) - Phase 4 added 2026-01-18"
requirements_version:
  commit: f95f611841ad397f909dde5d7f8be94b0fbf933a
  file: ../requirements.md
  note: "Updated 2026-01-18 to include Phase 4: Content Improvement"
---

# Goal: Implement User Needs Structure (Personas, Scenarios, User Flows)

## Objective

Create the complete `requirements_user_needs/` folder structure with:
1. Folder structure for personas, scenarios, and user flows
2. Comprehensive README.md with rationale, definitions, and writing guidelines
3. Define and explore optimal formats for personas, scenarios, and user flows
4. Create initial persona content from user-provided material
5. Define meta information standards and ID system
6. Define cross-referencing system between user needs and requirements_tasks
7. Plan skill modifications needed (create-persona, create-scenario, create-user-flow)
8. Define validation rules and hierarchy constraints

## Requirements Summary

This task implements **REQ-PROC-010: User Needs Structure Enhancement**, which adds a new layer above the existing requirements_tasks structure to capture:

- **Personas**: User archetypes with needs, constraints, and mental models
- **Scenarios**: Goal-oriented situations where personas try to achieve something
- **User Flows**: How the app helps achieve scenario goals (can touch multiple epics)

**Key Requirements**:
1. New folder `requirements_user_needs/` sits above `requirements_tasks/`
2. Hierarchy: Personas → Scenarios → User Flows → Epics → Features → Tasks
3. Cross-references between user flows and epics/features
4. Meta information with unique IDs (PERSONA-xxx, SCEN-xxx-xx, FLOW-xxx-xx-xx)
5. Validation rules ensuring lower levels don't contradict higher levels
6. Writing guidelines emphasizing psychology, behavior, and context over demographics

**Important Notes from Requirements**:
- Formats shown in requirements are **starting points**, not final decisions
- Task must **explore** optimal formats for personas/scenarios/flows
- Need standardized way to mark "grounded by data" vs. assumptions
- Proto personas first, adapt with real user data later
- References must include **commit hash** because files change over time
- Extensive appendix with best practices (Jobs to be Done, mental models, etc.)

**Requirements Version History**:
- Initial version (2026-01-17): commit 330603f96cebe22fba6865eb85458d1725ae75de
  ```
  git show 330603f96cebe22fba6865eb85458d1725ae75de:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
  ```
- **Current version (2026-01-18)**: commit f95f611841ad397f909dde5d7f8be94b0fbf933a (includes Phase 4: Content Improvement)
  ```
  git show f95f611841ad397f909dde5d7f8be94b0fbf933a:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
  ```

Current requirements: ../requirements.md

## Scope

### In Scope

**Phase 1: Foundation & Structure**
1. Create `requirements_user_needs/` folder structure
2. Create comprehensive README.md with:
   - Rationale (why we need this layer)
   - Structure explanation
   - Definitions of personas/scenarios/user flows
   - Writing guidelines (incorporating appendix best practices)
   - Meta information standards
   - Cross-referencing examples
   - Validation rules

**Phase 2: Format Exploration & Definition**
3. Explore optimal format for personas:
   - Incorporate best practices from appendix (mental models, JTBD, constraints)
   - Define sections and required fields
   - Determine how to mark "data-grounded" vs. "assumed" information
   - Create template with examples
4. Explore optimal format for scenarios:
   - Incorporate best practices (3-act structure, internal monologue, etc.)
   - Define sections and required fields
   - Create template with examples
5. Explore optimal format for user flows:
   - Incorporate best practices (happy path + exceptions, recovery paths)
   - Define how to document unhappy paths
   - Create template with examples

**Phase 3: Initial Content Creation**
6. Create initial persona files from user-provided content:
   - Dr. Thomas (Therapist)
   - Max (Client with Depression/ADHD)
   - Sarah (Self-User)
   - System/Maintenance
7. Create example scenarios for at least one persona
8. Create example user flows for at least one scenario

**Phase 4: Content Improvement (manually added phase during phase 3 based on created personas)**
9. The user wants to improve the created personas. He will provide instructions how to improve them, ask.
10. This persona improvements might lead to changes in the scenarios and changes in the scenarios might lead to changes to the user flows. Do not perform those changes, but create a plan that defines the necessary changes and include in that plan how the files could be improved to make this process easier in the future. This is also a test to discover how easy it is and how the file structures should change to inform the next step. 
11. Define a process, how changes to personas in the future will cause changes to all other layers, including the epics and feature requirements and eventually also lead to the creation of tasks that have the goal to modify the app to adopt the changes. This process needs to be reflected in the tooling (e.g. existing and/or new skills have to perform the steps defined by the process). To define a good process, changes to the rules how the files must look like are allowed.
12. Create a new task that has the goal to refine the personas to match the user input. The goal file must reference the user change requests from step 9. One question has to be clarified first: Where to place tasks that have the goal to create/modify information in the folder requirements_user_needs? Do we have to create a task folder in there to have a place to store the tasks? If yes, how to deal with that regarding existing scripts ands skills?

**Phase 5: Integration & Tooling**
13. Define how cross-references work in practice:
   - From user flows to epics/features
   - From epics/features to user flows (YAML format integration)
14. Document skill modifications needed:
    - New skills: create-persona, create-scenario, create-user-flow
    - Modified skills: setup-task, verify-quality, explore-requirements
15. Define validation rules and scripts needed
16. Create a new task to implement the changes to the skills.

### Out of Scope

- Creating ALL personas/scenarios/flows (only initial examples)
- Actually modifying skills (documented, but implementation is separate task)
- Creating validation scripts (defined, but implementation is separate task)
- Backfilling existing epics/features with user needs references (separate phase)
- Migrating content from requirements_general_overview (manual user task)

## Acceptance Criteria

- [ ] Folder structure `requirements_user_needs/personas/` exists
- [ ] README.md exists and contains all required sections:
  - [ ] Rationale and benefits
  - [ ] Structure explanation
  - [ ] Persona definition and format (incorporating appendix best practices)
  - [ ] Scenario definition and format (incorporating appendix best practices)
  - [ ] User flow definition and format (incorporating appendix best practices)
  - [ ] Meta information standards
  - [ ] Cross-referencing system
  - [ ] Writing guidelines
  - [ ] Validation rules
  - [ ] Data grounding methodology
- [ ] At least 1 complete persona file created (persona.md with full content)
- [ ] At least 1 complete scenario file created
- [ ] At least 1 complete user flow file created
- [ ] Templates documented in README for all three levels
- [ ] Cross-reference examples documented
- [ ] Skill modification requirements documented
- [ ] Validation rules documented
- [ ] All files use English language

## Implementation Steps

1. **Research & Analysis**
   - Read appendix thoroughly to understand best practices
   - Read user-provided initial persona content
   - Identify key elements for each level (persona/scenario/flow)

2. **Create Folder Structure**
   - Create `requirements_user_needs/` folder
   - Create `personas/` subfolder
   - Create example persona folder structure

3. **Draft README.md**
   - Write rationale section
   - Document folder structure
   - Define personas (incorporating appendix wisdom)
   - Define scenarios (incorporating appendix wisdom)
   - Define user flows (incorporating appendix wisdom)
   - Define meta information standards
   - Define cross-referencing system
   - Define writing guidelines
   - Define validation rules
   - Document data grounding approach

4. **Create Initial Persona(s)**
   - Transform user-provided content into structured persona.md
   - Apply best practices (mental models, JTBD, constraints, etc.)
   - Mark which parts are grounded vs. assumed

5. **Create Example Scenario**
   - Choose one persona
   - Create detailed scenario following 3-act structure
   - Include internal monologue, friction, context

6. **Create Example User Flow**
   - Choose one scenario
   - Document happy path + unhappy paths
   - Include edge cases and recovery paths

7. **Document Integration**
   - Define how epics/features reference user flows
   - Define YAML format for cross-references
   - Create examples

8. **Document Tooling Needs**
   - Specify skill modifications needed
   - Specify validation scripts needed

9. **Review & Validate**
   - Check all acceptance criteria
   - Verify structure matches requirements
   - Verify best practices incorporated

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-009 | implemented | Existing requirements structure must exist |

## Notes

### Key Insights from Appendix

**Personas**:
- Focus on **psychology, behavior, context** not demographics
- Include: Mental models, JTBD, emotional context, tech ecosystem, fears/barriers
- Define anti-persona traits (what they're NOT)
- Use real quotes from user interviews
- For mental health apps: energy budget and shame threshold matter more than age

**Scenarios**:
- Use 3-act structure: Context/Trigger → Interaction/Resistance → Result/Feeling
- Include internal monologue (doubts, fears, shame)
- Show imperfections and failures, not just happy paths
- Focus on emotional goals, not just functional tasks

**User Flows**:
- Separate happy path from unhappy paths (exceptions model)
- Document recovery paths for all errors
- Consider local storage failures (corruption, full storage, app kill)
- Distinguish user errors vs. system errors
- For mental health: adapt UI based on user state (e.g., hide streaks if mood < 3)

### Data Grounding Strategy

Need to define how to mark:
- **Grounded**: Based on user interviews, research, data
- **Proto-persona**: Based on assumptions, needs validation
- **Hypothesis**: Educated guess to be tested

Approach: Use commit hashes in references since personas evolve as we gather data.

### Initial Persona Content (User-Provided)

See user message for initial German-language persona descriptions:
- Der Therapeut: "Dr. Thomas" (Effizienz & Sicherheit)
- Der Klient: "Max" (Barrierefreiheit & Motivation)
- Der Selbstnutzer: "Sarah" (Autonomie & Insight)
- System-Rolle: "Maintenance & Notfall"

Transform these into structured persona.md files following best practices.
