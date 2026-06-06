---
task_id: TASK-PROC-020-01
type: impl
parent_requirement: REQ-PROC-020
urgency: 4
urgency_reason: U4-CLARITY
impact: 4
impact_reason: I4-USER_VALUE
status: completed
effort: M
created: 2026-02-07
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Extend Jana persona with missing therapeutic context about mood protocol structure, therapist expectations, and the accepted compromise"
---

# Goal: Jana Mood Protocol Context Enhancement

## Objective

Jana Persona um wichtigen therapeutischen Kontext zum Stimmungsprotokoll erweitern, damit die User Story vollständig nachvollziehbar und die Motivationen klar sind.

## Context & Problem

Beim Lesen von Janas Szenarien entsteht Verwirrung: Jana notiert am Ende des Tages nur eine einzelne Stimmungszahl, was die realen Schwankungen nicht abbildet. Der therapeutische Hintergrund fehlt.

**Der fehlende Kontext:**
- **Was die Therapeutin eigentlich will**: Mehrfache Datenpunkte pro Tag (Protokoll mit Uhrzeiten, Spalten/Zeilen) um Stimmungsschwankungen zu erfassen
- **Janas Hürde**: Sie fühlt sich von strukturierten Fragebögen mit vielen Zeilen/Spalten überfordert
- **Der Kompromiss**: Die Therapeutin erlaubt die Nutzung eines eigenen Notizbuchs ohne strikte Struktur als "Schritt-für-Schritt"-Ansatz, obwohl sie eigentlich mehr Daten möchte
- **Die offene Frage**: Wird das Protokoll unter diesen Umständen trotzdem gut ausgefüllt?

## Scope

### In Scope
- Jana Persona lesen und passende Stelle für Kontext identifizieren
- Therapeutischen Hintergrund zum Stimmungsprotokoll hinzufügen
- Kompromiss-Lösung dokumentieren
- Offene Frage formulieren
- Version increment + Changelog-Eintrag

### Out of Scope
- Andere Personas
- Technische Implementierung

## Acceptance Criteria

- [ ] Kontext zur Therapeutin-Anforderung (mehrfache Datenpunkte) ergänzt
- [ ] Janas Überforderung bei strukturierten Fragebögen erklärt
- [ ] Kompromiss (eigenes Notizbuch) dokumentiert
- [ ] Offene Frage zur Protokoll-Qualität formuliert
- [ ] Version increment in YAML frontmatter
- [ ] Changelog-Eintrag erstellt
- [ ] Review status ggf. auf `in_review` gesetzt

## Dependencies

Keine

## Notes

Diese Änderung ist wichtig, um zu verstehen:
1. Warum Jana so tracked wie sie tracked
2. Welche therapeutischen Anforderungen eigentlich bestehen
3. Wo der Kompromiss liegt
4. Welche offenen Fragen für die App-Entwicklung bestehen

Ohne diesen Kontext wirkt Janas Verhalten unmotiviert oder unverständlich.
