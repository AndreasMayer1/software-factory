---
id: REQ-PROC-010
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: implemented
effort: XL
stakeholder: developer
created: 2026-01-17
updated: 2026-02-21
after: [REQ-PROC-009]
blocks: [REQ-PROC-012, REQ-PROC-013, REQ-PROC-014, REQ-PROC-015, REQ-PROC-016, REQ-PROC-017, REQ-PROC-018, REQ-PROC-019, REQ-PROC-020, REQ-PROC-021, REQ-PROC-022, REQ-PROC-023, REQ-PROC-024, REQ-PROC-025, REQ-PROC-026, REQ-PROC-027, REQ-PROC-028]
  - REQ-PROC-039
trackable_items:
  sections:
    - id: SEC-01
      name: "Overview"
      heading: "## 1. Overview"
    - id: SEC-02
      name: "Folder Structure"
      heading: "## 2. Folder Structure"
    - id: SEC-03
      name: "Persona Definition"
      heading: "## 3. Persona Definition"
    - id: SEC-04
      name: "Scenario Definition"
      heading: "## 4. Scenario Definition"
    - id: SEC-05
      name: "User Flow Definition"
      heading: "## 5. User Flow Definition"
    - id: SEC-06
      name: "Meta Information Standards"
      heading: "## 6. Meta Information Standards"
    - id: SEC-07
      name: "Cross-referencing System"
      heading: "## 7. Cross-referencing System"
    - id: SEC-08
      name: "Skill Modifications"
      heading: "## 8. Skill Modifications"
    - id: SEC-09
      name: "Writing Guidelines"
      heading: "## 9. Writing Guidelines"
    - id: SEC-10
      name: "Validation Rules"
      heading: "## 10. Validation Rules"
    - id: SEC-11
      name: "Review Status System"
      heading: "## 11. Review Status System"
    - id: SEC-12
      name: "Cross-Reference Notation"
      heading: "## 12. Cross-Reference Notation"
    - id: SEC-13
      name: "Deviation Documentation"
      heading: "## 13. Deviation Documentation"
    - id: SEC-14
      name: "Technology Neutrality Principle"
      heading: "## 14. Technology Neutrality Principle"
---

# User Needs Structure Enhancement

## 1. User Story

As a developer, I want a structured way to capture user personas, scenarios, and user flows above the epic level, so that all requirements are clearly tied to actual user needs and goals, enabling better traceability and ensuring we build features that serve real user needs.

## 1. Overview

### The Problem

Currently, the `requirements_tasks/` folder contains requirements starting from epic level down to task level. While this provides good implementation tracking, it lacks the critical top layer: **why** are we building these features? What user needs drive them?

Epics focus on one part of the app, but they don't capture:
- **Who** the users are (personas with needs and constraints)
- **What goals** they're trying to achieve (goal-oriented scenarios)
- **How** the app helps them achieve these goals (user flows)

A single user flow can touch multiple epics, making it difficult to see the big picture of how features work together to serve user needs.

### The Solution

Add a new folder structure `requirements_user_needs/` that sits **above** the existing requirements structure, providing 3 new levels:

```
requirements_user_needs/         # NEW: Top-level user needs
├── personas/
│   ├── [persona_name]/
│   │   ├── persona.md          # Who they are, needs, constraints
│   │   └── scenarios/
│   │       ├── [scenario_name]/
│   │       │   ├── scenario.md  # What goal they're trying to achieve
│   │       │   └── user_flows/
│   │       │       └── [flow_name]/
│   │       │           └── flow.md  # How the app solves it
└── README.md                    # Rationale, structure, definitions

requirements_tasks/              # EXISTING: Implementation details
├── functional/
│   └── [app_role]/
│       └── [epic]/
│           ├── requirements.md  # References user flows & scenarios
│           └── features/
│               └── [feature]/
│                   └── requirements.md  # References user flows & scenarios
```

This creates a complete hierarchy:
```
Personas (who + needs)
  └─> Goal-oriented Scenarios (what they want to achieve)
      └─> User Flows (how the app solves it)
          └─> Epics (implementation slice)
              └─> Features (detailed implementation)
                  └─> Tasks (work items)
```

### Benefits

1. **Traceability**: Every epic/feature can reference which user flows it supports
2. **Gap Analysis**: Identify user needs not yet covered by any epic
3. **Consistency**: Ensure requirements don't contradict higher-level user needs
4. **Context**: When writing new epics, check scenarios/flows to understand the "why"
5. **Validation**: Prevent building features that don't serve actual user needs

## 2. Folder Structure

### requirements_user_needs/ Structure

```
requirements_user_needs/
├── README.md                              # Rationale, structure, definitions, writing guidelines
├── personas/
│   ├── dr_thomas/                         # Therapist persona
│   │   ├── persona.md                     # Profile, needs, pain points, constraints
│   │   └── scenarios/
│   │       ├── pre_session_patient_review/
│   │       │   ├── scenario.md            # Scenario description
│   │       │   └── user_flows/
│   │       │       ├── quick_triage_view/
│   │       │       │   └── flow.md        # Flow description
│   │       │       └── detailed_trend_analysis/
│   │       │           └── flow.md
│   │       └── treatment_plan_creation/
│   │           ├── scenario.md
│   │           └── user_flows/
│   │               └── template_based_plan/
│   │                   └── flow.md
│   ├── max_client/                        # Client persona
│   │   ├── persona.md
│   │   └── scenarios/
│   │       └── daily_mood_tracking/
│   │           ├── scenario.md
│   │           └── user_flows/
│   │               ├── quick_check_in/
│   │               │   └── flow.md
│   │               └── detailed_reflection/
│   │                   └── flow.md
│   └── sarah_self_user/                   # Self-user persona
│       ├── persona.md
│       └── scenarios/
│           └── self_reflection/
│               ├── scenario.md
│               └── user_flows/
│                   └── pattern_discovery/
│                       └── flow.md
```

### Integration with Existing Structure

Epic and feature `requirements.md` files will add a new section (example, details TBD, must be incorporated in existing yaml format):

```markdown
## User Needs Context

**Personas**: [Link to persona files]
**Scenarios**: [Link to scenario files]
**User Flows**: [Link to user flow files]

This epic/feature supports the following user flows:
- [Flow Name](../../requirements_user_needs/personas/.../flow.md)
```

## 3. Persona Definition

Everything in this section is just a starting point. Part of the task is to explore how our personas shall look like. There is additional information in the appendix. 
Another open point: We need a standardized way to mark parts of the information in the file as "grounded by data". We write proto personas in the frist place but eventually gather more data about the actual users and have the abiltiy to adapt to it and change the file. Therefore all references to the file must also include the commit hash, because the file changes over time.

### What is a Persona?

A persona represents a distinct user archetype with specific:
- **Background**: Who they are, context, role
- **Core Needs**: What they fundamentally require (that can be met through the app)
- **Pain Points & Frustrations**: What makes their life difficult
- **Constraints**: Technical, cognitive, emotional, or situational limitations
- **Mental Health Context** (where applicable): Special considerations for this user group

### Persona File Format (persona.md)

```markdown
---
persona_id: PERSONA-[NUMBER]
name: "[Display Name]"
role: therapist | client | self_user | system
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Persona: [Name]

## Background

[Who they are, their context, their role]

## Core Needs

- **[Need Category]**: [Description]
- **[Need Category]**: [Description]

## Pain Points & Frustrations

- [Pain point with solution reference if available]

## Constraints

- [Constraint description]

## Mental Health Context (if applicable)

[Special considerations for this user group]

## Implications for the App

[Key design/UX requirements this persona drives]
```

### Example Personas

1. **Dr. Thomas** (Therapist): Efficiency-focused, needs quick overview, zero-knowledge security
2. **Max** (Client): Depression/ADHD, needs low friction, forgiving design, stealth mode
3. **Sarah** (Self-User): Autonomy-focused, wants customization and insights
4. **System/Maintenance**: Technical edge cases (device migration, crashes, etc.)

## 4. Scenario Definition

Like for personas, the goal of this task is also to figure out the best way to write scenarios in our app. This chapter gives a first impression, not a final suggestion, refer the appendix for more information and examples.
Another open point: We need a standardized way to mark parts of the information in the file as "grounded by data". We write based on assumptions in the frist place but eventually gather more data about the actual users and have the abiltiy to adapt to it and change the file. Therefore all references to the file must also include the commit hash, because the file changes over time.

### What is a Scenario?

A scenario describes a **goal-oriented situation** where a persona is trying to achieve something. It captures:
- **The goal**: What the user wants to accomplish
- **Context**: When/where this happens, what triggers it
- **Success criteria**: What does success look like?
- **User flows**: Different ways the app can help achieve this goal

### Scenario File Format (scenario.md)

```markdown
---
scenario_id: SCEN-[PERSONA_ID]-[NUMBER]
persona_id: PERSONA-[NUMBER]
name: "[Scenario Name]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Scenario: [Name]

## Persona

[Link to persona.md]

## Goal

[What the user wants to achieve]

## Context

**Triggers**: [What prompts this scenario]
**Frequency**: [How often this occurs]
**Environment**: [Where/when this happens]

## Success Criteria

- [ ] [What makes this scenario successful]

## User Flows

This scenario can be accomplished through the following user flows:
- [Flow 1 Name](user_flows/flow1/flow.md)
- [Flow 2 Name](user_flows/flow2/flow.md)

## Related Scenarios

[Links to related scenarios]
```

## 5. User Flow Definition

Like for personas and scenarios this is just a first suggestion, but the task has the goal to find out what fits best. There's more in the appendix about user flows.
Another open point: We need a standardized way to mark parts of the information in the file as "grounded by data". We write based on assumptions in the frist place but eventually gather more data about the actual users and have the abiltiy to adapt to it and change the file. Therefore all references to the file must also include the commit hash, because the file changes over time.

### What is a User Flow?

A user flow describes **how the app helps** a user accomplish a scenario goal. It:
- Is **solution-oriented** (describes the app's behavior)
- Can touch **multiple epics** (cross-cutting)
- Includes **steps, screens, and interactions**
- Links to **epics/features** that implement it

### User Flow File Format (flow.md)

```markdown
---
flow_id: FLOW-[SCEN_ID]-[NUMBER]
scenario_id: SCEN-[PERSONA_ID]-[NUMBER]
name: "[Flow Name]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
implementation_status: not_started | partial | complete
---

# User Flow: [Name]

## Scenario

[Link to scenario.md]

## Overview

[Brief description of this flow]

## Flow Steps

1. **[Step Name]**
   - User action: [What the user does]
   - System response: [What the app does]
   - Related epic/feature: [Link to requirements.md]

2. **[Step Name]**
   - ...

## Screens/Components Involved

- [Screen/Component Name]: [Link to epic/feature]

## Implementing Epics/Features

This user flow is implemented across:
- [Epic Name](../../../requirements_tasks/functional/.../requirements.md)
- [Feature Name](../../../requirements_tasks/functional/.../requirements.md)

## Edge Cases

- [Edge case description and how it's handled]

## Implementation Status

- [ ] Step 1 implemented (Epic: [Link])
- [ ] Step 2 implemented (Feature: [Link])
- [x] Step 3 implemented (Feature: [Link])
```

## 6. Meta Information Standards

### Persona Meta Information

```yaml
persona_id: PERSONA-[NUMBER]  # PERSONA-001, PERSONA-002, ...
name: "[Display Name]"
role: therapist | client | self_user | system
created: YYYY-MM-DD
updated: YYYY-MM-DD
```

### Scenario Meta Information

```yaml
scenario_id: SCEN-[PERSONA_ID]-[NUMBER]  # SCEN-001-01, SCEN-001-02, ...
persona_id: PERSONA-[NUMBER]
name: "[Scenario Name]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
```

### User Flow Meta Information

```yaml
flow_id: FLOW-[SCEN_ID]-[NUMBER]  # FLOW-001-01-01, FLOW-001-01-02, ...
scenario_id: SCEN-[PERSONA_ID]-[NUMBER]
name: "[Flow Name]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
implementation_status: not_started | partial | complete
```

## 7. Cross-referencing System

### From User Flows to Epics/Features

User flow files link to implementing epics/features:

```markdown
## Implementing Epics/Features

This user flow is implemented across:
- [Epic: Client Data Input](../../../requirements_tasks/functional/client/epic_data_input/requirements.md)
- [Feature: Plan Evaluation View](../../../requirements_tasks/functional/shared/epic_evaluation/plan_evaluation_view/requirements.md)
```

### From Epics/Features to User Flows

Epic/feature requirements.md files add a section:

```markdown
## User Needs Context

**Personas**:
- [Dr. Thomas (Therapist)](../../../requirements_user_needs/personas/dr_thomas/persona.md)

**Scenarios**:
- [Pre-session Patient Review](../../../requirements_user_needs/personas/dr_thomas/scenarios/pre_session_patient_review/scenario.md)

**User Flows**:
- [Quick Triage View](../../../requirements_user_needs/personas/dr_thomas/scenarios/pre_session_patient_review/user_flows/quick_triage_view/flow.md)

This epic implements steps from the above user flows.
```

### Validation

References must be valid:
- User flows must reference existing scenarios
- Scenarios must reference existing personas
- Epics/features should reference at least one user flow (warning if missing)
- User flows should reference at least one implementing epic/feature (gap if missing)

## 8. Skill Modifications

### New Skills Needed

1. **create-persona** skill
   - Prompts for persona details (name, role, background, needs)
   - Generates `persona_id`
   - Creates `persona.md` file
   - Updates ID registry

2. **create-scenario** skill
   - Prompts for persona selection, goal, context
   - Generates `scenario_id`
   - Creates `scenario.md` file
   - Updates ID registry

3. **create-user-flow** skill
   - Prompts for scenario selection, flow steps
   - Generates `flow_id`
   - Creates `flow.md` file
   - Links to implementing epics/features
   - Updates ID registry

### Modified Skills

1. **setup-task** skill (when creating epics/features)
   - **Check higher levels**: Before creating epic/feature, prompt to link to user flows
   - **Gap filling**: If user flow information is missing, suggest checking personas/scenarios
   - **Validation**: Warn if epic/feature doesn't reference any user flow

2. **verify-quality** skill
   - **Contradiction check**: Ensure epic/feature doesn't contradict referenced user flows
   - **Completeness check**: Verify user flow references are valid
   - **Coverage check**: Identify user flows with no implementing epics/features

3. **explore-requirements** skill
   - **Context gathering**: When exploring requirements, read personas/scenarios/flows first
   - **Rationale extraction**: Extract "why" from user needs for requirement documentation

## 9. Writing Guidelines

### Persona Writing Guidelines

- **Focus on needs, not solutions**: Describe what they need, not how to solve it
- **Include constraints**: Technical, cognitive, emotional, situational
- **Real examples**: Use concrete pain points, not abstract statements
- **Implications section**: Translate needs into app design requirements

### Scenario Writing Guidelines

- **Goal-oriented**: Focus on what the user wants to achieve, not how
- **Context-rich**: Describe triggers, frequency, environment
- **Measurable success**: Clear success criteria
- **Multiple flows**: Acknowledge different ways to achieve the goal

### User Flow Writing Guidelines

- **Solution-oriented**: Describe how the app works, not user needs
- **Step-by-step**: Clear sequence of user actions and system responses
- **Cross-cutting**: Link to all epics/features involved
- **Implementation status**: Track which steps are implemented
- **Edge cases**: Document edge case handling

### Language and Tone

- **Language**: English (all files)
- **Tone**: Professional, clear, empathetic (especially for personas)
- **Perspective**:
  - Personas: Third person ("Dr. Thomas is...", "Max struggles with...")
  - Scenarios: User perspective ("The therapist wants to...")
  - Flows: Descriptive ("The app displays...", "The user taps...")

## 10. Validation Rules

### Structural Validation

- [ ] All personas have `persona.md` with valid YAML frontmatter
- [ ] All scenarios have `scenario.md` with valid YAML frontmatter and reference existing persona
- [ ] All user flows have `flow.md` with valid YAML frontmatter and reference existing scenario
- [ ] ID uniqueness: No duplicate IDs across all files

### Cross-reference Validation

- [ ] User flows reference at least one implementing epic/feature (warning if none)
- [ ] User flows' epic/feature references exist (error if broken)
- [ ] Scenarios reference at least one user flow (warning if none)
- [ ] Personas reference at least one scenario (warning if none)

### Content Validation

- [ ] Epics/features should reference user flows (warning if missing)
- [ ] Epic/feature content doesn't contradict referenced user flows (manual review)
- [ ] User flows don't duplicate content from epics (flows = high-level, epics = detailed)

### Hierarchy Validation

**Rule**: Lower levels must never contradict higher levels

- If a user flow says "quick check-in takes <30 seconds", epic requirements can't require 5-minute forms
- If a persona has "low friction" as a core need, features can't introduce unnecessary steps
- If a scenario requires "stealth mode", UI can't have large text saying "THERAPY"

**Process**: When creating/modifying lower levels, always check higher levels for constraints.

## 11. Migration from requirements_general_overview/

The existing `requirements_general_overview/` folder contains:
- High-level user stories (some valid, some outdated)
- Some implementation details (some incorporated, some not)

**Strategy**:
1. **Keep folder for now**: Manual extraction needed
2. **Mark as deprecated**: Not a source of truth
3. **Extract valid information**: User to manually review and migrate to new structure
4. **Remove once complete**: After all valid information is extracted

## 12. Initial Content

The user has provided initial persona content (see task notes). This should be used as the initial content for the first persona files when creating the structure.

## 13. Implementation Phases

### Phase 1: Foundation & Structure (Complete)
- Create folder structure
- Create README.md with rationale, definitions, writing guidelines
- Define meta information standards
- Create validation rules

### Phase 2: Format Exploration & Definition (Complete)
- Explore optimal format for personas
- Explore optimal format for scenarios
- Explore optimal format for user flows
- Create templates with examples

### Phase 3: Initial Content Creation (Complete)
- Create 4 initial personas from user-provided content
- Create example scenarios for at least one persona
- Create example user flows for at least one scenario

### Phase 4: Modification Workflow (Implemented)
**Status**: Completed 2026-01-25

**Created**:
- `modify-user-needs` skill for managing modifications with version tracking and impact analysis
- Task placement strategy: Modification tasks go under `user_needs_content/[persona_name]/tasks/` or `user_needs_content/tasks/` for cross-persona work
- Version incrementing strategy: Semantic versioning (major.minor) based on change type
- Hybrid approach: Skill for significant changes, direct edits for trivial fixes

**Key Features**:
- Automatic review status reset to `in_review` for significant modifications
- Automatic version incrementing based on change type
- Impact analysis (upstream and downstream dependencies)
- User approval workflow before applying changes
- Post-modification validation

**Task Placement Strategy**:
```
requirements_tasks/process/AI_rules/requirements_management/user_needs_content/
├── [persona_name]/
│   └── tasks/
│       └── YYYY-MM-DD_[type]_[description]/  # Persona-specific modifications
└── tasks/
    └── YYYY-MM-DD_[type]_[description]/      # Cross-persona modifications
```

**Version Incrementing Guidelines**:
| Change Type | Version Change | Example |
|-------------|----------------|---------|
| Typo/grammar fixes | No change | 2.0 → 2.0 |
| Minor content additions | Patch (+0.1) | 2.0 → 2.1 |
| Section rewrites | Minor (+0.1) | 2.0 → 2.1 |
| Structural changes | Major (+1.0) | 2.0 → 3.0 |
| Evidence level changes | Minor (+0.1) | 2.0 → 2.1 |

**When to Use Skill vs. Direct Edit**:
| Modification Type | Approach | Why |
|-------------------|----------|-----|
| Typo fixes, small wording changes | Direct edit | Overhead not justified |
| Adding new sections or significant content | `modify-user-needs` skill | Ensures review status, impact analysis |
| Major rewrites or structural changes | `modify-user-needs` skill | Critical for traceability |
| Changing evidence level markers | `modify-user-needs` skill | Affects data quality tracking |
| Updating cross-references | `modify-user-needs` skill | Needs validation |

### Phase 5: Integration & Tooling (Pending)
- Define cross-referencing implementation details
- Document skill modifications needed
- Define validation rules and scripts
- Create new skills (create-persona, create-scenario, create-user-flow)
- Modify existing skills (setup-task, verify-quality, explore-requirements)
- Update CLAUDE.md with new workflow

### Phase 6: Migration Support (Future)
- Add validation script for user needs structure
- Add coverage report for user flow → epic mapping
- Create tooling to identify gaps

### Phase 7: Backfill Existing Requirements (Future)
- Add "User Needs Context" section to existing epics/features
- Link existing epics to user flows
- Identify epics that don't map to any user flow (candidates for deprecation)

## 14. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-009 | implemented | Need existing requirements structure as foundation |

## 15. References

- User-provided persona content (see task notes)
- Existing requirements structure: requirements_tasks/
- CLAUDE.md: Software Factory Constitution

## Appendix

### Personas

Die meisten Personas scheitern, weil sie **„Bullshit-Bingo mit Stockfotos“** sind. Eine Persona, die nur aus „Susanne, 34, trinkt gerne Kaffee und liest Bücher“ besteht, ist für die Produktentwicklung wertlos.

Wenn du nach **Perfektion** (oder besser: maximaler Wirksamkeit) strebst, musst du weg von *Demografie* und hin zu *Psychologie, Kontext und Verhalten*.

Hier sind die Elemente, die in eine moderne, „perfekte“ Persona gehören und die oft vergessen werden:

#### 1. Mentale Modelle & Erwartungshaltung
Statt zu fragen „Wie alt ist sie?“, fragst du: „Wie glaubt sie, dass das System funktioniert?“
*   **Mental Models:** Vergleicht die Persona dein Produkt mit Excel, mit TikTok oder mit einem physischen Aktenordner? Das diktiert das UX-Design.
*   **Vorwissen:** Ist sie ein „Domain Expert“ (versteht das Fachgebiet, aber nicht die Software) oder ein „Tool Expert“ (kennt Software, aber nicht das Fachgebiet)?
*   **Lernbereitschaft:** Will sie das Tool meistern (Power User) oder will sie so wenig Zeit wie möglich darin verbringen (Satisficer)?

#### 2. Jobs to be Done (JTBD)
Die klassische Persona beschreibt den Menschen. Die perfekte Persona beschreibt den **Fortschritt**, den dieser Mensch machen will.
*   **Die Kernaufgabe:** Nicht „Ich will eine Bohrmaschine kaufen“, sondern „Ich will ein Loch in der Wand“, oder noch tiefer: „Ich will mein Wohnzimmer gemütlich machen“.
*   **Funktionale vs. Emotionale Jobs:**
    *   *Funktional:* „Daten exportieren.“
    *   *Emotional:* „Vor meinem Chef kompetent wirken, indem der Report gut aussieht.“
    *   *Sozial:* „Im Team als derjenige gelten, der Probleme schnell löst.“

#### 3. Der emotionale & physische Kontext (Environment)
Software wird nicht im Vakuum bedient.
*   **Trigger:** Was genau passiert in der Sekunde, *bevor* sie dein Produkt öffnet? (Ist eine E-Mail eingegangen? Hat der Chef geschrien? Ist der Server abgestürzt?)
*   **Stresslevel & Fokus:** Bedient sie die App entspannt auf dem Sofa (hohe Fehlertoleranz) oder schwitzend am Flughafen, während das Boarding läuft (Null Fehlertoleranz)?
*   **Geräuschkulisse & Umgebung:** Großraumbüro? Baustelle? Dunkles Schlafzimmer?

#### 4. Das Tech-Ökosystem & Kompetenz
*   **Digital Fluency:** Wie sicher bewegt sie sich *wirklich* digital? (Nicht nur „hoch/niedrig“, sondern spezifisch: Kann sie Shortcuts? Versteht sie Cloud-Konzepte?)
*   **Anker-Tools:** Welche Software nutzt sie den ganzen Tag? (Wenn sie 8 Stunden in Outlook verbringt, erwartet sie, dass dein Tool wie Outlook funktioniert.)
*   **Device-Realität:** Nutzt sie ein 3000€ MacBook oder einen 5 Jahre alten Windows-Laptop mit 125% Skalierung und schlechtem Kontrast?

#### 5. „Friction“ und Barrieren (Die echten Schmerzen)
„Möchte Zeit sparen“ ist kein echter Pain Point, das will jeder.
*   **Angst:** Wovor hat sie Angst, wenn sie dein Produkt nutzt? (Datenverlust? Dumm dazustehen? Geld zu verschwenden?)
*   **Inertia (Trägheit):** Warum wechselt sie *nicht*? Was hält sie bei der alten, schlechten Lösung? (Gewohnheit, Migrationsaufwand, politische Hürden im Unternehmen).

#### 6. Die Anti-Persona-Traits
Um eine Persona scharf zu machen, musst du definieren, was sie **nicht** ist.
*   *Beispiel:* „Diese Persona ist NICHT preissensibel.“ (Das erspart dem Design-Team Diskussionen darüber, ob man den Preis prominenter anzeigen muss).
*   *Beispiel:* „Diese Persona interessiert sich NICHT für Gamification.“ (Erspart unnötige Features).

#### 7. Zitate (Aber echte!)
Keine erfundenen Marketing-Sätze wie „Ich liebe Cloud-Lösungen“.
Nutze **O-Töne aus User-Interviews**.
*   *Gut:* „Ehrlich gesagt klicke ich einfach wild herum, bis das Fenster weggeht.“
*   *Gut:* „Ich hasse es, wenn ich mich jedes Mal neu einloggen muss, wenn ich nur kurz Kaffee hole.“
Das schafft echte Empathie im Team.

#### Zusammenfassung: Die Struktur einer „perfekten“ Persona

Wenn du das Layout baust, lass das Foto klein und den Namen irrelevant. Der Fokus sollte so aussehen:

1.  **Der Archetyp:** (z.B. „Der gehetzte Troubleshooter“ statt „IT-Manager Klaus“)
2.  **Der Trigger:** „Wenn der Server Alarm schlägt...“
3.  **Das Ziel (JTBD):** „...will ich in unter 30 Sekunden die Ursache sehen, um Panik zu vermeiden.“
4.  **Die Barriere:** „Ich habe Angst, etwas zu löschen, was wichtig ist.“
5.  **Das Mental Model:** „Ich erwarte eine Kommandozeile, keine bunten Buttons.“
6.  **Der Kontext:** „Lautes Büro, zwei Monitore, ständige Unterbrechungen.“

**Pro-Tipp:**
Gute Personas sind **datenbasiert**, nicht geraten. Wenn du diese Felder nicht mit Daten aus Interviews oder Beobachtungen füllen kannst, schreib lieber „Unbekannt“ oder mach eine Annahme kenntlich, als dir etwas auszudenken. Perfektion bedeutet hier Ehrlichkeit gegenüber der Datenlage.

Gerade im Bereich **Mental Health & Therapie** ist der Kontext alles. „18+ und westeuropäisch“ ist demografisch riesig, aber **psychologisch** kannst du hier sehr scharf trennen.

Hier ist der entscheidende Punkt für eine perfekte Persona in diesem Bereich: **Der mentale Zustand diktiert die UI/UX-Anforderungen.**

Ein Nutzer, der *präventiv* Habit-Tracking macht, hat völlig andere Bedürfnisse (Gamification, Statistik) als jemand, der gerade eine depressive Episode hat (Gamification erzeugt Druck, Statistiken erzeugen Scham).

Hier sind drei Vorschläge für „High-End“-Personas für deinen Kontext, die auf Verhalten und psychologischen Hürden basieren, statt auf Alter/Beruf:

#### Persona 1: Der „High-Functioning“ Verdränger
*Dieser Nutzer ist im Alltag erfolgreich, steht aber unter enormem Druck. Er nutzt die App nicht zur Therapie, sondern zur „Druckbetankung“ für Leistungserhalt.*

*   **Mentales Modell:** „Die App ist mein externer RAM.“ (Er will Dinge aus dem Kopf bekommen, um weiter zu funktionieren).
*   **Der Trigger (Kontext):** 23:30 Uhr, liegt im Bett, Gedankenkreisen, kann nicht einschlafen wegen der To-Dos und Sorgen von morgen.
*   **Job to be Done (JTBD):** „Ich will meine kreisenden Gedanken irgendwo ‚abladen‘ (Brain Dump), damit ich schlafen kann und morgen wieder leistungsfähig bin.“
*   **Emotionale Barriere (Scham/Angst):**
    *   Hat Angst, dass seine Gedanken „dumm“ oder „schwach“ klingen.
    *   **Privacy-Paranoia (Westeuropäisch):** „Was, wenn das Datenleck passiert und mein Arbeitgeber das liest?“ -> *Konsequenz: Er braucht extrem sichtbare Verschlüsselungshinweise.*
*   **Design-Implikation (Anti-Persona):** Will **keine** Achtsamkeitsübungen oder langsames Atmen. Er will schnelles Eingeben. Keine „Wie fühlst du dich?“-Frage mit 5 Klicks, sondern ein freies Textfeld.
*   **Das „Vulnerability Hangover“:** Wenn er am nächsten Morgen sieht, was er nachts geschrieben hat, schämt er sich vielleicht. Die App darf ihm das nicht ungefragt unter die Nase reiben („Dein Rückblick von gestern!“).

#### Persona 2: Der therapiebegleitende „Musterschüler“
*Dieser Nutzer ist bereits in Behandlung. Die App ist ein Werkzeug, um die Therapie effizienter zu machen.*

*   **Mentales Modell:** „Die App ist mein medizinischer Assistent / Aktenschrank.“
*   **Der Trigger:** Kurz vor der Therapiesitzung (Panik: „Worüber wollte ich reden?“) ODER direkt nach einer Situation, die der Therapeut als „Hausaufgabe“ aufgegeben hat.
*   **Job to be Done (JTBD):** „Ich will Muster in meinem Verhalten erkennen und dokumentieren, damit ich meine teure Therapiezeit nicht mit ‚Ich weiß nicht mehr, wie die Woche war‘ verschwende.“
*   **Inertia (Trägheit):** Das „Leere-Blatt-Syndrom“. Wenn die App fragt: „Schreib was auf“, ist sie überfordert. Sie braucht *Prompts* (Gezielte Fragen: „Was hat dich heute getriggert?“).
*   **Beziehung zu Gamification (Wichtig!):** Streaks (z.B. „Du hast 10 Tage in Folge geloggt!“) sind hier gefährlich. Wenn sie einen Tag wegen Depression im Bett lag und den „Streak“ verliert, fühlt sie sich als Versagerin. Eine perfekte Persona hier definiert: **„Erfolg ist Ehrlichkeit, nicht Kontinuität.“**
*   **Tech-Kontext:** Nutzt die Export-Funktion. Will dem Therapeuten vielleicht ein PDF zeigen.

#### Persona 3: Der skeptische Selbst-Optimierer (Quantified Self)
*Nutzt die App eher für Habit-Tracking und Stimmungsbarometer. Weniger Leidensdruck, mehr Neugier.*

*   **Mentales Modell:** „Die App ist ein Dashboard / Excel-Sheet für mein Leben.“
*   **Der Trigger:** Morgens beim Kaffee oder abends beim Tagesabschluss. Routine-getrieben.
*   **Job to be Done (JTBD):** „Ich will Korrelationen sehen. Schlafe ich schlechter, wenn ich Alkohol trinke? Bin ich glücklicher, wenn ich Sport mache?“
*   **Erwartungshaltung:** Erwartet Datenvisualisierung. Schöne Graphen. Westeuropäischer Kulturraum: Ist allergisch gegen „Esoterik“ oder „Woo-Woo“. Wenn die App zu spirituell wird („Spüre deine Aura“), ist er weg. Er will Wissenschaft/Psychologie.
*   **Barriere:** Dateneingabe-Aufwand. Wenn es länger als 30 Sekunden dauert, das Habit zu tracken, hört er auf.

#### Was diese Personas für dein Produkt bedeuten (Perfektions-Checkliste)

Um es dir „schwer“ (also qualitativ hochwertig) zu machen, musst du für diese Personas folgende Fragen beantworten:

1.  **Umgang mit Lücken:** Wie reagiert die App, wenn Persona 2 (Therapie) mal 3 Wochen fehlt?
    *   *Schlecht:* „Du hast deinen Streak verloren!“ (Erzeugt Schuldgefühle).
    *   *Perfekt:* „Willkommen zurück. Wie war die Pause für dich?“ (Empathisch, wertfrei).

2.  **Tonalität (Voice & Tone):**
    *   Persona 1 braucht Effizienz („Eintrag gespeichert“).
    *   Persona 2 braucht Wärme („Gut, dass du dir Zeit nimmst“).
    *   Wie balancierst du das? (Vielleicht durch Onboarding-Frage: „Willst du einen Coach oder einen Zuhörer?“)

3.  **Datenschutz als UX-Feature:**
    *   Für den westeuropäischen Markt ist „Server in Deutschland/EU“ kein Kleingedrucktes, sondern ein Core-Feature für Persona 1 & 2. Es gehört auf den Startscreen.

4.  **Der „Abbruch-Moment“:**
    *   Analysiere genau den Moment, in dem die App *zu viel* verlangt. Eine perfekte Persona für Mental Health hat ein sehr begrenztes Budget an „kognitiver Energie“. Wenn die App fragt: „Bewerte deinen Tag auf 5 Dimensionen und schreibe 200 Wörter“, ist das für jemanden mit Depression eine unüberwindbare Mauer.

**Zusammenfassend:** Die perfekte Persona in diesem Bereich definiert sich über ihren **Energiehaushalt** und ihre **Scham-Grenze**, nicht über ihr Alter.

### Goal based Scenarios

Das ist der logische nächste Schritt. Wenn Personas das „Wer“ und „Warum“ sind, sind Szenarien das „Wie“ und „Wann“.

Viele verwechseln Szenarien mit *Use Cases*.
*   **Use Case:** „Nutzer klickt auf ‚Neuer Eintrag‘, tippt Text, klickt ‚Speichern‘.“ (Technisch, emotionslos).
*   **Szenario:** Eine Geschichte mit Kontext, Konflikt und Auflösung.

Um **State of the Art** Szenarien zu schreiben, musst du den **„Happy Path“ verlassen**. Das Leben ist kein gerader Weg, besonders nicht bei mentaler Gesundheit. Ein perfektes Szenario beinhaltet Reibung, Zweifel und äußere Umstände.

Hier sind die Zutaten für High-End Goal-Oriented Scenarios und wie du sie strukturierst:

#### 1. Die Anatomie eines perfekten Szenarios

Ein gutes Szenario liest sich wie eine Kurzgeschichte. Es braucht drei Akte:

##### Akt 1: Der Kontext & Der „Inciting Incident“ (Der Auslöser)
Beginne nicht mit „Er öffnet die App“. Beginne in der echten Welt.
*   **Physischer Zustand:** Wo ist die Person? (Im Bett, im Bus, auf der Toilette bei der Arbeit?)
*   **Kognitive Last:** Wie viel „Hirnschmalz“ ist noch übrig? (Ist sie betrunken? Müde? Panisch?)
*   **Der Auslöser:** Warum *jetzt*? (Ein Gedanke lässt sie nicht los? Der Therapeut hat gefragt?)

##### Akt 2: Die Interaktion & Der Widerstand
Hier passiert die Nutzung, aber gepaart mit Gedanken (Internal Monologue).
*   **Die Hürde:** Was macht es schwer? (Tippfehler wegen zitternden Händen? Angst, dass der Partner auf das Display schaut?)
*   **Die System-Reaktion:** Wie hilft die App spezifisch in diesem Zustand? (Bietet sie Voice-Input an, weil Tippen zu anstrengend ist?)

##### Akt 3: Das Resultat & Das Gefühl (Post-Condition)
Nicht nur „Daten gespeichert“. Sondern:
*   **Emotionale Veränderung:** Fühlt sie sich leichter? Oder schämt sie sich jetzt?
*   **Nächster Schritt:** Schließt sie die App sofort oder scrollt sie noch?

#### 2. State-of-the-Art Elemente (Das „Extra“)

Füge diese Aspekte hinzu, um das Szenario realistisch und wertvoll für Designer/Entwickler zu machen:

*   **Der „Privacy-Glitch“:** Baue einen Moment ein, wo die Person das Handy schnell wegdreht, weil jemand den Raum betritt. Wie reagiert die App? (Blur-Screen? FaceID Lock?)
*   **Die Unvollkommenheit:** Lass die Persona abbrechen. Ein perfektes Szenario kann auch zeigen, wie jemand einen Eintrag *nicht* beendet, und wie die App damit beim nächsten Mal umgeht (Draft saving).
*   **Micro-Goals:** Das Ziel ist oft nicht „Tagebuch schreiben“, sondern „Druck ablassen“. Wenn das Tippen zu lange dauert, scheitert das Ziel, auch wenn die Funktion da ist.

#### 3. Konkrete Beispiele (Basierend auf deinen Personas)

Hier sind zwei Beispiele, wie sich „Standard“ von „Perfekt“ unterscheidet.

##### Beispiel A: Persona „Der High-Functioning Verdränger“
**Ziel:** Gedanken loswerden, um einschlafen zu können (Brain Dump).

> **Standard (Langweilig):**
> Markus liegt im Bett. Er öffnet die App. Er wählt „Neuer Eintrag“. Er schreibt seine Sorgen auf. Er speichert und schläft ein.

> **State of the Art (Perfekt):**
> **Kontext:** Es ist 01:15 Uhr. Markus liegt im Dunkeln neben seiner Frau. Er starrt an die Decke, sein Herz rasen leicht, weil er an das Meeting morgen denkt. Er will das Handy nicht zu hell machen, um sie nicht zu wecken.
>
> **Aktion & Reibung:** Er tastet nach dem Handy, öffnet die App. Dank des **OLED-Black-Mode** wird der Raum nicht erleuchtet (wichtig!). Seine Augen sind müde. Er will nicht tippen, das Klick-Geräusch der Tastatur wäre zu laut. Er sieht den Button für „Sprachnotiz zu Text“. Er flüstert leise drei Sätze in das Mikrofon.
>
> **Internal Monologue:** *„Hoffentlich speichert das das nicht in der Cloud, wo die IT-Abteilung es sehen kann.“* Er sieht ein kleines Schloss-Icon mit dem Text „Nur lokal verschlüsselt“. Er atmet aus.
>
> **Resultat:** Er drückt nicht mal auf Speichern, er lässt das Handy einfach sinken. Die App speichert automatisch (Auto-Save). Markus spürt, wie der Gedanke „im Kasten“ ist und nicht mehr in seinem Kopf kreisen muss. Er dreht sich um.

*Warum ist das besser?* Es diktiert dem Design-Team: Dark Mode ist Pflicht (nicht optional), Audio-Input muss flüster-sensitiv sein, „Speichern“ muss passiv passieren, Sicherheits-Icon muss sichtbar sein.

##### Beispiel B: Persona „Der therapiebegleitende Musterschüler“
**Ziel:** Ein Muster für die nächste Sitzung erkennen.

> **State of the Art (Perfekt):**
> **Kontext:** Sarah sitzt im Wartezimmer ihrer Therapeutin. Sie ist nervös. In 5 Minuten ist sie dran. Sie hat die Woche über kaum geloggt und fühlt sich schuldig („Ich habe meine Hausaufgaben nicht gemacht“).
>
> **Aktion & Reibung:** Sie öffnet die App, hofft auf eine Rettung. Sie erwartet eine leere Liste und ein schlechtes Gewissen. Stattdessen zeigt die App: „Keine Sorge wegen der Lücken. Aber schau mal, an den 2 Tagen, wo du geloggt hast, war dein Schlaf sehr kurz.“
>
> **Der Twist:** Sarah realisiert durch die Visualisierung, dass ihre Angstzustände immer nach Nächten mit unter 5h Schlaf auftraten.
>
> **Resultat:** Statt mit „Ich habe nichts zu erzählen“ in die Stunde zu gehen, geht sie rein mit: „Ich glaube, wir müssen über meinen Schlaf reden.“ Die App hat ihr das Gefühl von Kompetenz gegeben, trotz fehlender Daten.

*Warum ist das besser?* Es zeigt, wie die App mit *fehlenden* Daten („Null-Werten“) umgeht. Das ist ein Design-Problem, das oft vergessen wird.

#### Checkliste für deine Szenarien

Wenn du deine Szenarien schreibst, prüfe sie gegen diese Punkte:

1.  **Enthält es einen Zeitdruck oder physischen Stressor?** (Westeuropäischer Kontext: Pendeln in der U-Bahn, Warten auf Kaffee, kurz vor dem Meeting).
2.  **Gibt es einen internen Dialog?** (Zweifel, Scham, Angst, Stolz).
3.  **Wird ein „Fehler“ begangen?** (Tippfehler, Abbruch, Ablenkung durch Notification).
4.  **Ist das Ziel emotional definiert?** (Nicht „Button klicken“, sondern „Sicherheit fühlen“).

Schreibe lieber **3 detaillierte Szenarien** (eines für jede Kern-Persona in einer Krisen-Situation) als 20 flache „User klickt hier“-Texte. Das bringt deinem Produktteam den entscheidenden Mehrwert.

### User Flows

Das ist eine sehr gute Frage. Viele UX-Designer machen den Fehler, riesige „Spaghetti-Diagramme“ zu zeichnen, in denen man vor lauter Pfeilen den Hauptweg nicht mehr erkennt. Das ist unlesbar für Entwickler.

Wenn du nach **Perfektion** strebst, trennst du den **Happy Path** (alles läuft glatt) von den **Unhappy Paths / Edge Cases** (Fehler, Abbruch, leere Zustände).

Hier ist der „Goldstandard“ für die Dokumentation – und ein neues Beispiel für deine **„Quantified Self“ Persona (Der skeptische Optimierer)**.

#### Methode: Wie schreibt man Unhappy Paths? (The „Main Path + Exception“ Model)

Statt für jeden Fehler einen komplett neuen Flow zu malen (was zu Redundanz führt), nutzt man eine **nummerierte Schritt-Liste mit Ausnahmen**.

Stell dir den Flow wie eine Autobahn vor (Happy Path). Die Unhappy Paths sind die Ausfahrten, die wir aber sofort behandeln.

**Die Struktur:**
1.  **Schritt X** (Normalfall)
    *   *Ausnahme X.1:* (Was passiert, wenn Fehler A auftritt?) -> **Recovery** (Lösung)
    *   *Ausnahme X.2:* (Was passiert, wenn Fehler B auftritt?) -> **Recovery** (Lösung)

Da deine App **Privacy First & Local Storage** ist, fallen Server-Fehler (404, Timeout) weg. Dafür hast du andere, kritische Probleme: **Daten-Korruption, Speicherplatz voll, App-Absturz beim Schreiben, versehentliches Löschen.**


#### Neues Beispiel: Persona 3 – Der skeptische Selbst-Optimierer
**Kontext:** Er will morgens beim Kaffee seine Stimmung tracken, tippt aber aus Versehen das Falsche ein (ein klassischer „Fat Finger“ Fehler). Er ist ungeduldig.
**Ziel:** Daten korrigieren und Trend sehen.

##### Der User Flow (Text-Spezifikation)

**Prämissen:** App läuft lokal (SQLite DB auf dem Gerät). Keine Cloud.

| # | User Action (Trigger) | System Logic (Happy Path) | UI Feedback | **Unhappy Path / Edge Cases (Die „Perfektion“)** |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Öffnet App („Cold Start“). | Lädt lokale DB. Berechnet Statistik der letzten 7 Tage neu. | Dashboard erscheint (< 1s). | **1a. Datenbank korrupt:** App erkennt Lesefehler beim Start. <br>→ *Recovery:* Zeigt Screen „Datenbank wird repariert“ (Backup wiederherstellen), statt abzustürzen. |
| **2** | Tippt auf „Stimmung heute“ (Skala 1-10). Will eine „8“ tippen, rutscht ab auf „2“. | System registriert den Touch auf „2“. | Button „2“ leuchtet auf. Skala animiert. | **2a. Zittern/Fehleingabe:** User merkt *während* des Tippens den Fehler. <br>→ *Recovery:* Erneutes Tippen auf „8“ überschreibt die „2“ sofort (kein Deselect nötig). |
| **3** | Tippt reflexartig auf „Speichern“. | Schreibt Wert „2“ in DB. Zeitstempel: Jetzt. | Toast-Message: „Gespeichert“. Dashboard aktualisiert sich sofort (zeigt jetzt einen Absturz im Graph). | (Kein Fehler hier, System funktioniert, aber User hat Fehler gemacht). |
| **4** | Realisiert den Fehler: „Mist, ich bin nicht depressiv, mir geht's gut!“ | - | User sieht den falschen Graphen und ärgert sich. | **4a. Frustration:** Wenn er jetzt 5 Klicks braucht zum Ändern, schließt er die App. |
| **5** | **Der „Undo“-Moment:** Tippt auf die „Undo“-Option in der Snackbar (oder schüttelt das Handy - *Shake to Undo*). | Setzt Datenbank-Transaktion zurück (Rollback). | Wert im Graph springt zurück. Snackbar: „Eintrag widerrufen“. | **5a. Snackbar schon weg:** (Nach 3 Sek). User muss manuell in den Kalender -> Tag wählen -> Editieren. <br>→ *Lösung:* Der letzte Eintrag bleibt im Dashboard 30 Sek. lang direkt editierbar („Quick Edit“). |
| **6** | Tippt korrekte „8“ und speichert. | Update DB Record. Recalculate Stats. | Graph zeigt Aufwärtstrend. Animation: Konfetti (dezent). | - |


#### Was lernen wir daraus für deine Dokumentation?

Wenn du Flows schreibst (egal ob in Figma, Miro oder als Text), beachte diese drei Regeln für Perfektion:

##### 1. Lokale Konflikte sind die neuen Server-Fehler
Da du „Local Storage“ nutzt, musst du definieren:
*   **Storage Full:** Was, wenn das Handy voll ist? (Unhappy Path: Die App darf nicht einfach nichts tun. Sie muss sagen: „Kann nicht speichern, Speicher voll.“)
*   **Background Kill:** Was, wenn der User die App minimiert, *bevor* der Schreibprozess in die SQLite-DB fertig ist? (Lösung: Der Prozess muss atomar sein oder beim nächsten Start wiederaufgenommen werden).

##### 2. Unterscheide „Systemfehler“ und „User-Fehler“
In meinem Beispiel oben ist Schritt 4 ein User-Fehler.
*   Ein **schlechter Flow** ignoriert User-Fehler („Der User muss halt aufpassen“).
*   Ein **perfekter Flow** baut Sicherheitsnetze (Undo-Funktion, Papierkorb, Bestätigung nur bei kritischen Aktionen wie „Alles löschen“).

##### 3. Visuelle Darstellung (Best Practice)
Wenn du das visualisieren willst (z.B. in Figma), mach es so:
*   Zeichne den **Happy Path** horizontal von links nach rechts (dicke Pfeile).
*   Zeichne **Unhappy Paths** vertikal nach unten abzweigend (dünne Pfeile, vielleicht rot oder orange).
*   Führe den Unhappy Path **immer** zurück zum Happy Path (Recovery). Ein Fehler-Flow darf nie in einer Sackgasse enden (außer bei fatalem Absturz).

**Beispiel für eine Verzweigung im Diagramm:**
```text
[Eingabe Stimmung]  -----> [Speichern] -----> [Dashboard]
       |
       | (User tippt daneben / Undo)
       V
[Snackbar "Rückgängig"] -----> [Eingabe zurückgesetzt] --(zurück zu)--> [Eingabe Stimmung]
```

#### Zusammenfassung für dein Projekt

Du musst nicht für *alles* einen Flow machen. Konzentriere dich auf die **„Moments of Truth“**:
1.  **Onboarding:** Der erste Start (Privacy Erklärung & Passcode setzen).
2.  **Core Interaction:** Eintrag erstellen (unter Stress / mit Fehlern).
3.  **Crisis:** Was passiert, wenn der User angibt, dass es ihm *sehr* schlecht geht? (Unhappy Path des Lebens -> App muss Hilfsangebote einblenden, UI muss Farbe ändern, Gamification muss deaktiviert werden).

Das ist der Unterschied: Eine normale App zeigt einfach Daten an. Eine perfekte Mental-Health-App erkennt im Flow: *„Oh, Stimmung < 3? Deaktiviere 'Streak'-Anzeige, aktiviere 'Notfall-Nummern'-Button.“* Das gehört direkt in den Flow als logische Verzweigung.

---

## 11. Review Status System

All user needs documents (personas, scenarios, user flows) require review and approval before being referenced in other documents or used as a basis for implementation.

### YAML Frontmatter Requirements

All user needs documents must include:

```yaml
review_status: draft | in_review | approved | deprecated
review_history:
  - date: YYYY-MM-DD
    from: draft | in_review | approved | null
    to: draft | in_review | approved | deprecated
    reviewer: user | LLM | [name]
    notes: "Description of changes or review outcome"
```

### Review Workflow

1. **Creation**: Document starts as `draft`
2. **Submit for Review**: Status changes to `in_review` when ready
3. **Review**: Reviewer examines document
4. **Outcome**: Status → `approved` or back to `draft` with feedback
5. **Modifications**: Any change to `approved` document resets to `in_review`
6. **Deprecation**: Obsolete documents marked as `deprecated`

### Bidirectional Reviews

- LLM creates → User reviews and approves
- User creates → LLM reviews for consistency

### Status Tracking Script

```bash
python scripts/generate_user_needs_status.py
```

Generates `requirements_user_needs/STATUS.md` showing:
- Documents by status
- Documents pending review
- Recently modified documents

**Rule**: Only `approved` documents should be referenced in epics, features, or tasks.

---

## 12. Cross-Reference Notation

Standardized notation for referencing content across documents.

### Format

```
[DOC_TYPE]-[ID]#[SECTION]@[COMMIT]
```

**Components**:
- `DOC_TYPE`: PERSONA, SCEN, FLOW, REQ, EPIC, FEAT, TASK
- `ID`: Document identifier
- `SECTION`: Optional section identifier
- `COMMIT`: Optional Git commit hash

### Examples

**Basic references**:
```
PERSONA-001
SCEN-002-01
FLOW-002-01-01
```

**Section references**:
```
PERSONA-001#core_needs
SCEN-002-01#success_criteria
FLOW-003-01-01#step_5
```

**Version pinned**:
```
PERSONA-001@abc123
SCEN-002-01#privacy_requirements@def456
```

### Usage in Different Documents

**In User Flows**:
```markdown
## Implementation
- Step 1-3: EPIC-CLIENT-001
- Step 4-5: FEAT-CLIENT-001-002
```

**In Epics/Features**:
```markdown
## User Needs Context
Implements: FLOW-001-01-01
Based on: SCEN-001-01#goal
```

### Validation

The status script validates:
- Referenced documents exist
- Broken references are reported
- Circular dependencies are avoided

---

## 13. Deviation Documentation

User flows cannot always perfectly satisfy all scenario needs. Epics and features may require compromises. All deviations must be documented.

### When to Document

Document when:
- User flow cannot fully address scenario success criterion
- Epic/feature compromises on user flow requirement
- Technical constraint forces change to user needs
- Conscious trade-off is made (effort vs. value)

### Deviation Table Format

```markdown
## Deviations from User Needs

| User Need Reference | Deviation | Reason | Value Impact | Mitigation |
|---------------------|-----------|--------|--------------|------------|
| SCEN-002-01#success_criteria.3 | Cannot guarantee <10 min | Technical: STT varies | Low - primary goal met | Typing alternative |
| FLOW-001-01-01#step_2 | Cannot auto-detect | Effort: Out of MVP scope | Medium | Add in v2.0 |
```

**Columns**:
- **User Need Reference**: Cross-reference using notation from SEC-12
- **Deviation**: What differs from ideal
- **Reason**: Why (Technical/Effort/Business)
- **Value Impact**: High/Medium/Low + explanation
- **Mitigation**: Compensation or future plan

### Deviation Workflow

1. Identify gap during implementation planning
2. Assess impact on user value
3. Document in deviation table
4. Include in review process
5. Track for future iterations

### Maintaining Value

When documenting deviations, always ask:
1. Does core value still exist?
2. Is this temporary or permanent?
3. What alternatives exist?

---

## 14. Technology Neutrality Principle

Personas, scenarios, and user flows must remain technology-agnostic to preserve creative solution space.

### Why It Matters

**Problem**: Including implementation details (SQLite, OLED, Flutter) in user needs:
- Narrows solution space prematurely
- Distracts from actual user needs
- Makes documents brittle to technical changes
- Prevents creative, unexpected solutions

**Solution**: Focus on **what** users need and **how** interactions support goals, not **how** technology implements it.

### Guidelines by Document Type

#### Personas: Status Quo, Not Solutions

**FORBIDDEN**:
```markdown
## Implications for the App
- Uses end-to-end encryption
- Stores in encrypted SQLite
- Exports PDFs
```

**CORRECT**:
```markdown
## Current Status Quo (Pre-App)
- Uses paper questionnaires
- Must carry paper + pen everywhere
- Analysis difficult (overlaying protocols)

## Pain Points
- Easy to lose or forget
- Hard to see patterns
- Privacy risk if left out
```

**Principle**: Describe their world BEFORE the app exists.

#### Scenarios: Goals, Not App Behavior

**FORBIDDEN**:
```markdown
## Goal
Open dashboard, see client protocols in database

## Success Criteria
- Loads in <2 seconds
- Uses Material 3
- Synced via cloud
```

**CORRECT**:
```markdown
## Goal
Prepare protocol for client session, hand to client, instruct on filling

## Success Criteria
- Create in <5 minutes
- Clear instructions for client
- Privacy maintained (no other clients visible)

## Context
- When: Before session
- Where: Office
- Emotional state: Time pressure
```

**Principle**: Describe outcome, context, and success - not HOW app achieves it.

#### User Flows: Interaction Patterns, Not Implementation

**FORBIDDEN**:
```markdown
1. Taps button
2. Queries SQLite SELECT *
3. Flutter renders ListView
4. Syncs to Firebase
```

**CORRECT**:
```markdown
1. **Prepare Protocol**
   - Action: Select template, customize
   - Response: Present options, allow customization
   - Success: Ready in <5 min

2. **Share with Client**
   - Action: Generate shareable instance
   - Response: Create unique access (privacy-preserving)
   - Success: Client can access without seeing others
```

**Principle**: Interaction patterns, not technology.

### Allowed vs. Not Allowed

**OK to mention**:
- Interaction modalities: touch, voice, visual
- Non-negotiable constraints: privacy, offline
- User capabilities: screen sizes, accessibility

**NOT OK**:
- Specific tech: SQLite, Firebase, Flutter
- Implementation patterns: MVC, BLoC
- Architectures: client-server
- Libraries/frameworks

### Creative Solution Example

> **Scenario**: Persona needs physical closeness
>
> **Bad**: Social media suggests romantic content
>
> **Good**: App reminds user digital world can't satisfy this need, suggests closing app

This solution only emerges when technology is left open.

### Review Checklist

- [ ] Describes user needs or app features?
- [ ] Could be implemented multiple ways?
- [ ] Would tech change require rewriting?
- [ ] Preserves creative solution space?

If Features/No/Yes/No → revise for technology neutrality.

---

## Version History

| Date | Change |
|------|--------|
| 2026-01-17 | Initial requirement creation |
| 2026-01-18 | Added Phase 4: Content Improvement to Implementation Phases section |
| 2026-01-18 | Added SEC-11 (Review Status System), SEC-12 (Cross-Reference Notation), SEC-13 (Deviation Documentation), SEC-14 (Technology Neutrality Principle) |
