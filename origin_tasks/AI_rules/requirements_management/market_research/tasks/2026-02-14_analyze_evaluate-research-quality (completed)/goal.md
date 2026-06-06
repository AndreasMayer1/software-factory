---
task_id: TASK-PROC-029-03
type: analyze
parent_requirement: REQ-PROC-029
urgency: 2
urgency_reason: U2-PLANNED
impact: 3
impact_reason: I3-QUALITY
status: completed
completed: 2026-02-14
effort: S
created: 2026-02-14
after: [TASK-PROC-029-02]
awaiting: [TASK-PROC-029-02]
covers:
  acceptance_criteria: [AC-04, AC-05]
  sections: []
scope_description: "Evaluate the quality of the market research workflow and data produced by TASK-PROC-029-02; identify gaps and improvements"
requirements_version:
  commit: 25e51b1
  file: ../requirements.md
---

# Analysis Task: Evaluate Market Research Quality & Workflow

## Requirement Reference
- **Requirement**: `requirements_tasks/process/AI_rules/requirements_management/market_research/requirements.md` (REQ-PROC-029)
- **Status**: Not Started
- **Depends on**: TASK-PROC-029-02 must be completed first (the workflow and data must exist before evaluation)

## Goal

After TASK-PROC-029-02 has been implemented, perform a critical evaluation of:
1. The **quality and completeness of the market research data** in `requirements_market_research/`
2. The **soundness of the workflow** that pushes research findings into requirements and scope exclusions
3. The **data organisation and folder structure** inside `requirements_market_research/`

The output is a written report with concrete improvement recommendations — not code changes.

## Scope Overview

**Affected Layers**: Process layer (read-only review + written report)
**Estimated Files**: ~5–10 files to review; 1 output file (analysis report)
**Patterns to Follow**: Similar to how quality reviews are done for user needs content (REQ-PROC-027 review tasks)

## What to Evaluate

### 1. Market Research Data Quality

Review the contents of `requirements_market_research/` (all research rounds present after TASK-PROC-029-02):

- **Coverage**: What market segments, user groups, and questions are covered? What is conspicuously missing?
  - Example gaps to look for: pricing models, retention/churn data, user demographics, accessibility needs, international vs. German-only market
- **Recency**: How current is the data? What has likely changed since each research round?
- **Confidence levels**: Are confidence levels in `findings.md` assigned appropriately, or are they uniformly high/low?
- **Categorization quality**: Are findings correctly categorized (demand / quality / flow / exclusion)? Are any misclassified?
- **Source diversity**: Is the research based on a single source type (e.g., only Gemini web searches)? What additional source types would strengthen the findings?

### 2. Workflow Soundness

Review the `apply-market-research` skill and `README.md` created by TASK-PROC-029-02:

- **Completeness**: Does the workflow cover all four output channels (functional, non-functional, user flows, scope exclusions)?
- **Friction**: Are there steps that are unnecessarily complex or likely to be skipped in practice?
- **Conflict handling**: Is the guidance for resolving conflicts between the 3 flows (user needs / design bridge / market research) clear and actionable?
- **Reevaluation mechanism**: Is it clear HOW and WHEN to reevaluate past decisions when new research arrives?
- **Skill integration**: Do the updates to `explore-requirements`, `create-impl-task`, and `modify-user-needs` feel natural, or do they add too much friction to those workflows?

### 3. Data Organisation

Review the folder structure and file naming inside `requirements_market_research/`:

- **Discoverability**: Can an AI agent (or new developer) quickly understand what research exists and what it covers?
- **Naming conventions**: Are folder names (`YYYY-MM-DD_[topic]/`) consistent and informative?
- **Template usability**: Is the `findings_template.md` clear enough that a new research round can be processed without referring back to documentation?
- **Index/overview**: Should there be an index file listing all research rounds with date, topic, and status? Or does the README serve this purpose adequately?

## Output

Produce a report at:
`requirements_tasks/process/AI_rules/requirements_management/market_research/tasks/2026-02-14_analyze_evaluate-research-quality/plans_and_protocols/YYYY-MM-DD_analysis_report.md`

The report must contain:
- **Research gaps**: Specific missing topics with rationale for why they matter
- **Workflow improvements**: Concrete changes to the skill or README (reference specific sections)
- **Organisation improvements**: Specific folder/naming/index recommendations
- **Prioritized action list**: Which improvements are high-value vs. nice-to-have

Concrete follow-up tasks should be proposed for any high-value gap or improvement identified.

## Acceptance Criteria

- [ ] All three evaluation areas covered (data quality, workflow soundness, organisation)
- [ ] Specific gaps identified with rationale (not just "more research needed")
- [ ] Workflow assessment includes at least one concrete improvement or validation
- [ ] Report is written and committed to `plans_and_protocols/`
- [ ] High-value findings result in proposed follow-up tasks

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-029-02 | pending | Must be completed — workflow and data must exist first |

---

**Note**: This task describes WHAT to analyze, not HOW.
The analysis approach will be determined when this task is executed.
