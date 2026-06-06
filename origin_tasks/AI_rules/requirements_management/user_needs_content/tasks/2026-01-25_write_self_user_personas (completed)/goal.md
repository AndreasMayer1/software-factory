---
task_id: TASK-PROC-011-05
type: impl
parent_requirement: REQ-PROC-011
urgency: 3
urgency_reason: U3-QUAL
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-01-25
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Replace sarah_self_user persona with 4 distinct self-user personas: Lisa, Michael, Hanna, David"
tags: [user-needs, personas, self-user]
---

# Goal: Create 4 Self-User Personas

The existing persona sarah_self_user is not good enough. I want to replace it by 4 other personas. And none of them can be named sarah, because that name is already taken by the therapist...
Please add the personas based on the following descriptions (of course in english and you can add information based on your own knowledge of the groups if you can):


***

**1. Basisdaten & Archetyp**
*   **Name:** Lisa (Die Wartezeit-Überbrückerin)
*   **Rolle:** Self-User (Pre-Therapy)
*   **Archetyp:** "The Abandoned Seeker" (Die Alleingelassene Suchende)
*   **Kontext:** Lisa hat eine leichte bis mittelschwere depressive Episode diagnostiziert bekommen. Sie hat einen Vermittlungscode für die Terminvergabestelle, telefoniert Dutzende Therapeuten ab, bekommt aber nur Absagen oder Wartelisten-Plätze (Wartezeit: 6-9 Monate). Sie steckt in der deutschen "Versorgungslücke".

**2. Current Status Quo (Wie sie sich aktuell behilft)**
*   **Werkzeuge:** Sie hat sich ein "6-Minuten-Tagebuch" oder ein spezielles "Therapie-Tagebuch" aus Papier bei Amazon gekauft, weil sie *irgendetwas* tun wollte, um nicht tatenlos zu sein.
*   **Digitale Versuche:** Sie hat Apps wie "Daylio" probiert, aber wieder gelöscht, weil ihr die bunten Smileys zu trivial vorkamen ("Ich bin nicht einfach nur 'traurig', ich bin verzweifelt") und weil sie in der Datenschutzerklärung "Cloud Sync" gelesen hat.
*   **Verhalten:** Sie schreibt unregelmäßig in das Papierbuch. Wenn es ihr sehr schlecht geht (Antriebslosigkeit), bleibt das Buch leer, was Scham auslöst.
*   **Notizen:** Sie nutzt die Notiz-App ihres Handys für akute Krisengedanken, schreibt aber kryptisch, damit niemand, der ihr Handy nimmt, es versteht.

**3. Pain Points & Friction (Probleme mit dem Status Quo)**
*   **Datenschutz-Paranoia (DE-Spezifisch):** Lisa ist Studentin/Berufseinsteigerin. Sie hat massive Angst, dass eine Diagnose oder detaillierte Aufzeichnungen ihre Chancen auf Verbeamtung oder den Abschluss einer Berufsunfähigkeitsversicherung (BU) zerstören könnten. Cloud-Dienste sind für sie ein rotes Tuch.
*   **Die "Black Box":** Sie sammelt Daten (Papier), weiß aber nicht, ob diese für den zukünftigen Therapeuten überhaupt relevant sind. Sie hat Angst, "falsch" zu dokumentieren.
*   **Verlustangst:** Sie hat Angst, das physische Buch zu verlieren oder dass ihre WG-Mitbewohner es finden. Deshalb versteckt sie es, was die Hürde zur Nutzung erhöht (es liegt nicht griffbereit).

**4. Jobs to be Done (Bedürfnisse)**
*   **Vorbereitung:** Sie möchte ein "Daten-Paket" schnüren, das sie dem Therapeuten beim Erstgespräch in 6 Monaten übergeben kann, um die Diagnose zu beschleunigen ("Ich will keine Zeit mehr verlieren").
*   **Selbstwirksamkeit:** Sie muss das Gefühl haben, *aktiv* an ihrer Heilung zu arbeiten, um der Hilflosigkeit des Wartens entgegenzuwirken.
*   **Validierung:** Sie braucht einen Ort, an dem ihre Gefühle "echt" sein dürfen, ohne soziale Maske.

**5. Non-User Constraints**
*   **Versicherungen/Staat:** Darf keinen Zugriff auf Daten haben (Gegenteil von "Apple Health Sharing").
*   **Mitbewohner/Partner:** Dürfen das physische Tagebuch oder die App-Inhalte nicht sehen (Angst vor Stigma "Die Psycho-Lisa").

**6. Mental Health Context**
*   **Energie:** Schwankend. An schlechten Tagen ist selbst das Aufschlagen des Notizbuchs zu viel.
*   **Kognition:** Grübelneigung, Konzentrationsschwierigkeiten.



***

**1. Basisdaten & Archetyp**
*   **Name:** Michael (Der High-Performer)
*   **Rolle:** Self-User (Prevention/Optimization)
*   **Archetyp:** "The Functional Mask" (Der Funktionierende)
*   **Kontext:** Michael (38) ist Teamleiter im Consulting/IT. Er arbeitet 50-60 Stunden die Woche. Er definiert sich über Leistung. Er merkt seit Monaten, dass seine Konzentration nachlässt, er gereizt auf Mitarbeiter reagiert und schlecht schläft. Er nennt es "Stress", aber klinisch bewegt er sich auf einen Burnout zu. Er würde niemals zugeben, dass er "nicht mehr kann".

**2. Current Status Quo (Wie er sich aktuell behilft)**
*   **Werkzeuge:** Er ist ein "Quantified Self" Typ Light. Er trägt eine High-End Smartwatch (Garmin/Apple Watch), um seinen Schlaf und seine "Body Battery" zu tracken. Er nutzt Produktivitäts-Apps (ToDoist, Outlook), um sein Leben zu "managen".
*   **Verhalten:** Wenn die Uhr sagt "Schlechter Schlaf", versucht er es mit "Hacks" zu lösen (Magnesium, Blue-Light-Brille, noch strikteres Zeitmanagement). Er versucht, das emotionale Problem technisch zu lösen.
*   **Lücke:** Er hat unzählige Bio-Daten (Herzfrequenz, Schritte), aber ihm fehlt der Kontext. Er weiß nicht, *welches* Meeting ihn gestern so ausgelaugt hat. Er führt kein Tagebuch, weil er das für "esoterisch" oder Zeitverschwendung hält.

**3. Pain Points & Friction (Probleme mit dem Status Quo)**
*   **Massive Datenschutz-Angst (Job-Risk):** Sein Smartphone ist ein "Bring Your Own Device" oder Firmengerät mit MDM (Mobile Device Management). Er hat panische Angst, dass die IT-Abteilung sehen könnte, dass er eine App für psychische Gesundheit nutzt. Das wäre für ihn das Karriere-Aus ("Nicht belastbar"). Cloud-Sync ist daher ein No-Go.
*   **Scham vor Schwäche:** Er kann mit niemandem darüber reden (weder Chef noch Partnerin, die er nicht belasten will). Er ist isoliert in seiner "Funktions-Maske".
*   **Daten-Silos:** Sein Kalender weiß, wann er Stress hat. Seine Uhr weiß, wann er schlecht schläft. Aber die beiden reden nicht miteinander. Er muss die Zusammenhänge mühsam erraten.

**4. Jobs to be Done (Bedürfnisse)**
*   **Objektivierung:** Er braucht Daten ("Beweise"), um sich selbst einzugestehen, dass er kürzertreten muss. Gefühle zählt er nicht, Zahlen schon.
*   **Frühwarnsystem:** Er will eine "Tankanzeige" für seine mentale Energie, um den Crash zu verhindern, ohne die Leistung komplett runterzufahren.
*   **Diskretes Ventil:** Er braucht einen Ort, um Frust abzulassen (Schreiben), der absolut sicher und unsichtbar ist.

**5. Non-User Constraints**
*   **Arbeitgeber/IT-Admin:** Darf niemals Zugriff auf App-Inhalte oder Metadaten bekommen (Gefahr durch MDM-Profile oder Firmen-Backups).
*   **Kollegen (Shoulder Surfer):** Er nutzt das Handy oft im Zug oder im Open Space Office. Die App darf nicht nach "Therapie" aussehen (keine Pastellfarben, keine weinenden Emojis). Sie muss aussehen wie ein Business-Tool (Notizen/Kalender).

**6. Mental Health Context**
*   **Energie:** Hochfrequent, aber "falsche" Energie (Adrenalin/Cortisol getrieben). Kann nicht abschalten.
*   **Kognition:** Tunnelblick. Fokussiert auf Problemlösung, ignoriert emotionale Bedürfnisse.



***

**1. Basisdaten & Archetyp**
*   **Name:** Hanna (Die Schlaflose)
*   **Rolle:** Self-User (Symptom-Management)
*   **Archetyp:** "The Exhausted Ruminator" (Die erschöpfte Grüblerin)
*   **Kontext:** Hanna (45) leidet seit Jahren unter Durchschlafstörungen. Sie schläft ein, wacht aber zuverlässig zwischen 2:00 und 4:00 Uhr morgens auf. Dann beginnt das "Gedankenkarussell": Sorgen um die Kinder, To-Dos für die Arbeit, finanzielle Ängste. Sie ist tagsüber chronisch übermüdet.

**2. Current Status Quo (Wie sie sich aktuell behilft)**
*   **Werkzeuge:** Sie nutzt eine Smartwatch/App (z.B. Sleep Cycle oder Fitbit), die ihr jeden Morgen sagt: "Schlafqualität: 45%". Das frustriert sie ("Ich weiß, dass ich schlecht geschlafen habe, ich brauche keine App, die mir das sagt!").
*   **Analoge Versuche:** Ihr Arzt hat geraten: "Schreiben Sie Ihre Sorgen auf." Sie hat ein Notizbuch auf dem Nachttisch.
*   **Verhalten:** Wenn sie aufwacht, versucht sie oft, die Gedanken zu unterdrücken ("Nicht denken, schlaf jetzt!"), was den Druck erhöht.
*   **Medienkonsum:** Oft greift sie aus Verzweiflung zum Handy und scrollt durch Social Media (Doomscrolling), um das Gehirn zu "betäuben", was durch das Blaulicht das Wiedereinschlafen verhindert.

**3. Pain Points & Friction (Probleme mit dem Status Quo)**
*   **Licht-Barriere:** Sie teilt das Bett mit ihrem Partner. Wenn sie das Licht anmacht, um ins Notizbuch zu schreiben, wacht er auf. Das will sie vermeiden.
*   **Physische Hürde:** Im Dunkeln schreiben führt zu unleserlichem Gekritzel. Am nächsten Morgen kann sie ihre eigenen "Erkenntnisse" nicht mehr lesen.
*   **Fehlender Kontext:** Ihre Schlaf-Tracker-App zeigt ihr die physiologischen Daten (Wachphasen), aber sie kann diese nicht mit ihren Gedanken verknüpfen. Sie weiß morgens oft nicht mehr, *was* genau sie wachgehalten hat (Memory Fog).

**4. Jobs to be Done (Bedürfnisse)**
*   **Externalisierung:** Sie braucht einen Weg, Gedanken aus dem Kopf in einen "Container" zu verschieben, damit das Gehirn Ruhe geben kann ("Es ist notiert, ich muss nicht mehr daran denken").
*   **Nacht-Kompatibilität:** Der Prozess muss im Dunkeln funktionieren, ohne den Partner zu stören (kein Licht, keine Geräusche) und ohne sie selbst "wachzublitzen".
*   **Mustererkennung:** Sie will verstehen: "Grüble ich immer über Arbeit oder über Familie? Gibt es Muster?"

**5. Non-User Constraints**
*   **Partner im Bett (Auditory/Visual Witness):** Jedes helle Licht oder laute Tippen/Klicken ist verboten.
*   **Morgendliches Ich:** Will nicht sofort mit den negativen Gedanken der Nacht konfrontiert werden ("Vulnerability Hangover"), sondern die Daten nur analytisch sehen.

**6. Mental Health Context**
*   **Energie:** Morgens sehr niedrig (Anlaufschwierigkeiten). Nachts paradoxerweise hoch (nervoese Unruhe).
*   **Kognition:** Nachts eingeengtes Denken (Katastrophisieren), tagsüber Konzentrationsschwäche.



***

**1. Basisdaten & Archetyp**
*   **Name:** David (Der Struktur-Sucher)
*   **Rolle:** Self-User (Management & Structure)
*   **Archetyp:** "The Chaos Tamer" (Der Chaos-Bändiger)
*   **Kontext:** David (28) hat ADHS im Erwachsenenalter. Er ist kreativ und intelligent, scheitert aber oft an der "Exekutiven Dysfunktion": Er kann Aufgaben nicht beginnen, verliert den Faden oder vergisst Routinen. Sein Leben fühlt sich an wie ein ständiger Kampf gegen das Chaos.

**2. Current Status Quo (Wie er sich aktuell behilft)**
*   **Werkzeuge:** Ein Friedhof an versuchten Methoden. Drei halbvolle Papier-Kalender, überall Post-it-Zettel (die er nicht mehr wahrnimmt -> "Nose Blindness"), und fünf installierte "Habit Tracker" Apps, die er seit Wochen nicht geöffnet hat.
*   **Verhalten:** Er hat Phasen des "Hyperfokus", in denen er 3 Tage lang alles perfekt trackt. Dann vergisst er es einen Tag ("Streak broken"), fühlt sich als Versager und öffnet die App nie wieder ("Shame Spiral").
*   **Object Permanence Problem:** Was er nicht direkt sieht, existiert für ihn nicht. Wenn ein Notizbuch zugeklappt ist oder eine App nicht auf dem Homescreen leuchtet, vergisst er ihre Existenz.

**3. Pain Points & Friction (Probleme mit dem Status Quo)**
*   **Die "Wall of Awful":** Jede Hürde ist zu hoch. Wenn er sich erst durch 3 Menüs klicken muss, um "Medikamente genommen" zu loggen, macht er es nicht.
*   **Toxische Gamification:** Aktuelle Apps nutzen "Streaks" (Serien). Für David ist ein gerissener Streak keine Motivation ("Versuch's nochmal!"), sondern eine Bestätigung, dass er es "wieder nicht geschafft hat". Das demotiviert ihn total.
*   **Input-Paralyse:** Manche Tagebuch-Apps fragen "Wie war dein Tag?" mit einem leeren Textfeld. David weiß nicht, wo er anfangen soll, ist überwältigt und schreibt gar nichts.

**4. Jobs to be Done (Bedürfnisse)**
*   **Das "Externe Gehirn":** Er braucht ein System, das Dinge für ihn behält (Termine, Medikation, Stimmung), damit er seinen Arbeitsspeicher entlasten kann.
*   **Hürdenlosigkeit (Low Friction):** Die Erfassung muss < 3 Sekunden dauern und direkt verfügbar sein (Widget / One-Tap).
*   **Verzeihendes System:** Er braucht ein Tool, das Lücken akzeptiert ("Es ist okay, dass du 3 Tage weg warst") und ihn nicht bestraft, sondern sanft wieder reinholt.

**5. Non-User Constraints**
*   **Soziales Umfeld:** Er nutzt das Handy oft in Gesprächen oder Meetings als "Fidgeting" oder um schnell etwas zu notieren, bevor er es vergisst. Das muss diskret gehen, ohne unhöflich zu wirken.

**6. Mental Health Context**
*   **Energie:** Sprunghaft. Mal 200%, mal 0% (Dopamin-Mangel).
*   **Kognition:** Assoziativ, sprunghaft. Braucht visuelle Klarheit, keine Textwüsten.


***

Damit auch dokumentiert ist warum gerade diese drei Personas, hier noch die Herleitung. 
Zuerst ein Brainstorming welche möglichen NUtzergruppen es geben könnte für self assessment:
Hier ist die konsolidierte Liste aller identifizierten Gruppen, sortiert nach geschätzter Marktgröße und Nutzungs-Wahrscheinlichkeit:

1.  Die Schlafgestörten & Nächtlichen Grübler
2.  Die Burnout-Präventler & Gestressten
3.  Die Wechseljahre-Managerinnen & Hormon-Tracker (inkl. PMDS)
4.  Die Habit-Tracker & Gewohnheits-Bauer ("Atomic Habits")
5.  Die Wartezeit-Überbrücker (Leichte Depression/Angst)
6.  Die Migräne- & Schmerzpatienten
7.  Die ADHS-Struktur-Sucher
8.  Die "Emotional Eaters" & Food-Mood-Detektive
9.  Die Achtsamen & Dankbarkeits-Journaler
10. Die Beziehungs-Prüfer & -Pfleger
11. Die Jungen Mütter (Postpartale Belastung)
12. Die Reiz-Manager (Hochsensibilität / Autismus)
13. Die Angst-Analysten & Mut-Sammler
14. Die Mental-Load-Träger (Pflegende Angehörige)
15. Die Therapie-Alumni (Erhaltung)
16. Die Biohacker & Quantified-Self-Fans
17. Die "Sober Curious" & Sucht-Reduzierer
18. Die Winter-Blueser (SAD)
19. Die Medikamenten-Einsteller
20. Die "Flow"-Sucher & Produktivitäts-Optimierer
21. Die Social Battery Manager (Introvertierte)
22. Die Finanz-Psychologen (Frustkäufer)
23. Die Dopamin-Detoxer (Social Media Reduktion)
24. Die Bipolaren Wächter
25. Die Trauma-Verarbeiter
26. Die Wut-Regulierer
27. Die Imposter-Syndrom Fighter
28. Die Prüfungs-Paniker
29. Die Intervall-Faster
30. Die Trauernden
31. Die Long-Covid / CFS Pacer
32. Die Kinderwunsch-Patienten
33. Die Transition-Begleiter
34. Die Koffein-Kuratoren
35. Die Wetter-Optimierer & -Fühligen
36. Die Microdoser
37. Die Mondphasen-Tracker

Dann eine tiefere Bewertung davon:
Da deine App sich als **"Local First / Secure / Mental Health"** positioniert, gewichte ich das Kriterium **"Passung zur App & Privatsphäre"** und **"Auffindbarkeit (SEO)"** höher als die reine Gruppengröße.

Apps für "Habit Tracking" gibt es Tausende (Roter Ozean). Apps für "Sicheres psychologisches Journaling" sind seltener (Blauer Ozean).

Hier ist das **Scoring (0-100)**.
*Legende: 100 = Perfekter "Product-Market-Fit" für den Start.*

### 🥇 Top Tier (Der "Sweet Spot")
*Hoher Leidensdruck, Datenschutz kritisch, sucht explizit nach psychologischer Hilfe/Struktur.*

1.  **Die Wartezeit-Überbrücker (Score: 95)**
    *   *Größe:* Mittel (aber konstant nachwachsend).
    *   *Leidensdruck:* Extrem hoch (brauchen *jetzt* Hilfe).
    *   *Konkurrenz:* Meist teure DiGA-Apps oder schlechte Qualität.
    *   *SEO-Match:* Sucht exakt nach "Therapie App", "Depression Hilfe", "Stimmungstagebuch".
    *   *Warum:* Die App ist perfekt vorbereitet für den späteren Übergang zum Therapeuten.

2.  **Die Burnout-Präventler & Gestressten (Score: 92)**
    *   *Größe:* Riesig (Volkskrankheit).
    *   *Leidensdruck:* Hoch (Angst vor Jobverlust/Kollaps).
    *   *Privatsphäre:* **Kritisch** (Arbeitgeber darf nichts wissen -> Local First ist Killer-Feature).
    *   *SEO-Match:* "Stress Tagebuch", "Burnout prävention".
    *   *Konkurrenz:* Headspace/Calm (Meditations-Fokus), aber wenig analytische Tracker.

3.  **Die Schlafgestörten & Nächtlichen Grübler (Score: 88)**
    *   *Größe:* Sehr groß.
    *   *Leidensdruck:* Hoch (Schlafmangel macht mürbe).
    *   *App-Nutzen:* "Brain Dump" Feature passt perfekt.
    *   *Konkurrenz:* Stark (Sleep Cycle), aber die messen nur *Bewegung*. Deine App erklärt das *Warum* (Gedanken).

4.  **Die ADHS-Struktur-Sucher (Score: 85)**
    *   *Größe:* Mittel bis Groß (hohe Dunkelziffer bei Erwachsenen).
    *   *App-Nutzen:* Brauchen "Externes Gehirn". Lieben flexible Anpassbarkeit (deine App!).
    *   *Konkurrenz:* Oft zu komplex oder zu verspielt.
    *   *SEO-Match:* "ADHS Planer", "Struktur App".

---

### 🥈 Mid Tier (Gute Nischen oder starke Konkurrenz)
*Spezifische Probleme, gute Passung, aber teilweise starke Marktführer.*

5.  **Die Trauma-Verarbeiter (PTBS) (Score: 80)**
    *   *Privatsphäre:* Absolut entscheidend (Zero Knowledge).
    *   *Konkurrenz:* Wenig gute Angebote.
    *   *Nachteil:* Kleine Zielgruppe, sehr sensibel (App muss extrem vorsichtig designt sein).

6.  **Die Wechseljahre-Managerinnen (Score: 78)**
    *   *Größe:* Groß.
    *   *App-Nutzen:* Korrelation Hormon/Psyche.
    *   *Konkurrenz:* **Extrem stark** (Clue, Flo), aber diese fokussieren oft auf Fruchtbarkeit/Periode, weniger auf die psychische Menopause-Belastung.

7.  **Die Migräne- & Schmerzpatienten (Score: 75)**
    *   *App-Nutzen:* Schmerztagebuch ist Standard-Therapie.
    *   *Konkurrenz:* Migräne-App (TK) ist Marktführer in DE. Schwer dagegen anzukommen, außer über Privacy.

8.  **Die Reiz-Manager (Autismus/HSP) (Score: 74)**
    *   *Passung:* Deine App (reizarm, Dark Mode, anpassbar) ist perfekt für sie.
    *   *SEO:* Suchen oft nicht nach "Therapie App", sondern spezifischen Tools. Nische.

9.  **Die Bipolaren Wächter (Score: 72)**
    *   *Leidensdruck:* Hoch.
    *   *Nutzen:* Frühwarnsystem ist vital.
    *   *Größe:* Klein (ca. 1-2% der Bevölkerung).

10. **Die Jungen Mütter (Postpartal) (Score: 70)**
    *   *Leidensdruck:* Hoch.
    *   *Konkurrenz:* Baby-Tracker Apps (die oft Stimmung der Mutter mit abfragen).
    *   *SEO:* Suchen eher nach "Baby App" als nach "Mutter Depression App".

---

### 🥉 Low Tier (Schlechter Fit oder Roter Ozean)
*Entweder zu viel Konkurrenz, falsche Suchintention oder zu nischig.*

11. **Die Habit-Tracker ("Atomic Habits") (Score: 60)**
    *   *Problem:* **Roter Ozean.** Es gibt tausende Habit-Apps. Deine App heißt "Psychologie..." -> schreckt reine Optimierer ab.

12. **Die "Sober Curious" / Sucht (Score: 58)**
    *   *Konkurrenz:* "I am Sober" ist Platzhirsch. Sehr spezifische Features (Zähler) nötig, die du erst bauen müsstest.

13. **Die Beziehungs-Prüfer (Score: 55)**
    *   *Problem:* Suchen eher Ratgeber/Foren als Tracker. Schwierig in Daten zu fassen.

14. **Die "Emotional Eaters" (Score: 50)**
    *   *Konkurrenz:* Noom, Yazio, WeightWatchers. Gigantische Marketing-Budgets.

15. **... Rest der Liste (Scores < 50)**
    *   (Mondphasen, Microdoser, Wetter etc. -> zu nischig oder Spielerei).
