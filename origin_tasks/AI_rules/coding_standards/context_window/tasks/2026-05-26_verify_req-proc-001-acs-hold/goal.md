---
task_id: TASK-PROC-001-12
type: verify
verification_task: true
parent_requirement: REQ-PROC-001
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: pending
effort: M
created: 2026-05-26
after: [TASK-PROC-001-03, TASK-PROC-001-04, TASK-PROC-001-05, TASK-PROC-001-06, TASK-PROC-001-07, TASK-PROC-001-08, TASK-PROC-001-09, TASK-PROC-001-10, TASK-PROC-001-11]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08]
  sections: []
scope_description: "Verification task: audit every AC of REQ-PROC-001 across requirements_tasks/, the heavy skills (requ-explore, task-resolve, task-create, release-begin-impl), and CLAUDE.md §7."
release_description: ""
opus_recommended: true   # reason: synthesis-dependent — cross-checks 8 ACs across many tasks, skills, and CLAUDE.md simultaneously
writes_requirements: false
expected_tool_calls: 40
skill_chain_depth: 1
synthesis_dependent: true
synthesis_justification: "Cross-checks 8 ACs across requirements_tasks/, multiple skills, and CLAUDE.md simultaneously; conclusions depend on holding all evidence at once."
requirements_version:
  commit: 8c0eaa33
  file: ../../requirements.md
plan_source: requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/tasks/2026-05-24_impl_test-case-req-proc-001-decomposition/plans_and_protocols/2026-05-26_task_creation_plan.md
---
# Goal: Verify REQ-PROC-001 ACs hold across `requirements_tasks/` and skills

## Objective

Audit task confirming every AC of REQ-PROC-001 holds in practice across the
codebase's process artifacts. Must run AFTER the per-AC impl tasks land — it
checks the live state of `requirements_tasks/`, the heavy skills, and
CLAUDE.md §7 to confirm the rules are not merely written but actually applied.

This is the **mandatory verification task** for REQ-PROC-001 — none existed
prior to this. It closes the AC-02 gate of the `task-derive-from-requ` skill.

## Requirements Summary

REQ-PROC-001 defines four signals (S1–S4) governing task sizing and Opus
recommendation. Eight ACs (AC-01..AC-08) operationalise the User Story. This
task verifies each AC holds in practice after the implementation tasks
(TASK-PROC-001-03..-11) have landed.

For complete requirements at task creation time:
```
git show 8c0eaa33:requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

For each AC, perform the verification described and record findings in
`plans_and_protocols/<date>_verification_report.md`:

- **AC-01 — Sizing-signal declaration**: sample N≥10 most-recently-created
  `goal.md` files. Confirm each declares `expected_tool_calls` OR
  `skill_chain_depth`.
- **AC-02 — Synthesis-dependent flagging**: among the same sample, confirm
  every task with `synthesis_dependent: true` carries a one-line
  justification field.
- **AC-03 — High-volume escalation/split/fan-out**: confirm no task with
  `expected_tool_calls > 60` OR `skill_chain_depth ≥ 4` has both
  `opus_recommended: false` AND no documented fan-out / split.
- **AC-04 — Open-scope fan-out plan**: identify tasks whose In Scope is
  pattern-defined (e.g. "every feature under feat_*"). Confirm each carries a
  named agent fan-out plan in goal.md.
- **AC-05 — Heavy skills defer to agents**: read SKILL.md for `requ-explore`,
  `task-resolve`, `task-create`, `release-begin-impl`. Confirm each defers to
  agents when the per-task read budget is exceeded
  (`scripts/util/should_use_agents.py` integration).
- **AC-06 — requ-explore re-entry guard**: read `requ-explore/SKILL.md`.
  Confirm the re-entry guard is documented and enforced.
- **AC-07 — Iterative-fix loop opus escalation**: read `task-create-code/SKILL.md`.
  Confirm the AC-07 rule (verify-quality + lib/ + > 3 files / open scope →
  `opus_recommended: true`) is implemented after TASK-PROC-001-11 lands.
- **AC-08 — CLAUDE.md §7 documents the four signals**: read CLAUDE.md §7.
  Confirm S1–S4 are documented with their composition into a sizing decision.

### Out of Scope

- Re-running the impl tasks. If an AC fails, file a follow-up task (bugfix
  or extension); do not fix-in-place during the audit.
- Changing requirements.md. If an AC is found to be ambiguous, file a
  follow-up to clarify the AC via `requ-explore`.

## Acceptance Criteria

- [ ] `plans_and_protocols/<date>_verification_report.md` exists, one
      section per AC (AC-01..AC-08), each with: method used, sample/files
      audited, pass/fail, and any follow-ups filed.
- [ ] Every AC has been verified — no AC is skipped or "deferred".
- [ ] For every failing AC, a follow-up task (bugfix or extension) is filed
      against REQ-PROC-001 with a clear scope.
- [ ] The verification report is signed off (status note at top of report
      summarising pass/fail count).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-001-03 | pending | CLAUDE.md §7 four-signals doc (AC-08) |
| TASK-PROC-001-04 | pending | should-use-agents per-task mode (AC-05) |
| TASK-PROC-001-05 | pending | requ-explore re-entry guard (AC-06) |
| TASK-PROC-001-06 | pending | task-create sizing gate (AC-01/02/03) |
| TASK-PROC-001-07 | pending | task-create-code automated structural check (AC-01/03) |
| TASK-PROC-001-08 | pending | task-resolve automated file-set check (AC-05) |
| TASK-PROC-001-09 | pending | code-bugfix resume summarisation (AC-05) |
| TASK-PROC-001-10 | pending | Open-scope discovery gate (AC-04) |
| TASK-PROC-001-11 | pending | task-create-code AC-07 iterative-fix escalation (AC-07) |

## Notes

Derived by `task-derive-from-requ` (TASK-PROC-058-07 validation run) on
2026-05-26 from `plan_source`. This is the mandatory verification task per
REQ-PROC-058 AC-02 — REQ-PROC-001 had none prior.

`target_package` is intentionally omitted: per `task-create` rules,
`verification_task: true` keeps the task unpackaged so it ranks alongside the
impl tasks it verifies in `next_tasks.py`.
