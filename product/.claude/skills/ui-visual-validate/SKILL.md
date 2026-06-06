---
name: ui-visual-validate
description: Vision-compare screenshots against the approved scribble (advisory)
tools: "*"
model: inherit
---

You advisorily compare integration-test screenshots of the implemented Flutter screens against
the approved scribble, its `verification_seeds`, and the re-derive sources. Vision-based,
**advisory and non-blocking** — never exit non-zero on findings, never modify source.

**Trigger**: manually after implementation + integration-test screenshots exist; or after
ui-verify-flutter passes and a vision pass is wanted.
**Inputs**: (1) requirement path, e.g. `requirements_tasks/functional/<feature>/`; (2) optional
screenshots dir (default: `<requirement-path>/scribbles/flutter_review/screenshots/`).

**Scope boundary** (do not cross): ui-verify-flutter does code-only structural match;
ui-improve-flutter does human-driven polish that edits source. This skill only *looks and reports*.

## Phase 1 — Locate inputs

1. Find the approved scribble: the `scribbles/v{n}/` whose `metadata.yaml` has `status: approved`.
   None → report "no approved scribble; run ui-scribble-iterate" and stop (advisory exit 0).
2. Read `flutter_handoff.yaml` → its `verification_seeds:` block (per-screen seeds) and `screens:`.
   Absent or no seeds → report "no verification_seeds (regenerate handoff via ui-scribble-approve-handoff)"
   and stop (advisory exit 0). Seeds are the primary check list.
3. Map each scribble screen `NN_<name>` to a screenshot `NN_<name>.{png,jpg}` in the screenshots dir.
   Screenshots dir missing or empty → report which screens lack screenshots and stop (advisory exit 0);
   never fail.

## Phase 2 — Per-screen vision comparison

Spawn **one `general-purpose` agent per screen** (parallel; this session is Opus/vision-capable, so
agents inherit a vision model). Pass ONLY that screen's: screenshot path, scribble HTML, its
`verification_seeds`, and the re-derive sources below — never the whole codebase.

Each agent checks, per seed, whether the screenshot satisfies the seed's `expectation` (scoped by
`check`): `screen_presence`, `copy_text`, `hierarchy`, `component`, `state`, `sizing`,
`accessibility_intent`. Re-derive sources for `sizing`/visual context: `tokens.json`
(token-source), T1/T2 rules (`doc/presentation/design/`), persona sizing
(`requirements_user_needs/personas/` referenced in `metadata.yaml`). Each finding →
`match` | `advisory` (visible deviation) | `unverifiable` (screenshot can't show it), with the
seed's `locked_item` and one-line evidence.

## Phase 3 — Aggregate advisory report

Write `<requirement-path>/scribbles/flutter_review/visual_validation.md`:

```markdown
# Visual Validation — <Feature>  (ADVISORY · non-blocking)
Date: <today> · Approved scribble: scribbles/v{n}/ · Screenshots: <dir>

## Per-screen
| Screen | Screenshot | Seeds checked | match | advisory | unverifiable |
|--------|-----------|---------------|-------|----------|--------------|

## Advisory findings
- <screen :: locked_item :: check :: expected vs observed :: evidence>

## Unverifiable
- <screen :: locked_item :: why the screenshot can't confirm it>
```

Report path and a one-line summary. State clearly that findings are advisory and gate nothing;
suggest ui-improve-flutter only if visible polish deviations were found.

## Constraints

- Never modify source, scribble, or handoff files — read-only.
- Never exit non-zero and never block a commit or task — advisory only.
- Seeds cover LOCKED-IN items only; do not invent checks for RE-DERIVE items.
- One screen per agent; never load all screenshots/files into one context.
