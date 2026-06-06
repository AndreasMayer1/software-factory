# Consolidation — remaining scribble-content work, mapped to the real producers

**Task:** TASK-PROC-032-10 · **Date:** 2026-05-31 · **Model:** Opus 4.8
**Purpose:** Durable capture of session-held state so it survives session loss. Maps the still-untasked scribble-CONTENT work (Q1/Q2 substance from iterations 1–6) onto the `ui-scribble-*` skills/agents that the REQ-PROC-044 program actually built. This document is the intended input to the REQ-PROC-032 `requ-explore` pass that will encode these as ACs and seed implementation tasks.

> Answers the developer's question directly: **the scribble-workflow *implementation* tasks for the content bundles have NOT been created.** The REQ-PROC-044 program built the *infrastructure* (skill/agent split, contract mechanism, rubric, revision channel, heuristics corpus). The *content* that motivated TASK-PROC-032-10 (Q2 contract + several content skills) is not yet tasked. This file states exactly what exists, what's missing, and the one unblocking step.

---

## 1. Ground truth — what exists on disk (verified 2026-05-31)

### Skills (`.claude/skills/`)
- `ui-scribble-iterate` (53 lines) — thin orchestrator
- `ui-scribble-auto-review` (30) — spawns the 3 reviewers
- `ui-scribble-feedback-classify` (34)
- `ui-scribble-approve-handoff` (26)
- `ui-create-scribble-improve` (pre-existing, vision-eval loop)

### Agents (`.claude/agents/`)
- `ui-scribble-generator` (119) — carries the full original MUST-DO generation list
- `ui-scribble-rule-reviewer` (28)
- `ui-scribble-heuristics-reviewer` (31) — corpus PROVISIONAL (see §3)
- `ui-scribble-persona-walker` (28)
- `ui-scribble-feedback-classifier` (31)
- `ui-scribble-handoff-emitter` (36)

### Q1 heuristics corpus (`doc/presentation/heuristics/`) — EXISTS
`README.md`, `nielsen_usability.md`, `universal_design.md`, `microinteractions.md`, `dark_patterns.md`, `motion_as_function.md`. So the Q1 UX-protocol ports (iteration 2 §3.4, items A–F) landed as doctrine the heuristics-reviewer consumes.

### Contract mechanism — EXISTS
`.claude/schemas/` (goal_metadata, requirements_frontmatter, revision_target, flutter_handoff, +others); per-skill `contract.yaml`; `scripts/quality/check_skill_contracts.py`; factory map. (AC-05 schema↔corpus drift currently being fixed by the developer via TASK-PROC-044-15.)

---

## 2. What is DONE vs MISSING per original bundle

| Bundle (iteration 4 §9) | Status | Evidence |
|---|---|---|
| **SCRIBBLE-SPLIT** | ✅ DONE | 044-07 completed; orchestrator + 3 sub-skills + 6 agents exist (rubric revised 4→3+agents; supersedes file-09 §11 cut — see iteration 6 §2) |
| **Q1-AGENTS** (UX-protocol ports + persona walk + reviewers) | 🟡 MOSTLY DONE | heuristics corpus exists; heuristics-reviewer + persona-walker + rule-reviewer exist. **Missing:** corpus reconciliation (PROVISIONAL flag), iteration-fatigue detection, inter-version diff + HTML toggle (D44), auto-review brief (D46), persona-conflict/DDR link (D45) — none verified present |
| **Q2-CONTRACT** | ❌ MISSING | no "what a scribble commits to" section in SKETCHES_README; generator emits no CONTRACT BLOCK; no reviewer pre-brief framing; Sketch-Gate edits in code-simple/complex not done; ui-verify-flutter scope-restriction to locked items not done; rule-application audit log not done; L8 named-token refinement NOT applied (generator still hardcodes `min-height: 48px`); contributing_requirements / participating_flows / flow_navigation.yaml not confirmed |
| **NEW-SKILL** (claude-create-agent + claude-modify-agent) | ❓ PARTIAL | rubric codification (044-08) folded agent-creation guidance into claude-create-skill/claude-modify-skill per iteration-6 §3; whether standalone claude-create-agent/claude-modify-agent skills exist is unverified |
| **DOMAIN-VOCAB** (port to 6 existing agents) | ❓ UNVERIFIED | not checked this session |
| **VISUAL-VALIDATE** (`ui-visual-validate`, Opus vision) | ❌ MISSING | skill does not exist |
| **BREAKPOINTS** (persona `device_classes` → multi-breakpoint) | ❌ MISSING | skill/field does not exist |
| **INSPIRATION** (`inputs/inspiration.yaml`) | ❌ MISSING | not present |
| **PREBRIEF** (Phase-0.5 reviewer pre-brief) | ❌ MISSING | not present |
| **CROSS-FEATURE** (Haiku consistency check) | ❌ MISSING | not present |

---

## 3. The signal already embedded in the code

`ui-scribble-heuristics-reviewer.md` line 12 states verbatim:

> "Corpus status: PROVISIONAL pending the REQ-PROC-032 requ-explore reconciliation with the TASK-PROC-032-10 Q1-AGENTS design. Apply what is documented; do not invent beyond it."

The implementation itself points at the missing step. The infrastructure is built to *expect* a `requ-explore` pass on REQ-PROC-032 that:
1. Encodes the adopted Q1/Q2 decisions as ACs/sections in REQ-PROC-032 (it has 20 ACs today, none covering the contract or the heuristics corpus).
2. Finalizes the heuristics corpus (removes the PROVISIONAL flag).
3. Aligns AC language with the real `ui-scribble-*` producer names.

---

## 4. The Q2 contract content (the load-bearing missing piece)

This is the substance of the exploration's original Q2 and is wholly untasked. From iteration 1 §4.1 (as refined by iteration 4 §4.5 web research):

**LOCKED-IN (15 items)** — scribble commits, coder implements as shown:
L1 screen list+order · L2 Flutter widget choices · L3 information hierarchy · L4 copy text · L5 canon labels · L6 personas applied+constraint · L7 T1/T2 rules cited · L8 persona-derived sizing **as named token reference** (e.g. `min-tap-target`, NOT literal 48px — generator currently violates this) · L9 required states (empty/loading/error) · L10 navigation pattern · L11 dialog pattern · L12 component-library usage · L13 information-model boundary · L14 design decisions · **L15 accessibility intent** (semantic HTML, ARIA roles, alt-text, accessible-name)

**RE-DERIVE (8 items)** — coder derives from doc/ + tokens.json:
D1 exact token values · D2 colors · D3 accessibility *implementation* (focus order, announcements, WCAG verification) · D4 animation curves/timing · D5 responsive breakpoint mechanics · D6 hover/focus/pressed states · D7 BLoC/behavior wiring · D8 cross-persona constraints not visible in scribble

**Surfacing (iteration 4 §4.3 B1–B5 + reviewer framing from iteration 2 §1.5):**
- B1 — consolidated "What a Scribble Commits To" section in SKETCHES_README (single source of truth)
- B2 — CONTRACT BLOCK at top of scribble `index.html` + per-screen, with dual framing (FOR THE HUMAN REVIEWER: critique these / don't critique those; FOR THE FLUTTER CODER: implement locked / re-derive deferred) — emitted by `ui-scribble-generator`
- B3 — `contract:` block in `flutter_handoff.yaml` (locked_in/re_derive lists) — emitted by `ui-scribble-handoff-emitter`
- B4 — Sketch-Gate sentence rewrite in `code-simple` + `code-complex` (read the contract; implement locked, re-derive the rest)
- B5 — `ui-verify-flutter` classifications anchored to the contract (locked deviation = coder bug; re-derive item = out_of_contract, not opined on)
- Plus: rule-application audit log (D32), flow_navigation.yaml (D20), contributing_requirements + participating_flows (D29/D30), auto-discovery script reading `requirements_matrix.md` (D40; D41/D42 dropped per iteration 5 §3).

---

## 5. The one unblocking step (unchanged across iterations 5 & 6)

The content bundles are `impl` tasks whose natural parent is **REQ-PROC-032** (status active, 20 ACs, none covering the contract/heuristics content). `task-create §3c` redirects any standalone `impl` task under a requirement with uncovered ACs to `task-derive-from-requ`, which would decompose the *old* ACs — not these decisions.

**Factory-correct sequence:**
1. **`requ-explore` on REQ-PROC-032** — fold the adopted Q1/Q2 decisions (this file §4 + the 32-decision matrix in iterations 3–4) into REQ-PROC-032 as new ACs/sections; align with the real `ui-scribble-*` producers; finalize the heuristics corpus (clear PROVISIONAL).
2. **`task-derive-from-requ` on REQ-PROC-032** — emit grounded impl tasks for: Q2-CONTRACT (B1–B5 + audit log + L8 fix), VISUAL-VALIDATE, BREAKPOINTS, INSPIRATION, PREBRIEF, CROSS-FEATURE, and the Q1-AGENTS content remnants (fatigue detection, inter-version diff+toggle, auto-review brief, persona-conflict/DDR link). Several will be small edits layered onto the existing `ui-scribble-*` producers rather than greenfield work.
3. Add the derived tasks to `task_ordering_priority_override.txt` if they must precede 0.0.1 resumption (per total-cost framing, iteration 5 §7).

This is "Path 1" from iteration 6 §5. It keeps the Q1/Q2 substance owned by the scribble requirement that motivated it, and the existing infrastructure already expects it.

---

## 6. Closure status of TASK-PROC-032-10

The four explore ACs are genuinely met (Q1 and Q2 are thoroughly answered across iterations 1–6; problem-space reframed as contract-locality; decisions framed; uncertainties stated honestly). The exploration's *analytical* mandate is fulfilled.

What remains is *execution*, which is correctly owned by the requ-explore→derive pass on REQ-PROC-032, not by keeping this explore task open for more rounds. Recommendation: after this consolidation doc is committed, this task can be completed — the remaining work lives as the REQ-PROC-032 cycle, not as open analysis.

---

## 7. Pointers (for whoever runs the requ-explore pass)

- Decision matrix: iterations 3 (`_06`) §7, 4 (`_09`) §8 — the D1–D47 list with statuses
- Q2 contract detail: iteration 1 (`_01`) §4 + iteration 4 (`_09`) §4.5 (web-research refinements R1/R2)
- Redundancy resolutions: `_10` (R3 collapse verification_seeds into flutter_handoff; R9 claude-modify-agent)
- Token/session cuts: `_13` (which producers are agents vs sub-skills — already realized by 044-07)
- Reconciliation with what actually shipped: iteration 6 (`_15`)
- This consolidation: `_16` (you are here)
- The infrastructure mechanism spec: TASK-PROC-044-02's outputs in `factory_quality/tasks/2026-05-29_explore_skill-interface-contracts-mechanism/`
