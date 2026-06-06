---
task_id: TASK-PROC-053-08
type: explore
parent_requirement: REQ-PROC-053
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-05-26
after: [TASK-PROC-053-07]
awaiting: ["release 0.0.1 shipped"]
awaiting_note: "Cannot investigate real-world threshold performance until v0.0.1 has been released and used in production for a few weeks."
covers:
  acceptance_criteria: []
  sections: [SEC-04]
scope_description: "Post-release investigation of lookup threshold calibration quality"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: db92ca63
  file: ../requirements.md
---
# Goal — D4: Post-release threshold calibration investigation

## Objective

After release 0.0.1 has shipped and been used for several weeks, investigate how
well the per-technology trigger thresholds (from Tier 3) and the lookup system in
general are working in practice. Produce a report with calibration recommendations.

## Background

The synthesis §6 tables are best-effort defaults. D4 from user feedback:
*"create a task that is blocked and waits for release 0.0.1 to ship. the goal of
the task is to investigate how well the thresholds and the lookup in general works
and create a report with recommendations."*

This task is explicitly blocked until release 0.0.1 ships. After it ships, wait
for enough tasks to accumulate (≥ 2–4 weeks of normal development activity).

## Seeds

1. Are the lookup counts per task class within the §8.2 budget bands, or consistently over/under?
2. Which technologies trigger the most fallback-to-WebSearch records? Are they indexed now?
3. Are the "high-churn" Flutter surfaces (§6.2) generating excessive lookups, or are in-task caches effective?
4. Is the 5-second toolchain-clean probe cap (§4.5) causing budget friction?
5. Are the cycle-count correlations (§7.3) showing the predicted improvement?

## Output

A recommendations report at `plans_and_protocols/[date]_NN_calibration_report.md` with:
- Threshold adjustments per technology (if any)
- Budget band adjustments (if needed)
- Coverage gaps for context7 (technologies hitting fallback)
- Any systematic issues discovered

## Acceptance Criteria

- [ ] Exploration waited for release 0.0.1 (awaiting field unblocked by developer)
- [ ] At least 10 closed tasks with lookup_log.jsonl analyzed
- [ ] Calibration report produced with concrete recommendations

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-053-07 | pending | Analytics script needed for data collection |
| release 0.0.1 | external | Must be shipped before this task starts |
