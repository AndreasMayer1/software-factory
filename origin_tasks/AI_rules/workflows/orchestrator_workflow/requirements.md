---
id: REQ-PROC-008
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: implemented
effort: XL
stakeholder: developer
created: 2025-10-04
after: [REQ-PROC-004, REQ-PROC-005]
blocks:
  - REQ-PROC-041
trackable_items:
  sections:
    - id: SEC-01
      name: "Workflow Overview"
      heading: "## Workflow Overview"
    - id: SEC-02
      name: "Workflow Steps"
      heading: "## Workflow Steps"
    - id: SEC-03
      name: "Template System"
      heading: "## Template System"
    - id: SEC-04
      name: "Implementation Architecture"
      heading: "## Implementation Architecture: Individual Modes"
    - id: SEC-05
      name: "Scope"
      heading: "## Scope"
    - id: SEC-06
      name: "Continuous Improvement"
      heading: "## Continuous Improvement"
  acceptance_criteria:
    - id: AC-01
      text: "A rule file for the 'Interactive Brainstorming Workflow' exists in .roo/rules-architect/"
    - id: AC-02
      text: ".roo/rules-orchestrator/orchestrator_refactoring_process.md is renamed to .roo/rules-orchestrator/implementation_workflow.md"
    - id: AC-03
      text: "The implementation_workflow.md includes the 'Analysis & Validation Loop' and all refined phases"
    - id: AC-04
      text: "The implementation_workflow.md correctly links to orchestrator_testing_process.md"
    - id: AC-05
      text: "impl_considerations_new_feature.md exists in the appropriate location"
    - id: AC-06
      text: "impl_considerations_refactoring.md exists in the appropriate location"
    - id: AC-07
      text: "impl_considerations_bug_fixing.md exists in the appropriate location"
    - id: AC-08
      text: "The main .clinerules file references all new and updated workflow documents"
    - id: AC-09
      text: "All changes adhere to existing documentation and file naming conventions"
    - id: AC-10
      text: "All canonical templates exist in .roo-templates/"
    - id: AC-11
      text: "Each template contains: name/filename pattern, goal, whitelist, blacklist, structure guidance"
    - id: AC-12
      text: "Process usage guidance exists in .roo/rules-orchestrator/templates_usage.md"
    - id: AC-13
      text: "Orchestrator correctly passes template filenames to subtasks"
    - id: AC-14
      text: "Workflow includes post-verification documentation step"
    - id: AC-15
      text: "Architect mode subtask is triggered after user confirms working implementation"
    - id: AC-16
      text: "Comments explain WHY code exists, not what it does"
    - id: AC-17
      text: "Each workflow step has its own dedicated roo mode"
    - id: AC-18
      text: "Modes are based on original orchestrator/architect modes"
    - id: AC-19
      text: "Mode instructions are focused and maintainable"
    - id: AC-20
---

# Orchestrator Workflow Requirements

## User Story

As a developer, I want a clear and structured workflow for the orchestrator mode to facilitate efficient feature implementation through a unified AI development framework.

## Goal

To establish a comprehensive and unified framework that guides the AI's behavior in planning, implementing, and validating tasks, incorporating interactive brainstorming, detailed implementation workflows, task-specific considerations, and proper documentation practices.

---

## Workflow Overview

The orchestrator workflow provides a standardized approach to AI-assisted development that ensures consistency, clarity, and adherence to best practices across all development phases.

### Core Principles

The orchestrator workflow integrates the following guidelines and best practices:

- Clean Architecture and the BLoC pattern
- DRY, SOLID, and test-driven development principles
- Coding standards and best practices
- Documentation guidelines

### Operational Constraints

The orchestrator workflow must:

- Respect the limited context window by using appropriate strategies (e.g., subtasks, modular decomposition)
- Ensure that task constraints are respected (e.g., only edit specific files)
- Notify the user with detailed error messages when:
  - Task decomposition fails
  - Suitable tests cannot be found
  - Guidelines cannot be updated
  - User rejects proposed updates

---

## Workflow Steps

### Step 1: Planning

Analyze the requirements and create a detailed plan for implementation. The planning approach varies by task type:

- **Implementation Detail**: Create a detailed implementation plan
- **Explorative**: Explore potential solutions and define the problem

This phase corresponds to the "Interactive Brainstorming Workflow" for the `architect` mode.

### Step 2: Task Decomposition

Break down the plan into smaller, manageable tasks, considering:

- The chosen implementation approach
- Context window limitations
- Task-specific constraints

If decomposition fails, notify the user with a detailed error message.

### Step 3: Implementation

Implement the tasks following:

- The approved plan
- Coding guidelines
- Context window constraints
- Task-specific considerations based on task type:
  - New feature implementation (`impl_considerations_new_feature.md`)
  - Refactoring (`impl_considerations_refactoring.md`)
  - Bug fixing (`impl_considerations_bug_fixing.md`)

This phase follows the "Implementation Workflow" which includes the "Analysis & Validation Loop" for iterative refinement.

### Step 4: Testing

Write and run tests to ensure the implementation meets requirements:

- Follow the testing process defined in `orchestrator_testing_process.md`
- If suitable tests cannot be identified, notify the user with a detailed error message

### Step 5: Documentation

Document the implementation and update guidelines as needed:

- Update relevant documentation files
- If guidelines cannot be updated, notify the user with a detailed error message

### Step 6: Documentation Comments (Post-Verification)

**Trigger**: After the user confirms that the implementation works and tests pass.

**Purpose**: Prevent future AI sessions from removing code they don't understand.

**Process**:
1. Start a new subtask in architect mode
2. Read the relevant reports to understand what has been implemented and especially WHY it was implemented that way
3. Add comments to all new classes, functions, blocks, and lines of code explaining why they exist
4. Each comment must contain information that allows future readers to understand the underlying reason

**Note**: Comments are only added after verification to avoid maintaining outdated documentation for code that might change.

---

## Template System

### Overview

Certain workflow steps create files as artifacts. Each artifact type must have a corresponding template in `.roo-templates/`.

### Template Requirements

Each template must explicitly state:

- **Name and filename pattern**: Following the project's filename conventions for `plans_and_protocols` artifacts
- **Goal**: Why this file is needed
- **Whitelist**: What information must be present
- **Blacklist**: What must not be present
- **Structure**: How it should be written (structure, tone, level of depth)

### Canonical Template Inventory

| Template File | Purpose | Filename Pattern |
|--------------|---------|------------------|
| `template_plan.md` | Generic plan artifacts | `YYYY-MM-DD_##_plan_<short-name>.md` |
| `template_protocol.md` | Generic protocol / per-attempt protocol | `YYYY-MM-DD_##_protocol_<short-name>.md` or `part_attempt_<n>_protocol.md` |
| `template_analysis.md` | Analysis / condensation reports | `YYYY-MM-DD_##_analysis_<short-name>.md` |
| `template_arch_test_plan.md` | Architect test plan with required parts[] schema | `arch_test_plan` |
| `template_testfile_orchestrator_plan.md` | Test file orchestrator plans | `YYYY-MM-DD_##_plan_testfile_<fileId>.md` |
| `template_part_attempt_protocol.md` | Per-part attempt protocols | `part_attempt_<n>_protocol.md` |
| `template_file_protocol.md` | Aggregated file protocol | `YYYY-MM-DD_##_<fileId>_protocol.md` |
| `template_test_run_protocol.md` | Test run / verification protocol | `YYYY-MM-DD_##_test_run_protocol.md` |
| `template_metrics.md` | Metrics manifest | `plans_and_protocols/metrics.md` |
| `template_blocker.md` | Blocker / explore_test_blocker artifacts | `explore_test_blocker_<timestamp>.md` |
| `template_scope_too_large.md` | Scope-too-large protocol | `YYYY-MM-DD_##_protocol_scope_too_large.md` |
| `template_git_commit_error_protocol.md` | Git commit error protocol | `YYYY-MM-DD_##_git_commit_error_protocol.md` |
| `template_final_report.md` | Final report / summary artifacts | `YYYY-MM-DD_##_final_report.md` |

### Storage and Process Guidance

- **Templates**: MUST be stored in `.roo-templates/`
- **Process guidance**: MUST be stored in `.roo/rules-orchestrator/templates_usage.md` (or equivalent `.roo` rule files)
- **DO NOT** store process governance or enforcement rules under `doc/`

### Orchestrator Template Usage Requirements

When creating a subtask that will produce a `plans_and_protocols` artifact, the orchestrator MUST:

1. **Specify template**: Include the exact template filename from `.roo-templates/` in subtask instructions
2. **Define location**: Require the subtask to create the artifact in the parent task's `plans_and_protocols/` folder using the prescribed filename pattern
3. **Enforce rules**: Explicitly instruct which template sections are mandatory (whitelist) and forbidden (blacklist), requiring inclusion of required metadata fields
4. **Separate concerns**: For protocol and analysis artifacts, prohibit next-step owner assignments (those belong only in plan artifacts)
5. **Require plans when needed**: If a plan is required, request an architect-mode subtask to produce it using `template_plan.md`; do not accept ad-hoc "next steps" inside protocol/analysis artifacts

### Artifact Types

Not all artifacts are plans. The workflow prescribes when each type is appropriate:

- **Plans**: Required when actionable next steps are needed
- **Analyses**: For investigation and understanding
- **Protocols**: For recording execution and outcomes
- **Evidence captures**: For documenting proof of completion

### Extension and Maintenance

The canonical inventory is maintained by process owners (orchestrator maintainers). Adding or changing templates requires:

1. A documented plan and protocol under the relevant `requirements_tasks/.../plans_and_protocols/` folder
2. An update to `.roo/rules-orchestrator/templates_usage.md`
3. A recorded review and human approval before committing changes

AI-agent pilots may validate enforcement, but template additions/changes must be approved by a human reviewer before being treated as canonical.

### Compatibility

Existing `plans_and_protocols` artifacts remain valid historical records. New subtasks should prefer canonical templates and fill missing metadata fields when reasonable.

---

## Implementation Architecture: Individual Modes

### Problem Statement

The `orchestrator` roo mode contains too many instructions because it handles all process steps (except architecture mode).

### Solution

Create an individual roo mode for each step in the workflow. Each mode must:

- Be based on the original roo `orchestrator` or `architect` modes
- Handle only its specific workflow step
- Follow the unified framework principles

This modular approach improves:

- Maintainability of mode instructions
- Clarity of responsibilities
- Context efficiency (smaller, focused instruction sets)

---

## Scope

This requirement covers the definition and integration of:

- The "Interactive Brainstorming Workflow" for the `architect` mode
- The "Implementation Workflow" including the "Analysis & Validation Loop"
- Links to existing `orchestrator_testing_process.md`
- Task-specific consideration documents:
  - `impl_considerations_new_feature.md`
  - `impl_considerations_refactoring.md`
  - `impl_considerations_bug_fixing.md`
- Updates to the main `.clinerules` file
- Template system in `.roo-templates/`
- Individual roo modes per workflow step

---

## Continuous Improvement

The orchestrator workflow includes mechanisms for:

- Collecting lessons learned
- Identifying areas for workflow improvement
- Automating the process of updating the workflow based on collected data

---

## Acceptance Criteria

### Workflow Structure
- [ ] A rule file for the "Interactive Brainstorming Workflow" exists in `.roo/rules-architect/`
- [ ] `.roo/rules-orchestrator/orchestrator_refactoring_process.md` is renamed to `.roo/rules-orchestrator/implementation_workflow.md`
- [ ] The `implementation_workflow.md` includes the "Analysis & Validation Loop" and all refined phases
- [ ] The `implementation_workflow.md` correctly links to `orchestrator_testing_process.md`

### Task-Specific Considerations
- [ ] `impl_considerations_new_feature.md` exists in the appropriate location
- [ ] `impl_considerations_refactoring.md` exists in the appropriate location
- [ ] `impl_considerations_bug_fixing.md` exists in the appropriate location

### Configuration
- [ ] The main `.clinerules` file references all new and updated workflow documents
- [ ] All changes adhere to existing documentation and file naming conventions

### Template System
- [ ] All canonical templates exist in `.roo-templates/`
- [ ] Each template contains: name/filename pattern, goal, whitelist, blacklist, structure guidance
- [ ] Process usage guidance exists in `.roo/rules-orchestrator/templates_usage.md`
- [ ] Orchestrator correctly passes template filenames to subtasks

### Documentation Comments
- [ ] Workflow includes post-verification documentation step
- [ ] Architect mode subtask is triggered after user confirms working implementation
- [ ] Comments explain WHY code exists, not what it does

### Individual Modes
- [ ] Each workflow step has its own dedicated roo mode
- [ ] Modes are based on original orchestrator/architect modes
- [ ] Mode instructions are focused and maintainable

### Task Status Lifecycle
- **AC-20**: The canonical task status lifecycle is: `pending` → `in_progress` → `completed` (terminal). Valid statuses also include `blocked` (external blocker) and `cancelled`/`superseded`/`deprecated` (terminal). The status `active` is retired — it was previously used by `ux-flow-draft` tasks as a workaround, but is replaced by `status: in_progress` + `pending_feedback/question.md`. `next_tasks.py` `EXCLUDED_STATUSES` does not include `active` after migration.

---

## Version History

Consolidated from:
- 2025-10-04_requirement.md (original workflow)
- 2025-10-09_requirement.md (unified framework)
- 2025-10-12_requirement.md (documentation comments)
- 2025-11-01_requirement.md (template system)
- 2025-11-02_requirement.md (individual modes)

Consolidation date: 2026-01-04
Pre-migration commit: 1d3a2f9
