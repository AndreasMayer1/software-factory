# Prototype Scenario Index

**Task**: TASK-PROC-010-12
**Date**: 2026-02-06
**Agent**: Opus (direct content creation)
**Depends on**: `2026-02-06_01_scenario_pattern_analysis.md`, `2026-02-06_02_index_design_proposal.md`

---

**Note**: This is a PROTOTYPE for user review. Once approved, the final version will be placed at `requirements_user_needs/SCENARIO_INDEX.md`. The YAML frontmatter below is the machine-readable source of truth; the markdown body below it is the human-readable companion.

---

```yaml
---
# =============================================================================
# SCENARIO PATTERN INDEX
# =============================================================================
# Source of truth for canonical scenario names and cross-persona coverage.
#
# Purpose:
#   1. Prevent naming chaos when generating similar scenarios across personas
#   2. Track which personas have which scenario patterns (gap analysis)
#   3. Provide canonical names for create-scenario skill validation
#
# Maintenance:
#   - Updated by create-scenario skill on every scenario creation
#   - Updated manually when new patterns are discovered
#   - All scenario_id references must point to existing files
#
# Naming convention:
#   canonical_name = [action]_[object]_[qualifier]
#   Folder name = canonical_name (or canonical_name__variant for multiple per persona)
#
# Version: 1.0
# Updated: 2026-02-06
# Task: TASK-PROC-010-12
# =============================================================================

version: "1.0"
updated: 2026-02-06

# ---------------------------------------------------------------------------
# Lifecycle stages (ordered):
#   create   - Therapist/user creates a tracking structure
#   capture  - User records data (spontaneous or routine)
#   prepare  - User reviews own data before a session
#   transfer - User delivers data to therapist
#   review   - Therapist + user analyze data together
#   reflect  - User reviews own data alone (self-user, no therapist)
# ---------------------------------------------------------------------------

patterns:

  # =========================================================================
  # STAGE: CREATE
  # =========================================================================

  - canonical_name: "prepare_protocol_for_client"
    display_name: "Prepare Protocol for Client"
    description: >
      Therapist creates or customizes a structured tracking instrument
      (protocol/questionnaire) tailored to a specific client's therapy goals
      and current treatment phase. Includes planning how to introduce it
      and what instructions to give.
    lifecycle_stage: create
    applicable_roles:
      - role: therapist
        relevance: primary
        notes: "Core therapist workflow — creating homework for clients"
      - role: self_user
        relevance: edge_case
        notes: "Self-user designing own tracking structure without therapist guidance"
    tags: [protocol, preparation, therapist_workflow, customization]
    instances:
      - persona_id: PERSONA-001
        persona_folder: dr_sarah
        scenario_id: SCEN-001-01
        scenario_folder: prepare_protocol_for_client
        outcome: success
        variant_notes: "Paper-based anxiety protocol for client Anna. Includes margin notes, customized columns, and session handover plan."
    predicted_instances:
      - role: self_user
        notes: "A self-user deciding what to track and how to structure their own protocol (no therapist involved)."

  # =========================================================================
  # STAGE: CAPTURE
  # =========================================================================

  - canonical_name: "capture_data_spontaneously"
    display_name: "Capture Data Spontaneously"
    description: >
      User records thoughts, feelings, or data driven by internal urgency
      or an emotional trigger — not on a schedule. Typically under constraints
      (time pressure, darkness, noise sensitivity, low cognitive capacity).
      The recording is reactive, not habitual.
    lifecycle_stage: capture
    applicable_roles:
      - role: client
        relevance: primary
        notes: "Client experiencing emotional urgency (rumination, crisis, insight)"
      - role: self_user
        relevance: primary
        notes: "Identical need — spontaneous capture without therapist context"
    tags: [capture, spontaneous, urgency, constraints, data_entry]
    instances:
      - persona_id: PERSONA-002
        persona_folder: max_client
        scenario_id: SCEN-002-01
        scenario_folder: brain_dump_at_night
        outcome: failure
        variant_notes: "Nighttime brain dump. Paper/pen fails due to darkness, noise constraint (sleeping partner), illegible handwriting. Context: 2 AM, bedroom."
    predicted_instances:
      - role: client
        notes: "Other contexts: commute (train/bus), work break, waiting room. Different constraints (public space, time limit, social visibility)."
      - role: self_user
        notes: "Same urgency pattern without therapy homework framing."

  - canonical_name: "routine_data_entry"
    display_name: "Routine Data Entry"
    description: >
      User fills out their protocol or tracking tool as part of a regular
      routine (daily, after specific events, or at scheduled times).
      Driven by habit or obligation rather than emotional urgency.
      Risk of abandonment over time due to friction or low motivation.
    lifecycle_stage: capture
    applicable_roles:
      - role: client
        relevance: primary
        notes: "Client filling out therapy homework on schedule"
      - role: self_user
        relevance: primary
        notes: "Self-tracker maintaining a regular logging habit"
    tags: [capture, routine, habit, compliance, data_entry]
    instances: []
    predicted_instances:
      - role: client
        notes: "The daily act of filling in the protocol — referenced in multiple scenarios (Max's entries in prepare_for_therapy_session, Sophie's entries in successful_protocol_handover) but not yet a standalone scenario."
      - role: self_user
        notes: "Self-user maintaining daily mood/habit tracking as personal practice."

  # =========================================================================
  # STAGE: PREPARE
  # =========================================================================

  - canonical_name: "prepare_for_therapy_session"
    display_name: "Prepare for Therapy Session"
    description: >
      Client reviews their own recorded data before an upcoming therapy
      session to identify talking points, recognize patterns, and arrive
      feeling prepared rather than blindsided. Involves confronting gaps,
      illegible entries, and shame about incomplete data.
    lifecycle_stage: prepare
    applicable_roles:
      - role: client
        relevance: primary
        notes: "Client reviewing own tracking data to prepare for discussion with therapist"
      - role: therapist
        relevance: secondary
        notes: "Therapist reviewing client data before session (if pre-shared) — different scenario from collaborative review"
    tags: [preparation, self_review, therapy, pre_session]
    instances:
      - persona_id: PERSONA-002
        persona_folder: max_client
        scenario_id: SCEN-002-03
        scenario_folder: prepare_for_therapy_session
        outcome: partial
        variant_notes: "Sunday evening review. Paper protocol with context loss, illegible entries, shame about gaps. Arrives with 'fragments' rather than clarity."
    predicted_instances:
      - role: client
        notes: "Sophie version — ADHD-specific preparation with hyperfocus-fade pattern, medication timing concerns."
      - role: therapist
        notes: "Therapist reviewing digitally-shared data before session (future state, once app exists)."

  # =========================================================================
  # STAGE: TRANSFER
  # =========================================================================

  - canonical_name: "transfer_data_to_therapist"
    display_name: "Transfer Data to Therapist"
    description: >
      Client brings or delivers their tracked data to the therapist at
      session time. Includes the physical/digital act of handover and the
      emotional significance of presenting proof of effort. Can succeed
      (data arrives, session is productive) or fail (data forgotten/lost,
      session time wasted on reconstruction).
    lifecycle_stage: transfer
    applicable_roles:
      - role: client
        relevance: primary
        notes: "Client is the one who must transport/deliver the data"
    tags: [transfer, handover, session, compliance, data_delivery]
    instances:
      - persona_id: PERSONA-002
        persona_folder: max_client
        scenario_id: SCEN-002-02
        scenario_folder: forgotten_protocol_transfer
        outcome: failure
        variant_notes: "Protocol left on shoe rack at home. Attempted reconstruction from memory on train. 30% of session wasted. Shame spiral."
      - persona_id: PERSONA-010
        persona_folder: sophie_structure_seeker
        scenario_id: SCEN-010-01
        scenario_folder: successful_protocol_handover
        outcome: success
        variant_notes: "Protocol Pocket system works. 4 of 7 days filled. Ceremonial handover. Frau Kellner identifies medication-mood correlation. Fragile success dependent on hyperfocus week."
    predicted_instances:
      - role: client
        notes: "Other failure modes: paper damaged, wrong week grabbed, self-censored before sharing."

  # =========================================================================
  # STAGE: REVIEW
  # =========================================================================

  - canonical_name: "review_data_collaboratively"
    display_name: "Review Data Collaboratively"
    description: >
      Therapist and client analyze the client's tracked data together
      during a therapy session. Therapist identifies patterns, asks
      therapeutic questions, validates effort. The review reveals not
      just the data but meta-patterns (compliance, avoidance, recall
      bias). Happens on a shared surface (physical or digital).
    lifecycle_stage: review
    applicable_roles:
      - role: therapist
        relevance: primary
        notes: "Drives the analysis, asks probing questions, identifies clinical patterns"
      - role: client
        relevance: primary
        notes: "Participates, provides context behind entries, gains self-awareness"
    tags: [review, collaborative, therapy_session, pattern_recognition, analysis]
    instances:
      - persona_id: PERSONA-001
        persona_folder: dr_sarah
        scenario_id: SCEN-001-02
        scenario_folder: review_protocol_with_client
        outcome: success
        variant_notes: "Reviews Anna's anxiety protocol. Discovers anticipatory anxiety pattern, avoidance reinforcement. Data quality concern (Parking Lot Syndrome — entries possibly batch-written in waiting room)."
    predicted_instances:
      - role: client
        notes: "Client-perspective version of the same event — experiencing the review from the other side of the table."

  # =========================================================================
  # STAGE: REFLECT (Self-User, No Therapist)
  # =========================================================================

  - canonical_name: "self_review_and_reflect"
    display_name: "Self-Review and Reflect"
    description: >
      User reviews their own tracked data alone (no therapist present)
      to identify patterns, gain self-awareness, or assess personal
      progress. Differs from prepare_for_therapy_session in that there
      is no external accountability — the review is intrinsically motivated.
    lifecycle_stage: reflect
    applicable_roles:
      - role: self_user
        relevance: primary
        notes: "Core self-user workflow — reviewing own data for personal insight"
      - role: client
        relevance: secondary
        notes: "Client reviewing data between sessions for personal understanding (not just pre-session prep)"
    tags: [self_review, reflection, patterns, self_awareness, autonomous]
    instances: []
    predicted_instances:
      - role: self_user
        notes: "The quantified-self persona reviewing mood trends, sleep correlations, habit impacts."
      - role: client
        notes: "Client reviewing data mid-week to understand own patterns, independent of upcoming session."
```

---

# Scenario Index

## Purpose

This index is the **single source of truth** for scenario pattern names and cross-persona coverage. It serves three functions:

1. **Naming consistency**: Every new scenario's folder name is derived from a canonical pattern name listed here.
2. **Gap analysis**: Shows which personas have which patterns — and where gaps exist.
3. **Skill integration**: The `create-scenario` skill reads this file to validate names and suggest missing scenarios.

## How to Use This Index

- **Creating a new scenario**: Check if the pattern already exists. If yes, use the `canonical_name` as your folder name. If no, define a new pattern first.
- **Finding gaps**: Look at the Coverage Matrix below. Empty cells = potential scenarios to write.
- **Batch generation**: Pick a pattern, look at existing instances as gold standards, generate new instances for other personas.

## The Therapy Data Lifecycle

Scenarios follow a natural lifecycle of how tracking data flows through the therapy process:

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│ CREATE  │ →  │ CAPTURE │ →  │ PREPARE │ →  │ TRANSFER │ →  │  REVIEW  │
│         │    │         │    │         │    │          │    │          │
│Therapist│    │ Client  │    │ Client  │    │ Client → │    │Therapist │
│prepares │    │records  │    │reviews  │    │Therapist │    │+ Client  │
│protocol │    │data     │    │own data │    │          │    │together  │
└─────────┘    └─────────┘    └─────────┘    └──────────┘    └──────────┘
                    │                                              │
                    │              ┌──────────┐                    │
                    └─────────── →│ REFLECT  │← ─ ─ ─ ─ ─ ─ ─ ─ ┘
                                  │          │   (self-user path:
                                  │Self-user │    no therapist)
                                  │reviews   │
                                  │alone     │
                                  └──────────┘
```

**Key**: Not every persona touches every stage. Therapists primarily operate in CREATE and REVIEW. Clients operate in CAPTURE through TRANSFER. Self-users operate in CAPTURE and REFLECT (skipping TRANSFER and collaborative REVIEW).

## Patterns by Lifecycle Stage

### Stage: Create

#### `prepare_protocol_for_client`
- **Description**: Therapist creates or customizes a tracking instrument for a client.
- **Roles**: therapist (primary), self_user (edge case)
- **Instances**:
  - SCEN-001-01 — Dr. Sarah prepares Anna's anxiety protocol ✅
- **Gaps**: Self-user designing own tracking structure

---

### Stage: Capture

#### `capture_data_spontaneously`
- **Description**: User records data driven by emotional urgency, not on a schedule.
- **Roles**: client (primary), self_user (primary)
- **Instances**:
  - SCEN-002-01 — Max's brain dump at night (failure: paper in dark) ✅
- **Gaps**: Other contexts (commute, work), other personas, success variant

#### `routine_data_entry`
- **Description**: User fills out protocol on a regular schedule (daily, post-event).
- **Roles**: client (primary), self_user (primary)
- **Instances**: *(none yet — referenced in other scenarios but not standalone)*
- **Gaps**: All client and self_user personas need this

---

### Stage: Prepare

#### `prepare_for_therapy_session`
- **Description**: Client reviews own data before session to identify talking points.
- **Roles**: client (primary), therapist (secondary)
- **Instances**:
  - SCEN-002-03 — Max's Sunday evening review (partial success) ✅
- **Gaps**: Sophie version, therapist pre-review version

---

### Stage: Transfer

#### `transfer_data_to_therapist`
- **Description**: Client delivers tracked data to therapist at session time.
- **Roles**: client (primary)
- **Instances**:
  - SCEN-002-02 — Max forgets protocol at home (failure) ✅
  - SCEN-010-01 — Sophie's successful handover (success) ✅
- **Gaps**: Other failure modes (damaged, self-censored, wrong week)

---

### Stage: Review

#### `review_data_collaboratively`
- **Description**: Therapist and client analyze data together in session.
- **Roles**: therapist (primary), client (primary)
- **Instances**:
  - SCEN-001-02 — Dr. Sarah reviews Anna's protocol ✅
- **Gaps**: Client-perspective version of same event

---

### Stage: Reflect

#### `self_review_and_reflect`
- **Description**: User reviews own data alone for personal insight (no therapist).
- **Roles**: self_user (primary), client (secondary)
- **Instances**: *(none yet)*
- **Gaps**: All self_user personas, client mid-week review

---

## Coverage Matrix

Shows which personas have scenarios for each pattern. ✅ = exists, 🔲 = applicable but missing, ─ = not applicable for this role.

| Pattern | Dr. Sarah (therapist) | Max (client) | Sophie (client) | *Self-User Personas* |
|---------|----------------------|-------------|-----------------|---------------------|
| `prepare_protocol_for_client` | ✅ SCEN-001-01 | ─ | ─ | 🔲 edge case |
| `capture_data_spontaneously` | ─ | ✅ SCEN-002-01 | 🔲 | 🔲 |
| `routine_data_entry` | ─ | 🔲 | 🔲 | 🔲 |
| `prepare_for_therapy_session` | 🔲 secondary | ✅ SCEN-002-03 | 🔲 | ─ |
| `transfer_data_to_therapist` | ─ | ✅ SCEN-002-02 | ✅ SCEN-010-01 | ─ |
| `review_data_collaboratively` | ✅ SCEN-001-02 | 🔲 (client POV) | 🔲 (client POV) | ─ |
| `self_review_and_reflect` | ─ | 🔲 secondary | 🔲 secondary | 🔲 |

**Reading the matrix**:
- 12 cells marked 🔲 = potential scenarios to write
- The most impactful gaps are `routine_data_entry` (affects all client/self-user personas) and `self_review_and_reflect` (the core self-user scenario)

## Naming Quick Reference

### Convention
```
[action]_[object]_[qualifier]
```
- **action**: verb (prepare, capture, transfer, review, enter)
- **object**: what (data, protocol, thoughts)
- **qualifier**: distinguishing context (for_client, spontaneously, collaboratively)

### Variant Qualifier (same persona, multiple instances of same pattern)
```
[canonical_name]__[qualifier]
```
Double underscore separates canonical name from variant.

### Outcome Tracking
Outcome (success/failure/partial) is tracked in YAML metadata, NOT in the folder name.

### Word Standardization
| Use | Don't Use |
|-----|-----------|
| `transfer` | handover, deliver, hand_over |
| `protocol` | questionnaire, form, sheet |
| `capture` | dump, log, record |
| `data` | entries, information |
| `collaboratively` | with_client, together, jointly |

---

*This prototype is ready for user review. Once approved, this content will be placed at `requirements_user_needs/SCENARIO_INDEX.md` and the `create-scenario` skill will be updated to validate against it.*
