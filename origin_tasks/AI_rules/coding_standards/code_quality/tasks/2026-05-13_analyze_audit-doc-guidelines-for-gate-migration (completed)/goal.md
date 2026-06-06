---
task_id: TASK-PROC-046-12
type: analyze
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-13
started: 2026-05-15
completed: 2026-05-16
session_completed_at: 2026-05-16T10:04:35Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-13]
  sections: []
scope_description: "Walk every file under doc/, classify each rule as (a) gate-scriptable, (b) judgment-only, or (c) already enforced; for (a) propose a migration to analysis_options.yaml or scripts/quality/; for (b) confirm it stays in doc/ and is enforced by quality-checker reading; for (c) cross-reference the existing gate."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: 7da537ca-3e3d-46a6-a0e8-577dd315db74
session_account: gmail2
---

# Goal: Audit doc/ guidelines for rules that should be promoted to the gate set

## Objective

REQ-PROC-046's revised Developer Guidelines establishes the doc/-vs-gate-set border: scriptable rules belong in the gate set; judgment rules stay in `doc/`. Whether current `doc/` content sits on the right side of that line is unverified. This audit walks every guideline file, classifies each rule it contains, and produces a migration plan for the rules that should be gates but aren't.

## Requirements Summary

REQ-PROC-046 AC-13 (single authoritative location for the gate set and its relationship to `doc/`). The audit output informs which gates need to be added (downstream impl tasks) and which `doc/` rules should be tightened, simplified, or removed because they duplicate gates.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Walk every `.md` under `doc/` (architecture, domain, presentation, testing, linter, general, cross_cutting_standards).
- For each rule encountered, classify as:
  - **(a) Gate-scriptable** — compliance is decidable from a syntactic / structural property (e.g. "domain entities are immutable", "no `dynamic` types outside data-deserialisation boundaries", "BLoC events are sealed classes"). Note the proposed gate mechanism: analyzer lint? `dart_code_linter` rule? grep script under `scripts/quality/`?
  - **(b) Judgment-only** — compliance requires reading intent (e.g. "use BLoC for stateful presentation; provider for simple shared state"). Confirm `doc/` is the right home and the `quality-checker` agent's existing reading flow catches violations.
  - **(c) Already gate-enforced** — the rule is restated in `doc/` but is also in `analysis_options.yaml` or a script. Cross-reference and recommend whether `doc/` should keep the prose, replace it with a pointer to the gate, or both.
- For each (a) finding, write a one-line proposed gate definition (lint rule name, or regex pattern). Do not implement; just propose.
- For each (b) finding with no current narrative coverage, flag it as a gap.
- Output `plans_and_protocols/doc_audit.md` with a table per `doc/` file:
  - File path
  - Rule excerpt
  - Classification
  - Proposed action (migrate to gate / stays in doc / cross-reference existing gate)
  - Effort to implement migration (S / M / L)
- Summarise totals at the top: how many (a), (b), (c); estimated effort to migrate all (a).

### Out of Scope

- Implementing any migration. Each (a) finding becomes a candidate impl task; the audit only proposes.
- Editing `doc/` content. Even cross-reference updates are downstream work.
- Re-litigating which rules should exist. The audit classifies what's there; it doesn't add or remove rules.

## Acceptance Criteria

- [ ] Every file under `doc/` has been walked.
- [ ] `plans_and_protocols/doc_audit.md` lists rules with classifications and proposed actions.
- [ ] Totals are summarised at the top so the user can size the migration.
- [ ] (a) findings include a concrete proposed gate mechanism (lint name / regex / DCM rule).
- [ ] If the audit finds zero gate-scriptable rules in `doc/`, that fact is recorded explicitly (means the existing split is already correct).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

The audit produces a *menu* of potential gates, not a commitment to add all of them. After the audit, the user decides which proposals to schedule as impl tasks. Per REQ-PROC-046's "gate-set changes require user approval" rule, no autonomous follow-on creation of impl tasks from this audit — it's user-reviewed first.

Where a rule is restated in three places (e.g. `doc/architecture/dependency_injection.md` + a lint rule + a script that greps for `getIt` usage), the audit flags the duplication and recommends collapsing to one authoritative source.
