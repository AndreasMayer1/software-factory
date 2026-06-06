# Redundancy Check — iteration-3 + iteration-4 plan

**Task:** TASK-PROC-032-10 · **Date:** 2026-05-29 · **Model:** Opus 4.7
**Purpose:** Per user instruction in `2026-05-28_07_feedback.md`: *"we have to check for redundancies again — we don't want the process contain steps that do basically the same thing in a slightly different way."*
**Method:** Inspect each candidate from `2026-05-29_09_design_thinking_iteration_4.md` §12. For each: name the overlap, decide *collapse / differentiate-and-keep / keep-as-is*, and (if differentiate-keep) write the sharp boundary.

> Bottom line up front: of 10 candidates, **3 are real redundancies and should collapse**, **1 has a useful gap-fill opportunity** (new sub-skill), **6 are differentiation-keep with sharper boundaries documented**. No item is "true redundancy = drop one". The plan is leaner than expected.

---

## R1 — Phase-2 chain of reviewers (auto-review + ux-protocol-reviewer + persona-embodiment-reviewer)

**Three reviewers operating in sequence on the same scribble v(n)**:

| Reviewer | Lens | Source |
|---|---|---|
| Phase-2 auto-review | Rule-based: ACs covered, personas applied, T1/T2 rules applied, exception paths, info-model consistency, YAGNI state gate | Iteration 1 §4.1 / current skill |
| Phase-2b ux-protocol-reviewer (NEW) | Generic UX principles: Nielsen heuristics, Universal Design (Mace), Affordance/Microinteractions (Saffer), Dark Patterns, Motion-as-function | Iteration 2 §3.4 / Han ports |
| Phase-2.5 persona-embodiment-reviewer (NEW) | Per-persona walk: read persona + scenario + flow Domain Concepts; embody and walk through screens | Iteration 2 §2.2 + iteration 3 §4.2 |

**Potential overlap**:
- Persona-spectrum (Universal Design Principle 2) is in ux-protocol-reviewer's Protocol 2 AND is the entire purpose of persona-embodiment-reviewer
- Recognition-vs-recall (Nielsen Heuristic 6) is in ux-protocol-reviewer's Protocol 3 AND surfaces during persona embodiment for cognitive-trait personas
- Affordance/signifier checks (ux-protocol-reviewer Protocol 4) AND auto-review's `metadata.yaml.flutter_component_mapping` check both confirm "is this element interactive in a recognizable way"

**Verdict: differentiate-and-keep — but draw sharp lens boundaries.**

The three reviewers are NOT redundant because they answer different questions:

- **Auto-review** = "does the scribble satisfy our internal contract?" (project-specific rules)
- **UX-protocol-reviewer** = "does the scribble satisfy generic UX principles independent of our personas?" (universal heuristics)
- **Persona-embodiment-reviewer** = "does the scribble work for each of OUR personas in their lived context?" (project-specific empathy)

**Sharp exclusive scopes (write this into each agent's frontmatter description):**

| Reviewer | Owns | Explicitly NOT |
|---|---|---|
| Auto-review | ACs, T1/T2 rules, info-model consistency, exception coverage, component mapping completeness, YAGNI state gate | Nielsen heuristics; persona embodiment narrative |
| UX-protocol-reviewer | Nielsen 10, Universal Design 7, Affordance/Microinteractions (Saffer), Dark Patterns, Motion-as-function, generic-persona-spectrum (motor/cognitive/visual/temporary/situational as categories) | Project personas by name; T1/T2 rules; AC coverage |
| Persona-embodiment-reviewer | Per-named-persona walk through screens citing persona-trait + screen element; conflict surfacing (D45) | Generic heuristics; rule application; component mapping |

**Action**: bundle sharp-scope tables into the Q1-AGENTS impl task. Each new agent's prompt opens with its scope-owned list AND the scope-not-owned list. Anti-pattern guard added: "If a finding would be more naturally produced by sibling reviewer X, defer to X."

---

## R2 — Three "what changed and why" artifacts (diff + brief + APPROVAL_TRAIL)

**Three artifacts about decisions and changes**:

- **6.3 inter-version diff** — mechanical structural diff between v(n) and v(n+1) (added/removed screens, changed copy, rule-application changes); has HTML toggle for visual highlight
- **6.7 auto-review brief** — agent's selective note: "I prioritized fixing X; please re-walk Y because Z"; written by the auto-reviewer per version
- **6.1 APPROVAL_TRAIL.md** — aggregated decision history across all versions of a scribble (rejected alternatives, key trade-offs, "why this design"); written at approval time, single file per scribble

**Verdict: differentiate-and-keep — they answer different questions across different time horizons.**

| Artifact | Question | Audience | Cycle |
|---|---|---|---|
| Diff | "what changed between v3 and v4?" | Reviewer | Per version |
| Brief | "what should I look at this round?" | Reviewer | Per version |
| APPROVAL_TRAIL | "why is the final design this way?" | Future iterator, coder, next scribble cycle | Once at approval (with version-history references) |

**Coupling discipline (to avoid divergence)**:
- The brief MUST link to the diff (lives in the same `v(n+1)/` folder; cross-link them)
- The APPROVAL_TRAIL MUST aggregate the briefs + per-version `feedback.md` files (it's a synthesis, not an independent narrative)
- The APPROVAL_TRAIL script reads brief.md + diff.md + feedback.md across all versions to produce its synthesis

**Action**: bundle the cross-link convention into Q1-AGENTS (which owns the auto-reviewer and approval-handoff steps). Acceptance criterion: "the brief contains a hyperlink to the diff; the APPROVAL_TRAIL contains hyperlinks to all version-feedback and version-brief files."

---

## R3 — Four machine-readable handoff artifacts (flutter_handoff + contract block + flow_navigation + verification_seeds)

**Four post-approval YAML artifacts**:

| Artifact | Lives at | Carries |
|---|---|---|
| `flutter_handoff.yaml` | `<scribble_path>/v{n}/` | Per-element mapping (html_selector → flutter_widget → material3_variant → persona_constraints → rules_applied) |
| `contract:` block (within flutter_handoff.yaml) | top-level in `flutter_handoff.yaml` | LOCKED-IN / RE-DERIVE lists (per Q2) + source pointer to SKETCHES_README |
| `flow_navigation.yaml` | `requirements_user_needs/user_flows/<flow>/` (NOT in scribble folder) | Per-flow navigation edges, escape paths, back-stack policy |
| `verification_seeds.yaml` (D28) | `<scribble_path>/v{n}/` | Per-L-item integration-test suggestions |

**Real redundancy candidate: `verification_seeds.yaml` and `flutter_handoff.yaml` both live in the same folder and both describe per-element commitments — could they collapse?**

Analysis:
- `flutter_handoff.yaml` is consumed by `code-simple` / `code-complex` (implementation guidance) and `ui-verify-flutter` (structural check)
- `verification_seeds.yaml` is consumed by `code-test` / `code-run-integration` / `ui-visual-validate` (test scaffolding)
- The two have orthogonal consumers but overlapping content (both reference html_selector and flutter_widget)
- Collapse cost: a single file becomes the source-of-truth for both implementation and verification — easier to keep in sync
- Collapse risk: file grows; readers of either side load the whole thing

**Verdict: COLLAPSE.** Make `verification_seeds:` a top-level block within `flutter_handoff.yaml`, alongside `contract:` and `screens:`:

```yaml
# flutter_handoff.yaml (consolidated)
contract:
  source: requirements_tasks/SKETCHES_README.md#what-a-scribble-commits-to
  locked_in: [...]
  re_derive: [...]
flow_navigation_source: requirements_user_needs/user_flows/<flow>/flow_navigation.yaml   # external reference, not embedded
screens:
  - screen: 01_…
    elements: [...]
verification_seeds:
  - locked_item: L1_screen_list
    test_kind: screen_existence_smoke
    suggested_test_file: integration_test/<feature>/screens_smoke_test.dart
  - locked_item: L9_required_states
    test_kind: state_walk
    suggested_test_file: integration_test/<feature>/state_walk_test.dart
  ...
```

**`flow_navigation.yaml` stays external** — it lives in the flow folder (correct ownership), not the scribble folder. The handoff yaml points to it by path.

**Action**: bundle the consolidation into Q2-CONTRACT (which already touches the handoff yaml schema) and VISUAL-VALIDATE (which consumes verification_seeds). Decision D28 amended: produce a `verification_seeds:` block inside flutter_handoff.yaml, not a separate file.

---

## R4 — Pre-brief vs auto-review brief

**Two "what to focus on" artifacts at different boundaries**:

| Artifact | Boundary | Audience | Cost |
|---|---|---|---|
| Pre-brief (Phase 0.5, D17) | BEFORE Phase-1 generation | User (scope confirmation) | ≤300 words, 1-page read |
| Auto-review brief (D46) | AFTER Phase-2 auto-review, BEFORE Phase-3 user review | User (focus confirmation for review) | Selective; per version |

**Verdict: keep both — different boundaries, different decisions enabled.**

- Pre-brief enables "stop scope mismatch before expensive generation"
- Auto-review brief enables "stop reviewer wasting cycles on unaffected screens"

**Consistency requirements** (so the two don't drift into incompatible formats):

| Field | Pre-brief | Auto-review brief |
|---|---|---|
| Header | Date + requirement ID | Date + version ID |
| "What's covered" | Screens to be generated | Screens regenerated this round |
| "What's out of scope" | Out of scope for this round | Unchanged screens (with version reference) |
| "What to focus on" | Open assumptions to confirm | Specific re-walk requests + persona-conflict markers |
| Verbosity bound | ≤300 words | ≤300 words |

**Action**: shared "BRIEF" structural template in `SKETCHES_README.md` § "Brief Documents". Both PREBRIEF and Q1-AGENTS impl tasks reference it.

---

## R5 — Cross-feature consistency check vs flow-walk per-flow validation

**Two cross-scribble checks**:

| Check | What it does | Trigger |
|---|---|---|
| CROSS-FEATURE (D19) | Compare component choices across scribbles of features sharing a flow ("Feature X uses [FilledButton] for confirmation; Feature Y on the same flow uses [TextButton] — intentional?") | Phase-2 of any scribble whose flow has ≥2 contributing requirements with their own scribbles |
| Flow-walk per-flow validation (D39) | For each flow the scribble participates in: walk the scribble screens in flow-step order, verify intent supported, emit revision_request if a flow flaw is revealed | Phase-2 of any scribble with `participating_flows:` |

**Overlap**: both traverse multiple scribbles of features sharing a flow.

**Could the cross-feature check be folded into the per-flow walk?**

Analysis:
- The flow-walk is per-flow (walks one flow at a time)
- The cross-feature check is comparison (compares choices between sibling scribbles)
- Folding: during the per-flow walk, when crossing from feature X's scribble into feature Y's scribble (at the boundary step), check that the shared-flow component choices match
- Benefit: one fan-out across scribbles instead of two
- Risk: the cross-feature check has its OWN trigger conditions independent of flow walks (e.g. it can fire on scribble approval, not only on flow walk)

**Verdict: differentiate-and-keep, BUT make CROSS-FEATURE a sub-step of the per-flow walk when both are active.**

- When `D39` flow-walk encounters a screen from a sibling feature (`metadata.yaml.feature_path` differs from current scribble's), it triggers the component-choice comparison inline (the CROSS-FEATURE logic runs as a step inside the walk)
- When only CROSS-FEATURE applies (no flow-walk, e.g. cross-feature check on a feature whose scribble doesn't have participating_flows): it runs standalone
- Both are owned by the same Haiku check; the only difference is the trigger

**Action**: CROSS-FEATURE bundle's prompt is rephrased: "If invoked during a per-flow walk: integrate with the walk. If invoked standalone: run the fan-out as today." Decision D19 amended.

---

## R6 — Three escalation/feedback channels (revision_requests + pending_feedback + back-pressure)

**Three channels for "the workflow needs human or upstream attention"**:

| Channel | Triggered by | Goes to | Frequency |
|---|---|---|---|
| Back-pressure protocol (CLAUDE.md §7) | Quality-gate failure (verify-quality RED) | Cycle counter in `plans_and_protocols/cycle_state.json`; at cycle 5 → `automation/pending_feedback/` | Per task |
| `automation/pending_feedback/` | Skill or back-pressure escalation; agent asks the developer a question | Developer file-based reply | Per question |
| `revision_requests/` (D38, NEW) | Downstream skill discovers upstream artifact needs revision (coder→scribble, validator→scribble, scribble→flow) | Upstream skill's owner; queued for orchestrator scan | Per discovery |

**Real redundancy?** No — they handle different cases:
- Back-pressure = "gate failed, stuck in loop, escalate after N tries"
- pending_feedback = "open developer-facing question, halt until answered"
- revision_requests = "upstream artifact needs revision; no human required if upstream agent can autonomously revise"

But the channels overlap operationally:
- All three are file-based
- All three need orchestrator-scanning at session start
- All three follow a 5-cycle-then-escalate-to-human pattern (or should)

**Verdict: NEST not collapse.**

Proposed structure:
```
automation/
  pending_feedback/
    <task-id>/
      question.md
      answer.md
    revision_requests/                  # NEW (D38)
      <originator-skill>/
        <timestamp>_<artifact_id>.yaml
  cycle_state.json                      # back-pressure counter (existing)
```

Single channel root (`automation/`), structured subfolders for each pattern, shared scanning logic in `claude-route`. The 5-cycle escalation rule applies uniformly: a revision_request that bounces ≥5 times surfaces as a `pending_feedback/<task-id>/question.md` automatically.

**Action**: document this nesting in CLAUDE.md §7. The NEW-EXPLORATION (D37) ratifies the channel format; until then Q2-CONTRACT lands a minimal `revision_requests/` schema as a stub.

---

## R7 — Three scribble locators (contributing_requirements + participating_flows + feature_path)

**Three fields in scribble `metadata.yaml`**:

| Field | What it locates |
|---|---|
| `feature_path:` (D36, e.g. `therapist/data_transfer`) | The Flutter feature folder the scribble mirrors |
| `contributing_requirements:` (D29) | All requirements that contribute UI to this scribble (primary + cross-cutters) |
| `participating_flows:` (D30) | All user flows that touch this scribble's screens |

**Derivation analysis**:
- `feature_path` → primary requirement: derivable via convention (the requirement whose feature is `<feature_path>` is the primary owner). Strict 1:1 by lint.
- `feature_path` → contributing_requirements: NOT derivable (cross-cutters are outside the primary feature)
- `contributing_requirements` → participating_flows: PARTIALLY derivable (union of each requirement's `implements_flows`). Edge case: a scribble might participate in a flow not via any of its contributing requirements (rare but possible — e.g. it's part of an onboarding flow that has no requirement-of-its-own yet)
- `participating_flows` → contributing_requirements: NOT derivable (a flow lists `serves_requirements:` but a scribble might use a subset)

**Verdict: keep all three — none is fully derivable from the others.**

But add discipline:
- **Auto-discovery script** (per D40) computes `contributing_requirements` from `feature_path` + `participating_flows`'s `serves_requirements:` field; **user can override**, but lint warns on discrepancy
- **Consistency lint**: `contributing_requirements` MUST contain a requirement whose feature is `<feature_path>` (the primary). If absent, fail.
- **Documentation**: SKETCHES_README explicitly states the three fields' purposes and derivation paths, so future contributors don't mistake them as duplicates.

**Action**: bundle into Q2-CONTRACT (which already owns the metadata schema). Add the consistency lint to the scribble–feature parity check (D35).

---

## R8 — Three post-implementation UI skills (ui-verify-flutter + ui-improve-flutter + ui-visual-validate)

**Three skills running after Flutter implementation**:

| Skill | What it checks | How | Cost |
|---|---|---|---|
| `ui-verify-flutter` (existing) | Structural match of impl vs scribble (widget types, screen existence, persona constraints — locked-only per D11) | Code-only (no vision, no screenshots) | Low (existing) |
| `ui-improve-flutter` (existing) | Visual polish on a specific screen — colors, spacing, alignment, accessibility flags | Human-initiated; optional vision (developer screenshot) | M, max 5 files |
| `ui-visual-validate` (NEW, D12) | Automated post-impl visual check on integration-test screenshots; flags token violations, a11y impl gaps, drift | Vision + Opus; runs on CI cadence or explicit invocation | H (Opus + multiple screenshots) |

**Verdict: keep all three — sharp, non-overlapping scopes.**

The boundaries (write into each skill's frontmatter description):

| Skill | Owns | NOT |
|---|---|---|
| `ui-verify-flutter` | Locked-in items (L1–L15) structural check via code inspection; outputs `comparison.md` | Visual rendering; token values; accessibility implementation depth |
| `ui-improve-flutter` | Targeted polish iteration on a specific screen the developer flagged; can accept a developer screenshot | Automated regression scanning; cross-feature consistency; structural verification |
| `ui-visual-validate` | Automated screenshot-based check on integration-test outputs across all approved scribbles; advisory regression flags | Active polish work (that's `ui-improve-flutter`); structural code-only check (that's `ui-verify-flutter`) |

**No collapse**. The trigger conditions, costs, and outputs are genuinely different.

**Action**: bundle the boundary tables into Q2-CONTRACT (verifier scope clarity per D11) and VISUAL-VALIDATE (new skill's frontmatter).

---

## R9 — Three skill-management skills (`claude-create-skill` + `claude-modify-skill` + new `claude-create-agent`) — and the gap

**Three management skills**:

| Skill | What it does |
|---|---|
| `claude-create-skill` (existing) | Creates new skills with correct naming, structure, INDEX.md/factory_flows.md sync |
| `claude-modify-skill` (existing) | Modifies existing skills, syncs INDEX.md/factory_flows.md |
| `claude-create-agent` (NEW, D22) | Creates new agents with naming scheme + allowed_tools heuristic + when-to-create rule |

**Gap identified**: there is no `claude-modify-agent` skill.

This matters because:
- DOMAIN-VOCAB (D9) needs to edit 6 existing agents to add Domain Vocabulary + Anti-Patterns sections
- Q1-AGENTS will create new agents that may need future edits (vocabulary refinement, model upgrades, prompt iteration)
- Han-imported agents (currently only `han-adversarial-validator`) may need adaptation over time

**Options**:
- **Option A**: extend `claude-modify-skill` to handle agents too (treat agents as a skill variant). Probably wrong — different file conventions, different INDEX/registry concerns.
- **Option B**: create a separate `claude-modify-agent` skill. Symmetric with `claude-create-agent`. Cleanest design.
- **Option C**: rely on direct `Edit` calls for agent files; document the editing conventions in the `claude-create-agent` skill but don't enforce them via a modify skill.

**Verdict: gap-fill opportunity. Adopt Option B.** Bundle `claude-modify-agent` into NEW-SKILL (D22) — author both `claude-create-agent` and `claude-modify-agent` as a pair. Cost is small (the modify skill is ~half the size of the create skill).

**Action**: amend D22 — NEW-SKILL produces TWO skills: `claude-create-agent` AND `claude-modify-agent`. DOMAIN-VOCAB (D9) then uses `claude-modify-agent` to retrofit the 6 existing agents.

---

## R10 — DOMAIN-VOCAB retrofit vs Q1-AGENTS greenfield vocabulary

**Two paths to put Domain Vocabulary onto agents**:

| Path | Agents affected | Approach |
|---|---|---|
| DOMAIN-VOCAB (D9) | 6 existing agents (architecture-advisor, implementation-engineer, opus-advisor, quality-checker, setup-optimizer, test-engineer) | Retrofit via `claude-modify-agent` |
| Q1-AGENTS (D16, D18) | 4 NEW agents (scribble-generator, scribble-auto-reviewer, scribble-ux-protocol-reviewer, persona-embodiment-reviewer) | Born with vocabulary via `claude-create-agent` |

**Real redundancy?** No — they target different agent sets. But they SHOULD share the same vocabulary-section style guide so both retrofitted and greenfield agents read consistently.

**Verdict: keep both, anchor to one style guide.**

The style guide (lives in `claude-create-agent` skill, referenced by `claude-modify-agent`):
- Role identity ≤ 50 tokens
- `## Domain Vocabulary` section — 10–25 precise practitioner terms; pass the "15-year practitioner test"
- `## Anti-Patterns` section — 3–8 named anti-patterns with detection criteria
- `## Protocols` (when applicable) — numbered, each protocol describes what it examines
- `## Output` — exact format the agent emits
- `## Rules` — invariants ("Default posture is X", "MUST execute Y", "MUST NOT Z")

**Action**: NEW-SKILL (D22) authors the style guide as part of `claude-create-agent`. DOMAIN-VOCAB (D9) and Q1-AGENTS (D16, D18) reference it as the source-of-truth, ensuring vocabulary placement and Anti-Pattern naming are consistent.

---

## 11. Net effect on the plan

### Decisions that change

| ID | Change |
|---|---|
| D19 (CROSS-FEATURE) | Amend trigger: "if invoked during a per-flow walk, integrate with the walk; if standalone, run fan-out as today" |
| D22 (NEW-SKILL) | Amend output: produce TWO skills — `claude-create-agent` AND `claude-modify-agent` |
| D28 (verification_seeds) | Amend location: not a separate file; becomes a `verification_seeds:` block inside `flutter_handoff.yaml` (collapse with R3) |
| D38 (revision_requests) | Amend placement: subfolder of `automation/pending_feedback/`, not a sibling top-level channel (nesting per R6) |
| D9 (DOMAIN-VOCAB) | Add prerequisite: `claude-modify-agent` (from amended D22) must exist before retrofit can use it |

### Bundle re-shape

- **No bundle is dropped.** All 11 stay.
- **NEW-SKILL** scope widens: two skills instead of one. Effort revised: M-L (was M). Worth doing as a pair since they share design decisions.
- **DOMAIN-VOCAB** now depends on NEW-SKILL (was independent). Sequencing: NEW-SKILL → DOMAIN-VOCAB; DOMAIN-VOCAB no longer parallel to NEW-SKILL.
- **Q2-CONTRACT** loses one file (no separate `verification_seeds.yaml`) but adds the `verification_seeds:` block convention to the flutter_handoff schema. Net zero change in scope.
- **VISUAL-VALIDATE** reads `verification_seeds:` from `flutter_handoff.yaml` instead of from a separate file. Trivial change.
- **CROSS-FEATURE** prompt mentions both trigger modes. Trivial change.

### Net dependency graph (updated)

```
NEW-SKILL ──┬──► Q1-AGENTS ──┐
            │                │
            └──► DOMAIN-VOCAB │
                              ▼
NEW-EXPLORATION ─────────► SCRIBBLE-SPLIT

Q2-CONTRACT (independent)
VISUAL-VALIDATE (independent)
BREAKPOINTS (independent)
INSPIRATION (independent)
PREBRIEF (independent)
CROSS-FEATURE (independent)
```

Q1-AGENTS now waits ONLY on NEW-SKILL (was the case). DOMAIN-VOCAB now waits on NEW-SKILL (new). All other bundles parallel.

### What remains unredundant

After this check, the plan has:
- 3 distinct reviewers (R1) with sharp owned/not-owned scopes
- 3 distinct "what changed" artifacts (R2) with cross-link discipline
- 3 distinct handoff artifacts (R3 — was 4, collapsed to 3 by folding verification_seeds into flutter_handoff)
- 2 distinct briefs (R4) sharing a template
- 1 cross-feature check (R5) with two trigger modes
- 1 nested channel root (R6) with 3 subfolders
- 3 distinct metadata locators (R7) with consistency lint
- 3 distinct post-impl skills (R8) with documented boundaries
- 4 distinct skill-management skills (R9 — was 3, added `claude-modify-agent` gap-fill)
- 1 vocabulary style guide (R10) referenced by both retrofit and greenfield paths

**No item in the plan does the same thing as another item in a slightly different way.** The differentiation is now documented; each consumer knows which artifact / channel / reviewer to use.

---

## 12. Honest assessment

- **R3 collapse** (verification_seeds into flutter_handoff) is the only structural change. It's small and reversible.
- **R9 gap-fill** (adding `claude-modify-agent`) is genuinely new scope but small.
- **The other 8 candidates** were "differentiate-and-keep with sharper boundaries" — this is the right outcome when each reviewer or artifact answers a distinct question. The risk is that the boundaries are written down here but not enforced in the skill prompts. Mitigation: each amendment goes into the relevant impl task's ACs as a "boundary table present in the skill prompt" check.
- **No item was a "true redundancy = drop one".** This is meaningful — it suggests the iteration-3/4 design is reasonably lean already.
- **What the redundancy check did NOT do**: it did not re-question whether each item should EXIST at all. That's a different audit (a YAGNI re-check of the plan), which the user did not request and which would re-open decisions already made.

---

## 13. Next steps

1. Apply the 4 D-amendments above (D9, D19, D22, D28, D38) to the iteration-4 decision matrix mentally — they are reflected here; no re-write of iteration 4 needed.
2. User confirms (or reverses) the R3 collapse + R9 gap-fill (the two items that move material between bundles).
3. Proceed to seed the 11 impl-task `goal.md` files.
4. Tick exploration ACs in TASK-PROC-032-10's goal.md (already ticked by user; re-confirm).
5. `task-complete` on TASK-PROC-032-10.
