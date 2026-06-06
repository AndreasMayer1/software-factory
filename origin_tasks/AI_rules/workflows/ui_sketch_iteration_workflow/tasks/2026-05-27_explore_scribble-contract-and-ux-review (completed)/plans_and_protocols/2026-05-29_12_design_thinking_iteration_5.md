# Design-Thinking Iteration 5 — round-5 response + strategic narrowing

**Task:** TASK-PROC-032-10 · **Date:** 2026-05-29 · **Model:** Opus 4.7
**Input:** `2026-05-29_11_feedback.md` (round-5 user feedback)
**Companion document:** `2026-05-29_13_session_token_efficiency_analysis.md` (separate per user's explicit ask)

> Methodology: this iteration narrows the plan rather than expanding it. The user's central strategic shift is **seed only NEW-EXPLORATION first; iterate with its results**. The other refinements either *change* prior decisions or *defer* them. Three light analyses (factory alignment, frontmatter audit, PRINCE2) are completed inline; the deep token-efficiency analysis lives in the companion document.

---

## 1. Round-5 strategic shifts (top-level)

| # | User directive | Effect on the plan |
|---|---|---|
| S1 | "Don't create all tasks you propose already, only this single one [NEW-EXPLORATION]. Then continue our iteration. With the results." | **Reduces seeding from 11 tasks to 1.** Defer the other 10 until NEW-EXPLORATION execution surfaces what's actually needed. |
| S2 | "Tasks are the only real integration mechanism. Handoff files alone are dead ends." | **Every bundle must end with task creation**, not just artifacts. Revision_requests must route to tasks (or feed existing tasks via `awaiting:`). |
| S3 | "Cross-check factory_quality and factory_purpose; avoid duplicate work." | **REQ-PROC-044 is the parent for NEW-EXPLORATION** (not a new requirement) — see §3. |
| S4 | "Did you check existing frontmatter fields?" | **Use `requirements_matrix.md` files** as the cluster→requirement mapping source; don't invent new YAML fields unless audit confirms a real gap — see §4. |
| S5 | "Total-cost optimization: skill-workflow improvements now or wait for 0.0.1?" | **Do infrastructure now**; add to `task_ordering_priority_override.txt` — see §9. |
| S6 | "Separate document on what info is needed at which stage / token efficiency / session splits." | **Companion document** `2026-05-29_13_session_token_efficiency_analysis.md`. |
| S7 | "Skill workflow split — how many sessions? Each new session = empty context = re-reads = expensive." | Folded into S6 companion document. |
| S8 | "Meta-exploration agent findings are INCOMPLETE. Don't depend too much. Expect the formal task to change our approach." | Confirms S1 — defer downstream bundles until NEW-EXPLORATION ratifies the design. |

---

## 2. Factory-quality + factory-purpose alignment (S3)

### 2.1 REQ-PROC-044 already exists and covers our target

Inspected `requirements_tasks/process/AI_rules/factory_quality/requirements.md`. The requirement is **REQ-PROC-044 (Software Factory Quality Properties)**, `status: active`, owned by app_provider, with 6 ACs that directly cover the skill-interface-contracts goals:

| AC | Text | Skill-interface-contracts mapping |
|---|---|---|
| AC-01 | "Every skill has a documented, reachable output: given a valid set of input artifacts, an agent following the skill produces the expected output artifact without silent failure" | **This IS the contract goal**. The proposed `contract.yaml` (per meta-exploration §3.1) operationalizes this AC. |
| AC-02 | "The artifact pipeline is traceable from any code file back through its originating task, requirement, flow, scenario, and persona without gaps in the chain" | Bidirectional feedback (§4 of iteration 4) and structured `handoff:` blocks (§3.4 of meta-exploration) operationalize this. |
| AC-03 | "Any new task type, artifact layer, or skill can be integrated into the factory without modifying existing skills or scripts that do not consume the new type" | Sidecar contracts + schemas mean adding a skill doesn't ripple-edit consumer skills. |
| AC-04 | "Malformed or missing input artifacts cause a visible warning or graceful stop — they never cause a skill to silently produce incorrect output or corrupt a downstream artifact" | Pre-condition checks in `contract.yaml` + lint enforce this. |
| AC-05 | "Non-deterministic LLM behavior is isolated to clearly defined decision points; all deterministic steps (ID allocation, status transitions, file writes, script outputs) produce identical results for identical inputs" | Skills declare which steps are deterministic; structured outputs separate the two. |
| AC-06 | "The set of active skills, their artifact dependencies, and the ordering rules governing task execution are documented in a single authoritative location that is kept current as the factory evolves" | `.claude/contracts/` (or equivalent registry) becomes that location. |

**Verdict**: NEW-EXPLORATION is **not a new requirement**. It is an exploration task **under REQ-PROC-044** that produces a concrete mechanism (sidecar contracts + schemas + lint + handoff blocks + split rubric) satisfying these existing ACs.

**Update to D37**: `parent_requirement: REQ-PROC-044` (not REQ-PROC-TBD). The agent's draft goal.md needs this single change.

**Implication for the requirement itself**: REQ-PROC-044's ACs already exist as `status: active` (the requirement is alive but unsatisfied — typical for a living-document quality requirement). NEW-EXPLORATION's deliverable is the mechanism that *satisfies* these ACs. No new ACs needed on REQ-PROC-044 unless the exploration discovers gaps.

### 2.2 REQ-PROC-057 (factory_purpose) — in-progress, no conflict

The task `2026-05-26_explore_factory-purpose-and-improvement-loop/goal.md` (TASK-PROC-057-01) is exploring the apex factory purpose requirement. It explicitly references REQ-PROC-044 as a child ("factory-machine integrity"). Our work sits at the REQ-PROC-044 level; REQ-PROC-057 is one level up.

The factory_purpose exploration could surface a north-star statement that constrains the skill-interface-contracts approach (e.g., "minimum effective dose" might cap contract complexity). Risk: low — our mechanism choices (sidecar over inline; opt-in `contract_version: 0` for un-migrated skills) already align with minimum-effective-dose.

**Action**: NEW-EXPLORATION's goal.md should reference TASK-PROC-057-01 as awareness ("if completes first, integrate its constraints") — no hard dependency.

### 2.3 Other tasks to know about (named by user)

- `factory_quality/requirements.md` — REQ-PROC-044 (the parent). Read in §2.1.
- `factory_purpose/tasks/2026-05-26_explore_factory-purpose-and-improvement-loop/goal.md` — TASK-PROC-057-01 (apex, in-progress).
- "and probably other requ and exploration tasks" — the inventory of related-but-separately-pursued work is incomplete. **Action**: ask NEW-EXPLORATION's executing session to start with an inventory pass (read `requirements_tasks/STATUS.md`, grep for `type: explore` tasks in `process/AI_rules/factory_*`).

---

## 3. Frontmatter audit (S4)

User: "Did you check what fields currently exist? I don't want to introduce a new field that duplicates what's already there."

### 3.1 `presentation_layer:` proposal — audit result

Searched `requirements_tasks/**/requirements.md` for `presentation_layer:`, `presentation:`, `ui_scope:`, `has_ui:`. **No matches.** Existing requirements convey UI scope implicitly via:
- Folder hierarchy (under `epic_data_transfer/feat_*_ui/`)
- The presence of a `scribbles/` subfolder
- References to `user_needs.flows` (flows often have UI)

**Verdict**: no existing field duplicates this. But the field may also be **unnecessary** — UI scope can be derived without a new field:
- Auto-discovery script can check whether a requirement has a `scribbles/` subfolder (existing structure)
- Or whether it implements a flow with UI steps (flow.md frontmatter)
- Or whether its name contains `ui` / `screen` / `view`

**Updated proposal**: drop the new `presentation_layer:` field. Auto-discovery script uses the heuristic (scribbles/ folder exists OR name pattern OR flow with UI steps) and flags edge cases for user review.

### 3.2 `serves_requirements:` proposal — audit result

Inspected `requirements_user_needs/README_8_CROSS-REFERENCING_SYSTEMS.md` and the `flow.md` frontmatter for `instruct_client_on_protocol`.

**Existing cross-reference mechanisms**:

1. **Flow → Epic/Feature (markdown only)**: flow.md has an `## Implementing Epics/Features` markdown section listing the requirements that implement it.
2. **Epic/Feature → Flow (YAML)**: epic/feature requirements.md has `user_needs.flows: [FLOW-...]` upward reference.
3. **Cluster matrix (markdown)**: `requirements_user_needs/user_flows/_clusters/<cluster>/requirements_matrix.md` is a comprehensive table mapping every flow gap to existing requirements, with status, foundations, cross-flow markers, suggested packages.

The proposed `serves_requirements:` YAML in flow.md frontmatter would be the **machine-readable inverse of mechanism 2**. It exists today only in markdown form (mechanism 1).

**Verdict**: there IS partial duplication, but the YAML form is genuinely missing.

**Better approach — use the cluster matrix instead**: `requirements_matrix.md` already provides the data we need (which requirements contribute to a flow, with role and verification status). It's authored at cluster level, not flow level, but a script can read it and produce flow→requirement mappings.

**Updated proposal**: skip the `serves_requirements:` YAML field. Auto-discovery script reads `requirements_user_needs/user_flows/_clusters/<cluster>/requirements_matrix.md` (or per-flow `requirements_matrix.md` for single-flow features) and extracts the requirement-to-flow mapping. No new field; reuses existing comprehensive source.

If a flow has no cluster matrix (e.g., a brand-new flow not yet placed in a cluster), the script reports "no matrix found — author one or accept manual fallback."

### 3.3 Net change to D41 and D42

- **D41 (`presentation_layer:`): DROP.** Replace with heuristic-based auto-discovery.
- **D42 (`serves_requirements:`): DROP.** Replace with `requirements_matrix.md` parser.

Both decisions are GONE from the plan. The auto-discovery script (D40) is the load-bearing mechanism; it reads existing artifacts instead of new fields.

**This is a clean reduction — fewer artifacts to maintain, no risk of duplicate-source drift, and respects the user's "use what's there" instruction.**

---

## 4. PRINCE2 evaluation — skills vs artifacts as the focus (S2-related)

User question: "Should we focus the skills or the artifacts? You wrote it with the focus on the skills. But for example, if you consider PRINCE2, they decided to put the artifacts into focus for a good reason, right? but i might be wrong, evaluate."

### 4.1 PRINCE2's artifact-driven approach (briefly)

PRINCE2 organizes project work around **products** (artifacts with defined quality criteria), not activities. Each product has a Product Description (purpose, composition, quality criteria, format, derivation). Activities are derived from "what do we need to produce this product?" rather than "what should we do this week?".

**Why this works for PRINCE2**:
- Stable across role changes — the product spec outlives the person executing it
- Clear acceptance — a product is done when it meets quality criteria, not when an activity "feels finished"
- Auditable — the product trail is the project record
- Decouples planning from execution — multiple paths can produce the same product

### 4.2 Our current factory: skill-driven (with artifact side-effects)

Today our skills are the orchestration unit. Each skill describes what to do (steps, phases, agent spawns). Artifacts are *outputs* of skills, not first-class. Pain: §1 of the meta-exploration cited 7 categories of pain — most reduce to "the artifact contract isn't declared anywhere; only the skill knows what it produces, and only the consumer skills know how they interpret it."

### 4.3 What an artifact-driven shift would look like

Hypothetically: define every artifact in `.claude/artifacts/<artifact_name>/spec.yaml` with purpose, schema, producer-skills, consumer-skills, quality criteria. Then skills become *instances of "the skill that produces artifact X"* — naturally typed by output.

**Pros**:
- Aligns with REQ-PROC-044 AC-01, AC-02 directly (the artifact pipeline is the traceable thing)
- Solves the "concept_canon.yaml has 5 consumers but no declared schema" problem at the root
- Matches the user's intuition that the durable thing is the artifact, not the skill

**Cons**:
- Heavy refactor — every skill needs to be re-cast as "the producer of X"
- Loses the workflow-orchestration narrative that skills provide (some skills genuinely are *processes*, not *producers*)
- Sub-skills with shared intermediate state (e.g., the iterating orchestrator) don't fit cleanly

### 4.4 Verdict: hybrid — artifacts are the contract; skills are the executable workflow

The meta-exploration's recommended mechanism is *already* hybrid:

- **Artifacts are first-class** via `.claude/schemas/<artifact>.yaml` (one place describes the shape)
- **Skills retain workflow ownership** but declare their input/output contracts referencing the schemas
- **Sidecar `contract.yaml`** ties them together: skill X says "I consume artifact Y (schema link), produce artifact Z (schema link)"

This is closer to PRINCE2 than the current skill-centric prose, while preserving the workflow narrative.

**No change to the planned mechanism** — but the framing matters: NEW-EXPLORATION should explicitly call out the artifact-first lens (and that the recommendation is hybrid) so the reader understands what was considered and rejected.

### 4.5 `revision_requests/` vs creating a task

User: "revision_requests/ or create a task? what's better?"

**Both are needed, depending on the work the revision implies:**

| Revision work | Channel | Why |
|---|---|---|
| Standalone work needed (e.g. regenerate scribble v(n+1) reflecting coder feedback) | **Task** | A real artifact change requires a task; the orchestrator picks it up via normal task ordering |
| Decision needed before any work (e.g. "is this drift intentional?") | **revision_request file** | Lightweight; doesn't pollute the task list with non-actionable items |
| Question requiring developer answer | **pending_feedback/<task>/question.md** | Existing channel for human-required answers |

**Rule (proposed for NEW-EXPLORATION to formalize)**: a revision_request that auto-resolves into "do work" should create a task; one that needs review/decision goes to revision_requests/; one that needs developer answer goes to pending_feedback/. The receiving end (the upstream skill's owner) decides which path applies when it processes the request.

**Per S2** (tasks are the only real integration mechanism): the revision_request channel is a *triage* layer. The TASK channel is the only one that actually moves work forward.

---

## 5. Other round-5 refinements

### 5.1 Flow validation — human instructions (round-5 §5.2)

User ask: human-readable single-sentence instructions per flow telling the user what to walk through.

**Proposal**: the auto-review brief (D46) for any scribble whose `participating_flows:` has ≥1 entry includes a "PER-FLOW WALK INSTRUCTIONS" section:

```
PER-FLOW WALK INSTRUCTIONS
==========================
For FLOW-002 (Instruct Client on Protocol):
  Open: scribbles/<feature_path>/v{n}/index.html
  Walk: screens 01 → 02 → 04 → 05 in this order (per flow_navigation.yaml)
  Focus: does the flow's intent at each step match what the screen shows?

For FLOW-003 (Session Start & Data Transfer):
  Open: same index.html
  Walk: screens 03 → 05 (only these steps belong to FLOW-003 for this scribble)
  Focus: handover between flows at screen 05 — is the transition coherent?
```

Generated by the auto-reviewer agent (Q1-AGENTS). No new artifact; embedded in the existing brief.

### 5.2 Persona embodiment — 1 scenario confirmed

User: "reading just one scenario is enough. Because as I said, it must be the most relevant one."

Confirmed. Per iteration-3 §4.2 cap. Discovery via flow's `serves_scenarios` (per iteration-4 §5.1) — pick the scenario where `persona_id` matches the materially-affected persona AND `relationship: primary` (or first listed if no relationship field).

### 5.3 Scribble-location migration — needs `lib/features/` policy work too

User note: "for that to work, we really have to also improve how features in the lib folders are structured and when new features are created and what is in one feature."

True. The current `doc/presentation/coding/folder_structure.md` is brief (60 lines, 2025-02-21). A more formal "feature creation policy" doesn't exist.

**Action**: surface this as a known dependency. NOT bundled into Q2-CONTRACT (which is about scribble contracts; not the Flutter feature policy). Spin off as a separate exploration **only if** NEW-EXPLORATION confirms scribble-feature parity lint requires it. The parity lint can work today against the de-facto convention; if it fails too often, that's evidence the Flutter policy needs codifying.

**Defer to backlog**, with trigger: "scribble-feature parity lint produces ≥2 false-positive runs in 1 month."

### 5.4 Gaps fill — additional tasks

User: "In general for the gaps you've identified. We have to fill them, of course. We need to create additional tasks. If needed. Of course those additional tasks might belong to a different requirement and not the scribble requ."

Acknowledged. Concretely:
- Skill-interface-contracts gap → NEW-EXPLORATION (parent REQ-PROC-044)
- Token-efficiency / session-split analysis → companion document (§6); if it produces actionable recommendations, follow-up task(s) get created later
- `lib/features/` policy gap → deferred (§5.3 above)
- Frontmatter standardization gap → audited away in §3
- Other implicit-interface pain spots discovered by NEW-EXPLORATION → that task's deliverable

### 5.5 Round-5 §7 — sub-skill split + sessions/tokens

Folded into §6 (companion document `2026-05-29_13_session_token_efficiency_analysis.md`). The user's "what information is needed at which stage; which split minimizes token consumption" question is the right framing and deserves its own analysis.

---

## 6. Companion document: session/token efficiency

The user explicitly requested a separate document. Written to:

**`requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/2026-05-27_explore_scribble-contract-and-ux-review/plans_and_protocols/2026-05-29_13_session_token_efficiency_analysis.md`**

See that file for the full analysis. Key shape:
- Per-stage information-need map (what artifacts each phase reads)
- Per-stage token-cost estimate (rough)
- Split candidates (when does a fresh session beat reusing one)
- Recommended cuts for the scribble pipeline
- The "split too much vs split too little" trade-off

---

## 7. Total-cost decision — infrastructure now vs 0.0.1 first (S5)

User principle: "I'm interested in the total efficiency, the total cost. Things that we don't refactor now might lead to more work when we then actually refactor it because other things get added in the old style and those new things then also have to be refactored."

### 7.1 Total-work analysis

Three categories of upcoming work:

| Category | If done NOW (before 0.0.1) | If deferred (after 0.0.1) |
|---|---|---|
| **Scribble infrastructure** (Q2-CONTRACT + Q1-AGENTS + supporting bundles) | ~3-4 weeks of focused work; 0.0.1 implementation runs ON the improved infrastructure | Same ~3-4 weeks LATER, but every feature added during 0.0.1 will be in the old style and need re-doing (the user's concern made concrete: ~5-10 additional Flutter features built without scribble-contract clarity → re-iteration cost per feature) |
| **Skill-interface contracts** (NEW-EXPLORATION + downstream) | Discovery via NEW-EXPLORATION; possibly ~2-3 weeks of mechanism rollout | Same cost LATER; meanwhile every new skill written during 0.0.1 is in the old (implicit-interface) style and needs retrofitting |
| **0.0.1 features** (the actual product release) | Slower START but each feature lands in the improved infrastructure | Faster start, but accumulates technical debt at the rate features are added |

### 7.2 Recommendation: do infrastructure FIRST

The user's principle is correct: every feature added before the infrastructure refactor is a feature that has to be re-done after. The cost compounds. Doing infrastructure first is the lower-total-work path.

**Action**: add NEW-EXPLORATION to `task_ordering_priority_override.txt` immediately. The other bundles (Q2-CONTRACT, Q1-AGENTS, etc.) get added AFTER NEW-EXPLORATION returns and the user reviews — because their shape may change.

### 7.3 Risk: scope drift / never-ship

The danger of infrastructure-first is project failure — endless refinement, no shipped product. Mitigation:
- Each infrastructure task has bounded scope and ACs
- 0.0.1 stays the destination; the path adjusts
- Per-bundle "good enough" is the standard, not "perfect"
- The 5-cycle back-pressure protocol applies (max 5 iterations on a question before escalating to developer)

The user's commitment to total-cost optimization, combined with the existing back-pressure discipline, makes this safer than for a team without those guardrails.

---

## 8. The single task to seed now: NEW-EXPLORATION

Goal.md is largely drafted by the meta-exploration agent (file 08 §0). Updates needed per round-5 findings:

| Field | Original (file 08) | Updated |
|---|---|---|
| `parent_requirement` | REQ-PROC-TBD | **REQ-PROC-044** (per §2.1) |
| Background section | "developer's framing... 'transparency becomes an issue'" | Add reference to REQ-PROC-044 ACs that this task operationalizes |
| Seeds | 8 seed questions | Add: inventory pass at start (read STATUS.md; grep for related factory_* explore tasks); honest dependency on TASK-PROC-057-01 if it completes during this task |
| Execution Model | "Multiple rounds" | Add: total-cost framing — this task is the *prerequisite* for downstream infrastructure tasks (Q2-CONTRACT et al.); execute efficiently |
| Acceptance Criteria | 6 ACs | Add: "Recommendations include task-creation for downstream work" (per S2 — handoff files alone are dead ends) |
| Awareness | Not in original | Add: reference TASK-PROC-057-01 (apex, in-progress) — not a blocker; integrate constraints if it completes first |

After updating the draft, **invoke `task-create` once** to seed this single task. Add the resulting task ID to `task_ordering_priority_override.txt` (insert after the most recent REQ-PROC-049 entry; before the REQ-PROC-046 tier-0 group).

---

## 9. Net updated plan

### 9.1 What gets seeded NOW

1. **NEW-EXPLORATION** (TASK-PROC-044-XX, exact ID assigned by `allocate_task_id.py`) — single task. Parent: REQ-PROC-044.
2. Added to `task_ordering_priority_override.txt`.

### 9.2 What's deferred until NEW-EXPLORATION returns

All 10 other bundles from iteration-4 §9:
- Q2-CONTRACT, DOMAIN-VOCAB, NEW-SKILL, Q1-AGENTS, VISUAL-VALIDATE, BREAKPOINTS, INSPIRATION, PREBRIEF, CROSS-FEATURE, SCRIBBLE-SPLIT

Why deferred:
- NEW-EXPLORATION may discover the contract mechanism (sidecar vs frontmatter vs registry) differs from the meta-exploration's proposal → consumer-skill changes in Q2-CONTRACT depend on this
- NEW-EXPLORATION's sub-skill recommendation may differ from the agent's 4-cut → SCRIBBLE-SPLIT depends on this
- NEW-EXPLORATION's bidirectional-feedback formalization may differ from the stub in Q2-CONTRACT → revision_requests schema depends on this
- Token-efficiency analysis (companion §6) may recommend splits that affect Q1-AGENTS and SCRIBBLE-SPLIT
- Existing factory_purpose work (TASK-PROC-057-01) may complete during this period and impose constraints

### 9.3 Plan record (for the future iteration after NEW-EXPLORATION)

When NEW-EXPLORATION returns, re-open this exploration task (TASK-PROC-032-10) for iteration 6, which will:
1. Read NEW-EXPLORATION's synthesis + the companion token analysis
2. Update each of the 10 deferred bundles to reflect the ratified mechanism
3. Re-confirm dependency order
4. Seed the now-validated bundles via `task-create`
5. Add to `task_ordering_priority_override.txt`
6. Then tick the exploration ACs and `task-complete` on TASK-PROC-032-10

### 9.4 Updated decision changes (round 5 net)

| ID | Change |
|---|---|
| D37 (NEW-EXPLORATION) | parent_requirement = REQ-PROC-044, not a new REQ |
| D38 (revision_requests) | Rule added: standalone work → task; decision/review → revision_request file; developer question → pending_feedback. Formalized by NEW-EXPLORATION. |
| D41 (`presentation_layer:`) | **DROPPED** — auto-discovery heuristic instead |
| D42 (`serves_requirements:`) | **DROPPED** — `requirements_matrix.md` parser instead |
| D40 (auto-discovery script) | Updated: reads `requirements_matrix.md` + heuristic for UI scope |

---

## 10. Honest gaps and risks (round-5 specific)

- **The 1-task-only seeding** is a deliberate slowdown. If NEW-EXPLORATION takes longer than expected, the rest of the plan is gated. Mitigation: NEW-EXPLORATION is an explore-task with bounded scope; it's not an open-ended research project.
- **REQ-PROC-044 parent assumption** rests on the AC mapping in §2.1. If during NEW-EXPLORATION the actual mechanism turns out to need new ACs on REQ-PROC-044, that's a small `requ-explore` follow-up, not a re-parenting.
- **`requirements_matrix.md` may not exist for every flow.** Some flows are pre-cluster (single-flow) or post-cluster (still being authored). The auto-discovery script needs a fallback: "no matrix found — flag for user; do not silently produce empty contributing_requirements."
- **TASK-PROC-057-01 (apex) running in parallel** could surface a constraint that conflicts with our mechanism choice. Mitigation: NEW-EXPLORATION's executor reads TASK-PROC-057-01 progress at start; the apex's "minimum effective dose" framing already aligns with our sidecar-not-inline approach.
- **Hybrid PRINCE2 framing** in §4 may not survive contact with NEW-EXPLORATION's prototype phase. If the prototype shows artifact-first wins for a specific case, we adopt that case. The framing is a starting position, not a fixed conclusion.
- **The user warned the meta-exploration agent's findings are incomplete.** Honest concession: we are leaning on those findings to set the direction. NEW-EXPLORATION must validate. The fact that some recommendations may change is *expected*, not a failure.

---

## 11. Next steps

1. **Update the NEW-EXPLORATION goal.md draft** per §8 (parent_requirement → REQ-PROC-044; added seeds; added awareness of TASK-PROC-057-01).
2. **Invoke `task-create`** with the updated draft. Single task creation.
3. **Add the resulting task ID** to `flutter_app/.claude/task_ordering_priority_override.txt`.
4. **Do NOT tick** the exploration ACs on TASK-PROC-032-10's goal.md yet — wait for NEW-EXPLORATION to return and iteration-6 to incorporate it.
5. **Do NOT invoke `task-complete`** on TASK-PROC-032-10 yet — this exploration is paused, not done.
6. **Companion document** §6 is written separately.
