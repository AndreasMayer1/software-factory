# Opus Plan: Non-User Personas & Planet Centered Design Integration

**Date**: 2026-01-17
**Agent**: Opus (planning)
**Agent ID**: opus-plan-003
**Phase**: 3+ (Extended Content - Non-User Personas & PCD)

---

## Objective

Update `requirements_user_needs/README.md` to integrate:
1. **Non-User Personas** (Shoulder Surfer, Auditory Witness, Intimate Intruder) as environmental constraints
2. **Planet Centered Design (PCD)** as a cross-cutting layer affecting all personas/scenarios/flows

The key insight: Non-users are NOT separate personas (they have no goals in the app). They are **constraints** that modify main persona behavior. PCD is a **cross-cutting concern** that applies to all artifacts.

---

## Analysis Summary

### From Explore Agent Investigation

**Non-User Personas Integration Approach**:
- NOT separate persona files (violates hierarchy - no goals, no flows)
- YES as "Environmental Constraints" section in each main persona
- YES as friction/plot twists in scenarios (3-act structure)
- YES as "Environment/Non-User Swimlane" in user flows

**Three Shadow Personas**:
1. **Shoulder Surfer**: Stranger in public seeing display → needs low-contrast/discreet mode
2. **Auditory Witness**: Person hearing app sounds/voice input → needs headphone detection, panic-mute
3. **Intimate Intruder**: Trusted person with device access → needs app-switcher blur, biometric re-auth

**PCD Integration Approach**:
- NOT a separate persona
- YES as cross-cutting "Green Constraints" affecting all levels
- Five key principles: Hardware Longevity, Energy Efficiency, Data Minimization, Suffizienz, Co-Benefits

### Current README Structure (Line Numbers)

| Section | Line Start | Content |
|---------|------------|---------|
| 1. Overview | 3 | Problem, Solution, Benefits |
| 2. Folder Structure | 75 | File organization |
| 3. Persona Definition | 134 | 7 elements, mental health specifics, template |
| 4. Scenario Definition | 552 | 3-act structure, template |
| 5. User Flow Definition | 823 | Exception model, template |
| 6. Meta Information Standards | 1177 | YAML frontmatter |
| 7. Cross-referencing System | 1316 | Links between files |
| 8. Skill Modifications | 1456 | New skills needed |
| 9. Writing Guidelines | 1589 | Language, tone, perspective |
| 10. Validation Rules | 1697 | Structural, content checks |

---

## Execution Plan

### Single Agent: Implementation Engineer

**Why single agent**: This is a documentation update task. All changes are to one file (README.md) with interconnected content that requires consistent voice and cross-references.

### Step 1: Add Section 3.8 - Environmental Constraints (Non-User Personas)

**Location**: After Section 3.7 "Real Quotes" (around line 220), before "Mental Health Specific Requirements"

**Content to add**:
```markdown
#### 8. Environmental Constraints (Non-User Personas)

Beyond the user themselves, consider **who else might see, hear, or access** the app. These "non-users" don't have goals in your app, but their presence fundamentally shapes how your user interacts with it.

##### The Three Shadow Personas

For privacy-sensitive applications like mental health trackers, three non-user archetypes matter:

**1. The Shoulder Surfer**
*Stranger in public space (train, bus, waiting room)*

- **Behavior**: Sits nearby, casually glances at bright display out of boredom
- **Threat**: Reads sensitive words ("Therapy", "Depression", "Anxiety") or sees mood graphs
- **Impact on User**: Won't open app if content is visibly "medical" or "mental health"
- **Design Requirements**:
  - Low-contrast / Privacy mode with blur effect
  - Discreet icons (geometric shapes, not crying faces)
  - No large titles like "YOUR ANXIETY DIARY"
  - Quick toggle for "Discreet Mode"

**2. The Auditory Witness**
*Colleague in open office, family in adjacent room, stranger in café*

- **Behavior**: Listens without looking; perceives app sounds or spoken entries
- **Threat**: Hears voice-to-text input OR embarrassing app sounds (achievement "pling" during sad entry)
- **Impact on User**: Won't use voice features or may self-censor
- **Design Requirements**:
  - Headphone detection: Never play audio without headphones (default mute)
  - Panic-Mute: Flip phone face-down → immediate stop of audio/recording
  - Visual feedback instead of audio confirmation (waveform, not beeps)

**3. The Intimate Intruder**
*Partner, parent, child, or roommate with device access*

- **Behavior**: Picks up unlocked phone to "quickly Google something" or show photos
- **Threat**: Swipes into app via multitasking menu, reads intimate entries
- **Impact on User**: Fear of leaving phone unattended; may avoid honest entries
- **Design Requirements**:
  - App-switcher obfuscation: Preview thumbnail must be blurred or show logo, not content
  - Biometric re-auth: FaceID/fingerprint required when resuming from background (no delay)
  - Notifications hide content: "Time for your check-in" not "How was your panic attack?"

##### Plausible Deniability

For mental health apps, users may need to **deny the app's true purpose**. A controlling partner or nosy colleague might ask "What's that app?"

- **Bad Design**: App named "PsychoHelp" with medical symbols
- **Good Design**: App looks like a notes app or calendar on first glance
- **Best Design**: "Camouflage Mode" that transforms UI to look like a spreadsheet or weather widget

##### How to Document Environmental Constraints

In each persona, add a section:

```markdown
## Environmental Constraints

### Non-User: [Name] (e.g., Intimate Intruder)
- **Context**: [Where/when this non-user is present]
- **Threat**: [What they might see/hear/access]
- **Impact**: [How this affects user behavior]
- **Requirement**: [Design requirement to address this]
```

**Example for Max (Client)**:
```markdown
## Environmental Constraints

### Non-User: Intimate Intruder (Partner at Home)
- **Context**: Partner picks up Max's phone from nightstand
- **Threat**: Sees app in recent-apps list, opens it, reads mood entries
- **Impact**: Max censors entries or avoids using app when partner is home
- **Requirement**: Biometric re-auth on resume; blurred app-switcher preview

### Non-User: Shoulder Surfer (Public Transit)
- **Context**: Stranger on train sits next to Max
- **Threat**: Sees "mood: 2/10" or "Therapy homework: breathing exercises"
- **Impact**: Max won't log moods in public
- **Requirement**: Discreet Mode with low contrast, no visible labels
```
```

### Step 2: Add Section 4.8 - Non-User Integration in Scenarios

**Location**: After "Example Scenario: Brain Dump at Night" (around line 820), before Section 5

**Content to add**:
```markdown
### Non-User Integration in Scenarios

Non-users appear in scenarios as **friction points** or **plot twists** that force design considerations.

#### The "Privacy Glitch" Pattern

Include a moment in your scenario where the user must protect their screen or stop their action because a non-user appears.

**Structure**:
1. User is engaged with app
2. Non-user enters the scene (or user notices them)
3. User reacts (hides phone, closes app, activates privacy mode)
4. System response (how does the app help?)
5. Resolution (user continues or abandons)

**Example**: Brain Dump at Night (Extended with Non-User)

> **Act 2 (Extended)**:
> Marcus is whispering his third sentence into the app when his wife shifts in bed. His body freezes.
>
> *Internal thought: "Did she wake up? Can she hear me?"*
>
> He quickly lowers his voice to barely audible. The app's whisper-detection adjusts sensitivity automatically. The waveform shows it's still capturing.
>
> His wife settles back into sleep. Marcus exhales and finishes his entry.
>
> **What this reveals**: Voice-to-text must work at whisper level. Visual feedback (waveform) is critical when audio confirmation isn't possible.

#### Documenting Non-User Moments

In scenario files, use this pattern:

```markdown
### Act 2: Interaction & Resistance

[Regular flow description...]

**[Privacy Glitch]**
- **Non-User**: [Who appears/is present]
- **User Reaction**: [What user does]
- **System Response**: [How app helps]
- **Outcome**: [Resolution]
```
```

### Step 3: Add Section 5.9 - Environment/Non-User Swimlane

**Location**: After "Adaptive UI Based on State" section (around line 1025), before "User Flow Template"

**Content to add**:
```markdown
### Environment/Non-User Swimlane

For privacy-critical flows, extend the standard swimlane table with an **Environment** column that shows non-user presence and system adaptations.

#### Basic Structure

| Step | Environment (Non-User) | User Action | System Response | UI State |
|------|------------------------|-------------|-----------------|----------|
| 1 | [Who's present, context] | [What user does] | [What system does] | [Screen/state] |

#### Example: Discreet Entry on Public Transit

**Scenario**: Max wants to log anxiety while on a crowded train.

| Step | Environment | User Action | System Response | UI State |
|------|-------------|-------------|-----------------|----------|
| 1 | **Shoulder Surfer** sitting adjacent | Opens app | Detects public location (optional), default mode | Home screen |
| 2 | Surfer glances at screen | Taps "Discreet Mode" toggle | Activates low-contrast theme, hides labels | Discreet Mode active |
| 3 | Surfer still present | Starts typing entry | Text displayed in muted colors, no headers | Entry screen (discreet) |
| 4 | Surfer loses interest | Completes entry | Auto-saves | "Saved" indicator (subtle) |
| 5 | Surfer looks away | Continues or exits | Returns to normal mode (manual) or stays discreet | Normal/Discreet |

#### Key Concepts for Environment Swimlane

**Passive Triggers**: Non-user presence changes state without user action
- Flow rule: `IF environment == unsafe THEN default_view = discreet`

**Interrupts**: Non-user disrupts active flow
- User recording voice entry → Non-user enters room → User stops abruptly
- System must treat abrupt stop as "pause," not "cancel"

**Plausible Deniability States**: Screens that exist only to deceive non-users
- "Fake Exit" button → Shows calculator or calendar instead of closing
- Flow pauses visually but state is preserved

#### When to Use Environment Swimlane

Include Environment column when:
- [ ] Flow involves sensitive content (mood entries, therapy notes)
- [ ] Flow uses audio input/output
- [ ] Flow could be interrupted by others (home, office, public)
- [ ] User might need to quickly hide content

Skip Environment column when:
- Flow is purely technical (database migration, backup)
- Content is not sensitive (settings, preferences)
- User is guaranteed to be alone (explicitly stated in scenario)
```

### Step 4: Insert NEW Section 6 - Planet Centered Design Layer

**Location**: BEFORE current Section 6 (Meta Information Standards, line 1177)

**This requires renumbering**:
- Current Section 6 → Section 7
- Current Section 7 → Section 8
- Current Section 8 → Section 9
- Current Section 9 → Section 10
- Current Section 10 → Section 11

**Content to add as NEW Section 6**:
```markdown
---

## 6. Planet Centered Design Layer

### What is Planet Centered Design?

Planet Centered Design (PCD) extends Human Centered Design by considering environmental impact alongside user needs. If a feature helps the user but harms the planet (excessive energy use, e-waste acceleration), it's not good design.

For a **local-first mental health app**, PCD manifests as:
- Respecting device hardware limitations
- Minimizing energy consumption
- Reducing data accumulation (digital waste)
- Designing for "right measure" (Suffizienz), not engagement maximization

### Why PCD Matters for This App

1. **Local-first is already green**: No server farms, no cloud sync overhead = minimal CO₂ footprint
2. **Mental health + environment are linked**: Depression correlates with climate anxiety; sustainable habits improve wellbeing
3. **Hardware longevity = accessibility**: Vulnerable populations often use older devices; forcing upgrades creates barriers to care
4. **Suffizienz aligns with therapy**: "Minimum effective dose" is therapeutic AND ecological

### The Five PCD Principles

#### 1. Hardware Longevity (Against E-Waste)

**Principle**: The app must never be the reason a user needs a new phone.

**Constraints**:
- Support devices 5+ years old
- No heavy libraries that require latest hardware
- Graceful degradation on low-memory devices
- Works offline without sync pressure

**Design Implications**:
- Test on iPhone 8 / 5-year-old Android
- Keep app size < 50MB
- Minimize background processes
- Offer "Low Performance Mode" that disables animations

**Persona Integration**: Add to Tech Ecosystem section:
```markdown
**Device Reality**: [Include older device in range]
**PCD Constraint**: App must not require hardware upgrade
```

#### 2. Energy Efficiency (Battery & Screen)

**Principle**: Minimize battery drain, especially on OLED screens.

**Constraints**:
- Dark mode as DEFAULT (not option)
- True black (#000000) not dark grey (#121212) for OLED pixel-off savings
- Disable animations when battery < 20%
- No unnecessary background wake-ups

**Design Implications**:
- Dark Mode First: Justified by PCD, not just aesthetics
- Auto-dim based on ambient light
- "Battery Saver" mode that strips visual flourishes

**Flow Integration**: Note energy cost in Resource column:
```markdown
| Step | User Action | System Response | Energy Cost |
|------|-------------|-----------------|-------------|
| 1 | Opens app | Dark mode loads | Low (OLED black) |
```

#### 3. Data Minimization (Against Digital Waste)

**Principle**: Don't store data that isn't needed; old data slows devices and becomes liability.

**Constraints**:
- Define data lifecycle policies (e.g., audio → text after 30 days)
- Auto-archive old entries after threshold
- Compress media at source before storage
- Offer "Data Cleanup" assistant

**Design Implications**:
- Notify user: "I cleaned up 200MB of old cache to keep your phone fast"
- Don't store raw sensor data indefinitely
- Export before delete for data-conscious users

**Persona Integration**: Add to Friction & Barriers section:
```markdown
**PCD Concern**: [Data accumulation worries, storage anxiety]
```

#### 4. Suffizienz (Right Measure)

**Principle**: Design for quick exit, not extended engagement. "Minimum effective dose."

**Constraints**:
- Entry should complete in < 60 seconds
- After goal achieved, app suggests closing
- No "You might also like..." suggestions
- No streaks that shame for missed days

**Design Implications**:
- Post-entry message: "All done. Go breathe. App closes in 3...2...1"
- Success = honest entry, not time-on-app
- Hide engagement metrics from user

**Scenario Integration**: Add to Success Criteria:
```markdown
**Suffizienz Check**:
- [ ] Goal achieved with minimum necessary interaction
- [ ] No artificial engagement extension
- [ ] User exits feeling complete, not trapped
```

#### 5. Co-Benefits (Regenerative UX)

**Principle**: When possible, suggest actions that benefit user AND planet.

**Constraints**:
- Prioritize habits that have environmental co-benefits
- Mark "Planet Friendly" habits with subtle indicator
- Don't lecture; nudge gently

**Design Implications**:
- User wants "Move more" → Suggest cycling over gym
- User wants "Eat healthier" → Suggest seasonal/local food
- Small 🌿 icon for eco-friendly habit suggestions

**Flow Integration**: When creating habit suggestion flows, include co-benefit evaluation:
```markdown
| Habit Request | Standard Suggestion | PCD Co-Benefit Suggestion |
|---------------|---------------------|---------------------------|
| "Exercise more" | "Gym 3x/week" | "Cycle to work 2x/week" 🌿 |
| "Eat better" | "Count calories" | "Cook seasonal/local" 🌿 |
```

### Integrating PCD Across Levels

#### In Personas

Add "Device & Ecological Constraints" field:
```markdown
## Device & Ecological Constraints

**Device Range**: iPhone 8 to current; 5-year-old Android to current
**Energy Sensitivity**: [High if older device / limited battery]
**Data Sensitivity**: [Concerns about storage, cleanup preferences]
**Suffizienz Alignment**: [Does this persona want quick in/out or extended sessions?]
```

#### In Scenarios

Add PCD checkpoint to 3-act structure:
```markdown
### Act 3: Result & Feeling

[Resolution description...]

**PCD Check**:
- Time to complete: [Duration]
- Energy cost: [Low/Medium/High]
- Data generated: [Size estimate, lifecycle]
- Exit prompt shown: [Yes/No]
```

#### In User Flows

Add Resource Cost column (optional, for energy/data-intensive flows):
```markdown
| Step | User Action | System Response | Resource Cost |
|------|-------------|-----------------|---------------|
| 1 | Opens app | Loads dark theme | Low (OLED black) |
| 2 | Records voice | Transcribes locally | Medium (CPU) |
| 3 | Saves entry | SQLite write | Low |
```

### PCD as Competitive Advantage

**Local-first = Zero-network path**: Your app's offline-first architecture is inherently environmentally friendly. Highlight this:

- Onboarding: "Your data never leaves your device. Good for privacy. Good for the planet."
- Marketing: "Zero-network mood tracking"
- Settings: Show "Carbon footprint: 0g CO₂ per entry" (vs. cloud-syncing competitors)

### PCD Validation Checklist

Add these to Section 11 (Validation Rules):

- [ ] Dark mode is default (not light theme)
- [ ] True black (#000000) used for backgrounds on OLED
- [ ] App works on 5-year-old devices without crashes
- [ ] Data lifecycle policy defined (when old data is archived/deleted)
- [ ] Core entry flow completes in < 60 seconds
- [ ] No engagement-maximizing dark patterns (streaks that shame, endless feeds)
- [ ] Co-benefit suggestions marked where applicable
```

### Step 5: Renumber Sections 6-10 → 7-11

**Find and replace**:
- `## 6. Meta Information Standards` → `## 7. Meta Information Standards`
- `## 7. Cross-referencing System` → `## 8. Cross-referencing System`
- `## 8. Skill Modifications` → `## 9. Skill Modifications`
- `## 9. Writing Guidelines` → `## 10. Writing Guidelines`
- `## 10. Validation Rules` → `## 11. Validation Rules`

**Also update any cross-references** within the document that mention "Section 6", "Section 7", etc.

### Step 6: Update Persona Template (Section 3)

**Location**: In the Persona Template (around line 390-530)

**Add these fields to YAML frontmatter**:
```yaml
environmental_constraints:
  - non_user: [Shoulder Surfer | Auditory Witness | Intimate Intruder]
    context: "[Where/when present]"
    threat: "[What they might access]"
    requirement: "[Design requirement]"
pcd_constraints:
  device_range: "[Oldest supported device]"
  energy_sensitivity: low | medium | high
  data_sensitivity: low | medium | high
  suffizienz_alignment: quick_exit | moderate | extended_sessions
```

**Add new section to template body** (after Anti-Persona Traits, before Real Quotes):
```markdown
## Environmental Constraints

### Non-User: [Name]
- **Context**: [Where/when this non-user is present]
- **Threat**: [What they might see/hear/access]
- **Impact**: [How this affects user behavior]
- **Requirement**: [Design requirement to address this]

## Device & Ecological Constraints

**Device Range**: [Oldest to newest devices to support]
**Energy Sensitivity**: [Low/Medium/High - battery concerns]
**Data Sensitivity**: [Low/Medium/High - storage/cleanup concerns]
**Suffizienz Alignment**: [Does this persona want quick in/out?]
```

### Step 7: Update Scenario Template (Section 4)

**Location**: In the Scenario Template (around line 656-756)

**Add to Success Criteria section**:
```markdown
## Success Criteria

The scenario is successful when:
- [ ] [Functional success criterion]
- [ ] [Emotional success criterion]
- [ ] [Time-based criterion]

**Environmental Check** (if applicable):
- [ ] Privacy glitch handled appropriately
- [ ] Non-user presence documented
- [ ] Recovery from interruption defined

**PCD Check**:
- [ ] Completes in minimum necessary time
- [ ] No artificial engagement extension
- [ ] Data generated is proportional to value provided
```

### Step 8: Update User Flow Template (Section 5)

**Location**: In the User Flow Template (around line 1029-1155)

**Add Environment column to Happy Path table**:
```markdown
## Happy Path (Main Flow)

| # | Environment (if applicable) | User Action | System Response | UI State | Related Epic |
|---|-----------------------------|-------------|-----------------|----------|--------------|
| 1 | [Non-user presence] | [Action] | [Response] | [Screen] | [Link] |
```

**Add new section before Implementation Status**:
```markdown
### Environmental Considerations

**Non-User Risks**:
- [ ] Shoulder Surfer: [Mitigation if applicable]
- [ ] Auditory Witness: [Mitigation if applicable]
- [ ] Intimate Intruder: [Mitigation if applicable]

**PCD Considerations**:
- Energy cost per interaction: [Low/Medium/High]
- Data generated: [Size estimate]
- Suffizienz compliance: [Yes/No - exits cleanly after goal]
```

### Step 9: Update Validation Rules (now Section 11)

**Location**: Section 11 (formerly Section 10), around line 1697

**Add new subsection**:
```markdown
### Environmental Constraint Validation

Check that non-user threats are addressed:

- [ ] **All personas identify relevant non-users**: At least one environmental constraint per persona
- [ ] **Each constraint has design requirement**: Not just threat identification, but solution
- [ ] **Scenarios include privacy glitches**: At least one interruption/friction point per sensitive scenario
- [ ] **Flows include Environment column**: For privacy-sensitive flows
- [ ] **Biometric re-auth documented**: For Intimate Intruder scenarios
- [ ] **Discreet mode exists**: For Shoulder Surfer scenarios
- [ ] **Audio privacy handled**: For Auditory Witness scenarios (headphone detection, mute on flip)

### Planet Centered Design Validation

Check PCD principles are respected:

- [ ] **Dark mode is default**: Not light theme with dark option
- [ ] **True black backgrounds**: #000000 for OLED, not #121212
- [ ] **Old device support**: App tested on 5-year-old devices
- [ ] **Data lifecycle defined**: When/how old data is archived or deleted
- [ ] **Entry time < 60 seconds**: Core interaction is fast
- [ ] **No engagement dark patterns**: No shame-based streaks, no "endless feed" suggestions
- [ ] **Exit flow clean**: App suggests closing after goal achieved
- [ ] **Co-benefits marked**: Planet-friendly habits identified where applicable
```

### Step 10: Update Persona/Scenario/Flow Writing Checklists

**Persona Checklist** (around line 532-548):
Add:
```markdown
- [ ] **Environmental constraints identified**: At least one non-user threat documented with mitigation
- [ ] **PCD constraints documented**: Device range, energy/data sensitivity, suffizienz alignment
```

**Scenario Checklist** (around line 758-772):
Add:
```markdown
- [ ] **Privacy glitch included** (if sensitive): Shows non-user interruption and recovery
- [ ] **PCD check completed**: Time, energy, data proportionality verified
```

**Flow Checklist** (around line 1157-1173):
Add:
```markdown
- [ ] **Environment column included** (if sensitive): Non-user presence and system adaptations
- [ ] **PCD considerations documented**: Energy cost, data generated, suffizienz compliance
```

---

## Quality Criteria

- [ ] All new sections are clearly written in English
- [ ] Concrete examples provided (not just abstract principles)
- [ ] Mood tracker app context used in all examples
- [ ] Consistent with existing README tone and structure
- [ ] Section numbering is correct after renumbering (6→7, 7→8, etc.)
- [ ] All cross-references updated (e.g., "See Section 6" → "See Section 7")
- [ ] Templates are updated with new fields
- [ ] Validation rules include new checks
- [ ] Writing checklists include new items

---

## Risks & Mitigations

### Risk 1: Section Renumbering Breaks References
**Mitigation**: After renumbering, grep for "Section [6-10]" and update all occurrences.

### Risk 2: New Content Too Long
**Mitigation**: Focus on actionable content with examples. Avoid repetition from requirements addition document.

### Risk 3: Inconsistent Voice/Tone
**Mitigation**: Match existing README style (professional, clear, empathetic, specific examples).

### Risk 4: Missing Integration Points
**Mitigation**: Follow structured checklist - templates, checklists, validation rules all updated.

---

## Execution Summary

**Agent needed**: 1 (Implementation Engineer)

**Execution order**:
1. Add Section 3.8 (Environmental Constraints)
2. Add Section 4.8 (Non-User in Scenarios)
3. Add Section 5.9 (Environment Swimlane)
4. Insert NEW Section 6 (PCD Layer)
5. Renumber Sections 6-10 → 7-11
6. Update Persona Template
7. Update Scenario Template
8. Update User Flow Template
9. Update Validation Rules
10. Update Writing Checklists

**Estimated size**: ~500-600 lines added to README.md (from ~1860 to ~2400 lines)

---

## Success Definition

Task is complete when:

1. README.md contains all new sections (3.8, 4.8, 5.9, NEW 6)
2. Section numbering is correct (old 6→7, 7→8, 8→9, 9→10, 10→11)
3. Templates include environmental constraints and PCD fields
4. Validation rules include non-user and PCD checks
5. Writing checklists include new items
6. All examples are mood-tracker specific
7. Document passes existing quality criteria

---

**Agent ID**: opus-plan-003
**Status**: Plan READY for execution
**Date**: 2026-01-17
