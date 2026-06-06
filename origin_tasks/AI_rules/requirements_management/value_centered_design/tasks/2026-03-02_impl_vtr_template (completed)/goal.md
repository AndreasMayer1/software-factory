---
task_id: TASK-PROC-033-03
type: impl
parent_requirement: REQ-PROC-033
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-PAIN
status: completed
completed: 2026-03-02
effort: S
created: 2026-03-02
after:
  - TASK-PROC-033-02
awaiting: []
covers:
  acceptance_criteria:
    - AC-03
    - AC-04
    - AC-10
    - AC-11
    - AC-12
  sections:
    - SEC-02
    - SEC-06
    - SEC-07
    - SEC-08
scope_description: "Create the canonical Value Trade-off Record template, fix Lena's duplicate persona_id, record VCD activation date, and update related documentation. This task closes AC-10 and unblocks all parallel downstream tasks."
requirements_version:
  commit: dcc97ff
  file: ../requirements.md
---

# Goal: Create VTR Template, Fix Persona ID, Record Activation Date

## Objective

After persona values are populated (TASK-PROC-033-02), this task creates the operational infrastructure for Value Trade-off Records and resolves two administrative issues identified during exploration.

## Deliverables

### 1. Value Trade-off Record Template

Create: `requirements_user_needs/_meta/value_tradeoff_record_template.md`

Content — the canonical VTR format (from findings document):

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
- **Decision**: [What was decided? Or "OPEN — awaiting user decision" if unresolved]
- **Rationale**: [Why this decision over alternatives? Reference app_provider hierarchy if applicable]
- **Consequences**: [Which persona's values are degraded and how?]
```

The template file should also include:
- Usage instructions (when to use, where to embed)
- ID assignment instructions (next VTR-NNN)
- Link to the `vcd-log-tradeoff` skill (TASK-PROC-033-05)

### 2. Fix Lena's Duplicate persona_id

**Problem**: `requirements_user_needs/personas/lena_depth_seeker/persona.md` has `persona_id: PERSONA-015` — identical to `app_provider/persona.md`.

**Fix**: Update Lena's persona_id to the next available ID. Check existing persona IDs to find the gap. Based on current numbering (PERSONA-001 through PERSONA-015), Lena should receive **PERSONA-016**.

Steps:
1. Read all persona files to confirm current highest ID
2. Assign PERSONA-016 to Lena
3. Update `persona_id: PERSONA-016` in Lena's frontmatter
4. Add `review_history` entry noting the ID correction
5. Search for any references to Lena's old PERSONA-015 ID in other files and update them
   - Check: scenario files under `lena_depth_seeker/scenarios/`
   - Check: user flow files under `requirements_user_needs/user_flows/`
   - Check: requirement files in `requirements_tasks/`

### 3. Record VCD Activation Date

**Where**:
1. In `requirements_tasks/process/AI_rules/requirements_management/value_centered_design/requirements.md`: set `vcd_activation_date` YAML field to today's date (2026-03-02)
2. In `doc/presentation/design/persona_design_bridge.md`: add a note at the top of the document

**Note text for persona_design_bridge.md**:
```markdown
> **VCD Active since 2026-03-02**: All design decisions after this date must consult persona values
> from the `vcd:` YAML blocks in persona files. When decisions create value conflicts between
> personas, document a Value Trade-off Record inline in the artifact. See REQ-PROC-033.
```

### 4. Update requirements.md

In `requirements_tasks/process/AI_rules/requirements_management/value_centered_design/requirements.md`:

- Close the "Key Design Decisions" section — note that all decisions were resolved in TASK-PROC-033-01
- Add reference to the findings document
- Confirm AC-10 is resolved: standalone doc NOT needed; aggregation script used instead

## Acceptance Criteria

- [ ] `requirements_user_needs/_meta/value_tradeoff_record_template.md` exists with canonical VTR format
- [ ] Template includes YAML metadata block with `<!-- vcd-record` marker
- [ ] Lena's persona_id changed from PERSONA-015 to PERSONA-016 with no broken references
- [ ] `vcd_activation_date: 2026-03-02` recorded in requirements.md YAML
- [ ] Activation note added to `doc/presentation/design/persona_design_bridge.md`
- [ ] AC-10 formally closed in requirements.md body
- [ ] All changes committed

## Dependencies

- Requires: TASK-PROC-033-02 (persona values must exist to set activation date meaningfully)
- Unblocks: TASK-PROC-033-04, TASK-PROC-033-05, TASK-PROC-033-06 (all can run in parallel after this)
