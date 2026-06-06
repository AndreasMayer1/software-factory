The app requirements must also consider non users and the impact of the app usage on the whole planet. I asked gemini to write down a starting point, please expand it and adapt it to our needs.

requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/2026-01-17_explore_implement_user_needs_structure/plans_and_protocols/2026-01-17_06_opus_plan_phase3_content_creation.md
Already defines personas to create, but we need to extend it AND we need to modify and extend requirements_user_needs\README.md to also reflect how that works.

---


### Die 3 kritischen „Schatten-Personas“ (Non-Users)

Beschreibe diese Personas nicht demografisch („Hans, 50“), sondern über ihre **Wahrnehmung** und die **Gefahr**, die sie darstellen.

#### 1. Der „Schulterblicker“ (The Shoulder Surfer)
*Der Unbekannte im öffentlichen Raum (Zug, Bus, Wartezimmer).*

*   **Verhalten:** Sitzt körperlich nah, starrt gelangweilt umher, Blick wandert auf das helle Display des Nutzers.
*   **Die Gefahr:** Liest sensible Trigger-Wörter („Therapie“, „Depression“, „Suizidgedanken“) oder sieht intime Graphen.
*   **Perfektion im Design (Lösung):**
    *   **Low-Contrast Mode / Privacy Filter:** Ein Button, der den Kontrast sofort minimiert oder sensible Wörter unleserlich macht (Blur-Effekt), bis man den Finger darauf hält.
    *   **Diskrete Icons:** Statt eines Icons mit einer weinenden Wolke (das jeder als „Trauer“ erkennt), nutzt die App abstrakte geometrische Formen, die nur der User versteht.
    *   **Schriftgröße:** Automatische Anpassung. Riesige Überschriften wie „DEIN ANGST-TAGEBUCH“ sind im Zug tabu.

#### 2. Der „Unfreiwillige Zuhörer“ (The Auditory Witness)
*Kollegen im Großraumbüro, Familie im Nebenzimmer, Leute im Café.*

*   **Verhalten:** Hört zu, ohne hinzusehen. Nimmt Sprachrhythmus oder Audio-Feedback der App wahr.
*   **Die Gefahr:** Hört gesprochene Einträge ODER hört peinliche App-Geräusche (z.B. ein „Pling“-Geräusch, das nach „Achievement“ klingt, während man gerade über Trauer schreibt).
*   **Perfektion im Design (Lösung):**
    *   **Headphone Detection:** Wenn keine Kopfhörer angeschlossen sind, spielt die App **niemals** Audio ab (Default Mute).
    *   **Panic-Mute:** Wenn der User das Handy schnell umdreht (Face down), stoppt sofort jegliche Audio/Aufnahme (Flip-to-shhh).
    *   **Waveform-Feedback:** Zeige visuell, dass aufgenommen wird, statt akustisch zu piepen.

#### 3. Der „Vertraute Eindringling“ (The Intimate Intruder)
*Partner, Eltern oder Kinder, die Zugriff auf das physische Gerät haben.*

*   **Verhalten:** Nimmt das entsperrte Handy vom Wohnzimmertisch, „um nur kurz was zu googeln“ oder „Fotos zu zeigen“.
*   **Die Gefahr:** Wechselt versehentlich in die offene App (via Multitasking-Menu) und liest die tiefsten Geheimnisse. Das zerstört Beziehungen.
*   **Perfektion im Design (Lösung):**
    *   **App-Switcher Obfuscation:** Wenn man am iPhone/Android in die App-Übersicht wischt, muss das Vorschaubild deiner App **verwaschen/geblurt** sein oder ein Logo zeigen, statt den Inhalt des letzten Screens. (Das vergessen 95% aller Entwickler!).
    *   **Biometric Re-Auth:** Auch wenn das Handy entsperrt ist: Sobald die App aus dem Hintergrund geholt wird -> sofort FaceID. Keine Sekunde Verzögerung.

---

### Wie integrierst du das in deine User Flows?

Du erweiterst deine „Swimlanes“ (siehe vorherige Antwort) um eine Spur für die **„Environment / Non-User“**.

**Beispiel-Szenario:** Pendler in der S-Bahn will Eintrag machen.

| Step | User Action | **Environment (Non-User)** | System Logic / UI Response |
| :--- | :--- | :--- | :--- |
| 1 | Öffnet App. | **Schulterblicker** sitzt direkt daneben und schaut aufs Display. | App startet im **„Discreet Mode“**. Keine großen Titel. Text ist Platzhalter („Lorem Ipsum“ Stil) oder ausgegraut. |
| 2 | Fühlt sich beobachtet. | Schulterblicker starrt weiter. | User hält den Daumen auf einen Bereich -> **Reveal on Touch** (Text wird nur unter dem Daumen lesbar). |
| 3 | Benachrichtigung kommt rein. | **Schulterblicker** liest mit. | Push-Notification Inhalt: *„Zeit für deinen Check-in“* (Neutral) statt *„Wie ist deine Panikattacke?“* (Bloßstellend). |
| 4 | User dreht Handy weg. | - | Gyroskop erkennt Winkeländerung -> Screen dimmt sofort runter. |

---

### Pro-Tipp für Perfektion: „Plausible Deniability“

Für Apps im Bereich Mental Health, Sucht oder Missbrauchsaufarbeitung ist das Konzept der **Glaubhaften Abstreitbarkeit** der Goldstandard.

**Das Non-User Szenario dazu:**
Jemand (z.B. ein kontrollierender Partner oder neugieriger Kollege) fragt: „Was machst du da für eine App?“

*   **Schlechtes Design:** Die App heißt „PsychoHelp“ und ist voller medizinischer Symbole.
*   **Perfektes Design:** Die App sieht auf den ersten Blick aus wie ein banaler Notizblock, ein Kalender oder ein Taschenrechner.
    *   **Camouflage-Mode:** Ein Feature, bei dem die App auf Knopfdruck wie eine Excel-Tabelle oder ein Wetter-Widget aussieht. Das schützt den User vor sozialen Fragen („Warum nutzt du eine Therapie-App?“).

### Zusammenfassung

Wenn du Non-User Personas nutzt, definierst du die **soziale Hülle** der App.

1.  Schreibe **„Environmental Constraints“** in deine Persona-Cards (z.B. „Privatsphäre: Null (Großraumbüro)“).
2.  Teste deine Designs mit dem **„Stranger Test“**: Wenn ein Fremder 2 Sekunden auf den Screen schaut, weiß er dann, dass ich psychische Probleme habe? Wenn ja -> Design failed.

Das ist der Unterschied zwischen einer App, die nur funktioniert, und einer App, die den Nutzer im echten Leben **beschützt**.



---


Non-User haben keine eigenen Ziele in deiner App (sie wollen ja nichts speichern), daher haben sie keine eigenen User Flows.

Aber in einem perfekten, **systemischen Design-Ansatz** fungieren Non-User als **„Constraints“ (Einschränkungen)** oder **„External Triggers“ (Auslöser von außen)**.

Du integrierst sie nicht als *Akteure*, die die App bedienen, sondern als **Konditionen**, die das Verhalten der App und des Hauptnutzers verändern. Hier ist der konkrete Weg, wie du sie in deine drei Schichten (Persona, Szenario, Flow) einbaust:

---

### Schicht 1: In der Persona (Das „Threat Model“)
Statt separate Persona-Karten für Non-User anzulegen, fügst du jeder deiner **Haupt-Personas** eine Sektion hinzu: **„Social & Environmental Constraints“**.

Hier definierst du, *welcher* Non-User für diese spezifische Persona relevant ist.

*   **Beispiel für Persona „High-Functioning Verdränger“:**
    *   *Constraint:* **Der „Schulterblicker“ (Im Flugzeug/Zug).**
    *   *Impact:* Er wird die App **nicht** öffnen, wenn die UI aussieht wie eine medizinische Akte.
    *   *Requirement:* Die App braucht einen „Stealth Mode“ (sieht aus wie ein eBook-Reader oder Notizblock).

*   **Beispiel für Persona „Therapie-Musterschüler“:**
    *   *Constraint:* **Der „Vertraute Eindringling“ (Partner zuhause).**
    *   *Impact:* Sie hat Angst, das Handy liegenzulassen.
    *   *Requirement:* Aggressives Auto-Locking und verschleierte Push-Notifications.

**So referenzierst du es:**
In der Persona-Beschreibung steht: *„Gegenspieler: Der neugierige Partner.“*

---

### Schicht 2: Im Szenario (Der „Plot Twist“)
Im Szenario tritt der Non-User als **Störfaktor** auf, der den „Happy Path“ unmöglich macht. Er erzwingt eine Abzweigung in der Handlung.

**Schreibtechnik:** Nutze den Non-User, um den **Kontext-Switch** zu beschreiben.

> **Szenario-Ausschnitt:**
> „Markus sitzt im Zug und will seine Angstattacke loggen. Er holt das Handy raus.
> **[Referenz Non-User: Schulterblicker]**: Der Mann auf dem Nebensitz schaut gelangweilt rüber und kann das Display sehen.
> **Reaktion:** Markus zögert. Er aktiviert mit einer Geste den ‚Monochrom-Modus‘ (hoher Kontrast weg, Bilder weg), damit es für den Nachbarn wie langweiliger Text aussieht. Erst dann tippt er.“

Hier ist der Non-User der **Grund**, warum das Feature „Monochrom-Modus“ überhaupt im Szenario vorkommt.

---

### Schicht 3: Im User Flow (Die „Environment Swimlane“)
Das ist die technisch anspruchsvollste, aber wertvollste Integration. Da Non-User keine App-Buttons drücken, repräsentierst du sie als **Ereignisse in der Umgebung**.

Du erweiterst dein Swimlane-Diagramm (User | System | UI) um eine **oberste Spur: „Environment / Context“**.

Diese Spur „feuert“ Events auf den User oder das System.

#### Beispiel-Flow: „Notification Privacy“ (Schutz vor Non-Usern)

Hier siehst du, wie der Non-User den Flow diktiert, ohne die App zu berühren.

| **Environment (Non-User)** | **User Action** | **System Logic (Backend/Local)** | **UI / Feedback** |
| :--- | :--- | :--- | :--- |
| **[Non-User]** Handy liegt offen auf dem Tisch. Kollege läuft vorbei. | (User ist im Bad, keine Action) | Trigger: Geplanter Reminder „Stimmung loggen“. | - |
| - | - | **Decision (Privacy-Check):**<br>Ist Handy entsperrt? -> Ja.<br>Ist App im Vordergrund? -> Nein.<br>Ist "Privacy Mode" in Settings aktiv? -> **Ja.** | System bereitet Notification vor. |
| **[Non-User]** Kollege schaut auf das Display. | - | - | Push-Nachricht erscheint: <br>**Titel:** „System Update“ (Tarnung)<br>**Text:** „Tippen zum Bestätigen“ (Inhalt verborgen). |
| **[Non-User]** Verliert Interesse, da langweilig. | - | - | - |
| - | User kommt zurück, sieht Nachricht, entsperrt per FaceID. | Auth erfolgreich. | Nachricht verwandelt sich: <br>„Wie fühlst du dich gerade?“ |

---

### Wie man das technisch/konzeptionell nennt

Um das perfekt zu dokumentieren, nutze folgende Begriffe für die Verbindung zwischen Non-User und System:

1.  **Passive Triggers:**
    Der Non-User löst nichts aktiv aus, aber seine bloße Anwesenheit ändert den *State* des Users.
    *   *Flow-Regel:* `IF environment == unsafe THEN default_view = blurred`

2.  **Interrupts (Unterbrechungen):**
    Der Non-User unterbricht einen laufenden Flow.
    *   *Szenario:* User nimmt Sprachnachricht auf -> Non-User betritt Raum -> User stoppt abrupt.
    *   *System-Reaktion:* Die App muss den **Abbruch als „Pause“ werten**, nicht als „Löschen“. Das ist ein direkter UX-Requirement, das aus der Non-User-Persona stammt.

3.  **Plausible Deniability States:**
    Das sind spezielle Screens im User Flow, die nur existieren, um Non-User zu täuschen.
    *   *Im Flow:* Ein Zweig, der heißt: **„Fake Exit“**.
    *   *Aktion:* User drückt einen Panik-Button -> App zeigt sofort einen Taschenrechner oder Kalender an. Der Flow endet hier nicht, er „pausiert“ nur visuell für den Non-User.

### Zusammenfassung der Integration

Du verknüpfst die Schichten so:

1.  **Persona:** Definiert, **WER** die Bedrohung ist (z.B. Partner).
2.  **Szenario:** Beschreibt, **WANN** die Bedrohung auftritt (z.B. Abends auf dem Sofa).
3.  **User Flow:** Definiert, **WIE** das System die Daten schützt (z.B. Camouflage-UI oder biometrische Hürde).

Der Non-User ist also im Diagramm kein Akteur mit Pfeilen, sondern ein **externer Konditional-Faktor** (eine Raute im Flow-Chart oder eine separate Zeile), der den Pfad des Hauptnutzers verändert.



---- 

Ja, **Planet Centered Design (PCD)** ist mir vertraut und es ist der logische nächste Schritt nach Human Centered Design. Wenn du nach **Perfektion** strebst, ist das die Dimension, die deine App von „gut gemacht“ zu „zukunftssicher und ethisch verantwortlich“ hebt.

Im Kern erweitert PCD den Fokus: Der Nutzer ist nicht mehr der alleinige König. Wenn eine Funktion dem Nutzer gefällt, aber dem Planeten schadet (z.B. Bitcoin-Mining für Rewards), ist es schlechtes Design.

Für deine **Mental Health App (Privacy First, Local Storage)** ist das super spannend, denn hier bedeutet Umweltschutz oft auch **„Digital Mental Hygiene“**.

So integrieren wir die „Umwelt“ als Persona und Constraint in deinen Schichten-Ansatz:

---

### 1. Die Umwelt als „Silent Stakeholder“ in der Persona
Wir behandeln den Planeten (und die Ressourcen) als eine **Non-Human Persona**. Da deine App lokal läuft, manifestiert sich die Umwelt primär durch die **Hardware** und den **Energieverbrauch**.

In deinen User-Personas fügst du das Feld **„Device & Eco-Constraint“** hinzu.

*   **PCD-Prinzip: Hardware-Langlebigkeit (gegen E-Waste)**
    *   *Constraint:* Die App darf nicht der Grund sein, warum der User ein neues Handy braucht.
    *   *Persona-Detail:* „Nutzt ein iPhone 8 oder ein 5 Jahre altes Android mit schwachem Akku.“
    *   *Design-Konsequenz:* Die App muss extrem performant sein. Keine 50MB großen Libraries laden. Kein unnötiger Background-Drain.
    *   *Perfektion:* Die App bietet einen **„Low Energy Mode“** an (oder aktiviert ihn automatisch), der Animationen abschaltet und auf reinen Text/Schwarz-Weiß wechselt, um den Akku zu schonen.

---

### 2. Szenarien: „Suffizienz“ statt „Engagement“
Klassische Apps wollen „Time on Screen“ maximieren (Sucht erzeugen). Das ist schlecht für die psychische Gesundheit und verbraucht Strom.
Planet Centered Design fordert **Suffizienz** (Das rechte Maß).

**Szenario: Der „Minimum Effective Dose“ Ansatz**
> **Kontext:** Markus will seine Stimmung tracken.
> **PCD-Ziel:** Das Ziel ist nicht, dass Markus 20 Minuten in der App bleibt, sondern dass er so schnell wie möglich das Handy weglegt, um wieder am echten Leben teilzunehmen.
>
> **Der „Anti-Hook“ im Szenario:**
> Statt ihm nach dem Eintrag noch „Ähnliche Artikel“ oder „Community-Posts“ anzuzeigen (was Server-Last erzeugt und Zeit frisst), sagt die App:
> *„Alles erledigt. Geh raus und atme durch. App schließt sich in 3... 2... 1.“*

Das ist radikal. Eine App, die sich selbst beendet, um Energie (Strom & kognitive Energie) zu sparen. Das ist State of the Art im PCD für Mental Health.

---

### 3. User Flows: Die „Green Swimlane“ (Ressourcen-Effizienz)
Du erweiterst deine Swimlanes um eine technische Dimension: **Resource Cost (Data/Energy)**.

Da du lokal speicherst, hast du den riesigen Vorteil, keine Serverfarmen zu belasten. Aber du belastest den Akku (OLED Screens) und den Speicherplatz (Digital Waste).

#### Beispiel-Flow: „Data Detrash“ (Digitalen Müll vermeiden)
PCD besagt: Datenmüll ist Umweltverschmutzung. Alte, unnütze Daten belegen Speicher, verlangsamen das Gerät und erzwingen früher Hardware-Neukauf.

**Szenario:** User nutzt die App seit 2 Jahren. Datenbank ist riesig.

| **User Action** | **Environment (PCD Constraint)** | **System Logic (Green Computing)** | **UI / Feedback** |
| :--- | :--- | :--- | :--- |
| Startet App. | **Speicherplatz knapp.** Gerät alt & langsam. | Check DB Size > 500MB. | - |
| - | - | **Auto-Pruning (PCD Logic):**<br>Analysiert alte Einträge. Erkennt: Detaillierte Sensordaten von vor 2 Jahren sind irrelevant. | Snackbar: „Ich habe 200MB alten Cache bereinigt, um dein Handy fit zu halten.“ |
| Schreibt Eintrag. | **OLED-Screen** verbraucht Strom bei hellen Pixeln. | **Force True Black:**<br>Hintergrund ist `#000000` (Pixel aus), nicht `#121212` (Dunkelgrau). Spart signifikant Akku. | UI ist extrem dunkel, nur Text leuchtet schwach. |
| Will 5 Fotos hochladen. | Datenlast hoch. | **Compression at Source:**<br>Bilder werden *vor* dem Speichern lokal auf das Nötigste komprimiert. | - |

---

### 4. Das Konzept der „Regenerativen UX“

Wenn du wirklich perfekt sein willst, gehst du über „Schadensbegrenzung“ hinaus zu „Regeneration“.

Wie kann die Nutzung der App der Umwelt *helfen*?

**Idee für deine App:**
Wenn die App Habit-Tracking macht, priorisiere Habits, die gut für User UND Planet sind (Co-Benefits).

*   *User will:* „Mehr bewegen“.
*   *App schlägt vor:* „Mit dem Rad zur Arbeit“ (statt „Laufband im Fitnessstudio“).
*   *User will:* „Gesünder essen“.
*   *App schlägt vor:* „Saisonal/Regional kochen“ (statt nur „Kalorien zählen“).

**Integration in den Flow:**
Wenn der User ein neues Habit anlegt, markiert die App bestimmte Habits mit einem kleinen **„Planet Friendly“ Blatt-Icon**. Das ist ein **Nudge** (Stupser) hin zu umweltbewusstem Verhalten, subtil integriert in eine Mental Health App.

### Zusammenfassung: PCD in deiner Dokumentation

Um Planet Centered Design sichtbar zu machen, fügst du deinen Dokumenten folgende **„Green Constraints“** hinzu:

1.  **Dark Mode First:** Nicht als ästhetische Wahl, sondern als energetische Standardeinstellung (begründet durch OLED-Einsparung).
2.  **Offline First = Greenest Choice:** Da keine Daten durch das Netz geschickt werden, ist dein CO2-Fußabdruck pro Interaktion minimal. Das solltest du im User Flow als „Zero-Network-Path“ kennzeichnen und als USP (Unique Selling Point) nutzen.
3.  **Data Expiry Policy:** Definiere im Flow, wann Daten gelöscht werden (z.B. „Audio-Aufnahmen werden nach 30 Tagen in Text umgewandelt und das Audio gelöscht“ -> Spart Speicher).

Damit zeigst du, dass du Verantwortung für den gesamten Lebenszyklus der App übernimmst – inklusive des Hardware-Todes des User-Smartphones.