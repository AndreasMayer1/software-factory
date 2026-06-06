---
task_id: TASK-PROC-011-08
type: impl
parent_requirement: REQ-PROC-011
urgency: 3
urgency_reason: U3-QUAL
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-01-31
after: [TASK-PROC-011-06]
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Update all 4 self-user personas to sharpen self-management/intrinsic-motivation focus and distinguish them from client personas"
---

# Task: Update Self-User Personas

This task depends on requirements_tasks\process\AI_rules\requirements_management\user_needs_content\tasks\2026-01-31_write_client_personas\goal.md.

## Completion Summary

✅ **All 4 self-user personas successfully updated** (2026-01-31)

**Modified personas:**
- PERSONA-008 (David) - version 2.0 → 2.1
- PERSONA-005 (Lisa) - version 2.0 → 2.1
- PERSONA-007 (Hanna) - version 2.0 → 2.1
- PERSONA-006 (Michael) - version 2.0 → 2.1

**Key changes:**
- Sharpened self-management / intrinsic motivation focus
- Emphasized "no therapist" context (alone, app is only anchor)
- Clarified distinct pain points vs. client personas
- All marked with evidence markers and task references

**Files modified:**
- requirements_user_needs/personas/david_structure_seeker/persona.md
- requirements_user_needs/personas/lisa_waitlist_bridger/persona.md
- requirements_user_needs/personas/hanna_sleepless/persona.md
- requirements_user_needs/personas/michael_high_performer/persona.md

---

## Original Goal

Please modify the self user personas according to the following:



Da wir die Klienten-Personas nun so scharf auf den Kontext **"In Therapie / Compliance"** zugeschnitten haben, müssen die Selbstnutzer den Kontext **"Selbstmanagement / intrinsische Motivation"** (oder deren Mangel) abdecken.

Das Hauptunterscheidungsmerkmal ist hier nicht die Diagnose, sondern der **"Job to be done"**:
*   **Klient:** "Erfülle den Plan meines Therapeuten." (Externer Antrieb/Verpflichtung).
*   **Selbstnutzer:** "Hilf mir, mich selbst zu verstehen/zu regulieren, weil gerade kein Experte da ist." (Interner Antrieb/Not).

Ich schlage vor, wir behalten/überarbeiten **David**, **Hanna**, **Lisa** und **Michael** als Selbstnutzer. Sie decken die Lücken ab, die die Klienten offen lassen.

Hier ist der Vorschlag für die Anpassung (für den Task):

***

# Anweisung zur Überarbeitung der Selbstnutzer-Personas

Bitte überarbeite die folgenden 4 Selbstnutzer-Personas.
**Fokus:** Diese Nutzer haben **keinen** Therapeuten (oder warten darauf). Sie sind auf sich allein gestellt. Die App ist ihr einziger Anhaltspunkt. Beschreibe ihren Ist-Zustand und ihre spezifischen Hürden beim *eigenständigen* Bewältigen ihrer Probleme.

## 1. Persona: David (Der Struktur-Sucher / ADHD Self-Manager)
*   **Abgrenzung zu Sophie (Klientin):** Sophie hat Dr. Sarah, die ihr den Zettel gibt. David muss sich sein System *selbst* bauen – und scheitert daran ständig.
*   **Rolle:** Selbstnutzer (diagnostiziert oder Verdacht auf ADHS).
*   **Ist-Zustand & Pain Points:**
    *   David hat schon 20 Apps installiert und nach 3 Tagen gelöscht ("Shiny Object Syndrome").
    *   Er sucht den "Heiligen Gral" der Produktivität/Ordnung.
    *   Sein Problem ist nicht das *Anfangen* (wie bei Max), sondern das *Dranbleiben*. Sobald der Neuheitswert weg ist, stirbt die Nutzung.
    *   Er braucht eine App, die *sofort* belohnt und extrem geringe Reibung hat ("Quick Capture"), sonst vergisst er den Gedanken, bevor die App offen ist.

## 2. Persona: Lisa (Die Wartelisten-Überbrückerin)
*   **Rolle:** Selbstnutzerin (Leichte Depression / Angst, wartet auf Therapieplatz).
*   **Kontext:** "The Gap" – Diagnostiziert, aber unversorgt (6 Monate Wartezeit).
*   **Ist-Zustand & Pain Points:**
    *   Sie fühlt sich allein gelassen ("Bin ich krank genug?").
    *   Sie will die Wartezeit nicht "verschwenden", sondern Daten sammeln, um beim Erstgespräch ernst genommen zu werden ("Beweismaterial").
    *   Sie führt unstrukturierte Notizen im Handy oder Tagebuch, weiß aber nicht, *was* eigentlich relevant ist (Angst vor dem "falschen" Protokollieren).
    *   Sie braucht Psychoedukation (Leitplanken), weil kein Therapeut da ist, der ihr das Modell erklärt.

## 3. Persona: Hanna (Die Schlaflose / Night User)
*   **Rolle:** Selbstnutzerin (Insomnie / Grübeln).
*   **Kontext:** Nutzung ausschließlich nachts (2:00 - 4:00 Uhr) und im Bett.
*   **Ist-Zustand & Pain Points:**
    *   Ihr Hauptfeind ist das "Gedankenkarussell", das sie wach hält. Sie muss Gedanken "auslagern" (Brain Dump), um schlafen zu können.
    *   Helles Licht (Papier & Lampe oder weiße App) weckt sie oder den Partner auf -> Absolute No-Go-Hürde.
    *   Sie ist morgens oft frustriert über die nächtlichen Einträge oder kann sie nicht mehr lesen (Gekritzel im Dunkeln).
    *   *Implizites Cluster:* Senioren (oft Schlafstörungen), Partner-Rücksichtnahme.

## 4. Persona: Michael (Der High-Performer / Burnout-Prävention)
*   **Rolle:** Selbstnutzer (Stress / Burnout-Vorstufe).
*   **Kontext:** Funktional im Job, leugnet "Krankheit".
*   **Ist-Zustand & Pain Points:**
    *   Würde nie zu einem Therapeuten gehen ("Ich bin ja nicht verrückt, nur gestresst").
    *   Nutzt Wearables (Garmin/Apple Watch) für Körperdaten, aber ihm fehlt der Link zur Psyche ("Warum habe ich schlecht geschlafen?").
    *   Hat extreme Angst vor Datenlecks (Karriere-Risiko). Wenn die App nach "Gesundheits-App" aussieht, nutzt er sie nicht im Büro.
    *   Betrachtet Gefühle als "Datenpunkte zur Optimierung".

***

Damit haben wir eine saubere Trennung:
*   **Klienten (Max, Jana, Elias, Sophie):** Fokus auf Therapie-Prozess, Hausaufgaben, Datenaustausch, Compliance.
*   **Selbstnutzer (David, Lisa, Hanna, Michael):** Fokus auf Selbstmotivation, Strukturfindung, Überbrückung, Prävention/Privacy.
