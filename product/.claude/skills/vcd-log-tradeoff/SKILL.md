---
name: vcd-log-tradeoff
description: Document a Value Trade-off Record inline in an artifact when persona values conflict
tools: ["*"]
model: inherit
---

You document Value Trade-off Records (VTR) inline in artifacts when persona value conflicts arise.

## Invocation

`"Use vcd-log-tradeoff skill for [artifact path]: [brief decision description]"`

Or called from within ux-validate-rule, ux-create-flow, or requ-explore when a value conflict is identified.

## Workflow

### Step 1: Identify the Conflict

Parse the description to determine:
- The design decision being made
- Which artifact will contain the record
- Which personas are involved (ask user if not obvious)

### Step 2: Load Persona Values

Read `vcd:` YAML blocks from all involved personas in `requirements_user_needs/personas/`.
Extract: `primary_value`, `secondary_values`, `value_conflicts`.

### Step 3: Map the Conflict

For each involved persona, assess which values are supported or degraded by the proposed decision.

Present a concise conflict summary:
```
Conflict identified:
- PERSONA-NNN (Name): Primary value "[value]" is DEGRADED
- PERSONA-NNN (Name): Secondary value "[value]" is SUPPORTED

Primary value conflict → VTR is mandatory.
```

### Step 4: Surface Options — PAUSE FOR USER DECISION

Generate 2-3 options with per-persona value impact:
```
Option A: [Description]
  → PERSONA-NNN: [value] [supported | degraded | neutral]
  → PERSONA-NNN: [value] [supported | degraded | neutral]

Option B: [Description]
  → ...
```

**WAIT** for user to select an option or provide their own decision. Do NOT auto-resolve conflicts.

### Step 5: Assign VTR ID

Scan all `<!-- vcd-record` blocks in these directories for the highest existing VTR-NNN:
- `requirements_user_needs/`
- `requirements_tasks/`
- `doc/presentation/design/`

Or read `requirements_user_needs/_meta/id_registry.md` VTR section if available.
Assign next sequential ID (VTR-001 if none exist).

### Step 6: Generate Record

Compose the full VTR using the canonical template from `requirements_user_needs/_meta/value_tradeoff_record_template.md`.

Populate all fields from Steps 1–4 and the user's decision.

- `decision_status: decided` if user made a decision; `open` if deferred
- `decided_by: user` if explicitly chosen; `ai_recommended` if user accepted AI proposal unchanged

### Step 7: Insert Inline

Insert the record into the specified artifact under `## Value Trade-offs` section (create if absent, append if present).

Target by artifact type:
- User flows → `## Value Trade-offs`
- Requirements → `## Value Trade-offs`
- Design rules → `## Value Trade-offs`

**Never** create a separate file. Always insert inline.

### Step 8: Back-Reference (for code-level decisions)

If triggered by code-complex or code-simple:
- Note the code location in the record under "Consequences"
- Remind: WHY comment required at that location referencing VTR-NNN:
  ```dart
  /// Why: [Brief description of value trade-off]
  /// VCD: [VTR-NNN] — [artifact path]
  ```

### Step 9: Confirm

```
Value Trade-off Record created: VTR-[NNN]
Location: [artifact path] → ## Value Trade-offs
Decision status: [decided | open]
Personas affected: [list]

Next: python scripts/artifacts/aggregate_value_tradeoffs.py
```
