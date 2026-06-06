---
task_id: TASK-PROC-029-05
type: explore
parent_requirement: REQ-PROC-029
urgency: 2
urgency_reason: U2-PLANNED
impact: 4
impact_reason: I4-PRODUCT_DIRECTION
status: pending
effort: M
created: 2026-02-14
after: [TASK-PROC-029-04]
awaiting: []
covers:
  acceptance_criteria: [AC-04, AC-05]
  sections: []
scope_description: "Conduct primary-source research round targeting coverage gaps, apply unapplied findings, add Research Batch Index to README"
requirements_version:
  commit: 25e51b1
  file: ../requirements.md
---

# Goal: Primary-Source Research Round & Application Completeness

## Origin

This task was proposed as "Task B" in the analysis report for TASK-PROC-029-03:
- **Plan**: `../2026-02-14_analyze_evaluate-research-quality/plans_and_protocols/2026-02-14_01_opus_plan.md` (FT-02, FT-06)
- **Report**: `../2026-02-14_analyze_evaluate-research-quality/plans_and_protocols/2026-02-14_analysis_report.md` (Section 5, Task B; Issues I-02, I-08)

## Objective

Fill the HIGH-severity coverage gaps identified in the analysis report by conducting a new research round using verifiable primary sources, and address the 73% unapplied findings backlog.

## Scope

### In Scope

1. **New Research Batch** (create `requirements_market_research/YYYY-MM-DD_primary-source-validation/`):
   - Target HIGH-severity gaps from the analysis report (Section 1.2):
     - **Pricing / business models**: Check HelloBetter, Selfapy, Minddistrict pricing pages directly
     - **User demographics / therapy experience**: Consult published DiGA evaluation studies (BfArM annual reports)
     - **Retention / engagement data**: Search for published app efficacy studies (PubMed, Google Scholar)
     - **Therapist workflow needs**: Consult therapist-facing documentation from Minddistrict, MindDoc
   - Use at least 2 different source types per batch, with at least 1 primary source
   - Follow source quality standards from TASK-PROC-029-04

2. **Apply Unapplied Findings** (using `apply-market-research` skill):
   - Apply all 8 currently unapplied findings:
     - MR-2026-02-14-001, 002, 004, 006, 008
     - MR-2023-11-001, 002, 003
   - Track application status in findings.md files

3. **Research Batch Index** (README.md addition):
   - Add a Research Batch Index table to `requirements_market_research/README.md`
   - Columns: Batch, Date, Topic, Findings count, Applied count, Source Type
   - Serves as both discoverability aid and application completeness dashboard

### Out of Scope
- Defining source quality standards (that's Task A / TASK-PROC-029-04, must be done first)
- Fixing workflow routing or naming (that's Task C / TASK-PROC-029-06)
- MEDIUM-severity gaps (accessibility, App Store ratings, market size, regulatory trajectory) - can be addressed in future research rounds

## Acceptance Criteria

- [ ] New research batch created with findings from at least 2 different primary source types
- [ ] At least 3 of the 4 HIGH-severity coverage gaps addressed with new findings
- [x] All 8 previously unapplied findings applied via `apply-market-research` skill (or documented reason why not applicable)
- [x] Research Batch Index table added to README.md with all batches listed
- [x] New findings follow source quality standards from TASK-PROC-029-04

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-029-04 | pending | Source quality standards must exist before new research follows them |

## Notes

This task is effort M because it requires external research (web searches, reading primary documentation) rather than just internal configuration changes. The research itself cannot be fully automated - it requires evaluating source quality and relevance.
