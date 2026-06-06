---
title: "Strategische Analyse: Software Factory Strukturverbesserungen"
date: 2026-04-22
author: claude-opus-4-5
task: TASK-PROC-042-01
type: strategic_analysis
---

# Strategische Analyse: Software Factory Strukturverbesserungen

## 1. Systemanalyse

### Was ist dieses System im Kern?

Die Software Factory ist ein **Produktionssystem zweiter Ordnung** — ein System, das ein anderes System (die Flutter-App) herstellt. Diese Meta-Ebene ist konzeptionell wichtig: Fehler in der Factory kosten nicht nur Zeit, sie korrumpieren möglicherweise das Endprodukt selbst oder führen zu falsch priorisierten Entwicklungsrichtungen.

Aus CS-Sicht handelt es sich um eine **Komposition aus mehreren klassischen Mustern**:

**1. Directed Acyclic Graph (DAG) mit partieller Ordnung**
Die Artefakthierarchie (Persona → Scenario → Flow → Requirements → Task → Code) ist ein DAG. Die `after:`/`awaiting:`-Felder sind explizit deklarierte Kanten; die impliziten Abhängigkeiten sind die nicht-deklarierten Kanten, die das System strukturell instabil machen. Das Task-Ordering-Problem ist im Kern ein **topologisches Sortierungsproblem** auf einem unvollständig bekannten Graphen.

**2. Event-Driven Pipeline mit LLM-Prozessoren**
Jeder Skill ist ein Prozessor in einer Datenpipeline: er liest Eingabe-Artefakte, transformiert sie, schreibt Ausgabe-Artefakte. Die "Events" sind implizit (der Nutzer entscheidet, wann ein Skill aufgerufen wird), nicht explizit gepusht. Das System ist damit näher an einem **Pull-basierten Batch-System** als an einem echten Event-Driven System.

**3. Endliche Automaten (FSM) über Artefaktstatus**
Jedes Artefakt durchläuft Statusübergänge (defined → in_progress → implemented). Diese FSMs sind derzeit nur in der Dokumentation beschrieben, nicht formal deklariert. Das führt dazu, dass Übergänge inkonsistent sind — manche Skills setzen Status explizit, andere vergessen es.

**4. Constitution-Based Agent Orchestration**
CLAUDE.md ist eine Konstitution im rechtlichen Sinne: ein hochrangiges Regelwerk, das spezifischeren Regeln in Skills übergeordnet ist. Diese Hierarchie ist korrekt konzipiert, aber die Durchsetzung ist probabilistisch (LLMs halten sich mal mehr, mal weniger daran).

**5. Organisch gewachsenes Expertensystem**
Die Skills bilden zusammen ein Wissen über "wie man eine Flutter-App richtig entwickelt" ab, das normalerweise nur in den Köpfen erfahrener Entwickler lebt. Das System ist damit ein externalisiertes, kompiliertes Expertenwissen — aber eines, das inkrementell gewachsen ist und entsprechend unstrukturierte Stellen hat.

### Warum ist Refactoring von LLM-Systemen so schwierig?

Bevor wir Verbesserungsoptionen bewerten, muss dieser Kernpunkt präzisiert werden:

Bei klassischem Code-Refactoring gilt: Wenn die Testsuite grün ist, ist das Refactoring korrekt. Bei LLM-Systemen gilt das nicht, weil:

1. **Nichtdeterminismus**: Derselbe Skill-Text produziert bei verschiedenen Läufen unterschiedliche Ergebnisse. Eine "korrekte" Version kann dennoch in 20% der Fälle versagen.
2. **Kontextabhängigkeit**: LLMs lesen implizit den gesamten Kontext — eine kleine Änderung in einem Skill kann durch Interaktion mit anderen Kontextelementen unerwartete Effekte haben.
3. **Regressionsdetektion ist teuer**: Um zu bemerken, dass ein refactorter Skill schlechter funktioniert, muss man ihn mehrfach benutzen und die Outputs subjektiv bewerten.
4. **Produktions-Kopplung**: Das System läuft in Production. Ein fehlerhafter Skill kann echte Arbeitsprodukte beschädigen (falsche Requirements, falsch generierter Code, verlorene Artefakte).
5. **LLM-Drift**: Auch ohne Änderung am System kann ein Update des Modells (z.B. Claude Sonnet 4.6 → 4.7) das Verhalten aller Skills verändern.

Diese Faktoren bedeuten: **Jede strukturelle Verbesserung muss additiv sein, nicht substitutiv**. Der Goldstandard ist, neues Verhalten neben das alte zu stellen und es schrittweise zu aktivieren — nie das alte zu löschen, bevor das neue bewiesen ist.

---

## 2. Verbesserungsoptionen

Die folgenden Optionen sind unabhängig voneinander. Sie sind sortiert von "niedrigstem Risiko / höchstem sicheren Nutzen" zu "höchstem Risiko / theoretisch größtem Nutzen".

---

### Option A: Artifact State Machine formalisieren

**Was würde sich verbessern?**
Derzeit sind die Statusübergänge von Artefakten (z.B. `flow.md`: draft → in_review → aligned → approved) nur in der Dokumentation beschrieben. Kein Script validiert, ob ein Skill einen ungültigen Übergang gemacht hat. Das führt zu Inkonsistenzen (z.B. ein Requirement mit Status `defined` obwohl noch kein Explore-Task existiert).

Eine formale FSM-Deklaration (z.B. in einem YAML-File `.claude/artifact_states.yaml`) würde erlauben:
- Scripts können ungültige Statusübergänge erkennen und warnen
- Skills können vor dem Schreiben prüfen: "Darf ich diesen Status setzen?"
- `STATUS.md`-Generatoren können konsistentere Berichte erzeugen
- Neue Artefakttypen können sauber eingeführt werden

**Aufwand**: S (1 neues YAML-File, Anpassung von 3–5 Scripts, keine Skill-Änderungen erforderlich)

**Erfolgswahrscheinlichkeit**: hoch

Begründung: Dies ist primär ein deterministisches Script-Problem, kein LLM-Problem. Die FSM wird in YAML deklariert, Scripts lesen sie und validieren. LLMs müssen sich nicht ändern — sie schreiben einfach weiter in Frontmatter. Die Validierung passiert deterministisch danach.

**Hauptrisiken**:
- Die FSM-Deklaration könnte die Realität nicht korrekt abbilden (z.B. gibt es Artefakte mit 8 Status, von denen man nur 4 dokumentiert hat)
- Scripts könnten falsch-positive Warnungen emittieren und Vertrauen verlieren
- Mitigation: Nur als Warnung, nicht als hard Block einführen; zunächst im "observe only"-Modus betreiben

---

### Option B: Skill-Kontrakte einführen (Input/Output-Schema)

**Was würde sich verbessern?**
Aktuell ist jeder Skill ein Freitext-Dokument. Was ein Skill als Input erwartet und als Output produziert, ist prosaisch beschrieben — wenn überhaupt. Es gibt keine maschinell prüfbaren Verträge.

Würde man für jeden Skill ein explizites Schema einführen:
```yaml
# Beispiel: requ-derive-from-flow
inputs:
  - type: flow
    status: approved
    count: "1+"
  - type: notes
    status: optional
outputs:
  - type: goal_md
    layer: requirement_derivation
    flags: [writes_requirements: true, source_gap: required]
```

...hätte man die Grundlage für:
- Automatische Dependency-Vorschläge (welcher Skill kann das Input für diesen Skill liefern?)
- Validierung nach Skill-Ausführung (hat der Skill wirklich das deklarierte Output produziert?)
- Routing-Verbesserungen in `claude-route` (welcher Skill passt zu dieser Situation?)
- Dokumentation, die automatisch aktuell bleibt

**Aufwand**: L (50+ Skills müssen annotiert werden; neues Schema muss entworfen werden; `claude-route` und `factory_flows.md` profitieren, müssen aber nicht zwingend angepasst werden)

**Erfolgswahrscheinlichkeit**: mittel

Begründung: Das Schema-Design ist lösbar (S-Aufwand). Die Annotation von 50 Skills ist mühsam aber deterministisch — gut für einen Automatisierungslauf. Das Risiko liegt in der **Maintenance**: jedes Mal, wenn ein Skill sich ändert, muss sein Schema co-evolve. Wenn das Schema veraltet, ist es schlimmer als kein Schema (es täuscht Korrektheit vor). Skaliert das mit der Teamgröße von 1 Person?

**Hauptrisiken**:
- Schema-Drift: Skills ändern sich häufig, Schema bleibt zurück
- Overengineering: Wenn das Schema nie maschinell ausgewertet wird, ist es totes Dokumentation
- Mitigation: Nur die "stabilen Kern-Skills" annotieren (10–15 von 50); den Rest weglassen; Schema-Check in `claude-modify-skill` einbauen

---

### Option C: `factory_flows.md` als generierte Dokumentation (Single Source of Truth)

**Was würde sich verbessern?**
`factory_flows.md` ist derzeit manuell gepflegt und acknowledged als unvollständig. Es fehlen Scripts als Akteure; manche Kanten sind ungenau. Da Skills und Scripts sich ändern, läuft `factory_flows.md` ständig hinterher.

Alternative: `factory_flows.md` wird aus den Skill-Kontrakten (Option B) und dem `artifact_states.yaml` (Option A) **generiert** — ähnlich wie `requirements.md` aus den Einzeldateien generiert wird. Das Diagramm wäre dann immer korrekt.

**Aufwand**: M (abhängig von Option A + B; wenn diese existieren, ist die Generierung ~S; ohne sie ist es L)

**Erfolgswahrscheinlichkeit**: mittel (hoch wenn A + B vorhanden, niedrig alleine)

Begründung: Generierte Dokumentation ist konsistent per Definition. Aber es setzt voraus, dass die Eingabedaten (Skill-Kontrakte) korrekt sind. Wenn nicht: "Garbage in, garbage out".

**Hauptrisiken**:
- Generiertes Diagramm ist korrekter als das manuelle, aber weniger lesbar (zu viele Nodes)
- Mitigation: Generierung nur für Teilgraph (z.B. nur Artifact-Level, nicht Skill-Level); Skills sind dann Labels auf Kanten, nicht Nodes

---

### Option D: Observability-Schicht ("Factory Telemetry")

**Was würde sich verbessern?**
Das größte Blindspot des Systems: Was passiert wirklich, wenn die Autorun-Orchestrierung läuft? Wie oft schlägt ein Skill fehl? Welche Skills werden am häufigsten aufgerufen? Wo entstehen die meisten Korrekturen (Blocker, Repair-Tasks)?

Eine einfache Telemetry-Schicht (in bestehende `claude-log`-Infrastruktur integrierbar) würde erfassen:
- Skill-Name + Zeitstempel + Erfolg/Fehlschlag
- Artefakt-Statusübergänge (wann, durch welchen Skill)
- Geblockte Tasks (wie lange, was hat sie deblockiert)

Diese Daten würden `claude-optimize` signifikant verbessern: statt subjektiver Muster-Erkennung gäbe es quantitative Evidenz.

**Aufwand**: S (Erweiterung von `claude-log`; kein neues Konzept erforderlich)

**Erfolgswahrscheinlichkeit**: hoch

Begründung: `claude-log` existiert bereits und loggt Agent-IDs. Das Schema zu erweitern um Skill-Name und Outcome ist trivial. Die Daten werden bereits gesammelt (in den `.jsonl`-Dateien), sie werden nur nicht aggregiert. Ein einziger Python-Script als Aggregator genügt.

**Hauptrisiken**:
- LLMs "vergessen" manchmal `claude-log` aufzurufen (bereits bekanntes Problem)
- Daten sind unvollständig → Statistiken sind irreführend
- Mitigation: Hooks in `settings.json` können `claude-log` erzwingen; alternativ als optionale Verbesserung behandeln

---

### Option E: Skill-Kategorisierung und Layering

**Was würde sich verbessern?**
Die 50+ Skills sind derzeit flach in `.claude/skills/` — alphabetisch geordnet, durch `INDEX.md` beschrieben, aber ohne klare Abstraktionsebenen. Einige Skills sind "primitive" (claude-log, claude-commit), andere sind "compositional" (code-complex ruft intern mehrere Subflows auf), andere sind "meta" (claude-optimize, claude-modify-skill).

Eine explizite Layer-Struktur würde helfen:
- Layer 0 (Primitives): claude-log, claude-commit, claude-ask — grundlegende Operationen
- Layer 1 (Artifact Workers): ux-write-persona, requ-explore, code-simple — ein Artefakt transformieren
- Layer 2 (Orchestrators): product-intake, code-complex, claude-autorun — rufen Layer-1-Skills auf
- Layer 3 (Meta): claude-optimize, claude-modify-skill, claude-create-skill — ändern das System selbst

Diese Kategorisierung würde:
- LLMs bessere Entscheidungen treffen lassen (welche Ebene brauche ich hier?)
- Verhindern, dass Meta-Skills aus Layer-1-Kontexten aufgerufen werden
- Die Cognitive Load beim Lesen von `INDEX.md` reduzieren

**Aufwand**: XS (nur Reorganisation von `INDEX.md` + Namenskonvention; keine Skill-Inhalte ändern)

**Erfolgswahrscheinlichkeit**: hoch

Begründung: Das ist eine Dokumentationsverbesserung ohne funktionale Änderung. Worst case: das LLM ignoriert die Kategorisierung. Best case: die Struktur führt zu besseren Routing-Entscheidungen. Kein Regressionsrisiko.

**Hauptrisiken**:
- Kategorisierung ist nicht eindeutig (claude-route ist Layer 1 und Layer 2 gleichzeitig)
- Mitigation: Primäre Kategorie reicht; Hinweise auf Doppelnatur als Kommentar

---

### Option F: Skill-Konsolidierung (Reduktion von Complexity)

**Was würde sich verbessern?**
50+ Skills sind viel. Viele sind sehr ähnlich (z.B. `task-complete` vs `task-complete-bugfix`; `ux-flow-draft` / `ux-flow-complete` / `ux-flow-approve` vs `ux-create-flow` als Router). Das erhöht die Cognitive Load beim Routing und führt zu Duplikation von Logik.

Mögliche Konsolidierungen:
- `ux-flow-*` Subfamilie könnte in `ux-create-flow` mit Mode-Parameter aufgehen (als interne Implementation, nicht als externe Interfaces)
- `task-complete` und `task-complete-bugfix` könnten ein Skill mit Typ-Parameter sein

**Aufwand**: M–L (Zusammenführung von Skills erfordert sorgfältige Analyse der Unterschiede; jeder fehler kann Production-Tasks beschädigen)

**Erfolgswahrscheinlichkeit**: niedrig bis mittel

Begründung: Dies ist ein klassischer "Aufräum-Refactor" — theoretisch sinnvoll, in der Praxis riskant. Das Hauptproblem: Die Unterschiede zwischen `task-complete` und `task-complete-bugfix` sind nicht zufällig entstanden — sie spiegeln echte Unterschiede in den Workflows wider. Eine Zusammenführung könnte subtile Verhaltensunterschiede löschen, die nicht dokumentiert sind. LLMs sind außerdem sensitiv auf Prompt-Formulierungen: Ein konsolidierter Skill kann schlechter performen als zwei spezialisierte, selbst wenn die Logik "dieselbe" ist.

**Hauptrisiken**:
- Subtile Verhaltensänderungen durch Konsolidierung, die erst nach Wochen in Production sichtbar werden
- Kein Rollback-Mechanismus ohne manuelle Analyse
- Mitigation: Nur konsolidieren, wenn beide Skills parallel für 10+ Tasks validiert wurden; alte Skills als deprecated beibehalten

---

### Option G: Formale Skill-Testharness

**Was würde sich verbessern?**
"Keine deterministischen Tests" ist das Hauptproblem für Refactoring. Aber es gibt einen pragmatischen Mittelweg: **Snapshot-Tests für Skills**.

Idee: Für jeden Skill werden 3–5 "golden examples" gespeichert:
- Input: Konkreter Artefakt-Zustand (goal.md + relevante files)
- Expected output: Was der Skill produzieren sollte (Kernaussagen, nicht exakter Text)
- Evaluation: Ein separater LLM-Call der prüft: "Hat der Skill das Wesentliche getan?"

Das ist kein deterministischer Test, aber ein **probabilistischer Regressionstest**. Wenn ein modifizierter Skill in 4/5 Golden Examples das Wesentliche nicht mehr trifft, ist das ein starkes Signal.

**Aufwand**: XL (Konzept-Design + Tool-Entwicklung + 50 Skills × 3 Golden Examples = ~150 Beispiele + Evaluation-Infrastruktur)

**Erfolgswahrscheinlichkeit**: niedrig bis mittel

Begründung: Das Konzept ist solide (angelehnt an LLM-Eval-Frameworks wie RAGAS, Braintrust, etc.). Die Umsetzung ist jedoch enorm aufwändig und die "Erfolgswahrscheinlichkeit" hängt stark davon ab, wie man Erfolg definiert. Ein probabilistischer Testharness reduziert Risiko, eliminiert es nicht. Die Gefahr: man investiert XL Aufwand und hat am Ende ein System, das "meist" korrekt warnt — aber die 20% False Negatives (Regression nicht erkannt) oder False Positives (kein Problem, aber Alarm) untergraben das Vertrauen.

**Hauptrisiken**:
- Golden Examples veralten schnell, wenn sich das System verändert
- LLM-Evaluation ist teuer (API-Kosten pro Testlauf)
- System könnte das Ändern von Skills entmutigen ("jetzt muss ich auch noch Tests updaten")
- Mitigation: Nur für die 10 wichtigsten, stabilsten Skills; Rest ohne Tests

---

### Option H: Zweistufige Skill-Architektur (Deklarativ + Imperativ)

**Was würde sich verbessern?**
Derzeit sind alle Skills gleichartig: Markdown-Dokumente mit Prosa-Instruktionen. Ein erfahreneres Design würde unterscheiden:

- **Deklarative Skills** (Datentransformationen): Was transformiert wird, ist klar definierbar. Diese könnten formaler spezifiziert werden (Input-Schema → Output-Schema → Transformation-Rules als Prosa). Beispiele: `task-repair-meta`, `requ-assign-packages`.
- **Imperative Skills** (Prozessorchestrierung): Diese koordinieren andere Skills oder treffen komplexe Entscheidungen. Sie bleiben Prosa-Instruktionen. Beispiele: `code-complex`, `product-intake`.

Der Vorteil: Deklarative Skills können maschinell geprüft werden (Input vorhanden? Output korrekt strukturiert?). Imperative Skills brauchen das nicht.

**Aufwand**: L (Kategorisierung + Umbau der ~15 deklarativen Skills)

**Erfolgswahrscheinlichkeit**: mittel

Begründung: Die Kategorisierung ist konzeptuell sauber. Die Umsetzung ist riskant, weil viele Skills auf der Grenze liegen (halb deklarativ, halb imperativ). Eine unklare Kategorisierung führt zu inkonsistenter Anwendung.

**Hauptrisiken**:
- Viele Skills fallen in keine der beiden Kategorien klar rein
- Mitigation: "Mostly deklarativ" vs "Mostly imperativ" als Pragmatismus-Kompromiss

---

### Option I: Skill-Dependency-Graph (Skills als First-Class-Nodes im Factory-Graphen)

**Was würde sich verbessern?**
Derzeit sind Skills Prozessoren, aber sie sind nicht als Nodes im Graphen modelliert. Man weiß: "Flow geht in Requirements rein, Task kommt raus." Aber man weiß nicht maschinell: "Welcher Skill kann ich aufrufen, wenn ich einen approved Flow habe und einen Requirement-Explore-Task brauche?"

Wenn jeder Skill seinen Input und Output formal deklariert (Option B), ergibt sich automatisch ein **Skill-Dependency-Graph**: Eine gerichtete Struktur, die zeigt, welche Skills welche Artefakt-Transformationen leisten. Das ermöglicht:
- Automatisches Routing (claude-route wird zu einem Graph-Traversal statt Heuristik)
- "Was kann ich als nächstes tun?" — Antwort: alle Skills, deren Input-Bedingungen erfüllt sind
- Lückenerkennung: Wenn kein Skill den Übergang von Artefakt A zu Artefakt B macht, ist das eine dokumentierte Lücke

**Aufwand**: XL (setzt Option B voraus; dann M für Graph-Extraktion + L für Routing-Integration)

**Erfolgswahrscheinlichkeit**: niedrig

Begründung: Theoretisch das mächtigste Upgrade — es würde das System von einer "Skill-Bibliothek mit LLM-Routing" zu einem "selbstkartierenden Workflow-System" machen. Praktisch ist es das riskanteste: es setzt voraus, dass alle Skill-Kontrakte korrekt sind (Option B), dass der Graph korrekt traversiert wird, und dass das Routing zuverlässiger als der aktuelle LLM-basierte Ansatz ist. Bei 50 Skills und komplexen Interaktionen ist die Wahrscheinlichkeit für Fehler im Graph hoch.

**Hauptrisiken**:
- Graph-Fehler sind systemische Fehler (kein Failover wenn das Routing falsch läuft)
- Maintenance des Graphen ist aufwändiger als Maintenance von Prosa-Routing
- Mitigation: Als Ergänzung (Suggestions), nicht als Ersatz für LLM-Routing

---

## 3. Empfehlung

### Schicht 1: Sofortige Wins (XS/S Aufwand, hohe Wahrscheinlichkeit)

**Empfehlung 1A — Option E: Skill-Kategorisierung in INDEX.md**
Aufwand: XS. Nutzen: Besseres Routing, weniger Cognitive Load. Risiko: minimal. Dies kann in einem einzelnen Session ohne neues Konzept umgesetzt werden. Es ist der billigste strukturelle Gewinn.

**Empfehlung 1B — Option D: Observability via claude-log Erweiterung**
Aufwand: S. Nutzen: Quantitative Evidenz für `claude-optimize`. Risiko: minimal (additiv). Wenn `claude-log` ohnehin bei jedem Task aufgerufen wird, ist die Erweiterung um Skill-Name und Outcome trivial. Der ROI ist hoch: man beginnt, das System zu messen statt zu schätzen.

### Schicht 2: Mittelfristige Strukturverbesserungen (M Aufwand, mittlere Wahrscheinlichkeit)

**Empfehlung 2A — Option A: Artifact State Machine formalisieren**
Aufwand: S. Nutzen: Validierung von Statusübergängen, konsistentere Berichte. Risiko: niedrig (nur Validierung, kein Breaking Change). Dies ist die natürliche Erweiterung der bereits existierenden Frontmatter-Validierung.

Reihenfolge: Nach Option E und D, weil Observability-Daten zeigen werden, wo Status-Inkonsistenzen am häufigsten auftreten.

**Empfehlung 2B — Option B (Light): Skill-Kontrakte für Kern-Skills**
Aufwand: M (wenn auf 10–15 Kern-Skills begrenzt, nicht alle 50). Nutzen: Maschinell prüfbare Inputs/Outputs. Risiko: mittel (Schema-Drift wenn nicht gewartet).

Empfehlung: Nur die 10 meistgenutzten Skills annotieren. Liste: requ-derive-from-flow, requ-explore, task-create-impl, code-simple, code-complex, ux-create-flow, task-complete, claude-route, product-intake, claude-log. Diese haben den höchsten Hebel und sind stabil genug, dass Schema-Drift beherrschbar ist.

### Schicht 3: Strategische Investments (L/XL Aufwand, niedrige bis mittlere Wahrscheinlichkeit)

**Empfehlung 3A — Option G (Minimal): Snapshot-Tests für Top-5-Skills**
Begründung: Nicht für alle 50 Skills, sondern nur für die fünf, die am häufigsten durch Refactoring betroffen sein werden. Das senkt den Aufwand von XL auf L und macht den probabilistischen Testharness überhaupt erst wartbar.

**Nicht empfohlen (zu riskant/aufwändig für den Nutzen)**:
- Option F (Skill-Konsolidierung): Das Risiko unentdeckter Regressionen übersteigt den strukturellen Gewinn
- Option H (Zweistufige Architektur): Zu viele Skills liegen auf der Grenze
- Option I (Skill-Dependency-Graph): Theoretisch optimal, praktisch zu komplex und zu fragil

### Reihenfolge zusammengefasst

| Schritt | Option | Aufwand | Wann |
|---|---|---|---|
| 1 | E: Skill-Kategorisierung in INDEX.md | XS | Nächste freie Session |
| 2 | D: Observability via claude-log | S | Nach 1 |
| 3 | A: Artifact State Machine | S | Nach 2 (wenn Observability Daten liefert) |
| 4 | B (Light): Kern-Skill-Kontrakte | M | Nach Schicht 1 stabil |
| 5 | C: factory_flows.md generieren | M | Nach B (setzt Kontrakte voraus) |
| 6 | G (Minimal): Snapshot-Tests | L | Nur wenn ein Kern-Refactoring geplant ist |

### Übergreifende Empfehlung

Das System ist strukturell gesund für seine Phase. Es hat die typischen Wachstumsschmerzen eines Expertensystems das organisch entstanden ist — keine katastrophalen Designfehler, aber akkumulierte Komplexität an den Rändern.

**Die wichtigste Erkenntnis für ein LLM-gesteuertes System**: Halte Verbesserungen additiv, nicht substitutiv. Führe niemals einen Skill-Refactor durch, ohne den alten Skill zu archivieren. Führe niemals ein neues Routing-System ein, ohne das alte als Fallback zu behalten. Die Nichtdeterminiertheit von LLMs macht Rückgängigmachen schwieriger als bei klassischen Systemen.

**Die zweite Erkenntnis**: Messen, bevor man optimiert. Option D (Observability) sollte höchste Priorität haben — nicht weil es das drängendste Problem löst, sondern weil es zukünftige Optimierungsentscheidungen von Evidenz statt Intuition abhängig macht. Aktuell ist `claude-optimize` ein LLM das subjektiv Patterns erkennt. Mit Telemetrie-Daten wird es zu einem LLM das über Metriken nachdenkt.
