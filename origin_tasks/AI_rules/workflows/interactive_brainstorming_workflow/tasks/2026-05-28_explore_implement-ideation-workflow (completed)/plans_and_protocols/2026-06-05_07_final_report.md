# Final Report — TASK-PROC-004-02
## Implementing the Structured Ideation Workflow (the HOW)

**For**: the developer + the next implementer.
**Spec**: REQ-PROC-004 "Structured Ideation Workflow" (the WHAT). ⚠ The goal body refers to "REQ-PROC-067" — that ID is actually *Claude Code Usability*; the real controlling requirement is **REQ-PROC-004**. Worth correcting in the goal/requirement text.

---

## 1. Problem framing (condensed)

The factory's explorations converge too fast (adequate, not creative) AND their syntheses still carry open questions. The gathering phase showed these are **two orthogonal problems**:
- **Divergence** (idea quality) — the model converges prematurely as a *structural* failure.
- **Completeness** (answer coverage) — a single request's *output budget* can't emit the whole answer (the 2026-06-05 follow-up's clarification: this is NOT input-context/reload, it's output-production capacity).

Both are controlled by **one shared artifact, a Ledger**. And — the biggest surprise — **the factory already contains most of the machinery**; the build is largely composition, not invention.

## 2. Ideation highlights
- **Most useful**: the completeness loop already exists in disguise — orchestrator `--resume` = the continuation vehicle; `cycle_state.json` 5-cycle back-pressure = a bounded loop with human escalation; `requ-verify-flow-coverage` = gap-extraction→synthesis; `pending_feedback` = the file-watch user gate the requirement describes.
- **Most unusual**: a direct-Anthropic-API wrapper to actually set `temperature: 0.9` per phase — currently blocked (the CLI can't, and the dependency gate forbids it), but the *only* real temperature lever; recorded as a future unlock.
- **Sharpest**: "no gaps remain" defined as a **fixpoint** (no rows added or closed) / **thermostat** (coverage ≥ effort setpoint) — operational, not a vibe.

## 3. Recommended design (decisions, with rationale)

1. **Vehicle = layered, effort-gated** (not one thing):
   - **L0** — a protocol doc `doc/process/ideation_protocol.md` (ledger schema + prompt blocks), `Read` just-in-time by opt-in skills. No new always-loaded skill → protects token economy (REQ-PROC-059 b/e/h).
   - **L1** — inline multi-frame CoT divergence in the calling skill's own session (Quick/Standard).
   - **L2** — isolated branch agents (`ideation-explorer`) + a separate `*-reviewer` gap-critic agent (Deep / high-reversal-cost). Only the Agent tool isolates context (anti-anchoring, per the ADHD evidence).
2. **Divergence = prompt levers, NOT temperature** (CLI can't set it; it's empirically weak): chain-of-thought + a software-architecture **frame library** + **mechanical generator/critic mode separation** + curated random stimulus. A paste-ready ideation prompt block is in the synthesis (§Decision 2). REQ-PROC-004's seven techniques are kept but re-cast as frames/operations inside this structure.
3. **The Ledger** (`plans_and_protocols/[date]_NN_ledger.md`): markdown table; rows are `idea` or `gap`; `gap_type ∈ {breadth, depth}`; `status` kanban; critic is **append-only** (anti-oscillation). Full schema in synthesis §Decision 3.
4. **Completeness loop**: gap-detection **first** each iteration (set-difference `scope − answered`), advance only what fits this output budget, leave the rest `open`, hand forward via the ledger. **Continuation defaults to same-session** (no reload — the constraint is output not input); cold restart only when input-context is near limit or anti-anchoring is wanted. Terminate on `gaps_empty OR max_iter OR closure_rate < ε`; on a capped exit emit an `## Open Gaps` appendix (honesty). Effort bounds `max_iter` (Quick 1 / Standard 2 / Deep 3–4).
5. **One unified gate** via the existing `pending_feedback` mechanism with a `mode:` field (`ideation_review` at the divergence→synthesis boundary; `gap_escalation` only if capped-with-gaps). Completeness iterations are machine-internal — at most two human touch-points regardless of iteration count. Automated mode routes both through the orchestrator resume (sessions must not self-schedule — CLAUDE.md boundary).
6. **Integration order (minimal-first)**: `task-resolve` → `requ-explore` → `code-complex` planning → (later) ux-create-flow / task-create template. Build L0 → L1 → L2 in that order.

## 4. Decisions that need the developer (before implementation)

These are genuine forks the implementer should not silently pick:

- **D1 — Scope of the first build.** Recommend: build L0 (protocol doc) + L1 (inline) + wire into `task-resolve` only, and defer L2 agents until that proves out. Confirm, or ask for the full L0–L2 + multi-skill rollout in one pass.
- **D2 — Where the protocol doc lives.** Recommend `doc/process/ideation_protocol.md` (LAW, just-in-time read). Alternative: keep it inside REQ-PROC-004's requirement folder as guidance. `doc/` makes it enforceable for skills; the requirement folder keeps process docs together. Pick one.
- **D3 — Reviewer/critic as a separate agent (L2) vs. a self-pass at all tiers.** Evidence favors a *separate* critic (self-assessment is biased), but that's a spawn cost at every Deep run. Confirm separate-agent for Deep, self-pass for Quick/Standard — or mandate separate-critic everywhere.
- **D4 — Calibration constants** (`depth_score` threshold, `closure_rate ε`, per-effort `max_iter`): proposed values are in the synthesis but are first guesses. Accept as defaults to be tuned, or set explicit values now.
- **D5 — The ID correction**: fix the goal/requirement cross-reference (REQ-PROC-067 → REQ-PROC-004). Confirm this is a typo and not a missing requirement.

## 5. Open questions the exploration did NOT resolve (honest uncertainty)
- Whether L2 branch isolation's anti-anchoring benefit justifies its spawn cost at **Standard** effort (currently assigned L1) — only an A/B on real tasks settles this.
- Real values for `depth_score` threshold and `ε` — unknowable without observing actual iteration runs.
- Residual **critic oscillation** risk: "append-only" mitigates but doesn't eliminate it.
- Whether the seven REQ-PROC-004 techniques, re-cast as frames, fully cover *non-architecture* (UX, requirement) ideation — the ADHD evidence is architecture-specific.
- The "multilingual prompting" diversity lever is real in the literature but unverified for an English code-only factory; parked as optional.

## 6. Suggested next steps
1. Developer answers D1–D5 (these gate implementation).
2. Create an **impl task** for L0 + L1 + `task-resolve` integration (recommend `task-create-code`/`task-resolve`-style, opus not required — it's authoring a protocol doc + a skill section). Carry the synthesis §Decisions 2–5 as the spec.
3. After it runs on ~3 real explore tasks, create a **calibration follow-up** to set D4 constants and decide D3/Standard-L2 from observed data.
4. Optionally, a tiny requirement note recording I31 (direct-API temperature) as a future unlock dependent on the factory gaining direct Anthropic-API calls.

---
### Acceptance-criteria check (goal)
- ✅ ≥1 synthesis round — `..._06_synthesis.md`.
- ✅ Defines the space beyond what was known at creation — the divergence/completeness orthogonality + "the loop already exists in the factory" were not in the goal.
- ✅ Decisions needing user framed clearly — §4 D1–D5.
- ✅ Honest about uncertainty — §5.
- ✅ Multi-run iteration design with gap-ledger (breadth+depth), gap-driven terminal condition, runaway backstop — synthesis §Decisions 3–4.
