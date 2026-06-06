---
id: REQ-PROC-064
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: active
effort: M
stakeholder: developer
created: 2026-05-28
updated: 2026-05-28
after: [REQ-PROC-009, REQ-PROC-046]
blocks: []
market_research_refs: [] # No relevant findings identified
target_package: ""  # internal process tooling — unassigned
personas_served: [PERSONA-015]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "When a task includes a behavioral change to any artifact, the agent checks whether any requirement AC describes the behavior that was changed. A behavioral change is any modification that alters what the artifact does for some input: changed output, new/removed branch, altered side-effect, changed configuration behavior. Pure formatting, comment-only edits, import reordering, rename-only changes, and typo fixes are not behavioral changes."
    - id: AC-02
      text: "If the currency check (AC-01) identifies stale ACs — requirement ACs that now describe behavior that no longer exists or has changed — those ACs are updated via requ-explore or explicitly marked deprecated before the task is closed. An agent may not complete a task with known-stale ACs."
    - id: AC-03
      text: "The enforcement mechanism applies uniformly to all artifact types: Dart source under lib/ and test/, Python scripts under scripts/, skills under .claude/skills/, hook and permission configuration in .claude/settings.json and .claude/settings.local.json, guidelines under doc/, and devcontainer configuration. No artifact type is exempt from the currency check solely because of its type."
    - id: AC-04
      text: "When the currency check is skipped because a change is non-behavioral, the agent states which exemption applies (formatting, comment-only, import reorder, rename-only, typo fix). Silent skips are not permitted."
    - id: AC-05
      text: "The currency check is not triggered by changes to: requirements_tasks/ (requirement and task files), automation/ (task metadata and pending feedback), and generated files enumerated in CLAUDE.md §11 'Generated Files'. Changes to these paths are exempt by definition — they are not behavioral artifacts covered by requirement ACs."
---

# Requirement Currency

## Overview

When an AI agent changes the behavior of any artifact in the factory, requirements describing that behavior must stay current. Without this rule, requirements silently drift — they describe what the system used to do, not what it does now.

## Purpose

Requirements in this factory govern process and product behavior: Dart code, Python scripts, AI skills, hook configurations, doc/ guidelines, and devcontainer setup. Each of these is potentially covered by one or more requirement ACs. When a task modifies an artifact's behavior, those ACs can become stale — correct on the day they were written, false from the day the change landed.

The factory already enforces the top-down direction: product-intake (CLAUDE.md §1) prevents user-visible behavioral changes without a requirements chain, and REQ-PROC-009 defines what to do when a requirement changes after tasks exist. The bottom-up direction has no enforcement: an agent tasked with "change script X to do Z instead of Y" can complete that task while leaving the requirement that described Y untouched.

This requirement closes that gap by making the currency check a mandatory step before any task is closed — symmetrical with the top-down protection already in place.

## Behavior

A task that changes a behavioral artifact must, before closing:

1. Identify which requirement ACs (if any) describe the behavior that was changed.
2. If stale ACs are found: update them via requ-explore or mark them deprecated.
3. If no stale ACs are found: the task may close without a currency update.
4. If the change is non-behavioral: the task may skip the check, provided the applicable exemption is stated.

The exempted paths (requirements_tasks/, automation/, generated files) bypass the check unconditionally.

## Developer Guidelines

### Key Decisions

- **Scope boundary**: The check covers all file writes EXCEPT requirements_tasks/, automation/, and CLAUDE.md §11 generated files. These three categories are excluded because: (a) requirements_tasks/ changes are the output of the currency process, not inputs to it; (b) automation/ is task-orchestration metadata, not behavioral artifacts; (c) generated files have their behavioral specification in the source they are generated from, not in their own ACs.
- **Non-behavioral exemptions mirror claude-write-script**: The exemption categories align with those already defined in the claude-write-script skill (formatting, comment-only, import reorder, rename-only, typo fix). This alignment is intentional — the agent already applies this classification for the test-writing trigger; the currency check reuses the same gate.
- **HOW is deferred**: This requirement defines WHAT must be true. The detection mechanism — how the agent identifies which requirement ACs describe a changed artifact, where in the workflow the check runs, what tooling assists it — is defined by the enforcement exploration task (see Related Requirements).

### Common Pitfalls

- **Silent skip**: Completing a task without running or explicitly exempting the currency check. AC-04 requires a stated exemption — "non-behavioral" without naming which category does not satisfy it.
- **Scope creep into requirements_tasks/**: Treating a requ-explore run (itself the resolution of a currency check) as a trigger for another check. Changes to requirement files are the resolution, not a new trigger.
- **Over-broad stale detection**: Flagging ACs as stale because they mention a file that was touched, rather than because the AC's described behavior actually changed. The check targets behavioral change, not file-path proximity.

## Related Requirements

- [REQ-PROC-009](../requirements_and_tasks/requirements.md) — defines the top-down direction (what to do when a requirement changes after tasks exist); this requirement is the reverse direction
- [REQ-PROC-003](../requirements_writer_mode_flexibility/requirements.md) — governs how requirements are authored via requ-explore, which is the remediation path when stale ACs are found (AC-02)
- [REQ-PROC-045](../requirements_structure_quality/requirements.md) — structural quality of the requirements folder; orthogonal dimension to currency
- [REQ-PROC-046](../../coding_standards/code_quality/requirements.md) — code quality gates; primary candidate enforcement host for the check mechanism
- [REQ-PROC-050](../artifact_soundness/requirements.md) — soundness of user-needs artifacts from an evidence perspective; orthogonal dimension (evidence quality vs. behavioral currency)
- [REQ-PROC-058](../implementation_task_planning/requirements.md) — mentions stale-plan detection at plan level; a related concept applied to task plans rather than requirements

## References

- CLAUDE.md §1 "Source of Truth for Product Changes" — product-intake rule (the top-down complement to this requirement)
- CLAUDE.md §11 "Generated Files" — enumeration of exempt generated files
- `.claude/skills/claude-write-script/SKILL.md` — behavioral-change definition and exemption list (aligned with AC-01 and AC-04)
- `.claude/skills/verify-quality/SKILL.md` — candidate enforcement host
- `.claude/skills/task-complete/SKILL.md` — candidate enforcement host
