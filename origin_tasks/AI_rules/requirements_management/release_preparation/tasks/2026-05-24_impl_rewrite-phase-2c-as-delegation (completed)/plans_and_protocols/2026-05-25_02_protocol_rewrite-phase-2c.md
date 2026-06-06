---
task: TASK-PROC-035-19
date: 2026-05-25
session_id: 985c56ee-0538-437c-88d0-9b5e02c10fcb
status: complete
---

# Protocol: Rewrite Phase 2c as Delegation Orchestrator

## Execution

Followed the plan at `plans_and_protocols/2026-05-25_01_plan_rewrite-phase-2c.md` end-to-end. Used `claude-modify-skill` as mandated by both CLAUDE.md and the goal's final AC.

## Files Modified

- `.claude/skills/release-begin-impl/SKILL.md`
  - Top-of-file callout: updated which agents read `requirements.md` (now Phase 2 epic agents + Phase 2c per-requirement `task-derive-from-requ` agents, not a Phase 2c monolithic planner).
  - Phase 2c (lines 146–339): full rewrite. Replaced the monolithic single-agent planner with a 6-step delegation orchestrator:
    - Step 1: identify in-scope feature requirements (epics excluded per REQ-PROC-035 SEC-02).
    - Step 2: spawn one `task-derive-from-requ` agent per requirement; serial default, parallel-of-2 smoke test for work-list > 8; output convention `[task_path]/per_requirement_plans/<REQ-ID>/plan.md`; explicit spawn prompt template including the path override and the FAILED.md error contract.
    - Step 3: output-file polling; FAILED.md surfacing.
    - Step 4: release plan assembly per REQ-PROC-058 SEC-04 (unified format) with new `## Per-Requirement Plans` index section and union `## Coverage Matrix`.
    - Step 5: three release-level passes — (5a) package execution ordering, (5b) cross-requirement after-chain reconciliation (heuristic + explicit, with `# cross_ref_note:` markers for ambiguity), (5c) scope coverage re-check.
    - Step 6: Phase 2 reopener handling preserved.
  - Phase 5 — User Gate: extended to surface per-requirement plan paths and the new `## Cross-Requirement Notes` section.
  - Key Constraints table: replaced Phase 2c Planner row to describe the delegation model; updated Phase 5 row.
  - Closing constraint list: added explicit bullet that Phase 2c delegates and does not decompose.

- `requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/2026-05-24_impl_rewrite-phase-2c-as-delegation/goal.md`
  - `status: pending` → `status: in_progress`, added `started: 2026-05-25`.

- `plans_and_protocols/2026-05-25_01_plan_rewrite-phase-2c.md` (new — plan).
- `plans_and_protocols/2026-05-25_02_protocol_rewrite-phase-2c.md` (this file).

## Files NOT Modified

- `.claude/skills/INDEX.md` — skill description string unchanged (`Begin implementation of a release: verify scope, create holistic task plan, activate release, create first orchestration task`); the rewrite is a Phase 2c internal restructure that doesn't alter the externally visible purpose.
- `.claude/factory_flows.md` — diagram edges (RELEASES.md write, task_creation_plan.md, orchestration task) are unchanged. Per `claude-modify-skill`, internal step reordering needs no diagram change.
- `.claude/skills/task-derive-from-requ/SKILL.md` — out of scope (TASK-PROC-058-02, already complete).
- `scripts/tasks/create_orchestration_task.py`, `scripts/tasks/summarize_plan.py`, `scripts/tasks/parse_task_creation_plan.py` — consumer-side contracts preserved. The assembled release plan keeps the same outer structure (YAML frontmatter, `## Execution Order`, `## Planned Tasks` grouped by `### PKG-...`, per-task YAML block), so `task-create-code` Phase 0A and the orchestration-task scripts are unaffected.

## Acceptance Criteria Check

| AC | Status |
|---|---|
| Phase 2c in `.claude/skills/release-begin-impl/SKILL.md` rewritten as delegation orchestrator | done |
| Per-requirement agent spawning works (parallel or serial as appropriate) | done — serial default, parallel-of-2 smoke test for large work lists |
| Each agent invocation passes requirement path + receives per-requirement plan | done — explicit Spawn prompt template with `requirement_path` and `output_plan_path` |
| Release plan assembled from per-requirement plans in unified format (REQ-PROC-058 SEC-04) | done — Step 4 |
| Release-level concerns added on top: package ordering, cross-requirement after-chains, scope completeness | done — Step 5a/5b/5c |
| Phase 5 user gate presents per-requirement coverage matrices | done — Phase 5 step 3 lists per-requirement plan paths and `## Cross-Requirement Notes` |
| task-create-code Phase 0A still consumes the assembled plan correctly (no regression) | done by construction — outer plan format preserved |
| Documentation updated in skill body | done |
| Use `claude-modify-skill` for the modification | done |

## Risk Notes

- Cross-requirement reconciliation (Step 5b) is heuristic-based. The Phase 5 user gate explicitly surfaces `## Cross-Requirement Notes` so the developer can catch false positives/negatives before any release state mutation. If the heuristic proves noisy in practice, follow-up tuning is a small skill edit, not a structural change.
- The spawn prompt for `task-derive-from-requ` instructs the agent to write outside its own task workspace. This deviates from the skill's default behavior; the prompt is explicit about the override and the rationale.
- No feature flag / monolithic fallback was retained (see plan D7). Rollback is `git revert` of this one commit.
- No `lib/`, `test/`, or `integration_test/` files were touched — `verify-quality`'s code-gate suite has nothing to enforce for this task.
