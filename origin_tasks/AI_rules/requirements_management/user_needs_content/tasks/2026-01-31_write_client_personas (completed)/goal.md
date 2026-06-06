---
task_id: TASK-PROC-011-06
type: impl
parent_requirement: REQ-PROC-011
urgency: 3
urgency_reason: U3-QUAL
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-01-31
after: [TASK-PROC-011-01]
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Rewrite Max client persona and create three additional client personas: Jana, Elias, Sophie"
tags: [user-needs, personas, client]
---

# Goal: Create 4 Client Personas (Max, Jana, Elias, Sophie)

The existing persona max_client is not good enough. I want to rewrite it and add 3 additional client personas. 
Please add the personas based on the following descriptions (of course in english and you can add information based on your own knowledge of the groups if you can):



Wir schärfen **Max** und führen **Jana**, **Elias** und **Sophie** ein. Damit decken wir das gesamte Spektrum ab.

Hier ist der Block für Claude Code:

***

# Anweisung zur Erstellung/Überarbeitung der Klienten-Personas

Bitte erstelle oder überarbeite die folgenden 4 Klienten-Personas.
**Wichtigste Regel:** Beschreibe ausschließlich den **Ist-Zustand (Status Quo)**. Beschreibe, wie diese Personen *heute* (ohne die App) ihre Therapie-Hausaufgaben bewältigen (oder daran scheitern). Beschreibe ihre Frustrationen mit Stift, Papier, Excel oder Notiz-Apps. Erwähne **nicht**, wie unsere App diese Probleme löst.

## 1. Persona: Max (Der Überforderte)
*   **Rolle:** Klient (in Verhaltenstherapie wegen Depression).
*   **Kern-Diagnose:** Schwere Depression (Major Depression), Antriebsstörung.
*   **Implizite Cluster (Wen repräsentiert er auch?):**
    *   Burnout-Patienten (Erschöpfung).
    *   Long-Covid / CFS (Fatigue, begrenztes Energiebudget).
    *   Menschen in Trauerphasen.
*   **Ist-Zustand & Pain Points:**
    *   Max möchte "ein guter Patient" sein, aber der Weg zum Schreibtisch, um das Papier-Protokoll zu holen, fühlt sich an wie ein Marathon.
    *   Er leidet unter dem "weißen Blatt Syndrom": Leere Felder überfordern ihn kognitiv.
    *   Er erinnert sich abends nicht mehr an den Morgen (Memory Fog).
    *   Oft füllt er das Protokoll erst kurz vor der Stunde im Wartezimmer aus ("Parking Lot Syndrome"), was zu Schamgefühlen führt.

## 2. Persona: Jana (Die Hochgespannte)
*   **Rolle:** Klientin (in DBT/Schematherapie).
*   **Kern-Diagnose:** Borderline-Persönlichkeitsstörung (BPS), Emotionsregulationsstörung.
*   **Implizite Cluster (Wen repräsentiert sie auch?):**
    *   **Akute Krise & Suizidalität:** Menschen, die sofortige Intervention brauchen.
    *   PTBS (Flashbacks, Dissoziation).
    *   Impulskontrollstörungen (z.B. Wutausbrüche).
*   **Ist-Zustand & Pain Points:**
    *   Ihre Stimmungen wechseln in Sekunden. Ein Papierprotokoll am Abend kann diese Volatilität nicht abbilden ("Der Durchschnittswert lügt").
    *   In Momenten der Hochspannung (Krise) ist sie kognitiv eingeschränkt ("Tunnelblick"). Sie findet ihre "Skills-Liste" (Zettel) in der Tasche nicht oder kann die kleine Schrift nicht lesen.
    *   Sie braucht haptisches/schnelles Feedback, Feinmotorik ist in der Krise gestört (Zittern).

## 3. Persona: Elias (Der Skeptische Wächter)
*   **Rolle:** Klient (in Therapie wegen Sozialer Phobie / Angststörung).
*   **Kern-Diagnose:** Soziale Phobie, Generalisierte Angststörung.
*   **Implizite Cluster (Wen repräsentiert er auch?):**
    *   **Privacy-First Nutzer:** Angst vor Datenlecks an Arbeitgeber/Krankenkasse.
    *   "Heimliche Nutzer": Menschen in toxischen Beziehungen oder mit kontrollierenden Eltern.
    *   Pendler: Nutzen Therapie-Tools im öffentlichen Raum (ÖPNV).
*   **Ist-Zustand & Pain Points:**
    *   Elias soll Expositionsübungen in der Öffentlichkeit machen (z.B. Leute ansprechen). Er traut sich nicht, dabei ein auffälliges "Therapie-Heft" oder eine bunt leuchtende App herauszuholen.
    *   Er hat paranoide Angst, dass jemand auf sein Display schaut (Shoulder Surfing).
    *   Er vertraut Cloud-Diensten nicht und führt deshalb oft "Schatten-Buchführung" im Kopf, statt ehrlich zu protokollieren.

## 4. Persona: Sophie (Die Struktur-Suchende)
*   **Rolle:** Klientin (in Therapie wegen ADHS im Erwachsenenalter).
*   **Kern-Diagnose:** ADHS, Exekutive Dysfunktion.
*   **Implizite Cluster (Wen repräsentiert sie auch?):**
    *   Autismus-Spektrum (Bedürfnis nach Vorhersehbarkeit).
    *   Zwangsstörungen (Detailliertes Protokollieren von Ritualen).
    *   **Barrierefreiheit / Senioren:** Menschen, die klare Kontraste, große Schrift und eindeutige Nutzerführung brauchen (Cognitive Load Reduction).
*   **Ist-Zustand & Pain Points:**
    *   Sophie ist hochmotiviert, verliert aber ständig ihre Zettelwirtschaft.
    *   Sie vergisst das Protokollieren schlichtweg (Objektpermanenz), wenn es nicht "in your face" ist.
    *   Sie neigt dazu, sich in Details zu verlieren (Hyperfokus) und schreibt Romane statt Datenpunkte, was die Auswertung für den Therapeuten unmöglich macht.
    *   Sie braucht externe Struktur ("External Executive Function"), weil sie diese intern nicht generieren kann.