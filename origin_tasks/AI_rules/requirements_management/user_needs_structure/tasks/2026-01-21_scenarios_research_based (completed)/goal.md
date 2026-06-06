---
task_id: TASK-PROC-010-05
type: explore
parent_requirement: REQ-PROC-010
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-01-21
completed: 2026-01-24
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-04, SEC-09, SEC-14]
scope_description: "Change scenario writing rules to be user research based (status quo, not solution-based)"
requirements_version:
  commit: 09027a3
  file: ../requirements.md
---

# Goal: Update Scenario Writing Rules to Research-Based Approach

## Objective

Change the rules for how scenarios are written to be user research based. Scenarios should describe the status quo (current state without the app) rather than solution scenarios that include the app.

## Requirements Summary

From REQ-PROC-010 (User Needs Structure), sections:
- SEC-04: Scenario Definition
- SEC-09: Writing Guidelines
- SEC-14: Technology Neutrality Principle

Rule: As long as the app doesn't exist and hasn't been field-tested, scenarios always describe the status quo (current state) without the app. We use technologies that users currently use (pen, paper, Excel, email).

Purpose: We want to validate the problem and pain, not wrap our hypothetical solution in a story.

Exception: Only when explicitly requesting a "Future State Scenario" or "Solution Scenario" (e.g., for design exploration) may the app appear.

For complete requirements at task creation time:
```
git show 09027a3:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Update README file to reflect research-based scenario rules
- Update merge script to reflect new scenario approach
- Use existing dr_sarah scenarios as examples
- Document the status quo rule and its exception

### Out of Scope
- Do not modify existing scenarios (they remain as-is for now)

## Acceptance Criteria

- [ ] README.md updated with research-based scenario rules
- [ ] Merge script updated to reflect status quo approach
- [ ] Documentation clearly explains when app may/may not appear in scenarios
- [ ] Examples from dr_sarah scenarios incorporated

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-010 | implemented | Parent requirement defines user needs structure |

## Notes

The rules for how scenarios are written must change. They must be user research based. Change the README file (you can use one of the scenarios of dr_sarah as examples) to reflect that and also the script that merges the user needs file. More notes on that:

    Regel für Szenarien: Solange die App nicht existiert und im Feld getestet wurde, beschreiben Szenarien immer den Status Quo (Ist-Zustand) ohne die zu entwickelnde App. Wir nutzen Technologien, die die Nutzer jetzt verwenden (Stift, Papier, Excel, E-Mail).

        Zweck: Wir wollen das Problem und den Schmerz validieren, nicht unsere hypothetische Lösung in eine Geschichte verpacken.

        Ausnahme: Nur wenn explizit ein "Future State Scenario" oder "Solution Scenario" angefordert wird (z.B. für Design-Exploration), darf die App vorkommen.


Out of scope:
Do not modify the existing scenarios.
