# Questions / responses to `2026-05-14_feedback_02.md`

Same workflow as last round: I process each item, adapt the documents, and append open questions here. Sections marked **(not yet processed)** are still in flight.

---

## Allgemeines 1 — Sammelort für Verbesserungsvorschläge an den Skript-Regeln

### Design (based on research findings in `2026-05-14_research_automation_and_self_regen.md`)

**Wo sammeln**: neben den Regeln, nicht im Task-Ordner. Konkret unter `scripts/quality/proposals/<kategorie>/` mit Unterordnern:

- `analysis_options/` — Vorschläge für Analyzer-Config-Änderungen
- `grep_gates/` — Vorschläge für `scripts/quality/check_*.sh` Änderungen
- `thresholds/` — Schwellwert-Änderungen (Mutation %, Coverage %, Komplexität)
- `new_gates/` — komplett neue Gates

**Datei-Format**: eine Markdown-Datei pro Vorschlag, Dateiname `<YYYY-MM-DD>_<slug>_<source_task_id>.md`. YAML-Frontmatter mit `proposal_type`, `proposed_at`, **`proposed_by_model`** (genaues Modell-Identifier — beantwortet auch E.2), `source_task`, `status: pending_review | accepted | rejected | superseded`. Body: Reason / Proposed change / Expected effects / Alternatives considered.

**Wie hineintragen**: die AI legt die Datei direkt an, wenn sie während normaler Arbeit eine Verbesserungsmöglichkeit sieht. CLAUDE.md wird so erweitert, dass AI-Agenten dazu verpflichtet werden. Kein Autonomic-Edit der Gates — strikt: nur Vorschlag.

**Review-Task (self-regenerating)**: ein generischer Task `<date>_explore_review-quality-rule-proposals`, der per Aufruf alle pending Proposals einsammelt → `automation/pending_feedback/<TASK_ID>/question.md` schreibt mit allen offenen Entscheidungen → Session terminiert. Wenn du `answer.md` ausgefüllt hast: Session resumed, akzeptierte Proposals werden zu impl-Tasks via `task-create`, der Review-Task legt sich selbst neu an (Pattern aus `scripts/tasks/create_orchestration_task.py` mit `fcntl.flock` Duplicate-Guard).

### Geschaffen

**TASK-PROC-046-13** (impl, urgency 3, effort M, `after: [TASK-PROC-046-11]`). Goal.md beschreibt:

- Die vier Subordner unter `scripts/quality/proposals/` + jeweilige READMEs.
- Den Proposal-Datei-Format-Spec.
- Das `scripts/quality/create_proposals_review_task.py` Skript (modelliert auf `scripts/tasks/create_orchestration_task.py` Zeilen 191–241).
- Den Review-Task goal.md Template.
- Den CLAUDE.md / Skill-Update der AI-Agenten verpflichtet, Proposals zu filen.
- Ende-zu-Ende Smoke-Test als AC.

### Offene Frage

**Allgemeines.1 — Initiale Cadence des Review-Tasks.**

Aktuell ist der Task developer-manual triggered (Self-Regeneration aktiv, aber ohne periodischen Trigger). Soll er auch periodisch automatisch gefiltert werden — z.B. nach jedem N completed Tasks, oder einmal pro Release-Cycle? Mein Vorschlag: erstmal nur manuell + bei Release-Vorbereitung automatisch. Akzeptabel?

---

## Allgemeines 2 — Automation Q&A details documented at single point of truth

### Befund

Der Automatismus ist klar dokumentiert in `.claude/skills/claude-automated-mode/skill.md` Zeilen 76–139. **Das ist die kanonische Quelle.** Die Skripte sind:

- `scripts/automation/orchestrate.py` (Orchestrator)
- `scripts/tasks/is_awaiting_answer.py` (Per-Task-Check)
- `scripts/tasks/next_tasks.py:load_pending_feedback_ids` (Queue-Filter)
- `scripts/automation/terminate_session.sh` (Session-Terminierung)

Die Templates: `automation/pending_feedback/TEMPLATE_question.md` und `TEMPLATE_answer.md`. Live-Beispiel: `automation/pending_feedback/TASK-PROC-006-02/question.md`.

### Pre-session Q&A — bestätigt unterstützt

**Wichtig für unseren Fall**: ein Task kann mit pre-populierter `question.md` ins Repo gelegt werden BEVOR jemals eine Session darauf gelaufen ist. Voraussetzung: `session_id: NEW_SESSION_REQUIRED` (Sentinel, vom Orchestrator akzeptiert) und `account: <valid>`. Der Orchestrator findet das `goal.md` via `grep -rl "^task_id: <id>" requirements_tasks --include=goal.md` und startet eine frische Session mit dem Answer als Prompt-Kontext. `next_tasks.py` und `is_awaiting_answer.py` schließen den Task aus der Queue aus, bis `answer.md` ausgefüllt ist — exakt das "blocked, awaiting answer"-Verhalten, das du willst.

### Anwendung auf die Tasks die wir bauen

Alle Tasks die Nutzer-Entscheidungen brauchen BEVOR sie laufen können:

- **TASK-PROC-046-13** (Allgemeines 1) selbst hat keine pre-session-Fragen — startet sauber.
- Tasks die aus dem Review-Mechanismus entstehen (akzeptierte Proposals → neue Impl-Tasks) können bei Bedarf mit `session_id: NEW_SESSION_REQUIRED` + pre-populierter question.md angelegt werden, wenn die Implementierung Entscheidungen braucht.

### Single-Point-of-Truth-Referenz

In jedem Task der den Q&A-Mechanismus nutzt: Pfad-Referenz auf `.claude/skills/claude-automated-mode/skill.md` Zeilen 76–139 und auf die Templates. Habe ich bereits in TASK-PROC-046-11 und TASK-PROC-046-13 so eingebaut. Wenn sich der Mechanismus ändert, ändert sich nur die Skill-Datei — die Tasks referenzieren, nicht duplizieren.

### Keine offenen Fragen für Allgemeines 2.



---

## A — Accessibility

### Confirmed → applied

- **Target audience**: Einfache Sprache (your call confirmed; Leichte Sprache rejected as too restrictive for the personas).
- **Metric (German)**: Wiener Sachtextformel via local Python script (`scripts/quality/check_text_readability.py` — to be written by a later task).
- **Threshold**: ≤ 8 (Einfache Sprache norm), flag-for-review during initial calibration, blocking after baseline.
- **REQ-NFUNC-002 updated** with these confirmed values in AC-14 and a rewritten §3.7.

### New ACs added to REQ-NFUNC-002 from your feedback

- **AC-15 keyboard navigation** (Windows / macOS / Android-with-keyboard): Tab traversal, focus indicator, modal focus management, action keys (Enter/Space/Esc/arrows). MVP. Verified by integration test. → §3.8.
- **AC-16 component semantics**: button vs. link vs. form-field role correctness. Screen reader announces the right thing. Widget tests assert `SemanticsFlag.isButton` / `.isLink` / etc. → §3.9. *(This addresses your "grundlegende Dinge wie die richtigen Komponenten zu verwenden" — yes, scriptable: widget tests assert the `Semantics` flags.)*
- **AC-17 form assistance**: auto-complete suggestions where applicable (system-fields via `autofillHints`, domain-fields via recently-used lists); validation hints only after invalid input, naming the allowed range, with recovery path. → §3.10.
- **AC-18 audio (placeholder)**: when audio is introduced, every audible signal must have a non-audio equivalent. Not enforced today; recorded so the gate auto-activates when an audio feature lands. *(This is your "Vermerk schreiben für die Zukunft" applied to a specific AC.)*

### Accessibility-task summary report (from the Sonnet agent you asked me to run)

Findings recorded in `2026-05-14_accessibility_task_summary.md`. Headlines:

- **3 of 7** tasks make explicit accessibility commitments. All 3 are QR-transfer; all 3 cover only motion-safety (WCAG 2.3.1 / Reduce Motion).
- **The two Plan Evaluation tasks** (TASK-FUNC-005-04, -005-05) name **zero** REQ-NFUNC-002 ACs despite being the largest interactive surface in the codebase. They are currently `blocked` pending a missing user-flow.
- **TASK-PROC-046-07 and -08** (the inventory + backfill creator) committed only to the **four built-in `AccessibilityGuideline` checks** — that's now insufficient given AC-07's promotion to the full REQ-NFUNC-002 active set.
- **Most common gaps across the task set**: text scaling (6/7 missing), AA contrast (6/7), non-tap semantic labels (5/7), focus / screen-reader navigation (5/7).

### Actions taken from the agent's findings

- **TASK-PROC-046-08** (widget-test backfill creator) scope updated to require every created backfill task to enumerate the *full active AC set* its screen falls under — not just the four built-ins. The 2026-05-14 report is cross-referenced from the goal.md so the implementer reads it.
- The Plan Evaluation gap is **not** addressed by me directly here because those tasks are blocked on a missing user-flow. When the flow lands and the tasks unblock, REQ-PROC-046 AC-07's gate will fire on them automatically.

### Open questions for you

**A.1 — English readability metric mapping.**

Wiener Sachtextformel is German-specific. The candidate English metrics: Flesch–Kincaid Grade Level (US standard), Flesch Reading Ease (inverse — higher easier). Rough mapping: Wiener 8 ≈ Flesch–Kincaid 8 ≈ Flesch Reading Ease 60–70. The threshold for English would land in that band. I've recorded this as "to be confirmed when English localisation is introduced" in §3.7. Acceptable?

**A.2 — Screen-reader basics now vs. fully retrofittable.**

I went with the "scriptable basics now" route (AC-16 component semantics) and left advanced screen-reader flow (focus order optimisation, custom announcements, `MergeSemantics` grouping) in Phase 2 per REQ-NFUNC-002 §4.2. Your message read: "Für Screenreader Support haben wir, glaube ich, gesagt, wir erkennen das später." Acceptable that the *basics* are MVP and the *polish* is Phase 2?

**A.3 — Error recovery vs. "abstract" complaint.**

You wrote *"Fehler Recovery ist natürlich auch wichtig. Das ist allerdings natürlich auch recht abstrakt. Dann drauf an, ne? Weiß ich nicht, ob du da jetzt schon Regeln aufstellen kannst, konkret."* — I went concrete in AC-17: invalid input does not destroy other field state; user can clear / undo / re-enter without losing the rest. That's a verifiable rule for forms specifically. Sufficient, or do you want it loosened back to a guideline?

---

## B — Two-checkpoint rule for gate-set changes

### Confirmed → applied

**Two checkpoints, yes.** Your model: ideas accumulate where the rules are defined (not in the task folder); user reviews them; for those to be implemented, an answer file is created in `automation/pending_feedback/[task-id]/`; the implementing session adapts the rules; before completing, the session asks again for user confirmation.

This depends on the Q&A automation mechanism and the self-regenerating-task pattern — both being researched by the running agent. **I'll finalize B's implementation (the generic improvement-task, the idea-collection location and structure) once the research agent returns.**

### B.2 — Confirmed

Sequential ordering of doc-audit / key-storage-audit / test-hygiene-audit. Will encode `after:` chains accordingly when I revisit the audit tasks.

### Carry-over

The B-related changes (rules location, generic recurring improvement-task, model-version + date tagging on ideas — see also item E.2) will be batched after the research agent's report lands.

---

## C — Flutter performance, no heuristics

### Confirmed → applied

**No heuristic gates.** Patterns that aren't lint-checkable stay in `doc/presentation/coding/best_practices.md` and `quality-checker` reads them. Specifically the six items I listed under "Things considered but not yet gated" in the previous round (`RepaintBoundary` placement, `ListView.builder` usage, image caching off-main-isolate, BLoC selector granularity, lazy init, defer-to-idle) all move to `doc/` — no scripts will be written for them.

I will revisit `doc/presentation/coding/best_practices.md` (or have an implementation task do it) to ensure these patterns are documented there explicitly. Not done in this round.

### C.2 — Confirmed

Galaxy A40 only needs to be plugged in per release-candidate, not continuously. **G7 dynamic stays per-release-candidate cadence.** No change needed — that was already the spec.

---

## D — *(already addressed in last round; no new feedback)*

---

## E — doc/ size discipline + model-version tagging

### E.1 — Confirmed

Accept the existing cadence (REQ-PROC-048 auto-split tasks). No change.

### E.2 — Model version + date tagging on captured patterns

This is a new capability you raised. The mechanism: when `doc-update-guidelines` writes a pattern into `doc/`, the pattern is tagged with the model version and date that authored it.

**Proposed format** (to add to `doc-update-guidelines` skill output convention):

```markdown
## [Pattern Title]

<!-- Captured: 2026-05-14 by claude-opus-4-7 (via doc-update-guidelines from TASK-PROC-XXX-YY) -->

[pattern body]
```

In the future, an archival sweep can grep for old `Captured:` metadata and propose archiving patterns older than X months that haven't been touched since.

**Plumbing required:**

- The `doc-update-guidelines` skill is updated to include the `Captured:` HTML comment with: date, model identifier (e.g. `claude-opus-4-7`), source task ID.
- Model identifier is read from the running environment. Each major LLM (Claude, ChatGPT, Gemini) exposes its model string differently — for Claude Code, the model is set per session and visible in the environment.

**This is a small skill update; I won't make it now since I haven't read the current `doc-update-guidelines` skill yet. It's a candidate impl task** — let me know if I should schedule it.

### Open question

**E.3 — Where lives the archival logic?**

Once tagging is in place, you'll want a future task that does the archival sweep. Two homes:

1. **A new periodic task** (e.g., quarterly) that walks `doc/` for old `Captured:` markers and proposes archiving.
2. **Folded into the existing REQ-PROC-048 auto-split mechanism** — same script that splits oversized files also archives stale patterns.

My recommendation: **(1)** — different concern, different cadence, different action (split vs. archive). Keep separate.

Want me to schedule both the tagging update and the archival task, or just the tagging update for now?

---

## F — Integration tests

### F.1 — Confirmed

Single-process simulation for the data-transfer pipeline. Two-device manual testing on your side covers the optical path. **TASK-PROC-002-08's scope updated to drop the two-process pattern** and document single-process as the chosen approach.

### F.2 — Confirmed

Integration tests scheduled at the end of the work. **TASK-PROC-002-08 priority / urgency lowered** so `next_tasks.py` ranks it after the per-change gates land.

### F.3 — Integration tests as non-functional epic

### Befund (aus dem Research-Agent)

**`requ-derive-from-flow` ist die richtige Stelle.** Begründung aus dem Bericht §6:

- Liest bereits jeden flow.md (Phase 1.3)
- Hat in Phase 2 eine Opus-getriebene Gap-Matrix mit Status-Werten (`exists_complete`, `new_needed`, etc.)
- Emittiert in Phase 4.2 `type: explore` goal.md Dateien für non-functional Pfade
- Wird zum richtigen Zeitpunkt aufgerufen (früh im Per-Flow-Lifecycle, BEVOR Impl-Tasks geschrieben werden)

`release-begin-impl-finalize` wäre falsch — käme zu spät, alle Impl-Tasks existieren dann schon und Integration-Test-Requirements könnten nicht mehr informieren, was die Tasks bauen.

### Geschaffen

**TASK-PROC-002-09** (impl, urgency 2, effort M). Goal.md beschreibt die surgische Erweiterung von `.claude/skills/requ-derive-from-flow/skill.md`:

1. **Phase 2 Gap-Taxonomie** (Zeile 267 area): neuer Status `integration_test_needed` ergänzt.
2. **Phase 2 Opus-Matrix-Instruktion** (Zeile 261 area): "Für jeden Flow genau eine Matrix-Zeile mit Status `integration_test_needed` emittieren, gezielt auf `requirements_tasks/non-functional/integration_tests/<flow_id>/`, AUSSER ein solches Requirement existiert schon (dann `exists_complete`)."
3. **Phase 4.2 goal.md Template-Variante** für Integration-Test-Zeilen mit Scope-Text "Define what integration-test coverage this flow requires: happy path through every primary scenario step; each exception path; the boundary conditions...".
4. **Phase 4.2 Suggested-Package-Regel**: Integration-Test-Zeilen bekommen das gleiche `target_package` wie der primäre funktionale Gap des Flows — Integration-Tests shippen mit den Features die sie testen.
5. **Bootstrap**: einmaliges Anlegen von `requirements_tasks/non-functional/integration_tests/requirements.md` als Epic-Container (`REQ-NFUNC-*` ID via `allocate_req_id.py`).

### Wirkung in der Praxis

Wenn du das nächste Mal `requ-derive-from-flow` auf einen Flow laufen lässt, wird automatisch eine Integration-Test-Requirement-Zeile in der Matrix sichtbar. Die Bewertung "brauchen wir das?" passiert im Phase-3-Review zusammen mit den anderen Gaps. Das `target_package` matched dem funktionalen Gap, also landen Integration-Test-Requirements im gleichen Release wie das Feature.

### Keine offenen Fragen für F.3.



---

## G — Native (non-Dart) code

### G.1 — Confirmed

Follow recommendation: defer custom native linting (clang-tidy / ktlint / SwiftLint) until custom-native LOC crosses a threshold. The existing grep gates (SP1, SP3, SP4) still apply to native files at the pattern level.

### G.2 — Confirmed: native code is in `packages/`

Good — that means it's source-controlled in this repo and the grep gates can scan it as-is. **TASK-PROC-052-01 scope updated** to scan `packages/` as a native-code path. **REQ-PROC-052 §When Applies** updated to list `packages/` explicitly.

---

## H — Question file (not escalation file)

### Du hattest recht — kompletter Mechanismus-Fix

Mein vorheriger Vorschlag mit `escalation_[timestamp].md` war falsch. Der Automatismus erwartet exakt `question.md` und `answer.md` mit dem Template-Schema unter `automation/pending_feedback/TEMPLATE_*.md`. Sonst funktioniert der Resume-Mechanismus nicht (`scripts/automation/orchestrate.py:find_answered_feedback` erkennt nur diese Dateinamen).

### Geändert

**REQ-PROC-046 §Back-Pressure Protocol Step 4** komplett neu geschrieben:

- Datei: `automation/pending_feedback/<TASK_ID>/question.md` (nicht `escalation_*.md`)
- YAML-Frontmatter verbatim aus `automation/pending_feedback/TEMPLATE_question.md`:
  - `task_id`, `session_id` (UUID oder `NEW_SESSION_REQUIRED`), `account`, `status: awaiting_answer`, `asked_at`, `skill: verify-quality`
- Body: free-form Markdown, Vorschlag-Sections aus dem TASK-PROC-006-02 live example (Where this task is / Gates still failing / Cycle log / Suspected root cause / Decisions D1/D2/... mit Proposal/Alternative/Your answer / How this task closes)
- Companion: `answer.md` als verbatim copy von `TEMPLATE_answer.md` mit `<!-- AWAITING_HUMAN_ANSWER -->` Sentinel — AI schreibt NICHT in answer.md (das ist explizit verboten im Template)
- Termination: `bash scripts/automation/terminate_session.sh`
- Resume: orchestrator detektiert non-template answer.md → `claude --resume <session_id> -p <answer-content>` ODER `run_fresh_session_with_answer` falls `NEW_SESSION_REQUIRED`. Cycle-Counter resettet sich im resumed session.

**TASK-PROC-046-11 §Layer 2 (verify-quality skill)** ebenfalls neu geschrieben — referenziert exakt das `claude-automated-mode/skill.md` Zeilen 76–139 als Verfahrens-Wahrheit und alle Orchestrator-Skript-Pfade.

### H.1 — Konfirmiert

Datei lebt **nur** in `automation/pending_feedback/<TASK_ID>/`. Kein Hardlink oder Copy ins Task-Verzeichnis. Stattdessen Pfad-Referenz im goal.md. So sind du und der Orchestrator immer auf derselben Quelle.

### H.2 — Konfirmiert

Cycle-Counter reset to 0 on resolution. User-Trust-Default.

### H.3 — Konfirmiert + neue Frage

`task_id` im question.md = der Child-Task (wo die Verletzungen wohnen). Bestätigt.

**Deine neue Frage zu parallelen Implementations-Tasks:**

Szenario: Task A startet, hits 5-cycle cap, schreibt question.md → Session terminiert. Du startest stattdessen Task B (komplett unabhängiges Feature). Wird Task B's Pushback funktionieren?

**Antwort: ja, vollständig isoliert.** Der Pending-Feedback-Mechanismus ist task-scoped:

- Task A's `question.md` liegt in `automation/pending_feedback/<TASK_A>/`. Der Orchestrator's `find_answered_feedback` walkt alle Subfolder; Task B kümmert das nicht.
- `next_tasks.py:load_pending_feedback_ids` ist auch task-scoped; Task A wird aus der Queue ausgeschlossen, Task B nicht.
- Cycle-Counter pro Task im jeweiligen `plans_and_protocols/cycle_state.json` (oder analog) — kein geteilter Zustand zwischen Tasks.

Das einzige geteilte Konzept ist die **Session UUID**. Aber Task A's Session terminiert, bevor Task B gestartet wird. Wenn du Task B startest, allokiert der Orchestrator eine neue Session UUID. Task A bleibt mit seinem alten session_id im question.md liegen, bis du die Antwort schreibst → wird mit `claude --resume <task_a_session>` separat resumed. Keine Interferenz.

**Edge case**: was wenn Task B *auch* in den 5-cycle cap läuft? Dann hast du zwei separate `pending_feedback/<TASK_*>/` Ordner und zwei separate question.md Dateien. Du kannst sie in beliebiger Reihenfolge beantworten. Wenn der Orchestrator beide answer.md erkennt, wird er beide resumed (in deterministischer Reihenfolge, geguarded durch `fcntl.flock` gegen Race Conditions per `scripts/tasks/create_orchestration_task.py` lines 309–319). Keine offene Frage.

---

## I — Pitfall countermeasures

### I.1 — Konfirmiert

Mechanical helper extraction bleibt judgment-only. quality-checker liest den Diff, flag suspicious mass-extraction. Keine Heuristik-Gate.

### I.2 — Monitoring von Test-Code-Löschungen

Dein Vorschlag aufgreifen: Mutation-Test-Skripte schreiben Logs, Logs in git versioniert, bei jedem Lauf gelöscht und neu geschrieben → Veränderungen via `git log` sichtbar.

Plus deine Sorge: Refactoring löscht/ersetzt Zeilen → würde das System ständig eskalieren?

**Mein Refinement**: das Skript loggt *Surviving-Mutant-Counts pro File*, nicht *Mutationen pro File*. Bei einem Refactoring:
- Vor: file_x.dart hat 12 surviving mutants
- Refactoring entfernt 50 Zeilen, fügt 30 hinzu
- Nach: file_x.dart hat 10 surviving mutants (oder 8, oder 14 — keine direkte Beziehung zu Zeilen-Anzahl)

Eskalation nur wenn:
1. Total surviving-mutant count auf der Critical-Path-Liste *sinkt* deutlich (z.B. > 10% Reduktion) UND
2. Die Test-Coverage *steigt nicht entsprechend* (würde ja darauf hindeuten dass Tests-stärker-geworden ist) UND
3. Die file size sinkt deutlich (Indiz für Code-Löschung)

Das ist eine 3-Way-AND-Heuristik die Refactoring (gleiche Coverage, neue Tests, andere mutants) von Test-Evasion (weniger Code, weniger Tests, weniger mutants) unterscheidet. False-Positive-Rate sollte niedrig sein.

**Aktion**: dieser Mechanismus gehört in TASK-PROC-002-06 (surviving-mutant remediation creator) als neue AC oder in ein separates kleines Helper-Skript. Ich notiere als TODO im Task; baue es aber nicht jetzt — erst wenn TASK-PROC-002-02 (mutation tooling) gelandet ist und wir wirklich Logs haben.

**Repository-Größen-Sorge**: Logs in git zu versionieren ist tatsächlich nicht ideal. Alternative: Logs als separate Artefakte (`.git/info/exclude` ausschließen), aber per Snapshot in einer kleinen Manifest-Datei (`scripts/quality/mutation_baseline.json`) festhalten — only the deltas committed. So bleibt das Repo schlank.

### Keine offenen Fragen für I.

---

## K — DCM weg, very_good_analysis rein

### Bestätigt + Plan

**DCM raus.** Du hast keine kommerzielle Lizenz. Aktion: alle DCM-abhängigen Regeln aus TASK-PROC-046-03 ersetzen.

**very_good_analysis als Baseline** (K.4): bestätigt.

**bloc_lint** (K.5): bestätigt — purely additive, niedriges Risiko.

**clean_architecture_kit** (K.5): bestätigt — kannst du gerne ausprobieren; medium-FP von der naming-heuristic-detection ist verträglich, da unsere Konventionen klar sind.

**ban-name für ButtonStyle/TextStyle/Color** (K.1): bestätigt drin. Selbst-implementiert als grep-Script unter `scripts/quality/check_no_direct_styling.sh` (DCM-frei).

### Was VGA NICHT abdeckt (DCM-Lücken)

Diese Regeln verlieren wir durch DCM-Wegfall — Ersatz nötig:

| DCM-Regel | Ersatz |
|---|---|
| `cyclomatic-complexity: 20`, `number-of-parameters: 4`, `source-lines-of-code: 50`, `maximum-nesting-level: 5` | Custom Python script using `analyzer` package via `dart analyze --json` output parsing. NEW TASK. |
| `prefer-correct-type-name` (Regex-Konvention für Suffixe) | Custom grep script that finds class declarations and checks suffix. NEW TASK. |
| `avoid-banned-imports` (architectural layer boundaries) | Custom grep script that checks per-file imports against an allow-list per layer. NEW TASK. |
| `ban-name` (ButtonStyle/TextStyle/Color) | Custom grep script. NEW TASK. |
| `missing-test-assertion`, `avoid-empty-test-groups`, `prefer-test-matchers` | Custom grep + heuristic in scripts/quality/check_test_smells.sh. NEW TASK. |
| `avoid-unnecessary-setstate`, `avoid-shrink-wrap-in-lists`, `avoid-rebuilds`, `avoid-returning-widgets`, `prefer-extracting-callbacks`, `avoid-expensive-async-functions`, `avoid-passing-async-when-sync-expected` (Flutter perf) | Move to `doc/presentation/coding/best_practices.md` per item C decision. quality-checker reads + judges. |
| `avoid-dynamic`, `no-object-declaration`, `avoid-global-state` | VGA has `avoid_dynamic_calls` (similar but not identical). Move detailed `dynamic` audit to `doc/` per item C. |

### Plan für nächste Runde

In meiner nächsten Antwort:

1. **TASK-PROC-046-03 komplett neu schreiben** ohne DCM: VGA baseline + bloc_lint + clean_architecture_kit + core Dart lints.
2. **Neuer Task TASK-PROC-046-14**: Build custom replacement scripts for DCM-provided gates (complexity metrics, type-name regex, architectural imports, ban-name, test-smells). Substanzielle Arbeit — `dart analyze --json` parsing + grep heuristics.
3. **K.1 — Document WHY for rules**: deine Frage ist ausgezeichnet. Jeder rule in `analysis_options.yaml` bekommt einen YAML-Kommentar mit der Begründung. Format: `# Why: <Grund>; Source: <persona/req/doc-Referenz>`. Wird Teil von TASK-PROC-046-03's neuer Scope.
4. **K.2 — Folder-Taxonomy-Script**: bestätigt, gehört zu TASK-PROC-046-14. Macht ein eigenes Skript `scripts/quality/check_folder_taxonomy.sh` das prüft "files in `domain/` müssen in `entities/`, `repositories/`, `value_objects/`, `services/`, `failures/`, oder `events/`".
5. **K.1 Antwort auf `avoid-dynamic`/`no-object-declaration`**: das ist Type-Safety, nicht Performance. `dynamic` schaltet statische Typprüfung aus → Runtime-Fehler statt Compile-Zeit-Fehler. Performance ist nebensächlicher Vorteil (Analyzer kann nicht optimieren). Für JSON-Deserialisierung ist `dynamic` akzeptabel mit inline-justification — der Grenzfall ist `Map<String, dynamic>` aus `json.decode` zu typisierten Objekten. An anderen Stellen (Dateneingabe, BLoC state, etc.) ist `dynamic` nie nötig.

### Keine offenen Fragen für diese Runde — der K-Restructure folgt.

---

## Status der Runde

**Erledigt in dieser Runde**:
- Items A (außer A.5 → Agent fertig, Findings ins File), B.2, C, C.2, E.1, E.2, F.1, F.2, F.3, G.1, G.2, H, H.1, H.2, H.3, I.1, I.2 (Design notiert), K.4, K.5 Confirmation
- Neue Tasks: TASK-PROC-046-13 (Allgemeines 1+2), TASK-PROC-002-09 (F3)
- REQ-PROC-046 Step 4 mit echtem question.md Mechanismus
- TASK-PROC-046-11 update für question.md statt escalation
- REQ-NFUNC-002 neue ACs (AC-14 readability, AC-15 keyboard, AC-16 component semantics, AC-17 form assistance, AC-18 audio placeholder)

**Zu erledigen in nächster Runde** (große Arbeit):
- K-Restructure: TASK-PROC-046-03 komplett neu schreiben (no DCM)
- K.1 + K.2: TASK-PROC-046-14 erstellen für custom replacement scripts (complexity metrics via `analyzer` package, ban-name, folder taxonomy, type-name regex, architectural imports, test smells)
- WHY-comments-for-rules: Teil von TASK-PROC-046-03's neuem Scope

**Offene Fragen für deine Review**:
- A.1 (English readability metric mapping)
- A.2 (screen-reader basics now vs Phase 2 polish)
- A.3 (error recovery rule concrete enough?)
- Allgemeines.1 (review-task cadence: nur manuell, oder auch periodisch?)
- E.3 (model-version archival logic — wo lebt es?)


