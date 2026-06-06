---
id: REQ-PROC-032-02
status: active
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
effort: M
stakeholder: developer
created: 2026-02-28
updated: '2026-06-06'
after: []
blocks: []
market_research_refs: []
trackable_items:
  acceptance_criteria:
    - id: AC-01
      name: Iteration workflow defined
      description: Trigger → generate → auto-review (odd versions) → user feedback
        → rule update protocol → approve cycle; each version uses a dedicated fresh-context
        agent
    - id: AC-02
      name: Integration into existing workflows assessed
      description: 'Default ON; opt-out via skip_scribble: true; integrates with ux-validate-rule
        + doc-update-guidelines'
    - id: AC-03
      name: Design system alignment addressed
      description: T1/T2 rules read before generation; feedback triggers rule update
        protocol with Haiku impact agent
    - id: AC-04
      name: Scribble documentation location defined
      description: requirements_tasks/SKETCHES_README.md documents the scribble artifact
        format and workflow
  sections:
    - id: SEC-06
      name: Iteration Workflow
      heading: '## Iteration Workflow'
    - id: SEC-07
      name: Rule Update Protocol
      heading: '## Rule Update Protocol'
    - id: SEC-08
      name: Integration with Existing Workflows
      heading: '## Integration with Existing Workflows'
    - id: SEC-09
      name: Design System Alignment
      heading: '## Design System Alignment'
    - id: SEC-10
      name: Scribble Documentation Location
      heading: '## Scribble Documentation Location'
---

# Iteration And Rule Protocol

> **Implementation tasks:** This feature's ACs were implemented before REQ-PROC-032 was restructured into an epic (TASK-PROC-032-34, zero spec change), so it has no `tasks/` folder of its own. Some (if not all) of its implementing tasks live in the epic-level tasks folder `requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/` (the completed `scribble-*` batch). Only the genuinely-new features (F05–F07) carry their own derived `tasks/`.


## Iteration Workflow

Concrete steps for developer-AI UI scribble iteration. [AC-01]

```
1. Requirement has Presentation Layer scope
       │
       ▼
2. AI checks: skip_scribble: true in goal.md?
   ├── YES → proceed to implementation
   └── NO (default) ──────────────────────────────────────────────────┐
                                                                       ▼
                                               3. AI reads:
                                                  - requirements.md (personas served)
                                                  - relevant personas (trait constraints)
                                                  - doc/presentation/ T1/T2 rules
                                                       │
                                                       ▼
                                               4. Fresh agent generates scribbles/v{n}/
                                                  (n = 1, 3, 5 … odd versions)
                                                  - index.html
                                                  - one .html per screen
                                                  - metadata.yaml (status: draft)
                                                  - feedback.md template
                                                       │
                                                       ▼
                                               5. Fresh agent auto-reviews (v{n+1})
                                                  Checks ACs, personas, T1/T2 rules
                                                  Regenerates as v{n+1} (even version)
                                                       │
                                                       ▼
                                               6. Developer opens each screen HTML
                                                  in browser and reviews v{n+1}
                                                       │
                                                 ┌─────┴───────┐
                                                YES           NO — feedback given
                                                 │                    │
                                                 ▼                    ▼
                                          7. Developer          Rule Update Protocol
                                             approves           (see SEC-07)
                                             metadata.yaml           │
                                             status: approved        │
                                                 │             Rules anchored
                                                 │                    │
                                                 │             Fresh agent generates
                                                 │             scribbles/v{n+3}/
                                                 │             (loop to step 5)
                                                 ▼
                                          8. Implementation begins
                                                 │
                                                 ▼
                                          9. ui-verify-flutter (structural check)
                                                 │
                                                 ▼
                                         10. ui-improve-flutter (visual polish)
```

**Trigger**: Automatic when a Presentation Layer task starts, unless opted out via `skip_scribble: true` in `goal.md`.

**Agent per version**: Every scribble version (both generation and auto-review) uses a dedicated agent with a fresh context window. This prevents context overflow on multi-screen features. The orchestrating skill determines the next version number before spawning each agent.

**Auto-review loop**: After every odd-numbered version (v1, v3, …), a fresh agent automatically generates the next even version (v2, v4, …) by checking the scribble against requirements ACs, personas, and T1/T2 rules — before user feedback is requested. This catches structural gaps verifiable against documents without requiring a human review cycle for every issue.

**Review artifact**: Per-screen HTML files opened individually in any browser. `index.html` provides navigation.

**Feedback method**: Developer communicates verbally in the conversation. Each piece of feedback triggers the Rule Update Protocol (SEC-07) before the scribble is regenerated.

**Completion signal**: Developer explicitly states approval. AI updates `metadata.yaml` with `status: approved`. Implementation skill confirms approved scribble exists before proceeding.


## Rule Update Protocol

When developer feedback reveals a missing or incorrect design rule. [AC-02, AC-03]

This protocol applies whenever feedback implies a design rule should change. A rule change is NOT silently applied — it is always reviewed before being anchored.

### Step 1: Identify what the feedback implies

AI distinguishes:
- **Missing rule**: The scribble followed existing rules correctly, but the developer sees something that should be different → a new rule is needed
- **Requirement gap**: The screen is missing content or functionality → update `requirements.md`, not a design rule
- **Persona-derived constraint**: The feedback reflects a persona need already documented but not applied → apply the existing rule and note which was missed

### Step 2: Classify the tier of the new/changed rule

| Tier | Scope | Anchored in |
|------|-------|-------------|
| **T3** | This screen/feature only | Task's `goal.md` or `metadata.yaml` |
| **T2** | This pattern (2+ screens) | `doc/presentation/design/t2_[name].md` |
| **T1** | All screens system-wide | `doc/presentation/design/t1_[name].md` |

If `doc/presentation/design/` does not yet exist (REQ-PROC-026 not yet implemented), T1/T2 rules are anchored in `doc/presentation/[topic].md` until the subfolder structure is available.

### Step 3: Impact check for T1/T2 rules

For T2 and T1 rules: a Haiku agent runs an impact check to list which already-implemented requirements and screens would be affected by this rule change.

Developer decides:
- **Accept wider impact**: Promote to T2/T1, note affected requirements for future re-validation
- **Limit to T3**: Keep the rule screen-specific, mark as "candidate for promotion" in metadata

### Step 4: AI pauses for approval

AI presents:
```
New [T1/T2/T3] rule identified:

WHAT: [Rule statement]
HOW: [How to implement it — widget constraint or pattern]
WHY: [Persona justification or rationale]
Derived from: [Feedback text / persona trait]

[If T1/T2]: This rule would also affect:
  - REQ-FUNC-XXX (screen: Login) — currently implemented
  - REQ-FUNC-XXX (screen: Settings) — currently implemented
  → These would need re-validation against this rule.

Approve and anchor at [T1/T2/T3]? (yes / adjust / reject)
```

Human must explicitly approve before the rule is anchored.

### Step 5: Anchor the rule

- **T3**: Add to scribble `metadata.yaml` under `new_rules_anchored`
- **T2/T1**: Use `doc-update-guidelines` skill to create/update file in `doc/presentation/design/` (or current `doc/presentation/`)
- Rule format follows REQ-PROC-026 WHAT + HOW + WHY structure with persona justification

### Step 6: Regenerate scribble

New scribble version created with rule applied. Return to iteration workflow step 4 (odd version).

### Conflict resolution

If a new rule conflicts with an existing rule (e.g., Dr. Turan needs data density, Max needs simplicity):
- Use DDR (Design Decision Record) format from REQ-PROC-026
- DDR documents the conflict, the decision, and mitigations for the deprioritized persona
- AI presents the conflict before proceeding; human decides resolution


## Integration with Existing Workflows

How scribble iteration connects to other skills and workflows. [AC-02]

### code-simple and code-complex

When starting a Presentation Layer task:
1. Check `goal.md` for `skip_scribble: true`
2. If NOT present: check whether an approved scribble exists (`scribbles/` folder with a `status: approved` version)
3. If no approved scribble: generate scribble first (invoke `ui-create-sketch`), pause for developer approval
4. If approved scribble exists: proceed to implementation, reference scribble for element choices

**Opting out**: Add `skip_scribble: true` to `goal.md` YAML frontmatter. Use for:
- Trivial UI changes (label text, icon swap)
- Pure styling adjustments (color token update)
- Non-visual changes that happen to touch Presentation files

**Not applicable for**: Domain, Data, or infrastructure-only changes.

### ux-validate-rule (REQ-PROC-026, Task T3)

When Rule Update Protocol Step 4 produces a new T1/T2 rule, `ux-validate-rule` is used to:
- Verify the proposed rule is grounded in a documented persona need
- Classify the tier correctly
- Confirm the rule does not contradict an existing DDR

### doc-update-guidelines

When a T1/T2 rule is approved in Step 4, `doc-update-guidelines` anchors it in the appropriate `doc/presentation/` file. The scribble workflow does not write to `doc/` directly.

### requ-explore

If feedback reveals a requirement gap (missing functionality, not a missing design rule), `requ-explore` is invoked to update `requirements.md` before the next scribble iteration.


## Design System Alignment

How scribbles relate to design tokens and bridge to Flutter implementation. [AC-03]

**Approach**: Component-level mapping without visual styling. Scribbles define which Flutter widgets are used and their structural hierarchy — not their visual appearance.

**Component mapping block** (required at top of each screen HTML):
```html
<!--
  SCREEN: [Screen Name] — [Brief purpose]
  REQUIREMENT: REQ-[ID]
  VERSION: v[N]

  COMPONENT MAPPING — HTML element → Flutter widget
  ===================================================
  <button class="primary">     → FilledButton (M3)
  <button class="secondary">   → OutlinedButton
  <button class="text">        → TextButton
  <input type="text">          → TextField with OutlineInputBorder
  <input type="text" .error>   → TextField with errorText decoration
  <div class="card">           → Card with Material3 surfaceVariant
  <div class="list-item">      → ListTile
  <nav class="bottom-bar">     → NavigationBar (M3)
  <header class="app-bar">     → AppBar with Material3 surface tint
  <div class="chip">           → FilterChip / ChoiceChip

  PERSONAS APPLIED
  ================
  PERSONA-002 (Max): blank-field paralysis → structured prompts only, no empty free-text
  PERSONA-007 (Hanna): absolute darkness → dark background, no bright surfaces

  T1/T2 RULES APPLIED
  ====================
  T1: Touch targets ≥ 48dp (doc/presentation/design/t1_touch_targets.md)
  T1: Dark mode true black (doc/presentation/design/t1_dark_mode.md)
-->
```

**Token references are NOT required in scribbles**: Exact token values (spacing, sizing) are the implementation's job. The scribble defines structure; `ui-improve-flutter` handles token compliance on the real code.

**What approved scribbles define for implementation**:
- Element choices (FilledButton vs OutlinedButton)
- Information hierarchy (which elements are grouped, which are top-level)
- Screen flow sequence (via index.html)
- Persona constraints that must be preserved in Flutter code

**What scribbles do NOT define**:
- Colors, spacing values, or visual styling
- Exact animation curves or timings (Flutter animation test if needed)
- Exact responsive breakpoints (single design assumed)
- Accessibility attributes (handled in implementation per `doc/presentation/accessibility_guidelines.md`)
- Production-quality hover/focus states


## Scribble Documentation Location

Where the rules for the scribble artifact type are documented. [AC-04]

**Pattern**: Following the project convention where rules for artifact types live in co-located README files (e.g., `requirements_user_needs/README_*.md` for user needs artifacts, `requirements_tasks/README.md` for task artifacts), scribble artifact rules live in:

```
requirements_tasks/SKETCHES_README.md
```

This file documents:
- What a scribble is and what it is NOT
- Folder structure and file naming conventions
- `metadata.yaml` format and field definitions (including `design_decisions:`)
- Version lifecycle (draft → superseded → approved)
- How to provide feedback (verbal vs. annotated)
- How to signal approval
- How the Rule Update Protocol is triggered
- Post-implementation steps (`ui-verify-flutter`, `ui-improve-flutter`)

This is NOT in:
- `CLAUDE.md` (too low-level for the orchestrator constitution)
- `doc/presentation/` (that's coding guidelines for agents, not artifact format rules)

