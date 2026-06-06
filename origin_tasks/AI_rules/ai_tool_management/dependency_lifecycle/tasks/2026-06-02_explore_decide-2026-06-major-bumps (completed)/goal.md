---
task_id: TASK-PROC-061-07
type: explore
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-06-03
completed: 2026-06-03
session_completed_at: 2026-06-03T16:07:34Z
effort: M
created: 2026-06-02
expected_tool_calls: 45
skill_chain_depth: 2
synthesis_dependent: true
synthesis_justification: "Must hold breaking-change analysis, call-site impact, and project stability constraints simultaneously across 5 independent major-version bumps"
after: []
covers:
  acceptance_criteria: [AC-07, AC-11]
  sections: []
scope_description: "Evaluate and produce go/no-go decisions for the 8 manual-review packages from the 2026-06 dependency review"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 3cbd51ab
  file: ../requirements.md
session_id: d1fab414-3d99-4656-a96e-b10f4e3e5481
session_account: web

---
# Goal: Decide on 2026-06 Major Dependency Bumps

## Objective

The 2026-06 monthly dependency review flagged 8 packages as requiring manual review before any action. This task evaluates each one against the project's stability constraints and call-site impact, then produces a clear go/no-go decision and — for approved bumps — creates the corresponding impl task. The decisions are recorded so future sessions and the developer can see the reasoning without re-investigating.

## Background

Source: `automation/dependency_reviews/2026-06/proposal.md` (committed `16a86d94`).

The 2026-06 review identified the following packages requiring human pre-authorization (REQ-PROC-061 AC-07):

| Package | Jump | Notes from proposal |
|---|---|---|
| `get_it` | 8.2.0 → 9.2.1 (major) | Service locator; call sites across `lib/` |
| `injectable` | 2.5.1 → 3.0.0 (major) | Code-gen; must upgrade in lockstep with `injectable_generator` |
| `injectable_generator` | 2.9.0 → 3.0.2 (major) | Must upgrade in lockstep with `injectable` |
| `go_router` | 16.2.4 → 17.2.3 (major) | Constraint change; review ShellRoute usage |
| `camera` | 0.11.4 → 0.12.0+1 (0.x = breaking) | Local Windows fork `camera_windows_patched` must be verified |
| `qr` *(dev)* | 3.0.2 → 4.0.0 (major) | Dev-only; check test call sites |
| `google_fonts` *(dev)* | 6.3.2 → 8.1.0 (major, +2 versions) | Dev-only; v7 was skipped |
| `bloc_lint` *(dev)* | 0.3.7 → 0.4.1 (minor) | Pinned — analyzer conflict with `clean_architecture_kit` |

The user has pre-authorized investigation; each individual bump still requires a decision before an impl task is created.

## How to Approach This

For each package:
1. Read the package CHANGELOG / migration guide (via REQ-PROC-053 lookup — use a spawned `general-purpose` agent with a focused question per package; do not run WebFetch inline)
2. Identify breaking changes relevant to the project
3. Search call sites in `lib/` for impacted APIs
4. Assess effort (patch-like vs. multi-day migration)
5. Check if lockstep constraints are satisfied (get_it + injectable + injectable_generator must move together)
6. For `camera`: assess whether `camera_windows_patched` platform channel is still compatible
7. For `bloc_lint`: assess whether the analyzer conflict has resolved upstream

Then produce a decision per package: **Go** (create impl task), **Defer** (reason), or **Skip** (reason).

## Seeds

- Do `get_it` 9.x breaking changes affect the project's `GetIt.instance` / `locator` call pattern in `lib/core/injection/`?
- Does `injectable` 3.0 change the code-gen output format in a way that requires regenerating `injection_container.config.dart`?
- Does `go_router` 17.x change how `ShellRoute` or `GoRouterState` is used?
- Has `clean_architecture_kit` released a version that lifts the `_fe_analyzer_shared` ceiling, unblocking `bloc_lint` 0.4.x?
- For `camera` 0.12: does the platform-channel API that `camera_windows_patched` patches still exist in the same form?

## Output

A `plans_and_protocols/` document containing:
- Per-package decision (Go / Defer / Skip) with a one-paragraph rationale
- For each **Go** decision: an impl task created under this same requirement (`REQ-PROC-061`) covering that bump, with `after: [TASK-PROC-061-07]`
- For each **Defer** or **Skip**: the condition that would change the decision

## Acceptance Criteria

- [x] All 8 packages have a recorded decision (Go / Defer / Skip)
- [x] Each decision names the specific breaking changes reviewed and the project call sites assessed
- [x] Impl tasks created for all **Go** decisions, each with `after: [TASK-PROC-061-07]`
- [x] `bloc_lint` pin status re-evaluated against current `clean_architecture_kit` upstream

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
