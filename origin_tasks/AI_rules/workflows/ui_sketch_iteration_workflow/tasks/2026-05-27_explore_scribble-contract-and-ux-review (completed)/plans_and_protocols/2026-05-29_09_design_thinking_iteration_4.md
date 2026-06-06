# Design-Thinking Iteration 4 — pre-seeding final pass

**Task:** TASK-PROC-032-10 · **Date:** 2026-05-29 · **Model:** Opus 4.7
**Input:** `2026-05-28_07_feedback.md` (round-4 user feedback) + `2026-05-28_08_skill_interface_exploration.md` (meta-exploration agent findings)
**Output to:** this file. §11 finalizes the impl-task seed plan; §12 lists the open redundancy-check item.

> Methodology: address each round-4 feedback point with concrete proposals; fold in the meta-exploration agent's findings (interface contracts, divide-and-conquer, bidirectional feedback); update the decision matrix and impl-task plan. The redundancy-check is a separate deliverable per the user's instruction ("after exploration synthesis, evaluate redundancies in a separate document").

---

## 1. Round-4 input summary

User stance: **another iteration needed; still in exploration mode**; ideation responses + several substantive new asks. Key items:

| # | Topic | Decision |
|---|---|---|
| 1 | **Scribble location** | Move to `requirements_tasks/scribbles/` mirroring `lib/features/` |
| 2 | **Skill-interface meta-exploration** | Spawn an agent to draft + execute the exploration (done — findings in file 08) |
| 3 | **Persona-embodiment scenario discovery** | Use flow's `serves_scenarios:` field, not name-matching |
| 4 | **Flow navigation** | Scribbles span multiple flows; per-flow validation walks; bidirectional flow ↔ scribble feedback |
| 5 | **Cross-cutting discovery** | NOT manual — frontmatter + script |
| 6 | **Ideation responses (round-3 §6.1–6.8)** | Adopt 6.1, 6.3 (with HTML toggle), 6.5 (with VCD trigger), 6.6, 6.7, 6.8; reject 6.2, 6.4 |
| 7 | **Divide-and-conquer** | Yes — modules, smaller skills with clear interfaces |
| 8 | **Redundancy check** | Separate document after this iteration |

---

## 2. New scribble location: `requirements_tasks/scribbles/` mirroring `lib/features/`

### 2.1 Rationale (user's three reasons)

1. **Clean** — scribbles are first-class deliverable artifacts, not buried inside feature requirement folders
2. **Minimal migration effort** — only one scribble exists today (confirmed: `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/scribbles/v1,v2`)
3. **They are requirements** — scribbles describe the UI that requirements imply; they belong to `requirements_tasks/`, not `requirements_user_needs/`. User flow scribble indexes (which aggregate across scribbles) remain under `requirements_user_needs/user_flows/<flow>/` as today.

### 2.2 `lib/features/` structure findings (investigation §)

From `doc/presentation/coding/folder_structure.md` and the actual `lib/features/` tree:

**Top-level feature roots** (5 in current code):
- `client/` — role-specific root for the client persona
- `home/` — role-neutral landing surface (its own feature)
- `more/` — role-neutral overflow / settings entry
- `role_selection/` — role-neutral one-time-setup feature
- `therapist/` — role-specific root for the therapist persona

**Sub-feature pattern** (under role-specific roots): one folder per sub-feature, mirroring the role's surfaces. Examples currently present:
- `client/data_input/`, `client/data_receive/`
- `therapist/clients/`, `therapist/data_receive/`, `therapist/data_transfer/`, `therapist/inbox/`, `therapist/plan_templates/`

**Layer structure inside each feature**: `data/` `domain/` `presentation/` with `presentation/{bloc,widgets,screens}`.

**Naming rules observation**: `folder_structure.md` is dated 2025-02-21 and BRIEF (60 lines, mostly examples). It distinguishes "feature available to all user roles" (e.g. `auth/`, `plans/` per the doc example) from "feature specific for one user role" (e.g. `therapist/plans/`). It does **not** prescribe a formal naming policy (no snake_case rule, no max-depth rule, no scoping rubric for "when does X become its own feature vs a sub-feature of Y"). This is a known gap; the user's iteration-4 ask "Check how this structure is actually built" — current answer is **the policy is informal**.

**Implication for the scribble-location migration**: we need a light policy doc that says "scribble folders mirror `lib/features/` 1:1 by name and hierarchy." When `lib/features/` grows a new feature, the scribble folder for it is created on demand at the parallel path. When the feature is split or renamed, the scribble folder follows. This is a tracking discipline that should be encoded in `SKETCHES_README.md` and verifiable by a small script (`scripts/quality/check_scribble_feature_parity.py`).

### 2.3 Proposed scribble folder structure

```
flutter_app/requirements_tasks/scribbles/
├── _core/                                 # mirrors lib/core/ — for shared-chrome / cross-feature surfaces
│   ├── widget/
│   │   ├── therapist/                     # role-scoped chrome (e.g. navigation bar)
│   │   └── client/
│   └── design_system/                     # rare: scribbles for atom/molecule/organism patterns
├── client/                                # mirrors lib/features/client/
│   ├── data_input/
│   │   ├── v1/
│   │   ├── v2/
│   │   ├── metadata.yaml
│   │   ├── feedback.md
│   │   └── flutter_handoff.yaml
│   └── data_receive/
│       └── …
├── home/                                  # mirrors lib/features/home/
├── more/                                  # mirrors lib/features/more/
├── role_selection/                        # mirrors lib/features/role_selection/
├── therapist/                             # mirrors lib/features/therapist/
│   ├── clients/
│   ├── data_receive/
│   ├── data_transfer/                     # the existing scribble migrates here
│   ├── inbox/
│   └── plan_templates/
└── README.md                              # the migration + parity-with-features policy
```

**`_core/` for shared chrome.** When a scribble is for shared chrome (navigation bar, role-selection-aware app bar) it lives under `_core/widget/<role>/`. This parallels `lib/core/widget/{therapist,client}/`. Avoids the `_shared_scribbles/` ad-hoc folder from iteration-3 §5.4.

**Naming rule (codified)**: **scribble folder path = `requirements_tasks/scribbles/` + (`lib/features/` or `lib/core/` relative path), 1:1, snake_case.** Lint script enforces parity weekly (or on commit if cheap).

**Effect on `contributing_requirements`**: each scribble's `metadata.yaml` still declares which requirements it implements (a scribble in `therapist/data_transfer/` may implement REQ-FUNC-007-01 primarily plus REQ-NFUNC-018-02 cross-cutting). The path no longer encodes the primary owner; the metadata does. Path is solely the feature-mirror.

### 2.4 Migration

Single folder move:
- From: `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/scribbles/`
- To: `requirements_tasks/scribbles/therapist/data_transfer/`

Steps:
1. `git mv` the folder
2. Update `metadata.yaml` in both `v1/` and `v2/` (no path-self-references today)
3. Update REQ-PROC-032 §"Storage and Organization" (SEC-05) + SKETCHES_README.md §"Folder Structure"
4. Find + replace literal-path references in skills (`ui-create-scribble`, `ui-verify-flutter`, `ui-improve-flutter`, `code-simple`, `code-complex` — they all carry `[requirement]/scribbles/` patterns; replace with the new convention)
5. Update the path-discovery logic in skills: today they look in `[requirement_path]/scribbles/` — tomorrow they look in `requirements_tasks/scribbles/<feature_path>/` where `<feature_path>` is derived from the scribble's `feature:` metadata field (added next)

### 2.5 Coder-side guidance: how the implementer knows where to look

The downstream coder (implementation-engineer agent spawned by `code-simple` / `code-complex`) needs to find the right scribble for the Flutter file it's editing. Today it relies on the implicit folder convention. With the new location:

**Bidirectional lookup**:
- **From feature folder to scribble**: `lib/features/<path>/` → `requirements_tasks/scribbles/<same path>/` (by convention, lint-enforced)
- **From scribble to feature folder**: scribble's `metadata.yaml.feature_path: therapist/data_transfer` field declares the mirror target

**Sketch Gate update** (`code-simple`, `code-complex`): "If approved scribble exists at `requirements_tasks/scribbles/<feature_path>/`: read it. The `flutter_handoff.yaml` declares which Flutter files map to which scribble screens via the `feature_path` mirror convention. The verifier (`ui-verify-flutter`) walks the same mirror in reverse."

### 2.6 Edge cases worth surfacing

- **Multi-feature scribbles** (one screen, multiple Flutter features contribute): scribble lives at the **primary feature's** mirror path (the feature that owns the user task). `contributing_requirements` declares the cross-cutters. Decision rule per iteration-3 §5.4 still applies; the *location* is now under the primary feature.
- **No-feature scribbles** (e.g. global empty-state pattern, splash screen): live under `_core/` with a `feature_path: _core/<sub-path>` metadata field.
- **Scribbles for screens that span multiple `lib/features/` folders** (rare, but possible — e.g. a screen embedded by both `home/` and `more/`): primary-owner rule applies. The non-primary feature gets a `<feature>/READS_SCRIBBLE_FROM: <primary-feature-path>` pointer file (or, simpler, no pointer — coder finds via the mirror parity check).

---

## 3. Skill-interface meta-exploration — findings & disposition

### 3.1 Agent verdict

A dedicated exploration task IS justified. Findings file: `2026-05-28_08_skill_interface_exploration.md`. The implicit-interface problem is systemic — 7 pain categories spanning ≥10 sampled skills (code-*, ui-*, ux-*, requ-*, task-*, doc-*).

The agent drafted a `goal.md` for a new task **TASK-PROC-TBD-01** under a new requirement **REQ-PROC-TBD** (final naming: see §11). Effort L, opus_recommended true, type explore, 8 seed questions, multi-round execution model with a prototype phase.

### 3.2 Adopted mechanisms (for future implementation)

The agent's recommendation set:
- **Sidecar `contract.yaml` per skill** (zero token cost at skill load; lint-able)
- **`.claude/schemas/` for shared shapes** (goal.md frontmatter, metadata.yaml, flutter_handoff.yaml — currently shared across ~10 skills with no schema anywhere)
- **Pre-commit lint** (`scripts/quality/check_skill_contracts.py`, ~80 lines, added to `verify-quality`)
- **Structured `handoff:` block** (replace prose "use X next" with grep-able, lint-able structured handoffs)
- **Split-vs-bundle rubric** (added to `claude-create-skill` so the question gets asked at creation time)

These are paper designs; the exploration task validates them via prototypes before any rollout.

### 3.3 Impact on this task's plan

The interface-contracts work is **upstream** of the proposed sub-skill split for the scribble pipeline. Sequence:

1. **Now**: complete TASK-PROC-032-10 (this task) with the Q2-CONTRACT, Q1-AGENTS, etc. bundles authored as PLANS (impl-task seeds), not yet executed
2. **Next exploration**: TASK-PROC-TBD-01 (skill-interface-contracts) authored from the agent's draft + executed
3. **Then**: SCRIBBLE-SPLIT (split `ui-create-scribble` into 4 sub-skills using the new contract mechanism) — uses the contract format that TASK-PROC-TBD-01 ratifies
4. **In parallel with 2/3**: the other bundles from this task (Q2-CONTRACT, Q1-AGENTS, etc.) proceed independently — they don't need the formal contract mechanism to land first; they benefit from it when it does

The agent's proposed sub-skill split (`ui-scribble-generate`, `ui-scribble-auto-review`, `ui-scribble-feedback-classify`, `ui-scribble-approve-handoff`, with a thin `ui-scribble-iterate` orchestrator) becomes a NEW impl-task seed: **SCRIBBLE-SPLIT** (effort L; blocked by SKILL-INTERFACE-CONTRACTS).

---

## 4. Bidirectional feedback patterns — one pattern, three triggers

Adopted from the meta-exploration §5. **Key insight: the three back-flows (coder→scribble, reviewer→flow, validator→scribble) share one structural pattern with three triggers — not three different patterns.**

### 4.1 The pattern

A typed "needs-revision" message with a named originator and a named target-phase, written to a well-known file location. Schema:

```yaml
# .claude/needs_revision/<originator-skill>/<timestamp>_<artifact_id>.yaml
originator: <skill name producing the request>
target_skill: <skill name that owns the upstream artifact>
target_phase: <phase ID in the target skill, optional>
artifact: <path to the upstream artifact needing revision>
reason: <one of: structural | rule_conflict | infeasible | flow_flaw | drift | other>
detail: |
  <prose explanation; specific element / line / observation>
suggested_action: <one-line proposal>
blocks_completion_of: <task ID(s) blocked by this revision request>
```

### 4.2 Three triggers

| Trigger | Originator → Target | What it carries |
|---|---|---|
| Coder can't implement an element | `code-simple` / `code-complex` → `ui-create-scribble` | Specific element + which `doc/` rule it conflicts with + impact on the scribble |
| Reviewer finds a flow flaw via scribble walk | `ui-create-scribble` Phase 4 (feedback classify) → `ux-create-flow` | Which step / Domain Concept the scribble revealed as inconsistent; suggested flow revision |
| Visual-validation finds drift | `ui-visual-validate` → `ui-create-scribble` or coder | Which screen, which element, classification (structural / token / rule) |

### 4.3 File-based channel — reuse `pending_feedback/`

Don't invent a new channel. Use the existing `automation/pending_feedback/` convention with a new subfolder `revision_requests/<originator-skill>/<timestamp>_<artifact_id>.yaml`. `claude-route` scans this at session start (or when a skill is invoked) and surfaces unresolved items.

### 4.4 Escalation discipline

Same 5-cycle back-pressure protocol as `verify-quality` (CLAUDE.md §7). If a revision request bounces ≥5 times, the orchestrator writes a developer-facing question file and pauses.

### 4.5 What this enables

- **Coder→scribble**: when the coder hits an infeasible scribble element, they don't silently deviate (Position A guarantees zero silent deviation). Instead they emit a revision request; the scribble iterates to v(n+1) reflecting the resolution.
- **Reviewer→flow**: scribble approval cycles can REVEAL flow flaws (the screen reads as broken once visualized, even if the prose flow seemed fine). The reviewer emits a revision request to the flow author; the flow iterates; requirements may cascade-update.
- **Validator→scribble**: visual-validation discovers Flutter has drifted from the approved scribble in a way that's not the coder's fault (e.g., the implementation environment changed). The validator emits a revision request; the scribble iterates if the drift is correct, or the implementation is reverted.

### 4.6 Bidirectional flow ↔ scribble feedback — cascade handling

When a scribble walk reveals a flow flaw, the cascade is:

1. Revision request: `ui-create-scribble` → `ux-create-flow`
2. Flow author reviews; if the request is valid:
   - Flow is updated (a step is reworded, an exception path added, Domain Concepts changed)
   - The change triggers `product-intake` to cascade through requirements (one or more requirements may need to update)
   - Affected scribbles (those with `participating_flows: [FLOW-NNN]`) gain `stale_since: <date>` + `pending_flow_changes: [FLOW-NNN]` in their metadata
3. Stale scribbles are re-iterated on next touch; the iteration starts from the new flow as input

**Token discipline (user's concern)**: only the AFFECTED scribbles are re-iterated. The discovery script reads each scribble's `participating_flows:` field and marks only those that reference the changed flow. A typical change affects 1–3 scribbles, not all of them.

**Multi-flow flaws**: the same revision request can name multiple flows (`target_artifact: [FLOW-001, FLOW-002]`). The cascade fans out; the orchestrator handles ordering (typically: change the flow least likely to have downstream effects first).

---

## 5. Refinements to iteration 3 per round-4 feedback

### 5.1 Persona embodiment — scenario discovery via flow's `serves_scenarios`

User pointed out: flows already declare which scenarios they serve, e.g.:

```yaml
serves_scenarios:
  - scenario_id: SCEN-001-03
    persona_id: PERSONA-001
    persona_name: "Dr. Sarah (Therapist)"
    scenario_name: "Instruct Client on Protocol"
```

This is the canonical source. The persona-embodiment-reviewer agent reads `serves_scenarios` from the flow, identifies the scenarios for each materially-affected persona, and reads those scenario.md files. No name-matching heuristic needed.

**Updated reading scope for the agent**:
- Persona's `persona.md` (always — primary anchor)
- For each materially-affected persona: the scenario(s) listed in the parent flow's `serves_scenarios` block where `persona_id` matches
- Parent flow's `flow.md` Domain Concepts section
- The scribble itself (always — the artifact being walked)

**Why this matters**: pre-product scenarios are valuable empathy input (they describe the world without the app). The user noted "I think we have to try out if it is needed that the LLM actually reads those as well." Verdict from this iteration: yes, read them — they're already linked from the canonical source, and the cost is one extra read per persona.

### 5.2 Flow navigation — explicit multi-flow coverage + per-flow validation walks

User: "scribbles cover multiple user flows. that must be explicit." Already captured in iteration-3 §5.5 (`participating_flows:` field). Round-4 sharpens:

- The `participating_flows:` field lists ALL flows touching the scribble, with the steps each flow contributes
- **Validation discipline**: before approving a scribble, the reviewer (human and the auto-review agent) walks the scribble FOR EACH flow independently. "Read the flow, 'click through' the scribbles like the flow defines it, check if it matches and works." This is a new Phase-2 sub-step.
- The flow scribble index (`requirements_user_needs/user_flows/<flow>/scribble_index.html`) renders the scribble screens in that flow's step order — supporting the walk-through visually.
- If the walk reveals a flow flaw, the bidirectional-feedback pattern (§4) kicks in.

**Phase-2 auto-review extension**:
```
For each flow in metadata.yaml.participating_flows:
  - Walk the scribble screens in this flow's step order
  - For each step, verify the scribble's screen content supports the flow's intent
  - If a step's intent is not supported (e.g. the screen lacks a control the flow expects):
      - If the gap is in the scribble: regenerate that screen
      - If the gap is in the flow (the scribble reveals the flow is logically inconsistent): emit a revision_request to ux-create-flow
```

### 5.3 Cross-cutting auto-discovery — no manual; use frontmatter + script

User: "no don't let the user do it manually. we have frontmatters that should contain the information. if not we should add it (by modifying the skills that create those artifacts). a script should be able to do the discovery."

Updated approach for `contributing_requirements:` (iteration-3 §5.2):

**Discovery via script**:
1. The script reads the scribble's `metadata.yaml.feature_path` (e.g. `therapist/data_transfer`)
2. From the parent flow(s) listed in `participating_flows:`, the script reads each flow's frontmatter for `serves_requirements:` or equivalent — currently this field needs to be added to flow.md frontmatter if it isn't present
3. Any requirement that (a) `implements_flows` one of the participating flows AND (b) has UI scope (e.g. `presentation_layer: true` in requirements.md frontmatter) is a candidate cross-cutter
4. The script outputs the candidate list; the scribble's `contributing_requirements:` is auto-populated; primary is the one matching the feature_path mirror
5. Discrepancies (e.g. a requirement whose `implements_flows` includes the flow but whose UI scope is unclear) are flagged for user review, NOT auto-decided

**Required frontmatter extensions** (these are skill changes, bundled with Q2-CONTRACT):
- `requirements.md` frontmatter: add `presentation_layer: true/false` (whether the requirement has UI scope) — many already have related fields; this just standardizes
- `flow.md` frontmatter: add `serves_requirements: [REQ-...]` listing requirements that contribute UI to this flow's screens (this enables reverse lookup; `requ-derive-from-flow` populates it)
- Update the relevant skills: `requ-explore`, `ux-create-flow`, `requ-derive-from-flow` — to emit these fields

**Script**: `scripts/scribbles/discover_contributing_requirements.py`. Inputs: scribble path. Output: stdout list (writable into metadata.yaml). Runs as a Phase-1 step in the new `ui-scribble-generate` sub-skill.

### 5.4 Position A confirmed; no change

User did not revisit Position A. Held.

---

## 6. Ideation responses (round-3 §6.1–6.8 — user's votes)

| # | Item | User vote | Notes |
|---|---|---|---|
| 6.1 | Approval traceability aggregator (`APPROVAL_TRAIL.md`) | **Adopt** | "we also do for user flow iterations (not in a separate file, but still). it proved very helpful." → adopt as a separate file (single source per scribble, supports cross-version reading) |
| 6.2 | Live single-screen Flutter preview | **Reject** | "no" |
| 6.3 | Inter-version diff report | **Adopt — with HTML toggle** | "the best thing would be to have a toggle on the html page that, if enabled, highlights the changes visually. not sure how much token usage that would add and how well it would work" → implement as: structured diff report PLUS a toggle script injected into the screen HTML that highlights changed elements when enabled. **Token discipline**: the diff computation runs at Phase-2 end (once per version); the toggle is pure client-side JS (no LLM cost). |
| 6.4 | A/B variant generation | **Reject** | "no" |
| 6.5 | Persona-conflict marker + DDR auto-link | **Adopt — with VCD/flow update trigger** | "like stated above: that might be a point where the user could decide to modify the user flow or the vcd decisions from the past (wherever they are documented)." → when a persona-conflict marker is added, the reviewer is prompted: "this conflict suggests either a DDR is needed OR an upstream change (flow / VCD record). The revision-request pattern (§4) handles the upstream route." |
| 6.6 | Scribble-to-integration-test traceability | **Adopt** | "yes" |
| 6.7 | Auto-review brief for v(n+1) | **Adopt — clarified vs 6.3** | "yes, but what's the difference to 6.3?" Clarification below. |
| 6.8 | Rule-application audit log | **Adopt** | "yes" |

### 6.7 clarification — auto-review brief vs inter-version diff

These are complementary, not redundant:

- **6.3 inter-version diff** = STRUCTURAL difference between v(n) and v(n+1). Mechanical. Lists added/removed/restructured screens, changed copy, rule-application changes. Produced by a diff routine; visualisable via HTML toggle.
- **6.7 auto-review brief** = AGENT'S NOTE TO REVIEWER about what to focus on this round. Selective. Says things like "I prioritized fixing the missing exception path in screen 03; please re-walk PERSONA-009's path through screens 03–05 because the privacy copy was changed." Produced by the auto-review agent based on what it CHOSE to fix or leave open.

The diff answers "what changed?"; the brief answers "what should you check now?". The diff feeds the brief (the agent reads the diff and writes the brief). Both are cheap; both adopted.

---

## 7. Divide-and-conquer — sub-skill split for the scribble pipeline

Per the meta-exploration agent (§4 of file 08), `ui-create-scribble` is a candidate for splitting into 4 sub-skills + a thin orchestrator. The user's "divide and conquer? modules? smaller skills with clear boundaries and interface contracts?" framing applies directly.

### 7.1 Proposed split

| Sub-skill | Inputs | Outputs | Notes |
|---|---|---|---|
| **ui-scribble-generate** | `requirements.md`, personas, T1/T2 rules, `inputs/`, `flow_context`, `flow_scope`, `implementation_notes`, optional pre-brief | `scribbles/<feature_path>/v{n}/{index.html, NN_*.html, metadata.yaml, feedback.md}` | Phase 0 + Phase 1. Stateless w.r.t. previous versions. |
| **ui-scribble-auto-review** | `scribbles/<feature_path>/v{n}/` (n odd), same upstream context | `scribbles/<feature_path>/v{n+1}/` + `auto_review_report.md` + auto-review brief | Phase 2 + Component auto-promotion. |
| **ui-scribble-feedback-classify** | `feedback.md`, T1/T2 rule corpus | classifications.yaml; may invoke `requ-explore` / `doc-update-guidelines` / `ux-validate-rule`; may emit revision_request | Phase 4. Most rule-heavy phase. |
| **ui-scribble-approve-handoff** | approved `scribbles/<feature_path>/v{n}/` | `flutter_handoff.yaml` (schema-validated), `scribble_index.html` (flow composite), `flow_navigation.yaml` (per flow), `verification_seeds.yaml` (for integration tests), `metadata.yaml.status=approved` | Phase 5 + 5a + integration-test scaffolding from 6.6. |

**Thin orchestrator** (`ui-scribble-iterate`, formerly `ui-create-scribble`): dispatch + version tracking + user handoff + back-pressure cap.

### 7.2 What stays bundled

The orchestrator stays bundled (it owns the iteration loop, which is shared state by nature). The reason: splitting the orchestrator into separate skills loses the loop control. The orchestrator's contract is "produce one approved scribble per requirement under the right feature_path"; its phases are internal.

### 7.3 Sequencing

This split needs:
- The new `contract.yaml` mechanism (from SKILL-INTERFACE-CONTRACTS) to declare each sub-skill's interface
- The new agents (from Q1-AGENTS) that each sub-skill invokes (scribble-generator, scribble-auto-reviewer, scribble-ux-protocol-reviewer, persona-embodiment-reviewer)

Therefore the split is **blocked by both** SKILL-INTERFACE-CONTRACTS (for the mechanism) and Q1-AGENTS (for the agents). Bundled as **SCRIBBLE-SPLIT** impl task, effort L.

---

## 8. Final decision matrix (round 4 consolidated)

Adds D33–D47 to the iteration-3 set (D1–D32). All previously-adopted decisions remain unless explicitly changed.

| # | Decision | Status | Bundle |
|---|---|---|---|
| D1–D32 | (iteration-3 set, unchanged) | (per iteration 3) | (per iteration 3) |
| **D33** | **Scribble location moved to `requirements_tasks/scribbles/` mirroring `lib/features/`** | Adopt | Q2-CONTRACT (folder move + path-discovery logic update) |
| **D34** | **`_core/` scribble subfolder mirroring `lib/core/`** | Adopt | Q2-CONTRACT |
| **D35** | **Scribble–feature parity lint** | Adopt | Q2-CONTRACT |
| **D36** | **`feature_path:` field in scribble metadata** | Adopt | Q2-CONTRACT |
| **D37** | **Spawn SKILL-INTERFACE-CONTRACTS exploration task (draft ready in §0 of file 08)** | Adopt — **new impl-task seed** | NEW-EXPLORATION |
| **D38** | **Bidirectional feedback: one pattern, three triggers; file-based channel under `pending_feedback/revision_requests/`** | Adopt | NEW-EXPLORATION outputs the formal design; an interim "stub" implementation can land with Q2-CONTRACT (revision-request schema + escalation per CLAUDE.md §7) |
| **D39** | **Scribble walk per flow as Phase-2 sub-step** | Adopt | Q1-AGENTS |
| **D40** | **Cross-cutting auto-discovery: script + frontmatter (no manual)** | Adopt | Q2-CONTRACT |
| **D41** | **`presentation_layer: true/false` field in requirements.md frontmatter** | Adopt | Q2-CONTRACT |
| **D42** | **`serves_requirements:` field in flow.md frontmatter** | Adopt | Q2-CONTRACT |
| **D43** | **6.1 Approval traceability — separate `APPROVAL_TRAIL.md` per scribble** | Adopt | Q1-AGENTS (auto-reviewer emits) |
| **D44** | **6.3 Inter-version diff with HTML toggle for visual highlight** | Adopt | Q1-AGENTS (diff routine) + Q2-CONTRACT (toggle script + injection convention) |
| **D45** | **6.5 Persona-conflict marker triggers VCD/flow update prompt** | Adopt | Q1-AGENTS (persona-embodiment-reviewer emits the marker; revision-request pattern handles upstream propagation) |
| **D46** | **6.7 Auto-review brief — distinct from diff** | Adopt | Q1-AGENTS |
| **D47** | **SCRIBBLE-SPLIT (4 sub-skills + thin orchestrator), blocked by SKILL-INTERFACE-CONTRACTS + Q1-AGENTS** | Adopt — **new impl-task seed** | NEW (separate bundle) |

### 8.1 Rejected items (no change)

- D24 (Live Flutter preview) — rejected in iteration 2 by user "no"
- D26 (A/B variant generation) — rejected in iteration 2 by user "no"

### 8.2 Deferred to backlog (recorded only, not seeded)

- Phase B scribble-location restructure (per-screen catalogue) — was deferred in iteration 3; deferred again

---

## 9. Updated impl-task plan (11 bundles total)

Per the user's "create all the implementation tasks" instruction, all 11 bundles are seeded as `task-create` invocations. Execution is independent of seeding.

| Order | Task | Bundle ID | Effort | Blocked-by | Decisions covered |
|---|---|---|---|---|---|
| 1 | Create `claude-create-agent` skill (web research + draft) | NEW-SKILL | M | — | D22 |
| 2 | Make scribble–coder contract explicit (Q2 architecture + scribble location migration) | Q2-CONTRACT | L | — | D1, D2, D6, D7, D8, D11, D14, D20, D29, D30, D32, D33, D34, D35, D36, D38 (stub), D40, D41, D42, D44 (toggle script) |
| 3 | Port Domain Vocabulary + Anti-Patterns to 6 existing agents | DOMAIN-VOCAB | S | — | D9 |
| 4 | Create scribble-specific agents + UX-protocol ports + new auto-review features | Q1-AGENTS | L | NEW-SKILL | D3, D16, D18, D21, D25, D27, D31, D39, D43, D44 (diff routine), D45, D46 |
| 5 | Create `ui-visual-validate` skill (Opus, integration-test screenshots) | VISUAL-VALIDATE | M-L | — | D12, D28 |
| 6 | Multi-breakpoint scribbles via persona `device_classes` | BREAKPOINTS | M | — | D13 |
| 7 | Structured inspiration inputs (`inputs/inspiration.yaml`) | INSPIRATION | M | — | D15 |
| 8 | Reviewer pre-brief (Phase 0.5) with iteration model | PREBRIEF | S-M | — | D17 |
| 9 | Cross-feature consistency check (Haiku Phase-2 step) | CROSS-FEATURE | S | — | D19 |
| 10 | **NEW: Explore skill interface contracts (sidecar contract.yaml + schemas + lint + handoff blocks + split rubric)** | NEW-EXPLORATION | L | — | D37, D38 (formal design) |
| 11 | **NEW: Split `ui-create-scribble` into 4 sub-skills + thin orchestrator** | SCRIBBLE-SPLIT | L | NEW-EXPLORATION + Q1-AGENTS | D47 |

**Dependency graph**:

```
NEW-SKILL ──────────► Q1-AGENTS ────────────────────────────┐
                                                            │
NEW-EXPLORATION ─────────────────────────────────────────► SCRIBBLE-SPLIT
                          │
Q2-CONTRACT  (D38 stub) ──┴── (informed by NEW-EXPLORATION later)

DOMAIN-VOCAB, VISUAL-VALIDATE, BREAKPOINTS, INSPIRATION, PREBRIEF, CROSS-FEATURE — all independent
```

**Critical path**: NEW-SKILL → Q1-AGENTS → SCRIBBLE-SPLIT (requires both Q1-AGENTS and NEW-EXPLORATION). NEW-EXPLORATION is independent of NEW-SKILL and Q2-CONTRACT and can run in parallel.

---

## 10. Honest gaps and risks (round-4 specific)

- **Scribble-location migration policy is light.** `doc/presentation/coding/folder_structure.md` is brief and informal; the mirror-1:1 rule is a stronger discipline than the source folder enforces today. If `lib/features/` evolves loosely (e.g. someone moves `therapist/data_transfer/` to `therapist/transfer/`), the scribble parity lint will fire and need a manual sync. Mitigation: add the mirror-rule to `claude-create-skill` and to any feature-creation skill; treat the parity lint as a periodic check, not a blocker.
- **`presentation_layer:` and `serves_requirements:` field additions are intrusive.** They require updates to `requ-explore`, `ux-create-flow`, `requ-derive-from-flow`. Existing artifacts need backfill. Mitigation: schema-validate at lint time; backfill via a one-time script.
- **Bidirectional feedback via `pending_feedback/revision_requests/` is a stub design.** NEW-EXPLORATION ratifies the formal mechanism (channel format, escalation, target-phase semantics). The stub in Q2-CONTRACT is enough to start using the pattern; the formal version replaces the stub.
- **The proposed sub-skill split is one specific cut.** The agent's recommendation (generate / auto-review / feedback-classify / approve-handoff) is reasonable but not the only viable cut. NEW-EXPLORATION should validate before SCRIBBLE-SPLIT executes.
- **Persona-embodiment-reviewer reading scope grows.** Each materially-affected persona triggers read of persona.md + ≥1 scenario + flow Domain Concepts. For a screen with 4 affected personas, that's ≥12 file reads in addition to the scribble. Token cost is real; mitigation: cap per-persona reading to 1 scenario (the one with strongest semantic match to the screen's task).
- **The 11-bundle plan is ambitious.** Realistic execution is multiple weeks across multiple contributors. Seeding all 11 is the user's explicit ask ("we don't have to actually execute all implementation tasks we will create"). The dependency graph above tells the execution scheduler which can start in parallel.

---

## 11. Next steps

1. **Write the redundancy-check document** (separate, per user instruction): `2026-05-29_10_redundancy_check.md`. Scan the iteration-3 + iteration-4 decision matrix and the impl-task plan for steps that do basically the same thing in slightly different ways. (§12 below names the candidates to inspect.)
2. **User confirmation**: review §8 decision matrix and §9 impl-task plan. Any reversals?
3. **Seed the 11 impl-task goal.md files** via `task-create` skill. Each carries the bundle's decisions as ACs, parent_requirement, after-chain.
4. **Verify the 4 exploration ACs** in this task's goal.md (already ticked by the user) — re-confirm honestly given the additional iteration depth.
5. **`task-complete` on TASK-PROC-032-10**.

---

## 12. Redundancy-check candidates (input for the next document)

Items to inspect for potential redundancy or overlap:

| # | Candidate | Why it might be redundant |
|---|---|---|
| R1 | Phase-2 auto-review vs. Phase-2b ux-protocol-reviewer vs. Phase-2.5 persona-embodiment | Three reviewers in a row — could one cover another's territory? |
| R2 | Inter-version diff (6.3) vs. auto-review brief (6.7) vs. APPROVAL_TRAIL.md (6.1) | Three artifacts describing what changed and why. Differentiated above but overlapping in spirit. |
| R3 | `flutter_handoff.yaml` vs. `contract:` block within it vs. `flow_navigation.yaml` vs. `verification_seeds.yaml` | Four machine-readable handoff artifacts. Could some collapse? |
| R4 | Pre-brief (PREBRIEF) vs. auto-review brief (6.7) | "What to focus on" appears at both boundaries — generate and review. Probably necessary, but the structure should be coherent. |
| R5 | Cross-feature consistency check (CROSS-FEATURE) vs. flow-walk per-flow validation (D39) | Both look across multiple scribbles/features. Could the cross-feature check be folded into the per-flow walk? |
| R6 | Skill-interface revision_requests (D38) vs. existing `pending_feedback/` channel vs. CLAUDE.md back-pressure protocol | Three escalation/feedback channels. Should be one with sub-types? |
| R7 | `contributing_requirements:` (D29) vs. `participating_flows:` (D30) vs. `feature_path:` (D36) | All three locate the scribble in the requirement graph. Necessary? Could one derive from others? |
| R8 | `ui-verify-flutter` (post-impl structural) vs. `ui-improve-flutter` (visual polish) vs. `ui-visual-validate` (integration-test screenshots) | Three post-implementation skills. Their scopes should be cleanly separated; verify there's no creep. |
| R9 | `claude-modify-skill` + (proposed) `claude-create-agent` + `claude-create-skill` | Three skill-management skills. Do their contracts and outputs cohere? |
| R10 | DOMAIN-VOCAB port (D9) vs. the new agents created with proper Domain Vocabulary (D16, D18) | Two ways to get vocabulary onto agents — one retrofitting, one greenfield. Consistent design? |

The redundancy-check document will inspect each and recommend collapse, differentiation, or keep-as-is.
