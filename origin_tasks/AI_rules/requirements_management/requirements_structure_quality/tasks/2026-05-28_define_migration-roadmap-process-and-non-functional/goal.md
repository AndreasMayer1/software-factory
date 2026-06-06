---
task_id: TASK-PROC-045-09
type: explore
parent_requirement: REQ-PROC-045
urgency: 3
urgency_reason: U3-FIX
impact: 4
impact_reason: I4-ENAB
status: pending
effort: M
created: 2026-05-28
after: [TASK-PROC-045-08]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-12, AC-13, AC-14, AC-17]
  sections: [SEC-03]
scope_description: "Define the migration roadmap that converts existing process/ and non-functional/ folder structure to match REQ-PROC-045 — Strangler Fig approach, prioritization, spawn individual conversion impl tasks"
release_description: ""
opus_recommended: true   # reason: cross-cutting structural restructuring touching dozens of folders, ordering and risk decisions, dependency analysis
writes_requirements: false
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Define Migration Roadmap for process/ and non-functional/ Restructure

## Objective

REQ-PROC-045 now describes the target folder structure for `requirements_tasks/`: single-axis-per-level, anchor files on every grouping, sanctioned axes per top-level category, artifact-type axis for `process/`. The current state of `process/AI_rules/` and `non-functional/` does not match. Convert it.

This task defines **how and in what order** that conversion happens — without doing the conversion itself. The output is a plan plus a set of follow-up impl tasks created against this requirement.

## Background

REQ-PROC-045 was rewritten in TASK-PROC-045-08 to remove the carve-out that previously exempted `process/` and `non-functional/` from epic-enforcement and to introduce the sanctioned-taxonomy mechanism. The requirement deliberately contains no migration content — that is this task's deliverable.

Current state observations:
- `process/AI_rules/` mixes three axes at the same level (meta-principles / what-is-regulated / process). Most folders need to move under the new artifact-type axis at `process/` itself.
- `process/AI_rules/`, `process/documentation_rules/`, `process/tooling_rules/` dissolve as named top-level folders. Their contents redistribute by artifact type.
- `workflows/` and `requirements_management/` dissolve across multiple artifact-type buckets.
- `non-functional/` is closer to compliance — bare topic folders mostly hold single flat requirements; needs anchor files (`README.md`) declaring inclusion criteria + anti-scope + sub-axis. Some sub-clusters (e.g. `ui_ux_design_system/components/`) may need epic-promotion.
- `functional/` is largely compliant; needs `README.md` anchors added to grouping folders (`client/`, `shared/`, `therapist/`).
- Cross-cutting items (release-related, factory quality umbrella, end-to-end chain integrity) land in `process/cross_artifact_rules/`.

## Approach: Strangler Fig

Per the synthesis decisions captured in TASK-PROC-045-08, the migration follows Strangler Fig:

- New structure is set up incrementally alongside the old.
- Each move is reviewable as a single commit (Tidy First: pure rename, no content change).
- ID-based REQ-IDs make moves cheap — references survive folder changes; only relative paths and the `id_registry` need regeneration.
- Individual clusters move when related work next touches their area; the roadmap captures the order and dependencies, not a hard schedule.

## Seeds

1. **Establish target structure first, then move content.** Create the top-level skeleton (`process/persona_rules/`, `process/scenario_rules/`, …, `process/cross_artifact_rules/`, `process/meta_rules/`) with empty README anchors that declare inclusion criteria + anti-scope + sub-axis. This skeleton exists before any moves happen, so each move has a clear destination.
2. **What is the right unbundling order?** Some current folders need to split across multiple destinations (`requirements_management/`, `workflows/`). Decompose them or move whole? Probably decompose, but the order matters — `release_preparation/` and `release_workflow/` could go together to `cross_artifact_rules/release/` in one task.
3. **Cluster the moves by cohesion**, not by file count. A cohesive cluster of related folders moved together is reviewable; isolated single moves create churn.
4. **Avoid mid-migration breakage.** While the move is in progress, references inside `goal.md` files of in-progress tasks may point at old paths. Decide how to handle: rewrite as part of the move, or accept the breakage and fix on next task touch.
5. **What about `tooling_rules/`?** REQ-PROC-045's sanctioned axes list it as either a peer or folded into `meta_rules/`. Decide based on actual content during the inventory.
6. **What about `dev_infrastructure/`?** Same question — fits as an artifact-type peer or under `meta_rules/`.
7. **`non-functional/` migration scope.** Probably much smaller than `process/` — needs anchor files added to existing groupings, possibly epic-promotion for `ui_ux_design_system/components/`. Worth a clean separate roadmap section.
8. **`functional/` migration scope.** Even smaller — add `README.md` anchors to `client/`, `shared/`, `therapist/`. The structure inside is already compliant.

## Output

A migration roadmap document in `plans_and_protocols/` and a set of follow-up impl tasks created against REQ-PROC-045. The roadmap:

- Inventories every existing folder in `process/`, `non-functional/`, and grouping folders in `functional/` that does not match REQ-PROC-045.
- For each, names the target destination under the new structure and the resolution path (move whole / decompose into N targets / add anchor in place / promote to epic).
- Groups the moves into cohesive clusters, each cluster becoming one impl task.
- Sets a dependency order between cluster tasks (e.g. skeleton creation before any moves; `cross_artifact_rules/` skeleton before `release_preparation` moves into it).
- Spawns the follow-up impl tasks (using `task-create`) with appropriate `after:` chains.

The roadmap is descriptive of the plan, not normative. The normative source is REQ-PROC-045.

## Acceptance Criteria

- [ ] Every folder under `process/`, `non-functional/`, and `functional/`'s grouping level that does not match REQ-PROC-045 is inventoried with its target destination.
- [ ] Moves are grouped into cohesive clusters, each cluster becoming one impl task created against REQ-PROC-045.
- [ ] The dependency order between cluster impl tasks is recorded in their `after:` chains.
- [ ] The skeleton-first approach is explicitly captured as the first cluster task (create empty `process/` artifact-type folders with README anchors, before any content moves).
- [ ] The roadmap document is honest about which folders' placement is uncertain and surfaces those for user decision before the corresponding cluster task is created.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-045-08 | in_progress | Defined the target structure in REQ-PROC-045; this task plans the path to it. |
| TASK-PROC-045-10 | pending | Enforcement extension. Independent — can run in parallel with this roadmap, but the validation script's new checks will start surfacing the (still-uncorrected) violations as soon as TASK-PROC-045-10 lands. |
