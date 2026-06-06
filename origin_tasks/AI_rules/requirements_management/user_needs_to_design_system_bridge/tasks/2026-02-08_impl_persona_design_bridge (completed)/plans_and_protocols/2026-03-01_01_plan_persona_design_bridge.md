---
date: 2026-03-01
version: 01
type: plan
task_id: TASK-PROC-026-03
agent_id: architecture-advisor-sonnet-4-6-2026-03-01
---

# Implementation Plan: Persona-Design Bridge Document

## Overview

This plan defines the structure, content sources, and creation order for
`doc/presentation/design/persona_design_bridge.md` — the central reference
document that AI agents read during UI implementation to connect persona traits
to concrete design rules.

The document has one job: make the persona-to-design chain operational for AI
agents, without requiring them to browse all 13 persona files during every UI
task. It is a lookup table and decision guide, not academic prose.

**Output file**: `doc/presentation/design/persona_design_bridge.md`
**Destination folder status**: Exists (created by TASK-PROC-026-02)
**Primary source**: REQ-PROC-026 sections 4.0-4.8 and section 5
**Secondary sources**: Exploration protocol, all 13 persona files, existing doc/ patterns

---

## Document Structure

The document has 9 sections. Section numbers below correspond to the final
document's heading hierarchy.

### Section 0: Document Purpose and How to Use (Quick Reference)

**Subsections**:
- What this document is (lookup table for agent consumption)
- When to read it (every UI task — mandatory)
- How to use it (step-by-step for the agent: identify screen type, lookup
  relevant trait categories, apply rules, flag gaps)
- Where design rules live after derivation (T1/T2 in doc/, T3 in task)

**Content source**: REQ-PROC-026 section 4.0 "Architectural Context", goal.md
description, CLAUDE.md "WHY Comments" pattern

**Format**: Short bullet list + a 4-step "How agents use this doc" procedure.
No prose paragraphs.

### Section 1: Design-Relevant Trait Categories (Lookup Table)

**The primary lookup table agents use first when starting any UI task.**

**Subsections**:
- The 8 categories with: category name, description, affected personas (with
  PERSONA-IDs), and design implications
- "How to use": identify which categories apply to the screen being built

**Content source**: REQ-PROC-026 section 4.1 (already in final table format).
Cross-checked against all 13 persona files during this planning phase.

**Format**: Single Markdown table with columns: Category | Description |
Personas Affected | Key Design Implications

**Persona trait summary** (extracted during planning — verified against all
persona files):

| Category | Personas | Key evidence |
|---|---|---|
| Motor constraints | PERSONA-014 (Jana: "hands shake" crisis), PERSONA-010 (Sophie: cluster includes seniors with reduced motor precision), PERSONA-013 (Nina: fatigue-reduced coordination on bad days) | Jana "cannot read small print" on laminated card; Sophie cluster = "Accessibility/seniors: large touch targets" |
| Cognitive load budget | PERSONA-002 (Max: "White Sheet Syndrome"), PERSONA-008 (David: "Wall of Awful"), PERSONA-010 (Sophie: "input paralysis", open-ended questions), PERSONA-014 (Jana: tunnel vision during crisis), PERSONA-013 (Nina: "brain fog" is symptom) | Max: blank fields trigger paralysis; David: >3 taps = forgotten why opened |
| Time-to-capture window | PERSONA-008 (David: "<3 seconds from thought to logged"), PERSONA-012 (Dr. Turan: "3 minutes to decide"), PERSONA-014 (Jana: "crisis = seconds"), PERSONA-007 (Hanna: "any friction at 3 AM is fatal") | David key quote verbatim: "If it takes more than three taps, I've already forgotten why I opened the app" |
| Environmental light constraints | PERSONA-007 (Hanna: "Light barrier is ABSOLUTE — cannot turn on light"), PERSONA-005 (Lisa: "Writing in dark is impossible — late night"), PERSONA-015 (Lena: "by the time I find a pen and turn on the bedside lamp, the feeling is gone") | Hanna: "White/bright apps are unusable" |
| Privacy/discreteness requirements | PERSONA-009 (Elias: "therapy notebook appearance screams therapy"), PERSONA-006 (Michael: "Can't use anything that looks like a mental health app at work"), PERSONA-005 (Lisa: fears "Die Psycho-Lisa" stigma from roommates), PERSONA-007 (Hanna: partner must not see screen) | Elias literally cannot use app in public due to appearance |
| Emotional sensitivity to UI patterns | PERSONA-002 (Max: broken streaks = shame), PERSONA-010 (Sophie: "once streak broke, I never opened it again"), PERSONA-008 (David: "streak broken shame that kills motivation permanently"), PERSONA-014 (Jana: shame after crisis episodes) | Anti-gamification explicit in Max, Sophie, David, Nina anti-traits |
| Sensory/environmental adaptation | PERSONA-007 (Hanna: dark room, partner asleep), PERSONA-011 (Prof. Weber: no technology in therapy room), PERSONA-001 (Dr. Sarah: Windows desktop in office) | Prof. Weber: "The computer has no place in the therapy room" |
| Data density tolerance | PERSONA-012 (Dr. Turan: "I have three minutes to decide", needs dense scan), PERSONA-002 (Max: overwhelmed by density), PERSONA-008 (David: "needs simplicity"), PERSONA-013 (Nina: "cognitive load is the enemy") | Turan vs Max is the canonical conflict example from requirements |

### Section 2: Two-Stream Rule Creation Methodology

**The operational procedure for creating new design rules.**

**Subsections**:
- Stream 1: AI-Derived Rules (Bottom-Up) — the 5-step process
- Stream 2: Human-Defined Rules (Top-Down) — the 5-step process
- Provenance markers for both streams
- Token reference requirement in CODIFY/DOCUMENT steps

**Content source**: REQ-PROC-026 section 4.2 verbatim (already in procedural
format). No significant rewriting needed.

**Format**: Two numbered-step procedures. Each step = 1-2 lines. Code fence for
the procedure (makes it scannable as a process block). Provenance marker lines
after each procedure.

### Section 3: Concrete Examples (7 Examples with Tier Annotations)

**The worked examples that make the methodology concrete and referenceable.**

**Subsections**:
- 7 examples, each as a 4-row table (EXTRACT, DERIVE, CLASSIFY, CODIFY)
- Tier annotation in the heading of each example
- Token references in CODIFY column where available

**Content source**: REQ-PROC-026 section 4.3 (all 7 examples verbatim — they
are already in table format with tier annotations and token references).

**Examples to include (in order)**:
1. Jana's tremors → Touch target inflation (T1 + T2)
2. Hanna's darkness → True dark theme (T1)
3. David's 3-second window → Interaction budget (T1)
4. Max's blank-field paralysis → Pre-filled scaffolding (T1)
5. Elias's discreteness → Non-clinical app appearance (T1)
6. Delete button placement (T2) — shows tier classification for patterns
7. Plan preview button (T3) — shows when NOT to generalize

**Format**: Level-3 headings per example, each with a 4-row Markdown table.
Header format: `**Example N: [description]** \`T[n] ([tier name])\``

### Section 4: Rule Generality Tiers

**The classification system that determines where rules live.**

**Subsections**:
- The Three Tiers overview table (T1/T2/T3 with scope, decision criterion, example)
- Tier Classification Process (AI classifies, human confirms)
- AI Classification Signals table
- Uncertain cases (AI flags for human decision)
- Tier Lifecycle: Promotion (T3 → T2 → T1, never demoted)
- Rule Precedence (T3 overrides T2 overrides T1 within scope, CSS analogy)
- How Tiers Interact with Streams (2x3 matrix table)

**Content source**: REQ-PROC-026 section 4.4 verbatim.

**Format**: Tables for tier overview and signals. Code fence for promotion
workflow (T3 → T2 → T1 diagram). Numbered list for precedence rules. Inline
conflict examples in a separate table.

### Section 5: Architectural Context

**Explains how this document fits into the three-layer system so agents don't
confuse doc/ guidelines with requirements.**

**Subsections**:
- The Three Layers and Their Audiences (requirements vs doc/ vs tokens)
- How Design Rules Relate to Tokens (WHAT + HOW + WHY pattern, reference not
  redefine, diagram of reference chain)
- How This Relates to the Regular Feature Flow (T1/T2 cross-cutting vs T3
  feature-specific)
- Storage location by tier (table: T1 → doc/presentation/design/t1_*.md, etc.)

**Content source**: REQ-PROC-026 section 4.0 "Architectural Context" and section
4.5 "Where Design-as-Code Rules Live".

**Format**: Tables for the layer comparison and storage locations. Code fence for
the token reference chain (doc/ → tokens.json → .g.dart → lib/). Brief
comparison table for feature flow vs persona-design bridge.

**Critical rule to surface clearly**: T1/T2 rules MUST be in doc/ because agents
never browse requirements_tasks/ during implementation.

### Section 6: Human-in-the-Loop Gates

**The 8 decision types requiring human judgment, and when AI must pause.**

**Subsections**:
- What AI CAN Do (objective constraints derivable mechanically)
- What Requires HUMAN Judgment (8 decision types in table)
- The Human Review Gates (6 gate points: before/during/after implementation)
- Role Division (craftsperson/architect metaphor)
- Future evolution note (confidence-building phase → implementation-first later)

**Content source**: REQ-PROC-026 section 4.6 verbatim.

**Format**: Bullet list for AI capabilities. Table for the 8 human-judgment
types (Decision Type | Why AI Fails | Human Role | Example). Numbered list for
review gates. Diagram for role division (AI → human flow).

### Section 7: Persona Conflict Resolution (DDR Format)

**The standardized format for documenting persona conflicts.**

**Subsections**:
- When Conflicts Arise (conflict type table with 4 examples)
- Decision Documentation Format (DDR template as code fence)
- Where DDRs Are Stored (table: decision scope → tier → storage location)
- Example DDR (the density example from requirements)
- AI Behavior for Conflicts (numbered steps)

**Content source**: REQ-PROC-026 section 4.8 verbatim.

**Format**: Table for conflict types. Code fence for DDR template (so agents can
copy-paste the structure). Table for DDR storage by tier. Numbered list for AI
behavior.

### Section 8: Design Review Checklist

**The per-task checklist agents run before considering UI implementation
complete.**

**Subsections**:
- AI-Verifiable checks (6 items — mechanical checks agents can perform)
- Human-Review-Required checks (7 items — subjective checks requiring judgment)

**Content source**: REQ-PROC-026 section 5.1 verbatim.

**Format**: Two separate checkbox lists. Clear visual separation between AI-
verifiable and human-required. No prose between items.

### Section 9: When to Apply / When NOT to Apply

**Prevents over-application of the methodology to non-UI work.**

**Subsections**:
- Relationship to the Regular Feature Flow (table: UX decision type → where
  handled → where lives → example)
- When to Apply this Methodology
- When NOT to Apply

**Content source**: REQ-PROC-026 section 7 verbatim.

**Format**: Table for the feature flow relationship. Bullet lists for apply/
not-apply.

---

## Content Integration

How content flows from sources into the document:

```
REQ-PROC-026 (requirements.md)
    ↓ Sections 4.0-4.8, section 5 → Directly translates to doc sections
    ↓ Methodology, tiers, DDR format, checklist

Exploration protocol (2026-02-07_01_opus_plan.md)
    ↓ Original persona trait extraction → Validates section 1 content
    ↓ 5 initial examples → Expanded to 7 in requirements → All in section 3

All 13 persona files
    ↓ Design-relevant traits verified against actual persona text
    ↓ PERSONA-IDs confirmed for accuracy in section 1 lookup table
    ↓ Direct quotes usable as justification evidence in examples

doc/presentation/ existing files
    ↓ Formatting conventions (headers, tables, code fences, no prose)
    ↓ Confirmed: no YAML frontmatter in coding/ files (plain # heading)
    ↓ Confirmed: tables are the primary structure, code fences for patterns

tokens.json / token_system.md
    ↓ Available token names for HOW column in examples
    ↓ ComponentTokens.buttonMinHeight confirmed at 48.0
    ↓ SpacingTokens.md confirmed as available
    ↓ component.button.crisisMinHeight flagged as MISSING (needs creation)
```

**Content NOT to include in this document**:
- Implementation details for creating T1/T2 rule files (that is TASK-PROC-026-07)
- The ux-validate-rule skill specification (that is TASK-PROC-026-04)
- Retroactive annotation of existing requirements (that is TASK-PROC-026-06)
- Token values themselves (token_system.md is the source; this doc only
  references token names)

---

## AI-Readable Format Guidelines

The document is read by AI agents during implementation, not by humans studying
a methodology. Every structural choice must serve fast AI consumption.

### Use tables, not prose

Every categorical piece of information becomes a table:
- ✅ "The 8 categories with their personas" → table
- ✅ "The 3 tiers and their scopes" → table
- ✅ "8 human-judgment decision types" → table
- ❌ Paragraphs explaining categories → agent will miss half the content

### Use numbered steps, not narrative

Every process becomes a numbered step list:
- ✅ Stream 1: 5 steps (EXTRACT, DERIVE, CLASSIFY, CODIFY, REVIEW)
- ✅ "AI behavior for conflicts": 6 numbered steps
- ❌ "When an agent encounters a conflict, it should first..."

### Use code fences for templates

Every reusable format the agent needs to produce becomes a code fence:
- ✅ DDR template in a code fence (agent copy-pastes structure)
- ✅ Promotion workflow in a code fence (T3 → T2 → T1 diagram)
- ❌ Describing the DDR format in prose

### Use PERSONA-IDs in all references

Every persona reference includes the ID alongside the name:
- ✅ "PERSONA-014 (Jana): hands shake during crisis"
- ❌ "Jana has tremors"

This enables agents to cross-reference the actual persona file if needed,
without ambiguity about which persona is meant.

### Separate AI-verifiable from human-required

The checklist must visually separate what agents can verify mechanically from
what requires human judgment. Use two distinct subheadings, not a single mixed
list. This prevents agents from skipping human-required checks thinking they
already covered them.

### One decision tree for conflict detection

Rather than prose about conflicts, provide:
1. The DDR template (agent fills it in)
2. The AI behavior numbered list (agent follows it)
3. The storage-by-tier table (agent knows where to put the result)

---

## Implementation Order

The sections are not independent — some sections reference others. The correct
creation order minimizes re-reading and re-editing.

### Step 1: Document header and Section 0 (Purpose + How to Use)

**Why first**: Sets the frame for everything else. Defines the document's
audience and usage mode. Short to write (bullet list + 4-step procedure).

**Content needed**: goal.md description + doc/ formatting conventions (already
read).

**Dependencies**: None.

### Step 2: Section 5 (Architectural Context)

**Why second**: Before writing any rules or examples, the agent (the
implementation engineer) needs to understand the three-layer system. If Section
5 is written early, it anchors every subsequent section. Also, this section
has no dependencies on other sections.

**Content needed**: REQ-PROC-026 sections 4.0 and 4.5.

**Dependencies**: None.

### Step 3: Section 4 (Rule Generality Tiers)

**Why third**: The tier system (T1/T2/T3) is referenced in every subsequent
section (trait table, examples, DDR format, checklist). Writing it third means
it exists when needed for cross-references.

**Content needed**: REQ-PROC-026 section 4.4.

**Dependencies**: Section 5 (references token reference chain).

### Step 4: Section 1 (Design-Relevant Trait Categories)

**Why fourth**: The core lookup table. References tier concepts (now written).
Uses PERSONA-IDs (verified during this planning phase — data is ready).

**Content needed**: REQ-PROC-026 section 4.1 + persona file verification
(done in this plan).

**Dependencies**: Section 4 (tier terminology used in "design implications").

### Step 5: Section 3 (Concrete Examples)

**Why fifth**: Examples reference tiers (Section 4), personas (Section 1 data),
and token names. All prerequisite content is ready after steps 3-4.

**Content needed**: REQ-PROC-026 section 4.3 (all 7 examples already in table
format — minimal rewriting).

**Dependencies**: Sections 4 and 1.

### Step 6: Section 2 (Two-Stream Rule Creation Methodology)

**Why sixth**: References tiers and the CODIFY step (which now has examples to
illustrate it). Writing after examples means the methodology explanation is
grounded in concrete cases the agent just saw.

**Content needed**: REQ-PROC-026 section 4.2.

**Dependencies**: Sections 4 and 3 (examples illustrate the streams).

### Step 7: Section 6 (Human-in-the-Loop Gates)

**Why seventh**: References the streams (Section 2) and adds the human judgment
layer. Can now cross-reference the methodology it gates.

**Content needed**: REQ-PROC-026 section 4.6.

**Dependencies**: Section 2 (human gates apply to both streams).

### Step 8: Section 7 (Persona Conflict Resolution)

**Why eighth**: References tiers (Section 4), the human-in-loop concept
(Section 6), and DDRs. All prerequisite content exists.

**Content needed**: REQ-PROC-026 section 4.8.

**Dependencies**: Sections 4, 6.

### Step 9: Section 8 (Design Review Checklist)

**Why ninth**: The checklist references all previous concepts. It is the
synthesis of everything above — writing it last means no forward references.

**Content needed**: REQ-PROC-026 section 5.1.

**Dependencies**: All previous sections.

### Step 10: Section 9 (When to Apply)

**Why last**: Scoping section that references the complete methodology. Cleanest
to write after the full document exists.

**Content needed**: REQ-PROC-026 section 7.

**Dependencies**: All previous sections.

---

## Quality Verification Checklist

Before marking the document complete, verify each acceptance criterion:

### AC-01: Persona-to-design mapping methodology documented and referenceable by AI
- [ ] Section 2 (Two Streams) exists with numbered steps
- [ ] Section 0 explains HOW an agent uses this document
- [ ] Document is structured as a lookup table, not prose

### AC-02: Design-relevant trait categories extracted from all personas
- [ ] Section 1 table includes all 8 categories
- [ ] Every row references specific PERSONA-IDs (not just names)
- [ ] All 13 personas appear at least once in the trait table
  - PERSONA-001 (Dr. Sarah): sensory/environmental (desktop office)
  - PERSONA-002 (Max): cognitive load, emotional sensitivity, data density
  - PERSONA-005 (Lisa): light constraints, privacy/discreteness
  - PERSONA-006 (Michael): privacy/discreteness
  - PERSONA-007 (Hanna): light constraints, time-to-capture, sensory adaptation
  - PERSONA-008 (David): cognitive load, time-to-capture, emotional sensitivity, data density
  - PERSONA-009 (Elias): privacy/discreteness
  - PERSONA-010 (Sophie): motor constraints, cognitive load, emotional sensitivity
  - PERSONA-011 (Prof. Weber): sensory/environmental adaptation
  - PERSONA-012 (Dr. Turan): time-to-capture, data density
  - PERSONA-013 (Nina): motor constraints, cognitive load, data density
  - PERSONA-014 (Jana): motor constraints, cognitive load, time-to-capture, emotional sensitivity
  - PERSONA-015 (Lena): light constraints (confirmed from persona file: bedside lamp constraint)

### AC-05: doc/ presentation guidelines include persona-awareness section
- [ ] Document is located at `doc/presentation/design/persona_design_bridge.md`
- [ ] File uses `persona_` naming prefix per design/ README naming conventions
- [ ] design/ README already lists `persona_*.md` as allowed content type

### AC-06: Validation checklist exists for verifying design serves user needs
- [ ] Section 8 (Design Review Checklist) contains both lists
- [ ] AI-verifiable checks are clearly separated from human-review-required checks
- [ ] At least 6 AI-verifiable items and 6 human-review items

### AC-07: Human-in-the-loop decision points documented
- [ ] Section 6 includes the 8 decision types requiring human judgment
- [ ] Review gates (before/during/after) are listed
- [ ] AI behavior (flag and pause) is specified
- [ ] Role division is explicit (craftsperson vs architect metaphor)

### AC-08: Two-stream rule creation workflow documented
- [ ] Section 2 contains both Stream 1 and Stream 2 with numbered steps
- [ ] Provenance markers defined for both streams
- [ ] CODIFY/DOCUMENT steps include token reference requirement
- [ ] Critical principle stated: both streams must ground in personas

### AC-10: Rule generality tiers documented with classification signals and promotion workflow
- [ ] Section 4 includes T1/T2/T3 overview table
- [ ] Classification signals table exists
- [ ] Uncertain case flagging behavior specified
- [ ] Promotion workflow documented (T3 → T2 → T1, never demoted)

### AC-11: Rule precedence logic documented
- [ ] Section 4 "Rule Precedence" subsection exists
- [ ] CSS specificity analogy stated
- [ ] The four precedence situations in table format
- [ ] AI behavior for detected contradictions specified

### AC-12: Design Decision Record (DDR) format defined
- [ ] Section 7 contains DDR template in code fence
- [ ] All required DDR fields present: Conflict, Decision, Reason, Decided by, Date, Tier, Affected screens, Mitigations
- [ ] Storage-by-tier table specifies where T1/T2/T3 DDRs live
- [ ] Worked DDR example included (density by role)

### Additional quality checks:
- [ ] No token values are defined in the document (only token names referenced)
- [ ] `component.button.crisisMinHeight` token flagged as MISSING in Example 1
- [ ] All 7 examples from REQ-PROC-026 section 4.3 are present
- [ ] Document does not contain requirements (no acceptance criteria, no YAML frontmatter for requirements)
- [ ] No `///` Dart-style WHY comments (this is a doc/ file, not lib/ code)
- [ ] Section headings make the document navigable via Grep/anchor links

---

## Risks and Mitigations

**Risk 1: Document becomes too long for agents to read efficiently**

The requirements are rich — naive transcription would produce a 1500+ line file.

Mitigation: Tables replace prose everywhere possible. Each section must earn its
place — if a subsection is already clearly covered by a table in a previous
section, do not repeat it. The "Architectural Context" section (5) is the most
at risk — keep the token reference chain as a code fence diagram, not prose.

**Risk 2: PERSONA-IDs are wrong or inconsistent**

The exploration protocol used IDs from memory; persona files must be the
authoritative source.

Mitigation: IDs confirmed from persona files during this planning phase:
- PERSONA-001: Dr. Sarah, PERSONA-002: Max, PERSONA-005: Lisa,
  PERSONA-006: Michael, PERSONA-007: Hanna, PERSONA-008: David,
  PERSONA-009: Elias, PERSONA-010: Sophie, PERSONA-011: Prof. Weber,
  PERSONA-012: Dr. Turan, PERSONA-013: Nina, PERSONA-014: Jana,
  PERSONA-015: Lena

Note: PERSONA-003 is system_maintenance and PERSONA-004 is app_provider —
neither is design-relevant. The exploration protocol noted 13 design-relevant
personas, which matches the 13 in the requirements frontmatter. Confirmed.

**Risk 3: Token references are stale or fabricated**

If the document references tokens that do not exist, agents will fail when
trying to use them.

Mitigation: Only reference tokens verified to exist in tokens.json. Flag any
needed-but-missing tokens explicitly (e.g., `component.button.crisisMinHeight`
noted as MISSING). The implementation engineer must verify each token reference
against the actual tokens.json before writing the document.

**Risk 4: Overlap with future T1/T2 rule files creates duplication**

TASK-PROC-026-07 will create individual `t1_*.md` files for each system-level
rule. If the bridge document and the individual rule files duplicate content,
agents get confused about which is authoritative.

Mitigation: This document is the INDEX and METHODOLOGY reference. Individual
`t1_*.md` and `t2_*.md` files (T6 task) are the RULE DETAILS. The bridge
document should reference those files by name once they exist, not restate all
rules verbatim. For now (before T6), the examples in Section 3 serve as
illustration — they will not be extracted into separate files by this task.

---

## Files to Create / Modify

**This task creates exactly 1 file**:
- `doc/presentation/design/persona_design_bridge.md` (new file)

**This task modifies 0 files**:
- The design/ README already lists `persona_*.md` as allowed — no update needed.
- No other doc/ files need modification.

**Token flag** (action for implementation engineer, not a file modification by
this task):
- Verify `ComponentTokens.buttonMinHeight` = 48.0 exists (confirmed from
  memory/token_system.md context — double-check against tokens.json)
- Flag `component.button.crisisMinHeight` as MISSING in Example 1's CODIFY row
  (this will be created by the T6 task or whichever task implements crisis
  mode touch targets)

---

## Log

- **Date**: 2026-03-01
- **Agent ID**: architecture-advisor-sonnet-4-6-2026-03-01
- **Status**: Plan complete, awaiting user review and approval
- **Files read**: goal.md, requirements.md (full), 2026-02-07_01_opus_plan.md,
  2026-02-07_02_protocol_exploration.md, doc/presentation/design/README.md,
  doc/presentation/README.md, doc/presentation/coding/button_guidelines.md,
  doc/presentation/tokens/token_system.md, all 13 design-relevant persona files
- **Next action**: Implementation engineer reads this plan + goal.md + relevant
  doc/ files, then creates persona_design_bridge.md in the implementation order
  defined above (Step 1 through Step 10)
