---
task_id: TASK-PROC-029-04
type: impl
parent_requirement: REQ-PROC-029
urgency: 2
urgency_reason: U2-PLANNED
impact: 3
impact_reason: I3-QUALITY
status: completed
completed: 2026-02-14
effort: S
created: 2026-02-14
after: [TASK-PROC-029-03]
awaiting: []
covers:
  acceptance_criteria: [AC-05]
  sections: []
scope_description: "Establish source quality standards, recalibrate confidence levels, and add staleness tracking for market research data"
requirements_version:
  commit: 25e51b1
  file: ../requirements.md
---

# Goal: Data Quality Governance

## Origin

This task was proposed as "Task A" in the analysis report for TASK-PROC-029-03:
- **Plan**: `../2026-02-14_analyze_evaluate-research-quality/plans_and_protocols/2026-02-14_01_opus_plan.md` (FT-01, FT-05, FT-08)
- **Report**: `../2026-02-14_analyze_evaluate-research-quality/plans_and_protocols/2026-02-14_analysis_report.md` (Section 5, Task A; Issues I-01, I-03, I-07)

## Objective

Establish quality governance for market research data so that source quality, confidence calibration, and data freshness are systematically tracked and enforced.

## Scope

### In Scope

1. **Source Quality Standards** (README.md addition):
   - Define accepted source types: `primary_observation`, `primary_document`, `llm_synthesis`, `academic`, `industry_report`
   - Set minimum quality bar: at least one primary or academic source per batch
   - Add confidence calibration rule: LLM synthesis caps at "medium" unless independently verified
   - Note: LLM sources with web search grounding (e.g., Gemini with `enableSearchAsATool`) are still `llm_synthesis` because individual claims cannot be traced to specific grounding URLs

2. **Template Updates** (`_templates/findings_template.md`):
   - Add `source_type` field per finding
   - Add `review_by` field per finding
   - Add file-level header matching actual file format (`Source batch`, `Raw data`, `Extracted`, `Extracted by`)

3. **Retroactive Confidence Recalibration** (`2026-02-14_german-mental-health-apps/findings.md`):
   - Add `source_type: llm_synthesis` to all findings
   - Downgrade MR-2026-02-14-002 from "high" to "medium" with note: "Downgraded: source is LLM synthesis with opaque web grounding. Upgrade to high requires verification against Minddistrict primary documentation."
   - Downgrade MR-2026-02-14-006 from "high" to "medium" with same rationale
   - MR-2026-02-14-003: Add note "Retain medium. Upgrade to high after verification against BfArM DiGA directory (primary source)."

4. **Staleness Tracking** (README.md + template):
   - Add `review_by` guidance: 12 months for `llm_synthesis`, 18 months for primary sources
   - Add reevaluation trigger to README: "When adding a new batch, scan existing batches for findings past their `review_by` date"

### Out of Scope
- Conducting new research (that's Task B / TASK-PROC-029-05)
- Fixing workflow routing or naming inconsistencies (that's Task C / TASK-PROC-029-06)
- Applying unapplied findings to requirements

## Acceptance Criteria

- [ ] README.md contains "Source Quality Standards" section with source types, quality bar, and confidence calibration rule
- [ ] findings_template.md includes `source_type`, `review_by`, and file-level header fields
- [ ] MR-2026-02-14-002 and MR-2026-02-14-006 downgraded to "medium" with documented rationale
- [ ] All findings in 2026-02-14 batch have `source_type: llm_synthesis`
- [ ] README.md contains reevaluation trigger and `review_by` guidance

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-029-03 | in progress | Analysis report must exist (provides rationale for changes) |

## Notes

The analysis report found that the Gemini raw data file DOES contain Google Search grounding URIs (`vertexaisearch.cloud.google.com/grounding-api-redirect/`), so the source is not purely training-data synthesis. However, the grounding URLs are opaque redirects - individual claims cannot be traced to specific sources. This still warrants `llm_synthesis` classification with a "medium" confidence cap, but the governance section should acknowledge that web-grounded LLM output is stronger than pure synthesis.
