# Protocol — TASK-PROC-068-15 interactive resume (2026-07-02)

Developer resumed interactively and answered the parked question (answer.md):
1. T-B & T-C creation → **standalone authorized**.
2. T-C grounding (D3) → **create the other tasks first, then run `requ-explore` to find a home for the new
   AC; discuss placement together** ("you don't know where to put it").
3. T-D + 068-11 → **authorized to mint the obligation**.

Session is now genuinely interactive (`CLAUDE_AUTOMATED_MODE` empty, marker gone) — so standalone override
and obligation mint are both legitimate.

## Done (autonomous, this resume)

- **T-B = TASK-PROC-068-16** `extend-harness-deploy-full-factory` — REQ-PROC-068, covers **AC-10** (EGP F,
  MEDIUM), `after: []`. Carries exclude-set guidance + containment proof + recursive override rule. Schema PASS.
- **T-D = TASK-PROC-068-17** `resolve-068-11-targeting` — REQ-PROC-068, covers [], **mints
  `resolves_parked_task: TASK-PROC-068-11`** (dev-authorized), `after: [068-16, 041-04-06, -07, -08, -09]`.
  Verify-before-write + answer.md-untouched boundary baked in. Schema PASS.
- **068-11 rewired** `after: [] → [TASK-PROC-068-16]`.
- **Override**: 068-16 + 068-17 registered; a placeholder note records T-C + the 068-12 rewire as pending.

## Remaining (needs developer — D3 discussion, then finish)

- Settle T-C's grounding AC home (REQ-PROC-071 vs REQ-PROC-068) → `requ-explore` → author the AC.
- Create **T-C** `layer-derivation-reuse-of-deploy` grounded in that AC, `after: [068-16]`.
- Rewire **068-12** `after: [071-05-05, 068-11] → [+ T-C]`.
- Register T-C in the override; record **D4** flag (071-05-05 independently gates 068-12); no successor
  orchestration task; `task-complete`.

## D3 analysis (for the discussion)

T-C teaches `layer-derivation-start` (+ its unit skills) to run under the **deployed harness** so 068-12
consumes the same mechanism as 068-11. The new behavior ≈ "the layer-derivation workflow can run its unit
skills against a deployed/target-rooted harness, not only the main factory tree."

- **REQ-PROC-071 (Epic Layer Derivation)** — owns the layer-derivation subsystem; `layer-derivation-start`
  is a 071 artifact. If the AC is framed as a **durable capability of the derivation engine** (target-root /
  deployment awareness that outlives the playground), it belongs here. 071 is at 86% (6/7); a new AC would
  go at epic level or into a specific `feat_*`. **Leaning here.**
- **REQ-PROC-068 (Playground)** — owns the harness/deploy; AC-10 already says "a contained child can invoke
  *any* factory skill end-to-end." One could argue T-C is just an **impl realization of AC-10** for the
  derivation skill (→ **no new AC**, T-C covers AC-10 like T-B). But the developer's framing ("find a home
  for this new AC") implies a genuinely new behavior, which points away from plain AC-10 reuse.

**Recommendation to raise:** ground the new AC in **REQ-PROC-071** if the behavior is "derivation workflow
gains target-root/harness-run capability"; keep it in **REQ-PROC-068** (or reuse AC-10, no new AC) if we
frame it as "the harness runs the derivation workflow." Decide framing first, then requ-explore.
