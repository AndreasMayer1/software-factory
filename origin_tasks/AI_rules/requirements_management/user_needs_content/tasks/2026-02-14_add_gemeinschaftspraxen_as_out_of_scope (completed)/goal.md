---
task_id: TASK-PROC-027-12
type: impl
parent_requirement: REQ-PROC-027
urgency: 4
urgency_reason: U4-IMPL
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-02-14
effort: XS
created: 2026-02-14
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Document Gemeinschaftspraxen as out of scope via persona-level scope_exclusion on dr_med_turan"
requirements_version:
  commit: edb2b1e
  file: ../requirements.md
---

# Goal: Gemeinschaftspraxen als Out-of-Scope dokumentieren

## Objective

Dokumentieren, dass wir aktuell **keine Gemeinschaftspraxen** unterstützen können. Der Aufwand (regulatorische Anforderungen, geteilte Windows-Accounts, Multi-User-Datenzugriff) ist zu hoch für den aktuellen Scope. Es ist aber ein Feature, das irgendwann eingebaut werden könnte.

Die Dokumentation erfolgt als **persona-level scope_exclusion** bei `dr_med_turan`, da er der einzige Psychiater-Persona ist und aktuell explizit in einem MVZ/Klinik-Einzelsetting arbeitet (nicht in einer Gemeinschaftspraxis).

## Requirements Summary

Dr. med. Turan arbeitet laut Persona in einem MVZ oder Klinik-Ambulanz-Setting. Gemeinschaftspraxen haben spezielle Anforderungen:
- Gemeinsam genutzte Windows-Accounts (Sammelaccounts wie "Sprechzimmer 1")
- Mehrbenutzerzugriff auf Patientendaten
- Regulatorische Anforderungen nach KBV IT-Sicherheitsrichtlinie (§ 390 SGB V)
- DSGVO: individuelle Zuordenbarkeit von Zugriffen

Für complete requirements at task creation time:
```
git show edb2b1e:requirements_tasks/process/AI_rules/requirements_management/user_needs_content/requirements.md
```

Current requirements: ../requirements.md

**Hintergrundrecherche**: Die Analyse-Grundlage befindet sich in:
`requirements_tasks/process/AI_rules/requirements_management/user_needs_content/tasks/2026-02-14_add_gemeinschaftspraxen_as_out_of_scope/Windows Accounts In Arztpraxen Erkennen.json`

Diese Datei enthält eine Gemini-Recherche zu Windows-Account-Strukturen in Arztpraxen (KBV IT-Sicherheitsrichtlinie, DSGVO, Sammelaccounts vs. individuelle Accounts).

## Scope

### In Scope
- `scope_exclusions` Eintrag in `requirements_user_needs/personas/dr_med_turan/persona.md` hinzufügen
- Begründung referenziert die JSON-Datei als Grundlage

### Out of Scope
- Keine neuen Szenarien erstellen
- Kein separates Dokument erstellen
- Keine Änderungen an anderen Personas

## Acceptance Criteria

- [ ] `dr_med_turan/persona.md` enthält einen `scope_exclusions` Eintrag für Gemeinschaftspraxen
- [ ] Eintrag hat `reason: effort` (Aufwand zu hoch für aktuellen Scope)
- [ ] Eintrag hat `reconsider_in` gesetzt (ist ein zukünftiges Feature)
- [ ] `reason_detail` referenziert die JSON-Datei als Hintergrundrecherche
- [ ] Persona bleibt valides YAML

## Notes

Die JSON-Datei zeigt: In deutschen Arztpraxen gibt es häufig Sammelaccounts (z.B. "Sprechzimmer 1") auf Windows-Ebene. Die KBV IT-Sicherheitsrichtlinie fordert individuelle Zuordenbarkeit - was in der Praxis oft nur über das PVS (Praxisverwaltungssystem) gelöst wird, nicht auf Windows-Ebene. Eine App wie unsere müsste diese Komplexität berücksichtigen (Multi-User, Datenisolation, Compliance).
