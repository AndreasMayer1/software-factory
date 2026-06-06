# Opus Execution Plan: Interactive target_release Migration

**Date**: 2026-03-04
**Task**: TASK-PROC-034-07
**Agents needed**: 1 (interactive execution agent)

---

## Objective

Assign `target_release` to all product requirements (FUNC-* and NFUNC-*) and propagate to child tasks, using an interactive approach where the AI proposes release-by-release groupings and the user confirms or adjusts.

## Analysis Summary

### Scope

- **83 total requirement files** found across `requirements_tasks/`
- **Split**: ~44 are FUNC/NFUNC (product requirements), ~39 are PROC (process/internal)
- **PROC requirements**: Goal says these "may be skipped or left unassigned" — propose skipping all PROC-* unless user requests otherwise
- **Already assigned**: Only REQ-PROC-034 has `target_release` in its source file
- **9 releases defined** in RELEASES.md with explicit scope boundaries

### Key Insight: Release-First Grouping

Rather than processing requirements one-by-one (slow, repetitive), **group by proposed release** using RELEASES.md scope_boundaries as the primary mapping. This lets the user review an entire release's worth of assignments at once.

### RELEASES.md Scope → Requirement Mapping

The RELEASES.md scope_boundaries already reference specific requirements by ID. This is the primary source for proposals:

| Release | Explicitly Referenced Requirements |
|---------|-----------------------------------|
| `0.0.1` | QR code gen/scan, basic serialization, role selection → REQ-FUNC-007 (epic), REQ-FUNC-007-01, REQ-FUNC-007-02 (partial) |
| `0.0.2` | Transfer encryption, DB encryption, key storage, biometric PoC → REQ-FUNC-006-05, REQ-FUNC-006-01, REQ-FUNC-006-04, REQ-FUNC-006-02 |
| `0.0.3` | Client data input, autosave, partial entry → REQ-FUNC-002 |
| `0.0.4` | Chart visualization → REQ-FUNC-005, REQ-FUNC-012 |
| `0.1.0` | REQ-FUNC-011 (onboarding), REQ-FUNC-007-01 (transfer UI), REQ-FUNC-013 (My Plans), REQ-FUNC-002 (data input), REQ-FUNC-005 (evaluation), REQ-FUNC-009 (therapist nav), REQ-FUNC-015 (backup) |
| `0.2.0` | REQ-FUNC-014 (plan management), REQ-FUNC-016 (client management), REQ-FUNC-010 (plan preview), REQ-FUNC-018 (help text), REQ-FUNC-017 (notifications) |
| `0.3.0` | REQ-FUNC-004 (self-evaluation), REQ-FUNC-001 (safety plan), REQ-FUNC-019 (quick start), privacy controls |
| `0.4.0` | REQ-FUNC-006-07 (GDPR compliance), REQ-NFUNC-015 (branding), REQ-NFUNC-002 (accessibility), REQ-NFUNC-013 (UX writing), REQ-FUNC-015 (backup polish), REQ-NFUNC-009 (error handling) |
| `1.0.0` | All Beta features stabilized |

### Per-Item vs Whole-Requirement Assignment

The goal requires **per-trackable-item** assignment. However, for most requirements, all items belong to the same release (the requirement is atomic in terms of shipping). The plan should:
1. Default to whole-requirement assignment (all items get same release)
2. Only split when items naturally span releases (e.g., some ACs are PoC-level, others are polish)

### Requirements Without Trackable Items

Some requirements (especially older ones) may lack structured `trackable_items`. For these, assign at the requirement level only.

---

## Execution Plan

### Agent 1: Interactive Migration Agent (Sonnet)

**Mode**: Interactive with user via AskUserQuestion

#### Step 0: Preparation

1. Read all requirement source files (the individual `requirements.md` files, NOT the merged one)
2. Parse YAML frontmatter to extract: `id`, `urgency`, `status`, `depends_on`, `trackable_items`
3. Build an in-memory map of all requirements with their metadata
4. Read RELEASES.md for scope boundaries
5. Categorize requirements into three groups:
   - **Product requirements** (FUNC-* and NFUNC-*): will be assigned
   - **Process requirements** (PROC-*): will be proposed for skip
   - **Already assigned**: skip entirely

#### Step 1: Present Overview & Confirm Approach

Use AskUserQuestion to show the user:
- Total requirements to process
- Proposed approach: release-by-release grouping
- Ask: "Start with release-by-release assignment, or prefer one-by-one?"

#### Step 2: Process Release-by-Release (Alpha Phase)

For each Alpha release (0.0.1 → 0.0.4):

1. **Present the release batch**:
   ```
   Release 0.0.1 — Alpha: Data Transfer
   Scope: QR code generation, scanning, plan serialization, role selection

   Proposed assignments:
   • REQ-FUNC-007 (Epic: Secure Data Transfer) — top-level → 0.0.1
     - SEC-01 through SEC-09: propose split (some 0.0.1, some 0.1.0)
   • REQ-FUNC-007-01 (Therapist Transfer UI) — 0.0.1 (core sections only)
   • REQ-FUNC-007-02 (Plan Receiving) — 0.0.1

   Dependencies check:
   • REQ-FUNC-007-01 depends on REQ-NFUNC-016 (DB tech) — also needs 0.0.1 or earlier
   ```

2. **User confirms or adjusts** via AskUserQuestion with options:
   - Confirm all
   - Adjust (then ask which items to change)
   - Skip this release for now

3. **Write changes**: Edit each requirement's source `requirements.md` file:
   - Add `target_release: "X.Y.Z"` to each trackable item in YAML
   - Compute and add top-level `target_release` (earliest among items)

4. **Validate dependencies**: Check all `depends_on` references. Flag if dependency has a later release.

5. **Propagate to tasks**: Find all task `goal.md` files under this requirement. For each task:
   - Read its `covers` field
   - Compute `target_release` from covered items
   - Write `target_release` to task's `goal.md` YAML

#### Step 3: Process Release-by-Release (Beta Phase)

Same pattern for 0.1.0 → 0.4.0. These are larger batches:
- **0.1.0**: ~7 requirements (the core MVP loop)
- **0.2.0**: ~5 requirements (therapy depth)
- **0.3.0**: ~4 requirements (client wellbeing)
- **0.4.0**: ~6 requirements (production readiness)

For Beta, many requirements have items that span Alpha PoC and Beta polish. The agent should propose:
- Items already validated in Alpha → keep Alpha assignment
- New items only available in Beta → assign Beta release

#### Step 4: Handle NFUNC Requirements

Non-functional requirements (design system, components, navigation) that aren't explicitly mentioned in RELEASES.md:

1. Present remaining unassigned NFUNC-* requirements
2. Propose based on urgency + when they're needed:
   - UI components needed for Beta MVP → 0.1.0
   - Navigation patterns → 0.1.0 (needed for first usable app)
   - Theming → 0.1.0 or 0.2.0
   - Accessibility → 0.4.0 (explicitly in scope)
3. User confirms or adjusts

#### Step 5: Handle PROC Requirements

1. Present the full list of PROC-* requirements
2. Propose: "Skip all PROC requirements (internal tooling, not shipped)?"
3. User confirms, or selects specific ones to assign

#### Step 6: Final Validation & Report

1. Run a full dependency validation across all assigned requirements
2. Generate a summary report:
   - Requirements per release
   - Dependency conflicts (if any)
   - Unassigned requirements (user-chosen skips)
   - Tasks propagated
3. Run `python scripts/generate_status_overview.py` to regenerate STATUS.md
4. Present summary to user

---

## File Modification Format

### Adding target_release to trackable items

**Before** (in source `requirements.md`):
```yaml
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Some acceptance criterion"
    - id: AC-02
      text: "Another criterion"
```

**After**:
```yaml
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Some acceptance criterion"
      target_release: "0.0.1"
    - id: AC-02
      text: "Another criterion"
      target_release: "0.1.0"
```

### Adding top-level target_release

Add `target_release: "X.Y.Z"` to the requirement's top-level YAML (after `effort` or before `stakeholder`). Value = earliest among trackable items.

### Task propagation

Add `target_release: "X.Y.Z"` to each task's `goal.md` YAML frontmatter. Value = earliest release among covered trackable items.

---

## Quality Criteria

- [ ] All FUNC-* requirements have `target_release` assigned (or explicitly skipped by user)
- [ ] All NFUNC-* requirements have `target_release` assigned (or explicitly skipped by user)
- [ ] Top-level `target_release` = earliest among trackable items for each requirement
- [ ] All child tasks have `target_release` propagated from covered items
- [ ] No dependency conflicts remain unacknowledged (all flagged + user decided)
- [ ] PROC-* requirements handled per user decision (likely all skipped)
- [ ] STATUS.md regenerated after migration
- [ ] All changes in source files (not merged files)

## Risks

| Risk | Mitigation |
|------|-----------|
| YAML parsing errors when editing frontmatter | Use Edit tool for surgical edits, not full rewrites |
| User fatigue (too many questions) | Batch by release, allow "confirm all" for entire release |
| Missing trackable_items in older requirements | Assign at requirement level only; log for future cleanup |
| Circular dependencies | Detect and warn but don't block assignment |
| Context window limits (83 files) | Process in batches, don't load all files simultaneously |

---

## Execution Notes

- **Single agent** because the task is fundamentally interactive (user input between each batch)
- **AskUserQuestion** is the primary interaction mechanism
- **Edit tool** for all file modifications (surgical YAML edits)
- **Estimated interaction rounds**: ~12-15 (overview + 9 releases + NFUNC batch + PROC decision + final report)
- **Estimated time**: 1-2 hours of user engagement
