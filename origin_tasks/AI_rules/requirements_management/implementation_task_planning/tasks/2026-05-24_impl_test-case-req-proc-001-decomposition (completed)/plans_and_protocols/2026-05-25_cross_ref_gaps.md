# Cross-Reference Gaps — REQ-PROC-001 (Context Window)

Generated: 2026-05-25 by `task-derive-from-requ` Phase 1.5.1 (TASK-PROC-058-07).
Detector: `scripts/requirements/check_cross_refs.py` with explicit terms
`"context window" "fan-out" "tool-call" "escalation"` (auto-terms produced 128
generic false positives — see Finding F).

REQ-PROC-001 today has **no** cross-references (`after: []`, `blocks: []`, no
`## Related Requirements`).

This file is the developer's reference when filling
`automation/pending_feedback/TASK-PROC-058-07/answer.md`. Classify each candidate
as `hard`, `semantic`, or `ignore — <reason>`.

| # | REQ-ID | Title | Matched | File | Excerpt | Recommended |
|---|--------|-------|---------|------|---------|-------------|
| 1 | REQ-PROC-008 | Orchestrator Workflow | context window | `requirements_tasks/process/AI_rules/workflows/orchestrator_workflow/requirements.md` | "Respect the limited context window by using appropriate strategies" | **semantic** |
| 2 | REQ-PROC-058 | Implementation Task Planning | escalation | `requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/requirements.md` | "Automated mode: write question.md…" (consumes S1–S4 sizing signals; already refs PROC-001 one-way) | **semantic** |
| 3 | REQ-PROC-046 | Code Quality | escalation | `requirements_tasks/process/AI_rules/coding_standards/code_quality/requirements.md` | "Iteration bound: max five revision cycles" | **ignore** (PROC-046 already states "unrelated; concerns conversational context, not code quality") |
| 4 | REQ-PROC-005 | Testing Workflow | context window | `requirements_tasks/process/AI_rules/workflows/.../requirements.md` | "find a better way to implement tests…" | **ignore** (incidental) |
| 5 | REQ-PROC-026 | UN→Design System Bridge | escalation | `requirements_tasks/process/.../requirements.md` | "AI makes buttons equal…" (visual hierarchy) | **ignore** (incidental) |
| 6 | REQ-PROC-032 | (metadata design_decisions) | context window | `requirements_tasks/process/.../requirements.md` | "design_decisions: field in metadata.yaml" | **ignore** (incidental) |
| 7 | REQ-PROC-051 | Python Code Quality | escalation | `requirements_tasks/process/.../requirements.md` | "Code that fails any active gate … never declared complete" | **ignore** (gate boilerplate) |
| 8 | REQ-PROC-052 | Privacy/Security Gates | escalation | `requirements_tasks/process/.../requirements.md` | "Code that fails any active gate … never declared complete" | **ignore** (gate boilerplate) |
| 9 | REQ-PROC-056 | Dependency Governance | escalation | `requirements_tasks/process/.../requirements.md` | "A dependency change that violates this requirement …" | **ignore** (gate boilerplate) |

## Summary of recommendations
- **semantic** (add to `## Related Requirements`): REQ-PROC-008, REQ-PROC-058
- **ignore**: REQ-PROC-046, REQ-PROC-005, REQ-PROC-026, REQ-PROC-032, REQ-PROC-051, REQ-PROC-052, REQ-PROC-056
- **hard** (add to `after:`): none identified

If you accept the recommendations verbatim, copy the "Summary" lines into
`answer.md`. If you disagree on any, override per-REQ-ID.
