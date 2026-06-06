---
date: 2026-05-25
task_id: TASK-PROC-058-03
phase: implementation
---

# Protocol — Phase 1.5 implementation

## Summary

Replaced the placeholder Phase 1.5 stub in
`.claude/skills/task-derive-from-requ/SKILL.md` (lines 40–48 in the previous
version) with the full cross-reference completeness gate per REQ-PROC-058 AC-17.

Also updated the Automated Mode table to drop the "deferred to TASK-PROC-058-03"
tag on the Phase 1.5 row.

## Design decisions

1. **Detection mechanism — script-or-fallback.** AC-11 of REQ-PROC-045 owns the
   keyword-grep mechanism. That requirement's impl tasks have not yet been
   created (the goal.md flagged this explicitly). The skill text prefers a
   script at `scripts/requirements/detect_cross_ref_gaps.py` when present, and
   falls back to the same inline grep pattern requ-explore Phase 1.4 already
   uses. When the REQ-PROC-045 script lands, only the "preferred path"
   paragraph stays — the fallback paragraph can be deleted.

2. **Apply step is always agent-delegated.** The goal.md and REQ-PROC-058
   Behavior section both insist the write is delegated. Reason: requ-explore is
   heavy, multi-file, and would blow the main session's context. The agent is
   spawned with `run_in_background: true` per CLAUDE.md §2 (>5 min wall-clock),
   and the main session keeps a 4:30 heartbeat alive to protect the prompt
   cache.

3. **Checklist-shaped agent prompt — mitigates "stops early".** The goal.md
   warned that requ-explore in agent context has stopped early on a prior spike
   (REQ-PROC-035 background agent). Mitigations baked in:
   - The classifications are written to a stable file before spawning, so the
     agent has an authoritative input it can re-read.
   - The prompt lists steps as A–D with an explicit "YOU MUST COMPLETE STEPS
     A–D. Do not stop after step C."
   - The Resume step (1.5.4) independently audits the file diff — if the agent
     stopped early, the residual set is non-empty and the gate refuses to
     pass. The early-stop failure mode therefore cannot leak into Phase 2.

4. **Block-and-resume is explicit and symmetric.** Phase 2 cannot begin until
   the gate passes. In interactive mode, a residual set after Apply is a hard
   error the user resolves. In automated mode, it escalates via the standard
   `question.md` pattern — exactly the same procedure used by 1.5.2 for the
   initial classification round — so the orchestrator path is identical.

5. **Waiver semantics are simple.** If every candidate is classified `ignore`,
   the Apply step is skipped (nothing to write). Phase 2 proceeds. The protocol
   records each ignore reason for audit.

## Acceptance criteria coverage (goal.md)

| AC checklist item | Covered by |
|---|---|
| Phase 1.5 implemented in SKILL.md | Lines 40–232 of SKILL.md |
| Detect step calls REQ-PROC-045 mechanism or inline fallback | §1.5.1 |
| Interactive classification: hard / semantic / ignore | §1.5.2 interactive paragraph |
| Automated mode writes cross_ref_gaps.md + question.md | §1.5.2 automated paragraph, steps 1–5 |
| Apply step spawns requ-explore agent with structured input | §1.5.3 agent prompt template |
| Block semantics: Phase 2 blocked | §1.5.4 step 4 + Block-and-resume contract |
| Resume step re-runs Phase 1 and verifies | §1.5.4 |
| Documented with rationale | §1.5 preamble + this protocol |

## Files modified

- `.claude/skills/task-derive-from-requ/SKILL.md`
  - Replaced Phase 1.5 stub with full implementation (§1.5.1–1.5.5 + Block-and-resume contract)
  - Updated Automated Mode table row for Phase 1.5
