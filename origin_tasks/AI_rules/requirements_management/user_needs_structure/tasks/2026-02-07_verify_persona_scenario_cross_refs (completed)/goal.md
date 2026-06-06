---
task_id: TASK-PROC-010-14
type: verify
parent_requirement: REQ-PROC-010
urgency: 4
urgency_reason: U4-CONSISTENCY
impact: 4
impact_reason: I4-QUALITY
status: completed
effort: M
created: 2026-02-07
completed: 2026-02-07
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-07, SEC-08]
scope_description: "Verify bidirectional links between personas and scenarios, ensure skills have instructions to update persona.md when creating scenarios"
requirements_version:
  commit: a210650
  file: ../requirements.md
---

# Goal: Verify Persona-Scenario Cross-References

## Objective

Zwei-Wege-Verlinkung zwischen Personas und Szenarien prüfen und Skills entsprechend aktualisieren, um zukünftige Inkonsistenzen zu vermeiden.

## Requirements Summary

REQ-PROC-010 defines the user needs structure including cross-referencing system (SEC-07) and skill modifications (SEC-08). This task ensures the cross-referencing system works bidirectionally and that skills enforce it.

For complete requirements at task creation time:
```
git show a210650:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

**Prüfung 1: Persona → Scenario Links**
- Alle Personas durchgehen (`requirements_user_needs/personas/*/persona.md`)
- Für jede Persona: Welche Szenarien existieren darunter?
- Sind alle Szenarien in `persona.md` verlinkt?
- Falls fehlend: Links hinzufügen

**Prüfung 2: Skill Instructions**
- `create-scenario` Skill prüfen
- Weitere relevante Skills identifizieren (z.B. `modify-user-needs`)
- Prüfen ob Anweisung existiert: "Bei Erstellung eines neuen Szenarios auch die zugehörige persona.md aktualisieren"
- Falls fehlend: Anweisung hinzufügen

### Out of Scope
- Scenario → User Flow Links (separate task)
- Content quality review
- Technical implementation

## Acceptance Criteria

- [ ] Alle Personas durchgegangen und Scenario-Links überprüft
- [ ] Fehlende Links in persona.md ergänzt
- [ ] `create-scenario` Skill auf Persona-Update-Anweisung geprüft
- [ ] Falls fehlend: Anweisung in Skill ergänzt
- [ ] Weitere relevante Skills identifiziert und aktualisiert
- [ ] Dokumentation der Änderungen in protocol.md
- [ ] Git commit mit allen Änderungen

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-010 | implemented | User needs structure exists |

## Notes

Diese Aufgabe verbessert die Konsistenz der User Needs Dokumentation und stellt sicher, dass zukünftige Szenarien automatisch korrekt verlinkt werden. Dies verhindert, dass Personas "verwaist" werden und man sich wundert, welche Szenarien zu einer Persona gehören.

**Kontext**: Der User hat festgestellt, dass die Personas vermutlich nicht auf ihre neuen Szenarien verlinken. Dies führt zu Verwirrung beim Lesen der Dokumentation.
