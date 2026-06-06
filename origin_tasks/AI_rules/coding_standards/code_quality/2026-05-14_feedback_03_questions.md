# Antworten / Rückfragen zu `2026-05-14_feedback_03.md`

Plus K-Restructure (was vorher als "in nächster Runde" markiert).

---

## Allgemeines 1 — Redesign zu permanent loop-task

### Konzept verstanden, applied

Dein Modell ist klarer als meines: **ein permanent task** mit generic question.md, der nur "wende die Entscheidungen aus answer.md an" macht. Kein separater Review-Task der die question.md erst schreibt. Die Entscheidungs-Materie selbst lebt in `scripts/quality/proposals/<kategorie>/` Dateien, die der Nutzer direkt liest.

### Geändert

**TASK-PROC-046-13 komplett neu geschrieben** mit:

- **Permanent loop-task** unter `tasks/2026-05-14_impl_apply-quality-rule-proposals-loop/`, niemals via `(completed)` umbenannt.
- **Generic permanent question.md** in `automation/pending_feedback/<LOOP_TASK_ID>/question.md` (statt per-Runde geschrieben). Inhalt verweist nur auf `scripts/quality/proposals/<kategorie>/` und das Format der answer.md — keine Duplikation des Inhalts der einzelnen Proposal-Dateien.
- **Reset-Skript** `scripts/quality/reset_proposals_loop.py` — re-creates `pending_feedback/<LOOP_TASK_ID>/` aus den Templates nach jedem Lauf (orchestrator hat den Ordner vorher zu `answered_feedback/<TASK_ID>/timestamp_*/` verschoben). Reset cleart Session-ID, setzt status zurück auf pending, schreibt fresh Q&A. Audit-Trail bleibt erhalten in `answered_feedback/` plus git commits.
- **status: pending** (nicht "active") — Project's task-lifecycle kennt kein `active`-Status für Tasks; `pending` + nicht-leere answer.md ist exakt das was Orchestrator als "ready to resume" sieht. Keine Orchestrator-Änderungen nötig.
- **CLAUDE.md / task-complete update**: AI Agents werden verpflichtet, Proposals zu filen wenn sie Rule-Improvement-Opportunities sehen; Goodhart-Schutz bleibt (kein autonomes Gate-Edit).

Detail-Spec für die Proposal-Dateien (YAML frontmatter + Body-Sections) hat sich gegenüber feedback_02-Version nicht geändert.

### Kein neuer Successor-Task pro Runde

Du hattest beide Optionen offen gelassen. Ich bin mit deiner Empfehlung mitgegangen: **Option B (reset-Skript)**, weil:
- task-complete coupled mit commit ist und das Entkoppeln schwierig ist.
- Das Reset-Skript ist sauber und konzeptuell einfach (re-create Q&A files aus Templates).
- Audit-Trail bleibt erhalten (orchestrator archiviert nach `answered_feedback/`).

### Keine offenen Fragen für Allgemeines 1.

---

## A — Scripts als SPOT, Verlinkung von Requirements + Design-System auf Scripts

### Verstanden, applied

Die Skripte sind die SPOT für die *machine-checkable* Regeln. Die Requirements und Design-System-Dokumente verweisen auf sie, damit der Agent, der Code schreibt, weiß *wo* die Regeln im Detail definiert sind.

### Geändert

**REQ-NFUNC-002 §11.5 hinzugefügt** ("Relationship to the Pushback / Quality-Gate Mechanism"):

- Verweist auf REQ-PROC-046 AC-07 als die Stelle, die diese ACs als Gates promotet.
- Bidirektionalitäts-Hinweis: neue ACs hier erweitern automatisch das Gate-Set; aber auch — die Skripte können *feinere* Detection-Rules definieren, die nicht in den ACs erwähnt sind. **REQ-NFUNC-002 allein ist NICHT Single-Point-of-Truth** — das gemeinsame Lesen von Requirements + Scripts + Doc-Guidelines ist die volle Vertrag-Definition.
- AI agents writing UI code: read REQ-NFUNC-002 first, reference `scripts/quality/check_*.sh` for byte-level verification.

**REQ-PROC-046 Developer Guidelines**: neuer Bullet zur Gegenrichtung:

> The gate-set may detail rules beyond the acceptance-criteria of the requirements it enforces. A requirement (e.g. REQ-NFUNC-002 accessibility) states the intent at AC granularity; the actual analyzer rules, grep scripts, and threshold values in `analysis_options.yaml` and `scripts/quality/check_*.sh` may add finer-grained detection (e.g. AC-15 keyboard navigation in REQ-NFUNC-002 is enforced by a specific `tester.sendKeyEvent(LogicalKeyboardKey.tab)` test pattern that the AC text does not enumerate). **Neither side alone is the single point of truth** — the requirement is the *what*, the gates are the verifiable *how*, and the `doc/` guidelines fill the judgment band between them. When a rule in the gate set conflicts with the intent of a requirement, the requirement wins and the gate is corrected.

### A.2 — bidirektionale Sync-Pflicht beim Erweitern

Du schriebst: "sobald man neue Regeln aufstellt, muss das im Pushback-Mechanismus entsprechend auch eingetragen werden". Das ist jetzt explizit in §11.5 und im Developer-Guidelines-Bullet dokumentiert. Workflow:

- Neue AC in REQ-NFUNC-002 → REQ-PROC-046 AC-07 picks it up via "active set" reference → `verify-quality` (TASK-PROC-046-11) sees the new AC on next run.
- Neue Detection-Rule in `scripts/quality/check_*.sh` ohne korrespondierende AC → der Vorschlag flowt über `scripts/quality/proposals/grep_gates/` (Allgemeines 1 channel) und wenn akzeptiert wird der `# Why:`-Kommentar auf das Script die Referenz auf den Originating-Reason festhalten.

### A.3 — Form-Assistance ist abstrakt, soweit ok

Bestätigt. Konkrete Regeln für Undo / Recovery folgen wenn solche Features kommen. Aktuell ist die AC-17-Formulierung "passt".

### Keine offenen Fragen für A.

---

## E — Tagging only, no archival logic

### Verstanden, applied

Nur das Tagging — Archival kommt später bei Bedarf.

### Geändert

In **TASK-PROC-046-13** ist das `proposed_by_model:` Feld als mandatory in der Proposal-Frontmatter dokumentiert (Part A). Das ist das gesamte E-Update für diese Runde: Modell-Identifier + Datum werden ab jetzt mit jedem Proposal gespeichert. Die Archival-Logik bleibt als Future-Capability dokumentiert; kein Task für die Logik selbst.

Für `doc-update-guidelines` Captured-Marker (E im feedback_02 vorgesehen): das ist eine kleinere Skill-Änderung; ich schedule sie nicht jetzt, sondern füge es zu den Open-für-Backlog Punkten unten.

### Keine offenen Fragen für E.

---

## K-Restructure — DCM raus, very_good_analysis rein

(War aus feedback_02 für diese Runde versprochen; jetzt ausgeführt.)

### TASK-PROC-046-03 komplett neu geschrieben

Scope-Wechsel:

- Baseline: `flutter_lints` → **`very_good_analysis`** (188 rules vs 101; MIT-OSS).
- Hinzu: **`bloc_lint`** (purely additive BLoC rules) und **`clean_architecture_kit`** (medium-FP naming-heuristic für Architecture-Layer-Detection).
- Komplett raus: das gesamte `dart_code_linter:` Block in `analysis_options.yaml` plus die `dart_code_linter` dev-dep. Verloren damit: `prefer-correct-type-name`, `avoid-banned-imports`, `avoid-dynamic`, `no-object-declaration`, `avoid-global-state`, `ban-name`, alle Flutter-perf DCM rules (`avoid-unnecessary-setstate` etc.), und die Komplexitäts-Metriken.
- **Effort: M → L** wegen Volumen der zu fixenden Violations beim Baseline-Switch.

### Neue Task TASK-PROC-046-14 erstellt für custom DCM-free Ersatzskripte

Sechs neue Skripte unter `scripts/quality/`:

1. `check_complexity.py` (+ Dart-Helper unter `_complexity_analyzer/`): nutzt `package:analyzer` für AST-Parsing, emittiert JSON mit cyclomatic / params / SLOC / nesting per function. Thresholds: ≤ 20 / ≤ 4 / ≤ 50 / ≤ 5 (carried over).
2. `check_type_naming.sh`: grep + regex für `*Bloc`, `*Repository`, etc. Suffix-Convention.
3. `check_architectural_imports.sh`: per-path-glob deny-import Policy (domain → no Flutter, features → no direct material.dart, etc.). Policy externalised in `architectural_imports_policy.yaml`.
4. `check_no_direct_styling.sh`: grep `lib/features/` für `ButtonStyle\(`, `TextStyle\(`, `Color\(`, `Colors\.`, `ThemeData\(`. Erlaubt nur in `lib/core/design_system/`.
5. `check_test_smells.sh`: missing-assertion + empty-group + literal-expect heuristics über `test/` und `integration_test/`.
6. `check_folder_taxonomy.sh` (K.2 expliziter Wunsch): walks `domain/` folders, enforces allowed sub-folders. Allowlist externalised in `folder_taxonomy_allowlist.txt`.

Plus: `check_quality_gates.sh` entry-point updated, `README.md` updated, `verify-quality` skill (TASK-PROC-046-11) updated to invoke + parse these.

### K.1 — WHY-Kommentare an jeder Regel

Folded into TASK-PROC-046-03 Part C. Jede aktive Regel in `analysis_options.yaml` bekommt einen `# Why: ...; Source: ...` Kommentar. Format-Beispiel im Task:

```yaml
linter:
  rules:
    # Why: domain layer integrity — unhandled Futures in the data path silently
    # lose mental-health entries on slow eMMC storage when the process is killed.
    # Source: REQ-PROC-046 AC-05; PERSONA-004 zero-data-loss.
    unawaited_futures: true
```

Nur die *non-obvious* Regeln bekommen `Why:` Kommentare (project-specific Begründungen). Pure-Stilregeln, die VGA aus rein-ästhetischen Gründen aktiviert, werden nicht kommentiert — VGA's eigene Doku ist Authority dafür.

### K.1 Antwort auf `avoid-dynamic` / `no-object-declaration`

Diese sind **Type Safety, nicht Performance**. `dynamic` schaltet statische Typprüfung aus → Runtime-Fehler statt Compile-Time. Performance ist Nebeneffekt (Analyzer kann nicht optimieren).

Für JSON-Deserialisierung: `Map<String, dynamic>` aus `json.decode` ist als *Grenzfall* akzeptabel; sofort zu typisierten Objekten casten, `dynamic` nicht in Business-Logic-Code leaken.

VGA hat `avoid_dynamic_calls` (etwas enger: catches calls auf dynamic, nicht Variable-Deklarationen). Das ist nahe genug an dem, was DCM's `avoid-dynamic` machte. Die Lücke landet in `doc/` Guidelines.

### K.2 — Folder Taxonomy Script bestätigt drin

In TASK-PROC-046-14 als Skript Nr. 6. Externalisierte Allowlist erlaubt Erweiterung ohne Skript-Change.

---

## Status der Runde

**Erledigt in dieser Runde**:
- Allgemeines 1 redesign: permanent loop-task + reset-Skript (TASK-PROC-046-13 komplett neu geschrieben)
- A.2: bidirektionale Refs in REQ-NFUNC-002 §11.5 + REQ-PROC-046 Developer Guidelines
- A.3: passt — keine Aktion nötig
- E: nur Tagging applied (in TASK-PROC-046-13 Proposal-Frontmatter), Archival deferred
- **K-Restructure komplett**:
  - TASK-PROC-046-03 komplett neu geschrieben (VGA baseline + bloc_lint + clean_architecture_kit, keine DCM, WHY-Kommentare an Regeln)
  - TASK-PROC-046-14 erstellt (6 custom replacement scripts für DCM-Funktionalität)

**Offene Fragen aus früheren Runden (immer noch offen)**:
- A.1 (English readability metric mapping — gilt erst wenn Englisch-Localisation kommt)
- A.2 — Plan Evaluation Tasks haben aktuell keine accessibility ACs; sie sind blocked auf einen fehlenden Flow. Sobald sie unblocked sind, fängt AC-07 sie automatisch.
- Allgemeines.1 (review-task cadence) — *jetzt obsolet* durch das Redesign zu permanent loop-task; antwortet sich selbst.
- E.3 (model-version archival logic) — explicit deferred per dein feedback_03 E.

**Backlog (nicht für nächste Runde, aber notiert)**:
- `doc-update-guidelines` skill update für `<!-- Captured: ... -->` HTML-Kommentar mit Model-ID + Datum + Source-Task — kleine Skill-Änderung; warten bis es einen konkreten Anlass gibt.
- Periodischer Trigger für TASK-PROC-046-13 loop-task (z.B. pre-release auto-fire). Aktuell developer-manual triggered.

**Was ich JETZT bereit bin zu starten**:
- TASK-PROC-046-03 (Baseline-Switch + Violation Cleanup) — über `code-complex`, da Dart-Code-Edits substanziell.
- TASK-PROC-046-13 (Proposals-Loop bauen) — kein code-complex (scripts + skill update).
- TASK-PROC-046-14 (custom replacement scripts) — kein code-complex (scripts only; Dart-Helper ist isoliert).

Wenn du grünes Licht gibst (oder eine andere Reihenfolge willst), lege ich los. Ansonsten warte ich auf weiteres Feedback.
