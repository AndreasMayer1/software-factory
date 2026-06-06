# Opus Plan: Add Protocol/Homework Lists to All 13 Personas

**Created**: 2026-02-15
**Agent**: Opus (planning phase)
**Task**: TASK-PROC-027-13
**Status**: Plan ready for execution

---

## Objective

Add clinically grounded protocol and homework sections to all 13 human personas, based on the Gemini clinical research. Each section must use German clinical terminology, include source references where significant, and respect the structural conventions of the existing persona files.

## Analysis Summary

### File Structure Finding

All 13 personas follow a consistent pattern. The last sections before the file ends are always:
- `## Anti-Traits` (all personas)
- `## Cluster Representation` (clients and self-users only)
- `## Related Scenarios` (all personas, always last)

**Insertion point**: The new section goes immediately BEFORE `## Related Scenarios`.

### Three Distinct Section Formats Required

| Persona Role | Section Heading | Subsection Structure |
|---|---|---|
| Therapist (3) | `## Protocols & Homework (Verordnete Protokolle)` | Flat list of protocol entries with clinical sources |
| Client (5) | `## Self-Tracking Protocols` | Two subsections: `### Therapie-Hausaufgabe (Shared)` and `### Eigenbedarf (Private)` |
| Self-User (5) | `## Self-Tracking Protocols` | Flat list of protocol entries (all self-initiated, no therapist distinction) |

### Clinical Review Notes (Corrections/Extensions to Gemini Research)

1. **Dr. Sarah -- Skill-Ketten-Protokoll**: Gemini lists this under Dr. Sarah (VT), but skill chains are primarily a DBT concept (Linehan/Bohus). Dr. Sarah would more likely use a **Selbstbeobachtungsbogen** or **Stimmungsprotokoll** as her general-purpose tool. However, VT therapists who work with skill deficits (as stated in Dr. Sarah's persona: "increasingly ADHD and skill deficits requiring structured interventions") could legitimately use skill chain tracking. **Decision**: Keep it, but add a clarifying note that it is used for her skill-deficit patients, adapted from DBT into VT context.

2. **Dr. med. Turan -- Krisenplan/Notfallplan**: This is explicitly NOT a tracking protocol -- it's a static safety document. The Gemini research correctly flags this. **Decision**: Include it but mark it with a `(Statisches Dokument, kein Tracking)` tag to distinguish it from tracking protocols.

3. **Elias -- Sicherheits-Checkliste**: The Gemini research notes this may indicate obsessive-compulsive traits "die er vielleicht noch nicht thematisiert hat." This is clinically significant: the app capturing this data could unintentionally reveal a comorbidity the client hasn't disclosed. **Decision**: Include with a clinical note: `(Möglicher Hinweis auf zwanghafte Komorbidität -- nicht thematisiert in Therapie)`.

4. **Elias -- Datenschutz-Log**: This is a meta-need (monitoring the app itself), not a mental health protocol. **Decision**: Include it but mark it as `(Meta-Bedürfnis: App-Transparenz, kein klinisches Protokoll)`.

5. **Lena -- Briefe an den Verstorbenen**: This aligns with established Continuing Bonds theory (Klass, Silverman & Nickman, 1996) and is increasingly recognized in German grief therapy. **Decision**: Add source reference.

6. **Lisa -- Wartezeiten-Countdown**: This is organizational tracking, not clinical self-monitoring. **Decision**: Include but mark as `(Organisatorisches Tracking, kein klinisches Protokoll)`.

7. **Cross-reference: Therapist-Client protocol consistency**: The plan must ensure that what a therapist "prescribes" matches what the corresponding client "receives as homework." Specifically:
   - Dr. Sarah prescribes Wochenprotokoll --> Max receives Wochenprotokoll as homework
   - Frau Albrecht (not in our therapist personas, but referenced) prescribes DBT Diary Card --> Jana receives Diary Card as homework
   - Prof. Dr. Weber prescribes Traumtagebuch --> Lena receives Traumtagebuch as homework
   - Frau Kellner (not in our therapist personas) prescribes Medikations-Wirkungs-Protokoll --> Sophie receives it as homework
   - Frau Richter (not in our therapist personas) prescribes Angst-Hierarchie & Expositionsprotokoll --> Elias receives it as homework

8. **Nina -- Orthostase-Check**: Should reference POTS (Posturales orthostatisches Tachykardiesyndrom), which is a recognized Long-COVID comorbidity. **Decision**: Add clinical context.

9. **Hanna -- Grübel-Stuhl-Protokoll**: The name "Grübelstuhl" comes from the stimulus control technique by Bootzin but the German clinical term is more commonly "Gedankenstopp-Protokoll" or "Sorgenstuhl-Technik." **Decision**: Use Gemini's term "Grübel-Stuhl-Protokoll" since it maps well to Hanna's persona description of externalizing thoughts, but add source reference to Bootzin stimulus control.

10. **Additional protocol NOT in Gemini that should be considered**: For David (self-managed ADHD), a **Belohnungs-Log** (reward tracking) is a well-established ADHD self-management technique. The "Dopamin-Menu" covers this partially but is more of a static list. **Decision**: The Dopamin-Menu as described by Gemini is sufficient; it serves as both a static reference list and an active selection tool.

### Uncovered Persona Gaps (Out of Scope, Document Only)

The Gemini research identifies five additional clinical clusters not yet covered by any persona:
1. **Essstorungen** (Eating Disorders): Ess-Protokoll mit Kontext (Fairburn CBT-E), Spiegel-Expositionsprotokoll (Vocks & Legenbauer)
2. **Zwangsstorungen** (OCD): ERP-Protokoll -- Exposition mit Reaktionsverhinderung (Lakatos & Reinecker; Foa et al.)
3. **Sucht** (Addiction): Konsumtagebuch (DHS; Korkel), Craving-Protokoll / Urge Surfing (Marlatt & Gordon)
4. **Chronischer Schmerz** (Chronic Pain): Deutsches Schmerztagebuch (Deutsche Schmerzgesellschaft; KIBIS)
5. **Partnerschaft/Familie** (Systemic Therapy): Konflikt-Protokoll (Gottman; Bodenmann)

These will be documented as a gap note at the end of the execution protocol.

---

## Section Format Specifications

### Format A: Therapist Personas (`## Protocols & Homework (Verordnete Protokolle)`)

```markdown
## Protocols & Homework (Verordnete Protokolle)

Protokolle und Hausaufgaben, die [Persona Name] typischerweise an Klient:innen vergibt:

| # | Protokoll | Beschreibung | Klinischer Kontext |
|---|-----------|-------------|-------------------|
| 1 | **Name (Englischer Name)** | Kurzbeschreibung des Inhalts und Ziels | Fachliche Referenz oder Verfahrenskontext |
| 2 | ... | ... | ... |
```

**Rationale for table format**: Therapists think in terms of their toolkit. A table provides scannable, reference-card-style access. Each row is one tool they might deploy.

### Format B: Client Personas (`## Self-Tracking Protocols`)

```markdown
## Self-Tracking Protocols

### Therapie-Hausaufgabe (Shared with Therapist)

Von [Therapeutenname] verordnet:

- **Protokollname**: Kurzbeschreibung. *(Quelle: Referenz)*

### Eigenbedarf (Private -- nicht mit Therapeut:in geteilt)

Selbstinitiierte Protokolle, die [Persona Name] fur sich selbst fuhrt:

- **Protokollname**: Kurzbeschreibung. *(Kontextnotiz)*
```

**Rationale for list format**: Clients experience protocols as individual items, not a toolkit. The two-subsection split (shared/private) is the critical structural innovation from the Gemini research -- it maps directly to the app's data-sharing architecture.

### Format C: Self-User Personas (`## Self-Tracking Protocols`)

```markdown
## Self-Tracking Protocols

Selbstinitiierte Protokolle ohne therapeutische Anleitung:

- **Protokollname**: Kurzbeschreibung. *(Quelle/Kontext)*
```

**Rationale**: Self-users have no therapist distinction. All protocols are self-initiated. The simpler format reflects their autonomy and the absence of a shared/private boundary.

---

## Full Protocol Content for All 13 Personas

### GROUP 1: Therapists

#### 1. Dr. Sarah (PERSONA-001) -- `requirements_user_needs/personas/dr_sarah/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 157):

```markdown
## Protocols & Homework (Verordnete Protokolle)

Protokolle und Hausaufgaben, die Dr. Sarah typischerweise an Klient:innen vergibt:

| # | Protokoll | Beschreibung | Klinischer Kontext |
|---|-----------|-------------|-------------------|
| 1 | **Wochenprotokoll / Aktivitatenprotokoll (Activity Schedule)** | Erfassung von Tatigkeiten im Stundenraster mit Bewertung von Stimmung (M) und Bewaltigung/Leistung (B). Ziel: Aufbau positiver Aktivitaten bei Depression. | VT-Standard; Hautzinger (2003), *Kognitive VT bei Depressionen* |
| 2 | **Gedankenprotokoll (ABC-Modell / Thought Record)** | Spalten fur Situation, Gefuhl, Automatischer Gedanke, Rationaler Gegengedanke, Ergebnis. Ziel: Kognitive Umstrukturierung. | Beck (Kognitive Therapie); in DE verbreitet durch Wilken |
| 3 | **Angst-Tagebuch / Expositionsprotokoll** | Situation, Angststarke (0-10) vor/wahrend/nach der Situation, vermiedene vs. ausgefuhrte Handlung. | Margraf & Schneider (2018), *Lehrbuch der Verhaltenstherapie* |
| 4 | **Schlaftagebuch (Sleep Diary)** | Bettgehzeit, Einschlafdauer, Aufwachhaufigkeit, Aufstehzeit, Schlafqualitat. | KVT-I Standard; DGSM |
| 5 | **Verhaltensanalyse-Bogen (SORKC)** | Detaillierte Erfassung einer spezifischen Problemsituation: Stimulus, Organismus, Reaktion, Kontingenz, Konsequenz. | Kanfer (Selbstmanagement-Therapie) |
| 6 | **Skill-Ketten-Protokoll** | Fur Situationen mit hoher Anspannung: Wann wurde welche Fertigkeit eingesetzt? Verlauf der Anspannung. | Adaptiert aus DBT (Linehan/Bohus) fur VT-Kontext bei Skill-Defizit-Patienten (z.B. ADHS, Emotionsregulation) |

```

#### 2. Dr. med. Turan (PERSONA-012) -- `requirements_user_needs/personas/dr_med_turan/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 143):

```markdown
## Protocols & Homework (Verordnete Protokolle)

Protokolle und Hausaufgaben, die Dr. med. Turan typischerweise an Patient:innen vergibt:

| # | Protokoll | Beschreibung | Klinischer Kontext |
|---|-----------|-------------|-------------------|
| 1 | **Stimmungs- und Antriebskurve (Mood Chart)** | Einfache Grafik (z.B. -3 bis +3) fur Stimmung, Antrieb und Schlafzeit. Wichtig fur Bipolare Storungen und Rezidivprophylaxe. | DGBS Life-Charts; AMDP-System |
| 2 | **Medikamenten- & Nebenwirkungsprotokoll** | Einnahmezeitpunkt, Dosis, korperliche Symptome (Ubelkeit, Schwindel, Gewichtsveranderung, Libidoveranderung). | Psychiatrischer Medikationsstandard |
| 3 | **Schlaf-Wach-Rhythmus-Protokoll** | Fokus auf Regularitat und Schlafdauer. Besonders relevant bei Medikamenteneinstellung und -umstellung. | Schlafmedizinischer Standard |
| 4 | **Krisenplan / Notfallplan** | Statisches Sicherheitsdokument: Handlungsanweisungen fur den Krisenfall ("Was tun wenn Suizidalitat > 7?"). *(Statisches Dokument, kein Tracking)* | Psychiatrische Krisenintervention; S3-Leitlinie Suizidalitat |
| 5 | **Compliance-Checkliste** | Einfache Haken-Liste: "Morgens Tablette genommen? Ja/Nein." Minimaler Aufwand fur maximale Compliance-Transparenz. | Medikamenten-Adharenz-Monitoring |

```

#### 3. Prof. Dr. Weber (PERSONA-011) -- `requirements_user_needs/personas/prof_dr_weber/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 129):

```markdown
## Protocols & Homework (Verordnete Protokolle)

Protokolle und Aufgaben, die Prof. Dr. Weber seinen Patient:innen mitgibt -- bewusst offen und narrativ gehalten:

| # | Protokoll | Beschreibung | Klinischer Kontext |
|---|-----------|-------------|-------------------|
| 1 | **Traumtagebuch (Dream Journal)** | Freitext-Feld fur Trauminhalt, Assoziationen dazu, Tagesreste. Fokus auf emotionale Qualitat, nicht Faktentreue. | Freud (*Die Traumdeutung*); C.G. Jung; OPD-2 (Operationalisierte Psychodynamische Diagnostik) |
| 2 | **Resonanz-Protokoll** | "Was hat mich heute emotional bewegt?" Fokus auf Affekte und innere Bewegungen, nicht auf Verhalten oder Fakten. | Tiefenpsychologische Affektarbeit |
| 3 | **Beziehungs-Protokoll** | Beschreibung interpersoneller Konflikte oder bedeutsamer Begegnungen. Fokus: "Wie habe ich mich in Beziehung zum anderen gefuhlt?" | Luborsky (CCRT -- Zentrale Beziehungskonflikt-Themen) |
| 4 | **Freies Assoziieren (Morning Pages)** | Unstrukturierter Schreibfluss am Morgen, um Unbewusstes zuganglich zu machen. Keine Vorgaben zu Thema oder Struktur. | Psychoanalytische Grundregel; popularkulturell: Cameron (*The Artist's Way*) |
| 5 | **Symptom-Kontext-Tagebuch** | Wann tritt das Symptom auf und *woran habe ich gerade gedacht*? Suche nach psychodynamischen Auslosern und unbewussten Zusammenhangen. | Psychodynamische Symptomanalyse |

```

---

### GROUP 2: Clients

#### 4. Max (PERSONA-002) -- `requirements_user_needs/personas/max_client/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 115):

```markdown
## Self-Tracking Protocols

### Therapie-Hausaufgabe (Shared with Therapist)

Von Dr. Sarah verordnet:

- **Wochenprotokoll (Aktivitaten & Stimmung)**: Tagliches Erfassen von Aktivitaten mit Stimmungsbewertung (0-10) und Bewaltigungsgefuhl. Dr. Sarah nutzt dies, um Muster zwischen Aktivitatsniveau und Depression zu identifizieren. *(VT-Standard; Hautzinger, 2003)*

### Eigenbedarf (Private -- nicht mit Therapeutin geteilt)

Selbstinitiierte Protokolle, die Max fur sich selbst fuhrt:

- **"Brain Dump" Liste**: Unstrukturiertes Niederschreiben kreisender Gedanken, besonders nachts um 3 Uhr. Ziel: Externalisierung zur Entlastung, um schlafen zu konnen. Kein therapeutisches Protokoll, sondern Selbsthilfe-Mechanismus.
- **Energie-Tankstelle**: Liste von Dingen, die ihm gut tun (Ressourcen-Sammlung), um sich daran zu erinnern, wenn der Antrieb fehlt. Wirkt gegen die depressive Anhedonie ("Mir macht nichts mehr Spass").
- **Erfolgs-Tagebuch (klein)**: "3 Dinge, die ich heute geschafft habe." Wirkt gezielt gegen das depressive Gefuhl der Wertlosigkeit und Leistungsunfahigkeit. Niedrigschwellig: auch "aufgestanden" zahlt.

```

#### 5. Sophie (PERSONA-010) -- `requirements_user_needs/personas/sophie_structure_seeker/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 115):

```markdown
## Self-Tracking Protocols

### Therapie-Hausaufgabe (Shared with Therapist)

Von Frau Kellner verordnet:

- **Medikations-Wirkungs-Protokoll**: Wann Medikament genommen? Wann Wirkungseintritt? Wann Rebound (Nachlassen der Wirkung)? Dient der Feineinstellung der ADHS-Medikation und dem Erkennen des optimalen Einnahmezeitpunkts. *(ADHS-Medikationsmanagement)*

### Eigenbedarf (Private -- nicht mit Therapeutin geteilt)

Selbstinitiierte Protokolle, die Sophie fur sich selbst fuhrt:

- **Habit Tracker**: Bunte Liste zum Abhaken alltaglicher Aufgaben (Zahne putzen, Wasser trinken, Vitamine). Dient dem Dopamin-Kick durch sichtbare Erfolgserlebnisse -- kompensiert das ADHS-Belohnungsdefizit.
- **Impulskauf-Log**: "Was wollte ich kaufen und warum habe ich es nicht getan?" Dient der Finanzkontrolle bei ADHS-typischer Impulsivitat. Dokumentiert Impulskontrollerfolge.
- **Fokus-Zeit-Log**: Wie viele Stunden war sie produktiv? Oft verbunden mit Scham, wenn leer. Zeigt Muster zwischen Medikation, Tageszeit und Fokusfahigkeit.

```

#### 6. Jana (PERSONA-014) -- `requirements_user_needs/personas/jana_high_strung/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 128):

```markdown
## Self-Tracking Protocols

### Therapie-Hausaufgabe (Shared with Therapist)

Von Frau Albrecht verordnet:

- **DBT Diary Card**: Spannungskurve (0-10 uber den Tag), eingesetzte Skills, dysfunktionale Verhaltensweisen (Selbstverletzung, Substanzkonsum, dissoziative Episoden), Medikamenteneinnahme. Das zentrale Instrument der Dialektisch-Behavioralen Therapie. *(Linehan, 1993/2014, DBT Skills Training Manual; Bohus, DBT kompakt; Bohus & Wolf-Arehult, Interaktives Skillstraining)*
  - **Anmerkung**: Frau Albrecht wollte ursprunglich ein strukturiertes Mehrfacheintrage-Protokoll (zeitgestempelte Zeilen und Spalten). Jana empfand dies als "klinisch und erstickend." Kompromiss: informelles Notizbuch mit mindestens einem Eintrag pro Abend. Offene Frage: Reicht das vereinfachte Format fur die DBT-Verhaltenskettenanalyse?

### Eigenbedarf (Private -- NICHT mit Therapeutin geteilt)

Selbstinitiierte Protokolle, die Jana fur sich selbst fuhrt. Teilweise bewusst vor der Therapeutin verborgen:

- **Trigger-Logbuch**: Wer hat was gesagt, das sie wutend gemacht hat? Oft sehr detailliert und emotional aufgeladen. Dient der nachtragelichen Verarbeitung von Krisensituationen.
- **"Safe People" Liste**: Fotos oder Nachrichten von Freunden, die Stabilitat geben. Dient als Anti-Dissoziations-Hilfe und Realitatsanker in akuten Krisen. *(Kein Tracking-Protokoll, sondern Sicherheitsressource)*
- **Schwarzes Buch**: Unzensierte Wut und Gedanken, die Jana der Therapeutin *nicht* zeigen will. Schutz der therapeutischen Beziehung -- sie braucht einen Raum, der frei von Bewertung und Konsequenzen ist. *(Hochsensible Privatsphare: Dieses Protokoll darf unter keinen Umstanden geteilt werden)*

```

#### 7. Elias (PERSONA-009) -- `requirements_user_needs/personas/elias_skeptical_guardian/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 136):

```markdown
## Self-Tracking Protocols

### Therapie-Hausaufgabe (Shared with Therapist)

Von Frau Richter verordnet:

- **Angst-Hierarchie & Expositionsprotokoll**: Situation, erwartete Angst (0-10), tatsachliche Angst (0-10), Dauer der Exposition, Verlauf der Angst. Dient dem systematischen Abbau von Vermeidungsverhalten. *(Stangier et al., Kognitive Therapie der Sozialen Phobie)*

### Eigenbedarf (Private -- nicht mit Therapeutin geteilt)

Selbstinitiierte Protokolle, die Elias fur sich selbst fuhrt:

- **Sicherheits-Checkliste**: Hat er die Tur abgeschlossen? Ist der Herd aus? Fenster zu? Dokumentiert zwanghafte Kontrollrituale. *(Moglicher Hinweis auf zwanghafte Komorbiditat -- nicht thematisiert in Therapie)*
- **Beweis-Ordner**: Screenshots oder Notizen, die belegen, dass er *nicht* "komisch" war. Realitatsabgleich nach sozialen Situationen -- wirkt gegen die sozialphobie-typische Post-Event-Rumination ("War ich peinlich?").
- **Datenschutz-Log**: Wann hat die App Daten gesendet? Welche Berechtigungen wurden genutzt? *(Meta-Bedurfnis: App-Transparenz, kein klinisches Protokoll. Spiegelt Elias' generalisiertes Kontrollbedurfnis wider.)*

```

#### 8. Lena (PERSONA-015) -- `requirements_user_needs/personas/lena_depth_seeker/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 127):

```markdown
## Self-Tracking Protocols

### Therapie-Hausaufgabe (Shared with Therapist)

Von Prof. Dr. Weber verordnet:

- **Traumtagebuch**: Unmittelbares Festhalten von Traumen beim Aufwachen -- Fokus auf emotionale Qualitat ("Wie fuhlte sich der Traum an?"), nicht nur Handlung. Zentrales Material fur die tiefenpsychologische Arbeit. *(Psychoanalytische Traumarbeit; Freud, C.G. Jung)*

### Eigenbedarf (Private -- nicht mit Therapeut geteilt)

Selbstinitiierte Protokolle, die Lena fur sich selbst fuhrt:

- **Briefe an den Verstorbenen**: Narrative Eintrage in direkter Ansprache an Tobias. Dient der Aufrechterhaltung der Bindung (Continuing Bonds) und der Trauerbewaltigung. *(Klass, Silverman & Nickman, 1996, Continuing Bonds)*
- **Erinnerungs-Speicher**: "Heute habe ich das Lied gehort..." -- Sammlung von Erinnerungsfragmenten, Momenten, sensorischen Details. Getrieben von der Angst, Details zu vergessen, die Tobias lebendig halten.
- **Identitats-Notizen**: "Wer bin ich ohne ihn?" Philosophische, freie Eintrage, Zitate, Gedankenschnipsel. Dokumentiert Lenas Suche nach einem Selbst jenseits der Partnerrolle -- das tiefere therapeutische Thema, das sich hinter der Trauer verbirgt.

```

---

### GROUP 3: Self-Users

#### 9. Lisa (PERSONA-005) -- `requirements_user_needs/personas/lisa_waitlist_bridger/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 134):

```markdown
## Self-Tracking Protocols

Selbstinitiierte Protokolle ohne therapeutische Anleitung -- Lisa bereitet sich auf ihre kunftige Erstdiagnose vor:

- **Symptom-Tagebuch (ICD-10-orientiert)**: Systematisches Tracking von Depressionssymptomen, die sie online recherchiert hat: Schlaf, Appetit, Weinen, Freudlosigkeit, Konzentration. Ziel: "Beweisammlung" fur die erste Therapiesitzung -- will zeigen, dass sie "krank genug" ist.
- **Panik-Protokoll**: Wann treten Herzrasen, Atemnot, Schwindel auf? Kontext und Dauer. Ziel: Differentialdiagnostische Vorbereitung -- mochte korperliche Ursachen ausschliessen lassen.
- **Wartezeiten-Countdown**: Wie viele Therapeuten angerufen? Wer hat abgesagt? Nachste Termine? *(Organisatorisches Tracking, kein klinisches Protokoll. Dokumentiert den Kampf mit dem deutschen Versorgungssystem.)*

```

#### 10. David (PERSONA-008) -- `requirements_user_needs/personas/david_structure_seeker/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 131):

```markdown
## Self-Tracking Protocols

Selbstinitiierte Protokolle ohne therapeutische Anleitung -- David baut sich sein eigenes Selbstmanagement-System:

- **Pomodoro-Log**: Wie viele 25-Minuten-Fokusblacke geschafft? Einfache Strichliste. Gibt sofortige Sichtbarkeit der Produktivitat und nutzt die ADHS-typische Ansprechbarkeit auf kurzfristige Belohnungen.
- **Dopamin-Menu**: Kuratierte Liste von Aktivitaten, die gesunde Stimulation bieten (Sport, Musik, kurzes Gesprach) als Alternative zu Social-Media-Doom-Scrolling. Statische Referenzliste, die bei Langeweile/Understimulation konsultiert wird.
- **Medikamenten-Timer & Bestand**: "Habe ich es heute genommen?" (Ja/Nein) und "Muss ich nachbestellen?" (Restbestand). Kompensiert ADHS-typische Vergesslichkeit bei Medikamenteneinnahme und Rezeptverwaltung.
- **"Wall of Awful" Breaker**: Aufgaben in kleinste Teilschritte zerlegen (To-Do-Listen-Hybrid). Basiert auf dem ADHS-Konzept der "Wall of Awful" (emotionale Barriere vor ungeliebten Aufgaben). Jeder abgehakte Mikroschritt reduziert die Huerde.

```

#### 11. Hanna (PERSONA-007) -- `requirements_user_needs/personas/hanna_sleepless/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 121):

```markdown
## Self-Tracking Protocols

Selbstinitiierte Protokolle ohne therapeutische Anleitung -- Hanna kampft allein gegen die Schlaflosigkeit:

- **Schlaffenster-Protokoll**: Bettgehzeit vs. tatsachliche Schlafzeit, Aufwachzeitpunkt(e), Aufstehzeit. Ermoglicht die Berechnung der Schlafeffizienz (Schlafzeit / Bettzeit). *(KVT-I Standard; Riemann, 2018; DGSM)*
- **Grubel-Stuhl-Protokoll**: Wenn nachts wach: Aufstehen, Gedanken aufschreiben ("Worry Time" / "Grubelstuhl"), erst dann zuruck ins Bett. Externalisiert das Gedankenkarussell und bricht den Teufelskreis aus Grubeln und Schlaflosigkeit. *(Stimuluskontrolle nach Bootzin)*
- **Koffein- & Alkohol-Tracker**: Zeitpunkt und Menge von Koffein- und Alkoholkonsum. Ziel: Korrelation mit Wachphasen und Schlafqualitat erkennen. Hanna vermutet einen Zusammenhang, hat aber keine Daten.

```

#### 12. Michael (PERSONA-006) -- `requirements_user_needs/personas/michael_high_performer/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 127):

```markdown
## Self-Tracking Protocols

Selbstinitiierte Protokolle ohne therapeutische Anleitung -- Michael optimiert seine Leistung und sucht das fehlende Bindeglied zwischen Korper- und Psyche-Daten:

- **Stress vs. Recovery Log**: Korrelation von HRV-Daten (Garmin/Oura) mit subjektivem Stress-Empfinden. Ziel: Die Lucke zwischen objektiven Biometrie-Daten und mentalem Zustand schliessen. *(Kaluza, Gelassen und sicher im Stress; Polyvagal-Theorie, Porges)*
- **Arbeitszeit-Qualitat**: Deep Work vs. Meetings vs. administrative Tatigkeiten. Michael will wissen, ob er seine Zeit "gut" oder "schlecht" investiert -- und ob Meetingtage mit schlechtem Schlaf korrelieren.
- **Energie-Level (1-10)**: Morgens, Mittags, Abends. Ziel: Das "Mittagstief" oder den "Abend-Crash" visualisieren und mit Kalendereintregen korrelieren.
- **Physische Symptome**: Tinnitus, Ruckenschmerzen, Augenzucken, Kopfschmerzen. Dient als Fruhwarnsystem fur Burnout-Eskalation -- die korperlichen Signale, die Michael als "Stress" abtut, sind klinisch Alarmsignale.

```

#### 13. Nina (PERSONA-013) -- `requirements_user_needs/personas/nina_energy_budgeter/persona.md`

Insert BEFORE `## Related Scenarios` (currently line 138):

```markdown
## Self-Tracking Protocols

Selbstinitiierte Protokolle ohne therapeutische Anleitung -- Nina steuert ihr Energiebudget, um PEM-Crashs zu vermeiden:

- **Activity Log mit "Spoon Theory"**: Jede Tatigkeit bekommt einen Energiekosten-Wert ("Loffel"): Duschen = 3, Kochen = 5, Einkaufen = 8. Tagesbudget darf nicht uberschritten werden. Ziel: Pacing -- bewusste Belastungssteuerung innerhalb der Energiehulle. *(Charite Fatigue Centrum; "Stop. Rest. Pace." Guidelines)*
- **Symptom-Verzogerungs-Tracker**: Was hat Nina vor 24-48 Stunden getan, das den heutigen Crash ausgelost haben konnte? PEM (Post-Exertional Malaise) tritt verzogert auf -- der Zusammenhang zwischen Belastung und Crash ist ohne Tracking unsichtbar.
- **Ruhepuls-Protokoll**: Morgendlicher Ruhepuls vor dem Aufstehen. Aufstehen erst, wenn Puls unter individuellem Schwellenwert. Dient als objektiver Pacing-Indikator. *(HR-basiertes Pacing, ME/CFS-Community-Praxis)*
- **Orthostase-Check**: Schwindel, Schwarzwerden vor Augen, Herzrasen beim Aufstehen tracken. *(POTS -- Posturales orthostatisches Tachykardiesyndrom, haufige Long-COVID-Komorbiditat)*

```

---

## YAML Frontmatter Updates

For each persona file, the following YAML fields must be updated:

1. **`updated`**: Change to `2026-02-15`
2. **`version`**: Increment minor version by 0.1 (e.g., 4.3 --> 4.4, 1.1 --> 1.2)
3. **`review_history`**: Add new entry:

```yaml
  - date: 2026-02-15
    from: approved
    to: in_review
    reviewer: LLM
    notes: "Added protocols_and_homework / self_tracking_protocols section per TASK-PROC-027-13 (Gemini clinical research). Marked for user review."
```

4. **`review_status`**: Change to `in_review`

### Version Number Table

| Persona | Current Version | New Version |
|---|---|---|
| Dr. Sarah (PERSONA-001) | 4.3 | 4.4 |
| Dr. med. Turan (PERSONA-012) | 1.1 | 1.2 |
| Prof. Dr. Weber (PERSONA-011) | 1.0 | 1.1 |
| Max (PERSONA-002) | 5.0 | 5.1 |
| Sophie (PERSONA-010) | 1.0 | 1.1 |
| Jana (PERSONA-014) | 1.1 | 1.2 |
| Elias (PERSONA-009) | 1.1 | 1.2 |
| Lena (PERSONA-015) | 1.0 | 1.1 |
| Lisa (PERSONA-005) | 2.2 | 2.3 |
| David (PERSONA-008) | 2.2 | 2.3 |
| Hanna (PERSONA-007) | 2.1 | 2.2 |
| Michael (PERSONA-006) | 2.1 | 2.2 |
| Nina (PERSONA-013) | 1.1 | 1.2 |

---

## Execution Plan

### Recommended: 1 Agent, 3 Batches

This is a mechanical insertion task -- all content is fully specified above. No architectural decisions remain. A single agent executing in 3 batches (by role group) is the most efficient approach: it avoids coordination overhead while providing natural checkpoints.

### Agent 1: Implementation Engineer

**Batch 1 -- Therapists (3 personas)**

1. Open `requirements_user_needs/personas/dr_sarah/persona.md`
2. Update YAML frontmatter (updated, version, review_status, review_history)
3. Insert the `## Protocols & Homework (Verordnete Protokolle)` section before `## Related Scenarios`
4. Verify the file parses correctly (no broken markdown)
5. Repeat for Dr. med. Turan and Prof. Dr. Weber

**Batch 2 -- Clients (5 personas)**

6. Open `requirements_user_needs/personas/max_client/persona.md`
7. Update YAML frontmatter
8. Insert the `## Self-Tracking Protocols` section (with both subsections) before `## Related Scenarios`
9. Verify markdown integrity
10. Repeat for Sophie, Jana, Elias, Lena

**Batch 3 -- Self-Users (5 personas)**

11. Open `requirements_user_needs/personas/lisa_waitlist_bridger/persona.md`
12. Update YAML frontmatter
13. Insert the `## Self-Tracking Protocols` section before `## Related Scenarios`
14. Verify markdown integrity
15. Repeat for David, Hanna, Michael, Nina

**Batch 4 -- Verification & Documentation**

16. Run a verification pass across all 13 files:
    - Confirm `## Protocols & Homework` or `## Self-Tracking Protocols` exists in each
    - Confirm `## Related Scenarios` still appears as the last section
    - Confirm YAML frontmatter is valid (review_status: in_review, updated: 2026-02-15)
    - Confirm therapist-client cross-references are consistent (Dr. Sarah's Wochenprotokoll = Max's homework)
17. Document uncovered persona gaps (eating disorders, OCD, addiction, chronic pain, couples) in execution protocol
18. Log to protocol.md with agent ID

---

## Quality Criteria

- [ ] **All 13 personas modified**: Each has the new section
- [ ] **Section placement correct**: New section appears immediately before `## Related Scenarios` in every file
- [ ] **Format consistency**: Therapists use table format; clients use shared/private subsections; self-users use flat list
- [ ] **German clinical terminology**: All protocol names use established German terms (Expositionsprotokoll, not "Exposure Protocol")
- [ ] **Clinical sources included**: At minimum: Hautzinger, Beck/Wilken, Margraf, Linehan/Bohus, Riemann, Stangier, Kaluza, Charite for relevant protocols
- [ ] **Cross-reference consistency**: Max's homework matches Dr. Sarah's prescription; Lena's homework matches Prof. Weber's prescription
- [ ] **Special markers present**: Turan's Krisenplan marked as "Statisches Dokument"; Elias's Datenschutz-Log marked as "Meta-Bedurfnis"; Jana's Schwarzes Buch marked with privacy warning
- [ ] **YAML updated**: All 13 files have updated version, date, review_status, and review_history entry
- [ ] **No broken markdown**: All tables render correctly, no orphaned pipe characters, no broken links
- [ ] **Cluster protocols added**: Sophie (ERP), Nina (Schmerztagebuch), Dr. Sarah (Konsumtagebuch), Jana (Craving-Protokoll), Michael (Substanz-Konsum-Log)
- [ ] **Jana cluster expanded**: "Acute addiction patients" added to Cluster Representation
- [ ] **Dr. Sarah Anti-Traits updated**: Eating disorder exclusion documented with reasoning
- [ ] **Intentional exclusions documented**: Eating disorders (no cluster match) and systemic therapy (out of scope)

## Risks

1. **Umlauts in markdown tables**: Some markdown renderers struggle with umlauts in table cells. **Mitigation**: Use proper UTF-8 encoding; the existing persona files already use umlauts successfully.

2. **Table width in therapist format**: Long descriptions may make tables hard to read. **Mitigation**: Keep descriptions concise (1-2 sentences max); detailed clinical context goes in the "Klinischer Kontext" column.

3. **Jana's compromise note duplicates existing persona content**: The Diary Card compromise is already described in Jana's "Current Status Quo" section. **Mitigation**: The new section's note is brief and cross-referential, not a full re-explanation. It adds the structural context (what the original Diary Card contained) that the Status Quo section discusses narratively.

4. **Sophie's and Elias's therapists (Frau Kellner, Frau Richter) are not in the persona set**: These therapists are referenced only in the client personas. **Mitigation**: This is already the case in the Gemini research and the existing persona files. No new inconsistency is introduced.

---

## Amendment (2026-02-15): Cluster-Based Protocol Extensions

**Context**: User review identified that several "uncovered gaps" ARE covered by existing persona clusters ("Also Covers" / "Cluster Representation" sections). The following additions integrate cluster-based protocols into the affected personas.

### Amendment A1: Dr. Sarah — Add Addiction Protocol (Row 7 in Table)

Dr. Sarah's "Implicit Clusters Represented" explicitly names "addiction therapists (relapse protocols)" under "The Trainers." Add one row to her table:

```markdown
| 7 | **Konsumtagebuch & Ruckfallpraventions-Protokoll** | Tagliches Protokoll zu Konsumverhalten (Menge, Kontext, Trigger, Craving-Starke). Dient der Ruckfallpravention und der Fruherkennung von Risikosituationen. | Marlatt & Gordon (Relapse Prevention); Korkel (Kontrolliertes Trinken); DHS |
```

Additionally, update Dr. Sarah's **Anti-Traits** section to document intentional scope exclusions. Add after the existing last anti-trait bullet:

```markdown
- Not covering eating disorder protocols (Ess-Protokoll / CBT-E): Eating disorders have fundamentally different tracking requirements (meal context, body image, purging behavior) that are not represented by any current persona cluster. This is an intentional scope exclusion for now.
```

### Amendment A2: Sophie — Add OCD Cluster Protocol

Sophie's "Cluster Representation" explicitly names "OCD patients: Detailed ritual tracking, need to document compulsions/exposures." Add to her `### Eigenbedarf` subsection:

```markdown
- **ERP-Protokoll (Exposition mit Reaktionsverhinderung)**: Fur den OCD-Cluster, den Sophie mitreprasentiert: Dokumentation von Expositionsubungen (Situation, erwartete Angst, tatsachliche Angst, Ritualverzicht Ja/Nein, Anspannungsverlauf). *(Cluster-Protokoll: OCD-Patienten; Lakatos & Reinecker; Foa et al.)*
```

### Amendment A3: Nina — Add Chronic Pain Cluster Protocol

Nina's "Cluster Representation" explicitly names "Chronic pain with activity correlation: Fibromyalgia, chronic migraine with exertion triggers." Add to her protocol list:

```markdown
- **Schmerztagebuch (Deutsches Schmerztagebuch)**: Fur den Chronic-Pain-Cluster, den Nina mitreprasentiert: Schmerzstarke (VAS 0-10), Schmerzort, Ausloser, Aktivitat, Medikamenteneinnahme, Stimmung. Korrelation von Schmerz mit Aktivitatsniveau ermoglicht Pacing-Strategien. *(Cluster-Protokoll: Chronic Pain; Deutsche Schmerzgesellschaft; KIBIS)*
```

### Amendment A4: Jana — Expand Cluster + Add Addiction Protocol

Jana's current "Cluster Representation" lists "Impulse control disorders: Rage outbursts, self-harm urges, reactive aggression." This overlaps with acute addiction (Impulskontrolle, Craving-Management).

**Step 1**: Expand Jana's Cluster Representation section by adding a bullet:
```markdown
- **Acute addiction patients**: Craving management, impulse regulation, harm reduction — the emotional dysregulation and crisis-driven behavior patterns overlap significantly with BPD
```

**Step 2**: Add to Jana's `### Eigenbedarf (Private)` subsection:
```markdown
- **Konsumtagebuch / Craving-Protokoll**: Fur den Sucht-Cluster, den Jana mitreprasentiert: Was konsumiert? Wann? Wie stark war der Drang (0-10)? Was war der Ausloser? Welcher Skill wurde stattdessen eingesetzt? *(Cluster-Protokoll: Akute Sucht; Marlatt & Gordon, Urge Surfing; DHS)*
```

### Amendment A5: Michael — Add Habitual Addiction Protocols

Michael represents the "funktionaler Suchtkranker" — someone with habitual addiction patterns (alcohol after work, social drinking as coping, caffeine dependency) who is NOT in therapy and doesn't consider himself addicted. This extends his existing self-tracking focus on performance optimization.

Add to Michael's protocol list:
```markdown
- **Substanz-Konsum-Log**: Alkohol (Menge, Kontext: "nach der Arbeit", "Networking-Event"), Koffein (Menge, Uhrzeit), ggf. andere Substanzen. Michael sieht das als "Daten" — nicht als Suchtprotokoll. Die Korrelation mit Schlafqualitat und Energie-Level liefert den Weckruf, den er rational akzeptieren kann. *(Habitueller Konsum ohne Krankheitseinsicht; Korkel; DHS)*
```

### Amendment A6: Intentional Exclusions

The following clinical domains are **intentionally excluded** from protocol coverage:

| Domain | Reason | Where Documented |
|---|---|---|
| **Essstorungen (Eating Disorders)** | App-Anforderungen fundamental abweichend (Mahlzeiten-Kontext, Korperbildarbeit, Purging-Tracking). Kein bestehendes Persona-Cluster deckt die spezifischen Tracking-Bedurfnisse ab. | Dr. Sarah Anti-Traits (Amendment A1) |
| **Systemische Therapie** | Out of scope fur die App (zu aufwandig). Keine Therapeuten- oder Klienten-Persona geplant. | User-Entscheidung 2026-02-15 |

---

## Appendix: Remaining Uncovered Persona Gaps

After the amendments above, the following gaps remain as **intentional exclusions**:

| Clinical Domain | Key Protocols | Reason for Exclusion |
|---|---|---|
| Essstorungen (Eating Disorders) | Ess-Protokoll mit Kontext (Fairburn CBT-E), Spiegel-Expositionsprotokoll | Fundamental abweichende App-Anforderungen; kein Cluster-Match |
| Partnerschaft/Familie (Systemic) | Konflikt-Protokoll (Gottman; Bodenmann) | Systemische Therapie out of scope (User-Entscheidung) |
