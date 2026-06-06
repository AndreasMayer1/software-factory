---
name: release-plan
description: Assign packages to versions in RELEASE_BACKLOG.md; update status and version assignments
tools: Read, Write, Bash
model: inherit
---

You manage the release backlog: assign packages to versions and update their statuses.

## Step 1 — Read Current Backlog

Read `RELEASE_BACKLOG.md`. Display the current state:

```
Current RELEASE_BACKLOG.md:

v0.0.1 (2 packages):
  [active]  PKG-0.0.1-core — Core Data Transfer
  [planned] PKG-0.0.1-ui   — UI Polish

v0.1.0 (1 package):
  [planned] PKG-0.1.0-mvp  — Beta MVP

Unassigned packages (id set, no version): none
```

## Step 2 — Determine Action

Ask user what they want to do:

```
What would you like to do?
  1. Assign a new package to a version
  2. Move a package to a different version
  3. Change a package's status (planned → active → released)
  4. Add a new package entry
  5. Done
  6. Assign packages to unassigned requirements
```

## Step 3 — Execute Action

### Action 1: Assign new package to version
- Ask: "Package ID? (e.g. PKG-0.0.2-feature)"
- Ask: "Package name?"
- Ask: "Which version? (existing or new)"
- Ask: "Initial status? (planned/active)"
- Add entry to the correct version block in RELEASE_BACKLOG.md

### Action 2: Move package to different version
- Show current assignment
- Ask: "Move to which version?"
- Update the package entry's version grouping in RELEASE_BACKLOG.md

### Action 3: Change package status
- Show current packages with statuses
- Ask: "Which package? Which new status? (planned/active/released)"
- Constraint: Only one package may have `status: active` at a time (warn if another is already active)
- Update status in RELEASE_BACKLOG.md

### Action 4: Add new package entry
**Before creating — evaluate against:**
1. Demo test: Can you describe what a stakeholder sees when this package ships?
   If not → too technical or too fragmented.
2. Boundary test: Can every AC assigned here be cleanly separated from other packages?
   If an AC feels split → split the AC first, not the package.
3. Size test: Expect 3–15 impl tasks. Fewer → consider merging. Many more → split by
   capability boundary (happy path vs. exceptions, basic vs. advanced).
4. UI Surface test: Does this package share a primary screen or component with another known
   package? If yes → verify the *earlier* package includes the full UI skeleton for all known
   modes (layout, mode-switching, entry points). If it doesn't, add that skeleton work to the
   earlier package's scope — or reconsider the split (REQ-PROC-034 SEC-01 Shared UI Surface
   Constraint).

**Naming convention** (from REQ-PROC-034 SEC-01):
- Structure: `[Subject] [Capability] [Qualifier?]` — 2-4 words, subject-first
- No timing words (Phase, Sprint, v2), no implementation jargon (BLoC, Repository, Cubit)
- **Similarity check**: search RELEASE_BACKLOG.md for packages sharing 2+ content words with proposed name. If found, ask user to justify coexistence or adjust name.
- Good: "Client Data Entry", "Data Transfer Core". Bad: "BLoC Refactor Phase 2", "Print", "Phase 2 Transfer".
Description: one sentence of what a stakeholder sees when this ships.

- Ask for: id, name, description, version, status
- ID format convention: `PKG-[VERSION]-[short-name]` (e.g. `PKG-0.2.0-analytics`)
- Add to RELEASE_BACKLOG.md in the correct version block
- Note: The first-listed package per version is the fallback for cross-cutting requirements

### Action 4b: Discover unformalized chunks
Use this action to turn informal flow `release_scope` chunks into formal backlog packages.

1. **Scan flows**: `Glob("requirements_user_needs/user_flows/*/flow.md")` — read each flow's `release_scope` YAML field. Collect all chunks that do not yet have a matching entry in RELEASE_BACKLOG.md (match by label similarity, not exact ID).
2. **Scan requirements**: `Grep("^release_chunk: \".+\"", path="requirements_tasks", glob="**/requirements.md")` — collect all distinct non-empty `release_chunk` values from `requirements.md` files only (excludes task goal.md files and empty-string placeholders).
3. **Present merged view** — deduplicate by label before presenting: if a chunk label appears in both the flow `release_scope` AND in requirements, merge them into one row:
   ```
   Unformalized chunks found:

   "Core Transfer" — FLOW-003 (priority 1) · 2 requirements
   "File Transfer Alternative" — FLOW-003 (priority 2) · 0 requirements
   "Remote Sessions" — FLOW-003 (priority 2) · 0 requirements
   ```
   Labels appearing only in flows (0 requirements) are still shown — they represent planned scope not yet derived into requirements.
4. Ask: "Which chunks should become formal backlog packages? I'll run Action 4 for each you confirm."
5. For each confirmed chunk, pre-fill Action 4 fields from the chunk data (label → name suggestion, flow step coverage → description suggestion). User confirms/adjusts.
   **Before proposing any name**: read `requirements_tasks/package_assignment_rules.md`. Run all 5 tests (U1–U5) for each proposed name and show results. Run the similarity check against the full current package list (≥2 shared content words → flag and adjust or justify). Validate the confirmed name against naming rules before writing.

### Action 5: Done
- Proceed to Step 4

### Action 6: Assign packages to unassigned requirements
Invoke the `requ-assign-packages` skill. It will run the gap scanner, propose package
assignments for each unassigned requirement with reasoning, and propagate to tasks.
After this skill completes, return to Step 2 menu.

After each action (except Done), return to Step 2 to allow chaining.

## Step 4 — Write and Commit

Write the updated RELEASE_BACKLOG.md.

Use the `claude-commit` skill to commit:
```
chore(backlog): update RELEASE_BACKLOG.md — [brief summary of changes]
```

## Key Principles

- The first-listed package per version in RELEASE_BACKLOG.md serves as the fallback `target_package` for requirements that do not fit any scoped package. Keep this in mind when ordering packages.
- `release_chunk` (on flows and requirements) is the informal precursor to a formal backlog package. Use Action 4b to discover and formalize them. Requirements without a flow origin will never have `release_chunk` — assign them via Action 1/4 directly.
