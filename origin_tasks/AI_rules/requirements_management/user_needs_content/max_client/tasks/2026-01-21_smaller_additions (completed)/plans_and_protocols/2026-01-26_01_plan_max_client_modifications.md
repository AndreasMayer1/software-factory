# Plan: Max Client Persona and Scenarios Modifications

**Task ID**: TASK-PROC-013-01
**Agent ID**: architecture-advisor-2026-01-26-001
**Created**: 2026-01-26
**Status**: Plan Ready for Review

---

## Executive Summary

This plan covers modifications to the Max Client persona (`PERSONA-002`) and associated scenarios to:

1. **Persona Rewrite**: Convert the entire persona from describing app implications to pure status quo (pen and paper)
2. **New Sections**: Add Jobs to Be Done (therapy collaboration), Mental Models (psychological concepts), Pain Points (ineffective therapy sessions), Fears (context loss/mixing)
3. **Scenario Rewrite**: Rewrite `brain_dump_at_night` to status quo (pen and paper basis)
4. **New Scenario**: Create `forgotten_protocol_transfer` scenario

The persona is currently in DRAFT status (v2.0 from 2026-01-19) and already underwent one rewrite for Phase 4 standards. However, careful analysis reveals that **significant app solution references still remain** throughout the document that must be removed.

---

## Current State Analysis

### Persona (persona.md) - Current Issues

**Location**: `requirements_user_needs/personas/max_client/persona.md`
**Lines**: 378 total
**Version**: 2.0 (2026-01-19)
**Status**: Draft

#### Technology Neutrality Violations Found

The persona claims to describe status quo but contains numerous app-specific references:

| Section | Line(s) | Violation | Status Quo Equivalent |
|---------|---------|-----------|----------------------|
| Mental Models | 109-118 | "Tracking is **therapy homework** that he's supposed to do" - Acceptable, but mentions app in related sections | Keep therapy homework concept |
| Current Status Quo | 83-86 | "Alternative Attempts: Tried using **Notes app on phone**" - OK as current workaround | Keep as valid status quo |
| Anti-Persona Traits | 217-222 | "❌ **NOT a planner**: He uses the app reactively" - Direct app reference | Remove app reference |
| Section 3 Friction | 143-156 | References to "app" in barriers, "opening the app" | Rewrite to general tracking barriers |
| Environmental Constraints | 269, 289, 310 | "Any tracking solution must..." - Solution-oriented | Rewrite as pain point/need |
| Core Needs | 347-358 | "What would make Max adopt a new solution" - Solution-oriented | Remove or rewrite as needs |

#### Missing Sections (per goal.md requirements)

1. **Jobs to Be Done - Missing dimensions**:
   - Functional Jobs: Missing therapy preparation job, channel/content separation job
   - Social Jobs: Missing therapeutic alliance job

2. **Mental Models - Needs psychological concepts**:
   - Currently uses general concepts
   - Needs: "Protection of emotional investment" (Loeffel/energy concept)
   - Needs: "Sovereignty over disclosure" (control over sharing)

3. **Pain Points - Missing ineffective sessions**:
   - Current pain points focus on tracking mechanics
   - Missing: Wasted therapy time due to memory gaps

4. **Fears - Missing context mixing**:
   - Current fears focus on exposure/data
   - Missing: Fear of accidentally sharing private "venting" content with therapist

### Scenario (brain_dump_at_night/scenario.md) - Current Issues

**Location**: `requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/scenario.md`
**Lines**: 203 total
**Status**: in_review (flagged for technology neutrality review)

#### Critical Problem: This Scenario Describes the APP, Not Status Quo

The entire scenario describes Max using "the app" with features like:
- OLED dark mode (line 73)
- Voice-to-text button (line 75)
- Waveform visualization (line 82)
- Whisper detection (line 88)
- Auto-save (line 101)
- Lock icon with "local only" text (line 92)

**This completely violates the technology neutrality principle.** The scenario must be rewritten to show how Max currently handles this situation with pen and paper (status quo) and why it fails.

#### Notes and Feedback File

`notes_and_feedback.md` contains user feedback:
> "It's not true that using a smartphone keyboard is too loud, at least if the haptics and key press sounds are turned off. If that's the case it's quieter than speaking. But of course typing on a touchscreen is difficult in the middle of the night in bed."

This feedback should be incorporated into the status quo scenario to accurately represent the real friction (difficulty typing when tired/in dark) rather than false friction (keyboard noise).

### New Scenario Required: forgotten_protocol_transfer

A complete new scenario must be created based on the detailed content provided in goal.md. This scenario describes Max on public transit realizing he forgot his paper protocol at home before a therapy session.

---

## Required Changes (Detailed, Section by Section)

### 1. Persona: Jobs to Be Done Section (Lines 122-140)

**Current State**:
```markdown
### Functional Jobs
- **Track emotional/behavioral patterns for therapy**: ...
- **Offload circular thoughts**: ...
- **Document medication effects**: ...
- **Remember what happened**: ...

### Emotional Jobs
- **Feel less alone**: ...
- **Reduce therapy anxiety**: ...
- **Regain sense of control**: ...
- **Avoid "vulnerability hangover"**: ...

### Social Jobs
- **Be a "good patient"**: ...
- **Avoid burdening others**: Instead of texting friends at 2 AM, he logs thoughts in the app
```

**Required Changes**:

Add to **Functional Jobs**:
```markdown
- **Prepare for therapy session**: Max wants to collect information to discuss with Dr. Sarah. He wants to avoid sitting with "empty head" (Memory Fog) and wasting valuable therapy time with memory gaps.
- **Separate channel and content**: He needs to distinguish between "Private Outlet" (thoughts nobody should see) and "Therapeutic Material" (observations relevant for Dr. Sarah).
```

Add to **Social Jobs**:
```markdown
- **Strengthen therapeutic alliance**: He wants to fulfill his part of the agreement ("do homework") to actively participate in his recovery. He accepts the support even when it's exhausting.
```

Fix existing **Social Jobs** violation (line 139):
- Change: "Instead of texting friends at 2 AM, he logs thoughts in the app"
- To: "Instead of texting friends at 2 AM, he wants an outlet for processing thoughts"

### 2. Persona: Mental Models Section (Lines 107-120)

**Current State**:
```markdown
**How Max thinks about tracking**:
- Tracking is **therapy homework** that he's supposed to do but often fails at
- He wants to be a "good patient" but feels like he's constantly failing
- The act of writing thoughts down should provide **immediate relief** (externalizing rumination), not add more burden
- He needs **memory support**—something that remembers for him when his brain can't
```

**Required Changes**:

Add/Replace with psychological concepts:

```markdown
**How Max thinks about tracking**:

- **Protection of emotional investment**: For Max, it costs enormous energy ("spoons"/Loeffel) to put his feelings into words. Once he has invested this energy, he expects absolute safety that the result won't be lost (whether through lost papers or technical errors). A loss would trigger immediate resignation ("I don't have the strength to write that again").

- **Sovereignty over disclosure**: Max views his records as an extension of his memory. He expects that *nothing* leaves his device or is seen by others unless he decides in an explicit, conscious moment to "hand it over" (like handing over a piece of paper). Automatic background processes feel like loss of control.

- He needs **memory support**—something that remembers for him when his brain can't

- The act of writing thoughts down should provide **immediate relief** (externalizing rumination), not add more burden
```

### 3. Persona: Pain Points Section (Lines 93-105)

**Current State**:
```markdown
### Pain Points with Current Approach

**For Max (Tracking)**:
- ...existing points...

**For Therapy (Analysis)**:
- ...existing points...
```

**Required Addition**:

Add to "For Therapy (Analysis)":
```markdown
- 🔴 **Ineffective sessions**: Without records, Max spends the first 20 minutes of therapy trying to remember how the week was. He is frustrated that he cannot give Dr. Sarah concrete starting points to work on his problems.
```

### 4. Persona: Friction & Barriers Section (Lines 143-157)

**Current State** (line 148-149):
```markdown
- 🟡 **Failure at tracking**: If he misses days, he feels like he's "failing" even at self-help
- 🟡 **Privacy violated by voice input**: Worry that whispered entries are being recorded somewhere remotely
```

**Required Changes**:

1. Remove app-specific reference in line 149 (voice input worry is app-specific)
2. Add new fear:

```markdown
- 🟡 **Fear of context loss/mixing**: The worry that in the session he might accidentally read or hand over private, unfiltered anger-thoughts that were only meant for "venting." He needs a clear boundary between personal outlet and therapeutic material.
```

### 5. Persona: Anti-Persona Traits Section (Lines 216-224)

**Current State** (line 222):
```markdown
- ❌ **NOT a planner**: He uses the app reactively (when in distress), not proactively (daily habit)
```

**Required Change**:
```markdown
- ❌ **NOT a planner**: He tracks reactively (when in distress), not proactively (daily habit)
```

### 6. Persona: Environmental Constraints Section (Lines 251-319)

**Current Issues**:
- Lines 269, 289, 310 contain "Any tracking solution must..." language (solution-oriented)

**Required Changes**:

Replace solution requirements with needs statements:

Line 269:
- From: "**Requirement**: 🔴 Any tracking solution must prevent accidental exposure..."
- To: "**Need**: 🔴 Max needs a safe space for honest expression without risk of partner discovery"

Line 289:
- From: "**Requirement**: 🔴 Any tracking solution must enable silent expression in dark, shared bedroom..."
- To: "**Need**: 🔴 Max needs to be able to externalize thoughts silently in darkness without disturbing sleeping partner"

Line 310:
- From: "**Requirement**: 🟡 Any tracking solution should enable usage in semi-public spaces..."
- To: "**Need**: 🟡 Max needs to capture thoughts in public without revealing mental health context to observers"

### 7. Persona: Core Needs Section (Lines 347-365)

**Current Issues**:
- Line 360-364 contains solution-oriented language

**Required Changes**:

Remove or rewrite lines 360-364:
```markdown
**Current solution (paper journal + phone notes)**: Meets some needs poorly. Fails completely at nocturnal tracking, memory support, and shame-free gaps.
```
(This is acceptable status quo analysis - keep it)

Remove lines 360-364:
```markdown
**What would make Max adopt a new solution**:
- If it worked when and where he actually needs it (bed at 2 AM, commute, post-crisis)
- If it didn't add shame when he inevitably has gaps
- If it protected his privacy from Sophie and strangers
- If it was faster/easier than the current approach
```
(This is solution-oriented - DELETE this entire block)

---

## Scenario: brain_dump_at_night Rewrite

### Current State (INVALID)

The current scenario describes Max using an app with:
- OLED dark mode
- Voice-to-text with whisper detection
- Auto-save
- Privacy indicators

This is a **Future State Scenario** masquerading as a status quo scenario.

### Required Rewrite

Replace the entire scenario content with the status quo version provided in goal.md. Key elements:

**Act 1**: 02:15 AM, Max can't sleep, thoughts looping about work mistake and missed email. Reaches for therapy notebook on nightstand.

**Act 2**:
- Knocks over water glass (loud clatter)
- Partner (Sophie) stirs and asks if he's okay
- He can't turn on light (would wake Sophie fully)
- Can't go to living room (getting up = fully awake for 2 more hours)
- Chooses to write in the dark
- Pen clicking sounds loud
- Writes blindly, probably over yesterday's notes
- Can't see page edges, crossing spiral binding
- Friction of pen on paper feels loud
- Effort of writing legibly without sight increases agitation

**Act 3**:
- Gives up after 2 minutes of blind scribbling
- Lies back down, no relief
- Worries about whether writing is legible
- Anxiety about *method* replaces anxiety about work email
- **Next morning**: Opens notebook, page is mess of overlapping scrawls, mostly illegible
- Feels frustrated and stupid
- "Therapy homework" feels like another failure

**Emotional shift**: Anxiety (Looping thoughts) -> Frustration (Physical barriers) -> Resignation (Giving up) -> Shame (Next morning)

### Status Quo Analysis Section

Add analysis section showing why paper fails:
1. **Light Constraint**: Paper requires external light
2. **Sound Constraint**: Physical interactions are audible
3. **Physical Friction**: Moving to another room creates "Wall of Awful"
4. **Data Integrity**: Writing blindly = illegible data (Data Loss)
5. **Feedback Loop**: Failure creates new shame/anxiety

### Derived Needs Section (NOT solution features)

Describe needs, not features:
1. Need for dark/discreet usage
2. Need for silent input
3. Need for low-friction access
4. Need for legible/reliable capture

---

## New Scenario: forgotten_protocol_transfer

### File Location

Create: `requirements_user_needs/personas/max_client/scenarios/forgotten_protocol_transfer/scenario.md`

### Content Structure

Use the complete scenario provided in goal.md with these sections:

**Metadata**:
```yaml
---
scenario_id: SCEN-002-02
persona_id: PERSONA-002
name: Forgotten Protocol & Transfer Shame
created: 2026-01-26
updated: 2026-01-26
evidence_level: proto_persona
review_status: draft
review_history:
  - date: 2026-01-26
    from: null
    to: draft
    reviewer: LLM
    notes: "Initial creation per TASK-PROC-013-01"
---
```

**Goal**: Successfully hand over filled "Weekly Anxiety Protocol" to Dr. Sarah at session start

**Context**: Tuesday 15:45, on S-Bahn commuting to 16:00 therapy appointment

**Three-Act Structure**:
- Act 1: Verification & Shock (realizes protocol folder is at home on shoe rack)
- Act 2: Attempted Reconstruction (tries to reconstruct data on phone, realizes he's fabricating)
- Act 3: Confession & Wasted Time (admits to Dr. Sarah, 15 min spent reconstructing, session less effective)

**Status Quo Analysis**:
1. Single Point of Failure (data in one physical location)
2. Object Permanence (ADHD symptom)
3. Data Quality vs. Recall Bias
4. Inefficiency (therapy time wasted)
5. Relational Strain (teacher/student dynamic)

**Derived Needs**:
1. Data must be on device Max always has (phone)
2. No extra object to remember
3. Ability to transfer data even when running late

---

## Downstream Impact Assessment

### Affected Files

| File | Impact | Action Required |
|------|--------|-----------------|
| `persona.md` | Major rewrite | Apply all changes in sections 1-7 above |
| `brain_dump_at_night/scenario.md` | Complete rewrite | Replace with status quo version |
| `brain_dump_at_night/user_flows/quick_night_entry/flow.md` | Orphaned | Review - may need deletion or marking as "future state" |
| `brain_dump_at_night/notes_and_feedback.md` | Reference | Incorporate keyboard noise feedback into rewrite |

### New Files to Create

| File | Purpose |
|------|---------|
| `forgotten_protocol_transfer/scenario.md` | New scenario per goal.md |

### Cross-References to Update

The persona links to scenarios at the end (lines 347+). After creating the new scenario, add:
```markdown
## Related Scenarios

- [Brain Dump at Night](scenarios/brain_dump_at_night/scenario.md) - Nocturnal rumination and tracking friction
- [Forgotten Protocol Transfer](scenarios/forgotten_protocol_transfer/scenario.md) - Paper protocol forgotten at home before therapy
```

---

## Implementation Steps

### Step 1: Persona Modifications

1. Read current `persona.md` (already done in analysis)
2. Make changes to Jobs to Be Done section (add therapy preparation, channel separation, therapeutic alliance)
3. Make changes to Mental Models section (add psychological concepts: emotional investment protection, disclosure sovereignty)
4. Make changes to Pain Points section (add ineffective sessions)
5. Make changes to Friction & Barriers section (add context loss fear, remove app-specific references)
6. Make changes to Anti-Persona Traits section (remove app reference)
7. Make changes to Environmental Constraints section (convert solution requirements to needs)
8. Make changes to Core Needs section (remove solution-oriented block)
9. Update version to 3.0, update date, add review history entry

### Step 2: brain_dump_at_night Scenario Rewrite

1. Read current `scenario.md` (already done)
2. Create complete replacement content based on goal.md status quo version
3. Update metadata (review_status, version)
4. Incorporate feedback from notes_and_feedback.md (keyboard noise correction)
5. Add proper status quo analysis section
6. Remove all app-specific features and replace with paper-based workflow

### Step 3: Create forgotten_protocol_transfer Scenario

1. Create directory: `requirements_user_needs/personas/max_client/scenarios/forgotten_protocol_transfer/`
2. Create `scenario.md` with full content from goal.md
3. Ensure proper YAML frontmatter
4. Apply scenario template structure
5. Add evidence level markers

### Step 4: Verify and Update Cross-References

1. Update persona's Related Scenarios section
2. Check for any other files referencing modified content
3. Update CHANGE_PROPAGATION.md if needed

---

## Quality Criteria

### For Persona

- [ ] No app-specific references remain
- [ ] All sections describe status quo (pen and paper)
- [ ] Jobs to Be Done includes therapy preparation, channel separation, therapeutic alliance
- [ ] Mental Models includes psychological concepts (emotional investment, disclosure sovereignty)
- [ ] Pain Points includes ineffective sessions
- [ ] Fears includes context loss/mixing concern
- [ ] Evidence level markers are present
- [ ] Version updated to 3.0

### For brain_dump_at_night Scenario

- [ ] Describes status quo (paper/pen), NOT app
- [ ] Three-act structure maintained
- [ ] Status quo analysis section present
- [ ] Derived needs (not solution features) documented
- [ ] Evidence level markers present
- [ ] Incorporates keyboard noise feedback correction
- [ ] review_status updated

### For forgotten_protocol_transfer Scenario

- [ ] Complete scenario created per goal.md content
- [ ] Proper YAML frontmatter
- [ ] Three-act structure
- [ ] Status quo analysis section
- [ ] Derived needs documented
- [ ] Evidence level markers present

### General

- [ ] All changes follow README guidelines (persona definition, scenario definition, technology neutrality)
- [ ] German source content properly translated/adapted to English
- [ ] No emojis added (user instruction from CLAUDE.md)

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep into user flows | Medium | Explicitly exclude user flow modifications from this task |
| Loss of valuable app design insights | Low | Current app-focused content can be moved to separate "future state" documents if needed |
| Inconsistency with other personas | Low | Review Dr. Sarah persona for alignment after changes |
| German content translation quality | Medium | Flag any uncertain translations for user review |

---

## Notes

1. The goal.md content is partially in German. Translations should be reviewed for accuracy.

2. The current brain_dump_at_night scenario has significant value as a "future state" scenario. Consider:
   - Renaming current file to `scenario_future_state.md`
   - Creating new `scenario.md` with status quo content
   - Or simply replacing (simpler approach, loses future state vision)

3. The user flow `quick_night_entry/flow.md` under brain_dump_at_night describes app behavior and may need to be marked as future state or deleted. This is out of scope for this task but should be flagged.

---

**Plan Created By**: architecture-advisor-2026-01-26-001
**Ready for Review**: Yes
**Next Step**: User approval, then implementation by implementation-engineer agent
