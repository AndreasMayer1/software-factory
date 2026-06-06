---
task_id: TASK-PROC-027-03
type: explore
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-USER_VALUE
status: completed
effort: S
created: 2026-02-07
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Check whether client-side plan-handover scenarios exist, mark gold standard if found, create variants or a new scenario to close coverage gap"
---

# Goal: Client Perspective Plan Handover Scenarios

## Objective

Prüfen ob Szenarien zur Planübergabe aus Klientensicht bereits existieren. Falls ja: Als Goldstandard markieren und weitere Varianten erstellen. Falls nein: Neues Szenario für passende Persona (Max oder Jana) schreiben.

## Context

Aktuell existieren Szenarien zur Planübergabe aus Therapeutensicht (Dr. Turan). Die Klientenperspektive bei der Übergabe des Behandlungsplans fehlt jedoch. Beide Perspektiven sind wichtig für ein vollständiges Bild der User Journey und der Bedürfnisse beider Seiten.

## Scope

### In Scope
- Durchsuchen aller existierenden Szenarien nach Planübergabe (Klientensicht)
- Falls gefunden: Nutzer fragen, ob sie als `gold_standard: true` markiert werden sollen.
- Falls gefunden: Mindestens 2 weitere Varianten identifizieren/erstellen (batch creation)
- Falls nicht gefunden: Neues Szenario für Max oder Jana erstellen

### Out of Scope
- Therapeuten-Szenarien (bereits vorhanden)
- Technische Implementierung

## Acceptance Criteria

- [ ] Alle existierenden Szenarien auf Planübergabe (Klientensicht) durchsucht
- [ ] Falls vorhanden: Gold standard Status gesetzt
- [ ] Falls vorhanden: Varianten erstellt
- [ ] Falls nicht gefunden: Neues Szenario erstellt
- [ ] Beide Perspektiven (Therapeut + Klient) sind nun abgedeckt

## Dependencies

Keine

## Notes

Die Planübergabe ist ein kritischer Moment in der therapeutischen Beziehung - sowohl aus Sicht des Therapeuten als auch des Klienten. Beide Perspektiven müssen dokumentiert sein, um die App-Anforderungen vollständig zu verstehen.
