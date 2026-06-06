---
task_id: TASK-PROC-017-01
type: impl
parent_requirement: REQ-PROC-017
urgency: 2
urgency_reason: U2-PROCESS
impact: 3
impact_reason: I3-QUALITY
status: completed
effort: XS
created: 2026-02-07
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Mark all Dr. med. Turan scenarios as approved in YAML frontmatter and add review history entries"
---

# Goal: Approve Dr. Turan Scenarios

## Objective

Alle Szenarien von Dr. Turan (Therapeut) als "approved" markieren, da sie qualitativ hochwertig und abnahmebereit sind.

## Context

Die Szenarien von Dr. Turan sind bereits sehr gut ausgearbeitet und können als abgenommen gelten. Im Gegensatz zu Jana Szenarien, die noch Kontext-Erweiterungen zum Stimmungsprotokoll benötigen (siehe Task USERNEED-JANA-001).

## Scope

### In Scope
- Alle Dr. Turan Szenarien identifizieren
- YAML frontmatter auf `review_status` Feld prüfen
- Setzen auf `review_status: approved`
- Review-History Eintrag hinzufügen mit Datum 2026-02-07

### Out of Scope
- Jana Szenarien (noch NICHT approven - Kontext-Erweiterung steht aus)
- Andere Personas

## Acceptance Criteria

- [ ] Alle Dr. Turan Szenarien identifiziert
- [ ] `review_status: approved` in YAML frontmatter gesetzt
- [ ] `review_history` Eintrag hinzugefügt mit Datum 2026-02-07
- [ ] Jana Szenarien NICHT verändert (Kontrolle)
- [ ] Git commit mit allen Änderungen

## Dependencies

Keine

## Notes

Diese Markierung signalisiert dass die Szenarien review-approved sind und als Basis für weitere Arbeit (z.B. User Flows, Epics) dienen können.

**Wichtig**: Nur Dr. Turan Szenarien approven. Jana Szenarien erst nach USERNEED-JANA-001 approven.
