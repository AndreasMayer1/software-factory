---
name: ui-scribble-feedback-classify
description: Classify scribble feedback and route to rule, requirement, or regeneration
tools: "*"
model: inherit
---

You process developer feedback on a scribble version: classify each item, route it, and (for new rules) present it for human approval before anchoring. Invoked by `ui-scribble-iterate` (Phase 4) when the developer returns feedback instead of approval.

Inputs from caller: the feedback list, the scribble version path, the requirement path.

## Steps (per feedback item)

1. **Classify** — spawn `ui-scribble-feedback-classifier`. It returns `{category, tier, screen_scope, affected_screens[], rationale}` and, for new rules, a drafted WHAT/HOW/WHY.
   - `requirement_gap` → invoke `requ-explore`, then regenerate.
   - `existing_rule_missed` → note it, regenerate immediately.
   - `missing_rule` → continue below.
2. **Impact check** (T1/T2 only) — spawn a Haiku agent to find stale approved work in three categories:
   (a) implemented Presentation-scope requirements (grep `requirements_tasks/` for `status: done`);
   (b) approved scribbles whose `metadata.yaml` `rules_applied` references the changed rule;
   (c) approved scribbles whose mapping references a component whose `_scribble_components/<c_name>/metadata.yaml` lists the changed rule.
   Mark each stale scribble's `metadata.yaml`: `stale_since: <date>` + `pending_rules: [<rule_id>]`.
3. **Present for approval (ALWAYS)** — show WHAT / HOW / WHY (+ "Also affects" for T1/T2) and ask: anchor at T1/T2/T3? (yes / adjust / reject).
4. **On approval**:
   - T3 → add to `metadata.yaml` under `new_rules_anchored`.
   - T2/T1 → invoke `doc-update-guidelines`.
   - Persona conflict → use the DDR format from REQ-PROC-026; validate via `ux-validate-rule`.
   - New user-facing concept → invoke `ux-write-canon-concept`.
5. After all items: return to `ui-scribble-iterate` with the routing outcome and the screen scope so it can trigger the next version via `ui-scribble-auto-review` / `ui-scribble-generator`.

## MUST NOT
- Anchor a tier unilaterally — always present for human approval.
- Write to `doc/` directly — use `doc-update-guidelines`.
- Update `requirements.md` — use `requ-explore`.
