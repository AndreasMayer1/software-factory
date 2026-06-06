---
task_id: TASK-PROC-029-06
type: impl
parent_requirement: REQ-PROC-029
urgency: 2
urgency_reason: U2-PLANNED
impact: 3
impact_reason: I3-QUALITY
status: completed
completed: 2026-02-15
effort: S
created: 2026-02-14
after: [TASK-PROC-029-03]
awaiting: []
covers:
  acceptance_criteria: [AC-02, AC-04]
  sections: []
scope_description: "Fix flow channel routing in apply-market-research skill, create conflict decision record template, fix naming and template inconsistencies"
requirements_version:
  commit: 25e51b1
  file: ../requirements.md
---

# Goal: Workflow & Organisation Fixes

## Origin

This task was proposed as "Task C" in the analysis report for TASK-PROC-029-03:
- **Plan**: `../2026-02-14_analyze_evaluate-research-quality/plans_and_protocols/2026-02-14_01_opus_plan.md` (FT-03, FT-04, FT-07)
- **Report**: `../2026-02-14_analyze_evaluate-research-quality/plans_and_protocols/2026-02-14_analysis_report.md` (Section 5, Task C; Issues I-05, I-06, I-09)

## Objective

Fix the broken `flow` output channel in the apply-market-research skill, add operational conflict handling support, and resolve naming/template inconsistencies.

## Scope

### In Scope

1. **Fix Flow Category Routing** (`.claude/skills/apply-market-research/skill.md`):
   - Mode A currently groups `flow` with `demand` and `quality`, directing all to `requirements_tasks/`
   - Fix: For findings with `Category: flow`, search `requirements_user_needs/user_flows/` instead of `requirements_tasks/`
   - This ensures MR-2026-02-14-006 (therapist-assigns-homework flow) has a clear application pathway

2. **Conflict Decision Record Template** (`requirements_market_research/_templates/decision_record_template.md`):
   - Create template with fields: conflicting finding IDs, what each claims, which flow took precedence, reasoning, reviewer, date
   - Add reference to this template in the "Handling Conflicts" section of README.md
   - Define what constitutes a "contradiction" between flows (conflict detection heuristic)

3. **Naming Convention Fixes**:
   - Rename `2023-11_initial-market-overview/` to `2023-11-01_initial-market-overview/` (use first-of-month for unknown exact date)
   - Update finding IDs from `MR-2023-11-001/002/003` to `MR-2023-11-01-001/002/003` in all files that reference them
   - Update any cross-references in other files (findings.md, README.md)

4. **Template Header Fix** (`_templates/findings_template.md`):
   - Add file-level header section (`Source batch`, `Raw data`, `Extracted`, `Extracted by`) matching the format used in actual findings files

### Out of Scope
- Source quality standards and confidence recalibration (that's Task A / TASK-PROC-029-04)
- Conducting new research or applying findings (that's Task B / TASK-PROC-029-05)

## Acceptance Criteria

- [ ] apply-market-research skill routes `flow` findings to `requirements_user_needs/user_flows/` instead of `requirements_tasks/`
- [ ] Conflict decision record template exists at `_templates/decision_record_template.md`
- [ ] README.md "Handling Conflicts" section references the template
- [ ] `2023-11_initial-market-overview/` renamed to `2023-11-01_initial-market-overview/`
- [ ] Finding IDs updated from `MR-2023-11-*` to `MR-2023-11-01-*` across all files
- [ ] findings_template.md includes file-level header section

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-029-03 | in progress | Analysis report must exist (provides rationale) |

## Notes

The folder rename requires careful handling: use `git mv` to preserve history, then update all cross-references. Search for `2023-11_initial` and `MR-2023-11-` across the entire `requirements_market_research/` folder.
