---
name: ux-flow-complete
user-invocable: false
description: "[Internal — use ux-create-flow] Content-complete impact analysis for a flow"
tools: Read, Write, Bash, Glob, Grep, Agent
model: inherit
---

⚠ STOP — INTERNAL SKILL. Entry point is `ux-create-flow`.

If the **user** invoked this skill directly (not delegated here by `ux-create-flow`):
**Do NOT proceed with any steps below.** Instead call `Skill("ux-create-flow")` with the user's original message as args, then stop.

---

You run the content-complete impact analysis for a user flow.

## Pre-check: Verify flow is in_review

Read the flow's `review_status`. If it is not `in_review`, block and report:
"FLOW-[ID] has status [status], not in_review. Complete a CONTINUE pass (ux-flow-draft) first to advance the flow to in_review before signaling content complete."

---

## CC-0. Check for existing cluster membership

Read the flow's YAML frontmatter. If `approval_cluster` is already set:
- This flow will go to `aligned` (not `approved`) regardless of what the impact analysis finds
- The impact analysis (CC-A through CC-B) still runs for **all flows**, including cluster members — they are not exempt
- Proceed to CC-A normally

If `approval_cluster` is not set: proceed normally — impact analysis determines whether flow goes to `approved` or `aligned`.

## CC-A. Identify candidate sibling flows

Read `requirements_user_needs/user_flows/FLOW_INDEX.md`. Identify candidates:
- Flows modeling the reverse direction of the same interaction
- Flows in the same domain cluster or sharing structural similarities
- Flows referencing the same epics/features
- Flows serving overlapping personas or scenarios

When in doubt, include rather than exclude.

## CC-B. Sonnet agents for impact assessment

For each group of up to 3 candidate flows, spawn a **Sonnet subagent** (Agent tool, model: sonnet):

Provide:
- List of `flow.md` paths for this batch
- A summary of this flow: its purpose, happy path key steps, new exceptions or edge cases

Instruction: "For each flow.md: read it fully. Assess whether the changes in FLOW-[NNN] affect this flow. Consider: reverse-direction interactions, shared exceptions, shared assumptions, structural similarities. Return for each: flow_id, impact: yes/no, and if yes a concrete description of which steps/exceptions/edge cases are affected and how."

Do NOT read the raw flow.md files in the main session — use only the Sonnet summaries.

## CC-C. Decision: no impacts → directly approved

If Sonnet found **no impacts** on any candidate:
- Set `review_status: approved` in flow.md
- Add `review_history` entry: `seq: [N], from: in_review, to: approved, reviewer: Human, notes: "Approved by user. No cross-flow impacts detected."`
- Commit: `git commit -m "ux(FLOW-NNN): approve [flow name]"`
- Output: `=== FLOW APPROVED === No cross-flow impacts detected.`
- **Stop here** — do not continue to CC-D.

## CC-D. Set status to aligned (impacts exist)

- Set `review_status: aligned` in flow.md
- Add `review_history` entry: `seq: [N], from: in_review, to: aligned, reviewer: Human, notes: "Content approved by user. Pending joint approval with sibling flows: [FLOW-IDs]"`
- If `approval_cluster` is **not already set** in flow.md YAML: set `approval_cluster: FLOW-[NNN]` (this flow's own FLOW-ID). If it is already set, preserve the existing value — do not overwrite it.

## CC-E. Process each impacted sibling flow

For each flow where Sonnet returned `impact: yes`:

**Check: is the sibling flow currently `approved`?**

Spawn a Sonnet subagent: read the sibling flow's `review_status` and `review_history`. Return: current status, whether it was ever set to `approved`.

**If sibling is `aligned`**:
No user confirmation needed (`aligned` is not yet final — no joint approval has occurred).
- Set `review_status: pending_alignment` directly
- Add `review_history` entry: `seq: [N], from: aligned, to: pending_alignment, notes: "Rolled back: sibling FLOW-[NNN] content complete identified impact. Pending impacts to incorporate."`
- Proceed to add `## Pending Impacts` as usual

**If sibling is `approved`**:
Ask user: "FLOW-[ID] ([name]) is `approved` but is affected by this flow's changes. Roll back to `pending_alignment`? (y/n)"
- Yes → set `review_status: pending_alignment`, add `review_history` entry: `seq: [N], from: approved, to: pending_alignment, reviewer: LLM, notes: "Rolled back: sibling FLOW-[NNN] content complete identified impact. Pending re-alignment."`. Proceed to add `## Pending Impacts`.
- No → only create a task (no status change). Flag to user: "FLOW-[ID] stays approved — task created as reminder."

**If sibling is `draft`, `in_review`, or `pending_alignment`**:
No status change needed. Proceed to add `## Pending Impacts`.

**Add `## Pending Impacts` to sibling flow.md** (all cases except user said "No" to rollback):
```markdown
## Pending Impacts

> These impacts were identified when FLOW-[NNN] reached content_complete status.
> Address them in the next CONTINUE iteration of this flow.

### From FLOW-[NNN] ([name]) — content complete [date]
[Haiku impact description verbatim]
```

Also set `approval_cluster` in sibling flow.md YAML frontmatter — use the same value that was set (or already existed) in the source flow's `approval_cluster` field (a FLOW-ID, e.g. FLOW-010). If the sibling already has `approval_cluster` set to a different value, keep the existing value and flag to the user: "FLOW-[sibling-ID] is already in cluster [existing-value] — manual cluster merge may be needed."

**Alignment loop escape hatch**: If the user signals that further alignment iterations yield no new insights (e.g. "force align", "accept current state", "set all to aligned"), set all cluster flows directly to `aligned` without further impact analysis and proceed to joint approval. This is a deliberate user override.

## CC-F. Create CONTINUE tasks for impacted siblings

For each sibling that received a `## Pending Impacts` entry:

**Check if an open task already exists**: Grep `requirements_tasks/process/AI_rules/requirements_management/user_needs_content/user_flows/tasks/` for goal.md files referencing this sibling flow ID. If found → append `## Additional Impact from FLOW-[NNN]` to that task's goal.md. If not found → create new task.

New task location: `requirements_tasks/process/AI_rules/requirements_management/user_needs_content/user_flows/tasks/[today]_impl_align_[sibling_name]_with_[source_name]/`

Task goal.md template:
```markdown
## Context
FLOW-[NNN] ([name]) reached content_complete on [date].
Cross-flow impact analysis identified that this flow needs alignment.

## Known Impact (at task creation)
[Haiku impact description verbatim]

## Source Flow
- Flow: FLOW-[NNN]
- Path: requirements_user_needs/user_flows/[source_name]/flow.md
- Content complete: [date]

## Steps
1. Run CONTINUE on this flow (ux-create-flow CONTINUE MODE)
   - Sibling flow FLOW-[NNN] is in pending_alignment — it will be auto-read as context (Step 6)
   - Address all entries in the ## Pending Impacts section
2. When CONTINUE is done: this flow is in in_review — signal "content complete" when satisfied
3. When ALL cluster flows are aligned: run Joint Approval
```

## CC-G. Commit + Output

```bash
git add requirements_user_needs/ requirements_tasks/
git commit -m "ux(FLOW-NNN): content complete, aligned"
```

Output:
```
=== FLOW CONTENT COMPLETE ===

Flow: FLOW-[NNN] ([name])
Status: aligned
Date: [today]

Cross-flow impact analysis:
- Flows analyzed: [N]
- Impacts found: [M]

Sibling flows requiring CONTINUE (in recommended order):
1. FLOW-[ID] ([name]) — [brief impact reason]
   Status: pending_alignment
   → ## Pending Impacts added to flow.md
   → CONTINUE task: [path]
2. FLOW-[ID] ([name]) — [brief impact reason]
   ...

⚠ BEFORE JOINT APPROVAL — complete these steps in order:
[ordered list: CONTINUE on each sibling, then joint approve]

When ready: "approve FLOW-[IDs] jointly"
```

The recommended order in the output is: flows whose `## Pending Impacts` depend on other flows' CONTINUE results should come later (topological order where detectable from impact descriptions).
