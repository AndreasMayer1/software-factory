---
task_id: TASK-PROC-012-001
type: explore
parent_requirement: REQ-PROC-012
urgency: 3
urgency_reason: U3-QUAL (inherited from parent - quality improvement for core user persona)
impact: 4
impact_reason: I4-CORE (inherited from parent - affects core persona understanding)
status: completed
effort: XS
created: 2026-01-21
after: []
awaiting: []
covers:
  sections:
    - "Persona Pain Points"
    - "Mental Models & Expectations"
    - "Jobs to Be Done"
    - "Scenarios: prepare_protocol_for_client"
    - "Scenarios: review_protocol_with_client"
  acceptance_criteria:
    - "Add pain points about inefficient redundancy and parking lot syndrome"
    - "Add mental model about trust vs control (no metadata tracking)"
    - "Enhance JTBD for efficient plan creation and secure handover"
    - "Update prepare_protocol scenario to show time waste"
    - "Update review_protocol scenario to show data quality issues"
scope_description: |
  Incrementally improve Dr. Sarah persona by adding:
  1. Pain points around repetitive manual work and uncertain data compliance
  2. Mental model emphasizing trust over surveillance (ethical constraint)
  3. Enhanced functional jobs around efficient template reuse
  4. Updated scenarios showing real pain points during protocol preparation and review
requirements_version: b1b783a
---

Modify dr sarah like described below. Note that you must not just copy paste what is written below, but understand the contained information and write it to the files according to the requirements for the files. Maybe you have to add more information, maybe you have to remove or modify. If you have to remove or modify, ask the user how to do it.

# Persona

#### 1. Sektion: Current Status Quo (Pain Points ergänzen)
**Anweisung:** Ergänze im Bereich "Pain Points with Current Paper-Based Approach" den Aspekt der Repetitivität und Ineffizienz bei der Erstellung.

*   **Hinzufügen:**
    *   🔴 **Ineffiziente Redundanz:** Dr. Sarah muss oft identische Instruktionen oder Standardfragen für verschiedene Klienten immer wieder neu von Hand aufschreiben oder kopieren. Das fühlt sich nach unnötiger Fleißarbeit an, die Zeit für die eigentliche Therapievorbereitung raubt.
    *   🔴 **Unsicherer Transfer:** Sie sorgt sich bei digitalen Alternativen (E-Mail) um die DSGVO-Konformität. Papierübergabe ist sicher, aber wenn der Klient den Zettel verliert, ist der "Kanal" unterbrochen.

#### 2. Sektion: Mental Models & Expectations
**Anweisung:** Schärfe ihre Haltung zum Thema Datenüberwachung und Vertrauen.

*   **Hinzufügen/Anpassen:**
    *   **Haltung zu Daten:** Dr. Sarah lehnt "Überwachung" ab. Sie möchte keine Metadaten sehen, von denen der Klient nichts weiß (z.B. "Wie lange war die App offen?"). Sie vertraut auf den **bewussten Selbstbericht** des Klienten.
    *   **Erwartung an Tools:** Ein Werkzeug darf niemals das Vertrauensverhältnis gefährden, indem es den Klienten ausspioniert. Transparenz ist therapeutisch notwendig.

#### 3. Sektion: Jobs to Be Done (Functional Jobs)
**Anweisung:** Ergänze das Bedürfnis nach effizienter Plan-Erstellung und sicherer Übergabe.

*   **Anpassen:**
    *   **Therapiepläne bereitstellen:** Statt "Prepare Protocols" -> "Therapiepläne effizient erstellen und sicher übergeben".
    *   **Detail:** Sie möchte bewährte Vorlagen (z.B. Angstprotokoll) wiederverwenden und individuell anpassen, ohne jedes Mal bei Null anzufangen.
    *   **Detail:** Sie muss sicherstellen, dass sensible Pläne ausschließlich den betroffenen Klienten erreichen (Verwechslungssicherheit).



Ich ergänze die Pain Points um die Ineffizienz (Schreibarbeit) und die Unsicherheit bzgl. der Datenqualität, füge aber gleichzeitig den ethischen Constraint hinzu.

**Änderungen:**

*   **Unter `Current Status Quo (Before Digital Solution) / Pain Points` hinzufügen:**
    *   🔴 **Ineffiziente Redundanz:** Dr. Sarah muss oft identische Instruktionen (z.B. "Skala 0-10", "Bitte Uhrzeit notieren") für verschiedene Klienten immer wieder von Hand aufschreiben. Das ist ermüdende Fleißarbeit, die wertvolle Vorbereitungszeit kostet.
    *   🔴 **Ungewissheit über Compliance ("Parking Lot Syndrome"):** Sie erhält oft Protokolle, die sehr gleichförmig ausgefüllt wirken (gleiches Schriftbild, gleicher Stift). Sie vermutet, dass der Klient alles kurz vor der Sitzung ausgefüllt hat, was die Daten für die Therapie fast wertlos macht (Recall Bias).

*   **Unter `Mental Models & Expectations` hinzufügen:**
    *   **Vertrauen vor Kontrolle:** Obwohl sie die Datenvalidität verbessern will, lehnt sie digitale Überwachung ab. Sie möchte **nicht** sehen, wann genau der Klient die App geöffnet hat oder wie lange er brauchte (Metadaten-Tracking). Sie glaubt, dass technische Kontrolle das therapeutische Bündnis beschädigt. Die Lösung muss durch *Motivation* (Senkung der Hürde) erfolgen, nicht durch *Überwachung*.


# Scenarios

## prepare_protocol_for_client

**Änderungen:**

*   **Sektion `The Story / Act 2` (Interaction) komplett ersetzen:**
    *   *Inhalt:* Es ist 16:50 Uhr. Sarah ist müde. Sie zieht das Standard-Formular "Wochenprotokoll" aus dem Schrank. Sie seufzt, weil sie heute schon zum dritten Mal dasselbe schreibt.
    *   *Handlung:* Sie schreibt handschriftlich an den Rand: "Bitte Situation kurz beschreiben" und "Anspannung 0-10". Ihre Handschrift wird krakelig. Sie ärgert sich, dass sie das nicht einfach "copy-pasten" kann wie in ihren Arztbriefen am PC.
    *   *Gedanke:* "Ich verschwende hier Zeit mit Schönschreiben, die ich für die Fallkonzeption nutzen könnte."

## review_protocol_with_client

Änderungen:

    Sektion The Story / Act 1 (Inciting Incident) anpassen:

        Inhalt: Max legt den Zettel auf den Tisch. Er ist glatt, sauber, keine Eselsohren.

        Beobachtung: Sarah sieht, dass alle Eintragungen (Montag bis Sonntag) mit exakt demselben blauen Kugelschreiber und identischem Schwung geschrieben sind.

        Interner Konflikt: "Das sieht aus, als hätte er es eben im Wartezimmer in 5 Minuten geschrieben."

        Interaktion: Sie fragt vorsichtig: "Wie war es am Dienstag?" Max wirkt vage.

        Problem: Sie kann mit diesen Daten kaum arbeiten, weil sie vermutlich aus der Erinnerung rekonstruiert sind. Aber das ist ebenfalls ein guter Einstieg in das Gespräch: Warum wurde es nicht korrekt gemacht?


