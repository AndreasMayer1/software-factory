# Protocol — Apply Cross-Reference Classifications for REQ-PROC-001

Date: 2026-05-26
Target: `requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md`
Source classifications: `plans_and_protocols/2026-05-26_cross_ref_classifications.md`

## Verification (Step A)

- YAML frontmatter parsed cleanly via `python3 yaml.safe_load`.
- `after: []` unchanged; `blocks: []` unchanged; `id: REQ-PROC-001` unchanged.
- `## Related Requirements` section present with both REQ-PROC-008 and REQ-PROC-058 bullets.
- `scripts/requirements/check_structural_quality.py` not present in repo (REQ-PROC-045 deliverable, not yet landed) — manual checks are the authoritative verification per task instructions.

## Diff (Step B)

```diff
diff --git a/requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md b/requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md
index 1efbf70c..2f7ac7a0 100644
--- a/requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md
+++ b/requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md
@@ -142,6 +142,11 @@ CLAUDE.md §7 and recapitulated below.
   *recovery* path (user-triggered condensation). The ACs above
   govern the *prevention* path (task sizing at creation and runtime).
 
+## Related Requirements
+
+- [REQ-PROC-008](../../workflows/orchestrator_workflow/requirements.md) — Orchestrator workflow manages context budget via subtasks; this requirement's Design Decision references orchestrator mode as the manual context-management mechanism.
+- [REQ-PROC-058](../../requirements_management/implementation_task_planning/requirements.md) — task-derive-from-requ consumes the S1–S4 sizing signals defined here when planning tasks; REQ-PROC-058 already cross-references REQ-PROC-001 one-way and this is the reciprocal link.
+
 ---
 ## Version History
 Consolidated from:
```

## Completion Note (Step D)

Fields updated: a new `## Related Requirements` section was inserted in `requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md` immediately before `## Version History`, containing two bullets — REQ-PROC-008 (Orchestrator Workflow) and REQ-PROC-058 (Implementation Task Planning / task-derive-from-requ). YAML frontmatter (`after: []`, `blocks: []`, `id: REQ-PROC-001`) was left untouched per the classifications file (semantic links go to the body section, not `after:`). Commit SHA: `8c0eaa33a676e40842af139cc54b171fc8fbd1de`. Seven ignore reasons recorded from `2026-05-26_cross_ref_classifications.md`: (1) REQ-PROC-046 Code Quality — already documents REQ-PROC-001 as "unrelated; concerns conversational context, not code quality"; (2) REQ-PROC-005 Testing Workflow — incidental prose mention of "context window"; (3) REQ-PROC-026 UN→Design Bridge — keyword "escalation" used re visual hierarchy emphasis, unrelated; (4) REQ-PROC-032 metadata `design_decisions` — incidental mention; (5) REQ-PROC-051 Python Code Quality — gate-boilerplate use of "escalation", different sense; (6) REQ-PROC-052 Privacy/Security Gates — same gate boilerplate; (7) REQ-PROC-056 Dependency Governance — same gate boilerplate.
