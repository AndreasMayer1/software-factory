## 2026-05-25
**Agent**: claude-log (main session)
**Agent ID**: ccbc2765-5e77-4d98-98fa-180a71a387f9
**Action**: Updated `.claude/skills/task-create-code/SKILL.md` via `claude-modify-skill` to implement AC-10, AC-11, AC-12 consumer, AC-13, AC-15 requirements from REQ-PROC-058.

Changes applied:
1. Added `## Redirect Logic (AC-10) — Standalone Mode Only` section before Phase 0 — standalone+impl/verify+uncovered ACs → redirect to task-derive-from-requ; --standalone-override escape hatch; automated: never auto-override.
2. Phase 0A step 3: effort bullet changed to "accepted as baseline; Phase 2 still runs to refine (AC-15)"; opus_recommended similarly accepts baseline; added requirements_version bullet pointing to step 3.5.
3. Phase 0A step 3.5 (new): stale-plan check — compares plan's `requirements_version.commit` against current git hash; interactive warns+asks; automated writes question.md + stops.
4. Phase 2.3: added plan-driven escalation block — file analysis reveals Large when plan says S/M → interactive asks user (split/promote/override); automated writes question.md in plans_and_protocols/ and stops.
5. Phase 4.1: added plan-driven skip note — plan was approved upstream, proceed directly to 4.2.
6. Automated Mode table: 3 new rows (redirect, stale plan hash mismatch, plan-driven size mismatch); 2 new bullets in "When auto-accept is NOT safe".

Items already correct (no changes needed):
- propose_after.py scoped to `requirement_then_implementation` heuristic in plan-driven mode (lines 175+)
- AC-13 WHAT-not-HOW enforcement preserved throughout

**Outcome**: Pass — all 8 acceptance criteria met. Verified via grep on key markers in SKILL.md.
**Next Step**: Run `task-complete` on TASK-PROC-058-05.
