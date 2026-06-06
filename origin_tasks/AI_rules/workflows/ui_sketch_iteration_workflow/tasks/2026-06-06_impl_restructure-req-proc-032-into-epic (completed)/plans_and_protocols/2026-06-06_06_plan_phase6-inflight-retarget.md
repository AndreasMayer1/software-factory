# Phase 6 — In-flight task retargeting + F06 derivation (plan)

Executed in main AFTER the reference-rewrite agent lands. Files here are disjoint
from that agent (it excludes the 4 in-flight tasks).

## In-flight task → feature mapping + action

| Task | Account | Feature | New parent_requirement | Action |
|------|---------|---------|------------------------|--------|
| TASK-PROC-032-30 | gmail | F05 `feat_consistency_sci_layer` | REQ-PROC-032-05 | 1:1 — derive F05 directly. (Note: -30 still has an UNANSWERED human defer/proceed question; the restructure resolves the original blocker since A-stage ACs now exist — flag to developer, do not fabricate the answer.) |
| TASK-PROC-032-31 | web | F06 `feat_carrier_and_auto_review` | REQ-PROC-032-06 | Authoring done. Derivation delegated to new derive-F06 task. |
| TASK-PROC-032-32 | gmail | F06 `feat_carrier_and_auto_review` | REQ-PROC-032-06 | Authoring done. Derivation delegated to new derive-F06 task. |
| TASK-PROC-032-33 | web | F07 `feat_embedded_flow_viewer` | REQ-PROC-032-07 | 1:1 — derive F07 directly. |

AC renumber (for answer.md notes): AC-42..55→F05 AC-01..14; AC-56→F06 AC-02, AC-57..62→F06 AC-03..08, AC-31→F06 AC-01, AC-63..66→F06 AC-09..12; AC-67..70→F07 AC-01..04.

## Per-task edits
1. goal.md frontmatter: `parent_requirement` → the feature REQ-ID above. Update `covers.acceptance_criteria` to new ids if currently populated (authoring/explore tasks may have empty covers — leave empty if so). Do NOT alter requirements_version.
2. pending_feedback/<TASK>/answer.md: append a developer-authorized "STRUCTURE CHANGED" note (the developer explicitly authorized writing these). Content: REQ-PROC-032 is now epic+features (zero spec change, verified); your ACs now live in <feature REQ-ID> (<folder>) renumbered as <list>; CONTINUE against the FEATURE not the epic. For -31/-32: authoring complete → derivation handled by the new derive-F06 task; do NOT run task-derive-from-requ on F06 yourself. For -30/-33: run task-derive-from-requ on your feature.
   - **Standing directive (all four):** any task produced by task-derive-from-requ MUST be appended to `.claude/task_ordering_priority_override.txt` (no target_package → invisible to next_tasks.py otherwise).
   - -30 special: keep the awaiting-human state intact; add the structure note above it; the human still answers defer/proceed (now likely "proceed" since A-stage authored).

## New task: derive-F06
- Create via task-create under the epic (or under F06): type impl/derive, parent_requirement REQ-PROC-032-06, `after: [TASK-PROC-032-31, TASK-PROC-032-32]`, scope = run task-derive-from-requ on F06 (carrier + auto-review) ONCE, covering the genuinely-uncovered new ACs (AC-56..66 → F06 AC-01..12 minus any already covered).
- **Append the new task ID to `.claude/task_ordering_priority_override.txt`** (developer directive).

## Override-file directive (DEVELOPER, 2026-06-06)
- The new derive-F06 task ID → append to `.claude/task_ordering_priority_override.txt`.
- All tasks created by the in-flight tasks (via task-derive-from-requ) → append to the same file. Carried into each answer.md note.

## Then: regeneration + validation (Phase 5b)
- Regenerate: merge_requirements.py, generate_id_registry.py --requirements, generate_status_overview.py, generate_user_needs_status if needed.
- Validate: coverage_report.py + check_cross_refs.py on the features; confirm no dangling REQ-PROC-032 AC refs remain (epic has 0 ACs).
- Governed follow-up (NOT auto-edit): 2 skill files (ui-create-scribble-improve SKILL.md+contract.yaml "create task under REQ-PROC-032") via claude-modify-skill — point impl-task creation at the appropriate feature.
