---
name: ux-flow-approve
user-invocable: false
description: "[Internal — use ux-create-flow] Joint approval for an aligned flow cluster"
tools: Read, Write, Bash, Glob, Grep, Agent
model: inherit
---

⚠ STOP — INTERNAL SKILL. Entry point is `ux-create-flow`.

If the **user** invoked this skill directly (not delegated here by `ux-create-flow`):
**Do NOT proceed with any steps below.** Instead call `Skill("ux-create-flow")` with the user's original message as args, then stop.

---

You run joint approval for a cluster of aligned user flows.

## JA-A. Pre-flight check

Read each named flow's flow.md. Check:

1. **All flows must be `aligned`**: If any is not → block and report: "FLOW-[ID] is [status], not aligned. Complete its CONTINUE pass first."

2. **No `## Pending Impacts` sections may remain**: If any flow still contains `## Pending Impacts` → block and report: "FLOW-[ID] still has unresolved Pending Impacts — run CONTINUE on it first."

If both checks pass → proceed to JA-B.

## JA-B. Set all cluster flows to approved

For each flow in the cluster:
- Set `review_status: approved`
- Add `review_history` entry: `seq: [N], from: aligned, to: approved, reviewer: Human, notes: "Joint approval with cluster: [FLOW-IDs]. All sibling flows reviewed and aligned."`

## JA-C. External impact analysis (cluster flows excluded)

Identify candidate external flows (same logic as CC-A in ux-flow-complete, but **exclude** all flows in the approval cluster — they are already aligned).

Run Sonnet assessment on external candidates (same as CC-B in ux-flow-complete).

For each external flow with `impact: yes`: apply the same Case A/B logic from CC-E/CC-F in ux-flow-complete (Pending Impacts or task creation). These are external flows, not cluster members — no joint approval context applies.

## JA-D. Commit + Output

```bash
git add requirements_user_needs/ requirements_tasks/
git commit -m "ux(FLOW-A,FLOW-B): joint approval — [cluster name]"
```

Output:
```
=== JOINT APPROVAL COMPLETE ===

Flows approved: FLOW-[IDs]
Date: [today]

External cross-flow impacts:
- [if any] FLOW-[ID]: [description] → task/pending impacts created

Next step: Derive requirements from all approved flows together
→ Use: requ-derive-from-flow with all [N] flows as input
If flow(s) have a `release_scope` field → use task-create skill to create a task:
  type: impl, urgency: 5, body: "Run `release-plan → Action 4b`. Source: [flow path(s)]."
```
