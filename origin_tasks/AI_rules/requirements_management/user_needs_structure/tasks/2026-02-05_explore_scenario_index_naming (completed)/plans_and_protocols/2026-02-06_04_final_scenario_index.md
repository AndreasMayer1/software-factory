# Final Scenario Index (Post-Feedback Revision)

**Task**: TASK-PROC-010-12
**Date**: 2026-02-06
**Agent**: Opus
**Status**: Ready for user approval — once approved, place at `requirements_user_needs/SCENARIO_INDEX.md`

---

## How This Document Works

- **YAML frontmatter** = machine-readable source of truth (for skills)
- **Markdown body** = human-readable overview (for review, onboarding)
- **Categories are extensible** — start with what exists, grow organically
- **Existing scenarios are assigned** to categories; no renaming happens here

---

```yaml
---
# =============================================================================
# SCENARIO CATEGORY INDEX
# =============================================================================
#
# Central registry of scenario categories organized by data flow.
# Source of truth for:
#   - Canonical category and sub-category names
#   - Which persona roles each category applies to
#   - Which existing scenarios belong to which category
#   - Gold standard scenario tracking
#
# Data Flow:
#   Plan erstellen → Plan aushändigen → Plan ausfüllen →
#   Daten analysieren → Daten ablegen
#
# Naming convention (folder names):
#   [action]_[object]_[qualifier]   (snake_case)
#   Variant suffix: __[qualifier]   (double underscore, only when same
#                                    persona has multiple of same category)
#
# Process for new scenarios:
#   1. Check if a matching category exists here
#   2. If not → define new category, add to this index
#   3. Create scenario using canonical name as folder name
#   4. Ensure other relevant personas are flagged for coverage
#
# Version: 2.0
# Updated: 2026-02-06
# Task: TASK-PROC-010-12
# =============================================================================

version: "2.0"
updated: 2026-02-06

# =============================================================================
# SCENARIO METADATA SPEC (new fields for scenario.md YAML frontmatter)
# =============================================================================
# These fields must be added to every scenario's YAML header:
#
#   category: "capture.spontaneous"        # dot-notation: stage.sub_category
#   gold_status: true | false              # is this the gold standard for
#                                          # its category? (user-approved
#                                          # reference for batch generation)
#
# Gold Workflow:
#   1. Create scenario for ONE persona
#   2. User reviews and approves
#   3. User marks as gold (gold_status: true)
#   4. AI adapts gold scenario for other relevant personas
# =============================================================================

# =============================================================================
# CATEGORIES BY DATA FLOW STAGE
# =============================================================================

stages:

  # ===========================================================================
  # STAGE 1: PLAN CREATION (Planerstellung)
  # ===========================================================================
  # Therapist or self-user creates/designs a tracking instrument.

  - stage_id: creation
    display_name: "Plan Creation (Planerstellung)"
    description: >
      Creating or customizing structured tracking instruments (protocols,
      questionnaires, tracking plans) for therapy or self-use.
    categories:

      - id: "creation.prepare_protocol"
        canonical_name: "prepare_protocol_for_client"
        display_name: "Prepare Protocol for Client"
        description: >
          Therapist creates or customizes a tracking protocol tailored to
          a specific client's therapy goals and current treatment phase.
          Includes selecting template, writing instructions, personalizing
          columns/prompts.
        applicable_roles:
          - role: therapist
            relevance: primary
          - role: self_user
            relevance: edge_case
            notes: "Self-user designing own tracking structure"
        instances:
          - persona_id: PERSONA-001
            persona_folder: dr_sarah
            scenario_id: SCEN-001-01
            scenario_folder: prepare_protocol_for_client
            outcome: success
            gold_status: true
            notes: "Paper anxiety protocol for Anna. Margin notes, customized columns."
        gaps:
          - role: self_user
            notes: "Self-user creating own tracking plan without therapist guidance"

  # ===========================================================================
  # STAGE 2: PLAN DISTRIBUTION (Planübergabe)
  # ===========================================================================
  # Therapist hands protocol to client and provides instructions.

  - stage_id: distribution
    display_name: "Plan Distribution (Planübergabe)"
    description: >
      Handing a tracking protocol to the client, explaining what to track,
      when, and how. Includes addressing barriers and client concerns.
    categories:

      - id: "distribution.instruct_client"
        canonical_name: "instruct_client_on_protocol"
        display_name: "Instruct Client on Protocol"
        description: >
          Therapist hands protocol to client during session, explains usage,
          addresses potential barriers (forgetting, privacy concerns), and
          sets expectations. Currently embedded in Act 3 of SCEN-001-01 —
          may become its own standalone scenario if needed.
        applicable_roles:
          - role: therapist
            relevance: primary
          - role: client
            relevance: primary
            notes: "Client perspective: receiving, understanding, gaining confidence"
        instances: []
        gaps:
          - role: therapist
            notes: "Currently embedded in SCEN-001-01 Act 3, not standalone"
          - role: client
            notes: "Client perspective of receiving protocol and instructions"

  # ===========================================================================
  # STAGE 3: DATA CAPTURE (Datenerfassung)
  # ===========================================================================
  # Client/self-user records data — spontaneous or routine.

  - stage_id: capture
    display_name: "Data Capture (Datenerfassung)"
    description: >
      Recording mood, thoughts, symptoms, or behavioral data into the
      tracking instrument. Varies by trigger (urgent vs. scheduled),
      context (night, commute, work), and method (writing, voice, quick tap).
    categories:

      - id: "capture.spontaneous"
        canonical_name: "capture_data_spontaneously"
        display_name: "Capture Data Spontaneously"
        description: >
          Recording driven by internal urgency or emotional trigger — not
          on a schedule. Typically under constraints (darkness, noise,
          low cognitive capacity, time pressure). Reactive, not habitual.
        applicable_roles:
          - role: client
            relevance: primary
          - role: self_user
            relevance: primary
        instances:
          - persona_id: PERSONA-002
            persona_folder: max_client
            scenario_id: SCEN-002-01
            scenario_folder: brain_dump_at_night
            outcome: failure
            gold_status: true
            notes: "Nighttime brain dump. Paper fails (dark, noise, illegible). 2 AM, bedroom."
        gaps:
          - role: client
            notes: "Other contexts: commute, work break, waiting room"
          - role: self_user
            notes: "Same urgency without therapy homework framing"

      - id: "capture.routine"
        canonical_name: "routine_data_entry"
        display_name: "Routine Data Entry"
        description: >
          Filling out protocol on a regular schedule (daily, post-event,
          evening routine). Driven by habit or obligation rather than
          emotional urgency. Risk of abandonment over time.
        applicable_roles:
          - role: client
            relevance: primary
          - role: self_user
            relevance: primary
        instances: []
        gaps:
          - role: client
            notes: "Referenced in SCEN-002-03 and SCEN-010-01 but not standalone"
          - role: self_user
            notes: "Daily mood/habit tracking as personal practice"

  # ===========================================================================
  # STAGE 4: DATA ANALYSIS (Datenanalyse)
  # ===========================================================================
  # Reviewing, preparing, and analyzing tracked data — alone or together.

  - stage_id: analysis
    display_name: "Data Analysis (Datenanalyse)"
    description: >
      Reviewing tracked data to identify patterns, prepare for sessions,
      or gain personal insight. Includes pre-session preparation, data
      transfer to therapist, collaborative review, and self-reflection.
    categories:

      - id: "analysis.prepare_for_session"
        canonical_name: "prepare_for_therapy_session"
        display_name: "Prepare for Therapy Session"
        description: >
          Client reviews own recorded data before a therapy session to
          identify talking points, recognize patterns, and arrive feeling
          prepared. Involves confronting gaps, illegible entries, and
          shame about incomplete data.
        applicable_roles:
          - role: client
            relevance: primary
          - role: therapist
            relevance: secondary
            notes: "Therapist pre-reviewing shared data before session"
        instances:
          - persona_id: PERSONA-002
            persona_folder: max_client
            scenario_id: SCEN-002-03
            scenario_folder: prepare_for_therapy_session
            outcome: partial
            gold_status: true
            notes: "Sunday evening review. Context loss, illegible entries, shame about gaps."
        gaps:
          - role: client
            notes: "Sophie/other client versions with different constraints"

      - id: "analysis.transfer_to_therapist"
        canonical_name: "transfer_data_to_therapist"
        display_name: "Transfer Data to Therapist"
        description: >
          Client brings or delivers tracked data to therapist at session
          time. The physical/digital handover and its emotional significance
          (proof of effort). Can succeed or fail (forgotten, lost, censored).
        applicable_roles:
          - role: client
            relevance: primary
        instances:
          - persona_id: PERSONA-002
            persona_folder: max_client
            scenario_id: SCEN-002-02
            scenario_folder: forgotten_protocol_transfer
            outcome: failure
            gold_status: true
            notes: "Protocol forgotten at home. Memory reconstruction on train. 30% session wasted."
          - persona_id: PERSONA-010
            persona_folder: sophie_structure_seeker
            scenario_id: SCEN-010-01
            scenario_folder: successful_protocol_handover
            outcome: success
            gold_status: true
            notes: "Protocol Pocket system works. 4/7 days. Medication-mood correlation found."
        gaps:
          - role: client
            notes: "Other failure modes: damaged, self-censored, wrong week"

      - id: "analysis.review_collaboratively"
        canonical_name: "review_data_collaboratively"
        display_name: "Review Data Collaboratively"
        description: >
          Therapist and client analyze tracked data together during a
          therapy session. Pattern identification, therapeutic questioning,
          effort validation. Reveals meta-patterns (compliance, avoidance,
          recall bias).
        applicable_roles:
          - role: therapist
            relevance: primary
            notes: "Drives analysis, identifies clinical patterns"
          - role: client
            relevance: primary
            notes: "Participates, provides context, gains self-awareness"
        instances:
          - persona_id: PERSONA-001
            persona_folder: dr_sarah
            scenario_id: SCEN-001-02
            scenario_folder: review_protocol_with_client
            outcome: success
            gold_status: true
            notes: "Reviews Anna's anxiety protocol. Anticipatory anxiety pattern. Data quality concern."
        gaps:
          - role: client
            notes: "Client-perspective version of the same collaborative event"

      - id: "analysis.self_reflect"
        canonical_name: "self_review_and_reflect"
        display_name: "Self-Review and Reflect"
        description: >
          User reviews own tracked data alone (no therapist) to identify
          patterns, gain self-awareness, or assess progress. Intrinsically
          motivated — no external accountability.
        applicable_roles:
          - role: self_user
            relevance: primary
          - role: client
            relevance: secondary
            notes: "Client reviewing data between sessions independently"
        instances: []
        gaps:
          - role: self_user
            notes: "Core self-user scenario: reviewing mood trends, correlations"
          - role: client
            notes: "Mid-week independent review for personal understanding"

  # ===========================================================================
  # STAGE 5: DATA MANAGEMENT (Datenverwaltung)
  # ===========================================================================
  # Export, backup, restore, archive — long-term data handling.

  - stage_id: management
    display_name: "Data Management (Datenverwaltung)"
    description: >
      Long-term handling of tracked data: exporting for external use,
      backing up for safety, restoring after device changes, and
      archiving/cleaning old data.
    categories:

      - id: "management.export"
        canonical_name: "export_data_externally"
        display_name: "Export Data Externally"
        description: >
          Exporting tracked data to an external format (PDF, CSV) for
          use outside the app — sharing with a doctor, insurance,
          personal archive on a hard drive, or import into other software.
        applicable_roles:
          - role: client
            relevance: primary
            notes: "Exporting for therapist, insurance, or personal records"
          - role: therapist
            relevance: secondary
            notes: "Exporting client summaries for documentation"
          - role: self_user
            relevance: primary
            notes: "Personal data sovereignty — owning your own export"
        instances: []
        gaps:
          - role: client
            notes: "Client exporting data for external use"
          - role: self_user
            notes: "Self-user exporting for personal archive"

      - id: "management.backup_restore"
        canonical_name: "backup_and_restore_data"
        display_name: "Backup and Restore Data"
        description: >
          Safeguarding data against loss (device failure, theft, damage)
          and restoring it on a new device. Includes device migration
          scenarios (old phone → new phone).
        applicable_roles:
          - role: client
            relevance: primary
          - role: self_user
            relevance: primary
        instances: []
        gaps:
          - role: client
            notes: "Device change, accidental deletion, phone repair"
          - role: self_user
            notes: "Same scenarios without therapist context"
```

---

# Scenario Category Index

## Purpose

This index is the **central registry** of all scenario categories, organized by the therapy data flow. It serves as:

1. **Naming authority**: Canonical names for scenario folders
2. **Coverage tracker**: Which personas have which categories (gap analysis)
3. **Gold standard registry**: Which scenarios are approved references for batch generation
4. **Skill integration point**: `create-scenario` reads this to validate and suggest

## Data Flow

Scenarios follow the natural flow of therapy tracking data:

```
1. CREATION          2. DISTRIBUTION       3. CAPTURE
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Therapist    │ →  │ Therapist    │ →  │ Client/Self  │
│ creates plan │    │ hands plan   │    │ records data │
│              │    │ to client    │    │              │
│ • prepare_   │    │ • instruct_  │    │ • capture_   │
│   protocol_  │    │   client_on_ │    │   data_spon- │
│   for_client │    │   protocol   │    │   taneously  │
└──────────────┘    └──────────────┘    │ • routine_   │
                                        │   data_entry │
                                        └──────┬───────┘
                                               │
                                               ▼
4. ANALYSIS                              5. MANAGEMENT
┌──────────────────────────────────┐    ┌──────────────┐
│ Preparing, transferring,         │    │ Long-term    │
│ reviewing data                   │    │ data handling │
│                                  │    │              │
│ • prepare_for_therapy_session    │    │ • export_    │
│ • transfer_data_to_therapist    │    │   data_      │
│ • review_data_collaboratively   │    │   externally │
│ • self_review_and_reflect       │    │ • backup_    │
└──────────────────────────────────┘    │   and_       │
                                        │   restore_   │
                                        │   data       │
                                        └──────────────┘
```

## Categories Overview

### Stage 1: Plan Creation (Planerstellung)

| Category | Canonical Name | Roles | Existing Scenarios | Gaps |
|----------|---------------|-------|--------------------|------|
| Prepare Protocol | `prepare_protocol_for_client` | therapist, self_user (edge) | SCEN-001-01 (Dr. Sarah) ⭐ | self_user |

### Stage 2: Plan Distribution (Planübergabe)

| Category | Canonical Name | Roles | Existing Scenarios | Gaps |
|----------|---------------|-------|--------------------|------|
| Instruct Client | `instruct_client_on_protocol` | therapist, client | *(embedded in SCEN-001-01 Act 3)* | standalone needed? |

### Stage 3: Data Capture (Datenerfassung)

| Category | Canonical Name | Roles | Existing Scenarios | Gaps |
|----------|---------------|-------|--------------------|------|
| Spontaneous Capture | `capture_data_spontaneously` | client, self_user | SCEN-002-01 (Max, night) ⭐ | other contexts, self_user |
| Routine Entry | `routine_data_entry` | client, self_user | *(none standalone)* | all personas |

### Stage 4: Data Analysis (Datenanalyse)

| Category | Canonical Name | Roles | Existing Scenarios | Gaps |
|----------|---------------|-------|--------------------|------|
| Pre-Session Prep | `prepare_for_therapy_session` | client, therapist (sec.) | SCEN-002-03 (Max) ⭐ | Sophie, other clients |
| Transfer to Therapist | `transfer_data_to_therapist` | client | SCEN-002-02 (Max, fail) ⭐, SCEN-010-01 (Sophie, success) ⭐ | other failure modes |
| Collaborative Review | `review_data_collaboratively` | therapist, client | SCEN-001-02 (Dr. Sarah) ⭐ | client POV |
| Self-Reflection | `self_review_and_reflect` | self_user, client (sec.) | *(none)* | all self_user personas |

### Stage 5: Data Management (Datenverwaltung)

| Category | Canonical Name | Roles | Existing Scenarios | Gaps |
|----------|---------------|-------|--------------------|------|
| Export | `export_data_externally` | client, therapist (sec.), self_user | *(none)* | all roles |
| Backup & Restore | `backup_and_restore_data` | client, self_user | *(none)* | all roles |

**Legend**: ⭐ = Gold Standard scenario (approved reference for batch generation)

## Coverage Matrix

| Category | Dr. Sarah (therapist) | Max (client) | Sophie (client) | *Self-User* |
|----------|----------------------|-------------|-----------------|-------------|
| `prepare_protocol_for_client` | ⭐ SCEN-001-01 | ─ | ─ | 🔲 edge |
| `instruct_client_on_protocol` | 🔲 | 🔲 | 🔲 | ─ |
| `capture_data_spontaneously` | ─ | ⭐ SCEN-002-01 | 🔲 | 🔲 |
| `routine_data_entry` | ─ | 🔲 | 🔲 | 🔲 |
| `prepare_for_therapy_session` | 🔲 sec. | ⭐ SCEN-002-03 | 🔲 | ─ |
| `transfer_data_to_therapist` | ─ | ⭐ SCEN-002-02 | ⭐ SCEN-010-01 | ─ |
| `review_data_collaboratively` | ⭐ SCEN-001-02 | 🔲 client POV | 🔲 client POV | ─ |
| `self_review_and_reflect` | ─ | 🔲 sec. | 🔲 sec. | 🔲 |
| `export_data_externally` | 🔲 sec. | 🔲 | 🔲 | 🔲 |
| `backup_and_restore_data` | ─ | 🔲 | 🔲 | 🔲 |

✅/⭐ = exists | 🔲 = applicable, missing | ─ = not applicable

## New Scenario Metadata Fields

Every `scenario.md` YAML frontmatter should include these two new fields:

```yaml
# Add to existing scenario YAML frontmatter:
category: "capture.spontaneous"     # dot-notation: stage_id.sub_category_suffix
gold_status: false                  # true = user-approved gold standard
```

**Category format**: `[stage_id].[category_suffix]` where:
- `stage_id` = `creation`, `distribution`, `capture`, `analysis`, `management`
- `category_suffix` = short identifier derived from canonical_name

**Category values** (current):
| Category ID | Canonical Name |
|-------------|---------------|
| `creation.prepare_protocol` | `prepare_protocol_for_client` |
| `distribution.instruct_client` | `instruct_client_on_protocol` |
| `capture.spontaneous` | `capture_data_spontaneously` |
| `capture.routine` | `routine_data_entry` |
| `analysis.prepare_for_session` | `prepare_for_therapy_session` |
| `analysis.transfer_to_therapist` | `transfer_data_to_therapist` |
| `analysis.review_collaboratively` | `review_data_collaboratively` |
| `analysis.self_reflect` | `self_review_and_reflect` |
| `management.export` | `export_data_externally` |
| `management.backup_restore` | `backup_and_restore_data` |

## Gold Scenario Workflow

1. **Create**: Write scenario for ONE persona in a category
2. **Review**: User reads and provides feedback
3. **Approve**: User marks `gold_status: true` in YAML
4. **Propagate**: AI adapts gold scenario for all other relevant personas in that category
5. **Track**: Index updated with new instances

This ensures quality: every batch-generated scenario has a user-approved reference.

## Naming Quick Reference

### Folder Name Convention
```
[action]_[object]_[qualifier]     (snake_case)
```

### Variant Suffix (same persona, multiple scenarios of same category)
```
[canonical_name]__[qualifier]     (double underscore)
```
Only needed when ONE persona has multiple scenarios in the same category.

### Word Standardization
| Use | Avoid |
|-----|-------|
| `transfer` | handover, deliver |
| `protocol` | questionnaire, form |
| `capture` | dump, log, record |
| `collaboratively` | with_client, together |
| `spontaneously` | at_night, urgently |

## Integration Points

This index must be referenced in:
- [ ] `README_4_SCENARIO_DEFINITION.md` — link to this file, explain category system
- [ ] `create-scenario` skill — read YAML, validate category, suggest canonical name
- [ ] `README_7_META_INFO_STANDARDS.md` — document new `category` and `gold_status` fields

## Existing Scenario Assignments

| Scenario | Current Folder | Assigned Category | Notes |
|----------|---------------|-------------------|-------|
| SCEN-001-01 | `prepare_protocol_for_client` | `creation.prepare_protocol` | Name matches convention ✅ |
| SCEN-001-02 | `review_protocol_with_client` | `analysis.review_collaboratively` | Name acceptable, minor inconsistency (convention: `review_data_collaboratively`) |
| SCEN-002-01 | `brain_dump_at_night` | `capture.spontaneous` | Name inconsistent — context-based, not goal-based |
| SCEN-002-02 | `forgotten_protocol_transfer` | `analysis.transfer_to_therapist` | Name inconsistent — outcome-based |
| SCEN-002-03 | `prepare_for_therapy_session` | `analysis.prepare_for_session` | Name matches convention ✅ |
| SCEN-010-01 | `successful_protocol_handover` | `analysis.transfer_to_therapist` | Name inconsistent — outcome-based + wrong synonym |

**Renaming**: Handled by separate task (TASK-PROC-010-11 / fix persona scenario mismatches).
