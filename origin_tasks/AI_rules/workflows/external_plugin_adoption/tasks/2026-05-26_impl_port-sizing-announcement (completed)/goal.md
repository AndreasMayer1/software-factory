---
task_id: TASK-PROC-055-03
type: impl
parent_requirement: REQ-PROC-055
urgency: 2
urgency_reason: U2-OPP
impact: 4
impact_reason: I4-ENAB
status: completed
effort: M
created: 2026-05-26
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Port han's explicit small/medium/large sizing-before-dispatch into our multi-agent skills"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: 3053f73c
  file: ../requirements.md
started: 2026-05-27
completed: 2026-05-27
session_completed_at: 2026-05-27T08:42:53Z
session_id: 6135cb21-f11d-4877-9e19-43d542ef96c1
session_account: web
---
# Goal: Port han's Explicit Sizing-Before-Dispatch into Our Multi-Agent Skills

## Objective

Inspirationally adopt (no file copying) han's sizing mechanic: classify a job as small / medium / large, **announce the size and its justification before dispatching agents**, and calibrate the agent roster size and iteration depth to that band. Default to the smallest band; escalate only on a concrete signal (file count, layer count, security/PII surface, cross-cutting concern). Under-dispatching is recoverable (re-run larger); over-dispatching is not.

Today we split `code-simple` vs `code-complex` by file count informally and never announce a size or calibrate iteration depth. This realizes REQ-PROC-055 OR-2 and directly reinforces the CLAUDE.md cache-economics / "don't over-spawn agents" rules.

## Requirements Summary

Governed by REQ-PROC-055 (External Tooling & Plugin Adoption), OR-2. Source analysis: TASK-PROC-055-01.

For full context, read:
- `../tasks/2026-05-26_explore_han-plugin-evaluation/plans_and_protocols/2026-05-26_05_synthesis_decision_report.md` (section 5, item 3)
- `../tasks/2026-05-26_explore_han-plugin-evaluation/plans_and_protocols/2026-05-26_02_gather_han_agents.md` (Sizing + Multi-Agent Economics sections — bands, caps, 45% threshold)

Current requirements: ../requirements.md

## Scope

### In Scope
- Add an explicit small/medium/large classification + pre-dispatch announcement to the skills that fan out to multiple agents (primary: `code-complex`; review which other skills dispatch agent swarms and apply where it fits).
- Calibrate roster size and iteration depth to the band; default small.
- Make the size overridable by the user.
- Use `claude-modify-skill` for each edit (syncs INDEX.md + factory_flows.md).

### Out of Scope
- Copying any han file (re-author in our voice).
- Adding new agents (covered by the separate band-F agent pilot task).
- Changing the automation orchestrator's task-selection logic.

## Acceptance Criteria

- [x] Agent-dispatching skills classify work small/medium/large and announce the chosen size + justification before dispatching.
- [x] Roster size and iteration depth are calibrated to the band; the default is the smallest band.
- [x] The user can override the chosen size.
- [x] Each skill edit went through `claude-modify-skill`.
- [x] The change is re-validated against a representative impl task before reliance in automated mode (REQ-PROC-055 OR-5).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

One of three inspirational ports from the han evaluation. Applies REQ-PROC-055's policy rather than covering a section, so `covers` is intentionally empty. OR-5 re-test applies because this changes how `code-*` skills dispatch agents.

## Revert Note (2026-05-27)

The sizing-before-dispatch additions were implemented (commit c517a69e) and then reverted in a subsequent commit. Reason: the classification and announcement blocks added token usage on every skill invocation with no measurable benefit — the routing decision (code-simple vs code-complex) already encodes the size signal implicitly, and explicit size tables + announcement blocks increased prompt length without improving agent quality or preventing over-dispatch.

**Scribble skill inspiration (TASK-PROC-032-09 depends on this)**

The sizing-before-dispatch pattern applies directly to the `ui-create-scribble` Phase 1:

- Before spawning the Phase 1 generation agent, the skill should announce the expected
  screen count band: **small** (1–3 screens, e.g., a single feature state), **medium**
  (4–7 screens, typical feature), or **large** (8+ screens, multi-exception flow).
- Band is derived from: number of ACs in scope + number of flow steps in `steps[]` +
  number of exception paths directly referenced by those ACs.
- Iteration depth (whether Phase 2 gets one or two rounds, whether a third validation
  pass is scheduled) is calibrated to the band.

When implementing sizing in `code-complex`, document the band definitions and
derivation heuristics explicitly. TASK-PROC-032-09 will adapt those to the scribble
context. If the sizing bands need adjusting for screen-count semantics (vs. file-count),
note that in your protocol.
