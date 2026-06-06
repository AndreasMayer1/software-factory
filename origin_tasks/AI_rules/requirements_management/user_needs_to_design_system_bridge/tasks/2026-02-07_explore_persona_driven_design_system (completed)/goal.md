---
task_id: TASK-PROC-026-01
type: explore
parent_requirement: REQ-PROC-026
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-PAIN
status: completed
effort: L
created: 2026-02-07
completed: 2026-02-08
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore and document methodology for bridging user needs (personas/scenarios) to UI/UX design system rules through design-as-code approach"
requirements_version:
  commit: null
  file: ../requirements.md
  note: "Parent requirement REQ-PROC-026 needs to be created first"
---

# Goal: Bridge User Needs to UI/UX Design System (Design-as-Code)

## Objective

Analyze the gap between existing user needs (personas/scenarios in `requirements_user_needs/`) and UI/UX design system rules (in `requirements_tasks/non-functional/ui_ux_design_system/` and `doc/`), then create an implementation task that modifies the project (skills, guidelines, processes) to enable AI to derive design decisions from user needs.

**Core Question**: How can the AI translate persona characteristics and scenario contexts into concrete design system rules (typography, spacing, interaction patterns, UX writing)?

## Requirements Summary

**Current State:**
- ✅ We have well-defined personas with mental models, JTBD, and constraints (`requirements_user_needs/personas/`)
- ✅ We have scenarios describing usage contexts (`requirements_user_needs/scenarios/`)
- ✅ We have UX/UI design system rules:
  - Material Design 3 baseline
  - Design tokens (spacing, colors, typography)
  - UX Writing guidelines (REQ-NFUNC-013)
  - Atomic Design principles
  - Accessibility guidelines (REQ-NFUNC-002)
  - Navigation patterns
  - Component specifications

**The Gap:**
- ❌ No documented process for deriving design rules FROM user needs
- ❌ AI doesn't know HOW to translate "Persona has visual impairment" → "Minimum font size 18px"
- ❌ No examples of persona-driven design decisions
- ❌ Design system rules exist in isolation from the users they serve
- ❌ Risk of arbitrary design decisions not grounded in user needs

**Desired State:**
- ✅ Clear methodology: User Need → Design Decision
- ✅ AI skills that reference personas during UI implementation
- ✅ Design system rules annotated with user need justifications
- ✅ Examples showing the translation process
- ✅ Guidelines in `doc/` that teach AI to consider personas

For parent requirement (to be created): ../requirements.md

## Scope

### In Scope

1. **Analysis Phase:**
   - Review all existing personas and identify design-relevant characteristics
   - Review existing UI/UX design system requirements
   - Identify specific gaps where persona needs aren't reflected in design rules
   - Study Gemini's suggestions and adapt to our project structure

2. **Methodology Design:**
   - Create mapping framework: Persona Trait → Design Decision
   - Define where design-as-code rules should live
   - Establish validation process (how to check if design serves persona)
   - Create templates for persona-driven design documentation

3. **Documentation:**
   - Document findings in exploration protocol
   - Create examples of good persona-to-design mappings
   - Identify which files need modification (skills, guidelines, requirements)

4. **Implementation Planning:**
   - Create detailed implementation task (via `create-impl-task` skill)
   - Define concrete changes to:
     - `.claude/skills/` (which skills need persona awareness?)
     - `doc/` (how should AI read personas during implementation?)
     - `requirements_tasks/non-functional/ui_ux_design_system/` (add persona justifications?)
     - New requirements if needed

### Out of Scope

- ❌ Actual implementation of changes (that's the follow-up impl task)
- ❌ Creating new personas (we use existing ones)
- ❌ Redesigning the app (we derive rules, not redesign)
- ❌ Modifying Flutter code (this is process/guidelines work)

## Acceptance Criteria

- [ ] All existing personas analyzed for design-relevant characteristics
- [ ] Gap analysis documented: which persona needs aren't reflected in current design system
- [ ] Clear methodology documented: how to translate user needs → design rules
- [ ] At least 3 concrete examples of persona-driven design decisions
- [ ] Identified which project files need modification (skills/guidelines/requirements)
- [ ] Implementation task created with actionable steps
- [ ] Validation approach defined: how to verify design serves user needs

## Exploration Approach

### Phase 1: Understand Current State (Parallel Reads)
Read in parallel:
- `requirements_user_needs/README.md` and key persona files
- `requirements_tasks/non-functional/ui_ux_design_system/*/requirements.md`
- `doc/presentation.md` (current UI implementation guidelines)
- `.claude/skills/code-simple/skill.md`, `code-complex/skill.md`

### Phase 2: Analysis
- Extract design-relevant persona characteristics (vision, mobility, cognitive load, context)
- Map existing design rules to personas (which rules already serve which users?)
- Identify unmapped persona needs (gaps in design system)
- Review Gemini's "Design-as-Code" suggestions and adapt to our structure

### Phase 3: Methodology Design
- Create persona-to-design mapping framework
- Define where rules should live:
  - `doc/presentation.md` additions?
  - New `doc/design_system_derivation.md`?
  - Annotations in requirements?
- Design AI workflow: when implementing UI, AI should...
  1. Read relevant scenario/persona
  2. Consider user constraints
  3. Apply/create design rules accordingly
  4. Document justification

### Phase 4: Create Implementation Task
Use `create-impl-task` skill to create concrete implementation task covering:
- Skill modifications (teach AI to reference personas)
- Guideline updates (`doc/` additions)
- Requirement annotations (add persona justifications)
- Example creation (show good practices)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-010 | completed | User needs structure (personas/scenarios exist) |
| REQ-NFUNC-013 | defined | UX Writing guidelines (example of design system rule) |
| REQ-NFUNC-002 | defined | Accessibility guidelines (related to persona constraints) |
| requirements_user_needs/ | populated | Multiple personas and scenarios exist |

## Context from Gemini's Suggestions

**Key Ideas to Validate:**
1. **Design-as-Code**: Document design decisions in code/markdown, not just Figma
2. **Persona-Driven Rules**: "Large buttons because Persona Bärbel (vision impairment)"
3. **Scenario-Based Testing**: Reference scenarios during implementation ("Subway scenario → offline support")
4. **Design Tokens + Why**: Not just values, but justification from user needs
5. **Documentation Structure**: Separate files like `STRUCTURE.md`, `UI_RULES.md`, `WRITING.md`

**Adaptations Needed:**
- We already have Material Design 3 as baseline (not "Material UI")
- We use Flutter, not React
- Our design tokens are in Flutter theme system
- We need to fit this into existing `doc/` structure
- Skills already exist - we enhance, not create from scratch

## Notes

**Philosophy**: Design decisions should be **defensible** through user needs, not arbitrary preferences. When someone asks "Why are buttons this size?", the answer should be "Because Persona X needs Y."

**Success Metric**: After implementation, when AI creates a UI component, it should naturally consider relevant personas and document why design choices serve those users.

**Follow-up Work**: After this exploration, the implementation task will modify actual files. After implementation, we can validate by asking AI to implement a feature and checking if it references personas.
