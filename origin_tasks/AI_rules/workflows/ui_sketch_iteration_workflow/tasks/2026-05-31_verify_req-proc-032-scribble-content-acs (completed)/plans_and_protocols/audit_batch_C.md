# Audit Batch C — REQ-PROC-032 AC-32..AC-36

Verification standard: producer artifact must *specify* the behavior correctly with a real
algorithm / concrete fields / real comparison, and consumers must read it as the AC says.
Runtime instances not required.

## AC-32 — Multi-breakpoint scribbles from persona device classes

Verdict: COVERED

- Personas declare device classes as real data (`pcd.device_classes`):
  - `requirements_user_needs/personas/dr_sarah/persona.md:48` → `device_classes: [desktop, tablet]`
  - `requirements_user_needs/personas/dr_med_turan/persona.md:43` → `device_classes: [desktop]`
  - `requirements_user_needs/personas/felix/persona.md:33` → `device_classes: [mobile]` (most personas mobile)
  - `requirements_user_needs/personas/prof_dr_weber/persona.md:38` → `device_classes: []` (empty handled by fallback)
  - => a UNION across served personas genuinely produces 2+ breakpoints for mixed cohorts.
- Generator computes the UNION via a concrete algorithm:
  - `.claude/agents/ui-scribble-generator.md:53-57` step 0a: read `personas_served:`, locate each persona via `grep -rl "persona_id: <ID>"`, read `pcd.device_classes`, `required_breakpoints = sorted unique union ... excluding none and empty`, fallback `[mobile]`.
- Orchestrator (consumer) computes the same union and persists it:
  - `.claude/skills/ui-scribble-iterate/SKILL.md:35-50` Phase 0.3 — identical union algorithm, writes `breakpoints.yaml` with `derived_from[]` provenance and `fallback_used`, passes `required_breakpoints` to the Phase 1 generator (`SKILL.md:69`).
- SHARED vs duplicated decision is concretely defined (not just named):
  - `.claude/agents/ui-scribble-generator.md:62-66` — `shared` requires ALL of: no nav widget in body, no layout reflow, no width-gated panels; else `per_breakpoint`. File naming `NN_[name].shared.html` vs `NN_[name].[breakpoint].html`; index.html shared section with anti-duplication note; metadata `shared_screens` / `per_breakpoint_screens` (`:67-74`).
  - Single-breakpoint shortcut at `:59` (no duplication overhead when union = 1).

## AC-33 — Structured inspiration inputs

Verdict: COVERED

- Per-aspect use/ignore matrix consumed from `inputs/inspiration.yaml`:
  - `.claude/agents/ui-scribble-generator.md:76-91` step 0b — parse each reference entry, collect use/ignore matrix; `use: true` → extract & apply structural pattern; `use: false` → fall back to `doc/presentation/` project conventions.
- Scope + note supported: `screen_scope` honored at `:79` (`screens whose filename fragment matches any entry in screen_scope`); matrix domain vocabulary at `:22`.
- Per-screen annotation of inspiration source is concrete:
  - `:79-82` adds `<!-- inspiration: ref_001 "Label" — used: layout, spacing -->` listing only `true` aspects; metadata `inspiration_applied[]` with `id/label/used_aspects/screen_scope` (`:83-90`).
- Adversarial guards present: colors always RE-DERIVE even if `colors: true` (`:40`); annotation must reflect real applied HTML, not intent (`:41`).

## AC-34 — Reviewer pre-brief before generation

Verdict: COVERED

- Pre-brief produced before the first expensive generation (Phase 0.5, first generation only):
  - `.claude/skills/ui-scribble-iterate/SKILL.md:52-64`.
- <=300-word cap stated explicitly: `:53` "Produce a ≤300-word pre-brief".
- Required content all present: screens, personas+rules, out of scope, information-model boundary, open assumptions (`:54-58`).
- Three developer options — approve / adjust / reject scope (`:60`):
  - Approve → retained as version artifact `{SCRIBBLE_BASE}pre_brief.md` (`:62`).
  - Reject scope → routes to `requ-explore` (`:64`).
- BOUNDED iteration with escalation: Adjust → "Max 3 adjust iterations; if unapproved after 3, escalate via pending_feedback and terminate" (`:63`).

## AC-35 — Cross-feature consistency check

Verdict: COVERED

- Trigger condition matches AC (scribble belongs to a feature sharing a user flow with siblings that have scribbles):
  - `.claude/agents/ui-scribble-cross-feature-checker.md:11` spawned by auto-review when scribble has `flow_positions`; `:27` skips when no flow_positions.
- Sibling discovery by shared flow with real logic:
  - `:31-37` for each `flow_id`, `grep -rl "flow_id: <flow_id>"`, include only siblings whose `feature_path` differs and uses highest non-superseded version.
- Real component comparison for the same role (not merely named):
  - `:41-46` compares `flutter_component_mapping`: shared HTML element key with differing Flutter widget value → divergence; one-sided key → informational gap. HTML fallback extraction when mapping metadata absent (`:48-54`).
- Flags divergences for HUMAN resolution: `:66` "Divergences — Human Resolution Needed" table (Current vs Sibling widget per role/flow). Matches the AC example (FilledButton vs TextButton for same primary role).

## AC-36 — Automated visual validation after implementation

Verdict: COVERED

- Vision capability comparing integration-test screenshots vs approved scribble + re-derive sources:
  - `.claude/skills/ui-visual-validate/SKILL.md:8-9,33-41` — per-screen vision agents; re-derive sources tokens.json, T1/T2 rules, persona sizing.
- Reads per-locked-item verification seeds emitted in flutter_handoff.yaml:
  - `SKILL.md:24-26` reads `flutter_handoff.yaml` → `verification_seeds:` block; "Seeds are the primary check list"; per-seed `expectation`/`check` evaluated (`:38-44`).
- Schema actually defines `verification_seeds` with concrete per-locked-item fields:
  - `.claude/schemas/flutter_handoff.yaml:81-119` — array of `{screen, seeds[]}`; each seed `required_keys: [locked_item, expectation, check]`, optional `selector`; `check` enum (screen_presence, copy_text, sizing, hierarchy, component, state, accessibility_intent).
- Emitter actually emits them (per locked item, per screen):
  - `.claude/agents/ui-scribble-handoff-emitter.md:80-94` example block; `:102` derives one visually-checkable seed per LOCKED-IN item (L1/L4/L8/L3/L9/L15 minimum), LOCKED-IN only never RE-DERIVE; MUST-rule `:138`.
- Advisory / non-blocking by default:
  - `SKILL.md:9` "advisory and non-blocking — never exit non-zero"; constraints `:67-70` never block a commit/task.
- Scope distinct from ui-verify-flutter (code-only structural) and ui-improve-flutter (human-driven polish):
  - `SKILL.md:17-19` explicit scope boundary; "This skill only looks and reports".

## Summary

| AC | Verdict |
|----|---------|
| AC-32 | COVERED |
| AC-33 | COVERED |
| AC-34 | COVERED |
| AC-35 | COVERED |
| AC-36 | COVERED |

COVERED: 5 · PARTIAL: 0 · NOT_COVERED: 0
No fix tasks required for this batch.
