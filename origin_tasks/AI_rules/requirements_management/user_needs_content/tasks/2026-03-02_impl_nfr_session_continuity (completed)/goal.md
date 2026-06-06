---
task_id: TASK-PROC-027-35
type: impl
parent_requirement: REQ-PROC-027
urgency: 2
urgency_reason: U2-NICE
impact: 3
impact_reason: I3-UX
status: completed
completed: 2026-03-03
effort: S
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-05]
scope_description: "Document session continuity as a non-functional requirement — app must not require re-authentication during active use"
requirements_version:
  commit: c5117c0
  file: ../requirements.md
---

# Goal: Document NFR — Session Continuity During Active Use

## Objective

Formally document a non-functional requirement surfaced by the declined scenario *"The Login Rupture"* (Prof. Dr. Weber, PERSONA-011): the app must not interrupt an active session with authentication prompts, timeouts, or login screens.

## Background

Prof. Weber uses the app during psychoanalytic sessions. Therapeutic silence is a clinical tool — an unexpected re-authentication prompt (session timeout, biometric re-prompt, OS lock) destroys that silence and disrupts the therapeutic frame. This is also relevant for Dr. Sarah (mid-session protocol review) and Dr. Turan (patient data lookup during consultation).

This was declined as a standalone scenario because it does not describe a status-quo problem with analog tools — it is a reliability constraint on the digital product. It belongs in requirements.md as an NFR.

## NFR to Document

**NFR-SESSION-001: Session Continuity**

> The app must not require re-authentication or display login prompts during an active session view. An "active session" is defined as any screen where patient data is being viewed or entered. The app's session timeout must be configurable per user role and must default to "never timeout during active use." Re-authentication is only required when the app is foregrounded after being backgrounded for more than N minutes (configurable, default: 30 min for therapists, 10 min for self-users).

**Affected personas**: Prof. Dr. Weber (PERSONA-011), Dr. Sarah (PERSONA-001), Dr. med. Turan (PERSONA-012)

**Implementation implications**:
- Session timeout must be decoupled from OS screen lock
- Therapist role: longer timeout default (30 min) to cover full sessions
- The re-auth prompt must never appear mid-entry or mid-review (only on app resume from background)

## Target Location

Add to `requirements.md` under a Non-Functional Requirements section (create if it does not exist), or to an existing reliability/security section if one is present.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Declined scenario: *The Login Rupture* (Prof. Weber perspective)
- Protocol note: `plans_and_protocols/2026-03-02_01_protocol_evaluation.md` — Consolidation Addendum

## Acceptance Criteria

- [ ] NFR-SESSION-001 written into requirements.md in the appropriate section
- [ ] Affected personas listed in the NFR
- [ ] Configurable timeout values specified (with role-based defaults)
- [ ] NFR cross-referenced from Prof. Weber's persona.md (or scenario notes)
