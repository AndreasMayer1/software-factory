# Plan: Marketing Release Notes Generation (TASK-PROC-036-04)

## Context

TASK-PROC-036-04 implements the marketing release notes generation logic in the `/release` skill.
The `/release` skill does not yet exist — TASK-PROC-036-01 creates the full orchestration, but
depends on this task (and -02, -03, -05, -06) first. So this task creates the skill file with
the marketing notes section fully detailed; other tasks fill in their sections.

## Deliverables

1. `plans_and_protocols/2026-03-11_02_spec_marketing-notes-section.md` — this task's contribution:
   the marketing notes skill section verbatim, ready for TASK-PROC-036-01 to embed in the skill.
2. No direct changes to `.claude/skills/` — TASK-PROC-036-01 owns the skill file.

## Decision: Spec Document vs. Direct Skill Edit

Write the marketing notes content as a standalone spec document because:
- The release skill doesn't exist yet; -01 owns skill creation
- -04 cannot know the full skill structure -01 will design
- -01 simply reads this file and embeds the marketing section
- Clean task decomposition — no coordination at file level required

## Marketing Notes Section Design

### Input: from RELEASES.md
Read the release with `status: active`. Extract:
- `version`, `name`, `description`, `goals[]`, `scope_boundaries.includes[]`

### Output files
- `releases/[version]/release_notes_marketing_de.md` (German, du form)
- `releases/[version]/release_notes_marketing_en.md` (English, adapted)

### Tone rules (from REQ-PROC-037)
Priority order (higher overrides lower):
1. Calm — no urgency, no "!", no "NOW", no "Critical"
2. Honest — describes what exists, no superlatives, no unverifiable claims
3. Contextually appropriate — passes the "bad day" test
4. Shame-free — no "endlich", no streaks, no gaps implied
5. Non-advisory — no unsolicited tips or guidance

Voice: Sachlich-warm. Like a craftsperson explaining what they built.

### Forbidden patterns (SEC-07 condensed)
- Urgency signals: "Jetzt!", "Nicht verpassen", "Wichtiges Update"
- Milestone/streak: "30 Tage", "Fortschritt", "Feier"
- Recovery narratives: "Reise", "Weg", "Schritt für Schritt", "Licht"
- Growth metaphors: "Pflanze", "erblühe", "wachse"
- Benefit interpretation: "Verstehe dich besser", "Nimm deine Gesundheit..."
- Feature hype: "5 aufregende neue Features!"
- Social proof: "Tausende Nutzer..."

### Recommended structure (SEC-05)
```
[Versionsnummer] — [Monat Jahr]

[Zusammenfassung: was hat sich geändert, ein bis drei Sätze]

[Optional: Aufzählung sekundärer Änderungen]
```

### Example tone (good)
> "Version 0.0.1 — März 2026
>
> Die QR-Code-Planübergabe zwischen Therapeuten- und Klientengerät funktioniert.
> Alle Daten bleiben lokal auf dem Gerät — kein Server, keine Cloud-Verbindung."

### Review loop
Generate both drafts → present to user → request/apply changes → repeat until user approves
→ Only then write files to disk.

## INDEX.md Update

Add to Quick Reference table and create new section or add under appropriate category.
The `release` skill is user-invocable via `/release`.

## How TASK-PROC-036-01 Uses This

TASK-PROC-036-01 creates `.claude/skills/release/skill.md`. It must:
1. Read `plans_and_protocols/2026-03-11_02_spec_marketing-notes-section.md` from this task
2. Copy that content verbatim as the "Step 4 — Marketing release notes" section of the skill
3. The spec document's path: `requirements_tasks/process/AI_rules/workflows/release_workflow/tasks/2026-03-10_impl_marketing-release-notes/plans_and_protocols/2026-03-11_02_spec_marketing-notes-section.md`

## factory_flows.md

No diagram change needed — this task produces only a spec document, not a skill or artifact change.
