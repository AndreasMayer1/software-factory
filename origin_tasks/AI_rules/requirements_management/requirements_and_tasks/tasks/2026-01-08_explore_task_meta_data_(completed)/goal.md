---
task_id: TASK-PROC-009-10
type: explore
parent_requirement: REQ-PROC-009
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2026-01-08
completed: 2026-01-08
after:
  - TASK-PROC-009-09
awaiting: []
covers:
  sections:
    - SEC-06  # Meta Information Standards
    - SEC-11  # Coverage Tracking
scope_description: "Explore and design standardized meta information system for requirements and tasks"
requirements_version:
  commit: 2863782
  file: ../requirements.md
---

Die Tasks, sprich die goal.md Dateien enthalten noch keine oder wenige standardisierte meta Informationen. Das gleiche gilt für die requirements.md Dateien. Wir müssen das ändern, um den Überblick zu behalten und eine Auswertung der requirements und tasks per skript zu ermöglichen.

Lass uns gemeinsam überlegen was hier Sinn macht.

Das Ziel dieses Tasks ist die Datei requirements_tasks\process\AI_rules\requirements_management\requirements_and_tasks\requirements.md anzupassen, sodass diese standardisierte meta informationen aufgenommen sind.
Als Bonus soll dann ein impl task angelegt werden, der das Ziel hat diese neuen anforderungen umzusetzen.
Die Umsetzung ist also noch nicht Teil dieses exploration tasks.

Ich habe bereits mit Gemini Überlegungen angestellt wie die Priorität der einzelnen Tasks und requriements aussehen sollte.

# Prioitäten Vorschlag

---

## Das Priorisierungs-System

**Berechnungsformel:** `Score = (URGENCY * 10) + IMPACT`

**Anwendung:**
1.  Gehe die Listen von **oben (5)** nach **unten (0)** durch.
2.  Stoppe bei der **ersten Stufe**, wo *mindestens ein* Kriterium zutrifft.
3.  Dokumentiere die Entscheidung (z.B. "Urgency 5 wegen Tech-Blocker").

---

### SKALA A: URGENCY (Dringlichkeit / Zeitfaktor)
*Leitfrage: Warum muss das JETZT passieren? Was passiert, wenn wir warten?*

#### **5: Immediate / Blocker (Sofort)**
*Hier brennt die Hütte oder das Fundament fehlt.*
*   **Technischer Blocker:** Kein anderer Task kann begonnen oder abgeschlossen werden, ohne dass dieser Task fertig ist (z.B. Datenbank-Setup, Basis-Architektur).
*   **Prozess-Blocker (Enabler):** Das Team/die KI kann nicht effizient arbeiten. Die "Maschine stockt" (z.B. CI/CD kaputt, Projekt-Regeln fehlen, Linter funktioniert nicht).
*   **Kritisches Risiko (Data/Security):** Akute Gefahr von Datenverlust, Sicherheitslücken oder Abstürzen, die die App unbenutzbar machen.
*   **Exploration Gap (Muss):** Wir stehen vor einer MVP-Implementierung, haben aber absolut keine Idee *wie* wir es lösen (Blindflug). Ohne diese Exploration ist Planung unmöglich.

#### **4: Next Up / Prerequisite (Als nächstes)**
*Der logische nächste Schritt für den Projektfortschritt.*
*   **Logische Abhängigkeit:** Ist die direkte Vorbedingung für ein Feature, das fest für den nächsten Schritt eingeplant ist (z.B. "API-Client bauen" bevor "UI bauen").
*   **Fail-Fast / Risiko-Minimierung:** Ein komplexes/unsicheres Thema, das wir *jetzt* testen müssen. Wenn es fehlschlägt, müssen wir das gesamte Konzept ändern (lieber jetzt wissen als am Ende).
*   **Harte Deadline:** Ein externer Termin (Investor, Legal, Partner-Dependency) zwingt uns, das jetzt zu tun.

#### **3: Scheduled / Soon (Zeitnah)**
*Standard-Entwicklungsfluss.*
*   **Sprint-Fokus:** Gehört zum aktuellen Themenblock, blockiert aber nichts Kritisches.
*   **Kontext-Effizienz (Synergie):** Wir arbeiten sowieso gerade in diesem Modul/dieser Datei. Es jetzt mitzumachen spart späteres "Eindenken" (Rüstzeiten minimieren).
*   **User-Pain (Medium):** Ein Bug oder Problem, das Nutzer nervt, aber Workarounds existieren. Sollte nicht lange liegen bleiben.

#### **2: Later / Queue (Später)**
*Entkoppelte Aufgaben.*
*   **Keine Abhängigkeiten:** Kann heute, morgen oder in 3 Wochen gemacht werden, ohne dass es andere Tasks beeinflusst.
*   **Warten auf Input:** Wir können zwar anfangen, aber es fehlen noch Details/Assets/Feedback. Besser schieben.
*   **Performance (Non-Critical):** Optimierung, die erst bei viel mehr Nutzern relevant wird.

#### **1: Whenever / Filler (Irgendwann)**
*Lückenfüller für "Leerlauf".*
*   **Kosmetik:** Rechtschreibfehler in Kommentaren, Einrückungen, Dateinamen bereinigen.
*   **Micro-Refactoring:** Code ist hässlich, funktioniert aber und wird selten angefasst.
*   **Zero Context Switch:** Aufgaben, die man "mal eben" in 5 Minuten erledigen kann, wenn man auf einen Build wartet.

#### **0: Blocked / On Hold (Pausiert)**
*   **Blockiert:** Kann technisch nicht umgesetzt werden (z.B. warten auf 3rd Party Library Update).
*   **Veraltet/Unklar:** Anforderung macht keinen Sinn mehr oder muss komplett neu diskutiert werden.

---

### SKALA B: IMPACT (Auswirkung / Wert)
*Leitfrage: Welchen Wert schaffen wir für den User oder die Entwicklung?*

#### **5: Critical / Core (Existenziell)**
*Ohne das gibt es kein Produkt.*
*   **MVP Core:** Die Hauptfunktion der App (z.B. "Therapieplan sehen"). Ohne das ist die App nutzlos.
*   **Showstopper Bug:** Der User kann die App nicht nutzen (Login geht nicht, App stürzt beim Start ab).
*   **Massiver Enabler (DevEx):** Eine Änderung, die die Entwicklungsgeschwindigkeit für *alle* zukünftigen Tasks drastisch erhöht (z.B. Einführung eines Test-Frameworks, Automatisierung von Releases).
*   **Legal / Compliance:** Zwingend erforderlich, um nicht verklagt oder aus dem Store geworfen zu werden.

#### **4: High Value (Sehr wichtig)**
*Unterscheidungsmerkmal und hohe Qualität.*
*   **USP (Alleinstellungsmerkmal):** Features, weswegen der User *unsere* App nutzt und nicht Excel (z.B. "Intelligente Auswertung", "Push-Erinnerung").
*   **User Pain Relief:** Löst ein großes Problem des Users, auch wenn es theoretisch (umständlich) anders ginge.
*   **Major Refactoring (Debt):** Verhindert, dass das Projekt in 2 Monaten gegen die Wand fährt (Wartbarkeit retten).
*   **Data Integrity:** Verhindert schleichende Datenfehler.

#### **3: Medium / Standard (Erwartet)**
*Guter Standard, Hygienefaktoren.*
*   **Erwartete Features:** Dinge, die jede App hat (Passwort ändern, Profilbild, Einstellungen). Fehlen sie, wirkt die App "billig", aber sie funktioniert.
*   **Prozess-Optimierung:** Hilft dem Entwickler, ist aber kein Game-Changer (z.B. bessere Logs, Dokumentation aktualisieren).
*   **UX-Flow:** Macht die Bedienung flüssiger, spart Klicks.

#### **2: Low / Polish (Nett)**
*Der "Wohlfühl"-Faktor.*
*   **Delighters:** Nette Animationen, Haptic Feedback, hübsche Empty-States.
*   **Edge Cases:** Fehler, die nur 1% der User betreffen oder nur sehr selten auftreten.
*   **Text/Wording:** Verständlichere Fehlermeldungen oder Labels.

#### **1: Trivial (Kaum spürbar)**
*   **Unsichtbar:** Technische Änderungen ohne spürbaren Effekt auf Performance oder Wartbarkeit.
*   **Pixel-Schieben:** Ob der Button nun 8px oder 10px Padding hat.

#### **0: None / Deprecated (Kein Wert)**
*   **Negativer Value:** Features, die User verwirren oder Code aufblähen ohne Nutzen.

---

### Anwendungshilfe für "Spezialfälle" (Mapping)

Damit Sie in ein paar Wochen nicht raten müssen, hier ein Mapping für die häufigsten "schwierigen" Kategorien:

| Art des Tasks | Typische URGENCY | Typische IMPACT | Begründung |
| :--- | :--- | :--- | :--- |
| **Requirements schreiben (für MVP)** | **5** (Blocker) oder **4** (Pre-req) | **5** (Core) | Ohne Req kein Code (Blocker). Req erbt Wichtigkeit des Features. |
| **Exploration / Research (für MVP)** | **4** (Fail-Fast) | **5** (Core) | Wir müssen wissen, ob es geht, bevor wir planen. |
| **CI/CD / Dev-Tools fixen** | **5** (Process Blocker) | **5** (Enabler) | Wenn Devs nicht arbeiten können, steht das Projekt. |
| **Refactoring (Präventiv)** | **3** (Synergie) | **4** (High) | Mach es, wenn du eh an der Datei arbeitest. |
| **Refactoring (Akut/Blocker)** | **5** (Blocker) | **4** (High) | Code ist so schlecht, dass Features nicht mehr baubar sind. |
| **Tests schreiben** | **4** (Pre-req) | **4** (High) | Sollte Teil des Features sein (Definition of Done). |
| **Bug: Datenverlust** | **5** (Immediate) | **5** (Critical) | Notfall. |
| **Bug: Layout verschoben** | **2** (Later) | **2** (Polish) | Unschön, aber funktionell egal. |


---

## Priority Reason Codes (PRC) System

Jede Bewertung besteht aus zwei Teilen:
1.  Dem **Wert** (0-5)
2.  Dem **Reason-Code** (Standardisiertes Kürzel)

**Format:** `[SKALA][WERT]-[CODE]` (z.B. `U5-BLOCK`, `I5-MVP`)

---

### SKALA A: URGENCY (Dringlichkeit)
*Code-Format: `U[0-5]-[REASON]`*

| Wert | Code | Bedeutung (Kurz) | Detaillierte Definition |
| :--- | :--- | :--- | :--- |
| **5** | `U5-BLOCK` | **Technical Blocker** | Blockiert andere Tasks technisch. Nichts geht weiter ohne das. |
| **5** | `U5-PROC` | **Process Blocker** | Team/KI kann nicht effizient arbeiten (Enabler fehlt, Tool kaputt). |
| **5** | `U5-RISK` | **Critical Risk** | Akute Gefahr (Crash, Datenverlust, Security). Muss sofort gefixt werden. |
| **5** | `U5-GAP` | **Exploration Gap** | MVP-Implementierung steht an, aber Lösungsweg ist unbekannt. |
| **4** | `U4-DEP` | **Dependency** | Logischer Vorgänger für ein Feature, das als Nächstes geplant ist. |
| **4** | `U4-FAIL` | **Fail Fast** | Hohes Implementierungsrisiko. Muss früh getestet werden, um Architekturfehler zu vermeiden. |
| **4** | `U4-TIME` | **Hard Deadline** | Externer Termin (Legal, Investor, Partner) zwingt zur Umsetzung. |
| **3** | `U3-SPRINT`| **Sprint Focus** | Teil des aktuellen Themenblocks/Sprints, blockiert aber nichts Kritisches. |
| **3** | `U3-CTX` | **Context Synergy** | Effizienz-Gewinn: Wir sind eh gerade in diesem Modul/Code-Bereich. |
| **3** | `U3-FIX` | **Medium Fix** | User-Problem, das nervt, aber Workarounds hat. Sollte zeitnah weg. |
| **2** | `U2-FREE` | **Decoupled** | Keine Abhängigkeiten. Kann jederzeit geschoben werden. |
| **2** | `U2-WAIT` | **Waiting** | Warten auf Feedback, Assets oder externe Infos. |
| **2** | `U2-PERF` | **Non-Crit Perf** | Optimierung, die erst später (bei Skalierung) relevant wird. |
| **1** | `U1-COSM` | **Cosmetic** | Rechtschreibung, Formatierung, Dateinamen bereinigen. |
| **1** | `U1-REFA` | **Micro Refactor** | Kleines Aufräumen von funktionierendem Code ("Pfadfinder-Regel"). |
| **1** | `U1-FILL` | **Filler** | 5-Minuten-Task für Leerlaufzeiten. |
| **0** | `U0-HOLD` | **On Hold** | Technisch blockiert oder Anforderungen unklar. Pausiert. |

---

### SKALA B: IMPACT (Auswirkung/Wert)
*Code-Format: `I[0-5]-[REASON]`*

| Wert | Code | Bedeutung (Kurz) | Detaillierte Definition |
| :--- | :--- | :--- | :--- |
| **5** | `I5-MVP` | **MVP Core** | Hauptfunktion der App. Ohne das ist das Produkt nutzlos. |
| **5** | `I5-STOP` | **Showstopper** | Bug verhindert Nutzung komplett (Login kaputt, Crash). |
| **5** | `I5-ENAB` | **Massive Enabler** | Beschleunigt gesamte zukünftige Entwicklung drastisch (DevEx). |
| **5** | `I5-LEGAL` | **Compliance** | Zwingend erforderlich für Legal/Store-Release. |
| **4** | `I4-USP` | **Key Feature** | Alleinstellungsmerkmal oder hoher Kundennutzen (Differenzierung). |
| **4** | `I4-PAIN` | **Pain Relief** | Löst ein großes User-Problem (auch wenn Workaround möglich wäre). |
| **4** | `I4-DEBT` | **Debt Reduction** | Großes Refactoring zur Rettung der Wartbarkeit/Stabilität. |
| **4** | `I4-DATA` | **Data Integrity** | Verhindert schleichende Datenfehler/Inkonsistenzen. |
| **3** | `I3-STD` | **Standard Expect**| Hygienefaktor (Passwort ändern, Profil). User erwartet es einfach. |
| **3** | `I3-PROC` | **Process Opt** | Hilft dem Entwickler (bessere Logs, Doku), aber kein Game-Changer. |
| **3** | `I3-UX` | **UX Flow** | Macht Bedienung flüssiger, spart Klicks, vermeidet Verwirrung. |
| **2** | `I2-JOY` | **Delighter** | "Nice to have", Animationen, Haptic Feedback. |
| **2** | `I2-EDGE` | **Edge Case** | Betrifft < 1% der User oder sehr seltene Fälle. |
| **2** | `I2-TXT` | **Wording/Polish** | Bessere Texte, verständlichere Labels. |
| **1** | `I1-INV` | **Invisible** | Technische Änderung ohne spürbaren Effekt. |
| **1** | `I1-PIX` | **Pixel Polish** | Minimale Design-Anpassungen (Padding, Color Shades). |
| **0** | `I0-NONE` | **No Value** | Deprecated, unnötig oder negativer Nutzen. |

---

### Anwendung in der Datei (YAML Frontmatter)

In Ihren Markdown-Dateien (Requirements oder Task-Goals) sieht das dann so aus. Der Kommentar ist optional, aber der Code ist Pflicht.

**Beispiel 1: Ein kritischer Blocker-Task**
```yaml
id: TASK-DB-001
type: impl
urgency: 5
urgency_reason: U5-BLOCK  # Datenbank wird für alle Features benötigt
impact: 5
impact_reason: I5-ENAB    # Ermöglicht erst die Arbeit an User-Features
status: open
```

**Beispiel 2: Ein Explore-Task für ein MVP Feature**
```yaml
id: TASK-EXP-LOGIN
type: explore
urgency: 4
urgency_reason: U4-FAIL   # Authentifizierung ist komplex, wir müssen die Risiken früh klären
impact: 5
impact_reason: I5-MVP     # Login ist Kernfunktion
status: open
```

**Beispiel 3: Ein Nice-to-Have Feature**
```yaml
id: REQ-DARKMODE
type: functional
urgency: 2
urgency_reason: U2-FREE   # Keine Abhängigkeiten, kann warten
impact: 2
impact_reason: I2-JOY     # User freuen sich, aber App geht auch ohne
status: open
```

### Zusammenfassung für das Skript

Das Übersichtsskript liest nun:
1.  **`urgency`** (Zahl für Sortierung)
2.  **`urgency_reason`** (String für Anzeige/Traceability)
3.  **`impact`** (Zahl für Sortierung)
4.  **`impact_reason`** (String für Anzeige/Traceability)

Die Ausgabe im Bericht wäre dann extrem transparent:
> **[55] Datenbank Setup** (`U5-BLOCK`, `I5-ENAB`)
> **[45] Login Konzept** (`U4-FAIL`, `I5-MVP`)
> **[22] Dark Mode** (`U2-FREE`, `I2-JOY`)

Damit ist sofort klar, *warum* der Dark Mode unten steht, ohne dass man in die Datei schauen muss.