# Plan — TASK-PROC-032-19: ui-visual-validate skill

Date: 2026-06-01
Covers: AC-36

## Objective

Deliver an advisory (non-blocking) visual-validation capability that compares
integration-test screenshots of implemented Flutter screens against the approved
scribble + re-derive sources, using a vision-capable model and per-locked-item
`verification_seeds:` emitted in `flutter_handoff.yaml`.

## Approach: agent-assisted (inline orchestration by main session)

The work is three coherent deliverables. No fan-out research needed; the main
session authors them directly via the governed creation skills.

## Deliverables

1. **Schema + emitter: `verification_seeds`** (the R3-collapse — seeds live INSIDE
   `flutter_handoff.yaml`, not a separate file).
   - `.claude/schemas/flutter_handoff.yaml`: add a top-level OPTIONAL
     `verification_seeds:` block (per-screen list of per-locked-item seeds).
   - `.claude/agents/ui-scribble-handoff-emitter.md`: add emission protocol —
     derive one seed per visually-checkable LOCKED-IN item from the COMPONENT
     MAPPING blocks + screen-level states.
   - `.claude/agents/ui-scribble-handoff-emitter.contract.yaml`: no path change
     (seeds are inside the same `handoff` artifact).

2. **Vision agent: `ui-scribble-vision-reviewer`** (via claude-create-agent).
   - Role `reviewer` (evaluates, emits findings, non-mutating) — name follows the
     established `ui-scribble-{qualifier}-{role}` sibling pattern.
   - Per-screen vision comparison: one screenshot + matching scribble screen +
     that screen's `verification_seeds` → advisory findings.
   - tools: `Read, Grep, Glob` (read-only reviewer).

3. **Skill: `ui-visual-validate`** (via claude-create-skill).
   - Orchestrates: locate approved scribble + handoff, collect integration-test
     screenshots, fan out one `ui-scribble-vision-reviewer` per screen, aggregate
     into an advisory report.
   - Output: `requirements_tasks/<feature>/scribbles/flutter_review/visual_validation.md`
     (co-located with ui-verify-flutter's comparison.md, under the existing
     `flutter-review` artifact directory — no new artifact directory introduced).
   - Advisory / non-blocking: never exits non-zero on findings.
   - Scope distinct from ui-verify-flutter (code-only structural) and
     ui-improve-flutter (human polish).

## Artifact-registry / gate decision (REVISED after reading the live gate)

The token-resolve gate (`check_artifact_token_resolve.py`, wired into
`check_quality_gates.sh` with `artifact_token_baseline.txt`) IS live and the
registry now exists. The gate checks that each contract `path:`/agent token value
is **literally a registry token name** (no glob matching) and that every
`{expertise}-{role}` agent name's expertise is a registry token. All 443 existing
raw-path/legacy-name violations are grandfathered in the baseline; anything NEW
must resolve to a registered token or it fails the gate.

Consequences for this task:
- **No dedicated vision agent.** A new agent `ui-scribble-vision-reviewer` would
  add a new agent-name violation (expertise `ui-scribble-vision` is not a registry
  token) → gate FAIL, and the Artifact-Establishment Gate would force an
  escalation just to register the expertise. The rubric-correct outcome is that a
  dedicated agent is NOT warranted: the established sibling pattern (ui-verify-flutter)
  already does per-screen fan-out to `general-purpose` agents. ui-visual-validate
  carries the vision-comparison instructions and fans out the same way.
- **Skill contract reuses existing tokens only** (no new token, no escalation):
  - produces: `flutter-review` (the advisory report is a scribble-vs-implementation
    comparison artifact, co-located in `scribbles/flutter_review/`).
  - derived_from: `scribble`, `handoff`, `scribble-metadata`, `integration-test`
    (screenshot source), `token-source`, `design-rule`, `persona`.
  - New-format contracts put the **token name** as the `path:` value (create-skill §4b).

## verification_seeds schema (design)

Top-level optional block, per-screen, each seed names its LOCKED-IN key + a
visually-checkable expectation + a check category:

```yaml
verification_seeds:
  - screen: 01_home_night_mode
    seeds:
      - locked_item: L1
        expectation: "Screen is present and reachable in the implemented app"
        check: screen_presence
      - locked_item: L4
        selector: "button.primary"
        expectation: "Primary action label matches the scribble copy"
        check: copy_text
      - locked_item: L8
        selector: "button.primary"
        expectation: "Touch target is visually >= the min-tap-target token"
        check: sizing
```

## Verification

- check_skill_contracts.py passes for the new skill + agent.
- New flutter_handoff schema parses; emitter protocol references it.
- INDEX.md updated; factory_flows unchanged (no new input type).
- No `lib/`/`test/` changes → no Flutter quality gates triggered (process artifacts only).
