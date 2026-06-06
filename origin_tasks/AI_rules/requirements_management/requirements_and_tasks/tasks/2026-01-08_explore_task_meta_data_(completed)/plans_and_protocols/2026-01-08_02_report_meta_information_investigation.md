# Investigation Report: Meta Information for Requirements and Tasks

**Agent**: Explore (Opus)
**Agent ID**: ae09352
**Date**: 2026-01-08

---

## Executive Summary

This investigation analyzes the current state of requirements.md and goal.md files across the project, evaluates the proposed priority system from the goal.md, and proposes a comprehensive meta information structure for both file types.

---

## 1. CURRENT STATE ANALYSIS

### 1.1 Requirements.md Structure Analysis

I analyzed 11 requirements.md files across different categories:

#### Files Examined:

| # | File Path | Category |
|---|-----------|----------|
| 1 | `requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md` | Process |
| 2 | `requirements_tasks/process/AI_rules/workflows/orchestrator_workflow/requirements.md` | Process |
| 3 | `requirements_tasks/process/AI_rules/workflows/testing_workflow/requirements.md` | Process |
| 4 | `requirements_tasks/non-functional/architecture/requirements.md` | Non-Functional |
| 5 | `requirements_tasks/non-functional/ui_ux_design_system/components/toast/requirements.md` | Non-Functional |
| 6 | `requirements_tasks/non-functional/ui_ux_design_system/components/skeleton/requirements.md` | Non-Functional |
| 7 | `requirements_tasks/non-functional/ui_ux_design_system/navigation_patterns/responsive_layout_master_detail/requirements.md` | Non-Functional |
| 8 | `requirements_tasks/functional/client/epic_data_input/requirements.md` | Functional |
| 9 | `requirements_tasks/functional/therapist/epic_plan_management/requirements.md` | Functional |
| 10 | `requirements_tasks/functional/shared/epic_evaluation/plan_evaluation_view/requirements.md` | Functional |
| 11 | `requirements_tasks/functional/shared/epic_security/requirements.md` | Functional |

#### Current Meta Information Patterns Found:

**Pattern A: Minimal Header (3/11 files)**
- Example: `testing_workflow/requirements.md`
- Only `# User Story` heading, no explicit metadata
- Inconsistent with other files

**Pattern B: Explicit Header Fields (6/11 files)**
- Example: `toast/requirements.md` (lines 1-6):
  ```markdown
  # Requirement: Toast Component

  - **Category:** UI/UX Design System > Components
  - **Status:** To Be Implemented
  - **Priority:** High
  ```
- Fields: Category, Status, Priority (text, not numeric)

**Pattern C: Epic Header (2/11 files)**
- Example: `epic_security/requirements.md` (lines 1-4):
  ```markdown
  # Requirement: Application and Data Security Setup (Placeholder)

  - **Epic:** Shared/Security
  - **Status:** TBD (To Be Determined)
  ```

#### Meta Information Currently Present:

| Field | Occurrence | Format | Notes |
|-------|------------|--------|-------|
| **Status** | 8/11 (73%) | Free text | Values: "To Be Implemented", "TBD", "Defined", "Detailed Definition" |
| **Category/Epic** | 6/11 (55%) | Free text | Redundant with folder path |
| **Priority** | 2/11 (18%) | Text ("High") | Not standardized |
| **Design Reference** | 1/11 (9%) | Text | In `plan_evaluation_view/requirements.md` |
| **Version History** | 11/11 (100%) | Footer section | Added during git migration |

#### Gaps and Inconsistencies:

1. **No Unique IDs**: No requirement has a unique identifier
2. **Inconsistent Status Values**: "To Be Implemented", "TBD", "Defined", "Detailed Definition" - no standardization
3. **Priority Rarely Used**: Only 2/11 files have priority, and it's just "High"
4. **No Dependencies Listed**: References exist in body text but no structured dependencies
5. **No Urgency/Impact**: Only textual priority where present
6. **Category/Epic Redundant**: Already encoded in folder path
7. **No Creation/Update Dates**: Only "Consolidation date" in version history

---

### 1.2 Goal.md Structure Analysis

I analyzed 8 goal.md files from different task types:

#### Files Examined:

| # | File Path | Type |
|---|-----------|------|
| 1 | `2026-01-04_impl_migrate-to-git-versioning (completed)/goal.md` | impl |
| 2 | `2026-01-04_explore_gemini-requirements-update (completed)/goal.md` | explore |
| 3 | `2026-01-04_impl_phase1-domain-data/goal.md` | impl |
| 4 | `2025-12-31_impl_fix_responsive_layout_tests (completed)/goal.md` | impl |
| 5 | `2025-10-20_explore_roo_rules_update/goal.md` | explore |
| 6 | `2026-01-02_explore_investigate-in-detail-navigation (completed)/goal.md` | explore |
| 7 | `2025-10-09_impl_implement_unified_ai_development_framework (completed)/goal.md` | impl |
| 8 | `2026-01-04_explore_migration-plan (completed)/goal.md` | explore |

#### Current Meta Information Patterns:

**New Format (Post-Migration - 7/8 files)**
From `2026-01-04_explore_gemini-requirements-update (completed)/goal.md` (lines 1-13):
```markdown
---
**Requirements Source (at task creation):**
- Original File: 2026-01-03_requirement.md
- Pre-Migration Commit: 1d3a2f9
- Task Date: 2026-01-04

To view original requirements:
```
git show 1d3a2f9:requirements_tasks/functional/shared/epic_evaluation/plan_evaluation_view/2026-01-03_requirement.md
```

Current requirements: ../requirements.md
---
```

**Old Format (Pre-Migration - 1/8 files)**
From `2026-01-04_impl_migrate-to-git-versioning (completed)/goal.md` (lines 1-7):
```markdown
# Goal: Implement Migration to Git-Versioned Requirements

**Created:** 2026-01-04
**Based on Requirements:** ../2026-01-04_requirement_git_versioning.md
**Plan Reference:** ../2026-01-04_explore_migration-plan/plans_and_protocols/2026-01-04_01_plan_migration.md
**Type:** Implementation
**Status:** Ready to start
```

#### Meta Information Currently Present:

| Field | Occurrence | Format | Notes |
|-------|------------|--------|-------|
| **Requirements Source** | 7/8 (88%) | Structured section | New format from git migration |
| **Created/Task Date** | 8/8 (100%) | YYYY-MM-DD | In different locations |
| **Type** | 2/8 (25%) | Text | "Implementation", "Exploration" |
| **Status** | 2/8 (25%) | Text | "Ready to start", "Planning", "Not Started" |
| **Parent Task** | 1/8 (13%) | Path reference | For sub-tasks |
| **Phase** | 1/8 (13%) | "1 of 3" | For phased implementations |
| **Based on Requirements** | 2/8 (25%) | Path reference | Old format |

#### Gaps and Inconsistencies:

1. **No Unique Task IDs**: Tasks are identified only by folder name
2. **Status Not Standardized**: "Ready to start", "Not Started", "Planning" - inconsistent
3. **No Priority/Urgency/Impact**: Completely absent
4. **No Effort Estimation**: Not documented
5. **No Dependencies Section**: Only mentioned in body text
6. **Type Already in Folder Name**: Redundant if added to metadata
7. **Completion Status Only in Folder Name**: `(completed)` suffix

---

## 2. USER'S PRIORITY SYSTEM ANALYSIS

The priority system proposed in goal.md is well-thought-out and comprehensive.

### 2.1 Strengths

1. **Two-Dimensional System**: Separates URGENCY (time factor) from IMPACT (value factor)
   - Urgency: "Why now?"
   - Impact: "What value does this create?"

2. **Clear Score Calculation**: `Score = (URGENCY * 10) + IMPACT`
   - Score 55 (U5, I5) = Highest priority
   - Score 00 (U0, I0) = Lowest priority
   - Enables clear sorting

3. **Reason Codes**: Each rating has a standardized code
   - Format: `[SKALA][WERT]-[CODE]` (e.g., `U5-BLOCK`, `I5-MVP`)
   - Self-documenting: Code explains the rating
   - Enables filtering by reason type

4. **Comprehensive Mapping Table**: The goal.md provides a mapping table for common task types
   - Requirements writing: U5/U4, I5
   - CI/CD fixes: U5, I5
   - Refactoring: U3-U5 depending on severity
   - Tests: U4, I4

5. **YAML Frontmatter Format**: Examples show clean, parseable format
   ```yaml
   id: TASK-DB-001
   type: impl
   urgency: 5
   urgency_reason: U5-BLOCK
   impact: 5
   impact_reason: I5-ENAB
   status: open
   ```

### 2.2 Adaptations Needed

1. **Project-Specific Reason Codes**: Some codes may need project-specific additions:
   - `U5-REG` (Regression): Critical bug introduced by recent change
   - `I4-SEC` (Security): Security-related but not legal compliance

2. **Missing Dimensions**: The system focuses on priority but doesn't cover:
   - **Effort/Complexity** (how hard is this?)
   - **Risk** (how likely is this to fail?)
   - **Dependencies** (what blocks this?)

3. **Status Values Not Defined**: The examples use `status: open` but don't define the full status lifecycle

4. **Requirement vs Task Priority**: Should requirements and tasks have the same or different priority systems?
   - Requirements: More stable, broader scope
   - Tasks: May change priority based on context

### 2.3 Recommendation

The priority system is well-suited for this project. I recommend:
1. Adopting it as-is for the URGENCY and IMPACT dimensions
2. Adding an EFFORT dimension (see Section 3)
3. Adding a STATUS dimension with standardized values
4. Keeping the same system for both requirements.md and goal.md

---

## 3. META INFORMATION DESIGN

### 3.1 Requirements.md Meta Information

#### Proposed YAML Frontmatter:

```yaml
---
id: REQ-[CATEGORY]-[NUMBER]
urgency: 0-5
urgency_reason: U[0-5]-[CODE]
impact: 0-5
impact_reason: I[0-5]-[CODE]
status: draft | defined | in_progress | implemented | deprecated
effort: XS | S | M | L | XL
stakeholder: client | therapist | developer | shared
created: YYYY-MM-DD
updated: YYYY-MM-DD
depends_on:
  - REQ-xxx
  - REQ-yyy
blocks:
  - REQ-zzz
---
```

#### Field Definitions:

| Field | Purpose | Format | Required | Default | Validation | Example |
|-------|---------|--------|----------|---------|------------|---------|
| `id` | Unique identifier | `REQ-[CAT]-[NUM]` | Yes | Generated | Regex pattern | `REQ-FUNC-042` |
| `urgency` | Time pressure | Integer 0-5 | Yes | 2 | 0 <= x <= 5 | `4` |
| `urgency_reason` | Why this urgency | `U[0-5]-[CODE]` | Yes | `U2-FREE` | Enum list | `U4-DEP` |
| `impact` | Value created | Integer 0-5 | Yes | 3 | 0 <= x <= 5 | `5` |
| `impact_reason` | Why this impact | `I[0-5]-[CODE]` | Yes | `I3-STD` | Enum list | `I5-MVP` |
| `status` | Current state | Enum | Yes | `draft` | Enum list | `defined` |
| `effort` | Size estimate | T-shirt size | Yes | `M` | Enum list | `L` |
| `stakeholder` | Primary user | Enum | Yes | `shared` | Enum list | `therapist` |
| `created` | Creation date | ISO date | Yes | Today | Date format | `2026-01-08` |
| `updated` | Last update | ISO date | No | - | Date format | `2026-01-08` |
| `depends_on` | Dependencies | Array of IDs | No | [] | ID format | `[REQ-ARCH-001]` |
| `blocks` | What this blocks | Array of IDs | No | [] | ID format | `[REQ-FUNC-015]` |

#### ID Generation Rules for Requirements:

- **Format**: `REQ-[CATEGORY]-[NUMBER]`
- **Categories**:
  - `FUNC` = functional
  - `NFUNC` = non-functional
  - `PROC` = process
- **Number**: 3-digit sequential number (001, 002, ...)
- **Generation**: By script or AI (see Section 4)
- **Examples**:
  - `REQ-FUNC-001` (first functional requirement)
  - `REQ-NFUNC-015` (15th non-functional requirement)
  - `REQ-PROC-003` (3rd process requirement)

#### Status Values for Requirements:

| Status | Description | Next States |
|--------|-------------|-------------|
| `draft` | Initial capture, incomplete | `defined`, `deprecated` |
| `defined` | Complete, ready for implementation | `in_progress`, `deprecated` |
| `in_progress` | Has active tasks | `implemented`, `deprecated` |
| `implemented` | All tasks completed | `deprecated` |
| `deprecated` | No longer relevant | - |

#### Effort Scale (T-Shirt Sizing):

| Size | Description | Typical Duration |
|------|-------------|------------------|
| `XS` | Trivial change | < 1 hour |
| `S` | Small feature | 1-4 hours |
| `M` | Medium feature | 1-2 days |
| `L` | Large feature | 3-5 days |
| `XL` | Epic-sized | > 1 week |

---

### 3.2 Goal.md Meta Information

#### Proposed YAML Frontmatter:

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
effort: XS | S | M | L | XL
estimated_hours: number (optional)
created: YYYY-MM-DD
completed: YYYY-MM-DD (when applicable)
depends_on:
  - TASK-xxx
blocked_by:
  - TASK-yyy
assigned_agent: string (optional, for AI tracking)
requirements_version:
  commit: xxxxxxx
  file: ../requirements.md
---
```

#### Field Definitions:

| Field | Purpose | Format | Required | Default | Validation | Example |
|-------|---------|--------|----------|---------|------------|---------|
| `task_id` | Unique identifier | `TASK-[REQ]-[NUM]` | Yes | Generated | Regex pattern | `TASK-FUNC-042-01` |
| `type` | Task type | Enum | Yes | - | `impl\|explore` | `impl` |
| `parent_requirement` | Link to requirement | REQ ID | Yes | - | ID format | `REQ-FUNC-042` |
| `parent_task` | For sub-tasks | TASK ID | No | - | ID format | `TASK-FUNC-042-01` |
| `urgency` | Time pressure | Integer 0-5 | Yes | Inherit | 0 <= x <= 5 | `4` |
| `urgency_reason` | Why this urgency | Code | Yes | Inherit | Enum list | `U4-DEP` |
| `impact` | Value created | Integer 0-5 | Yes | Inherit | 0 <= x <= 5 | `5` |
| `impact_reason` | Why this impact | Code | Yes | Inherit | Enum list | `I5-MVP` |
| `status` | Current state | Enum | Yes | `pending` | Enum list | `in_progress` |
| `effort` | Size estimate | T-shirt size | Yes | `M` | Enum list | `S` |
| `estimated_hours` | Time estimate | Number | No | - | > 0 | `4` |
| `created` | Creation date | ISO date | Yes | Today | Date format | `2026-01-08` |
| `completed` | Completion date | ISO date | No | - | Date format | `2026-01-10` |
| `depends_on` | Task dependencies | Array of IDs | No | [] | ID format | `[TASK-FUNC-041-01]` |
| `blocked_by` | Blockers | Array of IDs | No | [] | ID format | `[]` |
| `assigned_agent` | AI agent tracking | String | No | - | Free text | `opus-4.5` |
| `requirements_version` | Requirements snapshot | Object | Yes | - | Object | See below |

#### ID Generation Rules for Tasks:

- **Format**: `TASK-[REQU_ID]-[NUMBER]`
- **REQU_ID**: The ID of the parent requirement (without REQ- prefix)
- **Number**: 2-digit sequential number (01, 02, ...)
- **Generation**: By AI during setup-task skill
- **Examples**:
  - `TASK-FUNC-042-01` (first task for REQ-FUNC-042)
  - `TASK-FUNC-042-02` (second task for same requirement)
  - `TASK-FUNC-042-01-01` (sub-task of TASK-FUNC-042-01)

#### Status Values for Tasks:

| Status | Description | Next States |
|--------|-------------|-------------|
| `pending` | Created, not started | `ready`, `cancelled` |
| `ready` | Dependencies met, can start | `in_progress`, `blocked` |
| `in_progress` | Currently being worked on | `review`, `blocked`, `completed` |
| `blocked` | Waiting on something | `ready`, `cancelled` |
| `review` | Awaiting user review | `completed`, `in_progress` |
| `completed` | Done and verified | - |
| `cancelled` | No longer needed | - |

#### Priority Inheritance:

Tasks can inherit priority from their parent requirement:
- Default: Inherit urgency and impact from requirement
- Override: Task can have different priority if justified
- Example: Bug fix task may have higher urgency than the overall requirement

---

### 3.3 Format Decision: YAML Frontmatter

**Recommendation**: Use **YAML Frontmatter** (as shown in goal.md examples)

**Justification**:

| Criterion | YAML | Markdown Table | JSON |
|-----------|------|----------------|------|
| **Readability** | Excellent | Good | Poor |
| **Parseability** | Excellent | Poor | Excellent |
| **Markdown Compatible** | Yes | Yes | Partial |
| **Human Editable** | Yes | Yes | Error-prone |
| **Tool Support** | Widespread | Limited | Widespread |
| **Nested Data** | Yes | No | Yes |
| **Standard Practice** | Industry standard | Custom | Less common in MD |

**YAML Benefits**:
1. Already used in goal.md examples
2. Standard practice (Hugo, Jekyll, Obsidian, etc.)
3. Easy to parse with many libraries
4. Human-readable and editable
5. Supports arrays and nested objects

---

## 4. SCRIPT REQUIREMENTS

### 4.1 Useful Reports/Analytics

| Report | Purpose | Fields Needed |
|--------|---------|---------------|
| **Priority Dashboard** | Overview of all items by priority | urgency, impact, status |
| **High Priority Items** | Focus list | urgency >= 4 OR impact >= 5 |
| **Blocked Items** | Identify bottlenecks | blocked_by, status = blocked |
| **Effort by Requirement** | Planning | effort (sum of tasks) |
| **Priority Distribution** | Balance check | urgency, impact (histogram) |
| **Orphaned Tasks** | Cleanup | parent_requirement (missing) |
| **Status Overview** | Progress tracking | status (all items) |
| **Dependency Graph** | Visualize dependencies | depends_on, blocks |
| **Stale Items** | Items not updated | updated, status |
| **Agent Workload** | AI usage tracking | assigned_agent |

### 4.2 Query Examples

**Python/Script pseudocode:**

```python
# List all high-priority tasks (Score >= 45)
def high_priority_tasks(tasks):
    return [t for t in tasks if (t.urgency * 10 + t.impact) >= 45]

# Find tasks blocked by requirement X
def tasks_blocked_by(tasks, req_id):
    return [t for t in tasks if req_id in t.blocked_by]

# Calculate total effort for a requirement
def total_effort(requirement_id, tasks):
    effort_map = {'XS': 0.5, 'S': 2, 'M': 8, 'L': 24, 'XL': 80}
    return sum(effort_map[t.effort] for t in tasks if t.parent_requirement == requirement_id)

# Show priority distribution
def priority_distribution(items):
    return {
        'urgent_critical': len([i for i in items if i.urgency >= 4 and i.impact >= 4]),
        'urgent_normal': len([i for i in items if i.urgency >= 4 and i.impact < 4]),
        'normal': len([i for i in items if i.urgency < 4 and i.impact < 4]),
    }

# Find orphaned tasks (no valid requirement link)
def orphaned_tasks(tasks, requirements):
    req_ids = {r.id for r in requirements}
    return [t for t in tasks if t.parent_requirement not in req_ids]
```

### 4.3 Metadata Requirements for Scripts

To enable these queries, the following metadata is **essential**:

1. **Unique IDs** (for linking and referencing)
2. **Urgency + Impact** (for priority calculations)
3. **Status** (for filtering active/completed)
4. **Dependencies** (for graph analysis)
5. **Effort** (for planning/estimation)
6. **Parent links** (for requirement-task relationships)

---

## 5. MIGRATION STRATEGY

### 5.1 Scope Assessment

| Item Type | Count | Complexity |
|-----------|-------|------------|
| requirements.md | ~37 files | Medium (add frontmatter) |
| goal.md | ~49 files | Medium (add frontmatter, keep existing content) |

### 5.2 Migration Approach

**Recommendation**: Semi-automated migration

#### Phase 1: ID Generation (Automated)
1. Scan all requirements.md files
2. Assign IDs based on category and order
3. Create ID mapping file

#### Phase 2: Requirements Migration (Semi-automated)
1. For each requirements.md:
   - Read existing content
   - Analyze for implicit metadata (Status, Priority mentions)
   - Generate YAML frontmatter with defaults
   - User reviews and adjusts priority/effort

#### Phase 3: Tasks Migration (Semi-automated)
1. For each goal.md:
   - Keep existing content (requirements version reference, etc.)
   - Add task_id based on parent requirement
   - Inherit priority from requirement (or prompt user)
   - Add status based on folder name (completed -> completed)

### 5.3 Migration Script Outline

```pseudocode
function migrate_requirements():
    requirements = find_all("requirements_tasks/**/requirements.md")
    id_counter = {FUNC: 0, NFUNC: 0, PROC: 0}

    for req in requirements:
        category = detect_category(req.path)
        id_counter[category] += 1
        id = f"REQ-{category}-{id_counter[category]:03d}"

        frontmatter = {
            id: id,
            urgency: 2,  # default
            urgency_reason: "U2-FREE",
            impact: 3,  # default
            impact_reason: "I3-STD",
            status: detect_status(req.content) or "defined",
            effort: "M",  # default
            stakeholder: detect_stakeholder(req.path),
            created: detect_date(req) or today(),
            depends_on: [],
            blocks: []
        }

        write_yaml_frontmatter(req, frontmatter)
        save_id_mapping(req.path, id)

function migrate_tasks():
    tasks = find_all("requirements_tasks/**/tasks/**/goal.md")
    id_mapping = load_id_mapping()

    for task in tasks:
        req_path = find_parent_requirement(task.path)
        req_id = id_mapping[req_path]
        task_num = count_tasks_for_requirement(req_id) + 1
        task_id = f"TASK-{req_id.replace('REQ-', '')}-{task_num:02d}"

        folder_name = get_folder_name(task.path)
        is_completed = "(completed)" in folder_name
        task_type = "impl" if "_impl_" in folder_name else "explore"

        frontmatter = {
            task_id: task_id,
            type: task_type,
            parent_requirement: req_id,
            urgency: get_from_requirement(req_id, 'urgency'),
            urgency_reason: get_from_requirement(req_id, 'urgency_reason'),
            impact: get_from_requirement(req_id, 'impact'),
            impact_reason: get_from_requirement(req_id, 'impact_reason'),
            status: "completed" if is_completed else "pending",
            effort: "M",  # default
            created: parse_date_from_folder(folder_name),
            depends_on: [],
            blocked_by: [],
            requirements_version: extract_existing_version_block(task.content)
        }

        insert_yaml_frontmatter(task, frontmatter)
```

### 5.4 Migration Task Scope

**Estimated Effort**: M-L (2-3 days)

Tasks:
1. Create migration script (Python or Dart)
2. Run on requirements.md files (with user review)
3. Run on goal.md files (with user review)
4. Update setup-task skill with new template
5. Update CLAUDE.md/doc if needed
6. Test priority queries

---

## 6. CONCRETE PROPOSAL

### 6.1 Requirements.md Template

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
updated: 2026-01-08
depends_on: []
blocks: []
---

# Requirement: [Descriptive Name]

## 1. User Story

As a [stakeholder], I want to [action], so that [benefit].

## 2. Specification

[Detailed specification...]

## 3. Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## 4. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-xxx | defined | Needs X first |

## 5. References

- Related: [path/to/related/requirements.md]

---
## Version History
Consolidated from: [original files]
Consolidation date: YYYY-MM-DD
Pre-migration commit: [hash]
```

### 6.2 Goal.md Template

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
depends_on: []
blocked_by: []
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

### 6.3 Complete Field Definitions

#### Urgency Reason Codes (from goal.md, preserved)

| Code | Value | Meaning |
|------|-------|---------|
| `U5-BLOCK` | 5 | Technical Blocker |
| `U5-PROC` | 5 | Process Blocker |
| `U5-RISK` | 5 | Critical Risk |
| `U5-GAP` | 5 | Exploration Gap |
| `U4-DEP` | 4 | Dependency |
| `U4-FAIL` | 4 | Fail Fast |
| `U4-TIME` | 4 | Hard Deadline |
| `U3-SPRINT` | 3 | Sprint Focus |
| `U3-CTX` | 3 | Context Synergy |
| `U3-FIX` | 3 | Medium Fix |
| `U2-FREE` | 2 | Decoupled |
| `U2-WAIT` | 2 | Waiting |
| `U2-PERF` | 2 | Non-Critical Perf |
| `U1-COSM` | 1 | Cosmetic |
| `U1-REFA` | 1 | Micro Refactor |
| `U1-FILL` | 1 | Filler |
| `U0-HOLD` | 0 | On Hold |

#### Impact Reason Codes (from goal.md, preserved)

| Code | Value | Meaning |
|------|-------|---------|
| `I5-MVP` | 5 | MVP Core |
| `I5-STOP` | 5 | Showstopper |
| `I5-ENAB` | 5 | Massive Enabler |
| `I5-LEGAL` | 5 | Compliance |
| `I4-USP` | 4 | Key Feature |
| `I4-PAIN` | 4 | Pain Relief |
| `I4-DEBT` | 4 | Debt Reduction |
| `I4-DATA` | 4 | Data Integrity |
| `I3-STD` | 3 | Standard Expected |
| `I3-PROC` | 3 | Process Optimization |
| `I3-UX` | 3 | UX Flow |
| `I2-JOY` | 2 | Delighter |
| `I2-EDGE` | 2 | Edge Case |
| `I2-TXT` | 2 | Wording/Polish |
| `I1-INV` | 1 | Invisible |
| `I1-PIX` | 1 | Pixel Polish |
| `I0-NONE` | 0 | No Value |

### 6.4 ID Generation Rules Summary

#### Requirements:
- **Generator**: Script (during migration) or AI (for new requirements)
- **Format**: `REQ-[FUNC|NFUNC|PROC]-[NNN]`
- **Uniqueness**: Global across project
- **Example**: `REQ-FUNC-042`

#### Tasks:
- **Generator**: AI (setup-task skill)
- **Format**: `TASK-[REQ-ID-without-prefix]-[NN]`
- **Uniqueness**: Global across project
- **Example**: `TASK-FUNC-042-01`

#### Sub-Tasks:
- **Generator**: AI (when creating sub-tasks)
- **Format**: `TASK-[PARENT-TASK-ID]-[NN]`
- **Example**: `TASK-FUNC-042-01-01`

---

## 7. RECOMMENDATIONS

### 7.1 Immediate Actions

1. **Adopt the priority system** from goal.md as-is (urgency + impact + reason codes)
2. **Add YAML frontmatter** to requirements.md and goal.md templates
3. **Create unique IDs** for all requirements and tasks
4. **Standardize status values** across all files

### 7.2 Implementation Approach

1. **Create implementation task** for migration
2. **Start with requirements.md** (fewer files, simpler)
3. **Then migrate goal.md** files
4. **Update setup-task skill** to generate new format
5. **Create simple query script** (Python or Dart)

### 7.3 Fields to Add (Summary)

**For requirements.md (new fields):**
- `id` (unique identifier)
- `urgency` + `urgency_reason` (from Gemini system)
- `impact` + `impact_reason` (from Gemini system)
- `effort` (T-shirt sizing)
- `stakeholder` (who benefits)
- `created` / `updated` (dates)
- `depends_on` / `blocks` (dependencies)

**For goal.md (new fields):**
- `task_id` (unique identifier)
- `parent_requirement` (link to requirement)
- `urgency` + `urgency_reason` (inherit or override)
- `impact` + `impact_reason` (inherit or override)
- `effort` (T-shirt sizing)
- `completed` (date when done)
- `depends_on` / `blocked_by` (task dependencies)
- `assigned_agent` (optional, for AI tracking)

### 7.4 What NOT to Add

1. **Category/Epic in metadata**: Already encoded in folder path (redundant)
2. **Type in goal.md metadata**: Already in folder name (`_impl_` or `_explore_`)
3. **Completion status in goal.md metadata**: Already in folder name (`(completed)`)
4. **Full requirements content**: Keep only version reference (git hash)

---

## 8. FILE REFERENCES

### Requirements.md Files Analyzed:
- `requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md` (lines 1-145)
- `requirements_tasks/process/AI_rules/workflows/orchestrator_workflow/requirements.md` (lines 1-275)
- `requirements_tasks/process/AI_rules/workflows/testing_workflow/requirements.md` (lines 1-34)
- `requirements_tasks/non-functional/architecture/requirements.md` (lines 1-52)
- `requirements_tasks/non-functional/ui_ux_design_system/components/toast/requirements.md` (lines 1-105)
- `requirements_tasks/non-functional/ui_ux_design_system/components/skeleton/requirements.md` (lines 1-99)
- `requirements_tasks/non-functional/ui_ux_design_system/navigation_patterns/responsive_layout_master_detail/requirements.md` (lines 1-134)
- `requirements_tasks/functional/client/epic_data_input/requirements.md` (lines 1-28)
- `requirements_tasks/functional/therapist/epic_plan_management/requirements.md` (lines 1-468)
- `requirements_tasks/functional/shared/epic_evaluation/plan_evaluation_view/requirements.md` (lines 1-182)
- `requirements_tasks/functional/shared/epic_security/requirements.md` (lines 1-71)

### Goal.md Files Analyzed:
- `requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/tasks/2026-01-04_impl_migrate-to-git-versioning (completed)/goal.md` (lines 1-114)
- `requirements_tasks/functional/shared/epic_evaluation/plan_evaluation_view/tasks/2026-01-04_explore_gemini-requirements-update (completed)/goal.md` (lines 1-35)
- `requirements_tasks/functional/shared/epic_evaluation/plan_evaluation_view/tasks/2026-01-04_impl_phase1-domain-data/goal.md` (lines 1-141)
- `requirements_tasks/non-functional/ui_ux_design_system/navigation_patterns/responsive_layout_master_detail/tasks/2025-12-31_impl_fix_responsive_layout_tests (completed)/goal.md` (lines 1-111)
- `requirements_tasks/process/AI_rules/workflows/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/goal.md` (lines 1-27)
- `requirements_tasks/non-functional/ui_ux_design_system/navigation_patterns/in_detail_navigation/tasks/2026-01-02_explore_investigate-in-detail-navigation (completed)/goal.md` (lines 1-114)
- `requirements_tasks/process/AI_rules/workflows/orchestrator_workflow/tasks/2025-10-09_impl_implement_unified_ai_development_framework (completed)/goal.md` (lines 1-33)
- `requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/tasks/2026-01-04_explore_migration-plan (completed)/goal.md` (lines 1-130)

---

This investigation provides a comprehensive foundation for implementing standardized meta information across all requirements and tasks in the project. The priority system from Gemini is well-designed and should be adopted with minimal modifications. The main additions are unique IDs, effort estimation, and standardized status values.
