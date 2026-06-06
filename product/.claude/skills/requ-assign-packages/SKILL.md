---
name: requ-assign-packages
description: Bulk-assign target_package to unassigned requirement ACs using 4-signal heuristics; propagates to tasks
tools: Read, Write, Bash, Glob, Grep
model: inherit
---

You assign release packages to requirements whose trackable_items lack a `target_package`.

## Step 1 — Run Gap Scanner

```bash
python3 scripts/requirements/sync_requirement_packages.py
```

Display the full output to the user. If zero unassigned items are found, report "All requirements already have packages assigned." and stop.

## Step 2 — Prerequisite Guard

Glob all `requirements_user_needs/user_flows/*/flow.md`. For each file, read its `release_scope` YAML field and collect all chunk labels.

Read `RELEASE_BACKLOG.md` packages list.

Fuzzy-match **every** chunk label across **all** flows against RELEASE_BACKLOG.md package names (LLM semantic judgment). Collect the full list of unmatched labels before taking any action.

**Only after checking all flows**: if any unformalized chunks were found, warn once with the complete list:

> "Unformalized chunks found: [all labels, grouped by flow]. One task will be created."

Use task-create skill **once**: type: impl, urgency: 5, body: "Run `release-plan → Action 4b`. Unformalized chunks: [all labels with flow references]."

Ask: "Continue anyway, or stop?"
- Stop → terminate.
- Continue → proceed with available packages only.

## Step 3 — Assign Packages

For each requirement with unassigned items (from Step 1 output):

### 3a. Read context

Read the full `requirements.md` (body + frontmatter). Read RELEASE_BACKLOG.md packages if not already loaded.

### 3b. Apply 4-signal heuristics (priority order)

For each unassigned AC or section, apply signals in order and stop at the first match:

**Signal 1 — `release_chunk` field (highest priority)**
Check requirement frontmatter for a `release_chunk:` field. If present, fuzzy-match the value to a RELEASE_BACKLOG.md package name (LLM semantic judgment: e.g. "core-transfer" → "Data Transfer Core"). Propose that package for ALL unassigned items of this requirement.

**Signal 2 — requirements_matrix.md lookup (flow-derived requirements)**
Check if the requirement frontmatter has a `user_needs.implements_flows` field. For each flow ID listed:
1. Find the flow directory under `requirements_user_needs/user_flows/`.
2. Read that flow's `flow.md` frontmatter. If it has a `cluster_matrix:` field, read that matrix file; otherwise look for `requirements_matrix.md` in the flow's own directory.
3. In the matrix, scan rows for "Suggested Package" column values whose Gap Description covers the same functional area as the AC (LLM semantic judgment — "covers the same functional area" means the AC and the gap description address the same user-visible behavior).
4. Fuzzy-match the chunk label to a RELEASE_BACKLOG.md package name.
Falls through silently if no matrix file exists for the flow.

**Signal 3 — semantic analysis (no flow origin)**
Read the full requirement body. Compare AC content against each package's `description` and `source.scope` in RELEASE_BACKLOG.md. Propose the best semantic match. If no existing package is a good match, propose a new package name following SEC-01 naming convention and note it as "[NEW — needs release-plan Action 4]".

**Signal 4 — sibling ACs (lowest priority)**
If other ACs in the same requirement already have a `target_package`, propose the same package unless the unassigned AC clearly belongs to a different capability area.

**No match from any signal**: note [REQ-ID / AC-ID] in a running "no-match" list. Show "→ No match" in the proposal output (see 3c). Do not prompt per-AC.

### 3c. Show proposal

After processing all unassigned items for one requirement, show the full proposal.
For each distinct proposed package, run the load check and append a load line:

```bash
grep -r '      target_package: "PACKAGE_NAME"' requirements_tasks/ --include="requirements.md" | wc -l
```

```
REQ-FUNC-007-06 — Transfer Notifications
AC-01: (no description)
  → Proposed: "Data Transfer Core"
    Reason: Signal 2 — matrix row Gap #3 "notifications during QR transfer" → "Data Transfer Core"
AC-02: (no description)
  → Proposed: "Data Transfer Core"
    Reason: Signal 4 — sibling AC-01 assigned to same package; same functional area
AC-07: (no description)
  → No match — run release-plan → Action 4 to create a package, or skip

Package load: "Data Transfer Core" — 8 assigned items (healthy; limit 15)
```

Thresholds: < 12 healthy · 12–15 approaching limit · > 15 warn and suggest split (see package_assignment_rules.md → Package Size Guidelines).

### 3d. User confirmation

Ask: "Accept all / Review individually / Skip this requirement"

- **Accept all**: write all proposed assignments (skip items with no match).
- **Review individually**: for each AC, confirm or enter a different package ID.
- **Skip**: move to next requirement without writing.

### 3e. Write accepted assignments

Use `split_frontmatter()` semantics (read/parse/write carefully):

1. For each accepted AC: set `target_package: "[package-id]"` on that item's frontmatter entry.
2. Recompute the top-level `target_package:` field as the earliest-versioned package across all items in the requirement (use semver ordering: lower version = earlier; unversioned packages are latest; among unversioned use backlog order).

Write the updated `requirements.md` with minimal changes (preserve formatting, only change/add the `target_package` fields).

## Step 4 — Propagate to Tasks

After processing all requirements, run:

```bash
python3 scripts/requirements/sync_task_packages.py --apply
```

Display the output so the user sees which tasks were synced.

## Assignment Rules

- One AC → exactly one package. Never split an AC across packages.
- If any ACs had no match across the full run → after Step 4, create one task via task-create skill (type: impl, urgency: 5, body: "Run `release-plan → Action 4`. No package found for: [REQ-ID/AC-ID list].").
- REQ-PROC-* requirements without a matching package: user may skip; these are intentionally unpackaged internal tooling.
- Ordering-independent: this skill works whether `release-plan` or `requ-derive-from-flow` ran first.
- Requirements with some ACs already assigned: only show and process the unassigned ACs; never overwrite existing assignments.

## Assignment Rules & Naming Validation

Read `requirements_tasks/package_assignment_rules.md` for all assignment rules: when-to-ask vs. auto-assign, "earliest" determination, Shared UI Surface Constraint, naming rules (pattern, 5 tests, role-subject convention), and size guidelines (3–15 task range, proxy count, split trigger). Apply these throughout the assignment process.

When proposing new packages (Signal 1-4 all miss): apply naming rules and run the 5 stakeholder tests from `package_assignment_rules.md → Package Naming Rules`. Suggest with `→ Suggested new package: "[Name]"` and note it requires user approval and `release-plan → Action 4` to formalize.
