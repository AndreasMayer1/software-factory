---
requirement: REQ-PROC-059
requirements_version: 1d78ce3f
created: 2026-05-30
mode: full
---

# Task Creation Plan for REQ-PROC-059

## Analysis

All three ACs of REQ-PROC-059 describe properties of the same artifact: the
principles requirements.md document. The document was authored by TASK-PROC-006-03.
These tasks cover the ACs by verifying and finalizing that document.

Since < 3 impl tasks, no separate verification task. Verification section appended
to the single impl task.

## Tasks

- task_name: "Verify LLM work principles document satisfies REQ-PROC-059 acceptance criteria"
  req_path: "requirements_tasks/process/AI_rules/llm_work_principles/requirements.md"
  requirements_version: "1d78ce3f"
  covers_acs: [AC-01, AC-02, AC-03]
  effort: XS
  layer: process/documentation
  after: []
  task_type: impl
  opus_recommended: false
  target_package: ""
  implementation_notes: |
    Read requirements_tasks/process/AI_rules/llm_work_principles/requirements.md
    and verify each AC:

    AC-01: All 8 principles (a–h) are present, each with a source reference
    and a one-line rationale. Slot (d) is reserved — verify it has a rationale
    for being reserved rather than a live principle.

    AC-02: Principle (c) specifies the irreversibility threshold decision rule
    with a clear promote-when / stay-in-prompt-when split.

    AC-03: No section of the document contains skill-specific audits,
    remediation tasks, or tooling prescriptions. If found, move them out.

    If any AC is not satisfied, update requirements.md accordingly (use
    requ-explore semantics for edits — preserve frontmatter structure).

    Verification section (no separate task needed — < 3 impl tasks):
    After any edits, run:
      python3 scripts/requirements/coverage_report.py | grep -A 10 REQ-PROC-059
    Confirm all 3 ACs show as covered by this task. Also run:
      python3 scripts/requirements/check_ac_coverage.py \
        requirements_tasks/process/AI_rules/llm_work_principles/requirements.md
    to confirm zero uncovered ACs.

    Concept docs (mandatory reading):
    - requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/
      tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/
      plans_and_protocols/2026-05-16_08_opus_synthesis_round4.md (Part 5)

## Coverage Matrix

| AC    | Task(s)                              | Package |
|-------|--------------------------------------|---------|
| AC-01 | verify-llm-work-principles-doc       | —       |
| AC-02 | verify-llm-work-principles-doc       | —       |
| AC-03 | verify-llm-work-principles-doc       | —       |

## Post-Creation Obligations (TASK-PROC-006-05 goal.md)

After the impl task is created:
1. Add its task ID to `.claude/task_ordering_priority_override.txt`
   under a `# --- LLM-work-principles impl ---` section.
2. Append its task ID to TASK-PROC-006-06's `after:` list in goal.md.
