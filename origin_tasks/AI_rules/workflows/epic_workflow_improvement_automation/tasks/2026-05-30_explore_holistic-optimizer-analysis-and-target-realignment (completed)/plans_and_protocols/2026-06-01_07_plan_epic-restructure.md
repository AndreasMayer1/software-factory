---
name: epic_restructure_plan
description: >
  Plan (NOT execution) for elevating REQ-PROC-006 "Workflow Improvement Automation"
  from a single feature requirement to an EPIC with feature requirements, per the
  developer's 2026-06-01 feedback. Proposes the feature breakdown with justification
  and a design-element coverage matrix, the handling of existing/pending tasks, the
  per-feature exploration tasks (each carrying its seeds + references), and an
  agent-based execution plan. Captures the round-4 developer answers/ideas as
  per-feature seeds. Requires developer approval before any execution.
created: 2026-06-01
type: restructure_plan
author: claude-opus
task: TASK-PROC-006-20
session: 97dbf4eb-4a12-4f8a-ab78-d7c1fa2b12fa
status: awaiting_approval
references:
  - 2026-05-30_02_synthesis_round1.md
  - 2026-05-30_04_synthesis_round2.md
  - 2026-05-31_06_synthesis_round3.md
  - 2026-05-30_03_feedback.md
  - 2026-05-31_05_feedback.md
  - 2026-06-01_feedback.md
  - ../../2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/ (rounds 1–4, decisions log)
  - requirements.md (REQ-PROC-006 — the requirement being elevated)
---

# Plan: Elevate REQ-PROC-006 to an Epic + Restructure

> **This is a plan, not an execution.** Per the developer's instruction ("don't just
> do the restructuring — create a plan first and ask me for approval; use agents to
> do it"), nothing below is acted on until approved. §6 is the execution plan that
> runs *after* approval, via agents.

---

## 0. Why now (developer's decision)

Three synthesis rounds (`_02`, `_04`, `_06`) have grown REQ-PROC-006 well past what a
single feature requirement should hold: it now spans detection, a target model, two
evaluation modalities (statistical + simulation), five guardrails, orchestration, an
audit, and a self-experiment. The developer's call: **stop iterating at the
whole-system level (it's good enough to close there), elevate to an epic, and push
the remaining gap-filling down into per-feature exploration tasks** — repeating, per
feature, the multi-round deepening we just did for the whole.

This plan does **not** finalize the feature designs. It defines the *structure* and
the *seeds*; each feature's own exploration task does the deepening (deferred, as the
developer asked).

---

## 1. Proposed structure

### 1.1 The epic

- **Folder:** rename `workflow_improvement_automation/` → `epic_workflow_improvement_automation/`
  (requ-explore convention: epics carry the `epic_` prefix).
- **ID:** the epic keeps **REQ-PROC-006**. Every existing cross-reference
  (REQ-PROC-044 / 008 / 046 / 059, the `.factory/optimize/` implementation, the
  deny-list, all `TASK-PROC-006-NN`) continues to resolve — the epic id is unchanged.
- **Epic requirements.md:** trimmed to epic-level content only (Overview, Purpose,
  Scope, Features index, Cross-Feature Invariants = the G-INVs, Dependencies,
  Glossary). The three non-removable guardrails G-INV-1/2/3 (and the proposed
  G-INV-4/5) live here as **Cross-Feature Invariants** because they bind *all*
  features. The current feature-level detail (monitor tables, taxonomy, heuristics,
  deny-list contents) moves down into the owning feature.

### 1.2 The features (recommended: 7)

Each is a cohesive, separately-explorable, separately-implementable concern. IDs
shown as derived child IDs (decision D-A in §5 — derived vs fresh).

| # | Feature folder | Owns (from the synthesis) |
|---|---|---|
| **F-01** | `feat_detection_event_pipeline` | The 4 monitors + aggregator, event schema/idempotency, the **consolidation combiner script** (R2 D-3), per-file granularity, queue ceiling, and **trajectory logging** so real tasks can be replayed (R3 §5.2). |
| **F-02** | `feat_targets_metrics_audit` | The **three-layer target model** (north-star + GQM leading indicators + guardrail pointers), AND the **audit skill** + effectiveness metrics + deterministic rubric (loop-hygiene *and* north-star-laddered halves). Merged because "what to aim at" and "how the loop is scored" are one measurement concern. Absorbs pending **TASK-PROC-006-16** (DuckDB optional query layer). |
| **F-03** | `feat_evaluation_statistical_contract` | The **slow real-signal evaluation contract**: events-not-tasks (`min_evidence`), mSPRT/e-value anytime-valid stopping, CUSUM drift, the pending→verdict lifecycle, attribution + holdback. |
| **F-04** | `feat_evaluation_simulation_harness` | The **fast offline verdict**: skill-creator paired old-vs-new, scenario sets, **Git-branch test-data management + cleanup + naming** (R4 seed), **held-out 60/40 split**, **synthetic-only-from-real** (R4 seed), the **dynamic per-skill simulation budget** (R4 seed), scenario-set deny-list + add/deprecate lifecycle (R4 seed). |
| **F-05** | `feat_guardrails_and_budgets` | The **session-byte budget start-gate** (G-INV-4, soft, shared-CCS-authoritative), **meta-work subordination** (G-INV-5), the **deny-list** (incl. scenario-set protection), and the **meta-recursion boundary** (optimizer tunes dials, never the ruler). G-INV-1/2/3 are stated in the epic but their enforcement detail lives here. |
| **F-06** | `feat_orchestration_cadence_production` | The **subordinate autonomous trigger** (reversed F-1, not preempt-all), the **activity-gated weekly cadence** (`last_self_run_iso_week`), the **producer skill** (`claude-optimize`), **ranked-batch consumption + proposal cap/digest**. |
| **F-07** | `feat_self_optimization_experiment` | The **two staged, developer-witnessed test runs** (drain&baseline, then optimizer-on-itself), **OEC + auto-abort guardrails**, the experiment's kill-switch. A bounded activity, distinct from the standing guardrails in F-05. |

**Alternatives noted (developer may prefer):**
- *Leaner (5):* merge F-03+F-04 into one "Improvement Evaluation" feature, and F-07
  into F-05. Risk: F-03/F-04 are each large and the developer treats simulation as a
  major distinct area — merging buries it.
- *Granular (8):* split F-02 back into separate "Targets" and "Audit" features. Risk:
  the audit exists only to score the targets; splitting duplicates context.
- **Recommendation: the 7 above** — clean seams, each maps to one exploration task,
  no element is orphaned or duplicated.

### 1.3 Coverage matrix (nothing lost)

Every design element from rounds 1–3 maps to exactly one feature:

| Design element (round) | Feature |
|---|---|
| Monitors, consolidation script, event ceiling, trajectory logging (R1 §3.2/3.3, R2 §4, R3 §5.2) | F-01 |
| North-star + GQM leading indicators, three-layer model (R1 §2, R2 §8.1) | F-02 |
| Audit skill, metrics, rubric, DuckDB layer (R1 §2.4, existing impl, 006-16) | F-02 |
| Statistical contract: events/mSPRT/CUSUM/lifecycle/attribution (R2 §2/§7) | F-03 |
| Simulation harness, scenario sets, Git-branch data, held-out, synthetic-from-real, sim budget (R3 §2/§5, R4) | F-04 |
| G-INV-4 budget start-gate, G-INV-5 subordination, deny-list, meta-recursion boundary (R1 §8.2, R2 §2.5/§3, R3 §1.2) | F-05 |
| Subordinate F-1 trigger, weekly cadence, producer skill, proposal cap/digest (R1 §3.1/3.2, R3 §3) | F-06 |
| Two test runs, OEC + auto-abort, kill-switch (R1 §5, R2 §5.2, R3) | F-07 |
| G-INV-1/2/3 (cross-cutting) | Epic (Cross-Feature Invariants) |

---

## 2. Handling existing tasks

Per the developer ("keep them on epic level… pending ones maybe to the correct
features"):

- **All completed / cancelled tasks (18) stay in the epic's `tasks/` folder.** They
  are historical record of how the epic was built; redistributing them would break
  references and gain nothing. *No change.*
- **The one pending impl task — TASK-PROC-006-16 (DuckDB optional query layer)** —
  moves to **F-02** (`feat_targets_metrics_audit/tasks/`), since it is an audit-
  analytics enhancement. Its `parent_requirement` updates to F-02's ID. *(Minor: the
  folders for 006-14 and 006-16 lack the `(completed)` suffix; 006-14 is actually
  completed — leave as-is, out of scope for this restructure.)*
- **This task, TASK-PROC-006-20 (in_progress),** closes at **epic level** — it is the
  cross-cutting analysis that birthed the epic. Its synthesis docs are the shared
  reference base for all feature explorations (§3).

---

## 3. The per-feature exploration tasks (the deferred deepening)

Create **one `explore` task per feature** (7 total). Each:

- Lives in its feature's `tasks/` folder; `parent_requirement` = the feature ID;
  `type: explore`; `writes_requirements: false` (it deepens, then a later `requ-explore`
  writes the feature requirement) — OR writes the feature requirement directly
  (decision D-B in §5).
- **References the full iteration history** in its goal.md: this task's
  `_02`/`_04`/`_06` syntheses and `_03`/`_05`/`_06-01` feedback, plus the old
  exploration (`2026-05-01_…/` rounds 1–4 + decisions log). The instruction the
  developer gave: *"so it has the whole picture."*
- **Carries its feature-specific seeds** (the round-4 inputs, distributed in §4).
- Goal: *fill the gaps we deferred and iterate before the implementation tasks are
  (re)written* — i.e., do per-feature what 006-20 did for the whole system.

These 7 tasks are created but **not run** by this restructure; they enter the normal
queue (subordinate to product delivery, per G-INV-5).

---

## 4. Round-4 developer inputs — captured as per-feature seeds

So they are not lost when this task closes:

**→ F-04 (simulation harness):**
- **Git-branch test-data sets.** Real logged tasks become test datasets pointed to by
  dedicated **git branches**, so any commit/dataset can be checked out and re-run.
  Needs: a **cleanup mechanism** and a **naming convention** that makes clear which
  branches are disposable vs must-keep. Same mechanism for synthetic datasets.
- **Synthetic-only-from-real.** Never synthesize test data "from nothing." First
  collect a **real** dataset; derive synthetic data *from* it. (Bounds R3 §5.3 /
  the web research's "replay-first, synthesize-for-gaps" — the developer is stricter:
  synthetic must be *derived from* real, not invented.)
- **Simulation cost is dynamic, per-skill.** Iterative/feedback skills → simulate
  **one iteration**. Token-heavy skills (e.g. scribble generation emitting many HTML
  files) cost far more. Approach: **first simulation of a skill runs UN-budgeted and
  is measured** to establish a per-skill baseline; thereafter allow ~**3 iterations**
  as a starting cap, adapt up/down from the measured baseline. This is a **separate
  simulation budget**, distinct from the 4 MB weekly meta-work budget (F-05).
- **Scenario deny-list lifecycle.** Once created, a scenario is **deny-listed** (can't
  be edited). But there must be a **tamper-resistant** mechanism to *add* new
  scenarios and *deprecate/delete* old ones — "a mechanism that cannot be tricked
  easily." (Open design problem for F-04.)

**→ F-06 (orchestration/cadence):**
- **Weekly trigger:** the developer accepted the activity-gated `last_self_run_iso_week`
  recommendation — *"let's not over-engineer it."* The date-aware `awaits` field is
  dropped for now.

**→ F-05 (guardrails/budgets):**
- The simulation budget (above) interacts with the 4 MB weekly budget — F-05 owns the
  weekly budget; F-04 owns the per-skill simulation sub-budget; they must compose.

---

## 5. Decisions needing the developer's nod (at approval)

- **D-A — Feature ID scheme.** Derived child IDs (`REQ-PROC-006-01 … -07`, implies
  membership by hierarchy) **vs** fresh top-level IDs (`REQ-PROC-0NN`). *Recommend
  derived* (clearest epic membership; the `allocate_req_id.py` script supports it).
  Caveat: derived REQ-PROC-006-NN visually rhymes with TASK-PROC-006-NN but the
  REQ-/TASK- prefixes keep the namespaces distinct.
- **D-B — Do the per-feature explore tasks write their feature requirement, or just
  deepen first?** *Recommend:* each explore task **deepens then writes its feature
  requirement** at the end (via `requ-explore`), so we don't need a second task per
  feature. (The feature requirements.md files are created as **placeholders** during
  the restructure, then filled by their explore task.)
- **D-C — Feature count: the recommended 7, the leaner 5, or the granular 8?** (§1.2)
- **D-D — When to execute?** Spawn the restructuring agents **in this session right
  after approval**, or hand off to the orchestrator as a separate effort? *Recommend:*
  execute right after approval (it is bounded, mostly mechanical), then close 006-20.

---

## 6. Execution plan (runs ONLY after approval — agent-based)

The developer asked for agents, not inline work, "because all tasks must be
distributed." Proposed sequence:

1. **Agent 1 — epic skeleton (`requ-explore` / structural).** Rename the folder to
   `epic_…`, rewrite `requirements.md` to epic-level (Overview/Purpose/Scope/Features
   index/Cross-Feature Invariants = G-INVs/Dependencies), apply the Epic Size Gate
   (≤90 body lines). Returns the trimmed epic + the list of feature folders to create.
2. **Agent 2 — feature placeholders.** Create the 7 `feat_*/requirements.md` files as
   `status: placeholder` with the §1.2 scope + the §4 seeds embedded, and allocate
   their IDs (per D-A). Move pending **TASK-PROC-006-16** into F-02 and fix its
   `parent_requirement`.
3. **Agent 3 — per-feature exploration tasks.** Via `task-create`, mint 7 `explore`
   goal.md files (one per feature), each referencing the full iteration history (§3)
   and carrying its seeds (§4).
4. **Validation + status.** Run `validate_meta.py`, regenerate STATUS, fix any
   dangling references (the merged `requirements.md`, cross-refs).
5. **Close 006-20** via `task-complete` (the human-gate AC is satisfied by this
   plan's approval + the executed restructure).

Each agent writes its result to `plans_and_protocols/` (claude-log) and is spawned
**in the background with a heartbeat** if long-running, per CLAUDE.md cache rules.

> Spawn agents only for steps that are bulk/multi-file (2 and 3 especially). Step 1
> is small enough to do directly if preferred. Final choice deferred to D-D.

---

## 7. Honest notes

- **Scope of this restructure is structural, not design-final.** The feature
  requirements created here are *placeholders*; the real per-feature design happens in
  the 7 exploration tasks. This is exactly the developer's intent (defer the
  gap-filling), but it means the epic is "shaped, not finished" after this step.
- **The synthesis docs (_02/_04/_06) stay in the epic's closed 006-20 task** and are
  referenced by all feature explorations — they are the canonical shared context. If
  they ever move, every feature task's references break; better to leave them put.
- **One genuine open problem is parked, not solved:** the tamper-resistant
  scenario-add/deprecate mechanism (§4 → F-04). Flagging so it isn't mistaken for
  designed.
- **No implementation tasks are modified here.** The developer was explicit: the
  per-feature explorations precede any rewrite of the implementation tasks.

---

## 8. What I need from you (approval gate)

Approve the structure (or adjust), and answer D-A…D-D (§5). On approval I will execute
§6 (agent-based) and close 006-20. If you'd rather change the feature breakdown,
merge/split, or rename anything, say so and I'll revise the plan before executing.
