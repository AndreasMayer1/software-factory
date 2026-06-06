# Plan: Flexibler Requirements Writer Modus

**Datum:** 2025-10-09

**Ziel:** Anpassung des `requirements-writer`-Modus, um sowohl einen detaillierten Implementierungsmodus als auch einen explorativen Modus zu unterstützen.

---

## 1. Anpassung des Workflows (`1_workflow.xml`)

-   **Neue Phase "Mode Selection":** Eine neue erste Phase wird eingeführt.
    -   **Aktion:** Stellt dem Benutzer die Frage: "Soll eine detaillierte Implementierungsaufgabe definiert werden (Implementation Detail Mode) oder soll zunächst eine Idee exploriert und Informationen gesammelt werden (Explorative Mode)?"
-   **Logische Verzweigung:**
    -   **Pfad A (Implementation Detail):** Führt die bestehenden Phasen (`Context Gathering`, `Decomposition`, `Detailed Specification`, `Iterative Refinement`) aus.
    -   **Pfad B (Explorative):** Führt einen neuen, vereinfachten Workflow aus, der sich auf Informationssammlung, Analyse und die Erstellung eines Ergebnisberichts konzentriert.

## 2. Namenskonvention für Tasks

-   Einführung einer klaren Namenskonvention für Aufgabenordner, um den Modus direkt im Dateisystem sichtbar zu machen.
-   **Konvention:**
    -   `[YYYY-MM-DD]_impl_[name of the task]/`: Für Aufgaben im "Implementation Detail Mode".
    -   `[YYYY-MM-DD]_explore_[name of the task]/`: Für Aufgaben im "Explorative Mode".

## 3. Aktualisierung der Dokumentation

-   Die neuen Modi und die Namenskonvention müssen in den zentralen Regelwerken dokumentiert werden, um Konsistenz zu gewährleisten.
-   **Betroffene Dateien:**
    -   `.clinerules`
    -   `.roo/rules-requirements-writer/3_requirement_structure.md`

## 4. Todo-Liste zur Umsetzung

-   [x] Plan zur Anpassung des `requirements-writer`-Modus erstellen und vorschlagen
-   [ ] `1_workflow.xml` anpassen, um eine Modus-Auswahl (explorativ vs. implementierend) zu ermöglichen
-   [ ] `.clinerules` aktualisieren, um die neue Namenskonvention für Tasks (`impl_` vs. `explore_`) zu definieren
-   [ ] `3_requirement_structure.md` aktualisieren, um die neuen Modi und die Namenskonvention zu dokumentieren
-   [x] Den finalen Plan in einer `plan.md`-Datei im Aufgabenverzeichnis speichern