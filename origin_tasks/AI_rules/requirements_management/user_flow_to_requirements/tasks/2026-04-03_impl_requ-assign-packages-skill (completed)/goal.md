---
task_id: TASK-PROC-030-10
type: impl
parent_requirement: REQ-PROC-030
urgency: 3
urgency_reason: "U3-WORKFLOW-GAP: 41/95 requirements have no target_package — tasks derived from them never surface in correct package context in next_tasks.py"
impact: 4
impact_reason: "I4-PAIN: Without bulk assignment, every requirement written before packages existed requires a separate requ-explore re-run just for package assignment"
status: completed
completed: 2026-04-03
effort: M
created: 2026-04-03
started: 2026-04-03
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Create sync_requirement_packages.py gap scanner, requ-assign-packages skill, release-plan Action 6, package quality guidance in release-plan Action 4 and requ-derive-from-flow Phase 2"
release_description: ""
requirements_version:
  commit: e9382676
  file: ../requirements.md
---

# Goal: requ-assign-packages Skill + Package Assignment Pipeline

## Objective

Deliver the bulk package assignment pipeline designed in TASK-PROC-030-08. The pipeline
closes the gap where requirements written before packages existed have no `target_package`
on their ACs, causing derived tasks to be invisible to `next_tasks.py`.

## Opus Evaluation Reference

Design evaluated by Opus (this conversation, 2026-04-03). Key findings incorporated:

1. **Protocol cleanup**: Sections 3–4b in the TASK-PROC-030-08 protocol are stale (reference the
   rejected `source.ref`-based approach). Mark them as superseded.
2. **"Suggested Package" column underspecified**: `requ-derive-from-flow` Phase 2 Opus instruction
   has no guidance on how to populate this column. Add chunking rules.
3. **Package quality guidance missing**: No skill explains what makes a well-scoped package.
   Add "demo test", boundary test, and size guidance at all three touch points.
4. **Pipeline is ordering-independent**: The `requ-assign-packages` skill works regardless of
   when `release-plan` or `requ-derive-from-flow` ran. Document this explicitly.

## Scope

### Deliverable 1 — `scripts/sync_requirement_packages.py` (~80 lines)

**Role**: Read-only gap scanner. Lists requirements with unassigned `trackable_items`.
No writing, no interactive mode. Used by the skill and standalone (CI/audit).

**Interface**:
```
python3 scripts/sync_requirement_packages.py [--requirement PATH]
```

**Output**:
```
Requirements with unassigned trackable items:

REQ-FUNC-007-06  requirements_tasks/functional/.../feat_transfer_notifications/requirements.md
  AC-01: "Notification is shown when transfer initiates"
  AC-02: "..."

3 requirements, 7 unassigned items.
```

**Reuse** from `sync_task_packages.py`: `split_frontmatter()`, `parse_release_backlog()`

### Deliverable 2 — `.claude/skills/requ-assign-packages/skill.md`

**Workflow**:
1. Run gap scanner → display gap list
2. **Prerequisite guard**: Glob all `requirements_user_needs/user_flows/*/flow.md`, read
   each `release_scope` field. If any chunk label has no matching entry in RELEASE_BACKLOG.md
   (fuzzy name match) → warn: "Unformalized chunks found: [labels]. Run `release-plan →
   Action 4b` first to create formal packages."
3. For each requirement with unassigned items:
   a. Read full `requirements.md` body + RELEASE_BACKLOG.md packages
   b. For each unassigned AC/section, apply heuristics in priority order:

   **Signal 1 — `release_chunk` field on the requirement (fastest)**:
   `requ-explore` writes `release_chunk: "chunk-label"` to requirements.md when the
   originating goal.md has `suggested_release_chunk`. If this field is present, match the
   chunk label to RELEASE_BACKLOG.md (fuzzy: "core-transfer" → "Data Transfer Core") and
   propose that package for all unassigned ACs of this requirement.

   **Signal 2 — requirements_matrix.md lookup (flow-derived reqs without release_chunk)**:
   - Check if requirement has `user_needs.implements_flows` → get flow ID(s)
   - For each flow: find `requirements_user_needs/user_flows/[flow_name]/requirements_matrix.md`
     (or `_clusters/[name]/requirements_matrix.md` if a cluster matrix exists — check
     flow.md frontmatter for `cluster_matrix:` field)
   - Search matrix rows for a "Suggested Package" value whose description aligns with the AC
   - Fuzzy-match the chunk label to a formal RELEASE_BACKLOG.md package name

   **Signal 3 — semantic analysis (no flow origin)**:
   Read the full requirement body. Compare AC content against each package's `description`
   and `source.scope` in RELEASE_BACKLOG.md. Propose best semantic match.

   **Signal 4 — sibling ACs already assigned**:
   If other ACs in the same requirement already have a `target_package`, propose the same
   unless the unassigned AC clearly belongs to a different capability area.

   c. Show full proposal for the requirement with per-AC reasoning. Example:
      ```
      REQ-FUNC-007-06 — Transfer Notifications
      AC-01: "Notification shown when transfer initiates"
        → Proposed: "Data Transfer Core"
          Reason: release_chunk "core-transfer" → matches "Data Transfer Core" in backlog
      AC-02: "Notification dismissed after 5s"
        → Proposed: "Data Transfer Core"
          Reason: sibling AC-01 assigned to same package; same functional area
      ```
   d. User confirms, adjusts per-AC, or skips the whole requirement.
   e. Write accepted assignments to `requirements.md` YAML (per-AC `target_package` +
      recompute top-level `target_package` as earliest-versioned package).
      Reuse `split_frontmatter()` and `semver_tuple()` from `sync_task_packages.py`.
4. After all requirements: run `sync_task_packages.py --apply` to propagate to tasks.

**Assignment rules** (embed in skill):
- One AC → exactly one package. Never split an AC across packages.
- If no package matches → tell user to run `release-plan → Action 4` to create one.
- Ordering-independent: works whether `release-plan` or `requ-derive-from-flow` ran first.
- Process requirements (REQ-PROC-*) that don't match any package: user may skip; they
  are intentionally unpackaged internal tooling.

### Deliverable 3 — `release-plan` Action 4: Package Quality Guidance

**File**: `.claude/skills/release-plan/skill.md`
**Edit**: In `### Action 4: Add new package entry`, insert before the line `- Ask for: id, name, description, version, status`:

```
**Before creating — evaluate against:**
1. Demo test: Can you describe what a stakeholder sees when this package ships?
   If not → too technical or too fragmented.
2. Boundary test: Can every AC assigned here be cleanly separated from other packages?
   If an AC feels split → split the AC first, not the package.
3. Size test: Expect 3–15 impl tasks. Fewer → consider merging. Many more → split by
   capability boundary (happy path vs. exceptions, basic vs. advanced).

Name rules: max 4 words, describes user-visible capability, not implementation artifact.
Good: "Client Data Entry". Bad: "BLoC Refactor Phase 2".
Description: one sentence of what a stakeholder sees when this ships.
```

### Deliverable 4 — `release-plan` Action 6: Invoke requ-assign-packages

**File**: `.claude/skills/release-plan/skill.md`
**Edit 1**: In Step 2 menu block, add after `  5. Done`:
```
  6. Assign packages to unassigned requirements
```
**Edit 2**: In Step 3, add after `### Action 5: Done` block, before `After each action (except Done)...`:

```
6. Assign packages to unassigned requirements
```

```
### Action 6: Assign packages to unassigned requirements
Invoke the `requ-assign-packages` skill. It will run the gap scanner, propose package
assignments for each unassigned requirement with reasoning, and propagate to tasks.
```

### Deliverable 5 — `requ-derive-from-flow` Phase 2: Suggested Package Guidance

**File**: `.claude/skills/requ-derive-from-flow/skill.md`

**Edit 1**: In the **FRESH mode** Opus instruction block, insert after the matrix format
block (after the line `- Cross-flow gaps use the source flow ID(s)...`)
and before the line `Before writing the file, self-check the Summary table:`:

```
Suggested Package column rules:
- Use the chunk label from the flow's release_scope that covers the relevant steps.
  If no release_scope exists, write "—".
- Do NOT invent chunk names not present in the flow's release_scope.
- Chunking principles:
    • Happy path = one chunk (always). Exception bundles = separate chunks.
    • A chunk must be demoable: when all its gaps are implemented, a stakeholder can see
      something work. If a chunk requires another chunk to be visible, merge them.
    • Write "see flow" if a gap spans multiple chunks; write "—" if no chunk applies.
```

**Edit 2**: In the Notes block of the same FRESH mode instruction (the block starting with
`- Use FLOW-XXX#step_N format...`), find the line:
`- Suggested Release Chunk: use the chunk label from the flow's release_scope...`
Rename `Suggested Release Chunk` → `Suggested Package` to match the column header.

## Acceptance Criteria

- [ ] `scripts/sync_requirement_packages.py` exists, runs read-only, outputs gap list correctly
- [ ] `requ-assign-packages` skill exists with heuristic logic, prerequisite guard, and pipeline call
- [ ] Skill correctly distinguishes flow-derived (matrix lookup) vs. direct (semantic) requirements
- [ ] `release-plan` Action 4 contains demo/boundary/size guidance before field prompts
- [ ] `release-plan` Action 6 added (invokes skill); after it completes, release-plan returns to Step 2 menu
- [ ] `requ-derive-from-flow` Phase 2 Opus instruction contains Suggested Package chunking rules
- [ ] "Suggested Release Chunk" note renamed to "Suggested Package" in requ-derive-from-flow Notes
- [ ] Manual test: run gap scanner → shows approximately 41 unassigned requirements
- [ ] Process requirements (REQ-PROC-*) without matching packages can be skipped without error
- [ ] Requirements with some ACs already assigned show only unassigned ACs in gap scanner output and skill proposals
- [ ] Gap scanner handles AC entries without `text:` field gracefully (shows ID only)
- [ ] Skill falls through from Signal 1→4 when higher-priority signals produce no match, without erroring

## References

- Exploration: `tasks/2026-04-03_explore_bulk-package-assignment-to-requirements (completed)/plans_and_protocols/2026-04-03_01_protocol_bulk-package-assignment.md`
- Opus evaluation: conversation 2026-04-03 (findings in Objective section above)
- Pattern: `scripts/sync_task_packages.py` (gap scanner reuses its helpers)
- REQ-PROC-034: Release Package Management (assignment rules, package schema)
