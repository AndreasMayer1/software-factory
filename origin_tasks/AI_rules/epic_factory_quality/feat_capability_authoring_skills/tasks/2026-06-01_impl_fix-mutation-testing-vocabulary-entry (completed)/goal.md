---
task_id: TASK-PROC-044-01-06
type: impl
parent_requirement: REQ-PROC-044-01
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
status: completed
effort: XS
created: 2026-06-01
started: 2026-06-01
completed: 2026-06-01
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03]
  sections: []
scope_description: "Reformat ALL Domain Vocabulary sections in all agents to the comma-separated bare-term format (han-adversarial-validator reference model); clarify AC-03 to enforce this format"
release_description: ""
opus_recommended: false
writes_requirements: true
requirements_version:
  commit: 4d4b3e26
  file: ../requirements.md
---

# Goal: Reformat all agent Domain Vocabulary sections to comma-separated bare-term format

## Objective

ALL `## Domain Vocabulary` sections across all agents must use the format established by `han-adversarial-validator` — a single comma-separated line of bare terms with no bullets, no bold, and no inline explanations:

```
term1, term2, term3, ...
```

The current format in most agents uses markdown bullet points with bold and prose explanations:
```
- **mutation testing**: seeding faults to measure how much behavior the suite actually verifies
```

This is wrong on two levels: (1) prose explanations inflate agent context without adding value — the term alone activates the LLM's existing domain knowledge; (2) the bullet+bold format is heavier than needed for a vocabulary list.

Affected agents (7): `architecture-advisor`, `implementation-engineer`, `opus-advisor`, `quality-checker`, `setup-optimizer`, `test-engineer`, `ui-scribble-persona-walker`.

## Requirements Summary

AC-03 of REQ-PROC-044-01 governs the Domain-Vocabulary authoring aid. It currently specifies quantity (10–25 terms) and quality bar (15-year practitioner test) but is silent on format. The clarification adds: terms are listed as a comma-separated bare-term list with no inline explanations.

Current requirements: ../requirements.md

## Scope

### In Scope
- Reformat `## Domain Vocabulary` section in all 7 affected agents to comma-separated bare-term list
- Strip backtick formatting from terms in the comma list (plain text)
- Amend AC-03 in REQ-PROC-044-01 to specify the comma-separated format
- Regenerate `requirements.md`

### Out of Scope
- Changing the terms themselves (only format, not content)
- Agents already using the correct format (`han-adversarial-validator`)
- Agents with no vocabulary section (`ui-scribble-*` except persona-walker)

## Acceptance Criteria

- [x] All 7 affected agents' `## Domain Vocabulary` sections contain a single comma-separated line of bare terms (no bullets, no bold, no explanations)
- [x] Terms are plain text (no backtick formatting)
- [x] AC-03 of REQ-PROC-044-01 includes a format clause specifying comma-separated bare terms
- [x] `requirements.md` is regenerated after the AC-03 amendment

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-044-01-02](../2026-05-31_impl_port-domain-vocabulary-to-existing-agents%20(completed)/goal.md) | Predecessor — delivered the vocabulary entries this task refines |
