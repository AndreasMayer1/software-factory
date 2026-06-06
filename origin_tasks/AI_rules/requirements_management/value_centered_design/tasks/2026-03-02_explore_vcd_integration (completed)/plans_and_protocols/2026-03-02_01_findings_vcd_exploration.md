# Findings: Value Centered Design Integration Exploration

- **Task**: TASK-PROC-033-01
- **Date**: 2026-03-02
- **Author**: Opus (claude-opus-4-6)
- **Status**: Complete — pending user review

---

## Executive Summary

1. **Methodology chosen**: Literature-backed hybrid using Schwartz Value Theory + Beauchamp-Childress Medical Ethics + Nissenbaum Contextual Integrity, filtered for design relevance. AI derives values from existing persona documentation; results tagged `literature_derived` (distinct from `grounded` for app_provider).
2. **Value Trade-off Records**: Mandatory only when a design decision causes one persona's primary or secondary value to be degraded in favor of another's. Small, single-persona decisions do NOT trigger a record. Records live inline in the artifact where the decision is made.
3. **Standalone "Value Principles" document**: NOT needed. The aggregation script (AC-08) replaces it entirely by generating a read-only summary from inline records.
4. **Skills to adapt**: 5 skills need changes — `ux-validate-rule`, `ux-create-flow`, `code-complex`, `code-simple`, and `requ-explore`. Changes are lightweight: a single checklist step per skill, not a restructuring.
5. **Aggregation script**: Parses a YAML metadata block embedded in each Value Trade-off Record. Output lives in `requirements_user_needs/_meta/value_tradeoff_summary.md`.
6. **VCD activation**: Forward-only. Activation date recorded in `requirements.md` for REQ-PROC-033 and in the persona design bridge document.
7. **Persona scope confirmed**: 14 personas included (10 client/self-user + 3 therapist + app_provider). `system_maintenance` excluded. All 14 benefit from value fields.

---

## Q1: Persona Value Sources — Methodology & Risk Assessment

### Can an AI meaningfully define persona values for therapeutic app users?

**Yes, with explicit methodological boundaries.**

The distinction is critical:

| What AI CAN do | What AI CANNOT do |
|---|---|
| Map documented persona behaviors, fears, barriers, and anti-traits to established value frameworks via logical deduction | Conduct empirical value research with real humans |
| Identify design-relevant value conflicts between personas | Claim certainty about what real therapy clients truly value |
| Apply the Design-Relevance Filter to exclude values with no design impact | Replace user research if it ever becomes available |

This is exactly what Value Sensitive Design (Friedman, University of Washington) prescribes for the conceptual investigation phase: derive values from documented stakeholder attributes using established frameworks, then validate iteratively.

### Scientific Framework: Three Pillars

**Pillar 1: Schwartz Theory of Basic Human Values**
The most empirically validated cross-cultural value model (Schwartz Value Survey, 70+ countries). Provides a circular motivational continuum of 10 value types:

- Self-Direction (autonomy, freedom, creativity)
- Stimulation (novelty, excitement)
- Hedonism (pleasure, self-gratification)
- Achievement (success, competence, influence)
- Power (authority, status, wealth)
- Security (safety, stability, order)
- Conformity (compliance with social norms)
- Tradition (respect for customs)
- Benevolence (care for close others)
- Universalism (concern for all, social justice)

**Relevance**: Schwartz values map directly to persona motivations. Michael's "Achievement" drives his dashboard-mental-model. Elias's "Security" drives his privacy obsession. Max's need for "Benevolence" (from therapist) drives his "good patient" identity.

**Pillar 2: Beauchamp & Childress — Principles of Biomedical Ethics**
Four principles that govern medical/therapeutic contexts:

- **Autonomy**: Respect for the patient's right to self-determination
- **Beneficence**: Acting in the patient's best interest
- **Non-maleficence**: "First, do no harm"
- **Justice**: Fair distribution of benefits and burdens

**Relevance**: The app operates in a therapeutic context. Every design decision implicates at least one of these principles. The app_provider's decision hierarchy (wellbeing > privacy > ethical integrity) is a direct operationalization of Beauchamp-Childress.

**Pillar 3: Nissenbaum — Contextual Integrity**
Information flows are ethical when they conform to the norms of the context in which they were collected. Data shared in a therapeutic context must not flow into insurance, employment, or social contexts.

**Relevance**: This is the theoretical foundation for the entire local-first, no-cloud architecture. Elias's, Michael's, and Lisa's privacy fears are instances of contextual integrity violations they anticipate and guard against.

### The Design-Relevance Filter

Not all values matter for design. We apply a filter:

**A value is design-relevant if and only if**:
1. It can be supported OR degraded by a concrete UI/UX/architecture decision, AND
2. It creates a tension with at least one other persona's design-relevant value, OR
3. It imposes a non-obvious constraint on feature design that a developer would not assume by default

**Examples of design-relevant values**: Privacy (affects architecture), Simplicity (affects UI complexity), Autonomy (affects notification design), Efficiency (affects data density).

**Examples of non-design-relevant values**: Tradition, Stimulation, Hedonism — these do not meaningfully constrain or conflict in this app's design space.

### Recommended Persona Value Structure

For each persona's YAML frontmatter, add:

```yaml
vcd:
  evidence_method: literature_derived  # or "grounded" for app_provider
  primary_value:
    name: "Contextual Integrity"
    framework: "Nissenbaum"
    design_relevance: "Drives camouflage UI, local-only architecture, no-cloud constraint"
  secondary_values:
    - name: "Autonomy"
      framework: "Schwartz / Beauchamp-Childress"
      design_relevance: "User must control what is visible, exportable, deletable"
    - name: "Security"
      framework: "Schwartz"
      design_relevance: "App must resist shoulder-surfing, intimate intrusion, data leakage"
    - name: "Predictability"
      framework: "Schwartz (Security sub-dimension)"
      design_relevance: "No surprise behaviors, no unexpected data exposure"
  value_conflicts:
    - tension: "Contextual Integrity vs. Therapeutic Utility"
      description: "Elias needs maximum camouflage, but therapy homework requires clear, fast data entry. Camouflage constraints degrade usability."
      opposing_personas: ["PERSONA-010"]  # Sophie needs ease-of-use
```

### Evidence Tagging

| Tag | Meaning | When to use |
|---|---|---|
| `grounded` | Values confirmed directly by the person the persona represents | app_provider only (currently) |
| `literature_derived` | Values logically deduced from persona documentation using Schwartz + Beauchamp-Childress + Nissenbaum frameworks | All client, self-user, and therapist personas |
| `user_confirmed` | Values validated through direct user research | Future: when real user research becomes available |

**Rule**: When real user research validates or contradicts a `literature_derived` value, the tag upgrades to `user_confirmed` or the value is revised. The `literature_derived` tag is NOT a weakness marker — it signals methodological transparency.

### Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| **Values are wrong**: AI-derived values don't match what real users would report | Medium | (1) Ground in established frameworks, not intuition. (2) Tag transparently. (3) Design features to degrade gracefully if values turn out wrong. (4) Upgrade to `user_confirmed` when research becomes available. |
| **Values are too generic**: Schwartz values are so broad they don't discriminate between personas | Low | The Design-Relevance Filter prevents this. We only include values that cause concrete design differences. "Security" for Elias means camouflage UI; "Security" for Dr. Turan means clinical data accuracy — same word, different design implications. |
| **False conflicts**: AI identifies a value conflict that wouldn't exist in practice | Low | The "AI flags and pauses" workflow means no conflict is auto-resolved. The user decides. False conflicts are caught at decision time. |
| **Missing values**: AI fails to identify a value that matters | Medium | Mitigated by using three complementary frameworks (Schwartz covers motivation, Beauchamp-Childress covers medical ethics, Nissenbaum covers information flow). Gaps are more likely in niche areas — flag and revisit when new persona insights emerge. |
| **Projection bias**: AI projects its training data's value assumptions onto vulnerable populations | Medium | (1) Always cite framework source, never "common sense." (2) User reviews all value assignments before they become active. (3) Evidence tag system makes methodology transparent. |

### Preliminary Value Mapping (Overview)

Based on the full persona analysis, here is the initial value landscape. This is a preview — the actual value fields will be written during the implementation task.

| Persona | Primary Value | Key Secondary Values | Central Design Tension |
|---|---|---|---|
| **Max** (PERSONA-002) | Non-maleficence (shame-free design) | Simplicity, Benevolence (therapeutic alliance) | Shame avoidance vs. data completeness |
| **Lisa** (PERSONA-005) | Autonomy (self-directed preparation) | Security (career protection), Benevolence (self-care) | Need for guidance vs. no therapist to provide it |
| **Michael** (PERSONA-006) | Achievement (performance optimization) | Autonomy (self-management), Security (career privacy) | Data depth vs. anti-therapy identity |
| **Hanna** (PERSONA-007) | Non-maleficence (no light, no noise) | Autonomy (self-management), Security (partner privacy) | Externalization need vs. environmental constraints |
| **David** (PERSONA-008) | Autonomy (self-built system) | Stimulation (novelty/dopamine), Non-maleficence (shame-free) | Need for structure vs. novelty addiction |
| **Elias** (PERSONA-009) | Contextual Integrity (privacy) | Autonomy, Security, Predictability | Camouflage vs. therapeutic utility |
| **Sophie** (PERSONA-010) | Beneficence (external scaffolding) | Simplicity, Non-maleficence (shame-free) | Ease-of-use vs. data richness |
| **Prof. Weber** (PERSONA-011) | Beneficence (therapeutic depth) | Autonomy (analog sanctity), Non-maleficence | Narrative richness vs. digital reduction |
| **Dr. Turan** (PERSONA-012) | Beneficence (patient safety) | Efficiency (time optimization), Justice (evidence-based) | Speed vs. depth of patient data |
| **Nina** (PERSONA-013) | Autonomy (self-management of illness) | Security (energy conservation), Non-maleficence | Tracking need vs. tracking-as-energy-drain |
| **Jana** (PERSONA-014) | Non-maleficence (crisis safety) | Autonomy (uncensored expression), Beneficence | Emotional capture accuracy vs. crisis accessibility |
| **Dr. Sarah** (PERSONA-001) | Beneficence (patient progress) | Efficiency, Justice (evidence-based) | Structured data vs. patient compliance burden |
| **Lena** (PERSONA-015b) | Autonomy (meaning-making) | Beneficence (continuing bonds), Non-maleficence | Narrative depth vs. searchability/structure |
| **app_provider** (PERSONA-015) | Beneficence (user wellbeing) | Contextual Integrity (privacy), Justice (ethical integrity) | Feature richness vs. solo-dev sustainability |

### Key Conflict Axes (Value Matrix)

The Gemini analysis proposed two axes. Based on the full persona set, three axes better capture the design space:

**Axis 1: Privacy/Camouflage ←→ Utility/Transparency**
- Extreme privacy: Elias, Michael
- Extreme utility: Dr. Turan, Sophie
- Balanced: Max, Lisa, Dr. Sarah

**Axis 2: Autonomy/Self-Direction ←→ Guidance/External Structure**
- Extreme autonomy: Michael, David, Nina
- Extreme guidance: Max, Sophie
- Balanced: Jana (needs both crisis guidance AND autonomous expression)

**Axis 3: Depth/Narrative ←→ Speed/Efficiency**
- Extreme depth: Lena, Prof. Weber
- Extreme speed: Dr. Turan, Hanna (3 AM constraint)
- Balanced: Dr. Sarah (structured but not rushed)

**Coverage assessment**: All quadrants of all three axes are populated. No new persona is needed to represent a missing value combination. Gemini's prediction confirmed.

---

## Q2: Value Trade-off Record — Scope & Triggers

### When is a Value Trade-off Record mandatory?

**Trigger rule**: A Value Trade-off Record is MANDATORY when ALL of the following are true:

1. A design decision exists (conscious choice between alternatives)
2. At least two personas have conflicting values relevant to the decision
3. The decision degrades at least one persona's primary or secondary value to favor another's

**Trigger examples**:
- Notification design: Sophie (needs reminders) vs. Michael (notifications = exposure risk) → RECORD
- Data entry complexity: Dr. Turan (needs rich data) vs. Max (overwhelmed by forms) → RECORD
- Dark mode default: Hanna (mandatory dark at night) vs. Dr. Sarah (clinical readability) → RECORD

### What is "too small" for a record?

**No record needed when**:
- The decision affects only one persona and no others are degraded
- The decision is purely technical with no value implications (e.g., "use ListView vs. Column")
- The decision follows an existing design rule that already has a trade-off record
- The decision is a straightforward application of the app_provider's decision hierarchy with no real tension

**Examples NOT requiring a record**:
- "Use local storage" — this follows the app_provider's privacy principle, no persona opposes it
- "Add a back button" — standard UX, no value tension
- "Sort entries by date" — default behavior, no conflict

### Inline vs. separate file?

**Decision: Inline, in the artifact where the decision is made.**

Rationale:
- Trade-off records are contextual — they make sense where the decision lives
- User flows, requirements, and design rule files are the natural homes
- A separate log file would create a maintenance burden and become a disconnected archive
- The aggregation script (AC-08) renders the separate-file approach unnecessary — it collects inline records automatically

**Location rules**:
- In **user flows**: Under a `## Value Trade-offs` section at the bottom
- In **requirements**: Under a `## Value Trade-offs` section or inline within the relevant acceptance criterion
- In **design rule files** (`doc/presentation/design/t*.md`): Under `## Value Trade-offs` section
- In **code**: Via WHY comment referencing the trade-off in the requirement/flow file (code itself does NOT contain the full record)

### How do code-level decisions reference back?

Code-level design decisions that involve value trade-offs should:

1. Add a WHY comment in code referencing the requirement or flow where the trade-off is documented:
   ```dart
   /// Why: Notification timing is 4h minimum (not adaptive) because Sophie needs
   /// consistent reminders while Michael's privacy requires predictable behavior.
   /// Source: requirements_tasks/.../requirements.md#value-trade-off-notification-timing
   ```
2. The actual Value Trade-off Record lives in the requirement, NOT in the code
3. This avoids bloating code with full trade-off documentation while maintaining traceability

---

## Q3: Standalone "Value Principles as Design Constraints" Document

### Decision: NOT needed.

**Justification**:

1. **Maintenance cost is prohibitive**: A standalone document requires manual updates whenever persona values change, new trade-offs are recorded, or design rules evolve. In a solo-dev project, this is unsustainable.

2. **AI agents can read values directly**: The persona files with their `vcd:` YAML blocks are machine-readable. Any skill that needs persona values reads them from the source — no intermediate document needed.

3. **The aggregation script replaces it**: AC-08's script generates a read-only summary of all value trade-off records. This provides the "at-a-glance" overview that a standalone doc would offer, but auto-generated and always current.

4. **User preference aligns**: The product owner explicitly prefers the aggregation approach over a static document.

**What the aggregation script output provides instead**:
- List of all personas with their primary/secondary values (extracted from persona YAML)
- List of all recorded value trade-offs (extracted from inline records across all artifacts)
- Conflict frequency matrix (which persona pairs conflict most often)
- Unresolved tensions (trade-offs flagged but not yet decided)

This is strictly superior to a manually maintained document.

---

## Q4: Skills Adaptation

### Skills requiring changes

| Skill | Change Description | Overhead Impact |
|---|---|---|
| **ux-validate-rule** | Add step between current steps 4 and 5: "Extract persona values from `vcd:` YAML block. Check if proposal creates a value conflict between personas. If YES, flag for Value Trade-off Record." | Minimal — one additional check in an already-thorough validation |
| **ux-create-flow** | Add to analysis phase (Step 3a): "For multi-persona flows, identify value conflicts between serving personas. If conflicts exist, include a `## Value Trade-offs` section in the flow." | Minimal — extends existing analysis, doesn't add new phases |
| **code-complex** | Add to plan step (Step 2): "If plan involves Presentation Layer changes affecting multiple personas, architecture-advisor must check persona values and flag potential trade-offs." Add to quality step (Step 6): "Verify value trade-off records exist for decisions that degrade persona values." | Minimal — one line in planning prompt, one line in quality check |
| **code-simple** | Add a single guard: "If the change affects a feature used by personas with conflicting values (check `vcd:` YAML), flag for user review before proceeding." | Negligible — most simple tasks won't trigger this |
| **requ-explore** | Add to Phase 1.6 (Map User Needs): "For each persona served, read `vcd:` YAML block. Identify value conflicts between personas. Document in requirements under `## Value Trade-offs` section if conflicts exist." | Minimal — extends existing persona analysis |

### Skills NOT requiring changes

| Skill | Reason |
|---|---|
| `task-create` | Infrastructure skill — creates folder structure. No design decisions. |
| `task-complete` | Verification skill — checks completeness. No design decisions. |
| `claude-log` | Logging skill — records what happened. No design decisions. |
| `ui-create-sketch` | Sketch creation. Value awareness comes from the flow/requirement it implements, not the sketching skill itself. |
| `ux-create-persona` | Persona creation. Will need the `vcd:` YAML block added to the persona template, but this is a template change, not a skill logic change. |
| `ux-create-scenario` | Scenario creation. Scenarios describe user behavior, not design decisions. Value conflicts surface in flows, not scenarios. |

### What "consult persona values" looks like in practice

A single checklist step added to the skill's workflow:

```
**VCD Check**: Read `vcd:` YAML from persona files involved in this decision.
- Do any primary/secondary values conflict?
- If YES → Document in a Value Trade-off Record (inline in this artifact).
- If the conflict cannot be resolved without user input → PAUSE and present options to user.
```

This is 3-4 lines of skill text per skill. It does NOT restructure any skill's workflow.

---

## Q5: Aggregation Script (AC-08)

### Parseable format for Value Trade-off Records

Each inline Value Trade-off Record must include a YAML metadata block that the script can parse. The block is fenced with HTML comments to remain invisible in rendered markdown:

```markdown
### Value Trade-off: [Short Title]

<!-- vcd-record
id: VTR-[sequential-number]
date: 2026-03-15
artifact: requirements_tasks/functional/.../requirements.md
personas:
  - id: PERSONA-009
    value: Contextual Integrity
    impact: degraded
  - id: PERSONA-010
    value: Simplicity
    impact: supported
decision_status: decided  # or "open" for unresolved
-->

- **Problem**: [What conflict or tension exists?]
- **Personas & Values**: [Which personas, which values are in tension?]
- **Options Considered**: [What alternatives were evaluated?]
- **Decision**: [What was decided?]
- **Rationale**: [Why this decision over alternatives?]
- **Consequences**: [What trade-offs does this decision accept?]
```

### Script behavior

The script:
1. Recursively scans `requirements_user_needs/`, `requirements_tasks/`, and `doc/presentation/design/` for `<!-- vcd-record` blocks
2. Parses the YAML within each block
3. Generates an aggregated summary file

### Output file location

`requirements_user_needs/_meta/value_tradeoff_summary.md`

This location:
- Lives alongside the existing `id_registry.md` in the meta folder
- Is clearly a generated artifact (read-only)
- Is accessible to all skills that read `requirements_user_needs/`

### What the output enables

1. **Audit trail**: Complete list of every value trade-off decision, sorted by date
2. **Conflict frequency matrix**: Which persona pairs conflict most often (reveals systemic design tensions)
3. **Open items**: Trade-offs flagged but not yet decided (`decision_status: open`)
4. **Value impact summary**: Per persona, how many times each value was supported vs. degraded (reveals if a persona is consistently losing)
5. **Pattern detection**: Recurring conflicts may suggest missing design rules or architectural changes

### Script invocation

```bash
python scripts/aggregate_value_tradeoffs.py
```

Output is regenerated on demand (not automatically on every commit — that would add CI complexity inappropriate for a solo-dev project).

---

## Q6: VCD Activation Scope

### Decision: Forward-only.

**Rationale**:
- Retroactive application would require reviewing every past design decision, user flow, and requirement — an enormous effort with diminishing returns
- Past decisions were made in good faith with the information available; re-litigating them creates churn without proportional benefit
- Going forward, all new design decisions naturally go through the VCD-aware workflow

### Activation date

**Date**: The date the first implementation task of REQ-PROC-033 is completed (persona value fields populated).

**Where to record**:
1. In `requirements_tasks/process/AI_rules/requirements_management/value_centered_design/requirements.md` — add a `vcd_activation_date` field to the YAML frontmatter
2. In `doc/presentation/design/persona_design_bridge.md` — add a note at the top: "VCD active since [date]. All design decisions after this date must check persona values for conflicts."

### What "forward-only" means in practice

- **New user flows**: Must include `## Value Trade-offs` section if multi-persona conflicts exist
- **New design rules**: Must include persona value justification (already required by REQ-PROC-026)
- **New requirements**: Must check persona values during exploration (requ-explore update)
- **Existing artifacts**: NOT retroactively updated. If an existing flow is revised for other reasons, the revision should add value awareness opportunistically.

---

## Q7: Persona Count & Scope Confirmation

### Included personas (14 total)

| # | Persona ID | Name | Role | VCD applicable? |
|---|---|---|---|---|
| 1 | PERSONA-001 | Dr. Sarah | therapist | YES |
| 2 | PERSONA-002 | Max | client | YES |
| 3 | PERSONA-005 | Lisa | self_user | YES |
| 4 | PERSONA-006 | Michael | self_user | YES |
| 5 | PERSONA-007 | Hanna | self_user | YES |
| 6 | PERSONA-008 | David | self_user | YES |
| 7 | PERSONA-009 | Elias | client | YES |
| 8 | PERSONA-010 | Sophie | client | YES |
| 9 | PERSONA-011 | Prof. Dr. Weber | therapist | YES |
| 10 | PERSONA-012 | Dr. med. Turan | therapist | YES |
| 11 | PERSONA-013 | Nina | self_user | YES |
| 12 | PERSONA-014 | Jana | client | YES |
| 13 | PERSONA-015 | app_provider | system | YES (grounded) |
| 14 | PERSONA-015b | Lena | client | YES |

### Excluded

| Persona ID | Name | Role | Reason |
|---|---|---|---|
| PERSONA-004 | system_maintenance | system | Technical infrastructure persona. Has no human values — represents system constraints (battery, storage, compatibility). Values are not applicable. |

### Edge cases

- **app_provider**: Included but with `evidence_method: grounded`. Values are already extensively documented in the persona file's "Decision-Making Principles" section. The VCD `vcd:` block will formalize what's already there.
- **Self-user personas** (Michael, Hanna, David, Lisa, Nina): These personas have no therapist. Their value conflicts are primarily internal (want help vs. refuse to seek it) or between themselves and the app's design. VCD is still valuable — it surfaces tensions between self-user needs and client/therapist-oriented features.
- **Lena**: Her persona_id in the files is listed as PERSONA-015 but this conflicts with app_provider's PERSONA-015. This should be corrected during implementation — Lena should have a unique ID. (For this document, I refer to her as PERSONA-015b pending correction.)

---

## Finalized Value Trade-off Record Format

This is the canonical format. All records must follow this structure exactly.

```markdown
### Value Trade-off: [Short Descriptive Title]

<!-- vcd-record
id: VTR-[NNN]
date: [YYYY-MM-DD]
artifact: [relative path to the file containing this record]
personas:
  - id: [PERSONA-NNN]
    value: [value name]
    impact: [supported | degraded | neutral]
  - id: [PERSONA-NNN]
    value: [value name]
    impact: [supported | degraded | neutral]
decision_status: [decided | open]
decided_by: [user | ai_recommended]
-->

- **Problem**: [What conflict or tension exists between persona values?]
- **Personas & Values**: [Which personas are affected? Which specific values are in tension?]
- **Options Considered**:
  1. [Option A]: [Brief description and which values it supports/degrades]
  2. [Option B]: [Brief description and which values it supports/degrades]
  3. [Option C]: [if applicable]
- **Decision**: [What was decided? Or "OPEN — awaiting user decision" if unresolved]
- **Rationale**: [Why this decision over alternatives? Reference to app_provider's decision hierarchy if applicable]
- **Consequences**: [What trade-offs does this decision accept? Which persona's values are degraded and how?]
```

### ID scheme

- Format: `VTR-[NNN]` (zero-padded, sequential)
- Registry: Tracked in `requirements_user_needs/_meta/id_registry.md` (extend existing registry)
- Script generates IDs: `python scripts/generate_id_registry.py --user-needs` should be extended to scan for `vcd-record` blocks

---

## Persona Value Fields Schema

### YAML frontmatter addition to persona files

```yaml
# Added to existing persona YAML frontmatter, after pcd: block
vcd:
  evidence_method: literature_derived  # grounded | literature_derived | user_confirmed
  framework_sources:
    - "Schwartz (2012) Basic Human Values"
    - "Beauchamp & Childress (2019) Principles of Biomedical Ethics"
  primary_value:
    name: "[Value Name]"
    framework: "[Which framework this maps to]"
    design_relevance: "[1-2 sentences: how this value constrains or drives design decisions]"
  secondary_values:
    - name: "[Value Name]"
      framework: "[Framework]"
      design_relevance: "[1-2 sentences]"
    - name: "[Value Name]"
      framework: "[Framework]"
      design_relevance: "[1-2 sentences]"
    - name: "[Value Name]"
      framework: "[Framework]"
      design_relevance: "[1-2 sentences]"
  value_conflicts:
    - tension: "[Value A] vs. [Value B]"
      description: "[2-3 sentences: what the tension is and when it manifests]"
      opposing_personas: ["PERSONA-NNN"]  # personas whose values create this tension
```

### Rules

- **Primary value**: Exactly ONE. The non-negotiable core value that, if violated, makes the persona abandon the app.
- **Secondary values**: Exactly THREE. Supporting values that shape behavior but can be traded against each other.
- **Value conflicts**: At least ONE. The most significant tension this persona experiences. Can list multiple if distinct.
- **framework_sources**: List frameworks used to derive values. Provides audit trail.
- **evidence_method**: Must be one of the three defined tags.

---

## Implementation Task Breakdown

The following tasks should be created to implement REQ-PROC-033. They are listed in dependency order.

### Task 1: Populate Persona Value Fields
- **Type**: impl
- **Name**: `impl_populate_persona_values`
- **Scope**: Add `vcd:` YAML block to all 14 personas (excluding system_maintenance)
- **Depends on**: This findings document (approved)
- **Effort**: M
- **Details**:
  - For each persona, derive primary value, 3 secondary values, and value conflicts using the three-pillar framework
  - Apply Design-Relevance Filter
  - Tag as `literature_derived` (except app_provider: `grounded`)
  - For app_provider: formalize the existing Decision-Making Principles as VCD values
  - User must review and approve each persona's values before proceeding
- **Acceptance criteria covered**: AC-01, AC-02, AC-09

### Task 2: Create Value Trade-off Record Template & Documentation
- **Type**: impl
- **Name**: `impl_vtr_template`
- **Scope**: Create the canonical VTR template, document the methodology, update requirements.md
- **Depends on**: Task 1
- **Effort**: S
- **Details**:
  - Create a template file at `requirements_user_needs/_meta/value_tradeoff_record_template.md`
  - Document the methodology in the VCD requirements.md (SEC-06)
  - Add `vcd_activation_date` to requirements.md YAML
  - Update `doc/presentation/design/persona_design_bridge.md` with VCD activation note
  - Fix Lena's duplicate PERSONA-015 ID
- **Acceptance criteria covered**: AC-03, AC-04, AC-09, AC-10

### Task 3: Adapt Skills for VCD Awareness
- **Type**: impl
- **Name**: `impl_adapt_skills_vcd`
- **Scope**: Update 5 skills with VCD checklist steps
- **Depends on**: Task 2
- **Effort**: S
- **Details**:
  - Add VCD check step to: `ux-validate-rule`, `ux-create-flow`, `code-complex`, `code-simple`, `requ-explore`
  - Each skill gets 3-5 lines added (no structural changes)
  - Update `ux-create-persona` template to include `vcd:` YAML block
- **Acceptance criteria covered**: AC-06

### Task 4: Create VCD Documentation Skill
- **Type**: impl
- **Name**: `impl_vcd_log_skill`
- **Scope**: Create a `vcd-log-tradeoff` skill that guides consistent trade-off documentation
- **Depends on**: Task 2
- **Effort**: S
- **Details**:
  - Skill reads persona values, identifies conflicting values, presents options to user
  - Generates a Value Trade-off Record in the correct format with YAML metadata block
  - Inserts the record inline in the specified artifact
  - Assigns the next VTR-NNN ID
- **Acceptance criteria covered**: AC-05, AC-07

### Task 5: Build Aggregation Script
- **Type**: impl
- **Name**: `impl_vcd_aggregation_script`
- **Scope**: Python script to aggregate all VTR records into a summary
- **Depends on**: Task 2 (needs at least one VTR record to test against)
- **Effort**: M
- **Details**:
  - Scan `requirements_user_needs/`, `requirements_tasks/`, `doc/presentation/design/` for `<!-- vcd-record` blocks
  - Parse YAML metadata
  - Generate `requirements_user_needs/_meta/value_tradeoff_summary.md`
  - Include: audit trail, conflict frequency matrix, open items, per-persona impact summary
  - Extend `scripts/generate_id_registry.py` to scan for VTR IDs
- **Acceptance criteria covered**: AC-08

### Task 6 (optional, post-activation): First Value Trade-off Records
- **Type**: impl
- **Name**: `impl_first_vtr_records`
- **Scope**: Document 2-3 existing design decisions as Value Trade-off Records to validate the format
- **Depends on**: Tasks 1-4
- **Effort**: S
- **Details**:
  - Select 2-3 existing design decisions that clearly involve value trade-offs (e.g., animated QR code, notification design, dark mode)
  - Document them retroactively as VTR records to validate the format works in practice
  - This is a limited retroactive exercise to test tooling, NOT a full retroactive application

---

## Requirements.md Update Proposals

### Proposed YAML additions to REQ-PROC-033

```yaml
vcd_activation_date: null  # Set when Task 2 completes
```

### Proposed acceptance criteria revisions

| AC | Current | Proposed Change |
|---|---|---|
| AC-01 | All personas (except system_maintenance) have mandatory 'Primary Values' and 'Value Conflicts' fields | No change needed — aligns with `vcd:` YAML schema |
| AC-02 | app_provider persona has Primary Values and Value Conflicts (sourced from real-user input) | Add: "evidence_method: grounded" |
| AC-09 | Methodology for deriving persona values without real user research is documented and justified | Add: "Three-pillar framework (Schwartz + Beauchamp-Childress + Nissenbaum) with Design-Relevance Filter, documented in requirements.md SEC-06" |
| AC-10 | Decision documented and closed: standalone 'Value Principles as Design Constraints' doc — needed or not | Close as: "NOT needed. Aggregation script (AC-08) replaces it. See findings document Q3." |

### Proposed new acceptance criteria

| New AC | Text |
|---|---|
| AC-11 | Lena's persona ID conflict (duplicate PERSONA-015) is resolved with a unique ID |
| AC-12 | VCD activation date is recorded in requirements.md YAML and persona_design_bridge.md |
| AC-13 | Value Trade-off Record ID scheme (VTR-NNN) is integrated into the existing ID registry system |

### Proposed "Out of Scope" update

Current out-of-scope states: "Retroactive application to all past decisions."
Proposed addition: "Limited retroactive exercise (2-3 decisions) for format validation is in scope (Task 6)."

---

## Appendix: References

- Friedman, B., Hendry, D.G. (2019). *Value Sensitive Design: Shaping Technology with Moral Imagination*. MIT Press.
- Schwartz, S.H. (2012). An Overview of the Schwartz Theory of Basic Values. *Online Readings in Psychology and Culture*, 2(1).
- Beauchamp, T.L., Childress, J.F. (2019). *Principles of Biomedical Ethics* (8th ed.). Oxford University Press.
- Nissenbaum, H. (2010). *Privacy in Context: Technology, Policy, and the Integrity of Social Life*. Stanford University Press.
- Klass, D., Silverman, P.R., Nickman, S. (1996). *Continuing Bonds: New Understandings of Grief*. Taylor & Francis.
- Linehan, M.M. (2014). *DBT Skills Training Manual* (2nd ed.). Guilford Press.
- Hautzinger, M. (2003). *Kognitive Verhaltenstherapie bei Depressionen*. Beltz.
