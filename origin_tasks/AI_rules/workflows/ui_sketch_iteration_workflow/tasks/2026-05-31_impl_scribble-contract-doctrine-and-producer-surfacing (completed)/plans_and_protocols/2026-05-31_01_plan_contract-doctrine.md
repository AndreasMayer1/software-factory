# Plan: Scribble Contract Doctrine and Producer Surfacing

Date: 2026-05-31
Task: TASK-PROC-032-11

## Approach: Inline

All 4 deliverables are mechanically specified by AC-21..AC-27 and the requirements SEC-15 text.
No ambiguity; no agent needed.

## Phases

### Phase 1 — SKETCHES_README.md (AC-21)
Add "What a Scribble Commits To" section after the "What a Scribble Is" section.
Content: two disjoint sets LOCKED-IN (L1–L15) and RE-DERIVE (D1–D8) verbatim from requirements.
This section is the ONLY place these lists live (no restatement).
Success: section present, enumerates exactly L1–L15 and D1–D8.

### Phase 2 — ui-scribble-generator agent (AC-22, AC-26, AC-27)
Changes (via claude-modify-agent governance):
a) Step 6 motor-constraint line: change `min-height: 48px` → `var(--min-tap-target)` (and `64px` → `var(--min-tap-target-crisis)` for crisis flows). Add named-token comment.
b) New step after 6: accessibility-INTENT — for each interactive/informational element add semantic element, ARIA role identity, alt-text obligation, accessible-name presence.
c) Add CONTRACT BLOCK emission instructions (index.html + compact per-screen), verbatim from SKETCHES_README section, dual framing.
d) Add rule-application audit trace instructions (machine-readable per-screen trace of which T1/T2 rule → which element).
Success: generator instructions require all four behaviors.

### Phase 3 — ui-scribble-handoff-emitter agent (AC-23)
Changes (via claude-modify-agent governance):
a) Add `contract:` block emission: top-level YAML block with `locked_in:` (item keys L1–L15) and `re_derive:` (item keys D1–D8) + `source:` pointer to SKETCHES_README section.
b) Add `design_decisions:` block: propagates `metadata.yaml design_decisions[]` to coder.
Success: handoff YAML carries both blocks.

### Phase 4 — flutter_handoff.yaml schema (AC-23)
Add optional top-level blocks to schema:
- `contract:` block: `locked_in` (array of strings), `re_derive` (array of strings), `source` (string pointer)
- `design_decisions:` block: array of objects with `decision` + `reason` fields
Success: schema validates both new top-level blocks.

## Execution Order
1. SKETCHES_README.md (needed first — agents reference it as source)
2. Schema update (independent of agents)
3. Generator agent (references SKETCHES_README)
4. Handoff-emitter agent (references SKETCHES_README and schema)
