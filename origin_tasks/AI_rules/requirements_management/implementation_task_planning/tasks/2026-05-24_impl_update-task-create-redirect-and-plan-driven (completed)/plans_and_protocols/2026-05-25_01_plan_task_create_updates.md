# Plan: Update task-create Skill (TASK-PROC-058-04)

**Session**: 37fe32ed-ddf4-4326-94c4-7df1c284972a
**Date**: 2026-05-25

## Summary

Modify `.claude/skills/task-create/SKILL.md` to add:
1. **Redirect logic (AC-10)**: When standalone mode + impl/verify type + parent has uncovered ACs → redirect to task-derive-from-requ
2. **Plan-driven mode (AC-11)**: Accept pre-computed values from a plan; skip coverage-asking, package prompting, user confirmation at step 4

## Exact Changes

### Change 1 — New "Operating Modes" section

**Location**: Insert after line 8 (`You are a task workspace initializer.`) and before `## Core Responsibility`

**Insert**:
```markdown
## Operating Modes

**Standalone mode** (default, no plan entry provided): Full workflow with interactive coverage-asking and user confirmation. Redirect logic applies (§3c below).

**Plan-driven mode** (activated when a plan entry is passed as input): Called by `task-derive-from-requ` Phase 5 or `release-begin-impl` Phase 2c. Skips: step 3b coverage-asking, step 3.4 package prompting, step 4 user location-confirmation. Uses plan values directly for goal.md frontmatter.

### Plan entry format (YAML, inline or file path)

```yaml
task_name: "descriptive name"
req_path: "path/to/requirements.md"
requirements_version: "abc1234"
covers_acs: [AC-01, AC-02]
effort: M
layer: domain
after: []
task_type: impl
implementation_notes: "context for implementer"
opus_recommended: false
target_package: "PKG-X"
```

Pass as: inline YAML block in the skill argument, OR a file path to a YAML file, OR via env var `TASK_CREATE_PLAN_ENTRY=<path>`. Presence of a plan entry activates plan-driven mode automatically.
```

### Change 2 — New "3c. Redirect Logic" section

**Location**: Insert between `### 3b. Requirements Coverage Check (MANDATORY)` section end and `### 4. Reason and Propose Location`

**Insert**:
```markdown
### 3c. Redirect Logic (AC-10) — Standalone Mode Only

**Skip entirely if ANY of these apply**:
- Plan-driven mode is active (plan entry provided)
- Task type is `bugfix`, `explore`, `define`, `analyze`, or `review`

**Trigger** (all three must be true):
1. Standalone mode
2. Task type is `impl` or `verify`
3. Parent requirement has `trackable_items.acceptance_criteria` AND ≥ 1 AC has zero task coverage

**Check uncovered ACs**:
```bash
python3 scripts/requirements/coverage_report.py 2>/dev/null | grep -A 20 "REQ-XXX"
```
Or read existing tasks' `covers.acceptance_criteria` fields and compare against the requirement's `trackable_items.acceptance_criteria` list.

**Redirect action**: Stop task creation and print:
```
This requirement has N uncovered ACs: [AC-XX, AC-YY, ...].
Routing to task-derive-from-requ for holistic decomposition.
```
Then invoke `task-derive-from-requ` skill with the requirement path.

**Override**: If the user explicitly passes `--standalone-override` as an argument, skip the redirect and continue. In automated mode (`CLAUDE_AUTOMATED_MODE=1`): never auto-override — always redirect. Log the override in the goal.md Notes section when used.
```

### Change 3 — Plan-driven bypass at step 4

**Location**: In `### 4. Reason and Propose Location`, after the "**ASK USER TO CONFIRM** before proceeding" line.

**Add**:
```markdown
**Plan-driven mode**: Skip user confirmation. The plan's `req_path` determines the requirement location; the task folder is derived from it. Log: "Location auto-accepted (plan-driven mode): [proposed path]".
```

### Change 4 — Plan-driven bypass in Coverage Tracking

**Location**: In `### Coverage Tracking (covers field)`, in the "If trackable_items exists" block that ends with asking "Which items does this task implement?"

**Add** (before the "Example interaction" block):
```markdown
**Plan-driven mode**: Skip user interaction. Use `covers_acs` from plan entry directly. Log: "Coverage auto-set from plan: [covers_acs list]".
```

### Change 5 — Plan-driven bypass in Package Inheritance

**Location**: In `### Package Inheritance (target_package field)`, at the start of the logic block (after the "Skip this entire section" conditions).

**Add** (as first item after the skip conditions):
```markdown
**Plan-driven mode**: If plan entry includes `target_package`, use it directly. Skip rules 1–4. Log: "target_package auto-set from plan: [value]". Proceed to rule 5 (write to frontmatter).
```

## Acceptance Criteria Mapping

| AC | Change | Verification |
|----|--------|-------------|
| AC-10 | Change 2 (redirect logic) | Test: standalone impl task on requirement with uncovered ACs → redirects |
| AC-11 | Changes 1,3,4,5 (plan-driven mode) | Test: call with plan entry → no coverage-asking, no package prompting, no step 4 confirmation |
| AC-10 exemptions | Change 2 (skip conditions) | Test: bugfix/explore/define task → no redirect |
| Plan-driven standalone | Change 1 (operating modes) | task-create still works without plan entry on reqs without ACs |
| claude-modify-skill | (mandatory per CLAUDE.md) | Use claude-modify-skill for all edits |
