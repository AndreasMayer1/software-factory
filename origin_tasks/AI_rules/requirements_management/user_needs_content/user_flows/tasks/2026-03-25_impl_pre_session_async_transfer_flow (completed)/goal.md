---
task_id: TASK-PROC-039-01
type: impl
parent_requirement: REQ-PROC-039
urgency: 3
urgency_reason: U3-WORKFLOW-GAP
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-04-19
session_completed_at: 2026-04-19T17:47:24Z
started: 2026-03-26
session_id: 4a5f00c4-f641-40e8-b328-491df6564dac
session_account: web
effort: M
created: 2026-03-25
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-02, SEC-03]
scope_description: "Create and approve FLOW-004 (Flexible Data Transfer) for Prof. Dr. Weber / async-preference therapists; then jointly approve FLOW-003 and derive requirements from both flows together"
release_description: ""
related_flows:
  - FLOW-003
  - FLOW-004
requirements_version:
  commit: a56db665
  file: ../requirements.md
---

# Goal: Write User Flow — Flexible Data Transfer (FLOW-004)

> **Note**: The flow was created as FLOW-004 "Flexible Data Transfer" (broader scope than the original "Pre-Session Async Transfer" name — covers Weber's primary use case but also serves all therapist personas as an alternative transfer path).
> **Flow file**: `requirements_user_needs/user_flows/flexible_data_transfer/flow.md`

## Objective

Create `requirements_user_needs/user_flows/flexible_data_transfer/flow.md` using the **`ux-create-flow` skill**. Iterate until the user approves the flow.

When this flow reaches `review_status: approved`, **also approve FLOW-003 at the same time** — both flows share the same transfer UI surfaces and must be approved together before any requirements are derived. See decision rationale below.

## Current State (2026-03-25)

- **This flow**: Not yet created. Entry exists in `FLOW_INDEX.md` under "Needed Flows" with key questions, trigger, and related flows documented there. Read that entry before starting.
- **FLOW-003** (`requirements_user_needs/user_flows/session_start_data_transfer/flow.md`): Fifth iteration complete. User is satisfied with the content. Approval is intentionally deferred — see decision rationale below.

## Decision: Joint Approval (Option B)

FLOW-003 and the Pre-Session Async Transfer flow both influence the same transfer UI surfaces on the client side (the "Transfer Section" entry point, Transfer Detail Screen, and scope controls). If FLOW-003 were approved and requirements derived in isolation, the transfer UI requirements would be incomplete — the async delivery mechanism (file export, notification reminder, etc.) and any shared navigation architecture would be missing.

**Decision (2026-03-25)**: Wait until both flows are approved, then:
1. Approve FLOW-003 (`review_status: approved`)
2. Approve this flow (`review_status: approved`)
3. Run `requ-derive-from-flow` on both flows together as context flows

Note: FLOW-002 (Instruct Client on Protocol) will also need a consistency review once both transfer flows are approved — the therapist side of FLOW-002 shares personas with both transfer flows.

## Context

- Primary persona: Prof. Dr. Weber (PERSONA-011) — no in-room technology by clinical design (DEV-1 in FLOW-003)
- Also covers: any async-preference therapist
- Related: FLOW-003 (in-room QR path, which cannot serve Weber)

## Scope

- Create and iterate the flow using `ux-create-flow`
- Update `FLOW_INDEX.md` when the flow is created (move from Needed → Existing Flows)
- Stop when user approves (`review_status: approved`) — then jointly approve FLOW-003
- Requirements derivation (`requ-derive-from-flow` on both flows together) is out of scope here — happens after joint approval
