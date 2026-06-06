# Investigation Protocol: Bidirectional Linking Between Requirements and Tasks

**Agent**: Explore (Opus)
**Agent ID**: ac022a4
**Date**: 2026-01-08

---

## Investigation Report: Bidirectional Linking Mechanism for Requirements and Tasks

### Executive Summary

This investigation analyzes how to create a robust bidirectional linking mechanism between requirements and tasks, enabling coverage tracking at a granular level. The proposed solution uses a hybrid system with Acceptance Criteria IDs and Section IDs, combined with computed-at-query-time coverage reporting.

---

### 1. Requirement Structure Analysis

I analyzed 11+ requirements.md files across the project and identified the following structural patterns:

**Common Structure Elements:**
- **User Story** (Section 1): Goal statement in "As a... I want... so that..." format
- **Overview/Goal** (Section 2): Detailed description
- **Numbered Sections** (3-8+): Design, Behavior, Technical, etc.
- **Acceptance Criteria** (typically Section 10): Checkbox list format
- **Dependencies** (usually last before Version History)
- **Version History** (footer): Consolidation metadata

**Key Observations:**

| File | Has Acceptance Criteria | Format | Section Count |
|------|-------------------------|--------|---------------|
| `plan_evaluation_view/requirements.md` | Yes (Section 10) | 12 checkboxes | 11 sections |
| `responsive_layout_master_detail/requirements.md` | No explicit | Table-based | 4 sections |
| `toast/requirements.md` | Yes (Section 8) | 7 checkboxes | 10 sections |
| `skeleton/requirements.md` | Yes (Section 6) | 6 checkboxes | 9 sections |

**Patterns Found:**
- **Acceptance Criteria**: ~60% of requirements have explicit checkboxes
- **Numbered Sections**: All use markdown heading sections (## 1., ## 2., etc.)
- **Dependencies Table**: Most complex requirements have structured dependencies
- **No Unique IDs**: No requirement sections have explicit identifiers

---

### 2. Linking Granularity Evaluation

**Option A: Whole Requirement**
```yaml
covers:
  requirement: REQ-FUNC-042
```
- **Pros**: Simple, low maintenance
- **Cons**: Not granular enough - one large task covers everything, or multiple tasks with no clear scope

**Option B: Acceptance Criteria**
```yaml
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03]
```
- **Pros**: Already present in ~60% of requirements; clear success metrics
- **Cons**: Not all requirements have them; AC may not cover all aspects

**Option C: Named Sections**
```yaml
covers:
  sections: [visual-design, behavior, zoom-controls]
```
- **Pros**: Flexible; works with existing heading structure
- **Cons**: Section names must be standardized; refactoring breaks links

**Option D: Arbitrary Text Ranges**
```yaml
covers:
  text_ranges:
    - start: "## 4. Chart Visualization"
      end: "## 5. Detail Interaction"
```
- **Pros**: Most precise
- **Cons**: Extremely fragile; any edit breaks links

**Recommendation**: **Option B (Acceptance Criteria) + Option C (Sections) Hybrid**

Rationale:
1. Acceptance Criteria already exist and define success conditions
2. Sections provide broader scope for complex areas
3. Both can be identified with stable IDs that survive minor edits

---

### 3. Metadata Design Proposal

#### In requirements.md:

```yaml
---
id: REQ-FUNC-042
# ... existing fields from previous investigation ...
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Displays questionnaire results over time"
    - id: AC-02
      text: "Simple Mode shows basic charts with date navigation"
    - id: AC-03
      text: "Advanced Mode adds tabs, filters, zoom controls"
    # ... etc ...
  sections:
    - id: SEC-01
      name: "Chart Visualization Logic"
      heading: "## 4. Chart Visualization Logic"
    - id: SEC-02
      name: "Detail Interaction & Editing"
      heading: "## 5. Detail Interaction"
---
```

**Key Design Decisions:**
1. **IDs are stable**: AC-01, SEC-01 never change even if text changes
2. **Text is descriptive**: Helps human readability
3. **Dual system**: Both AC and sections can be tracked
4. **No automatic extraction**: IDs must be manually assigned

#### In goal.md:

```yaml
---
task_id: TASK-FUNC-042-01
parent_requirement: REQ-FUNC-042
# ... existing fields ...
covers:
  acceptance_criteria: [AC-01, AC-02]
  sections: [SEC-01]
scope_description: "Phase 1: Data Interface - defines input interface and shortLabel field"
---
```

**Design Rationale:**
- `covers` is explicit list of what this task implements
- `scope_description` provides human-readable summary
- Both types (AC and sections) can coexist

---

### 4. Maintenance Burden Analysis

**Who Updates?**

| Update Event | Actor | Trigger |
|--------------|-------|---------|
| Initial AC/Section IDs | AI (setup-task skill) | Requirement creation |
| Task linking | AI (setup-task skill) | Task creation |
| Status updates | Script (automated) | Task completion |
| Requirement restructure | AI + Human review | Requirement change |

**When Updated?**

| Phase | What Changes |
|-------|--------------|
| Requirement Creation | Assign IDs to AC and sections |
| Task Creation | Link task to AC/sections via `covers:` |
| Task Completion | Script updates coverage status in requirement |
| Requirement Change | Human must verify existing task links still valid |

**Synchronization Strategy:**

**Option 1: Computed at Query Time (Recommended)**
- Requirements only store `trackable_items` with IDs
- Tasks store `covers: [AC-01, AC-02]`
- Coverage is computed by script scanning all tasks

```python
def compute_coverage(requirement_id):
    tasks = find_tasks_for_requirement(requirement_id)
    coverage = {}
    for task in tasks:
        for ac in task.covers.acceptance_criteria:
            if ac not in coverage:
                coverage[ac] = {'status': 'not_started', 'tasks': []}
            coverage[ac]['tasks'].append(task.id)
            if task.status == 'completed':
                coverage[ac]['status'] = 'implemented'
            elif task.status == 'in_progress' and coverage[ac]['status'] != 'implemented':
                coverage[ac]['status'] = 'in_progress'
            elif task.status == 'pending' and coverage[ac]['status'] == 'not_started':
                coverage[ac]['status'] = 'planned'
    return coverage
```

**Option 2: Stored in Requirement (Higher Maintenance)**
- Requires updating requirement file when task status changes
- Creates merge conflicts
- Not recommended

**Recommendation**: **Option 1 - Compute at query time**

---

### 5. Query/Report Requirements

**Essential Queries:**

```python
# 1. Requirement Coverage Report
def requirement_coverage(req_id: str) -> CoverageReport:
    """
    Returns:
    - total_items: int
    - implemented: int (covered by completed tasks)
    - in_progress: int (covered by in_progress tasks)
    - planned: int (covered by pending tasks)
    - not_started: int (no task coverage)
    - coverage_percentage: float
    - details: dict[item_id, {status, tasks}]
    """

# 2. Find Gaps
def uncovered_items(req_id: str) -> List[TrackableItem]:
    """Returns acceptance criteria/sections with no task coverage"""

# 3. Task Scope
def task_scope(task_id: str) -> TaskScope:
    """Returns which AC/sections this task covers"""

# 4. Item History
def item_implementation_history(req_id: str, item_id: str) -> List[Task]:
    """Returns all tasks that covered a specific AC/section"""

# 5. Coverage Matrix
def coverage_matrix() -> DataFrame:
    """
    Returns grid:
    Requirement | Total AC | Implemented | In Progress | Planned | Gaps
    REQ-001     | 12       | 8           | 2           | 1       | 1
    REQ-002     | 5        | 5           | 0           | 0       | 0
    """
```

---

### 6. Real-World Examples Analysis

#### Example 1: PlanEvaluationView (5 tasks, 12 acceptance criteria)

**Current State:**
- 5 tasks in `tasks/` folder
- 1 explore task (requirements update)
- 1 parent impl task (orchestrating)
- 3 phase subtasks (actual implementation)

**How linking would work:**

```yaml
# In requirements.md
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Displays questionnaire results over time"
    - id: AC-02
      text: "Simple Mode shows basic charts with date navigation"
    - id: AC-03
      text: "Advanced Mode adds tabs, filters, zoom controls"
    - id: AC-04
      text: "Charts support stacked scales"
    - id: AC-05
      text: "Data points rendered as capsules with whiskers"
    - id: AC-06
      text: "Tapping capsule opens LeafPopout"
    - id: AC-07
      text: "Edit button opens fullscreen edit dialog"
    - id: AC-08
      text: "Time Range modal supports consecutive/weekday patterns"
    - id: AC-09
      text: "Text View tab shows chronological log"
    - id: AC-10
      text: "Multi-day comparison uses distinct line styles"
    - id: AC-11
      text: "Follows App Theme"
    - id: AC-12
      text: "Responsive layout"

# In phase1-domain-data/goal.md
covers:
  acceptance_criteria: [AC-04]  # Domain work enables stacked scales
  sections: [SEC-DOMAIN]

# In phase2-simple-mode-chart/goal.md
covers:
  acceptance_criteria: [AC-01, AC-02, AC-05, AC-11, AC-12]

# In phase3-advanced-features/goal.md
covers:
  acceptance_criteria: [AC-03, AC-06, AC-07, AC-08, AC-09, AC-10]
```

**Coverage Report Output:**
```
REQ-FUNC-042: PlanEvaluationView
Total: 12 AC | Implemented: 0 | In Progress: 0 | Planned: 12 | Gaps: 0
Coverage: 100% planned

AC-01: planned (phase2-simple-mode-chart)
AC-02: planned (phase2-simple-mode-chart)
AC-03: planned (phase3-advanced-features)
...
```

#### Example 2: Responsive Layout Master-Detail (8 tasks, table-based requirements)

**Challenge:** No explicit acceptance criteria checkboxes

**Solution:** Use sections instead:

```yaml
trackable_items:
  sections:
    - id: SEC-FOUNDATION
      name: "Foundational Elements"
      heading: "### 1. Foundational Elements"
    - id: SEC-MASTER-DETAIL
      name: "Master-Detail Flow"
      heading: "#### 2.1. Master-Detail Flow"
    - id: SEC-NESTED
      name: "Nested Master-Detail"
      heading: "#### 2.2. Nested Master-Detail Flow"
    - id: SEC-EDGE-CASES
      name: "Edge Cases"
      heading: "### 3. Edge Cases and Conditions"
```

---

### 7. Alternative Approaches Comparison

| Approach | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| **A: Explicit Linking (proposed)** | Clear traceability, queryable | Requires ID assignment, some maintenance | **RECOMMENDED** |
| **B: Status Inference** | Zero maintenance | Cannot track partial coverage | Not recommended |
| **C: Separate Tracking File** | Doesn't touch requirement file | Another file to maintain, can get out of sync | Partially useful for reports |
| **D: Inline Comments** | Low overhead | Not queryable, gets verbose | Not recommended |
| **E: Script-Based Analysis** | Fully automated | Cannot handle semantic meaning | Supplement only |

**Hybrid Recommendation:**
- Use **Approach A** (Explicit Linking) for the source of truth
- Use **Approach E** (Script Analysis) to generate reports
- Optionally generate **Approach C** (Separate File) as cached report

---

### 8. Concrete Proposal

#### 8.1 Chosen Linking Mechanism

**Dual Tracking System:**
1. **Primary: Acceptance Criteria IDs** (for requirements that have AC)
2. **Secondary: Section IDs** (for requirements without AC, or for broader scope)

**Justification:**
- Acceptance Criteria are already widely used (~60% of requirements)
- They represent testable success conditions
- Sections cover remaining cases and provide broader granularity

#### 8.2 Metadata Structure

**requirements.md:**
```yaml
---
id: REQ-FUNC-042
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-MVP
status: in_progress
effort: XL
created: 2026-01-03
updated: 2026-01-08
depends_on: []
# NEW: Trackable items for coverage tracking
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Short description of AC"
    - id: AC-02
      text: "Another AC"
  sections:
    - id: SEC-01
      name: "Section Name"
      heading: "## 4. Section Heading"
---
```

**goal.md:**
```yaml
---
task_id: TASK-FUNC-042-01
type: impl
parent_requirement: REQ-FUNC-042
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-MVP
status: pending
effort: M
created: 2026-01-08
# NEW: What this task covers
covers:
  acceptance_criteria: [AC-01, AC-02, AC-05]
  sections: [SEC-01]
scope_description: "Brief human-readable scope summary"
requirements_version:
  commit: abc1234
  file: ../requirements.md
---
```

#### 8.3 Maintenance Workflow

| Event | Who | Action |
|-------|-----|--------|
| New requirement | AI | Assign IDs to all AC items and major sections |
| New task | AI (setup-task) | Add `covers:` field with relevant AC/section IDs |
| Task completion | Script | Recompute coverage (no file changes needed) |
| Requirement restructure | AI + User | Verify task `covers:` fields still valid |
| Generate report | Script | Scan all tasks, compute coverage matrix |

#### 8.4 Validation Rules

```python
# Rule 1: Every AC/section ID in covers must exist in requirement
def validate_covers(task):
    req = load_requirement(task.parent_requirement)
    valid_ids = {item.id for item in req.trackable_items.acceptance_criteria}
    valid_ids |= {item.id for item in req.trackable_items.sections}
    for covered_id in task.covers.acceptance_criteria + task.covers.sections:
        if covered_id not in valid_ids:
            raise ValidationError(f"Unknown ID: {covered_id}")

# Rule 2: Completed tasks should cover something
def validate_completed_task(task):
    if task.status == 'completed' and not task.covers:
        warn(f"Task {task.id} completed but covers nothing")

# Rule 3: AC should have coverage (warning only)
def check_uncovered_items(req):
    coverage = compute_coverage(req.id)
    for ac in req.trackable_items.acceptance_criteria:
        if ac.id not in coverage:
            warn(f"AC {ac.id} has no task coverage")
```

#### 8.5 Query Capabilities

| Query | Input | Output |
|-------|-------|--------|
| `coverage_report(REQ-XXX)` | Requirement ID | Coverage statistics + per-item status |
| `uncovered_items(REQ-XXX)` | Requirement ID | List of AC/sections with no tasks |
| `task_scope(TASK-XXX)` | Task ID | List of covered AC/sections |
| `find_tasks_for_item(REQ-XXX, AC-01)` | Requirement + Item ID | All tasks covering that item |
| `coverage_matrix()` | None | All requirements with coverage % |

#### 8.6 Complete Example

**requirements.md (plan_evaluation_view):**
```yaml
---
id: REQ-FUNC-042
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-MVP
status: defined
effort: XL
stakeholder: shared
created: 2026-01-03
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Displays questionnaire results over time in timeline chart format"
    - id: AC-02
      text: "Simple Mode shows basic charts with date navigation"
    - id: AC-03
      text: "Advanced Mode adds tabs, filters, zoom controls, and chart management"
    - id: AC-04
      text: "Charts support stacked scales for multiple question types"
    - id: AC-05
      text: "Data points rendered as capsules with whiskers for duration events"
    - id: AC-06
      text: "Tapping capsule opens LeafPopout with detail view"
    - id: AC-07
      text: "Edit button in popout opens fullscreen edit dialog"
    - id: AC-08
      text: "Time Range modal supports consecutive days and weekday patterns"
    - id: AC-09
      text: "Text View tab shows chronological log of data"
    - id: AC-10
      text: "Multi-day comparison uses distinct line styles for accessibility"
    - id: AC-11
      text: "Follows App Theme (Tree Theme / Simple Mode)"
    - id: AC-12
      text: "Responsive layout for different screen sizes"
  sections:
    - id: SEC-DOMAIN
      name: "Domain & Data Interface"
      heading: "## 2. Global Behavior & Data Model"
    - id: SEC-CHART
      name: "Chart Visualization"
      heading: "## 4. Chart Visualization Logic"
    - id: SEC-INTERACTION
      name: "Detail Interaction"
      heading: "## 5. Detail Interaction & Editing"
---
```

**goal.md (phase2-simple-mode-chart):**
```yaml
---
task_id: TASK-FUNC-042-02
type: impl
parent_requirement: REQ-FUNC-042
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-MVP
status: pending
effort: L
created: 2026-01-04
covers:
  acceptance_criteria: [AC-01, AC-02, AC-04, AC-05, AC-11, AC-12]
  sections: [SEC-CHART]
scope_description: "Core Simple Mode UI with timeline chart visualization and date navigation"
requirements_version:
  commit: 1d3a2f9
  file: ../requirements.md
---
```

**Coverage Report Output:**
```
=== REQ-FUNC-042: PlanEvaluationView ===
Coverage: 12/12 AC planned (100%)
Status: defined -> in_progress (when tasks start)

Acceptance Criteria:
  [planned] AC-01: Displays questionnaire results... (TASK-FUNC-042-02)
  [planned] AC-02: Simple Mode shows basic charts... (TASK-FUNC-042-02)
  [planned] AC-03: Advanced Mode adds tabs... (TASK-FUNC-042-03)
  [planned] AC-04: Charts support stacked scales... (TASK-FUNC-042-01, TASK-FUNC-042-02)
  [planned] AC-05: Data points rendered as capsules... (TASK-FUNC-042-02)
  [planned] AC-06: Tapping capsule opens LeafPopout... (TASK-FUNC-042-03)
  [planned] AC-07: Edit button opens fullscreen... (TASK-FUNC-042-03)
  [planned] AC-08: Time Range modal... (TASK-FUNC-042-03)
  [planned] AC-09: Text View tab... (TASK-FUNC-042-03)
  [planned] AC-10: Multi-day comparison... (TASK-FUNC-042-03)
  [planned] AC-11: Follows App Theme... (TASK-FUNC-042-02)
  [planned] AC-12: Responsive layout... (TASK-FUNC-042-02)

Sections:
  [planned] SEC-DOMAIN: Domain & Data Interface (TASK-FUNC-042-01)
  [planned] SEC-CHART: Chart Visualization (TASK-FUNC-042-02)
  [planned] SEC-INTERACTION: Detail Interaction (TASK-FUNC-042-03)
```

#### 8.7 Migration Impact

**For Existing Requirements:**
1. Add `trackable_items` section with IDs for existing AC items
2. Can be done incrementally (only when editing a requirement)
3. Estimated effort: ~30 minutes per requirement

**For Existing Tasks:**
1. Add `covers:` field to goal.md
2. Map to newly created AC/section IDs
3. Estimated effort: ~10 minutes per task

**Script Assistance:**
- Script can auto-extract AC text from markdown checkboxes
- Script can suggest IDs (AC-01, AC-02, ...)
- Human review required for section mapping

---

### 9. Recommendations

1. **Adopt the hybrid AC + Sections approach** for maximum coverage
2. **Compute coverage at query time** (do not store in requirement file)
3. **Make IDs immutable** - once assigned, never change
4. **Start with new requirements** - add to existing files gradually
5. **Build a simple Python/Dart script** to:
   - Validate `covers:` references
   - Generate coverage reports
   - Detect uncovered items
6. **Update setup-task skill** to auto-assign IDs and prompt for covers
7. **Document the convention** in `requirements_and_tasks/requirements.md`

**Priority of Implementation:**
| Phase | Task | Effort |
|-------|------|--------|
| 1 | Update requirements.md with trackable_items schema | S |
| 2 | Update goal.md template with covers field | S |
| 3 | Build coverage report script | M |
| 4 | Update setup-task skill | M |
| 5 | Migrate existing files (incremental) | L |

---

This completes the investigation into bidirectional linking between requirements and tasks. The proposed system balances granularity with maintainability and leverages existing structures (acceptance criteria) while providing flexibility (sections) for varying requirement formats.
