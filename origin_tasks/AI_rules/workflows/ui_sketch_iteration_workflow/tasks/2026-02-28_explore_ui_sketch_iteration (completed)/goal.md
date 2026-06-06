---
task_id: TASK-PROC-032-01
type: explore
parent_requirement: REQ-PROC-032-01
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-03-01
effort: L
created: 2026-02-28
after: []
awaiting: []
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04]
  sections: [SEC-01, SEC-02, SEC-03, SEC-04, SEC-05, SEC-06]
scope_description: "Explore and define the complete UI sketch iteration workflow: format, storage, AI rules, organization, and integration with existing implementation workflows"
requirements_version:
  commit: 222ba57
  file: ../requirements.md
---

# Goal: Explore and Define UI Sketch Iteration Workflow

## Objective

Research and define a complete workflow that allows the developer to iterate on UI design with the AI **before** any real Flutter implementation happens. The output of this exploration is a set of concrete decisions and documented rules that can be anchored in the project (either in `doc/`, a new top-level folder, a README, or another appropriate location).

## Background

The developer wants the AI to produce UI that matches their vision. Current design rules are incomplete — they don't cover everything that influences UI decisions. Rather than trying to specify all rules upfront, the preferred approach is:

1. AI generates a lightweight, static UI sketch
2. Developer reviews it and identifies missing rules
3. Rules are added, sketch is regenerated
4. Repeat until satisfied
5. Only then implement in Flutter

Iterating directly in Flutter is expensive because widget trees are complex, and restructuring UI architecture (e.g., form → wizard) requires extensive refactoring. Lightweight sketches enable cheap, fast iteration.

## Requirements Summary

For full requirements at task creation:
```
git show 222ba57:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Questions to Answer

### Q1: Sketch Format
- **HTML/CSS**: Easily viewable in browser, familiar, but requires maintaining a parallel styling system separate from Flutter design tokens
- **Flutter dev sandbox**: Uses real design tokens, but requires building/running the app; harder to view sketches as disposable
- **ASCII / Markdown**: Very fast to generate, but limited fidelity — may not clearly show element structure
- **SVG**: Text format, precise, but harder for AI to generate meaningfully
- **Evaluate**: What is the minimum fidelity needed? What can the developer actually use to assess information architecture and element placement?

### Q2: AI Behavior Rules
What exact constraints must the AI follow when generating sketches?
- Enumerate: what it MUST do (list all screens of a flow, show element hierarchy, label elements)
- Enumerate: what it MUST NOT do (interactions, data binding, BLoC, real routing, pixel-perfect styling)
- Where should these rules live? (`doc/` guideline? CLAUDE.md addition? Skill instructions?)

### Q3: Storage and Organization
Where do sketch iterations live in the project?
- Option A: Inside the requirement folder — `requirements_tasks/.../sketches/v1/`, `v2/`, etc.
  - Pro: Co-located with requirements, easy to find
  - Con: Mixes development process artifacts with requirements
- Option B: Top-level `ui_sketches/` folder with mirrored structure
  - Pro: Clean separation
  - Con: Two folder structures to maintain
- Option C: Dev-only area inside `lib/dev_ui/` or a separate Flutter app entry
  - Pro: Uses real design tokens
  - Con: Committed Flutter code that is not production

### Q4: Iteration Workflow
Define the exact steps:
1. How does the developer trigger a sketch? (new skill? part of explore-requirements? manual instruction?)
2. What is the review artifact? (HTML file to open in browser? Flutter screen to run?)
3. How does the developer communicate feedback? (annotate the sketch file? verbal instruction?)
4. When does iteration end? What signals "approved"? (metadata flag in sketch file? commit to repo?)

### Q5: Integration with Existing Workflows
Should `simple-implementation` and `complex-implementation` skills require a sketch approval gate?
- If YES: which conditions trigger the gate? (only when Presentation Layer changes are involved?)
- If NO: is there a separate skill for triggering sketches?
- Consider: overhead for trivial UI changes vs. safety for complex layouts

### Q6: Where to Anchor the Rules
Where should the final defined rules live so AI agents automatically respect them?
- `doc/` subfolder (e.g., `doc/ui_iteration/`) — gets read by implementation agents
- New top-level folder (e.g., `ui_workflow/`)
- Additions to CLAUDE.md
- New skill (`create-ui-sketch`)
- Hybrid: rules in `doc/`, skill for execution

## Scope

### In Scope
- Evaluating sketch format options and recommending one (or a combination)
- Defining AI behavior rules for sketch generation
- Defining storage location and organization structure for sketches
- Defining the developer-AI iteration workflow (steps, triggers, completion criteria)
- Assessing integration with `simple-implementation` and `complex-implementation` skills
- Identifying where rules should be anchored in the project
- Producing concrete output: either draft documentation, skill outlines, or a structured recommendation the developer can approve

### Out of Scope
- Actually implementing the sketch workflow (that is a follow-up impl task)
- Creating the HTML/CSS or Flutter sandbox (follow-up)
- Retroactively sketching existing requirements (follow-up)

## Acceptance Criteria

- [ ] AC-01: Sketch format chosen and justified
- [ ] AC-02: AI rules for sketching enumerated and located
- [ ] AC-03: Storage location decided and justified
- [ ] AC-04: Organization structure defined (naming, versioning)
- [ ] AC-05: Iteration workflow steps documented (trigger → generate → review → iterate → approve)
- [ ] AC-06: Integration decision made for implementation skills (gate or separate skill)
- [ ] AC-07: Rules anchor location decided (doc/, CLAUDE.md, new skill, hybrid)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-026 (Persona-Design Bridge) | in progress | Design system rules being established; sketches must align |

## Blocking Note

This task blocks all outstanding work that involves the Presentation Layer. If it is unclear whether an outstanding task touches the Presentation Layer, assume it does.

## Notes

- The developer emphasized: sketches are "static pictures" — the goal is NOT a runnable prototype
- Multiple screens per flow are required (e.g., a 3-step wizard = 3 sketch panels)
- The developer is open to Flutter sandbox if it's fast enough to work with
- Key constraint: the first iteration is always a throwaway — speed matters more than perfection in early rounds
- The exploration should produce a recommendation the developer can directly approve, not just open-ended analysis
