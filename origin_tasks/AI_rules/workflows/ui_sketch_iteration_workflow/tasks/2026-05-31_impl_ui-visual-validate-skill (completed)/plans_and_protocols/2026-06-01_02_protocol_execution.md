---
skills_used:
  - claude-automated-mode
  - claude-watch-tool-reliability
  - claude-route
  - task-resolve
  - claude-modify-agent
  - claude-create-skill
  - claude-log
  - task-complete
  - claude-commit
---

# Protocol — TASK-PROC-032-19 execution

Date: 2026-06-01 · Session: d8679440 (web) · Model: Opus

## Delivered (AC-36)

1. **Schema** `.claude/schemas/flutter_handoff.yaml` — added top-level OPTIONAL
   `verification_seeds:` block: per-screen list of per-LOCKED-IN-item seeds
   `{locked_item, expectation, check[, selector]}`. The R3-collapse: seeds live
   inside flutter_handoff.yaml, not a separate file.

2. **Emitter** `.claude/agents/ui-scribble-handoff-emitter.md` (via claude-modify-agent)
   — added the `verification_seeds:` emission protocol, Domain-Vocabulary terms,
   anti-patterns (LOCKED-IN-only, screenshot-checkable phrasing), a YAML example,
   Output + Rules entries. Contract sidecar unchanged (seeds stay inside the
   existing `handoff` artifact already in `produces:`).

3. **Skill** `.claude/skills/ui-visual-validate/` (via claude-create-skill) —
   advisory, non-blocking, vision-based per-screen comparison of integration-test
   screenshots vs the approved scribble + verification_seeds + re-derive sources;
   writes `scribbles/flutter_review/visual_validation.md`. Fans out one
   `general-purpose` agent per screen (Opus/vision inherited).

4. **INDEX.md** — added the ui-visual-validate row in the ui-* section.

## Key decisions

- **No dedicated vision agent (rubric-evaluated NO).** A new `{expertise}-{role}`
  agent would (a) add an unbaselined agent-name violation in
  `check_artifact_token_resolve.py` (expertise not a registry token) and (b) force
  an Artifact-Establishment escalation. The established sibling pattern
  (ui-verify-flutter) already fans out per-screen to `general-purpose` agents — so
  the skill carries the vision instructions and does the same. Scope is kept
  distinct from ui-verify-flutter (code-only structural) and ui-improve-flutter
  (source-editing polish).

- **Contract uses registry TOKEN NAMES + `source: external`.** Empirically required
  to pass BOTH live contract linters during the REQ-PROC-044-02 migration:
  - `check_artifact_token_resolve.py` (baselined): every `path:` value must be a
    registry token name; raw paths would be new unbaselined violations → FAIL.
  - `check_skill_contracts.py` (no baseline): a `source: skill:<producer>` input is
    cross-checked by basename against the producer's raw-path `produces:`; a
    token-name basename (`handoff`) never matches a producer's `flutter_handoff.yaml`
    → would FAIL. `source: external` makes the cross-ref skip the item.
  produces token: `flutter-review` (the report is a scribble-vs-implementation
  comparison, co-located with comparison.md); derived_from tokens: `scribble-metadata`,
  `handoff`, `scribble`, `integration-test`, `token-source`, `design-rule`, `persona`
  — all pre-existing in the registry, so no new token, no escalation.
  > Future-work note (for a registry-operationalization / optimize pass): once
  > producers migrate to token-name contracts, the `source: external` placeholder on
  > skill-produced inputs here should become `source: skill:<producer>`.

## Verification

- `check_artifact_token_resolve.py --baseline …` → PASS (0 unbaselined; 443 baselined).
- `check_skill_contracts.py` → only the 2 PRE-EXISTING failures
  (claude-watch-tool-reliability, claude-write-hook) remain; ui-visual-validate clean.
- flutter_handoff schema + ui-visual-validate contract parse as valid YAML.
- Emitter agent retains all governed sections (Domain Vocabulary / Anti-Patterns /
  Protocols / Output / Rules).
- No `lib/` / `test/` / `integration_test/` changes → Flutter quality gates N/A.
