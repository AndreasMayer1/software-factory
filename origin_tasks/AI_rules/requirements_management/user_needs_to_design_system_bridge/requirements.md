---
id: REQ-PROC-026
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-PAIN
status: implemented
updated: 2026-03-01
effort: L
stakeholder: developer
created: 2026-02-07
after:
  - REQ-NFUNC-002
  - REQ-NFUNC-013
blocks:
  - REQ-PROC-033
user_needs:
  personas_served:
    - PERSONA-001
    - PERSONA-002
    - PERSONA-005
    - PERSONA-006
    - PERSONA-007
    - PERSONA-008
    - PERSONA-009
    - PERSONA-010
    - PERSONA-011
    - PERSONA-012
    - PERSONA-013
    - PERSONA-014
  notes: "This requirement serves ALL personas indirectly — it ensures every design decision is grounded in actual user needs rather than arbitrary defaults."
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Persona-to-design mapping methodology documented and referenceable by AI"
    - id: AC-02
      text: "Design-relevant trait categories extracted from all personas"
    - id: AC-03
      text: "Existing design system rules annotated with persona justifications"
    - id: AC-04
      text: "Implementation skills reference persona traits during UI work"
    - id: AC-05
      text: "doc/ presentation guidelines include persona-awareness section"
    - id: AC-06
      text: "Validation checklist exists for verifying design-serves-user-needs"
    - id: AC-07
      text: "Human-in-the-loop decision points documented (what AI can derive vs. what requires human judgment)"
    - id: AC-08
      text: "Two-stream rule creation workflow documented (AI-derived and human-defined)"
    - id: AC-09
      text: "ux-validate-rule skill created for proactive validation of human UX proposals"
    - id: AC-10
      text: "Rule generality tiers (T1 System, T2 Pattern, T3 Screen-specific) documented with classification signals and promotion workflow"
    - id: AC-11
      text: "Rule precedence logic documented (T3 overrides T2 overrides T1 within scope)"
    - id: AC-12
      text: "Design Decision Record (DDR) format defined for persona conflict resolution"
    - id: AC-13
      text: "doc/presentation/ restructured into subfolders (coding/, design/, navigation/, etc.)"
    - id: AC-14
      text: "File naming conventions for design rules defined (t1_, t2_, ddr_ prefixes)"
    - id: AC-15
      text: "Existing design system requirements retroactively annotated with persona justifications"
    - id: AC-16
      text: "Every doc/presentation/ subfolder has a README.md defining allowed content, forbidden content, and naming conventions"
---

# Requirement: Bridge User Needs to UI/UX Design System

## 1. Overview

This requirement defines the methodology and artifacts needed to create a traceable chain from **persona characteristics** to **concrete design system rules**. Every design decision should be defensible: when someone asks "Why are buttons this size?", the answer traces back to a specific persona need.

**Core principle**: Design decisions are not arbitrary preferences — they are derived from documented user constraints.

**Two streams for rule creation**:
1. **AI-derived (bottom-up)**: AI extracts persona traits → derives constraints → codifies rules → human reviews
2. **Human-defined (top-down)**: Human proposes UX rule → validates against personas → documents if aligned → AI implements

Both streams maintain persona-grounding. The difference is who initiates and who validates.

## 2. Purpose

- Make design decisions **defensible** through user-need traceability
- Ensure AI agents **consider personas** when implementing UI components
- Prevent design rules from existing in isolation, disconnected from the users they serve
- Enable validation: "Does this design actually serve its intended users?"

## 3. The Gap

### What exists

| Pillar | Status | Location |
|--------|--------|----------|
| Personas with rich constraints | 13 personas, approved | `requirements_user_needs/personas/` |
| Design system rules | Defined, partially implemented | `requirements_tasks/non-functional/ui_ux_design_system/` |
| Cross-referencing system | Flow ↔ Epic traceability | `README_8`, `README_13` |
| AI implementation skills | Orchestrated workflows | `.claude/skills/` |
| Presentation guidelines | Accessibility, responsive, semantics | `doc/presentation.md` |

### What is missing

| Gap | Impact |
|-----|--------|
| No methodology for deriving design rules FROM persona traits | Design rules are generic, not grounded in user reality |
| AI skills don't read personas during UI implementation | AI follows rules mechanically without understanding *who* they serve |
| Design system requirements lack persona justifications | Rules can be weakened or removed because their purpose is invisible |
| No structured extraction of design-relevant traits from personas | Same persona information is re-analyzed every time instead of extracted once |
| No validation approach for "design serves user needs" | No way to verify that implemented UI actually addresses persona constraints |
| **No workflow for human-defined UX rules** | **Humans propose UX ideas but can't validate them against personas proactively → wasted implementation cycles** |

## 4. Methodology: Persona Trait → Design Rule

### 4.0 Architectural Context: How This Fits Into the Existing System

#### The Three Layers and Their Audiences

The project has a clear separation of concerns. Design rules from this methodology must respect it:

| Layer | Location | Audience | Contains | Example |
|-------|----------|----------|----------|---------|
| **Requirements** | `requirements_tasks/` | Task planning, human review | WHAT to build + WHY (acceptance criteria, user stories) | REQ-NFUNC-002: "App must meet WCAG AA, 48dp touch targets" |
| **doc/ guidelines** | `doc/presentation/` | Implementation agent (reads ALWAYS) | HOW to build correctly + WHY it matters (actionable rules, code patterns, token references) | "Use `ComponentTokens.buttonMinHeight` for all interactive elements. Persona justification: Jana (tremors), Sophie (motor imprecision)" |
| **Design tokens** | `lib/config/theme/` | Implementation agent (uses in code) | The actual coded values (primitives → semantic → component tokens) | `ComponentTokens.buttonMinHeight = 48.0` |

**Critical rule**: An implementation agent reads its **one task** (goal.md) + **all relevant `doc/`** guidelines. It does NOT browse `requirements_tasks/` for general rules. Therefore:

- **T1/T2 design rules MUST live in `doc/`** — they are cross-cutting guidelines the agent needs for ANY task
- **T3 design rules live in the task** — they are feature-specific decisions the agent gets via its goal.md
- **Requirements** define acceptance criteria and create tasks, but are NOT read by the coding agent during implementation

#### How Design Rules Relate to Tokens

Design rule files in `doc/presentation/design/` are **actionable guidelines with persona armor**, not pure requirements. They contain three things:

1. **WHAT** — the design constraint (e.g., "all touch targets >= 48dp")
2. **HOW** — the token or code pattern to use (e.g., "use `ComponentTokens.buttonMinHeight`")
3. **WHY** — the persona justification (e.g., "because Jana has tremors, Sophie has motor imprecision")

The WHY is the new addition from this methodology. It serves as **armor** — it prevents future agents or humans from weakening rules whose purpose is invisible.

Design rule files **reference** tokens, they do NOT redefine values:

```
doc/presentation/design/t1_touch_targets.md  (WHAT + HOW + WHY)
    ↓ references
lib/config/theme/tokens.json  (the actual value: 48px)
    ↓ generates
lib/config/theme/tokens.g.dart  (ComponentTokens.buttonMinHeight = 48.0)
    ↓ used by
lib/  (implementation code)
```

If a design rule requires a new token (e.g., crisis-mode 64dp targets), the rule file documents the need, and the implementation creates the token in `tokens.json`.

#### How This Relates to the Regular Feature Flow

The existing feature flow already handles many UX decisions:

```
persona → scenario → user flow → (epic →) feature → task → agent implements
```

Some UX decisions are captured in user flows and flow into feature tasks (e.g., "mood capture requires max 3 steps"). The implementation agent receives these via its task's goal.md.

**What the persona-design bridge adds** are cross-cutting rules that NO SINGLE TASK should have to specify because they apply to EVERY task:

| Already covered by feature flow | Added by persona-design bridge |
|--------------------------------|-------------------------------|
| Feature-specific UX decisions (screen layout, specific interactions) | Cross-cutting design constraints (touch targets, dark mode, auto-save) |
| Captured in user flows → features → tasks | Captured in `doc/presentation/design/` (T1/T2 rules) |
| Agent reads from its task's goal.md | Agent reads from `doc/` (always) |
| T3 (screen-specific) decisions | T1 (system) and T2 (pattern) decisions |

**The boundary**: If a UX decision applies to only one screen, it belongs in the feature task (T3). If it applies to multiple screens or all screens, it belongs in `doc/` (T1/T2) so every agent follows it automatically.

### 4.1 Design-Relevant Trait Categories

Not every persona detail matters for design. The following categories are design-relevant — traits that directly constrain or shape UI/UX decisions:

| Category | Description | Example personas |
|----------|-------------|------------------|
| **Motor constraints** | Physical ability to interact with touch targets, perform precise gestures | Jana (tremors), Sophie (motor imprecision), Nina (fatigue) |
| **Cognitive load budget** | Capacity for processing information, making decisions, following steps | Max (depression fog), David (ADHD 3s window), Nina (brain fog), Jana (tunnel vision) |
| **Time-to-capture window** | Maximum acceptable duration from intent to completed action | David (<3 taps), Dr. Turan (3-min appointments), Jana (crisis = seconds) |
| **Environmental light constraints** | Ambient light conditions during primary usage | Hanna (absolute darkness), Lisa (late night), Elias (needs discrete brightness) |
| **Privacy/discreteness requirements** | Need for app to be non-identifiable as mental health tool | Elias (therapy stigma), Michael (career fear), Lisa (Verbeamtung), Hanna (partner) |
| **Emotional sensitivity to UI patterns** | Vulnerability to guilt, shame, or anxiety triggered by UI elements | Max (blank-field paralysis), Sophie (streak shame), Jana (crisis vulnerability) |
| **Sensory/environmental adaptation** | Need for the app to adapt to specific physical contexts | Hanna (dark room), Prof. Weber (no tech in therapy), Dr. Sarah (desktop office) |
| **Data density tolerance** | Capacity for consuming dense information displays | Dr. Turan (wants density, 3-min scan), Max (overwhelmed by density), David (needs simplicity) |

### 4.2 Two Streams for Rule Creation

UX design rules can originate from two sources, both grounded in personas:

#### Stream 1: AI-Derived Rules (Bottom-Up)

**When to use**: When implementing a feature with no existing design direction, or when exploring what personas need.

**Process**:
```
1. EXTRACT: Identify design-relevant trait from persona document
   Source: persona.md → "What doesn't work" / "Barriers" / "Anti-Traits" / "Trigger & Context"

2. DERIVE: Translate trait into design constraint
   Format: "Because [persona] has [trait], the UI must [constraint]"

3. CLASSIFY TIER: Determine rule generality (see section 4.4)
   - T1 (System): Applies to ALL screens
   - T2 (Pattern): Applies to recurring pattern
   - T3 (Screen-specific): Applies to one screen only
   If uncertain, flag for human decision.

4. CODIFY: Express constraint as actionable implementation guideline
   - WHAT: The design constraint (specific, measurable)
   - HOW: Token reference or code pattern (e.g., "use ComponentTokens.buttonMinHeight")
   - WHY: Persona justification with PERSONA-IDs
   - If no token exists for the value, flag that a new token needs to be created in tokens.json
   Stored in tier-appropriate location (T1/T2 → doc/, T3 → task)

5. HUMAN REVIEW: Human approves rule AND confirms tier classification
```

**Provenance marker**: `## AI-Derived, [Tier] (persona-grounded)`

#### Stream 2: Human-Defined Rules (Top-Down)

**When to use**: When human has UX expertise/preference and wants to validate it against user needs proactively (before AI implements).

**Process**:
```
1. PROPOSE: Human specifies UX rule (e.g., "swipe gesture for quick entry", "bottom sheet for filters")

2. VALIDATE: Use ux-validate-rule skill to check against personas:
   - Which personas would use this feature?
   - Does the rule align with their traits?
   - Does it contradict any anti-traits?
   - Does it address documented pain points?
   - Does it conflict with existing persona-derived rules?

3. CLASSIFY TIER: AI proposes tier, human confirms (see section 4.4)
   - T1 (System): "This should apply globally"
   - T2 (Pattern): "This applies wherever [pattern] occurs"
   - T3 (Screen-specific): "This only applies to [this screen]"

4. DOCUMENT: If aligned, write rule to tier-appropriate location as actionable guideline:
   - WHAT: The design constraint
   - HOW: Token reference or code pattern (identify existing token or flag need for new one)
   - WHY: Persona validation results with PERSONA-IDs
   - Provenance: "Human expertise, validated against [PERSONA-IDs], Tier [T1/T2/T3]"

5. IMPLEMENT: AI implements the validated rule
```

**Provenance marker**: `## Human-Defined, [Tier] (persona-validated)`

**Critical principle**: Both streams MUST ground in personas. Human ideas are not arbitrary—they must validate against user needs or be rejected.

### 4.3 Concrete Examples (with Tier Classification)

**Example 1: Motor impairment → Touch target inflation** `T1 (System) + T2 (Pattern)`

| Step | Content |
|------|---------|
| EXTRACT | PERSONA-014 (Jana): "hands shake" during crisis; PERSONA-010 (Sophie): cluster includes "seniors" with reduced motor precision |
| DERIVE | Because Jana's hands shake during crisis and Sophie's cluster includes users with motor imprecision, interactive elements in emotion-capture flows must exceed the 48dp Material minimum |
| CLASSIFY | Base 48dp rule = **T1 (System)** — applies to ALL screens. Crisis-mode 64dp inflation = **T2 (Pattern)** — applies to emotion-capture screens specifically |
| CODIFY | **T1 Rule**: All touch targets ≥ 48dp — use `ComponentTokens.buttonMinHeight` (48.0). **T2 Rule**: Crisis-mode touch targets ≥ 64dp — needs new token `component.button.crisisMinHeight`. Spacing between adjacent destructive actions ≥ 16dp — use `SpacingTokens.md` |

**Example 2: Absolute darkness → True dark theme** `T1 (System)`

| Step | Content |
|------|---------|
| EXTRACT | PERSONA-007 (Hanna): "Light barrier is ABSOLUTE — cannot turn on light", "White/bright apps are unusable" |
| DERIVE | Because Hanna uses the app in complete darkness next to a sleeping partner, standard Material Dark (grey #121212) is still too bright |
| CLASSIFY | **T1 (System)** — dark mode affects every screen globally |
| CODIFY | **T1 Rule**: Dark mode background must be OLED-true black (#000000). Maximum surface elevation tint: 4% white. Night-mode text uses reduced contrast (not pure white) |

**Example 3: 3-second cognitive window → Interaction budget** `T1 (System)`

| Step | Content |
|------|---------|
| EXTRACT | PERSONA-008 (David): "If it takes more than three taps, I've already forgotten why I opened the app"; PERSONA-014 (Jana): crisis tunnel vision limits multi-step processing |
| DERIVE | Because David's ADHD creates a ~3-second window and Jana's crisis state narrows cognition, core capture flows cannot require deliberation |
| CLASSIFY | **T1 (System)** — auto-save and interaction budget apply to all data-capture flows |
| CODIFY | **T1 Rule**: Primary data-capture flows complete in ≤ 3 interactions (tap → input → auto-save). No explicit "save" button — auto-save on every change |

**Example 4: Blank-field paralysis → Pre-filled scaffolding** `T1 (System)`

| Step | Content |
|------|---------|
| EXTRACT | PERSONA-002 (Max): "Empty fields feel cognitively overwhelming — he doesn't know where to start"; PERSONA-010 (Sophie): "Open-ended questions trigger overwhelm" |
| DERIVE | Because Max and Sophie experience cognitive paralysis from empty forms, input screens must provide structure |
| CLASSIFY | **T1 (System)** — all input screens should avoid blank-field paralysis |
| CODIFY | **T1 Rule**: Never present empty free-text fields without either (a) structured prompts, (b) pre-filled defaults, or (c) selection-first input (slider/chips/radio before optional text) |

**Example 5: Discrete identity → Non-clinical app appearance** `T1 (System)`

| Step | Content |
|------|---------|
| EXTRACT | PERSONA-009 (Elias): "cannot bring himself to pull out therapy homework notebook in public"; PERSONA-006 (Michael): "Can't use anything that looks like a mental health app at work" |
| DERIVE | Because Elias and Michael face real social consequences if the app is identified as mental-health-related, the app's visual identity must be neutral |
| CLASSIFY | **T1 (System)** — app identity, icon, and default appearance affect everything |
| CODIFY | **T1 Rule**: App icon, splash screen, and default view must not contain mental health signifiers (hearts, brains, meditation imagery, pastel palettes). Name and icon should be neutral/professional |

**Example 6: Delete button placement** `T2 (Pattern)` — *showing tier classification in action*

| Step | Content |
|------|---------|
| EXTRACT | PERSONA-014 (Jana): tremors make mis-taps likely; PERSONA-002 (Max): accidental deletion increases shame |
| DERIVE | Because Jana and Max are vulnerable to accidental destructive actions, delete buttons must be distanced from primary actions |
| CLASSIFY | **T2 (Pattern)** — applies to all entity-modification screens (plans, protocols, entries), not just one screen. Found in: plan modification, protocol modification. Likely to recur for: client management, entry editing |
| CODIFY | **T2 Rule**: On entity-modification screens, destructive actions go in AppBar overflow menu (not inline with primary actions). Two-step confirmation required. Current example: master-detail pattern |

**Example 7: Plan preview button** `T3 (Screen-specific)` — *showing a one-off decision*

| Step | Content |
|------|---------|
| CONTEXT | Plan modification screen has a unique "Preview as client" feature showing how a plan looks when filled out |
| CLASSIFY | **T3 (Screen-specific)** — this feature exists only on the plan modification screen. No other screen has a "preview as different role" concept. Promotion unlikely |
| DECISION | Button placement, styling, and behavior documented in the plan modification feature's own `requirements.md`, not in global guidelines |

### 4.4 Rule Generality Tiers

Not all design rules have the same scope. A rule like "touch targets ≥ 48dp" applies everywhere, while "preview button placement on plan modification screen" applies only once. Confusing these leads to either **over-engineering** (generalizing one-offs) or **inconsistency** (deciding recurring patterns ad-hoc on each screen).

#### The Three Tiers

| Tier | Name | Scope | Decision criterion | Example |
|------|------|-------|-------------------|---------|
| **T1** | **System-Level** | ALL screens, extends/overrides Material Design | Universal constraint that no screen should violate | "Touch targets ≥ 48dp", "Auto-save on every change", "Dark mode uses OLED black" |
| **T2** | **Pattern-Level** | Recurring pattern across multiple screens/features | Pattern needed in ≥2 contexts, or very likely to recur | "Delete button always in AppBar overflow menu", "Master-detail opens via push navigation", "Destructive actions use two-step confirmation" |
| **T3** | **Screen-Specific** | One screen/feature only | Unique to this context, unlikely to recur | "Preview plan button placement on plan modification screen", "Therapist quick-triage filter layout" |

#### Tier Classification Process

AI classifies the tier; human confirms (especially for uncertain cases).

**AI Classification Signals:**

| Signal | Points toward | Example |
|--------|--------------|---------|
| "Every screen needs this" | T1 (System) | Touch targets, color contrast, auto-save |
| "This pattern exists on another screen already" | T2 (Pattern) | Delete confirmation, master-detail navigation |
| Persona trait applies to ALL usage contexts | T1 (System) | David's 3-tap limit applies everywhere |
| Persona trait applies to specific scenario type | T2 (Pattern) | Jana's crisis-mode touch inflation applies to emotion-capture screens |
| Feature is unique in the product | T3 (Screen-specific) | Plan preview is only on plan modification |
| No similar pattern found in codebase | Likely T3 initially | New interaction without precedent |

**Uncertain cases** (AI flags for human decision):
- Pattern exists once today but *might* recur → AI flags: "Currently T3, could become T2. Promote now or wait?"
- Rule seems universal but has exceptions → AI flags: "T1 candidate with exclusions. Confirm scope."

#### Tier Lifecycle: Promotion

Rules can be **promoted** from lower to higher tiers when patterns emerge:

```
T3 (Screen-specific) → T2 (Pattern) → T1 (System)
    Never demoted (demotion = deletion from higher tier)
```

**Promotion trigger**: When implementing a second screen that needs the same design decision, the AI should:
1. Search for existing T3 rules on similar screens
2. If found: propose promotion to T2 with both examples as evidence
3. Human approves promotion and defines the generalized rule

**Example promotion**:
```
Original (T3): "On plan modification screen, delete button is in AppBar overflow menu"
Trigger: Implementing protocol modification screen — also needs a delete button
Promotion (T2): "On all entity-modification screens, destructive actions go in AppBar overflow menu"
Evidence: plan modification, protocol modification
Validated against: Jana (tremors → destructive actions need distance from primary actions),
                   Max (depression → accidental deletion risk)
```

#### Rule Precedence (Override Logic)

When rules at different tiers address the same concern, the **more specific tier overrides** the more general one for its scope:

```
T3 overrides T2 overrides T1 (within the more specific scope)
```

This is analogous to CSS specificity: a specific rule wins over a general one.

| Situation | Resolution |
|-----------|------------|
| T1 says "touch targets ≥ 48dp", T2 says "crisis screens: touch targets ≥ 64dp" | **T2 wins** for crisis screens. T1 still applies everywhere else. No conflict. |
| T1 says "auto-save on every change", T3 says "on plan preview screen: explicit save button required" | **T3 wins** for that screen. T1 still applies everywhere else. Document WHY in T3. |
| Two T2 rules contradict for the same pattern scope | **Conflict** — requires human resolution (see section 4.8) |
| T2 tries to weaken a T1 rule globally | **Forbidden** — T2 can only be MORE restrictive than T1, or override for a specific scope. Weakening T1 globally requires changing the T1 rule itself. |

**AI behavior**: When AI detects that a decision contradicts a higher-tier rule, it should flag it and ask:
- "This overrides T1 rule [X] for this specific scope. Is this intentional? If yes, I'll document it as a T2/T3 override with justification."

#### How Tiers Interact with Streams

Tier classification applies to **both** streams:

| Stream | + T1 (System) | + T2 (Pattern) | + T3 (Screen-specific) |
|--------|--------------|----------------|----------------------|
| **AI-Derived** | AI derives universal constraint from persona trait | AI notices recurring pattern across features | AI derives rule for specific screen |
| **Human-Defined** | Human defines global design standard | Human standardizes a recurring interaction pattern | Human specifies a one-off design decision |

### 4.5 Where Design-as-Code Rules Live

Design rules are stored based on their **tier**. The key architectural rule is: **implementation agents read `doc/` always but do NOT browse `requirements_tasks/` for general rules.** Therefore T1/T2 rules MUST be in `doc/`.

| Tier | Storage Location | Content Format | Agent reads |
|------|-----------------|----------------|-------------|
| **T1 (System)** | `doc/presentation/design/t1_*.md` | Actionable guideline: WHAT (constraint) + HOW (token/code pattern reference) + WHY (persona justification) | Always (every UI task) |
| **T2 (Pattern)** | `doc/presentation/design/t2_*.md` | Pattern guideline: WHAT (when the pattern applies) + HOW (token/code pattern reference) + WHY (persona justification) | Always (agent matches pattern to current task) |
| **T3 (Screen-specific)** | Feature task's `goal.md` or `plans_and_protocols/` | Design decision documented inline in the task | Only when implementing that specific task |

**Key principles**:
- `doc/presentation/design/` contains **actionable implementation guidelines**, not requirements. They tell the agent HOW to build correctly, with persona justification as armor.
- T3 rules stay with their feature task — the agent gets them via its goal.md, not via `doc/`.
- Design system **requirements** (`requirements_tasks/non-functional/ui_ux_design_system/`) define acceptance criteria and create tasks. They receive persona annotations (T5) for traceability, but the agent reads the `doc/` guideline, not the requirement file.

**Note**: `doc/` subdirectories contain individual source files (not merged). AI reads relevant files directly via Glob/Grep. The previous merge script is being removed (see TASK-PROC-027-01).

#### Subfolder Structure for `doc/presentation/`

The current `doc/presentation/` folder mixes coding conventions with design rules. With persona-derived rules being added, a subfolder structure is needed to keep things navigable:

```
doc/presentation/
├── coding/                          # HOW to code UI (technical patterns, Flutter conventions)
│   ├── README.md                    # Defines: coding conventions, Flutter widget patterns, state management patterns
│   ├── button_guidelines.md         # (existing, moved)
│   ├── component_api.md             # (existing, moved)
│   ├── component_states.md          # (existing, moved)
│   ├── state_management.md          # (existing, moved)
│   ├── folder_structure.md          # (existing, moved)
│   ├── atomic_design.md             # (existing, moved)
│   ├── best_practices.md            # (existing, moved)
│   └── ...
│
├── design/                          # Actionable design guidelines with persona justification (WHAT + HOW + WHY)
│   ├── README.md                    # Defines: persona-derived design guidelines, DDRs, tier system, naming conventions
│   ├── persona_design_bridge.md     # Main lookup table: trait categories → rules
│   ├── t1_touch_targets.md          # System-level rules (T1)
│   ├── t1_dark_mode.md
│   ├── t1_auto_save.md
│   ├── t1_input_scaffolding.md
│   ├── t1_discrete_identity.md
│   ├── t2_destructive_actions.md    # Pattern-level rules (T2)
│   ├── t2_crisis_mode_targets.md
│   ├── t2_master_detail.md
│   ├── ddr_density_by_role.md       # Design Decision Records (DDRs)
│   └── ...
│
├── navigation/                      # Navigation patterns
│   ├── README.md                    # Defines: navigation architecture, routing patterns, deep linking
│   ├── navigation_patterns.md       # (existing, moved)
│   └── responsive_layout.md         # (existing, moved)
│
├── platform/                        # Platform-specific & responsive
│   ├── README.md                    # Defines: platform-specific adaptations, responsive breakpoints, localization
│   ├── platform_guidelines.md       # (existing, moved)
│   ├── grid_system.md               # (existing, moved)
│   └── localization.md              # (existing, moved)
│
├── tokens/                          # Design tokens & theme system
│   ├── README.md                    # Defines: design token definitions, theme configuration, color/typography tokens
│   ├── token_system.md              # (existing, moved)
│   └── design_system.md             # (existing, moved)
│
├── accessibility/                   # Accessibility guidelines
│   ├── README.md                    # Defines: WCAG compliance rules, screen reader patterns, semantic markup
│   └── accessibility_guidelines.md  # (existing, moved)
│
└── libs/                            # Library references (existing)
    ├── README.md                    # Defines: third-party library usage guidelines, API references
    ├── material_component_api.md
    └── wolt_responsive_layout_grid.md
```

#### Subfolder README Requirements

**Every subfolder** in `doc/presentation/` MUST have a `README.md` that defines:

1. **Purpose**: What kind of content belongs in this folder
2. **Allowed content**: What types of files may be added here (with examples)
3. **Forbidden content**: What does NOT belong here (to prevent misplacement)
4. **Naming conventions**: File naming rules specific to this subfolder (if any)

This prevents content drift where files end up in the wrong folder over time. AI agents use these READMEs as gatekeepers when deciding where to place new files.

#### File Naming Conventions

Within `doc/presentation/design/`, files follow a naming convention that makes tier and type immediately visible:

| Prefix | Meaning | Example |
|--------|---------|---------|
| `t1_` | System-level rule (applies everywhere) | `t1_touch_targets.md` |
| `t2_` | Pattern-level rule (applies to recurring pattern) | `t2_destructive_actions.md` |
| `ddr_` | Design Decision Record (persona conflict resolution) | `ddr_density_by_role.md` |
| `persona_` | Persona-design bridge reference | `persona_design_bridge.md` |

**No T3 files in this folder** — T3 rules are screen-specific and live with their feature.

**AI discovery**: When implementing UI, AI runs `Glob("doc/presentation/design/t1_*.md")` for system rules and `Glob("doc/presentation/design/t2_*.md")` for pattern rules relevant to the current screen type.

**Provenance markers** now include tier:
- `## AI-Derived, System-Level (T1, persona-grounded)`
- `## Human-Defined, Pattern-Level (T2, persona-validated)`
- `## Human-Defined, Screen-Specific (T3, persona-validated)`

### 4.6 Human-in-the-Loop: What AI Cannot Decide

**The limitation**: AI is probabilistic — it predicts the *most likely* answer from training data. In design, "most likely" often means **"average"** or **"generic"**. AI can derive *constraints* from personas but cannot make *subjective choices* about aesthetics, cultural nuance, or strategic trade-offs.

**Research basis**: Nielsen Norman Group and design leaders like Jared Spool have documented where AI design tools fail — they produce the "average of the internet" rather than intentional, differentiated design.

#### What AI CAN Do (Mechanical Derivation)

These are objective constraints that AI can extract and codify:

- **Numeric thresholds** from persona traits (e.g., "Jana has tremors → touch targets ≥ 64dp")
- **Boolean rules** from persona needs (e.g., "Hanna requires darkness → dark mode must exist")
- **Interaction budgets** from cognitive constraints (e.g., "David has 3s window → ≤3 taps")
- **Pattern violations** (e.g., "Sophie/Max are anti-gamification → no streaks")
- **Technical accessibility** (contrast ratios, ARIA labels, focus order)

#### What Requires HUMAN Judgment

These decisions involve **subjective aesthetics**, **cultural context**, or **strategic trade-offs** that AI cannot resolve:

| Decision Type | Why AI Fails | Human Role | Example |
|---------------|--------------|------------|---------|
| **1. Brand Personality** | AI picks "safe" defaults (Roboto, blue, rounded icons). It cannot judge if a typeface *feels* trustworthy vs. playful vs. clinical. | Human chooses: primary typeface, color emotion, icon style (rounded/angular), overall aesthetic direction | Personas say "non-clinical appearance" — AI can rule out pastel/heart imagery, but cannot choose between neutral-professional vs. neutral-technical vs. neutral-warm |
| **2. Holistic Flow Continuity** | AI designs screens in isolation. It misses logical breaks across screens (e.g., button position flips, redundant data requests, inconsistent terminology). | Human architects the end-to-end journey, checks for continuity, ensures red thread | Navigation between screens may individually follow rules but create jarring transitions |
| **3. Tone of Voice & Cultural Nuance** | AI defaults to US-centric, enthusiastic tone ("Awesome! You did it!"). Cannot judge cultural appropriateness or context-sensitive language. | Human defines tone guidelines, reviews UX copy for cultural fit, adapts idioms | German users expect different formality than US users; clinical context requires different tone than consumer apps |
| **4. Strategic Trade-offs Between Conflicting Personas** | When personas conflict (Dr. Turan wants data density, Max needs simplicity), AI cannot make strategic product decisions. | Human decides: which persona is primary for this feature? What gets prioritized? What's the compromise? | Dashboard design: optimize for therapist efficiency or client simplicity? Both are valid, AI cannot choose |
| **5. Edge Cases & Error States** | AI designs the "happy path" where everything works. Misses: offline states, extreme data (500-char names), multi-device conflicts, deletion consequences. | Human proactively defines edge cases, designs error recovery, writes error copy | What happens when user is offline? When data conflicts between devices? AI won't think of these |
| **6. Visual Hierarchy & Intentional Emphasis** | AI makes buttons equal size/prominence. Cannot decide what deserves visual weight vs. de-emphasis. | Human establishes information hierarchy, makes "Save" bigger than "Delete" (or vice versa for de-escalation patterns) | Confirmation dialog: should "Confirm" or "Cancel" be more prominent? Depends on whether we want to encourage or discourage the action |
| **7. Innovation vs. Convention** | AI only remixes existing patterns from training data. Cannot invent new interaction paradigms. | Human specifies novel patterns explicitly if needed (e.g., Tinder swipe when it was new) | If your app needs a unique interaction, AI will default to standard patterns unless instructed otherwise |
| **8. Semantic Accessibility** | AI can check contrast ratios mechanically but misses cognitive accessibility: Is this text too complex? Is the `alt` text contextually meaningful (not just "image of person")? | Human reviews for cognitive accessibility, writes contextual alt text, simplifies complex language | Alt text: AI writes "user profile image", human writes "upload your profile photo to help others recognize you" |

#### The Human Review Gates

**Review mode**: AI flags decisions requiring human judgment and **pauses for approval** before proceeding. This ensures the human maintains full control until confidence in AI design output is established.

When implementing UI following persona-derived rules, these decision points **require human approval** (AI must pause and present the decision):

1. **Before implementation**: Brand personality choices (typeface, primary colors, icon style)
2. **During implementation**: Strategic trade-offs when personas conflict
3. **After AI implementation**: Holistic flow review (does the journey make sense end-to-end?)
4. **Before finalization**: UX copy tone review (culturally appropriate? contextually sensitive?)
5. **Edge case review**: Did AI consider offline, errors, extreme data, deletion scenarios?
6. **Visual hierarchy check**: Is emphasis intentional or accidental?

**Future evolution**: Once the human has gained confidence that AI delivers good design results consistently, the review mode may evolve to "AI implements, human reviews before finalization" to reduce back-and-forth.

#### The Role Division

```
PERSONAS provide objective constraints
   ↓
AI derives mechanical rules (numbers, thresholds, patterns)
   ↓
AI implements following those rules
   ↓
HUMAN makes subjective choices (aesthetics, trade-offs, tone)
   ↓
HUMAN reviews for gaps (edge cases, continuity, cultural fit)
```

**Metaphor**: AI is the **craftsperson** (builds the wall straight and fast). Human is the **architect** (decides where the wall goes) and **interior designer** (decides what color and texture).

### 4.7 Validating Human-Defined UX Rules

When a human proposes a UX rule (Stream 2), a dedicated skill validates it against personas BEFORE implementation. This prevents wasted effort implementing rules that contradict user needs.

#### The `ux-validate-rule` Skill Workflow

**User invokes**: `"Use ux-validate-rule skill for [UX proposal]"` or `"Validate this UX idea against personas: [description]"`

**Input from user**:
- UX rule proposal (e.g., "Use swipe gesture for deleting entries")
- Target feature/screen (e.g., "Daily mood log screen")
- Rationale (optional, but helpful: "I think swipes are faster than tap-and-hold")

**Skill execution**:

1. **Identify relevant personas**:
   - Which personas will use this feature?
   - Use existing flow/epic cross-references if available
   - If new feature, ask user which personas it serves

2. **Extract relevant traits**:
   - Read identified personas' design-relevant traits
   - Focus on: motor constraints, cognitive load, time-to-capture, environmental context, anti-traits

3. **Alignment check**:
   ```
   For each relevant persona:
   - ✅ SUPPORTS: Does the rule address a documented pain point?
   - ⚠️ NEUTRAL: Rule doesn't help but doesn't harm
   - ❌ CONFLICTS: Rule contradicts traits or anti-traits
   ```

4. **Conflict detection**:
   - Does the rule conflict with existing persona-derived rules?
   - Does it create new accessibility barriers?
   - Does it violate existing design system principles?

5. **Classify tier** (AI proposes, human confirms):
   - Search codebase for similar patterns on other screens
   - T1 if universal constraint, T2 if recurring pattern, T3 if one-off
   - If uncertain, present reasoning and ask user

6. **Generate validation report**:
   ```markdown
   ## Validation Report: [UX Rule Proposal]

   **Proposal**: [Description]
   **Target**: [Feature/screen]
   **Proposed Tier**: [T1/T2/T3] — [reasoning]

   ### Persona Alignment

   | Persona | Alignment | Rationale |
   |---------|-----------|-----------|
   | PERSONA-008 (David) | ✅ SUPPORTS | Swipe is <3 taps, aligns with time-to-capture constraint |
   | PERSONA-014 (Jana) | ❌ CONFLICTS | Swipe requires motor precision; tremors during crisis make this error-prone |
   | PERSONA-002 (Max) | ⚠️ NEUTRAL | No specific motor constraint, but accidental deletion risk |

   ### Tier Classification

   **Proposed**: T2 (Pattern) — swipe-to-delete could apply to any list with deletable items
   **Evidence**: Daily log list, protocol list, possibly entry list
   **Confidence**: Medium — depends on whether other lists will have deletion

   ### Recommendation

   **Result**: MODIFY
   - Swipe could work for personas without motor constraints
   - Add confirmation dialog for destructive swipes (addresses Jana's tremor risk and Max's accidental deletion)
   - OR: Offer swipe as alternative to button, not replacement (user choice)

   ### Conflicts with Existing Rules
   - None detected

   ### Next Steps
   - [ ] User confirms tier (T2 or keep as T3?)
   - [ ] User decides: add confirmation, make optional, or reconsider
   - [ ] If approved, document rule with provenance marker and tier
   ```

7. **Document if approved**:
   - Write rule to **tier-appropriate location** (see section 4.5):
     - T1/T2: `doc/presentation/` source files or design system requirements
     - T3: Feature's own `requirements.md` or task docs
   - Include validation report, provenance marker, and tier classification
   - Reference persona IDs that were checked

8. **Reject if misaligned**:
   - If rule conflicts with critical persona traits and cannot be modified, recommend rejection
   - Explain why it would harm specific personas
   - Suggest alternative approaches if possible

#### Example Validation: "Swipe to Delete"

```
Proposal: "Use swipe gesture to delete daily mood entries"
Target: "Daily log screen (mood tracker)"

VALIDATION:
- David (ADHD): ✅ Fast interaction, good
- Jana (BPD, tremors): ❌ Motor precision required during crisis - BAD
- Sophie (ADHD client): ⚠️ Accidental deletion risk due to impulse

RECOMMENDATION: MODIFY
- Add "undo" snackbar (5-second window to reverse)
- OR: Swipe reveals "Delete" button (two-step)
- OR: Make swipe optional (settings toggle)

RATIONALE: Swipe serves time-constrained personas (David) but harms motor-impaired personas (Jana). Two-step pattern balances both needs.
```

### 4.8 Resolving Persona Conflicts (Standardized Format)

When persona traits lead to contradictory design constraints, AI cannot resolve the trade-off — the **human decides** and states a reason. The decision is documented at the appropriate tier level.

#### When Conflicts Arise

| Conflict type | Example | Resolution approach |
|--------------|---------|---------------------|
| **Density vs. Simplicity** | Dr. Turan wants dense data dashboards; Max needs minimal cognitive load | Feature-level: "This screen serves therapists primarily" |
| **Speed vs. Safety** | David needs <3 taps; Jana needs mis-tap protection | Pattern-level: Combine both (fast path + undo, not confirmation dialog) |
| **Privacy vs. Visibility** | Elias needs discrete appearance; Dr. Sarah needs clear professional identity | Role-based: Different default themes per user role |
| **Richness vs. Restraint** | Prof. Weber wants narrative depth; Dr. Turan wants numbers only | Feature-level: Configurable display mode |

#### Decision Documentation Format

Every persona conflict resolution is documented in a **Design Decision Record (DDR)** at the appropriate tier:

```markdown
### DDR: [Short Title]

**Conflict**: [Which persona needs contradict each other?]
- PERSONA-XXX needs: [need A]
- PERSONA-YYY needs: [need B]

**Decision**: [What was decided and for which scope?]

**Reason**: [Why this trade-off? What was prioritized and why?]

**Decided by**: human
**Date**: YYYY-MM-DD
**Tier**: T1 / T2 / T3
**Affected screens/features**: [List or "all"]

**Mitigations**: [How is the deprioritized persona's need still partially addressed?]
```

#### Where DDRs Are Stored (By Tier)

| Decision scope | Tier | Storage location | Example |
|---------------|------|------------------|---------|
| "This applies to the entire app" | **T1** | `doc/presentation/design/ddr_[topic].md` | "App-wide: prioritize simplicity over density for client role" |
| "This applies whenever [pattern] occurs" | **T2** | `doc/presentation/design/ddr_[topic].md` | "Deletion pattern: fast path + undo snackbar (balances David's speed and Jana's safety)" |
| "This applies only to [this screen]" | **T3** | Feature's `requirements.md` or task `plans_and_protocols/` | "Plan modification screen: therapist-density layout because only therapists see this screen" |

#### Example DDR

```markdown
### DDR: Data Density on Therapist Dashboard

**Conflict**:
- PERSONA-012 (Dr. Turan) needs: Dense data display to make decisions in 3-minute appointments
- PERSONA-002 (Max, as client) needs: Minimal cognitive load, no overwhelming data density

**Decision**: Therapist-facing screens use dense data layouts. Client-facing screens use minimal layouts. Shared screens (if any) default to minimal with optional "detailed view" toggle.

**Reason**: These personas use different parts of the app. The role system already separates their UIs. No compromise needed — each role gets its optimal density.

**Decided by**: human
**Date**: 2026-02-07
**Tier**: T1 (System-level — applies to all screens based on role)
**Affected screens/features**: All therapist screens, all client screens

**Mitigations**: If a therapist has the same cognitive constraints as Max (e.g., tired end-of-day), they can't switch to "simple mode" yet. Future consideration: therapist accessibility settings.
```

#### AI Behavior for Conflicts

1. AI detects conflict: two persona traits lead to contradictory constraints
2. AI presents the conflict clearly with the DDR template partially filled
3. AI suggests possible resolutions (but does NOT choose)
4. **Human decides** and provides reason
5. AI documents the DDR at the appropriate tier location
6. AI implements the decided approach

## 5. Validation Approach

### 5.1 Design Review Checklist

When implementing or reviewing UI, verify:

**AI-Verifiable (Mechanical):**
- [ ] **Persona identification**: Which personas will use this screen/component?
- [ ] **Trait scan**: Do any of those personas have design-relevant traits (motor, cognitive, environmental, privacy, emotional)?
- [ ] **Rule check**: Are existing design rules sufficient for those traits, or do new rules need to be derived?
- [ ] **Justification**: Can every non-default design decision trace back to a persona need?
- [ ] **Contradiction check**: Does the design contradict any persona anti-trait? (e.g., gamification for Sophie/David/Max = anti-trait violation)
- [ ] **Numeric thresholds**: Touch targets, timing, interaction budgets meet persona-derived minimums?

**Human-Review-Required (Subjective):**
- [ ] **Brand personality**: Have typeface, primary colors, icon style been explicitly chosen (not defaulted)?
- [ ] **Flow continuity**: Does the screen-to-screen journey feel coherent? Any jarring transitions?
- [ ] **Tone appropriateness**: Is UX copy culturally appropriate and contextually sensitive for the persona?
- [ ] **Trade-off clarity**: If personas conflict, has the strategic choice been made and documented?
- [ ] **Edge cases**: Offline states, extreme data, errors, multi-device conflicts considered?
- [ ] **Visual hierarchy**: Is emphasis intentional? Do destructive actions have appropriate weight (or de-emphasis)?
- [ ] **Innovation check**: If using a novel pattern, is it intentional and well-justified? If using standard patterns, is that the right choice?

### 5.2 Automated Validation (Future)

- Existing cross-reference validation (`README_8` rules) extended to check persona annotations on design requirements
- Warning when a design system requirement has no `## Persona Justifications` section
- Warning when a UI-facing epic/feature doesn't reference any persona in its `user_needs` YAML

## 6. Implementation Roadmap

This requirement is too large for a single implementation task. It should be split into multiple tasks with dependencies.

### 6.1 Task Breakdown

| # | Task | Effort | Depends on | Description |
|---|------|--------|------------|-------------|
| **T0** | Remove doc merge script | S | — | TASK-PROC-027-01 (already created). Remove merge script and merged output files. Prerequisite for all other tasks. |
| **T1** | Restructure `doc/presentation/` subfolders | S | T0 | Create subfolder structure (`coding/`, `design/`, `navigation/`, etc.). Move existing files to appropriate subfolders. Create README.md for each subfolder (defining allowed/forbidden content). Update references in CLAUDE.md and skills. |
| **T2** | Create persona-design bridge file | M | T1 | Write `doc/presentation/design/persona_design_bridge.md` with trait categories, lookup table, methodology reference. This is the central reference AI reads. |
| **T3** | Create `ux-validate-rule` skill | M | T2 | Build the skill for Stream 2 validation workflow. |
| **T4** | Update implementation skills | S | T2 | Add persona-reading step to `code-simple` and `code-complex` skills. Update quality checker. |
| **T5** | Retroactive annotation of ALL existing requirements | L | T2 | Add persona justifications and tier classifications to ALL existing design system requirements (not just high-impact ones — clean start). Mark as "pre-framework, human-defined." |
| **T6** | Extract initial T1/T2 rules | M | T1, T2 | Create individual `t1_*.md` and `t2_*.md` files in `doc/presentation/design/` for the most important persona-derived rules identified in this exploration. |

### 6.2 Detailed Changes Per Area

#### Skills (`.claude/skills/`)

| Skill | Change needed | Task |
|-------|---------------|------|
| `code-simple/skill.md` | Add step in "Read & Assess" to identify relevant personas for UI work and read persona-design bridge | T4 |
| `code-complex/` | Add step in planning phase to map personas to design constraints | T4 |
| Quality checker agent | Add persona-design validation to quality checklist (including DDR check for conflicts) | T4 |
| **NEW: `ux-validate-rule/`** | Create new skill for human-defined UX rule validation (Stream 2 workflow) | T3 |

**Principle**: Skills should contain a one-line reference to the persona-design bridge, not the full content. Keep skills token-efficient.

#### The ux-validate-rule Skill

**Purpose**: Validate human-proposed UX rules against personas BEFORE implementation (Stream 2).

**Location**: `.claude/skills/ux-validate-rule/skill.md`

**Key responsibilities**:
1. Identify relevant personas for the proposed rule
2. Extract design-relevant traits from those personas
3. Check alignment: SUPPORTS / NEUTRAL / CONFLICTS
4. Detect conflicts with existing rules
5. Classify tier (AI proposes, human confirms)
6. Generate validation report with recommendation
7. Document approved rules with provenance marker at tier-appropriate location
8. Suggest modifications if conflicts exist

#### Guidelines (`doc/`)

| File | Change needed | Task |
|------|---------------|------|
| `doc/presentation/` | Create subfolder structure with README.md per subfolder (see section 4.5) | T1 |
| `doc/presentation/design/persona_design_bridge.md` | Consolidated trait→rule lookup table | T2 |
| `doc/presentation/design/t1_*.md` | Individual system-level rule files | T6 |
| `doc/presentation/design/t2_*.md` | Individual pattern-level rule files | T6 |
| `doc/presentation/design/ddr_*.md` | Design Decision Records (as conflicts are resolved) | Ongoing |

**Dependency**: T0 (TASK-PROC-027-01) must be completed first.

#### Existing Design System Requirements (Retroactive Annotation)

All existing design system requirements predate this framework. They need:
- **Tier classification** (most are T1 or T2)
- **Persona justification** annotations (which personas drove these rules?)
- **Provenance marking**: `## Pre-Framework, Human-Defined` (they were created before this methodology existed)

| Requirement | Tier | Persona justifications needed | Task |
|-------------|------|-------------------------------|------|
| `REQ-NFUNC-002` (Accessibility) | T1 | 48dp targets (Jana, Sophie), WCAG AA (all), Simple Mode (Sophie cluster) | T5 |
| `REQ-NFUNC-013` (UX Writing) | T1 | Empathetic tone (Max, Jana), sensitive context (all client personas), no guilt language (Sophie, David) | T5 |
| `REQ-NFUNC-009` (Loading/Error) | T1/T2 | Timing rules (David), retry patterns (Nina), confirmation dialogs (Jana) | T5 |
| Theming (growth tree theme) | T1 | Dark mode (Hanna), discrete appearance (Elias, Michael), Simple Mode (Sophie cluster) | T5 |
| Navigation patterns | T2 | Master-detail (Dr. Sarah, Dr. Turan), in-detail navigation | T5 |
| Components (toast, skeleton, etc.) | T2 | Error messages (Max, UX writing), loading indicators (Nina, David) | T5 |

#### Cross-Reference System

| Artifact | Change needed |
|----------|---------------|
| `README_8` / `README_13` | Consider extending notation to support trait-to-rule references (lightweight, optional) |

## 7. When to Use / When NOT to Use

### Relationship to the Regular Feature Flow

The regular feature flow (persona → scenario → user flow → feature → task) already handles **feature-specific** UX decisions. Those decisions flow into task goal.md files and the implementation agent receives them naturally.

This persona-design bridge methodology adds **cross-cutting** design rules that apply to multiple features. These are rules that no single task should have to specify because they apply everywhere (or to a recurring pattern).

| UX decision type | Handled by | Where it lives | Example |
|-----------------|-----------|----------------|---------|
| Feature-specific layout/interaction | Regular feature flow | Task goal.md (T3) | "Plan preview button placement on this screen" |
| Recurring pattern across features | Persona-design bridge | `doc/presentation/design/t2_*.md` | "Delete buttons always in AppBar overflow menu" |
| System-wide constraint | Persona-design bridge | `doc/presentation/design/t1_*.md` | "All touch targets >= 48dp" |
| Persona conflict on a specific feature | Feature task + DDR | Task goal.md + DDR at appropriate tier | "Dashboard density: therapist vs. client view" |

### When to Apply This Methodology

- Creating **new T1/T2 design rules** that apply across features
- Implementing any **user-facing** screen or component (agent reads existing T1/T2 rules from `doc/`)
- Reviewing existing UI for persona alignment
- When a **pattern recurs** and needs promotion from T3 to T2

### When NOT to Apply

- Pure backend/infrastructure work with no UI surface
- Automated tests (unless testing persona-specific scenarios)
- System persona (PERSONA-003) work — system maintenance doesn't drive UI design
- `doc/` guideline changes that are purely technical (architecture, DI, routing)
- Feature-specific UX decisions that are already covered by the task's goal.md (these are T3, handled by the regular flow)

## 8. Acceptance Criteria

- [ ] Persona-to-design mapping methodology documented and referenceable by AI
- [ ] Design-relevant trait categories extracted from all personas
- [ ] Existing design system rules annotated with persona justifications
- [ ] Implementation skills reference persona traits during UI work
- [ ] `doc/` presentation guidelines include persona-awareness section
- [ ] Validation checklist exists for verifying design serves user needs
- [ ] Human-in-the-loop decision points documented (what AI can derive vs. what requires human judgment)
- [ ] Two-stream rule creation workflow documented (AI-derived and human-defined)
- [ ] `ux-validate-rule` skill created for proactive validation of human UX proposals
- [ ] Rule generality tiers (T1 System, T2 Pattern, T3 Screen-specific) documented with classification signals and promotion workflow
- [ ] Rule precedence logic documented (T3 overrides T2 overrides T1 within scope)
- [ ] Design Decision Record (DDR) format defined for persona conflict resolution
- [ ] `doc/presentation/` restructured into subfolders (`coding/`, `design/`, `navigation/`, etc.)
- [ ] File naming conventions for design rules defined (`t1_`, `t2_`, `ddr_` prefixes)
- [ ] Existing design system requirements retroactively annotated with persona justifications
- [ ] Every `doc/presentation/` subfolder has a README.md defining allowed content, forbidden content, and naming conventions

## 9. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| **TASK-PROC-027-01** (Remove doc merge script) | **pending** | **PREREQUISITE** — must complete before any doc/presentation/ restructuring |
| REQ-NFUNC-002 (Accessibility) | defined | Will receive persona annotations (Task T5) |
| REQ-NFUNC-013 (UX Writing) | defined | Will receive persona annotations (Task T5) |
| REQ-NFUNC-009 (Loading/Error) | defined | Will receive persona annotations (Task T5) |
| Personas (all 13) | approved | Source material for trait extraction |
| Cross-reference system (README_8, README_13) | documented | Existing traceability framework to extend |

## 10. References

- Personas: `requirements_user_needs/personas/`
- Accessibility: `requirements_tasks/non-functional/ui_ux_design_system/accessibility/requirements.md`
- UX Writing: `requirements_tasks/non-functional/ui_ux_design_system/ux_writing/requirements.md`
- Loading/Error: `requirements_tasks/non-functional/ui_ux_design_system/loading_error_handling/requirements.md`
- Cross-referencing: `requirements_user_needs/README_8_CROSS-REFERENCING_SYSTEMS.md`
- Cross-reference notation: `requirements_user_needs/README_13_CROSS_REFERENCE_NOTATION.md`
- Presentation guidelines: `doc/presentation/` (subfolders + READMEs defined by this requirement)
- Guideline file organization (size limits, restructuring): `requirements_tasks/process/documentation_rules/guideline_file_organization/` (REQ-PROC-048)
