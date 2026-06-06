---
task_id: TASK-PROC-044-04
type: impl
parent_requirement: REQ-PROC-044
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-05-30
session_completed_at: 2026-05-30T01:37:55Z
effort: L
created: 2026-05-29
started: 2026-05-29
after: [TASK-PROC-044-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04]
  sections: []
scope_description: "Wave 2 of the skill-interface-contracts rollout. Author contract.yaml for consumer skill families (code-simple, code-complex, code-bugfix, code-test, ui-verify-flutter, ui-improve-flutter, task-derive-from-requ, task-create-code, task-complete). Author scripts/quality/validate_against_schema.py (YAML-dialect schema validator). Add 5-line bash pre-checks at the top of each consumer skill body. Re-run sub-skill-vs-agent rubric on every skill being migrated; document refinements; if any signal weight needs adjustment, propose via revision_target.yaml to FU-6's tracking task."
release_description: ""
opus_recommended: true   # reason: cross-cutting across 9 skills + new schema validator + rubric re-run discipline
writes_requirements: false
requirements_version:
  commit: b10665f5
  file: ../../requirements.md
source_exploration: TASK-PROC-044-02
bundle_id: FU-2
session_id: 136c4709-8241-4f09-95dd-5bcbc4a65ae7
session_account: gmail
---
# Goal: Wave 2 — Skill Contracts for Consumer Families + Runtime Pre-Checks

## Objective

Land Wave 2 of the contract mechanism: the consumer-side of the producer-consumer graph established by Wave 1 (TASK-PROC-044-03). This wave adds the **verification leg** — the runtime check that PwC's 7× evidence (web research file 02 §Q7) argues carries the largest measurable win.

## Background

Wave 1 establishes producer contracts + schemas + commit-time lint. Wave 2 extends to:
- Consumer-side contract.yaml for the major code-*, ui-*, task-* consumers
- A YAML-dialect schema validator (`scripts/quality/validate_against_schema.py`) — the schemas from Wave 1 become *runtime-enforced*, not just documentation
- 5-line bash pre-checks at the top of consumer skills — the runtime guard pattern

See `requirements_tasks/process/AI_rules/factory_quality/tasks/2026-05-29_explore_skill-interface-contracts-mechanism/plans_and_protocols/05_round_3_synthesis.md` §D-2 component 3 + §D-5 Wave 2.

## How to Approach This

1. Read the exploration synthesis + amendments + the Wave-1 deliverables (review what Wave 1 actually produced — there may be deltas vs the design).
2. Author contract.yaml for each of: code-simple, code-complex, code-bugfix, code-test, ui-verify-flutter, ui-improve-flutter, task-derive-from-requ, task-create-code, task-complete.
3. Build `scripts/quality/validate_against_schema.py` (use `claude-write-script`). The validator reads a YAML file + a schema file (`.claude/schemas/<artifact>.yaml`), checks required-keys present, optional-keys allowed, enums respected. Output: 0 on pass, 1 with specific message on fail (per file 02 §Q5 anti-punting rule).
4. For each consumer skill, add a 5-line bash pre-check block at the top of its execution body. Pattern:
   ```bash
   [ -f "${ARTIFACT_PATH}" ] || { echo "ERR: missing input X per contract.yaml"; exit 2; }
   python3 scripts/quality/validate_against_schema.py "${ARTIFACT_PATH}" .claude/schemas/<artifact>.yaml || exit 2
   ```
5. **Rubric re-run**: for every consumer skill migrated, apply the 4-signal sub-skill-vs-agent rubric (from FU-6 / `claude-create-skill`). Document each skill's score in this task's `plans_and_protocols/`. If any skill scores at the borderline (2/4) or surprises (3/4 score on what feels integrated, or 1/4 on what feels split-worthy), propose via `revision_target.yaml` to FU-6 (TASK-PROC-044-08) for rubric refinement.

## Acceptance Criteria

- [x] contract.yaml present and lint-passing for all 9 named consumer skills
- [x] `scripts/quality/validate_against_schema.py` exists, follows tier B annotation, passes G1-G3 Python gates
- [x] 5-line bash pre-checks present at the top of all 9 consumer skill bodies
- [x] Rubric re-run documented per-skill in `plans_and_protocols/` (one entry per skill: scores + verdict + any refinement proposal)
- [x] If rubric refinement was proposed: revision_target.yaml exists in FU-6's task workspace pointing back to this task
- [x] No false-positive lint violations across the 9 contracts (each `derived_from` item has correct `source:` annotation)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-03 (Wave 1) | pending | Producer contracts + initial schemas + lint must land first |

## Notes

This task is in `flutter_app/.claude/task_ordering_priority_override.txt`. Wave 3 (TASK-PROC-044-05) follows this task.
