---
task_id: TASK-PROC-011-09
type: impl
parent_requirement: REQ-PROC-011
urgency: 3
urgency_reason: U3-QUAL
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-01-31
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Rewrite Dr. Sarah persona and create two new therapist personas (Prof. Dr. Weber, Dr. med. Turan) to cover the full therapist spectrum"
---

The existing persona dr_sarah is not good enough. I want to rewrite it and add 2 additional therapist personas. 
Please add the personas based on the following descriptions (of course in english and you can add information based on your own knowledge of the groups if you can):


---

## 1. Persona: Dr. Sarah (Die Strukturierte / VT-Standard)
*Dies ist ein Update der bestehenden Persona. Bitte überschreibe oder erweitere sie massiv.*

*   **Rolle:** Psychologische Psychotherapeutin (Verhaltenstherapie).
*   **Hintergrund:** Eigene Kassenpraxis, ca. 20-25 Patienten/Woche.
*   **Implizite Cluster (Wen sie mit abdeckt):**
    *   *Die Edukativen:* Alle, die mit Hausaufgaben, Psychoedukation und Leitfäden arbeiten.
    *   *Die Trainer:* ADHS-Spezialisten (Strukturtraining), DBT-Therapeuten (Skill-Ketten), Sucht-Therapeuten (Rückfall-Protokolle).
    *   *Die Anfänger:* Therapeuten in Ausbildung (PiA), die Sicherheit durch Standard-Protokolle suchen.
*   **Mentales Modell:** "Therapie ist Hilfe zur Selbsthilfe. Wir brauchen Daten, um Muster zu erkennen und Verhalten zu ändern."
*   **Current Workflow (Ist-Zustand):**
    *   Nutzt Word-Vorlagen ("Wochenprotokoll", "Angst-Tagebuch") am Praxis-PC.
    *   Druckt diese vor der Stunde aus oder gibt Stapel von Kopien mit.
    *   Patienten bringen Zettel (oft zerknittert, kaffeefleckig) zur Stunde mit.
    *   In der Stunde: Sie legt die Zettel auf den Tisch und versucht, Handschriften zu entziffern und manuell Zusammenhänge zu finden ("War die Panik vor oder nach dem Streit?").
    *   Dokumentation: Heftet die Zettel in die Papierakte oder scannt sie mühsam ein.
*   **Pain Points:**
    *   **Parking Lot Syndrome:** Patienten füllen Bögen kurz vor der Stunde im Auto aus (Gedächtnisverzerrung).
    *   **Muster-Blindheit:** Sie kann 14 einzelne Tages-Zettel nicht "übereinanderlegen", um Langzeittrends zu sehen.
    *   **Zeitverlust:** 10-15 Min. der Sitzung gehen für Admin/Sichten drauf.
    *   **Compliance:** Patienten vergessen die Zettel zu Hause -> Keine Datengrundlage für die Stunde.

## 2. Persona: Prof. Dr. Weber (Der Narrative & Vorsichtige / TP-Analytiker)
*   **Rolle:** Tiefenpsychologe / Psychoanalytiker (Privatpraxis oder älterer Kassensitz).
*   **Hintergrund:** Fokus auf Beziehung, Unbewusstes und qualitativem Erleben. Tech-Skeptiker.
*   **Implizite Cluster (Wen er mit abdeckt):**
    *   *Die Tech-Skeptiker:* Alle, die Technologie als Störung der Beziehung empfinden.
    *   *Die Narrativen:* Systemiker, Gestalttherapeuten (Fokus auf Text/Audio/Bild statt Zahlen).
    *   *Die Somatiker (Low Prio):* Körpertherapeuten, die "Body Maps" (Einzeichnen von Gefühlen im Körper) nutzen würden.
    *   *Die Datenschützer:* Nutzer mit extrem hohen Anforderungen an lokale Datenspeicherung.
*   **Mentales Modell:** "Der Computer hat im Behandlungsraum nichts verloren. Es geht um das Unausgesprochene, Träume und Assoziationen, nicht um Checkboxen."
*   **Current Workflow (Ist-Zustand):**
    *   Arbeitet ausschließlich mit Füller und Notizbuch.
    *   Kein Computer im Sprechzimmer.
    *   Bittet Patienten, "Tagebuch zu führen" (freies Heft) oder Träume zu notieren.
    *   Patienten lesen in der Stunde aus ihren Heften vor.
*   **Pain Points:**
    *   **Medienbruch:** Junge Patienten (Gen Z) nutzen ihr Smartphone für Notizen. Weber kommt an diese "Black Box" nicht heran, fühlt sich ausgeschlossen.
    *   **Vergessen:** Patienten erinnern sich emotional nicht mehr an den Traum von vor 5 Tagen ("Der Vibe ist weg").
    *   **Angst vor der Cloud:** Er würde gerne digitale Hilfsmittel nutzen, traut aber keinem Anbieter ("Alles landet in den USA").
    *   **Unzugänglichkeit:** Er kann Patienten in Krisen zwischen den Stunden nichts "mitgeben" (kein Übergangsobjekt).

## 3. Persona: Dr. med. Turan (Der Monitor / Psychiater & Klinik)
*   **Rolle:** Facharzt für Psychiatrie in einem Medizinischen Versorgungszentrum (MVZ) oder Klinik-Ambulanz.
*   **Hintergrund:** Hoher Patientendurchlauf (40+/Woche), kurze Taktung (10-20 Min). Fokus auf Medikation und Krisenintervention.
*   **Implizite Cluster (Wen er mit abdeckt):**
    *   *Die Mediziner:* Stationsärzte, Konsil-Dienste (schnelle Übersicht nötig).
    *   *Die Risiko-Manager:* Forensik, Krisendienste (Suizidalität/Aggression im Blick behalten).
    *   *Die Datensammler:* Forscher, Burnout-Coaches (Schnittstelle zu Wearables/objektiven Daten).
    *   *Die Effizienz-Optimierer:* Alle, die keine Zeit für Prosa haben.
*   **Mentales Modell:** "Ich brauche Fakten für medizinische Entscheidungen. Wirkt das Medikament? Schläft der Patient? Ist er suizidal? Ich habe 3 Minuten für die Entscheidung."
*   **Current Workflow (Ist-Zustand):**
    *   Nutzt veraltete Klinik-Software (KIS) am Desktop.
    *   Fragt im Gespräch standardisiert ab: "Wie ist der Schlaf? Stimmung 1-10? Antrieb?"
    *   Patienten antworten vage ("Weiß nicht, ging so").
    *   Entscheidet Medikation oft nach "Bauchgefühl" mangels harter Daten.
*   **Pain Points:**
    *   **Blindflug:** Er sieht nicht, was zwischen den Quartals-Terminen passiert ist (Absetzen der Medikation, manische Phasen).
    *   **Ineffizienz:** Muss in jedem Termin mühsam Basisdaten erfragen, statt Trends zu sehen.
    *   **Fehlende Objektivität:** "Gefühlte" Verbesserung vs. "Gemessene" Verbesserung (z.B. Schlafdaten).
    *   **Sicherheitsrisiko:** Erfährt von Suizidgedanken oft erst, wenn es zu spät ist.
