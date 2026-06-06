---
id: REQ-PROC-030
status: implemented
updated: 2026-02-22
urgency: 3
urgency_reason: "U3-WORKFLOW-GAP: Existing workflow has a documented gap that causes manual, error-prone work after every user flow approval"
impact: 4
impact_reason: "I4-PAIN: Without this, engineer must manually analyze every flow to derive requirements — tedious, inconsistent, gaps get missed"
effort: M
stakeholder: developer
created: 2026-02-21
after: []
blocks:
  - REQ-PROC-040
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "derive-requirements-from-flow skill exists in .claude/skills/derive-requirements-from-flow/skill.md"
    - id: AC-02
      text: "Skill reads all relevant flow sections: Implementing Epics/Features, Gaps, Open Questions, Screens/Components, Scope Boundaries"
    - id: AC-03
      text: "Skill scans existing requirements and correctly categorizes each gap"
    - id: AC-04
      text: "Skill generates a Requirements Matrix covering all identified gaps"
    - id: AC-05
      text: "User can review, correct, and prioritize the matrix before any files are created"
    - id: AC-06
      text: "Skill creates goal.md files only for user-approved gaps"
    - id: AC-07
      text: "Each generated goal.md references the source flow and the specific gap it addresses"
    - id: AC-08
      text: "Open Questions appear as decision_needed — never silently skipped"
    - id: AC-09
      text: "Scope boundaries appear as out_of_scope — documented, not missed"
    - id: AC-10
      text: "Requirements Matrix is saved as requirements_matrix.md alongside the flow file"
    - id: AC-11
      text: "Skill successfully processes FLOW-002 (7 known gaps as validation test)"
    - id: AC-12
      text: "Generated goal.md files are sufficient for explore-requirements to execute without additional context"
---

# Requirement: Derive Requirements from User Flow

## 1. Overview

This requirement defines a **workflow and AI skill** that bridges the gap between completed user flows and the requirement documents they imply.

When a user flow is finished, it identifies which requirements already exist, which need to be extended, and which are entirely missing. Today, this analysis happens manually — someone reads the flow's "Implementing Epics/Features" table and "Gaps Requiring New Requirements" section, then decides what to do next. There is no systematic, automated support for this transition step.

This requirement defines the `derive-requirements-from-flow` skill, which automates the gap analysis and generates actionable work items for each identified requirement gap.

**Analogy to existing work**: REQ-PROC-026 (user_needs_to_design_system_bridge) bridges personas → design system rules. This requirement bridges user flows → functional/non-functional requirements. Same principle, different layer.

## 2. The Gap

The current workflow chain has a missing step:

```
create-user-flow → ??? → explore-requirements → create-impl-task → implementation
```

After a user flow is approved (or reaches a stable draft), the engineer must manually:

1. Read through the flow's "Implementing Epics/Features" and "Gaps Requiring New Requirements" sections
2. Identify what requirements exist, what needs updating, what is entirely missing
3. Decide on priority and sequencing
4. Create goal.md files for each new or updated requirement

This is:
- **Error-prone**: Gaps in the flow are missed when reading manually
- **Tedious**: FLOW-002 alone has 7 identified gaps across a 400-line document
- **Inconsistent**: No standard format for the analysis — each engineer does it differently
- **Untraceable**: No artifact documents which flow gaps were addressed and how

**Concrete trigger**: After completing FLOW-002 "Instruct Client on Protocol", 7 requirement gaps were identified in the flow document. There was no structured path to turn these into concrete `explore-requirements` tasks.

## 3. Desired Workflow

```
create-user-flow [draft or approved]
       ↓
derive-requirements-from-flow
  ├── Reads flow (Gaps, Implementing Epics, Open Questions, Screens, Scope Boundaries)
  ├── Scans existing requirements for matches
  ├── Generates Requirements Matrix (exists_complete / exists_needs_update / new_needed / ...)
  ├── User reviews, corrects, and prioritizes
  └── Creates goal.md files for approved gaps
       ↓
explore-requirements (per gap, for new/update)
       ↓
create-impl-task
       ↓
implementation
```

## 4. Skill Behavior

### 4.1 Inputs

- Path to a user flow file (`flow.md`)
- Optional: specific areas to focus on (defaults to all)

### 4.2 Analysis Steps

**Step 1 — Read the flow**: Extract structured information from:
- "Implementing Epics/Features" table — what steps map to which existing epics/features, and what the coverage status is
- "Gaps Requiring New Requirements" section — explicitly identified missing requirements
- "Open Questions" — items that need human decisions before requirements can be written
- "Screens/Components Involved" — implicit UI requirements not always captured in explicit gaps
- Scope boundaries ("This flow does NOT cover...") — deferred items, potential future flows

**Step 2 — Scan existing requirements**: For each gap, search `requirements_tasks/` to determine:
- Does a requirement exist that covers this?
- If yes: does it cover it fully, partially, or only in name (placeholder)?

**Step 3 — Build Requirements Matrix**: One row per identified gap:

| Flow Reference | Gap Description | Existing Requirement | Status | Action |
|---|---|---|---|---|
| Steps 1-4, Instruction View | Shared data entry component in instruction view | `feat_therapist_transfer_ui/requirements.md` | `exists_needs_update` | Extend REQ-FUNC-007-01 |
| Steps 6-7, Plan Receiving | Client receipt confirmation with accept/decline | `feat_plan_receiving/requirements.md` | `exists_placeholder` | Full spec needed |
| Steps 9-11, Data Entry | Core client data entry screen | — | `new_needed` | Create new epic |
| Open Question 4 | Notification content behavior | — | `decision_needed` | Human decision first |
| "This flow does NOT cover..." | Ongoing daily entry | — | `out_of_scope` | Note for future flow |

**Step 4 — Present matrix to user**: Show full matrix and ask:
- Are there gaps I missed?
- Which are priority for this iteration?
- Which Open Questions need decisions before writing requirements?

**Step 5 — Generate work items**: For each gap approved by user, create a `goal.md` in the appropriate task location. Each goal.md references the source flow and specific gap.

### 4.3 Gap Status Categories

| Status | Meaning | Skill Action |
|---|---|---|
| `exists_complete` | Requirement already fully covers this | No action, note in matrix |
| `exists_needs_update` | Requirement exists but needs extension | Create update goal.md |
| `exists_placeholder` | Requirement exists but is largely empty/stub | Create full-spec goal.md |
| `new_needed` | No requirement exists | Create explore goal.md for new epic/feature |
| `decision_needed` | Human decision required before writing req | Flag for user, no goal.md |
| `out_of_scope` | Explicitly deferred or excluded by the flow | Document in matrix, no action |

### 4.4 Output

After user approval of the matrix:

```
Requirements Matrix saved: requirements_user_needs/user_flows/[flow_name]/requirements_matrix.md

Created goal.md files (3 of 7 gaps — per user priority):
  - requirements_tasks/functional/client/epic_data_input/tasks/2026-02-21_explore_data_entry_screen/goal.md
  - requirements_tasks/functional/shared/epic_data_transfer/feat_plan_receiving/tasks/2026-02-21_explore_plan_receipt_ui/goal.md
  - requirements_tasks/functional/client/.../tasks/2026-02-21_explore_notification_time_mapping/goal.md

Pending (awaiting human decisions):
  - Open Question 4: Notification content behavior (decision_needed)
  - Open Question 8: Reflection prompt type (decision_needed)

Deferred (out_of_scope per flow):
  - Ongoing daily entry → separate flow needed
  - Protocol update delivery → Open Question 7

Next step: Use explore-requirements skill for each created goal.md
```

## 5. Quality Criteria

A high-quality `derive-requirements-from-flow` execution:

- **Comprehensive**: Finds all flow gaps, not only those explicitly labeled "gaps"
- **Precise**: Correctly distinguishes `exists_needs_update` from `new_needed` — no duplicate requirements created
- **Traceable**: Each generated goal.md references the source flow and gap number/ID
- **Decision-aware**: Flags all Open Questions that block requirement writing as `decision_needed`, never silently skips them
- **Scope-aware**: Captures "This flow does NOT cover..." as `out_of_scope` items — they are not missed, they are consciously deferred
- **Non-invasive**: Does NOT write requirements directly — it sets up the workspace for `explore-requirements` to execute
- **Lean output**: Generated goal.md files are specific enough that `explore-requirements` can execute without additional context from the user

## 6. Acceptance Criteria

- [ ] `derive-requirements-from-flow` skill exists in `.claude/skills/derive-requirements-from-flow/skill.md`
- [ ] Skill reads all relevant flow sections: Implementing Epics/Features, Gaps, Open Questions, Screens/Components, Scope Boundaries
- [ ] Skill scans existing requirements and correctly categorizes each gap (not just gaps explicitly listed in the flow)
- [ ] Skill generates a Requirements Matrix covering all identified gaps
- [ ] User can review, correct, and prioritize the matrix before any files are created
- [ ] Skill creates goal.md files only for user-approved gaps
- [ ] Each generated goal.md references the source flow and the specific gap it addresses
- [ ] Open Questions appear as `decision_needed` — never silently skipped
- [ ] Scope boundaries appear as `out_of_scope` — documented, not missed
- [ ] Requirements Matrix is saved as `requirements_matrix.md` alongside the flow file
- [ ] Skill successfully processes FLOW-002 "Instruct Client on Protocol" (7 known gaps as validation test)
- [ ] Generated goal.md files are sufficient for `explore-requirements` to execute without additional context

## 7. What This Requirement Is NOT

This requirement is about the **gap analysis and task-generation step only**. It is NOT about:

- Writing the actual requirements (that is `explore-requirements`)
- Updating existing requirement files directly (that is done by `explore-requirements` when invoked on the generated goal.md)
- Deciding what to build (that is the human's decision, informed by the matrix)
- Replacing user judgment (the matrix is always reviewed before goal.md files are created)

## 8. References

- Source flow that triggered this requirement: `requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md`
- Analogous requirement (persona → design system bridge): `requirements_tasks/process/AI_rules/requirements_management/user_needs_to_design_system_bridge/requirements.md`
- Downstream skill: `.claude/skills/explore-requirements/skill.md`
- Upstream skill: `.claude/skills/create-user-flow/skill.md`
- Workflow wizard: `.claude/skills/workflow-wizard/skill.md` (needs updating once skill exists)
