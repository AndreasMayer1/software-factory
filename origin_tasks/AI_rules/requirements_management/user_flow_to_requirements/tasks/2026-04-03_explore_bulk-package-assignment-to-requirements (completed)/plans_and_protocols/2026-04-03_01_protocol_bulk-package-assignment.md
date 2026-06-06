# Protocol: Bulk Package Assignment from release-plan to Unassigned Requirements
**Task**: TASK-PROC-030-08
**Date**: 2026-04-03
**Status**: Investigation complete — design revised after review (source.ref-based auto-assignment rejected)

---

## 1. Gap Confirmation

### AC-01: No bulk assignment mechanism exists

**Confirmed.** There is no existing mechanism to push packages from `RELEASE_BACKLOG.md` to
unassigned ACs in existing requirements after `release-plan` runs.

Full trace of the current state:

**Step 1**: `release-plan` runs. User creates or formalizes packages via Actions 1–4.
Result: RELEASE_BACKLOG.md updated with new entries (e.g. `id: "Data Transfer Core"`,
`source.ref: "REQ-FUNC-007"`, `assigned_release: "0.0.1"`).

**Step 2**: Existing requirements that were written before these packages existed still have
no `target_package` on their ACs:
```yaml
# requirements.md — after release-plan, before bulk assignment
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "..."          # no target_package
    - id: AC-02
      text: "..."          # no target_package
```

**Step 3**: `next_tasks.py` calls `find_next_package()`. It scans all task goal.md files for
`target_package` values. If tasks were created from these unassigned requirements, their
`target_package` is also absent (confirmed via TASK-PROC-030-06 trace).
Result: tasks for these requirements never surface in the `next_package` context — they
land in the "unassigned" bucket and are deprioritized.

**Step 4**: Only recourse is to re-run `requ-explore` on each affected requirement
individually to trigger Phase 2.4 package assignment.

**Scale confirmed**: 41 of 95 requirements currently have no `target_package` at all
(`grep -rL "target_package" requirements_tasks --include="requirements.md"`).
Not all of these need packages (some are process/internal tooling by design), but
functional requirements with matching backlog entries are definitely affected.

---

## 2. Existing Skill/Script Audit

| Mechanism | Purpose | Does bulk assignment? |
|-----------|---------|----------------------|
| `release-plan` Actions 1–5 | Manage entries in RELEASE_BACKLOG.md | No |
| `release-plan` Action 4b | Discover unformalized chunks from flows | No (creates packages only) |
| `requ-explore` Phase 2.4 | Per-requirement interactive package assignment | No (single req only) |
| `scripts/migrate_target_release_to_package.py` | One-time bulk migration: `target_release` → `target_package` | No (replaces a field, not fills a gap) |
| `scripts/sync_task_packages.py` (TASK-PROC-030-09) | Propagates requirement AC packages → covering tasks | No (downstream only; requires ACs already have packages) |

**Upstream gap confirmed**: The `sync_task_packages.py` chain (from TASK-PROC-030-09)
only works once requirements have packages. This task addresses the prior step: getting
packages INTO requirements in the first place.

---

## 3. Auto-assignment Feasibility — REJECTED

**Initial proposal**: Use `source.ref` in RELEASE_BACKLOG.md to auto-match packages to
requirement ACs (reusing `migrate_target_release_to_package.py` logic).

**Why rejected after review**:

1. **`source.ref` is not reliably set**: `release-plan` Action 4 never asks for it. All
   existing packages have it because it was manually added — not because the skill enforces it.
   Auto-assignment built on an unreliable field creates silent failures.

2. **Redundancy**: Storing "Package → REQ" in RELEASE_BACKLOG.md AND "AC → Package" in
   requirements.md is the same relationship from two directions. The requirement's
   `target_package` is the actual source of truth. The backlog's `source.ref` is a
   human-readable traceability note, not a mapping mechanism.

3. **Complexity for multi-package requirements**: REQ-FUNC-007 maps to 4 packages with
   partially overlapping AC ranges. Scope disambiguation is fragile and already complex
   in the deleted migration script. Replicating it for assignment is not worth the
   maintenance surface.

4. **The assignment decision is inherently human**: Which AC belongs to which package is
   a product decision that `requ-explore` Phase 2.4 already handles correctly (interactively).
   Auto-deriving it from `source.ref` removes the right human checkpoint.

**Conclusion**: `source.ref` remains valuable as a traceability note in the backlog
("why does this package exist?") but must NOT drive automated AC assignment.

**Revised approach**: `sync_requirement_packages.py` is **interactive** — it presents
unassigned requirements and their ACs to the user grouped for efficiency, then the user
assigns packages (same UX as Phase 2.4 but batched across multiple requirements in one
session). No `source.ref` dependency.

---

## 4. Fix Location Decision

### Option A: New action in `release-plan` (Action 6)

**Pros**:
- Natural moment: user just created/formalized packages, immediately propagate
- Builds on an existing skill's action structure

**Cons**:
- `release-plan` semantics are "manage the backlog" — pushing to requirements is a
  different concern
- Adding propagation logic inline would bloat the skill with a separate domain

**Assessment**: Release-plan Action 6 is the right **entry point** (trigger), but should
delegate entirely to a script, not contain the logic itself.

### Option B: New script `scripts/sync_requirement_packages.py` (recommended)

**New file**: `scripts/sync_requirement_packages.py`

**Pros**:
- Single responsibility: fills `target_package` gaps in requirements
- Reuses the full resolution algorithm already implemented in
  `migrate_target_release_to_package.py` (functions: `split_frontmatter`, `semver_tuple`,
  `earliest_package`, `parse_release_backlog`, `build_lookup`, `resolve_package`,
  `parse_ac_range_from_scope`, `disambiguate_by_scope`)
- Callable standalone or from `release-plan` Action 6
- Composes cleanly with `sync_task_packages.py`: run bulk_assign first,
  then sync_task to propagate to tasks

**Cons**:
- New file in scripts/ — small maintenance surface

**Verdict**: Option B as the implementation vehicle, Option A as the optional trigger.

### Option C: Extension to `requ-explore` Phase 2.4 (batch mode)

`requ-explore` is per-requirement by design. A batch mode would blur its scope.
Rejected: adds complexity where a dedicated script is cleaner.

---

## 4b. Prerequisite: `release-plan` Action 4 Must Set `source.ref`

`sync_requirement_packages.py` relies entirely on `source.ref` in each RELEASE_BACKLOG.md
package to match packages to requirements. If `source.ref` is missing, auto-assignment
fails silently (reports NO_REF_MATCH instead).

**Current state of `release-plan` Action 4**: It asks for `id`, `name`, `description`,
`version`, `status` — but **not** for `source.ref`. Existing packages in RELEASE_BACKLOG.md
have `source.ref` set because the user added them manually. There is no skill-enforced rule.

**Required fix** (Deliverable 3): Add `source.ref` to Action 4's required inputs:

```
### Action 4: Add new package entry
- Ask for: id, name, description, version, status
+ Ask for: source.ref (requirement ID this package delivers, e.g. REQ-FUNC-007;
                       enter "null" for standalone packages with no single requirement)
+ Ask for: source.scope (optional — which ACs/sections this package covers,
                         e.g. "AC-06–17: hardware-adaptive settings")
```

This makes `source.ref` a first-class field set at package creation time, ensuring
`sync_requirement_packages.py` can reliably resolve packages to requirements without
manual data repair.

---

## 5. Design Proposal

### Deliverable 1 — `scripts/sync_requirement_packages.py` (gap scanner only)

**Naming rationale**: Consistent with `sync_task_packages.py` (TASK-PROC-030-09).
Convention: `sync_[target]_packages.py` — the target is where packages are written into.
- `sync_requirement_packages.py` → gap scanner: finds unassigned ACs in requirements
- `sync_task_packages.py`        → requirements.md AC packages → task goal.md files

**Role**: Read-only gap scanner. Identifies which requirements have unassigned trackable
items. No interactive mode, no writing. Used by the AI skill (Deliverable 2) and callable
standalone for CI/audit purposes.

**Interface**:
```
python3 scripts/sync_requirement_packages.py [--requirement PATH]
```
- `--requirement PATH`: folder containing a requirements.md (or ancestor folder);
  scans all requirements_tasks/ if omitted
- Always read-only — outputs gap list only

**Output**:
```
Requirements with unassigned trackable items:

REQ-FUNC-007-06  requirements_tasks/functional/.../feat_transfer_notifications/requirements.md
  AC-01: "Notification is shown when transfer initiates"
  AC-02: "..."
  SEC-01: "Error Handling"

REQ-FUNC-003     requirements_tasks/functional/client/epic_onboarding/requirements.md
  (no trackable_items — skipped)

3 requirements, 7 unassigned items.
```

**Logic**:
1. For each `requirements.md`, read `trackable_items.acceptance_criteria` and `sections`
2. Report items with no `target_package`; skip items that already have one

**Code reuse** from `sync_task_packages.py`:
- `split_frontmatter()` — frontmatter parsing
- `parse_release_backlog()` — optional (for version context in output)

**Estimated size**: ~80 lines

### Deliverable 2 — AI skill: `requ-assign-packages`

**Rationale for a skill over a Python script**: The assignment decision requires context
the user cannot easily reconstruct from AC text alone — full requirement body, related ACs,
package descriptions, release scope. An AI reading the full documents and proposing
assignments with reasoning is strictly better than a terminal dialog where the user has
to open files manually.

**Workflow**:
1. Run `python3 scripts/sync_requirement_packages.py` → get gap list
2. For each requirement with unassigned items:
   a. Read the full `requirements.md` (not just the AC text)
   b. Read `RELEASE_BACKLOG.md` — all packages with descriptions and versions
   c. For each unassigned AC/section: propose a package with explicit reasoning:
      ```
      AC-03: "Scanner initializes hardware-adaptive tier at pairing"
      → Proposed: "Adaptive Scanner Settings" (0.0.1)
      Reason: AC describes tier-probe behaviour at pairing — directly in scope of
              the Adaptive Scanner Settings package (AC-06–17 scope in backlog).
      ```
   d. Show full proposal for this requirement — user confirms, adjusts, or skips items
   e. Write accepted assignments to `requirements.md` YAML
3. After all requirements processed: run `sync_task_packages.py --apply` to propagate
   to covering tasks

**How packages and matrix suggestions share the same origin**:

Packages in RELEASE_BACKLOG.md are derived from flows too:

```
flow.md → release_scope: [{label: "core-transfer", priority: 1}, ...]
      ↓
requ-derive-from-flow → matrix: Gap #3 → "Suggested Package: core-transfer"
      ↓
release-plan Action 4b → formalizes: "core-transfer" → "Data Transfer Core" in RELEASE_BACKLOG.md
```

The matrix "Suggested Package" labels and formal backlog package names share the same
source (flow `release_scope` chunks). They are aligned by design once Action 4b has run.
Cross-flow is consistent: two flows with `release_scope: core-transfer` both map to the
same backlog package — the matrix suggestions converge.

**Prerequisite guard**: `requ-assign-packages` must check whether Action 4b has been run:
- If chunks from flow `release_scope` fields are absent from RELEASE_BACKLOG.md → warn user:
  "Some chunks are not yet formalized. Run `release-plan → Action 4b` first."

**Heuristics for proposals (priority order)**:

1. **Matrix "Suggested Package" → backlog label match (primary, flow-derived requirements)**:
   For requirements derived from a flow (`source_gap` present in goal.md):
   - Read goal.md → extract `source_gap: "Gap #N"` → find flow path from `source_flows`
   - Read the flow's `requirements_matrix.md` → find gap row → read "Suggested Package"
   - Match that label to a formal RELEASE_BACKLOG.md package (fuzzy name match, since
     labels may differ slightly: "core-transfer" → "Data Transfer Core")
   - Propose with reasoning: "Matrix Gap #N suggested 'core-transfer' → matches backlog
     package 'Data Transfer Core'"
   This is near-automatic when Action 4b has aligned the labels.

2. **Semantic analysis (fallback — requirements without a flow origin)**:
   - Read the full requirements.md body
   - Read RELEASE_BACKLOG.md package descriptions
   - Match semantically: which package's description/scope aligns with the AC content?
   - Reasoning: "Semantic match: package description covers [topic]"

3. **Sibling ACs already assigned** (secondary signal for both cases):
   If other ACs in the same requirement already have a package assigned, propose the
   same one unless the unassigned AC's content clearly belongs to a different package.

### Deliverable 2 — `release-plan` Action 6

**File**: `.claude/skills/release-plan/skill.md`

**Insert**: A new Action 6 in Step 2's action list, and its implementation in Step 3.

**Step 2 addition**:
```
  6. Propagate packages to unassigned requirements
```

**Step 3 addition (Action 6)**:
```
### Action 6: Propagate packages to unassigned requirements
Run:
```bash
python3 scripts/sync_requirement_packages.py --dry-run
```
Review the output. If it looks correct, confirm and run with `--apply`.
After applying, run `sync_task_packages.py` to propagate to covering tasks:
```bash
python3 scripts/sync_task_packages.py --apply
```
```

**Why include the sync_task call**: Ensures the full pipeline runs in one shot:
release-plan creates packages → bulk_assign writes them to requirements →
sync_task propagates to tasks. No orphaned tasks.

---

## 6. Composition with sync_task_packages.py

The two scripts form a complete pipeline:

```
RELEASE_BACKLOG.md
       │ (packages exist with source.ref)
       ▼
sync_requirement_packages.py
       │ assigns target_package to requirement ACs
       ▼
requirements.md (ACs have target_package)
       │
       ▼
sync_task_packages.py   ← already planned (TASK-PROC-030-09)
       │ propagates requirement AC packages to covering impl tasks
       ▼
tasks/*/goal.md (impl tasks have target_package)
       │
       ▼
next_tasks.py (tasks surface in correct package context)
```

The scripts are independent and can be run in any combination:
- `bulk_assign` alone: useful when only requirements need fixing
- `sync_task` alone: useful after manual `requ-explore` package assignment
- Both together: full repair of the pipeline

---

## 7. Interactive vs Rule-Based

| Situation | Behavior |
|-----------|----------|
| AC/section has no `target_package` | Present to user with package list — user assigns or skips |
| AC/section already has `target_package` | Preserve — not shown |
| `--dry-run` | List which requirements/ACs need assignment; no prompts |
| User types 'skip' for an AC | Left unassigned — shown again on next run |
| Process/cross-cutting requirements | Shown like any other — user can skip or assign a version-fallback package |

---

## 8. Acceptance Criteria Status

- [x] **AC-01**: Gap confirmed — no bulk mechanism exists between `release-plan` and
  unassigned requirements (Section 1)
- [x] **AC-02**: Fix location identified — new script `scripts/sync_requirement_packages.py`;
  optional trigger in `release-plan` Action 6 (Sections 4–5)
- [x] **AC-03**: Design proposal written:
  - [x] How packages are mapped to ACs at scale (Section 5 — `resolve_package_by_ref()`)
  - [x] How it composes with sync_task_packages.py (Section 6 — sequential pipeline)
- [x] **AC-04**: Specific edit locations defined (Section 5 — Deliverable 1 + 2)

---

## 9. Next Steps

Three implementation tasks to create:

1. **impl (S)**: Create `scripts/sync_requirement_packages.py` (gap scanner, read-only)
   - ~80 lines, reuse `split_frontmatter()` from `sync_task_packages.py`
   - No interactive mode, no writing

2. **impl (S)**: Create `.claude/skills/requ-assign-packages/skill.md`
   - AI skill: runs scanner, reads full requirement docs, proposes assignments with reasoning
   - Calls `sync_task_packages.py --apply` at end to propagate to tasks

3. **impl (XS)**: Add `release-plan` Action 6 that invokes `requ-assign-packages` skill
   - File: `.claude/skills/release-plan/skill.md`
   - ~5 lines

**Execution order**: Script first (1), then skill (2), then release-plan hook (3).
TASK-PROC-030-09 (`sync_task_packages.py`) must be completed before or with (2) —
the skill calls it at the end of the pipeline.

**Note**: The `source.ref` fix for `release-plan` Action 4 is **dropped** — not needed.
`source.ref` remains a voluntary traceability field; no enforcement needed.
