---
task_id: TASK-PROC-033-05
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
  - TASK-PROC-033-03
awaiting: []
covers:
  acceptance_criteria:
    - AC-05
    - AC-07
  sections:
    - SEC-03
scope_description: "Create the vcd-log-tradeoff skill that guides the user through documenting a Value Trade-off Record inline in an artifact. The skill reads persona values, surfaces the conflict, presents options, and inserts the completed record."
requirements_version:
  commit: dcc97ff
  file: ../requirements.md
---

# Goal: Create vcd-log-tradeoff Skill

## Objective

Create a new skill `.claude/skills/vcd-log-tradeoff/skill.md` that guides consistent documentation of Value Trade-off Records. This is the primary tool for AC-05 (skill for consistent trade-off documentation) and AC-07 (back-referencing code/doc decisions in the originating requirement).

## Background

See findings document Q2 and Q5 for the trigger criteria and format. The skill operationalizes those decisions.

## Skill Workflow

### Invocation

User invokes: `"Use vcd-log-tradeoff skill for [artifact path]: [brief description of the decision]"`

Or called from within another skill (ux-validate-rule, ux-create-flow, requ-explore) after a value conflict is identified.

### Step 1: Identify the conflict

Parse the user's description to identify:
- The design decision being made
- Which artifact will contain the record (user flow, requirement, design rule)
- Which personas are involved (ask user if not obvious)

### Step 2: Load persona values

Read `vcd:` YAML blocks from all involved personas. Extract:
- Primary value for each persona
- Secondary values for each persona
- Existing value_conflicts entries that might be relevant

### Step 3: Map the conflict

For each involved persona, assess:
- Which value(s) does the proposed decision support?
- Which value(s) does it degrade?
- Is this a primary value conflict? (higher severity) or secondary? (lower severity)

Present a concise conflict summary to the user:
```
Conflict identified:
- PERSONA-009 (Elias): Primary value "Contextual Integrity" is DEGRADED
- PERSONA-010 (Sophie): Secondary value "Simplicity" is SUPPORTED

This affects a primary value — Value Trade-off Record is mandatory.
```

### Step 4: Surface options

Generate 2-3 design options with their value impact for each option:

```
Option A: [Description]
  → PERSONA-009: Contextual Integrity [degraded by 30%]
  → PERSONA-010: Simplicity [supported]

Option B: [Description]
  → PERSONA-009: Contextual Integrity [supported]
  → PERSONA-010: Simplicity [degraded]

Option C: [Compromise description]
  → PERSONA-009: Contextual Integrity [neutral]
  → PERSONA-010: Simplicity [neutral — neither fully served]
```

**PAUSE** — present options to user. Wait for user to select or provide their own decision.

### Step 5: Assign VTR ID

Determine next available VTR-NNN ID:
- Read `requirements_user_needs/_meta/id_registry.md` for current highest VTR-NNN
- Or scan all existing `<!-- vcd-record` blocks to find the highest current ID
- Assign next sequential ID

### Step 6: Generate the record

Compose the full Value Trade-off Record using the canonical template from `requirements_user_needs/_meta/value_tradeoff_record_template.md`.

Populate all fields from the information gathered in steps 1-4 and the user's decision in step 4.

Set `decision_status: decided` if user made a decision; `open` if deferred.
Set `decided_by: user` if user chose explicitly; `ai_recommended` if AI proposed and user accepted without modification.

### Step 7: Insert inline

Insert the record into the specified artifact under the appropriate section:
- User flows → `## Value Trade-offs` section (create if absent, append if present)
- Requirements → `## Value Trade-offs` section (create if absent, append if present)
- Design rules → `## Value Trade-offs` section (create if absent, append if present)

**Never** create a separate file for the record. Always inline.

### Step 8: Back-reference (AC-07)

If the decision was triggered by a code-level concern (reported by code-complex or code-simple):
- Note the code location in the record under "Consequences"
- Add a comment to the agent/protocol: "WHY comment required at [file:line] referencing this record"

The WHY comment format for code:
```dart
/// Why: [Brief description of value trade-off]
/// VCD: [VTR-NNN] — [artifact path]
```

### Step 9: Output

Confirm completion:
```
Value Trade-off Record created: VTR-[NNN]
Location: [artifact path] → ## Value Trade-offs section
Decision status: [decided | open]
Personas affected: [list]

Next: Run aggregation script to update summary.
  python scripts/aggregate_value_tradeoffs.py
```

## Skill File Location

`.claude/skills/vcd-log-tradeoff/skill.md`

## Skill Design Constraints

- **Token-efficient**: No verbose explanations. Steps are instructions, not essays.
- **No Dart-style `///` WHY comments** in the skill file itself. Use inline `(reason)` if needed.
- **Pause behavior**: The skill MUST pause for user decision in Step 4. It does NOT auto-resolve conflicts.
- **Inline only**: Records are never written to separate files.

## Acceptance Criteria

- [ ] Skill file exists at `.claude/skills/vcd-log-tradeoff/skill.md`
- [ ] Skill reads persona values from `vcd:` YAML blocks
- [ ] Skill generates 2-3 options with per-persona value impact
- [ ] Skill pauses for user decision (does not auto-resolve)
- [ ] Skill assigns next available VTR-NNN ID
- [ ] Skill inserts record inline in the specified artifact
- [ ] Skill includes back-reference guidance for code-level decisions (AC-07)
- [ ] Skill description added to CLAUDE.md or `.claude/README.md` skill list

## Dependencies

- Requires: TASK-PROC-033-03 (template must exist to reference)
- Can run in parallel with: TASK-PROC-033-04, TASK-PROC-033-06
