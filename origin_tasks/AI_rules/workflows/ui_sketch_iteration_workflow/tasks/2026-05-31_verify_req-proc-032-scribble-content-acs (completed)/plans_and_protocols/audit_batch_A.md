# Audit — Batch A (AC-21 .. AC-27)

REQ-PROC-032 scribble-content ACs. AUDIT-ONLY. Verification standard: producer artifact
*specifies* required behavior correctly AND named consumers read it where the AC says.
The only scribble (`therapist/data_transfer`, `status: draft`) is pre-feature — judged
against the generator SPEC; runtime mismatch is an observation, not a gap.

---

## AC-21 — Scribble–coder contract is single-sourced

Verdict: COVERED

- `requirements_tasks/SKETCHES_README.md:33-72` has the **"What a Scribble Commits To"**
  section declaring itself the single normative source: `SKETCHES_README.md:35`
  "The canonical enumeration below is the **single normative source** — no other artifact
  restates these two lists."
- Two disjoint sets present and complete:
  - LOCKED-IN L1–L15 (`SKETCHES_README.md:37-55`) covers all 15 required items: screen
    list+order (L1), Flutter widget choices (L2), information hierarchy (L3), copy text (L4),
    canon labels (L5), personas-applied+constraint (L6), T1/T2 rules cited (L7),
    persona-derived sizing as named token references (L8), required states empty/loading/error
    (L9), navigation pattern (L10), dialog pattern (L11), component-library usage (L12),
    information-model boundary (L13), design decisions (L14), accessibility intent (L15).
  - RE-DERIVE D1–D8 (`SKETCHES_README.md:57-68`) covers exact token values (D1), colors (D2),
    accessibility implementation (D3), animation curves/timing (D4), responsive breakpoint
    mechanics (D5), hover/focus/pressed states (D6), BLoC/behaviour wiring (D7), cross-persona
    constraints not visible (D8).
- "No other artifact restates the two lists" — verified by grep for list strings ("Screen list
  and order", "Animation curves and timing", etc.). The only full restatements are:
  - `requirements.md:2852-2879` — the **generated** merge of SKETCHES_README via
    `merge_requirements.py` (header at `requirements.md:3-5` declares originals are source of
    truth). Derivative copy, not an independent normative source.
  - The generator CONTRACT BLOCK template (`ui-scribble-generator.md:106-112`) — explicitly an
    *emitted output* labelled "verbatim from requirements_tasks/SKETCHES_README.md" (line 101);
    not a competing source.
  - Consumer skills/agents cite the *keys* L1–L15/D1–D8 with a source pointer back to
    SKETCHES_README (e.g. `ui-scribble-handoff-emitter.md:96-98`), not a restated enumeration.
- The therapist/data_transfer requirements.md table match is the REQ-PROC-032 AC text itself.

---

## AC-22 — CONTRACT BLOCK present in scribble output

Verdict: COVERED

- Generator emits the full CONTRACT BLOCK into `index.html` verbatim from SKETCHES_README:
  `ui-scribble-generator.md:97-114` (step 1c) with dual framing — REVIEWER line ("Critique
  LOCKED-IN … do NOT critique RE-DERIVE", line 103) and CODER line ("Implement LOCKED-IN …
  as shown; RE-DERIVE items … from doc/presentation/ and the token registry regardless of
  what the scribble depicts", line 104).
- Compact per-screen variant specified: `ui-scribble-generator.md:181-188` (step 13b)
  "SCREEN CONTRACT (LOCKED-IN for this screen) … RE-DERIVE: … see doc/presentation/ + token
  registry".
- Not hand-authored: enforced by Rule `ui-scribble-generator.md:246` "MUST NOT hand-author
  CONTRACT BLOCK content — copy verbatim from SKETCHES_README" and Anti-Pattern line 35.
- Output contract confirms both: `ui-scribble-generator.md:226` (index CONTRACT BLOCK) and
  `:227` (per-screen "compact CONTRACT BLOCK").
- Observation (not a gap): the draft `therapist/data_transfer/v2/` scribble predates the
  feature — `grep -c "CONTRACT BLOCK" index.html` = 0, no `SCREEN CONTRACT` in any screen.
  Plan §"Critical fact" accounts for this; judged against the SPEC, which is correct.

---

## AC-23 — Contract block in flutter_handoff.yaml

Verdict: COVERED

- Emitter produces a top-level `contract:` block with `locked_in`, `re_derive`, and a source
  pointer: `ui-scribble-handoff-emitter.md:54-57` (example) and `:96` (spec) "Always emit at
  top-level. Use the exact item keys L1–L15 and D1–D8 … Set `source:` to
  `requirements_tasks/SKETCHES_README.md#what-a-scribble-commits-to`." Rule at `:135`,
  Anti-Pattern at `:34`.
- Emitter produces a top-level `design_decisions:` block propagating metadata's
  `design_decisions[]`: `ui-scribble-handoff-emitter.md:59-61` (example) and `:98` (spec)
  "Propagate `design_decisions[]` from `metadata.yaml` verbatim … Do not omit the key."
- Schema validates both blocks: `.claude/schemas/flutter_handoff.yaml:44-63` (`contract:`
  with `locked_in`/`re_derive`/`source` keys) and `:64-80` (`design_decisions:` array with
  `decision` required / `reason` optional). Schema named as consumer at file header `:8`.
- Emitter validates against the schema before reporting: `ui-scribble-handoff-emitter.md:139`.

---

## AC-24 — Coding consumers honor the contract

Verdict: COVERED (minor wording divergence noted)

- code-simple Sketch Gate directs the implementer to read flutter_handoff.yaml's contract
  block: `code-simple/SKILL.md:45` "Read `flutter_handoff.yaml` … locate the top-level
  `contract:` block"; LOCKED-IN "implement exactly as depicted" (`:47`); RE-DERIVE "derive
  from `doc/presentation/` and `tokens.json` **regardless of what the scribble shows**"
  (`:48`).
- code-complex Sketch Gate is equivalent: `code-complex/SKILL.md:37-40`, contract block read
  at `:37`, LOCKED-IN at `:39`, RE-DERIVE at `:40`.
- Both gates fire only for Presentation tasks with an approved scribble and require each
  scribble-element note to state its contract side (`code-simple/SKILL.md:50`,
  `code-complex/SKILL.md:42`).
- Minor divergence (does not defeat the AC): code-complex `:40` omits the "regardless of what
  the scribble shows" clause that AC-24 phrases as "regardless of whether the scribble depicts
  them"; code-simple `:48` includes it verbatim. code-complex still lists the re-derive items
  as derived from doc/+tokens, so the operative instruction holds, but the explicit
  "regardless" guard is weaker on the complex path.

---

## AC-25 — Verifier scope anchored to the contract

Verdict: COVERED

- ui-verify-flutter reads `contract.locked_in` / `contract.re_derive` first:
  `ui-verify-flutter/SKILL.md:40-44` (step 2c).
- Evaluates ONLY locked-in items: `SKILL.md:64` "If the key is in `contract.locked_in`:
  verify … Divergence → `coder_defect`"; `:65` "If the key is in `contract.re_derive`:
  record as `out_of_contract` — do NOT evaluate against the scribble."
- Phase 3 repeats the split: locked-in checks → `coder_defect` (`:71-76`); re-derive items
  "do NOT evaluate against scribble, record as `out_of_contract`" (`:77-80`).
- Taxonomy makes the boundary explicit in every finding: `SKILL.md:128` "Every finding must
  state its contract side (`locked-in` or `re-derive`) in the entry"; report table column
  "Contract Side" (`:105`), Findings sections `coder_defect`/`out_of_contract` (`:110-118`),
  Phase 5 classification (`:141-144`). Legacy default is conservative (all locked-in, `:44`).
- contract.yaml restates the consumer role: `ui-verify-flutter/contract.yaml:5-6`, `:43-47`.

---

## AC-26 — Persona sizing as token reference; accessibility intent locked

Verdict: COVERED

- Persona-derived sizing as named token references (not literal px), literal resolves from
  registry: `SKETCHES_README.md:48` (L8) and `:70` note; generator step 6
  (`ui-scribble-generator.md:117`) "every interactive element gets
  `min-height: var(--min-tap-target)` … **NEVER use literal pixel values**"; Rule `:244`;
  Anti-Pattern `:32`.
- Accessibility INTENT locked and present in generated scribbles: `SKETCHES_README.md:55`
  (L15) and `:72` note; generator step 6b (`ui-scribble-generator.md:124-128`) requires
  semantic element, ARIA role identity (`a11y-intent: role=`), alt-text obligation,
  accessible-name presence on every interactive/informational element.
- Accessibility IMPLEMENTATION (focus order, announcements, WCAG) is RE-DERIVE:
  `SKETCHES_README.md:63` (D3); generator step 6b `:130` "Do NOT specify focus order, tab
  sequence, announcement text, or WCAG conformance — those are D3 RE-DERIVE items"; Rule
  `:245`; Anti-Pattern `:34`.
- Observation (not a gap): draft `therapist/data_transfer/v2/` carries no `a11y-intent` and
  no `var(--min-tap` references (pre-feature). Judged against SPEC, which is correct.

---

## AC-27 — Rule-application audit trace

Verdict: COVERED

- Generator emits a per-screen machine-readable RULE AUDIT TRACE: `ui-scribble-generator.md:132-143`
  (step 7) — `rule-trace: <T1/T2 rule> → <HTML element/CSS selector> (<enforcement>)`, one
  line per rule application, "do not omit rules that only appear in comments elsewhere".
- Each line binds a claimed rule to a concrete element (not metadata assertion): step 6 `:122`
  "A rule comment without a corresponding HTML enforcement is incomplete"; Anti-Pattern `:36`
  "Citing a T1/T2 rule … with no corresponding HTML element enforcement — the rule-reviewer
  will flag this as a GAP"; Rule `:248` "MUST NOT omit the RULE AUDIT TRACE from screens that
  have T1/T2 rule citations".
- Verifiable by rule-reviewer and human: trace is an HTML comment block in each screen
  (machine-readable), output contract `:227` lists "RULE AUDIT TRACE" inside the per-screen
  mapping block.
- Observation (not a gap): draft `therapist/data_transfer/v2/` has no `RULE AUDIT TRACE` /
  `rule-trace:` lines (pre-feature). Judged against SPEC, which is correct.

---

### Summary count

COVERED: 7 (AC-21, AC-22, AC-23, AC-24, AC-25, AC-26, AC-27) · PARTIAL: 0 · NOT_COVERED: 0
(AC-24 carries a noted minor wording divergence in code-complex; not severe enough to drop below COVERED.)
