---
id: REQ-PROC-030-01
status: completed
market_research_refs: [] # No relevant findings identified
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "requ-derive-from-flow performs a keyword-grep pass across requirements_tasks/functional/ and requirements_tasks/non-functional/ for each gap before categorizing it as new_needed, using terms derived from the gap description to surface semantic overlaps where folder names and IDs differ"
    - id: AC-02
      text: "requ-explore uses keyword-grep as the primary overlap-detection mechanism when scanning for related requirements in section 1.4, not solely a folder-walk; the grep targets requirements_tasks/functional/ and requirements_tasks/non-functional/ and is performed in addition to reading the immediate folder hierarchy"
    - id: AC-03
      text: "requ-explore documents all semantically related requirements found via keyword-grep in the ## Related Requirements section of the new requirement, so future agents do not need to repeat the overlap search"
    - id: AC-04
      text: "requ-explore section 1.5 includes an explicit check for orphaned implementations: after identifying relevant code in lib/, the skill verifies that an existing requirement covers the observed behavior; if none is found, this gap is recorded in the protocol before proceeding"
    - id: AC-05
      text: "requ-explore section 1.5 prescribes a minimum search scope: at least 2–3 grep passes on lib/ for key domain terms before concluding that no existing implementation exists for the requirement topic"
---

# Requirements Pipeline Consistency Checks

## Overview

This feature specifies the consistency and conflict-prevention mechanisms that `requ-derive-from-flow` and `requ-explore` must apply when creating or updating requirements. These mechanisms ensure that no new requirement silently duplicates or contradicts an existing requirement or an existing implementation.

## Purpose

A gap in these checks caused an incident: `requ-explore` wrote a requirement specifying that a data migration mechanism needed to be implemented, without knowing that the mechanism already existed in `lib/`. The AI did not find the existing implementation because section 1.5 did not perform a sufficiently targeted search of `lib/`, and the sibling-requirement scan in section 1.4 used only a folder-walk, missing semantically related requirements in other branches of the hierarchy.

This requirement defines the end state where such contradictions are caught before a requirements.md or goal.md is written.

## Scope

- In scope: overlap-detection mechanisms in `requ-derive-from-flow` (section 1.3) and `requ-explore` (sections 1.4, 1.5)
- Out of scope: the one-time requirements backfill task (addressed in a separate explore task)
- Out of scope: full source-code scanning in `requ-derive-from-flow` — implementation awareness belongs in `requ-explore`
- Out of scope: scanning `requirements_tasks/process/` — requirements derived from user flows target functional and non-functional categories only

## Behavior

### Keyword-Grep in `requ-derive-from-flow` (section 1.3)

When assessing whether a gap is `new_needed`, `exists_complete`, `exists_needs_update`, or `exists_placeholder`, the skill performs a targeted keyword-grep across `requirements_tasks/functional/` and `requirements_tasks/non-functional/` using terms derived from the gap description (domain nouns, action verbs, component names). A gap is not categorized as `new_needed` until this grep pass returns no relevant hits. This supplements the existing file-read approach and catches overlaps where folder names or IDs differ.

### Keyword-Grep + Related Requirements in `requ-explore` (section 1.4)

When reading parent and sibling requirements, the skill runs a keyword-grep across `requirements_tasks/functional/` and `requirements_tasks/non-functional/` using terms from the requirement topic being explored. The grep results are read to identify semantic overlaps even when folder names or IDs differ. The folder-walk (reading files at the same folder level) is preserved as supplementary structural context.

All related requirements found via this grep are listed in the `## Related Requirements` section of the newly created requirement document. This makes the overlap check's findings persistent and discoverable by future agents without repeating the search.

### Implementation Analysis in `requ-explore` (section 1.5)

Section 1.5 ("Analyze Implementation") includes an explicit orphaned-implementation check: after identifying relevant code in `lib/`, the skill verifies that an existing requirement covers the observed behavior. If code implementing the concept is found but no requirement covers it, this gap is explicitly recorded in the protocol before proceeding — not silently accepted as normal.

A minimum search scope applies: at least 2–3 grep passes on `lib/` for key domain terms are executed before concluding that no existing implementation exists for the requirement topic.

## Developer Guidelines

### Key Decisions

- `process/` is excluded from the keyword-grep scope: requirements derived from user flows always target functional or non-functional categories. Process requirements encode AI workflow rules, not application behavior.
- Keyword-grep terms are derived from the gap description at runtime — typical sources: domain nouns from the gap title, action verbs, component names, and personas mentioned. 2–4 terms per grep pass is sufficient.
- The orphaned-implementation check does not require a full codebase scan. A best-effort grep for key domain terms in `lib/` is sufficient. Absence of hits after 2–3 targeted passes is enough to proceed.
- Documenting related requirements in `## Related Requirements` is not optional: it transforms the consistency check from a one-time cost into a reusable artifact. Future agents reading the requirement benefit without repeating the grep.

### Common Pitfalls

- Using only the folder-walk in section 1.4 without a keyword-grep: creates a false sense of completeness when related requirements exist in a different folder branch.
- Deriving grep terms only from requirement IDs (e.g. `REQ-FUNC-007`) rather than semantic domain terms: IDs don't surface requirements that cover the same concept under a different name.
- Treating "code found in lib/" as confirmation that a requirement exists: the orphaned-implementation check explicitly tests the inverse — does a requirement exist for what the code does?
- Leaving `## Related Requirements` empty after a keyword-grep that returned hits: the hits must be evaluated and the relevant ones listed.

## Related Requirements

- Parent: `requirements_tasks/process/AI_rules/requirements_management/user_flow_to_requirements/requirements.md` (REQ-PROC-030) — AC-03 ("Skill scans existing requirements and correctly categorizes each gap")

## References

- `.claude/skills/requ-derive-from-flow/skill.md` — section 1.3 (Scan existing requirements)
- `.claude/skills/requ-explore/skill.md` — sections 1.4 (Read Requirement Hierarchy), 1.5 (Analyze Implementation)
