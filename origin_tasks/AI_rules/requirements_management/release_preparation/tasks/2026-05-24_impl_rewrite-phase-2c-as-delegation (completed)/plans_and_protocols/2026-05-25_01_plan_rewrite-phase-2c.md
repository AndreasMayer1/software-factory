---
task: TASK-PROC-035-19
date: 2026-05-25
author: implementation orchestrator
status: draft
---

# Plan: Rewrite Phase 2c as Delegation Orchestrator

## Goal

Replace the current monolithic Phase 2c in `.claude/skills/release-begin-impl/SKILL.md` with a delegation orchestrator that spawns one `task-derive-from-requ` agent per in-scope feature requirement, assembles their per-requirement plans into a release plan, and layers release-level concerns on top.

Source of authority: REQ-PROC-035 SEC-05 / SEC-06 (commit f58c811e) and REQ-PROC-058 AC-14 + SEC-04 (unified plan format).

## Design Decisions

### D1 — Which requirements get delegated to?

Only **feature-level** requirements with acceptance criteria. Per REQ-PROC-035 SEC-02 epics are exempt from impl task coverage; per REQ-PROC-058 the decomposition skill consumes requirements with ACs. Detection: requirements listed in `STATUS_NEXT_RELEASE.md` for this release whose `requirements.md` has at least one AC. Epic requirements (those with feature children but no own ACs) are skipped — their child features are the delegation targets.

### D2 — Parallel vs serial agent fan-out

Default: **serial**. Rationale: each `task-derive-from-requ` invocation is itself heavy (Phase 1.5 cross-ref gate may spawn its own subagent, Phase 1 reads multiple files, full mode can take 5+ min). Running N feature requirements in parallel from the main orchestrator risks compounding context cost and triggers our long-running-agent cache protection rule for each one simultaneously. Serial keeps a single 4:30 heartbeat loop active and bounds total spawn count.

Escape hatch: if a release has > 8 feature requirements, the planner spawns the first 2 in parallel as a smoke test, falls back to serial if any of them stalls > 10 min. This is documented as an operator-tunable knob in the skill but defaults to plain serial.

### D3 — Output file convention (output-file polling)

Each per-requirement agent writes to:
```
[task_path]/per_requirement_plans/<REQ-ID>/plan.md
```
The orchestrator polls for the existence of `plan.md` for each requirement. This matches the Phase 2b pattern (no agent-ID tracking; presence of output file = done).

Per `task-derive-from-requ` Phase 4: the skill normally writes plan to its own task's `plans_and_protocols/` because it's invoked on a task. Here Phase 2c is invoking it cross-task. We override the output path in the spawn prompt — the agent writes to the path given by Phase 2c, not its own task path.

### D4 — Cross-requirement after-chain reconciliation

Each per-requirement plan only knows its own ACs. The monolithic agent had implicit cross-visibility ("REQ-A task X depends on REQ-B task Y"). To compensate, Phase 2c runs a reconciliation step **after** assembly:

1. Read all per-requirement plans
2. For each requirement's `Related Requirements` and `after:` frontmatter, identify cross-requirement dependency relationships
3. For tasks whose `implementation_notes` mention a concept owned by another requirement (e.g., "uses data model from REQ-XXX"), inject a cross-requirement `after:` edge to the latest covering task in the other requirement's plan
4. Heuristic + explicit. Where ambiguous, leave a `# cross_ref_note:` comment on the task and surface it in the Phase 5 summary for user review

This is deliberately conservative — wrong cross-edges are easier for the user to notice during Phase 5 review than missing ones.

### D5 — Release plan assembly format

The release plan stays at `[task_path]/task_creation_plan.md`. Per-requirement plans live as siblings under `per_requirement_plans/<REQ-ID>/plan.md` and are referenced from the release plan via a `## Per-Requirement Plans` index section. The assembled release plan's `## Planned Tasks` section concatenates the entries from all per-requirement plans, regrouped under `### PKG-...` headings (the release-level reordering by package). YAML frontmatter remains release-level (`plan_id`, `release`, `explore_task`, etc.).

`task-create-code` Phase 0A continues to consume the release `task_creation_plan.md` — no consumer-side change required because the assembled plan keeps the same outer structure.

### D6 — Phase 5 surface change

Phase 5 today shows: `summarize_plan.py` output + plan path + findings paths. New: also list the `per_requirement_plans/<REQ-ID>/plan.md` paths (one per requirement) so the developer can drill into per-requirement coverage matrices. The summary itself doesn't need to change because the assembled plan already feeds `summarize_plan.py`.

### D7 — Feature-flag/fallback?

The goal note mentions feature-flag with monolithic fallback. **Decision: no flag.** Reasons:
- The monolithic agent prose lives only in the skill body — replacing it does not delete code anyone calls programmatically
- A flag would require maintaining two divergent Phase 2c flows in the same skill file; the skill is already large
- Rollback is `git revert` of this one commit
- TASK-PROC-035-18 already committed the requirement-level change describing the new pattern, so the skill is currently out of sync with its requirement

Risk mitigation: the rewrite is gated behind the user gate at Phase 5 — if the assembled plan looks broken, the developer rejects and the orchestrator iterates before any release state changes.

### D8 — What about the existing "Large-release mitigation" note (>100KB split)?

Removed. The new delegation pattern is inherently per-requirement, so total context is bounded by the largest single requirement. The mitigation note no longer applies.

## Steps

1. Draft new Phase 2c body for SKILL.md
2. Update Phase 5 body to mention per-requirement plan paths
3. Update the `## Key Constraints` table (replace "Phase 2c Planner" row)
4. Update the top-of-file callout (orchestrator never reads requirements.md — still true; the per-req agent does)
5. Update INDEX.md only if the skill description string changes (it doesn't — description stays the same)
6. Apply edits via `claude-modify-skill`
7. Run verify-quality (no `lib/` files touched but the skill-level gates still apply)

## Acceptance Criteria Mapping (from goal.md)

| AC | Implementation step |
|---|---|
| Phase 2c rewritten as delegation orchestrator | Step 1 |
| Per-requirement agent spawning works | Step 1 (Spawn block in new Phase 2c) |
| Each agent passes requirement path + receives per-requirement plan | Step 1 (Spawn prompt template) |
| Release plan assembled in unified format | Step 1 (Assembly subsection) |
| Release-level concerns added on top | Step 1 (Reconciliation + Package ordering subsections) |
| Phase 5 presents per-requirement coverage matrices | Step 2 |
| task-create-code Phase 0A unaffected | Outer plan structure preserved (D5) — no skill change to task-create-code |
| Documentation updated | Step 1 prose |
| Use claude-modify-skill | Step 6 |

## Risk Notes

- `task-derive-from-requ` writing to a non-default path is a deviation from its current default behavior. The spawn prompt makes the output path explicit and includes a "do not write to your own plans_and_protocols/" instruction.
- Cross-requirement reconciliation (D4) is heuristic. If it produces noisy false edges, the user catches them at Phase 5 and we tune the heuristic in a follow-up task — do not over-engineer this pass.
