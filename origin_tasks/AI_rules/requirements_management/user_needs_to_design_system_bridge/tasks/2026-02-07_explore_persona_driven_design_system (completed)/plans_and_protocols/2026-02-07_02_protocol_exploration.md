# Exploration Protocol: Persona-Driven Design System Bridge

**Date**: 2026-02-07
**Task**: TASK-PROC-026-01
**Agent**: Opus (claude-switch-opus skill, invoked from requ-explore workflow)

## What was done

### Phase 1: Investigation (Sonnet gathered, Opus analyzed)

**Documentation read:**
- `doc/architecture.md` — understood layer separation, DI patterns
- `doc/presentation.md` (first 500 lines) — accessibility guidelines, semantic widgets, responsive patterns, state management
- `requirements_user_needs/README.md` — index of 16 README chapters
- `requirements_user_needs/README_8_CROSS-REFERENCING_SYSTEMS.md` — bidirectional traceability system
- `requirements_user_needs/README_13_CROSS_REFERENCE_NOTATION.md` — notation format, YAML integration for epics/features

**All 13 personas read:**
- PERSONA-001: Dr. Sarah (Therapist, VT, protocol-driven)
- PERSONA-002: Max (Client, depression, overwhelmed)
- PERSONA-005: Lisa (Self-user, waitlist bridger, privacy-conscious)
- PERSONA-006: Michael (Self-user, high-performer, therapy-averse)
- PERSONA-007: Hanna (Self-user, sleepless, dark room constraint)
- PERSONA-008: David (Self-user, ADHD structure seeker)
- PERSONA-009: Elias (Client, social phobia, discrete needs)
- PERSONA-010: Sophie (Client, ADHD structure seeker, therapy-guided)
- PERSONA-011: Prof. Dr. Weber (Therapist, analog depth explorer)
- PERSONA-012: Dr. med. Turan (Therapist, rapid monitor, high-volume)
- PERSONA-013: Nina (Self-user, Long-COVID energy budgeter)
- PERSONA-014: Jana (Client, BPD, crisis-mode usage)
- System Maintenance persona (not design-relevant)

**Design system requirements read:**
- REQ-NFUNC-002 (Accessibility) — 48dp targets, WCAG AA, Simple Mode
- REQ-NFUNC-009 (Loading/Error) — timing rules, retry, confirmation dialogs
- REQ-NFUNC-013 (UX Writing) — tone, error patterns, sensitive context
- Full list of 13 design system requirement files identified via glob

**Skills analyzed:**
- `code-simple/skill.md` — no persona-reading step exists
- `code-complex/` — identified as needing persona-awareness step

### Phase 2: Analysis

**Key finding**: Two strong pillars (User Needs, Design System) that never connect.

**7 design-relevant trait categories identified** across all personas:
1. Motor constraints
2. Cognitive load budget
3. Time-to-capture window
4. Environmental light constraints
5. Privacy/discreteness requirements
6. Emotional sensitivity to UI patterns
7. Sensory/environmental adaptation
8. Data density tolerance (added during analysis — Dr. Turan vs Max spectrum)

**5 concrete persona→design-rule mappings created** as examples of the methodology:
1. Jana's tremors → 64dp crisis-mode touch targets
2. Hanna's darkness → OLED-true-black dark theme
3. David's 3s window → ≤3-interaction capture flows
4. Max's blank-field paralysis → pre-filled scaffolding rule
5. Elias's discreteness → non-clinical app identity

### Phase 3: Requirements Document

**Created**: `requirements_tasks/process/AI_rules/requirements_management/user_needs_to_design_system_bridge/requirements.md`
- ID: REQ-PROC-026
- Contains: methodology, trait framework, concrete examples, files-to-modify list, validation approach, **human-in-the-loop section**
- 7 acceptance criteria defined

**User feedback incorporated** (2026-02-07):

**Iteration 1: Human-in-the-Loop**
- Added section 4.5 "Human-in-the-Loop: What AI Cannot Decide"
- Documented 8 decision types requiring human judgment (brand personality, flow continuity, tone/culture, trade-offs, edge cases, visual hierarchy, innovation, semantic accessibility)
- Updated validation checklist to separate AI-verifiable vs. human-review-required checks
- Added human review gates (before/during/after implementation decision points)
- Research basis: Nielsen Norman Group findings on AI design limitations (AI produces "average of the internet")

**Iteration 2: Two-Stream Rule Creation**
- Identified critical gap: humans often have UX ideas upfront but no way to validate them proactively
- Added section 4.2 "Two Streams for Rule Creation":
  - **Stream 1 (AI-derived)**: Bottom-up extraction from personas (existing methodology)
  - **Stream 2 (Human-defined)**: Top-down proposals validated against personas (NEW)
- Added section 4.6 "Validating Human-Defined UX Rules"
- Designed new `ux-validate-rule` skill workflow:
  - Takes human UX proposal as input
  - Identifies relevant personas
  - Checks alignment (SUPPORTS/NEUTRAL/CONFLICTS)
  - Generates validation report with recommendation
  - Documents approved rules with provenance marker
- Added 2 new acceptance criteria (AC-08, AC-09)
- Updated "What is missing" gap analysis
- Rationale: Prevents wasted implementation cycles, captures human expertise proactively, maintains persona-grounding for all rules

**Iteration 3: Rule Generality Tiers**
- Identified the "how generic is this rule?" dimension: Material Design gives generic rules, some decisions apply to all screens, some to recurring patterns, some only to one screen
- Added section 4.4 "Rule Generality Tiers" with three levels:
  - **T1 (System-Level)**: Extends/overrides Material Design for ALL screens (e.g., 48dp targets, OLED dark mode)
  - **T2 (Pattern-Level)**: Recurring pattern across multiple screens (e.g., delete button placement, master-detail navigation)
  - **T3 (Screen-Specific)**: One-off decisions for a single screen (e.g., plan preview button)
- **AI classifies tier, human confirms** — with signals table for classification and uncertainty flagging
- Added **promotion workflow**: T3 → T2 → T1 when patterns recur (never demote)
- Updated section 4.5 "Where Design-as-Code Rules Live" to include tier-based storage:
  - T1/T2: `doc/` and design system requirements (globally visible)
  - T3: Feature-level docs only (no global pollution)
- Updated all 5 concrete examples with tier annotations
- Added 2 new examples: T2 (delete button placement) and T3 (plan preview button)
- Updated CODIFY step in both streams to include tier classification
- Updated ux-validate-rule workflow to include tier proposal
- New acceptance criterion (AC-10)

**Iteration 4: Rule Precedence, Conflict Resolution, Subfolder Structure, Retroactive Classification**

User feedback: (1) Need rule precedence logic, (2) Need standardized format for persona conflict resolution with tier-based documentation, (3) Multiple implementation tasks needed, (4) doc/presentation/ needs subfolders to separate coding conventions from design rules, plus file naming conventions.

Changes:
- Added **Rule Precedence** to section 4.4: T3 overrides T2 overrides T1 within scope (CSS specificity analogy). T2 cannot weaken T1 globally.
- Added section 4.8 **Resolving Persona Conflicts**: Standardized **Design Decision Record (DDR)** format with conflict/decision/reason/tier/mitigations fields. DDRs stored at tier-appropriate locations (`doc/presentation/design/ddr_*.md` for T1/T2, feature docs for T3).
- Replaced section 6 with **Implementation Roadmap**: 7 tasks (T0-T6) with dependencies, from merge script removal through retroactive annotation. Detailed table mapping existing requirements to personas and tiers.
- Added **subfolder structure** for `doc/presentation/`: `coding/` (existing technical files), `design/` (new persona-derived rules, DDRs), `navigation/`, `platform/`, `tokens/`, `accessibility/`, `libs/`
- Added **file naming conventions**: `t1_`, `t2_`, `ddr_`, `persona_` prefixes for design rules
- Created TASK-PROC-027-01 for doc merge script removal (prerequisite)
- 6 new acceptance criteria (AC-11 through AC-15), total now 15
- Updated dependencies to include TASK-PROC-027-01 as prerequisite

**Iteration 5: Subfolder READMEs**

User feedback: Every subfolder in `doc/presentation/` must have a README.md defining what kind of content is allowed in that folder.

Changes:
- Added `README.md` to every subfolder in the structure diagram (section 4.5)
- Added **"Subfolder README Requirements"** subsection defining the 4 mandatory sections: Purpose, Allowed content, Forbidden content, Naming conventions
- Added AC-16: "Every doc/presentation/ subfolder has a README.md defining allowed content, forbidden content, and naming conventions"
- Updated implementation roadmap task T1 to include README creation
- Total acceptance criteria: 16

**Iteration 6: Architectural Context — doc/ vs requirements vs tokens**

User feedback: Design rule files in doc/presentation/design/ must be actionable guidelines (not requirements). They should reference tokens in lib/config/theme/, not redefine values. Need to clarify how this relates to the existing feature flow (persona → scenario → user flow → feature → task) and the rule that implementation agents read doc/ always but don't browse requirements_tasks/.

Changes:
- Added **section 4.0 "Architectural Context"** to requirements with three subsections:
  - "The Three Layers and Their Audiences" — doc/ (agent reads always), requirements (task planning), tokens (coded values)
  - "How Design Rules Relate to Tokens" — WHAT + HOW + WHY pattern, reference not redefine
  - "How This Relates to the Regular Feature Flow" — T1/T2 cross-cutting in doc/ vs T3 feature-specific in tasks
- Updated **CODIFY step** in Stream 1 and **DOCUMENT step** in Stream 2 to include token references
- Updated **Example 1** (touch targets) with token references
- Updated **section 4.5** storage table to clarify content format and agent reading patterns
- Updated **design/ folder** comment from "WHAT to build" to "Actionable design guidelines with persona justification (WHAT + HOW + WHY)"
- Updated **section 7** with "Relationship to the Regular Feature Flow" showing boundary between feature flow and persona-design bridge
- Updated **task files** T2, T4, T6 with architectural context sections explaining doc/ vs requirements distinction and token references

User decisions documented:
- Annotate ALL design system requirements immediately (clean start)
- AI flags and pauses for human approval (gain confidence first before switching to implementation-first)

## Artifacts created

1. `plans_and_protocols/2026-02-07_01_opus_plan.md` — Opus analysis plan
2. `plans_and_protocols/2026-02-07_02_protocol_exploration.md` — This protocol
3. `../requirements.md` — The REQ-PROC-026 requirements document (6 iterations of user feedback)
4. `../tasks/2026-02-08_impl_restructure_presentation_subfolders/goal.md` — TASK-PROC-026-02 (T1)
5. `../tasks/2026-02-08_impl_persona_design_bridge/goal.md` — TASK-PROC-026-03 (T2)
6. `../tasks/2026-02-08_impl_validate_ux_rule_skill/goal.md` — TASK-PROC-026-04 (T3)
7. `../tasks/2026-02-08_impl_update_implementation_skills/goal.md` — TASK-PROC-026-05 (T4)
8. `../tasks/2026-02-08_impl_retroactive_requirement_annotation/goal.md` — TASK-PROC-026-06 (T5)
9. `../tasks/2026-02-08_impl_extract_initial_design_rules/goal.md` — TASK-PROC-026-07 (T6)

**Final requirements document includes**:
- Architectural context: doc/ vs requirements vs tokens (WHAT + HOW + WHY pattern)
- 8 design-relevant trait categories
- Two-stream rule creation (AI-derived + human-defined) with token references in CODIFY/DOCUMENT steps
- Human-in-the-loop decision points (8 types requiring judgment), AI flags and pauses mode
- ux-validate-rule skill specification
- 7 concrete persona→design examples (with tier annotations and token references)
- Rule generality tiers (T1/T2/T3) with classification, promotion, and precedence
- Design Decision Records (DDRs) for persona conflict resolution
- doc/presentation/ subfolder structure with README requirements
- Relationship to regular feature flow (T1/T2 cross-cutting vs T3 feature-specific)
- Implementation roadmap (7 tasks T0-T6)
- Updated validation checklist (AI-verifiable + human-review-required)
- 16 acceptance criteria

## Next steps

- Complete-task skill to mark exploration as done
- Git commit all artifacts
  - **Create new `ux-validate-rule` skill** for Stream 2 workflow
  - Run doc merge to update `doc/presentation.md`

## Open questions for user

1. ~~Should the persona-design bridge live as a `doc/presentation/` source file (merged into presentation.md), or as a standalone `doc/persona_design_bridge.md`?~~ **RESOLVED**: Lives at `doc/presentation/design/persona_design_bridge.md` (decided during subfolder structure design, iteration 4).
2. How heavy should the skill modifications be? Options:
   - **Lightweight**: One-line "If implementing UI, check doc/presentation.md persona-design section" in existing skills
   - **Medium**: Dedicated step in skills that reads relevant personas based on the feature being implemented
   - **Heavy**: New skill/agent specifically for persona-aware design review
3. ~~Should we annotate ALL existing design system requirements immediately, or start with the 3 highest-impact ones (accessibility, UX writing, theming)?~~ **RESOLVED**: Annotate ALL immediately for a clean start (user decision, 2026-02-08).
4. ~~**Human review workflow**: How should human-in-the-loop reviews be triggered?~~ **RESOLVED**: Option A — AI flags decisions requiring human judgment and pauses for approval. User wants to first gain confidence that AI delivers good results before switching to implementation-first (user decision, 2026-02-08).
