---
task_id: TASK-PROC-033-02
type: impl
parent_requirement: REQ-PROC-033
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-PAIN
status: completed
completed: 2026-03-02
effort: M
created: 2026-03-02
after:
  - TASK-PROC-033-01
awaiting: []
covers:
  acceptance_criteria:
    - AC-01
    - AC-02
    - AC-09
  sections:
    - SEC-01
    - SEC-06
scope_description: "Add vcd: YAML block (primary_value, secondary_values, value_conflicts) to all 14 personas using the three-pillar framework. User reviews and approves each set of values before the task is complete."
requirements_version:
  commit: dcc97ff
  file: ../requirements.md
---

# Goal: Populate Persona Value Fields

## Objective

Add `vcd:` YAML frontmatter blocks to all 14 active personas (all except `system_maintenance`) using the methodology established in TASK-PROC-033-01.

This task produces the data foundation for the entire VCD system. No downstream tasks (skills adaptation, trade-off recording, aggregation) can function without this.

## Background

See: `../2026-03-02_explore_vcd_integration/plans_and_protocols/2026-03-02_01_findings_vcd_exploration.md`

**Methodology** (Q1 answer): Three-pillar framework:
1. Schwartz Theory of Basic Human Values — motivational value types
2. Beauchamp & Childress Principles of Biomedical Ethics — Autonomy, Beneficence, Non-maleficence, Justice
3. Nissenbaum Contextual Integrity — information flow ethics

**Design-Relevance Filter**: Only derive values that cause real design trade-offs. Ignore values with no UI/UX/architecture implications.

**Evidence tagging**:
- `literature_derived` — all client, self-user, and therapist personas
- `grounded` — app_provider only (values already confirmed by the creator)

## YAML Schema

Add to each persona's YAML frontmatter (after `pcd:` block):

```yaml
vcd:
  evidence_method: literature_derived  # or "grounded" for app_provider
  framework_sources:
    - "Schwartz (2012) Basic Human Values"
    - "Beauchamp & Childress (2019) Principles of Biomedical Ethics"
    - "Nissenbaum (2010) Contextual Integrity"  # include only if used
  primary_value:
    name: "[Value Name]"
    framework: "[Schwartz | Beauchamp-Childress | Nissenbaum]"
    design_relevance: "[1-2 sentences: concrete design implication]"
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
      description: "[2-3 sentences: when this tension manifests in design]"
      opposing_personas: ["PERSONA-NNN"]
```

## Personas to Update

Process in this order (clients first, then self-users, then therapists, app_provider last):

### Clients (evidence_method: literature_derived)
1. `requirements_user_needs/personas/max_client/persona.md` (PERSONA-002)
2. `requirements_user_needs/personas/elias_skeptical_guardian/persona.md` (PERSONA-009)
3. `requirements_user_needs/personas/sophie_structure_seeker/persona.md` (PERSONA-010)
4. `requirements_user_needs/personas/jana_high_strung/persona.md` (PERSONA-014)
5. `requirements_user_needs/personas/lena_depth_seeker/persona.md` (PERSONA-015b — see persona ID note below)

### Self-Users (evidence_method: literature_derived)
6. `requirements_user_needs/personas/lisa_waitlist_bridger/persona.md` (PERSONA-005)
7. `requirements_user_needs/personas/michael_high_performer/persona.md` (PERSONA-006)
8. `requirements_user_needs/personas/hanna_sleepless/persona.md` (PERSONA-007)
9. `requirements_user_needs/personas/david_structure_seeker/persona.md` (PERSONA-008)
10. `requirements_user_needs/personas/nina_energy_budgeter/persona.md` (PERSONA-013)

### Therapists (evidence_method: literature_derived)
11. `requirements_user_needs/personas/dr_sarah/persona.md` (PERSONA-001)
12. `requirements_user_needs/personas/prof_dr_weber/persona.md` (PERSONA-011)
13. `requirements_user_needs/personas/dr_med_turan/persona.md` (PERSONA-012)

### System — app_provider (evidence_method: grounded)
14. `requirements_user_needs/personas/app_provider/persona.md` (PERSONA-015)
    - Values already documented in "Decision-Making Principles" section
    - Formalize into `vcd:` YAML block — do NOT change the body text
    - Primary value: Beneficence (user wellbeing)
    - User must explicitly confirm the formalized values

## Preliminary Value Mapping (from findings document)

Use this as starting guidance. AI derives the specific formulation from each persona file:

| Persona | Primary Value | Central Tension |
|---|---|---|
| Max | Non-maleficence (shame-free) | Shame avoidance vs. data completeness |
| Lisa | Autonomy (self-directed prep) | Guidance need vs. no therapist |
| Michael | Achievement (optimization) | Data depth vs. anti-therapy identity |
| Hanna | Non-maleficence (no light/noise) | Externalization need vs. 3 AM constraints |
| David | Autonomy (self-built system) | Structure need vs. novelty addiction |
| Elias | Contextual Integrity (privacy) | Camouflage vs. therapeutic utility |
| Sophie | Beneficence (external scaffolding) | Ease-of-use vs. data richness |
| Prof. Weber | Beneficence (depth/meaning) | Narrative richness vs. digital reduction |
| Dr. Turan | Beneficence (patient safety) | Speed vs. depth |
| Nina | Autonomy (illness self-management) | Tracking value vs. tracking-as-energy-drain |
| Jana | Non-maleficence (crisis safety) | Emotional accuracy vs. crisis accessibility |
| Dr. Sarah | Beneficence (patient progress) | Structured data vs. compliance burden |
| Lena | Autonomy (meaning-making) | Narrative depth vs. searchability |
| app_provider | Beneficence (user wellbeing) | Feature richness vs. solo-dev sustainability |

## Important: Persona ID Issue

Lena (`lena_depth_seeker/persona.md`) currently has `persona_id: PERSONA-015` — the same as app_provider. This is a pre-existing conflict. **Do NOT fix this in this task.** It is addressed in TASK-PROC-033-03. For this task, add the `vcd:` block to Lena's file without changing her persona_id.

## Workflow

For each persona:
1. Read full persona.md
2. Identify primary value using Design-Relevance Filter + three-pillar framework
3. Identify 3 secondary values
4. Identify 1+ value conflicts (opposing persona's values)
5. Propose the `vcd:` YAML block to user
6. **PAUSE** — wait for user approval before writing to file
7. Write approved block to persona.md (insert after `pcd:` block)
8. Add `review_history` entry noting VCD fields added

## Acceptance Criteria

- [ ] All 14 personas have `vcd:` YAML blocks
- [ ] Each block has exactly 1 primary value, exactly 3 secondary values, at least 1 value conflict
- [ ] All values pass the Design-Relevance Filter
- [ ] Each value cites its framework source
- [ ] app_provider uses `evidence_method: grounded`
- [ ] All other personas use `evidence_method: literature_derived`
- [ ] User explicitly approved each persona's values before writing
- [ ] All persona files have updated `review_history` entries
- [ ] Findings written to `plans_and_protocols/`

## Dependencies

- Requires: TASK-PROC-033-01 (findings document approved) ✓

## Notes

- Process one persona at a time (not batch). User approval is required per persona.
- The Design-Relevance Filter is the critical quality gate — if a value doesn't affect design decisions, exclude it.
- Reference the preliminary mapping above but do NOT copy blindly — read each persona file and derive values from the actual documented content.
