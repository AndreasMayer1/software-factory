# Protocol: FLOW-003 Iteration Approach — Q&A + VTR + Deviations

**Date**: 2026-03-24
**Status**: Active — use this as the playbook for all remaining FLOW-003 iterations

---

## Context

### Iteration history

- **Iteration 1** (2026-03-20): First feedback round on the draft flow
- **Iteration 2** (2026-03-21): Second feedback round
- **Iteration 3** (2026-03-21): Third feedback round — flow reached sufficient maturity for AI review
- **AI reviews** (2026-03-23): Opus conducted per-persona fit reviews and a cross-flow consistency review (FLOW-002 vs. FLOW-003). See `ai_reviews/` folder.
- **Iteration 4** (2026-03-24): Incorporated `user_feedback/2026-03-24_04_feedback.md` — time-based detection model (Step 5), Exception refinements, two FLOW-002 gaps.
- **Iteration 5** (2026-03-25): Q&A decisions round — incorporated all 11 decisions from `user_feedback/2026-03-25_05_qa_answers.md`. Major changes: QR-first UX (Q1), mid-transfer exit no-dialog (Q2), Dr. Turan safety Adaptive UI Rule (Q3), non-blocking first-session orientation (Q4), transitional animations (Q5), icon-only progressive disclosure (Q8), therapist scenario relationships corrected to 'supporting' (Q9), battery non-blame framing (Q10), Environment column deviation (Q11), DEV-1 Weber deviation + FLOW_INDEX.md async flow entry (DEV-1), VTR-004 + VTR-005 added. Committed: dc208289. Agent: claude-sonnet-4-6-2026-03-25

### Why a new approach after iteration 4

After three feedback iterations and the AI reviews, the remaining open issues are no longer simple gaps — they are **design decisions** involving conflicting persona values. An AI improving the flow without explicit user input will either make silent trade-offs or produce a flow that serves no persona well.

The AI reviews are:
- `ai_reviews/2026-03-23_review_flow_comparison.md`
- `ai_reviews/2026-03-23_review_max.md`
- `ai_reviews/2026-03-23_review_jana.md`
- `ai_reviews/2026-03-23_review_dr_sarah.md`
- `ai_reviews/2026-03-23_review_sophie.md`
- `ai_reviews/2026-03-23_review_weber.md`
- `ai_reviews/2026-03-23_review_turan.md`

---

## Iteration Approach

### Step 1 — AI extracts open decision points

Opus reads all persona reviews + current `flow.md` and extracts the open decision points: cases where the flow cannot serve all personas simultaneously and a trade-off must be made. It presents these as numbered questions, grouped by severity (High / Medium / Low), with:
- Clear options
- Per-persona impact for each option
- Its own recommendation (if one is clearly better)

### Step 2 — User answers

The user answers each question. These answers are the authoritative design decisions.

### Step 3 — AI writes next iteration

The AI incorporates the decisions into `flow.md` via `ux-update` skill, as in previous iterations.

### Step 4 — Document decisions

After incorporating, each decided trade-off is documented using one of two mechanisms:

- **Value Trade-off Record (VTR)**: When a decision consciously degrades one persona's value to serve another's. Embedded inline in `flow.md` using the `vcd-log-tradeoff` skill. Format defined in `requirements_user_needs/_meta/value_tradeoff_record_template.md`.
- **Deviation entry**: When a need is structurally out of scope for FLOW-003 (not a conflict, but a limit). Added to the `## Deviations from User Needs` section in `flow.md`. Format defined in `requirements_user_needs/README_14_DEVIATION_DOCUMENTATION.md`.

### Step 5 — Repeat

Until all High and Medium decision points are resolved and the user grants approval (`review_status: approved`).

---

## Known Decisions Already Made

### Dr. Weber — pre-session async transfer is a new flow

FLOW-003 requires a laptop with webcam in the therapy room. Prof. Dr. Weber's room has no visible technology by design — this is a clinical constraint, not a preference. An exception inside FLOW-003 cannot resolve this because the entire in-session transfer model is incompatible with his practice.

**Decision**: This is a Deviation in FLOW-003 (structural limit), not a VTR. A new dedicated flow covers the pre-session / async transfer model:
- Client sends encrypted file in advance (e.g. email)
- Therapist reviews visualization before the session, device closed before client enters
- Potentially useful for other therapists too (e.g. Dr. Sarah may prefer reviewing before the session)

**Action items for next iteration**:
1. Add Deviation entry to FLOW-003 for Weber's use case, referencing the planned new flow
2. Add brainstorm entry to `requirements_user_needs/user_flows/FLOW_INDEX.md` for the pre-session async transfer flow

---

## Files to Read Before Starting Any Iteration

1. `requirements_user_needs/user_flows/session_start_data_transfer/flow.md` — current flow
2. `requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md` — FLOW-002 (reference for consistency)
3. All files in `ai_reviews/` — persona fit analysis
4. `user_feedback/` — all feedback files (sorted by date = chronological order of iterations)
5. `requirements_user_needs/README_14_DEVIATION_DOCUMENTATION.md` — deviation format
6. `requirements_user_needs/_meta/value_tradeoff_record_template.md` — VTR format
