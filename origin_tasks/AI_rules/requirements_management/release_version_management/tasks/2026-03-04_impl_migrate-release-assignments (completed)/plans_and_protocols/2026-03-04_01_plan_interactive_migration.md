# Plan: Interactive Migration of target_release Assignments

**Agent**: Architecture Advisor (Haiku)
**Agent ID**: arch-advisor-haiku-2026-03-04-task-proc-034-07
**Date**: 2026-03-04
**Task**: TASK-PROC-034-07

---

## Executive Summary

Migrate `target_release` assignments to ~69 existing requirements (out of 87 total), following a prioritized, interactive approach where the AI proposes assignments based on context and the user confirms or adjusts. The process will propagate assignments to child tasks using existing inheritance logic from TASK-PROC-034-06.

---

## Context Gathered

### Current State

- **Total requirements**: 87
- **Already assigned `target_release`**: 2 (all others unassigned)
- **With trackable items**: Most requirements have AC or section trackable items
- **RELEASES.md status**: Complete (9 versions: 4 alpha, 4 beta, 1 production)
- **Skill updates**: TASK-PROC-034-05 (requ-explore) and TASK-PROC-034-06 (task-create-impl) ready

### Urgency Distribution (driving priority order)

| Urgency | Count | Status Distribution |
|---------|-------|---------------------|
| U0 | 3 | 2 defined, 1 implemented |
| U1 | 2 | 1 defined, 1 implemented |
| U2 | 4 | 2 defined, 2 implemented |
| U3 | 35 | 19 defined, 2 pending, 10 implemented, 4 other |
| **U4** | **29** | 19 defined, 5 in_progress, 5 implemented |
| **U5** | **12** | 7 defined, 3 pending, 2 implemented |
| **Total High Urgency (U4-U5)** | **41** | ~24 defined/pending/in_progress |

### Status Distribution

| Status | Count | Impact |
|--------|-------|--------|
| in_progress | 3 | Critical to assign correctly (active work) |
| pending | 17 | Ready to start; should target near-term releases |
| defined | 41 | Defined requirements awaiting decision |
| implemented | 21 | Completed; should target completion release |
| draft | 2 | Early stage; may remain unassigned |
| approved/cancelled/deprecated | 3 | Edge cases; may skip |

### Dependency Landscape

- REQ-PROC-034 itself has 6 trackable sections (SEC-01 through SEC-06)
- Many feature requirements depend on epic requirements
- Some dependencies are within the same release (expected), others span releases

---

## Migration Strategy: Three-Phase Approach

### Phase 1: High-Priority Requirements (U4-U5, in_progress)

**Scope**: ~29 requirements (U4 + U5)
**Includes**: 5 in_progress + 24 defined/pending
**Expected duration**: ~1–2 hours user interaction time
**Rationale**: These are closest to shipping; assignments here will have immediate impact on release planning

#### Order

1. **in_progress first** (3 requirements) — active work, highest confidence in timing
2. **U5** (12 requirements) — most urgent after current work
3. **U4** (14 requirements) — important, near-term targets

#### Interactive Pattern

For each requirement:

1. **Show summary**:
   ```
   REQ-FUNC-007: Therapist Transfer UI
   - Urgency: U4-PLAN
   - Status: pending
   - Trackable items:
     • AC-01: "Therapist can transfer via QR code" [target_release: unassigned]
     • AC-02: "Transfer encryption works" [target_release: unassigned]
     • AC-03: "Error handling on transfer failure" [target_release: unassigned]
   ```

2. **Propose per-item releases** (AI suggests based on: requirement scope, urgency, dependencies):
   ```
   Proposal:
   - AC-01 → 0.0.1 (core QR capability, proof-of-concept scope)
   - AC-02 → 0.0.2 (encryption iteration, dependency on 0.0.1 transfer)
   - AC-03 → 0.1.0 (polish after PoC; fits Beta MVP scope)
   ```

3. **User confirms/adjusts**:
   ```
   User input options:
   a) Confirm all proposals
   b) Adjust individual item (e.g., "AC-01 → 0.0.2 instead")
   c) Skip this requirement (unassigned)
   d) Manual entry for entire requirement
   ```

4. **Compute requirement-level release**: Earliest among assigned items (automation)

5. **Validate dependencies**:
   ```
   Checking dependencies for REQ-FUNC-007 (proposed: 0.0.1):
   - Depends on REQ-FUNC-006 (currently unassigned → skip check)
   - No conflicts detected
   ✓ Assignment valid
   ```

6. **Propagate to child tasks** (automation):
   ```
   Writing to requirements.md:
   - AC-01: target_release: 0.0.1
   - AC-02: target_release: 0.0.2
   - AC-03: target_release: 0.1.0
   - [REQ] target_release: 0.0.1

   Propagating to child tasks:
   - TASK-FUNC-007-01 (covers AC-01) → target_release: 0.0.1
   - TASK-FUNC-007-02 (covers AC-02) → target_release: 0.0.2
   - TASK-FUNC-007-03 (covers AC-03) → target_release: 0.1.0
   ```

7. **Persist** (write to file immediately, no batching)

### Phase 2: Moderate-Priority Requirements (U3, pending/defined)

**Scope**: ~35 requirements (U3 status)
**Expected duration**: ~1–2 hours
**Rationale**: Important for full roadmap visibility; less time-critical than Phase 1

#### Approach

Same interactive pattern as Phase 1, but with option to batch-process lower-stakes items:

- **Batch option**: "For the next 10 U3 requirements, use the same heuristic" (no user confirmation per item, only summary after batch)
- **Spot-check**: AI still validates dependencies and flags conflicts
- **Conservative default**: If uncertain, propose `unassigned` rather than guess

### Phase 3: Low-Priority Requirements (U0-U2, Implemented, Draft)

**Scope**: ~20 requirements
**Expected duration**: ~30 minutes
**Rationale**: Lower priority; may remain unassigned or follow a simple rule

#### Approach

- **Implemented requirements**: Auto-assign to the release where they completed (user confirmation only if ambiguous)
- **Draft/deprecated**: Ask user to skip or confirm unassigned status
- **Process requirements** (PROC-*): May remain entirely unassigned (internal tooling, not shipped)

---

## Interaction Model: Step-by-Step

### Workflow Loop

```
for each requirement in sorted_list:
    1. Display requirement header and trackable items
    2. AI proposes target_release per item
    3. User chooses: confirm | adjust | skip | batch-continue
    4. Write to file
    5. Validate dependencies (report conflicts; suggest fixes)
    6. Propagate to child tasks (log summary)
    7. Print progress: "3/69 assigned (4%)"
```

### Prompts and User Interaction Points

#### Prompt 1: Start & Scope Confirmation

```
Interactive Migration: Assign target_release to 69 requirements

Current state:
- 2 already assigned (skip)
- 41 U4-U5 (high priority) → Phase 1
- 35 U3 (medium priority) → Phase 2
- 20 U0-U2/implemented (lower priority) → Phase 3

Ready to start with Phase 1 (U4-U5)?
→ yes | review-phases | export-list | quit
```

#### Prompt 2: Per-Requirement Confirmation

```
──────────────────────────────────────────────
REQ-FUNC-007: Therapist Transfer UI
Urgency: U4-PLAN | Status: pending | Category: FUNC
──────────────────────────────────────────────

Trackable Items:
  AC-01: "Therapist can transfer plan via QR code"
  AC-02: "Transfer encryption works end-to-end"
  AC-03: "Error handling on transfer failure"

Dependencies:
  ← REQ-FUNC-006 (Security: Key Storage) [unassigned]

PROPOSAL:
  AC-01 → 0.0.1 (Alpha – Data Transfer, PoC scope)
  AC-02 → 0.0.2 (Alpha – Encryption, builds on 0.0.1)
  AC-03 → 0.1.0 (Beta MVP, polish phase)

[REQ] Computed release: 0.0.1 (earliest item)

Actions:
→ confirm     (accept proposal)
→ adjust      (change specific items)
→ manual      (enter custom assignment)
→ skip        (leave unassigned)
→ batch:yes   (use proposal heuristic for next 5)
→ quit
```

#### Prompt 3: Adjustment Interface (if user chooses "adjust")

```
Edit assignment for REQ-FUNC-007:

AC-01: [current: 0.0.1] → ?
  (leave blank to keep, type version to change)
  Proposed: 0.0.1 (PoC scope)
  Available: 0.0.1, 0.0.2, 0.0.3, 0.0.4, 0.1.0, 0.2.0, 0.3.0, 0.4.0, 1.0.0

AC-02: [current: 0.0.2] → ?

AC-03: [current: 0.1.0] → ?

(or type "cancel" to go back)
→ save
```

#### Prompt 4: Batch Confirmation (optional, Phase 2+)

```
Batch-processing next 10 U3 requirements with heuristic:
  - Pending items (status: pending) → earliest release for urgency tier
  - Defined items (status: defined) → next release after current work

Continue with batch?
→ yes | review-list | manual-mode | quit

(Processed 15/69, estimated 10 more in batch)
```

#### Prompt 5: Dependency Conflict Detection

```
⚠ Dependency Conflict Detected

REQ-FUNC-013 (proposed: 0.1.0)
  depends on REQ-FUNC-014 (assigned: 0.2.0)

Problem: Dependency ships LATER than dependent
         (REQ-FUNC-014 is 0.2.0, but REQ-FUNC-013 needs it in 0.1.0)

Options:
→ adjust-this    (change REQ-FUNC-013 to 0.2.0 or later)
→ adjust-dep     (change REQ-FUNC-014 to 0.1.0 or earlier)
→ keep-both      (accept conflict; will be flagged in reports)
→ skip-this      (leave REQ-FUNC-013 unassigned)
```

---

## AI Proposal Logic (Heuristic)

For each trackable item in a requirement:

### Heuristic Rules

1. **in_progress requirements**:
   - Propose earliest alpha release if primarily exploratory/PoC
   - Propose first beta release if completing a core loop
   - Ask user if ambiguous

2. **U5 requirements**:
   - Propose earliest alpha/beta release where the feature fits scope
   - Check RELEASES.md scope_boundaries to match

3. **U4 requirements**:
   - Propose alpha or first beta, depending on scope
   - Slightly later than U5 (unless actively in_progress)

4. **U3 requirements**:
   - Propose beta or later (not alpha)
   - Can skip if internal/non-user-facing

5. **Implemented requirements**:
   - Propose the release where implementation finished (ask user)
   - If completed in current WIP, propose "pending" (user confirms)

6. **Security/Encryption features**:
   - Always start at 0.0.2 minimum (0.0.1 is unencrypted PoC)
   - Check RELEASES.md boundaries (0.0.2 includes encryption)

7. **Backup/Data Persistence**:
   - Propose 0.1.0+ (post-Alpha, fits Beta MVP scope)

8. **GDPR/Privacy/Compliance**:
   - Propose 0.4.0 (Beta 4 – Production Readiness scope)

9. **Polish/UX refinement**:
   - Propose one release after core feature (e.g., core in 0.0.1, polish in 0.1.0)

---

## Propagation Logic (Task Inheritance)

After each requirement assignment, the AI automatically:

1. **Find all child tasks** of the requirement (`requires_task_id` cross-reference)

2. **For each task**:
   - Read its `covers` field (which trackable items it implements)
   - Extract the earliest `target_release` among covered items
   - Write to task's `goal.md` YAML: `target_release: [version]`

3. **Log summary**:
   ```
   Propagated REQ-FUNC-007 → 3 child tasks:
   - TASK-FUNC-007-01 (covers AC-01) → 0.0.1
   - TASK-FUNC-007-02 (covers AC-02) → 0.0.2
   - TASK-FUNC-007-03 (covers AC-03) → 0.1.0
   ```

4. **Skip tasks with `covers: []`** (tasks with no specific trackable items):
   - Log: "TASK-FUNC-007-04 has no covers → requires manual assignment"
   - Offer to prompt user: "Which release for this task?" (Yes/No)

---

## Validation Checks (After Each Assignment)

### Dependency Graph Check

For the assigned requirement X:
- For each `depends_on: [Y1, Y2, ...]`:
  - If Y has `target_release`: Check semver(X) >= semver(Y)
  - If Y is unassigned: Skip (cannot validate)
  - If conflict: Show prompt (Prompt 5 above)

### Circular Dependency Detection

- Warn if any circular dependencies exist (rare, but check)
- Do not block assignment, only alert user

### Cross-Release Consistency

- After assignment, check if any tasks in earlier releases depend on this task
- Flag: "TASK-FUNC-007-02 (0.0.2) is depended on by TASK-FUNC-008-01 (0.0.1) — logically backwards"

---

## Data Model & File Format

### Requirement File Updates

For each assigned requirement, update `requirements.md`:

**Before**:
```yaml
---
id: REQ-FUNC-007
urgency: 4
urgency_reason: U4-PLAN
# ... other fields ...
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Therapist can transfer plan via QR code"
    - id: AC-02
      text: "Transfer encryption works"
---
```

**After**:
```yaml
---
id: REQ-FUNC-007
urgency: 4
urgency_reason: U4-PLAN
target_release: "0.0.1"           # ← Computed: earliest among items
# ... other fields ...
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Therapist can transfer plan via QR code"
      target_release: "0.0.1"     # ← Per-item assignment
    - id: AC-02
      text: "Transfer encryption works"
      target_release: "0.0.2"     # ← Per-item assignment
---
```

### Task File Updates

For each child task, update `goal.md`:

**Before**:
```yaml
---
task_id: TASK-FUNC-007-01
covers:
  acceptance_criteria: [AC-01]
  sections: []
# ... other fields ...
---
```

**After**:
```yaml
---
task_id: TASK-FUNC-007-01
covers:
  acceptance_criteria: [AC-01]
  sections: []
target_release: "0.0.1"           # ← Inherited from AC-01
# ... other fields ...
---
```

---

## Success Criteria & Tracking

### Phase Completion Criteria

| Phase | Complete When | User Action |
|-------|---------------|-------------|
| Phase 1 | All U4-U5 assigned (or explicitly skipped) | Continue to Phase 2 |
| Phase 2 | All U3 assigned (or explicitly skipped) | Continue to Phase 3 |
| Phase 3 | All remaining assigned (or explicitly skipped) | Review & finalize |

### Progress Tracking

Throughout the migration, display:
```
Progress: 12/69 assigned (17%)
  Phase 1 (U4-U5): 8/29 (28%)
  Phase 2 (U3): 3/35 (9%)
  Phase 3 (U0-U2): 1/20 (5%)
Estimated time remaining: 45 min
```

### Output Artifacts

1. **Migration log** (per-requirement summary):
   ```
   ✓ REQ-FUNC-007: 3 items assigned, target_release: 0.0.1, 3 tasks propagated
   ⊘ REQ-FUNC-008: skipped (user choice)
   ⚠ REQ-FUNC-009: assigned with 1 dependency conflict (flagged for review)
   ```

2. **Conflict report** (if any):
   ```
   Dependency Conflicts Detected (2):
   1. REQ-FUNC-013 (0.1.0) depends on REQ-FUNC-014 (0.2.0) — BACKWARD
   2. TASK-FUNC-015-02 (0.0.2) depends on TASK-FUNC-016-01 (0.0.3) — BACKWARD

   (Conflicts will also appear in STATUS.md under "Release-Dependency Conflicts")
   ```

3. **Task assignment summary**:
   ```
   Tasks Propagated:
   - 52 child tasks automatically assigned via inheritance
   - 3 tasks with empty covers flagged for manual review

   Examples:
   TASK-FUNC-007-01 (0.0.1), TASK-FUNC-007-02 (0.0.2), ...
   ```

4. **Final STATUS.md regeneration**:
   - Run `scripts/generate_status_overview.py --release-summary`
   - Generate both `--release-summary` and `--full` reports
   - Commit all changes with reference to TASK-PROC-034-07

---

## Implementation Approach (How the AI Will Execute)

### Option A: Interactive Python Script (Recommended)

Create a lightweight interactive migration script:

```
scripts/migrate_target_release.py
  - Reads all requirements.md files
  - Sorts by urgency + status
  - For each requirement:
    - Parse RELEASES.md
    - Show summary + proposal
    - Wait for user input (stdin)
    - Update requirements.md
    - Propagate to tasks
    - Validate dependencies
    - Log to migration_log.txt

Usage:
  python scripts/migrate_target_release.py [--phase 1|2|3] [--dry-run] [--batch]
```

### Option B: Manual Interactive Loop

AI (or skilled human) manually:
1. Iterate through sorted list of requirements
2. For each, display Prompt 2 (per-requirement confirmation)
3. User responds in chat
4. AI updates files directly via Edit tool
5. AI reports propagation + validation

**Recommendation**: Start with Option B (fully controlled, easy to adjust mid-migration) → transition to Option A if the user wants repeatable bulk migration later.

---

## Key Assumptions & Risks

### Assumptions

1. **User availability**: Interactive mode requires ~2–3 hours of user engagement
2. **RELEASES.md is frozen**: No new releases will be added mid-migration
3. **Requirements are stable**: No major requirement changes during migration
4. **Task covers are accurate**: All child tasks accurately reference the ACs they implement

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| User changes assignment mid-migration | Data inconsistency | Log all changes, easy rollback via git |
| Dependency conflicts | Logical impossibility | Flag immediately, offer fix options |
| Circular task dependencies | Infinite loop in propagation | Check for cycles before propagation |
| Missing RELEASES.md | Cannot propose versions | Graceful fallback: ask user for freetext entry |
| Large backlog of unconfirmed tasks | Unbounded task creation | Limit to 5 unconfirmed tasks at once; require confirmation |

---

## Decision Points for User

Before starting, clarify:

1. **Interactive vs. Batch?**
   - Interactive (recommended): Full control per item, longer duration
   - Batch with heuristic: Faster, less control, higher risk of errors

2. **All phases or Phase 1 only?**
   - All (69 requirements): Complete roadmap alignment, ~2–3 hours
   - Phase 1 only (29 requirements): Highest priorities first, ~1 hour

3. **Task propagation automatic?**
   - Yes (recommended): AI updates child task goal.md files, logged for audit
   - Manual review: AI prepares list of changes, user approves each batch

4. **Conflict handling?**
   - Auto-flag: Report conflicts, ask user before proceeding
   - Stop on conflict: Halt migration, require user fix before continuing
   - Continue with warning: Flag conflicts, include in final report, continue

---

## Next Steps

1. **User confirms plan** (this document)
2. **User selects execution mode** (interactive vs. batch, phases, conflict handling)
3. **Migration begins** (use Option B: manual interactive loop via chat)
4. **After completion**:
   - Run `scripts/generate_status_overview.py --release-summary` to validate
   - Commit all changes with TASK-PROC-034-07 reference
   - Generate final conflict report (if any)
   - Task marked complete

---

## Related Context

- **REQ-PROC-034**: Parent requirement defining release version management
- **TASK-PROC-034-05**: requ-explore skill updated with release assignment (COMPLETED)
- **TASK-PROC-034-06**: task-create-impl skill updated with release inheritance (COMPLETED)
- **RELEASES.md**: Single source of truth for 9 planned releases
- **generate_status_overview.py**: Updated to report releases and conflicts (COMPLETED)

