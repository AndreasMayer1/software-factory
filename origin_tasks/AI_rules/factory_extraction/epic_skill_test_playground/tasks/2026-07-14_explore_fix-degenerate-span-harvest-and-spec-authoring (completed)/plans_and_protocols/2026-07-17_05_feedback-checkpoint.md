---
skill: requ-explore (embedded ideation-start end-of-run gate)
mode: automated
decision: ""
task_id: TASK-PROC-068-27
captured_at: 2026-07-17
---

# Question

---
task_id: TASK-PROC-068-27
session_id: de9647b5-61b2-4b75-9729-0bf119b96ce6
account: gmail2
asked_at: 2026-07-17T16:47:38Z
skill: requ-explore (embedded ideation-start end-of-run gate)
---

# Pending Question — Approve the degenerate-span-fix synthesis + intended requirement changes

Structured ideation is complete (IDEATION-023, composition, viable_count 1/K 1). This is the end-of-run
gate **and** goal AC-03: your approval is required before the requirement edits (they change the
HIGH-consequence EGP-F **AC-18**). Reply **by number**.

## Artifacts (open to read — not restated here)
- Synthesis (recommended design, per sub-problem + residual): `…/plans_and_protocols/2026-07-15_004_synthesis.md`
- Analysis (crux, criteria, decomposition): `…/plans_and_protocols/2026-07-15_003_analysis.md`
- Context (mechanism + defect + prior art): `…/plans_and_protocols/2026-07-15_002_context_summary.md`
- Ledger (38 ideas, criteria, 10 adversarial gaps, SOL-01): `…/plans_and_protocols/2026-07-15_001_ideation_ledger.yaml`

(paths under `requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-07-14_explore_fix-degenerate-span-harvest-and-spec-authoring/`)

## Recommended design (SOL-01) — the decision to approve
- **Fix locus (SP-1):** a distinct terminal `UnitStatus.VACUOUS`, granted **only** by a mechanism-computed
  **structural zero-authoring-pair proof** (never a child self-declaring); harvest oracle satisfied by
  `DONE ∪ VACUOUS`. The content-gate poka-yoke stays fully in force for every span that has authoring pairs,
  so VACUOUS cannot mask a real under-finish. (Rejected: overloading DONE = lies; oracle-only tolerance =
  can't tell a no-op from a real gate-fail; upstream drop-the-unit = breaks span-indexed chain-state.)
- **AC-18/19 (SP-2):** reword AC-18 so *abandoned* = a unit **with real authoring pairs** left not-terminal
  (a degenerate no-op is never abandoned/blamed); AC-19 clarifies "finished" = real spans DONE ∧ degenerate
  spans VACUOUS. Keeps the real "skill silently under-finished" guarantee true.
- **Harvestability pre-flight (SP-3):** an offline plan-time predictor reusing `resolve_spans` +
  per-span disposition + the oracle predicate to predict the verdict over the best-case terminal; fails a
  doomed spec loudly with a distinct exit code; persists a **resume-re-validated `harvestable` stamp**.
- **Spec-authoring surface (SP-4):** extend `layer-derivation-start` to **derive `span_units` from
  `fixed_layers`** (degenerate-span mapping structurally inexpressible) + a governed spec template + a
  **teaching linter that IS the pre-flight gate** (guidance and gate are the same code; NOT `doc/`). No new
  standalone skill.
- **Migration/reporting tier:** migrate persisted `ESCALATED('gate_content_fail')` zero-pair units to
  VACUOUS; `layer-derivation-status` reports VACUOUS as "no-op complete"; one shared test helper migrates the
  ≥7 ESCALATE-skip sites. **Retires the 068-26/068-12 Option-A workaround.**

## Open adversarial findings (weigh these — informational)
- analyze→ideate: ADV-01 poka-yoke collision (addressed by structural-proof gating); ADV-02 ≥7 test-site
  blast radius; ADV-03 layer-derivation-status mis-report; ADV-04 FORWARD/REVERSE + task_code degeneracy;
  ADV-05 multiple/all-degenerate chains; ADV-06 chain-state migration; ADV-07 `screen_derivability` is dead
  code in the production path.
- synthesize→gate: ADV-sg-01 `resolve_spans` zero-pair vs task_code-excluded conflation could wrongly stamp
  VACUOUS; ADV-sg-02 best-case pre-flight misses a span that can *never* reach DONE (no authoring skill for
  its pair); ADV-sg-03 migration could silently reclassify a *real* past gate-fail.

## Residual uncertainty needing your call
- **R1 (affects an AC):** an **all-degenerate** chain — complete-but-empty-harvest, or should the pre-flight
  **reject** it as a mis-specified `fixed_layers` set? (Recommendation: pre-flight rejects/warns.)
- **R2 (scope):** wire the dead `screen_derivability` (empty-required-elements) into the same VACUOUS route,
  or leave it out of scope?

## Options — reply by number
1. **APPROVE** — accept SOL-01 as-is; I proceed to edit REQ-PROC-068 (AC-18/19 + new pre-flight AC) and
   REQ-PROC-071/`layer-derivation-start` (new spec-authoring AC) via requ-explore, then emit impl task(s)
   via task-derive-from-requ. (Please also answer R1 and R2, or I take the recommendations: R1 = reject
   all-degenerate specs at pre-flight; R2 = wire screen_derivability into the VACUOUS route.)
2. **APPROVE WITH CHANGES** — state what to change in the design or the intended requirement edits.
3. **ITERATE** — re-run changed phases (say what changed: weights, framing, a new frame, new info).
4. **DROP** — abandon this run / relax framing.

# Developer Answer

APPROVE

# Rationale Captured

(Automated archival — no rationale extracted.)
