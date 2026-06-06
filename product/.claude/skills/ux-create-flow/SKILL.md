---
name: ux-create-flow
description: Create, iterate, or approve a user flow
tools: "*"
model: inherit
---

## CRITICAL: THIS SKILL IS A ROUTER ONLY

**YOU MUST NOT DO ANY WORK HERE. YOUR ONLY JOB IS TO CALL ONE OF THESE THREE SKILLS:**

```
Skill("ux-flow-draft",   args: "<user's original message> | flow: <FLOW-ID or path>")
Skill("ux-flow-complete", args: "<user's original message> | flow: <FLOW-ID>")
Skill("ux-flow-approve",  args: "<user's original message> | cluster: <cluster name or FLOW-IDs>")
```

**FORBIDDEN — do not do any of the following:**
- Read flow.md or any other file
- Use the Read, Glob, Grep, or Bash tools
- Execute flow steps or load context
- Ask clarifying questions (except the one ambiguity case below)

**WRONG:** Reading flow.md to understand the flow, then deciding what to do.
**RIGHT:** Determine target skill from the message alone → call Skill tool → stop.

---

## Step 0: Sync FLOW_INDEX

Run `python3 scripts/user_needs/sync_flow_index.py` (use Bash tool). This ensures any status check in Step 1 reads accurate data.

## Step 1: Determine Target Skill (from message only)

**Only ask for clarification when the user's intent is genuinely ambiguous** (e.g. bare "FLOW-003" with no other context). If the message clearly signals intent, dispatch immediately without asking.

| Signal in user message | Target skill |
|------------------------|--------------|
| "jointly approve" / multiple FLOW-IDs + "approve" | **ux-flow-approve** |
| "content complete FLOW-NNN" / "I'm done" / "approve FLOW-NNN" / user answered "yes" to approval question | **ux-flow-complete** |
| FLOW-ID + revision intent (improve, verbessern, add, change, fix, fehlt, nochmal, update, iteration, feedback, missing) | **ux-flow-draft** |
| FLOW-ID + approval/derive intent (jointly approve, approve cluster, derive requirements, requirements ableiten) | **ux-flow-approve** or **requ-derive-from-flow** |
| FLOW-ID or task path provided (no other signal) — check flow status (read ONLY the YAML frontmatter `review_status` field, nothing else): `draft`/`in_review`/`pending_alignment` → **ux-flow-draft**; `aligned` → ask (a)/(b) below; `approved` → ask (a)/(b) below |  |
| No FLOW-ID, no path, no context → NEW flow | **ux-flow-draft** |

**The ONLY permitted file read in this skill:** If you need to know the flow's `review_status` and cannot determine it from the message, read ONLY the YAML frontmatter block of the flow.md (first ~30 lines). Nothing else.

### Ambiguous intent for `aligned` flows — ask once:

> "FLOW-[ID] ([name]) is aligned (awaiting joint approval). What would you like to do?
> (a) **Revise the flow** — returns to in_review.
> (b) **Start joint approval** — use ux-flow-approve instead.
> Reply (a) or (b)."

- (a) → ux-flow-draft; (b) → ux-flow-approve

### Ambiguous intent for `approved` flows — ask once:

> "FLOW-[ID] ([name]) is approved. What would you like to do?
> (a) **Revise the flow** — returns to in_review and goes through the full review cycle again.
> (b) **Derive requirements** — use requ-derive-from-flow (flow content stays unchanged).
> Reply (a) or (b)."

- (a) → ux-flow-draft; (b) → requ-derive-from-flow

---

## Step 2: Call the Skill tool and stop

Pass the user's full original message as args, plus `flow: <FLOW-ID>` if known. Do not add anything else.

---

## Reference: Flow Status State Machine

(For context only — you do not execute these transitions. The sub-skills do.)

| From status | Trigger | Guard | To status | Skill |
|-------------|---------|-------|-----------|-------|
| (none) | NEW mode | — | draft | ux-flow-draft |
| draft / in_review | CONTINUE | — | in_review | ux-flow-draft |
| pending_alignment | CONTINUE | — | in_review | ux-flow-draft |
| in_review | content complete | no sibling impacts | approved | ux-flow-complete |
| in_review | content complete | sibling impacts exist | aligned | ux-flow-complete |
| aligned | sibling CONTINUE identifies impact | — | pending_alignment | ux-flow-complete |
| draft / in_review / pending_alignment | sibling CONTINUE identifies impact | — | pending_alignment | ux-flow-complete |
| approved | sibling CONTINUE identifies impact | user confirms rollback | pending_alignment | ux-flow-complete |
| approved | sibling CONTINUE identifies impact | user declines rollback | approved (no change) | ux-flow-complete |
| aligned | joint approve | all cluster flows aligned, no Pending Impacts remain | approved | ux-flow-approve |

**Illegal transitions** (sub-skills enforce these):
- approved → any status without explicit user confirmation
- aligned → approved without joint approve
- any → approved while `## Pending Impacts` section exists in flow.md

## Guard Rails

- Never create a duplicate flow. If uncertain, ask.
- Never modify an existing flow without explicit user confirmation.
- Never set status to `approved` while `## Pending Impacts` exists in flow.md.
- Never approve an `aligned` flow directly — joint approval required.

## Canon Check (pass-through)

When new step labels introduce a user-facing noun/verb/state not in `concept_canon.yaml`, pass this in args to `ux-flow-draft` so it invokes `ux-write-canon-concept`.
