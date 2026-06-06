# Investigation: Session Continuity NFR Documentation

**Task**: TASK-PROC-027-35
**Date**: 2026-03-03
**Phase**: Phase 1 Investigation

---

## Executive Summary

The goal is to formally document NFR-SESSION-001 in the main `requirements.md` file. This NFR consolidates a reliability concern surfaced by the declined scenario *"The Login Rupture"* (Prof. Dr. Weber, PERSONA-011) into a non-functional requirement that applies across all therapist personas.

**Key Finding**: This is NOT a new feature requirement — it's a reliability and UX constraint on existing session management. The existing Session Management feature (60-second grace period) handles backgrounding. The NFR ensures that the app never interrupts *during active clinical use* with authentication prompts.

---

## Investigation Findings

### 1. Source & Context

- **Source Document**: Evaluation task TASK-PROC-027-20 (Gemini scenario evaluation)
- **Location**: `plans_and_protocols/2026-03-02_02_opus_consolidation_analysis.md:170`
- **Original Scenario**: *"The Login Rupture"* (Prof. Dr. Weber perspective)
- **Decision**: DECLINED as standalone scenario, but insight → convert to NFR
- **Reasoning**: "IT problems disrupting therapeutic silence is a general usability concern, not a scenario-specific insight. Every app must minimize interruptions. Better as a non-functional requirement."

### 2. Affected Personas

Three therapist personas explicitly depend on uninterrupted session contexts:

| Persona | Role | Context | Why It Matters |
|---------|------|---------|----------------|
| PERSONA-011: Prof. Dr. Weber | Depth psychologist | Long 50-minute sessions with emphasis on silence and free association | Therapeutic silence is a clinical tool; unexpected prompts destroy the frame |
| PERSONA-001: Dr. Sarah | VT therapist | Live protocol review & adjustment during sessions | Session workflow includes real-time pattern analysis and patient interaction |
| PERSONA-012: Dr. med. Turan | Psychiatrist | 10-20 minute appointments with rapid data lookups | Patient lookup queries during appointments cannot be interrupted |

### 3. Current Session Management Feature

**Location**: `requirements.md:5035-5150` ("Feature: Session Management")

**Current Behavior**:
- 60-second grace period after app backgrounding
- If user returns within 60s → stays unlocked
- If user returns after 60s → requires re-authentication
- Implemented via `WidgetsBindingObserver` (app lifecycle tracking)

**Limitation**: Does NOT prevent re-auth prompts during *active* use (e.g., if OS resets session, device lock triggers re-auth request, biometric state changes mid-session).

### 4. Requirement Hierarchy

**Parent Requirement**: REQ-PROC-027 (User Needs Content Creation)
**Related Feature**: REQ-FUNC-006-03 (Session Management) in `requirements.md:5035`

**No existing "Non-Functional Requirements" section** in `requirements.md`. Must create one.

### 5. Personas File Status

All three affected personas files have been recently updated (2026-03-02 to 2026-03-03):
- PERSONA-011: `review_status: in_review` (added VCD per TASK-PROC-033-02)
- PERSONA-001: `review_status: in_review` (added VCD + between-session constraints)
- PERSONA-012: `review_status: in_review` (added VCD + crisis routing)

No explicit mention of session continuity needs in their current persona.md files, but implied through:
- Prof. Weber's value: "Beneficence (Therapeutic Depth and Authenticity)"
- Dr. Sarah's value: "Efficiency (Session Time Preservation)"
- Dr. Turan's value: "Beneficence (Patient Safety Through Data)"

---

## NFR Specification to Document

### NFR-SESSION-001: Session Continuity During Active Clinical Use

**Definition**:
The application must not display login prompts, re-authentication requests, or session-expired messages while a user is actively viewing or interacting with patient data on a clinical screen. "Active session view" is defined as any screen displaying patient information, treatment data, or enabling data entry.

**Scope**:
- Therapists (Dr. Sarah, Dr. Turan, Prof. Weber)
- Clinical self-users (Max, Lisa, etc.) who are in active session with the app
- Active session = any screen showing patient/personal tracking data or entry interface

**Re-authentication Timing** (role-based):
- **During active clinical use**: NEVER interrupt
- **After app backgrounding**: Require re-auth only if:
  - Therapist role: backgrounded for >30 minutes (configurable)
  - Self-user role: backgrounded for >10 minutes (configurable)
  - Re-auth prompt appears ONLY on app resume, not mid-entry

**Exceptions** (can interrupt):
- Critical security event (device compromised, OS session destroyed)
- Explicit manual app exit / close
- Device reboot or OS-level session reset

**Implementation Implications**:
- Session timeout must be decoupled from OS screen lock
- Biometric re-prompt must not trigger mid-entry
- Grace period for app backgrounding must be role-aware
- No popup overlays during active data review/entry

---

## Where to Document

**Location in requirements.md**:
Create new top-level section after existing features:

```markdown
# Non-Functional Requirements

## NFR-001: Session Continuity During Active Clinical Use
...
```

**Alternative**: Add as a subsection to the existing Session Management feature (line 5035) with cross-reference.

**Recommendation**: Create separate section to:
1. Distinguish NFRs (reliability constraints) from functional features
2. Make NFR discoverable for implementation teams
3. Allow NFRs to scale (current plan: just NFR-001, future: may add more)

---

## Quality Check

- [x] Declined scenario analyzed and insight extracted
- [x] Affected personas identified and documented
- [x] Related functional requirements found (Session Management feature)
- [x] No existing NFR section in requirements.md → must create
- [x] All three therapist personas represented
- [x] Cross-reference to PERSONA-011/-001/-012 will be added to the NFR body
- [x] Role-based configuration options specified
- [x] Implementation implications documented

---

## Next Steps (Phase 2: Synthesis)

1. **Create NFR-SESSION-001** in requirements.md with full specification
2. **Add YAML frontmatter** with:
   - `id: NFR-SESSION-001`
   - `status: defined`
   - `personas_served: [PERSONA-001, PERSONA-011, PERSONA-012]`
3. **Cross-reference** from Session Management feature back to this NFR
4. **Update affected persona files** (optional): Add reference to the NFR in their persona.md files

---

## User Review Needed

Before proceeding to Phase 2 (writing the NFR), confirm:

1. **NFR scope**: Should this apply to self-users too (Max, Lisa), or just therapists?
2. **Grace period defaults**: Are 30 min (therapist) / 10 min (self-user) correct?
3. **Section location**: Separate "Non-Functional Requirements" section, or subsection of Session Management?
4. **Additional roles**: Should system_maintenance (PERSONA-004) have different rules?
