---
date: 2026-05-18
type: protocol
session_id: aa6503be-7aaf-4b22-91bc-47e8fab4b17b
session_account: gmail
task_id: TASK-PROC-002-09
---

# Implementation Protocol — TASK-PROC-002-09

## Summary

Extended `.claude/skills/requ-derive-from-flow/skill.md` to emit per-flow integration-test requirements, and bootstrapped the integration-tests non-functional epic at `requirements_tasks/non-functional/integration_tests/requirements.md` with allocated ID **REQ-NFUNC-023**.

## Changes Applied

### 1. Bootstrapped non-functional epic

- Allocated REQ-ID via `scripts/requirements/allocate_req_id.py --parent-id REQ-NFUNC --parent-path requirements_tasks/non-functional/` → **REQ-NFUNC-023**
- Wrote `requirements_tasks/non-functional/integration_tests/requirements.md` with standard non-functional epic frontmatter (status: active, urgency 3 / U3-CTX, impact 4 / I4-QUAL, stakeholder: developer, effort: XL), Overview, Purpose, Features placeholder
- Released reserve marker `.reserve-REQ-NFUNC-023`

### 2. Skill edits — `.claude/skills/requ-derive-from-flow/skill.md`

| Edit | Phase | What changed |
|------|-------|-------------|
| 1 | Phase 2 gap taxonomy | Added `integration_test_needed` status between `foundation_gap` and `out_of_scope`, with the directive "emit exactly one row per flow processed unless requirement already exists at that path (then `exists_complete`)" |
| 2 | Phase 2 Summary table | Added `integration_test_needed` row alongside the other status counters |
| 3 | Phase 2 Notes section | Added a "Per-flow integration-test row (always emit)" bullet making the side-output rule explicit and visible to Opus; clarifies that the row is not derived from gap analysis but is always emitted, and appears at end of Flow Gaps table |
| 4 | Phase 2 Suggested Package rules | Added rule for `integration_test_needed` rows: copy Suggested Package from the primary functional gap (lowest-numbered new_needed / exists_needs_update / exists_placeholder row) — integration tests ship with the features they cover |
| 5 | Phase 4.2 target task folder mapping | Added `integration_test_needed` → `requirements_tasks/non-functional/integration_tests/<flow_id>/tasks/[today]_explore_<flow_id>_integration_tests/`, with parent_requirement pointing at REQ-NFUNC-023 |
| 6 | Phase 4.2 goal.md template variant | Added a variant block right after the main template with fixed `## Goal` and `## What to Create / Update` wording for integration_test_needed rows, naming the happy-path / exception-path / boundary-conditions coverage requirement |

## Acceptance Criteria — Status

| AC | Status |
|----|--------|
| Phase 2 gap taxonomy includes `integration_test_needed` | ✓ |
| Phase 2 Opus matrix instruction emits the integration-test row per flow | ✓ (taxonomy entry + Notes bullet) |
| Phase 4.2 goal.md template handles the new row type with the documented scope text | ✓ (variant after main template) |
| Phase 4.2 Suggested Package rule routes integration-test rows to the same package as the primary functional gap | ✓ |
| `requirements_tasks/non-functional/integration_tests/requirements.md` exists with standard frontmatter and the next available `REQ-NFUNC-*` ID | ✓ (REQ-NFUNC-023) |
| Smoke test: run `requ-derive-from-flow` on an existing flow and observe the new row + goal.md | **Deferred** — end-to-end skill execution requires user-interactive Phase 0/3/3.5 confirmations and Opus matrix generation; not runnable in this automated session. The skill modifications are surgical text additions to existing slot points; manual code-read review confirms each AC sub-criterion is wired. The next manual run of the skill will exercise the path. |

## Files Touched

- `.claude/skills/requ-derive-from-flow/skill.md` (modified)
- `requirements_tasks/non-functional/integration_tests/requirements.md` (created)
- `requirements_tasks/process/AI_rules/coding_standards/testing/tasks/2026-05-14_impl_extend-requ-derive-from-flow-for-integration-tests/goal.md` (status → in_progress)

## Notes

- INDEX.md and factory_flows.md not modified: skill description unchanged (still "Analyze user flow(s) to find requirement gaps"); no new artifact type — integration-test requirements are still requirements flowing into the existing REQ node of the factory diagram. Per claude-modify-skill rules, additive logic within an existing role doesn't require diagram changes.
- Backfill is out of scope per goal.md; next `requ-derive-from-flow` run on each flow will pick up the new row automatically.
