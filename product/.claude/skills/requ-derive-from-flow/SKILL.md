---
name: requ-derive-from-flow
description: Analyze user flow(s), identify requirement gaps, generate goal.md files for requ-explore
tools: Read, Write, Glob, Grep, AskUserQuestion
model: inherit
---

You bridge user flows to requirements by analyzing gaps and creating actionable requ-explore tasks.

**User invokes**: `"Use derive-requirements-from-flow skill for [path/to/flow.md]"`
**Solo mode** (skip related flow check): append `--solo`

---

## Pre-flight: Primary Flow Approval Guard

Before any phase runs:

1. Run `python3 scripts/user_needs/sync_flow_index.py` to ensure FLOW_INDEX.md reflects actual flow.md statuses
2. Read `requirements_user_needs/user_flows/FLOW_INDEX.md`
3. For each flow ID given (e.g. FLOW-003, FLOW-004), find its `Status:` line in FLOW_INDEX
3. If any flow is NOT `approved`, **block immediately**:

> "FLOW-[ID] is `[status]`, not `approved`. Requirements must not be derived until the flow is approved.
> To proceed: get the flow back to `approved` (ux-create-flow CONTINUE → content complete → [joint] approve), then re-run this skill."

If ALL primary flows are `approved` → continue to Phase 0.

---

## Phase 0: Related Flow Discovery (main session)

(Skip this phase if user passed `--solo`.)

### 0.1 Scan for related flows

1. Read `requirements_user_needs/user_flows/FLOW_INDEX.md`
2. Read target flow.md frontmatter + `serves_scenarios` section

Identify overlap candidates by checking (in priority order):
1. **Explicit cross-references**: Target flow's notes/deviations/scope boundaries mention another flow by ID, or FLOW_INDEX notes link them
2. **Shared UI surfaces**: Flows whose steps involve the same screens or components (detectable from FLOW_INDEX notes or flow purpose)
3. **Shared scenarios**: Another flow serves the same scenario IDs (even partially)
4. **Complementary scope**: Target flow's "out of scope" or deviation entries point to a planned/existing flow

Weaker signals (same personas only, same lifecycle stage) noted but not prioritized.

### 0.2 Present findings to user

**If overlap found**: Show each candidate with:
- Overlap reason (which criterion matched)
- Candidate's current `review_status` from FLOW_INDEX

**If any candidate is NOT `approved`**: Warn explicitly:
> "[Flow X] is still [status] — requirements derived now may need rework when that flow is finalized. Consider waiting."

Special case for `pending_alignment`:
> "[Flow X] is `pending_alignment` — its content is user-approved but it is waiting for sibling flows to be aligned. Requirements MUST NOT be derived until the full cluster is jointly approved (`approved`). Deriving requirements now will miss cross-flow requirements."

Ask user to choose:
- **Include as context**: "Include [Flow A, Flow B] as context flows alongside [target]?" → multi-flow Phase 1
- **Solo**: "Proceed with [target] only (skip related flows)" → single-flow Phase 1
- **Wait**: "Wait until [Flow X] is approved before deriving" → skill terminates with a note

**If user chooses Include**: This is a **cluster analysis**. Suggest a cluster name derived from the shared theme of the flows (e.g., "transfer_cluster" for data-transfer flows). Ask: "Cluster name? (suggested: [name])" User confirms or adjusts. Store as `[cluster_name]`. The matrix will be saved to `requirements_user_needs/user_flows/_clusters/[cluster_name]/`.

**If no overlap found**: Note "No related flows identified in FLOW_INDEX.md" and proceed to Phase 1.

---

## Phase 0.5: Matrix State Check

Determine `[matrix_directory]`:
- **Single-flow**: `[primary_flow_directory]`
- **Cluster**: `requirements_user_needs/user_flows/_clusters/[cluster_name]`

Check `[matrix_directory]` for existing matrix files **before** Phase 1.

### Draft exists (`requirements_matrix_draft.md`)

An earlier run was interrupted before finalization. Ask:

```
requirements_matrix_draft.md already exists [in cluster/flow directory].
- Resume: skip Phase 2, go directly to Phase 3 review
- Restart: delete draft, run fresh analysis
```

- Resume → skip to Phase 3.
- Restart → delete draft, proceed to Phase 1 (FRESH mode).

### Finalized matrix exists (`requirements_matrix.md`)

Read the file. Extract: the `Generated:` date and the `### Pipeline Status` section (if present).

**Single-flow**: Read the flow's `review_history` YAML. Identify entries dated **after** the matrix `Generated:` date.

**Cluster**: Read the `review_history` of ALL constituent flows. Identify entries in any flow dated **after** the matrix `Generated:` date.

**No flow changes since matrix date** → show pipeline status and ask:

```
requirements_matrix.md already exists for FLOW-XXX (generated [date]). No flow changes detected since then.
Pipeline Status: [table, or "no Pipeline Status section found"]

Options:
- Exit: matrix is current, no action needed
- Force re-run: overwrite matrix entirely (destructive — existing decisions and pipeline status will be lost)
```

- Exit → terminate.
- Force re-run → Phase 1 (FRESH mode).

**Flow changes detected since matrix date** → set mode: **INCREMENTAL**. Inform user:

```
requirements_matrix.md exists (generated [date]).
Flow changes detected since then:
  - [review_history entries after matrix date]

Running in incremental mode: existing matrix preserved, only new/affected gaps analyzed.
```

Continue to Phase 1 (INCREMENTAL mode).

### Neither file exists → Phase 1 (FRESH mode).

---

## Phase 1: Read & Gather (main session)

### 1.1 Read the primary flow

Read the provided `flow.md` in full. Extract and organize:

**A. Gaps Requiring New Requirements** (if explicitly listed):
Numbered gaps with descriptions

**B. Open Questions** (if present):
Questions needing human decisions before requirements can be written

**C. Screens/Components Involved** (if present):
UI components that imply requirements not captured in explicit gaps

**D. Scope Boundaries** ("This flow does NOT cover..." / "separate flow needed"):
Explicitly deferred or excluded concerns

**E. Release Scope** (if `release_scope` YAML field present):
Release chunks from the flow (label + priority integer) that inform which release unit the derived requirements belong to.

### 1.1b Developer Notes Check

After reading `flow.md`, check for a sibling `notes.md` in the same flow folder.

**If `notes.md` exists:**
1. Read it in full
2. Build a notes lookup: map each `[Step N]` / `[Exception N.N]` reference to its item text; collect `[General]` items separately
3. For each goal.md generated in Phase 4.2, match notes to the steps/exceptions that gap covers:
   - Step-specific items → include only in goal.md files that reference that step
   - `[General]` items → include in ALL goal.md files for this flow
4. Store the matched notes per gap for use in Phase 4.2 goal.md generation (see `## Developer Intent` section in the goal.md template)

**If `notes.md` does not exist:** no action — proceed normally.

### 1.2 Read context flows (if included from Phase 0)

For each context flow, read only (context window protection):
- Frontmatter + serves_scenarios
- Steps overview (step names + actor + one-line summary)
- Exceptions list (names + triggers only)
- Gaps section
- Scope boundaries

Extract sections A, C, D only (not B — open questions belong to each flow's own derivation).

**INCREMENTAL mode — also**: Read the existing `requirements_matrix.md`. Note which existing gap rows reference flow sections that appear in the post-matrix `review_history` changes. These are **affected rows** — flag them for Opus in Phase 2.

### 1.3 Scan existing requirements

For gaps from 1.1A, search:
- `requirements_tasks/functional/**/requirements.md` (use Glob)
- `requirements_tasks/non-functional/**/requirements.md` (use Glob)

For each candidate match, read briefly to assess coverage quality.

**Keyword-grep pass (before categorizing any gap as `new_needed`)**:

For each gap that has no match from the Glob step above, derive 2–4 search terms from the gap description (domain nouns, action verbs, component names). Run a grep across `requirements_tasks/functional/` and `requirements_tasks/non-functional/` for those terms:

```bash
grep -rl "<term>" requirements_tasks/functional/ requirements_tasks/non-functional/
```

Read any hits to assess whether they constitute existing coverage. **A gap must not be categorized as `new_needed` until this grep pass returns no relevant hits.** This surfaces semantic overlaps where folder names and IDs differ from the gap description.

**Duplicate task detection — supplement (for manually-created tasks)**:

Run two grep passes:

**Pass 1 — source_gap lookup**:
```bash
grep -rl "source_gap:" requirements_tasks/
```
For each match, read only the YAML frontmatter (first 20 lines) to extract `source_gap` value and file path. Build a lookup table: `source_gap_text → existing_task_path`. Carry this lookup into Phase 3 to flag gaps whose description fuzzy-matches an already-existing task's `source_gap`.

**Pass 2 — covers lookup** (catches tasks written without source_gap, e.g. from earlier workflow runs):
```bash
grep -rl "covers:" requirements_tasks/
```
For each match, read only the YAML frontmatter (first 30 lines) to extract:
- `parent_requirement` (the REQ-ID this task targets, e.g. `REQ-FUNC-014`)
- `covers.sections` list (e.g. `[SEC-08]`)
- `covers.acceptance_criteria` list (e.g. `[AC-03]`)

Build a coverage lookup keyed by `(parent_requirement, item_id)` pairs:
- For each section: key = `(parent_requirement, "SEC-NN")` → value = existing_task_path
- For each AC: key = `(parent_requirement, "AC-NN")` → value = existing_task_path

**Important**: The key always includes the REQ-ID to avoid false matches — SEC-08 in REQ-FUNC-014 is different from SEC-08 in any other requirement. Never match on section or AC ID alone.

When assessing a gap in Phase 3:
- Determine the target REQ-ID from the matrix row's "Existing Req" path or "Suggested Action" (e.g. a gap targeting `requirements_tasks/functional/therapist/epic_plan_management/requirements.md` resolves to `REQ-FUNC-014`)
- For each section or AC the gap is expected to add/update, look up `(REQ-ID, item_id)` in the coverage lookup
- If a match is found → the gap is already covered by an existing task (regardless of whether that task is pending, in_progress, or completed) → add to "already handled" set

Carry both lookup tables into Phase 3.

---

## Phase 2: Build Requirements Matrix with Dependency Discovery

**INCREMENTAL mode**: Using the existing `requirements_matrix.md` + flagged affected rows + Phase 1 content, produce a Delta Matrix at `[matrix_directory]/requirements_matrix_draft.md` containing:

1. NEW gaps not present in existing matrix — use same format as existing matrix rows, number starting after last existing row
2. AFFECTED rows — re-evaluate each flagged row; mark as "unchanged", "needs update [reason]", or "superseded [reason]"
3. No other sections — omit summary, decisions, out-of-scope (those are preserved from the existing matrix)

After writing the file in INCREMENTAL mode, skip to Phase 3 (INCREMENTAL).

---

**FRESH mode**: Using all extracted content from Phase 1 (sections A–E for primary flow), context flow extracts (sections A, C, D) if present, and all relevant existing requirements found in Phase 1.3, build a Requirements Matrix per the instructions below:

```
Build a Requirements Matrix for the user flow(s). For each gap:
1. Determine status (see categories below)
2. Suggest target path in requirements_tasks/ for new/update items
3. Identify foundational dependencies (step 4 below)
4. Write the matrix to: [matrix_directory]/requirements_matrix_draft.md

Gap status categories:
- exists_complete: Requirement fully covers this gap → no action
- exists_needs_update: Requirement exists but needs extension — **only use this if you can identify specific content from the gap that is absent in the existing requirement**. If all key behaviors, rules, and constraints described in the gap are already present in the requirement (even under different headings or wording), set exists_complete instead. When in doubt, prefer exists_complete over exists_needs_update.
- exists_placeholder: Requirement exists but is largely empty/stub
- new_needed: No requirement exists → suggest new epic/feature path
- decision_needed: Human decision required before writing requirement
- decision_needed_exploration: Decision requires investigation before user can decide → create exploration goal.md (same structure as new_needed, purpose is decision-enabling)
- foundation_gap: Not a direct flow gap, but a technical/architectural prerequisite that one or more flow gaps depend on. Only add when the foundation is missing or incomplete in requirements_tasks/.
- integration_test_needed: Per-flow integration-test coverage requirement. For every flow processed, emit exactly one row of this status, targeted at `requirements_tasks/non-functional/integration_tests/<flow_id>/`, UNLESS such a requirement already exists at that path (in which case emit `exists_complete` for that row instead). This is a non-functional Feature under the `integration_tests` epic; one Feature per user flow.
- out_of_scope: Explicitly deferred or excluded by the flow

Dependency discovery (run for each gap with status new_needed, exists_needs_update, or exists_placeholder):
- Identify what the gap depends on: architectural decisions, shared components, technical prerequisites, data models, infrastructure
- Search requirements_tasks/ for existing coverage of each dependency
- If a dependency is fully covered → note it in the "Foundations" column (link only, no new row)
- If a dependency is missing or incomplete → add a new row with status: foundation_gap. In "Foundations" column of the depending gap, reference the foundation row number (F1, F2, ...).

Multi-Flow Analysis (when context flows are provided):
- Identify **shared UI surfaces** across flows: screens, components, or navigation paths that appear in multiple flows
- For gaps touching shared UI surfaces: note which flows contribute requirements to that surface and flag potential conflicts; if gaps from the same surface land in different packages, flag that the *earlier* package must include the full UI skeleton for all known modes (REQ-PROC-034 SEC-01 Shared UI Surface Constraint)
- Consolidate gaps that would result in the same requirement across flows (mark as "cross-flow gap" with source flows listed)
- For each gap: note in the "Cross-Flow" column whether it is isolated to the primary flow or affects context flows too
- When a context flow's scope boundary creates a gap that the primary flow must account for (or vice versa), create a "cross-flow coordination" entry

Matrix format to write:

## Requirements Matrix: [Flow Name]
Source flows: [flow path(s), primary marked with (primary)]
Generated: [date]

### Flow Gaps

| # | Source in Flow | Gap Description | Existing Req | Status | Foundations | Cross-Flow | Suggested Package | Suggested Action / Target |
|---|----------------|----------------|--------------|--------|-------------|------------|-------------------|--------------------------|
| 1 | Gap #N | [description] | [path or —] | [status] | [F1, F2 or —] | [isolated / FLOW-XXX / —] | [PKG-id or —] | [action] |
...

(If single-flow mode: omit Cross-Flow column.)

### Foundation Gaps

| # | Foundation Description | Existing Req | Status | Needed By | Suggested Action / Target |
|---|------------------------|--------------|--------|-----------|--------------------------|
| F1 | [description] | [path or —] | foundation_gap | [#1, #3] | [action] |
...

(If no foundation gaps are found, write "No foundation gaps identified." instead of the table.)

### Pending Decisions
- [Open Question text] → needs human decision before requirement can be written

### Out of Scope
- [Scope boundary description] → [why deferred]

### Summary
| Status | Count |
|--------|-------|
| new_needed | N |
| exists_needs_update | N |
| exists_placeholder | N |
| decision_needed | N |
| decision_needed_exploration | N |
| foundation_gap | N |
| integration_test_needed | N |
| out_of_scope | N |

Notes:
- For `exists_needs_update` rows: the "Suggested Action / Target" cell must name the specific missing content (e.g. "Add lifecycle states and orphan detection to SEC-08"). A vague "extend requirement" is not acceptable — if you cannot name what is missing, reconsider whether the status should be exists_complete.
- Use `FLOW-XXX#step_N` format for specific step references in gap descriptions
- Minor items too small for standalone gaps may be grouped in a "Mechanics Additions" subsection below the main table
- If multiple gaps address the same requirement, consolidate: mark absorbed gaps as "Addressed as part of Gap #N"; list absorbed gap numbers in the primary gap's Suggested Action cell
- Foundation gaps use F-prefixed numbers (F1, F2, ...) to distinguish them from flow gaps
- Cross-flow gaps use the source flow ID(s) in the Cross-Flow column; isolated gaps use "isolated" or "—"
- Suggested Package: use the chunk label from the flow's `release_scope` that covers the relevant steps; "see flow" if multiple chunks apply; leave blank (—) if flow has no `release_scope`
- **Per-flow integration-test row (always emit)**: in addition to gaps discovered from the flow body, emit exactly one row of status `integration_test_needed` per flow processed (primary and each context flow), targeted at `requirements_tasks/non-functional/integration_tests/<flow_id>/`. If a requirement already exists at that path, emit `exists_complete` for that row instead. This row is a side-output — not tied to any single gap in the flow body — and should appear at the end of the Flow Gaps table for each flow.

Suggested Package column rules:
- Use the chunk label from the flow's release_scope that covers the relevant steps.
  If no release_scope exists, write "—".
- Do NOT invent chunk names not present in the flow's release_scope.
- Chunking principles:
    • Happy path = one chunk (always). Exception bundles = separate chunks.
    • A chunk must be demoable: when all its gaps are implemented, a stakeholder can see
      something work. If a chunk requires another chunk to be visible, merge them.
    • Write "see flow" if a gap spans multiple chunks; write "—" if no chunk applies.
- For `integration_test_needed` rows: copy the Suggested Package value of the **primary functional gap** of the same flow (the lowest-numbered gap whose status is `new_needed`, `exists_needs_update`, or `exists_placeholder`). Reason: integration tests should ship with the features they cover, not in a separate package. If the flow has no functional gap (every functional row is `exists_complete`), use "—".

Before writing the file, self-check the Summary table:
1. Every gap row's `Status` value must appear in exactly one Summary row — no gap counted twice, none missing.
2. Any parenthetical annotation in the Summary (e.g. "partial new") must have a corresponding explanation in the gap row itself; remove it if it does not.

After writing the file, continue. Do NOT create goal.md files — that happens in the next phase.
```

Continue with Phase 3.

---

## Phase 3: Review & Prioritize (main session)

### 3.1 Read the draft matrix

Read `[matrix_directory]/requirements_matrix_draft.md`.

**INCREMENTAL mode**: Also re-read the existing `requirements_matrix.md` for context. The draft contains only new/affected rows.

**Already-created gap detection** (run before presenting to user):

Build an "already handled" set from three sources:

1. **Pipeline Status table** (if `requirements_matrix.md` exists): extract every row where status is `"created"` or `"done"`. Record those gap numbers.

2. **source_gap lookup from Phase 1.3**: for each gap in the current matrix, check if its gap description fuzzy-matches any `source_gap:` value in the lookup. A match means a manually-created task already covers this gap. Record those gap numbers.

3. **covers lookup from Phase 1.3**: for each gap targeting an existing requirement, resolve its target REQ-ID (from the "Existing Req" path or "Suggested Action" column). Then check the coverage lookup for any `(REQ-ID, SEC-NN)` or `(REQ-ID, AC-NN)` key that matches the sections/ACs the gap is expected to add or update. A match means an existing task already covers those items — regardless of that task's status (pending, in_progress, or completed). Record those gap numbers.

   **Key constraint**: always match on `(REQ-ID, item_id)` — never on item_id alone. SEC-08 in REQ-FUNC-014 ≠ SEC-08 in REQ-FUNC-007.

Gaps in the "already handled" set are shown in a separate section in the Phase 3.2 prompt and are **excluded from the creation selection by default**. The user can explicitly include them to re-create (e.g. to overwrite a stale task).

### 3.2 Present to user

**INCREMENTAL mode** — show only delta content:

```
Found [N] new gaps and [M] affected existing rows since [matrix date]:

New gaps:
- [gap list]

Affected existing rows:
- Row #N: [unchanged / needs update — reason / superseded — reason]

Which new gaps should I create goal.md files for?
```

**FRESH mode** — show the full matrix and ask:

```
Found [N] gaps in [flow name] (+ [M] context flows):
- [X] new requirements needed
- [Y] existing requirements to update/complete
- [Z] decisions needed before writing requirements
- [F] foundation gaps (technical prerequisites)
- [C] cross-flow gaps (shared with context flows)
- [W] out of scope (deferred)

Already handled (excluded by default):
- Gap #N → [existing task path]  (source: pipeline status / source_gap match)
- ...

Which gaps should I create goal.md files for?
Example: "1, 2, 4, F1" or "all new_needed" or "skip 3 and 5"
(To re-create an already-handled gap, include its number explicitly.)
```

For each `decision_needed` item, ask: "Has this been decided, or should it remain pending?"
For each `decision_needed_exploration` item: create an exploration goal.md regardless — the decision requires investigation before the user can decide.
For `foundation_gap` items: highlight which flow gaps depend on them so the user can make informed priority decisions.

---

## Phase 3.5: Urgency/Impact Inheritance from Flow Priority (main session)

This phase derives scheduling priority for exploration tasks from the flow's `release_scope` chunk priorities. It answers "when should this exploration task be executed?" without touching package assignment (which belongs to `release-plan` once all requirements exist).

**Skip this phase if**: the flow has no `release_scope` field (no chunk priorities defined).

### 3.5.1 Build chunk → urgency/impact mapping

Read the primary flow's `release_scope` field. Extract each chunk label and its priority integer.

Apply this mapping:

| Chunk priority | urgency | impact | Rationale |
|----------------|---------|--------|-----------|
| 1 | 4 | 4 | Blocks the main flow's implementation — explore soon |
| 2 | 3 | 3 | Important but not the critical path |
| 3 | 2 | 2 | Needed before release but can wait |
| 4+ | 1 | 1 | Low urgency — deferred part of the flow |
| No chunk assigned | 2 | 2 | Default: medium-low |

Set:
- `urgency_reason`: `"Derived from [FLOW-ID] release_scope chunk '[chunk_label]' (priority [N])"`
- `impact_reason`: `"Enables implementation of '[chunk_label]' — flow chunk priority [N]"`

### 3.5.2 Present to user for confirmation

Show the proposed mapping and ask the user to confirm or adjust before goal.md files are created:

```
Urgency/impact from flow release_scope:

Chunk "core-transfer"   (priority 1) → urgency 4, impact 4   [confirm / change]
Chunk "ui-polish"       (priority 2) → urgency 3, impact 3   [confirm / change]
Chunk "advanced"        (priority 3) → urgency 2, impact 2   [confirm / change]
Gaps with no chunk                   → urgency 2, impact 2   [confirm / change]

These values determine which exploration tasks appear first in STATUS.md.
Package assignment is left to release-plan once all requirements exist.
```

Store the confirmed mapping as `chunk_priority_map` for use in Phase 4.2.

---

## Phase 4: Generate Work Items (main session)

### 4.1 Finalize and save matrix

**FRESH mode**: Rename (or rewrite) `[matrix_directory]/requirements_matrix_draft.md` → `[matrix_directory]/requirements_matrix.md`. Remove any internal "ready to rename" status notes. Append a `### Pipeline Status` section with columns `# | Goal.md | Completion`, one row per gap, initial status "pending". Update as goal.md files are created in 4.2.

**INCREMENTAL mode**: Merge the draft into the existing `[matrix_directory]/requirements_matrix.md`:
- Append new gap rows to the main gap table
- For affected rows marked "needs update": add an inline note in the existing row (e.g., `⚠ [date]: [reason]`)
- For affected rows marked "superseded": strike through or annotate inline
- Update `Generated:` date to today
- Append new rows to `### Pipeline Status` (initial status "pending"); leave existing rows unchanged
- Delete `[matrix_directory]/requirements_matrix_draft.md` after merging
- Do NOT overwrite existing rows, decisions, or out-of-scope sections

**Cluster mode — additional steps** (run after matrix is saved, for both FRESH and INCREMENTAL):

1. **Update FLOW_INDEX.md**: Add or update a `## Clusters` section. Each entry:
   ```
   ### [cluster_name]
   Flows: FLOW-XXX, FLOW-YYY, FLOW-ZZZ
   Matrix: requirements_user_needs/user_flows/_clusters/[cluster_name]/requirements_matrix.md
   ```

2. **Update each constituent flow.md**: Add or update a `cluster_matrix` field in the YAML frontmatter:
   ```yaml
   cluster_matrix: requirements_user_needs/user_flows/_clusters/[cluster_name]/requirements_matrix.md
   ```
   This makes the cluster matrix discoverable from any constituent flow.

### 4.2 Create goal.md files for approved gaps

**Timeless task rule**: goal.md files describe the target state of the requirement (WHAT the requirement should cover when done), not specific textual changes to make to the current requirements.md. The agent executing the task reads the current requirement at execution time and derives the concrete changes then. Do NOT write "add line X" or "change section Y to say Z" — write what the requirement must cover or express once complete.

**Determine target task folder** for each approved gap:
- `new_needed` or `foundation_gap` (no existing req) → `[suggested_path]/tasks/[today]_explore_[name]/`
- `exists_needs_update` or `exists_placeholder` or `foundation_gap` (partial existing req) → `[existing_req_folder]/tasks/[today]_explore_update_[name]/`
- `integration_test_needed` → `requirements_tasks/non-functional/integration_tests/<flow_id>/tasks/[today]_explore_<flow_id>_integration_tests/`. The `parent_requirement` field references the integration-tests epic (`REQ-NFUNC-023`) — the explore task creates the per-flow Feature requirement under that epic.

**Batch and delegate** — do NOT create goal.md files directly in the main session:

1. Divide approved gaps into batches of **at most 7 gaps** each (use 5 per batch if gaps are cross-flow or foundation gaps with long context).
2. Spawn one **general-purpose** agent per batch (not implementation-engineer — no code is written here).
3. Each agent receives:
   - The full batch of gap rows (number, description, target folder, gap status, cross-flow info, release chunk)
   - The resolved urgency/impact per gap from `chunk_priority_map` (Phase 3.5). If Phase 3.5 was skipped (no release_scope), omit urgency/impact — task-create will ask the user.
   - The goal.md template below
   - The flows involved (paths) so the agent can read relevant excerpts
   - **This mandatory instruction**: "For each gap in your batch, invoke the `task-create` skill. Pass the target task folder path and the goal.md content. Do NOT create folders or files manually — always use the `task-create` skill. Note: task-create will automatically run propose_after.py to propose `after:` entries before writing goal.md — in automated mode it auto-accepts same-package proposals and skips others."
4. Wait for all agents to complete before proceeding to 4.3.

**Write goal.md** using this template:

```markdown
---
source_flows:
  - FLOW-XXX — [primary flow name] (primary)
  - FLOW-YYY — [context flow name]  # (only for cross-flow gaps)
source_gap: [Gap #N | F#N] — [gap description]
status: not_started
created: [today]
type: explore
writes_requirements: true
urgency: [0-5]               # from chunk_priority_map (Phase 3.5); omit if Phase 3.5 skipped
urgency_reason: "[derived from FLOW-ID release_scope chunk 'label' (priority N)]"
impact: [0-5]                # from chunk_priority_map (Phase 3.5); omit if Phase 3.5 skipped
impact_reason: "[enables implementation of 'chunk label' — flow chunk priority N]"
opus_recommended: false  # set true for cross-cutting, security, or complex trade-off features
foundation_for: []  # (foundation gaps only) list of gap numbers this enables, e.g. [Gap #1, Gap #3]
after_foundations: []  # (flow gaps only) list of foundation gap numbers, e.g. [F1, F2]
cross_flow_impact: isolated  # or: FLOW-XXX, FLOW-YYY (for cross-flow gaps)
suggested_release_chunk: "chunk label"  # from flow's release_scope; omit if flow has none
---

# Exploration Task: [Requirement Name]

## Source

- **Primary Flow**: [FLOW-XXX] — [flow name] (`[flow path]`)
- **Context Flows**: [FLOW-YYY — name, ...] or "none"
- **Gap**: [#N | F#N] — [gap description]
- **Gap Status**: [was: new_needed / exists_placeholder / foundation_gap / etc.]
- **Cross-Flow Impact**: [isolated / shared with FLOW-YYY — describe how]

## Goal

[1–3 sentences: what requirement to create or update, and why it is needed]

## Context from Flow

[Key excerpts from the flow relevant to this requirement:
- Which steps depend on this requirement
- Design notes, constraints, or exceptions that affect scope
- Personas served (from the flow's serves_scenarios)
- Cross-flow considerations (if shared UI surface: what each flow expects from this component)]

## What to Create / Update

[Precise instruction for requ-explore:
- If new: Create a new [Epic/Feature] requirement at [suggested path]. This is a [functional/non-functional] requirement.
- If update: Extend [existing requirement path] to cover [specific missing coverage].
]

## Key Acceptance Criteria (from flow)

[Copy relevant success metrics or constraints from the flow's "Success Metrics" section]

## Developer Intent

<!-- Present only if notes.md existed for this flow AND contained items matching this gap's steps.
     Omit this section entirely if no matching notes were found. -->

[List matched items from notes.md. Tag each as [PREFERENCE] (user expressed a wish) or
[CONSTRAINT] (user said "must" / "don't" / "never"). Example:
- [PREFERENCE] Use ModalBottomSheet for the pairing overlay (FLOW-NNN Step 3, notes.md)
- [CONSTRAINT] Do not use Firebase Cloud Messaging for notifications (FLOW-NNN General, notes.md)
]

## References

- Primary flow: `[flow path]`
- Context flows: `[paths]` or "none"
- [Existing requirement if applicable]: `[path]`
- Related gaps from same flow: [other gap numbers if interdependent]
- [Foundation gaps only] Enables: [list of flow gaps that depend on this foundation]
- [Flow gaps only] Depends on foundations: [list of foundation gap numbers, if any]
```

**Variant for `integration_test_needed` rows**: use the same template above, with these field overrides:
- `source_gap`: `"Integration-test coverage for FLOW-XXX"`
- `type: explore`, `writes_requirements: true` (the explore task creates the per-flow Feature requirement under the integration-tests epic)
- `parent_requirement` field on the task points to `REQ-NFUNC-023` (the integration-tests epic)
- The `## Goal` section uses this fixed wording (replace `FLOW-XXX` and `[flow name]` with the actual flow):

  > Define the integration-test coverage required for FLOW-XXX — [flow name]. The Feature requirement must cover: the happy path through every primary scenario step; each exception path defined in the flow; and the boundary conditions named in the flow's `exceptions:` and `boundaries:` YAML.

- The `## What to Create / Update` section uses this fixed wording:

  > Create a new Feature requirement at `requirements_tasks/non-functional/integration_tests/<flow_id>/requirements.md` under the integration-tests epic (`REQ-NFUNC-023`). This is a non-functional requirement. Its acceptance criteria enumerate the integration-test scenarios derived from FLOW-XXX (happy path per primary step, each exception path, each boundary condition). The integration tests themselves are downstream impl work — this task only writes the requirement.

- All other sections (`## Context from Flow`, `## Key Acceptance Criteria`, `## References`, …) follow the standard template.

### 4.3 Output summary

After all batch agents have completed, update the `### Pipeline Status` table in `requirements_matrix.md`: set status to "created" for each successfully created goal.md (agents report paths back).

```
Requirements Matrix saved: [matrix_directory]/requirements_matrix.md

Analyzed: [primary flow] + [N] context flows
Created [N] goal.md files (via [B] agents, [X] gaps/agent):
  - [path]/goal.md  → [gap description]
  - [path]/goal.md  → [gap description]

Cross-flow gaps ([C] items):
  - [gap description] → shared with [FLOW-XXX]

Pending decisions ([M] items):
  - [Open Question text]

Out of scope ([W] items):
  - [scope boundary]

Next step: Use requ-explore skill for each created goal.md
If the analyzed flow(s) had a `release_scope` field → use task-create skill to create a task:
  type: impl, urgency: 5, body: "Run `release-plan → Action 4b`. Source: [flow path(s)]."
After exploration tasks complete per bundle → run each verification task via "do next task"
(verification tasks are automatically unblocked when their bundle's exploration tasks are all done).
```

### 4.4 Wire Dependencies (batched agents)

Build a dependency map from the finalized `requirements_matrix.md`:

1. Read the `### Foundation Gaps` table: for each F-row, extract its "Needed By" gap numbers.
2. Read the `### Flow Gaps` table: for each gap row, extract its "Foundations" column values (e.g. F1, F2).
3. Cross-reference both tables with `### Pipeline Status` to resolve gap numbers and F-numbers → task IDs.

Result: a list of `(goal.md path, awaiting: [task IDs], after: [task IDs])` for every task that has at least one dependency entry.

**If the list is empty**: skip this phase — nothing to wire.

**If the list is non-empty**:

1. Divide into batches of **at most 7 tasks** each.
2. Spawn one **general-purpose** agent per batch (run all batches in parallel).
3. Each agent receives:
   - Its batch: a list of `(goal.md path, awaiting task IDs, after task IDs)`
   - This exact instruction:

```
For each item in your batch:
1. Read the goal.md file at the given path.
2. In the YAML frontmatter, replace the `awaiting: []` value with the provided awaiting task IDs.
3. In the YAML frontmatter, replace the `after: []` value with the provided after task IDs.
4. In the `## Dependencies` table, add one row per dependency task ID (status: pending, notes: derived from requirements matrix).
5. Do NOT make any other changes to the file.
After processing all files in your batch, report: "Done. Updated: [list of paths]."
```

4. Wait for all agents to complete.
5. Log wired tasks in the Phase 4.3 summary output (append a "Dependencies wired:" line).

### 4.5 Create Verification Tasks (main session)

**Bundle grouping**: Group all exploration tasks created in Phase 4.2 by the **"Suggested Package" column** in the requirements matrix. Each unique value = one bundle. Never use `target_package` for this step — `target_package` is assigned by `release-plan` only after all requirements exist.

**Foundation gap assignment**: Foundation gaps (F-prefix) have no package of their own. Assign each to the bundle of the highest-urgency gap in its "Needed By" column (highest urgency wins; ties broken by lowest gap number).

**Maximum verification tasks**: Cap at **6 verification tasks** (default). If `bundle_count ≤ 6`: create one task per bundle. If `bundle_count > 6`: merge consecutive bundles into 6 groups using this algorithm:

> 1. Sort bundles by number of pending exploration tasks (ascending — fewer pending completes sooner).
> 2. Ties: sort by max urgency of tasks in bundle (descending).
> 3. Ties: sort by lowest gap number in bundle (ascending).
> 4. Divide the sorted list into 6 consecutive equal-sized groups (round up for early groups: e.g. 11 bundles → groups of 2,2,2,2,2,1).
>
> This ensures early verification tasks cover fast-completing bundles; later ones cover slow bundles — checkpoints are spread across the pipeline, not piled at the end.

For each group, create ONE verification goal.md via the `task-create` skill:

**Frontmatter fields**:
```yaml
type: explore
writes_requirements: true
verification_task: true
verification_bundle:          # YAML list — always list all bundle names in this group
  - "[Bundle Name A]"
  - "[Bundle Name B]"         # omit if only one bundle
verification_gaps: [list of all gap numbers across all bundles in this group]
verification_foundations: [list of F-IDs across all bundles in this group]  # omit if empty
source_matrix: "[path to requirements_matrix.md]"
after: [all TASK-IDs of exploration tasks across all bundles in this group]  # dynamic: unblocks automatically when all listed tasks reach terminal status
awaiting: []          # MUST be empty — never put task IDs here; next_tasks.py treats non-empty awaiting as a permanent block
urgency: [max urgency across all bundles in this group]
impact: [max impact across all bundles in this group]
effort: S
```

**Body** (use this template — for merged groups, add one sub-section per bundle):
```markdown
# Goal: Verify Flow Coverage — [Bundle A] + [Bundle B] Bundles

## Objective

Run flow–requirement coverage verification for the **"[Bundle A]"** and **"[Bundle B]"** bundles.
This task invokes `requ-verify-flow-coverage` in bundle mode.

## Verification Scope

**Matrix**: `[source_matrix path]`

### Bundle 1: [Bundle A]
**Gaps to verify**: [gap numbers]
[**Foundations to verify**: F1, F2]  # omit if none

### Bundle 2: [Bundle B]
**Gaps to verify**: [gap numbers]
[**Foundations to verify**: F3]  # omit if none

### Gap → Requirement Mapping

| Gap | Bundle | Requirement | What to check |
|-----|--------|-------------|---------------|
[one row per gap: gap number | bundle name | requirement path | brief description]

## Source Flows

[list of flow paths from the matrix header]

## Execution

Invoke `requ-verify-flow-coverage` with this goal.md as context.

## Acceptance Criteria

- [ ] Coverage report written to plans_and_protocols/
- [ ] Each gap assessed as covered / partial / not_covered
- [ ] Findings presented to user with recommended actions
- [ ] If remediation needed: user confirms approach before requirements are updated
```

**Parent requirement for task-create**: use the REQ-ID most commonly referenced among all gaps in the group. If gaps span multiple epics with no clear common ancestor, use the primary flow's epic.

After all verification tasks are created:
1. Add one row per verification task to the `### Pipeline Status` table in `requirements_matrix.md` (prefix `V1`, `V2`, ...; initial status "created").
2. Append to the Phase 4.3 summary output:
```
Verification tasks created ([N] tasks covering [M] bundles):
  - [path]/goal.md  → [bundle names] ([gap count] gaps, depends on [task count] tasks)
```

---

## Key Principles

1. **Read first, write second**: All analysis before any files are created
2. **User approves before creation**: Matrix shown and confirmed before goal.md files are written
3. **No requirements written directly**: This skill only creates goal.md task files; requ-explore writes the actual requirements
4. **Trace everything**: Each goal.md references source flow(s) + gap number
5. **decision_needed never silently skipped**: Open Questions always surface to user
6. **out_of_scope is not missed**: Scope boundaries are documented, not ignored
7. **Gap absorption**: Consolidate gaps addressing the same requirement. Mark absorbed gaps in the matrix; list them in the primary gap's goal.md References.
8. **Foundations discovered early**: Dependency discovery happens during matrix building (Phase 2), not as a post-hoc pass. Foundation gaps appear alongside flow gaps in one unified matrix.
9. **Multi-flow awareness**: Flows sharing UI surfaces, scenarios, or scope boundaries should be analyzed together. Phase 0 identifies these relationships via FLOW_INDEX.md. Isolated derivation is allowed (`--solo`) but the user is always informed of related flows first. When context flows are not yet approved, warn that derived requirements may need rework.
10. **Cluster matrices live in `_clusters/`**: A multi-flow (cluster) analysis produces a single matrix at `requirements_user_needs/user_flows/_clusters/[cluster_name]/requirements_matrix.md`. Each constituent flow.md carries a `cluster_matrix:` frontmatter pointer for discoverability. Single-flow matrices stay in the flow's own directory.
11. **Batched goal.md creation**: goal.md files are never written directly by the main session. Spawn one general-purpose agent per batch of ≤7 gaps; each agent uses the `task-create` skill. Large volumes (e.g. 25 gaps) are split into ≥4 parallel agents.
12. **Priority ≠ packaging**: Urgency/impact (Phase 3.5) answers "when should this exploration run?" and is derivable from a single flow's chunk priorities. Package assignment answers "what ships together?" and requires the full cross-flow picture — that belongs to `release-plan`, not here. Never assign `target_package` in this skill. Verification task bundling (Phase 4.5) uses the matrix "Suggested Package" column — never `target_package`.
