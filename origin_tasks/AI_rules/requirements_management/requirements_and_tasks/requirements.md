---
id: REQ-PROC-009
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: active
effort: XL
stakeholder: developer
created: 2025-08-31
updated: 2026-03-05
after: []
blocks: [REQ-PROC-010, REQ-PROC-029]
  - REQ-PROC-035
  - REQ-PROC-034
  - REQ-PROC-045
trackable_items:
  acceptance_criteria:
    - id: AC-01
    - id: AC-02
    - id: AC-03
  sections:
    - id: SEC-01
      name: "Overview"
      heading: "## Overview"
    - id: SEC-02
      name: "Folder Structure"
      heading: "## Folder Structure"
    - id: SEC-03
      name: "Requirements Versioning"
      heading: "## Requirements Versioning"
    - id: SEC-04
      name: "Task Structure"
      heading: "## Task Structure"
    - id: SEC-05
      name: "Task Lifecycle"
      heading: "## Task Lifecycle"
    - id: SEC-06
      name: "Meta Information Standards"
      heading: "## Meta Information Standards"
    - id: SEC-07
      name: "Priority System"
      heading: "## Priority System"
    - id: SEC-08
      name: "ID Generation Rules"
      heading: "## ID Generation Rules"
    - id: SEC-09
      name: "Status Values"
      heading: "## Status Values"
    - id: SEC-10
      name: "Effort Scale"
      heading: "## Effort Scale (T-Shirt Sizing)"
    - id: SEC-11
      name: "Coverage Tracking"
      heading: "## Coverage Tracking"
    - id: SEC-12
      name: "Templates"
      heading: "## Templates"
    - id: SEC-13
      name: "Meta Information Lifecycle"
      heading: "## Meta Information Lifecycle"
    - id: SEC-14
      name: "Migration Strategy"
      heading: "## Migration Strategy"
---

# Requirements and Tasks Structure

## User Story

As a developer I want to have a clear structure and process when working with the AI so that the current state is clear and transparent and the history is preserved in a readable way. I want standardized meta information for requirements and tasks that enables querying, reporting, and coverage tracking.

## Overview

The `requirements_tasks/` folder is the central repository for all requirements and AI tasks in this project. It provides:

- **Organization**: All functional, non-functional, and process requirements in one place
- **Traceability**: Tasks are always linked to specific requirements with coverage tracking
- **History**: Git versioning preserves the complete evolution of requirements
- **Transparency**: Clear folder structure makes the current state immediately visible
- **Queryability**: Standardized meta information enables scripts to generate reports and analytics
- **Coverage Tracking**: Bidirectional linking between requirements and tasks shows what's implemented, in progress, planned, or missing

## Folder Structure

```
requirements_tasks/
├── [category]/                              # e.g., "process", "features", "infrastructure"
│   └── [requirement_name]/                  # Unique, verbose name
│       ├── requirements.md                  # Single file, git-versioned
│       └── tasks/
│           └── [YYYY-MM-DD]_[impl|explore]_[task_name][_(completed)]/
│               ├── goal.md                  # Task objective + requirements version reference
│               └── plans_and_protocols/
│                   └── [YYYY-MM-DD]_[##]_[plan|protocol]_[name].md
```

### Key Elements

| Element | Description |
|---------|-------------|
| `[category]/` | Requirement category (only user can create new categories; AI may suggest) |
| `[requirement_name]/` | Must be unique and verbose across the project |
| `requirements.md` | Single source of truth for the requirement (versioned by git) |
| `tasks/` | Contains all tasks needed to implement the requirement |
| `goal.md` | Task objective with reference to requirements version (git commit hash) |
| `plans_and_protocols/` | AI working documents: plans and execution protocols |

## Requirements Versioning

Requirements are versioned using **git** rather than date-prefixed files:

- **Single file**: Each requirement has exactly one `requirements.md` file
- **Git history**: Changes are tracked via git commits
- **Task traceability**: Each task's `goal.md` references the git commit hash of the requirements version it was created against

### Why Git Versioning?

| Benefit | Description |
|---------|-------------|
| **Maintenance** | Single file to edit per requirement |
| **Traceability** | Git commit hash preserves exact state for each task |
| **Self-documenting** | Summary in goal.md provides quick reference |
| **Git-native** | Leverages git's built-in versioning capabilities |
| **Minimal redundancy** | Only summary stored, not full copy |
| **Tool support** | Standard git tools for diffs, blame, history |

## Task Structure

### Task Folder Naming

```
[YYYY-MM-DD]_[type]_[task_name][_(completed)]
```

- **Date**: Shows creation order and links to requirements version
- **Type**: `impl` (implementation) or `explore` (exploration/research)
- **Name**: Descriptive task name
- **Completion marker**: `_(completed)` suffix added when task is done

### goal.md Template

Each task's `goal.md` must include a requirements version reference:

```markdown
**Requirements Version:**
- Git Commit: [hash]
- Date: [YYYY-MM-DD]
- File: ../requirements.md

## Requirements Summary
[Brief summary of relevant requirements at task creation]

## Full Requirements
For complete requirements at task creation time:
`git show [hash]:path/to/requirements.md`

## Task Objective
[Description of what needs to be done]
```

### plans_and_protocols/ Contents

Files follow the naming pattern:
```
[YYYY-MM-DD]_[##]_[plan|protocol]_[name].md
```

- **Date**: When the file was created
- **Number** (`##`): Sequential number (01, 02, 03...) to maintain order
- **Type**: `plan` (strategy/approach) or `protocol` (execution log)
- **Name**: Descriptive name for the content

**Purpose**:
- **Plans**: Describe the approach to solve the task
- **Protocols**: Document what was tried, what worked, and what didn't

## Task Lifecycle

1. **Creation**: Task folder created with `goal.md` containing requirements version reference
2. **Planning**: AI creates plan files in `plans_and_protocols/`
3. **Execution**: AI documents progress in protocol files
4. **Retrospection**: Before completion, lessons learned must be documented
5. **Completion**: User decides if task is complete; `_(completed)` suffix added to folder name

### Important Rules

- Only the **user** can mark a task as completed
- Lessons learned must be documented **before** marking complete
- The AI must create working documents in `plans_and_protocols/` during execution

## Viewing Historical Requirements

To see the exact requirements a task was based on:

```bash
# Using the git commit hash from goal.md
git show [commit_hash]:path/to/requirements.md
```

This ensures historical tasks remain fully understandable, even months or years later.

---

## Meta Information Standards

### Philosophy

Standardized meta information enables:
- **Prioritization**: Clear urgency and impact scoring
- **Planning**: Effort estimation and dependency tracking
- **Reporting**: Scripts can query status, coverage, and priorities
- **Traceability**: Every requirement and task has a unique ID
- **Coverage**: Track which parts of requirements are implemented

### requirements.md Meta Information

Each `requirements.md` file must include YAML frontmatter with standardized metadata:

```yaml
---
id: REQ-[CATEGORY]-[NUMBER]
urgency: 0-5
urgency_reason: U[0-5]-[CODE]
impact: 0-5
impact_reason: I[0-5]-[CODE]
status: draft | defined | in_progress | implemented | active | deprecated
effort: XS | S | M | L | XL | XXL
stakeholder: client | therapist | developer | shared
created: YYYY-MM-DD
updated: YYYY-MM-DD
after: []
blocks: []
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Description of acceptance criterion"
  sections:
    - id: SEC-01
      name: "Section Name"
      heading: "## X. Section Heading"
---
```

#### Field Definitions

| Field | Purpose | Format | Required | Default | Example |
|-------|---------|--------|----------|---------|---------|
| `id` | Unique identifier | `REQ-[CAT]-[NUM]` | Yes | Generated | `REQ-FUNC-042` |
| `urgency` | Time pressure (0-5) | Integer | Yes | 2 | `4` |
| `urgency_reason` | Why this urgency | `U[0-5]-[CODE]` | Yes | `U2-FREE` | `U4-DEP` |
| `impact` | Value created (0-5) | Integer | Yes | 3 | `5` |
| `impact_reason` | Why this impact | `I[0-5]-[CODE]` | Yes | `I3-STD` | `I5-MVP` |
| `status` | Current state | Enum | Yes | `draft` | `defined` |
| `effort` | Size estimate | T-shirt size | Yes | `M` | `L` |
| `stakeholder` | Primary beneficiary | Enum | Yes | `shared` | `therapist` |
| `created` | Creation date | ISO date | Yes | Today | `2026-01-08` |
| `updated` | Last update | ISO date | No | - | `2026-01-08` |
| `after` | Requirement dependencies | Array of IDs | No | [] | `[REQ-ARCH-001]` |
| `blocks` | What this blocks | Array of IDs | No | [] | `[REQ-FUNC-015]` |
| `trackable_items` | Coverage tracking | Object | No | - | See below |

#### Trackable Items (Coverage Tracking)

The `trackable_items` field enables bidirectional linking between requirements and tasks:

- **`acceptance_criteria`**: Testable success conditions (use when requirement has explicit AC)
- **`sections`**: Major requirement sections (use for broader scope or when AC doesn't exist)

Each item must have:
- **`id`**: Stable identifier (AC-01, AC-02... or SEC-01, SEC-02...)
- **`text/name`**: Human-readable description
- **`heading`** (sections only): Reference to markdown heading

**Purpose**: Tasks can reference specific AC or sections they implement, enabling coverage queries like "which acceptance criteria are not yet covered by any task?"

### goal.md Meta Information

Each `goal.md` file must include YAML frontmatter:

```yaml
---
task_id: TASK-[REQU_ID]-[NUMBER]
type: impl | explore
parent_requirement: REQ-xxx
parent_task: TASK-xxx (if sub-task)
urgency: 0-5
urgency_reason: U[0-5]-[CODE]
impact: 0-5
impact_reason: I[0-5]-[CODE]
status: pending | ready | in_progress | blocked | review | completed | cancelled
effort: XS | S | M | L | XL  # XXL is NOT allowed for tasks
estimated_hours: number (optional)
created: YYYY-MM-DD
completed: YYYY-MM-DD (when applicable)
after: []
awaiting: []        # Array of IDs: TASK-*, REQ-*, FLOW-*, or any artifact ID
awaiting_note: ""   # Required when awaiting is empty; free-text explanation of what is blocking
assigned_agent: string (optional)
covers:
  acceptance_criteria: [AC-01, AC-02]
  sections: [SEC-01]
scope_description: "Brief summary"
requirements_version:
  commit: xxxxxxx
  file: ../requirements.md
---
```

#### Field Definitions

| Field | Purpose | Format | Required | Default | Example |
|-------|---------|--------|----------|---------|---------|
| `task_id` | Unique identifier | `TASK-[REQ]-[NUM]` | Yes | Generated | `TASK-FUNC-042-01` |
| `type` | Task type | Enum | Yes | - | `impl` |
| `parent_requirement` | Link to requirement | REQ ID | Yes | - | `REQ-FUNC-042` |
| `parent_task` | For sub-tasks | TASK ID | No | - | `TASK-FUNC-042-01` |
| `urgency` | Time pressure (0-5) | Integer | Yes | Inherit | `4` |
| `urgency_reason` | Why this urgency | Code | Yes | Inherit | `U4-DEP` |
| `impact` | Value created (0-5) | Integer | Yes | Inherit | `5` |
| `impact_reason` | Why this impact | Code | Yes | Inherit | `I5-MVP` |
| `status` | Current state | Enum | Yes | `pending` | `in_progress` |
| `effort` | Size estimate | T-shirt size | Yes | `M` | `S` |
| `estimated_hours` | Time estimate | Number | No | - | `4` |
| `created` | Creation date | ISO date | Yes | Today | `2026-01-08` |
| `completed` | Completion date | ISO date | No | - | `2026-01-10` |
| `after` | Task dependencies | Array of IDs | No | [] | `[TASK-FUNC-041-01]` |
| `awaiting` | Blocking artifact IDs (TASK-*, REQ-*, FLOW-*, etc.) | Array of IDs | No | [] | `[FLOW-003]` |
| `awaiting_note` | Free-text reason when no referenceable ID exists | String | Conditional | `""` | `"Waiting for user decision on X"` |
| `assigned_agent` | AI agent tracking | String | No | - | `opus-4.5` |
| `covers` | What this implements | Object | No | - | See below |
| `scope_description` | Brief summary | String | No | - | `"Phase 1: Domain"`|
| `requirements_version` | Snapshot | Object | Yes | - | See template |

#### Covers Field (Coverage Tracking)

The `covers` field links tasks to specific parts of requirements:

```yaml
covers:
  acceptance_criteria: [AC-01, AC-02, AC-05]
  sections: [SEC-01]
```

**Purpose**: Enables queries like "which tasks implement acceptance criterion AC-03?" or "what's the coverage status of this requirement?"

**Priority Inheritance**: Tasks inherit `urgency` and `impact` from their parent requirement by default, but can override if justified.

---

## Priority System

The project uses a two-dimensional priority system: **URGENCY** (time factor) and **IMPACT** (value factor).

**Score Calculation**: `Priority Score = (URGENCY × 10) + IMPACT`
- Highest priority: 55 (U5, I5)
- Lowest priority: 00 (U0, I0)

### URGENCY Scale (0-5)

*Leitfrage: Why must this happen NOW? What happens if we wait?*

| Value | Code | Meaning | Description |
|-------|------|---------|-------------|
| **5** | `U5-BLOCK` | Technical Blocker | Blocks other tasks technically |
| **5** | `U5-PROC` | Process Blocker | Team/AI can't work efficiently |
| **5** | `U5-RISK` | Critical Risk | Acute danger (crash, data loss, security) |
| **5** | `U5-GAP` | Exploration Gap | MVP implementation blocked by unknown approach |
| **4** | `U4-DEP` | Dependency | Prerequisite for next planned feature |
| **4** | `U4-FAIL` | Fail Fast | High risk, must test early |
| **4** | `U4-TIME` | Hard Deadline | External deadline forces action |
| **3** | `U3-SPRINT` | Sprint Focus | Part of current sprint |
| **3** | `U3-CTX` | Context Synergy | Efficiency gain (working in this area now) |
| **3** | `U3-FIX` | Medium Fix | User pain but workarounds exist |
| **2** | `U2-FREE` | Decoupled | No dependencies, can be delayed |
| **2** | `U2-WAIT` | Waiting | Needs external input |
| **2** | `U2-PERF` | Non-Critical Perf | Optimization for later scale |
| **1** | `U1-COSM` | Cosmetic | Formatting, typos |
| **1** | `U1-REFA` | Micro Refactor | Small cleanup |
| **1** | `U1-FILL` | Filler | 5-minute tasks for downtime |
| **0** | `U0-HOLD` | On Hold | Blocked or unclear |

### IMPACT Scale (0-5)

*Leitfrage: What value does this create for users or development?*

| Value | Code | Meaning | Description |
|-------|------|---------|-------------|
| **5** | `I5-MVP` | MVP Core | Main function, product is useless without it |
| **5** | `I5-STOP` | Showstopper | Bug prevents app usage |
| **5** | `I5-ENAB` | Massive Enabler | Drastically increases dev speed |
| **5** | `I5-LEGAL` | Compliance | Required for legal/store compliance |
| **4** | `I4-USP` | Key Feature | Differentiator, high user value |
| **4** | `I4-PAIN` | Pain Relief | Solves major user problem |
| **4** | `I4-DEBT` | Debt Reduction | Rescues maintainability/stability |
| **4** | `I4-DATA` | Data Integrity | Prevents data corruption |
| **3** | `I3-STD` | Standard Expected | Hygiene factor (expected feature) |
| **3** | `I3-PROC` | Process Optimization | Helps developers |
| **3** | `I3-UX` | UX Flow | Makes UI smoother |
| **2** | `I2-JOY` | Delighter | Nice animations, polish |
| **2** | `I2-EDGE` | Edge Case | Affects <1% of users |
| **2** | `I2-TXT` | Wording/Polish | Better text/labels |
| **1** | `I1-INV` | Invisible | Technical change, no visible effect |
| **1** | `I1-PIX` | Pixel Polish | Minor design tweaks |
| **0** | `I0-NONE` | No Value | Deprecated/unnecessary |

---

## ID Generation Rules

### Requirement IDs

- **Format**: `REQ-[CATEGORY]-[NUMBER]`
- **Categories**:
  - `FUNC` = functional
  - `NFUNC` = non-functional
  - `PROC` = process
- **Number**: 3-digit sequential (001, 002, ...)
- **Generator**: Script (migration) or AI (new requirements)
- **Uniqueness**: Global across project
- **Examples**:
  - `REQ-FUNC-001`
  - `REQ-NFUNC-015`
  - `REQ-PROC-003`

#### Hierarchical IDs

When an epic requirement exists **before** its child features are created, child features use IDs derived from the epic:
- Epic: `REQ-FUNC-007` → Features: `REQ-FUNC-007-01`, `REQ-FUNC-007-02`, ...
- Epic: `REQ-NFUNC-018` → Features: `REQ-NFUNC-018-01`, `REQ-NFUNC-018-02`, ...

This applies to all categories (functional, non-functional, process).

#### Epic Back-References

Child requirements do **not** need a `parent_epic:` field in their YAML frontmatter. The folder hierarchy implies membership. Retroactive application to existing requirements is not required.

### Task IDs

- **Format**: `TASK-[REQU_ID_WITHOUT_PREFIX]-[NUMBER]`
- **Number**: 2-digit sequential (01, 02, ...)
- **Generator**: AI (setup-task skill)
- **Uniqueness**: Global across project
- **Examples**:
  - `TASK-FUNC-042-01` (first task for REQ-FUNC-042)
  - `TASK-FUNC-042-02` (second task)

### Sub-Task IDs

- **Format**: `TASK-[PARENT_TASK_ID]-[NUMBER]`
- **Example**: `TASK-FUNC-042-01-01` (sub-task of TASK-FUNC-042-01)

### Trackable Item IDs

- **Acceptance Criteria**: `AC-01`, `AC-02`, ...
- **Sections**: `SEC-01`, `SEC-02`, ...
- **Immutability**: Once assigned, IDs never change (even if text changes)

### ID Registry Content Contract

The ID registry (`requirements_tasks/_meta/id_registry.md`, generated by `scripts/artifacts/generate_id_registry.py`) is the project's catalog of assigned requirement identifiers and the source of each category's next free ID. Because IDs are globally unique, the catalog's value depends on enumerating all of them — top-level and hierarchical alike.

- **AC-01 — Complete enumeration**: The registry catalog lists every valid requirement ID, including hierarchical sub-requirement IDs (`REQ-CAT-NNN-NN`). Each hierarchical ID appears as its own entry grouped under its parent epic's top-level ID.
- **AC-02 — Counts include hierarchical IDs**: Every per-category count and the registry total reflect the full catalog, hierarchical sub-requirement IDs included.
- **AC-03 — Next-available is top-level only**: Each category's "Next Available ID" is derived solely from top-level IDs. A hierarchical sub-requirement ID shares its parent epic's top-level number and so does not advance its category's next-available number.

---

## Status Values

### Requirement Status Lifecycle

| Status | Description | Next States |
|--------|-------------|-------------|
| `draft` | Initial capture, incomplete | `defined`, `deprecated` |
| `defined` | Complete, ready for tasks | `in_progress`, `active`, `deprecated` |
| `in_progress` | Has active tasks | `implemented`, `deprecated` |
| `implemented` | All acceptance criteria defined in the current version are satisfied by completed tasks; requirement is stable — no open work remains and no further work is anticipated unless the requirement itself is revised | `deprecated` |
| `active` | Living document: the requirement describes a continuously evolving process, standard, or guideline that is currently in effect. New improvement tasks may be spawned at any time without this status changing. | `deprecated` |
| `deprecated` | No longer relevant | — |

> **`implemented` vs `active`**: Use `implemented` for concrete deliverables where "all work is done" has a clear meaning. Use `active` for living documents (coding standards, testing rules, AI workflow rules, process guidelines) where improvement tasks will always continue to emerge. A requirement is a **living document** when ALL of these apply: it describes a process/standard/guideline (not a concrete deliverable); it is expected to spawn improvement tasks over time; "all tasks done" would never truly end its evolution.
>
> **Cannot auto-set `implemented`** when no `trackable_items.acceptance_criteria` are present — requires manual user confirmation in that case.

### Task Status Lifecycle

| Status | Description | Next States |
|--------|-------------|-------------|
| `pending` | Created, not started | `ready`, `cancelled` |
| `ready` | Dependencies met, can start | `in_progress`, `blocked` |
| `in_progress` | Currently being worked on | `review`, `blocked`, `completed` |
| `blocked` | Waiting on something — **MUST** have non-empty `awaiting` list, non-empty `awaiting_note`, or both | `ready`, `cancelled` |
| `review` | Awaiting user review | `completed`, `in_progress` |
| `completed` | Done and verified | - |
| `cancelled` | No longer needed | - |

---

## Effort Scale (T-Shirt Sizing)

| Size | Description | Typical Duration | Allowed in |
|------|-------------|------------------|------------|
| `XS` | Trivial change | < 1 hour | requirements, tasks |
| `S` | Small feature | 1-4 hours | requirements, tasks |
| `M` | Medium feature | 1-2 days | requirements, tasks |
| `L` | Large feature | 3-5 days | requirements, tasks |
| `XL` | Large multi-week effort | > 1 week | requirements, tasks |
| `XXL` | Epic — spans multiple requirements or releases | Months | **requirements only** |

> **Rule**: `XXL` is **forbidden in tasks** (`goal.md`). Tasks must be broken down until they fit within `XL` or smaller.

---

## Coverage Tracking

Below is a description of the coverage tracking system, but some details are omitted. Refer requirements_tasks\process\AI_rules\requirements_management\requirements_and_tasks\tasks\2026-01-08_explore_task_meta_data\plans_and_protocols\2026-01-08_03_protocol_requirement_task_linking.md for all details.

### Purpose

Track which parts of requirements have been implemented, are in progress, planned, or missing.

### How It Works

1. **Requirements** define `trackable_items` (acceptance criteria and/or sections with stable IDs)
2. **Tasks** reference items they implement via `covers` field
3. **Scripts** compute coverage by scanning all tasks for a requirement

### Coverage Queries

Scripts can answer:
- **Coverage percentage**: How much of this requirement is implemented?
- **Gaps**: Which acceptance criteria have no task coverage?
- **Task scope**: What does this task implement?
- **Implementation history**: Which tasks covered this AC/section?
- **Coverage matrix**: Overview of all requirements

### Example Coverage Report

```
REQ-FUNC-042: PlanEvaluationView
Total: 12 AC | Implemented: 8 | In Progress: 2 | Planned: 1 | Gaps: 1
Coverage: 92% complete

AC-01: ✅ implemented (TASK-FUNC-042-02, completed)
AC-02: ✅ implemented (TASK-FUNC-042-02, completed)
AC-03: ⏳ in progress (TASK-FUNC-042-03)
...
AC-12: ❌ no coverage (gap!)
```

---

## Templates

### requirements.md Template

```markdown
---
id: REQ-[CATEGORY]-[NUMBER]
urgency: 3
urgency_reason: U3-SPRINT
impact: 4
impact_reason: I4-USP
status: defined
effort: M
stakeholder: therapist
created: 2026-01-08
after: []
blocks: []
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "First acceptance criterion"
    - id: AC-02
      text: "Second acceptance criterion"
  sections:
    - id: SEC-01
      name: "Section Name"
      heading: "## 4. Section Heading"
---

# Requirement: [Descriptive Name]

## 1. User Story

As a [stakeholder], I want to [action], so that [benefit].

## 2. Specification

[Detailed specification...]

## 3. Acceptance Criteria

- [ ] AC-01: First acceptance criterion
- [ ] AC-02: Second acceptance criterion

## 4. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-xxx | defined | Needs X first |

## 5. References

- Related: [path/to/related/requirements.md]

---
## Version History
[Version history information]
```

### goal.md Template

```markdown
---
task_id: TASK-[REQ-ID]-[NUMBER]
type: impl
parent_requirement: REQ-FUNC-042
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-MVP
status: pending
effort: M
created: 2026-01-08
after: []
awaiting: []
covers:
  acceptance_criteria: [AC-01, AC-02]
  sections: [SEC-01]
scope_description: "Brief summary of scope"
requirements_version:
  commit: abc1234
  file: ../requirements.md
---

# Goal: [Descriptive Task Name]

## Objective

[Clear description of what needs to be done]

## Requirements Summary

[Brief summary of relevant requirements at task creation]

For complete requirements at task creation time:
```
git show [commit]:path/to/requirements.md
```

Current requirements: ../requirements.md

## Scope

[What's in scope, what's out of scope]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Implementation Steps

1. Step 1
2. Step 2
3. Step 3

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-xxx | completed | Needs X first |

## Notes

[Additional context, constraints, decisions]
```

---

## Meta Information Lifecycle

This section defines the processes for creating, updating, and maintaining meta information throughout the lifecycle of requirements and tasks.

### Creating New Requirements (setup-task skill)

When creating a new requirement:

1. **Generate ID**: Use next available ID from `requirements_tasks/_meta/id_registry.md`
2. **Determine Priority**: Use the decision trees below
3. **Set Initial Status**: `draft` (incomplete), `defined` (concrete deliverable, ready for tasks), or `active` (living document — coding standards, AI rules, process guidelines)
4. **Define trackable_items**: Extract from acceptance criteria or identify major sections
5. **Run Validation**: Execute `python scripts/validate_meta.py` to verify

#### Priority Determination Decision Tree

**Step 1: Determine URGENCY (Time Factor)**

Ask: *"Why must this happen NOW? What happens if we wait?"*

| If... | Then Urgency | Code |
|-------|--------------|------|
| Blocks other tasks technically | 5 | `U5-BLOCK` |
| Team/AI can't work efficiently | 5 | `U5-PROC` |
| Acute danger (crash, data loss, security) | 5 | `U5-RISK` |
| MVP blocked by unknown approach | 5 | `U5-GAP` |
| Prerequisite for next planned feature | 4 | `U4-DEP` |
| High risk, must test early | 4 | `U4-FAIL` |
| External deadline forces action | 4 | `U4-TIME` |
| Part of current sprint | 3 | `U3-SPRINT` |
| Working in this area now (context synergy) | 3 | `U3-CTX` |
| User pain but workarounds exist | 3 | `U3-FIX` |
| No dependencies, can be delayed | 2 | `U2-FREE` |
| Needs external input | 2 | `U2-WAIT` |
| Optimization for later scale | 2 | `U2-PERF` |
| Formatting, typos | 1 | `U1-COSM` |
| Small cleanup | 1 | `U1-REFA` |
| 5-minute tasks for downtime | 1 | `U1-FILL` |
| Blocked or unclear | 0 | `U0-HOLD` |

**Step 2: Determine IMPACT (Value Factor)**

Ask: *"What value does this create for users or development?"*

| If... | Then Impact | Code |
|-------|-------------|------|
| Main function, product useless without | 5 | `I5-MVP` |
| Bug prevents app usage | 5 | `I5-STOP` |
| Drastically increases dev speed | 5 | `I5-ENAB` |
| Required for legal/store compliance | 5 | `I5-LEGAL` |
| Differentiator, high user value | 4 | `I4-USP` |
| Solves major user problem | 4 | `I4-PAIN` |
| Rescues maintainability/stability | 4 | `I4-DEBT` |
| Prevents data corruption | 4 | `I4-DATA` |
| Hygiene factor (expected feature) | 3 | `I3-STD` |
| Helps developers | 3 | `I3-PROC` |
| Makes UI smoother | 3 | `I3-UX` |
| Nice animations, polish | 2 | `I2-JOY` |
| Affects <1% of users | 2 | `I2-EDGE` |
| Better text/labels | 2 | `I2-TXT` |
| Technical change, no visible effect | 1 | `I1-INV` |
| Minor design tweaks | 1 | `I1-PIX` |
| Deprecated/unnecessary | 0 | `I0-NONE` |

**Step 3: Estimate EFFORT**

| Size | Typical Duration | Examples |
|------|------------------|----------|
| `XS` | < 1 hour | Fix typo, add comment, simple config change |
| `S` | 1-4 hours | Add simple function, minor UI tweak |
| `M` | 1-2 days | New feature component, moderate refactor |
| `L` | 3-5 days | Multi-file feature, significant refactor |
| `XL` | > 1 week | Epic-sized, architectural change |

### Creating New Tasks (setup-task skill)

When creating a new task:

1. **Generate task_id**: `TASK-[CATEGORY]-[REQ_NUM]-[NEXT_NUM]`
   - Look up parent requirement ID
   - Count existing tasks to determine next number
2. **Inherit Priority**: Copy urgency/impact from parent requirement
   - Override ONLY if task has different urgency (document reason)
3. **Determine covers**:
   - Read parent's `trackable_items`
   - Ask user which AC/sections this task implements
   - Leave empty for explore tasks
4. **Set Initial Status**: `pending`
5. **Run Validation**: Execute validation script

### Completing Tasks (complete-task skill)

When marking a task as completed:

1. **Update goal.md YAML frontmatter**:
   - Set `status: completed`
   - Set `completed: YYYY-MM-DD`
2. **Verify covers**: Ensure `covers` accurately reflects what was implemented
3. **Check Requirement Status Propagation**:
   - If requirement `status: active` → leave as `active` (living documents never transition out)
   - If requirement has `trackable_items.acceptance_criteria` → check if all ACs are covered by completed tasks; if yes → set `status: implemented`
   - If requirement has NO acceptance criteria → ask user to manually confirm before setting `status: implemented`
4. **Run Validation**: Ensure all references are valid
5. **Regenerate Reports**: Run status overview script

### Quality Gates (verify-quality skill)

Before completing any task, verify:

1. **Meta Information Exists**: YAML frontmatter present in goal.md
2. **Required Fields Present**: task_id, parent_requirement, status, covers
3. **covers References Valid**: All referenced AC/SEC IDs exist in parent requirement
4. **Status Consistency**: Task status matches actual state

### When Requirements Change

If requirement content changes after tasks exist:

1. **Adding New AC/Sections**:
   - Assign next available ID (AC-03, SEC-04, etc.)
   - IDs are IMMUTABLE - never reuse or change
   - Existing tasks' `covers` remain valid

2. **Removing AC/Sections**:
   - Mark as deprecated in trackable_items (don't delete)
   - Existing tasks' `covers` remain valid for history

3. **Changing AC/Section Text**:
   - Keep the same ID
   - Update the `text` field only
   - ID stability ensures historical traceability

4. **Re-assessing Priority**:
   - If requirement scope changes significantly, re-evaluate urgency/impact
   - Document reason for change in requirement file

### Status Overview Reports

The `scripts/generate_status_overview.py` script generates reports in multiple modes:

| Mode | Flag | Description |
|------|------|-------------|
| Summary | `--summary` | Quick stats: open, completed, coverage % |
| Priority | `--priority` | Tasks sorted by priority score (U×10+I) |
| Coverage | `--coverage` | Coverage % per requirement, gaps highlighted |
| Blockers | `--blockers` | Tasks with status=blocked or U5 urgency |
| Sprint | `--sprint` | Tasks with U3-SPRINT or higher urgency |
| Full | `--full` | Complete report with all sections |

Output: `requirements_tasks/STATUS.md` (or custom path with `--output`)

**Integration Points**:
- Run after completing tasks
- Run before sprint planning
- Run to identify coverage gaps

---

## Migration Strategy

### For Existing Requirements

1. Add YAML frontmatter with metadata
2. Assign unique ID
3. Add `trackable_items` for acceptance criteria and/or sections
4. Estimated effort: ~30 minutes per requirement
5. Can be done incrementally

### For Existing Tasks

1. Add YAML frontmatter with metadata
2. Link to parent requirement via `parent_requirement`
3. Add `covers` field mapping to requirement's trackable items
4. Estimated effort: ~10 minutes per task
5. Can be done incrementally

### Migration Script Support

Scripts can assist with:
- Auto-extracting AC text from markdown checkboxes
- Suggesting IDs (AC-01, AC-02, ...)
- Validating references
- Generating coverage reports

---

## Version History

Consolidated from:
- 2025-08-31_requirement.md (original date-prefixed structure)
- 2026-01-04_requirement_git_versioning.md (git versioning migration)
- 2026-01-08_meta_information_standards.md (meta information and coverage tracking)

Consolidation date: 2026-01-08
Pre-migration commit: 835166b
