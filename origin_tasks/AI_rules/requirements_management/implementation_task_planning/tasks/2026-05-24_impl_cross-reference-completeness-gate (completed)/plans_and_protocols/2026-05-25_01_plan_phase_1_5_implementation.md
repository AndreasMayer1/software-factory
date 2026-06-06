---
date: 2026-05-25
task_id: TASK-PROC-058-03
mode: inline
---

# Plan — Implement Phase 1.5 in task-derive-from-requ

## Objective

Replace the placeholder Phase 1.5 block in `.claude/skills/task-derive-from-requ/SKILL.md`
(currently a stub deferring to "TASK-PROC-058-03") with the actual cross-reference
completeness gate implementation per REQ-PROC-058 AC-17.

## Approach

**Inline mode.** Single skill file to edit. No agents needed — this is documentation
authoring, not codebase exploration. The required context (requ-explore Phase 1.4,
REQ-PROC-045 AC-11, REQ-PROC-058 AC-17 + Behavior section) is already gathered.

## Phases

1. **Author Phase 1.5 body** in SKILL.md, structured as four steps:
   1.5.1 Detect — keyword-grep mechanism (REQ-PROC-045) with inline fallback
   1.5.2 Classify — interactive vs automated (writes cross_ref_gaps.md + question.md, copies TEMPLATE_answer.md, terminates)
   1.5.3 Apply — spawn ONE general-purpose agent that invokes requ-explore against the target requirement; very explicit prompt to prevent early stop
   1.5.4 Resume — re-run 1.5.1; on remaining non-ignored gaps, block
   Plus: waiver semantics and block-and-resume rules.

2. **Update Automated Mode table** in SKILL.md — remove "deferred to TASK-PROC-058-03"
   tag on the Phase 1.5 row.

3. **Write WHY-style protocol entry** to plans_and_protocols/.

4. **Wrap up** — claude-log, doc-update-guidelines, task-complete.

## Files to modify

- `.claude/skills/task-derive-from-requ/SKILL.md` — replace Phase 1.5 stub (lines 40-48)
  and update Automated Mode row (line 209).

## Out of scope

- The REQ-PROC-045 keyword-grep script itself — owned by a separate impl task there;
  Phase 1.5 calls the script if it exists, otherwise uses inline fallback.
- Modifying requ-explore — already exists; we just invoke it from the spawned agent.
- Real end-to-end test on a live requirement — the verification task for REQ-PROC-058
  will exercise the flow holistically.

## Risk notes

The goal.md flags a known risk: requ-explore in agent context may stop early
(observed on the REQ-PROC-035 background agent). Mitigation: the spawned agent's
prompt is structured as a numbered checklist with an explicit "you MUST complete
all steps, do not stop early" instruction; the Resume step then audits the actual
file diff and treats incomplete application as a blocking error.
