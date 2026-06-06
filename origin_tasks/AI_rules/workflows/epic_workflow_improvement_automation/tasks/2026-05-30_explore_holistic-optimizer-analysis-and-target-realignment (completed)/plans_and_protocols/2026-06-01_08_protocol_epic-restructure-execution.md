---
name: epic_restructure_execution_protocol
description: >
  Execution protocol for the approved epic restructure (plan _07). Records what the
  background executor agent did, the allocated IDs, and verification by the parent
  session. Written by the parent session because the executor agent hit a per-account
  session usage limit immediately after committing its final step, before it could
  write its own protocol.
created: 2026-06-01
type: execution_protocol
author: claude-opus (parent session) + general-purpose executor agent a4ec1b78a984c4554
task: TASK-PROC-006-20
references:
  - 2026-06-01_07_plan_epic-restructure.md (the approved plan)
---

# Epic Restructure — Execution Protocol

## Outcome: COMPLETE and verified

The developer approved the plan ("Approved" — all recommendations: D-A derived IDs,
D-B explore tasks write their feature requirement, D-C 7 features, D-D execute now).
A background `general-purpose` agent (id `a4ec1b78a984c4554`) executed plan §6. It
hit a per-account session usage limit right after its last commit, so it did not
write this protocol itself — the parent session verified the committed result and
authored this record.

## What was done (commits, oldest→newest)

| Commit | Step |
|---|---|
| `6cf54094` | rename folder → `epic_workflow_improvement_automation/` (git mv, history preserved) |
| `a1589109` | reduce `requirements.md` to epic-level (id REQ-PROC-006, status active, 53 body lines ≤90) |
| `e8622ba2` | fix(skills): defer task-create in requ-explore until after location approval (bug the agent hit + fixed) |
| `74dfea86` | add 7 feature placeholders under the epic |
| `20e4af16` | move TASK-PROC-006-16 → feat_targets_metrics_audit |
| `b2c7fa5f` | update TASK-PROC-006-16 parent_requirement → REQ-PROC-006-02 |
| `841b9043` | add 7 per-feature exploration tasks |
| `c3d95a2c` | fix feature frontmatter for validate_meta (status `draft`, priority fields, re-map covers) |
| `46699345` | regenerate STATUS.md |
| `a88ea83f` | regenerate merged requirements.md |

## Allocated structure

Epic **REQ-PROC-006** (`active`) → 7 features (status `draft`; the agent chose `draft`
over the plan's `placeholder` so `validate_meta` passes — an acceptable, validated
substitution):

| Feature folder | Feature ID | Per-feature explore task |
|---|---|---|
| feat_detection_event_pipeline | REQ-PROC-006-01 | TASK-PROC-006-01-01 |
| feat_targets_metrics_audit | REQ-PROC-006-02 | TASK-PROC-006-02-01 (+ moved TASK-PROC-006-16 impl) |
| feat_evaluation_statistical_contract | REQ-PROC-006-03 | TASK-PROC-006-03-01 |
| feat_evaluation_simulation_harness | REQ-PROC-006-04 | TASK-PROC-006-04-01 |
| feat_guardrails_and_budgets | REQ-PROC-006-05 | TASK-PROC-006-05-01 |
| feat_orchestration_cadence_production | REQ-PROC-006-06 | TASK-PROC-006-06-01 |
| feat_self_optimization_experiment | REQ-PROC-006-07 | TASK-PROC-006-07-01 |

## Verification (parent session)

- Epic id REQ-PROC-006, status active, body 53 lines (Epic Size Gate ✓).
- All 7 feature requirements exist with derived IDs and carry their scope + R4 seeds
  (spot-checked feat_evaluation_simulation_harness: Git-branch test data, synthetic-
  from-real, per-skill simulation budget, scenario deny-list + tamper-resistant
  add/deprecate all present).
- All 7 per-feature explore tasks exist, each `type: explore`, parented to its
  feature, **referencing the full iteration history** (syntheses _02/_04/_06, feedback
  _03/_05/_06-01, plan _07, and the 2026-05-01 redesign exploration) — the developer's
  "so it has the whole picture" requirement is met.
- TASK-PROC-006-16 relocated to feat_targets_metrics_audit/tasks/, parent REQ-PROC-006-02.
- 18 completed/cancelled tasks remain at epic level (history), as planned.

## Residual / honest notes

- **Feature status is `draft`, not `placeholder`** (validate_meta compatibility) — the
  per-feature explore tasks will deepen each feature and a `requ-explore` will move it
  to `defined`/`active`.
- **One open problem deferred to feat_evaluation_simulation_harness:** the tamper-
  resistant scenario-set add/deprecate mechanism (carried as a seed, not solved).
- **No implementation tasks were modified** — per the developer, per-feature
  exploration precedes any impl rewrite.
- The agent's session-limit interruption affected only protocol authorship; all
  functional commits landed and are verified above.
