---
task_id: TASK-PROC-055-02
type: impl
parent_requirement: REQ-PROC-055
urgency: 2
urgency_reason: U2-OPP
impact: 4
impact_reason: I4-ENAB
status: completed
effort: M
created: 2026-05-26
started: 2026-05-27
completed: 2026-05-27
session_completed_at: 2026-05-27T08:32:11Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Port han's YAGNI two-gate evidence test (inspirational adoption) into our requirement/planning skills"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: 3053f73c
  file: ../requirements.md
session_id: 60b73e52-19d3-4e28-ae60-40f89db80796
session_account: gmail2

---
# Goal: Port han's YAGNI Evidence-Gate into Our Requirement & Planning Skills

## Objective

Inspirationally adopt (no file copying) han's YAGNI two-gate evidence test as a systematic gate in our own skills. Today we have the *ethos* ("don't add features beyond what the task requires") but no *gate* and no defer-with-trigger discipline.

The gate has two parts:
- **Gate 1 (inclusion):** any committed item (an acceptance criterion, a planned scope item, a spec line) must cite at least one piece of real evidence: a user-described need, a named direct dependency, an existing production code path that breaks without it, a regulation demonstrably in effect, or a documented incident / fired alert / measured metric. Hypotheticals ("for future flexibility", "when we scale", "best practice says") do not qualify.
- **Gate 2 (shape):** when evidence justifies inclusion, prefer the strictly simpler version that satisfies the same evidence.

Items failing Gate 1 are **deferred with a named reopen-when trigger**, never silently dropped.

This realizes REQ-PROC-055 OR-2 (inspirational-first adoption) in a concrete skill change.

## Requirements Summary

Governed by REQ-PROC-055 (External Tooling & Plugin Adoption), OR-2. Source analysis: the han evaluation in TASK-PROC-055-01.

For full context, read:
- `../tasks/2026-05-26_explore_han-plugin-evaluation/plans_and_protocols/2026-05-26_05_synthesis_decision_report.md` (section 5, item 1)
- `../tasks/2026-05-26_explore_han-plugin-evaluation/plans_and_protocols/2026-05-26_01_gather_han_skills.md` (YAGNI section — exact two-gate definition + Deferred-section format)

Current requirements: ../requirements.md

## Scope

### In Scope
- Add the YAGNI two-gate evidence test to `requ-explore` (AC inclusion step), `task-derive-from-requ`, and `code-complex` (planning step).
- Define a standard "Deferred (evidence pending)" output convention with a named reopen-when trigger.
- Keep wording token-efficient (skills are loaded into every agent call); no `///` WHY comments in skills.
- Use the `claude-modify-skill` skill for each skill edit (mandatory; syncs INDEX.md + factory_flows.md).

### Out of Scope
- Copying any han file (this is inspirational adoption — re-author in our voice).
- Changing quality-gate scripts or analysis_options.yaml.
- Any lib/ code change.

## Acceptance Criteria

- [x] `requ-explore`, `task-derive-from-requ`, and `code-complex` each apply a YAGNI inclusion gate (evidence test) before committing items.
- [x] A simpler-version (shape) check is part of the same gate.
- [x] A standard "deferred with reopen-when trigger" convention exists; items lacking evidence are deferred, never silently dropped.
- [x] Each skill edit went through `claude-modify-skill` (INDEX.md + factory_flows.md stay in sync).
- [x] The user can override any single deferral (the gate makes cost visible; it does not veto the user).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

This task is one of three inspirational ports chosen from the han evaluation (the others: explicit sizing announcement, and a band-F agent pilot). It applies REQ-PROC-055's standing policy rather than "covering" a section of it, so `covers` is intentionally empty.

**Scribble skill inspiration (TASK-PROC-032-09 depends on this)**

The YAGNI evidence gate has a direct application in the `ui-create-scribble` skill:

- Phase 2 auto-review should apply the gate to each generated screen state: "Is there
  evidence in the requirement or flow that this state can occur AND that the system
  has the information available to render it?" States failing Gate 1 (no evidence) are
  flagged rather than silently generated. States failing Gate 2 (implementable with
  simpler variant) are annotated.
- The "defer with named reopen-when trigger" convention maps neatly to flagging impossible
  or unsupported states as `<!-- state-deferred: [reason] [trigger] -->` comments.

When implementing the YAGNI gate in planning skills, document how the gate definition
(evidence test wording, defer format) should be expressed in Phase 2 of the scribble
skill. TASK-PROC-032-09 will read your protocol before editing the scribble skill.
