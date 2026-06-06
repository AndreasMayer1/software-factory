---
task_id: TASK-PROC-044-01-07
type: impl
parent_requirement: REQ-PROC-044-01
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-06-01
after: [TASK-PROC-044-01-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-03, AC-05]
  sections: []
scope_description: "Remediate the three AC-02/AC-03/AC-05 gaps found by the TASK-PROC-044-01-03 audit of the capability-authoring skills + six agents."
release_description: ""
opus_recommended: false  # reason: bounded, mechanical normalization of agent/skill/index files — no architectural judgment
writes_requirements: false
requirements_version:
  commit: 01945351
  file: ../../requirements.md
---

# Goal: Fix the REQ-PROC-044-01 audit gaps (AC-02, AC-03, AC-05)

## Objective

The TASK-PROC-044-01-03 audit verified the shipped capability-authoring skills and
the six modified agents against REQ-PROC-044-01. AC-01 and AC-04 passed; three gaps
were confirmed. Close all three, each via its governed authoring skill — never by
hand-editing.

## Requirements Summary

REQ-PROC-044-01 (Capability-Authoring Skills): AC-02 (required structural sections),
AC-03 (Domain-Vocabulary aid incl. format + reference model), AC-05 (single
authoritative ownership index with per-entry governing-AC cross-links).

For complete requirements at task creation time:
```
git show 01945351:requirements_tasks/process/AI_rules/epic_factory_quality/feat_capability_authoring_skills/requirements.md
```

Current requirements: ../../requirements.md

Audit evidence (read first):
`../2026-05-31_verify_capability-authoring-skills/plans_and_protocols/2026-06-01_01_protocol_audit.md`

## Scope

### In Scope

- **AC-02 gap** — the six agents (`architecture-advisor`, `implementation-engineer`,
  `opus-advisor`, `quality-checker`, `setup-optimizer`, `test-engineer`) each carry
  only `## Domain Vocabulary` + `## Anti-Patterns`; none has literal `## Protocols`,
  `## Output`, `## Rules`. Through **`claude-modify-agent`** (not by hand), bring each
  to the full five-section structure: re-home the existing procedural body under
  `## Protocols`, lift the result/output statement into `## Output`, and add a
  `## Rules` section (extract the hard constraints already implied by the body).
  **Preserve all existing content and meaning** — this is normalization, not rewrite.
- **AC-03 gap** — `claude-create-agent §5` (the Domain-Vocabulary aid) is missing two
  AC-03-mandated clauses. Through **`claude-modify-skill`**, add: (a) the format
  directive — terms as a single comma-separated plain-text line, no bullets/bold/inline
  explanations, the term alone activating domain knowledge; (b) the pointer naming the
  `han-adversarial-validator` agent as the reference model for that format.
- **AC-05 gap** — `.claude/skills/INDEX.md` governed-set table lists a 7th row
  (`claude-write-hook`) while the prose says "These six," and that row carries no
  governing-AC cross-link. Reconcile: either (a) keep write-hook and update the prose
  count + give it a real governing reference, or (b) drop it from the AC-05 governed
  set. Decide and make the table internally consistent with AC-05's "each ownership
  entry cross-links the existing ACs."

### Out of Scope

- Re-auditing AC-01 / AC-04 (passed).
- The `ui-scribble-*` agents (REQ-PROC-032 strand).
- Any `lib/`, `test/`, `integration_test/` change.

## Acceptance Criteria

- [ ] AC-02: all six agents carry `## Domain Vocabulary`, `## Anti-Patterns`, `## Protocols`, `## Output`, `## Rules` (in order), authored via `claude-modify-agent`, with no loss of existing procedural content
- [ ] AC-03: `claude-create-agent §5` states the comma-separated-line format directive and names `han-adversarial-validator` as the reference model, via `claude-modify-skill`
- [ ] AC-05: `.claude/skills/INDEX.md` governed-set table is internally consistent (prose count matches rows; every listed entry has a governing-AC cross-link or is removed from the AC-05 set)
- [ ] Each agent's `contract.yaml` re-checked after the AC-02 edits (no token/structure drift)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-01-03 | in_progress | Audit that identified these gaps; read its protocol first |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-044-01-03](../2026-05-31_verify_capability-authoring-skills/goal.md) | Predecessor — the audit that filed these gaps; carries the per-AC evidence |
| [TASK-PROC-044-01-02](../2026-05-31_impl_port-domain-vocabulary-to-existing-agents%20(completed)/goal.md) | The port task whose two-section scope decision left the AC-02 gap |

## Notes

The AC-02 gap traces to TASK-PROC-044-01-02's recorded scope decision (it added only
the two knowledge sections, judging the other three "already encoded" under existing
headings). The literal AC-02 requires all five `##` sections, so the gap stands and is
remediated here.
