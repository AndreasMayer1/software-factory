---
name: requ-verify-flow-coverage
description: Verify and remediate flow–requirement coverage gaps
tools: "*"
model: inherit
---

You verify that completed exploration tasks produced requirements that actually address their flow gaps, then offer to remediate confirmed gaps.

**User invokes**: `"Use requ-verify-flow-coverage for [flow path | FLOW-ID | --all]"` or via a verification goal.md

---

## Phase 0: Resolve Context

**Bundle mode** (invoked from a goal.md with `verification_bundle:` frontmatter):
1. Read the goal.md — extract `verification_bundle`, `verification_gaps`, `verification_foundations`, `source_matrix`
2. Use the Gap → Requirement Mapping table in goal.md as the gap list (pre-computed, no re-derivation needed)
3. Task folder is already set — write outputs to `plans_and_protocols/` inside it

**Standalone mode** (user command):
1. Check if an active task exists for this work (look for a goal.md with `verification_task: true` and `status: in_progress`)
2. If none: invoke `task-create` to create a minimal verification task workspace (goal: "Verify flow coverage for [scope]")
3. Resolve scope: `--all` → all approved flows in FLOW_INDEX.md; FLOW-ID or path → that flow's matrix
4. Find matrix: check flow.md frontmatter for `cluster_matrix:` → use cluster matrix; else use `[flow_dir]/requirements_matrix.md`
5. Read matrix Pipeline Status — collect gaps with status `done` (these have requirements to verify)
6. Build gap list from matrix rows for the resolved scope

---

## Phase 1: Per-Gap Extraction (parallel Sonnet agents)

Divide gaps into batches of ≤5. Spawn one general-purpose agent per batch.

Each agent receives its gap batch and does the following for each gap:
1. Read the gap description from the matrix (the full cell text)
2. Read ONLY the specific flow sections referenced in the gap (use the "Source in Flow" column — e.g. "FLOW-002 Steps 1–4", NOT the full flow file)
3. Read the target requirement's `requirements.md`
4. Produce a **structured extraction** written to `plans_and_protocols/gap_[N]_extraction.md`:

```
## Gap #[N] Extraction

### Expected behaviors (from flow)
- Behavior A: [description]
- Behavior B: [description]
...

### Found in requirement
- Behavior A: ✓ [AC/section reference] — or — ✗ not found
- Behavior B: ✓ ... — or — ✗ not found
...

### Cross-reference check
- [Req path] referenced by gap: present / missing in requirement

### Foundation linkage (foundations only)
- Foundation F[N] referenced by dependent requirement: yes / no

### Assessment
- Status: covered | partial | not_covered | placeholder
- Covered: N/M behaviors (XX%)
- Missing: [list]
```

Wait for all extraction agents to complete.

---

## Phase 2: Synthesis

Using the gap extractions (the structured summaries — NOT raw flow/requirement text), the matrix Summary table and Foundation Gaps table (from `source_matrix`), and cross-flow metadata (which gaps have `Cross-Flow` ≠ isolated), produce a synthesis report covering:

```

1. CONFIRMED GAPS: Missing behaviors with no documented reason
   - For each: check if the requirement has a VTR entry, rationale field, or note explaining the deviation
   - If none found → confirmed gap, recommend remediation

2. INTENTIONAL DEVIATIONS: Missing behaviors with documented justification
   - VTR found → mark as "intentional (VTR-NNN)"
   - Explicit rationale in requirement → mark as "intentional (documented)"
   - Deviation serves another flow → mark as "intentional (serves FLOW-XXX)"

3. NEEDS USER DECISION: Conflicts without documented resolution
   (e.g., requirement says X, flow says Y, no VTR or note explaining why)

4. CROSS-CUTTING PATTERNS: Issues that appear in multiple gaps
   (e.g., all WCAG items missing → suggests systematic gap)

5. REMEDIATION PLAN for confirmed gaps:
   - Safe to add: new content, no conflict risk
   - Needs review: would change existing behavior
   - Needs user decision: conflicts with explicit design choices

Write findings to: plans_and_protocols/synthesis_[YYYY-MM-DD].md
After writing, terminate.
```

---

## Phase 3: Report

After Opus terminates, read the synthesis file. Build and write `plans_and_protocols/coverage_report_[YYYY-MM-DD].md`:

```markdown
# Flow–Requirement Coverage Report
Generated: [date] | Bundle: [name] | Matrix: [path]

## Summary
| Metric | Value |
|--------|-------|
| Gaps verified | N |
| Fully covered | N (XX%) |
| Partial | N |
| Not covered | N |
| Intentional deviations | N |
| Needs decision | N |
| Cross-cutting patterns | N |

## Per-Gap Results
[table: Gap # | Requirement | Coverage | Behaviors covered | Notes]

## Confirmed Gaps (remediation recommended)
[list with specific missing items]

## Intentional Deviations (no action needed)
[list with VTR/rationale references]

## Needs Your Decision
[list with conflict description]

## Cross-Cutting Patterns
[list]
```

**Automatic matrix update** — after writing the coverage report, update Pipeline Status in `source_matrix` for each verified gap:
- Gap fully covered (0 missing behaviors, 0 confirmed issues): set Pipeline Status cell to `exists_complete`; replace the Guidance column content with: `✓ Fully covered by [REQ-ID]. Verified [date] via [task-id]. [One sentence on intentional deviations, if any.]`
- Gap partial or not covered: leave Pipeline Status unchanged

Apply edits directly to the matrix file (no separate agent needed for this).

Present findings to user.
- If N confirmed gaps = 0: skill terminates (report + matrix update are the output; no remediation needed)
- If N confirmed gaps > 0: Ask **"Do you want to remediate the [N] confirmed gaps?"** → Yes = Phase 4; No = skill terminates

---

## Phase 4: Remediate (user-gated)

For each confirmed gap's remediation plan:

**Safe to add**: Present the proposed addition, ask user to batch-approve or skip individual items.
**Needs review**: Show existing text + proposed change side-by-side, user picks per item.
**Needs user decision**: Park as `decision_needed` — add a note to the matrix Pipeline Status row.

After user approves a set of changes: spawn one general-purpose agent per requirement file to apply changes.
- Agent reads the current requirements.md
- Applies only the approved additions/changes
- Does NOT restructure or reformat unrelated content

After all agents complete: do a quick re-read of changed requirements to confirm changes were applied. Update coverage report: mark remediated gaps as `remediated`.

---

## Key Rules

1. **Per-gap agents read flow excerpts only** — never the full flow file. Use "Source in Flow" column references.
2. **Matrix is source of truth** — do not re-derive gap list from flow
3. **Opus receives summaries, not raw text** — structured extractions only (~200 words per gap)
4. **Remediation is always user-gated** — no requirement changes without explicit approval
5. **Report always written** — even if all gaps are covered, write the report as an audit trail
6. **Cluster matrices processed once** — if multiple flows share a matrix, it is one verification scope
