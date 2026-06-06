# Spec: Marketing Release Notes Section for /release Skill

**Usage by TASK-PROC-036-01**: Copy everything from the `## Step 4` heading below verbatim into
the release skill as one of its numbered steps. Do not copy this preamble.

**Source rules**: REQ-PROC-037 — `requirements_tasks/process/documentation_rules/marketing_writing/requirements.md`
**Output files**: `releases/[version]/release_notes_marketing_de.md` + `releases/[version]/release_notes_marketing_en.md`

---

## Step 4 — Marketing release notes

### 4.1 Read active release

Read `requirements_tasks/RELEASES.md`. Find the entry with `status: active`. Extract:
- `version` (e.g. `"0.0.1"`), `name`, `description`, `goals[]`, `scope_boundaries.includes[]`

If no `status: active` entry exists, stop: "No active release found in RELEASES.md."

### 4.2 Create output directory

Create `releases/[version]/` if it does not exist.

### 4.3 Generate German draft

Generate the German release note using the extracted release data. Use this mapping:

| Source field | How to use it |
|---|---|
| `description` | One-sentence release summary. Use as inspiration for the opening line — rewrite in release-note voice, do not quote verbatim. |
| `goals` | Understand what the release was trying to achieve. Do NOT expose goals as bullet points — they are author intent, not user-facing content. Use to calibrate which included items matter most. |
| `scope_boundaries.includes` | The concrete things shipped. Write one sentence per significant item, or a compact bullet list for secondary items. Skip items with no user-observable effect (e.g. internal refactors, CI changes). |

**Tone hierarchy** (higher always overrides lower when they conflict):

1. **Calm** — no urgency signals of any kind: no `!` for emphasis, no "Jetzt", "Wichtig!", "Nicht verpassen", "Kritisch", "Dringend"
2. **Honest** — describe what exists; no superlatives; no claims the product does not support
3. **Contextually appropriate** — every sentence passes: *"Würde das jemandem mit einem sehr schlechten Tag wehtun?"*
4. **Shame-free** — no "endlich", no streak language, no "du hast verpasst", no progress milestones
5. **Non-advisory** — no unsolicited tips, improvement suggestions, or behavioral guidance

**Voice: Sachlich-warm.** A skilled craftsperson explaining what they built. Competent, direct, approachable — not a salesperson, not a coach. The app describes its function; the user decides what it means for them.

**Stability framing — the default mental model:**

Before writing, ask: *"What does the app do now that it didn't before?"* Then describe that as a plain function statement — not a novelty event.

- "Die Planübergabe funktioniert jetzt auch ohne WLAN." — not "Aufregendes neues Offline-Feature!"
- "Die QR-Code-Erkennung ist zuverlässiger bei schlechtem Licht." — not "Noch besser als je zuvor!"
- For bug-fix-only releases: "Die App arbeitet wie bisher, mit Korrekturen bei [kurze Beschreibung]."

**Structure** (adapt to release size — conciseness is always better):

    [Version] — [Monat Jahr]

    [Kernaussage: was ist neu oder besser — ein bis drei Sätze]

    [Optional: Aufzählung sekundärer Änderungen als kurze Bullet-Liste]

    [Optional: Spendenhinweis — nur bei bedeutender neuer Funktion; Regeln siehe unten]

**Language:**
- Du form throughout
- German terms over Anglicisms: "Einstellungen" not "Settings", "Protokoll" not "Log", "Auswertung" not "Analytics", "Planübergabe" not "Plan Transfer"
- Literal language over metaphors; use a metaphor only when it is more precise than the literal alternative

**Forbidden patterns — never appear in any form:**
- Urgency: "Jetzt!", "!", "Nicht verpassen", "Wichtiges Update erfordert", "Dringend"
- Milestone/progress: "30 Tage", "Streak", "Fortschritt feiern", "Meilenstein erreicht"
- Recovery narratives: "Reise", "Weg", "Schritt für Schritt", "Licht am Ende des Tunnels"
- Growth metaphors: "Pflanze den Samen", "erblühe", "wachse über dich hinaus"
- Benefit interpretation: "Verstehe dich besser", "Erkenne endlich deine Muster", "Nimm deine Gesundheit in die Hand"
- Feature hype: "5 neue Features!", "Noch mehr Möglichkeiten", "Revolutionär", "Aufregende Neuigkeiten"
- Social proof: "Tausende nutzen...", "Beliebter als je zuvor", "Besser als X"
- Assumed continuity: "Wie du weißt...", "Wie wir letztes Mal erklärt haben..."
- Guilt-based: "Wir brauchen deine Hilfe", "Vergiss uns nicht", "Ohne dich geht es nicht"

**Donation prompt** (optional, SEC-05):

Include only when this release adds a significant new user-visible feature. Do NOT include for:
bug-fix-only releases, internal/infrastructure work, or alpha/proof-of-concept releases.

If included, place at the end of the German note using this exact conditional framing:

    Wenn die App hilft, kann die Entwicklung hier unterstützt werden: [link-placeholder]

No "bitte", no urgency, no guilt — the donation is an option for those who feel helped, not a request to everyone.

**Examples:**

Feature release:

    Version 0.0.1 — März 2026

    Die Planübergabe per QR-Code zwischen Therapeuten- und Klientengerät funktioniert.
    Alle Daten bleiben lokal auf dem Gerät — kein Server, keine Cloud-Verbindung.

Bug-fix release:

    Version 0.0.2 — April 2026

    Die App arbeitet wie bisher, mit Korrekturen:
    - QR-Code-Scan: Lesefehler bei schlechter Beleuchtung behoben
    - Datenübertragung: Timeout-Fehler beim wiederholten Scan behoben

### 4.4 Generate English draft

Write an English version. **Adapt, do not translate** — English release notes have different
natural phrasing than German.

How to adapt:
- German compound nouns → English noun phrases: "Planübergabe" → "plan transfer"
- German passive often → English active (when natural): "Daten werden gespeichert" → "Data is stored locally"
- Avoid "you can now" constructions — they frame changes as novelty events rather than function statements
- "du form" → "you" form throughout
- All tone rules from 4.3 apply unchanged in English: no "Finally!", no "Exciting new features!", no "Don't miss"
- Same forbidden patterns apply: "Finally", "Important update required", "Don't forget", "streak" are all forbidden

**Examples** (same releases as 4.3):

Feature release:

    Version 0.0.1 — March 2026

    QR-code plan transfer between therapist and client device is working.
    All data stays on the device — no server, no cloud connection.

Bug-fix release:

    Version 0.0.2 — April 2026

    The app works as before, with corrections:
    - QR scan: fixed read errors in low-light conditions
    - Data transfer: fixed timeout errors on repeated scans

### 4.5 Present drafts for review

Show the user both drafts using this format (render as markdown, do not wrap in a code block):

---
**Marketing release notes — draft for review**

**DE** · `releases/[version]/release_notes_marketing_de.md`

[German draft content here]

---

**EN** · `releases/[version]/release_notes_marketing_en.md`

[English draft content here]

---

*Drafts follow REQ-PROC-037 (Marketing Writing Rules). Type **approve** to write and continue, or describe what to change.*

---

**Do not write any files to disk. Do not proceed to Step 5. Wait for the user's response.**

### 4.6 Revisions

While the user has not typed "approve" (case-insensitive, with or without punctuation):
1. Apply the requested changes to the relevant draft(s)
2. Re-display using the same format as 4.5, showing the full updated draft(s)
3. Repeat until "approve" is received

### 4.7 Write approved files

After explicit "approve":
1. Write German draft → `releases/[version]/release_notes_marketing_de.md`
2. Write English draft → `releases/[version]/release_notes_marketing_en.md`
3. Confirm: "Marketing release notes written to `releases/[version]/`."

---

## Acceptance Criteria Verification

| Acceptance criterion | Met by |
|---|---|
| `release_notes_marketing_de.md` generated in German, du form, per REQ-NFUNC-013 + REQ-PROC-037 | Step 4.3 — tone hierarchy, language rules, generation algorithm |
| `release_notes_marketing_en.md` generated in English | Step 4.4 — adaptation rules + examples |
| Skill presents both drafts and waits for user approval — does NOT auto-proceed | Step 4.5 — explicit gate + "Do not proceed" directive |
| User can request revisions; skill regenerates on request | Step 4.6 — revision loop |
| Release marked `released` only after user explicitly approves | Step 4.7 writes files after approval; Step 5 (marking released) follows only thereafter |
