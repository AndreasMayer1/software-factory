# Audit Findings — Release 0.0.1 Preparation
Date: 2026-03-06
Agent: claude-sonnet-4-6 (main session)
Status: PENDING USER DECISIONS — task creation blocked

---

## 0.0.1 Release Scope (from RELEASES.md)

Name: Alpha — Data Transfer
Description: Proof of concept for QR code data beam between therapist and client devices (unencrypted).

Includes:
- QR code generation (therapist side)
- QR code scanning and plan reception (client side)
- Basic plan serialization/deserialization
- Role selection (Client / Therapist)

---

## Requirement Audit

### REQ-FUNC-007 — Epic: Secure Data Transfer
- Status: defined
- 0.0.1 items: AC-07 only ("QR Data Beam supports adjustable animation speed")
- Task coverage: Epic-level → no impl tasks required (per REQ-PROC-009 epic rules)
- Assessment: OK at epic level. Sub-features (007-01, 007-02) have issues — see below.
- Pending task: TASK-FUNC-007-03 (analysis pipeline) is `pending` — designed for full encrypted version

### REQ-FUNC-007-01 — Therapist Transfer UI
- Status: draft
- 0.0.1 items: SEC-04 only (Transfer Flow - Local Data Beam)
- Task coverage: NONE (existing pipeline TASK-FUNC-007-03→06 is pending and designed for encrypted version)
- Issue: No implementation tasks exist. Pipeline is complex and designed for 0.0.2+ encrypted flow.

### REQ-FUNC-007-02 — Plan Receiving (Client-Side)
- Status: defined
- 0.0.1 items: AC-03 (accurate progress indicator), AC-08 (decline plan without saving)
- Task coverage: NONE
- Issue: Same pipeline dependency as 007-01.

### REQ-FUNC-014 — Epic: Plan Management
- Status: in_progress
- 0.0.1 items: SEC-07 only (Export a Plan for a Client)
- Task coverage: NONE for SEC-07 (existing tasks are explore/analyze at epic level)
- Issue: SEC-07 is the trigger that opens the transfer dialog (REQ-FUNC-007-01). Needs impl task.
- Note: All other sections (SEC-01–06, 08, 09) are 0.2.0.

### REQ-NFUNC-001 — Data Model Versioning
- Status: defined
- 0.0.1 items: ALL 5 ACs (export version field, import matching, migration function, older version migration, newer version error)
- Task coverage: CRITICAL GAP — no tasks directory exists at all
- Action required: Create impl task.

### REQ-NFUNC-010 — In-Detail Navigation
- Status: implemented
- 0.0.1 items: All sections
- Task coverage: Explore task completed (2026-01-02_explore_investigate-in-detail-navigation)
- Assessment: Already implemented. No new impl task needed. Existing completed explore task is sufficient.

### REQ-NFUNC-011 — Main Navigation
- Status: implemented
- 0.0.1 items: All sections
- Task coverage: impl task completed (2026-01-02_impl_update-navigation-guidelines at navigation_patterns level)
- Assessment: Covered.

### REQ-NFUNC-012 — Growth Tree Theme
- Status: draft (but completed: 2026-01-25)
- 0.0.1 items: AC-05 (Simple Mode animations), AC-08 (components support both modes), AC-09 (tokens.json), AC-10 (design_tokens_builder), AC-11 (pre-processing script), AC-12 (duration tokens per theme), AC-13 (token hierarchy), AC-14 (theme in Hive), AC-15 (AppThemeExtension)
- Task coverage: Multiple impl tasks completed (design token migration series, 2026-01-16)
- Issue: Status inconsistency — `status: draft` but `completed: 2026-01-25`. Need to confirm 0.0.1 ACs are covered.

### REQ-NFUNC-014 — Responsive Layout Master-Detail
- Status: implemented
- 0.0.1 items: All sections
- Task coverage: Multiple impl tasks completed (refactor series 2025-09, 2025-10, 2025-12)
- Assessment: Fully covered.

### REQ-NFUNC-016 — Local Database Technology
- Status: defined
- 0.0.1 items: All 7 ACs (technology selection, encryption, cross-platform, field lookup, abstraction layer, migration path)
- Task coverage: Explore task exists but PENDING (TASK-NFUNC-016-01)
- Issue: Explore task not started, no impl tasks. This is a hard dependency for REQ-FUNC-007-01 and 007-02.

---

## Scope Gaps

### Gap 1 — Role Selection (CRITICAL)
RELEASES.md 0.0.1 requires: "Role selection (Client / Therapist)"
REQ-FUNC-011 (User Onboarding & Role Selection):
- target_release: "0.1.0" for ALL ACs
- Full v2 onboarding requires security setup — excluded from 0.0.1
- v1 implementation (2025-10-01) used a simpler flow without mandatory security for clients

No requirement is currently assigned to 0.0.1 for role selection. This is a scope gap.

### Gap 2 — Plan Availability for PoC
For the therapist to trigger SEC-07 (export plan for client), a plan must exist.
Full plan creation/editing (REQ-FUNC-014 SEC-01–05) is 0.2.0.
For the 0.0.1 PoC, a plan must come from somewhere (seeded data? existing codebase?).
This gap is unresolved.

---

## Open Questions for User

### Q1 — Architecture Decision (BLOCKS task creation for 007-01, 007-02, 014-SEC-07)
0.0.1 is an "unencrypted proof of concept". The existing requirements for REQ-FUNC-007-01 and
007-02 were designed for the full encrypted architecture (AES-256-GCM, BIP-39 pairing, etc.).
The existing task pipeline (TASK-FUNC-007-03→06) was built for that full version.

Two options:
(A) SIMPLIFIED: Implement Data Beam WITHOUT encryption for 0.0.1. JSON → QR chunks → scan → display.
    No pairing flow. Pro: matches PoC intent, simpler. Con: some code will be replaced in 0.0.2.
(B) FULL ARCHITECTURE: Implement the full encrypted transfer architecture immediately.
    Pro: no throwaway code. Con: significantly more complex for 0.0.1; blocks on REQ-FUNC-006.

Which option?

=> Create new tasks that instruct implementation without encryption like defined for the release. How the UI looks is secondary, it's a proof of concept that the plans that currently exist in the app can be transfered via qr code. Make sure to include the data compression - it's likely that we need that.

### Q2 — Role Selection Gap Resolution
Options:
(A) Create new minimal requirement "Basic Role Selection (0.0.1)": role choose → navigate to
    role-specific home, no security setup. New requirement ID (e.g. REQ-FUNC-011-01).
(B) Reassign REQ-FUNC-011 ACs (AC-01–05, AC-08) to 0.0.1 (removing security-setup dependency
    from these ACs for the PoC phase).
(C) Confirm role selection is already implemented (v1 from 2025-10-01) and just needs
    a tracking task, not new code.

Which option?

=> (C) works, because it is already implemented (I know that). It doesn't look like it should in the app in the end, the UI is different, but the user can select a role. 

### Q3 — Plan Availability for PoC
For the 0.0.1 PoC, where does the therapist's plan come from?
(A) Use existing codebase plan templates (already seeded in the app)
(B) Create a minimal plan seeder as part of the PoC
(C) The therapist can create a plan manually (would require some SEC-01–05 from REQ-FUNC-014)

=> (A) Use  the currently existing plan templates.

### Q4 — REQ-NFUNC-012 Status
Status is `draft` but `completed: 2026-01-25`. Multiple design token impl tasks are completed.
Should the status be updated to `implemented` (assuming 0.0.1 ACs are covered)?
If not, which 0.0.1 ACs are NOT yet implemented?

=> It's not completed, I removed that from the requirement. Nothing to do.

### Q5 — REQ-NFUNC-010 Task Coverage
REQ-NFUNC-010 (in-detail navigation) is `implemented` but only has an explore task, no dedicated
impl task. The parent-level impl task (navigation-guidelines) may cover it.
Is this sufficient, or should a tracking impl task be created?

=> The requirement files says: "**COMPLETE** - This requirement is fully documented based on codebase investigation.". So nothing to do.

---

## Summary — What Blocks Task Creation

| Blocker | Required Decision |
|---------|-----------------|
| Q1 (Architecture) | Must decide before creating 007-01, 007-02, 014-SEC-07 tasks |
| Q2 (Role selection) | Must decide before creating role selection tasks |
| Q3 (Plan for PoC) | Must decide before scoping 014-SEC-07 task |
| Q4 (NFUNC-012 status) | Clarification needed before closing this requirement |
| REQ-NFUNC-001 task | Can be created immediately — no open decisions |
| REQ-NFUNC-016 explore | Can be started immediately (TASK-NFUNC-016-01 pending) |
