---
task: TASK-PROC-032-18
date: 2026-06-01
approach: inline
---

# Plan: Scribble Contract Consumers — Sketch Gate and Verifier

## Objective

Wire two downstream consumers to honor the LOCKED-IN / RE-DERIVE contract established by
TASK-PROC-032-11: the Sketch Gate in code-simple/code-complex (AC-24) and the finding
taxonomy in ui-verify-flutter (AC-25).

## Files to Modify

| File | Change |
|------|--------|
| `.claude/skills/code-simple/SKILL.md` | Expand Sketch Gate step 4 to read `contract:` block and split locked-in vs re-derive |
| `.claude/skills/code-complex/SKILL.md` | Replace the scribble-check bullet in Plan step with a structured Sketch Gate block |
| `.claude/skills/ui-verify-flutter/SKILL.md` | Add Phase 0.5 contract read; rewrite component check + report taxonomy to coder_defect / out_of_contract |

## Contract Reference (from TASK-PROC-032-11 / SKETCHES_README.md)

LOCKED-IN (L1–L15): screen list/order, widget choices, info hierarchy, copy text, canon
labels, personas applied + constraints, T1/T2 rules cited, persona-sizing named tokens,
screen states, navigation pattern, dialog pattern, component-library usage, info-model
boundary, design decisions, accessibility intent (semantic element, ARIA role, alt-text
obligation, accessible-name).

RE-DERIVE (D1–D8): exact token values, colors, a11y implementation (focus order,
announcements, WCAG verification), animation curves/timing, responsive breakpoint
mechanics, hover/focus/pressed states, BLoC and behavior wiring, cross-persona
constraints not visible in scribble.

## AC-24 Change (Sketch Gate)

code-simple step 4 — from:
  "If approved scribble exists: reference it during implementation for element choices"

To:
  4a. Read flutter_handoff.yaml `contract:` block (locked_in, re_derive, source)
  4b. LOCKED-IN → implement exactly as depicted
  4c. RE-DERIVE → derive from doc/presentation/ + tokens.json; ignore scribble depiction
  4d. Every implementation note states its contract side

code-complex step 2 — replace the "verify scribble" bullet with a Sketch Gate block
with identical split logic.

## AC-25 Change (ui-verify-flutter)

Add Phase 0.5 to read `contract:` block from flutter_handoff.yaml before any checks.

Update Phase 2 component check: deviation on locked-in item → `coder_defect`; if
item is in re-derive set → `out_of_contract` (skip evaluation against scribble).

Update Phase 3 persona/rule check:
- L8 sizing tokens, L4 copy, L15 a11y intent → locked-in → divergence = `coder_defect`
- D3 a11y implementation → re-derive → `out_of_contract` (skip)

Update Phase 4 report taxonomy:
  Old: token_violation / rule_violation / missing_element / deviation / acceptable
  New: coder_defect (locked-in divergence) / out_of_contract (re-derive items — not
       evaluated against scribble) / match / acceptable
  Every finding states its contract side.

Update Phase 5 severity chart to use new taxonomy names.

## INDEX.md / factory_flows.md

No description or category changes → INDEX.md unchanged.
Changes are internal logic (step reordering, wording) → factory_flows.md unchanged.

## Phases

1. Modify code-simple Sketch Gate (AC-24)
2. Modify code-complex Sketch Gate (AC-24)
3. Modify ui-verify-flutter taxonomy (AC-25)
4. Verify ACs, log, complete task
