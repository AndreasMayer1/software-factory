---
id: REQ-PROC-011
urgency: 3
urgency_reason: U3-TECH
impact: 2
impact_reason: I2-TECH
status: implemented
effort: S
stakeholder: developer
created: 2026-01-19
updated: 2026-01-23
after: []
blocks:
  - REQ-PROC-012  # Dr. Sarah persona depends on this (symmetric)
  - REQ-PROC-013  # Max client persona depends on this (symmetric)
  - REQ-PROC-014  # Sarah self-user persona depends on this (symmetric)
  - REQ-PROC-015  # System maintenance persona depends on this (symmetric)
  - REQ-PROC-016  # David persona depends on this (symmetric)
  - REQ-PROC-017  # Dr. med. Turan persona depends on this (symmetric)
  - REQ-PROC-018  # Elias persona depends on this (symmetric)
  - REQ-PROC-019  # Hanna persona depends on this (symmetric)
  - REQ-PROC-020  # Jana persona depends on this (symmetric)
  - REQ-PROC-021  # Lisa persona depends on this (symmetric)
  - REQ-PROC-022  # Michael persona depends on this (symmetric)
  - REQ-PROC-023  # Nina persona depends on this (symmetric)
  - REQ-PROC-024  # Prof. Dr. Weber persona depends on this (symmetric)
  - REQ-PROC-025  # Sophie persona depends on this (symmetric)
  - REQ-PROC-028  # Lena persona depends on this (symmetric)
trackable_items:
  sections:
    - id: SEC-01
      name: "Deprecation Strategy"
      heading: "## Deprecation Strategy"
    - id: SEC-02
      name: "Preservation Guidelines"
      heading: "## Preservation Guidelines"
    - id: SEC-03
      name: "Obsolete Tasks Handling"
      heading: "## Obsolete Tasks Handling"
---

# Roo Code Deprecation and Archival

## Overview

As the project has transitioned from Roo Code to Claude Code, the existing Roo Code rules and configurations are now outdated. However, AI coding tools are still emerging and evolving, and we may need to switch tools again in the future. This requirement defines how to deprecate and archive Roo Code rules while preserving them for potential future adaptation.

## Problem Statement

Currently, we have:
- Outdated Roo Code rules in `.roo/` directory and `.clinerules` file
- 3 pending tasks focused on updating Roo rules (now irrelevant):
  - TASK-PROC-005-03: Explore Roo Rules Update (testing_workflow)
  - TASK-PROC-007-01: Explore Roo Rules Update (workflow_improvement_automation)
  - TASK-PROC-006-01: Explore Roo Rules Update (guideline_updates)

These rules represent valuable process knowledge but are no longer compatible with Claude Code workflows.

## Deprecation Strategy

### Current Roo Code Structure

The project contains extensive Roo Code configuration:

**Configuration Files (Root Level):**
- `.clinerules` (201 lines): Legacy project instructions for Roo Code
- `.roomodes` (138 lines): 6 custom mode definitions
- `.roo/` directory: 11 subdirectories with specialized rules
- `.roo-templates/` directory: 14 documentation templates

**Roo Rules Organization:**
- `rules-orchestrator/`: 7 files defining implementation workflow and testing orchestration
- `rules-architect/`: Interactive brainstorming workflow rules
- `rules-code/`: Code implementation and refactoring rules
- `rules-requirements-writer/`: Two-mode workflow (Implementation Detail + Explorative)
- `rules-architect-post-implementation/`: Post-implementation documentation rules
- Testing-specific rule sets: `rules-orchestrator-testing/`, `rules-orchestrator-testing-file/`, etc.

### Deprecation Options

**Option A: Archive Folder Approach** (RECOMMENDED)

Create `.roo_archive/` folder at project root containing:

1. **Move all Roo Code files**:
   - `.roo/` → `.roo_archive/roo/`
   - `.roo-templates/` → `.roo_archive/roo-templates/`
   - `.clinerules` → `.roo_archive/clinerules`
   - `.roomodes` → `.roo_archive/roomodes`

2. **Create DEPRECATED_README.md** at `.roo_archive/DEPRECATED_README.md`:
   ```markdown
   # Roo Code - DEPRECATED

   **Deprecated Date**: 2026-01-19
   **Reason**: Project migrated from Roo Code to Claude Code
   **Replaced By**: CLAUDE.md + .claude/ directory

   ## What This Was
   [Brief description of Roo Code setup]

   ## Why Deprecated
   [Explanation of Claude Code transition]

   ## How to Reactivate (If Needed)
   [Conceptual steps for reactivation]

   ## Migration Summary
   [What translated well, what changed, what was lost]

   See KNOWLEDGE_TRANSFER.md for valuable patterns to preserve.
   ```

3. **Create KNOWLEDGE_TRANSFER.md** at `.roo_archive/KNOWLEDGE_TRANSFER.md`:
   Document valuable process patterns independent of tool:
   - 3-Phase Implementation Workflow structure
   - Testing Orchestration Hierarchy pattern
   - Template-driven documentation approach
   - Flakiness Investigation Protocol
   - Scope Enforcement mechanisms
   - WHY comments for non-obvious code
   - Metrics Collection patterns

**Benefits**:
- Clean separation (archived files no longer clutter root)
- Clear visual signal (files in archive = deprecated)
- Complete preservation (nothing deleted)
- Easy to reference or restore if needed

**Option B: In-Place Deprecation**

Keep files in current locations but add deprecation markers:
- Add `DEPRECATED.md` in `.roo/` and `.roo-templates/`
- Prepend deprecation notice to `.clinerules` and `.roomodes`

**Drawbacks**: Files still appear "active", less clear signal

**Option C: Documentation-Only Approach**

Create single `ROO_CODE_DEPRECATION.md` at project root documenting the deprecation.

**Drawbacks**: Roo Code files remain active-looking, no physical separation

### Recommended Approach

**Use Option A (Archive Folder)** for these reasons:
1. Cleanest separation between active (Claude Code) and archived (Roo Code) tooling
2. Clear visual signal when browsing project root
3. Preserves everything for future reference
4. Follows migration pattern found in codebase (create → migrate → archive)
5. Easier to restore if needed (just move files back)

## Preservation Guidelines

### What to Preserve

The Roo Code setup contains valuable process knowledge that transcends any specific AI tool. When archiving, preserve these patterns in `KNOWLEDGE_TRANSFER.md`:

**1. 3-Phase Implementation Workflow**
- **Phase 1**: Analysis & Validation Loop (catch flawed assumptions early)
- **Phase 2**: Iterative Implementation Cycle (incremental progress with feedback)
- **Phase 3**: Final Integration Verification (ensure everything works together)
- **Source**: `.roo/rules-orchestrator/implementation_workflow.md:1-94`

**2. Testing Orchestration Hierarchy**
- Multi-level delegation pattern:
  - Outer Orchestrator → Testing Orchestrator → Test File Orchestrator → Test Part Orchestrator → Code subtasks
- Escalation policies for flakiness and blockers
- N-run probes for non-deterministic failures
- **Source**: `.roo/rules-orchestrator/orchestrator_testing_process.md:1-46`

**3. Template-Driven Documentation**
- Standardized templates for plans, protocols, blockers, metrics
- Consistent structure across all task documentation
- Metadata requirements (scope, objectives, constraints)
- **Source**: `.roo-templates/template_*.md` (14 templates)

**4. Scope Enforcement Mechanisms**
- Explicit "Scope of Work" definitions in plans
- "Forbidden Content" sections in templates
- Clear boundaries to prevent scope creep
- **Source**: `.roo-templates/template_plan.md:1-94`

**5. Flakiness Investigation Protocol**
- Structured approach to non-deterministic test failures
- N-run probes with statistical analysis
- Blocker documentation for unresolvable flakiness
- **Source**: `.roo/rules-orchestrator/orchestrator_testing_process.md`

**6. Post-Implementation Documentation Requirements**
- WHY comments for non-obvious code (algorithms, workarounds, optimizations)
- Architecture Decision Records (ADRs)
- Traceability to requirements and tests
- **Source**: `.roo/rules-code/rules.md:1-64`

**7. Interactive Brainstorming Workflow**
- 5-step iterative exploration process:
  1. Information Gathering
  2. Present and Inquire
  3. Iterative Deepening
  4. Conclusion Trigger
  5. Flexible Outcomes
- **Source**: `.roo/rules-architect/rules.md:1-31`

### What Translated to Claude Code

These patterns successfully migrated from Roo Code to Claude Code (see CLAUDE.md):

**Preserved Concepts:**
- Task folder structure (`requirements_tasks/[category]/[requirement]/tasks/[date]_[name]/`)
- `plans_and_protocols/` for persistent memory across sessions
- Template-driven approach to documentation
- Separation of planning and implementation phases
- WHY comments for non-obvious code
- Validation/approval step before implementation

**Adapted Concepts:**
- Mode system (.roomodes) → Skill system (.claude/skills/)
- Subtask orchestration → Subagent delegation (Task tool)
- Custom memory persistence → Native context + file-based protocol.md
- Manual template enforcement → Workflow skill automation

### What Was Lost in Migration

Document these for potential future tools:

**1. Explicit Validation Loop Terminology**
- Roo Code: "Analysis & Validation Loop" (Phase 1)
- Claude Code: Implicit in "plan approval"
- **Value**: Explicit phase name emphasizes catching assumptions early

**2. Multi-Level Testing Orchestration**
- Roo Code: 4-level hierarchy (Testing Orchestrator → File → Part → Code)
- Claude Code: Single `test-engineer` agent
- **Value**: Fine-grained control for complex testing scenarios

**3. Metrics Collection Framework**
- Roo Code: `metrics.md` files tracking execution stats
- Claude Code: No built-in metrics
- **Value**: Data-driven workflow improvement

**4. Flakiness Investigation Protocols**
- Roo Code: Structured N-run probes with statistical analysis
- Claude Code: Manual investigation
- **Value**: Systematic approach to non-deterministic failures

**5. Template Enforcement**
- Roo Code: Strict template requirements (forbidden content sections)
- Claude Code: Guidance-based (less strict)
- **Value**: Consistency across team/sessions

### Migration Summary for KNOWLEDGE_TRANSFER.md

Document this comparison for future tool switches:

| Pattern | Roo Code Implementation | Claude Code Implementation | Tool-Agnostic Principle |
|---------|------------------------|---------------------------|-------------------------|
| Memory Persistence | Files in plans_and_protocols/ | Native context + protocol.md | Always use file-based memory for cross-session work |
| Orchestration | Custom modes (.roomodes) | Skills + subagents | Delegate complex work to specialized agents |
| Planning | Analysis & Validation Loop | Plan mode + approval | Always validate assumptions before coding |
| Testing | 4-level hierarchy | Single test agent | Orchestrate testing systematically |
| Documentation | 14 strict templates | Flexible templates + WHY comments | Use templates for consistency |
| Scope Control | Forbidden content sections | Skill-level constraints | Explicitly define scope boundaries |

## Obsolete Tasks Handling

### Tasks to Cancel

Three pending tasks became obsolete when the project switched from Roo Code to Claude Code:

**TASK-PROC-005-03** (testing_workflow):
- **Path**: `requirements_tasks/process/AI_rules/workflows/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/`
- **Current Status**: `pending`
- **Work Done**: YES - Contains 175-line gap analysis in `plans_and_protocols/2025-10-20_03_rule_changes_and_gap_analysis.md`
- **Context**: Third iteration (two previous attempts superseded)
- **Value**: Contains detailed analysis of proposed Roo testing orchestration improvements

**TASK-PROC-007-01** (workflow_improvement_automation):
- **Path**: `requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/2025-10-04_explore_roo_rules_update/`
- **Current Status**: `pending`
- **Work Done**: NO - plans_and_protocols/ folder does not exist
- **Created**: 2025-10-04
- **Value**: Minimal (no work started)

**TASK-PROC-006-01** (guideline_updates):
- **Path**: `requirements_tasks/process/documentation_rules/guideline_updates/tasks/2025-10-04_explore_roo_rules_update/`
- **Current Status**: `pending`
- **Work Done**: NO - plans_and_protocols/ folder does not exist
- **Created**: 2025-10-04
- **Value**: Minimal (no work started)

### Cancellation Procedure

For each task, follow this pattern:

**1. Update YAML frontmatter in goal.md**

Add these fields to the YAML frontmatter:
```yaml
status: cancelled
cancellation_reason: "Tool migration from Roo Code to Claude Code. Roo rules no longer applicable. See REQ-PROC-011 for deprecation strategy."
cancelled_date: 2026-01-19
```

**2. Rename task folder**

Append `(cancelled)` suffix to folder name for visual indication:
- `2025-10-20_explore_roo_rules_update` → `2025-10-20_explore_roo_rules_update (cancelled)`
- `2025-10-04_explore_roo_rules_update` → `2025-10-04_explore_roo_rules_update (cancelled)`

**3. Preserve all content**

DO NOT delete any files. Keep:
- `goal.md` with updated YAML
- `plans_and_protocols/` folder (if exists) - contains valuable analysis
- Any other task artifacts

**Rationale**: Preserving cancelled tasks provides historical context for why work stopped and what was learned before cancellation.

### Handling Superseded Tasks

For TASK-PROC-005-03, two previous iterations exist marked `(superseded)`:
- `2025-10-04_explore_roo_rules_update (superseded)`
- `2025-10-15_explore_roo_rules_update (superseded)`

These should be kept as they are.

### Task Status Terminology

Use `cancelled` status (not `obsolete` or `deprecated`):
- `obsolete` - Reserved for requirements that are no longer relevant
- `deprecated` - Reserved for features/patterns being phased out
- `cancelled` - Specific to tasks that were stopped before completion
- `superseded` - Reserved for tasks replaced by another iteration (but still relevant at the time)

### Cross-References

Update parent requirements to reflect task cancellation:
- REQ-PROC-005 (Testing Workflow): Note TASK-PROC-005-03 cancelled
- REQ-PROC-006 (Workflow Improvement Automation): Note TASK-PROC-007-01 cancelled
- REQ-PROC-007 (Guideline Updates): Note TASK-PROC-006-01 cancelled

Add note in each parent requirement:
```markdown
## Related Tasks

### Cancelled Tasks
- TASK-PROC-###-##: [Task name] - Cancelled 2026-01-19 due to Roo Code → Claude Code migration. See REQ-PROC-011.
```


### Requirement Metadata Standards

Add `tool_dependency` field to requirement YAML frontmatter:

**Purpose**: Identify requirements that are tool-specific vs. tool-agnostic

**Values**:
- `tool_agnostic`: Requirement applies regardless of AI tool used
- `claude_code`: Specific to Claude Code
- `roo_code`: Specific to Roo Code (now deprecated)
- `[tool_name]`: For future tools

**Example**:
```yaml
---
id: REQ-PROC-011
tool_dependency: tool_agnostic
urgency: 3
impact: 2
status: pending
---
```

**Usage**: When switching tools, filter requirements by `tool_dependency` to quickly identify what needs updating.

### Deprecation Pattern for Future Use

When deprecating future tools, follow this pattern:

1. **Create Deprecation Requirement**: Document the deprecation strategy (like this REQ-PROC-011)
2. **Archive Files**: Move tool-specific files to `.[tool]_archive/` folder
3. **Add Documentation**: Create DEPRECATED_README.md and KNOWLEDGE_TRANSFER.md
4. **Cancel Affected Tasks**: Update YAML and rename folders with `(cancelled)` suffix
5. **Update Main Docs**: Add deprecation notice to main documentation files
6. **Preserve Knowledge**: Document what patterns should carry forward

**DO NOT**:
- Delete archived files (history is valuable)
- Leave deprecated files in active locations (causes confusion)
- Forget to update parent requirements (maintain cross-references)
- Skip documenting why deprecated (future context is critical)

## Acceptance Criteria

### Deprecation Strategy (SEC-01)
- [x] Archive folder created (`.roo_archive/`)
- [x] All Roo Code files moved to archive
- [x] DEPRECATED_README.md created explaining deprecation
- [ ] KNOWLEDGE_TRANSFER.md created documenting valuable patterns
- [x] Root directory cleaned of Roo Code files

### Preservation Guidelines (SEC-02)
**Status**: Cancelled (Decided 2026-01-23)
**Reasoning**: Pre-documenting patterns in KNOWLEDGE_TRANSFER.md assumes what future AI coding tools will need. When a new tool is adopted, it's more effective for that tool to directly inspect the archived Roo Code files (`.roo_archive/`) and extract what it needs. The new tool knows best what patterns it requires and what it may already support natively. The archive itself serves as the knowledge source.
- [N/A] All 7 valuable patterns documented in KNOWLEDGE_TRANSFER.md
- [N/A] Migration comparison table included (what translated, adapted, lost)
- [N/A] Tool-agnostic principles extracted from Roo Code
- [N/A] Source file references included for all patterns
- [x] No Roo Code files deleted (everything preserved in archive)

### Obsolete Tasks Handling (SEC-03)
- [ ] TASK-PROC-005-03 status changed to `cancelled` with reasoning
- [ ] TASK-PROC-007-01 status changed to `cancelled` with reasoning
- [ ] TASK-PROC-006-01 status changed to `cancelled` with reasoning
- [ ] All plans_and_protocols/ content preserved
- [ ] Parent requirements updated with cancellation notes

### Future-Proofing
- [ ] `tool_dependency` field added to requirement metadata standards
- [ ] Deprecation pattern documented for future use

## Related Tasks

### Cancelled Tasks
- TASK-PROC-011-02: Populate KNOWLEDGE_TRANSFER.md with Roo Code Patterns - Cancelled 2026-01-23. Future AI tools will inspect archived files directly and extract what they need. See SEC-02 for reasoning.

## Related Requirements

- REQ-PROC-005: Testing Workflow (has obsolete Roo task)
- REQ-PROC-006: Workflow Improvement Automation (has obsolete Roo task)
- REQ-PROC-007: Guideline Updates (has obsolete Roo task)

---
## Version History
Created: 2026-01-19
