# Persona Coverage Gap Analysis - Findings

**Task**: TASK-PROC-027-02
**Date**: 2026-02-08
**Agent**: opus (via switch-to-opus skill)
**Phase**: Exploration (Phase 1 of goal.md)

## Executive Summary

Analyzed all 13 existing personas across therapy types. **One critical gap identified**: Prof. Dr. Weber (Tiefenpsychologie therapist) has no corresponding client persona. This gap represents fundamentally different app requirements (dream diaries, narrative processing vs. structured protocols).

**Recommendation**: Create one new TP client persona. Flag Systemische Therapie gap for user decision.

---

## Current Persona Landscape

### By Role
- **Therapists** (3): Dr. Sarah (VT), Dr. med. Turan (Psychiatry), Prof. Dr. Weber (TP/PA)
- **Clients** (4): Max (VT/Depression), Sophie (VT/ADHD), Jana (DBT/BPD), Elias (VT/Exposure)
- **Self-Users** (5): David, Hanna, Lisa, Michael, Nina
- **System** (1): System/Maintenance

### Therapy Type Coverage Matrix

| Richtlinienverfahren | Client Persona | Therapist Persona | Status |
|---|---|---|---|
| **Verhaltenstherapie (VT)** | Max, Sophie, Elias | Dr. Sarah | ✅ Fully covered |
| **DBT** (VT variant) | Jana | Dr. Sarah (implicit cluster) | ✅ Covered (client exists) |
| **Tiefenpsychologie (TP)** | **NONE** | Prof. Dr. Weber | ❌ **CRITICAL GAP** |
| **Psychoanalyse (PA)** | **NONE** | Prof. Dr. Weber | ⚠️ Low priority (niche, overlaps TP) |
| **Systemische Therapie (ST)** | **NONE** | **NONE** | ⚠️ Flag for user |
| **Psychiatrie** | None explicit | Dr. med. Turan | ⚠️ Sophie covers medication |

---

## Gap Analysis & Decisions

### Gap 1: Tiefenpsychologie Client ❌ CRITICAL

**Status**: Prof. Dr. Weber exists as therapist, NO client persona

**Why it matters**:
- TP is one of the 3 German Richtlinienverfahren (alongside VT and ST)
- TP homework is **fundamentally different** from VT:
  - VT: Structured protocols, checkboxes, mood scales, exposure logs
  - TP: Dream diaries, free association, narrative journaling, "felt sense"
- Prof. Dr. Weber's anti-metrics stance creates unique requirements
- No existing client persona captures TP therapy experience

**Requirements impact**:
- Dream diary functionality (time-on-waking capture, emotional texture preservation)
- Free-form narrative entry (vs. structured forms)
- Anti-quantification UI patterns (no graphs, no streaks, no metrics)
- Memory preservation ("What did the dream *feel* like?" not just "What happened?")

**Decision**: **CREATE NEW PERSONA**
**User pre-approval**: YES (from goal.md)
**Persona ID**: PERSONA-015
**Proposed name**: Lena (The Depth Seeker)
**Proposed archetype**: "The Meaning-Maker"

---

### Gap 2: Systemische Therapie (ST) ⚠️ FLAG

**Status**: No therapist OR client persona

**Why it matters**:
- ST became Kassenleistung in 2020 (one of 3 official Richtlinienverfahren)
- Growing adoption, especially for relationship/family issues
- Unique homework patterns: circular questioning, genograms, solution-focused scaling, relationship mapping

**Requirements impact**:
- Visual/diagram tools (family genograms, relationship maps)
- Circular questioning frameworks
- Solution-focused scaling (0-10 scales with narrative context)
- Multi-person perspective tracking

**Decision**: **FLAG AND PAUSE FOR USER**
**Rationale**: Significant enough to warrant consideration, but creates scope creep. User should decide priority.

---

### Gap 3: DBT Therapist ⚠️ NO ACTION

**Status**: Jana (DBT client) exists, no dedicated DBT therapist persona

**Why it's acceptable**:
- Dr. Sarah's implicit clusters explicitly include "DBT therapists (skill chains)"
- DBT is technically a VT variant (billed as VT in Germany)
- Therapist-side DBT requirements are largely covered by VT patterns
- Jana already captures the unique *client* experience (emotion volatility, crisis access)

**Decision**: **NO ACTION NEEDED**
**Rationale**: Adding a dedicated DBT therapist adds minimal unique requirements beyond what Dr. Sarah + Jana already cover.

---

### Gap 4: Psychiatry Client for Dr. Turan ⚠️ NO ACTION (SCENARIO INSTEAD)

**Status**: Dr. med. Turan exists, no client explicitly describes psychiatry appointments

**Why it's acceptable**:
- Sophie already covers medication tracking (ADHD medication)
- Psychiatry appointments are brief, focused on medication efficacy
- The medication tracking *need* is already represented

**Decision**: **NO ACTION (or ADD SCENARIO)**
**Rationale**: If needed, add a scenario to Sophie like "psychiatry_medication_check" rather than creating a full persona. The core requirement (medication tracking) is already covered.

**Alternative**: Add scenario to existing client showing psychiatrist relationship.

---

### Gap 5: Psychoanalyse (PA) Client ⚠️ NO ACTION

**Status**: Prof. Dr. Weber covers both TP and PA on therapist side, no client

**Why it's acceptable**:
- PA and TP share homework patterns (dream work, free association, narrative)
- PA is a niche with very few patients compared to TP
- One TP client persona covers both therapeutic approaches

**Decision**: **COVERED BY TP CLIENT**
**Rationale**: The new TP client (PERSONA-015) will also represent PA clients since the homework patterns are nearly identical.

---

## Implementation Recommendations

### Phase 2: Immediate Actions (User Pre-Approved)

1. **Create PERSONA-015**: Tiefenpsychologie client
   - Use `create-persona` skill
   - Name: Lena (The Depth Seeker)
   - Archetype: "The Meaning-Maker"
   - Contrasts with VT clients: narrative vs. structured, felt sense vs. metrics
   - review_status: draft
   - gold_status: false

2. **Create REQ-PROC-028**: Incremental improvement requirement for new persona
   - Follow pattern of REQ-PROC-012 through REQ-PROC-025

### Phase 2: User Decision Required

3. **Systemische Therapie gap**: Present to user
   - Question: "Should we create ST therapist + client personas now, or defer to future requirement?"
   - Impact: Medium priority, growing user base, unique visual/relational requirements
   - Effort: 2 personas (therapist + client)

---

## Decision Criteria Summary

**When to CREATE new persona**:
- Introduces requirements NO existing persona covers
- Represents a distinct therapy type or user pattern
- Has fundamentally different homework/tracking needs

**When to ADD SCENARIO instead**:
- Core requirements already covered by existing persona
- Only need to show a different context or trigger
- Difference is situational, not fundamental

**When NO ACTION needed**:
- Requirements fully covered by existing personas
- Difference is superficial or edge case
- Adding persona would duplicate coverage

---

## Next Steps

1. User reviews this gap analysis
2. User decides on Systemische Therapie gap (create now vs. defer)
3. Proceed to Phase 2: Create PERSONA-015 using `create-persona` skill
4. Create REQ-PROC-028 for new persona's incremental improvement

**Agent ID for resuming**: (Opus write complete, return to Sonnet orchestrator)
