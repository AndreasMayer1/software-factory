---
task_id: TASK-PROC-033-04
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
    - AC-06
  sections:
    - SEC-04
scope_description: "Add lightweight VCD checklist steps to 5 skills and update the ux-create-persona template. Changes are additive only — no skill's existing workflow is restructured."
requirements_version:
  commit: dcc97ff
  file: ../requirements.md
---

# Goal: Adapt Skills for VCD Awareness

## Objective

Add a single VCD check step to each of the 5 identified skills so that design decisions automatically surface persona value conflicts and trigger Value Trade-off Records when needed.

## Guiding Principle

**Minimal footprint**: Each skill gets 3-8 lines added. No workflow restructuring. The check fits naturally into the existing flow at the point where persona conflicts would logically surface.

## Skills to Modify

All skill files are in `.claude/skills/[name]/skill.md`.

---

### 1. `ux-validate-rule` skill

**Where to insert**: Between current Step 4 (Check alignment per persona) and Step 5 (Detect conflicts).

**What to add** — new step 4b:

```
4b. **VCD Check** — For personas classified as CONFLICTS or affected by this rule:
   - Read each persona's `vcd:` YAML block (primary_value, secondary_values)
   - Does this rule degrade any persona's primary or secondary value?
   - If YES → the validation report must include a "Value Trade-off Required" flag
   - Use the `vcd-log-tradeoff` skill after approval to document the trade-off
```

---

### 2. `ux-create-flow` skill

**Where to insert**: In Step 3a (Analysis Phase), after the existing analysis structure.

**What to add** — new item in the analysis document:

```
7. **Value Conflicts** (VCD check — required for multi-persona flows):
   - Read `vcd:` YAML blocks for all personas this flow serves
   - List any primary/secondary value conflicts between serving personas
   - If conflicts exist → flow.md must include a `## Value Trade-offs` section
   - Use the `vcd-log-tradeoff` skill to document each conflict record
```

Also add to Step 6 (Generate flow.md) instructions:

```
**VCD**: If value conflicts were identified in Step 3a, include a `## Value Trade-offs`
section at the bottom of flow.md with inline Value Trade-off Records.
```

---

### 3. `code-complex` skill

**Where to insert**: Step 2 (Plan — architecture-advisor agent tasks), add to agent task list.

**What to add**:

```
   - If plan involves Presentation Layer changes affecting multiple personas:
     read `vcd:` YAML blocks for affected personas and flag any value conflicts
     in the plan document (use section "Value Trade-offs Identified")
```

Also in Step 6 (Quality — quality-checker agent), add:

```
   - VCD: Verify that any value trade-off decisions in implemented code have a
     WHY comment referencing the trade-off record in the originating artifact
```

---

### 4. `code-simple` skill

**Where to insert**: Before the implementation step, as a guard.

**What to add** — guard step:

```
**VCD Guard** (skip if change is purely technical with no UX impact):
If this change affects a feature used by personas with conflicting values:
1. Read `vcd:` YAML blocks for the 2-3 most relevant personas
2. Does this change degrade any persona's primary value?
3. If YES → PAUSE and present the conflict to the user before implementing
4. If NO → proceed
```

---

### 5. `requ-explore` skill

**Where to insert**: Phase 1.6 (Map User Needs), after the existing persona mapping.

**What to add**:

```
**VCD Analysis** (for requirements serving multiple personas):
- For each persona in `personas_served`, read their `vcd:` YAML block
- Identify value conflicts between serving personas
- If conflicts exist → add `## Value Trade-offs` section to the requirement body
- Document each conflict using the template in `requirements_user_needs/_meta/value_tradeoff_record_template.md`
```

---

### 6. `ux-create-persona` template update

The persona creation skill (or its internal template) must include the `vcd:` YAML block as a placeholder in new personas:

Find in `ux-create-persona` skill where persona YAML is generated and add the `vcd:` block template with `TODO` placeholders. Also add a step: "After creating persona body, derive VCD values using three-pillar framework and populate the `vcd:` block."

---

## Acceptance Criteria

- [ ] `ux-validate-rule`: VCD check added between steps 4 and 5
- [ ] `ux-create-flow`: VCD conflict check added to Step 3a analysis structure
- [ ] `code-complex`: VCD flag added to planning agent task list and quality check
- [ ] `code-simple`: VCD guard step added before implementation
- [ ] `requ-explore`: VCD analysis added to Phase 1.6
- [ ] `ux-create-persona`: `vcd:` YAML placeholder added to persona template
- [ ] No existing skill logic was removed or restructured
- [ ] All changes are token-efficient (no verbose explanations in skill files)

## Dependencies

- Requires: TASK-PROC-033-03 (template must exist to reference it in skill instructions)
- Can run in parallel with: TASK-PROC-033-05, TASK-PROC-033-06
