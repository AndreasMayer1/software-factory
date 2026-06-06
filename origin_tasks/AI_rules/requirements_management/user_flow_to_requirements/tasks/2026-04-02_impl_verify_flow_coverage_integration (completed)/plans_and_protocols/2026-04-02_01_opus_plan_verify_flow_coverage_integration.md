# Opus Plan: Integrate requ-verify-flow-coverage into the Derive-from-Flow Pipeline

## Objective

Embed verification checkpoints into the exploration-task pipeline so that flow–requirement coverage is validated automatically as part of the "do next task" workflow, without relying on the user to remember.

## Analysis Summary

### Current Sorting Mechanism

`next_tasks.py` ranks tasks by:
1. Explore before impl (type_rank)
2. Tasks in the next release first
3. Requirements already in-progress first
4. Priority score = urgency × 10 + impact (tiebreaker)

Blocked tasks (via `depends_on` referencing non-terminal task IDs) are **excluded** entirely from the eligible set.

### Bundle Grouping

The `Suggested Package` column in the requirements matrix already groups gaps into thematic bundles that align with the flow's `release_scope` chunks. Examples from the transfer cluster:
- "Core Protocol Delivery" (priority 1)
- "Core QR Transfer" (priority 1)
- "Scope & Privacy Controls" (priority 2)
- "Notification System" (priority 2)
- "Phase 2 Edge Cases" (lower)

Each chunk maps to urgency/impact values via Phase 3.5 of `requ-derive-from-flow`.

### Key Design Decision: depends_on vs. priority manipulation

**Recommendation: Use `depends_on`**, not priority tricks.

Rationale:
- Integer priorities (0–5) leave no room for fractional interleaving between bundles at the same priority level
- `depends_on` already works: `_is_blocked()` excludes tasks whose dependencies are not in `completed_ids`
- A verification task with `depends_on: [TASK-A, TASK-B, TASK-C]` (all exploration tasks in its bundle) will naturally become eligible only when ALL those tasks are completed
- No script changes needed — the existing `next_tasks.py` handles this correctly
- If a user skips or defers a task in the bundle, the verification stays blocked (which is correct — you can't verify incomplete exploration)

**The priority of the verification task should match its bundle**, so that when it becomes unblocked, it surfaces at the correct position relative to other bundles.

---

## Answers to the 8 Key Questions

### Q1: Bundle Definition

**Use the `Suggested Package` column from the requirements matrix.** This already groups gaps into thematic bundles and directly corresponds to the flow's `release_scope` chunks.

Concretely, during Phase 4 of `requ-derive-from-flow`, after all exploration goal.md files are created:
1. Group the created tasks by their `target_package` value (which comes from the matrix's Suggested Package → Phase 3.5 mapping)
2. Each unique `target_package` value defines one bundle
3. Foundations (F1, F2, F3) belong to the bundle of the highest-priority gap that depends on them (determined from the "Needed By" column)

Edge case: gaps that span two packages (e.g., "Core Protocol Delivery / Core QR Transfer") → assign to the earlier-priority package. The verification task for that bundle will still check this gap.

### Q2: Priority Interleaving

**No interleaving tricks needed.** The `depends_on` mechanism handles ordering:

- Verification task gets **the same urgency/impact as its bundle's exploration tasks**
- Verification task sets `depends_on: [list of all TASK-IDs in this bundle]`
- Result: while bundle tasks are pending/in-progress, the verification task is blocked → invisible to `next_tasks.py`
- Once all bundle tasks are completed → verification becomes eligible → surfaces immediately (same priority, type=explore)
- Next bundle's tasks are already eligible but were lower priority, so verification runs first

**One concern**: if a bundle's exploration task is blocked by a foundation task in a different bundle, the verification task will wait. This is *correct behavior* — you can't verify a requirement that was never explored because its foundation wasn't done yet.

### Q3: Verification goal.md Structure

The verification task needs to be **self-contained but lightweight** — it should embed just enough context to let the executing session know what to read, without duplicating the matrix content.

```yaml
---
task_id: TASK-FUNC-007-V01  # V-prefix distinguishes verification tasks
type: explore               # stays explore so type_rank ordering works
parent_requirement: REQ-FUNC-007  # nearest common ancestor of the bundle
urgency: 4
urgency_reason: "Derived from FLOW-002/003/004 release_scope chunk 'Core Protocol Delivery' (priority 1)"
impact: 4
impact_reason: "Verification gate — ensures Core Protocol Delivery requirements reflect flows before implementation"
status: pending
effort: S
created: 2026-04-02
depends_on: [TASK-FUNC-007-01-03, TASK-FUNC-014-02, ...]  # all exploration task IDs in this bundle
blocked_by: []
blocked_reason: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Verify that requirements updated by Core Protocol Delivery exploration tasks correctly cover FLOW-002/003/004 gaps #1, #2, #3, #4, #7"
release_description: ""
requirements_version:
  commit: ""
  file: ""
verification_bundle: "Core Protocol Delivery"
verification_gaps: [1, 2, 3, 4, 7]
verification_foundations: [F1]
source_matrix: "requirements_user_needs/user_flows/_clusters/flexible_data_transfer/requirements_matrix.md"
---

# Goal: Verify Flow Coverage — Core Protocol Delivery Bundle

## Objective

Run flow–requirement coverage verification for the "Core Protocol Delivery" bundle
of the transfer cluster (FLOW-002 / FLOW-003 / FLOW-004).

This task invokes the `requ-verify-flow-coverage` skill in **bundle mode**.

## Verification Scope

**Matrix**: `requirements_user_needs/user_flows/_clusters/flexible_data_transfer/requirements_matrix.md`
**Bundle**: Core Protocol Delivery
**Gaps to verify**: #1, #2, #3, #4, #7 + Foundation F1

### Gap → Requirement Mapping (for quick reference)

| Gap | Requirement | What to check |
|-----|-------------|---------------|
| F1 | REQ-FUNC-007 (pairing data model section) | Pairing entity: all attributes, lifecycle |
| #1 | REQ-FUNC-007-01 | Protocol Delivery Interface: non-wizard layout, Instruction View Modal, Plan Editor |
| #2 | REQ-FUNC-014 | Client Copy Architecture: creation, lifecycle, navigation, visual distinction |
| #3 | REQ-FUNC-007-02 | Receipt confirmation: pairing scanner, progress, receipt screen, multi-therapist |
| #4 | REQ-FUNC-002 | First-entry enhancements: schedule filtering, partial acceptance, notification prompt |
| #7 | REQ-FUNC-007-01 | Time-based detection model: shared contract, button states, grey-zone |

## Source Flows

- FLOW-002: `requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md`
- FLOW-003: `requirements_user_needs/user_flows/session_start_data_transfer/flow.md`
- FLOW-004: `requirements_user_needs/user_flows/flexible_data_transfer/flow.md`

## Execution

Invoke `requ-verify-flow-coverage` with this goal.md as context.
The skill will read the matrix, flows, and requirements, then produce a coverage report.

## Acceptance Criteria

- [ ] Coverage report written to plans_and_protocols/
- [ ] Each gap assessed as covered / partial / not_covered
- [ ] Findings presented to user with recommended actions
- [ ] If remediation needed: user confirms approach before requirements are updated
```

**Design notes:**
- `verification_bundle`, `verification_gaps`, `verification_foundations`, `source_matrix` are custom frontmatter fields that the verification skill reads to know its scope
- The Gap → Requirement Mapping table is pre-computed by `requ-derive-from-flow` at creation time (it has all this info from the matrix)
- The skill never needs to re-derive which requirements to check — it's in the goal.md
- `type: explore` ensures it sorts correctly (explore before impl)
- **Task ID format**: Use a V-suffix convention — `TASK-FUNC-007-V01`, `TASK-FUNC-007-V02`. This will need a minor extension to the task ID allocation logic (or just use the regular allocator and add a `verification_task: true` flag in frontmatter so `claude-route` can detect it)

### Q4: Divide-and-Conquer Strategy

This is the hardest problem. Here is a three-layer approach:

#### Layer 1: Sonnet Extracts (per-gap agents)

For each gap in the bundle, spawn one Sonnet agent that:
1. Reads the gap description from the matrix (short — one cell)
2. Reads the target requirement's full requirements.md
3. Reads ONLY the specific flow sections referenced by the gap (e.g., "FLOW-002 Steps 1–4" — not the entire 500-line flow)
4. Produces a **structured extraction**: a JSON-like summary:

```markdown
## Gap #1 Extraction

### Expected from flow
- Behavior A: non-wizard button-based layout with three functions
- Behavior B: Instruction View — full-screen modal using shared data entry component
- Behavior C: In-Context Plan Editor — per-question edit buttons
- Behavior D: "Editing copy for [Client Name]" indicator
- Behavior E: App store reference when client lacks app
- Behavior F: Estimated transfer duration display
- Constraint G: Screen stays on, no auto-dim
- Constraint H: Editor changes immediately reflected in instruction view

### Found in requirement
- AC-08: ✓ Non-wizard layout (Section SEC-07)
- AC-09: ✓ Instruction View Modal (Section SEC-08)
- AC-10: ✓ Plan Editor (Section SEC-09)
- Behavior D: ✗ Client-copy indicator not found
- Behavior E: ✓ App store reference (AC-12)
- Behavior F: ✗ Estimated duration not specified
- Constraint G: ✗ Screen stay-on not specified
- Constraint H: ✓ Editor-view sync (SEC-09, paragraph 3)

### Assessment
- Status: partial
- Covered: 5/8
- Missing: client-copy indicator (D), estimated duration (F), screen stay-on (G)
```

**Why this works**: Each agent handles ONE gap, reads only the specific flow excerpt + one requirement. Context window usage: ~2–5K tokens per gap (not the full 100+ page flow).

#### Layer 2: Opus Synthesis

After all per-gap agents complete, invoke `claude-switch-opus` with:
- All gap extractions (compressed: the structured summaries, NOT the raw flow/requirement text)
- The full matrix summary table (one page — already exists)
- Cross-flow metadata (which gaps share requirements, which gaps have cross-flow impact)

Opus's job:
1. **Cross-cutting analysis**: Are there cross-gap inconsistencies? (e.g., Gap #1 says "shared data entry component" but Gap #3 describes a different component for the same screen)
2. **Coherence check**: Do the partial/missing items across gaps form a pattern? (e.g., all accessibility items systematically missing → suggests one requ-explore session missed the WCAG cascade)
3. **Intentional deviation detection**: For each "missing" item, check if the requirement explicitly addresses a different approach and WHY (e.g., requirement says "wizard layout" instead of "non-wizard" — check if there's a noted trade-off or VTR)
4. **Remediation plan**: For each confirmed gap, draft the specific changes needed in the requirement, categorized as:
   - **Safe to add**: New content that doesn't conflict with anything
   - **Needs review**: Content that would change existing behavior (other flows may depend on it)
   - **Needs user decision**: Content that conflicts with explicit design decisions

**Why Opus**: The synthesis requires judgment about intent, trade-offs, and cross-cutting patterns. This is where the "whole picture" coherence lives — and it works because Opus receives condensed summaries (not raw text), keeping context manageable.

#### Layer 3: Sonnet Presents + Remediates

After Opus returns the synthesis:
1. Sonnet presents findings to user (organized by gap, with counts)
2. User approves/adjusts the remediation plan
3. For "safe to add" items: Sonnet agents update requirements in parallel (one agent per requirement file)
4. For "needs review" items: Sonnet presents each with the existing text + proposed change, user picks
5. For "needs user decision": flag and park — these become new `decision_needed` items in the matrix

### Q5: Intentional Deviations

The Opus synthesis layer handles this via a three-step check:

1. **Explicit VTR check**: Search the requirement and its parent epic for VTR (Value Trade-off Record) entries. If a VTR exists that explains the deviation → mark as "intentional (VTR-NNN)" in the report
2. **Multi-flow check**: If the requirement serves flows beyond the current cluster, read those flows' frontmatter to check if the "deviation" is actually a compromise serving another flow → mark as "intentional (serves FLOW-XXX)"
3. **Requirement audit trail**: Check if the requirement's `requirements.md` YAML has a `rationale` or inline note explaining the choice → mark as "intentional (documented)"

If none of these checks trigger → flag as "unintentional gap" for remediation.

**UX for the user**: The report categorizes findings as:

```
CONFIRMED GAPS (remediation recommended):
  Gap #1, item D: client-copy indicator — not in requirement, no VTR, no multi-flow conflict
  → Recommend: add to SEC-09 acceptance criteria

INTENTIONAL DEVIATIONS (no action needed):
  Gap #4, item C: warm confirmation text — VTR-012 documents minimal feedback preference
  → No change; VTR explains deliberate brevity

NEEDS YOUR DECISION:
  Gap #7, item E: grey-zone duration — requirement says 10s, flow says 5s, no documented reason
  → Which value should the requirement use?
```

### Q6: Integrate vs. Separate

**Recommendation: Integrate remediation into `requ-verify-flow-coverage` as an optional Phase 2.**

Rationale:
- Verification and remediation share all the same context (gap extractions, requirement readings)
- A separate skill would need to re-read everything → wasteful
- The user can opt out of remediation ("verify only") if they just want the report
- The skill becomes a two-phase workflow: Phase 1 = verify + report, Phase 2 = remediate (user-gated)

Structure:
```
Phase 1: Verify (always runs)
  → per-gap agents extract
  → Opus synthesizes
  → report written
  → findings presented to user

User gate: "Do you want to remediate the confirmed gaps?"
  Yes → Phase 2
  No → skill terminates

Phase 2: Remediate (user-approved)
  → for each confirmed gap: propose specific change
  → user approves per-change or batch
  → Sonnet agents update requirements
  → re-verify changed items (quick re-read, no Opus needed)
  → updated report written
```

### Q7: Quantitative Metrics

Yes, there IS a useful quantitative layer. The per-gap extraction in Layer 1 naturally produces a **behavior checklist** from the gap description:

**Metric 1: Behavior Coverage Ratio**
- Extract discrete behaviors/constraints from each gap description (the extraction agents already do this)
- Count: found in requirement vs. not found
- Per gap: "5 of 8 behaviors covered (62%)"
- Per bundle: "34 of 41 behaviors covered (83%)"
- Per cluster: aggregate

**Metric 2: AC Coverage**
- Count how many trackable ACs in the requirement were created/filled by the exploration task
- Compare against what the gap description expects
- "Requirement has 13 ACs; 11 map to flow behaviors; 2 are not traceable to any flow gap"

**Metric 3: Cross-reference completeness**
- Count how many cross-references the gap description mentions (e.g., "reference REQ-FUNC-017 Section 4.2")
- Check if those cross-references actually exist in the requirement
- "3 of 4 required cross-references present"

**Metric 4: Foundation linkage**
- For gaps that depend on foundations: check if the requirement references the foundation requirement
- "Foundation F1 referenced: yes/no"

These metrics are included in the coverage report as both per-gap scores and aggregate summary.

### Q8: Concrete Modifications Needed

#### A. Modifications to `requ-derive-from-flow`

**Where**: Phase 4, after all exploration goal.md files are created (new Phase 4.5)

**New Phase 4.5: Create Verification Tasks**

1. Group all created exploration tasks by their `target_package` (= bundle)
2. For each bundle:
   a. Collect all task IDs created for this bundle
   b. Collect the gap numbers belonging to this bundle
   c. Generate a verification goal.md using the template from Q3
   d. Set `depends_on` to ALL task IDs in this bundle
   e. Set urgency/impact to match the bundle's values
   f. Invoke `task-create` skill for each verification task
3. Update Pipeline Status table: add verification task rows with status "created", marker "V" or distinct notation
4. Update Phase 4.3 output summary to include verification tasks created

**Estimated additions to skill**: ~40-50 lines (Phase 4.5 section + template reference)

#### B. Major Rewrite of `requ-verify-flow-coverage`

The current skill is a simple "read matrix → check done gaps → write report" flow. It needs to become a full multi-phase skill with Opus integration. The new structure:

```
Phase 0: Resolve Context
  - Detect invocation mode: bundle (from goal.md) vs. standalone (user command)
  - If standalone without task: call task-create
  - Read goal.md to extract verification_bundle, verification_gaps, source_matrix
  - OR (standalone): read matrix, prompt user for scope

Phase 1: Gather (Sonnet, per-gap agents)
  - For each gap: spawn agent to read flow excerpt + requirement → produce structured extraction
  - Foundation gaps: also check dependency linkage

Phase 2: Synthesize (Opus)
  - claude-switch-opus with all extractions
  - Cross-cutting analysis, coherence check, intentional deviation detection
  - Produce categorized findings: confirmed gaps / intentional deviations / needs decision

Phase 3: Report (Sonnet)
  - Write coverage report to plans_and_protocols/
  - Include quantitative metrics
  - Present findings to user

Phase 4: Remediate (Sonnet, user-gated)
  - User approves remediation scope
  - Per-requirement agents update requirements
  - Quick re-verify
  - Update report
```

**Estimated skill length**: ~80-100 lines (aggressive token-efficiency required; templates referenced, not embedded)

#### C. Minor changes elsewhere

1. **`claude-route`**: Add detection for verification tasks (check `verification_task: true` or `verification_bundle` field in goal.md frontmatter → invoke `requ-verify-flow-coverage` instead of `requ-explore`)
2. **`task-create`**: May need awareness of verification task type (or just treat as regular explore task — the frontmatter fields are custom and don't break anything)
3. **`next_tasks.py`**: No changes needed — `depends_on` blocking already works correctly
4. **Task ID allocation**: Verification tasks use regular task ID allocation (V-prefix was considered but adds complexity; just use TASK-FUNC-007-XX with a `verification_task: true` flag in frontmatter)

---

## Execution Plan

### Phase A: Modify `requ-derive-from-flow` (1 agent)

**Agent type**: implementation-engineer

1. Read current `requ-derive-from-flow/skill.md`
2. Add Phase 4.5 after Phase 4.4 (Wire Dependencies)
3. Phase 4.5 creates verification goal.md tasks per bundle:
   - Group created tasks by `target_package`
   - For each bundle: create verification goal.md with the template
   - Set `depends_on` to all bundle task IDs
   - Call `task-create` skill
   - Update Pipeline Status
4. Update Phase 4.3 output summary to mention verification tasks
5. Ensure the verification goal.md template includes all needed frontmatter fields

### Phase B: Rewrite `requ-verify-flow-coverage` (1 agent)

**Agent type**: implementation-engineer

1. Read the current `requ-verify-flow-coverage/skill.md`
2. Rewrite completely with the new multi-phase structure:
   - Phase 0: Context resolution (bundle mode vs. standalone)
   - Phase 1: Per-gap extraction agents
   - Phase 2: Opus synthesis
   - Phase 3: Report with quantitative metrics
   - Phase 4: User-gated remediation
3. Keep under 100 lines (token efficiency)
4. Ensure standalone invocation path works (auto-create task if needed)

### Phase C: Update `claude-route` (1 agent, can run in parallel with A+B)

**Agent type**: implementation-engineer

1. Read `claude-route/skill.md`
2. Add detection logic: if goal.md has `verification_bundle` or `verification_task: true` → invoke `requ-verify-flow-coverage` (not `requ-explore`)
3. Keep change minimal

### Phase D: Update INDEX.md description (trivial, done with Phase B)

Update the one-line description for `requ-verify-flow-coverage` if the current one no longer reflects the expanded scope.

---

## Quality Criteria

- [ ] `requ-derive-from-flow` Phase 4.5 creates verification tasks with correct `depends_on` lists
- [ ] Verification tasks are blocked by `next_tasks.py` until all bundle exploration tasks complete
- [ ] `requ-verify-flow-coverage` handles both bundle mode (from goal.md) and standalone mode
- [ ] Per-gap agents read only relevant flow excerpts (not entire flows) to stay within context
- [ ] Opus synthesis identifies cross-cutting issues, not just per-gap results
- [ ] Quantitative metrics (behavior coverage ratio) appear in the report
- [ ] Remediation phase is user-gated and handles intentional deviations
- [ ] `claude-route` correctly dispatches verification tasks to the verification skill
- [ ] Skill files stay under 100 lines each (token efficiency)
- [ ] No changes needed to `next_tasks.py` or other infrastructure scripts

## Risks

1. **Per-gap agents may read the wrong flow excerpt**: Mitigation — the goal.md's gap table includes "Source in Flow" references (e.g., "FLOW-002 Steps 1–4") which agents use to locate exact sections
2. **Opus synthesis context may still be large for clusters with 20+ gaps**: Mitigation — structured extractions are ~200 words each; 20 × 200 = 4K words ≈ 6K tokens. Well within Opus window even with matrix summary
3. **Remediation may introduce conflicts with other requirements**: Mitigation — Opus categorizes changes as "safe" vs. "needs review"; user confirms before any write
4. **Foundation tasks shared across bundles may complicate depends_on**: Mitigation — each foundation task belongs to ONE bundle (the highest-priority one). Other bundles' tasks that depend on it are individually blocked via their own `depends_on` lists (already wired in Phase 4.4)
5. **Task ID allocation for verification tasks**: Mitigation — use regular allocator. The verification task's parent_requirement should be the nearest common ancestor of the bundle's gaps (usually an epic-level REQ). If gaps span multiple epics → use the cluster's primary flow's epic as parent

---

## Summary

- **Plan file**: This file
- **Execution agents needed**: 3 (Phases A, B, C can run in parallel; Phase D is trivial merge with B)
- **No infrastructure script changes** — the `depends_on` mechanism already handles ordering
- **Key insight**: Bundle-based verification tasks with `depends_on` lists are the simplest, most robust integration point — they piggyback on the existing task ordering system without any priority hacks
