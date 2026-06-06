---
task_id: TASK-PROC-044-12
type: impl
parent_requirement: REQ-PROC-044
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-05-31
session_completed_at: 2026-05-31T14:38:18Z
effort: M
created: 2026-05-30
started: 2026-05-30
after: [TASK-PROC-044-11]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-04, AC-08]
  sections: []
scope_description: "Roll out external factory-boundary contract declarations to a canonical home, author missing schemas, add input_modality to the schema dialect, and wire a boundary-contract lint into verify-quality. Source: TASK-PROC-044-10 synthesis §5 (FU-8b)."
release_description: ""
writes_requirements: false
opus_recommended: false
requirements_version:
  commit: b10665f5
  file: ../../requirements.md
source_exploration: TASK-PROC-044-10
session_id: 34137435-8387-445f-91c0-0272c8b46455
session_account: gmail
---
# Goal: Roll Out External-Boundary Contract Declarations

## Objective

Promote the external-interface contract mechanism explored in TASK-PROC-044-10 from drafts
to a live, linted part of the factory. The exploration produced: 3 concrete contract drafts
(E1/E4/E5), an analogy table for E2/E3/E6/E7/E9, the additive `input_modality:` field
analysis, and 8 working validator scripts (`scripts/factory/external_state/`). This task
makes them canonical and enforced.

## Requirements Summary

REQ-PROC-044 (after TASK-PROC-044-11 lands its boundary AC) requires every external
factory-boundary interface to carry a contract in the same format, with `quality_criteria`
referencing the external-state vocabulary, and a failing check producing a visible warning
or graceful stop (extends AC-01/AC-04 to the boundary).

For complete requirements at task creation time:
```
git show b10665f5:requirements_tasks/process/AI_rules/factory_quality/requirements.md
```
Current requirements: ../../requirements.md

## Scope

### In Scope
- Choose + create the canonical home for boundary contracts (proposal: `.claude/contracts/external/`) — MUST be outside `.claude/skills/` so `check_skill_contracts.py`'s glob does not ingest them.
- Promote the E1/E4/E5 drafts from `2026-05-29_explore_external-interface-contracts/plans_and_protocols/02_external_contracts.md` and author the remaining interfaces (E2, E3, E6, E7, E9).
- Author the missing schema(s) referenced by the drafts (e.g. `.claude/schemas/pending_question.yaml`).
- Add `input_modality:` (enum file|frontmatter|conversation|invocation_arg|command_output|url_response) to the schema dialect, defaulting to `file` so existing Wave 1–3 internal contracts remain valid without edits — implement and TEST that default.
- Write a boundary-contract lint (sibling to `check_skill_contracts.py`) that resolves each `quality_criteria.check` to a script under `scripts/factory/external_state/`; wire it into `verify-quality` per-change gates.

### Out of Scope
- Contracts for E10 (git-remote) and E11 (Windows-host) — no automated channel exists today (deferred per synthesis §6).
- Live network/OS testing of `url_returned_2xx` / `package_installed_at_version`.

## Acceptance Criteria

- [ ] Boundary contracts for E1–E7 + E9 exist at a canonical home outside `.claude/skills/`
- [ ] Every referenced schema exists; `input_modality:` is part of the schema dialect with a tested `file` default
- [ ] A boundary-contract lint validates check→script resolution and runs in verify-quality
- [ ] `check_skill_contracts.py` still passes (boundary contracts are not ingested by its glob)
- [ ] All Python gates green

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-11 | pending | Adds the boundary AC this task covers |
| TASK-PROC-044-10 | in_progress | Source exploration: drafts, vocabulary, validator scripts |
